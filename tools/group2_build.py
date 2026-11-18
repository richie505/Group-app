"""APPSC Group 2: APPSC Complete cut down to the Group 2 syllabus (Screening and Mains), as its own app.

Takes the sections the Group 2 syllabus lists (exams.json, "Group 2") from APPSC Complete, with their notes (the
trimmed full notes and the MCQ notes), MCQs, key terms and hidden pages, renumbered as rows 0.. of each book, and
writes a fresh plan from TODAY to the exam (same phases and priorities as APPSC Complete's plan). Progress starts
fresh: no id moves from older versions.

    python3 tools/group2_build.py [start=2026-11-05]
    python3 tools/build_plan_mcq.py app/src/group2/assets
"""
import datetime as dt
import json
import os
import sys

C = "app/src/complete/assets"
# the MCQ notes APPSC Complete ships (mbook*.json): in simple English (tools/simple_build.py), else as written
C2 = "app/src/complete/mcqnotes" if os.path.exists("app/src/complete/mcqnotes/book1.json") else "app/src/complete2/assets"
G = "app/src/group2/assets"
START = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-11-05")
EXAM = dt.date(2027, 1, 24)
LAST = dt.date(2027, 1, 21)  # 22-23 Jan: the buffer
TIERS = ["HIGH", "MED", "LIGHT"]
ORDER = [2, 1, 4, 3, 5, 6]
os.makedirs(G, exist_ok=True)
for _b in range(1, 7):  # APPSC Complete no longer ships the MCQ notes, so Group 2 does not either
    if os.path.exists(f"{G}/mbook{_b}.json"): os.remove(f"{G}/mbook{_b}.json")
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))

import re

# --- Group 2 only: nothing of Group 1 shows (codes, tags, past-paper counts, sources, cited G1 papers, G1 PYQs)
G1REF = r"(?:APPSC[- ]?)?(?:G-?1|Group[- ]?(?:1|I)(?![I\w]))[ -]?(?:Mains |Prelims )?\**\d{4}\**(?:\s*(?:,|/|and|&)\s*\**\d{4}\**)*"


def no_g1(t):
    t = re.sub(r"\bG1,\s*G2 PYQ", "G2 PYQ", t)
    t = re.sub(r"\s*\((?:G1 Re-exam \d{4};\s*)?G1 PYQ(?:,\s*[^()]*)?\)", "", t)
    t = re.sub(r"\bG1 Re-exam \d{4};?\s*", "", t)
    t = re.sub(r";\s*G1 PYQ\b|\bG1 PYQ;\s*|\(G1 PYQ\)|\bG1 PYQ\b,?\s*", "", t)
    t = re.sub(r"\s*\(see [A-G]-\d+\)", "", t)  # cross-references to Group 1 topic codes
    t = re.sub(r"[,;]?\s*\bsee [A-G]-\d+\b", "", t)
    t = re.sub(r"APPSC[- ]?(?:G-?1|Group[- ]?1)\b", "APPSC", t)  # "APPSC Group-1 key: ..." -> "APPSC key: ..."
    t = re.sub(r"\s*\(\s*" + G1REF + r"[^()]*\)", "", t)  # "(APPSC-G1 2024, I and II correct)"
    t = re.sub(r"(?:(?<=^)|(?<=: ))" + G1REF + r"\s*[:\-–—]\s*", "", t)  # "APPSC-G1 2024: Avanti-Ujjain"
    t = re.sub(r"\s*;?\s*" + G1REF + r"\s*;?", "", t)
    return re.sub(r"\(\s*;\s*", "(", re.sub(r"\s{2,}", " ", t))


def clean_block(o):
    """every text run ([text, style]) in a block, at any depth, without Group 1 citations"""
    if isinstance(o, list):
        if len(o) >= 2 and isinstance(o[0], str) and isinstance(o[1], int):
            return [no_g1(o[0])] + o[1:]
        return [clean_block(x) for x in o]
    if isinstance(o, dict):
        return {k: (clean_block(v) if k not in ("k", "o") else v) for k, v in o.items()}
    return no_g1(o) if isinstance(o, str) else o


