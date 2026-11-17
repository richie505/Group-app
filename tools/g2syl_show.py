"""Prints a Group 2 section's notes as structured markdown (tools/structured_md.py), for reading.

    python3 tools/g2syl_show.py <book> <group2 row>        e.g. python3 tools/g2syl_show.py 1 205
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

b, r = int(sys.argv[1]), int(sys.argv[2])
bk = json.load(open(f"app/src/group2/assets/book{b}.json"))
row = [x for u in bk["units"] for x in u["rows"]][r]
print(f"# SECTION {b}:{r} {row['title']}")
for s in row["secs"]:
    if s.get("empty") or not s["b"]:
        continue
    print(f"\n## {s['t']}")
    md = from_blocks(s["b"], inline_tables=True)
    print(md if isinstance(md, str) else md[0])
