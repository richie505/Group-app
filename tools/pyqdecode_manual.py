"""Stages 7-8: build the two PYQ Decoding Manuals (HTML -> PDF) from data/pyqdecode/pyq.db.
Every number is computed here from the database; every judgement (truth, mechanism, decisive phrase, rule) is the
Stage-4 analysis stored in the database. Official papers drive all statistics; the app-bank tiers are shown as
related evidence only.
    python3 tools/pyqdecode_manual.py [g1|g2 ...] [--html-only]
Output: manuals/APPSC_Group_1_Complete_PYQ_Decoding_Manual.pdf, manuals/APPSC_Group_2_Complete_PYQ_Decoding_Manual.pdf
(HTML kept in data/pyqdecode/manual_<g>.html)."""
import collections, html, json, re, sqlite3, sys, datetime

con = sqlite3.connect("data/pyqdecode/pyq.db")
con.row_factory = sqlite3.Row
E = lambda t: html.escape(str(t if t is not None else ""))
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
FMT = {"pair-matching": "matching", "odd-pair": "matching", "ordering": "chronology", "chronology/sequence": "chronology",
       "ranking/order one-liner": "chronology", "two-statement": "statement-based", "all-of-the-above": "multiple-correct"}


def fmt(f):
    f = re.sub(r"\s*\(.*\)", "", f or "?").strip()
    return FMT.get(f, f)


def frac(n, d):
    return f"{n}/{d} = {100 * n / d:.1f}%" if d else f"{n}/0 = –"


def anchor(code):
    return "L-" + re.sub(r"[^A-Za-z0-9]+", "-", code)


# Phase 11 families of the canonical mechanisms (defined here, printed in the manual)
FAMILY = {"Authority / institution swaps": {"authority swap", "institution substitution", "wrong institution", "function/power substitution"},
          "Numerical changes": {"numerical alteration", "fraction/majority alteration"},
          "Chronology changes": {"chronological displacement", "wrong period"},
          "Geographical changes": {"location substitution"},
          "Exception / scope traps": {"exception removal", "exception insertion", "scope expansion", "scope restriction", "quantifier distortion"},
          "Multi-clause traps": {"true core + false extra", "multi-fact merge"}}
LAYER1 = {"Absolute quantifiers": r"\b(only|all|every|none|always|never|exclusively|sole|solely|entire|any)\b",
          "Negative statements": r"\b(not|never|no|neither|nor|cannot|none)\b|n't\b",
          "Superlatives": r"\b(first|last|largest|highest|oldest|biggest|smallest|longest|tallest|lowest|earliest|most|least|best|greatest)\b",
          "Comparisons": r"\b(more|less|higher|lower|greater|fewer|larger|smaller|older|earlier|later) than\b|\bthan\b",
          "Dates": r"\b(1[0-9]{3}|20[0-9]{2})\b|\b(century|BCE|BC|CE|AD|A\.D\.)\b",
          "Numbers": r"\d",
          "Authorities": r"\b(President|Governor|Parliament|Lok Sabha|Rajya Sabha|Speaker|Prime Minister|Chief Minister|Supreme Court|High Court|Election Commission|Reserve Bank|RBI|Cabinet|Council of Ministers|Legislature|Comptroller|CAG|Finance Commission|NITI|Planning Commission|Attorney|Advocate|Union Public Service|UPSC|Chief Justice)\b",
          "Locations": r"\b(located|situated|district|river|capital|headquarter\w*|state of|coast|basin|hills?|plateau|region|city|town|village)\b",
          "Multi-clause statements": r";|\b(whereas|while|which|who|whose|but|however|although)\b|, and\b"}
L1RX = {k: re.compile(v, re.I) for k, v in LAYER1.items()}
WORDS = ["only", "all", "every", "none", "always", "never", "however", "but", "not", "did not", "whereas", "while",
         "unlike", "more than", "less than", "higher than", "lower than", "first", "largest", "highest", "oldest", "main",
         "primary", "chief", "member of", "elected", "appointed", "recommended", "approved", "reviewed", "established",
         "introduced", "implemented", "applicable", "exempted", "national", "state", "regional", "central", "local",
         "both", "neither", "exclusively", "sole", "must", "may", "mandatory", "constitutional", "statutory"]
WRE = {w: re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in WORDS}


def label(n):
    return "High historical recurrence" if n >= 5 else "Moderate historical recurrence" if n >= 3 else \
        "Low historical recurrence" if n >= 1 else "Insufficient evidence"


def confidence(q, years):
    return "STRONG EVIDENCE" if q >= 6 and years >= 3 else "MODERATE EVIDENCE" if q >= 3 else "WEAK EVIDENCE" if q >= 1 else "NO EVIDENCE"


# ---------------- syllabus trees ----------------
def tree_g2():
    """[(part_code, part_title, [(sec_code, sec_title, [(leaf, text, depth)])])]"""
    parts = []
    for line in open("data/g2syl/leaves.md"):
        if line.startswith("## "):
            c, t = line[3:].strip().split(" ", 1); parts.append((c, t, []))
        elif line.startswith("### "):
            c, t = line[4:].strip().split(" ", 1); parts[-1][2].append((c, t, []))
        else:
            m = re.match(r"(\s*)-?\s*([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):\s*(.+)", line)
            if m and parts and parts[-1][2]:
                parts[-1][2][-1][2].append((m.group(2), m.group(3).strip(), 1 if "/" in m.group(2) else 0))
    return parts


def tree_g1():
    d = json.load(open("data/g1syl/leaves.json"))
    parts, idx = [], {}
    for it in d["items"]:
        if it["part"] not in idx:
            idx[it["part"]] = len(parts); parts.append((it["part"].split("·")[-1].strip().split(".")[0], it["part"], []))
        parts[idx[it["part"]]][2].append((it["code"], it["text"], []))
    sec = {s[0]: s for p in parts for s in p[2]}
    for lf in d["leaves"]:
        sec[lf["item"]][2].append((lf["leaf"], lf["text"], 1))
    return parts