def g2_pyq(t):
    m = re.search(r"G2\s*(\d+)", t or "")
    return f"G2 {m.group(1)}" if m else ""


G1_PYQ = re.compile(r"group[- ]?(1|i)\b(?!i)|\bg-?1\b", re.I)
exams = J(f"{C}/exams.json")
g2 = next(e for e in exams if e["title"] == "Group 2")
# sections the blueprint did not tag for Group 2 but a Group 2 question can be set from (data/g2map/book*-map.json,
# each checked against the full Group 2 syllabus): added to their syllabus items, after the item's own sections
code_at = {g["code"]: (si, gi) for si, sj in enumerate(g2["subjects"]) for gi, g in enumerate(sj["groups"])}
EXTRA = {}
for b in range(1, 7):
    f = f"data/g2map/book{b}-map.json"
    if os.path.exists(f):
        for r, v in J(f).items():
            cs = [c for c in v.get("codes") or [] if c in code_at]
            if cs: EXTRA[(b, int(r))] = cs
for (b, r), cs in sorted(EXTRA.items()):
    for c in cs:
        si, gi = code_at[c]
        g = g2["subjects"][si]["groups"][gi]
        if [b, r] not in g["rows"]: g["rows"].append([b, r])
for sj in g2["subjects"]:
    n = len({tuple(x) for g in sj["groups"] for x in g["rows"]})
    sj["sub"] = re.sub(r"\d+ sections", f"{n} sections", sj["sub"])
g_title = {g["code"]: g["title"] for sj in g2["subjects"] for g in sj["groups"]}
codes, subj = {}, {}  # (book, row) -> its Group 2 syllabus codes; -> its first subject (index), item order
for si, sj in enumerate(g2["subjects"]):
    for gi, g in enumerate(sj["groups"]):
        for b, r in g["rows"]:
            codes.setdefault((b, r), []).append(g["code"])
            subj.setdefault((b, r), (si, gi))
# a section with codes from several subjects goes under its own book's subject (e.g. "AP location" in Geography,
# not under History because it also carries S1-92)
HOME = {1: ("S1", "M1-A"), 2: ("M1-B", "S3"), 3: ("M2-A",), 4: ("S2",), 5: ("M2-B",), 6: ("S4",)}
for k, cs in codes.items():
    home = [code_at[c] for c in cs if c in code_at and c.startswith(HOME[k[0]])]
    if home: subj[k] = min(home)
# --- built on the OFFICIAL APPSC syllabus (27-04-2023, data/g2syl/, tools/g2syl_lib.py): a section's codes are the
# official lines it teaches; it sits under its book's own official subject, in the order of the official lines;
# sections no official line covers go last, under "Beyond the official syllabus"
import g2syl_lib as SY
ckey = lambda k: f"{k[0]}:{k[1]}"
for k in list(subj):
    lv = SY.leaves_of(ckey(k))
    codes[k] = lv or ["X"]
    h = SY.home(k[0], lv)
    hs = SY.SUBJ_ORDER.index(h) if h in SY.SUBJ_ORDER else len(SY.SUBJ_ORDER)
    subj[k] = (hs, min((SY.ORDER[c] for c in lv if SY.subject_of(c) == h), default=0))
keep = sorted(subj)
new = {}  # (book, old row) -> new row: rows in the order of the Group 2 syllabus (subject, then item)
for b in range(1, 7):
    for i, k in enumerate(sorted([k for k in keep if k[0] == b], key=lambda k: (subj[k], k[1]))):
        new[k] = i
old_of = {v: k for k, v in new.items()}
BOOKS = {1: ("Indian History and Social & Cultural History of Andhra Pradesh", "History"),
         2: ("Indian Constitution and Indian Society", "Constitution & Society"),
         3: ("Indian & AP Economy", "Economy"), 4: ("Geography", "Geography"),
         5: ("Science & Technology", "Science & Tech"), 6: ("Current Affairs", "Current Affairs")}
