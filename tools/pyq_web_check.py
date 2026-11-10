"""Second step after tools/pyq_notes_check.py: checks the PYQs the notes could not confirm (CONFLICT, NO_KEY and,
optionally, NOT_COVERED) with web search, one PYQ per request, on the Message Batches API.

The model prefers the official answer key (APPSC / UPSC / the board that set the paper) and otherwise standard
sources, and answers KEEP / KEY n / UNSURE with a source URL. collect writes the decisions in tools/keys_apply.py's
format (data/keys/out/<n>.md), so applying them is:  python3 tools/keys_apply.py

    python3 tools/pyq_web_check.py build --run web --from full                    # CONFLICT + NO_KEY + NOT_COVERED
                                                          # 8 PYQs of the same paper per request (--group 1: one each)
    python3 tools/pyq_web_check.py build --run webpilot --from full --sample 100  # a small paid test first
    python3 tools/pyq_web_check.py build --run deep --from full --retry-from web --group 4   # deep pass on UNSURE
    python3 tools/pyq_web_check.py submit  --run web
    python3 tools/pyq_web_check.py status  --run web
    python3 tools/pyq_web_check.py collect --run web      # results.jsonl, summary.md, data/keys/out/<n>.md
    python3 tools/pyq_web_check.py resume  --run web      # re-submit turns that paused mid-search, then collect again

Files go to data/keys/web_check/<run>/.
"""
import argparse
import glob
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pyq_notes_check as nc  # noqa: E402

ROOT = nc.ROOT
OUT = os.path.join(ROOT, "data/keys/web_check")
KEYS_OUT = os.path.join(ROOT, "data/keys/out")
MODEL = "claude-sonnet-5-5"
EFFORT = "medium"
MAX_SEARCHES = 3
# Batch API: half of list token prices (Sonnet 5.5: $2 in / $10 out per MTok); web search $10 per 1,000, not discounted.
PRICE_IN, PRICE_OUT, PRICE_SEARCH = 1.00, 5.00, 0.01

SYSTEM = """You verify the answer key of one previous-year exam question (PYQ) for an APPSC exam-preparation app. \
Search the web and decide which option is correct.

Priority of sources: (1) the official final answer key of the board that set the paper (APPSC, UPSC, TSPSC, UPPSC, \
SSC, etc.), taking any official revision into account; (2) primary/official sources (constitution and acts, \
government sites, PIB, RBI, Census, NCERT, ISRO, UNESCO, Britannica); (3) standard reference books. Quiz/coaching \
sites only as a last resort, and never alone against a better source. A question with an official key keeps the \
official answer unless the board itself revised it. For a time-sensitive fact, judge it as of the exam year.

End your reply with ONE line of JSON and nothing after it:
{"verdict": "KEEP" | "KEY" | "UNSURE", "option": <1-based correct option, 0 if UNSURE>, "source": "<best URL>", \
"fact": "<one sentence stating the correct fact, usable as the explanation>"}
- KEEP: the given key is correct (option = the key's number).
- KEY: the given key is wrong or missing and "option" is correct, shown by the source.
- UNSURE: sources disagree, nothing reliable was found, or the question/options are garbled. Never guess."""

WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": MAX_SEARCHES}

# Grouped mode: several PYQs of the SAME exam paper in one request, so one search for that paper's official key
# (or one topic search) can settle several of them.
SYSTEM_GROUP = SYSTEM.replace("the answer key of one previous-year exam question (PYQ)",
                              "the answer keys of several previous-year exam questions (PYQs), mostly from one paper,")
