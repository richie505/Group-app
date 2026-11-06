"""APPSC Complete's notes rebuilt to the blueprint (data/blueprint/APPSC_Notes_Blueprint.md): one topic per
blueprint unit (the app topics of a unit merged), one page per numbered section of the unit as written
(data/blueprint/out/<unit>.md, tools/blueprint_md.py). Current-affairs units keep one topic per period: their
writers wrote one file per app topic (<unit>-<k>.md, k = 1.. in the unit's topic order).

Writes app/src/complete/assets: book*.json, index.json, mcq*.json (every MCQ moved to its unit's topic and to the
page that holds its answer), keyterms.json, exams.json, empty.json, moved.json (old page ids -> new, so read marks
and bookmarks move); and app/src/complete/mcqnotes/book*.json (the same notes: one set of notes now). The old
notes are kept in data/blueprint/before/ the first time it runs. Then run tools/blueprint_plan.py.

    python3 tools/blueprint_build.py [--allow-missing] [--out DIR]   (DIR: write there instead, to try it)
"""
import collections
import json
import math
import os
import re
import shutil
import sys

sys.path.insert(0, "tools")
from blueprint_md import unit_pages  # noqa: E402
from blueprint_src import units  # noqa: E402

A = "app/src/complete/assets"
N = "app/src/complete/mcqnotes"
OUT = "data/blueprint/out"
BEFORE = "data/blueprint/before"
ARG_OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
CA_UNITS = {f"U{n:04d}" for n in range(812, 830)}
TIER = {}

# keep the notes as they were, once
if not os.path.exists(f"{BEFORE}/index.json"):
    os.makedirs(BEFORE, exist_ok=True)
    for f in os.listdir(A):
        shutil.copy(f"{A}/{f}", f"{BEFORE}/{f}")
    os.makedirs(f"{BEFORE}/mcqnotes", exist_ok=True)
    for f in os.listdir(N):
        shutil.copy(f"{N}/{f}", f"{BEFORE}/mcqnotes/{f}")

if ARG_OUT:
    A, N = f"{ARG_OUT}/assets", f"{ARG_OUT}/mcqnotes"
    os.makedirs(A, exist_ok=True)
    os.makedirs(N, exist_ok=True)
bp = units("data/blueprint/APPSC_Notes_Blueprint.md")
for u, (body, _) in bp.items():
    m = re.search(r"\*\*Tier:\*\* (\w+)", body)
    TIER[u] = m.group(1) if m else "LOW"
# the old topics: from the notes as they were
idx0 = J(f"{BEFORE}/index.json")
code_rows = {}
for b in idx0["books"]:
    for ri, r in enumerate(b["rows"]):
        for c in r["codes"]:
            code_rows.setdefault(c, []).append((b["id"], ri))
row_unit = {}
for u, (body, codes) in bp.items():
    if TIER.get(u) == "APT":
        continue
    for c in codes:
        for k in code_rows.get(c, []):
            row_unit.setdefault(k, u)
unit_rows = collections.defaultdict(list)
for k, u in sorted(row_unit.items()):
    unit_rows[u].append(k)

allow_missing = "--allow-missing" in sys.argv
missing = []


def text(rs):
    return "".join(r[0] for r in rs)


def block_text(x):
    if x.get("k") == "t":
        return " ".join(text(c) for row in [x.get("h", [])] + x.get("r", []) for c in row)
    return text(x.get("x", []))


def sec_text(s):
    return s["t"] + " " + " ".join(block_text(x) for x in s["b"])


STOP = set("""the a an and or of in on to for by with at from as is are was were be been this that which who whom
its it their his her not no yes all any each other than then into over under after before about also only
first last one two three four five six seven eight nine ten
following given correct incorrect statement statements consider which above below none both""".split())


def toks(t):
    return [w for w in re.findall(r"[a-z0-9]+", t.lower()) if (len(w) > 2 or w.isdigit()) and w not in STOP]


books0 = {b: J(f"{BEFORE}/book{b}.json") for b in range(1, 7)}
flat0 = {b: [r for u in books0[b]["units"] for r in u["rows"]] for b in range(1, 7)}


def old_pages(b, ri):
    """fallback for a unit not written yet: the topic's full-notes pages as they were"""
    r = flat0[b][ri]
    full = [s for s in r["secs"] if s.get("f")] or r["secs"]
    return [{"t": s["t"], "badges": [x for x in s.get("badges", []) if x != "Full notes"], "p": s.get("p", 0), "b": s["b"]}
            for s in full if s["b"]]


def written(name):
    p = f"{OUT}/{name}.md"
    if os.path.exists(p):
        title, pages = unit_pages(open(p).read())
        if pages:
            return title, pages
    return None


