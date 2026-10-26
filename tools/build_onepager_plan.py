"""APPSC Complete's (and APPSC One-liners') study plan for the one-page notes: 927 topics, about 4 hours a day.

    python3 tools/build_onepager_plan.py   (then tools/onepager_app.py all, or build_plan_mcq.py per app)

Writes app/src/complete/assets/plan.json (One-liners takes it from there):
- Phase 1, 26 Oct - 3 Dec: first pass, ~24 one-pagers a day, one subject a day, the subjects interleaved;
- Phase 2, 4 - 19 Dec: R2 revision, ~58 a day; Phase 3, 20 - 27 Dec: R3 revision, ~116 a day;
- Phase 4, 28 Dec - 21 Jan: MCQ days (~49 topics each) with a full mock every fourth day; 22 - 23 Jan: the buffer.
Each topic's MCQs are spread over its days (row "q", twentieths of its MCQs due by then): half on the first
pass, a little more at R2 and R3, the rest on its MCQ day.
"""
import datetime as dt
import json
import re

START, EXAM = dt.date(2026, 10, 26), dt.date(2027, 1, 24)
PHASES = [  # (days, type, phase, share of each topic's MCQs due by then)
    (39, "study", "PHASE 1 FIRST PASS", 10),
    (16, "revision", "PHASE 2 R2 REVISION", 13),
    (8, "revision", "PHASE 3 R3 REVISION", 14),
]
MOCKS = {  # Phase 4 day -> the mock (counted from 28 Dec)
    3: "Full mock: G1 Prelims Paper-I (150 Q, 150 min)",
    7: "Full mock: G2 Screening paper (150 Q, 150 min)",
    11: "Full mock: G1 Prelims Paper-II (150 Q, 150 min)",
    15: "Full mock: G2 Screening paper, another year (150 Q, 150 min)",
    19: "Full mock: G1 Prelims 2018 Paper-I + Paper-II",
    23: "Full mock: G2 Screening 2016 or 2018 paper",
}
PRACTICE_DAYS = 25  # 28 Dec - 21 Jan
ORDER = [2, 1, 4, 3, 5, 6]  # Polity first, as before
TASKS = {
    "study": [("07:00-09:00", "One-pagers 1", "First half of today's pages. After each page: close it and say its exam corner aloud."),
              ("10:00-12:00", "One-pagers 2", "Second half. Mark anything you could not recall."),
              ("16:00-17:00", "MCQs", "Today's MCQs (MCQs tab): half of each topic's MCQs. Every miss goes to Answered wrong."),
              ("20:00-20:30", "Recall + tick", "Blank-sheet recall of today's topics; tick only pages truly finished.")],
    "revision": [("07:00-09:00", "Revise 1", "First half of today's pages: tables, timelines and exam corners first."),
                 ("10:00-12:00", "Revise 2", "Second half. Re-read only what you could not recall."),
                 ("16:00-17:00", "MCQs", "Today's MCQs, then Answered wrong from the earlier days.")],
    "practice": [("07:00-10:00", "MCQs", "Today's MCQs: the rest of each topic's MCQs. Read the one-pager again for every miss."),
                 ("16:00-17:00", "Answered wrong", "Retry Answered wrong; note each repeat miss on its one-pager.")],
    "mock": [("10:00-12:30", "Mock", "Full mock in exam conditions."),
             ("15:00-17:00", "Repair", "Every wrong or guessed question: its one-pager, then its MCQs.")],
}


def topics():
    index = json.load(open("app/src/complete/assets/index.json"))
    out = {}
    for b in index["books"]:
        rows = []
        for ri, r in enumerate(b["rows"]):
            pyq = sum(int(x) for x in re.findall(r"\d+", r.get("pyq", "")))
            rows.append({"codes": r["codes"], "topic": r["title"], "p": str(ri + 1), "pyq": str(pyq), "ref": [b["id"], ri]})
        out[b["id"]] = (b["short"], rows)
    every = sorted(int(r["pyq"]) for _, rs in out.values() for r in rs)
    high, light = every[int(len(every) * 0.55)], every[int(len(every) * 0.08)]
    for _, rs in out.values():
        for r in rs:
            r["pri"] = "HIGH" if int(r["pyq"]) >= high else "LIGHT" if int(r["pyq"]) < light else "MED"
    return out


