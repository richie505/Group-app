"""Applies checked dedup decisions (work/dedup/out_*.md) to the notes.

    python3 tools/dedup_import.py [--dry]
For each cluster that passes tools/dedup_check.py and whose units still read as exported: dropped units leave
their page, a kept unit with an "N" text is rewritten, and every page that lost a unit gets an "Also covered
in" link (cov) to the page that kept the fact. Headings left with nothing under them, and empty tables, go.
A page is never emptied: if a page would lose all its content, its units stay. Pages keep their ids, so read
marks, bookmarks and MCQ filing do not move. Run build_key_terms.py / build_revision.py afterwards.
"""
import glob, json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from dedup_check import parse_in, parse_out, check
from dedup_export import units_of
from structured_md import to_blocks, runs

A = "app/src/main/assets"
D = os.environ.get("DEDUP_DIR", "work/dedup")
dry = "--dry" in sys.argv

books = {b: json.load(open(f"{A}/book{b}.json")) for b in range(1, 7)}
rows = {b: [r for u in n["units"] for r in u["rows"]] for b, n in books.items()}


def page(uid):
    b, r, s = uid.split(":")[:3]
    return int(b), int(r), int(s)


current = {}
for b in rows:
    for ri, r in enumerate(rows[b]):
        for si, s in enumerate(r["secs"]):
            for uid, md, _ in units_of(b, ri, si, s):
                current[uid] = md

drop, replace, links, applied, stale = set(), {}, defaultdict(set), 0, 0
for f in sorted(glob.glob(f"{D}/out_*.md")):
    n = f[-6:-3]
    src = parse_in(open(f"{D}/in_{n}.md").read())
    dec, _ = parse_out(open(f).read())
    for c, units in src.items():
        d = dec.get(c)
        if not d or d["all"] or check(units, d):
            continue
        if any(current.get(u) != md for u, md in units.items()):
            stale += 1
            continue
        homes = {page(u) for u in d["keep"]}
        for u in units:
            if u not in d["keep"]:
                drop.add(u)
                for h in homes:
                    if h[:2] != page(u)[:2]:
                        links[page(u)].add(h)
        for u, lines in d["new"].items():
            replace[u] = lines
        applied += 1

# group by page, apply bottom-up
by_page = defaultdict(list)
for u in drop | set(replace):
    by_page[page(u)].append(u)
kept_back = 0
for (b, ri, si), us in by_page.items():
    sec = rows[b][ri]["secs"][si]
    bl = sec["b"]
    spans = {}   # block index -> end index (bullet groups)
    for uid, _, _ in units_of(b, ri, si, sec):
        last = uid.split(":")[3]
        if "." not in last:
            i = int(last)
            j = i + 1
            while j < len(bl) and bl[j].get("k") == "s" and bl[i].get("k") != "x":
                j += 1
            spans[i] = j
    new_bl = [dict(x) for x in bl]
    remove_blocks, remove_rows, new_rows, new_groups = set(), defaultdict(set), {}, {}
    for u in us:
        last = u.split(":")[3]
        if "." in last:
            i, r = map(int, last.split("."))
            if u in drop:
                remove_rows[i].add(r)
            else:
                cells = replace[u][0].strip().strip("|").split(" | ")
                new_rows[(i, r)] = [runs(c.strip()) for c in cells]
        else:
            i = int(last)
            if u in drop:
                remove_blocks |= set(range(i, spans[i]))
            else:
                new_groups[i] = (spans[i], to_blocks("\n".join(replace[u]), []))
    out = []
    i = 0
    while i < len(new_bl):
        if i in new_groups:
            end, blocks = new_groups[i]
            out += blocks
            i = end
            continue
        if i in remove_blocks:
            i += 1
            continue
        x = new_bl[i]
        if x.get("k") == "t":
            rr = [new_rows.get((i, r), row) for r, row in enumerate(x["r"]) if r not in remove_rows[i]]
            if rr:
                x = dict(x, r=rr)
                out.append(x)
            i += 1
            continue
        out.append(x)
        i += 1
    # headings with nothing under them
    clean = [x for k, x in enumerate(out) if not (x.get("k") == "h" and (k + 1 == len(out) or out[k + 1].get("k") == "h"))]
    if not any(x.get("k") != "h" for x in clean):
        kept_back += 1
        links.pop((b, ri, si), None)
        continue
    sec["b"] = clean
for (b, ri, si), homes in links.items():
    sec = rows[b][ri]["secs"][si]
    cov = [list(c) for c in sec.get("cov", [])]
    for h in sorted(homes):
        if list(h) not in cov:
            cov.append(list(h))
    sec["cov"] = cov

words = lambda: sum(len(json.dumps(r["secs"], ensure_ascii=False)) for b in rows for r in rows[b])
print(f"clusters applied {applied}, stale {stale}; units dropped {len(drop)}, rewritten {len(replace)}; "
      f"pages linked {len(links)}; pages kept whole {kept_back}")
if not dry:
    for b, n in books.items():
        json.dump(n, open(f"{A}/book{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
