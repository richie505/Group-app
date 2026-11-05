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
C2 = "app/src/complete2/assets"  # the MCQ notes (APPSC Complete ships them as mbook*.json)
G = "app/src/group2/assets"
START = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-11-05")
EXAM = dt.date(2027, 1, 24)
LAST = dt.date(2027, 1, 21)  # 22-23 Jan: the buffer
TIERS = ["HIGH", "MED", "LIGHT"]
ORDER = [2, 1, 4, 3, 5, 6]
os.makedirs(G, exist_ok=True)
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))

import re

# --- Group 2 only: nothing of Group 1 shows (codes, tags, past-paper counts, sources, cited G1 papers, G1 PYQs)
G1REF = r"(?:APPSC[- ]?)?(?:G-?1|Group[- ]?(?:1|I)(?![I\w]))[ -]?(?:Mains |Prelims )?\**\d{4}\**(?:\s*(?:,|/|and|&)\s*\**\d{4}\**)*"


def no_g1(t):
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
codes, subj = {}, {}  # (book, row) -> its Group 2 syllabus codes; -> its first subject (index), item order
for si, sj in enumerate(g2["subjects"]):
    for gi, g in enumerate(sj["groups"]):
        for b, r in g["rows"]:
            codes.setdefault((b, r), []).append(g["code"])
            subj.setdefault((b, r), (si, gi))
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
UNIT = {si: {"code": re.sub(r"-\d+$", "", sj["groups"][0]["code"]), "title": f"{sj['title']} ({sj['sub'].split(' · ')[0]})"}
        for si, sj in enumerate(g2["subjects"])}


def g2_row(r, k):
    """a section's own fields, Group 2 only"""
    r = dict(r, codes=codes[k], tag="GROUP-II", pyq=g2_pyq(r.get("pyq")))
    if "sub" in r:
        r["sub"] = [x for x in r["sub"] if x.startswith("Group-II")]
    if "src" in r:
        r["src"] = [no_g1(x) for x in r["src"] if not x.startswith("Sources: Group-I:")]
    if "see" in r:
        r["see"] = [x for x in r["see"] if not re.search(r"\b[A-G]-\d+\b|Group-I\b", json.dumps(x))]
    if "secs" in r:
        r["secs"] = [dict(sec, t=no_g1(sec["t"]), b=[clean_block(x) for x in sec["b"]]) for sec in r["secs"]]
    return r
page = lambda pid: (lambda b, r, s: f"{b}:{new[(b, r)]}:{s}" if (b, r) in new else None)(*map(int, pid.split(":")))

# --- notes: full (trimmed) and MCQ notes; units kept only where a row is left
idx = J(f"{C}/index.json")
for src, name in ((C, "book{}.json"), (C2, "mbook{}.json")):
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
ids = set()
for b in range(1, 7):
    m = J(f"{C}/mcq{b}.json")
    rows, subs = {}, {}
    for r, v in m["rows"].items():
        if (b, int(r)) not in new:
            continue
        sb = m.get("subs", {}).get(r, [-1] * len(v))
        kept = [(q, x) for q, x in zip(v, sb) if not G1_PYQ.search(q.get("src", ""))]
        for q, _ in kept:
            for f in ("x", "s"):
                if q.get(f):
                    q[f] = no_g1(q[f])
            for f in ("n", "xa"):
                if q.get(f):
                    q[f] = [no_g1(t) for t in q[f]]
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
W(f"{G}/exams.json", [dict(g2, subjects=[dict(s, groups=[dict(g, rows=[[b, new[(b, r)]] for b, r in g["rows"]])
                                                            for g in s["groups"]]) for s in g2["subjects"]])])
emp = J(f"{C}/empty.json")
W(f"{G}/empty.json", {k: [p for p in map(page, v) if p] for k, v in emp.items()})
kt = J(f"{C}/keyterms.json")
W(f"{G}/keyterms.json", {page(k): v for k, v in kt.items() if page(k)})
d = J(f"{C}/dups.json")
W(f"{G}/dups.json", {k: v for k, v in d.items() if k in ids} if isinstance(d, dict) else [x for x in d if x in ids])
W(f"{G}/merged.json", {k: v for k, v in J(f"{C}/merged.json").items() if k in ids})
W(f"{G}/edition.json", {"edition": "complete", "name": "APPSC Group 2"})
W(f"{G}/moved.json", {"v": "group2-1", "m": {}})
W(f"{G}/notemoves.json", [])
W(f"{G}/mcqlinks.json", {})

# --- the plan: 5 Nov -> 21 Jan, phases in APPSC Complete's proportions, HIGH first
old = J(f"{C}/plan.json")
pri = {tuple(r["ref"]): r for d in old["days"] for r in d["rows"] if r.get("ref")}
template = {}
for dd in old["days"]:
    template.setdefault(dd["type"], dd)
