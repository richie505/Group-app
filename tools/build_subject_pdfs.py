#!/usr/bin/env python3
"""Subject-wise PDFs of the app's notes and MCQs: for each of the 6 books, "<n> <subject> - Notes.pdf" and
"<n> <subject> - MCQs.pdf".

Both follow the app: Unit -> Section (syllabus row) -> Subsection (page). The notes PDF has every page's
headings, bullets, tables and exam angles; the MCQ PDF has every section MCQ under its subsection, each with its
answer, Solution and Additional Information. A contents list opens each PDF and the PDF outline (bookmarks)
goes to every unit and section.

Usage: python3 tools/build_subject_pdfs.py app/src/main/assets <out_dir> [notes|mcqs]
(the app's name in the headers comes from the assets' edition.json, e.g. APPSC Complete)
"""
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
import build_mcq_pdfs as M  # noqa: E402  (fonts, colours, styles, footer)
from reportlab.lib.colors import HexColor  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

S, T = M.S, M.T
C = {k: HexColor(v) for k, v in T.items() if isinstance(v, str)}
X = {
    "body": ParagraphStyle("nb", fontName="Sans", fontSize=9.6, leading=13.6, textColor=C["body"]),
    "h": ParagraphStyle("nh", fontName="Sans-Bold", fontSize=10, leading=14, textColor=C["ink"], spaceBefore=4),
    "b": ParagraphStyle("nbul", fontName="Sans", fontSize=9.6, leading=13.6, textColor=C["body"], leftIndent=12, bulletIndent=2),
    "s": ParagraphStyle("nsub", fontName="Sans", fontSize=9.3, leading=13, textColor=C["body"], leftIndent=26, bulletIndent=15),
    "x": ParagraphStyle("nx", fontName="Sans", fontSize=9.3, leading=13, textColor=C["ink"], backColor=HexColor("#FFF4E0"),
                        borderPadding=(4, 6, 4, 6), leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=4),
    "cell": ParagraphStyle("nc", fontName="Sans", fontSize=8.4, leading=11, textColor=C["body"]),
    "cellh": ParagraphStyle("nch", fontName="Sans-Bold", fontSize=8.4, leading=11, textColor=C["title"]),
    "unit": ParagraphStyle("nu", fontName="Sans-Bold", fontSize=15, leading=20, textColor=C["title"]),
    "sol_k": ParagraphStyle("sk", fontName="Sans-Bold", fontSize=8, leading=11, textColor=C["accent"], leftIndent=8, spaceBefore=2),
    "sol": ParagraphStyle("sb", fontName="Sans", fontSize=8.8, leading=12, textColor=C["body"], leftIndent=20, bulletIndent=10),
}


def runs(rs):
    """App text runs [[text, flags], ...] -> reportlab markup (1 bold, 2 italic, 4 muted, 8 full form)."""
    out = []
    for x in rs:
        text, flags = x[0], (x[1] if len(x) > 1 else 0)
        t = escape(text).replace("\n", "<br/>")
        if flags & 4:
            t = f'<font color="{T["faint"]}" size="7.5">{t}</font>'
        elif flags & 8:
            t = f'<i><font color="{T["muted"]}">{t}</font></i>'
        else:
            if flags & 2:
                t = f"<i>{t}</i>"
            if flags & 1:
                t = f"<b>{t}</b>"
        out.append(t)
    return "".join(out)


