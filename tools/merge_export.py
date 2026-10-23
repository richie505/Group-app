"""Prep topics with the ROCKET-sheet blocks that belong to them, for merging (guide: tools/merge_guide.md).

    python3 tools/merge_export.py <book> [rows e.g. 8-14] [words per batch=9000]
reads work/merge/rocket_map.json (tools/merge_map.py) and the new app's notes ($MERGE_ASSETS, default
app/src/complete/assets); writes $TOPIC_DIR (default work/merge)/b<book>/in_NNN.md:
    === ROW <row> | <topic title>
    ## S<k> | <Prep page title>                   (the Prep pages, as tools/topic_export.py writes them)
    <page>
    === ROCKET
    ## R<n> | <ROCKET sheet / page>   -> S<k>      (the Prep page it matched best)
    <block>
Only topics with at least one ROCKET block are written.
"""
import json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from topic_export import topic

A = os.environ.get("MERGE_ASSETS", "app/src/complete/assets")


def main():
    book = int(sys.argv[1])
    only = None
    if len(sys.argv) > 2 and sys.argv[2] != "all":
        only = set()
        for part in sys.argv[2].split(","):
            a, _, b = part.partition("-")
            only |= set(range(int(a), int(b or a) + 1))
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 9000
    notes = json.load(open(f"{A}/book{book}.json"))
    rows = [r for u in notes["units"] for r in u["rows"]]
    by_row = defaultdict(list)
    for x in json.load(open("work/merge/rocket_map.json")):
        if x["to"][0] == book:
            by_row[x["to"][1]].append(x)
    d = os.environ.get("TOPIC_DIR", "work/merge") + f"/b{book}"
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith("in_"):
            os.remove(f"{d}/{f}")
    # topics already merged (the pilot, or an earlier run) are not exported again
    skip = set()
    for f in [f"{d}/imported.json", f"{d}_pilot/imported.json"]:
        if os.path.exists(f):
            skip |= {int(k) for k in json.load(open(f))}
    batches, cur, words = [], [], 0
    for ri, r in enumerate(rows):
        if (only is not None and ri not in only) or not by_row.get(ri) or ri in skip:
            continue
        rk = [f"## R{n} | {x['title']} -> S{x['to'][2]}\n{x['md'].strip()}" for n, x in enumerate(by_row[ri])]
        text = topic(ri, r) + "\n\n=== ROCKET\n\n" + "\n\n".join(rk)
        w = len(text.split())
        if cur and words + w > limit:
            batches.append(cur)
            cur, words = [], 0
        cur.append(text)
        words += w
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches):
        open(f"{d}/in_{i:03d}.md", "w").write("\n\n".join(b) + "\n")
    print(f"book {book}: {sum(len(b) for b in batches)} topics in {len(batches)} batches -> {d}")


if __name__ == "__main__":
    main()