UNIT = {si: {"code": s["code"], "title": f"{s['title']} ({'Prelims' if s['stage'] == 'Prelims' else 'Mains · ' + s['paper']})"}
        for si, s in enumerate(SY.TREE["subjects"])}
UNIT[len(SY.SUBJ_ORDER)] = {"code": "X", "title": "Beyond the official syllabus (kept for practice)"}


def g2_row(r, k):
    """a section's own fields, Group 2 only"""
    r = dict(r, codes=codes[k], tag="GROUP-II", pyq=g2_pyq(r.get("pyq")))
    # the official syllabus lines it teaches, in APPSC's words
    r["sub"] = [f"Official {c}: {SY.LEAF[c]['text']}" for c in codes[k] if c in SY.LEAF] or ["Beyond the official APPSC syllabus"]
    # notes written where an official line was thin (data/g2syl/depth-out-*.jsonl): extra subsections at the end
    adds = SY.added_secs(ckey(k))
    if "secs" in r:
        r["secs"] = list(r["secs"]) + [{kk: vv for kk, vv in a.items() if kk != "leaf"} for a in adds]
    elif "n" in r:
        r["n"] = r["n"] + len(adds)
    if "src" in r:
        r["src"] = [no_g1(x) for x in r["src"] if not x.startswith("Sources: Group-I:")]
    if "see" in r:
        r["see"] = [x for x in r["see"] if not re.search(r"\b[A-G]-\d+\b|Group-I\b", json.dumps(x))]
    if "secs" in r:
        r["secs"] = [dict(sec, t=no_g1(sec["t"]), b=[clean_block(x) for x in sec["b"]]) for sec in r["secs"]]
    return r
page = lambda pid: (lambda b, r, s: f"{b}:{new[(b, r)]}:{s}" if (b, r) in new else None)(*map(int, pid.split(":")))

# Group 2 row -> APPSC Complete row, for the official-syllabus data (data/g2syl/, keyed by Complete rows)
W("data/g2syl/rowmap.json", {f"{b}:{i}": [b, r] for (b, r), i in sorted(new.items(), key=lambda x: (x[0][0], x[1]))})
# --- notes: full (trimmed) and MCQ notes; units kept only where a row is left
idx = J(f"{C}/index.json")
for src, name in ((C, "book{}.json"),):  # one set of notes, like APPSC Complete (the old MCQ notes are not shipped)
    for b in range(1, 7):
        bk = J(f"{src}/book{b}.json")
        flat = [r for u in bk["units"] for r in u["rows"]]
        order = sorted([k for k in new if k[0] == b], key=lambda k: new[k])
        units = []
        for k in order:
            si = subj[k][0]
            if not units or units[-1][0] != si:
                units.append((si, []))
            units[-1][1].append(g2_row(flat[k[1]], k))
        W(f"{G}/{name.format(b)}", dict(bk, title=BOOKS[b][0], short=BOOKS[b][1],
                                         units=[dict(UNIT[si], rows=rows) for si, rows in units]))

ib = []
for b, book in enumerate(idx["books"], 1):
    order = sorted([k for k in new if k[0] == b], key=lambda k: new[k])
    us = []
    for k in order:
        if subj[k][0] not in us:
            us.append(subj[k][0])
    rows = [g2_row(dict(book["rows"][k[1]], u=us.index(subj[k][0])), k) for k in order]
    ib.append(dict(book, title=BOOKS[b][0], short=BOOKS[b][1], units=[UNIT[si] for si in us], rows=rows, uq={}))
W(f"{G}/index.json", dict(idx, books=ib))

