"""Checks every PYQ answer key in APPSC Complete against the app's own notes, with the Message Batches API.

Each request carries one topic's notes (APPSC Complete + the same topic in Prep, One-liner and Complete2; Group 2's
notes are a near copy of Complete's and are left out), the best-matching sections of the UPSC Prep and Rocket apps'
notes (other repos, picked by keyword search) and up to 20 PYQs filed under that topic. The model answers
per PYQ:  AGREE (notes support the key) | CONFLICT (notes point to another option) | NOT_COVERED (notes are silent).
Nothing in the app is changed: conflicts are reviewed later (web search / official keys) and applied with
tools/keys_apply.py.

    python3 tools/pyq_notes_check.py extract                 # UPSC Prep + Rocket notes -> extra_notes.jsonl
    python3 tools/pyq_notes_check.py crosscheck              # free: same PYQ, different key in another app's bank
    python3 tools/pyq_notes_check.py build --run pilot --sample 500      # --scope all adds app/ca/rocket MCQs
    python3 tools/pyq_notes_check.py build --run full
    python3 tools/pyq_notes_check.py submit --run pilot       # needs ANTHROPIC_API_KEY, KEY or key
    python3 tools/pyq_notes_check.py status --run pilot
    python3 tools/pyq_notes_check.py collect --run pilot      # results.jsonl, usage.json, summary.md
    python3 tools/pyq_notes_check.py summarize --run pilot    # rewrite summary.md from results.jsonl (no API)

Files go to data/keys/notes_check/<run>/.
"""
import argparse
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPLETE = os.path.join(ROOT, "app/src/complete/assets")
NOTE_APPS = [("APPSC Complete", "complete"), ("APPSC Prep", "main"), ("One-liner", "oneliner"), ("Complete2", "complete2")]
BANK_APPS = [("APPSC Prep", "main"), ("Group 2", "group2"), ("One-liner", "oneliner")]
OUT = os.path.join(ROOT, "data/keys/notes_check")
# Other repos' notes, organised by different topics: their sections are picked per request by keyword search.
EXTRA_SRC = [("UPSC Prep", "../upscprep/app/src/main/assets"),
             ("Rocket", "../richie505/groupsrocket/android/app/src/main/assets")]
EXTRA_FILE = os.path.join(OUT, "extra_notes.jsonl")  # extracted sections, committed so any session can build
EXTRA_CHARS = 11000  # ~3,000 tokens of the best-matching UPSC / Rocket sections per request

MODEL = "claude-sonnet-5-5"
EFFORT = "medium"
PER_REQUEST = 20
# Batch API = 50% of list price. Sonnet 5.5 list: input $2, output $10, cache write (5 min) $2.50, cache read $0.10 per MTok.
PRICE = {"input": 1.00, "output": 5.00, "cache_write": 1.25, "cache_read": 0.05}

SYSTEM = """You check the answer keys of previous-year exam questions (PYQs: APPSC, UPSC, other state PSCs, SSC) for an \
APPSC exam-preparation app. For each PYQ you get the question, its numbered options and the key the app currently \
gives. Judge the key ONLY against the study notes supplied in the message (several apps' notes on the same topic). \
Do not use outside knowledge to overrule the notes; if the notes do not settle it, say so.

For every PYQ return one result:
- AGREE: the notes clearly support the given key.
- CONFLICT: the notes clearly support a different option. Give that option's number in "option" and quote or closely \
paraphrase the deciding line of the notes in "evidence". Also use CONFLICT when the notes contradict each other on \
this exact point (option = what the stronger/more specific note says; say "notes disagree" in evidence).
- NOT_COVERED: the notes do not contain the fact needed, or the question is garbled/unanswerable as written \
(say which in evidence).

Rules: "option" is 1-based and 0 when there is no alternative option (AGREE / NOT_COVERED). CONFLICT means \
"option" differs from the given key's number: never return CONFLICT with the key's own option. If the given key is \
"none", return CONFLICT with the option the notes support (or NOT_COVERED). For "which is NOT \
correct", "wrong pair" and statement-combination questions, work out which option the notes make right before \
judging. Keep evidence under 30 words; leave it empty for AGREE. Return exactly one result per PYQ id, in order."""

SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["AGREE", "CONFLICT", "NOT_COVERED"]},
                    "option": {"type": "integer"},
                    "evidence": {"type": "string"},
                },
                "required": ["id", "verdict", "option", "evidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


# ---------- notes -> text ----------

def inline(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        if len(x) == 2 and isinstance(x[0], str) and isinstance(x[1], int):
            return x[0]
        return "".join(inline(i) for i in x)
    return ""


SKIP_KINDS = {"n", "V", "a"}  # app chrome: "no MCQs yet", "VERY IMPORTANT" badges, anchors


def block_lines(blk):
    k = blk.get("k")
    if k in SKIP_KINDS:
        return []
    if k == "t":
        out = [" | ".join(inline(c) for c in blk.get("h", []))]
        out += [" | ".join(inline(c) for c in row) for row in blk.get("r", [])]
        return [l for l in out if l.strip(" |")]
    t = inline(blk.get("x", "")).strip()
    if not t:
        return []
    return [("## " + t) if k == "h" else t]


def load_rows(app, book):
    try:
        bk = json.load(open(os.path.join(ROOT, f"app/src/{app}/assets/book{book}.json")))
    except FileNotFoundError:
        return []
    return [r for u in bk.get("units", []) for r in u.get("rows", [])]


def row_text(row):
    lines = []
    for s in row.get("secs", []):
        if s.get("t"):
            lines.append("# " + s["t"])
        for blk in s.get("b", []):
            lines += block_lines(blk)
    return lines


def topic_notes(book, idx, cache):
    """All apps' notes for Complete's topic row idx of book, duplicate lines dropped."""
    key = (book, idx)
    if key in cache:
        return cache[key]
    base = load_rows_cached("complete", book, cache)[idx]
    codes = tuple(base.get("codes") or [])
    seen, parts = set(), []
    for label, app in NOTE_APPS:
        rows = load_rows_cached(app, book, cache)
        match = [r for r in rows if tuple(r.get("codes") or []) == codes] if app != "complete" else [base]
        lines = []
        for r in match[:1]:
            for l in row_text(r):
                n = re.sub(r"\W+", " ", l.lower()).strip()
                if n and n not in seen:
                    seen.add(n)
                    lines.append(l)
        if lines:
            parts.append(f"=== {label} notes ===\n" + "\n".join(lines))
    text = f"TOPIC: {base.get('title', '')}\n\n" + "\n\n".join(parts)
    cache[key] = text
    return text


def load_rows_cached(app, book, cache):
    k = ("rows", app, book)
    if k not in cache:
        cache[k] = load_rows(app, book)
    return cache[k]


# ---------- UPSC Prep / Rocket notes: keyword retrieval ----------

STOP = set("the of and a an in to is was which for by on with as at from that this be are or it its were following "
           "who what when where not correct statement statements given below code select answer using none all above "
           "only both neither nor 1 2 3 4 i ii iii iv".split())


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP and len(w) > 1]


def extract(args):
    """Writes every section of the UPSC Prep and Rocket notes to extra_notes.jsonl."""
    n = 0
    with open(EXTRA_FILE, "w") as f:
        for label, rel in EXTRA_SRC:
            d = os.path.normpath(os.path.join(ROOT, rel))
            if not os.path.isdir(d):
                sys.exit(f"missing {d}: clone that repo next to Group-app first")
            for b in range(1, 10):
                try:
                    bk = json.load(open(os.path.join(d, f"book{b}.json")))
                except FileNotFoundError:
                    continue
                for u in bk.get("units", []):
                    for r in u.get("rows", []):
                        for sec in r.get("secs", []):
                            lines = []
                            for blk in sec.get("b", []):
                                lines += block_lines(blk)
                            if lines:
                                f.write(json.dumps({"app": label, "topic": r.get("title", ""), "t": sec.get("t", ""),
                                                    "text": "\n".join(lines)}, ensure_ascii=False) + "\n")
                                n += 1
    print(f"{n} sections -> {EXTRA_FILE}")


class Extra:
    """BM25 over the UPSC Prep / Rocket sections."""

    def __init__(self):
        import math
        self.docs = [json.loads(l) for l in open(EXTRA_FILE)] if os.path.exists(EXTRA_FILE) else []
        self.tf, self.df = [], {}
        for d in self.docs:
            ws = words(d["topic"] + " " + d["t"] + " " + d["text"])
            c = {}
            for w in ws:
                c[w] = c.get(w, 0) + 1
            self.tf.append((c, len(ws)))
            for w in c:
                self.df[w] = self.df.get(w, 0) + 1
        n = max(len(self.docs), 1)
        self.avg = sum(l for _, l in self.tf) / n
        self.idf = {w: math.log(1 + (n - k + 0.5) / (k + 0.5)) for w, k in self.df.items()}

    def best(self, query, limit=EXTRA_CHARS):
        if not self.docs:
            return ""
        q = set(words(query))
        scored = []
        for i, (c, ln) in enumerate(self.tf):
            sc = 0.0
            for w in q:
                f = c.get(w)
                if f:
                    sc += self.idf[w] * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * ln / self.avg))
            if sc > 0:
                scored.append((sc, i))
        scored.sort(reverse=True)
        out, used = {}, 0
        for sc, i in scored:
            d = self.docs[i]
            block = f"# {d['topic']} / {d['t']}\n{d['text']}"
            if used + len(block) > limit:
                if used:
                    continue
                block = block[:limit]
            out.setdefault(d["app"], []).append(block)
            used += len(block)
            if used >= limit * 0.95:
                break
        return "\n\n".join(f"=== {app} notes (best-matching sections) ===\n" + "\n\n".join(bl)
                           for app, bl in out.items())


