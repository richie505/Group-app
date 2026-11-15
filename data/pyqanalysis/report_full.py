"""Compile the PYQ-anatomy pilot (job-*.out.jsonl) into an HTML report (then PDF)."""
import json, glob, html, re, sys
from collections import Counter, defaultdict
DS = ["data/pyqanalysis/pilot", "data/pyqanalysis/full"]
qs = {}
for f in sorted(sum([glob.glob(f"{D}/job-*.json") for D in DS], [])):
    if f.endswith(".out.json"): continue
    for q in json.load(open(f)): qs[q["id"]] = q
rows = []
seen_ids = set()
for f in sorted(sum([glob.glob(f"{D}/job-*.out.jsonl") for D in DS], [])):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if r["id"] in seen_ids: continue
        seen_ids.add(r["id"]); rows.append(r)
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
        u = dict(u, _p=r.get("pattern"), _b=int(q.get("book") or 0), _id=r["id"])
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
STMT_P = {"statements", "assertion", "sequence"}
er_T, er_F = Counter(), Counter(); oT, oF = Counter(), Counter(); sb = [0, 0]; ob = [0, 0]
for u in all_units:
    if u["_distr"]: continue
    st_ = u["_p"] in STMT_P
    (sb if st_ else ob)[u.get("truth") == "F"] += 1
    for e in set(u.get("english_rule") or []):
        if st_: (er_F if u.get("truth") == "F" else er_T)[e] += 1
        else: (oF if u.get("truth") == "F" else oT)[e] += 1
base_F = sb[1] / max(1, sum(sb)); base_O = ob[1] / max(1, sum(ob))
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
out.append(f"<h1>How APPSC makes a statement true or false — full APPSC report</h1><p>{len(rows)} APPSC past-paper questions (every APPSC paper in the app: Group 1, Group 2, departmental and other recruitments) taken apart unit by unit: "
           f"{len(all_units)} units ({len(T_units)} true, {len(F_units)} false; {len(F_units)-len(core_F)} of the false ones are the wrong pairs that match-question distractors offer).</p>")

def share(e):
    n = er_T[e] + er_F[e]; return (er_F[e] / n * 100 if n else 0), n
def units_of(p): return [r for r in rows if r.get("pattern") == p]
# statements: number false + position
st = units_of("statements"); nf = Counter(); pos = Counter()
for r in st:
    fs = [i for i, u in enumerate(r.get("units", [])) if u.get("truth") == "F"]
    nf[min(len(fs), 3)] += 1
    for i in fs: pos[i + 1] += 1
anch = sum(1 for r in st if "STMT_ANCHOR" in (r.get("solve", {}).get("technique") or []))
mt = units_of("match"); manch = sum(1 for r in mt if {"MATCH_ANCHOR", "MATCH_UNIQUE"} & set(r.get("solve", {}).get("technique") or []))
sq = units_of("sequence"); sends = sum(1 for r in sq if "SEQ_ENDS" in (r.get("solve", {}).get("technique") or []))
ol = units_of("one-liner"); orec = sum(1 for r in ol if (r.get("solve", {}).get("technique") or []) == ["RECALL"])
ar = units_of("assertion"); aro = Counter()
for r in ar:
    us = r.get("units", []); t = [u.get("truth") for u in us[:3]]
    if len(t) >= 2:
        aro[("A✓" if t[0] == "T" else "A✗") + " " + ("R✓" if t[1] == "T" else "R✗") + ((" explains" if len(t) > 2 and t[2] == "T" else " not-explain") if t[0] == "T" and t[1] == "T" else "")] += 1
top = ", ".join(f"<b>{CHANGE.get(k,k).lower()}</b> ({v})" for k, v in chg.most_common(6))
warn = [e for e in sorted(set(er_T) | set(er_F), key=lambda e: -share(e)[0]) if share(e)[1] >= 30 and share(e)[0] > base_F * 100 + 6]
lean = [e for e in sorted(set(er_T) | set(er_F), key=lambda e: share(e)[0]) if share(e)[1] >= 30 and share(e)[0] < base_F * 100 - 6]
out.append(f"<h2>Rulebook in one page ({len(rows):,} APPSC PYQs)</h2><ol>"
 f"<li><b>Most false statements are made by swapping one fact, not by changing the language.</b> Top changes: {top}. For every statement ask: <i>which number, name, place, date or body here could have been swapped?</i></li>"
 f"<li><b>Words that point to FALSE</b> (share of statements carrying them that were false; base rate {base_F*100:.0f}%): " + " · ".join(f"<b>{e.lower()}</b> {share(e)[0]:.0f}%" for e in warn) + "</li>"
 f"<li><b>Words that lean TRUE</b>: " + " · ".join(f"<b>{e.lower()}</b> {share(e)[0]:.0f}% false" for e in lean) + "</li>"
 f"<li><b>Multi-statement questions ({len(st)}):</b> none false {nf[0]}, one false {nf[1]}, two false {nf[2]}, three+ {nf[3]}. False statement position: " + ", ".join(f"#{k} {v}" for k, v in sorted(pos.items())[:5]) + f". Anchoring on the surest statement reached the key in {anch} of {len(st)}.</li>"
 f"<li><b>Match ({len(mt)}):</b> one sure pair / a unique item solved {manch} of {len(mt)}.</li>"
 f"<li><b>Assertion–reason ({len(ar)}):</b> outcomes " + ", ".join(f"{k} {v}" for k, v in aro.most_common()) + " – never assume 'both true, R explains A'.</li>"
 f"<li><b>NOT / except:</b> turn it into 'which three are true' – the true options share a pattern, the false one breaks it.</li>"
 f"<li><b>Sequence ({len(sq)}):</b> fixing the first/last item solved {sends}.</li>"
 f"<li><b>One-liners ({len(ol)}):</b> {orec} ({orec*100//max(1,len(ol))}%) are pure recall – knowledge decides; odd-one-out and same-class checks rescue the rest.</li></ol>")

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
           f"<p>Measured on the numbered statements, assertion/reason parts, and sequence steps ({sum(sb):,} units), where a statement can freely be true or false. Base rate: {base_F*100:.0f}% false. A rule well above the base rate is a warning sign; well below leans true. (One-liner options are shown separately below, because 3 of 4 options are false by design.)</p>")
