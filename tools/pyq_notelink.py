"""Links each exam PYQ of APPSC Complete to the exact notes lines that state its answer, as tools/notelink.py does
for the app's own MCQs, and writes an explanation for PYQs that have none. With a link, the book icon's sheet reads
like a notes MCQ's: "The correct answer is (2) gold." + the explanation + "From your notes" with the lines marked.

Batch API: each request holds one topic's notes, every line numbered (row:sec:block[.tablerow], as notelink.py
show prints them), and up to 20 PYQs of that topic with their (already checked) key. The model returns per PYQ the
line refs that state the answer ([] when the notes lack the fact) and, for a PYQ with no explanation, a short one.

    python3 tools/pyq_notelink.py build --run links [--exclude-from data/keys/web_check/deep/requests.jsonl]
    python3 tools/pyq_notelink.py submit  --run links
    python3 tools/pyq_notelink.py status  --run links
    python3 tools/pyq_notelink.py collect --run links      # validates refs -> results.jsonl, summary.md
    python3 tools/pyq_notelink.py apply   --run links      # notelinks.json + missing explanations (APPSC Complete)

Files go to data/notelink/pyq_<run>/.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notelink as nl  # noqa: E402
import pyq_notes_check as nc  # noqa: E402
from structured_md import from_blocks  # noqa: E402
from notes_fix import rows_of  # noqa: E402

ROOT = nc.ROOT
A = os.path.join(ROOT, "app/src/complete/assets")
OUT = os.path.join(ROOT, "data/notelink")
MODEL = "claude-sonnet-5-5"
EFFORT = "medium"
PER_REQUEST = 20
PRICE_IN, PRICE_OUT = 1.00, 5.00  # Batch API, Sonnet 5.5

SYSTEM = """You link exam questions (PYQs) to the study notes of an APPSC exam-preparation app. Every notes line \
has a reference in square brackets, e.g. [14:0:3] or, for a table row, [14:0:5.2]. For each PYQ you get the \
question, its options and its correct answer (already verified: do not dispute it).

For every PYQ return:
- "lines": the references of the 1-3 notes lines that state the fact which makes the correct answer right (for a \
"NOT correct"/"wrong pair"/statement question, the line(s) that settle it). Use a table ROW reference (with .N), \
never a whole table. Return [] if no line states the needed fact; do not link a line that is merely on the topic.
- "x": only when the PYQ's current explanation is "(none)": one or two sentences saying why the correct answer is \
right (and, where useful, why the tempting wrong option is wrong), consistent with the linked lines. Otherwise "".

