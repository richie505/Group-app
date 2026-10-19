#!/usr/bin/env python3
"""MCQ Clue Sheet (PDF): answer-key patterns of the app's 43,937 MCQs, checked against real past papers.

    python3 tools/mcq_patterns.py > app.json
    python3 tools/mcq_patterns.py <past-paper dir> > past.json
    python3 tools/mcq_patterns.py <past-paper dir> --appsc > appsc.json
    python3 tools/build_clue_sheet.py app.json past.json appsc.json <out.pdf>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_mcq_pdfs as M  # noqa: E402
from reportlab.lib.colors import HexColor  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

S, T = M.S, M.T
C = {k: HexColor(v) for k, v in T.items() if isinstance(v, str)}
body = ParagraphStyle("b", fontName="Sans", fontSize=9.4, leading=13.4, textColor=C["body"])
bul = ParagraphStyle("u", parent=body, leftIndent=12, bulletIndent=2)
cell = ParagraphStyle("c", fontName="Sans", fontSize=8.6, leading=11.4, textColor=C["body"])
cellh = ParagraphStyle("ch", fontName="Sans-Bold", fontSize=8.6, leading=11.4, textColor=C["title"])
box = ParagraphStyle("x", parent=body, backColor=HexColor("#FFF4E0"), borderPadding=(5, 7, 5, 7), leftIndent=7, rightIndent=7,
                     spaceBefore=4, spaceAfter=8, textColor=C["ink"])
WIDTH = A4[0] - 32 * mm


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "–"


def table(rows, widths, head=True):
    data = [[Paragraph(str(c), cellh if head and i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[WIDTH * w for w in widths], repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, C["line"]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EAF6")))
    t.setStyle(TableStyle(st))
    return [t, Spacer(1, 8)]


def h(text):
    return [Spacer(1, 6), Paragraph(text, S["section"]), Spacer(1, 4)]


def b(text):
    return Paragraph(text, bul, bulletText="•")


def main():
    A, P, Q = (json.load(open(f)) for f in sys.argv[1:4])
    out = sys.argv[4]

    def rule(X, name):
        r = X["rules"][name]
        return f"<b>{r['rate']:.0f}%</b> <font size=7 color='{T['muted']}'>of {r['applies']:,}</font>"

    def pos(X, kind, i):
        v = X["position_by_kind"].get(kind, {})
        n = sum(v.values())
        return f"{pct(v.get(f'({i})', 0), n)}"

    def numrank(X, k):
        v = X["number_rank_of_key"]
        return pct(v.get(k, 0), sum(v.values()))

    R = {k: k for k in A["rules"]}
    LONG = "Clearly longest option (25%+ longer than the rest) is the key"
    ALL = "'All of them' / 'Both' option, when offered, is the key"
    NONE = "'None' / 'Neither' option, when offered, is the key"
    NOABS = "Direct Qs: the only option WITHOUT an absolute word (only/always/never/all) is the key"
    HEDGE = "Direct Qs: the only option with a hedge word (may/generally/mainly) is the key"
    NEGABS = "NOT/incorrect Qs: the only option with an absolute word is the key"
    ALIKE = "The option most like the other three (distractors are variations of the key)"
    ECHO = "The only option that echoes a word of the question"
    assert all(x in R for x in (LONG, ALL, NONE, NOABS, HEDGE, NEGABS, ALIKE, ECHO))

    f = [Paragraph("APPSC PREP · MCQ CLUE SHEET", S["topic_k"]), Spacer(1, 3),
         Paragraph("Tricks to crack the MCQs — read from 43,937 answer keys", S["title"]), Spacer(1, 4),
         Paragraph(f"Every trick below was measured: how many questions it applies to and how often it lands on the keyed "
                   f"answer. A blind guess is right <b>25%</b> of the time. Each trick was checked on three sets: "
                   f"<b>this app's {A['total']:,} MCQs</b>, <b>{P['total']:,} real past-paper questions</b> and the "
                   f"<b>{Q['total']:,} of them from APPSC papers</b>.", body), Spacer(1, 6),
         Paragraph(f"<b>The honest headline.</b> Followed blindly, the best procedure here gets <b>{A['strategies']['app']}%</b> "
                   f"of the app's MCQs but only <b>{Q['strategies']['real']}%</b> of real APPSC questions. The app's bank has "
                   f"strong key patterns (Part B) that real papers do not. In the exam these tricks are for the questions you "
                   f"cannot answer: they turn a blind guess into a small edge (Part D). Knowing the fact still beats every trick.",
                   box)]

    f += h("Part A — Tricks that also work in real APPSC papers")
    f += table([
        ["Trick", "APPSC papers", "All past papers", "App MCQs"],
        ["<b>NOT / incorrect questions</b> (\"Which is NOT…\", \"…is incorrect\"): the key is option <b>(4)</b> more than any other",
         f"<b>{pos(Q, 'negative', 4)}</b>", pos(P, 'negative', 4), pos(A, 'negative', 4)],
        ["NOT questions: if exactly one option has an absolute word (<i>only, always, never, all, every, must</i>), that is the false one — pick it",
         rule(Q, NEGABS), rule(P, NEGABS), rule(A, NEGABS)],
        ["<b>Number options</b> (years, %, counts): the key is a <b>middle value</b> — the smallest is rarely right",
         f"middle <b>{pct(Q['number_rank_of_key'].get('2nd', 0) + Q['number_rank_of_key'].get('3rd', 0), sum(Q['number_rank_of_key'].values()))}</b>, smallest {numrank(Q, 'smallest')}",
         f"middle {pct(P['number_rank_of_key'].get('2nd', 0) + P['number_rank_of_key'].get('3rd', 0), sum(P['number_rank_of_key'].values()))}",
         f"middle {pct(A['number_rank_of_key'].get('2nd', 0) + A['number_rank_of_key'].get('3rd', 0), sum(A['number_rank_of_key'].values()))}"],
        ["Direct questions: if exactly one option has <b>no</b> absolute word, it is often the key", rule(Q, NOABS), rule(P, NOABS), rule(A, NOABS)],
        ["Options with an absolute word are rarely right — eliminate them first", f"{Q['absolute_word_options_keyed_pct']:.0f}% keyed",
         f"{P['absolute_word_options_keyed_pct']:.0f}% keyed", f"{A['absolute_word_options_keyed_pct']:.0f}% keyed"],
        ["<b>Assertion–Reason</b>: \"Both true and R explains A\" is the most common key", f"{pct(Q['assertion_reason_keys'].get('Both true, R IS the correct explanation', 0), Q['kinds'].get('assertion-reason', 0))}",
         pct(P['assertion_reason_keys'].get('Both true, R IS the correct explanation', 0), P['kinds'].get('assertion-reason', 0)),
         pct(A['assertion_reason_keys'].get('Both true, R IS the correct explanation', 0), A['kinds'].get('assertion-reason', 0))],
        ["\"All of the above\" / \"Both 1 and 2\", when offered", rule(Q, ALL), rule(P, ALL), rule(A, ALL)],
        ["The clearly longest option (25%+ longer than the others)", rule(Q, LONG), rule(P, LONG), rule(A, LONG)],
    ], [0.52, 0.17, 0.15, 0.16])
    f.append(Paragraph("<b>Avoid</b> in real papers: \"None of the above / Neither\" "
                       f"({NONE and Q['rules'][NONE]['rate']:.0f}% in APPSC, {P['rules'][NONE]['rate']:.0f}% in all papers) and the lone "
                       f"\"hedge\" option with <i>may / generally / mainly</i> ({Q['rules'][HEDGE]['rate']:.0f}% in APPSC) — both are "
                       "below a blind guess. Among direct questions APPSC keys lean slightly to option (1) "
                       f"({pos(Q, 'direct', 1)}) and away from (4) ({pos(Q, 'direct', 4)}).", body))

    f += h("Part B — Patterns in this app's answer keys (they do not carry to the exam)")
    f.append(Paragraph("These come from how the app's questions were written. They crack the app's MCQs, but real "
                       "papers do not follow them — use them to spot a lucky guess in practice, never as exam strategy.", body))
    f.append(Spacer(1, 5))
    def code(c, X=A):
        v = X["statement_codes"].get(c)
        return f"{v['rate']:.0f}% <font size=7 color='{T['muted']}'>of {v['offered']:,}</font>" if v else "–"

    f += table([
        ["Question type / option", "App MCQs", "Real papers (all)", "APPSC"],
        ["Statement questions — code <b>\"1 and 2 only\"</b> is the key", code("1 and 2 only"), code("1 and 2 only", P), code("1 and 2 only", Q)],
        ["Statement questions — code <b>\"2 and 3 only\"</b> is the key", code("2 and 3 only"), code("2 and 3 only", P), code("2 and 3 only", Q)],
        ["Statement questions — <b>\"1, 2, 3 and 4\"</b> / <b>\"1, 2 and 4 only\"</b>", f"{code('1, 2, 3 and 4')} / {code('1, 2 and 4 only')}", "–", "–"],
        ["Statement questions — key in position (3)", pos(A, 'statements', 3), pos(P, 'statements', 3), pos(Q, 'statements', 3)],
        ["Match the following — key is option (1)", pos(A, 'match', 1), pos(P, 'match', 1), pos(Q, 'match', 1)],
        ["Chronological order — key is option (1)", pos(A, 'order', 1), pos(P, 'order', 1), pos(Q, 'order', 1)],
        ["Assertion–Reason — key is option (1)", pos(A, 'assertion-reason', 1), pos(P, 'assertion-reason', 1), pos(Q, 'assertion-reason', 1)],
        ["Direct questions — clearly longest option", rule(A, LONG), rule(P, LONG), rule(Q, LONG)],
        ["Number options — the 3rd-smallest value", f"{numrank(A, '3rd')}", numrank(P, '3rd'), numrank(Q, '3rd')],
        ["The only option echoing a word of the question", rule(A, ECHO), rule(P, ECHO), rule(Q, ECHO)],
        ["The option most like the other three", rule(A, ALIKE), rule(P, ALIKE), rule(Q, ALIKE)],
    ], [0.52, 0.18, 0.16, 0.14])

    f += h("Part C — Playbook by question type")
    f += [
        b("<b>Statement questions</b> (\"Which of the statements is/are correct?\"): judge the statement you are surest of, "
          "then strike every code that contradicts it — one sure statement usually leaves two codes, two leave one. "
          "Look for the absolute word (<i>only, all, never, first</i>) in a statement: it is usually the false one."),
        b("<b>Match the following</b>: match the pair you know best, strike codes without it, then the next pair. Two sure "
          "pairs settle almost every code; never work all four from scratch."),
        b("<b>Chronological order</b>: fix the first and the last event only; codes rarely agree on both ends."),
        b("<b>Assertion–Reason</b>: decide A, then R, separately. Only if both are true ask \"does R say <i>why</i> A happens?\" "
          "— R that only restates or adds a side fact is \"not the correct explanation\"."),
        b("<b>NOT / incorrect</b>: read the options as true/false statements; the one with an absolute word or a wrong number "
          "is your answer. Last option (4) is the most common key in APPSC."),
        b("<b>Number options</b>: drop the smallest first, then the largest; choose between the two middle values with whatever "
          "you remember (era, order of magnitude)."),
        b("<b>Direct questions</b>: cross out options with absolute words, then any option outside the question's subject; "
          "between the rest the more precise / qualified one is more often right."),
    ]

    f += h("Part D — When to guess (APPSC: +1 right, −⅓ wrong)")
    edge = Q["strategies"]["real"] / 100
    f += table([
        ["Your situation", "Chance of the key", "Expected marks for a guess"],
        ["Blind guess, 4 options", "25%", "0.00 — no gain, no loss on average"],
        ["Patterns only (Parts A + C, nothing known)", f"{100 * edge:.0f}%", f"{edge - (1 - edge) / 3:+.2f}"],
        ["One option eliminated for sure", "33%", f"{1 / 3 - (2 / 3) / 3:+.2f}"],
        ["Two options eliminated", "50%", f"{0.5 - 0.5 / 3:+.2f}"],
    ], [0.45, 0.2, 0.35])
    f.append(Paragraph("Rule of thumb: <b>guess whenever you can strike out at least one option</b> for a real reason; with "
                       "nothing to go on, a pattern-based guess is barely positive — skip it if time is short.", body))
    f.append(Spacer(1, 8))
    f.append(Paragraph(f"Counted from this app's {A['total']:,} MCQs and {P['total']:,} past-paper questions "
                       f"({Q['total']:,} APPSC). Rebuild: tools/mcq_patterns.py and tools/build_clue_sheet.py.", S["meta"]))

    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
                            title="MCQ Clue Sheet", author="APPSC Prep")
    deco = M.page_decor("APPSC Prep · MCQ Clue Sheet")
    doc.build(f, onFirstPage=deco, onLaterPages=deco)
    print(out, doc.page, "pages")


if __name__ == "__main__":
    main()