rws = []
for e in sorted(set(er_T) | set(er_F), key=lambda e: -(er_T[e] + er_F[e])):
    n = er_T[e] + er_F[e]
    if n < 3: continue
    pf = er_F[e] / n * 100
    rws.append([f"<b>{e}</b>", n, f"{pf:.0f}% false", "⬆ warning" if pf > base_F * 100 + 12 else ("⬇ leans true" if pf < base_F * 100 - 12 else "")])
out.append(tbl(["English rule", "Units", "False share", "Signal"], rws))
rw2 = []
for e in sorted(set(oT) | set(oF), key=lambda e: -(oT[e] + oF[e])):
    n = oT[e] + oF[e]
    if n < 10: continue
    pf = oF[e] / n * 100
    rw2.append([f"<b>{e}</b>", n, f"{pf:.0f}% false", "⬆ distractor sign" if pf > base_O * 100 + 6 else ("⬇ often the key" if pf < base_O * 100 - 6 else "")])
out.append(f"<h3>One-liner / NOT options (base rate {base_O*100:.0f}% false)</h3>" + tbl(["English rule", "Options", "False share", "Signal"], rw2))
out.append("<h3>Cue words seen in false statements</h3><p>" + " · ".join(f"<span class='k'>{html.escape(w)}</span> {n}" for w, n in cue.most_common(45)) + "</p>")
out.append("<h2>3. How to reach the key (techniques)</h2>")
mx = max(tech.values())
out.append(tbl(["Technique", "Questions", ""], [[f"<b>{k}</b> – {TECH.get(k,k)}", v, bar(v, mx)] for k, v in tech.most_common()]))
out.append("<h3>By pattern</h3>")
tc = [k for k, _ in tech.most_common(9)]
out.append(tbl(["Pattern"] + tc, [[p] + [tech_by_p[p][c] or "" for c in tc] for p in tech_by_p]))
out.append(f"<p>Difficulty: " + ", ".join(f"{k} {v}" for k, v in diff.most_common()) + "</p>")
YR = {}
for r in rows:
    m = re.search(r"(19|20)\d\d", qs.get(r["id"], {}).get("exam", "")); YR[r["id"]] = m.group(0) if m else None
dec = lambda y: (y[:3] + "0s") if y else "year not stated"
chg_by_y = defaultdict(Counter); q_by_y = Counter()
for r in rows: q_by_y[dec(YR[r["id"]])] += 1
for u in core_F: chg_by_y[dec(YR[u["_id"]])][u.get("change")] += 1
out.append("<h3>By decade of the paper</h3>")
out.append(tbl(["Decade", "Qs"] + codes, [[d, q_by_y[d]] + [chg_by_y[d][c] or "" for c in codes] for d in sorted(q_by_y)]))
pat_by_b = defaultdict(Counter)
for r in rows: pat_by_b[SUBJ.get(int(qs.get(r["id"], {}).get("book") or 0), "?")][r.get("pattern")] += 1
pl = [k for k, _ in P.most_common()]
out.append("<h3>Patterns by subject</h3>" + tbl(["Subject"] + pl, [[sb] + [pat_by_b[sb][p] or "" for p in pl] for sb in pat_by_b]))
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
    h = f"<div class='card'><p class='small'>{html.escape(p)} · {SUBJ.get(int(q.get('book') or 0))} · {html.escape(q.get('exam',''))}</p><p><b>{html.escape(q.get('q','')).replace(chr(10),'<br>')}</b></p>"
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
out.append(f"<h2>6. Keys / stems flagged by the analysis ({len(doubts):,})</h2><p class='small'>Each line: question · key in the app → why it was flagged. These are flags for a human check, not corrections.</p>")
grp = defaultdict(list)
for i, d in doubts: grp[SUBJ.get(int(qs.get(i, {}).get("book") or 0), "?")].append((i, d))
for sb in SUBJ.values():
    if not grp.get(sb): continue
    out.append(f"<h3>{sb} ({len(grp[sb])})</h3><ol class='small'>")
    for i, d in grp[sb]:
        q = qs.get(i, {}); qt = re.sub(r"\s+", " ", q.get("q", ""))[:150]
        out.append(f"<li><b>{html.escape(qt)}</b> · key: {html.escape(str(q.get('key_text',''))[:60])} → {html.escape(d)}</li>")
    out.append("</ol>")
out.append("</body></html>")
open(sys.argv[1], "w").write("".join(out))
print(len(rows), "questions,", len(all_units), "units,", len(doubts), "doubts")
