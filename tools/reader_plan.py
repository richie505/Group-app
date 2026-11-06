"""APPSC Reader's reading plan (app/src/reader/assets/plan.json): every one of the 927 topics read once from
START, in APPSC Complete's first-pass order, a day's share by words (about the same reading time each day; the words of the Reader's own notes, tools/reader_build.py); then
revision days for the HIGH-priority topics and your own markers; then two buffer days before the exam.

    python3 tools/reader_plan.py
"""
import datetime as dt
import json

A = "app/src/complete/assets"
START = dt.date(2026, 11, 6)
FIRST_END = dt.date(2027, 1, 10)   # first reading of everything done
LAST = dt.date(2027, 1, 21)        # last plan day; 22-23 Jan are buffer days
EXAM = dt.date(2027, 1, 24)
WPM = 110                          # careful study reading, words a minute

src = json.load(open(f"{A}/plan.json"))
order, seen = [], set()
for d in src["days"]:
    if d["type"] == "study":
        for r in d["rows"]:
            k = tuple(r["ref"])
            if k not in seen:
                seen.add(k)
                order.append(r)
words = {}
for b in range(1, 7):
    ri = 0
    for u in json.load(open(f"app/src/reader/assets/book{b}.json"))["units"]:  # the Reader's full notes
        for row in u["rows"]:
            n = 0
            for s in row["secs"]:
                for x in s["b"]:
                    if "x" in x:
                        n += len("".join(t[0] for t in x["x"]).split())
                    elif x.get("k") == "t":
                        n += sum(len("".join(t[0] for t in c).split()) for rr in x.get("r", []) for c in rr)
            words[(b, ri)] = n
            ri += 1
# any topic the first pass did not list goes at the end of its subject
for k in words:
    if k not in seen:
        order.append({"codes": [], "topic": "", "p": "", "pyq": "", "ref": list(k), "pri": "LOW"})
        seen.add(k)
assert len(order) == len(words) == 927, (len(order), len(words))
idx = json.load(open(f"{A}/index.json"))
titles = {(b["id"], i): r["title"] for b in idx["books"] for i, r in enumerate(b["rows"])}
shorts = {b["id"]: b["short"] for b in idx["books"]}

first_days = (FIRST_END - START).days + 1
total = sum(words.values())
per = total / first_days
days, cur, acc, n = [], [], 0, 0


def left(d):
    k = (EXAM - d).days
    return f"{k} days to 24 Jan 2027"


def row(r):
    b, ri = r["ref"]
    return {"codes": r["codes"], "topic": titles[(b, ri)], "p": r["p"], "pyq": r["pyq"], "ref": [b, ri], "pri": r["pri"]}


def subjects(rows):
    out = []
    for r in rows:
        s = shorts[r["ref"][0]]
        if s not in out:
            out.append(s)
    return out


groups = []
for r in order:
    cur.append(r)
    acc += words[tuple(r["ref"])]
    # close the day when it reaches its share of the words so far
    if acc >= per * (len(groups) + 1) and len(groups) < first_days - 1:
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
date = START
for g in groups:
    w = sum(words[tuple(r["ref"])] for r in g)
    mins = round(w / WPM / 15) * 15
    subj = subjects(g)
    days.append({
        "n": len(days) + 1, "date": date.isoformat(), "dow": date.strftime("%a"), "phase": "PHASE 1 FIRST READING",
        "focus": " + ".join(s.upper() for s in subj),
        "brief": [f"Read {len(g)} topics of {' + '.join(subj)}: about {w:,} words, {mins // 60} h {mins % 60:02d} min of careful reading.",
                  "Mark the lines to revise (select text, then Marker); tap a hard word for its simple meaning."],
        "tasks": [
            {"time": "07:00-09:00", "block": "Read 1", "task": "First half of today's topics. Select a hard word for its meaning."},
            {"time": "10:00-12:00", "block": "Read 2", "task": "Second half. Mark key lines in yellow, dates and numbers in green."},
            {"time": "20:00-20:30", "block": "Recall + tick", "task": "Say each topic's main points aloud; tick pages truly finished."},
        ],
        "left": left(date), "type": "study", "rows": [row(r) for r in g],
    })
    date += dt.timedelta(days=1)
# revision: the HIGH topics, then the rest of your markers
high = [r for r in order if r["pri"] == "HIGH"]
rev_days = (LAST - date).days + 1
hw = sum(words[tuple(r["ref"])] for r in high)
per = hw / rev_days
groups, cur, acc = [], [], 0
for r in high:
    cur.append(r)
    acc += words[tuple(r["ref"])]
    if acc >= per * (len(groups) + 1) and len(groups) < rev_days - 1:
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
for g in groups:
    subj = subjects(g)
    days.append({
        "n": len(days) + 1, "date": date.isoformat(), "dow": date.strftime("%a"), "phase": "PHASE 2 REVISION",
        "focus": " + ".join(s.upper() for s in subj),
        "brief": [f"HIGH priority. Revise {len(g)} topics of {' + '.join(subj)}: your markers first, then the bold lines and tables.",
                  "Evening: the Markers list (Saved tab) of the earlier days."],
        "tasks": [
            {"time": "07:00-10:00", "block": "Revise", "task": "Today's topics: markers, bold terms, tables. Re-read only what you could not recall."},
            {"time": "16:00-17:00", "block": "Markers", "task": "Saved tab, Markers: read everything you marked so far."},
        ],
        "left": left(date), "type": "revision", "rows": [row(r) for r in g],
    })
    date += dt.timedelta(days=1)
assert date == LAST + dt.timedelta(days=1), date
plan = {"start": START.isoformat(), "exam": EXAM.isoformat(), "examLabel": "24 Jan 2027", "days": days,
        "buffer": [{"dates": "22 Jan", "work": "Your markers and bookmarks only, fast"},
                   {"dates": "23 Jan", "work": "Light review, admit card, centre route, sleep by 22:00"}]}
json.dump(plan, open("app/src/reader/assets/plan.json", "w"), ensure_ascii=False, separators=(",", ":"))
fp = [d for d in days if d["type"] == "study"]
print(f"{len(days)} days: {len(fp)} first reading ({total:,} words, about {total / len(fp) / WPM / 60:.1f} h a day), "
      f"{len(days) - len(fp)} revision ({len(high)} HIGH topics)")
