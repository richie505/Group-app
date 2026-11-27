"""Build the APPSC MCQ Tactics guides (Group 1, Group 2): Part A = techniques for every question type, with numbers
measured on the official papers; Part B = topic-by-topic technique sheets (data/tactics/out/<g>-<section>.json).
    python3 tools/tactics_guide.py [g1|g2] [--html-only]
Output: manuals/APPSC_Group_<n>_MCQ_Tactics.pdf (HTML: data/tactics/tactics_<g>.html, gitignored)."""
import collections, html, json, os, re, sqlite3, subprocess, sys

con = sqlite3.connect("data/pyqdecode/pyq.db")
E = lambda t: html.escape(str(t if t is not None else ""))
FMT = {"pair-matching": "matching", "odd-pair": "matching", "ordering": "chronology", "chronology/sequence": "chronology",
       "ranking/order one-liner": "chronology", "two-statement": "statement-based", "all-of-the-above": "multiple-correct"}


def fmt(f):
    f = re.sub(r"\s*\(.*\)", "", f or "?").strip()
    return FMT.get(f, f)


def frac(n, d):
    return f"{n} of {d} ({100 * n / d:.0f}%)" if d else "–"


def cite(t):
    """[question id] -> readable 'year · Qn' link-free reference; a leading '[tag]' (checker workaround) is dropped"""
    t = re.sub(r"^\[[^\]#]{1,40}\]\s*", "", str(t or ""))
    def r(m):
        qid = m.group(1)
        row = con.execute("SELECT p.year, p.stage, q.qno FROM question q JOIN paper p ON p.id=q.paper_id WHERE q.id=?", (qid,)).fetchone()
        return f"<span class='cite'>[{row[0]} {row[1]} Q{row[2]}]</span>" if row else f"<span class='cite'>[{E(qid)}]</span>"
    return re.sub(r"\[([^\]\s]+#[^\]\s]+)\]", r, E(t))


ALL = re.compile(r"^\s*(all (of )?the above|all of these|all are correct|all the above)\b", re.I)
NONE = re.compile(r"none of|neither", re.I)


def measure(exam):
    rows = con.execute("""SELECT q.id, q.options_json, q.key_index, q.format, q.text_original, p.year FROM question q JOIN paper p ON p.id=q.paper_id
        WHERE p.exam=? AND q.analysed IS NOT NULL AND q.deleted=0 AND q.options_json IS NOT NULL""", (exam,)).fetchall()
    rows = [(i, json.loads(o), k, fmt(f), t, y) for i, o, k, f, t, y in rows]
    rows = [r for r in rows if r[1] and r[2] is not None and 0 <= r[2] < 4 and len(r[1]) == 4]
    m = {"n": len(rows)}
    m["pos"] = collections.Counter("ABCD"[r[2]] for r in rows)
    a = [r for r in rows if any(ALL.search(x) for x in r[1])]
    m["all"] = (sum(1 for r in a if ALL.search(r[1][r[2]])), len(a))
    b = [r for r in rows if any(NONE.search(x) for x in r[1])]
    m["none"] = (sum(1 for r in b if NONE.search(r[1][r[2]])), len(b))
    L = [r for r in rows if len({len(x) for x in r[1]}) == 4]
    m["longest"] = (sum(1 for r in L if len(r[1][r[2]]) == max(map(len, r[1]))), len(L))
    num = []
    for r in rows:
        v = [re.fullmatch(r"[^\d]*?([\d,]+(?:\.\d+)?)[^\d]*", x.replace(" ", "")) for x in r[1]]
        if all(v):
            try:
                vals = [float(x.group(1).replace(",", "")) for x in v]
            except ValueError:
                continue
            if len(set(vals)) == 4:
                num.append(sorted(vals).index(vals[r[2]]))
    m["num"] = (sum(1 for k in num if k in (1, 2)), len(num), collections.Counter(num))
    neg = [r for r in rows if re.search(r"\b(not|incorrect|wrong|false|except)\b", r[4], re.I)]
    m["neg"] = (len(neg), len(rows))
    ar = [r for r in rows if r[3] == "assertion-reason"]
    def arc(t):
        t = t.lower()
        if re.search(r"both.*true|both.*correct|are true|are correct", t) and re.search(r"not (the )?(a )?correct|does not|doesn't|not explain", t):
            return "A and R true, R does NOT explain A"
        if re.search(r"both.*true|both.*correct|are true|are correct", t):
            return "A and R true, R explains A"
        if re.search(r"a\)? is true.*r\)? is false|a is true.*r is false", t):
            return "A true, R false"
        if re.search(r"a\)? is false.*r\)? is true|a is false.*r is true", t):
            return "A false, R true"
        return "other"
    m["ar"] = (collections.Counter(arc(r[1][r[2]]) for r in ar), len(ar))
    m["formats"] = collections.Counter(r[3] for r in rows)
    st = con.execute("""SELECT s.mechanism, q.format FROM statement s JOIN question q ON q.id=s.question_id JOIN paper p ON p.id=q.paper_id
        WHERE p.exam=? AND s.truth='F' AND s.tier='official'""", (exam,)).fetchall()
    m["mech"] = collections.Counter(x[0] for x in st)
    m["mech_n"] = len(st)
    m["mech_fmt"] = {f: collections.Counter(x[0] for x in st if fmt(x[1]) == f) for f in ("one-liner", "statement-based", "matching", "negative one-liner")}
    return m