def merge_pyq(rows):
    g = collections.Counter()
    for r in rows:
        for k, n in re.findall(r"(G[12])\s+(\d+)", r.get("pyq", "") or ""):
            g[k] += int(n)
    return " + ".join(f"{k} {g[k]}" for k in ("G1", "G2") if g[k]) or rows[0].get("pyq", "")


def merge_tag(rows):
    tags = {r.get("tag", "") for r in rows}
    if any("GROUP-I +" in t for t in tags) or ({"GROUP-I", "GROUP-II"} <= tags):
        return "GROUP-I + GROUP-II"
    return rows[0].get("tag", "")


# --- the new topics, book by book, in the old order (a unit where its first topic was)
topic_of = {}      # (b, old ri) -> new ri
new_books = {}
new_index_rows = {}
tiers = {}
for b in range(1, 7):
    bk = books0[b]
    rows_out, units_out, seen = [], [], {}
    ib = idx0["books"][b - 1]
    for ri, r in enumerate(flat0[b]):
        u = row_unit.get((b, ri))
        if u in CA_UNITS:
            key = (u, ri)
        else:
            key = u or ("row", ri)
        if key in seen:
            topic_of[(b, ri)] = seen[key]
            rows_out[seen[key]]["_old"].append(ri)
            continue
        n = len(rows_out)
        seen[key] = n
        topic_of[(b, ri)] = n
        rows_out.append({"_key": key, "_old": [ri], "_u": ib["rows"][ri].get("u", 0)})
    for t in rows_out:
        key, olds = t["_key"], t["_old"]
        orow = [flat0[b][ri] for ri in olds]
        irow = [ib["rows"][ri] for ri in olds]
        if isinstance(key, tuple) and key[0] in CA_UNITS:
            u = key[0]
            name = f"{u}-{unit_rows[u].index((b, key[1])) + 1}"
        elif isinstance(key, str):
            u, name = key, key
        else:
            u, name = None, None
        got = written(name) if name else None
        if got:
            title, pages = got
            secs = [{"t": pt, "badges": [], "p": orow[0].get("p1", 0), "b": blocks} for pt, blocks in pages]
            if isinstance(key, tuple):
                title = orow[0]["title"]  # a current-affairs period keeps its own title
                if name.endswith("-1"):  # the first period now runs to 4 Nov 2026
                    title = title.replace("Sep–Oct 2026", "Sep–4 Nov 2026")
        else:
            if name:
                missing.append(name)
            title = orow[0]["title"]
            secs = [s for ri in olds for s in old_pages(b, ri)]
        codes = list(dict.fromkeys(c for r in irow for c in r["codes"]))
        tiers[(b, rows_out.index(t))] = TIER.get(u, "LOW") if u else "LOW"
        row = dict(orow[0], codes=codes, title=title, tag=merge_tag(irow), pyq=merge_pyq(irow),
                   p1=min(r.get("p1", 0) for r in irow), p2=max(r.get("p2", 0) for r in irow),
                   sub=[x for r in orow for x in (r.get("sub") or [])], src=[x for r in orow for x in (r.get("src") or [])],
                   secs=secs, tier=TIER.get(u, "LOW") if u else "LOW", unit=u or "")
        row.pop("see", None)
        t["row"] = row
        t["irow"] = dict(irow[0], codes=codes, title=title, tag=row["tag"], pyq=row["pyq"], p1=row["p1"], p2=row["p2"],
                         n=len(secs), tier=row["tier"])
    # units (syllabus units of the book): each new topic stays in its first old topic's unit
    unit_list = [dict(code=u["code"], title=u["title"]) for u in bk["units"]]
    grouped = collections.defaultdict(list)
    for t in rows_out:
        grouped[t["_u"]].append(t["row"])
    new_books[b] = dict(bk, units=[dict(unit_list[i], rows=grouped[i]) for i in range(len(unit_list)) if grouped[i]])
    # rows are numbered in the order the book lists them
    order = [t for i in range(len(unit_list)) for t in rows_out if t["_u"] == i]
    renum = {rows_out.index(t): k for k, t in enumerate(order)}
    for k in [k for k in topic_of if k[0] == b]:
        topic_of[k] = renum[topic_of[k]]
    used_units = [i for i in range(len(unit_list)) if grouped[i]]
    new_index_rows[b] = [dict(t["irow"], u=used_units.index(t["_u"])) for t in order]
    new_books[b]["_units_used"] = used_units

if missing and not allow_missing:
    sys.exit(f"{len(missing)} units not written yet, e.g. {missing[:8]} (use --allow-missing to build anyway)")

