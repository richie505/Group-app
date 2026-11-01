"""APPSC answer secrets PDF: the measured answer patterns of the keyed APPSC previous-year questions
(data/pyq/secrets.json, tools/pyq_secrets.py), checked against UPSC and other state-PSC papers (secrets-others.json),
subject by subject and topic by topic.

    python3 tools/pyq_secrets_pdf.py [out.pdf=pdfs/APPSC-Answer-Secrets.pdf]
"""
import html, json, os, subprocess, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "pdfs/APPSC-Answer-Secrets.pdf"
A = json.load(open("data/pyq/secrets.json"))
O = json.load(open("data/pyq/secrets-others.json"))
BOOKS = {"1": "History & Culture", "2": "Polity, Governance & Society", "3": "Economy (India & AP)",
         "4": "Geography (India, World & AP)", "5": "Science, Technology & Environment", "6": "Current Affairs"}
E = html.escape


def r(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def cell(d, k):
    return d["options"].get(k + " right", 0), d["options"].get(k + " n", 0)


def row(label, a, o, chance="25%", verdict=""):
    return (f"<tr><td>{label}</td><td><b>{r(*a)}</b> <span class=n>({a[0]}/{a[1]})</span></td>"
            f"<td>{r(*o)} <span class=n>({o[0]}/{o[1]})</span></td><td>{chance}</td><td>{verdict}</td></tr>")


def table(head, rows):
    return f"<table><tr>{''.join(f'<th>{h}</th>' for h in head)}</tr>{''.join(rows)}</table>"


def pos_row(name, c):
    n = sum(c.values()) or 1
    return f"<tr><td>{name}</td>" + "".join(f"<td>{r(c.get(str(i), 0), n)}</td>" for i in range(1, 5)) + f"<td>{n}</td></tr>"


def main():
    sec = []
    n = A["n"]
    sec.append(f"""<h1>APPSC Answer Secrets</h1>
<p class=sub>Measured from <b>{n:,} APPSC questions with the Commission's own keys</b> (Group 1, Group 2, the department
screening tests and the AP History previous papers), and checked against <b>{O['n']:,} UPSC and state-PSC questions</b>.
Every percentage is "how often the key agreed", with the count beside it.</p>
<div class=box><b>Read this first.</b> Nothing here replaces knowing the fact. These are <b>tie-breakers for the
questions you half-know</b>: when two options survive, they tell you which one the examiner usually keys. A pattern is
worth trusting when it holds in <i>both</i> columns (APPSC and other exams) and on a decent count - those are marked
<span class=ok>strong</span>; small or one-sided counts are marked <span class=weak>weak</span>.</div>
<h2>0. The negative-marking rule that decides when to guess</h2>
<p>APPSC papers print "Negative marks: 1/3" - a wrong answer costs a third of a mark.</p>
{table(["What you can rule out", "Chance of a hit", "Expected marks for a guess", "Do it?"], [
"<tr><td>Nothing (blind guess among 4)</td><td>25%</td><td>0.25 - 0.75/3 = <b>0.00</b></td><td>No gain - skip</td></tr>",
"<tr><td>1 option surely wrong (3 left)</td><td>33%</td><td>0.33 - 0.67/3 = <b>+0.11</b></td><td>Yes</td></tr>",
"<tr><td>2 options surely wrong (2 left)</td><td>50%</td><td>0.50 - 0.50/3 = <b>+0.33</b></td><td>Always</td></tr>",
"<tr><td>2 left + a strong pattern below (about 60%)</td><td>60%</td><td>0.60 - 0.40/3 = <b>+0.47</b></td><td>Always</td></tr>"])}
<p>So: <b>never guess blind; always guess once you can strike out one option.</b> The patterns below push a 50-50 to about 60-70.</p>
""")
    # 1. option-shape table
    oa, oo = A["options"], O["options"]
    g = lambda d, k: (d.get(k + " right", 0), d.get(k + " n", 0))
    sec.append("<h2>1. Option shapes - how often each kind of option is the key</h2>" + table(
        ["When an option is ...", "APPSC", "Other exams", "Blind chance", "Verdict"], [
            row('"None of the above / None of these"', g(oa, "none of the above"), g(oo, "none of the above"), "25%", "<span class=ok>strong</span>: almost never - strike it first"),
            row('"Neither 1 nor 2"', g(oa, "neither"), g(oo, "neither"), "25%", "<span class=ok>strong</span>: rarely the key"),
            row('"Both 1 and 2"', g(oa, "both"), g(oo, "both"), "25%", "<span class=ok>strong</span>: the key about half the time"),
            row('"All of the above"', g(oa, "all of the above"), g(oo, "all of the above"), "25%", "<span class=ok>strong</span> in other exams (2 in 3); APPSC count small"),
            row("The longest option (clearly longest)", g(oa, "longest"), g(oo, "longest"), "25%", "slight lean - last resort"),
            row("The shortest option", g(oa, "shortest"), g(oo, "shortest"), "25%", "no edge"),
            row("The option sharing most words with the other three", g(oa, "centre"), g(oo, "centre"), "25%", "<span class=ok>strong</span>: the 'centre' option is keyed 1 in 3"),
            row("The option repeating most words of the question", g(oa, "echo"), g(oo, "echo"), "25%", "<span class=weak>weak</span> - don't rely on it"),
        ]) + """<ul>
<li><b>The centre-option trick:</b> examiners build three wrong options by changing one detail of the right one, so the right option
tends to share words with all the others. ("Gautamiputra Satakarni / Vasishthiputra Pulumavi / Gautamiputra Yajna Sri / Vasishthiputra
Satakarni" - the key is often the one whose two halves each appear elsewhere.)</li>
<li><b>Strike "None of the above" and "Neither" first</b> - that alone turns a blind 25% into 33% and makes the guess worth taking.</li></ul>""")
    # numbers and years
    def rk(d, k):
        tot = d.get(k + " n", 0)
        return [d.get(f"{k} rank{i}", 0) for i in range(1, 5)], tot
    nA, nAt = rk(oa, "number"); nO, nOt = rk(oo, "number"); yA, yAt = rk(oa, "year"); yO, yOt = rk(oo, "year")
    sec.append("<h2>2. Numbers and years in the options</h2>" + table(
        ["Options are ...", "smallest", "2nd", "3rd", "largest", "count"], [
            f"<tr><td>Numbers / % - APPSC</td>{''.join(f'<td>{r(x, nAt)}</td>' for x in nA)}<td>{nAt}</td></tr>",
            f"<tr><td>Numbers / % - other exams</td>{''.join(f'<td>{r(x, nOt)}</td>' for x in nO)}<td>{nOt}</td></tr>",
            f"<tr><td>Years - APPSC</td>{''.join(f'<td>{r(x, yAt)}</td>' for x in yA)}<td>{yAt}</td></tr>",
            f"<tr><td>Years - other exams</td>{''.join(f'<td>{r(x, yOt)}</td>' for x in yO)}<td>{yOt}</td></tr>"]) +
        f"""<ul><li><b>The smallest number is the key least often</b> (APPSC {r(nA[0], nAt)}, others {r(nO[0], nOt)}) - <span class=ok>strong</span>.
Between the smallest and a middle value, lean middle.</li>
<li><b>Years: the earliest year is rarely keyed</b> (APPSC {r(yA[0], yAt)}); the 2nd and 3rd years carry two-thirds of keys. Examiners put the
true year in the middle and pad with one earlier and one later decoy.</li>
<li>The "two close values" folk trick (pick one of the two nearest numbers) gives no edge: APPSC {r(oa.get('number closepair', 0), nAt)} against 50% chance.</li></ul>""")
    # 3. positions
    sec.append("<h2>3. Which option number is keyed</h2>" + table(["", "1", "2", "3", "4", "count"], [
        pos_row("APPSC - all questions", A["position"]), pos_row("APPSC - NOT / INCORRECT questions", A["neg"]["position"]),
        pos_row("Other exams - NOT / INCORRECT questions", O["neg"]["position"])] +
        [pos_row(f"APPSC - {k}", v) for k, v in A["position_by_kind"].items() if sum(v.values()) >= 30]) +
        f"""<ul><li><b>In NOT / INCORRECT / EXCEPT questions, option 4 is the key about 1 time in 3</b> (APPSC {r(A['neg']['position'].get('4', 0), A['neg']['n'])},
others {r(O['neg']['position'].get('4', 0), O['neg']['n'])}) - <span class=ok>strong</span>. Examiners write three true statements first and put the
false one last. If two options survive in a NOT question and one is option 4, take option 4.</li>
<li>Across all APPSC questions option 4 is the <b>least</b> used ({r(A['position'].get('4', 0), n)}); options 1 and 2 the most. In an ordinary
question, do not default to D.</li></ul>""")
    # 4. statements
    def shape_rows(d):
        out = []
        for k in ("2", "3", "4"):
            c = d["statement_shapes"].get(k, {})
            t = sum(c.values()) or 1
            out.append(f"<tr><td>{k} statements</td>" + "".join(
                f"<td>{r(c.get(f'{j} of {k} true', 0), t)}</td>" for j in range(0, 5)) + f"<td>{t}</td></tr>")
        return out
    sec.append("<h2>4. Statement questions (\"Consider the following statements\")</h2><h3>How many statements are true</h3>" +
               "<p><b>APPSC</b></p>" + table(["", "0 true", "1 true", "2 true", "3 true", "4 true", "count"], shape_rows(A)) +
               "<p><b>Other exams</b></p>" + table(["", "0 true", "1 true", "2 true", "3 true", "4 true", "count"], shape_rows(O)) +
               f"""<ul><li><b>A statement in an APPSC set is true {r(A['statements'].get('true', 0), A['statements'].get('statements', 1))} of the time</b>
(others {r(O['statements'].get('true', 0), O['statements'].get('statements', 1))}). With no idea about a statement, lean "true".</li>
<li><b>"All false / Neither / None" is rare</b> - about 1 set in 10. Do not mark "none of the statements" unless you can disprove each one.</li>
<li><b>3 statements: "two of three true" is the commonest key</b> in APPSC; <b>4 statements: other exams favour "three of four"</b>.</li>
<li><b>2 statements:</b> exactly one true and both true are near even - judge each; "neither" is the outsider.</li></ul>""")
    # 5. keywords
    kwA, kwO = A["keyword_truth"], O["keyword_truth"]
    order = sorted([k for k in kwA if k != "(any statement)" and kwA[k][1] + kwO.get(k, [0, 0])[1] >= 8],
                   key=lambda k: (kwA[k][0] + kwO.get(k, [0, 0])[0]) / (kwA[k][1] + kwO.get(k, [0, 1])[1]))
    rows = []
    for k in order:
        a, o = kwA[k], kwO.get(k, [0, 0])
        tot = (a[0] + o[0]) / max(a[1] + o[1], 1)
        v = "leans <b class=f>FALSE</b>" if tot < 0.42 else "leans <b class=t>TRUE</b>" if tot > 0.62 else "no signal"
        rows.append(f"<tr><td>{E(k)}</td><td>{r(*a)} <span class=n>({a[0]}/{a[1]})</span></td><td>{r(*o)} <span class=n>({o[0]}/{o[1]})</span></td><td>{v}</td></tr>")
    base_a, base_o = kwA["(any statement)"], kwO["(any statement)"]
    sec.append(f"""<h2>5. Keywords inside a statement - how often such a statement is TRUE</h2>
<p>From every statement whose truth the key settles (statement sets, "which statement is correct / NOT correct", "which pair is correctly
matched"). Baseline: any statement is true APPSC {r(*base_a)}, others {r(*base_o)}.</p>""" +
               table(["Statement contains", "APPSC true", "Other exams true", "Verdict"], rows) +
               """<ul><li><b>"exclusively / solely / entirely / completely" - almost always FALSE.</b> Absolute words that close every exception are the
examiner's favourite way to falsify a true fact.</li>
<li><b>"any", "not", "cannot" and "all" inside a statement lean false</b> (true only 1 time in 3 to 2 in 5).</li>
<li><b>"first" and Andhra-specific statements lean true</b> (about 3 in 4); "largest / highest / most" mildly so - APPSC writes its true
statements about AP and its "firsts" straight from the textbook.</li>
<li><b>"only" is NOT a reliable giveaway in APPSC</b> - it is true about as often as any statement (UPSC folklore says otherwise).
Don't strike an option just for saying "only"; check the fact.</li>
<li>"may / can" (hedged) statements are near the baseline - no edge.</li></ul>""")
    # 6. assertion-reason and match
    def ar_rows(d):
        c = d["assertion"]; t = sum(c.values()) or 1
        names = ["both true, R explains A", "both true, R not the explanation", "A true, R false", "A false, R true", "both false"]
        return "".join(f"<td>{r(c.get(x, 0), t)}</td>" for x in names) + f"<td>{t}</td>"
    m = A["match"]; mo = O["match"]
    sec.append("<h2>6. Assertion-Reason and Match-the-following</h2>" + table(
        ["", "Both true, R explains", "Both true, R doesn't explain", "A true, R false", "A false, R true", "Both false", "count"],
        [f"<tr><td>APPSC</td>{ar_rows(A)}</tr>", f"<tr><td>Other exams</td>{ar_rows(O)}</tr>"]) +
        f"""<ul><li><b>Assertion-Reason: "both true and R explains A" is the key about 4 times in 10</b> - <span class=ok>strong</span> in both columns.
"A false, R true" is the rarest (APPSC {r(A['assertion'].get('A false, R true', 0), sum(A['assertion'].values()))}). Method: decide A alone, then R alone;
only if both are true ask "does R answer <i>why</i> A?" - if you can put "because" between them, take option 1.</li></ul>
<h3>Match the following (4 pairs)</h3>
<ul><li>APPSC prints few code-style match questions ({m.get('parsed', 0)} with readable codes) - too few for a probability. What does hold:
<b>you never need all four pairs</b>. Fix the one pair you are surest of; usually only one or two codes keep it. Then check one more pair.</li>
<li><b>The "consensus" code</b> (the one agreeing most with the other three codes, pair by pair) was keyed {m.get('consensus right', 0)} of {m.get('consensus unique', 0)} times in APPSC
but only {mo.get('consensus right', 0)} of {mo.get('consensus unique', 0)} in other exams - <span class=weak>not reliable</span>.</li>
<li><b>The straight code A-1, B-2, C-3, D-4</b> was keyed {m.get('identity right', 0)}/{m.get('identity offered', 0)} in APPSC, {mo.get('identity right', 0)}/{mo.get('identity offered', 0)} elsewhere - examiners do
use it, so do not strike it for "looking too easy".</li>
<li>In APPSC the commoner match form is <b>"Which pair is correctly / INCORRECTLY matched?"</b> with four pairs as options - treat it as four
true/false statements; in INCORRECT form remember option 4 is keyed most.</li></ul>""")
    # 7. subject-wise
    parts = ["<h2>7. Subject by subject</h2>"]
    for b, s in A["subjects"].items():
        if not s["n"] or b == "0":
            continue
        k = s["kinds"]; t = s["n"]
        shapes = ", ".join(f"{E(x)} {r(c, t)}" for x, c in sorted(k.items(), key=lambda kv: -kv[1])[:5])
        po = s["position"]; pt = sum(po.values()) or 1
        so = s["options"]
        tips = []
        if so.get("none of the above n"):
            tips.append(f"'None of the above' keyed {so.get('none of the above right', 0)}/{so['none of the above n']}")
        if so.get("both n"):
            tips.append(f"'Both' keyed {so.get('both right', 0)}/{so['both n']}")
        if so.get("longest n"):
            tips.append(f"longest option keyed {r(so.get('longest right', 0), so['longest n'])}")
        units = "".join(f"<li>{E(u)} <b>({c})</b></li>" for u, c in s["units"][:8] if u)
        topics = "".join(f"<li>{E(u)} <b>({c})</b></li>" for u, c in s["topics"][:12])
        parts.append(f"""<h3>{E(BOOKS.get(b, b))} - {t} keyed APPSC questions</h3>
<p><b>Shapes:</b> {shapes}. <b>NOT-type:</b> {r(s['neg'], t)}. <b>Key position:</b> 1 {r(po.get('1', 0), pt)}, 2 {r(po.get('2', 0), pt)}, 3 {r(po.get('3', 0), pt)}, 4 {r(po.get('4', 0), pt)}.
<b>Option habits:</b> {'; '.join(tips)}.</p>
<div class=cols><div><b>Most-asked units</b><ol>{units}</ol></div><div><b>Most-asked topics</b><ol>{topics}</ol></div></div>""")
    sec.append("".join(parts))
    # 8. topic-wise patterns from the audit
    asked = {}
    for b in range(1, 7):
        for rr, qs in json.load(open(f"app/src/complete/assets/mcq{b}.json"))["rows"].items():
            asked[f"{b}:{rr}"] = sum(1 for q in qs if q.get("ap"))
    titles = {}
    for b in range(1, 7):
        ri = 0
        for u in json.load(open(f"app/src/complete/assets/book{b}.json"))["units"]:
            for x in u["rows"]:
                titles[f"{b}:{ri}"] = x["title"]; ri += 1
    import re
    parts = ["<h2>8. Topic by topic - how APPSC sets each high-yield topic</h2><p>The 15 topics per subject with the most APPSC questions, with what the examiner keeps asking there.</p>"]
    for b in range(1, 6):
        parts.append(f"<h3>{E(BOOKS[str(b)])}</h3>")
        for k in sorted((k for k in asked if k.startswith(f"{b}:")), key=lambda k: -asked[k])[:15]:
            f = f"data/pyq/audit/out/{k.replace(':', '-')}.json"
            pats = [p for p in (json.load(open(f)).get("patterns", []) if os.path.exists(f) else []) if not re.search(r"\bapp\b|app's|app MCQ", p, re.I)]
            if pats:
                parts.append(f"<div class=topic><b>{E(titles[k])}</b> <span class=n>({asked[k]} APPSC Qs)</span><ul>"
                             + "".join(f"<li>{E(p)}</li>" for p in pats[:4]) + "</ul></div>")
    sec.append("".join(parts))
    sec.append("""<h2>9. The one-page drill</h2><ol>
<li>Know it? Mark it. Don't use any trick on a question you know.</li>
<li>Half-know: strike "None of the above" and "Neither" first; strike anything you can disprove.</li>
<li>Two left in a NOT / INCORRECT question: prefer option 4.</li>
<li>Two left in a statement set: lean towards more statements true ("Both", "two of three") - "none" is rare.</li>
<li>A statement says exclusively / solely / entirely / any → suspect it false; first / largest / an AP fact → suspect it true.</li>
<li>Numbers / years: drop the smallest / earliest first.</li>
<li>Still stuck: the option sharing most words with the other three.</li>
<li>Blind (nothing ruled out): leave it - with 1/3 negative marking a blind guess gains nothing.</li></ol>""")
    css = """@page{size:A4;margin:15mm 13mm}body{font-family:'Noto Sans','DejaVu Sans',sans-serif;font-size:10pt;color:#1d1d1f;line-height:1.42}
h1{font-size:23pt;margin:0 0 4pt;color:#7a1f00}h2{font-size:14.5pt;color:#7a1f00;border-bottom:2px solid #7a1f00;padding-bottom:2pt;margin-top:16pt;page-break-after:avoid}
h3{font-size:11.5pt;margin:10pt 0 3pt;color:#0b3d91;page-break-after:avoid}.sub{color:#555}.box{background:#fff4ec;border-left:4px solid #7a1f00;padding:7pt 10pt;margin:8pt 0}
table{border-collapse:collapse;width:100%;margin:5pt 0;font-size:9pt;page-break-inside:avoid}td,th{border:1px solid #ccd;padding:3pt 5pt;text-align:left}th{background:#f3e9e2}
.n{color:#888;font-size:8pt}.ok{color:#0a7a2f;font-weight:700}.weak{color:#a66300;font-weight:700}.t{color:#0a7a2f}.f{color:#b00020}
.cols{display:flex;gap:14pt}.cols>div{flex:1}.cols ol{margin:2pt 0 0 14pt;padding:0;font-size:9pt}.topic{margin:5pt 0;page-break-inside:avoid}.topic ul{margin:2pt 0 3pt 15pt;padding:0}li{margin:1.5pt 0}"""
    doc = f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{''.join(sec)}</body></html>"
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    h = os.path.abspath(OUT.replace(".pdf", ".html"))
    open(h, "w").write(doc)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('file://{h}');await p.pdf({{path:'{os.path.abspath(OUT)}',format:'A4',printBackground:true}});await b.close();}})();")
    subprocess.run(["node", "-e", js], check=True)
    os.remove(h)
    print(OUT)


if __name__ == "__main__":
    main()
