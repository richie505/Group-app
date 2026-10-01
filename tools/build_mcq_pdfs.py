#!/usr/bin/env python3
"""90-day MCQ schedule as PDFs: one PDF per plan day, MCQs only, each followed by its answer.

Headings follow the app: Day -> Topic (unit) -> Section (syllabus row) -> Subsection -> MCQs.

  * Study and Sunday days: every MCQ of each section the plan brings in for the first time that day.
    Sections the plan never lists go on the day of the nearest listed section of the same book, so
    all MCQs in the app appear exactly once across these days.
  * Days that only revisit earlier sections (revision days, some Sundays): a revision set from those
    sections (HIGH 15, MED 8, LOW 5 questions per section, spread over its subsections).
  * Mock days (84-90) have no sections in the plan, so they get no PDF.

Each day also gets an answer key ("<out_dir>/Answer Keys/"): question numbers and answers only, in a grid
under the section headings, numbered exactly as in that day's MCQ PDF.

Usage: python3 tools/build_mcq_pdfs.py app/src/main/assets <out_dir>
"""
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Sans", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")

# app colours (ui/theme/Theme.kt)
NAVY, INK, BODY, MUTED = HexColor("#0F2557"), HexColor("#12203A"), HexColor("#1F2937"), HexColor("#5A6B88")
ACCENT, ACCENT_SOFT, GREEN, LINE = HexColor("#3949AB"), HexColor("#E8EAF6"), HexColor("#15803D"), HexColor("#E5E8EF")
PRI = {"HIGH": "#C62828", "MED": "#B45309", "LOW": "#4B5563"}

S = {
    "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=20, leading=25, textColor=NAVY),
    "sub": ParagraphStyle("sub", fontName="Sans", fontSize=10.5, leading=15, textColor=MUTED),
    "brief": ParagraphStyle("brief", fontName="Sans", fontSize=9, leading=13, textColor=MUTED),
    "toc": ParagraphStyle("toc", fontName="Sans", fontSize=9, leading=13, textColor=BODY, leftIndent=10),
    "topic_k": ParagraphStyle("topic_k", fontName="Sans-Bold", fontSize=8.5, leading=12, textColor=ACCENT),
    "topic": ParagraphStyle("topic", fontName="Sans-Bold", fontSize=13, leading=17, textColor=INK),
    "section": ParagraphStyle("section", fontName="Sans-Bold", fontSize=11.5, leading=15.5, textColor=INK),
    "meta": ParagraphStyle("meta", fontName="Sans", fontSize=8.5, leading=12, textColor=MUTED),
    "subsec": ParagraphStyle("subsec", fontName="Sans-Bold", fontSize=10, leading=14, textColor=ACCENT),
    "key_h": ParagraphStyle("key_h", fontName="Sans-Bold", fontSize=9.5, leading=13, textColor=INK),
    "key": ParagraphStyle("key", fontName="Sans", fontSize=8.6, leading=11, textColor=INK),
    "q": ParagraphStyle("q", fontName="Sans", fontSize=10, leading=14, textColor=BODY, alignment=TA_LEFT),
    "opt": ParagraphStyle("opt", fontName="Sans", fontSize=9.6, leading=13.2, textColor=BODY, leftIndent=26, firstLineIndent=-18),
    "ans": ParagraphStyle("ans", fontName="Sans-Bold", fontSize=9.6, leading=13.2, textColor=GREEN, leftIndent=8),
}


def esc(text):
    return escape(text).replace("\n", "<br/>")


def title_case(focus):
    small = {"and", "of", "&", "the", "in", "+"}
    words = focus.lower().split()
    out = " ".join(w if w in small or not w[0].isalpha() else w[0].upper() + w[1:] for w in words)
    return out.replace("Ir", "IR")


def day_title(day):
    """The day's heading as the app shows it (DayScreens.kt): Sundays have no focus in the plan."""
    if not day["focus"] and day["type"] == "sunday":
        return "Weekly Review + Current Affairs"
    return title_case(day["focus"])


def load(assets):
    index = json.loads((assets / "index.json").read_text())["books"]
    plan = json.loads((assets / "plan.json").read_text())
    subs_titles, mcq = {}, {}
    for b in range(1, 7):
        book = json.loads((assets / f"book{b}.json").read_text())
        rows = [r for u in book["units"] for r in u["rows"]]
        subs_titles[b] = [[s["t"] for s in r["secs"]] for r in rows]
        m = json.loads((assets / f"mcq{b}.json").read_text())
        mcq[b] = {int(r): list(zip(m["subs"][r], qs)) for r, qs in m["rows"].items()}
    return index, plan, subs_titles, mcq