SYSTEM_GROUP = SYSTEM_GROUP[:SYSTEM_GROUP.index("End your reply")] + """Search efficiently: first look for the \
official answer key of the paper(s) named, which can settle many questions at once; then search only for the \
questions still open, combining related questions in one query where you can.

End your reply with one JSON line per question, in the given order, and nothing after them:
{"id": "<question id>", "verdict": "KEEP" | "KEY" | "UNSURE", "option": <1-based correct option, 0 if UNSURE>, \
"source": "<best URL>", "fact": "<one sentence stating the correct fact, usable as the explanation>"}
- KEEP: the given key is correct (option = the key's number).
- KEY: the given key is wrong or missing and "option" is correct, shown by the source.
- UNSURE: sources disagree, nothing reliable was found, or the question/options are garbled. Never guess."""


# Deep pass for what the first web check left UNSURE (or could not answer): fewer PYQs per request, more effort,
# more searches, and web fetch so the model can open official answer-key PDFs and primary sources.
WEB_FETCH = {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 4, "max_content_tokens": 20000}
DEEP_NOTE = """These questions were left UNSURE by a first, quick check. Dig deeper this time: open (web_fetch) the \
official answer-key PDF of the paper, or the primary source (bare act, census table, government page), rather than \
relying on search snippets. Decide whenever a reliable source supports one option. When reliable sources genuinely \
conflict, prefer: official key (or its official revision) > primary source > standard textbook (NCERT, Telugu \
Academy, Laxmikanth, Spectrum, Ramesh Singh) > the app's own notes, and say in "fact" which source you followed. Use \
UNSURE only when the question or options are garbled, or no reliable source exists at all.

"""


def paper(src):
    """Exam paper label for grouping: 'U.P.P.C.S. (Mains) 2017 +1 more' -> 'u p p c s mains 2017'."""
    return nc.norm(re.sub(r"\+\s*\d+\s*more", "", str(src)))


def tidy_rows(run):
    pyq = {q["id"]: q for ps in nc.pyqs_by_row("all").values() for q in ps}
    rows = [json.loads(l) for l in open(os.path.join(nc.OUT, run, "results.jsonl"))]
    for r in rows:
        r["final"] = nc.tidy(r, pyq.get(r["id"], {}))
    return rows, pyq


def prompt(q, r):
    opts = "\n".join(f"({i + 1}) {o}" for i, o in enumerate(q["o"]))
    a = q.get("a", -1)
    key = f"({a + 1}) {q['o'][a]}" if 0 <= a < len(q["o"]) else "none (the app has no key for this question)"
    note = {"CONFLICT": f"The app's own notes point to option ({r['option']}): {r['evidence']}",
            "NO_KEY": f"The app's notes suggest option ({r['option']})." if r["option"] else "",
            "NOT_COVERED": "The app's notes do not cover this question."}.get(r["final"], "")
    return (f"Exam: {q.get('src', 'unknown')}\nQuestion: {q['s']}\nOptions:\n{opts}\nGiven key: {key}\n"
            f"{note}\n\nCheck the key.")


def prompt_group(items):
    parts = []
    for i, (q, r) in enumerate(items, 1):
        body = prompt(q, r).replace("\n\nCheck the key.", "")
        parts.append(f"--- Question {i}, id={q['id']} ---\n{body}")
    return "\n\n".join(parts) + "\n\nCheck every key."


