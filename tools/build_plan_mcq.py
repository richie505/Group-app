"""Writes planmcq.json for APPSC Complete's MCQs tab: for every plan day (in plan order), the ids of the notes
MCQs on its topics, each MCQ on the first day that has it (DailyTarget.planMcqs does the same in the app).

    python3 tools/build_plan_mcq.py [assets dir=app/src/complete/assets]
Run it again whenever the plan or the MCQs change (CompleteTest checks the file is current).
"""
import json, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
plan = json.load(open("app/src/main/assets/plan.json"))
rows = {b: json.load(open(f"{A}/mcq{b}.json"))["rows"] for b in range(1, 7)}
seen, out = set(), []
for d in plan["days"]:
    ids = []
    for r in d["rows"]:
        if r.get("ref"):
            b, ri = r["ref"]
            for q in rows[b].get(str(ri), []):
                if q["id"] not in seen:
                    seen.add(q["id"])
                    ids.append(q["id"])
    out.append(ids)
open(f"{A}/planmcq.json", "w").write(json.dumps(out, separators=(",", ":")))
print(f"{len(out)} plan days, {len(seen)} MCQs")
