"""The APPSC MCQ tricks PDF: patterns of the APPSC previous-year questions (with UPSC for contrast), from
data/pyq/patterns.json (tools/pyq_patterns.py), data/pyq/appsc_heat.json and the questions themselves.

    python3 tools/pyq_tricks_pdf.py [out.pdf=pdfs/APPSC-MCQ-Tricks.pdf]
"""
import html, json, os, re, sys
from collections import Counter

sys.path.insert(0, "tools")
from pyq_place import cleaned, usable, bank  # noqa: E402
from pyq_apply import rank, broken, label  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "pdfs/APPSC-MCQ-Tricks.pdf"
BOOKS = {1: "History & Culture", 2: "Polity, Governance & Society", 3: "Economy (India & AP)", 4: "Geography (India, World & AP)",
         5: "Science, Technology & Environment", 6: "Current Affairs"}
E = html.escape


TREND = {"Statement-based (\"consider the following\")": r"statement|consider the following", "Assertion-Reason": r"assertion",
         "Match the following": r"\bmatch|list-?i\b", "Negative (NOT / INCORRECT)": r"\bnot\b|incorrect|false|wrongly",
         "Report / data (\"As per ... Survey / Index\")": r"^(?:as per|according to)|survey|report|index",
         "About Andhra Pradesh": r"andhra|\bA\.?P\.?\b|amaravati|visakha|ysr|tirupati|godavari|krishna|telugu",
         "Tied to a recent year": r"\b20(?:1\d|2\d)\b", "Schemes / missions": r"scheme|yojana|mission|abhiyan",
         "Superlatives (first, largest ...)": r"\b(?:first|largest|highest|longest|most|least|smallest)\b"}