# --- MCQs
# the Arihant book's PYQs (tools/arihant_apply.py) are APPSC Complete's only
ARIHANT = set(J("data/pyq/arihant/applied.json")) if os.path.exists("data/pyq/arihant/applied.json") else set()
ids = set()
QBY = SY.defaultdict(list)  # official line -> its MCQs
# the full official Group 2 papers: each question goes under the first section (and subsection) of its official line;
# the partial copies of the same papers' questions already in the notes MCQs are left out
PAPERS = SY.papers()
PAPER_QS = [q for _, qs in PAPERS for q in qs]
PAPER_YRS = {str(SY.year({"src": m["name"]})) for m, _ in PAPERS}  # the years of the full papers in the app
SUBJ_OF_PAPER = {"History": "P1", "Geography": "P2", "Indian Society": "P3", "Current Affairs": "P4",
                 "Social & Cultural History of AP": "M1A", "Indian Constitution": "M1B", "Indian & AP Economy": "M2A", "Science & Technology": "M2B",
                 "General Studies": "P4", "Economy": "M2A", "Planning & Economy": "M2A"}
ORDERED = sorted(new, key=lambda k: (k[0], new[k]))
PLACE = SY.defaultdict(list)


def first_sub(k, leaf):
    s = SY.SUBLEAF.get(ckey(k), {})
    return min((i for i, v in s.items() if v == leaf), default=-1)


# where a paper question goes: among the sections that teach its official line, the section and subsection whose
# titles, notes and MCQs are closest to it (TF-IDF); the subsection must be one tied to that line when there is one
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
_SECS = {}
for _b in range(1, 7):
    _flat = [r for u in J(f"{C}/book{_b}.json")["units"] for r in u["rows"]]
    _m = J(f"{C}/mcq{_b}.json")
    for _ri, _row in enumerate(_flat):
        if (_b, _ri) not in new:
            continue
        _qs = _m["rows"].get(str(_ri), [])
        _sb = _m.get("subs", {}).get(str(_ri)) or [-1] * len(_qs)
        for _si, _sec in enumerate(_row["secs"]):
            _t = [_row["title"], _sec["t"]] + ["".join(t for t, _ in bl.get("x") or []) for bl in _sec["b"] if bl.get("x")]
            _t += [q["s"] for q, s in zip(_qs, _sb) if s == _si]
            _SECS[(_b, _ri, _si)] = " ".join(_t)
_KEYS = list(_SECS)
_VEC = TfidfVectorizer(stop_words="english", sublinear_tf=True).fit(_SECS.values())
_DOC = _VEC.transform([_SECS[k] for k in _KEYS])
_POS = {k: i for i, k in enumerate(_KEYS)}


def best_place(q, cand):
    v = _VEC.transform([q["s"] + " " + (q.get("at") or (q["o"][q["a"]] if q.get("a", -1) >= 0 and q.get("o") else ""))])
    opts = []
    for k in cand:
        subs = SY.SUBLEAF.get(ckey(k), {})
        tied = [i for i, l in subs.items() if l == q["lf"]]
        n_secs = sum(1 for kk in _KEYS if kk[:2] == k)
        for si in (tied or range(n_secs)):
            if (k[0], k[1], si) in _POS:
                opts.append((k, si))
    if not opts:
        return cand[0], -1
    sims = cosine_similarity(v, _DOC[[_POS[(k[0], k[1], si)] for k, si in opts]])[0]
    return opts[int(sims.argmax())]


for meta, qs in PAPERS:
    raw = {q["n"]: q for q in SY.J(f"data/g2papers/{dict((t, n) for n, (t, _) in SY.PAPER_TAG.items())[meta['id']]}.json")["questions"]}
    for q in qs:
        cand = [k for k in ORDERED if q["lf"] in codes[k]]
        if not cand:  # beyond the official syllabus: the sections of its paper subject
            sc = SUBJ_OF_PAPER.get(raw[int(q["id"][-3:])].get("subject"), "P4")
            cand = [k for k in ORDERED if any(SY.subject_of(c) == sc for c in codes[k])]
        k, si = best_place(q, cand)
        PLACE[k].append((q, si))
