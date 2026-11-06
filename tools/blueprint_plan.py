"""Moves APPSC Complete's plan onto the blueprint notes (run after tools/blueprint_build.py).

Every plan row's topic ref goes through data/blueprint/topic_of.json (old book row -> new topic) and takes the
new topic's title, codes and first page. Day briefs and tasks are rewritten for the new notes: they name topics
and their page count (the notes are now full topics, not one-pagers), and give each study day's MCQ count.
The plan's days, dates and order stay the same. Then run tools/build_plan_mcq.py.

    python3 tools/blueprint_plan.py [assets dir=app/src/complete/assets]
"""
import json, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
plan = json.load(open(f"{A}/plan.json"))
topic_of = json.load(open("data/blueprint/topic_of.json"))
idx = json.load(open(f"{A}/index.json"))["books"]
mcq = {b: json.load(open(f"{A}/mcq{b}.json"))["rows"] for b in range(1, 7)}
SHORT = {b["id"]: b.get("short", b["title"]) for b in idx}
ROWS = {b["id"]: b["rows"] for b in idx}


def ranges(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"{nums[i]}" if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


WORDS = [("one-pagers", "topics"), ("one-pager PDFs", "notes"), ("one-pager", "notes"), ("One-pagers", "Notes"),
         ("its exam corner", "its traps box"), ("exam corners", "traps boxes"), ("exam corner", "traps box")]


def reword(s):
    for a, b in WORDS:
        s = s.replace(a, b)
    return s


seen = set()
for d in plan["days"]:
    books, pages, nq = {}, 0, 0
    for r in d["rows"]:
        if not r.get("ref"):
            continue
        b, ri = r["ref"]
        nri = topic_of[f"{b}:{ri}"]
        t = ROWS[b][nri]
        r.update(ref=[b, nri], topic=t["title"], codes=t["codes"], p=str(t.get("p1", r.get("p", ""))))
        books.setdefault(b, []).append(nri + 1)
        pages += t.get("n", 0)
        for i, q in enumerate(mcq[b].get(str(nri), [])):
            if i % 20 < r.get("q", 20) and q["id"] not in seen:
                seen.add(q["id"])
                nq += 1
    pri = d["brief"][0].split(" priority")[0] if d["brief"] and " priority" in d["brief"][0] else ""
    names = " + ".join(SHORT[b] for b in books)
    n = len(d["rows"])
    if d["type"] == "study" and books:
        where = "; ".join(f"{SHORT[b]} topics {ranges(v)}" for b, v in books.items())
        d["brief"] = [f"{pri} priority. Read {n} topics ({pages} pages): {where}.",
                      f"Read each topic's numbered sections in order, then its traps box; then today's MCQs ({nq})."]
    elif d["type"] == "revision" and books:
        d["brief"] = [f"{pri} priority. Revise {n} topics of {names} ({pages} pages): tables, number game and traps first."]
    else:
        d["brief"] = [reword(x) for x in d["brief"]]
    for k in d.get("tasks", []):
        k["block"], k["task"] = reword(k["block"]), reword(k["task"])
plan["buffer"] = [dict(x, work=reword(x["work"])) for x in plan.get("buffer", [])]
open(f"{A}/plan.json", "w").write(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
print(f"{len(plan['days'])} plan days moved onto the blueprint topics; {len(seen)} MCQs due on study days")
