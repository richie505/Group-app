"""APPSC Complete's whole plan (from 26 Oct, Day 1), by priority: HIGH topics first, then MED, then LIGHT.

Days before KEEP_BEFORE (if any) stay exactly as they were. From then on:
- the rest of the first pass (to 3 Dec): HIGH topics, then MED, then LIGHT; still one subject a day, subjects
  interleaved, and each day about the same number of MCQs (the time goes on MCQs, not on topic count);
- R2, R3 revision and the Phase 4 MCQ days (mocks where they were): HIGH first, then MED, then LIGHT.
Dates, phases and each topic's MCQ shares stay as they were. Then run tools/build_plan_mcq.py.

    python3 tools/priority_plan.py
"""
import json
import re

A = "app/src/complete/assets"
KEEP_BEFORE = "2026-10-26"  # the whole plan, from Day 1
TIERS = ["HIGH", "MED", "LIGHT"]
ORDER = [2, 1, 4, 3, 5, 6]  # Polity first, as in the plan

plan = json.load(open(f"{A}/plan.json"))
short = {b["id"]: b["short"] for b in json.load(open(f"{A}/index.json"))["books"]}
mcqs = {}
for b in range(1, 7):
    for ri, v in json.load(open(f"{A}/mcq{b}.json"))["rows"].items():
        mcqs[(b, int(ri))] = len(v)
w = lambda r: max(1, mcqs.get(tuple(r["ref"]), 0))
strip = lambda r: {k: v for k, v in r.items() if k != "q"}

keep = [d for d in plan["days"] if d["date"] < KEEP_BEFORE]
rest = [d for d in plan["days"] if d["date"] >= KEEP_BEFORE]
study = [d for d in rest if d["type"] == "study"]
later = [d for d in rest if d["type"] != "study"]
pool = [strip(r) for d in study for r in d["rows"]]
q_study = study[0]["rows"][0]["q"]


def syllabus(r):
    return ORDER.index(r["ref"][0]), r["ref"][1]


def balanced(rows, n):
    """rows split into n contiguous chunks of about equal MCQs."""
    total, out, cur, acc = sum(map(w, rows)), [], [], 0
    for i, r in enumerate(rows):
        cur.append(r)
        acc += w(r)
        left_rows, left_days = len(rows) - i - 1, n - len(out) - 1
        if left_days and (acc >= total * (len(out) + 1) / n or left_rows == left_days):
            out.append(cur)
            cur = []
    out.append(cur)
    return [c for c in out if c] + [[] for _ in range(n - len([c for c in out if c]))]


def subjects(rows):
    seen = []
    for r in rows:
        if short[r["ref"][0]] not in seen:
            seen.append(short[r["ref"][0]])
    return " + ".join(seen)


# --- the rest of the first pass: (tier, subject) groups, days by MCQ weight, one subject a day
groups = [(t, b, sorted([r for r in pool if r["pri"] == t and r["ref"][0] == b], key=syllabus))
          for t in TIERS[:2] for b in ORDER]
# LIGHT topics are few and small: they share mixed-subject days at the end
groups.append(("LIGHT", 0, sorted([r for r in pool if r["pri"] == "LIGHT"], key=syllabus)))
groups = [g for g in groups if g[2]]
D, W = len(study), sum(map(w, pool))
# every group one day, then each spare day to the group with the heaviest days (keeps the days even)
days_for = [1] * len(groups)
while sum(days_for) < D:
    k = max(range(len(groups)), key=lambda k: sum(map(w, groups[k][2])) / days_for[k])
    days_for[k] += 1
seq = []
for t in TIERS:  # within a tier, each day goes to the subject furthest behind its share
    gi = [k for k, g in enumerate(groups) if g[0] == t]
    done = {k: 0 for k in gi}
    for _ in range(sum(days_for[k] for k in gi)):
        k = min(gi, key=lambda k: (done[k] + 1) / days_for[k] if done[k] < days_for[k] else 9)
        seq.append(k)
        done[k] += 1
parts = {k: balanced(groups[k][2], days_for[k]) for k in range(len(groups))}
used = {k: 0 for k in parts}


def pages(rows):
    ns, out = sorted(int(r["p"]) for r in rows), []
    for n in ns:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


for d, k in zip(study, seq):
    t, b, _ = groups[k]
    rows = parts[k][used[k]]
    used[k] += 1
    n = sum(map(w, rows))
    d["rows"] = [dict(r, q=q_study) for r in rows]
    if b:
        d["focus"] = short[b].upper()
        what = f"{len(rows)} one-pagers of {short[b]}, topics {pages(rows)} (same page numbers in its one-pager PDF)"
    else:
        d["focus"] = subjects(rows).upper()
        what = f"{len(rows)} one-pagers: " + "; ".join(
            f"{short[x]} {pages([r for r in rows if r['ref'][0] == x])}" for x in ORDER if any(r["ref"][0] == x for r in rows))
    d["brief"] = [f"{t} priority. Read: {what}.",
                  f"About 10 minutes a page; then today's MCQs (about {n // 2} of their {n})."]

# --- R2, R3 and Phase 4: every topic, HIGH first
allrows = {tuple(r["ref"]): strip(r) for d in plan["days"] for r in d["rows"]}
by_pri = sorted(allrows.values(), key=lambda r: (TIERS.index(r["pri"]), syllabus(r)))


def tiers(rows):
    return " + ".join(t for t in TIERS if any(r["pri"] == t for r in rows))


for kind, phase in [("revision", "PHASE 2 R2 REVISION"), ("revision", "PHASE 3 R3 REVISION")]:
    ds = [d for d in later if d["phase"] == phase]
    q = ds[0]["rows"][0]["q"]
    per = len(by_pri)
    for i, d in enumerate(ds):
        rows = by_pri[per * i // len(ds): per * (i + 1) // len(ds)]
        d["rows"] = [dict(r, q=q) for r in rows]
        d["focus"] = subjects(rows).upper()
        how = "about 4 minutes a page" if "R2" in phase else "about 2 minutes a page: the boxes and exam corners"
        d["brief"] = [f"{tiers(rows)} priority. Revise {len(rows)} one-pagers ({subjects(rows)}): {how}."]
ds = [d for d in later if d["type"] == "practice"]
for d, rows in zip(ds, balanced(by_pri, len(ds))):
    d["rows"] = [dict(r) for r in rows]
    d["focus"] = subjects(rows).upper()
    d["brief"] = [f"{tiers(rows)} priority. MCQs of {len(rows)} topics ({subjects(rows)}): the rest of their MCQs "
                  f"(about {sum(map(w, rows))} in all). Re-read the one-pager of every miss."]

plan["days"] = keep + rest
seen = [tuple(r["ref"]) for d in plan["days"] if d["type"] == "study" for r in d["rows"]]
assert len(seen) == len(set(seen)) == len(allrows), (len(seen), len(set(seen)), len(allrows))
open(f"{A}/plan.json", "w").write(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
for d in plan["days"]:
    if d["date"] >= KEEP_BEFORE and d["type"] in ("study", "practice"):
        print(d["n"], d["date"], d["brief"][0][:70], "| MCQs", sum(map(w, d["rows"])))