def md(text):
    """**bold** in explanation bullets -> markup."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def table(b, width):
    head, rows = b["h"], b["r"]
    cols = max([len(head)] + [len(r) for r in rows])
    if cols == 0:
        return None
    has_head = any(runs(c).strip() for c in head)
    data = ([head] if has_head else []) + rows
    # column share by the square root of its text (as the app does), never under 12% of the page
    tot = [max(1, sum(len("".join(x[0] for x in (r[c] if c < len(r) else []))) for r in data)) ** 0.5 for c in range(cols)]
    w = [max(0.12, x / sum(tot)) for x in tot]
    w = [width * x / sum(w) for x in w]
    cells = [[Paragraph(runs(r[c]) if c < len(r) else "", X["cellh"] if has_head and i == 0 else X["cell"]) for c in range(cols)]
             for i, r in enumerate(data)]
    t = Table(cells, colWidths=w, repeatRows=1 if has_head else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.5, C["line"]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if has_head:
        style.append(("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EAF6")))
    for i in range(1 if has_head else 0, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), C["zebra"]))
    t.setStyle(TableStyle(style))
    return t


def block(b, width):
    k = b["k"]
    if k == "t":
        t = table(b, width)
        return [Spacer(1, 3), t, Spacer(1, 4)] if t else []
    text = runs(b.get("x", []))
    if not text.strip():
        return []
    if k == "h":
        return [Paragraph(text, X["h"])]
    if k == "b":
        return [Paragraph(text, X["b"], bulletText="•")]
    if k == "s":
        return [Paragraph(text, X["s"], bulletText="–")]
    if k == "x":
        # some notes already open with "Exam angle:"
        text = re.sub(r"^(<b>)?\s*Exam angle:\s*(</b>)?\s*", "", text)
        return [Paragraph(f"<b>Exam angle:</b> {text}", X["x"])]
    return [Paragraph(text, X["body"])]


class Doc(SimpleDocTemplate):
    """Adds PDF outline entries for paragraphs tagged with ._outline = (level, title, key)."""

    def afterFlowable(self, f):
        o = getattr(f, "_outline", None)
        if o:
            level, title, key = o
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=level, closed=level == 0)


def tagged(text, style, level, title, key):
    p = Paragraph(text, style)
    p._outline = (level, title, key)
    return p


def cover(book, kind, units, count_line, app="APPSC Prep"):
    flow = [Paragraph(f"{escape(app.upper())} · {kind.upper()}", S["topic_k"]), Spacer(1, 3),
            Paragraph(escape(book["title"]), S["title"]), Spacer(1, 3), Paragraph(count_line, S["sub"]), Spacer(1, 10),
            Paragraph("Contents", S["section"]), Spacer(1, 4)]
    n = 0
    for u in units:
        flow.append(Paragraph(escape(u["title"]), S["subsec"]))
        for r in u["rows"]:
            n += 1
            flow.append(Paragraph(f"{n}. {escape(r['title'])}", S["toc"]))
        flow.append(Spacer(1, 4))
    flow.append(PageBreak())
    return flow


def build(job):
    assets, out, b, kind = Path(job["assets"]), Path(job["out"]), job["book"], job["kind"]
    book = json.loads((assets / f"book{b}.json").read_text())
    units = book["units"]
    width = A4[0] - 32 * mm
    flow, n_row, count = [], 0, 0
    mcq = json.loads((assets / f"mcq{b}.json").read_text()) if kind == "mcqs" else None
    if kind == "notes":
        pages = sum(len(r["secs"]) for u in units for r in u["rows"])
        line = f"{sum(len(u['rows']) for u in units)} sections · {pages} subsections"
    else:
        total = sum(len(v) for v in mcq["rows"].values())
        line = f"{total} MCQs, each with its answer, solution and additional information"
    flow += cover(book, "Notes" if kind == "notes" else "MCQs", units, line, job["app"])
    qn = 0
    for ui, u in enumerate(units):
        flow.append(CondPageBreak(60 * mm))
        flow.append(tagged(f"Unit {ui + 1}. {escape(u['title'])}", X["unit"], 0, f"Unit {ui + 1}. {u['title']}", f"u{ui}"))
        flow.append(Spacer(1, 6))
        for r in u["rows"]:
            ri = n_row
            n_row += 1
            head = [CondPageBreak(40 * mm), M.rule(), Spacer(1, 4),
                    tagged(f"{ri + 1}. {escape(r['title'])}", S["section"], 1, f"{ri + 1}. {r['title']}", f"r{ri}"),
                    Spacer(1, 4)]
            if kind == "notes":
                flow += head
                for si, s in enumerate(r["secs"]):
                    body = [f for blk in s["b"] for f in block(blk, width)]
                    hd = [Paragraph(f"{ri + 1}.{si + 1}  {escape(s['t'])}", S["subsec"]), Spacer(1, 2)]
                    flow.append(KeepTogether(hd + body[:1]))
                    flow += body[1:]
                    flow.append(Spacer(1, 6))
                    count += 1
            else:
                qs = mcq["rows"].get(str(ri), [])
                subs = mcq["subs"].get(str(ri), [-1] * len(qs))
                if not qs:
                    continue
                flow += head
                groups = {}
                for sub, q in zip(subs, qs):
                    groups.setdefault(sub, []).append(q)
                order = sorted(groups, key=lambda x: (x < 0, x))
                for sub in order:
                    title = r["secs"][sub]["t"] if 0 <= sub < len(r["secs"]) else "Other MCQs of this section"
                    label = f"{ri + 1}.{sub + 1}  {escape(title)}" if sub >= 0 else escape(title)
                    first = True
                    for q in groups[sub]:
                        qn += 1
                        top, rest = question(qn, q)
                        if first:
                            top = [Paragraph(label, S["subsec"]), Spacer(1, 3)] + top
                            first = False
                        flow.append(KeepTogether(top))
                        flow += rest
                    flow.append(Spacer(1, 4))
                count += len(qs)
    doc = Doc(str(out), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
              title=f"{book['short']} - {'Notes' if kind == 'notes' else 'MCQs'}", author=job["app"])
    deco = M.page_decor(f"{job['app']} · {book['short']} · {'Notes' if kind == 'notes' else 'MCQs'}")
    doc.build(flow, onFirstPage=deco, onLaterPages=deco)
    return out.name, count, doc.page


def question(n, q):
    """(the question with its options and answer, kept together; then its explanation)."""
    top = [Paragraph(f"<b>Q{n}.</b> {M.esc(q['s'])}", S["q"])]
    top += [Paragraph(f"({i + 1})&nbsp;&nbsp;{M.esc(o)}", S["opt"]) for i, o in enumerate(q["o"])]
    a = q.get("a", -1)
    if 0 <= a < len(q["o"]):
        top.append(Paragraph(f"Answer: ({a + 1}) {M.esc(q['o'][a])}", S["ans"]))
    out = []
    if q.get("xs"):
        for head, items in (("SOLUTION", q["xs"]), ("ADDITIONAL INFORMATION", q.get("xa") or [])):
            if items:
                bullets = [Paragraph(md(x), X["sol"], bulletText="•") for x in items]
                out.append(KeepTogether([Paragraph(head, X["sol_k"]), bullets[0]]))  # no heading alone at a page end
                out += bullets[1:]
    elif q.get("x"):
        out.append(Paragraph(f"<b>Explanation:</b> {M.esc(q['x'])}", X["sol"]))
    out.append(Spacer(1, 8))
    return top, out


def main():
    assets, out_dir = sys.argv[1], Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    index = json.loads((Path(assets) / "index.json").read_text())["books"]
    edition = Path(assets) / "edition.json"
    app = json.loads(edition.read_text())["name"] if edition.exists() else "APPSC Prep"
    only = sys.argv[3] if len(sys.argv) > 3 else None
    jobs = []
    for b in index:
        name = f"{b['id']} {b['short'].replace('/', '-')}"
        for kind, suffix in (("mcqs", "MCQs"), ("notes", "Notes")):
            if only in (None, kind):
                jobs.append({"assets": assets, "book": b["id"], "kind": kind, "app": app,
                             "out": str(out_dir / f"{name} - {suffix}.pdf")})
    with ProcessPoolExecutor() as ex:
        for name, count, pages in ex.map(build, jobs):
            print(f"{name}: {count} {'subsections' if 'Notes' in name else 'MCQs'}, {pages} pages", flush=True)


if __name__ == "__main__":
    main()