def schedule(index, plan, mcq):
    """day n -> list of (book, row, kind) where kind is 'new' or 'rev'."""
    first = {}
    for d in plan["days"]:
        for r in d["rows"]:
            if r.get("ref"):
                first.setdefault(tuple(r["ref"]), d["n"])
    # sections the plan never lists: same day as the nearest listed section of the book, placed after it
    extra = defaultdict(list)  # anchor (book,row) -> [rows]
    for b in index:
        bid, n = b["id"], len(b["rows"])
        for ri in range(n):
            if (bid, ri) in first or not mcq[bid].get(ri):
                continue
            anchor = next(((bid, j) for j in range(ri - 1, -1, -1) if (bid, j) in first), None) \
                or next(((bid, j) for j in range(ri + 1, n) if (bid, j) in first), None)
            extra[anchor].append((bid, ri))
    days = {}
    for d in plan["days"]:
        refs = list(dict.fromkeys(tuple(r["ref"]) for r in d["rows"] if r.get("ref")))
        new = [x for x in refs if first[x] == d["n"]]
        if new:
            out = []
            for x in new:
                out.append((*x, "new"))
                out += [(*e, "new") for e in extra.get(x, [])]
            days[d["n"]] = out
        else:
            days[d["n"]] = [(*x, "rev") for x in refs]
    return days, first


def pick_revision(qs, k):
    """k questions spread evenly over a section's list (it is in subsection order)."""
    if len(qs) <= k:
        return qs
    step = len(qs) / k
    return [qs[int(i * step)] for i in range(k)]


def question_block(n, q):
    flow = [Paragraph(f"<b>Q{n}.</b> {esc(q['s'])}", S["q"])]
    for i, o in enumerate(q["o"]):
        flow.append(Paragraph(f"({i + 1})&nbsp;&nbsp;{esc(o)}", S["opt"]))
    flow.append(Paragraph(f"Answer: ({q['a'] + 1}) {esc(q['o'][q['a']])}", S["ans"]))
    flow.append(Spacer(1, 7))
    return KeepTogether(flow)


def header_block(day, headline, sub, lines):
    flow = [
        Paragraph("APPSC PREP · MCQ SCHEDULE", S["topic_k"]),
        Spacer(1, 3),
        Paragraph(esc(headline), S["title"]),
        Spacer(1, 2),
        Paragraph(esc(sub), S["sub"]),
        Spacer(1, 6),
    ]
    flow += [Paragraph(esc(t), S["brief"]) for t in lines]
    flow.append(Spacer(1, 8))
    return flow


def rule():
    t = Table([[""]], colWidths=["100%"], rowHeights=[0.6])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, LINE)]))
    return t


def select(job):
    """The day's sections and their MCQs, in print order: [(book, row, [(sub, q)])], plus a summary line."""
    rows, mcq = job["rows"], job["data"]["mcq"]
    rev = all(k == "rev" for *_, k in rows)
    sel = []  # (book, row, [(sub, q)])
    for b, ri, kind in rows:
        # subsection order (the generator interleaves them a little); section-level ones last
        qs = sorted(mcq[b].get(ri, []), key=lambda x: (x[0] < 0, x[0]))
        if kind == "rev":
            pri = job["pri"].get((b, ri), "MED")
            qs = pick_revision(qs, {"HIGH": 15, "MED": 8, "LOW": 5}.get(pri, 8))
        if qs:
            sel.append((b, ri, qs))
    total = sum(len(qs) for *_, qs in sel)
    kind_line = (f"Revision set · {total} MCQs from today's {len(sel)} sections (first given on Days "
                 f"{min(job['first'][(b, r)] for b, r, _ in sel)}–{max(job['first'][(b, r)] for b, r, _ in sel)})"
                 if rev else f"{total} MCQs · {len(sel)} sections")
    return sel, kind_line


def build_day(job):
    day, rows, data, out = job["day"], job["rows"], job["data"], Path(job["out"])
    index, subs_titles, mcq = data["index"], data["subs"], data["mcq"]
    n_day = day["n"]
    when = date.fromisoformat(day["date"])
    datestr = f"{day['dow']}, {when.day} {when.strftime('%b %Y')}"
    story = []
    qn = 0

    sel, kind_line = select(job)
    story += header_block(day, f"Day {n_day} of 90 · {day_title(day)}",
                          f"{datestr} · {title_case(day['phase'])} · {kind_line}", [])
    # contents: sections with question ranges
    start = 1
    toc = []
    for i, (b, ri, qs) in enumerate(sel, 1):
        row = index[b - 1]["rows"][ri]
        toc.append(Paragraph(f"{i}.&nbsp;&nbsp;{esc(row['title'])} <font color='#8A96AD'>· Q{start}–{start + len(qs) - 1}</font>", S["toc"]))
        start += len(qs)
    story += toc + [Spacer(1, 10)]

    last_unit = None
    for i, (b, ri, qs) in enumerate(sel, 1):
        info = index[b - 1]
        row = info["rows"][ri]
        unit = (b, row["u"])
        if unit != last_unit:
            u = info["units"][row["u"]]
            story.append(rule())
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"TOPIC {row['u'] + 1} · {esc(info['short'].upper())} &nbsp;<font color='#5A6B88'>{esc(u['code'])}</font>", S["topic_k"]))
            story.append(Paragraph(esc(u["title"]), S["topic"]))
            story.append(Spacer(1, 8))
            last_unit = unit
        pri = job["pri"].get((b, ri))
        meta = [f"<font color='{PRI[pri]}'><b>{pri}</b></font>"] if pri in PRI else []
        meta += [esc(" · ".join(row["codes"]))] if row["codes"] else []
        meta += [f"Book {b} · pp {row['p1']}-{row['p2']}", f"{len(qs)} MCQs"]
        story.append(KeepTogether([
            Paragraph(f"{i}. {esc(row['title'])}", S["section"]),
            Paragraph("&nbsp;&nbsp;·&nbsp;&nbsp;".join(meta), S["meta"]),
            Spacer(1, 6),
        ]))
        last_sub = None
        for si, q in qs:
            if si != last_sub:
                name = subs_titles[b][ri][si] if si >= 0 else "Other MCQs of this section"
                num = f"{i}.{si + 1}" if si >= 0 else f"{i}.–"
                story.append(Paragraph(f"{num}&nbsp;&nbsp;{esc(name)}", S["subsec"]))
                story.append(Spacer(1, 4))
                last_sub = si
            qn += 1
            story.append(question_block(qn, q))
        story.append(Spacer(1, 6))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(16 * mm, 9 * mm, f"APPSC Prep · Day {n_day} of 90 · {datestr}")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=16 * mm,
                            title=f"APPSC Prep MCQ Schedule - Day {n_day}", author="APPSC Prep")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return n_day, qn, out.name


