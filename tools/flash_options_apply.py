"""Question + answer cards (PYQs whose printed options were lost) made 4-option MCQs (data/flashopts/job-*.out.jsonl,
written by helpers at the owner's request): the official answer is kept, 3 options are written, the stem is laid out.
Tagged "optgen" (the app says the options were written by the app). Idempotent.

    python3 tools/flash_options_apply.py [assets dir=app/src/complete/assets]
"""
import glob, json, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
fix = {}
for f in sorted(glob.glob("data/flashopts/job-*.out.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            if "o" in o and "skip" not in o:
                fix[o["id"]] = o
n = 0
for b in range(1, 7):
    p = f"{A}/mcq{b}.json"
    m = json.load(open(p))
    for qs in m["rows"].values():
        for q in qs:
            u = fix.get(q["id"])
            if not u or q.get("k") not in ("f",):
                continue
            q["s"], q["o"], q["a"] = u["s"], u["o"], u["a"]
            for k in ("k", "at"):
                q.pop(k, None)
            q["tg"] = [t for t in q.get("tg", []) if t != "optgen"] + ["optgen"]
            n += 1
    open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
print(f"{A}: {n} question + answer cards made MCQs ({len(fix)} written)")
