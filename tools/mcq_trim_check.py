"""Checks MCQ trim answers: python3 tools/mcq_trim_check.py <book> [NNN]

Every question label of in_NNN.md must be decided exactly once in out_NNN.jsonl (keep / drop / one
merge's "from"); merges need 4 distinct options, an answer 0-3 and an explanation; subsections must exist.
"""
import json, os, re, sys
A = os.environ.get("TRIM_ASSETS", "app/src/main/assets")  # APPSC Complete: app/src/complete/assets
W = os.environ.get("TRIM_DIR", "work/mcqtrim")

book = int(sys.argv[1])
only = sys.argv[2] if len(sys.argv) > 2 else None
d = f"{W}/b{book}"
notes = json.load(open(f"{A}/book{book}.json"))
nsecs = [len(r["secs"]) for u in notes["units"] for r in u["rows"]]


def check(n):
    src = open(f"{d}/in_{n}.md").read()
    labels = re.findall(r"^\[(Q\d+\.\d+)\]", src, re.M)
    path = f"{d}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], None
    errs, seen = [], {}
    kept = drops = merges = 0
    for ln, line in enumerate(open(path), 1):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            errs.append(f"line {ln}: bad JSON ({e})")
            continue
        dd = o.get("d")
        names = o.get("from", []) if dd == "merge" else [o.get("q")]
        for q in names:
            if q not in labels:
                errs.append(f"line {ln}: unknown label {q}")
            elif q in seen:
                errs.append(f"line {ln}: {q} decided twice (also line {seen[q]})")
            else:
                seen[q] = ln
        rows = {int(q[1:].split(".")[0]) for q in names if q}
        if "sub" in o:
            if len(rows) != 1 or not isinstance(o["sub"], int) or not -1 <= o["sub"] < nsecs[next(iter(rows))]:
                errs.append(f"line {ln}: bad sub {o.get('sub')}")
        if dd == "keep":
            kept += 1
        elif dd == "drop":
            drops += 1
            if not str(o.get("why", "")).strip():
                errs.append(f"line {ln}: drop without why")
        elif dd == "merge":
            merges += 1
            opts = o.get("o")
            if len(names) < 2:
                errs.append(f"line {ln}: merge needs 2+ labels")
            if len(rows) != 1:
                errs.append(f"line {ln}: merge across topics")
            if "sub" not in o:
                errs.append(f"line {ln}: merge without sub")
            if not str(o.get("s", "")).strip() or not str(o.get("x", "")).strip():
                errs.append(f"line {ln}: merge without stem or explanation")
            if not isinstance(opts, list) or len(opts) != 4 or len({str(x).strip().lower() for x in opts}) != 4 or not all(str(x).strip() for x in opts):
                errs.append(f"line {ln}: merge needs 4 distinct options")
            if o.get("a") not in (0, 1, 2, 3):
                errs.append(f"line {ln}: merge answer must be 0-3")
        else:
            errs.append(f"line {ln}: unknown decision {dd}")
    missing = [q for q in labels if q not in seen]
    if missing:
        errs.append(f"{len(missing)} labels not decided: {' '.join(missing[:12])}")
    return errs, (len(labels), kept + merges)


ns = [only] if only else sorted(f[3:6] for f in os.listdir(d) if f.startswith("in_"))
ok = tot_in = tot_out = 0
for n in ns:
    errs, counts = check(n)
    if counts:
        tot_in += counts[0]
        tot_out += counts[1]
    if errs:
        print(f"{n}: FAIL", *errs[:15], sep="\n  ")
    else:
        ok += 1
        if only:
            print(f"{n}: pass, {counts[0]} -> {counts[1]} MCQs ({counts[1] * 100 // max(counts[0], 1)}%)")
print(f"{ok}/{len(ns)} batches pass" + (f"; {tot_in} -> {tot_out} MCQs" if tot_in else ""))