def paper_year(q):
    m = re.match(r"APPSC - (\d{4})", q.get("exam", ""))
    if m:
        return int(m.group(1))
    ys = re.findall(r"(20\d\d|19\d\d)", q.get("paper", "") + " " + q.get("exam", "") + " " + q.get("year", ""))
    return int(ys[0]) if ys else 0


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def main():
    P = json.load(open("data/pyq/patterns.json"))
    heat = json.load(open("data/pyq/appsc_heat.json"))
    ap, up, sp = P["APPSC"], P["UPSC"], P["State PSC"]
    qs = [q for q in map(cleaned, bank()) if usable(q) and not broken(q) and rank(q) == 0 and q["a"] >= 0]
    g12 = [q for q in qs if re.search(r"group[- ]?(?:1|i|2|ii)\b|\bG[12]\b", q["file"] + q.get("paper", "") + q.get("exam", ""), re.I)]
    place = json.load(open("data/pyq/place-complete.json"))["place"]
    # examples: confidently on a syllabus topic (no reasoning items), no OCR letters left over
    good = [q for q in qs if place.get(q["id"], [0, 0, 0, 0])[3] >= 0.3 and not re.search(r"\b[A-D]\)|\bQ\d", q["s"])]
    pool = [q for q in good if q in g12] + [q for q in good if q not in g12]

    def examples(rx, n=3, maxlen=330):
        out = []
        for q in pool:
            if re.search(rx, q["s"], re.I | re.S) and len(q["s"]) < maxlen and all(len(o) < 120 for o in q["o"]):
                out.append(q)
                if len(out) == n:
                    break
        return out

    def ex_html(items):
        h = []
        for q in items:
            src = label(q)
            opts = "".join(f"<li{' class=ok' if i == q['a'] else ''}>{E(o)}</li>" for i, o in enumerate(q["o"]))
            h.append(f"<div class=ex><div class=q>{E(q['s'])}</div><ol>{opts}</ol><div class=src>{E(src)}</div></div>")
        return "".join(h)

    tot = ap["count"]
    types = dict(ap["types"]); utypes = dict(up["types"])
    rows = "".join(f"<tr><td>{E(k)}</td><td>{v}</td><td>{pct(v, tot)}</td><td>{pct(utypes.get(k, 0), up['count'])}</td></tr>"
                   for k, v in ap["types"])
    pos = ap["answer_position"]; ptot = sum(pos)
    sh = ap["answer_shapes"]
    lo = ap["longest_option_correct"]; xo = ap["extreme_option"]; uxo = up["extreme_option"]
    by_book = []
    for b in map(str, range(1, 7)):
        t = ap["types_by_book"].get(b, [])
        n = sum(c for _, c in t) or 1
        top = ", ".join(f"{E(k)} ({pct(c, n)})" for k, c in t[:5])
        hot = "".join(f"<li>{E(x)} <b>({c})</b></li>" for x, c in heat.get(b, [])[:10])
        by_book.append(f"<h3>{E(BOOKS[int(b)])}</h3><p><b>How it is asked:</b> {top}</p><p><b>Most-asked topics (APPSC questions filed there):</b></p><ol class=hot>{hot}</ol>")

    EX0 = ex_html(examples(r"^(?:who|which|what|when|where)\b(?!.*(?:statement|following|not\b|incorrect))", 3, 150))
    EX1 = ex_html(examples(r"^(?:as per|according to)", 3))
    EX2 = ex_html(examples(r"_{2,}", 2, 200))
    EX3 = ex_html(examples(r"\b(?:NOT|INCORRECT)\b", 3, 220))
    EX4 = ex_html(examples(r"match", 2, 380))
    sec = []
    sec.append(f"""
<h1>APPSC MCQ Tricks</h1>
<p class=sub>Patterns read from {tot:,} APPSC previous-year questions (Group 1, Group 2 and other APPSC screening tests, with
the Commission's keys), set against {up['count']:,} UPSC Prelims and {sp['count']:,} other state-PSC questions.
Every number below is counted from those papers.</p>
<div class=box><b>The one-line summary.</b> APPSC is a <b>fact-recall exam with an Andhra Pradesh tilt</b>: about half its
questions are direct one-liners (who / what / which / when / where) and one in five is about Andhra Pradesh. The modern
paper (2021-25) is moving: longer questions, more statements and Assertion-Reason, a quarter on AP, more report data. Win it by knowing crisp facts, AP data and the latest reports, then use the
answer-shape habits below to settle the questions you half-know.</div>
""")
    allap = [q for q in map(cleaned, bank()) if usable(q) and not broken(q) and rank(q) == 0]
    old = [q for q in allap if 2010 <= paper_year(q) <= 2019]
    new = [q for q in allap if 2021 <= paper_year(q) <= 2026]
    def share(G, rx):
        return 100 * sum(1 for q in G if re.search(rx, q["s"], re.I)) / max(len(G), 1)
    trows = "".join(f"<tr><td>{E(k)}</td><td>{share(old, v):.0f}%</td><td><b>{share(new, v):.0f}%</b></td></tr>" for k, v in TREND.items())
    olen = sum(len(q["s"]) for q in old) / max(len(old), 1); nlen = sum(len(q["s"]) for q in new) / max(len(new), 1)
    sec.append(f"""
<h2>0. The modern APPSC paper (2021-2025) - what changed</h2>
<p>{len(new):,} questions from APPSC papers of 2021-2025 against {len(old):,} from 2010-2019. Prepare for the right-hand column.</p>
<table><tr><th>Share of questions that are ...</th><th>2010-2019</th><th>2021-2025</th></tr>{trows}
<tr><td>Average question length</td><td>{olen:.0f} characters</td><td><b>{nlen:.0f} characters</b></td></tr></table>
<ul>
<li><b>Questions are nearly twice as long.</b> The modern paper wraps a fact in context ("As per the Socio-Economic Survey 2023-24 ...", "Which of the following statements regarding ... is/are correct?"). Read the last line first to see what is actually asked.</li>
<li><b>Statement-based questions jumped from almost none to about one in eight</b>, and Assertion-Reason now appears. These are 2-statement and 3-statement sets with codes ("Only I", "Both I and II", "Neither") - practise judging each statement on its own.</li>
<li><b>Andhra Pradesh doubled</b> to about a quarter of the paper: AP economy data, AP schemes by name, AP geography and the formation / bifurcation history.</li>
<li><b>Report-based and year-tagged questions doubled</b>: the latest Survey, Budget, index rank, the scheme or event of the last 1-2 years. Static facts alone no longer carry the paper.</li>
<li><b>Still mostly single-fact at heart</b>: even the long statement questions test one standard fact per statement - not UPSC-style fine print.</li>
</ul>
""")
    sec.append(f"""
<h2>1. What kind of questions APPSC asks</h2>
<table><tr><th>Question type</th><th>APPSC count</th><th>APPSC share</th><th>UPSC share</th></tr>{rows}</table>
<p class=note>A question can fall in more than one type (a "NOT" question about a scheme counts under both); "Direct one-liner" means none of the other shapes.</p>
<ul>
<li><b>Direct one-liners dominate</b> ({pct(types.get('Direct one-liner (what/which)', 0), tot)} of APPSC vs {pct(utypes.get('Direct one-liner (what/which)', 0), up['count'])} of UPSC). Your notes must give the <b>one exact fact</b> - the name, the year, the place, the number - not only the idea.</li>
<li><b>Statement questions: rare in the old papers, rising fast</b> ({pct(types.get('Statement-based (consider the following)', 0), tot)} of all APPSC questions, but about one in eight since 2021; UPSC {pct(utypes.get('Statement-based (consider the following)', 0), up['count'])}). They stay short: 2-4 statements, codes like "Only I", "Both I and II", "Neither".</li>
<li><b>Superlatives and firsts</b> ({pct(types.get('Superlative / first / largest', 0), tot)}): first, largest, highest, longest, oldest - in India and in AP. Keep a "firsts and largests" list per subject.</li>
<li><b>Schemes and programmes</b> ({pct(types.get('Scheme / programme / mission', 0), tot)}): name, launch year, ministry, target group, what it pays. AP state schemes are asked by name.</li>
<li><b>Data questions</b> ({pct(types.get('Data / number fact', 0), tot)}) start with "As per ..." / "According to ..." a report: Socio-Economic Survey of AP, Union and AP Budgets, India State of Forest Report, NITI Aayog indices, Census 2011, RBI. The question is the report's headline number.</li>
<li><b>Fill in the blank</b> ({pct(types.get('Fill in the blank', 0), tot)}) is an APPSC habit UPSC almost never uses: the blank is always a single word or number from a standard sentence.</li>
</ul>
<h3>Examples</h3>
<h4>Direct one-liner</h4>{EX0}
<h4>Report / data ("As per ...")</h4>{EX1}
<h4>Fill in the blank</h4>{EX2}
""")
    sec.append(f"""
<h2>2. The keywords inside the question</h2>
<ul>
<li><b>Negative questions are printed in CAPITALS</b> in APPSC papers: NOT, INCORRECT, NOT CORRECT, FALSE, EXCEPT, "wrongly listed",
"wrongly matched". About {pct(types.get('Negative (NOT / incorrect / false)', 0), tot)} of questions are negative. Circle the capital word,
then mark each option T or F - the answer is the single F.</li>
<li><b>"Which of the following ..."</b> is the most common opener. Read all four options before answering: "Which of the following is
the deep-water port" has exactly one fully correct option and three that are real but wrong (other ports).</li>
<li><b>"As per / According to / In the year"</b> means the answer is tied to that report or year. Choose the figure from <i>that</i>
edition, not the latest one you remember.</li>
<li><b>Qualifiers decide the answer</b>: "primarily", "most important", "best suitable", "mainly", "first", "largest". APPSC takes the
standard textbook answer (NCERT, Laxmikanth, the AP Socio-Economic Survey), not an exception.</li>
<li><b>"Match the following"</b> ({pct(types.get('Match the following', 0), tot)}) is the APPSC way to test 4 facts at once - find the one
pair you are surest of and eliminate codes; you rarely need all four.</li>
<li><b>Assertion-Reason</b> is rare ({types.get('Assertion-Reason', 0)} questions) and almost always in the newer screening tests.</li>
</ul>
<h4>Negative</h4>{EX3}
<h4>Match the following</h4>{EX4}
""")
    ap_shapes = "".join(f"<tr><td>{E(k)}</td><td>{v[1]}</td><td>{v[0]}</td><td>{pct(v[0], v[1])}</td></tr>" for k, v in sh.items())
    sec.append(f"""
<h2>3. Answer-shape habits (for the questions you half-know)</h2>
<p>These are tie-breakers, not rules: use them only after you have eliminated what you can.</p>
<table><tr><th>When an option says ...</th><th>questions</th><th>it was the answer</th><th>rate</th></tr>{ap_shapes}</table>
<ul>
<li><b>"Both" is the answer in about half the questions that offer it</b> ({pct(sh.get('Both', [0, 1])[0], sh.get('Both', [0, 1])[1])}). In a two-statement APPSC question, if you are sure one statement is true and cannot fault the other, "Both" is the best bet.</li>
<li><b>"All of the above" wins {pct(sh.get('All of the above / 1,2,3 all', [0, 1])[0], sh.get('All of the above / 1,2,3 all', [0, 1])[1])}</b> of the times it appears (a blind pick is 25%). If you know two of the listed items are right, take "All".</li>
<li><b>"None of the above" / "Neither" is rarely right</b> ({pct(sh.get('None of the above / neither', [0, 1])[0], sh.get('None of the above / neither', [0, 1])[1])}). Pick it only when you can positively reject every other option.</li>
<li><b>Extreme words are not a giveaway in APPSC.</b> Options with only / all / never / always / must were the answer {pct(xo.get('correct', 0), xo.get('total', 1))} of the time (UPSC {pct(uxo.get('correct', 0), uxo.get('total', 1))}) - the same as chance. Do not eliminate an option just because it says "only".</li>
<li><b>The longest option</b> was right {pct(lo[0], lo[1])} of the time (chance 25%) - a slight lean, useful only as a last resort.</li>
<li><b>Answer position</b>: option 1 {pct(pos[0], ptot)}, option 2 {pct(pos[1], ptot)}, option 3 {pct(pos[2], ptot)}, option 4 {pct(pos[3], ptot)}. Option 4 is the least used - do not "default to D".</li>
<li><b>Numbers and years</b>: when the four options are numbers, the smallest was right least often. Keys also differ between paper sets and between Initial and Final keys, so learn the answer by its <b>text</b>, never by its option number.</li>
</ul>
""")
    sec.append(f"""
<h2>4. The Andhra Pradesh tilt</h2>
<ul>
<li><b>About one APPSC question in five is about Andhra Pradesh</b> (rivers, soils, minerals, ports, districts, schemes, economy, formation history), against 3% in UPSC.</li>
<li><b>History</b>: formation of Andhra State 1953 (Potti Sriramulu), Visalandhra and the Gentlemen's Agreement 1956, the 2014 bifurcation, social reformers (Kandukuri Veeresalingam), Satavahanas, Kakatiyas, Vijayanagara.</li>
<li><b>Geography</b>: Godavari / Krishna / Penna / Vamsadhara / Nagavali, red soils over most of AP, beach-sand minerals, bauxite, ports (Visakhapatnam, Gangavaram, Krishnapatnam), national parks (Papikonda, Sri Venkateswara).</li>
<li><b>Economy</b>: GSDP, growth and sector shares from the latest Socio-Economic Survey, AP Budget heads, agriculture (APCNF / natural farming, Rythu Bharosa Kendras), industrial policy, the new state's capital and corridor projects.</li>
<li><b>Schemes</b> are asked by the AP name ("YSR Cheyutha", "Amma Vodi", "Aarogyasri") - who it serves, what it gives, when it began. Keep a table of current AP schemes with these four columns.</li>
</ul>
""")
    sec.append("<h2>5. Subject by subject</h2>" + "".join(by_book))
    sec.append(f"""
<h2>6. APPSC vs UPSC - what to copy and what to skip</h2>
<table><tr><th></th><th>APPSC</th><th>UPSC Prelims</th></tr>
<tr><td>Typical shape</td><td>Direct one-liner, 4 single-fact options</td><td>"Consider the following statements", "How many of the above"</td></tr>
<tr><td>Statements per question</td><td>2-4, codes like "I and II only", "Both"</td><td>3-4, often "only one / only two / all three"</td></tr>
<tr><td>Depth</td><td>Standard fact, the textbook answer</td><td>Fine distinctions, exceptions, recent reports</td></tr>
<tr><td>State content</td><td>~20% AP-specific</td><td>~3%</td></tr>
<tr><td>Current affairs</td><td>1-2 years before the exam; awards, sports, schemes, AP news</td><td>Concepts behind the news</td></tr>
</table>
<p>Use UPSC questions for <b>which facts matter</b> (the exam angle) but answer APPSC questions at <b>APPSC depth</b>: one fact, the standard answer.</p>
<h2>7. A checklist for every question</h2>
<ol>
<li>Spot the capital-letter word (NOT / INCORRECT / EXCEPT) and the qualifier (first, largest, primarily, as per ...).</li>
<li>Name the fact being tested in one phrase before reading the options.</li>
<li>Eliminate options that belong to a neighbouring fact (another port, another scheme, another year).</li>
<li>Statements: judge each on its own; with two statements and no fault found, "Both".</li>
<li>Half-known: "All of the above" if two items are surely right; avoid "None"; don't default to option 4; don't cut "only" options blindly.</li>
<li>Numbers / years: anchor to one fact you know (a Plan's start year, a Census figure) and count from it.</li>
</ol>
""")
    # 8. topic by topic: the audit's notes on how APPSC asks each topic (data/pyq/audit/out), for the most-asked topics
    asked = {}
    for b in range(1, 7):
        for r, qs in json.load(open(f"app/src/complete/assets/mcq{b}.json"))["rows"].items():
            asked[f"{b}:{r}"] = sum(1 for q in qs if q.get("ap"))
    titles = {}
    for b in range(1, 7):
        ri = 0
        for u in json.load(open(f"app/src/complete/assets/book{b}.json"))["units"]:
            for r in u["rows"]:
                titles[f"{b}:{ri}"] = r["title"]
                ri += 1
    parts = ["<h2>8. Topic by topic - how APPSC asks the most-asked topics</h2>",
             "<p>From reading every APPSC, UPSC and state-PSC question filed under each topic. The ten topics per subject with the most APPSC questions.</p>"]
    for b in range(1, 6):
        parts.append(f"<h3>{E(BOOKS[b])}</h3>")
        top = sorted((k for k in asked if k.startswith(f"{b}:")), key=lambda k: -asked[k])[:10]
        for k in top:
            f = f"data/pyq/audit/out/{k.replace(':', '-')}.json"
            if not os.path.exists(f):
                continue
            pats = [p for p in json.load(open(f)).get("patterns", []) if not re.search(r"\bapp\b|app's|app MCQ", p, re.I)]
            if pats:
                parts.append(f"<div class=topic><b>{E(titles[k])}</b> <span class=n>({asked[k]} APPSC questions)</span><ul>"
                             + "".join(f"<li>{E(p)}</li>" for p in pats[:5]) + "</ul></div>")
    doc_topics = "".join(parts)
    css = """
@page{size:A4;margin:16mm 14mm}
body{font-family:'Noto Sans','DejaVu Sans',sans-serif;font-size:10.5pt;color:#1d1d1f;line-height:1.45}
h1{font-size:24pt;margin:0 0 4pt;color:#0b3d91}h2{font-size:15pt;color:#0b3d91;border-bottom:2px solid #0b3d91;padding-bottom:2pt;margin-top:18pt;page-break-after:avoid}
h3{font-size:12pt;margin:12pt 0 4pt;color:#7a3e00}h4{font-size:10.5pt;margin:8pt 0 3pt;color:#444}
.sub{color:#555}.box{background:#eef4ff;border-left:4px solid #0b3d91;padding:8pt 10pt;margin:10pt 0}
table{border-collapse:collapse;width:100%;margin:6pt 0;font-size:9.5pt}td,th{border:1px solid #ccd;padding:3pt 6pt;text-align:left}th{background:#e8ecf5}
.ex{border:1px solid #dde;border-radius:4pt;padding:5pt 8pt;margin:5pt 0;page-break-inside:avoid;background:#fafbfd}.ex .q{font-weight:600;white-space:pre-wrap}
.ex ol{margin:3pt 0 2pt 18pt;padding:0}.ex li.ok{color:#0a7a2f;font-weight:700}.ex .src{font-size:8.5pt;color:#777}
.topic{margin:6pt 0;page-break-inside:avoid}.topic ul{margin:2pt 0 4pt 16pt;padding:0}.n{color:#777;font-size:9pt}
.note{font-size:8.5pt;color:#666}ol.hot{margin-top:0}li{margin:2pt 0}
"""
    doc = f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{''.join(sec)}{doc_topics}</body></html>"
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    h = OUT.replace(".pdf", ".html")
    open(h, "w").write(doc)
    import subprocess
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('file://{os.path.abspath(h)}');await p.pdf({{path:'{os.path.abspath(OUT)}',format:'A4',printBackground:true}});"
          "await b.close();})();")
    subprocess.run(["node", "-e", js], check=True)
    os.remove(h)
    print(OUT)


if __name__ == "__main__":
    main()