# ---------------- data ----------------
def load(exam, col):
    Q = [dict(r) for r in con.execute("""SELECT q.*, p.year, p.stage, p.title AS ptitle, p.key_status AS pks, p.key_doc_kind FROM question q
        JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.analysed IS NOT NULL ORDER BY p.year, q.paper_id, q.qno""", (exam,))]
    S = collections.defaultdict(list)
    for r in con.execute("""SELECT s.* FROM statement s JOIN question q ON q.id=s.question_id JOIN paper p ON p.id=q.paper_id
        WHERE p.exam=? AND q.analysed IS NOT NULL ORDER BY s.question_id, CAST(substr(s.id, instr(s.id, ':')+1) AS INTEGER)""", (exam,)):
        S[r["question_id"]].append(dict(r))
    # duplicate copies of the same question (same stem + options) count once
    seen, dup = {}, {}
    for q in Q:
        k = norm(q["text_original"]) + "|" + norm(q["options_json"] or "")
        if k in seen:
            dup[q["id"]] = seen[k]
        else:
            seen[k] = q["id"]
    # related tiers (app bank): each question under its first mapped leaf
    rel = collections.defaultdict(lambda: {"secondary": [], "tertiary": []})
    for r in con.execute(f"""SELECT q.id, q.text_original, q.key_text, q.{col} AS lv, p.exam, p.title FROM question q JOIN paper p ON p.id=q.paper_id
        WHERE q.paper_id LIKE 'app:%' ORDER BY q.id"""):
        lv = json.loads(r["lv"] or "[]")
        if not lv:
            continue
        if r["exam"] == exam:
            rel[lv[0]]["secondary"].append(dict(r))
        elif r["exam"] == "Other APPSC exam":
            rel[lv[0]]["tertiary"].append(dict(r))
    return Q, S, dup, rel


# ---------------- rendering helpers ----------------
def table(head, rows, cls=""):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def tag(kind, text):
    return f'<span class="tag {kind}">{E(text)}</span>'


def strip_ai(t):
    return re.sub(r"^\s*AI-GENERATED PRACTICE \(not an APPSC PYQ\):\s*", "", t or "")


def qblock(q, sts, dup):
    opts = json.loads(q["options_json"]) if q["options_json"] else None
    rec = json.loads(q["reconstruction"]) if q["reconstruction"] else {}
    o = ""
    if opts:
        o = "<ol class='opts'>" + "".join(f"<li{' class=key' if i == q['key_index'] else ''}>{E(x)}</li>" for i, x in enumerate(opts)) + "</ol>"
    ks = q["key_status"] or q["pks"]
    keyline = ("<b>Deleted by APPSC</b> – no answer counted. " if q["deleted"] else
               f"<b>{E(q['key_text'])}</b>" + (f" (option {q['key_index'] + 1})" if opts and q["key_index"] is not None and q["key_index"] >= 0 else ""))
    rows = []
    for s in sts:
        ph = json.loads(s["phrases_json"] or "[]")
        phs = "; ".join(f"<i>{E(p.get('phrase'))}</i>{' ✗' if p.get('correct') is False else ''}"
                        + (f" → {E(p.get('would_be_correct_if'))}" if p.get("correct") is False and p.get("would_be_correct_if") else "")
                        for p in ph if p.get("role") in ("trap", "qualifier") or p.get("correct") is False)
        tv = {"T": "<span class='T'>TRUE</span>", "F": "<span class='F'>FALSE</span>"}.get(s["truth"], "<span class='U'>UNSETTLED</span>")
        an = []
        if s["decisive_phrase"]:
            an.append(f"<span class='dec'>Decisive:</span> {E(s['decisive_phrase'])}")
        if s["truth"] == "F":
            an.append(f"<span class='mech'>{E(s['mechanism'] or 'unclassified')}</span>")
            if s["true_fact"]:
                an.append(f"<span class='fact'>Correct:</span> {E(s['true_fact'])}")
        if phs:
            an.append(f"<span class='ph'>Words:</span> {phs}")
        if s["fact_source"]:
            an.append(f"<span class='src'>Source: {E(s['fact_source'])}</span>")
        rows.append([E(s["label"]), E(s["text"]), f"{tv}<br><small>{E(s['truth_basis'])}</small>", "<br>".join(an)])
    st = table(["Unit", "Statement (as tested)", "Verdict / basis", "Analysis"], rows, "st") if rows else ""
    r = ""
    if rec:
        r = ("<div class='rec'>"
             + (f"<div><span class='lab fact'>Verified fact</span> {E(rec.get('correct_statement'))}</div>" if rec.get("correct_statement") else "")
             + (f"<div><span class='lab mech'>APPSC transformation</span> {E(rec.get('transformation'))}</div>" if rec.get("transformation") else "")
             + (f"<div><span class='lab dec'>Decisive</span> {E(rec.get('decisive'))}</div>" if rec.get("decisive") else "")
             + (f"<div><span class='lab why'>Why</span> {E(rec.get('why'))}</div>" if rec.get("why") else "")
             + (f"<div><span class='lab rule'>Micro-topic rule</span> {E(rec.get('micro_topic_rule'))}</div>" if rec.get("micro_topic_rule") else "")
             + "</div>")
    note = f"<div class='lim'><b>Key note:</b> {E(q['key_note'])}</div>" if q["key_note"] else ""
    pr = f"<div class='ai'>{E(strip_ai(q['practice']))}</div>" if q["practice"] else ""
    dp = f" <span class='tag dup'>duplicate of {E(dup[q['id']])} – not counted again</span>" if q["id"] in dup else ""
    return (f"<div class='q' id='Q-{re.sub(r'[^A-Za-z0-9]+', '-', q['id'])}'>"
            f"<div class='qh'>{tag('off', 'OFFICIAL PYQ')} <b>{E(q['year'])} · {E(q['stage'])} · {E(q['ptitle'])} · Q{E(q['qno'])}</b> · "
            f"<span class='fmt'>{E(fmt(q['format']))}</span>{dp}</div>"
            f"<div class='stem'>{E(q['text_original'])}</div>{o}"
            f"<div class='ans'>{tag('ans', 'OFFICIAL ANSWER')} {keyline} <small>· key: {E(ks)} · check: {E((q['key_check'] or '')[:160])}</small></div>"
            f"<div class='core'><span class='lab fact'>Core fact</span> {E(q['core_fact'])}"
            + (f" <small>· micro-topic: {E(q['micro_topic'])} · keyword: {E(q['blueprint_keyword'])}</small>" if q["micro_topic"] else "")
            + (f"<br><small>Mapping note: {E(q['leaf_note'])}</small>" if q["leaf_note"] else "")
            + f"</div>{st}{r}{note}{pr}</div>")


