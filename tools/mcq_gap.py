"""Gap fill for pages with notes but few MCQs (2.48).

    python3 tools/mcq_gap.py export [min_words=40] [max_mcqs=2] [pages per batch=25]
        writes work/mcqgap/in_NNN.md: each page's notes and the MCQs already filed under it
    python3 tools/mcq_gap.py check [NNN]
    python3 tools/mcq_gap.py apply
        adds every passing batch's new MCQs after the page's own MCQs; updates index.json counts

An agent answers in work/mcqgap/out_NNN.jsonl, one line per page:
    {"book":2,"row":70,"sub":4,"facts":[{"f":"...","by":["Q70.3"]}],"new":[{"s":..,"o":[4],"a":0,"x":..,"tq":..}]}
facts[].by names an existing MCQ label of the page or "newK" (K = index in new, from 0).
"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from collections import Counter
from structured_md import from_blocks
from notes_fix import text
from mcq_cut_export import question

A = "app/src/main/assets"
D = "work/mcqgap"


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def qid(stem, options):  # as tools/mcq_cut_import.py
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


def load(b):
    notes = json.load(open(f"{A}/book{b}.json"))
    return [r for u in notes["units"] for r in u["rows"]], json.load(open(f"{A}/mcq{b}.json"))


def export(min_words=40, max_mcqs=2, per=25):
    os.makedirs(D, exist_ok=True)
    for f in os.listdir(D):
        if f.startswith("in_"):
            os.remove(f"{D}/{f}")
    pages = []
    for b in range(1, 7):
        rows, mcq = load(b)
        for ri, r in enumerate(rows):
            subs, qs = mcq["subs"].get(str(ri), []), mcq["rows"].get(str(ri), [])
            c = Counter(subs)
            for si, s in enumerate(r["secs"]):
                if len(" ".join(text(x) for x in s["b"]).split()) < min_words or c[si] > max_mcqs:
                    continue
                md, _ = from_blocks(s["b"], inline_tables=True)
                js = [j for j, k in enumerate(subs) if k == si]
                part = [f"=== BOOK {b} ROW {ri} SUB {si} | {r['title']} > {s['t']}", "--- notes ---", md,
                        f"--- MCQs already on this page ({len(js)}) ---"]
                part += [question(f"Q{ri}.{j}", qs[j]) for j in js]
                pages.append("\n".join(part))
    for n in range(0, len(pages), per):
        open(f"{D}/in_{n // per:03d}.md", "w").write("\n\n".join(pages[n:n + per]) + "\n")
    print(f"{len(pages)} pages, {(len(pages) + per - 1) // per} batches")


def pages_of(n):
    out = {}
    for line in open(f"{D}/in_{n}.md"):
        m = re.match(r"=== BOOK (\d) ROW (\d+) SUB (\d+) \|", line)
        if m:
            key = tuple(map(int, m.groups()))
            out[key] = []
        m = re.match(r"\[(Q\d+\.\d+)\]", line)
        if m:
            out[key].append(m.group(1))
    return out


def ok_new(q):
    o = q.get("o")
    return (str(q.get("s", "")).strip() and str(q.get("x", "")).strip() and isinstance(o, list) and len(o) == 4
            and len({str(x).strip().lower() for x in o}) == 4 and all(str(x).strip() for x in o)
            and q.get("a") in (0, 1, 2, 3))


def check(n):
    pg, errs, done, new = pages_of(n), [], set(), 0
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], 0
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
            key = (int(o["book"]), int(o["row"]), int(o["sub"]))
        except Exception as e:
            errs.append(f"line {ln}: bad line ({e})")
            continue
        if key not in pg:
            errs.append(f"line {ln}: page {key} not in batch")
            continue
        if key in done:
            errs.append(f"line {ln}: page {key} twice")
        done.add(key)
        news = o.get("new", [])
        for q in news:
            if not ok_new(q):
                errs.append(f"line {ln}: new MCQ needs stem, 4 distinct options, answer 0-3, why")
        ids = set(pg[key]) | {f"new{i}" for i in range(len(news))}
        if not o.get("facts"):
            errs.append(f"line {ln}: page {key} lists no facts")
        for f in o.get("facts", []):
            if not f.get("by") or not set(f["by"]) <= ids:
                errs.append(f"line {ln}: fact not covered by this page's MCQ or a new one: {str(f.get('f'))[:50]}")
        new += len(news)
    miss = [k for k in pg if k not in done]
    if miss:
        errs.append(f"{len(miss)} pages without a line: {miss[:6]}")
    return errs, new


def apply():
    adds = {}
    for f in sorted(os.listdir(D)):
        if f.startswith("out_"):
            n = f[4:7]
            if check(n)[0]:
                print(f"skip {n}")
                continue
            for line in open(f"{D}/{f}"):
                if line.strip():
                    o = json.loads(line)
                    adds.setdefault(o["book"], []).append(o)
    index = json.load(open(f"{A}/index.json"))
    total = 0
    for b, items in adds.items():
        rows, mcq = load(b)
        for o in items:
            r, si = str(o["row"]), o["sub"]
            qs, subs = mcq["rows"].setdefault(r, []), mcq["subs"].setdefault(r, [])
            have = {q["id"] for q in qs}
            at = max((j + 1 for j, k in enumerate(subs) if k <= si), default=0)
            for q in o.get("new", []):
                m = {"id": qid(q["s"], q["o"]), "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"], "tq": q.get("tq", "")}
                if m["id"] in have:
                    continue
                qs.insert(at, m)
                subs.insert(at, si)
                at += 1
                total += 1
        for ri, row in enumerate(index["books"][b - 1]["rows"]):
            row["q"] = len(mcq["rows"].get(str(ri), []))
        open(f"{A}/mcq{b}.json", "w").write(json.dumps(mcq, ensure_ascii=False, separators=(",", ":")))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    print(f"added {total} MCQs")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(*map(int, sys.argv[2:]))
    elif cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, new = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1
                print(f"{n}: pass, {new} new")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "apply":
        apply()
