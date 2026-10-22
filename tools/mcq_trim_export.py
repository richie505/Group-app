"""Splits a book's MCQs into review batches: each topic's subsections (notes in the markdown form of
tools/structured_md.py) followed by the MCQs filed under that subsection.

    python3 tools/mcq_trim_export.py 2 [MCQs per batch]
writes work/mcqtrim/b2/in_NNN.md. Questions are labelled Q<row>.<index> (index in the topic's list);
an agent answers in out_NNN.jsonl (see tools/mcq_trim_guide.md), checked by tools/mcq_trim_check.py.
"""
import json, os, sys
A = os.environ.get("TRIM_ASSETS", "app/src/main/assets")  # APPSC Complete: app/src/complete/assets
W = os.environ.get("TRIM_DIR", "work/mcqtrim")
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

book = int(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 330
notes = json.load(open(f"{A}/book{book}.json"))
mcq = json.load(open(f"{A}/mcq{book}.json"))
rows = [r for u in notes["units"] for r in u["rows"]]
out = f"{W}/b{book}"
os.makedirs(out, exist_ok=True)


def question(label, q):
    lines = [f"[{label}] " + ("(ROCKET) " if q.get("src") == "rocket" else "") + q["s"]]
    lines += [f"  {'ABCD'[i]}) {o}" for i, o in enumerate(q["o"])]
    lines.append(f"  ANSWER: {'ABCD'[q['a']] if 0 <= q['a'] < 4 else q['a']}")
    if q.get("x"):
        lines.append(f"  WHY: {q['x']}")
    return "\n".join(lines)


def topic(ri):
    r, qs, subs = rows[ri], mcq["rows"].get(str(ri), []), mcq["subs"].get(str(ri), [])
    if not qs:
        return "", 0
    parts = [f"=== ROW {ri} | {r['title']}"]
    under = {}
    for j, s in enumerate(subs):
        under.setdefault(s, []).append(j)
    if -1 in under:
        parts.append("## SUB -1 | whole topic (no single subsection)")
        parts += [question(f"Q{ri}.{j}", qs[j]) for j in under[-1]]
    for si, s in enumerate(r["secs"]):
        md, _ = from_blocks(s["b"], inline_tables=True)
        parts.append(f"## SUB {si} | {s['t']}\n--- notes ---\n{md}\n--- MCQs ({len(under.get(si, []))}) ---")
        parts += [question(f"Q{ri}.{j}", qs[j]) for j in under.get(si, [])]
    return "\n\n".join(parts), len(qs)


batch, count, n = [], 0, 0
only = {int(x) for x in os.environ["TRIM_ROWS"].split(",")} if os.environ.get("TRIM_ROWS") else None
for ri in range(len(rows)):
    if only is not None and ri not in only:
        continue
    text, k = topic(ri)
    if not k:
        continue
    if batch and count + k > limit:
        open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n, batch, count = n + 1, [], 0
    batch.append(text)
    count += k
if batch:
    open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
    n += 1
print(f"book {book}: {sum(len(v) for v in mcq['rows'].values())} MCQs in {n} batches")
