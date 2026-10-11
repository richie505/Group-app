"""Puts rewritten pages (work/restructure/b<book>/out_*.md) into app/src/main/assets/book<book>.json.

    python3 tools/restructure_import.py 2
Only pages that pass tools/restructure_check.py are taken. The reader's own notes are keyed by the index of the
gap line they fill ("2:61:0#8"); gap lines move in the rewrite, so each run adds a round of old -> new keys to
app/src/main/assets/notemoves.json (the app applies each round once, ProgressStore.migrateNotes). A page is
imported once: pages that no longer match their exported input are left alone.
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks, to_blocks
from restructure_check import pages, problems

book = int(sys.argv[1])
path = f"app/src/main/assets/book{book}.json"
d = json.load(open(path))
secs = {}
row = 0
for u in d["units"]:
    for r in u["rows"]:
        for si, s in enumerate(r["secs"]):
            secs[f"{book}:{row}:{si}"] = s
        row += 1

mpath = "app/src/main/assets/notemoves.json"
rounds = json.load(open(mpath)) if os.path.exists(mpath) else []
moved = {}


def gap_text(b):
    x = b.get("x")
    t = x if isinstance(x, str) else "".join(r[0] for r in (x or []))
    return t.strip() if t.strip().startswith("Not in your sources") else None


done = skipped = 0
for f in sorted(glob.glob(f"work/restructure/b{book}/out_*.md")):
    n = f[-6:-3]
    old = pages(open(f"work/restructure/b{book}/in_{n}.md").read())
    for pid, (head, md) in pages(open(f).read()).items():
        if pid not in old or pid not in secs or problems(old[pid][1], md):
            skipped += 1
            continue
        s = secs[pid]
        if from_blocks(s["b"])[0].strip() != old[pid][1].strip():
            continue  # already imported
        _, tables = from_blocks(s["b"])
        new = to_blocks(md, tables)
        gaps_old = {i: gap_text(b) for i, b in enumerate(s["b"]) if gap_text(b)}
        gaps_new = {}
        for i, b in enumerate(new):
            g = gap_text(b)
            if g:
                gaps_new.setdefault(g, i)
        for i, g in gaps_old.items():
            if g in gaps_new and gaps_new[g] != i:
                moved[f"{pid}#{i}"] = f"{pid}#{gaps_new[g]}"
        s["b"] = new
        done += 1

json.dump(d, open(path, "w"), ensure_ascii=False, separators=(",", ":"))
if moved:
    rounds.append({"id": f"b{book}-{len(rounds) + 1}", "m": moved})
json.dump(rounds, open(mpath, "w"), ensure_ascii=False, separators=(",", ":"))
print(f"book {book}: {done} pages rewritten, {skipped} skipped (failed the check); {len(moved)} note keys moved")
