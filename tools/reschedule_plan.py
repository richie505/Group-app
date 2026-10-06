"""Move the 90-day plan to new dates: Day 1 on START, the exam on EXAM, the final buffer in between.

Each day keeps its content and number (R1 "Day 07" links still match); only dates, weekdays and the
"N days to ..." line change. The buffer blocks are spread over the days left after Day 90.

    python3 tools/reschedule_plan.py app/src/main/assets/plan.json 2026-10-06 2027-01-24
"""
import json
import sys
from datetime import date, timedelta

# final buffer: (share of the buffer days, work) - shares are scaled to the days available
BUFFER = [
    (4, "Polity + Society, History + AP History: error log rows first, then HIGH rows via fact sheets"),
    (4, "Geography, Economy (AP SES / budget data), S&T + Environment"),
    (2, "Current Affairs: CA book + last 12 months log, AP first"),
    (2, "Mental Ability: Tier-A formula sheet + two 25-Q timed sets; decide your MA skip list"),
    (1, "Exam simulation: G1 Prelims 2018 Paper-I + Paper-II (APPSC PYQs\\01 Carpe Diem IAS)"),
    (1, "Exam simulation: G2 Screening 2016 or 2018 paper (APPSC PYQs\\05 / 02 folders)"),
    (1, "Repair from both simulations"),
    (4, "Error log + fact sheets only; CA last 3 months"),
    (1, "Light review, admit card, centre route, sleep by 22:00"),
]


def label(d: date) -> str:
    return f"{d.day} {d.strftime('%b')} {d.year}"


def span(a: date, b: date) -> str:
    if a == b:
        return f"{a.day} {a.strftime('%b')}"
    if a.month == b.month:
        return f"{a.day}-{b.day} {a.strftime('%b')}"
    return f"{a.day} {a.strftime('%b')} - {b.day} {b.strftime('%b')}"


def main(path: str, start: str, exam: str) -> None:
    plan = json.load(open(path, encoding="utf-8"))
    s, e = date.fromisoformat(start), date.fromisoformat(exam)
    for d in plan["days"]:
        day = s + timedelta(days=d["n"] - 1)
        d["date"] = day.isoformat()
        d["dow"] = day.strftime("%a")
        d["left"] = f"{(e - day).days} days to {label(e)}"
        if d["type"] == "sunday":  # every 7th day, whatever the weekday now
            d["phase"] = d["phase"].replace("SUNDAY REVIEW", "WEEKLY REVIEW")
    first = s + timedelta(days=len(plan["days"]))
    free = (e - first).days  # days between Day 90 and the exam
    if free < len(BUFFER):
        raise SystemExit(f"only {free} days between Day {len(plan['days'])} and the exam")
    # whole days per block, in proportion, the last ones taking what is left
    total = sum(w for w, _ in BUFFER)
    sizes = [max(1, round(w * free / total)) for w, _ in BUFFER]
    sizes[-2] += free - sum(sizes)
    buf, day = [], first
    for n, (_, work) in zip(sizes, BUFFER):
        buf.append({"dates": span(day, day + timedelta(days=n - 1)), "work": work})
        day += timedelta(days=n)
    plan.update(start=s.isoformat(), exam=e.isoformat(), examLabel=label(e), buffer=buf)
    json.dump(plan, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"Day 1 {s}, Day {len(plan['days'])} {plan['days'][-1]['date']}, buffer {span(first, e - timedelta(days=1))}, exam {e}")
    for b in buf:
        print(" ", b["dates"], "-", b["work"][:50])


if __name__ == "__main__":
    main(*sys.argv[1:4])