short = {b["id"]: b["short"] for b in ib}
mcqs = {(b, int(r)): len(v) for b in range(1, 7) for r, v in J(f"{G}/mcq{b}.json")["rows"].items()}
pool = []
for (b, r), n in sorted(new.items(), key=lambda kv: (ORDER.index(kv[0][0]), kv[1])):
    o = pri[(b, r)]
    pool.append({k: v for k, v in o.items() if k != "q"} | {"ref": [b, n], "codes": codes[(b, r)]})
w = lambda r: max(1, mcqs.get(tuple(r["ref"]), 0))
dates = [START + dt.timedelta(i) for i in range((LAST - START).days + 1)]
N = len(dates)
n_study, n_r2, n_r3 = round(N * 39 / 88), round(N * 16 / 88), round(N * 8 / 88)
n4 = N - n_study - n_r2 - n_r3
mock_at = {round(n4 * k / 6) for k in (1, 2, 3, 4, 5)}  # five mocks spread over Phase 4
MOCKS = iter(["Group 2 Screening (150 Q, 150 min)", "Group 2 Mains Paper I (150 Q, 150 min)",
              "Group 2 Mains Paper II (150 Q, 150 min)", "Group 2 Screening (150 Q, 150 min)",
              "Group 2 Mains Paper I + II (300 Q)"])


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


# first pass: (tier, subject) groups, days by MCQ weight, one subject a day, HIGH then MED then LIGHT
groups = [(t, b, [r for r in pool if r["pri"] == t and r["ref"][0] == b]) for t in TIERS[:2] for b in ORDER]
groups.append(("LIGHT", 0, [r for r in pool if r["pri"] == "LIGHT"]))
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
parts = {k: balanced(groups[k][2], days_for[k]) for k in range(len(groups))}
used = {k: 0 for k in parts}
by_pri = sorted(pool, key=lambda r: (TIERS.index(r["pri"]), ORDER.index(r["ref"][0]), r["ref"][1]))


def day(i, typ, phase, focus, brief, rows):
    t = template[typ]
    dte = dates[i]
    return {"n": i + 1, "date": str(dte), "dow": dte.strftime("%a"), "phase": phase, "focus": focus,
            "brief": brief, "tasks": t["tasks"], "left": f"{(EXAM - dte).days} days to 24 Jan 2027",
            "type": typ, "rows": rows}


days = []
for i, k in enumerate(seq):
    t, b, _ = groups[k]
    rows = parts[k][used[k]]
    used[k] += 1
    focus = (short[b] if b else subjects(rows)).upper()
    days.append(day(i, "study", "PHASE 1 FIRST PASS", focus,
                    [f"{t} priority. Read {len(rows)} topics of {short[b] if b else subjects(rows)}.",
                     f"Then today's MCQs (all {sum(map(w, rows))} of them)."], [dict(r) for r in rows]))
for phase, n, q, how in (("PHASE 2 R2 REVISION", n_r2, 13, "about 4 minutes a page"),
                         ("PHASE 3 R3 REVISION", n_r3, 14, "about 2 minutes a page: the boxes and exam corners")):
    for j in range(n):
        rows = by_pri[len(by_pri) * j // n: len(by_pri) * (j + 1) // n]
        days.append(day(len(days), "revision", phase, subjects(rows).upper(),
                        [f"{tiers(rows)} priority. Revise {len(rows)} topics ({subjects(rows)}): {how}."],
                        [dict(r, q=q) for r in rows]))
practice = balanced(by_pri, n4 - len(mock_at))
pi = iter(practice)
for j in range(n4):
    if j in mock_at:
        days.append(day(len(days), "mock", "PHASE 4 MCQS + MOCKS", "", [f"Full mock: {next(MOCKS)}"], []))
    else:
        rows = next(pi)
        days.append(day(len(days), "practice", "PHASE 4 MCQS + MOCKS", subjects(rows).upper(),
                        [f"{tiers(rows)} priority. MCQs of {len(rows)} topics ({subjects(rows)}): the rest of their "
                         f"MCQs (about {sum(map(w, rows))} in all). Re-read the notes of every miss."],
                        [dict(r) for r in rows]))
assert len(days) == N
seen = [tuple(r["ref"]) for d in days if d["type"] == "study" for r in d["rows"]]
assert len(seen) == len(set(seen)) == len(pool), (len(seen), len(pool))
W(f"{G}/plan.json", dict(old, start=str(START), days=days))
print(f"{len(keep)} sections, {len(ids)} MCQs; plan {START} - {LAST}: {n_study} study, {n_r2} R2, {n_r3} R3, "
      f"{n4 - len(mock_at)} MCQ days, {len(mock_at)} mocks")
for d in days[:n_study]:
    print(d["n"], d["date"], d["focus"][:30], len(d["rows"]), "topics", sum(map(w, d["rows"])), "MCQs")
