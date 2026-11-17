"""Writes planmcq.json for APPSC Complete's MCQs tab: for every plan day (in plan order), the ids of the notes
MCQs on its topics, each MCQ on the first day that has it (DailyTarget.planMcqs does the same in the app).

    python3 tools/build_plan_mcq.py [assets dir=app/src/complete/assets]
Run it again whenever the plan or the MCQs change (CompleteTest checks the file is current).
"""
import json, os, re, sys

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

# "spread": over each run of study days, the same number of MCQs a day (an MCQ never before the day of its topic,
# so a heavy topic's extra goes on the next days). DueMcqs.planMcqs in the app does the same.
if plan.get("spread") and os.path.exists(f"{A}/plan.json"):
    days, i = plan["days"], 0
    while i < len(days):
        if days[i]["type"] != "study":
            i += 1
            continue
        j = i
        while j < len(days) and days[j]["type"] == "study":
            j += 1
        flat = [x for k in range(i, j) for x in out[k]]
        n, have, prev, new = j - i, 0, 0, []
        for k in range(n):
            have += len(out[i + k])
            cum = min(have, len(flat) * (k + 1) // n)
            new.append(flat[prev:cum])
            prev = cum
        out[i:j] = new
        i = j
    # the day's brief says how many (Group 2: "Then today's MCQs (...)."; Complete: "...; then all its MCQs (N today).")
    for d, ids in zip(days, out):
        if d["type"] != "study":
            continue
        say = f"today's MCQs ({len(ids)}, the same each study day: what is left of earlier topics, then today's)"
        d["brief"] = [f"Then {say}." if b.startswith("Then today's MCQs")
                      else re.sub(r"then (all its MCQs \(\d+ today\)|today's MCQs \(\d+, the same each study day: what is left of earlier topics, then today's\))", "then " + say, b) for b in d["brief"]]
        for t in d.get("tasks", []):
            if t.get("block") == "MCQs":
                t["task"] = re.sub(r"Today's MCQs \(MCQs tab\): (all|half) of each topic's MCQs\.", "Today's MCQs (Today tab or MCQs tab).", t["task"])
    open(f"{A}/plan.json", "w").write(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
open(f"{A}/planmcq.json", "w").write(json.dumps(out, separators=(",", ":")))
print(f"{len(out)} plan days, {len(seen)} MCQs")
