"""Whole topics (rows) as batch files, for reorganising each topic's subsections (guide: tools/topic_guide.md).

    python3 tools/topic_export.py <book> [words per batch=6000] [rows e.g. 0-4]
writes work/topic/b<book>/in_NNN.md:
    === ROW <row> | <topic title>
    ## S<sec> | <subsection title>          (" | universal" on the Universal angles page)
    <the page in markdown form, tables written out>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

def topic(ri, r):
    parts = [f"=== ROW {ri} | {r['title']}"]
    for si, s in enumerate(r["secs"]):
        md, _ = from_blocks(s["b"], inline_tables=True)
        parts.append(f"## S{si} | {s['t']}" + (" | universal" if "u" in s else "") + "\n" + md.strip())
    return "\n\n".join(parts)


if __name__ == "__main__":
    book = int(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    only = None
    if len(sys.argv) > 3:
        a, _, b = sys.argv[3].partition("-")
        only = range(int(a), int(b or a) + 1)
    d = json.load(open(f"app/src/main/assets/book{book}.json"))
    out = f"work/topic/b{book}"
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("in_"):
            os.remove(f"{out}/{f}")


    rows = [r for u in d["units"] for r in u["rows"]]
    done = json.load(open(f"{out}/imported.json")) if os.path.exists(f"{out}/imported.json") else {}
    batch, words, n = [], 0, 0
    for ri, r in enumerate(rows):
        if (only is not None and ri not in only) or str(ri) in done:
            continue
        t = topic(ri, r)
        w = len(t.split())
        if batch and words + w > limit:
            open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
            n, batch, words = n + 1, [], 0
        batch.append(t)
        words += w
    if batch:
        open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n += 1
    print(f"book {book}: {n} batches")
