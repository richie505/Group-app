"""APPSC Prelims & Mains: Cracked - the elimination rules and the exam strategy, each tested on APPSC's own papers.

    python3 tools/tricks_pdf.py      -> docs/APPSC-Cracked.html and docs/APPSC-Cracked.pdf
Uses tools/appsc_tricks.py (statements whose truth the key fixes), data/tricks/repeats-*.json and types.json.
"""
import collections, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T

E = html.escape
S, Q = [], []
PAPER = {}
for f in T.PAPERS:
    p = json.load(open(f))
    PAPER[os.path.basename(f)[:-5]] = p
    s, q = T.statements(f, p)
    S += s
    Q += q
ST = [x for x in S if x["kind"] != "item"]
MAIN = ["Group 2 Prelims", "Group 2 Mains", "Group 1 Prelims"]
OLD = "Earlier & other APPSC tests"
grp = lambda x: x["exam"] if x["exam"] in MAIN else OLD
BASE = sum(not x["true"] for x in ST) / len(ST)
REC = [x for x in ST if int(x["year"] or 0) >= 2023]
BASE_REC = sum(not x["true"] for x in REC) / len(REC)
types = json.load(open("data/tricks/types.json"))
rep35 = json.load(open("data/tricks/repeats-0.35.json"))
rep50 = json.load(open("data/tricks/repeats-0.5.json"))


def short_paper(x):
    return f"{x['exam'].replace('Group ', 'G')} {x['year']} · Q{x['n']}"


def rule_stats(k):
    hits = [x for x in ST if T.COMP[k].search(x["text"])]
    rows = []
    for g in MAIN + [OLD]:
        ys = sorted({x["year"] for x in hits if grp(x) == g}, reverse=True)
        for y in (ys if g != OLD else ["2008-20"]):
            h = [x for x in hits if grp(x) == g and (x["year"] == y or g == OLD)]
            if not h:
                continue
            w = [x for x in h if not x["true"]]
            rows.append((g, y, len(w), len(h) - len(w), len(h), 100 * len(w) / len(h), sorted({x["n"] for x in w})[:5]))
    w = [x for x in hits if not x["true"]]
    rec = [x for x in hits if int(x["year"] or 0) >= 2023]
    pick = lambda L: sorted(L, key=lambda x: (-int(x["year"] or 0), len(x["text"])))
    def distinct(L):
        seen, out = set(), []
        for x in L:
            if x["kind"] in ("list", "option") and 40 < len(x["text"]) < 260 and (x["paper"], x["n"]) not in seen \
                    and not re.search(r"\s[-–]\s*\(?([ivx]+|[IVX]+|\d)[.)]", x["text"]):
                seen.add((x["paper"], x["n"])); out.append(x)
        return out
    ok = distinct(pick(w))
    bad = distinct(pick([x for x in hits if x["true"]]))
    return {"n": len(hits), "w": len(w), "pct": 100 * len(w) / max(1, len(hits)), "rows": rows,
            "rec_n": len(rec), "rec_pct": 100 * sum(not x["true"] for x in rec) / max(1, len(rec)),
            "ok": ok[:2], "bad": bad[:1]}


def mark(text, k):
    t = E(text)
    return re.sub(T.R[k][1], lambda m: f"<mark>{m.group(0)}</mark>", t, flags=re.I)


# ---------------------------------------------------------------- the rules, grouped by what the data says
RULES = [
    # key, name, what to do, why examiners do it
    ("but_not", "\"…but…not…\" is a trap", "A statement that sets up a fact and then twists it with <b>but … not</b> (\"X is a Fundamental Right <i>but not</i> enforceable\") is usually false. Read it as two claims and test the second one hard.", "The twist is where the examiner plants the error."),
    ("only", "The word \"only\" is a red flag", "\"<b>Only</b> the President can…\", \"applicable <b>only</b> to…\": an exclusive claim is false in three of four APPSC statements. Ask yourself: is there really no second case?", "Real rules almost always have exceptions; \"only\" erases them."),
    ("extreme", "Extreme words make a statement fragile", "<b>always, never, all, none, every, any, entirely, must, cannot, solely</b>: one counter-example kills the statement. Unless you know it is a constitutional absolute, lean to <i>false</i>.", "Absolutes are easy to make wrong and hard to make right."),
    ("compare", "Comparisons are often swapped", "\"X <b>whereas</b> Y\", \"<b>unlike</b> X\", \"<b>higher than</b>\", \"<b>more than</b>\": the examiner often gives X's feature to Y. Check each side separately.", "A swapped comparison still sounds technical and correct."),
    ("negated", "A negative statement is usually the planted one", "Statements that themselves say <b>not / no / never / did not</b> (\"The Governor does <i>not</i> appoint…\") were false in about six of ten APPSC cases.", "Negating a true textbook line is the quickest way to write a false option."),
    ("by_institution", "\"Launched / set up / implemented <i>by</i> …\": check the body", "Schemes, missions, reports and bodies: the error is usually the <b>ministry, department or agency</b> named, not the scheme itself.", "The scheme is real; only its owner is swapped."),
    ("main", "\"Main / primary / chief aim\" is risky", "A statement that pins one <b>main objective</b> or <b>primary reason</b> on something with several is more often false.", "Most institutions and schemes have several aims."),
]
NOEDGE = [
    ("exactnum", "Exact figures", "UPSC students learn \"exact data is wrong\". In APPSC, statements with exact numbers were false at about the base rate: APPSC <b>does</b> test numbers (seats, percentages, distances, Articles). Learn them; don't eliminate them."),
    ("year", "Years and dates", "A precise year is no more likely to be wrong than any other statement. APPSC (especially AP history) asks dates straight."),
    ("constitution", "\"The Constitution provides / Article X says…\"", "The UPSC habit of distrusting \"according to the Constitution\" does not pay in APPSC: these statements were false at the base rate. Know the Article."),
    ("authority", "Named offices (President, Governor, Speaker…)", "The authority-swap trap exists, but overall statements naming an office are false only at the base rate. Use knowledge, not the rule."),
    ("because", "Reasons (because / due to / hence)", "A reason in the statement doesn't make it more likely false in APPSC."),
    ("intl_org", "Named international organisations", "Statements naming WHO / UNEP / World Bank etc. were <b>more often true</b> than false in APPSC. Don't eliminate on the name alone."),
]
REVERSE = [
    ("first", "\"First / largest / highest / oldest\" claims are usually TRUE", "APPSC loves superlatives and firsts (\"AP's first…\", \"the largest…\"), and about seven in ten of them were <b>true</b>. Do not eliminate a statement just because it says \"first\" or \"largest\"."),
    ("ap", "Andhra Pradesh claims are usually TRUE", "Statements about AP (places, dynasties, schemes, rivers) were true about two times in three. The examiner builds AP questions to <i>reward</i> AP knowledge, so the AP fact is usually right."),
    ("multi", "Statements packing two or more facts are usually TRUE", "The UPSC rule \"multiple facts = wrong\" fails in APPSC: long, packed statements were true in about six of ten cases (APPSC lifts them from textbook lines)."),
]
RARE = ["trend", "contemporary", "native", "binding", "tax", "hq"]


def verdict(p):
    return ("strong", "Strong") if p >= 65 else ("good", "Useful") if p >= 55 else ("none", "No edge") if p >= 42 else ("rev", "Reverse")


def table(st):
    out = ["<table class='proof'><tr><th>Exam</th><th>Year</th><th>Rule right</th><th>Rule failed</th><th>Total</th><th>% right</th><th>Questions (rule right)</th></tr>"]
    for g, y, w, f, t, p, refs in st["rows"]:
        out.append(f"<tr><td>{E(g)}</td><td>{y}</td><td>{w}</td><td>{f}</td><td>{t}</td><td class='{verdict(p)[0]}'>{p:.0f}%</td><td>{', '.join('Q' + str(r) for r in refs) if g != OLD else '—'}</td></tr>")
    out.append(f"<tr class='tot'><td colspan=2>All APPSC papers</td><td>{st['w']}</td><td>{st['n'] - st['w']}</td><td>{st['n']}</td><td class='{verdict(st['pct'])[0]}'>{st['pct']:.0f}%</td><td>base rate {100 * BASE:.0f}%</td></tr></table>")
    return "".join(out)


def example(x, k, ok=True):
    return (f"<div class='ex {'ok' if ok else 'bad'}'><span class='src'>{E(short_paper(x))}</span>"
            f"<span class='v'>{'FALSE in the key — rule works' if ok else 'TRUE in the key — rule fails'}</span><p>{mark(x['text'], k)}</p></div>")


