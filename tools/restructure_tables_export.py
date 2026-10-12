"""Pages whose tables repeat each other (same topic tabled twice), as batches for merging.

    python3 tools/restructure_tables_export.py [words per batch]
writes work/restructure/t<book>/in_NNN.md with the tables written out as markdown tables
(tools/structured_md.py); rewrite with tools/restructure_tables_guide.md, check and import with
RS_PREFIX=t tools/restructure_check.py / tools/restructure_import.py.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5000


def t(cell):
    s = "".join(r[0] for r in cell) if isinstance(cell, list) else str(cell)
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", s).lower()).strip()


def overlapping(blocks):
    ts = []
    for b in blocks:
        if b["k"] != "t":
            continue
        keys = {t(r[0]) for r in b["r"] if r and t(r[0])}
        words = set(" ".join(t(c) for r in b["r"] for c in r).split())
        ts.append((keys, words))
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            (a, wa), (b, wb) = ts[i], ts[j]
            if a and b and (len(a & b) / min(len(a), len(b)) >= 0.5 or len(wa & wb) / max(1, min(len(wa), len(wb))) >= 0.6):
                return True
    return False


total = 0
for book in range(1, 7):
    d = json.load(open(f"app/src/main/assets/book{book}.json"))
    out = f"work/restructure/t{book}"
    os.makedirs(out, exist_ok=True)
    pages, row = [], 0
    for u in d["units"]:
        for r in u["rows"]:
            for si, s in enumerate(r["secs"]):
                if overlapping(s["b"]):
                    pages.append(f"=== {book}:{row}:{si} | {s['t']}\n" + from_blocks(s["b"], True)[0])
            row += 1
    batch, words, n = [], 0, 0
    for p in pages:
        batch.append(p)
        words += len(p.split())
        if words >= limit:
            open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
            n, batch, words = n + 1, [], 0
    if batch:
        open(f"{out}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n += 1
    total += len(pages)
    print(f"book {book}: {len(pages)} pages in {n} batches")
print("total", total)