def first_pass_days(books, n):
    """n days, each one subject; a subject's days spread over the phase in proportion to its topics."""
    total = sum(len(books[b][1]) for b in ORDER)
    days_for = {b: max(1, round(n * len(books[b][1]) / total)) for b in ORDER}
    while sum(days_for.values()) != n:
        b = max(ORDER, key=lambda b: len(books[b][1]) / days_for[b]) if sum(days_for.values()) < n else \
            min(ORDER, key=lambda b: len(books[b][1]) / days_for[b])
        days_for[b] += 1 if sum(days_for.values()) < n else -1
    # interleave: each day goes to the subject furthest behind its share
    done, seq = {b: 0 for b in ORDER}, []
    for d in range(n):
        b = min(ORDER, key=lambda b: (done[b] + 1) / days_for[b] if done[b] < days_for[b] else 9)
        seq.append(b)
        done[b] += 1
    out, at = [], {b: 0 for b in ORDER}
    for b in seq:
        k = len(books[b][1]) * (at[b] + 1) // days_for[b] - len(books[b][1]) * at[b] // days_for[b]
        start = len(books[b][1]) * at[b] // days_for[b]
        out.append(books[b][1][start:start + k])
        at[b] += 1
    return out


def chunks(rows, n):
    return [rows[len(rows) * i // n: len(rows) * (i + 1) // n] for i in range(n)]


def main():
    books = topics()
    short = {b: books[b][0] for b in books}
    fp = first_pass_days(books, PHASES[0][0])
    order = [r for d in fp for r in d]
    plan_days, date = [], START

    def add(kind, phase, rows, q, brief, focus):
        nonlocal date
        n = len(plan_days) + 1
        plan_days.append({
            "n": n, "date": date.isoformat(), "dow": date.strftime("%a"), "phase": phase, "focus": focus.upper(),
            "brief": brief, "tasks": [{"time": t, "block": b, "task": x} for t, b, x in TASKS[kind]],
            "left": f"{(EXAM - date).days} days to 24 Jan 2027", "type": kind,
            "rows": [dict(r, q=q) if q < 20 else dict(r) for r in rows],
        })
        date += dt.timedelta(days=1)

    def subjects(rows):
        seen = []
        for r in rows:
            if short[r["ref"][0]] not in seen:
                seen.append(short[r["ref"][0]])
        return " + ".join(seen)

    for rows in fp:
        b = rows[0]["ref"][0]
        add("study", PHASES[0][2], rows, PHASES[0][3],
            [f"Read: {len(rows)} one-pagers of {short[b]}, topics {rows[0]['p']}-{rows[-1]['p']} (pages {rows[0]['p']}-{rows[-1]['p']} of its one-pager PDF).",
             "About 10 minutes a page; then today's MCQs."], short[b])
    for days, kind, phase, q in PHASES[1:]:
        for rows in chunks(order, days):
            add(kind, phase, rows, q, [f"Revise {len(rows)} one-pagers ({subjects(rows)}): "
                                       f"{'about 4 minutes a page' if q == 13 else 'about 2 minutes a page: the boxes and exam corners'}."],
                subjects(rows))
    practice = [i for i in range(1, PRACTICE_DAYS + 1) if i not in MOCKS]
    rows_for = dict(zip(practice, chunks(order, len(practice))))
    for i in range(1, PRACTICE_DAYS + 1):
        if i in MOCKS:
            add("mock", "PHASE 4 MCQS + MOCKS", [], 20, [MOCKS[i]], "")
        else:
            rows = rows_for[i]
            add("practice", "PHASE 4 MCQS + MOCKS", rows, 20,
                [f"MCQs of {len(rows)} topics ({subjects(rows)}): the rest of their MCQs. Re-read the one-pager of every miss."],
                subjects(rows))
    assert date == dt.date(2027, 1, 22), date
    plan = {"start": START.isoformat(), "exam": EXAM.isoformat(), "examLabel": "24 Jan 2027", "days": plan_days,
            "buffer": [{"dates": "22 Jan", "work": "Answered wrong + every exam corner (one-pager PDFs), fast"},
                       {"dates": "23 Jan", "work": "Light review, admit card, centre route, sleep by 22:00"}]}
    open("app/src/complete/assets/plan.json", "w").write(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
    per = [len(d["rows"]) for d in plan_days]
    print(f"{len(plan_days)} days; topics a day: first pass {min(per[:39])}-{max(per[:39])}, "
          f"R2 {min(per[39:55])}-{max(per[39:55])}, R3 {min(per[55:63])}-{max(per[55:63])}; "
          f"{len(order)} topics, {len(set(tuple(r['ref']) for r in order))} distinct")


if __name__ == "__main__":
    main()
