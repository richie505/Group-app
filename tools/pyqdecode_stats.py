"""Stage 6: statistics for the PYQ Decoding Manuals, from pyq.db (official papers only unless stated), per exam.
Writes data/pyqdecode/stats_<g1|g2>.json and coverage_<g1|g2>.csv. Units are always explicit:
  Q = question, S = statement (one testable unit), SW = statement-level occurrence of a word (a word counted once per
  statement it appears in), M = false statement classified by mechanism.
    python3 tools/pyqdecode_stats.py"""
import collections, csv, json, re, sqlite3

con = sqlite3.connect("data/pyqdecode/pyq.db")
G2L = dict(re.findall(r"\b([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):\s*(.+)", open("data/g2syl/leaves.md").read()))
G1L = {x["leaf"]: x["text"] for x in json.load(open("data/g1syl/leaves.json"))["leaves"]}
G1PART = {x["leaf"]: x["part"] for x in json.load(open("data/g1syl/leaves.json"))["leaves"]}
WORDS = ["only", "all", "every", "none", "always", "never", "however", "but", "not", "did not", "whereas", "while",
         "unlike", "more than", "less than", "higher than", "lower than", "first", "largest", "highest", "oldest", "main",
         "primary", "chief", "member of", "elected", "appointed", "recommended", "approved", "reviewed", "established",
         "introduced", "implemented", "applicable", "exempted", "national", "state", "regional", "central", "local",
         "both", "neither", "exclusively", "sole", "must", "may", "mandatory", "constitutional", "statutory"]
FMT = {"pair-matching": "matching", "odd-pair": "matching", "ordering": "chronology", "chronology/sequence": "chronology",
       "ranking/order one-liner": "chronology", "two-statement": "statement-based", "all-of-the-above": "multiple-correct"}


def fmt(f):
    f = re.sub(r"\s*\(.*\)", "", f or "?").strip()
    return FMT.get(f, f)


WRE = {w: re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in WORDS}


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def label(n):
    """recurrence label from the number of distinct years with direct official PYQs"""
    return "High historical recurrence" if n >= 5 else "Moderate historical recurrence" if n >= 3 else \
        "Low historical recurrence" if n >= 1 else "Insufficient evidence"


def confidence(q, years):
    return "STRONG EVIDENCE" if q >= 6 and years >= 3 else "MODERATE EVIDENCE" if q >= 3 else "WEAK EVIDENCE" if q >= 1 else "NO EVIDENCE"


