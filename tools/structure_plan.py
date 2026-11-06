"""APPSC Reader, full notes only and well structured, step 1: for each of the 927 topics, its full-notes pages
(titles and first lines) and the topic's one-page summary headings as a hint, as packets for the writers
(data/structure/in/<n>.md, rules in data/structure/INSTRUCTIONS.md). tools/structure_check.py checks their
answers and tools/reader_build.py builds the Reader's notes from them.

    python3 tools/structure_plan.py
"""
import json
import os

A = "app/src/complete/assets"
PER = 30


def text(rs):
    return "".join(r[0] for r in rs)


def first_lines(sec, n=2):
    out = []
    for x in sec["b"]:
        if "x" in x and x.get("k") != "n":
            t = text(x["x"]).strip()
            if t:
                out.append(t[:110])
        if len(out) >= n:
            break
    return " / ".join(out)


topics = []
for b in range(1, 7):
    ri = 0
    for u in json.load(open(f"{A}/book{b}.json"))["units"]:
        for row in u["rows"]:
            full = [s for s in row["secs"] if s.get("f")]
            hint = [s["t"] for s in row["secs"] if not s.get("f")]
            lines = [f"T {b}:{ri} | {row['title']}", "HINT " + " ; ".join(hint)]
            for i, s in enumerate(full, 1):
                lines.append(f"P{i} {s['t']} :: {first_lines(s)}")
            topics.append("\n".join(lines))
            ri += 1
os.makedirs("data/structure/in", exist_ok=True)
for n in range(0, len(topics), PER):
    open(f"data/structure/in/{n // PER}.md", "w").write("\n\n".join(topics[n:n + PER]) + "\n")
print(len(topics), "topics,", (len(topics) + PER - 1) // PER, "packets")