def leaf_chapter(code, text, pos, qs, S, dup, rel, depth):
    ind = [q for q in qs if q["id"] not in dup]
    sts = [s for q in qs for s in S[q["id"]]]
    sts_i = [s for q in ind for s in S[q["id"]]]
    T = [s for s in sts_i if s["truth"] == "T"]; F = [s for s in sts_i if s["truth"] == "F"]; TF = len(T) + len(F)
    years = sorted({q["year"] for q in ind})
    h = f"<section class='leaf' id='{anchor(code)}'><h3>{E(code)} {E(text)}</h3>"
    h += f"<div class='pos'><b>Syllabus position:</b> {E(pos)}</div>"
    # 3 core facts
    cf = list(dict.fromkeys(q["core_fact"] for q in ind if q["core_fact"]))
    h += "<h4>3 · Core facts tested</h4><ul class='cf'>" + "".join(f"<li>{E(x)}</li>" for x in cf) + "</ul>"
    # 11 frequency (shown early as the summary box)
    fm = collections.Counter(fmt(q["format"]) for q in ind)
    mech = collections.Counter(s["mechanism"] or "unclassified" for s in F)
    fam = [(k, sum(n for m, n in mech.items() if m in v)) for k, v in FAMILY.items()]
    small = " <span class='tag small'>SMALL SAMPLE</span>" if len(ind) < 3 else ""
    h += ("<h4>11 · Frequency and recurrence (official papers)</h4><div class='freq'>"
          f"Questions: <b>{len(ind)}</b>{small} · years: {E(', '.join(map(str, years)))} ({len(years)} distinct) · "
          f"statements: {len(sts_i)} (true {frac(len(T), TF)}; false {frac(len(F), TF)}; denominator = settled T+F statements)<br>"
          f"Formats (unit = question): " + "; ".join(f"{E(k)} {frac(n, len(ind))}" for k, n in fm.most_common()) + "<br>"
          f"False-statement families (unit = false statement, denominator {len(F)}): "
          + "; ".join(f"{E(k)} {n}" for k, n in fam if n) + (" – none" if not any(n for _, n in fam) else "")
          + f"<br><b>{label(len(years))}</b> · {confidence(len(ind), len(years))} <small>(historical observation, not a prediction)</small></div>")
    # 4 + 5 PYQ collection with statement deconstruction and reconstruction (template phase 10)
    h += "<h4>4–5 · Complete PYQ collection with statement-by-statement deconstruction</h4>"
    h += "".join(qblock(q, S[q["id"]], dup) for q in qs)
    # 6 words and phrases
    wr = []
    for w, rx in WRE.items():
        hit = [s for s in sts_i if s["truth"] in ("T", "F") and rx.search(s["text"] or "")]
        if hit:
            t = sum(1 for s in hit if s["truth"] == "T")
            ex = "; ".join(f"“{E(s['text'][:110])}” <b class='{s['truth']}'>{s['truth']}</b>" for s in hit[:2])
            wr.append([f"<b>{E(w)}</b>", len(hit), t, len(hit) - t, frac(t, len(hit)).split('= ')[1], frac(len(hit) - t, len(hit)).split('= ')[1], ex])
    traps = []
    for s in sts_i:
        for p in json.loads(s["phrases_json"] or "[]"):
            if p.get("role") == "trap":
                traps.append([E(p.get("phrase")), E(p.get("meaning_here")), E(p.get("would_be_correct_if")), E(p.get("note"))])
    h += "<h4>6 · Word and phrase analysis</h4>"
    if wr:
        h += ("<p class='u'>Unit = statement-level occurrence (a word counted once per statement); T/F percentages use the settled "
              "statements containing the word in THIS micro-topic as denominator.</p>"
              + table(["Word", "Statements", "True", "False", "True %", "False %", "Context (actual PYQ statements)"], wr, "w"))
    else:
        h += "<p class='u'>None of the tracked qualifier words occurs in this micro-topic's statements.</p>"
    if traps:
        h += "<p class='u'>Fact-bearing words whose change made a statement false here:</p>" + table(
            ["Phrase as tested", "Meaning here", "Would be correct if", "Note"], traps, "tr")
    # 7 transformation patterns
    if F:
        ex = collections.defaultdict(list)
        for s in F:
            ex[s["mechanism"] or "unclassified"].append(s)
        rows = [[f"<b>{E(m)}</b>", frac(n, len(F)), "<br>".join(f"“{E(s['text'][:120])}” → {E((s['true_fact'] or '')[:120])}" for s in ex[m][:2])]
                for m, n in mech.most_common()]
        h += "<h4>7 · APPSC transformation patterns</h4><p class='u'>Unit = false statement; denominator = all false statements of this micro-topic.</p>" + table(
            ["Mechanism", "Share", "Actual examples (exam wording → fact)"], rows, "m")
    # 8 true-statement construction
    if T:
        h += (f"<h4>8 · True-statement construction</h4><p class='u'>{len(T)} true statements. How APPSC phrases a true one here:</p><ul>"
              + "".join(f"<li>“{E(s['text'])}” <small>(decisive: {E(s['decisive_phrase'])})</small></li>" for s in T[:6]) + "</ul>")
    # 9 false-statement construction
    if F:
        h += (f"<h4>9 · False-statement construction</h4><p class='u'>{len(F)} false statements; the fact each one breaks:</p><ul>"
              + "".join(f"<li>{tag('tf', s['mechanism'] or 'unclassified')} “{E(s['text'])}” → <span class='fact'>{E(s['true_fact'])}</span></li>" for s in F[:8])
              + ("</ul><p class='u'>All of them are listed with their questions in section 4–5.</p>" if len(F) > 8 else "</ul>"))
    # 10 formats
    h += "<h4>10 · Question-format patterns</h4><p>" + "; ".join(f"{E(k)}: {n} question(s)" for k, n in fm.most_common()) + "</p>"
    # 12 confusions
    conf = []
    for s in F:
        for p in json.loads(s["phrases_json"] or "[]"):
            if p.get("correct") is False and p.get("would_be_correct_if"):
                conf.append(f"<li><i>{E(p['phrase'])}</i> ≠ {E(p['would_be_correct_if'])}</li>")
    if conf:
        h += "<h4>12 · Common factual confusions</h4><ul class='cfu'>" + "".join(dict.fromkeys(conf)) + "</ul>"
    # 13 rules
    rules = list(dict.fromkeys(json.loads(q["reconstruction"]).get("micro_topic_rule") for q in ind if q["reconstruction"]))
    rules = [r for r in rules if r]
    if rules:
        h += "<h4>13 · Exam-oriented decoding rules</h4><ul class='rule'>" + "".join(f"<li>{E(r)}</li>" for r in rules) + "</ul>"
    # 14 practice
    pr = [q["practice"] for q in ind if q["practice"]]
    if pr:
        h += ("<h4>14 · AI-generated practice (not APPSC PYQs)</h4><div class='ai'>"
              + "<br>".join(E(re.sub(r"^AI-GENERATED PRACTICE \(not an APPSC PYQ\):\s*", "", p)) for p in pr) + "</div>")
    # 15 evidence
    nk = sum(1 for q in ind if (q["key_check"] or "").startswith(("NO_OFFICIAL", "NOT_IN_DOC", "pending")))
    lim = []
    if len(ind) < 3:
        lim.append("fewer than three official questions – patterns here are observations, not rules")
    if nk:
        lim.append(f"{nk} of {len(ind)} answers rest on a key with no APPSC document available")
    un = [s for s in sts_i if s["truth"] == "U"]
    if un:
        lim.append(f"{len(un)} statement(s) unsettled")
    h += (f"<h4>15 · Evidence and confidence</h4><div class='freq'><b>{confidence(len(ind), len(years))}</b> – {len(ind)} official question(s) in "
          f"{len(years)} year(s).</div>" + (f"<div class='lim'>Limitations: {E('; '.join(lim))}.</div>" if lim else ""))
    h += related(rel.get(code))
    return h + "</section>"


