"""Group 2 app notes of one topic as plain text, for writing its infographic.
    python3 tools/infonotes.py B J      (book 1-6, row index as in data/infographics/jobs/job-N.txt)"""
import json, sys

def tx(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "".join(tx(t[0]) if isinstance(t, list) and t and not isinstance(t[0], list) else tx(t) for t in x)
    return str(x)

b, j = int(sys.argv[1]), int(sys.argv[2])
bk = json.load(open(f"app/src/group2/assets/book{b}.json"))
rows = [r for u in bk["units"] for r in u["rows"]]
r = rows[j]
print(f"# {r['title']}")
for s in r["secs"]:
    print(f"\n## {s['t']}")
    for blk in s["b"]:
        k = blk.get("k")
        if k == "h":
            print(f"### {tx(blk['x'])}")
        elif k in ("b", "x", "s"):
            print(("- " if k == "b" else "  ") + tx(blk.get("x", "")))
        elif k == "t":
            print("| " + " | ".join(tx(c) for c in (blk.get("h") or [])) + " |")
            for row in blk.get("r") or []:
                print("| " + " | ".join(tx(c) for c in row) + " |")
