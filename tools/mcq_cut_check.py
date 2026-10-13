"""Checks MCQ coverage answers: python3 tools/mcq_cut_check.py <book> [NNN]

One line per page; every MCQ label of the page decided once (keep / move / drop with a reason); moves stay in
the topic; new MCQs well formed; every listed fact covered by a kept, moved or new MCQ.
"""
import json, os, re, sys

book = int(sys.argv[1])
only = sys.argv[2] if len(sys.argv) > 2 else None
d = f"work/mcqcut/b{book}"
notes = json.load(open(f"app/src/main/assets/book{book}.json"))
nsecs = [len(r["secs"]) for u in notes["units"] for r in u["rows"]]


def pages(src):
    """{(row, sub): [labels]} for every page in the batch."""
    out, cur, row = {}, None, None
    for line in src.split("\n"):
        m = re.match(r"=== ROW (\d+) \|", line)
        if m:
            row = int(m.group(1))
            continue
        m = re.match(r"## SUB (-?\d+) \|", line)
        if m:
            cur = (row, int(m.group(1)))
            out[cur] = []
            continue
        m = re.match(r"\[(Q\d+\.\d+)\]", line)
        if m and cur:
            out[cur].append(m.group(1))
    return out


def new_ok(q):
    o = q.get("o")
    return (str(q.get("s", "")).strip() and str(q.get("x", "")).strip() and isinstance(o, list) and len(o) == 4
            and len({str(x).strip().lower() for x in o}) == 4 and all(str(x).strip() for x in o)
            and q.get("a") in (0, 1, 2, 3))


def check(n):
    pg = pages(open(f"{d}/in_{n}.md").read())
    path = f"{d}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], None
    errs, seen, done = [], set(), set()
    kept = new = 0
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
            key = (int(o["row"]), int(o["sub"]))
        except Exception as e:
            errs.append(f"line {ln}: bad line ({e})")
            continue
        if key not in pg:
            errs.append(f"line {ln}: no page ROW {key[0]} SUB {key[1]} in this batch")
            continue
        if key in done:
            errs.append(f"line {ln}: page ROW {key[0]} SUB {key[1]} twice")
        done.add(key)
        labels = pg[key]
        keep, move, drop, news = o.get("keep", []), o.get("move", {}), o.get("drop", {}), o.get("new", [])
        decided = list(keep) + list(move) + list(drop)
        for q in decided:
            if q not in labels:
                errs.append(f"line {ln}: {q} is not on ROW {key[0]} SUB {key[1]}")
            elif q in seen:
                errs.append(f"line {ln}: {q} decided twice")
            seen.add(q)
        for q in labels:
            if q not in decided:
                errs.append(f"line {ln}: {q} not decided")
        for q, k in move.items():
            if not isinstance(k, int) or not -1 <= k < nsecs[key[0]]:
                errs.append(f"line {ln}: {q} moved to bad page {k}")
        for q, why in drop.items():
            if not re.match(r"(dup Q\d+\.\d+|off|trivia)\b", str(why)):
                errs.append(f"line {ln}: {q} drop reason must be 'dup Qr.n', 'off' or 'trivia'")
        ids = set()
        for q in news:
            if not new_ok(q):
                errs.append(f"line {ln}: new MCQ {q.get('id')} needs stem, 4 distinct options, answer 0-3, why")
            ids.add(q.get("id"))
        covered = set(keep) | set(move) | ids
        for f in o.get("facts", []):
            if not f.get("by") or not set(f["by"]) <= covered:
                errs.append(f"line {ln}: fact not covered by a kept/new MCQ: {str(f.get('f'))[:50]}")
        kept += len(keep) + len(move)
        new += len(news)
    missing = [k for k in pg if k not in done]
    if missing:
        errs.append(f"{len(missing)} pages without a line: " + ", ".join(f"ROW {r} SUB {s}" for r, s in missing[:8]))
    return errs, (sum(len(v) for v in pg.values()), kept, new)


if __name__ == "__main__":
    ns = [only] if only else sorted(f[3:6] for f in os.listdir(d) if f.startswith("in_"))
    ok = ti = tk = tn = 0
    for n in ns:
        errs, c = check(n)
        if c:
            ti, tk, tn = ti + c[0], tk + c[1], tn + c[2]
        if errs:
            print(f"{n}: FAIL", *errs[:15], sep="\n  ")
        else:
            ok += 1
            if only:
                print(f"{n}: pass, {c[0]} MCQs -> {c[1]} kept + {c[2]} new")
    print(f"{ok}/{len(ns)} batches pass" + (f"; {ti} MCQs -> {tk} kept + {tn} new" if ti else ""))
