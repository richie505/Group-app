"""Compile the PYQ-anatomy pilot (job-*.out.jsonl) into an HTML report (then PDF)."""
import json, glob, html, re, sys
from collections import Counter, defaultdict
D = "data/pyqanalysis/pilot"
qs = {}
for f in sorted(glob.glob(f"{D}/job-*.json")):
    if f.endswith(".out.json"): continue
    for q in json.load(open(f)): qs[q["id"]] = q
rows = []
for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
    for l in open(f):
        if l.strip(): rows.append(json.loads(l))
SUBJ = {1: "History", 2: "Polity", 3: "Economy", 4: "Geography", 5: "Sci-Tech-Env", 6: "Current Affairs"}
CHANGE = {"NUM": "Number / quantity changed", "DATE": "Date / year shifted", "PERSON": "Person swapped", "PLACE": "Place swapped",
          "BODY": "Organisation / scheme / body swapped", "SCOPE": "Scope word added/removed (only, all, first)", "NEGATION": "Negation flipped",
          "REVERSAL": "Relation reversed (cause↔effect, more↔less, who↔whom)", "CATEGORY": "Wrong category / class", "PARTIAL": "Half-true (true + false clause)",
          "MISPAIR": "Wrong pairing", "CHRONO": "Wrong order", "OUTDATED": "Outdated fact", "DEFINITION": "Definition altered",
          "ATTRIBUTE": "Property moved to the wrong thing", "FABRICATED": "Made-up item", "OTHER": "Other"}
TECH = {"STMT_ANCHOR": "Anchor on one sure statement", "STMT_COUNT": "Count the true statements", "MATCH_ANCHOR": "Anchor on one sure pair",
        "MATCH_UNIQUE": "An item that fits only one place", "AR_CHECK": "A true? R true? 'because' test", "SEQ_ENDS": "Fix the first / last",
        "NOT_REVERSE": "Reverse for NOT / except", "ODD_ONE_OUT": "Odd one out", "SAME_CLASS": "Options of one kind", "EXTREME": "Reject the extreme option",
        "CONTAINMENT": "Option containing another", "RECALL": "Pure recall (no shortcut)"}
by = lambda f: Counter(f(r) for r in rows)
F_units, T_units, all_units = [], [], []
for r in rows:
    q = qs.get(r["id"], {})
    for u in r.get("units", []):
        u = dict(u, _p=r.get("pattern"), _b=q.get("book"), _id=r["id"])
        # match distractor pairs (wrong pairs offered by other options) counted apart
        u["_distr"] = r.get("pattern") == "match" and u.get("truth") == "F"
        all_units.append(u)
        (F_units if u.get("truth") == "F" else T_units).append(u)
core_F = [u for u in F_units if not u["_distr"]]
chg = Counter(u.get("change") for u in core_F)
chg_by_p = defaultdict(Counter); chg_by_b = defaultdict(Counter)
for u in core_F:
    chg_by_p[u["_p"]][u.get("change")] += 1; chg_by_b[SUBJ.get(u["_b"], "?")][u.get("change")] += 1
# english rules: share of units carrying the rule that are FALSE
er_T, er_F = Counter(), Counter()
for u in all_units:
    if u["_distr"]: continue
    for e in set(u.get("english_rule") or []):
        (er_F if u.get("truth") == "F" else er_T)[e] += 1
base_F = len(core_F) / max(1, len(core_F) + len([u for u in T_units]))
cue = Counter()
for u in core_F:
    for w in u.get("cue_words") or []:
        w = w.lower().strip()
        if len(w) <= 22: cue[w] += 1
tech = Counter(t for r in rows for t in (r.get("solve", {}).get("technique") or []))
tech_by_p = defaultdict(Counter)
for r in rows:
    for t in r.get("solve", {}).get("technique") or []: tech_by_p[r.get("pattern")][t] += 1
diff = Counter(r.get("difficulty") for r in rows)
subj_rules = defaultdict(list)
for u in core_F:
    s = (u.get("subject_rule") or "").strip()
    if s: subj_rules[SUBJ.get(u["_b"], "?")].append(s)
doubts = [(r["id"], r["doubt"]) for r in rows if r.get("doubt")]

def tbl(head, rows_, cls=""):
    h = "<table class='%s'><tr>%s</tr>" % (cls, "".join(f"<th>{html.escape(x)}</th>" for x in head))
    for r_ in rows_: h += "<tr>" + "".join(f"<td>{x}</td>" for x in r_) + "</tr>"
    return h + "</table>"