def bars(items, maxv=100, unit="%", base=None, h=17):
    """horizontal bars: [(label, value, cls)]"""
    W, L = 640, 250
    rows = []
    for i, (lab, v, cls) in enumerate(items):
        y = i * (h + 8)
        w = (W - L - 60) * v / maxv
        rows.append(f"<text x='{L - 8}' y='{y + h * 0.7}' text-anchor='end' class='bl'>{E(lab)}</text>"
                    f"<rect x='{L}' y='{y}' width='{w:.1f}' height='{h}' rx='4' class='b-{cls}'/>"
                    f"<text x='{L + w + 6}' y='{y + h * 0.7}' class='bv'>{v:.0f}{unit}</text>")
    H = len(items) * (h + 8)
    if base is not None:
        x = L + (W - L - 60) * base / maxv
        rows.append(f"<line x1='{x}' y1='-4' x2='{x}' y2='{H}' class='base'/><text x='{x + 4}' y='{H + 12}' class='bv'>base rate {base:.0f}%</text>")
    return f"<svg viewBox='0 -6 {W} {H + 22}' class='chart'>{''.join(rows)}</svg>"


def stacked():
    order = ["direct", "statements", "which-statement", "matching", "assertion", "order"]
    lab = {"direct": "Direct one-liners", "statements": "Statement sets", "which-statement": "Which statement is (in)correct",
           "matching": "Matching / pairs", "assertion": "Assertion–Reason", "order": "Order / chronology"}
    pick = [("G2 Prelims 2017", "prelims-2017"), ("G2 Prelims 2019", "prelims-2019"), ("G2 Prelims 2024", "prelims-2024"),
            ("G2 Mains 2017 P-II", "mains-2017-paper2"), ("G2 Mains 2025 P-I", "mains-2025-paper1"), ("G2 Mains 2025 P-II", "mains-2025-paper2"),
            ("G1 Prelims 2017", "group1-prelims-2017-paper1"), ("G1 Prelims 2019 P-I", "group1-prelims-2019-paper1"),
            ("G1 Prelims 2023 P-I", "group1-prelims-2023-paper1"), ("G1 Prelims 2024 P-I", "group1-prelims-2024-paper1")]
    by = {r[2]: r for r in types}
    W, L, h = 640, 150, 15
    out = []
    for i, (name, key) in enumerate(pick):
        r = by[key]
        tot = sum(r[4].values())
        x = L
        y = i * (h + 5)
        out.append(f"<text x='{L - 8}' y='{y + 11}' text-anchor='end' class='bl'>{name}</text>")
        for t in order:
            v = r[4].get(t, 0)
            w = (W - L - 10) * v / tot
            if w > 0:
                out.append(f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' height='{h}' class='t-{t}'/>")
                if w > 26:
                    out.append(f"<text x='{x + w / 2:.1f}' y='{y + 11}' text-anchor='middle' class='tv'>{100 * v / tot:.0f}%</text>")
            x += w
    H = len(pick) * (h + 5)
    leg = "".join(f"<span><i class='t-{t}'></i>{lab[t]}</span>" for t in order)
    return f"<svg viewBox='0 0 {W} {H}' class='chart'>{''.join(out)}</svg><div class='legend'>{leg}</div>"


# ---------------------------------------------------------------- question-level numbers
def qstats(g):
    qs = [q for q in Q if q["exam"] == g]
    rec = [q for q in qs if int(q["year"] or 0) >= 2017]
    return qs, rec


def opt_rule(rx, qs):
    have = [q for q in qs if any(re.search(rx, x, re.I) for x in q["o"])]
    right = [q for q in have if re.search(rx, q["o"][q["a"]], re.I)]
    return len(have), len(right)


AOA = r"\ball (of )?(the )?(above|these|them)\b|^\s*all\b|\bI, II, III and IV\b|\b1, 2, 3 and 4\b|\ba, b, c and d\b"
NOTA = r"\bnone of (the )?(above|these|them)\b|^\s*none\b|\bneither\b"


def stdist(g, n):
    by = collections.defaultdict(list)
    for x in S:
        if x["exam"] == g and x["kind"] in ("list", "pair", "item"):
            by[(x["paper"], x["n"])].append(x["true"])
    c = collections.Counter(sum(v) for v in by.values() if len(v) == n)
    return [c[i] for i in range(n + 1)], sum(c.values())


def numeric(qs):
    mid = tot = 0
    for q in qs:
        nums = []
        for x in q["o"]:
            m = re.fullmatch(r"\s*[₹$]?\s*([\d,]+(?:\.\d+)?)\s*(%|per ?cent|crore|lakh|km|million|billion|kg|years|days|members|seats)?\.?\s*", x)
            nums.append(float(m.group(1).replace(",", "")) if m else None)
        if all(v is not None for v in nums) and len(set(nums)) == len(nums) == 4:
            tot += 1
            mid += sorted(range(4), key=lambda i: nums[i]).index(q["a"]) in (1, 2)
    return tot, mid


def longest(qs):
    t = r = 0
    for q in qs:
        L = [len(x) for x in q["o"]]
        if len(L) == 4 and min(L) > 20 and L.count(max(L)) == 1:
            t += 1
            r += L.index(max(L)) == q["a"]
    return t, r


def pos(qs):
    c = collections.Counter(q["a"] for q in qs if q["nopt"] == 4)
    return [c[i] for i in range(4)]


def ident(qs):
    IDN = r"\s*[aA]\s*-\s*(I|1)\s*,\s*[bB]\s*-\s*(II|2)\s*,\s*[cC]\s*-\s*(III|3)\s*,\s*[dD]\s*-\s*(IV|4)\s*"
    have = [q for q in qs if any(re.fullmatch(IDN, x) for x in q["o"])]
    return len(have), sum(bool(re.fullmatch(IDN, q["o"][q["a"]])) for q in have)


def ar(qs):
    c = collections.Counter()
    for q in qs:
        if not re.search(r"assertion|\(A\).*\(R\)|reason \(R\)", q["s"], re.I):
            continue
        t = q["o"][q["a"]].lower()
        if "both" in t and "not" not in t:
            c["both true, R explains A"] += 1
        elif "both" in t:
            c["both true, R doesn't explain A"] += 1
        elif re.search(r"\(a\) is (true|correct)|a is true|a is correct", t):
            c["A true, R false"] += 1
        elif re.search(r"\(a\) is (false|not correct|incorrect)|a is false", t):
            c["A false, R true"] += 1
        else:
            c["other"] += 1
    return c


ALLQ = [q for q in Q if q["exam"] in MAIN]
RECQ = [q for q in ALLQ if int(q["year"] or 0) >= 2023]
aoa_all, aoa_rec = opt_rule(AOA, ALLQ), opt_rule(AOA, RECQ)
nota_all, nota_rec = opt_rule(NOTA, ALLQ), opt_rule(NOTA, RECQ)
num_all = numeric([q for q in Q])
long_all = longest(ALLQ)
pos_rec = pos(RECQ)
id_all = ident(ALLQ)
ar_all = ar(ALLQ)
d2, n2 = stdist("Group 1 Prelims", 2)
d3, n3 = stdist("Group 1 Prelims", 3)
d4, n4 = stdist("Group 1 Prelims", 4)
m3, mn3 = stdist("Group 2 Mains", 3)
m4, mn4 = stdist("Group 2 Mains", 4)
p3, pn3 = stdist("Group 2 Prelims", 3)
p4, pn4 = stdist("Group 2 Prelims", 4)


def pct(a, b):
    return 100 * a / max(1, b)


# ---------------------------------------------------------------- page
CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
:root { --ink:#14213d; --body:#2b3445; --muted:#6b7280; --line:#e5e7eb; --accent:#3949ab; --soft:#eef0fb;
  --green:#15803d; --gsoft:#e8f5ec; --red:#b91c1c; --rsoft:#fdecec; --amber:#b45309; --asoft:#fdf3e2; }
* { box-sizing: border-box; }
body { font-family: Inter, 'DejaVu Sans', sans-serif; color: var(--body); font-size: 9.4pt; line-height: 1.42; margin: 0; background:#fff; }
h1 { font-size: 30pt; line-height: 1.1; color: var(--ink); margin: 0 0 6mm; letter-spacing: -0.5px; }
h2 { font-size: 17pt; color: var(--ink); margin: 0 0 3mm; padding-top: 1mm; letter-spacing: -0.2px; }
h3 { font-size: 11.5pt; color: var(--ink); margin: 3.5mm 0 1.2mm; }
p { margin: 0 0 2.5mm; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.kicker { font-size: 8.5pt; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: var(--accent); margin-bottom: 2mm; }
.cover { height: 260mm; display: flex; flex-direction: column; justify-content: space-between; }
.cover .band { background: linear-gradient(135deg,#1e3a8a,#3949ab); color: #fff; border-radius: 6mm; padding: 14mm 12mm; }
.cover .band h1 { color: #fff; font-size: 34pt; }
.cover .band p { color: #e0e7ff; font-size: 12pt; }
.facts { display: grid; grid-template-columns: repeat(4,1fr); gap: 4mm; margin-top: 8mm; }
.fact { background: var(--soft); border-radius: 3mm; padding: 4mm; }
.fact b { display: block; font-size: 20pt; color: var(--accent); line-height: 1.1; }
.fact span { font-size: 8.5pt; color: var(--muted); }
.note { font-size: 8.5pt; color: var(--muted); }
.box { border: 1px solid var(--line); border-radius: 3mm; padding: 2.6mm 3.4mm; margin: 2.2mm 0; break-inside: avoid; }
.box.blue { background: var(--soft); border-color: #c7cdf3; }
.box.green { background: var(--gsoft); border-color: #bfe3cb; }
.box.red { background: var(--rsoft); border-color: #f3c2c2; }
.box.amber { background: var(--asoft); border-color: #f1d4a4; }
.rule { break-inside: avoid; margin: 0 0 5mm; }
.rule .head { display: flex; align-items: baseline; gap: 3mm; border-bottom: 2px solid var(--ink); padding-bottom: 1mm; margin-bottom: 2mm; }
.rule .num { font-weight: 800; color: var(--accent); font-size: 11pt; white-space: nowrap; }
.rule .title { font-weight: 700; color: var(--ink); font-size: 12.5pt; flex: 1; }
.tag { font-size: 8pt; font-weight: 700; border-radius: 99px; padding: 0.6mm 2.6mm; white-space: nowrap; }
.tag.strong { background: var(--green); color: #fff; } .tag.good { background: var(--gsoft); color: var(--green); }
.tag.none { background: #eef0f3; color: var(--muted); } .tag.rev { background: var(--red); color: #fff; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 1.5mm 0; }
th { background: var(--ink); color: #fff; text-align: left; font-weight: 600; padding: 1.1mm 1.8mm; }
td { border-bottom: 1px solid var(--line); padding: 0.9mm 1.8mm; }
tr.tot td { font-weight: 700; background: #f7f8fb; }
td.strong { color: var(--green); font-weight: 700; } td.good { color: var(--green); }
td.none { color: var(--muted); } td.rev { color: var(--red); font-weight: 700; }
.ex { border-left: 3px solid var(--green); background: #f6fbf7; padding: 2mm 3mm; margin: 1.5mm 0; font-size: 9pt; }
.ex.bad { border-color: var(--red); background: #fdf6f6; }
.ex .src { font-weight: 700; color: var(--ink); margin-right: 2mm; } .ex .v { font-size: 8pt; color: var(--muted); }
.ex p { margin: 1mm 0 0; }
mark { background: #fde68a; padding: 0 0.5mm; border-radius: 1mm; }
.chart { width: 100%; height: auto; margin: 1mm 0 2mm; }
.bl { font-size: 11px; fill: #374151; } .bv { font-size: 10.5px; fill: #374151; font-weight: 600; } .tv { font-size: 9.5px; fill: #fff; font-weight: 700; }
.b-strong { fill: #15803d; } .b-good { fill: #4ade80; } .b-none { fill: #cbd5e1; } .b-rev { fill: #dc2626; } .b-blue { fill: #3949ab; }
line.base { stroke: #111827; stroke-dasharray: 4 3; stroke-width: 1.2; }
.t-direct { fill: #94a3b8; background: #94a3b8; } .t-statements { fill: #3949ab; background: #3949ab; } .t-which-statement { fill: #7c83db; background: #7c83db; }
.t-matching { fill: #0d9488; background: #0d9488; } .t-assertion { fill: #d97706; background: #d97706; } .t-order { fill: #be185d; background: #be185d; }
.legend { display: flex; flex-wrap: wrap; gap: 2mm 5mm; font-size: 8.5pt; color: var(--muted); }
.legend i { display: inline-block; width: 3mm; height: 3mm; border-radius: 1mm; margin-right: 1.2mm; vertical-align: -0.3mm; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }
ul, ol { margin: 0 0 2.5mm; padding-left: 5mm; } li { margin-bottom: 1mm; }
.big { font-size: 22pt; font-weight: 800; color: var(--accent); line-height: 1; }
.cheat { font-size: 9pt; } .cheat h3 { margin-top: 3mm; }
.toc li { margin-bottom: 1.5mm; }
.chips { display: flex; flex-wrap: wrap; gap: 1.5mm; margin: 1mm 0; }
.chip { font-size: 8pt; border-radius: 99px; padding: 0.6mm 2.4mm; }
.chip.f { background: var(--rsoft); color: var(--red); } .chip.t { background: var(--gsoft); color: var(--green); }
.chip i { font-style: normal; color: var(--muted); margin-left: 1mm; font-size: 7pt; }
.ex .truth { color: var(--green); }
"""


def cover():
    nst = len(ST)
    papers = len({q["paper"] for q in Q if q["nopt"]})
    return f"""<section class='page cover'><div>
<div class='band'><div class='kicker' style='color:#c7d2fe'>APPSC Group 1 &amp; Group 2 · Prelims &amp; Mains</div>
<h1>APPSC: Cracked</h1>
<p>Elimination rules, question patterns and a study plan, each one <b>tested on APPSC's own papers</b> and their keys
— not borrowed from UPSC.</p></div>
<div class='facts'>
<div class='fact'><b>{papers}</b><span>APPSC objective papers, 2008–2025</span></div>
<div class='fact'><b>{len(Q):,}</b><span>questions read with their keys</span></div>
<div class='fact'><b>{nst:,}</b><span>statements whose truth the key fixes</span></div>
<div class='fact'><b>{len(T.R)}</b><span>rules put to the test</span></div></div>
<h3 style='margin-top:10mm'>What's inside</h3>
<ol class='toc'>
<li><b>The exam has changed</b> — one-liners have given way to statements, matching and Assertion–Reason.</li>
<li><b>Seven rules that work in APPSC</b> — with a proof table for every exam and year.</li>
<li><b>UPSC rules that fail here</b> — and three that work the other way round in APPSC.</li>
<li><b>Question-type playbook</b> — 2-, 3-, 4-statement sets, All/None of the above, matching, A–R, numbers.</li>
<li><b>The negative-marking maths</b> — exactly when to guess.</li>
<li><b>What to study</b> — weightage, repeats from other exams, the Current Affairs window.</li>
<li><b>Exam-day method.</b></li>
<li><b>Subject by subject</b> — for each of the eight subjects: the rules that work there, the words its statements give away, how APPSC built its real false statements, and the topics asked most.</li>
<li><b>Proof across 40,000 PYQs and a backtest</b> — every rule checked on the app's whole PYQ bank, and a model that "sits" APPSC 2023–25 using the tricks alone.</li>
<li>A one-page <b>cheat sheet</b>.</li></ol></div>
<p class='note'>Data: the full APPSC papers in this app (Group 2 Prelims 2017 / 2019 / 2024, Group 2 Mains 2017 / 2025,
Group 2 2008 / 2012, Group 1 Prelims 2008–2024, and other APPSC screening tests 2017–2022) with their keys — official final
keys where APPSC published them; the Group 1 Prelims 2024 key is the initial key and the Group 2 2008 key is unofficial.
Group 2 Mains 2019 (question + answer only) and Mental Ability questions are left out. A rule is a probability, never a
certainty: knowledge comes first; rules are for the questions you can't answer from knowledge.</p></section>"""


def shift_page():
    g2p = {r[2]: r for r in types}
    d24 = g2p["prelims-2024"][4]
    g124 = g2p["group1-prelims-2024-paper1"][4]
    return f"""<section class='page'><div class='kicker'>Part 1</div><h2>The exam has changed</h2>
<p>Until 2019, an APPSC paper was almost entirely <b>direct one-liners</b>: "Who founded…?", "Where is…?". Recall was enough. From 2023
the papers look like UPSC's: <b>statement sets</b>, "which statement is incorrect", <b>matching</b>, <b>Assertion–Reason</b> and
<b>chronology</b>. In Group 1 Prelims 2024 Paper I only <b>{g124.get('direct', 0)} of 120</b> questions were direct.</p>
{stacked()}
<div class='cols'>
<div class='box blue'><b>What this means</b><ul>
<li>Knowing a fact roughly is no longer enough: each statement is a separate true/false test.</li>
<li>Elimination now decides marks: in Group 2 Prelims 2024, <b>{d24.get('statements', 0) + d24.get('which-statement', 0)} of 118</b> questions were statement-based.</li>
<li>Practice must be in the new format. One-liner drills build recall; statement drills build accuracy.</li></ul></div>
<div class='box amber'><b>Base rate to remember</b><p>Across all {len(ST):,} APPSC statements whose truth the key fixes,
<b>{100 * BASE:.0f}% were false</b> ({100 * BASE_REC:.0f}% in 2023–25 papers). So a rule only helps if the statements it picks
out are false clearly more often than {100 * BASE:.0f}%. Every rule in this guide is measured against that line.</p></div></div>
<h3>The current pattern (check the notification of your year)</h3>
<table><tr><th>Exam</th><th>Paper</th><th>Questions / marks</th><th>Sections</th></tr>
<tr><td>Group 2 Prelims</td><td>Screening test</td><td>150 / 150</td><td>Indian History, Geography, Indian Society, Current Affairs, Mental Ability — 30 each</td></tr>
<tr><td>Group 2 Mains</td><td>Paper I</td><td>150 / 150</td><td>Social &amp; Cultural History of AP (75) + Indian Constitution (75)</td></tr>
<tr><td>Group 2 Mains</td><td>Paper II</td><td>150 / 150</td><td>Indian &amp; AP Economy (75) + Science &amp; Technology (75)</td></tr>
<tr><td>Group 1 Prelims</td><td>Paper I · General Studies</td><td>120 / 120</td><td>History &amp; Culture, Constitution &amp; Polity, Indian &amp; AP Economy, Geography — about 30 each</td></tr>
<tr><td>Group 1 Prelims</td><td>Paper II · General Aptitude</td><td>120 / 120</td><td>Mental ability &amp; reasoning, plus Science &amp; Technology and Current Events</td></tr>
<tr><td>Group 1 Mains</td><td>Descriptive</td><td>—</td><td>Essay and General Studies papers; Telugu and English qualifying</td></tr></table>
<p class='note'>Objective APPSC papers carry negative marking (one-third of a question's marks for a wrong answer in recent
notifications) — Part 5 shows what that means for guessing.</p></section>"""


def rules_page():
    st = {k: rule_stats(k) for k in T.R}
    items = [(T.R[k][0].replace('"', '')[:34], st[k]["pct"], verdict(st[k]["pct"])[0]) for k, *_ in RULES] + \
            [(T.R[k][0].replace('"', '')[:34], st[k]["pct"], verdict(st[k]["pct"])[0]) for k, *_ in NOEDGE] + \
            [(T.R[k][0].replace('"', '')[:34], st[k]["pct"], verdict(st[k]["pct"])[0]) for k, *_ in REVERSE]
    over = f"""<section class='page'><div class='kicker'>Part 2</div><h2>Which rules actually work in APPSC</h2>
<p>For every rule: of the APPSC statements it fires on, how many were <b>false</b> in the key? The dashed line is the
{100 * BASE:.0f}% base rate. Bars well to the right are rules you can use; bars near the line are no help; red bars mean the
opposite of the UPSC advice is true in APPSC.</p>{bars(items, base=100 * BASE)}
<div class='legend'><span><i class='t-x' style='background:#15803d'></i>Strong (65%+)</span><span><i style='background:#4ade80'></i>Useful (55–65%)</span>
<span><i style='background:#cbd5e1'></i>No edge</span><span><i style='background:#dc2626'></i>Reverse: such statements are usually TRUE</span></div>
<div class='box blue' style='margin-top:4mm'><b>How to use a rule</b><ol>
<li>Answer from knowledge first. A rule never overrides something you know.</li>
<li>When unsure of a statement, check it against the strong rules; each one that fires tilts it toward <i>false</i>.</li>
<li>Use the option structure (Part 4): once one statement is decided, often only two options are left.</li>
<li>Guess only when the maths of Part 5 says so.</li></ol></div></section>"""
    pages = [over]
    cur = []
    for i, (k, name, do, why) in enumerate(RULES, 1):
        s = st[k]
        v = verdict(s["pct"])
        ex = "".join(example(x, k, True) for x in s["ok"]) + "".join(example(x, k, False) for x in s["bad"])
        cur.append(f"""<div class='rule'><div class='head'><span class='num'>Rule {i}</span><span class='title'>{name}</span>
<span class='tag {v[0]}'>{v[1]} · {s['pct']:.0f}% of {s['n']}</span></div><p>{do} <span class='note'>{why}</span></p>{table(s)}{ex}</div>""")
        if len(cur) == 2 or i == len(RULES):
            pages.append(f"<section class='page'>{'<div class=kicker>Part 2 · rules that work</div>' if len(pages) == 1 else ''}{''.join(cur)}</section>")
            cur = []
    # no edge + reverse
    ne = "".join(f"<div class='box'><b>{name}</b> <span class='tag none'>{st[k]['pct']:.0f}% false of {st[k]['n']}</span><p>{txt}</p></div>" for k, name, txt in NOEDGE)
    rv = "".join(f"""<div class='rule'><div class='head'><span class='num'>Reverse</span><span class='title'>{name}</span>
<span class='tag rev'>only {st[k]['pct']:.0f}% false of {st[k]['n']}</span></div><p>{txt}</p>{table(st[k])}
{''.join(example(x, k, False) for x in [x for x in sorted([x for x in ST if T.COMP[k].search(x['text']) and x['true']], key=lambda x: (-int(x['year'] or 0), len(x['text']))) if 40 < len(x['text']) < 240 and x['kind'] in ('list', 'option') and not re.search(r"\s[-–]\s*\(?([ivx]+|[IVX]+|\d)[.)]", x['text'])][:2])}</div>""" for k, name, txt in REVERSE)
    rare = ", ".join(f"{T.R[k][0]} ({st[k]['n']}×)" for k in RARE)
    pages.append(f"""<section class='page'><div class='kicker'>Part 3</div><h2>UPSC rules that don't pay in APPSC</h2>
<p>Coaching books built on UPSC teach these as elimination rules. On APPSC's own papers they are false no more often than any
other statement — use knowledge, not the rule.</p>{ne}
<p class='note'>Too rare in APPSC to matter (fired fewer than ten times in all papers): {E(rare)}.</p></section>""")
    pages.append(f"""<section class='page'><div class='kicker'>Part 3 · the reversals</div><h2>Three rules that run the other way in APPSC</h2>
<p>These are the costly ones: apply the UPSC habit here and you will eliminate the right answer.</p>{rv}</section>""")
    return "".join(pages), st


def playbook():
    def row(label, have, right, note, chance=25):
        r = pct(right, have)
        v = "clearly above chance" if r >= chance + 8 else "at chance level" if r < chance + 4 else "slightly above chance"
        return f"<tr><td>{label}</td><td>{have}</td><td>{right}</td><td><b>{r:.0f}%</b></td><td><b>{v[0].upper() + v[1:]}.</b> {note}</td></tr>"
    arc = ar_all
    arn = sum(arc.values())
    d3t = ", ".join(f"{i} true: {v}" for i, v in enumerate(d3))
    d4t = ", ".join(f"{i} true: {v}" for i, v in enumerate(d4))
    return f"""<section class='page'><div class='kicker'>Part 4</div><h2>Question-type playbook</h2>
<h3>Statement sets: how many statements are usually true?</h3>
<table><tr><th>Set</th><th>Exam</th><th>Questions</th><th>How many statements were true</th><th>Most likely</th></tr>
<tr><td>3 statements</td><td>Group 1 Prelims</td><td>{n3}</td><td>{d3t}</td><td><b>exactly 2 ({pct(d3[2], n3):.0f}%)</b>; all 3 in {pct(d3[3], n3):.0f}%</td></tr>
<tr><td>4 statements</td><td>Group 1 Prelims</td><td>{n4}</td><td>{d4t}</td><td><b>2 or 3 ({pct(d4[2] + d4[3], n4):.0f}%)</b>; all 4 only {pct(d4[4], n4):.0f}%</td></tr>
<tr><td>3 statements</td><td>Group 2 Mains</td><td>{mn3}</td><td>{', '.join(f'{i} true: {v}' for i, v in enumerate(m3))}</td><td>exactly 2</td></tr>
<tr><td>4 statements</td><td>Group 2 Mains</td><td>{mn4}</td><td>{', '.join(f'{i} true: {v}' for i, v in enumerate(m4))}</td><td>2 or 3; all 4 does happen in Mains</td></tr>
<tr><td>2 statements</td><td>Group 1 Prelims</td><td>{n2}</td><td>{', '.join(f'{i} true: {v}' for i, v in enumerate(d2))}</td><td>no safe pattern — decide each</td></tr></table>
<div class='box green'><b>The play:</b> in a 3- or 4-statement set, settle the statement you are surest of first and strike every
option that contradicts it. In Group 1 Prelims, "all four correct" was the key only {d4[4]} time(s) in {n4} four-statement sets
— with nothing else to go on, avoid it. In Group 2 Mains it is more common, so don't apply that there.</div>
<h3>Option-level rules</h3>
<table><tr><th>Pattern</th><th>Questions where it appeared</th><th>It was the key</th><th>Rate</th><th>Verdict (chance = 25%)</th></tr>
{row('"All of the above" / all statements', aoa_all[0], aoa_all[1], 'Never pick it by default; it is the key only about one time in four when it appears.')}
{row('"None of the above" / neither', nota_all[0], nota_all[1], 'Unlike UPSC, APPSC often keys NOTA / "neither": do not dismiss it.')}
{row('Straight matching code a-I, b-II, c-III, d-IV', id_all[0], id_all[1], 'The UPSC belief that it is never right does not hold here.')}
{row('Middle value among four numbers', num_all[0], num_all[1], 'Chance is 50% here: with no idea, pick one of the two middle values.', chance=50)}
{row('Longest option (sentence options)', long_all[0], long_all[1], 'No real edge: don\'t pick by length.')}</table>
<div class='cols'>
<div class='box'><b>Answer position (2023–25 papers)</b><p>A: {pos_rec[0]} · B: {pos_rec[1]} · C: {pos_rec[2]} · D: {pos_rec[3]}
— spread evenly. There is no "safe letter"; never fill blanks by pattern.</p></div>
<div class='box'><b>Assertion–Reason ({arn} questions)</b><p>{'; '.join(f'{k}: {v}' for k, v in arc.most_common())}.
Most often both are true and R explains A — but check that R really is the <i>reason</i>, not just a true sentence.</p></div></div>
<h3>Matching and chronology</h3>
<ul><li><b>Matching:</b> fix the one pair you are surest of, strike every code without it, then fix a second pair: usually one code is left.
Don't count on any code shape.</li>
<li><b>Chronology:</b> place the earliest and the latest event first; in APPSC orders the middle two decide fewer options than the ends.</li>
<li><b>"Which one is NOT correctly matched":</b> treat each pair as a true/false statement; the odd one out is often the pair with a swapped
place or person from the same family (two Mughal battles, two Satavahana kings).</li></ul></section>"""


def maths():
    rows = []
    for k, lab in [(0, "Pure guess (no option ruled out)"), (1, "One option ruled out"), (2, "Two options ruled out"), (3, "Three ruled out (you know it)")]:
        n = 4 - k
        ev = 1 / n - (n - 1) / n * (1 / 3)
        rows.append(f"<tr><td>{lab}</td><td>1 in {n}</td><td><b>{ev:+.2f}</b> marks</td><td>{'Skip' if ev <= 0.001 else 'Answer'}</td></tr>")
    return f"""<section class='page'><div class='kicker'>Part 5</div><h2>The negative-marking maths</h2>
<p>With one-third of a mark taken for a wrong answer, a blind guess on a four-option question is worth <b>exactly zero</b> on
average. Every option you can rule out makes guessing pay.</p>
<table><tr><th>Your situation</th><th>Chance right</th><th>Expected marks per question</th><th>Decision</th></tr>{''.join(rows)}</table>
<div class='cols'><div class='box green'><b>Rule of thumb</b><p>If you can strike <b>one</b> option with a real reason, answer.
Strike two, and the question is worth a third of a mark on average. Over 20 such questions that is about 7 marks — often the
cut-off margin.</p></div>
<div class='box red'><b>When not to guess</b><ul><li>All four options look equally possible (expected value zero, variance only).</li>
<li>The "reason" you struck an option with is a rule from Part 3 (no edge, or reverse).</li>
<li>You're changing an answer you got from knowledge on a gut feeling.</li></ul></div></div>
<h3>Using the rules together</h3><ol>
<li>Statements you know: mark them T/F.</li>
<li>Statements you don't: check Rules 1–7. Two or more firing = lean false; a reversal pattern (first/largest, AP fact, packed statement) = lean true.</li>
<li>Strike the options that disagree with your T/F marks. If two options remain, the question is worth about +0.33 marks: answer.</li></ol></section>"""


def study():
    w = {}
    for q in Q:
        if q["exam"] in MAIN:
            w.setdefault(f"{q['exam']} {q['year']}", collections.Counter())[q["subject"] or "?"] += 1
    def wt(key):
        c = w.get(key, {})
        tot = sum(c.values())
        return ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda x: -x[1]))
    reprow = "".join(f"<tr><td>{E(k)}</td><td>{v['n']}</td><td>{rep50[k]['repeat']} ({pct(rep50[k]['repeat'], v['n']):.0f}%)</td><td>{v['repeat']} ({pct(v['repeat'], v['n']):.0f}%)</td>"
                     f"<td>{', '.join(f'{ {'ot': 'other States/exams', 'up': 'UPSC', 'ap': 'other APPSC', 'g2': 'APPSC Group 2'}.get(t, t)} {n}' for t, n in sorted(v['by'].items(), key=lambda x: -x[1]))}</td></tr>"
                     for k, v in rep35.items())
    return f"""<section class='page'><div class='kicker'>Part 6</div><h2>What to study — from the papers themselves</h2>
<h3>Weightage is fixed by section — so no section can be skipped</h3>
<table><tr><th>Paper</th><th>Questions by subject</th></tr>
<tr><td>Group 2 Prelims 2024</td><td>{wt('Group 2 Prelims 2024')} (+ Mental Ability 30)</td></tr>
<tr><td>Group 2 Mains 2025</td><td>{wt('Group 2 Mains 2025')}</td></tr>
<tr><td>Group 1 Prelims 2024 (P-I + P-II Part B)</td><td>{wt('Group 1 Prelims 2024')}</td></tr>
<tr><td>Group 1 Prelims 2023 (P-I + P-II Part B)</td><td>{wt('Group 1 Prelims 2023')}</td></tr></table>
<h3>How much is asked again?</h3>
<p>Each recent question compared with {len([1])and '42,000+'} earlier PYQs (APPSC, UPSC, other State PSCs, SSC) in this app:</p>
<table><tr><th>Paper</th><th>Questions</th><th>Same question asked before</th><th>Same fact area asked before</th><th>Where the earlier one came from</th></tr>{reprow}</table>
<div class='box green'><b>The lesson:</b> only a small share repeats word for word, but about <b>one question in five</b> tests a fact
area already examined — and most of those come from <b>other State PSCs</b> (UPPSC, MPPSC, BPSC, TNPSC…) rather than APPSC or UPSC.
Practise other States' PYQs on Indian history, polity and geography, not only APPSC's.</div>
<h3>Current Affairs: the window and the AP share</h3>
<ul><li><b>Window:</b> every dated Current Affairs question in Group 2 Prelims 2024 (Feb 2024) was about 2023–24 events — the last
<b>12–15 months</b> before the exam, plus events announced for the coming year (e.g. the 2025 Asian Winter Games).</li>
<li><b>AP share:</b> 6 of 30 Current Affairs questions in Group 2 Prelims 2024, and 9 of 30 in Group 1 Prelims 2023, were about AP.
AP schemes, appointments, awards, investments and firsts are a guaranteed block.</li>
<li><b>Angles asked:</b> awards (who / field / edition), appointments, summits (venue, host, edition, theme), sports winners, firsts,
schemes (ministry, target group), reports (publisher, India's / AP's rank). Statement sets on one event (e.g. Asian Winter Games 2025:
venue, slogan, mascots, emblem) are now common — learn 3–4 facts per big event, not one.</li></ul>
<h3>Group 2 Mains 2025: the balance</h3>
<p>Paper I = AP history (75) + Constitution (75); Paper II = Economy with AP economy (75) + Science &amp; Technology (75). About half
of Paper I and a quarter of Paper II were statement, matching or A–R questions — study AP history and the Constitution at
statement depth (who, when, which Article, what exactly), not headline depth.</p></section>"""


def method():
    return f"""<section class='page'><div class='kicker'>Part 7</div><h2>Exam-day method</h2>
<div class='cols'>
<div><h3>Three passes</h3><ol>
<li><b>Pass 1 (about 60% of the time):</b> answer everything you know. Mark "?" on questions where you can strike at least one option, skip the rest.</li>
<li><b>Pass 2:</b> return to the "?" questions. Apply the statement rules and the option structure; answer when two options or fewer remain.</li>
<li><b>Pass 3 (last 10 minutes):</b> fill the OMR / review. Don't change knowledge answers on a feeling.</li></ol>
<h3>Reading a statement set</h3><ol>
<li>Read the question line first: <b>correct</b> or <b>incorrect</b>? (About one in seven statement questions in the 2023–25 papers asks for the incorrect ones — easy to misread under time.)</li>
<li>Mark each statement T / F / ? in the margin.</li>
<li>Look at the options before deciding the "?" ones: often they no longer matter.</li></ol></div>
<div><h3>Trap words to circle</h3>
<p><b>Lean false:</b> only · but…not · always / never / all / none / every · whereas / unlike / more than · not / no / did not ·
main / primary aim · launched / set up <i>by</i> (check the body).</p>
<p><b>Do NOT lean false:</b> exact figures · years · "Article X" · international organisations · named offices · reasons.</p>
<p><b>Lean true in APPSC:</b> first / largest / oldest · AP-specific facts · long statements packing several facts.</p>
<h3>Preparation that matches the new paper</h3><ul>
<li>Revise every topic as <b>true/false statements</b>, not only as one-liners: for each fact, know the likely twist (swapped body, year, place, number).</li>
<li>For AP history and the Constitution, keep "pairs" lists (ruler–capital, Article–subject, scheme–ministry): matching questions are built from them.</li>
<li>Practise 4-statement sets under time; aim for one decided statement per question before looking at options.</li>
<li>Current Affairs: 12–15 months back, AP first; for each big event, 3–4 facts.</li></ul></div></div></section>"""


def cheat(st):
    bank = lambda k: f" · all PYQs {CORP['rules'][k]['all'][1]:.0f}%" if CORP else ""
    good = "".join(f"<li><b>{T.R[k][0]}</b> — APPSC {st[k]['pct']:.0f}%{bank(k)} false</li>" for k, *_ in RULES)
    rev = "".join(f"<li><b>{T.R[k][0]}</b> — APPSC {st[k]['pct']:.0f}%{bank(k)} false</li>" for k, *_ in REVERSE)
    ne = "".join(f"<li>{T.R[k][0]}</li>" for k, *_ in NOEDGE)
    return f"""<section class='page cheat'><div class='kicker'>One page</div><h2>Cheat sheet</h2>
<div class='cols3'>
<div class='box green'><h3>Lean FALSE</h3><ul>{good}</ul></div>
<div class='box'><h3>No edge — use knowledge</h3><ul>{ne}</ul></div>
<div class='box red'><h3>Lean TRUE in APPSC</h3><ul>{rev}</ul><p class='note'>Bank-wide only the AP claims stay clearly true; the other two are near the 38% base — never eliminate on them.</p></div></div>
<div class='cols'>
<div class='box blue'><h3>Statement sets</h3><ul>
<li><b>Know one statement first</b>: it leaves ~2.5 options and lifts a guess from 25% to ~47% (backtest on APPSC 2023–25).</li>
<li>3 statements: exactly 2 true is most common ({pct(d3[2], n3):.0f}% in Group 1 Prelims).</li>
<li>4 statements: 2 or 3 true ({pct(d4[2] + d4[3], n4):.0f}%); all 4 rare in Prelims ({pct(d4[4], n4):.0f}%).</li>
<li>Decide the surest statement first; strike options that contradict it.</li>
<li>Check "correct" vs "incorrect" in the question line before marking.</li></ul></div>
<div class='box blue'><h3>Options</h3><ul>
<li>All of the above: key only {pct(aoa_all[1], aoa_all[0]):.0f}% of the times it appears — never a default.</li>
<li>None of the above / neither: key in {pct(nota_all[1], nota_all[0]):.0f}% — don't dismiss it.</li>
<li>Four numbers: a middle value {pct(num_all[1], num_all[0]):.0f}% of the time.</li>
<li>Straight a-I, b-II… code: chance only. Answer letters: evenly spread.</li></ul></div></div>
<div class='cols'>
<div class='box amber'><h3>Guessing (−⅓ per wrong answer)</h3><ul>
<li>Blind guess: 0 expected marks — skip.</li><li>One option struck: +0.11 — answer.</li><li>Two struck: +0.33 — answer.</li></ul></div>
<div class='box amber'><h3>Study priorities</h3><ul>
<li>Every section carries a fixed 30 (Prelims) / 75 (Mains): none can be skipped.</li>
<li>~1 in 5 questions repeats a fact area — mostly from other State PSCs.</li>
<li>Current Affairs: last 12–15 months; about a quarter on AP.</li></ul></div></div>
<p class='note'>Built from APPSC papers 2008–2025 and their keys; percentages are from those papers only. Rules are probabilities:
when you know the fact, the fact wins.</p></section>"""


# ---------------------------------------------------------------- Part 8: subject by subject
SUBJ = json.load(open("data/tricks/subjects.json")) if os.path.exists("data/tricks/subjects.json") else {}
TW = {}
for _f in sorted(__import__("glob").glob("data/tricks/twist-job-*.out.jsonl")):
    for _l in open(_f):
        if _l.strip():
            _o = json.loads(_l)
            TW[_o["id"]] = _o
FS = [json.loads(l) for l in open("data/tricks/false-statements.jsonl")] if os.path.exists("data/tricks/false-statements.jsonl") else []
TWN = {"swap-person": "Wrong person", "swap-place": "Wrong place", "swap-body": "Wrong body / office", "wrong-number": "Number changed",
       "wrong-date": "Date / order changed", "extreme": "Absolute word added", "negation": "\"not\" added or removed",
       "reversed": "Relation flipped", "wrong-category": "Wrong category", "overreach": "True core + wrong extra",
       "invented": "Invented claim", "other": "Other"}
ADVICE = {
    "Indian History": "<b>How to crack it:</b> most history statements are <b>true</b> (only 31% false), so in a set expect two or three correct and hunt for "
        "the <b>one wrong person</b> — a swapped ruler, author, founder or governor-general is the trap in a third of the false ones. Every 3-statement "
        "set had exactly 2 true; four of five 4-statement sets had 3 true. Still mostly direct questions (68%), so breadth of facts pays most.",
    "AP History & Culture": "<b>How to crack it:</b> the gentlest subject: only 23% of statements false, and AP-specific claims were true 92% of the time — "
        "the examiner rewards AP knowledge. The traps are a <b>wrong person</b> (poet, king, leader) or a <b>wrong place</b> (capital, temple, inscription). "
        "Matching is now 14% of the questions: keep ruler–capital, poet–work, movement–leader pairs.",
    "Polity & Constitution": "<b>How to crack it:</b> the harshest subject: half the statements are false, and 4-statement sets most often had only <b>1 or 2</b> "
        "true (all four just 3 of 40). The favourite trap is a <b>\"not\" added or removed</b>, then a <b>wrong category</b> (Fundamental Right vs DPSP, "
        "Article vs Schedule) and a <b>wrong Article number</b>. \"but\", \"however\", \"the Constitution\", \"Parliament / House / Lok Sabha\" lean false; "
        "\"elected\" leans true.",
    "Indian Society": "<b>How to crack it:</b> more than half the statements are false. The traps are mostly <b>a changed year or number</b> on an Act or "
        "scheme (POCSO 2012, JJ Act 2015, age limits) and a stretched scope. Learn each Act's year and its exact beneficiaries; small sample, so lean on knowledge.",
    "Economy": "<b>How to crack it:</b> half the statements are false, and the favourite trap is a <b>flipped relation</b> (a third of them): raising CRR "
        "<i>increases</i> credit, a weaker rupee <i>cuts</i> exports. For every cause–effect, check the direction. Negative statements were false 88% of the time, "
        "comparisons 78%, extreme words 70%. Assertion–Reason is now 13% of Economy questions.",
    "Geography": "<b>How to crack it:</b> the traps are a <b>flipped direction</b> (east/west-flowing, higher/lower, north/south) and a <b>wrong place</b> "
        "(river, pass, state, port). Unlike other subjects, \"first / largest\" claims here were <b>false</b> 67% of the time (the examiner moves the record "
        "to a neighbour), while packed multi-fact statements were all true. Matching is now 16% of Geography questions — learn location pairs.",
    "Science, Technology & Environment": "<b>How to crack it:</b> the traps are a <b>wrong agency</b> (ISRO vs DRDO, MoEFCC vs CPCB), a <b>changed number</b> and "
        "a <b>flipped</b> effect. Years and long technical statements were usually true (only 25% false). Statement sets dominate 2023–25 (28%), with "
        "\"exactly 2 of 3\" the common answer. Waste, biotechnology and nuclear energy are the rising topics.",
    "Current Affairs": "<b>How to crack it:</b> the examiner swaps the <b>venue / host country</b> and the <b>organiser / ministry</b> (half the false "
        "statements). \"First\" claims were almost always true (only 12% false) and \"was held\" statements were true. In 4-statement sets, 3 true was the most "
        "common answer. For each big event learn venue, host, edition, theme and who organised it.",
}


def twists_of(sj):
    rows = [(x, TW.get(x["id"])) for x in FS if x["subject"] == sj]
    rows = [(x, t) for x, t in rows if t and not t.get("doubt")]
    c = collections.Counter(t["twist"] for _, t in rows if t["twist"] != "other")
    return rows, c


def hl(text, spot):
    t = E(text)
    sp = E(spot or "")
    if sp and sp in t:
        t = t.replace(sp, f"<mark>{sp}</mark>", 1)
    return t


def mix_bar(m_old, m_new):
    order = ["direct", "statements", "which-statement", "matching", "assertion", "order"]
    W, L, h = 640, 90, 15
    out = []
    for i, (lab, m) in enumerate((("2017–19", m_old), ("2023–25", m_new))):
        tot = max(1, sum(m.values()))
        x, y = L, i * (h + 5)
        out.append(f"<text x='{L - 8}' y='{y + 11}' text-anchor='end' class='bl'>{lab}</text>")
        for t in order:
            w = (W - L - 10) * m.get(t, 0) / tot
            if w > 0:
                out.append(f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' height='{h}' class='t-{t}'/>")
                if w > 26:
                    out.append(f"<text x='{x + w / 2:.1f}' y='{y + 11}' text-anchor='middle' class='tv'>{100 * m.get(t, 0) / tot:.0f}%</text>")
            x += w
    return f"<svg viewBox='0 0 {W} {2 * (h + 5)}' class='chart' style='max-height:16mm'>{''.join(out)}</svg>"


def subject_page(sj, d):
    base = d["base"]
    newst = d["mix_new"]
    nn = max(1, sum(newst.values()))
    stshare = 100 * (nn - newst.get("direct", 0)) / nn
    # rules in this subject: compare with the subject's own base
    rr = []
    for k, r in sorted(d["rules"].items(), key=lambda kv: -kv[1]["pct"]):
        diff = r["pct"] - base
        cls = "strong" if diff >= 20 else "good" if diff >= 10 else "rev" if diff <= -10 else "none"
        word = "lean FALSE" if diff >= 10 else "lean TRUE" if diff <= -10 else "no edge"
        rr.append(f"<tr><td>{E(r['title'])}</td><td>{r['n']}</td><td class='{cls}'>{r['pct']:.0f}%</td><td class='{cls}'>{word}</td></tr>")
    rules = ("<table><tr><th>Rule (in this subject)</th><th>Statements</th><th>False</th><th>Use it as</th></tr>" + "".join(rr) + "</table>") if rr else \
        "<p class='note'>Too few statements in this subject for any rule to be measured on its own; use the general rules of Part 2.</p>"
    chip = lambda c, cls: f"<span class='chip {cls}'>{E(c[0])} <b>{c[3]}%</b><i>{c[1]}</i></span>"
    cues = ""
    if [c for c in d["lean_false"] if c[2] >= 4] or d["lean_true"]:
        cues = "<h3>Words found in this subject's statements</h3><div class='chips'>" + \
               "".join(chip(c, "f") for c in d["lean_false"][:10] if c[2] >= 4) + "".join(chip(c, "t") for c in d["lean_true"][:6]) + \
               "</div><p class='note'>Red: statements with this word were false that often (number of statements in grey). " \
               "Green: usually true. Only words seen in 5+ statements and well away from this subject's base rate.</p>"
    rows, c = twists_of(sj)
    anat = ""
    if c:
        tot = sum(c.values())
        items = [(TWN.get(k, k), 100 * v / tot, "blue") for k, v in c.most_common(6)]
        exs = []
        seen = set()
        for k, _ in c.most_common(3):
            for x, t in sorted(rows, key=lambda r: -int(r[0]["year"] or 0)):
                if t["twist"] == k and x["id"] not in seen and len(x["statement"]) < 180:
                    seen.add(x["id"])
                    exs.append(f"<div class='ex'><span class='src'>{E(TWN.get(k, k))}</span><span class='v'>{E(x['exam'].replace('Group ', 'G'))} {x['year']}</span>"
                               f"<p>✗ {hl(x['statement'], t.get('spot'))}</p><p class='truth'>✓ {E(t.get('truth', ''))}</p></div>")
                    break
        anat = f"<div style='break-inside:avoid'><h3>Trap anatomy: how APPSC built {tot} of its false statements in this subject</h3>{bars(items, base=None, h=13)}{''.join(exs)}</div>"
    dist = []
    for n in ("3", "4"):
        v = d["dist"].get(n) or d["dist"].get(int(n)) or []
        if sum(v) >= 3:
            dist.append(f"{n}-statement sets ({sum(v)}): " + ", ".join(f"{i} true: {k}" for i, k in enumerate(v)))
    tops = "".join(f"<tr><td>{E(t['topic'])}</td><td>{t['q17']}</td><td>{t['q23']}</td><td>{t['st']}</td></tr>" for t in d["topics"][:8])
    hot = "" if sj == "Current Affairs" else ", ".join(E(h) for h in d["hot"][:6])
    adv = ADVICE.get(sj, "")
    return f"""<section class='page'><div class='kicker'>Part 8 · subject by subject</div><h2>{E(sj)}</h2>
<div class='facts' style='margin-top:1mm;grid-template-columns:repeat(4,1fr)'>
<div class='fact'><b>{d['questions']}</b><span>questions in APPSC papers (all years)</span></div>
<div class='fact'><b>{stshare:.0f}%</b><span>non-direct in 2023–25 (statements, matching, A–R…)</span></div>
<div class='fact'><b>{d['statements']}</b><span>statements with a known truth</span></div>
<div class='fact'><b>{base:.0f}%</b><span>of them false — this subject's base rate</span></div></div>
{mix_bar(d['mix_old'], d['mix_new'])}
{('<div class="box green">' + adv + '</div>') if adv else ''}
<div class='cols'><div>{rules}{cues}</div>
<div><h3>Most asked topics (2017–25)</h3><table><tr><th>Topic</th><th>Qs</th><th>2023–25</th><th>Stmts</th></tr>{tops}</table>
{('<p><b>Rising in 2023–25:</b> ' + hot + '</p>') if hot else ''}{('<p class="note">' + '<br>'.join(dist) + '</p>') if dist else ''}</div></div>
{anat}</section>"""


def subjects_overview():
    rows = []
    for sj, d in SUBJ.items():
        nn = max(1, sum(d["mix_new"].values()))
        rows_, c = twists_of(sj)
        top = ", ".join(TWN.get(k, k) for k, _ in c.most_common(2)) if c else "—"
        good = [r["title"] for r in sorted(d["rules"].values(), key=lambda r: -r["pct"]) if r["pct"] - d["base"] >= 10][:2]
        rev = [r["title"] for r in sorted(d["rules"].values(), key=lambda r: r["pct"]) if r["pct"] - d["base"] <= -10][:2]
        rows.append(f"<tr><td><b>{E(sj)}</b></td><td>{d['base']:.0f}%</td><td>{100 * (nn - d['mix_new'].get('direct', 0)) / nn:.0f}%</td>"
                    f"<td>{E(top)}</td><td>{E('; '.join(good)) or '—'}</td><td>{E('; '.join(rev)) or '—'}</td></tr>")
    return f"""<section class='page'><div class='kicker'>Part 8</div><h2>Subject by subject: at a glance</h2>
<p>The general rules hide big differences between subjects. In AP history the examiner mostly writes <b>true</b> statements; in
Polity and Economy about half are false. The trap the examiner prefers also changes by subject. Each subject page that follows
measures the rules inside that subject, lists the words its statements give away, dissects its real false statements, and ranks
its topics.</p>
<table><tr><th>Subject</th><th>Statements false</th><th>Non-direct Qs 2023–25</th><th>Favourite traps</th><th>Lean FALSE on</th><th>Lean TRUE on</th></tr>{''.join(rows)}</table>
<div class='box blue'><b>Reading the base rate.</b> It is the share of this subject's statements that were false. When it is low
(AP history ~{SUBJ.get('AP History & Culture', {}).get('base', 0):.0f}%), an unsure statement is more likely true — so in a "which are correct"
set the option with more statements is the better bet; when it is high (Polity ~{SUBJ.get('Polity & Constitution', {}).get('base', 0):.0f}%), treat every
statement as a coin you must test.</div></section>"""


# ---------------------------------------------------------------- Part 9: the whole PYQ bank + backtest
CORP = json.load(open("data/tricks/corpus.json")) if os.path.exists("data/tricks/corpus.json") else {}
BT = json.load(open("data/tricks/backtest.json")) if os.path.exists("data/tricks/backtest.json") else {}


def bank_pages():
    if not CORP:
        return ""
    tiers = ["g2", "ap", "up", "ot", "all"]
    tn = {"g2": "APPSC Group 2", "ap": "Other APPSC", "up": "UPSC", "ot": "Other PSCs", "all": "All PYQs"}
    base = CORP["base"]
    rows = []
    for k, r in sorted(CORP["rules"].items(), key=lambda kv: -kv[1]["all"][1]):
        if r["all"][0] < 30:
            continue
        cells = []
        for t in tiers:
            n, pc = r[t]
            cls = "" if n < 12 else ("strong" if pc - base >= 20 else "good" if pc - base >= 10 else "rev" if pc - base <= -5 else "none")
            cells.append(f"<td class='{cls}'>{pc:.0f}% <span class='note'>{n}</span></td>" if n else "<td>—</td>")
        d = r["all"][1] - base
        call = "<b>lean FALSE</b>" if d >= 10 else "slight lean false" if d >= 5 else "<b>lean TRUE</b>" if d <= -5 else "no edge"
        rows.append(f"<tr><td>{E(r['title'])}</td>{''.join(cells)}<td>{call}</td></tr>")
    tt = "".join(f"<tr><td>{E(v['name'])}</td><td>{v['pyq']:,}</td><td>{v['n']:,}</td><td>{v['false']:.0f}%</td></tr>" for v in CORP["tiers"].values())
    cues = ""
    for sj, d in CORP["subjects"].items():
        lf = [c for c in d["lean_false"] if c[2] >= 8][:10]
        lt = d["lean_true"][:6]
        if not lf and not lt:
            continue
        cues += (f"<div class='box'><b>{E(sj)}</b> <span class='note'>{d['n']:,} statements, {d['base']:.0f}% false</span><div class='chips'>"
                 + "".join(f"<span class='chip f'>{E(c[0])} <b>{c[3]}%</b><i>{c[1]}</i></span>" for c in lf)
                 + "".join(f"<span class='chip t'>{E(c[0])} <b>{c[3]}%</b><i>{c[1]}</i></span>" for c in lt) + "</div></div>")
    p1 = f"""<section class='page'><div class='kicker'>Part 9 · the whole PYQ bank</div><h2>Proof across {CORP['n_pyq']:,} PYQs</h2>
<p>APPSC's own papers give a few hundred statements per rule at best. The app's PYQ bank — APPSC, UPSC, other State PSCs and SSC
papers, duplicates removed — gives <b>{CORP['n_st']:,} statements</b> whose truth the key fixes. Same method: of the statements a rule
fires on, how many were false? Base rate across the bank: <b>{base:.0f}%</b>.</p>
<table style='width:60%'><tr><th>Exam family</th><th>PYQs</th><th>Statements</th><th>False</th></tr>{tt}</table>
<table style='font-size:7.6pt'><tr><th>Rule</th>{''.join(f'<th>{tn[t]}</th>' for t in tiers)}<th>Verdict (bank)</th></tr>{''.join(rows)}</table>
<p class='note'>Grey numbers = statements the rule fired on. Colours only where at least 12 statements.</p>
</section>"""
    p2 = f"""<section class='page'><div class='kicker'>Part 9 · the whole PYQ bank</div><h2>Words that give a statement away — confirmed on thousands</h2>
<p>The same word search as in Part 8, now on the whole bank: a word is listed only if it appeared in 20+ statements and its false rate is
far from the subject's base (red = lean false, green = lean true; grey = number of statements).</p><div class='box amber'><b>What the bigger sample changes</b><ul>
<li><b>Confirmed strong everywhere:</b> "only" and "but … not" are false about seven times in ten in every exam family; "launched / set up by …"
and extreme words also lean false (extreme words most in UPSC, least in other PSCs).</li>
<li><b>Confirmed no edge:</b> exact figures and years are false at the base rate in every family — learn them, never eliminate on them.</li>
<li><b>Corrected:</b> comparisons (whereas / unlike) are only a weak signal across the bank (46%), not the 62% the APPSC papers alone suggested.
"First / largest" claims are false at about the base rate overall — leaning true only in APPSC Group 2. Either way: never eliminate on them.</li>
<li><b>UPSC habits that don't transfer:</b> "The Constitution provides / Article X…" is false 74% of the time in UPSC but only 32% in other APPSC exams.</li>
<li><b>Lean TRUE everywhere:</b> Andhra Pradesh-specific claims ({CORP['rules']['ap']['all'][1]:.0f}% false across {CORP['rules']['ap']['all'][0]} statements).</li></ul></div>{cues}
<div class='box blue'><b>Polity, the subject with the most robust cues:</b> statements about <b>who is a member of</b> a body, what a <b>Schedule</b>
contains, what <b>cannot be</b> done and what <b>the Government</b> does are false about seven times in ten. Statements about <b>electoral</b>
matters and <b>funds</b> (Consolidated / Contingency) are usually true. In Economy, a named <b>ministry</b> is the trap (75% false); in Geography,
"<b>located</b> in …" statements are usually true.</div></section>"""
    if not BT:
        return p1 + p2
    q = BT["questions"]
    k1 = q.get("k1", 0)
    p3 = f"""<section class='page'><div class='kicker'>Part 9 · the backtest</div><h2>Can the tricks alone crack APPSC 2023–25?</h2>
<p>A fair test: a model learns the rules and the words of statements from the PYQ bank only — {BT['train']:,} statements, with every
statement of the recent papers taken out — and then "sits" APPSC Group 1 Prelims 2023 and 2024, Group 2 Prelims 2024 and Group 2 Mains
2025 knowing nothing about the subjects.</p>
<div class='facts' style='grid-template-columns:repeat(4,1fr)'>
<div class='fact'><b>{BT['test']}</b><span>statements in the recent papers ({BT['test_false']:.0f}% false)</span></div>
<div class='fact'><b>{BT['rules+words']['auc']:.2f}</b><span>AUC (0.50 = no signal, 1.00 = perfect)</span></div>
<div class='fact'><b>{100 * q['right'] / max(1, q['questions']):.0f}%</b><span>of {q['questions']} statement questions right, picking blind (chance 25%)</span></div>
<div class='fact'><b>{BT['marks']:+.0f}</b><span>marks over those {q['questions']} questions with −⅓ negative marking</span></div></div>
<h3>What it shows</h3><ol>
<li><b>The tricks are real but small.</b> Judging statements blind, the model is right {BT['rules+words']['acc']:.0f}% of the time — barely
better than calling everything true. On the {BT['rules+words']['conf_share']:.0f}% of statements where the signal is strong (several cues
at once), it is right {BT['rules+words']['acc_conf']:.0f}%.</li>
<li><b>Picking options blind still pays a little:</b> {100 * q['right'] / max(1, q['questions']):.0f}% right against 25% chance is worth about
+{BT['marks'] / max(1, q['questions']):.2f} marks per question — positive, but no way to clear a cut-off.</li>
<li><b>Knowing ONE statement is worth far more than every trick.</b> Simulated on the same questions: if you are sure of just one statement and
strike the options that contradict it, <b>{q.get('k1_left', 0) / max(1, k1):.1f}</b> options are left on average and a guess among them is
right <b>{100 * q.get('k1_guess', 0) / max(1, k1):.0f}%</b> of the time (+{(q.get('k1_guess', 0) / max(1, k1)) * 4 / 3 - 1 / 3:.2f} marks per
question). Letting the tricks choose among those remaining options lifts it to <b>{100 * q.get('k1_model', 0) / max(1, k1):.0f}%</b>.</li>
<li><b>Elimination by the tricks:</b> the option the model ranks last was wrong {100 * BT['elim']['worst_wrong'] / max(1, BT['elim']['n']):.0f}%
of the time (chance 75%) — use the tricks to strike, not to choose.</li></ol>
<div class='box green'><b>The conclusion for the exam hall:</b> (1) settle the one statement you are surest of — that alone roughly doubles your
odds; (2) strike every option that contradicts it; (3) only then use the trap words ("only", "but…not", extreme words, "launched by")
to choose among what is left; (4) answer whenever two or fewer options remain. Tricks are the tie-breaker, knowledge of single
statements is the engine.</div>
<h3>Which cues carry the most weight (learnt from the bank)</h3>
<p class='note'>{' · '.join(f"{E(t)} {w:+.2f}" for t, w in BT.get('weights', [])[:12])}</p>
<p class='note'>Weights are log-odds of "false" when the cue fires, all cues together; positive = lean false, negative = lean true.</p></section>"""
    return p1 + p2 + p3


def main():
    rp, st = rules_page()
    body = cover() + shift_page() + rp + playbook() + maths() + study() + method() + subjects_overview() + "".join(subject_page(sj, d) for sj, d in SUBJ.items()) + bank_pages() + cheat(st)
    doc = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>APPSC: Cracked</title><style>{CSS}</style></head><body>{body}</body></html>"
    os.makedirs("docs", exist_ok=True)
    open("docs/APPSC-Cracked.html", "w").write(doc)
    import subprocess
    subprocess.run(["node", "tools/html_to_pdf.js", "docs/APPSC-Cracked.html", "docs/APPSC-Cracked.pdf", "APPSC: Cracked"], check=True)
    print("docs/APPSC-Cracked.pdf")


if __name__ == "__main__":
    main()