def example(exam, f, n=1):
    """recent official questions of a format with their statement verdicts"""
    out = []
    for q in con.execute("""SELECT q.id, q.text_original, q.options_json, q.key_text, p.year, p.stage, q.qno, q.reconstruction FROM question q
            JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.analysed IS NOT NULL AND q.deleted=0 AND q.options_json IS NOT NULL
            AND q.reconstruction IS NOT NULL ORDER BY p.year DESC, q.qno""", (exam,)):
        if fmt(con.execute("SELECT format FROM question WHERE id=?", (q[0],)).fetchone()[0]) != f:
            continue
        sts = con.execute("SELECT label, text, truth, mechanism, true_fact FROM statement WHERE question_id=? ORDER BY rowid", (q[0],)).fetchall()
        if len(sts) < 3 or len(q[1]) > 900:
            continue
        rec = json.loads(q[7])
        h = (f"<div class='ex'><div class='exh'>Real PYQ · {q[4]} {E(q[5])} Q{q[6]}</div><div class='stem'>{E(q[1])}</div><ol class='opts'>"
             + "".join(f"<li>{E(o)}</li>" for o in json.loads(q[2])) + "</ol><div class='walk'><b>Solve it:</b><ul>"
             + "".join(f"<li>{E(l)}: <b class='{t}'>{'TRUE' if t == 'T' else 'FALSE' if t == 'F' else '?'}</b>"
                       + (f" – {E(m)}: {E(tf)}" if t == 'F' and tf else "") + "</li>" for l, _, t, m, tf in sts)
             + f"</ul>Answer: <b>{E(q[3])}</b>. {E(rec.get('why', ''))}</div></div>")
        out.append(h)
        if len(out) >= n:
            break
    return "".join(out)


MECH_HELP = [
    ("location substitution", "Place swapped for another real place of the same type (another port, district, river, capital).",
     "Ask: is THIS place tied to THIS event/site? Learn sites in pairs with their unique feature."),
    ("person substitution", "The right deed, the wrong person – usually a contemporary or a member of the same dynasty/body.",
     "Anchor the person by one unique fact (title, date, work). Same-family names (I/II) are the favourite swap."),
    ("chronological displacement", "Right event, wrong year/century – often a near year or another event's year.",
     "Memorise anchor years; check the decade first, then the year. Order the options and test the middle ones."),
    ("similar-term confusion", "A near-identical term (Ryotwari/Mahalwari, Lok Adalat/Gram Nyayalaya).",
     "Keep a confusion list per topic (Part B); state the one feature that separates the twins."),
    ("true fact not the one asked", "Option is true but answers a different question (the second-largest, another 'first').",
     "Re-read the stem's exact demand: first/largest/NOT/'in Andhra'/'at present'. Superlatives and 'first' live here."),
    ("numerical alteration", "Changed number: count, percentage, age, majority, article number.",
     "Know the number with its unit; with numeric options test the closest pair first."),
    ("fabricated", "A plausible-sounding but non-existent link or claim.",
     "If you cannot recall ANY source for it and the other options are verifiable, suspect fabrication."),
    ("institution substitution", "Function given to the wrong body (Finance Commission ↔ NITI Aayog, RBI ↔ SEBI).",
     "For every body, learn 'who appoints / who reports to / what it does'."),
    ("wrong pair", "In matching: a real item paired with another real item's partner.",
     "Lock the pair you are surest of; eliminate every option that breaks it."),
    ("authority swap", "Power given to the wrong authority (President ↔ Governor, Speaker ↔ Chairman).",
     "Ask 'who has THIS power under THIS article'; check exceptions (money bill, emergency)."),
]