def bar(n, mx): return f"<div class='bar' style='width:{int(140 * n / max(1, mx))}px'></div> {n}"

out = ["<html><head><meta charset='utf-8'><style>",
       "@page{size:A4;margin:12mm 11mm 14mm 11mm} body{font-family:'Noto Sans',Arial,sans-serif;font-size:9.5pt;color:#111;margin:0} h1{color:#1e3a8a;font-size:20pt} h2{color:#fff;background:#1e3a8a;padding:5px 9px;font-size:13pt;margin-top:8mm;page-break-after:avoid}"
       "h3{color:#9a3412;font-size:11pt;margin:4mm 0 1mm} table{border-collapse:collapse;margin:2mm 0;width:100%} th,td{border:1px solid #cbd5e1;padding:3px 5px;text-align:left;vertical-align:top;font-size:8.8pt} th{background:#e2e8f0}"
       ".bar{display:inline-block;height:9px;background:#3b82f6;vertical-align:middle} .card{border:1px solid #cbd5e1;border-radius:5px;padding:6px 8px;margin:3mm 0;break-inside:avoid} .T{color:#065f46;font-weight:700} .F{color:#b91c1c;font-weight:700}"
       ".k{background:#fef3c7;padding:0 3px;border-radius:3px} .small{color:#64748b;font-size:8pt} p{margin:1.5mm 0}</style></head><body>"]
P = Counter(r.get("pattern") for r in rows)
out.append(f"<h1>How APPSC makes a statement true or false — pilot report</h1><p>{len(rows)} APPSC past-paper questions (2022–26 first; every pattern, every subject) taken apart unit by unit: "
           f"{len(all_units)} units ({len(T_units)} true, {len(F_units)} false; {len(F_units)-len(core_F)} of the false ones are the wrong pairs that match-question distractors offer).</p>")
out.append('''<h2>Rulebook in one page (pilot, 300 APPSC PYQs)</h2><ol>
<li><b>Most false statements are made by swapping one fact, not by changing the language.</b> Top changes: a <b>number</b> changed, a <b>place</b> swapped, the wrong <b>category</b>, a <b>made-up item</b>, a property moved to the wrong thing, the wrong <b>organisation / scheme</b>. So for every statement ask: <i>which number, name, place or body here could have been swapped?</i></li>
<li><b>Words that point to FALSE</b> (share of statements carrying them that were false, base rate 43%): <b>negation</b> 68% · <b>modal</b> (must/shall/may in a legal sense) 62% · <b>quantifier</b> (most/majority/at least) 58% · <b>absolute</b> (only/all/never/always) 57% · <b>causal</b> (because/due to/leads to) 56% · <b>agent</b> (launched/set up/written by X) 54%.</li>
<li><b>Words that point to TRUE</b>: a <b>hedge</b> (some/may/generally/one of the) – 0 of 15 false · two claims joined by <b>and / both</b> – 24% false · a <b>definition</b> ("X is / means") – 40% false.</li>
<li><b>Multi-statement questions:</b> usually exactly <b>one</b> statement is false (33 of 69), sometimes two (17); 13 had none false ("all correct"). The false one is most often <b>statement 2 or 3</b>, rarely the last. Decide the statement you are surest of and strike out the options – this alone reached the key in 56 of 69.</li>
<li><b>Match questions:</b> one sure pair kills 2–3 options (41 of 45 solved by anchoring); look for an item that can fit only one place.</li>
<li><b>Assertion–reason:</b> APPSC's keys spread over all four outcomes – "both true, R explains A" is not the default. Test A, then R, then read "A because R" aloud.</li>
<li><b>NOT / except:</b> turn it into "which three are true" – the three true options share a pattern, the false one breaks it.</li>
<li><b>Sequence:</b> fix the first and last item (16 of 20); the middle follows.</li>
<li><b>One-liners</b> are mostly pure recall (65 of 90): here knowledge decides. The odd-one-out and same-class checks rescue the rest.</li>
</ol>''')
out.append(tbl(["Pattern", "Questions"], [[html.escape(k), v] for k, v in P.most_common()]))
out.append("<h2>1. How a false statement is made (what the examiner changed)</h2>")
mx = max(chg.values())
out.append(tbl(["Change", "False units", ""], [[f"<b>{k}</b> – {CHANGE.get(k,k)}", v, bar(v, mx)] for k, v in chg.most_common()]))
out.append("<h3>By pattern</h3>")
codes = [k for k, _ in chg.most_common(10)]
out.append(tbl(["Pattern"] + codes, [[p] + [chg_by_p[p][c] or "" for c in codes] for p in chg_by_p]))
out.append("<h3>By subject</h3>")
out.append(tbl(["Subject"] + codes, [[s] + [chg_by_b[s][c] or "" for c in codes] for s in chg_by_b]))
out.append("<h2>2. English rules — how often a statement carrying the cue is false</h2>"
           f"<p>Base rate: {base_F*100:.0f}% of units are false. A rule well above the base rate is a warning sign; well below is a sign of a true statement.</p>")
