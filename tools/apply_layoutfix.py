"""Apply the hand repairs of MCQ layout (data/layoutfix_*.jsonl, made from data/layoutfix_todo.jsonl) to the apps'
question banks. A question is changed only where its stem and options still equal the flagged original (blank lines
ignored), so re-running is safe; options keep their order and the key index is never touched.
    python3 tools/apply_layoutfix.py"""
import glob, json, re

norm = lambda t: re.sub(r"\n\s*\n+", "\n", t).strip()
todo = {}
for l in open("data/layoutfix_todo.jsonl"):
    x = json.loads(l); todo[x["id"]] = (norm(x["s"]), x["o"])
fix = {}
for f in sorted(glob.glob("data/layoutfix_[0-9].jsonl")):
    for l in open(f):
        x = json.loads(l)
        if not x.get("ok") and not x.get("skip") and (x.get("s") or x.get("o")):
            fix[x["id"]] = x
n = 0
for app in ("complete", "group1", "group2"):
    for f in sorted(glob.glob(f"app/src/{app}/assets/mcq[0-9].json")):
        m = json.load(open(f)); ch = 0
        for qs in m["rows"].values():
            for q in qs:
                x = fix.get(q["id"])
                if not x or (norm(q["s"]), q["o"]) != todo[q["id"]]:
                    continue
                if x.get("o") and len(x["o"]) != len(q["o"]):
                    print("option count changed, skipped:", q["id"]); continue
                if x.get("s"): q["s"] = x["s"]
                if x.get("o"): q["o"] = x["o"]
                ch += 1
        if ch:
            json.dump(m, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
            n += ch; print(f, ch)
print("questions repaired:", n, "from", len(fix), "repairs")
