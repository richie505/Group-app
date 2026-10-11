"""Splits a book's pages into batch files (markdown form, tools/structured_md.py) for rewriting.

    python3 tools/restructure_export.py 2 [words per batch]
writes work/restructure/b2/in_NNN.md; each page starts with "=== book:row:sec | title".
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

book = int(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
d = json.load(open(f"app/src/main/assets/book{book}.json"))
out = f"work/restructure/b{book}"
os.makedirs(out, exist_ok=True)
pages, row = [], 0
for u in d["units"]:
    for r in u["rows"]:
        for si, s in enumerate(r["secs"]):
            if any(b["k"] == "h" for b in s["b"]):
                continue  # already structured
            md, _ = from_blocks(s["b"])
            pages.append((f"{book}:{row}:{si}", s["t"], md))
        row += 1
batch, words, n = [], 0, 0
def flush():
    global batch, words, n
    if batch:
        open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n += 1
    batch, words = [], 0
for pid, title, md in pages:
    batch.append(f"=== {pid} | {title}\n{md}")
    words += len(re.findall(r"\S+", md))
    if words >= limit:
        flush()
flush()
print(len(pages), "pages in", n, "batches")
