"""Group 2: gives the Unlock IAS PYQs (tools/unlockias_add.py) what every other PYQ of the app carries:
"lf" - the syllabus line the question is asked under, the one its section and subsection map to (the same line the
       other MCQs of that subsection have; g2syl_lib.question_leaf gives it at build time);
"rl" - the source tier (g2syl_source.tier: UPSC "up", other exams "ot").
Without "lf" a question does not show under its syllabus line in the Syllabus tab. Idempotent.

    python3 -X utf8 tools/unlockias_g2fields.py [--check]
"""
import hashlib, json, sys
from collections import Counter

sys.path.insert(0, "tools")
from g2syl_source import tier  # noqa: E402

A = "app/src/group2/assets"
CHECK = "--check" in sys.argv
placed = json.load(open("data/pyq/unlockias/added-group2.json"))["placed"]
new = {"y" + hashlib.sha1(k.encode()).hexdigest()[:11] for k in placed}
stats = Counter()
for b in range(1, 7):
    m = json.load(open(f"{A}/mcq{b}.json"))
    for r, qs in m["rows"].items():
        subs = m["subs"].get(r) or [-1] * len(qs)
        by_sub, row = {}, Counter()
        for q, s in zip(qs, subs):
            if q["id"] not in new and q.get("lf") and not q["id"].startswith(("g2l", "pq", "yQ", "yg2")):
                by_sub.setdefault(s, Counter())[q["lf"]] += 1
                row[q["lf"]] += 1
        for q, s in zip(qs, subs):
            if q["id"] not in new:
                continue
            if s in by_sub:
                lf = by_sub[s].most_common(1)[0][0]; stats["lf from its subsection"] += 1
                stats["subsections with more than one line"] += len(by_sub[s]) > 1
            elif row:
                lf = row.most_common(1)[0][0]; stats["lf from its section"] += 1
            else:
                lf = "x"; stats["no line (section has none)"] += 1
            q["lf"], q["rl"] = lf, tier(q)
            stats["rl " + q["rl"]] += 1
    if not CHECK:
        open(f"{A}/mcq{b}.json", "w", encoding="utf8").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
print(dict(stats))
