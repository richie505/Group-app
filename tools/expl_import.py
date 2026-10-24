"""Puts checked structured explanations (work/expl/b<book>/out_*.md) into mcq<book>.json.

    python3 tools/expl_import.py <book>
Each MCQ that passes tools/expl_check.py gets "xs" (solution bullets) and "xa" (additional information bullets);
its one-line "x" stays (the wrong-pick highlight and the hint still use it).
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from expl_check import parse_in, parse_out, check

A = os.environ.get("EXPL_ASSETS", "app/src/main/assets")  # APPSC Complete: app/src/complete/assets
book = sys.argv[1]
d = os.environ.get("EXPL_DIR", "work/expl") + f"/b{book}"
done = {}
for f in sorted(glob.glob(f"{d}/out_*.md")):
    n = f[-6:-3]
    src = parse_in(open(f"{d}/in_{n}.md").read())
    got, _ = parse_out(open(f).read())
    for k, s in src.items():
        if k in got and not check(s, got[k]):
            done[k] = got[k]
p = f"{A}/mcq{book}.json"
mcq = json.load(open(p))
n = 0
for qs in list(mcq["rows"].values()) + list(mcq.get("units", {}).values()):
    for q in qs:
        if q["id"] in done:
            q["xs"], q["xa"] = done[q["id"]]
            n += 1
json.dump(mcq, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
total = sum(len(v) for v in mcq["rows"].values())
have = sum(1 for v in mcq["rows"].values() for q in v if "xs" in q)
print(f"book {book}: {n} explanations imported; {have}/{total} MCQs have one")