def related(r, cap=12):
    if not r or not (r["secondary"] or r["tertiary"]):
        return ""
    h = "<div class='relb'><b>Related evidence (not official keys; not counted in any statistic)</b>"
    for k, lab in (("secondary", "Same exam, from the app's PYQ bank"), ("tertiary", "Other APPSC exams")):
        xs = r[k]
        if xs:
            h += f"<div><i>{lab}: {len(xs)} question(s)</i><ul>" + "".join(
                f"<li>{E(x['text_original'][:220])} – <b>{E(x['key_text'])}</b> <small>({E(x['title'])})</small></li>" for x in xs[:cap if k == 'tertiary' else 10 ** 6]) \
                 + (f"<li><small>… {len(xs) - cap} more in the source index</small></li>" if k == "tertiary" and len(xs) > cap else "") + "</ul></div>"
    return h + "</div>"


CSS = """
@page { size: A4; margin: 16mm 13mm 16mm 13mm; }
:root { --ink:#1b1f24; --muted:#5b6470; --line:#d6dbe1; --off:#0b5394; --ans:#38761d; --fact:#1e7b4f; --mech:#a61c00; --dec:#7f3fbf;
        --rule:#b45f06; --ai:#7a5c00; --lim:#8a1538; }
body { font-family: "DejaVu Sans", "Noto Sans Telugu", sans-serif; color: var(--ink); background:#fff; font-size: 9.4pt; line-height: 1.38; }
h1 { font-size: 22pt; margin: 0 0 6pt; } h2 { font-size: 15pt; border-bottom: 2px solid var(--off); padding-bottom: 3pt; margin-top: 0; break-before: page; color: var(--off);}
h2.sub { font-size: 13pt; } h3 { font-size: 11.5pt; background:#eef3f9; padding: 4pt 6pt; border-left: 4px solid var(--off); margin: 14pt 0 4pt; break-after: avoid; }
h4 { font-size: 9.8pt; margin: 9pt 0 3pt; color:#334; break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 8pt; font-size: 8.4pt; } th, td { border: 1px solid var(--line); padding: 2.5pt 4pt; vertical-align: top; text-align: left; overflow-wrap: anywhere; }
th { background: #f2f4f7; overflow-wrap: normal; word-break: keep-all; } tr { break-inside: avoid; }
table.st td:nth-child(1) { width: 7%; } table.st td:nth-child(2) { width: 38%; } table.st td:nth-child(3) { width: 10%; }
.q { border: 1px solid var(--line); border-radius: 4pt; padding: 5pt 7pt; margin: 6pt 0 9pt; }
.qh { font-size: 8.6pt; color: var(--muted); margin-bottom: 3pt; } .stem { white-space: pre-wrap; font-weight: 600; margin: 2pt 0; }
ol.opts { margin: 2pt 0 3pt 16pt; padding: 0; } ol.opts li.key { font-weight: 700; color: var(--ans); }
.ans { margin: 3pt 0; } .core { margin: 3pt 0; }
.tag { display: inline-block; font-size: 7pt; font-weight: 700; letter-spacing: .3pt; padding: 0.5pt 4pt; border-radius: 3pt; color: #fff; }
.tag.off { background: var(--off);} .tag.ans { background: var(--ans);} .tag.tf { background: var(--mech);} .tag.small { background: var(--lim);} .tag.dup { background:#777;}
.lab { font-size: 7.4pt; font-weight: 700; text-transform: uppercase; margin-right: 3pt; }
.fact { color: var(--fact); } .mech { color: var(--mech); font-weight: 700; } .dec { color: var(--dec); font-weight: 700; } .rule { color: var(--rule); } .why { color:#444; }
.ph { color: var(--muted); font-weight: 700; } .src { color: var(--muted); font-size: 7.6pt; }
.T { color: var(--ans); font-weight: 700; } .F { color: var(--mech); font-weight: 700; } .U { color: var(--lim); font-weight: 700; }
.rec { background: #fbfaf4; border-left: 3px solid var(--rule); padding: 3pt 6pt; margin: 3pt 0; }
.ai { background: #fff6d6; border: 1px dashed var(--ai); padding: 3pt 6pt; margin: 3pt 0; }
.ai::before { content: "AI-GENERATED PRACTICE – NOT AN APPSC PYQ"; display: block; font-size: 7pt; font-weight: 700; color: var(--ai); }
.lim { background: #fbeef1; border-left: 3px solid var(--lim); padding: 2pt 6pt; margin: 3pt 0; font-size: 8.4pt; }
.freq { background: #eef6f0; border-left: 3px solid var(--fact); padding: 3pt 6pt; margin: 3pt 0; }
.pos { color: var(--muted); font-size: 8.4pt; } .u { color: var(--muted); font-size: 8.2pt; margin: 2pt 0; }
.relb { border-top: 1px dotted var(--line); margin-top: 6pt; padding-top: 3pt; font-size: 8.2pt; color: #333; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; } .cover p { font-size: 11pt; color: var(--muted); }
.toc a { color: var(--ink); text-decoration: none; } .toc li { margin: 1pt 0; } .toc ul { margin: 0 0 0 12pt; padding: 0; list-style: none; }
.legend span { margin-right: 8pt; } .nopyq { columns: 2; font-size: 8.4pt; }
a { color: var(--off); }
"""