def build_key(job):
    """Answer key: question number and answer only, in a grid under each section's heading."""
    day, out = job["day"], Path(job["key_out"])
    index = job["data"]["index"]
    n_day = day["n"]
    when = date.fromisoformat(day["date"])
    datestr = f"{day['dow']}, {when.day} {when.strftime('%b %Y')}"
    sel, kind_line = select(job)
    story = header_block(day, f"Day {n_day} of 90 · Answer Key",
                         f"{day_title(day)} · {datestr} · {kind_line}",
                         ["Answers are option numbers (1)–(4), as printed in the day's MCQ PDF."])
    cols = 10
    width = (A4[0] - 32 * mm) / cols
    qn = 0
    for i, (b, ri, qs) in enumerate(sel, 1):
        row = index[b - 1]["rows"][ri]
        head = Paragraph(f"{i}. {esc(row['title'])} <font color='#8A96AD'>· Q{qn + 1}–{qn + len(qs)}</font>", S["key_h"])
        cells = []
        for _, q in qs:
            qn += 1
            cells.append(Paragraph(f"<font color='#5A6B88'>{qn}.</font>&nbsp;<b>({q['a'] + 1})</b>", S["key"]))
        grid = [cells[k:k + cols] for k in range(0, len(cells), cols)]
        grid[-1] += [""] * (cols - len(grid[-1]))
        t = Table(grid, colWidths=[width] * cols)
        t.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F7F8FA")]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        # short sections stay on one page; long grids may break across pages
        story += [KeepTogether([head, Spacer(1, 3), t])] if len(grid) <= 8 else [head, Spacer(1, 3), t]
        story.append(Spacer(1, 8))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(16 * mm, 9 * mm, f"APPSC Prep · Day {n_day} of 90 · Answer Key")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=16 * mm,
                            title=f"APPSC Prep MCQ Schedule - Day {n_day} Answer Key", author="APPSC Prep")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return n_day, qn, out.name


def file_name(day):
    focus = re.sub(r"\((\d)/(\d)\)", r"(\1 of \2)", day_title(day))
    focus = re.sub(r'[\\:*?"<>|]', "", focus)
    return f"Day {day['n']:02d} - {focus}.pdf"


def main():
    assets, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    index, plan, subs_titles, mcq = load(assets)
    days, first = schedule(index, plan, mcq)
    pri = {}
    for d in plan["days"]:
        for r in d["rows"]:
            if r.get("ref"):
                pri.setdefault(tuple(r["ref"]), r.get("pri"))

    data = {"index": index, "subs": subs_titles, "mcq": mcq}
    jobs = []
    for d in plan["days"]:
        if not days[d["n"]]:  # mock week: no sections
            continue
        jobs.append({"day": d, "rows": days[d["n"]], "data": data, "pri": pri, "first": first,
                     "out": str(out_dir / file_name(d)),
                     "key_out": str(out_dir / "Answer Keys" / file_name(d).replace(".pdf", " - Answer Key.pdf"))})
    once = sum(len(mcq[b].get(r, [])) for rows in days.values() for b, r, k in rows if k == "new")
    print("MCQs given once on study days:", once, "of", sum(len(v) for b in mcq for v in mcq[b].values()))
    with ProcessPoolExecutor() as ex:
        for n, qn, name in ex.map(build_day, jobs):
            print(f"{name}: {qn} MCQs")
        for n, qn, name in ex.map(build_key, jobs):
            print(f"{name}: {qn} answers")


if __name__ == "__main__":
    main()