# ---------- PYQs ----------

APP_MADE = {"app", "ca", "rocket"}  # src tags of app-written, current-affairs and Rocket-app MCQs (not exam PYQs)


def pyqs_by_row(scope="all"):
    """{(book, row_index): [pyq, ...]} for APPSC Complete MCQs with a src: scope "exam" = real exam PYQs only,
    "all" = also the app-written / current-affairs / Rocket MCQs."""
    out = {}
    for b in range(1, 7):
        m = json.load(open(os.path.join(COMPLETE, f"mcq{b}.json")))
        for ri, qs in m.get("rows", {}).items():
            ps = [q for q in qs if isinstance(q, dict) and q.get("src")
                  and (scope == "all" or q["src"] not in APP_MADE)]
            if ps:
                out[(b, int(ri))] = ps
    return out


def pyq_line(n, q):
    opts = "  ".join(f"({i + 1}) {o}" for i, o in enumerate(q["o"]))
    a = q.get("a", -1)
    key = f"({a + 1}) {q['o'][a]}" if 0 <= a < len(q["o"]) else "none"
    return f"{n}. id={q['id']}  [{q.get('src', '')}]\nQ: {q['s']}\nOptions: {opts}\nGiven key: {key}"


def build(args):
    random.seed(args.seed)
    rows = pyqs_by_row(args.scope)
    chunks = []
    for (b, ri), ps in sorted(rows.items()):
        for c in range(0, len(ps), PER_REQUEST):
            chunks.append((b, ri, c // PER_REQUEST, ps[c:c + PER_REQUEST]))
    if args.sample:
        random.shuffle(chunks)
        picked, n = [], 0
        for ch in chunks:
            if n >= args.sample:
                break
            picked.append(ch)
            n += len(ch[3])
        chunks = sorted(picked)
    cache = {}
    extra = Extra()
    if not extra.docs:
        print("note: no extra_notes.jsonl, building without UPSC Prep / Rocket notes")
    d = os.path.join(OUT, args.run)
    os.makedirs(d, exist_ok=True)
    n_pyq = chars = 0
    with open(os.path.join(d, "requests.jsonl"), "w") as f:
        for b, ri, c, ps in chunks:
            notes = topic_notes(b, ri, cache)
            qtext = "\n\n".join(pyq_line(i + 1, q) for i, q in enumerate(ps))
            more = extra.best(" ".join(q["s"] + " " + " ".join(map(str, q["o"])) for q in ps))
            params = {
                "model": MODEL,
                "max_tokens": 16000,
                "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
                "system": [{"type": "text", "text": SYSTEM}],
                "messages": [{"role": "user", "content": [
                    # no cache_control: batch requests rarely hit the cache (pilot: ~10%) and writes cost 1.25x
                    {"type": "text", "text": "STUDY NOTES\n\n" + notes},
                    {"type": "text", "text": (more + "\n\n" if more else "") + f"PYQs to check ({len(ps)}):\n\n" + qtext},
                ]}],
            }
            f.write(json.dumps({"custom_id": f"b{b}r{ri}c{c}", "params": params, "ids": [q["id"] for q in ps]},
                               ensure_ascii=False) + "\n")
            n_pyq += len(ps)
            chars += len(SYSTEM) + len(notes) + len(qtext) + len(more)
    est_in = chars / 3.6
    print(f"{args.run}: {len(chunks)} requests, {n_pyq} PYQs, ~{est_in / 1e6:.1f}M input tokens "
          f"(~${est_in / 1e6 * PRICE['input']:.0f} at batch price before caching) -> {d}/requests.jsonl")


# ---------- API ----------

def client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("KEY") or os.environ.get("key")
    if not key:
        sys.exit("No API key: set ANTHROPIC_API_KEY, KEY or key.")
    return anthropic.Anthropic(api_key=key)


def submit(args):
    d = os.path.join(OUT, args.run)
    reqs = [json.loads(l) for l in open(os.path.join(d, "requests.jsonl"))]
    c = client()
    ids = []
    for i in range(0, len(reqs), 50000):  # well under the 100,000-request / 256 MB batch limit
        part = reqs[i:i + 50000]
        batch = c.messages.batches.create(requests=[{"custom_id": r["custom_id"], "params": r["params"]} for r in part])
        ids.append(batch.id)
        print(f"batch {batch.id}: {len(part)} requests, {batch.processing_status}")
    json.dump({"batches": ids}, open(os.path.join(d, "batches.json"), "w"))


def status(args):
    d = os.path.join(OUT, args.run)
    c = client()
    for bid in json.load(open(os.path.join(d, "batches.json")))["batches"]:
        b = c.messages.batches.retrieve(bid)
        print(bid, b.processing_status, b.request_counts)


def collect(args):
    d = os.path.join(OUT, args.run)
    reqs = {}
    for l in open(os.path.join(d, "requests.jsonl")):
        r = json.loads(l)
        reqs[r["custom_id"]] = r
    pyq = {q["id"]: q for ps in pyqs_by_row().values() for q in ps}
    c = client()
    usage = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    rows, failed = [], []
    for bid in json.load(open(os.path.join(d, "batches.json")))["batches"]:
        if c.messages.batches.retrieve(bid).processing_status != "ended":
            sys.exit(f"batch {bid} has not ended yet")
        for res in c.messages.batches.results(bid):
            cid = res.custom_id
            if res.result.type != "succeeded":
                failed.append((cid, res.result.type))
                continue
            msg = res.result.message
            u = msg.usage
            usage["input"] += u.input_tokens or 0
            usage["output"] += u.output_tokens or 0
            usage["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
            usage["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
            if msg.stop_reason != "end_turn":
                failed.append((cid, f"stop_reason={msg.stop_reason}"))
                continue
            text = next((b.text for b in msg.content if b.type == "text"), "")
            try:
                got = {x["id"]: x for x in json.loads(text)["results"]}
            except (ValueError, KeyError) as e:
                failed.append((cid, f"bad JSON: {e}"))
                continue
            for qid in reqs[cid]["ids"]:
                x = got.get(qid)
                if not x:
                    failed.append((cid, f"missing {qid}"))
                    continue
                rows.append({"id": qid, "request": cid, **{k: x[k] for k in ("verdict", "option", "evidence")}})
    with open(os.path.join(d, "results.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"usage": usage, "failed": failed}, open(os.path.join(d, "usage.json"), "w"))
    summarize(args)


def tidy(r, q):
    """Fixes the model's own inconsistencies. CONFLICT naming the key's own option -> AGREE; CONFLICT with no
    option -> NOT_COVERED; a PYQ that has no key in the app -> NO_KEY (option = what the notes support)."""
    a = q.get("a", -1)
    has_key = 0 <= a < len(q.get("o", []))
    v, o = r["verdict"], r["option"]
    if not has_key:
        return "NO_KEY"
    if v == "CONFLICT" and o == a + 1:
        return "AGREE"
    if v == "CONFLICT" and not (1 <= o <= len(q["o"])):
        return "NOT_COVERED"
    return v


def summarize(args):
    """Rewrites summary.md from results.jsonl + usage.json (no API calls)."""
    d = os.path.join(OUT, args.run)
    pyq = {q["id"]: q for ps in pyqs_by_row("all").values() for q in ps}
    rows = [json.loads(l) for l in open(os.path.join(d, "results.jsonl"))]
    for r in rows:
        r["final"] = tidy(r, pyq.get(r["id"], {}))
    meta = json.load(open(os.path.join(d, "usage.json")))
    usage, failed = meta["usage"], meta["failed"]
    cost = sum(usage[k] / 1e6 * PRICE[k] for k in usage)
    n = len(rows)
    kinds = ("AGREE", "CONFLICT", "NOT_COVERED", "NO_KEY")
    counts = {v: sum(r["final"] == v for r in rows) for v in kinds}
    fixed = sum(r["final"] != r["verdict"] for r in rows)
    out = [f"# PYQ key check against the app notes: {args.run}", "",
           f"Model {MODEL}, effort {EFFORT}, Message Batches API. {n} PYQs answered, {len(failed)} failures. "
           f"{fixed} verdicts tidied (a CONFLICT naming the key's own option counts as AGREE; a PYQ with no key "
           f"in the app is NO_KEY).", "",
           "| Verdict | PYQs | Share |", "|---|---|---|"]
    out += [f"| {v} | {k} | {k / max(n, 1):.1%} |" for v, k in counts.items()]
    out += ["", f"Tokens: input {usage['input']:,}, cache write {usage['cache_write']:,}, "
                f"cache read {usage['cache_read']:,}, output {usage['output']:,}.",
            f"Cost (batch price): ${cost:.2f} = ${cost / max(n, 1) * 1000:.2f} per 1,000 PYQs; "
            f"per 25,076 exam PYQs: ${cost / max(n, 1) * 25076:.0f}.", ""]
    if failed:
        out += ["## Failures", ""] + [f"- {cid}: {why}" for cid, why in failed] + [""]

    def line(r):
        q = pyq.get(r["id"], {})
        o, a = q.get("o", []), q.get("a", -1)
        given = f"({a + 1}) {o[a]}" if 0 <= a < len(o) else "none"
        nt = f"({r['option']}) {o[r['option'] - 1]}" if 1 <= r["option"] <= len(o) else "-"
        return (f"- `{r['id']}` [{q.get('src', '')}] {q.get('s', '')}\n  key {given} → notes {nt}. "
                f"{r['evidence']}")

    for v, title in (("CONFLICT", "Conflicts: notes support another option"),
                     ("NO_KEY", "No key in the app"), ("NOT_COVERED", "Not covered by the notes")):
        out += [f"## {title}", ""] + [line(r) for r in rows if r["final"] == v] + [""]
    open(os.path.join(d, "summary.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out[:13]))
    print(f"-> {d}/summary.md")


# ---------- free cross-app key comparison ----------

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def crosscheck(args):
    def bank(app):
        out = {}
        for b in range(1, 7):
            try:
                m = json.load(open(os.path.join(ROOT, f"app/src/{app}/assets/mcq{b}.json")))
            except FileNotFoundError:
                continue
            stack = [m]
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    if "s" in x and "o" in x and "a" in x and isinstance(x["o"], list):
                        a = x["a"]
                        if isinstance(a, int) and 0 <= a < len(x["o"]):
                            out.setdefault((norm(x["s"]), tuple(sorted(norm(o) for o in x["o"]))),
                                           set()).add(norm(x["o"][a]))
                    else:
                        stack.extend(x.values())
                elif isinstance(x, list):
                    stack.extend(x)
        return out

    others = [(label, bank(app)) for label, app in BANK_APPS]
    d = os.path.join(OUT, "crosscheck")
    os.makedirs(d, exist_ok=True)
    found, checked = [], 0
    for ps in pyqs_by_row().values():
        for q in ps:
            a = q.get("a", -1)
            if not (0 <= a < len(q["o"])):
                continue
            k = (norm(q["s"]), tuple(sorted(norm(o) for o in q["o"])))
            mine = norm(q["o"][a])
            hit = False
            for label, bk in others:
                theirs = bk.get(k)
                if theirs is None:
                    continue
                hit = True
                if mine not in theirs:
                    other = sorted(theirs)[0]
                    oi = next((i for i, o in enumerate(q["o"]) if norm(o) == other), -1)
                    found.append({"id": q["id"], "app": label, "src": q.get("src", ""), "q": q["s"],
                                  "key": f"({a + 1}) {q['o'][a]}",
                                  "other_key": f"({oi + 1}) {q['o'][oi]}" if oi >= 0 else other})
            checked += hit
    with open(os.path.join(d, "mismatches.jsonl"), "w") as f:
        for r in found:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ids = {r["id"] for r in found}
    print(f"{checked} PYQs also found in another app's bank; {len(ids)} have a different key there "
          f"({len(found)} app pairs) -> {d}/mismatches.jsonl")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--run", required=True)
    b.add_argument("--sample", type=int, default=0, help="about this many PYQs, in whole topic chunks")
    b.add_argument("--seed", type=int, default=7)
    b.add_argument("--scope", choices=["exam", "all"], default="exam",
                   help="exam = real exam PYQs only (default); all = also app/ca/rocket MCQs")
    for name in ("submit", "status", "collect", "summarize"):
        sub.add_parser(name).add_argument("--run", required=True)
    sub.add_parser("crosscheck")
    sub.add_parser("extract")
    a = p.parse_args()
    {"build": build, "submit": submit, "status": status, "collect": collect, "summarize": summarize, "crosscheck": crosscheck, "extract": extract}[a.cmd](a)


if __name__ == "__main__":
    main()