def build(args):
    rows, pyq = tidy_rows(args.source)
    want = set(args.verdicts.split(","))
    picked = [r for r in rows if r["final"] in want and r["id"] in pyq]
    if args.retry_from:  # deep pass: what web run <retry_from> left UNSURE or could not answer
        prev = os.path.join(OUT, args.retry_from)
        got = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(prev, "results.jsonl"))}
        failed = re.findall(r"^- `?([A-Za-z0-9_-]+)`?: no verdict", open(os.path.join(prev, "summary.md")).read(), re.M)
        ruled = {l.split(" | ")[0] for f in glob.glob(os.path.join(KEYS_OUT, "*.md"))
                 for l in open(f) if "owner review" in l}  # questions the owner already decided by hand
        out_file = os.path.join(ROOT, "data/keys/out", os.path.basename(open(os.path.join(prev, "keys_out_file.txt")).read().strip()))
        unsure = [l.split(" | ")[0] for l in open(out_file) if " | UNSURE | " in l]  # incl. KEY lines without a source
        redo = unsure + [i for i in failed if i not in got]
        redo = [i for i in dict.fromkeys(redo) if i not in ruled]
        by_id = {r["id"]: r for r in rows}
        picked = [by_id.get(i, {"id": i, "final": "NOT_COVERED", "option": 0, "evidence": ""}) for i in redo
                  if i in pyq]
        want = {r["final"] for r in picked}
    if args.include_missing:  # exam PYQs the notes run returned no verdict for: treat as NOT_COVERED
        seen = {r["id"] for r in rows}
        picked += [{"id": q["id"], "final": "NOT_COVERED", "option": 0, "evidence": ""}
                   for ps in nc.pyqs_by_row("exam").values() for q in ps if q["id"] not in seen]
    if args.sample:
        random.seed(args.seed)
        picked = random.sample(picked, min(args.sample, len(picked)))
    d = os.path.join(OUT, args.run)
    os.makedirs(d, exist_ok=True)
    n_req = 0
    with open(os.path.join(d, "requests.jsonl"), "w") as f:
        if args.group <= 1:
            for r in picked:
                params = {"model": MODEL, "max_tokens": 16000, "output_config": {"effort": EFFORT},
                          "system": SYSTEM, "tools": [WEB_SEARCH],
                          "messages": [{"role": "user", "content": prompt(pyq[r["id"]], r)}]}
                f.write(json.dumps({"custom_id": r["id"], "params": params, "ids": [r["id"]],
                                    "notes_verdict": {r["id"]: r["final"]}}, ensure_ascii=False) + "\n")
                n_req += 1
        else:
            # same paper together; leftovers of small papers are packed with others of the same exam board
            by_paper = {}
            for r in picked:
                by_paper.setdefault(paper(pyq[r["id"]].get("src", "")), []).append(r)
            chunks, rest = [], []
            for k in sorted(by_paper):
                rs = by_paper[k]
                full = len(rs) - len(rs) % args.group if len(rs) >= args.group else 0
                chunks += [rs[i:i + args.group] for i in range(0, full, args.group)]
                rest += rs[full:]
            rest.sort(key=lambda r: paper(pyq[r["id"]].get("src", "")))
            chunks += [rest[i:i + args.group] for i in range(0, len(rest), args.group)]
            for i, ch in enumerate(chunks):
                tool = dict(WEB_SEARCH, max_uses=min(2 + len(ch), 10))
                system, effort, tools = SYSTEM_GROUP, EFFORT, [tool]
                if args.retry_from:
                    system = DEEP_NOTE + SYSTEM_GROUP
                    effort, tools = "high", [dict(WEB_SEARCH, max_uses=min(4 + 2 * len(ch), 12)), WEB_FETCH]
                params = {"model": MODEL, "max_tokens": 32000, "output_config": {"effort": effort},
                          "system": system, "tools": tools,
                          "messages": [{"role": "user", "content": prompt_group([(pyq[r["id"]], r) for r in ch])}]}
                f.write(json.dumps({"custom_id": f"g{i}", "params": params, "ids": [r["id"] for r in ch],
                                    "notes_verdict": {r["id"]: r["final"] for r in ch}}, ensure_ascii=False) + "\n")
                n_req += 1
    by = {v: sum(r["final"] == v for r in picked) for v in sorted(want)}
    print(f"{args.run}: {len(picked)} PYQs {by} in {n_req} requests -> {d}/requests.jsonl")


def submit_file(c, d, name, out_name):
    reqs = [json.loads(l) for l in open(os.path.join(d, name))]
    ids = []
    for i in range(0, len(reqs), 10000):
        part = reqs[i:i + 10000]
        b = c.messages.batches.create(requests=[{"custom_id": r["custom_id"], "params": r["params"]} for r in part])
        ids.append(b.id)
        print(f"batch {b.id}: {len(part)} requests, {b.processing_status}")
    path = os.path.join(d, out_name)
    old = json.load(open(path))["batches"] if os.path.exists(path) else []
    json.dump({"batches": old + ids}, open(path, "w"))