def run(g, exam, L):
    qs = con.execute("""SELECT q.id, p.year, p.stage, q.format, q.leaf_code, q.subject, q.deleted FROM question q JOIN paper p
        ON p.id=q.paper_id WHERE p.exam=? AND q.analysed IS NOT NULL""", (exam,)).fetchall()
    st = con.execute("""SELECT s.question_id, s.truth, s.mechanism, s.text, s.decisive_phrase, s.leaf_code, s.truth_basis, p.year, p.stage
        FROM statement s JOIN question q ON q.id=s.question_id JOIN paper p ON p.id=q.paper_id
        WHERE p.exam=? AND q.analysed IS NOT NULL""", (exam,)).fetchall()
    out = {"exam": exam, "units": {"Q": "official question", "S": "statement (testable unit)", "SW": "statement-level word occurrence", "M": "false statement by mechanism"}}
    out["papers"] = [dict(zip(("id", "year", "stage", "title", "key_status", "key_doc_kind"), r)) for r in con.execute(
        "SELECT id, year, stage, title, key_status, key_doc_kind FROM paper WHERE exam=? AND id NOT LIKE 'app:%' ORDER BY year, id", (exam,))]
    out["totals"] = {"Q": len(qs), "Q_deleted": sum(1 for r in qs if r[6]), "S": len(st),
                     "S_T": sum(1 for r in st if r[1] == "T"), "S_F": sum(1 for r in st if r[1] == "F"), "S_U": sum(1 for r in st if r[1] == "U"),
                     "S_basis": dict(collections.Counter(r[6] for r in st))}
    out["formats"] = collections.Counter(fmt(r[3]) for r in qs).most_common()
    out["formats_by_stage"] = {s: collections.Counter(fmt(r[3]) for r in qs if r[2] == s).most_common()
                               for s in sorted({r[2] for r in qs})}
    F = [r for r in st if r[1] == "F"]
    out["mechanisms"] = [(m, n, pct(n, len(F))) for m, n in collections.Counter(r[2] or "unclassified" for r in F).most_common()]
    out["mechanisms_denominator"] = len(F)
    # per leaf
    leaf = collections.defaultdict(lambda: {"Q": 0, "years": set(), "formats": collections.Counter(), "S": 0, "T": 0, "F": 0,
                                            "mech": collections.Counter(), "qids": []})
    for r in qs:
        d = leaf[r[4]]
        d["Q"] += 1; d["years"].add(r[1]); d["formats"][fmt(r[3])] += 1; d["qids"].append(r[0])
    for r in st:
        d = leaf[r[5]]
        d["S"] += 1; d["T"] += r[1] == "T"; d["F"] += r[1] == "F"
        if r[1] == "F":
            d["mech"][r[2] or "unclassified"] += 1
    # words: per word overall and per leaf, statement-level occurrence with truth
    words = {}
    for w, rx in WRE.items():
        hits = [r for r in st if r[3] and rx.search(r[3]) and r[1] in ("T", "F")]
        if not hits:
            continue
        per = collections.defaultdict(lambda: [0, 0])
        dec = sum(1 for r in hits if r[4] and rx.search(r[4]))
        for r in hits:
            per[r[5]][0 if r[1] == "T" else 1] += 1
        T = sum(1 for r in hits if r[1] == "T")
        words[w] = {"SW": len(hits), "T": T, "F": len(hits) - T, "T%": pct(T, len(hits)), "F%": pct(len(hits) - T, len(hits)),
                    "in_decisive_phrase": dec, "by_leaf": sorted(([lf, t, f, t + f] for lf, (t, f) in per.items()), key=lambda x: -x[3])}
    out["words"] = words
    # coverage matrix over every syllabus leaf, with the secondary/tertiary evidence from the app bank
    sec = collections.Counter(); ter = collections.Counter()
    col = "g1_leaves" if g == "g1" else "g2_leaves"
    for pid, ex, leaves in con.execute(f"SELECT q.paper_id, p.exam, q.{col} FROM question q JOIN paper p ON p.id=q.paper_id WHERE q.paper_id LIKE 'app:%' OR p.exam='Other APPSC exam'"):
        for lf in set(json.loads(leaves or "[]")):
            if ex == exam:
                sec[lf] += 1
            elif ex == "Other APPSC exam":
                ter[lf] += 1
    rows = []
    for code, text in L.items():
        d = leaf.get(code)
        q = d["Q"] if d else 0
        yrs = len(d["years"]) if d else 0
        status = "Analysed with direct official PYQ evidence" if q else (
            "Covered only through related evidence (other tiers)" if (sec[code] or ter[code]) else "Analysed, but no direct PYQ found in available papers")
        rows.append({"leaf": code, "official_wording": text, "part": G1PART.get(code, code.split(".")[0]) if g == "g1" else code.split(".")[0],
                     "official_Q": q, "years": yrs, "years_list": sorted(d["years"]) if d else [], "S": d["S"] if d else 0,
                     "T": d["T"] if d else 0, "F": d["F"] if d else 0, "top_mechanisms": d["mech"].most_common(4) if d else [],
                     "formats": d["formats"].most_common() if d else [], "secondary_Q_topic_level": sec[code], "tertiary_Q_topic_level": ter[code],
                     "status": status, "recurrence": label(yrs), "confidence": confidence(q, yrs), "qids": d["qids"] if d else []})
    other = {k: v for k, v in leaf.items() if k not in L}
    out["unmapped_leaf_codes"] = {str(k): v["Q"] for k, v in other.items()}
    out["coverage"] = rows
    n = len(rows); direct = sum(1 for r in rows if r["official_Q"])
    out["coverage_summary"] = {"leaves": n, "direct": direct, "related_only": sum(1 for r in rows if r["status"].startswith("Covered only")),
                               "none": sum(1 for r in rows if r["status"].startswith("Analysed, but")), "direct_pct": pct(direct, n)}
    json.dump(out, open(f"data/pyqdecode/stats_{g}.json", "w"), ensure_ascii=False, indent=1, default=list)
    with open(f"data/pyqdecode/coverage_{g}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["leaf", "official_wording", "status", "official_questions", "years", "statements", "true", "false", "recurrence", "confidence",
                    "secondary_topic_level", "tertiary_topic_level"])
        for r in rows:
            w.writerow([r["leaf"], r["official_wording"], r["status"], r["official_Q"], " ".join(map(str, r["years_list"])), r["S"], r["T"], r["F"],
                        r["recurrence"], r["confidence"], r["secondary_Q_topic_level"], r["tertiary_Q_topic_level"]])
    print(exam, out["totals"], out["coverage_summary"], "unmapped codes:", out["unmapped_leaf_codes"])


run("g1", "Group 1", G1L)
run("g2", "Group 2", G2L)
