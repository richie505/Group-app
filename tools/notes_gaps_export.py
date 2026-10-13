"""Open items left in the notes, in batches for agents (guide: tools/notes_gaps_guide.md).

    python3 tools/notes_gaps_export.py [per_batch=40]
Two kinds of item, each one block of the notes:
    GAP    a "!! Not in your sources: ..." line (a fact the notes lack)
    HEDGE  a block that says "some notes / other notes / older notes / verify / misprint" (an unsettled fact)
Writes work/notegaps/in_NNN.md; a topic's items always stay in one batch.
"""
import json, os, re, sys

per = int(sys.argv[1]) if len(sys.argv) > 1 else 40
HEDGE = re.compile(r"(?i)some notes|other notes|older notes|\bverify\b|misprint")
out = "work/notegaps"
os.makedirs(out, exist_ok=True)
for f in os.listdir(out):
    if f.startswith("in_"):
        os.remove(f"{out}/{f}")

topics = []  # (book, row, title, [(kind, sec, block, text)])
for book in range(1, 7):
    d = json.load(open(f"app/src/main/assets/book{book}.json"))
    for ri, r in enumerate(row for u in d["units"] for row in u["rows"]):
        items = []
        for si, s in enumerate(r["secs"]):
            for bi, b in enumerate(s["b"]):
                if b["k"] == "t":
                    t = " | ".join("".join(x[0] for x in (c if isinstance(c, list) else [[c, 0]])) for row in [b["h"]] + b["r"] for c in row)
                    gap = False
                else:
                    x = b["x"] if isinstance(b["x"], list) else [[b["x"], 0]]
                    t = "".join(run[0] for run in x)
                    gap = any(run[1] == 6 for run in x)
                if gap:
                    items.append(("GAP", si, bi, t))
                elif HEDGE.search(t):
                    items.append(("HEDGE", si, bi, t))
        if items:
            topics.append((book, ri, r["title"], items))

batches, cur = [], []
for t in topics:
    if cur and sum(len(x[3]) for x in cur) + len(t[3]) > per:
        batches.append(cur)
        cur = []
    cur.append(t)
if cur:
    batches.append(cur)

total = 0
for n, batch in enumerate(batches):
    lines = []
    for book, ri, title, items in batch:
        lines.append(f"=== BOOK {book} ROW {ri} | {title}")
        for kind, si, bi, t in items:
            lines.append(f"- {kind} sec {si} block [{bi}]: {t}")
            total += 1
        lines.append("")
    open(f"{out}/in_{n:03d}.md", "w").write("\n".join(lines))
print(f"{total} items in {len(batches)} batches")
