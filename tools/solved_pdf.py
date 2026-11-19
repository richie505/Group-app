"""The latest APPSC papers, solved: every question with the method used, the steps to the key, the words that support
the trick underlined, the fact to remember, and the earlier PYQ it reflects (data/solved/job-*.out.jsonl,
data/solved/reflect.json).

    python3 tools/solved_pdf.py     -> docs/solved/APPSC-<paper>-Solved.pdf (one per exam) + a summary
"""
import collections, glob, html, json, os, re, subprocess

E = html.escape
PAPERS = [
    ("G1-Prelims-2024", "APPSC Group 1 Prelims 2024 — Solved", "Paper I General Studies (120) and Paper II Part B: Science & Technology, Current Events (60). "
     "Held 17 March 2024. Key: APPSC's initial key (the final key was not available).",
     [("g1p24p1", "data/appscpapers/group1-prelims-2024-paper1.json", "Paper I · General Studies"),
      ("g1p24p2", "data/appscpapers/group1-prelims-2024-paper2.json", "Paper II · Part B")]),
    ("G2-Prelims-2024", "APPSC Group 2 Prelims 2024 — Solved", "Screening test held 25 February 2024 (Series A). Final key. Mental Ability questions are not included.",
     [("g2p24", "data/g2papers/prelims-2024.json", "General Studies")]),
    ("G2-Mains-2025", "APPSC Group 2 Mains 2025 — Solved", "Held 23 February 2025 (Series A). Final key.",
     [("g2m25p1", "data/g2papers/mains-2025-paper1.json", "Paper I · AP History & Constitution"),
      ("g2m25p2", "data/g2papers/mains-2025-paper2.json", "Paper II · Economy and Science & Technology")]),
]
SOL = {}
for f in sorted(glob.glob("data/solved/job-*.out.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            SOL[(o["paper"], int(o["n"]))] = o
REF = json.load(open("data/solved/reflect.json"))["questions"] if os.path.exists("data/solved/reflect.json") else {}
LET = "abcd"

CSS = """
@page { size: A4; margin: 13mm 13mm 14mm 13mm; }
:root { --ink:#14213d; --body:#2b3445; --muted:#6b7280; --line:#e5e7eb; --accent:#3949ab; --soft:#eef0fb; --green:#15803d; --gsoft:#e8f5ec;
  --red:#b91c1c; --rsoft:#fdecec; --amber:#b45309; --asoft:#fdf3e2; }
body { font-family: Inter, 'DejaVu Sans', sans-serif; color: var(--body); font-size: 8.9pt; line-height: 1.4; margin: 0; }
h1 { font-size: 24pt; color: var(--ink); margin: 0 0 3mm; } h2 { font-size: 14pt; color: var(--ink); margin: 5mm 0 2mm; }
h3 { font-size: 11pt; color: var(--ink); margin: 3mm 0 1mm; }
.cover { page-break-after: always; }
.band { background: linear-gradient(135deg,#1e3a8a,#3949ab); color: #fff; border-radius: 5mm; padding: 9mm 9mm; }
.band h1 { color: #fff; } .band p { color: #e0e7ff; margin: 0; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 1.5mm 0 3mm; }
th { background: var(--ink); color: #fff; text-align: left; padding: 1mm 1.6mm; font-weight: 600; }
td { border-bottom: 1px solid var(--line); padding: 0.8mm 1.6mm; }
.q { border: 1px solid var(--line); border-radius: 2.5mm; padding: 2.4mm 3mm; margin: 0 0 2.6mm; break-inside: avoid; }
.qh { display: flex; gap: 2mm; align-items: baseline; flex-wrap: wrap; margin-bottom: 1mm; }
.qn { font-weight: 800; color: var(--accent); font-size: 10pt; }
.tag { font-size: 7.3pt; font-weight: 700; border-radius: 99px; padding: 0.3mm 2mm; background: var(--soft); color: var(--accent); }
.tag.m { background: var(--ink); color: #fff; } .tag.r1 { background: #b91c1c; color: #fff; } .tag.r2 { background: var(--asoft); color: var(--amber); }
.tag.r3 { background: #fef3c7; color: #92400e; } .tag.del { background: var(--rsoft); color: var(--red); }
.stem { white-space: pre-line; color: var(--ink); font-size: 9.1pt; margin-bottom: 1mm; }
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6mm 4mm; margin: 0.6mm 0 1.4mm; }
.opt { padding: 0.5mm 1.6mm; border-radius: 1.5mm; }
.opt.key { background: var(--gsoft); color: var(--green); font-weight: 700; }
u { text-decoration: none; border-bottom: 2px solid #f59e0b; background: #fef9c3; padding: 0 0.3mm; }
.steps { margin: 0.5mm 0 0.6mm; padding-left: 4.5mm; } .steps li { margin: 0.2mm 0; }
.why { font-size: 7.6pt; color: var(--muted); } .why b { color: #92400e; }
.fact { font-size: 8pt; color: var(--green); margin-top: 0.6mm; }
.prev { font-size: 7.6pt; color: var(--muted); margin-top: 0.6mm; border-top: 1px dashed var(--line); padding-top: 0.6mm; }
.note { font-size: 7.6pt; color: var(--muted); }
.sec { background: var(--soft); color: var(--accent); font-weight: 800; padding: 1.6mm 3mm; border-radius: 2mm; margin: 2mm 0 2.4mm; }
"""


def mark(text, spans):
    """underline the given substrings (non-overlapping, first occurrence each)"""
    t = text
    marks = []
    for sp in spans:
        if not sp:
            continue
        i = t.find(sp)
        if i < 0:
            continue
        if any(not (i + len(sp) <= a or i >= b) for a, b in marks):
            continue
        marks.append((i, i + len(sp)))
    out, last = [], 0
    for a, b in sorted(marks):
        out.append(E(t[last:a]) + "<u>" + E(t[a:b]) + "</u>")
        last = b
    out.append(E(t[last:]))
    return "".join(out)


def card(code, q):
    s = SOL.get((code, q["n"]), {})
    ul = s.get("underline", [])
    sp = lambda where: [u["text"] for u in ul if u.get("in") == where]
    deleted = q.get("deleted") or q.get("a", -1) < 0
    opts = "".join(f"<div class='opt{' key' if i == q.get('a') else ''}'>({LET[i]}) {mark(o, sp(f'o{i}'))}</div>" for i, o in enumerate(q.get("o", [])))
    r = REF.get(f"{code}:{q['n']}", {})
    lvl = r.get("level", "new")
    rtag = {"same": ("r1", "Asked before"), "area": ("r2", "Same fact area asked before"), "part": ("r3", "A statement asked before")}.get(lvl)
    prev = ""
    if rtag:
        if lvl == "part" and r.get("st_hits"):
            h = r["st_hits"][0]
            prev = f"<div class='prev'>↺ {r.get('st_hit')} of {r.get('st_total')} statements seen before · e.g. “{E(h['st'][:110])}” — {E(h['src'][:70])}</div>"
        else:
            prev = f"<div class='prev'>↺ {E(r.get('src', '')[:80])}: “{E((r.get('q') or '')[:150])}” → {E(r.get('ans', ''))}</div>"
    tricks = "".join(f"<span class='tag'>{E(t)}</span>" for t in s.get("tricks", [])[:3])
    why = " · ".join(f"<b>{E(u['text'][:40])}</b> — {E(u.get('why', ''))}" for u in ul[:5])
    steps = "".join(f"<li>{E(x)}</li>" for x in s.get("steps", []))
    return f"""<div class='q'><div class='qh'><span class='qn'>Q{q['n']}</span><span class='tag'>{E(q.get('subject', ''))}</span>
{'<span class="tag m">' + E(s.get('method', '')) + '</span>' if s.get('method') else ''}{tricks}
{'<span class="tag ' + rtag[0] + '">' + rtag[1] + '</span>' if rtag else ''}{'<span class="tag del">Deleted / no key</span>' if deleted else ''}</div>
<div class='stem'>{mark(q['s'], sp('s'))}</div><div class='opts'>{opts}</div>
{('<ol class="steps">' + steps + '</ol>') if steps else ''}{('<div class="why">Underlined: ' + why + '</div>') if why else ''}
{('<div class="fact">✓ Remember: ' + E(s['fact']) + '</div>') if s.get('fact') else ''}{prev}</div>"""


def summary_rows(parts):
    rows, tot = [], collections.Counter()
    for code, f, label in parts:
        qs = json.load(open(f))["questions"]
        by = collections.defaultdict(collections.Counter)
        for q in qs:
            r = REF.get(f"{code}:{q['n']}", {"level": "new"})
            c = by[q.get("subject", "")]
            c["n"] += 1
            c[r["level"]] += 1
        for sj, c in by.items():
            refl = c["same"] + c["area"] + c["part"]
            rows.append(f"<tr><td>{E(label)}</td><td>{E(sj)}</td><td>{c['n']}</td><td>{c['same']}</td><td>{c['area']}</td><td>{c['part']}</td>"
                        f"<td><b>{refl} ({100 * refl / max(1, c['n']):.0f}%)</b></td></tr>")
            tot.update(c)
    refl = tot["same"] + tot["area"] + tot["part"]
    rows.append(f"<tr style='font-weight:700;background:#f7f8fb'><td colspan=2>Whole exam</td><td>{tot['n']}</td><td>{tot['same']}</td><td>{tot['area']}</td>"
                f"<td>{tot['part']}</td><td>{refl} ({100 * refl / max(1, tot['n']):.0f}%)</td></tr>")
    return "".join(rows)


def method_rows(parts):
    c = collections.Counter()
    t = collections.Counter()
    for code, f, _ in parts:
        for q in json.load(open(f))["questions"]:
            s = SOL.get((code, q["n"]))
            if s:
                c[s.get("method", "?")] += 1
                for x in s.get("tricks", []):
                    t[x.lower()] += 1
    n = sum(c.values())
    m = "".join(f"<tr><td>{E(k)}</td><td>{v}</td><td>{100 * v / max(1, n):.0f}%</td></tr>" for k, v in c.most_common())
    tr = ", ".join(f"{E(k)} ({v})" for k, v in t.most_common(14))
    return m, tr, n


def build(slug, title, sub, parts):
    m, tr, n = method_rows(parts)
    cover = f"""<section class='cover'><div class='band'><h1>{E(title)}</h1><p>{E(sub)}</p></div>
<h2>How each question is solved</h2><p>Every question below shows the <b>method</b> a prepared candidate would use, the <b>steps</b> to the key,
the words that support the trick <u>underlined</u>, the one fact to remember, and — where the app's PYQ bank has it — the <b>earlier PYQ</b>
the question reflects. Methods and tricks are those of <i>APPSC: Cracked</i> (tested on APPSC's papers and 40,000 PYQs).</p>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:5mm'><div><h3>Methods used ({n} questions)</h3><table><tr><th>Method</th><th>Questions</th><th>Share</th></tr>{m}</table></div>
<div><h3>Tricks used most</h3><p>{tr}</p>
<h3>Legend</h3><p><span class='tag m'>Method</span> the main method · <u>underlined</u> the words that trigger or support it ·
<span class='tag r1'>Asked before</span> the same question was in an earlier exam · <span class='tag r2'>Same fact area asked before</span>
· <span class='tag r3'>A statement asked before</span> one statement of the set appeared in an earlier PYQ · green option = the key.</p></div></div>
<h2>How much of this exam was already in the app's PYQs</h2>
<table><tr><th>Paper</th><th>Subject</th><th>Questions</th><th>Same question</th><th>Same fact area</th><th>A statement</th><th>Reflected</th></tr>{summary_rows(parts)}</table>
<p class='note'>Matched against the app's ~40,000 PYQs from exams held before this one (APPSC, UPSC, other State PSCs, SSC). "Same question" =
near-identical wording and answer; "same fact area" = the same fact or concept asked differently; "a statement" = at least one statement
of a statement set matches an earlier PYQ. Text matching, so an approximate but conservative count.</p></section>"""
    body = []
    for code, f, label in parts:
        body.append(f"<div class='sec'>{E(label)}</div>")
        for q in json.load(open(f))["questions"]:
            if q.get("o"):
                body.append(card(code, q))
    doc = f"<!doctype html><html><head><meta charset='utf-8'><title>{E(title)}</title><style>{CSS}</style></head><body>{cover}{''.join(body)}</body></html>"
    os.makedirs("docs/solved", exist_ok=True)
    hp = f"docs/solved/APPSC-{slug}-Solved.html"
    open(hp, "w").write(doc)
    subprocess.run(["node", "tools/html_to_pdf.js", hp, hp[:-5] + ".pdf", E(title)], check=True)
    print(hp[:-5] + ".pdf", sum(1 for c, _, _ in parts for q in json.load(open(_)) ["questions"]) if False else "")


def reflect_summary():
    """one page: all latest papers, subject-wise reflection"""
    rows = "".join(f"<h2>{E(t)}</h2><table><tr><th>Paper</th><th>Subject</th><th>Questions</th><th>Same question</th><th>Same fact area</th><th>A statement</th><th>Reflected</th></tr>{summary_rows(p)}</table>"
                   for _, t, _, p in PAPERS)
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><title>Reflected from PYQs</title><style>{CSS}</style></head><body>"
           f"<div class='band'><h1>Latest APPSC papers: how much came from earlier PYQs</h1><p>Subject-wise, matched against the app's PYQ bank.</p></div>{rows}"
           f"<p class='note'>Same question = near-identical; same fact area = the same fact asked differently; a statement = one statement of a set matches an earlier PYQ.</p></body></html>")
    open("docs/solved/APPSC-Reflected-from-PYQs.html", "w").write(doc)
    subprocess.run(["node", "tools/html_to_pdf.js", "docs/solved/APPSC-Reflected-from-PYQs.html", "docs/solved/APPSC-Reflected-from-PYQs.pdf", "Reflected from PYQs"], check=True)


if __name__ == "__main__":
    for p in PAPERS:
        build(*p)
    reflect_summary()
    print("solutions present:", len(SOL))