def part_a(g, exam, m):
    pos = m["pos"]; n = m["n"]
    fm = m["formats"]
    h = [f"<h2 id='A'>Part A · Techniques for every question type</h2>"
         f"<p class='lead'>Measured on {n} keyed official {exam} questions with four options. Each technique below is a way to reach the answer through "
         "facts. The numbers tell you which shortcuts are real and which are myths.</p>"]
    # 1 universal method
    h.append("""<h3>A1 · The 4-step method for ANY APPSC MCQ</h3><ol class='steps'>
<li><b>Read the demand.</b> Circle the question's direction word – <i>correct / NOT correct / first / largest / at present / in Andhra</i>. Many
wrong options are true facts that answer a different question.</li>
<li><b>Name the micro-topic and its decisive fact.</b> Ask "what one fact decides this?" – a person, a date, a place, an authority, a number.</li>
<li><b>Mark every option or statement T/F from facts</b>, starting with the one you are SUREST of – never with the first one printed.</li>
<li><b>Let the options do the rest.</b> One sure verdict usually removes two options in statement and matching questions; read the survivors
only for the deciding difference.</li></ol>""")
    # 2 answer pattern facts
    a1, a2 = m["all"]; n1, n2 = m["none"]; l1, l2 = m["longest"]; u1, u2, uc = m["num"]
    h.append("<h3>A2 · Answer-pattern facts (what the keys show)</h3>" + table(["Pattern", "Observed in the official keys", "Use it?"], [
        ["Answer position A/B/C/D", " · ".join(f"{k}: {frac(pos[k], n)}" for k in "ABCD"),
         "<b>No.</b> The answers are spread almost evenly – guessing by position gains nothing."],
        ["'All of the above / all of these' offered", f"keyed {frac(a1, a2)} (chance level 25%)",
         "<b>Yes, as a tie-breaker:</b> if you are sure two options are true and the fourth is 'all of the above', it is usually the answer." if a2 and a1 / a2 > 0.4 else "Only as a weak tie-breaker."],
        ["'None of the above / neither' offered", f"keyed {frac(n1, n2)}", "Do not avoid it – it is a real answer often enough."],
        ["Longest option", f"keyed {frac(l1, l2)} (chance 25%)", "<b>Weak.</b> Slightly above chance – use only when two options are left and you know nothing."],
        ["Numeric options (four different numbers)", f"key is one of the two middle values in {frac(u1, u2)} (chance 50%)",
         "<b>Weak.</b> When eliminating, test the extremes first; but always check the fact."],
        ["Negative stems (NOT / incorrect / except)", frac(*m["neg"]) + " of questions",
         "Every 'NOT' question flips the logic – mark T/F for each option and pick the F. Circle the NOT before reading options."],
    ]))
    # guessing
    h.append("""<h3>A3 · When to guess</h3><p>With a ⅓-mark penalty for a wrong answer (check your notification for the rule that applies),
a blind guess among four options is break-even: ¼ × 1 − ¾ × ⅓ = 0. Eliminate ONE option and the expected gain becomes positive
(⅓ − ⅔ × ⅓ ≈ +0.11 per question); eliminate TWO and it is +0.33. So: <b>guess only after at least one sure elimination</b> – the
techniques below exist to give you that elimination.</p>""")
    # 3 per format
    fsec = []
    fsec.append(("Statement-based questions", fm.get("statement-based", 0) + fm.get("multiple-correct", 0), """
<ol><li>Judge the statement you are surest of first.</li><li>A FALSE statement removes every option that contains it; a TRUE statement removes every
option that leaves it out. One sure verdict usually leaves two options.</li><li>Compare the two survivors: they differ by one statement – judge
only that one.</li><li>Inside each statement, find the fact-bearing words (who, when, where, how many, which body). A long statement is usually
true at its core and false in ONE inserted detail (see 'true core + false extra').</li></ol>""", "statement-based"))
    fsec.append(("One-liners", fm.get("one-liner", 0), """
<ol><li>Turn each option into a full sentence with the stem and test it.</li><li>Expect the distractors to be the same TYPE as the answer: other kings
of the same dynasty, other ports, other years of the same decade. Your fact must be specific enough to separate them.</li>
<li>Superlative / 'first' stems: the distractors are often TRUE members of the same set (second largest, another early ruler) – rank, don't just recognise.</li></ol>""", "one-liner"))
    fsec.append(("Negative one-liners (NOT / incorrect / except)", fm.get("negative one-liner", 0), """
<ol><li>Circle NOT. Three options are true facts; you need the false one.</li><li>Tick the options you know are true – the last one standing is the answer even if
you have never seen it.</li><li>The odd one out is usually a swap (person, place, year) of a true fact – look for the detail that 'nearly' fits.</li></ol>""", "negative one-liner"))
    fsec.append(("Matching", fm.get("matching", 0), """
<ol><li>Lock the pair you are surest of; strike every option that breaks it.</li><li>Lock a second pair among the survivors – usually only one option is left.</li>
<li>APPSC's wrong pairs are real items paired with the neighbour's partner – similar entities (two reformers, two reports, two rivers of one basin). Learn the one
feature that separates them.</li></ol>""", "matching"))
    fsec.append(("Chronology / sequence", fm.get("chronology", 0), """
<ol><li>Find the earliest and the latest item – most options fail on the first or last position.</li><li>Use anchor years (Part B lists them per topic).</li>
<li>For the middle, compare only the two items you are unsure of.</li></ol>""", "chronology"))
    arc, arn = m["ar"]
    arline = "; ".join(f"{k}: {frac(v, arn)}" for k, v in arc.most_common()) if arn else ""
    fsec.append(("Assertion–Reason", arn, f"""
<ol><li>Judge A alone. Judge R alone. Only if both are true, ask "does R give the reason FOR A?" – read it as "A because R".</li>
<li>R can be a true fact on the same topic that does not explain A (APPSC's favourite trap here), or a reversed cause.</li></ol>
<p class='num'>Keyed outcomes in the official papers: {arline}.</p>""", "assertion-reason"))
    h.append("<h3>A4 · Format by format</h3>")
    for title, cnt, body, f in fsec:
        mf = m["mech_fmt"].get(f)
        top = ""
        if mf:
            tot = sum(mf.values())
            top = "<p class='num'>How the false options/statements were built here: " + "; ".join(f"{E(k)} {frac(v, tot)}" for k, v in mf.most_common(5)) + ".</p>"
        h.append(f"<h4>{E(title)} <small>({cnt} official questions)</small></h4>{body}{top}{example(exam, f) if f in ('statement-based', 'matching', 'assertion-reason') else ''}")
    # 4 the 10 ways
    tot = m["mech_n"]
    h.append("<h3>A5 · The ways APPSC makes a statement false – and the check for each</h3>" + table(
        ["Mechanism", "Share of all false statements", "What it looks like", "Your check"],
        [[f"<b>{E(k)}</b>", frac(m['mech'].get(k, 0), tot), E(a), E(b)] for k, a, b in sorted(MECH_HELP, key=lambda x: -m["mech"].get(x[0], 0))]))
    h.append("""<h3>A6 · Words: never decide by the word alone</h3><p>"Only", "all", "first", "not", "appointed" are false in some topics and true in others.
The word only tells you WHERE to look – the fact decides. Part B gives, for every topic, the exact words APPSC changes there.</p>""")
    return "".join(h)