# MCQs written for official lines that had almost none (data/g2syl/newmcq.jsonl; "g2" = Group 2 rows of that time)
import hashlib
_RN = SY.J("data/g2syl/rowmap-at-newmcq.json")
if os.path.exists("data/g2syl/newmcq.jsonl"):
    for l in open("data/g2syl/newmcq.jsonl"):
        if l.strip():
            o = json.loads(l)
            k = tuple(_RN[o["g2"]])
            q = {"id": "g2l" + hashlib.md5((o["s"] + "|".join(o["o"])).encode()).hexdigest()[:11], "s": o["s"], "o": o["o"],
                 "a": o["a"], "x": o["x"], "src": "app", "lf": o["leaf"]}
            PLACE[k].append((q, first_sub(k, o["leaf"])))
for b in range(1, 7):
    m = J(f"{C}/mcq{b}.json")
    rows, subs = {}, {}
    for r, v in m["rows"].items():
        if (b, int(r)) not in new:
            continue
        sb = m.get("subs", {}).get(r, [-1] * len(v))
        kept = list(zip(v, sb))  # every MCQ and every PYQ of the section (Group 1 and other papers' PYQs too)
        kept = [(q, s) for q, s in kept if not (PAPER_QS and q["id"].startswith("y") and re.search(r"Group[- ]?(II|2)", q.get("src", ""))
                                                    and any(y in q.get("src", "") for y in PAPER_YRS) and SY.is_copy(q, PAPER_QS))]
        for q, _ in kept:
            for f in ("x", "s"):
                if q.get(f):
                    q[f] = no_g1(q[f])
            for f in ("n", "xa"):
                if q.get(f):
                    q[f] = [no_g1(t) for t in q[f]]
        # each MCQ: the official line it is asked under ("x" beyond the syllabus); each PYQ: the paper it came from
        kept += PLACE.get((b, int(r)), [])
        for q, sb in kept:
            if not q.get("lf") or not (q["id"].startswith(SY.PAPER_PREFIXES) or q["id"].startswith("g2l")):
                q["lf"] = SY.question_leaf(f"{b}:{r}", sb)
            if q["id"].startswith("y"):
                q["rl"] = SY.tier(q)
            QBY[q["lf"]].append(q)
        rows[str(new[(b, int(r))])] = [q for q, _ in kept]
        subs[str(new[(b, int(r))])] = [x for _, x in kept]
    for v in rows.values():
        ids |= {q["id"] for q in v}
    W(f"{G}/mcq{b}.json", dict(m, rows=rows, subs=subs, units={}))

# the index's MCQ counts: after the Group 1 PYQs are gone
ix = J(f"{G}/index.json")
for b, book in enumerate(ix["books"], 1):
    m = J(f"{G}/mcq{b}.json")["rows"]
    for ri, r in enumerate(book["rows"]):
        r["q"] = len(m.get(str(ri), []))
W(f"{G}/index.json", ix)
ib = ix["books"]

# --- the rest
# the Notes tab's syllabus: the official subjects, each official line with its sections; then syllabus.json (the
# official tree with each line's MCQs, PYQs, Group 2 years and priority) for the Syllabus screens
ROWS_BY = SY.defaultdict(list)
for k in sorted(new, key=lambda k: (k[0], new[k])):
    for c in codes[k]:
        if c in SY.LEAF:
            ROWS_BY[c].append([k[0], new[k]])
LPRI, LSCORE = SY.priorities(QBY)
W(f"{G}/exams.json", [{"title": "Group 2", "sub": "Official APPSC syllabus (27-04-2023): Prelims and Mains", "subjects": [
    {"title": s["title"], "sub": f"{s['stage']}{'' if s['stage'] == 'Prelims' else ' · ' + s['paper']} · {s['marks']} marks · "
                                 f"{len({tuple(x) for c in SY.LEAF if SY.subject_of(c) == s['code'] for x in ROWS_BY[c]})} sections",
     "groups": [{"title": f"{c}: {SY.LEAF[c]['text']}", "code": c, "rows": ROWS_BY[c]} for c in SY.LEAF if SY.subject_of(c) == s["code"]]}
    for s in SY.TREE["subjects"]]}])
