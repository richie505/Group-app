"""Puts reorganised topics (work/topic/b<book>/out_*.md, passing tools/topic_check.py) into the app.

    python3 tools/topic_import.py <book> [--dry]
For each topic whose input still matches the shipped notes:
  * book<book>.json: the topic's subsections replaced (badges/page/cov/o carried from the "from:" sources);
  * mcq<book>.json "subs": each MCQ re-filed to the new subsection (among those its old one went into) whose
    text shares most words with it;
  * moved.json (v = VERSION): every subsection id as shipped in the last release -> its new id, so read marks,
    bookmarks and the last position move (ProgressStore.migrate); repeated runs compose;
  * notemoves.json: a round moving the reader's own notes under gap lines ("b:r:s#block") to their new place;
  * cov refs in every book, index.json subsection counts. Run tools/build_key_terms.py afterwards.
"""
import glob, hashlib, json, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import to_blocks
from notes_fix import plain_cells, text
from topic_check import topics, parse_head, check

VERSION = os.environ.get("IDS_VERSION", "2.55")
A = os.environ.get("MERGE_ASSETS", "app/src/main/assets")
# MERGE=1: the batch is a merge of ROCKET blocks into the topic (tools/merge_guide.md, checked by merge_check.py)
MERGE = bool(os.environ.get("MERGE"))
book = int(sys.argv[1])
dry = "--dry" in sys.argv
d = os.environ.get("TOPIC_DIR", "work/topic") + f"/b{book}"
done_path = f"{d}/imported.json"
imported = json.load(open(done_path)) if os.path.exists(done_path) else {}

notes = json.load(open(f"{A}/book{book}.json"))
rows = [r for u in notes["units"] for r in u["rows"]]
from topic_export import topic as export_topic  # the same text the agents were given


def words(s):
    return Counter(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2)


def sec_text(s):
    return " ".join(text(b) for b in s["b"])


idmap, notemap, applied, sources = {}, {}, [], {}
for f in sorted(glob.glob(f"{d}/out_*.md")):
    n = f[-6:-3]
    in_text, out_text = open(f"{d}/in_{n}.md").read(), open(f).read()
    if MERGE:
        import merge_check
        merged_in, back = merge_check.split_in(in_text), merge_check.not_here(out_text)
        in_text = re.sub(r"(?ms)^=== ROCKET\n.*?(?=^=== ROW |\Z)", "", in_text)
        out_text = re.sub(r"(?m)^=== NOT HERE:.*$", "", out_text)
    old_t, new_t = topics(in_text), topics(out_text)
    for ri, new in new_t.items():
        if ri not in old_t:
            continue
        if (merge_check.check(merged_in[ri], new, back.get(ri, set())) if MERGE else check(old_t[ri], new)):
            continue
        r = rows[ri]
        src = open(f"{d}/in_{n}.md").read()
        cur = export_topic(ri, r)
        if f"=== ROW {ri} | " not in src or cur.strip() not in src:
            continue  # notes changed since export (or already imported)
        olds = r["secs"]
        new_secs = []
        for head, body in new[1]:
            title, frm, universal = parse_head(head)
            srcs = [olds[k] for k in frm]
            # a merged page may come from ROCKET blocks only: no Prep page behind it
            s = {"t": title, "badges": list(dict.fromkeys(b for x in srcs for b in x.get("badges", []))),
                 "p": min((x.get("p", 0) for x in srcs), default=0), "b": [plain_cells(b) for b in to_blocks(body, [])],
                 "o": srcs[0].get("o", f"{book}:{ri}:{frm[0]}") if srcs else f"{book}:{ri}:rocket"}
            cov = [c for x in srcs for c in x.get("cov", [])]
            cov = [list(c) for c in dict.fromkeys(tuple(c) for c in cov) if not (c[0] == book and c[1] == ri)]
            if cov:
                s["cov"] = cov
            if universal:
                s["u"] = 1
            new_secs.append((s, frm))
        # where each old subsection went: the new page holding most of its words
        nw = [words(sec_text(s)) for s, _ in new_secs]
        primary = {}
        for k, o in enumerate(olds):
            ow = words(sec_text(o))
            cands = [j for j, (_, frm) in enumerate(new_secs) if k in frm]
            primary[k] = max(cands, key=lambda j: sum(min(c, nw[j][w]) for w, c in ow.items()))
        for k in range(len(olds)):
            idmap[f"{book}:{ri}:{k}"] = f"{book}:{ri}:{primary[k]}"
        # a new page counts as read when every old page it was made from was read
        for j, (_, frm) in enumerate(new_secs):
            sources[f"{book}:{ri}:{j}"] = [f"{book}:{ri}:{k}" for k in frm]
        # gap lines: old key -> new key, matched by their text in order
        where = defaultdict(list)
        for j, (s, _) in enumerate(new_secs):
            for bi, b in enumerate(s["b"]):
                if b["k"] != "t" and any(x[1] == 6 for x in b["x"]):
                    where[text(b)].append(f"{book}:{ri}:{j}#{bi}")
        for k, o in enumerate(olds):
            for bi, b in enumerate(o["b"]):
                if b["k"] != "t" and isinstance(b["x"], list) and any(x[1] == 6 for x in b["x"]) and where.get(text(b)):
                    to = where[text(b)].pop(0)
                    if to != f"{book}:{ri}:{k}#{bi}":
                        notemap[f"{book}:{ri}:{k}#{bi}"] = to
        r["secs"] = [s for s, _ in new_secs]
        applied.append((ri, primary, [frm for _, frm in new_secs], nw))
        imported[str(ri)] = hashlib.sha1(cur.encode()).hexdigest()[:12]