def table(head, rows):
    return ("<table><thead><tr>" + "".join(f"<th>{E(x)}</th>" for x in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table>")


def sheet(o, pk):
    nq = len(pk["official_questions"])
    h = [f"<section class='sheet' id='S-{re.sub(r'[^A-Za-z0-9]+', '-', pk['section'])}'><h3>{E(pk['title'])}</h3>",
         f"<p class='lead'>{cite(o.get('overview'))} <small>({nq} official questions)</small></p>"]
    lv = {"High historical recurrence": "hi", "Moderate historical recurrence": "mo", "Low historical recurrence": "lo"}
    if o.get("possibility"):
        h.append("<h4>What APPSC asks here – topic by topic</h4>" + table(["Angle", "Asked so far", "Level", "What they ask"], [
            [f"<b>{E(p.get('angle'))}</b>", cite(p.get("evidence")), f"<span class='lv {lv.get(p.get('level'), 'na')}'>{E(p.get('level'))}</span>", cite(p.get("what_they_ask"))]
            for p in o["possibility"]]))
    if o.get("traps"):
        h.append("<h4>Traps APPSC used</h4>" + "".join(
            f"<div class='trap'><b>{E(t.get('trap'))}</b><br><span class='k'>Spot it:</span> {cite(t.get('spot'))}<br>"
            f"<span class='k'>Beat it:</span> {cite(t.get('fix'))}<br><span class='pyq'>{cite(t.get('pyq'))}</span></div>" for t in o["traps"]))
    if o.get("techniques"):
        h.append("<h4>Techniques</h4>" + "".join(
            f"<div class='tech'><b>{E(t.get('name'))}</b> – {cite(t.get('how'))}<div class='pyq'>Example: {cite(t.get('example'))}</div></div>" for t in o["techniques"]))
    if o.get("confusions"):
        h.append("<h4>Don't confuse</h4>" + table(["", "", "Remember"], [[E(c.get("a")), E(c.get("b")), cite(c.get("remember"))] for c in o["confusions"]]))
    if o.get("anchors"):
        h.append("<h4>Anchor facts</h4><ul class='anch'>" + "".join(f"<li>{cite(a)}</li>" for a in o["anchors"]) + "</ul>")
    if o.get("checklist"):
        h.append("<h4>30-second checklist</h4><ul class='chk'>" + "".join(f"<li>{cite(a)}</li>" for a in o["checklist"]) + "</ul>")
    return "".join(h) + "</section>"


CSS = """
@page { size: A4; margin: 15mm 13mm; }
:root { --ink:#1b1f24; --muted:#5b6470; --line:#d6dbe1; --acc:#0b5394; --t:#38761d; --f:#a61c00; }
body { font-family: "DejaVu Sans", "Noto Sans Telugu", sans-serif; color: var(--ink); background:#fff; font-size: 9.6pt; line-height: 1.42; }
h1 { font-size: 24pt; margin: 0 0 8pt; color: var(--acc); } h2 { font-size: 16pt; color: var(--acc); border-bottom: 2px solid var(--acc); break-before: page; padding-bottom: 3pt; }
h3 { font-size: 12pt; background: #eef3f9; border-left: 4px solid var(--acc); padding: 4pt 7pt; margin: 14pt 0 5pt; break-after: avoid; }
section.sheet { break-before: page; } section.sheet h3 { margin-top: 0; }
h4 { font-size: 10pt; margin: 10pt 0 4pt; color: #223; break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 8pt; font-size: 8.6pt; } th, td { border: 1px solid var(--line); padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #f2f4f7; } tr { break-inside: avoid; }
.lead { color: #333; } .num { color: var(--muted); font-size: 8.6pt; } .cite { color: var(--acc); font-size: 8pt; white-space: nowrap; }
.trap { border-left: 3px solid var(--f); background: #fdf3f1; padding: 3pt 7pt; margin: 4pt 0; break-inside: avoid; }
.tech { border-left: 3px solid var(--t); background: #f1f8ef; padding: 3pt 7pt; margin: 4pt 0; break-inside: avoid; }
.k { font-weight: 700; color: var(--muted); } .pyq { color: #444; font-size: 8.6pt; }
.lv { font-size: 7.6pt; font-weight: 700; padding: 0.5pt 4pt; border-radius: 3pt; color: #fff; background: #888; white-space: nowrap; }
.lv.hi { background: #a61c00; } .lv.mo { background: #b45f06; } .lv.lo { background: #38761d; }
.ex { border: 1px solid var(--line); border-radius: 4pt; padding: 5pt 8pt; margin: 5pt 0 8pt; break-inside: avoid; }
.exh { font-size: 8pt; color: var(--muted); font-weight: 700; } .stem { white-space: pre-wrap; font-weight: 600; } .opts { margin: 2pt 0 2pt 16pt; padding: 0; }
.walk { background: #fbfaf4; padding: 3pt 6pt; } .T { color: var(--t); } .F { color: var(--f); }
.steps li { margin: 3pt 0; } .cover { height: 245mm; display: flex; flex-direction: column; justify-content: center; } .cover p { font-size: 11pt; color: var(--muted); }
.toc a { color: var(--ink); text-decoration: none; } .toc ul { list-style: none; margin: 0 0 0 12pt; padding: 0; columns: 2; font-size: 8.8pt; }
.chk li::marker { content: "☐ "; }
"""


def build(g):
    exam = "Group 1" if g == "g1" else "Group 2"
    m = measure(exam)
    jobs = [n for n, _ in json.load(open("data/tactics/jobs.json")) if n.startswith(g + "-")]
    sheets, toc, missing = [], [], []
    for n in jobs:
        pk = json.load(open(f"data/tactics/packs/{n}.json"))
        p = f"data/tactics/out/{n}.json"
        if not os.path.exists(p):
            missing.append(n); continue
        sheets.append(sheet(json.load(open(p)), pk))
        toc.append(f"<li><a href='#S-{re.sub(r'[^A-Za-z0-9]+', '-', pk['section'])}'>{E(pk['title'].split('›')[-1].strip()[:80])}</a></li>")
    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>APPSC {exam} MCQ Tactics</title><style>{CSS}</style></head><body>"
           f"<div class='cover'><h1>APPSC {exam} – MCQ Tactics</h1><p>Techniques and tricks to crack every type of MCQ, and topic by topic: what APPSC asks, "
           f"the traps it sets, how to eliminate, what not to confuse.</p><p>Built from every official {exam} paper and its answer key. "
           "Every trick is fact-based and backed by real PYQs; recurrence is past observation, not a promise.</p></div>"
           f"<h2 id='toc'>Contents</h2><ol class='toc'><li><a href='#A'>Part A · Techniques for every question type</a></li>"
           f"<li><a href='#B'>Part B · Topic-by-topic tactics</a><ul>{''.join(toc)}</ul></li></ol>"
           + part_a(g, exam, m) + "<h2 id='B'>Part B · Topic-by-topic tactics</h2><p class='lead'>One sheet per syllabus section, in syllabus order. "
           "Levels: <span class='lv hi'>High</span> asked in ≥ 5 years · <span class='lv mo'>Moderate</span> 3–4 · <span class='lv lo'>Low</span> 1–2 · "
           "<span class='lv na'>not yet asked</span> syllabus angle. References like [2019 Prelims Q12] point to the real official question.</p>"
           + "".join(sheets) + "</body></html>")
    path = f"data/tactics/tactics_{g}.html"
    open(path, "w").write(doc)
    print(g, "sheets", len(sheets), "missing", missing)
    return path, exam


if __name__ == "__main__":
    for g in [a for a in sys.argv[1:] if a in ("g1", "g2")] or ["g1", "g2"]:
        path, exam = build(g)
        if "--html-only" not in sys.argv:
            os.makedirs("manuals", exist_ok=True)
            out = f"manuals/APPSC_{exam.replace(' ', '_')}_MCQ_Tactics.pdf"
            subprocess.run(["node", "tools/pyqdecode_pdf.js", path, out, f"APPSC {exam} MCQ Tactics"], check=True)
            print(out, os.path.getsize(out) // 1024, "KB")
