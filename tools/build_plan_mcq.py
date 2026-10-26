"""Writes planmcq.json for APPSC Complete's MCQs tab: for every plan day (in plan order), the ids of the notes
MCQs on its topics, each MCQ on the first day that has it (DailyTarget.planMcqs does the same in the app).

    python3 tools/build_plan_mcq.py [assets dir=app/src/complete/assets]
Run it again whenever the plan or the MCQs change (CompleteTest checks the file is current).
"""
import json, os, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
# the app's own plan, else APPSC Complete's (APPSC One-liners), else the Prep app's
plan = json.load(open(next(p for p in (f"{A}/plan.json", "app/src/complete/assets/plan.json", "app/src/main/assets/plan.json")
                            if os.path.exists(p))))
rows = {b: json.load(open(f"{A}/mcq{b}.json"))["rows"] for b in range(1, 7)}
seen, out = set(), []
for d in plan["days"]:
    ids = []
    for r in d["rows"]:
        if r.get("ref"):
            b, ri = r["ref"]
            for i, q in enumerate(rows[b].get(str(ri), [])):
                if i % 20 < r.get("q", 20) and q["id"] not in seen:  # the share of the topic due by this day
                    seen.add(q["id"])
                    ids.append(q["id"])
    out.append(ids)
open(f"{A}/planmcq.json", "w").write(json.dumps(out, separators=(",", ":")))
print(f"{len(out)} plan days, {len(seen)} MCQs")