W(f"{G}/syllabus.json", SY.syllabus_json(dict(ROWS_BY), QBY, LPRI, [m for m, _ in PAPERS]))
emp = J(f"{C}/empty.json")
W(f"{G}/empty.json", {k: [p for p in map(page, v) if p] for k, v in emp.items()})
kt = J(f"{C}/keyterms.json")
W(f"{G}/keyterms.json", {page(k): v for k, v in kt.items() if page(k)})
d = J(f"{C}/dups.json")
W(f"{G}/dups.json", {k: v for k, v in d.items() if k in ids} if isinstance(d, dict) else [x for x in d if x in ids])
W(f"{G}/merged.json", {k: v for k, v in J(f"{C}/merged.json").items() if k in ids})
if os.path.exists(f"{C}/unmerged.json"):  # 3-statement MCQs taken apart again: answers pass to their one-fact MCQs
    W(f"{G}/unmerged.json", {k: [x for x in v if x in ids] for k, v in J(f"{C}/unmerged.json").items() if any(x in ids for x in v)})
W(f"{G}/edition.json", {"edition": "complete", "name": "APPSC Group 2"})
W(f"{G}/moved.json", {"v": "group2-1", "m": {}})
W(f"{G}/notemoves.json", [])
W(f"{G}/mcqlinks.json", {})
# the book icon's checked notes lines (tools/notelink.py): same secs and blocks, rows renumbered; a line on a
# row Group 2 does not keep is dropped (the app then falls back to its own guess)
if os.path.exists(f"{C}/notelinks.json"):
    nl = {}
    for qid, refs in J(f"{C}/notelinks.json").items():
        if qid not in ids:
            continue
        kref = []
        for ref in refs:
            b, r, rest = ref.split(":", 2)
            if (int(b), int(r)) in new:
                kref.append(f"{b}:{new[(int(b), int(r))]}:{rest}")
        if kref:
            nl[qid] = kref
    W(f"{G}/notelinks.json", nl)

# --- the plan, in two parts by the syllabus:
#   PRELIMS (Screening: S1 History, S2 Geography, S3 Indian Society, S4 Current Affairs): today -> 19 Feb,
#       20 Feb light review, 21 Feb the Prelims;  only sections that carry a Screening item
#   MAINS (Paper I: M1-A AP history, M1-B Constitution; Paper II: M2-A Economy, M2-B Sci-Tech): 22 Feb -> 19 May,
#       first pass of the Mains-only sections, then revision of every Mains section, MCQs and Mains mocks
#       (Mains date not announced: planned for 22 May 2027; 20-21 May the final buffer)
# each part: first pass (HIGH, then MED, then LIGHT; one subject a day; days by MCQ weight), R2, R3, MCQ days + mocks
old = J("data/plan/g2_template_plan.json")
pri = {tuple(r["ref"]): r for d in old["days"] for r in d["rows"] if r.get("ref")}
template = {}
for dd in old["days"]:
    template.setdefault(dd["type"], dd)
short = {b["id"]: b["short"] for b in ib}
mcqs = {(b, int(r)): len(v) for b in range(1, 7) for r, v in J(f"{G}/mcq{b}.json")["rows"].items()}
PRELIMS = dt.date(2027, 2, 21)
MAINS = dt.date(2027, 5, 22)
pool_all = []
for (b, r), n in sorted(new.items(), key=lambda kv: (ORDER.index(kv[0][0]), kv[1])):
    o = pri[(b, r)]
    # priority from the official lines it teaches (marks and how often Group 2 / APPSC asked them: SY.priorities)
    lp = [LPRI[c] for c in codes[(b, r)] if c in LPRI]
    p = "HIGH" if "HIGH" in lp else "MED" if "MED" in lp else "LIGHT"
    pool_all.append({k: v for k, v in o.items() if k != "q"} | {"ref": [b, n], "codes": codes[(b, r)], "pri": p})
is_s = lambda r: any(c.startswith("P") for c in r["codes"])
# Mains: its official lines; sections beyond the official syllabus are kept (all their PYQs) as LIGHT Mains-part topics
is_m = lambda r: any(c.startswith("M") for c in r["codes"]) or r["codes"] == ["X"]
w = lambda r: max(1, mcqs.get(tuple(r["ref"]), 0))