rws = []
for e in sorted(set(er_T) | set(er_F), key=lambda e: -(er_T[e] + er_F[e])):
    n = er_T[e] + er_F[e]
    if n < 3: continue
    pf = er_F[e] / n * 100
    rws.append([f"<b>{e}</b>", n, f"{pf:.0f}% false", "⬆ warning" if pf > base_F * 100 + 12 else ("⬇ leans true" if pf < base_F * 100 - 12 else "")])
out.append(tbl(["English rule", "Units", "False share", "Signal"], rws))
out.append("<h3>Cue words seen in false statements</h3><p>" + " · ".join(f"<span class='k'>{html.escape(w)}</span> {n}" for w, n in cue.most_common(45)) + "</p>")
out.append("<h2>3. How to reach the key (techniques)</h2>")
mx = max(tech.values())
out.append(tbl(["Technique", "Questions", ""], [[f"<b>{k}</b> – {TECH.get(k,k)}", v, bar(v, mx)] for k, v in tech.most_common()]))
out.append("<h3>By pattern</h3>")
tc = [k for k, _ in tech.most_common(9)]
out.append(tbl(["Pattern"] + tc, [[p] + [tech_by_p[p][c] or "" for c in tc] for p in tech_by_p]))
out.append(f"<p>Difficulty: " + ", ".join(f"{k} {v}" for k, v in diff.most_common()) + "</p>")
out.append("<h2>4. Subject habits (examples from the false statements)</h2>")
for s, l in subj_rules.items():
    c = Counter(re.sub(r"\s+", " ", x) for x in l)
    out.append(f"<h3>{s}</h3><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x, _ in c.most_common(10)) + "</ul>")
out.append("<h2>5. Sample question breakdowns</h2>")
seen = Counter()
for r in rows:
    p = r.get("pattern")
    if seen[p] >= 4: continue
    seen[p] += 1
    q = qs.get(r["id"], {})
    h = f"<div class='card'><p class='small'>{html.escape(p)} · {SUBJ.get(q.get('book'))} · {html.escape(q.get('exam',''))}</p><p><b>{html.escape(q.get('q','')).replace(chr(10),'<br>')}</b></p>"
    h += "<p class='small'>" + " · ".join(f"({i+1}) {html.escape(o)}" for i, o in enumerate(q.get("options", []))) + f" — <b>key ({q.get('key',0)+1})</b></p><ul>"
    for u in r.get("units", [])[:8]:
        t = u.get("truth")
        h += (f"<li><span class='{t}'>{t}</span> <b>{html.escape(u.get('label',''))}</b>: {html.escape(u.get('text',''))[:220]}"
              + (f"<br><span class='small'>→ true fact: {html.escape(u.get('true_fact') or '')} · change <b>{u.get('change')}</b>" if t == "F" else "<br><span class='small'>")
              + (f" · cue: {', '.join(html.escape(w) for w in (u.get('cue_words') or []))}" if u.get("cue_words") else "")
              + (f" · rule: {', '.join(u.get('english_rule') or [])}" if u.get("english_rule") else "") + "</span></li>")
    s = r.get("solve", {})
    h += f"</ul><p>🔑 <b>{', '.join(s.get('technique') or [])}</b>: {html.escape(s.get('steps',''))}<br><span class='small'>Minimum knowledge: {html.escape(s.get('min_knowledge',''))} · {r.get('difficulty')}</span></p></div>"
    out.append(h)
out.append("<h2>6. Keys / notes flagged by the analysis</h2><ul>" + "".join(f"<li><b>{i}</b>: {html.escape(d)}</li>" for i, d in doubts) + "</ul>")
out.append("</body></html>")
open(sys.argv[1], "w").write("".join(out))
print(len(rows), "questions,", len(all_units), "units,", len(doubts), "doubts")