def build(g):
    exam = "Group 1" if g == "g1" else "Group 2"
    col = "g1_leaves" if g == "g1" else "g2_leaves"
    parts = tree_g1() if g == "g1" else tree_g2()
    Q, S, dup, rel = load(exam, col)
    stats = json.load(open(f"data/pyqdecode/stats_{g}.json"))
    ver = json.load(open(f"data/pyqdecode/verification_{g}.json"))
    other = json.load(open(f"data/pyqdecode/stats_{'g2' if g == 'g1' else 'g1'}.json"))
    byleaf = collections.defaultdict(list)
    for q in Q:
        byleaf[q["leaf_code"]].append(q)
    ind = [q for q in Q if q["id"] not in dup]
    allS = [s for q in ind for s in S[q["id"]]]
    F = [s for s in allS if s["truth"] == "F"]; T = [s for s in allS if s["truth"] == "T"]; TF = len(T) + len(F)
    out = []
    # 1 cover
    out.append(f"<div class='cover'><h1>APPSC {exam} – Complete PYQ Decoding Manual</h1>"
               f"<p>How APPSC turns a syllabus fact into a true or a false exam statement – reverse-engineered, statement by statement, "
               f"from every available official {exam} paper ({len(Q)} questions, {len(allS)} statements).</p>"
               f"<p><b>Central rule:</b> a word is not a trap by itself. The factual relationship inside the exact micro-topic decides "
               f"whether a statement is true or false.</p><p>Generated {datetime.date.today():%d %B %Y} from the project database "
               f"(<code>data/pyqdecode/pyq.db</code>). Historical frequencies are observations, never predictions.</p></div>")
    # TOC
    chap = ["How to use the manual", "Dataset and source audit", "Official syllabus and blueprint mapping", "Examination structure",
            "Overall question-format analysis", "Universal language patterns", "Subject-wise micro-topic decoding",
            "Matching and chronology", "Assertion-reason", "Micro-topic frequency tables", "High historical recurrence topics",
            f"{exam}-specific patterns", "Revision framework", "Coverage, evidence and source index"]
    toc = "<h2 id='toc'>Contents</h2><ol class='toc'>"
    for i, c in enumerate(chap, 2):
        toc += f"<li><a href='#C{i}'>{E(c)}</a>"
        if i == 8:
            toc += "<ul>" + "".join(f"<li><a href='#P-{anchor(p[0])}'>{E(p[1])}</a><ul>" + "".join(
                f"<li><a href='#{anchor(s[0])}-sec'>{E(s[0])} {E(s[1][:90])}</a></li>" for s in p[2]) + "</ul></li>" for p in parts) + "</ul>"
        toc += "</li>"
    out.append(toc + "</ol>")
    # 2 how to use
    out.append(f"""<h2 id='C2'>How to use the manual</h2>
<p>Chapter 8 is the core: one block per official syllabus micro-topic, in syllabus order. Each block follows the same template –
core facts, frequency, every official PYQ with each statement deconstructed, word and phrase behaviour, transformation patterns,
true- and false-statement construction, formats, factual confusions, decoding rules, labelled practice, and evidence.</p>
<p class='legend'>Visual key: {tag('off', 'OFFICIAL PYQ')} the question as printed · {tag('ans', 'OFFICIAL ANSWER')} the published key (status shown) ·
<span class='lab fact'>Verified fact</span> · <span class='lab mech'>Transformation</span> · <span class='lab dec'>Decisive</span> ·
<span class='lab rule'>Micro-topic rule</span> · <span class='freq'>frequency data</span> · <span class='ai'>AI practice</span> ·
<span class='lim'>evidence limitation</span>.</p>
<p><b>Units.</b> Q = official question (duplicate copies counted once); S = statement, one testable unit (a numbered statement, a pair,
an assertion, a reason, a chronology step, or an option read as a full sentence); SW = statement-level word occurrence (a word counted once
per statement); M = a false statement classified by its mechanism. Every percentage shows numerator/denominator. {exam} is analysed on its own –
no number is pooled with the other group.</p>
<p><b>Truth basis.</b> <i>key</i> – the official key fixes the unit; <i>key+fact</i> – key and an independent fact agree; <i>fact</i> – the key does not
fix the unit, the fact was checked; <i>pending</i>/UNSETTLED – neither settles it (kept out of T/F percentages). The published key is never changed;
disagreements are shown as key notes.</p>
<p><b>Recurrence labels</b> (by distinct years with a direct official question): High ≥ 5 years, Moderate 3–4, Low 1–2, Insufficient evidence 0.
<b>Confidence:</b> STRONG ≥ 6 questions over ≥ 3 years; MODERATE ≥ 3 questions; WEAK 1–2; NO EVIDENCE 0. A factual rule may be definitive; a
wording pattern is never a guarantee that it will recur.</p>""")
    # 3 dataset audit
    pr = [[E(p["title"] or p["id"]), p["year"], E(p["stage"]), E(p["key_status"]), E(p["key_doc_kind"]), p["Q"], p["deleted"], p["key_match"],
           p["key_changed"], p["no_official_doc"], p["third_party_conflict"]] for p in ver["papers"]]
    tiers = con.execute("SELECT p.exam, count(*) FROM question q JOIN paper p ON p.id=q.paper_id WHERE q.paper_id LIKE 'app:%' GROUP BY p.exam").fetchall()
    out.append(f"<h2 id='C3'>Dataset and source audit</h2><p>{len(ver['papers'])} official {exam} papers, {len(Q)} questions"
               + (f" ({len(dup)} duplicate copy counted once: {E(', '.join(f'{a} = {b}' for a, b in dup.items()))})" if dup else "")
               + f". Keys were compared with copies of APPSC documents (initial / final key booklets) wherever one could be found; "
               "APPSC's own site could not be reached from the build machine, so every 'APPSC document' is a copy, named in the table.</p>"
               + table(["Paper", "Year", "Stage", "Key status", "Key document", "Q", "Deleted", "Key = APPSC doc", "Changed by APPSC", "No APPSC doc",
                        "3rd-party conflict"], pr)
               + "<p><b>Evidence tiers.</b> Tier 1 (all statistics): the official papers above. Tier 2/3 (related evidence only, shown under each "
               "micro-topic, never counted): " + "; ".join(f"{E(e)} {n}" for e, n in tiers) + " questions from the app's APPSC PYQ bank "
               "(keys web-checked by the app, not APPSC documents).</p>"
               + f"<p>Statements: {len(allS)} (true {frac(len(T), TF)}, false {frac(len(F), TF)}, unsettled {sum(1 for s in allS if s['truth'] == 'U')}). "
               "Basis: " + "; ".join(f"{E(k)} {v}" for k, v in collections.Counter(s["truth_basis"] for s in allS).most_common()) + ".</p>"
               + f"<p>Verification (details in chapter 15): {len(ver['deleted'])} deleted questions, {len(ver['conflicts'])} key conflicts or "
               f"disagreements recorded, {len(ver['unresolved'])} unsettled statements, {len(ver['time_sensitive'])} time-sensitive facts.</p>")
    # 4 syllabus mapping
    cs = stats["coverage_summary"]
    rows = []
    for p in parts:
        lv = [l for s in p[2] for l in ([(s[0], s[1], 0)] + s[2])]
        codes = {l[0] for l in lv}
        d = sum(1 for c in codes if byleaf.get(c))
        rows.append([E(p[1]), len(codes), d, sum(len([q for q in byleaf.get(c, []) if q["id"] not in dup]) for c in codes)])
    out.append(f"<h2 id='C4'>Official syllabus and blueprint mapping</h2><p>Every official question was mapped by hand to ONE official syllabus "
               f"code – the micro-topic actually tested – during the statement analysis. {cs['leaves']} syllabus codes; {cs['direct']} have a direct "
               f"official question ({cs['direct_pct']}%), {cs['related_only']} only related evidence, {cs['none']} none.</p>"
               + table(["Syllabus part", "Codes", "Codes with direct PYQ", "Questions"], rows))
    # 5 structure
    ys = collections.defaultdict(collections.Counter)
    for q in ind:
        ys[(q["year"], q["stage"])][q["subject"] or "?"] += 1
    subs = sorted({s for c in ys.values() for s in c})
    out.append("<h2 id='C5'>Examination structure</h2><p>Questions per paper year/stage and subject label (unit = question).</p>"
               + table(["Year · stage"] + subs, [[f"{y} · {E(st)}"] + [c.get(s, "") for s in subs] for (y, st), c in sorted(ys.items())]))
    # 6 formats
    fm = collections.Counter(fmt(q["format"]) for q in ind)
    stg = sorted({q["stage"] for q in ind})
    rows = [[E(f), frac(n, len(ind))] + [frac(sum(1 for q in ind if fmt(q["format"]) == f and q["stage"] == s), sum(1 for q in ind if q["stage"] == s)) for s in stg]
            for f, n in fm.most_common()]
    fy = collections.defaultdict(collections.Counter)
    for q in ind:
        fy[q["year"]][fmt(q["format"])] += 1
    top = [f for f, _ in fm.most_common(6)]
    out.append("<h2 id='C6'>Overall question-format analysis</h2><p>Unit = question; denominators are all questions, then each stage.</p>"
               + table(["Format", "All"] + [f"{s}" for s in stg], rows)
               + "<h4>Formats by year (unit = question)</h4>" + table(["Year"] + top + ["total"], [[y] + [c.get(f, 0) for f in top] + [sum(c.values())] for y, c in sorted(fy.items())])
               + "<p class='u'>Format notes. <b>Statement-based</b>: each statement is a unit; options combine them, so a unit's truth follows from the key only when "
               "one reading fits. <b>One-liner</b>: each option is read as 'stem + option'; a true fact that is not the answer asked for is false here "
               "(mechanism 'true fact not the one asked'). <b>Matching</b>: each keyed pair and each wrong pair offered by a distractor is a unit. "
               "<b>Chronology</b>: each adjacent step of the keyed order. <b>Assertion-reason</b>: A, R and 'R explains A' are three units.</p>")
    # 7 universal language patterns
    l1 = []
    for k, rx in L1RX.items():
        hit = [s for s in allS if s["truth"] in ("T", "F") and rx.search(s["text"] or "")]
        t = sum(1 for s in hit if s["truth"] == "T")
        mm = collections.Counter(s["mechanism"] for s in hit if s["truth"] == "F").most_common(3)
        l1.append([f"<b>{E(k)}</b>", len(hit), frac(t, len(hit)), frac(len(hit) - t, len(hit)), "; ".join(f"{E(m)} {n}" for m, n in mm)])
    base = frac(len(T), TF)
    wr = []
    for w, d in sorted(stats["words"].items(), key=lambda x: -x[1]["SW"]):
        lv = [x for x in d["by_leaf"] if x[3] >= 3]
        spread = "; ".join(f"{E(x[0])}: {x[1]}T/{x[2]}F" for x in lv[:5])
        wr.append([f"<b>{E(w)}</b>", d["SW"], frac(d["T"], d["SW"]), frac(d["F"], d["SW"]), d["in_decisive_phrase"], spread or "<small>no micro-topic with ≥ 3</small>"])
    out.append(f"<h2 id='C7'>Universal language patterns</h2><p><b>Layer 1 – general reference only.</b> Unit = settled statement (T or F). "
               f"Baseline: {base} of all settled statements are true. A category's false rate above or below this baseline describes the papers, "
               "not a rule – the micro-topic tables in chapter 8 are the primary layer.</p>"
               + table(["Category (cue regex)", "Statements", "True", "False", "Top mechanisms among the false"], l1)
               + "<p class='u'>Cues: " + "; ".join(f"<b>{E(k)}</b> <code>{E(v)}</code>" for k, v in LAYER1.items()) + "</p>"
               "<h4>Tracked qualifier words</h4><p class='u'>Unit = SW (statement-level occurrence). 'Decisive' = statements where the word is "
               "inside the decisive phrase. The last column shows how the SAME word behaves in different micro-topics (codes with ≥ 3 occurrences).</p>"
               + table(["Word", "SW", "True", "False", "Decisive", "Behaviour by micro-topic (T/F)"], wr)
               + "<h4>False-statement mechanisms (all micro-topics)</h4><p class='u'>Unit = false statement (M); denominator "
               + str(stats["mechanisms_denominator"]) + ".</p>"
               + table(["Mechanism", "Count", "Share"], [[E(m), n, f"{n}/{stats['mechanisms_denominator']} = {p}%"] for m, n, p in stats["mechanisms"]])
               + "<p class='u'>Families used in the frequency boxes: " + "; ".join(f"<b>{E(k)}</b> = {E(', '.join(sorted(v)))}" for k, v in FAMILY.items()) + ".</p>")
    # 8 subject-wise micro-topic decoding
    body = ["<h2 id='C8'>Subject-wise micro-topic decoding</h2><p>One block per official syllabus code with at least one direct official question; "
            "codes without one are listed at the end of their section with any related evidence.</p>"]
    done = set()
    for p in parts:
        body.append(f"<h2 class='sub' id='P-{anchor(p[0])}'>{E(p[1])}</h2>")
        for s in p[2]:
            body.append(f"<h3 id='{anchor(s[0])}-sec' style='background:#dfe9f5'>{E(s[0])} {E(s[1])}</h3>")
            nop = []
            for code, text, depth in [(s[0], s[1], 0)] + s[2]:
                if code in done:
                    continue
                done.add(code)
                qs = byleaf.get(code, [])
                if qs:
                    body.append(leaf_chapter(code, text, f"{p[1]} › {s[0]} {s[1][:120]}", qs, S, dup, rel, depth))
                elif code != s[0] or not s[2]:
                    nop.append((code, text))
            if nop:
                body.append("<h4>Codes in this section with no direct official PYQ</h4><div class='nopyq'><ul>" + "".join(
                    f"<li id='{anchor(c)}'><b>{E(c)}</b> {E(t)}{related(rel.get(c), cap=4)}</li>" for c, t in nop) + "</ul></div>")
    out.append("".join(body))
    # 9 matching and chronology
    def idx(fs):
        rows = []
        for q in ind:
            if fmt(q["format"]) in fs:
                st = S[q["id"]]
                f = [s for s in st if s["truth"] == "F"]
                rows.append([f"<a href='#Q-{re.sub(r'[^A-Za-z0-9]+', '-', q['id'])}'>{E(q['year'])} Q{E(q['qno'])}</a>", f"<a href='#{anchor(q['leaf_code'])}'>{E(q['leaf_code'])}</a>",
                             E(q["text_original"][:140]), f"{len(st) - len(f)} / {len(f)}", "; ".join(f"{E(m)} {n}" for m, n in collections.Counter(s['mechanism'] for s in f).most_common(3))])
        return rows
    for cid, title, fs, intro in ((9, "Matching and chronology", {"matching", "chronology"},
                                   "Each keyed pair / step is a true unit; each wrong pair or order offered by a distractor is a false unit."),
                                  (10, "Assertion-reason", {"assertion-reason"}, "Units: A, R, and 'R explains A'.")):
        rows = idx(fs)
        allu = [s for q in ind if fmt(q["format"]) in fs for s in S[q["id"]]]
        f = [s for s in allu if s["truth"] == "F"]
        out.append(f"<h2 id='C{cid}'>{E(title)}</h2><p>{intro} {len(rows)} questions, {len(allu)} units, false {frac(len(f), len([s for s in allu if s['truth'] in 'TF']))}. "
                   "Mechanisms among false units: " + "; ".join(f"{E(m)} {frac(n, len(f))}" for m, n in collections.Counter(s['mechanism'] for s in f).most_common(6))
                   + ". Full deconstruction: follow the link to the question in chapter 8.</p>"
                   + table(["Question", "Code", "Stem", "T / F units", "Mechanisms"], rows))
    # 11 frequency tables
    rows = [[f"<a href='#{anchor(r['leaf'])}'>{E(r['leaf'])}</a>", E(r["official_wording"][:80]), r["official_Q"], r["years"], r["S"], f"{r['T']}/{r['F']}",
             E("; ".join(f"{m} {n}" for m, n in r["top_mechanisms"][:3])), E(r["recurrence"].replace(" historical recurrence", "")), E(r["confidence"].replace(" EVIDENCE", ""))]
            for r in stats["coverage"] if r["official_Q"]]
    out.append("<h2 id='C11'>Micro-topic frequency tables</h2><p class='u'>Q = official questions; years = distinct years; S = statements; T/F = true/false statements; "
               "recurrence and confidence as defined in chapter 2. Counts include the one duplicate copy where noted in chapter 3.</p>"
               + table(["Code", "Micro-topic", "Q", "Years", "S", "T/F", "Top mechanisms (M)", "Recurrence", "Confidence"], rows))
    # 12 high recurrence
    hi = sorted([r for r in stats["coverage"] if r["years"] >= 5], key=lambda r: (-r["years"], -r["official_Q"]))
    mo = [r for r in stats["coverage"] if 3 <= r["years"] < 5]
    out.append(f"<h2 id='C12'>High historical recurrence topics</h2><p>{len(hi)} codes appeared in ≥ 5 distinct years; {len(mo)} more in 3–4 years. "
               "Recurrence describes the available papers only – it is not a forecast.</p>"
               + table(["Code", "Micro-topic", "Years", "Q", "Year list", "Top mechanisms"],
                       [[f"<a href='#{anchor(r['leaf'])}'>{E(r['leaf'])}</a>", E(r["official_wording"]), r["years"], r["official_Q"], E(", ".join(map(str, r["years_list"]))),
                         E("; ".join(f"{m} {n}" for m, n in r["top_mechanisms"][:3]))] for r in hi])
               + "<h4>Moderate historical recurrence (3–4 years)</h4>"
               + table(["Code", "Micro-topic", "Years", "Q"], [[f"<a href='#{anchor(r['leaf'])}'>{E(r['leaf'])}</a>", E(r["official_wording"]), r["years"], r["official_Q"]] for r in mo]))
    # 13 group-specific
    om = {m: (n, p) for m, n, p in other["mechanisms"]}
    rows = [[E(m), f"{n}/{stats['mechanisms_denominator']} = {p}%", f"{om.get(m, (0, 0))[0]}/{other['mechanisms_denominator']} = {om.get(m, (0, 0))[1] or 0}%"]
            for m, n, p in stats["mechanisms"][:15]]
    of = dict(other["formats"]); otot = other["totals"]["Q"]
    frows = [[E(f), frac(n, len(ind)), frac(of.get(f, 0), otot)] for f, n in fm.most_common(8)]
    ox = "Group 2" if g == "g1" else "Group 1"
    out.append(f"<h2 id='C13'>{exam}-specific patterns</h2><p>{exam} compared with {ox} on the same units, each with its own denominator. The two exams have different "
               "syllabi and papers; the comparison is of the mix, not of individual questions.</p>"
               + "<h4>False-statement mechanisms (unit = false statement)</h4>" + table(["Mechanism", exam, ox], rows)
               + "<h4>Formats (unit = question)</h4>" + table(["Format", exam, ox], frows)
               + f"<p>Statements per question: {exam} {len(allS) / max(1, len(ind)):.2f} ({len(allS)}/{len(ind)}); {ox} "
               f"{other['totals']['S'] / max(1, otot):.2f} ({other['totals']['S']}/{otot}).</p>")
    # 14 revision framework
    rv = []
    for p in parts:
        items = []
        for s in p[2]:
            for code, text, depth in [(s[0], s[1], 0)] + s[2]:
                qs = [q for q in byleaf.get(code, []) if q["id"] not in dup]
                rules = [r for r in dict.fromkeys(json.loads(q["reconstruction"]).get("micro_topic_rule") for q in qs if q["reconstruction"]) if r]
                if rules:
                    items.append(f"<li><a href='#{anchor(code)}'><b>{E(code)}</b></a> {E(text[:70])}: " + " · ".join(E(r) for r in rules[:4]) + "</li>")
        if items:
            rv.append(f"<h4>{E(p[1])}</h4><ul class='rule'>" + "".join(items) + "</ul>")
    out.append("<h2 id='C14'>Revision framework</h2><p>The decoding rules, by syllabus code (up to four per code; all are in chapter 8). "
               "Revise the fact, then the rule, then the false versions APPSC built from it.</p>" + "".join(rv))
    # 15 coverage, evidence, source index
    cov = [[f"<a href='#{anchor(r['leaf'])}'>{E(r['leaf'])}</a>", E(r["official_wording"][:90]), E(r["status"].replace("Analysed with direct official PYQ evidence", "direct PYQ")
            .replace("Covered only through related evidence (other tiers)", "related only").replace("Analysed, but no direct PYQ found in available papers", "none")),
            r["official_Q"], r["secondary_Q_topic_level"], r["tertiary_Q_topic_level"]] for r in stats["coverage"]]
    vv = "".join(f"<li><a href='#Q-{re.sub(r'[^A-Za-z0-9]+', '-', c['id'])}'>{E(c['id'])}</a> – key <b>{E(c['key'])}</b>. {E(c['note'])}</li>" for c in ver["conflicts"])
    un = "".join(f"<li>{E(u['id'])} {E(u['label'])} [{E(u['truth'])}/{E(u['basis'])}] {E(u['text'])}</li>" for u in ver["unresolved"])
    ts = "".join(f"<li>{E(t['id'])} ({E(t['year'])}) – {E(t['note'])}</li>" for t in ver["time_sensitive"])
    srcs = collections.Counter(s["fact_source"] for s in allS if s["fact_source"])
    out.append("<h2 id='C15'>Coverage, evidence and source index</h2><h4>Coverage matrix – every syllabus code</h4><p class='u'>Official Q = direct official "
               "questions; secondary / tertiary = app-bank questions mapped to the code at topic level (related evidence).</p>"
               + table(["Code", "Official wording", "Status", "Official Q", "Secondary", "Tertiary"], cov)
               + f"<h4>Key conflicts and disagreements ({len(ver['conflicts'])}) – published key kept in every case</h4><ul>{vv}</ul>"
               + f"<h4>Unsettled statements ({len(ver['unresolved'])})</h4><ul>{un}</ul>"
               + f"<h4>Time-sensitive facts ({len(ver['time_sensitive'])})</h4><ul>{ts}</ul>"
               + "<h4>Fact sources cited (statements citing each, top 80)</h4>" + table(["Source", "Statements"], [[E(k), n] for k, n in srcs.most_common(80)])
               + "<h4>Papers</h4><ul>" + "".join(f"<li>{E(p['title'])} – key: {E(p['key_status'])}, {E(p['key_doc_kind'])}</li>" for p in ver["papers"]) + "</ul>")
    doc = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>APPSC {exam} PYQ Decoding Manual</title><style>{CSS}</style></head><body>{''.join(out)}</body></html>"
    path = f"data/pyqdecode/manual_{g}.html"
    open(path, "w").write(doc)
    print(g, "html", len(doc) // 1024, "KB")
    return path, exam


def pdf(path, exam):
    import os, subprocess
    os.makedirs("manuals", exist_ok=True)
    out = f"manuals/APPSC_{exam.replace(' ', '_')}_Complete_PYQ_Decoding_Manual.pdf"
    subprocess.run(["node", "tools/pyqdecode_pdf.js", path, out, f"APPSC {exam} PYQ Decoding Manual"], check=True)
    print("pdf", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    gs = [a for a in sys.argv[1:] if a in ("g1", "g2")] or ["g1", "g2"]
    for g in gs:
        path, exam = build(g)
        if "--html-only" not in sys.argv:
            pdf(path, exam)