def balanced(rows, n):
    total, out, cur, acc = sum(map(w, rows)), [], [], 0
    for i, r in enumerate(rows):
        cur.append(r)
        acc += w(r)
        if len(out) < n - 1 and (acc >= total * (len(out) + 1) / n or len(rows) - i - 1 == n - len(out) - 1):
            out.append(cur)
            cur = []
    out.append(cur)
    out = [c for c in out if c]
    return out + [[] for _ in range(n - len(out))]


def subjects(rows):
    seen = []
    for r in rows:
        if short[r["ref"][0]] not in seen:
            seen.append(short[r["ref"][0]])
    return " + ".join(seen)


def tiers(rows):
    return " + ".join(t for t in TIERS if any(r["pri"] == t for r in rows))


days = []


def day(dte, typ, phase, focus, brief, rows, exam, label):
    t = template[typ]
    return {"n": len(days) + 1, "date": str(dte), "dow": dte.strftime("%a"), "phase": phase, "focus": focus,
            "brief": brief, "tasks": t["tasks"], "left": f"{(exam - dte).days} days to the {label}",
            "type": typ, "rows": rows}


def part(name, study_pool, rev_pool, start, last, exam, label, mock_names, shares):
    """one exam's days: first pass of study_pool, R2/R3 of rev_pool, MCQ days of rev_pool with mocks"""
    dates = [start + dt.timedelta(i) for i in range((last - start).days + 1)]
    N = len(dates)
    n_study, n_r2, n_r3 = (round(N * x) for x in shares)
    n4 = N - n_study - n_r2 - n_r3
    mock_at = {round(n4 * k / (len(mock_names) + 1)) for k in range(1, len(mock_names) + 1)}
    mocks = iter(mock_names)
    groups = [(t, b, [r for r in study_pool if r["pri"] == t and r["ref"][0] == b]) for t in TIERS[:2] for b in ORDER]
    groups.append(("LIGHT", 0, [r for r in study_pool if r["pri"] == "LIGHT"]))
    groups = [g for g in groups if g[2]]
    days_for = [1] * len(groups)
    while sum(days_for) < n_study:
        k = max(range(len(groups)), key=lambda k: sum(map(w, groups[k][2])) / days_for[k])
        days_for[k] += 1
    seq = []
    for t in TIERS:
        gi = [k for k, g in enumerate(groups) if g[0] == t]
        done = {k: 0 for k in gi}
        for _ in range(sum(days_for[k] for k in gi)):
            k = min(gi, key=lambda k: (done[k] + 1) / days_for[k] if done[k] < days_for[k] else 9)
            seq.append(k)
            done[k] += 1
    parts_ = {k: balanced(groups[k][2], days_for[k]) for k in range(len(groups))}
    used = {k: 0 for k in parts_}
    by_pri = sorted(rev_pool, key=lambda r: (TIERS.index(r["pri"]), ORDER.index(r["ref"][0]), r["ref"][1]))
    di = iter(dates)
    for k in seq:
        t, b, _ = groups[k]
        rows = parts_[k][used[k]]
        used[k] += 1
        focus = (short[b] if b else subjects(rows)).upper()
        days.append(day(next(di), "study", f"{name} · PHASE 1 FIRST PASS", focus,
                        [f"{name}: {t} priority. Read {len(rows)} topics of {short[b] if b else subjects(rows)}.",
                         f"Then today's MCQs (all {sum(map(w, rows))} of them)."], [dict(r) for r in rows], exam, label))
    for phase, n, q, how in (("PHASE 2 R2 REVISION", n_r2, 13, "about 4 minutes a page"),
                             ("PHASE 3 R3 REVISION", n_r3, 14, "about 2 minutes a page: the boxes and exam corners")):
        for j in range(n):
            rows = by_pri[len(by_pri) * j // n: len(by_pri) * (j + 1) // n]
            days.append(day(next(di), "revision", f"{name} · {phase}", subjects(rows).upper(),
                            [f"{name}: {tiers(rows)} priority. Revise {len(rows)} topics ({subjects(rows)}): {how}."],
                            [dict(r, q=q) for r in rows], exam, label))
    practice = iter(balanced(by_pri, n4 - len(mock_at)))
    for j in range(n4):
        if j in mock_at:
            days.append(day(next(di), "mock", f"{name} · PHASE 4 MCQS + MOCKS", "", [f"Full mock: {next(mocks)}"], [], exam, label))
        else:
            rows = next(practice)
            days.append(day(next(di), "practice", f"{name} · PHASE 4 MCQS + MOCKS", subjects(rows).upper(),
                            [f"{name}: {tiers(rows)} priority. MCQs of {len(rows)} topics ({subjects(rows)}): the rest of "
                             f"their MCQs (about {sum(map(w, rows))} in all). Re-read the notes of every miss."],
                            [dict(r) for r in rows], exam, label))
    return n_study, n_r2, n_r3, n4 - len(mock_at), len(mock_at)


pre = [r for r in pool_all if is_s(r)]
mains_new = [r for r in pool_all if is_m(r) and not is_s(r)]
mains_all = [r for r in pool_all if is_m(r)]
P_LABEL, M_LABEL = "Prelims (21 Feb 2027)", "Mains (planned 22 May 2027)"
st1 = part("PRELIMS", pre, pre, START, PRELIMS - dt.timedelta(2), PRELIMS, P_LABEL,
           ["Group 2 Screening (150 Q, 150 min)"] * 5, (40 / 88, 18 / 88, 9 / 88))
d = PRELIMS - dt.timedelta(1)
days.append(day(d, "revision", "PRELIMS · EXAM EVE", "LIGHT REVIEW",
                ["Prelims tomorrow. Light review only: answered-wrong MCQs and the traps boxes; admit card, centre route, "
                 "sleep by 22:00."], [], PRELIMS, P_LABEL))
days.append(day(PRELIMS, "mock", "PRELIMS · EXAM DAY", "", ["GROUP 2 PRELIMS (SCREENING) today. No study: rest after the exam."],
                [], PRELIMS, P_LABEL))
st2 = part("MAINS", mains_new, mains_all, PRELIMS + dt.timedelta(1), MAINS - dt.timedelta(3), MAINS, M_LABEL,
           ["Group 2 Mains Paper I (150 Q, 150 min)", "Group 2 Mains Paper II (150 Q, 150 min)"] * 3,
           (36 / 88, 16 / 88, 8 / 88))
for i, dd in enumerate(days):
    dd["n"] = i + 1
seen = [tuple(r["ref"]) for dd in days if dd["type"] == "study" for r in dd["rows"]]
assert len(seen) == len(set(seen)) == len(pre) + len(mains_new), (len(seen), len(pre), len(mains_new))
not_in = [r for r in pool_all if not is_s(r) and not is_m(r)]
assert not not_in, not_in[:3]
for dd in days:
    for t in dd.get("tasks", []):
        if t.get("block") == "MCQs" and "half of each topic" in t.get("task", ""):
            t["task"] = "Today's MCQs (Today tab or MCQs tab). Every miss goes to Answered wrong."
W(f"{G}/plan.json", dict(old, start=str(START), exam=str(MAINS), examLabel=M_LABEL, days=days,
                         stages=[{"date": str(PRELIMS), "label": P_LABEL}, {"date": str(MAINS), "label": M_LABEL}],
                         buffer=[{"dates": "20 May", "work": "Answered wrong + every traps box (notes), fast"},
                                 {"dates": "21 May", "work": "Light review, admit card, centre route, sleep by 22:00"}]))
print(f"{len(new)} sections ({len(pre)} Prelims, {len(mains_new)} Mains-only, {len(mains_all)} Mains), {len(ids)} MCQs; "
      f"plan {START} - {days[-1]['date']}: Prelims {st1}, Mains {st2} (study, R2, R3, MCQ days, mocks)")