if not applied:
    print(f"book {book}: nothing to import")
    sys.exit(0)

# MCQs: re-file to the new page (among those the old one went into) sharing most words
mcq = json.load(open(f"{A}/mcq{book}.json"))
moved_q = 0
for ri, primary, froms, nw in applied:
    qs, subs = mcq["rows"].get(str(ri), []), mcq["subs"].get(str(ri), [])
    for i, (q, k) in enumerate(zip(qs, subs)):
        if k < 0 or k not in primary:
            continue
        qw = words(q["s"] + " " + q["o"][q["a"]] + " " + q.get("x", ""))
        cands = [j for j, frm in enumerate(froms) if k in frm]
        best = max(cands, key=lambda j: (sum(min(c, nw[j][w]) for w, c in qw.items()), j == primary[k]))
        subs[i] = best
        moved_q += best != k

# cov refs in every book
moves = {tuple(map(int, a.split(":"))): tuple(map(int, b.split(":"))) for a, b in idmap.items()}
books = {}
for b in range(1, 7):
    bd = notes if b == book else json.load(open(f"{A}/book{b}.json"))
    changed = False
    for u in bd["units"]:
        for r in u["rows"]:
            for s in r["secs"]:
                if "cov" in s:
                    new = [list(moves.get(tuple(c), tuple(c))) for c in s["cov"]]
                    new = [list(c) for c in dict.fromkeys(tuple(c) for c in new)]
                    if new != s["cov"]:
                        s["cov"], changed = new, True
    if b == book or changed:
        books[b] = bd

# moved.json: shipped (last release) id -> new id, composed over runs
mv = json.load(open(f"{A}/moved.json"))
base = mv["m"] if mv.get("v") == VERSION else {}
composed = {k: idmap.get(v, v) for k, v in base.items()}
composed.update({k: v for k, v in idmap.items() if k not in composed})
composed = {k: v for k, v in composed.items() if k != v}
rsrc = dict(mv.get("r", {})) if mv.get("v") == VERSION else {}
rsrc.update(sources)
mvnew = {"v": VERSION, "m": composed, "g": [], "r": rsrc}

nm = json.load(open(f"{A}/notemoves.json"))
if notemap:
    nm.append({"id": f"topic-b{book}-{len([x for x in nm if x['id'].startswith(f'topic-b{book}-')]) + 1}", "m": notemap})

index = json.load(open(f"{A}/index.json"))
for ri, _, froms, _ in applied:
    index["books"][book - 1]["rows"][ri]["n"] = len(froms)

print(f"book {book}: {len(applied)} topics imported; MCQs re-filed {moved_q}; note keys moved {len(notemap)}; "
      f"subsections {sum(len(p) for _, p, _, _ in applied)} -> {sum(len(f) for _, _, f, _ in applied)}")
if dry:
    sys.exit(0)
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
for b, bd in books.items():
    open(f"{A}/book{b}.json", "w").write(dump(bd))
open(f"{A}/mcq{book}.json", "w").write(dump(mcq))
open(f"{A}/moved.json", "w").write(dump(mvnew))
open(f"{A}/notemoves.json", "w").write(dump(nm))
open(f"{A}/index.json", "w").write(dump(index))
json.dump(imported, open(done_path, "w"))
