"""Broken PYQs repaired (data/pyqrepair/job-*.out.jsonl, action "fix"): the original question as asked, with its 4
options and key, put back in the MCQ files (a "Knew it / Did not know" card becomes a real MCQ again). Idempotent.

    python3 tools/pyq_repair_apply.py [assets dir=app/src/complete/assets]
"""
import glob, json, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
fix = {}
for f in sorted(glob.glob("data/pyqrepair/job-*.out.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            if o.get("action") == "fix":
                fix[o["id"]] = o
n = 0
for b in range(1, 7):
    p = f"{A}/mcq{b}.json"
    m = json.load(open(p))
    ch = False
    for qs in m["rows"].values():
        for q in qs:
            u = fix.get(q["id"])
            if not u:
                continue
            new = {"s": u["s"], "o": u["o"], "a": u["a"]}
            if all(q.get(k) == v for k, v in new.items()) and "k" not in q:
                continue
            q.update(new)
            for k in ("k", "at", "cx"):
                q.pop(k, None)
            if u.get("x") and "repaired" not in q.get("tg", []):
                q["x"] = u["x"] + ("\n" + q["x"] if q.get("x") else "")
            tg = [t for t in q.get("tg", []) if t != "repaired"] + ["repaired"]
            q["tg"] = tg
            n += 1
            ch = True
    if ch:
        open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
print(f"{A}: {n} PYQs repaired ({len(fix)} fixes)")
