"""APPSC Complete's plan from a start date to 2 days before the exam: every day reads notes and practises those
topics' MCQs. No revision, practice-only or mock days. Each topic is on exactly one day, with all its MCQs.

Order: HIGH topics, then MED, then LIGHT. Within a tier, one subject a day, subjects interleaved. Days are evened
by study time (about 10 minutes a page plus 1 minute an MCQ). Then run tools/build_plan_mcq.py.

    python3 tools/straight_plan.py [start=2026-11-06]
"""
import datetime as dt
import json
import sys

A = "app/src/complete/assets"
TIERS = ["HIGH", "MED", "LIGHT"]
ORDER = [2, 1, 4, 3, 5, 6]  # Polity first

plan = json.load(open(f"{A}/plan.json"))
start = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-11-06")
exam = dt.date.fromisoformat(plan["exam"])
end = exam - dt.timedelta(days=2)
dates = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
short = {b["id"]: b["short"] for b in json.load(open(f"{A}/index.json"))["books"]}
mcqs, secs = {}, {}
for b in range(1, 7):
    for ri, v in json.load(open(f"{A}/mcq{b}.json"))["rows"].items():
        mcqs[(b, int(ri))] = len(v)
    flat = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
    for ri, r in enumerate(flat):
        secs[(b, ri)] = len(r["secs"])
q = lambda r: mcqs.get(tuple(r["ref"]), 0)
pg = lambda r: secs.get(tuple(r["ref"]), 1)
w = lambda r: 10 * pg(r) + q(r)

allrows = {}
for d in plan["days"]:
    for r in d["rows"]:
        allrows.setdefault(tuple(r["ref"]), {k: v for k, v in r.items() if k != "q"})
pool = list(allrows.values())
syllabus = lambda r: (ORDER.index(r["ref"][0]), r["ref"][1])


def balanced(rows, n):
    total, out, cur, acc = sum(map(w, rows)), [], [], 0
    for i, r in enumerate(rows):
        cur.append(r)
        acc += w(r)
        if n - len(out) - 1 and (acc >= total * (len(out) + 1) / n or len(rows) - i - 1 == n - len(out) - 1):
            out.append(cur)
            cur = []
    out.append(cur)
    out = [c for c in out if c]
    return out + [[] for _ in range(n - len(out))]


groups = [(t, b, sorted([r for r in pool if r["pri"] == t and r["ref"][0] == b], key=syllabus))
          for t in TIERS[:2] for b in ORDER]
groups.append(("LIGHT", 0, sorted([r for r in pool if r["pri"] == "LIGHT"], key=syllabus)))
groups = [g for g in groups if g[2]]
D = len(dates)
days_for = [1] * len(groups)
while sum(days_for) < D:
    k = max(range(len(groups)), key=lambda k: sum(map(w, groups[k][2])) / days_for[k] if len(groups[k][2]) > days_for[k] else 0)
    days_for[k] += 1
seq = []
for t in TIERS:
    gi = [k for k, g in enumerate(groups) if g[0] == t]
    done = {k: 0 for k in gi}
    for _ in range(sum(days_for[k] for k in gi)):
        k = min(gi, key=lambda k: (done[k] + 1) / days_for[k] if done[k] < days_for[k] else 9)
        seq.append(k)
        done[k] += 1
parts = {k: balanced(groups[k][2], days_for[k]) for k in range(len(groups))}
used = {k: 0 for k in parts}


def nums(rows):
    ns, out = sorted(int(r["p"]) for r in rows), []
    for n in ns:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


days = []
for i, (date, k) in enumerate(zip(dates, seq)):
    t, b, _ = groups[k]
    rows = parts[k][used[k]]
    used[k] += 1
    nq, npg = sum(map(q, rows)), sum(map(pg, rows))
    if b:
        focus = short[b].upper()
        what = f"{len(rows)} topics ({npg} pages): {short[b]} topics {nums(rows)}"
    else:
        bs = [x for x in ORDER if any(r["ref"][0] == x for r in rows)]
        focus = " + ".join(short[x] for x in bs).upper()
        what = f"{len(rows)} topics ({npg} pages): " + "; ".join(
            f"{short[x]} {nums([r for r in rows if r['ref'][0] == x])}" for x in bs)
    left = (exam - date).days
    days.append({
        "n": i + 1, "date": date.isoformat(), "dow": date.strftime("%a"), "phase": "NOTES + MCQS",
        "focus": focus,
        "brief": [f"{t} priority. Read {what}.",
                  f"Read each topic's numbered sections in order, then its traps box; then all its MCQs ({nq} today)."],
        "tasks": [
            {"time": "07:00-10:00", "block": "Notes 1", "task": "First half of today's pages. After each page: close it and say its traps box aloud."},
            {"time": "11:00-13:00", "block": "Notes 2", "task": "Second half. Mark anything you could not recall."},
            {"time": "16:00-19:00", "block": "MCQs", "task": "Today's MCQs (MCQs tab): all of each topic's MCQs. Read the notes again for every miss."},
            {"time": "20:00-20:30", "block": "Recall + tick", "task": "Blank-sheet recall of today's topics; tick only pages truly finished."}],
        "left": f"{left} days to {plan['examLabel']}", "type": "study",
        "rows": [dict(r) for r in rows]})

plan["start"] = start.isoformat()
plan["days"] = days
plan["buffer"] = [{"dates": (exam - dt.timedelta(days=1)).strftime("%-d %b"),
                   "work": "No new study: admit card, centre route, sleep by 22:00"}]
seen = [tuple(r["ref"]) for d in days for r in d["rows"]]
assert len(seen) == len(set(seen)) == len(allrows), (len(seen), len(set(seen)), len(allrows))
assert all(d["rows"] for d in days), "a day with no topics"
open(f"{A}/plan.json", "w").write(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
for d in days:
    print(d["n"], d["date"], d["focus"][:30], "| topics", len(d["rows"]), "pages", sum(map(pg, d["rows"])),
          "MCQs", sum(map(q, d["rows"])))
print(f"{len(days)} days, {start} to {end}; buffer {plan['buffer'][0]['dates']}")
