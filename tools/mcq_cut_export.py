"""MCQ coverage check (2.47): every very important fact of each page tested by an MCQ; repeats, off-notes and
trivia dropped; gaps filled with new MCQs (tools/mcq_cut_guide.md). No quota.

    python3 tools/mcq_cut_export.py <book> [MCQs per batch=450]
writes work/mcqcut/b<book>/in_NNN.md: each topic, each page's notes and its MCQs labelled
Q<row>.<index>. An agent answers in out_NNN.jsonl (tools/mcq_cut_guide.md), checked by
tools/mcq_cut_check.py, applied by tools/mcq_cut_import.py.
"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks
from notes_fix import text

A = "app/src/main/assets"
RATE = {"HIGH": 4, "MED": 3, "LIGHT": 2}
SCALE = 120


def priorities():
    plan = json.load(open(f"{A}/plan.json"))
    return {tuple(r["ref"]): r.get("pri") for d in plan["days"] for r in d.get("rows", []) if r.get("ref")}


def targets(book, rows, mcq, pri=None):
    """{(row, sec): target}; sec -1 = MCQs filed under the whole topic."""
    pri = pri if pri is not None else priorities()
    out = {}
    for ri, r in enumerate(rows):
        rate = RATE.get(pri.get((book, ri)), 2)
        for si, s in enumerate(r["secs"]):
            w = len(" ".join(text(b) for b in s["b"]).split())
            out[(ri, si)] = max(1, round(rate * max(0.5, min(2.0, w / SCALE))))
        out[(ri, -1)] = rate
    return out


def question(label, q):
    lines = [f"[{label}] {q['s']}"]
    lines += [f"  {'ABCD'[i]}) {o}" for i, o in enumerate(q["o"])]
    lines.append(f"  ANSWER: {'ABCD'[q['a']]}")
    if q.get("x"):
        lines.append(f"  WHY: {q['x']}")
    return "\n".join(lines)


if __name__ == "__main__":
    book = int(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    notes = json.load(open(f"{A}/book{book}.json"))
    mcq = json.load(open(f"{A}/mcq{book}.json"))
    rows = [r for u in notes["units"] for r in u["rows"]]
    tg = targets(book, rows, mcq)
    out = f"work/mcqcut/b{book}"
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("in_"):
            os.remove(f"{out}/{f}")

    def topic(ri):
        r, qs, subs = rows[ri], mcq["rows"].get(str(ri), []), mcq["subs"].get(str(ri), [])
        if not qs:
            return "", 0
        under = {}
        for j, s in enumerate(subs):
            under.setdefault(s, []).append(j)
        parts = [f"=== ROW {ri} | {r['title']}"]
        if -1 in under:
            parts.append("## SUB -1 | whole topic (no single page)")
            parts += [question(f"Q{ri}.{j}", qs[j]) for j in under[-1]]
        for si, s in enumerate(r["secs"]):
            md, _ = from_blocks(s["b"], inline_tables=True)
            js = under.get(si, [])
            parts.append(f"## SUB {si} | {s['t']}\n--- notes ---\n{md}\n--- MCQs ({len(js)}) ---")
            parts += [question(f"Q{ri}.{j}", qs[j]) for j in js]
        return "\n\n".join(parts), len(qs)

    batch, count, n = [], 0, 0
    for ri in range(len(rows)):
        t, k = topic(ri)
        if not k:
            continue
        if batch and count + k > limit:
            open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
            n, batch, count = n + 1, [], 0
        batch.append(t)
        count += k
    if batch:
        open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n += 1
    cnt = Counter((int(ri), s) for ri, ss in mcq["subs"].items() for s in ss)
    print(f"book {book}: {sum(cnt.values())} MCQs, {n} batches")