Copy references exactly as written. Return exactly one result per PYQ id, in order."""

SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "lines": {"type": "array", "items": {"type": "string"}},
                       "x": {"type": "string"}},
        "required": ["id", "lines", "x"], "additionalProperties": False}}},
    "required": ["results"], "additionalProperties": False,
}


def numbered(book_json, r):
    """The topic's notes with every line's reference, as notelink.py show prints them."""
    row = rows_of(book_json)[r]
    out = [f"TOPIC: {row['title']}"]
    for si, s in enumerate(row["secs"]):
        out.append(f"## {s['t']}")
        for bi, blk in enumerate(s["b"]):
            if blk.get("k") in nc.SKIP_KINDS:
                continue
            if blk["k"] == "t":
                out.append(f"TABLE ({' | '.join(nl.cell(h) for h in blk['h'])})")
                out += [f"[{r}:{si}:{bi}.{ti}] " + " | ".join(nl.cell(c) for c in tr) for ti, tr in enumerate(blk["r"])]
            else:
                out.append(f"[{r}:{si}:{bi}] {from_blocks([blk], inline_tables=True)[0]}")
    return "\n".join(out)


def build(args):
    skip = set()
    if args.exclude_from:
        for l in open(args.exclude_from):
            skip.update(json.loads(l).get("ids", []))
    links = json.load(open(os.path.join(A, "notelinks.json")))
    d = os.path.join(OUT, f"pyq_{args.run}")
    os.makedirs(d, exist_ok=True)
    n_req = n_q = chars = 0
    with open(os.path.join(d, "requests.jsonl"), "w") as f:
        for b in range(1, 7):
            bk = json.load(open(os.path.join(A, f"book{b}.json")))
            m = json.load(open(os.path.join(A, f"mcq{b}.json")))
            for ri, qs in sorted(m["rows"].items(), key=lambda kv: int(kv[0])):
                ps = [q for q in qs if isinstance(q, dict) and q.get("src") and q["src"] not in nc.APP_MADE
                      and q["id"] not in skip and q["id"] not in links and 0 <= q.get("a", -1) < len(q["o"])]
                if not ps:
                    continue
                notes = numbered(bk, int(ri))
                for c in range(0, len(ps), PER_REQUEST):
                    ch = ps[c:c + PER_REQUEST]
                    qtext = "\n\n".join(
                        f"{i + 1}. id={q['id']}\nQ: {q['s']}\nOptions: "
                        + "  ".join(f"({j + 1}) {o}" for j, o in enumerate(q["o"]))
                        + f"\nCorrect answer: ({q['a'] + 1}) {q['o'][q['a']]}\nCurrent explanation: "
                        + (q.get("x", "").strip() or "(none)")
                        for i, q in enumerate(ch))
                    params = {"model": MODEL, "max_tokens": 16000,
                              "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
                              "system": SYSTEM,
                              "messages": [{"role": "user", "content": f"NOTES\n\n{notes}\n\nPYQs ({len(ch)}):\n\n{qtext}"}]}
                    f.write(json.dumps({"custom_id": f"b{b}r{ri}c{c // PER_REQUEST}", "book": b, "params": params,
                                        "ids": [q["id"] for q in ch],
                                        "need_x": [q["id"] for q in ch if not q.get("x", "").strip()]},
                                       ensure_ascii=False) + "\n")
                    n_req += 1
                    n_q += len(ch)
                    chars += len(SYSTEM) + len(notes) + len(qtext)
    print(f"{args.run}: {n_q} PYQs in {n_req} requests, ~{chars / 3.6 / 1e6:.1f}M input tokens -> {d}/requests.jsonl")


def submit(args):
    d = os.path.join(OUT, f"pyq_{args.run}")
    reqs = [json.loads(l) for l in open(os.path.join(d, "requests.jsonl"))]
    c = nc.client()
    ids = []
    for i in range(0, len(reqs), 50000):
        b = c.messages.batches.create(requests=[{"custom_id": r["custom_id"], "params": r["params"]}
                                                for r in reqs[i:i + 50000]])
        ids.append(b.id)
        print(f"batch {b.id}: {len(reqs[i:i + 50000])} requests, {b.processing_status}")
    json.dump({"batches": ids}, open(os.path.join(d, "batches.json"), "w"))


def status(args):
    c = nc.client()
    for bid in json.load(open(os.path.join(OUT, f"pyq_{args.run}", "batches.json")))["batches"]:
        b = c.messages.batches.retrieve(bid)
        print(bid, b.processing_status, b.request_counts)


def collect(args):
    d = os.path.join(OUT, f"pyq_{args.run}")
    reqs = {json.loads(l)["custom_id"]: json.loads(l) for l in open(os.path.join(d, "requests.jsonl"))}
    books = {b: json.load(open(os.path.join(A, f"book{b}.json"))) for b in range(1, 7)}
    c = nc.client()
    rows, failed = [], []
    tin = tout = 0
    for bid in json.load(open(os.path.join(d, "batches.json")))["batches"]:
        if c.messages.batches.retrieve(bid).processing_status != "ended":
            sys.exit(f"batch {bid} has not ended yet")
        for res in c.messages.batches.results(bid):
            rq = reqs[res.custom_id]
            if res.result.type != "succeeded":
                failed.append((res.custom_id, res.result.type))
                continue
            msg = res.result.message
            tin += msg.usage.input_tokens or 0
            tout += msg.usage.output_tokens or 0
            try:
                got = {x["id"]: x for x in json.loads(next(b.text for b in msg.content if b.type == "text"))["results"]}
            except (ValueError, KeyError, StopIteration) as e:
                failed.append((res.custom_id, f"bad JSON ({msg.stop_reason}): {e}"))
                continue
            for qid in rq["ids"]:
                x = got.get(qid)
                if not x:
                    failed.append((res.custom_id, f"missing {qid}"))
                    continue
                good = [ref for ref in x["lines"] if nl.line_text(books[rq["book"]], ref) is not None][:3]
                bad = [ref for ref in x["lines"] if ref not in good]
                rows.append({"id": qid, "book": rq["book"], "lines": good, "bad": bad,
                             "x": x["x"].strip() if qid in rq["need_x"] else ""})
    with open(os.path.join(d, "results.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    cost = tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT
    linked = sum(bool(r["lines"]) for r in rows)
    need = sum(len(r["need_x"]) for r in reqs.values())
    got_x = sum(bool(r["x"]) for r in rows)
    out = [f"# PYQ notes links: {args.run}", "",
           f"{len(rows)} PYQs answered, {len(failed)} failures. Linked to notes lines: {linked} "
           f"({linked / max(len(rows), 1):.0%}); no line states the fact: {len(rows) - linked}. "
           f"Invalid refs dropped: {sum(len(r['bad']) for r in rows)}.",
           f"Explanations written for PYQs that had none: {got_x} of {need}.",
           f"Tokens: input {tin:,}, output {tout:,}. Cost (batch price): ${cost:.2f}.", ""]
    if failed:
        out += ["## Failures", ""] + [f"- {c_}: {w}" for c_, w in failed] + [""]
    open(os.path.join(d, "summary.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out[:6]))


def apply(args):
    d = os.path.join(OUT, f"pyq_{args.run}")
    rows = [json.loads(l) for l in open(os.path.join(d, "results.jsonl"))]
    path = os.path.join(A, "notelinks.json")
    cur = json.load(open(path))
    n_links = 0
    for r in rows:
        if r["lines"]:
            cur[r["id"]] = [f"{r['book']}:{ref}" for ref in r["lines"]]
            n_links += 1
    json.dump(cur, open(path, "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    xs = {r["id"]: r["x"] for r in rows if r["x"]}
    n_x = 0
    for b in range(1, 7):
        mp = os.path.join(A, f"mcq{b}.json")
        m = json.load(open(mp))
        hit = False
        for k in ("rows", "units"):
            for qs in m.get(k, {}).values():
                for q in qs:
                    if isinstance(q, dict) and q["id"] in xs and not q.get("x", "").strip():
                        q["x"] = xs[q["id"]]
                        hit = True
                        n_x += 1
        if hit:
            json.dump(m, open(mp, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"notelinks.json: {n_links} PYQs linked; explanations added: {n_x}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--run", required=True)
    b.add_argument("--exclude-from", help="a requests.jsonl whose PYQ ids to leave out (e.g. the deep web pass)")
    for name in ("submit", "status", "collect", "apply"):
        sub.add_parser(name).add_argument("--run", required=True)
    a = p.parse_args()
    {"build": build, "submit": submit, "status": status, "collect": collect, "apply": apply}[a.cmd](a)


if __name__ == "__main__":
    main()