def submit(args):
    submit_file(nc.client(), os.path.join(OUT, args.run), "requests.jsonl", "batches.json")


def resume(args):
    d = os.path.join(OUT, args.run)
    if not os.path.exists(os.path.join(d, "paused.jsonl")):
        sys.exit("nothing paused")
    submit_file(nc.client(), d, "paused.jsonl", "batches.json")


def status(args):
    c = nc.client()
    for bid in json.load(open(os.path.join(OUT, args.run, "batches.json")))["batches"]:
        b = c.messages.batches.retrieve(bid)
        print(bid, b.processing_status, b.request_counts)


def parse_all(text):
    out = []
    for m in re.finditer(r"\{[^{}]*\"verdict\"[^{}]*\}", text):
        try:
            x = json.loads(m.group(0))
        except ValueError:
            continue
        if x.get("verdict") in ("KEEP", "KEY", "UNSURE"):
            out.append(x)
    return out


def parse(text):
    xs = parse_all(text)
    return xs[-1] if xs else None


def collect(args):
    d = os.path.join(OUT, args.run)
    reqs = {json.loads(l)["custom_id"]: json.loads(l) for l in open(os.path.join(d, "requests.jsonl"))}
    pyq = {q["id"]: q for ps in nc.pyqs_by_row("all").values() for q in ps}
    c = nc.client()
    done, paused, failed = {}, [], []
    tok_in = tok_out = searches = 0
    for bid in json.load(open(os.path.join(d, "batches.json")))["batches"]:  # later batches (resumes) win
        if c.messages.batches.retrieve(bid).processing_status != "ended":
            sys.exit(f"batch {bid} has not ended yet")
        for res in c.messages.batches.results(bid):
            cid = res.custom_id
            if res.result.type != "succeeded":
                failed.append((cid, res.result.type))
                continue
            msg = res.result.message
            u = msg.usage
            tok_in += (u.input_tokens or 0) + (getattr(u, "cache_read_input_tokens", 0) or 0) + \
                      (getattr(u, "cache_creation_input_tokens", 0) or 0)
            tok_out += u.output_tokens or 0
            stu = getattr(u, "server_tool_use", None)
            searches += (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
            if msg.stop_reason == "pause_turn":
                p = json.loads(json.dumps(reqs[cid]["params"]))
                p["messages"] = p["messages"] + [{"role": "assistant",
                                                  "content": [b.to_dict() for b in msg.content]}]
                paused.append({"custom_id": cid, "params": p})
                continue
            text = "".join(b.text for b in msg.content if b.type == "text")
            ids = reqs[cid].get("ids", [cid])
            nv = reqs[cid]["notes_verdict"]
            xs = parse_all(text)
            if len(ids) == 1 and xs:
                got = {ids[0]: xs[-1]}
            else:
                got = {str(x.get("id")): x for x in xs}
            for qid in ids:
                x = got.get(qid)
                if not x:
                    failed.append((qid, f"no verdict line in {cid} (stop_reason={msg.stop_reason})"))
                    continue
                x = {k: v for k, v in x.items() if k != "id"}
                done[qid] = {"id": qid, "notes_verdict": nv.get(qid) if isinstance(nv, dict) else nv, **x}
    # a turn that paused in an earlier batch and finished in a resume batch counts as done
    paused = [x for x in paused if not all(i in done for i in reqs[x["custom_id"]].get("ids", [x["custom_id"]]))]
    failed = [x for x in failed if x[0] not in done]
    with open(os.path.join(d, "results.jsonl"), "w") as f:
        for r in done.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(d, "paused.jsonl"), "w") as f:
        for p in paused:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # keys_apply.py format, one line per PYQ: KEEP | KEY n | url | fact | UNSURE
    lines = []
    for r in done.values():
        q = pyq.get(r["id"], {})
        a, o = q.get("a", -1), r.get("option") or 0
        fact = str(r.get("fact", "")).replace("|", "/").replace("\n", " ").strip()
        src = str(r.get("source", "")).replace("|", "/").strip()
        if r["verdict"] == "KEY" and 1 <= o <= len(q.get("o", [])) and o != a + 1 and src and fact:
            lines.append(f"{r['id']} | KEY {o} | {src} | {fact}")
        elif r["verdict"] in ("KEEP", "KEY") and o == a + 1:
            lines.append(f"{r['id']} | KEEP | {fact}")
        else:
            lines.append(f"{r['id']} | UNSURE | {fact or 'sources did not settle it'}")
    os.makedirs(KEYS_OUT, exist_ok=True)
    marker = os.path.join(d, "keys_out_file.txt")
    if os.path.exists(marker):
        out_file = open(marker).read().strip()
    else:
        nums = [int(re.findall(r"\d+", os.path.basename(p))[-1]) for p in glob.glob(os.path.join(KEYS_OUT, "*.md"))]
        out_file = os.path.join(KEYS_OUT, f"{max(nums + [0]) + 1}.md")
        open(marker, "w").write(out_file)
    open(out_file, "w").write("\n".join(lines) + "\n")

    cost = tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT + searches * PRICE_SEARCH
    n = len(done)
    kinds = {k: sum(l.split(" | ")[1].startswith(k) for l in lines) for k in ("KEEP", "KEY", "UNSURE")}
    out = [f"# PYQ web check: {args.run}", "",
           f"Model {MODEL}, effort {EFFORT}, web search (max {MAX_SEARCHES}), Message Batches API. {n} PYQs decided, "
           f"{len(paused)} paused mid-search (run resume), {len(failed)} failures.", "",
           "| Decision | PYQs |", "|---|---|"] + [f"| {k} | {v} |" for k, v in kinds.items()]
    out += ["", f"Tokens: input {tok_in:,}, output {tok_out:,}; web searches {searches:,}.",
            f"Cost: ${cost:.2f} (${cost / max(n, 1) * 100:.2f} per 100 PYQs).",
            f"keys_apply.py file: {os.path.relpath(out_file, ROOT)}", ""]
    if failed:
        out += ["## Failures", ""] + [f"- {cid}: {why}" for cid, why in failed] + [""]
    out += ["## Key changes", ""]
    for l in lines:
        p = l.split(" | ")
        if not p[1].startswith("KEY"):
            continue
        q = pyq.get(p[0], {})
        a, n2 = q.get("a", -1), int(p[1].split()[1])
        old = f"({a + 1}) {q['o'][a]}" if 0 <= a < len(q["o"]) else "none"
        out.append(f"- `{p[0]}` [{q.get('src', '')}] {q.get('s', '')}\n  {old} → ({n2}) {q['o'][n2 - 1]}. "
                   f"{p[3]} ({p[2]})")
    open(os.path.join(d, "summary.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out[:12]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--run", required=True)
    b.add_argument("--from", dest="source", required=True, help="pyq_notes_check run to take verdicts from")
    b.add_argument("--verdicts", default="CONFLICT,NO_KEY,NOT_COVERED")
    b.add_argument("--sample", type=int, default=0)
    b.add_argument("--seed", type=int, default=7)
    b.add_argument("--retry-from", help="deep pass on what this web run left UNSURE or unanswered "
                                        "(use with --group 4)")
    b.add_argument("--include-missing", action="store_true",
                   help="also check exam PYQs the notes run gave no verdict for")
    b.add_argument("--group", type=int, default=8, help="PYQs per request, same exam paper together (1 = one each)")
    for name in ("submit", "status", "collect", "resume"):
        sub.add_parser(name).add_argument("--run", required=True)
    a = p.parse_args()
    {"build": build, "submit": submit, "status": status, "collect": collect, "resume": resume}[a.cmd](a)


if __name__ == "__main__":
    main()
