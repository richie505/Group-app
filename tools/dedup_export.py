"""Facts said twice: groups of note lines that repeat across pages, in batches for review (guide: tools/dedup_guide.md).

    python3 tools/dedup_export.py [clusters per batch=40]
A "unit" is one bullet with its sub-bullets, one exam-angle line, or one table row. Units whose rare words
largely overlap (one is >= 60% contained in the other, >= 3 shared rare words) are linked; linked units form a
cluster. Writes $DEDUP_DIR (default work/dedup)/in_NNN.md and units.json (uid -> where it lives):
    === C<n>
    U <uid> | <topic> > <page>
    <the unit in markdown>
uid = book:row:sec:block (a bullet group / exam line) or book:row:sec:block.row (a table row).
"""
import json, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from notes_fix import text

A = "app/src/main/assets"
STOP = set("""the and with from that this which their they were have been into upon over under than then also about
for are was its not but has had per only both more most other such these those when where while will would after
before between first under during each india indian state states""".split())


def toks(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if (len(w) > 3 or w.isdigit()) and w not in STOP}


def run_md(runs):
    return "".join(f"**{t}**" if f == 1 else t for t, f in runs)


def cell_md(cell):
    return run_md(cell) if cell and isinstance(cell[0], list) else str(cell)


def units_of(book, ri, si, sec):
    """[(uid, markdown, plain text)]"""
    out, bl = [], sec["b"]
    i = 0
    while i < len(bl):
        b = bl[i]
        k = b.get("k")
        if k == "b" or (k == "s" and (i == 0 or bl[i - 1].get("k") not in ("b", "s"))):
            j = i + 1
            while j < len(bl) and bl[j].get("k") == "s":
                j += 1
            md = "\n".join(("- " if x.get("k") == "b" else "  - ") + run_md(x["x"]) for x in bl[i:j])
            if not any(f == 6 for x in bl[i:j] for _, f in x["x"]):   # gap lines stay where they are
                out.append((f"{book}:{ri}:{si}:{i}", md, " ".join(text(x) for x in bl[i:j])))
            i = j
            continue
        if k == "x" and not any(f == 6 for _, f in b["x"]):
            out.append((f"{book}:{ri}:{si}:{i}", "> " + run_md(b["x"]), text(b)))
        elif k == "t":
            head = "| " + " | ".join(cell_md(c) for c in b["h"]) + " |"
            for r, row in enumerate(b["r"]):
                md = "| " + " | ".join(cell_md(c) for c in row) + " |"
                out.append((f"{book}:{ri}:{si}:{i}.{r}", head + "\n" + md, " ".join(cell_md(c) for c in row).replace("**", "")))
        i += 1
    return out


def all_units():
    units, where = [], {}
    for book in range(1, 7):
        n = json.load(open(f"{A}/book{book}.json"))
        rows = [r for u in n["units"] for r in u["rows"]]
        for ri, r in enumerate(rows):
            for si, s in enumerate(r["secs"]):
                for uid, md, plain in units_of(book, ri, si, s):
                    units.append((uid, md, toks(plain)))
                    where[uid] = f"{r['title'][:70]} > {s['t'][:60]}"
    return units, where


def clusters(units):
    df = Counter(w for _, _, ts in units for w in ts)
    idx = defaultdict(list)
    for i, (_, _, ts) in enumerate(units):
        for w in ts:
            if df[w] <= 40:
                idx[w].append(i)
    parent = list(range(len(units)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, (_, _, ts) in enumerate(units):
        if len(ts) < 4:
            continue
        cand = Counter(j for w in ts if df[w] <= 40 for j in idx[w] if j > i)
        for j, c in cand.items():
            tj = units[j][2]
            if c < 3 or len(tj) < 4:
                continue
            if len(ts & tj) / min(len(ts), len(tj)) >= 0.6:
                parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i in range(len(units)):
        groups[find(i)].append(i)
    # a group spanning several units of one page only is a list, not a repeat; very large groups are topic hubs
    out = []
    for g in groups.values():
        pages = {units[i][0].rsplit(":", 1)[0] for i in g}
        if len(g) > 1 and len(pages) > 1 and len(g) <= 8:
            out.append(sorted(g, key=lambda i: units[i][0]))
    return sorted(out, key=lambda g: units[g[0]][0])


if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    d = os.environ.get("DEDUP_DIR", "work/dedup")
    os.makedirs(d, exist_ok=True)
    units, where = all_units()
    cl = clusters(units)
    json.dump({units[i][0]: where[units[i][0]] for g in cl for i in g}, open(f"{d}/units.json", "w"), ensure_ascii=False)
    for f in os.listdir(d):
        if f.startswith("in_"):
            os.remove(f"{d}/{f}")
    for b in range(0, len(cl), size):
        parts = []
        for n, g in enumerate(cl[b:b + size], start=b):
            parts.append(f"=== C{n}\n" + "\n".join(f"U {units[i][0]} | {where[units[i][0]]}\n{units[i][1]}" for i in g))
        open(f"{d}/in_{b // size:03d}.md", "w").write("\n\n".join(parts) + "\n")
    print(f"{len(cl)} clusters, {sum(len(g) for g in cl)} units, {(len(cl) + size - 1) // size} batches -> {d}")
