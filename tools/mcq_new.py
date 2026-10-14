"""Write MCQs for the important facts no bank MCQ tests (work/mcqgap/untested.txt).

    python3 tools/mcq_new.py export [facts per batch=22]   -> work/mcqnew/in_NNN.md
    python3 tools/mcq_new.py check [NNN]
    python3 tools/mcq_new.py apply                          -> files the new MCQs under their page

An agent answers in work/mcqnew/out_NNN.jsonl (tools/mcq_new_guide.md): one line per fact,
    {"fact":"F3","s":"stem","o":["A","B","C","D"],"a":1,"x":"why","tq":"tip"}
and a last line {"done":N} with N = the number of facts in the batch.
"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks
from mcq_cut_export import question

A = "app/src/main/assets"
D = "work/mcqnew"
LINE = re.compile(r"book (\d+) row (\d+) sub (-?\d+): (.*)")


def qid(stem, options):
    norm = lambda t: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


def load(b):
    notes = json.load(open(f"{A}/book{b}.json"))
    return [r for u in notes["units"] for r in u["rows"]], json.load(open(f"{A}/mcq{b}.json"))


def pages():
    """[(book,row,sub,[facts])] in file order."""
    out = {}
    for l in open("work/mcqgap/untested.txt"):
        m = LINE.match(l.strip())
        if m:
            out.setdefault(tuple(map(int, m.groups()[:3])), []).append(m.group(4))
    return [(*k, v) for k, v in out.items()]


def export(per=22):
    os.makedirs(D, exist_ok=True)
    for f in os.listdir(D):
        if f.startswith("in_"):
            os.remove(f"{D}/{f}")
    facts, batch, n, count, cache = {}, [], 0, 0, {}
    def flush():
        nonlocal batch, n, count
        if batch:
            open(f"{D}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
            n, batch, count = n + 1, [], 0
    for b, r, s, fs in pages():
        if b not in cache:
            cache[b] = load(b)
        rows, mcq = cache[b]
        row, sec = rows[r], rows[r]["secs"][s]
        md, _ = from_blocks(sec["b"], inline_tables=True)
        qs, subs = mcq["rows"].get(str(r), []), mcq["subs"].get(str(r), [])
        have = [question(q["id"], q) for q, k in zip(qs, subs) if k == s]
        labels = []
        for f in fs:
            lab = f"B{b}R{r}S{s}F{len(labels) + 1}"
            facts[lab] = {"book": b, "row": r, "sub": s, "f": f}
            labels.append(f"[{lab}] {f}")
        if batch and count + len(fs) > per:
            flush()
        batch.append(f"=== BOOK {b} ROW {r} SUB {s} | {row['title']} > {sec['t']}\n--- notes ---\n{md}\n"
                     f"--- MCQs already on this page ({len(have)}) ---\n" + "\n\n".join(have) +
                     "\n--- FACTS TO TEST ---\n" + "\n".join(labels))
        count += len(fs)
    flush()
    json.dump(facts, open(f"{D}/facts.json", "w"), ensure_ascii=False)
    print(f"{n} batches, {len(facts)} facts")


def batch_facts(n):
    return re.findall(r"^\[(B\d+R\d+S-?\d+F\d+)\] ", open(f"{D}/in_{n}.md").read(), re.M)


def check(n):
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], []
    want, errs, got, done = set(batch_facts(n)), [], [], None
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            errs.append(f"line {ln}: bad JSON ({e})"); continue
        if "done" in o:
            done = o["done"]; continue
        f = o.get("fact")
        if f not in want:
            errs.append(f"line {ln}: {f} is not a fact of this batch")
        if o.get("skip"):
            if not str(o["skip"]).strip():
                errs.append(f"line {ln}: skip needs a reason")
            continue
        opts = o.get("o")
        if not str(o.get("s", "")).strip():
            errs.append(f"line {ln}: empty stem")
        if not isinstance(opts, list) or len(opts) != 4 or len({x.strip().lower() for x in opts}) != 4 or not all(x.strip() for x in opts):
            errs.append(f"line {ln}: needs 4 distinct non-empty options")
        if o.get("a") not in (0, 1, 2, 3):
            errs.append(f"line {ln}: a must be 0-3")
        if not str(o.get("x", "")).strip():
            errs.append(f"line {ln}: needs x")
        got.append(o)
    if done != len(want):
        errs.append(f"last line must be {{\"done\":{len(want)}}}; got {done}")
    return errs, got


def apply():
    facts = json.load(open(f"{D}/facts.json"))
    index = json.load(open(f"{A}/index.json"))
    cache, total, left = {}, 0, []
    covered = set()
    for f in sorted(os.listdir(D)):
        if not f.startswith("out_"):
            continue
        n = f[4:7]
        errs, got = check(n)
        if errs:
            print(f"skip {n}: does not pass"); continue
        for o in got:
            fc = facts[o["fact"]]
            b, r, si = fc["book"], str(fc["row"]), fc["sub"]
            if b not in cache:
                cache[b] = load(b)
            mcq = cache[b][1]
            qs, subs = mcq["rows"].setdefault(r, []), mcq["subs"].setdefault(r, [])
            q = {"id": qid(o["s"], o["o"]), "s": o["s"].strip(), "o": [x.strip() for x in o["o"]],
                 "a": o["a"], "x": o["x"].strip(), "tq": str(o.get("tq", "")).strip()}
            if q["id"] in {x["id"] for x in qs}:
                continue
            at = max((j + 1 for j, k in enumerate(subs) if k <= si), default=0)
            qs.insert(at, q); subs.insert(at, si)
            covered.add(o["fact"]); total += 1
    for b, (rows, mcq) in cache.items():
        for ri, row in enumerate(index["books"][b - 1]["rows"]):
            row["q"] = len(mcq["rows"].get(str(ri), []))
        open(f"{A}/mcq{b}.json", "w").write(json.dumps(mcq, ensure_ascii=False, separators=(",", ":")))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    left = [f"book {v['book']} row {v['row']} sub {v['sub']}: {v['f']}" for k, v in facts.items() if k not in covered]
    open(f"{D}/still_untested.txt", "w").write("\n".join(left) + "\n")
    print(f"added {total} MCQs; {len(left)} facts still untested ({D}/still_untested.txt)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(*map(int, sys.argv[2:]))
    elif cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, got = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1; print(f"{n}: pass, {len(got)} MCQs")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "apply":
        apply()