# --- MCQs: to the unit's topic, and to the page that holds the answer
moved_q = 0
answer_found = total_q = 0
for b in range(1, 7):
    m = J(f"{BEFORE}/mcq{b}.json")
    secs_of = {ri: r["secs"] for ri, r in enumerate(r for u in new_books[b]["units"] for r in u["rows"])}
    rows, subs = collections.defaultdict(list), collections.defaultdict(list)
    df = collections.Counter()
    sec_tok = {}
    for ri, secs in secs_of.items():
        sec_tok[ri] = [collections.Counter(toks(sec_text(s))) for s in secs]
        for c in sec_tok[ri]:
            df.update(set(c))
    nsec = sum(len(v) for v in sec_tok.values()) or 1
    idf = lambda w: math.log(1 + nsec / (1 + df[w]))
    for r, qs in sorted(m["rows"].items(), key=lambda kv: int(kv[0])):
        t = topic_of[(b, int(r))]
        for q in qs:
            ans = q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q["o"]) else ""
            qt = collections.Counter(toks(q["s"] + " " + q.get("x", "") + " " + " ".join(q.get("n") or [])))
            at = set(toks(ans))
            best, bi = 0.0, -1
            for si, c in enumerate(sec_tok[t]):
                sc = sum(idf(w) for w in qt if w in c) + 2.5 * sum(idf(w) for w in at if w in c)
                if sc > best:
                    best, bi = sc, si
            rows[str(t)].append(q)
            subs[str(t)].append(bi)
            total_q += 1
            if ans and bi >= 0 and at and all(w in sec_tok[t][bi] for w in at):
                answer_found += 1
            moved_q += 1
    W(f"{A}/mcq{b}.json", dict(m, rows=dict(rows), subs=dict(subs), units={}))
    for ri, row in enumerate(new_index_rows[b]):
        row["q"] = len(rows.get(str(ri), []))

# --- old page -> new page (read marks, bookmarks, the last page), and key terms
moved, keyterms = {}, {}
kt0 = J(f"{BEFORE}/keyterms.json")
for b in range(1, 7):
    flat = [r for u in new_books[b]["units"] for r in u["rows"]]
    for ri, r in enumerate(flat0[b]):
        t = topic_of[(b, ri)]
        new_secs = flat[t]["secs"]
        cs = [collections.Counter(toks(sec_text(s))) for s in new_secs]
        for si, s in enumerate(r["secs"]):
            old = f"{b}:{ri}:{si}"
            ot = set(toks(sec_text(s)))
            best = max(range(len(cs)), key=lambda i: sum(1 for w in ot if w in cs[i])) if cs else 0
            moved[old] = f"{b}:{t}:{best}"
            for term in kt0.get(old, []):
                tl = term.lower()
                where = next((i for i, s2 in enumerate(new_secs) if tl in sec_text(s2).lower()), best)
                lst = keyterms.setdefault(f"{b}:{t}:{where}", [])
                if term not in lst:
                    lst.append(term)

# --- write the notes and the index
for b in range(1, 7):
    bk = dict(new_books[b])
    bk.pop("_units_used")
    W(f"{A}/book{b}.json", bk)
    os.makedirs(N, exist_ok=True)
    W(f"{N}/book{b}.json", bk)
idx = dict(idx0)
idx["books"] = []
for b, ib in enumerate(idx0["books"], 1):
    used = new_books[b]["_units_used"]
    idx["books"].append(dict(ib, units=[ib["units"][i] for i in used], rows=new_index_rows[b],
                             uq=[0] * len(used) if isinstance(ib.get("uq"), list) else 0))
W(f"{A}/index.json", idx)
W(f"{A}/keyterms.json", keyterms)
W(f"{A}/empty.json", {"mcq": [], "full": []})
W(f"{A}/moved.json", {"v": "blueprint-1", "m": {k: v for k, v in moved.items() if k != v}})
ex = J(f"{BEFORE}/exams.json")
for e in ex:
    for s in e["subjects"]:
        tops = set()
        for g in s["groups"]:
            seen_r = []
            for bb, r in g["rows"]:
                k = [bb, topic_of[(bb, r)]]
                if k not in seen_r:
                    seen_r.append(k)
            g["rows"] = seen_r
            tops |= {tuple(k) for k in seen_r}
        pages = sum(idx["books"][bb - 1]["rows"][r]["n"] for bb, r in tops)
        s["sub"] = re.sub(r"\d+ topics · \d+ sections", f"{len(s['groups'])} topics · {pages} pages", s["sub"])
W(f"{A}/exams.json", ex)
json.dump({f"{b}:{ri}": t for (b, ri), t in topic_of.items()}, open("data/blueprint/topic_of.json", "w"))

topics_n = sum(len(b["rows"]) for b in idx["books"])
pages_n = sum(r["n"] for b in idx["books"] for r in b["rows"])
print(f"{topics_n} topics, {pages_n} pages; {total_q} MCQs moved, answer words on their page for "
      f"{answer_found * 100 // max(total_q, 1)}%; {len(missing)} units not written yet")
