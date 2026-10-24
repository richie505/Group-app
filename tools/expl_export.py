"""MCQs with their topic's notes, in batches, for writing structured explanations (guide: tools/expl_guide.md).

    python3 tools/expl_export.py <book> [MCQs per batch=45] [rows e.g. 0-4,9]
writes $EXPL_DIR (default work/expl)/b<book>/in_NNN.md:
    === ROW <row> | <topic title>
    ## S<sec> | <page title>
    <the page in markdown>
    === MCQS
    Q <id> | page S<sec>
    <stem>
    (1) <option> ... (4) <option>
    Answer: (<n>) <option>
    Old: <current one-line explanation>
A topic with more MCQs than the batch size is split; each part carries the topic's notes again.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from topic_export import topic

A = os.environ.get("EXPL_ASSETS", "app/src/main/assets")  # APPSC Complete: app/src/complete/assets


def q_text(q, sub):
    lines = [f"Q {q['id']} | page S{sub}" if sub >= 0 else f"Q {q['id']} | page -", q["s"].strip()]
    lines += [f"({i + 1}) {o}" for i, o in enumerate(q["o"])]
    if 0 <= q.get("a", -1) < len(q["o"]):
        lines.append(f"Answer: ({q['a'] + 1}) {q['o'][q['a']]}")
    if q.get("x"):
        lines.append(f"Old: {q['x']}")
    return "\n".join(lines)


def batches(book, size, only=None):
    notes = json.load(open(f"{A}/book{book}.json"))
    rows = [r for u in notes["units"] for r in u["rows"]]
    mcq = json.load(open(f"{A}/mcq{book}.json"))
    out, cur, n = [], [], 0
    for ri, r in enumerate(rows):
        if only is not None and ri not in only:
            continue
        qs = mcq["rows"].get(str(ri), [])
        subs = mcq["subs"].get(str(ri), [-1] * len(qs))
        # EXPL_MISSING=1: only MCQs without a structured explanation yet (APPSC Complete's ROCKET / CA app ones)
        keep = [i for i, q in enumerate(qs) if not (os.environ.get("EXPL_MISSING") and "xs" in q)]
        if not keep:
            continue
        parts = [keep[i:i + size] for i in range(0, len(keep), size)]
        for idx in parts:
            if n and n + len(idx) > size:
                out.append(cur); cur, n = [], 0
            cur.append(topic(ri, r) + "\n\n=== MCQS\n\n" + "\n\n".join(q_text(qs[i], subs[i]) for i in idx))
            n += len(idx)
    if cur:
        out.append(cur)
    return out


if __name__ == "__main__":
    book = int(sys.argv[1])
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    only = None
    if len(sys.argv) > 3:
        only = set()
        for part in sys.argv[3].split(","):
            a, _, b = part.partition("-")
            only |= set(range(int(a), int(b or a) + 1))
    d = os.environ.get("EXPL_DIR", "work/expl") + f"/b{book}"
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith("in_"):
            os.remove(f"{d}/{f}")
    bs = batches(book, size, only)
    for i, b in enumerate(bs):
        open(f"{d}/in_{i:03d}.md", "w").write("\n\n".join(b) + "\n")
    qre = re.compile(r"^Q \S+ [|] page", re.M)
    nq = sum(len(qre.findall(t)) for b in bs for t in b)
    print(f"book {book}: {len(bs)} batches, {nq} MCQs -> {d}")
