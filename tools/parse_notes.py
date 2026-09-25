#!/usr/bin/env python3
"""Convert the Combined Notes PDFs (G1+G2) into JSON for the app.

Hierarchy produced per book:
    unit (Topic) -> row (Section) -> sec (Subsection, the blue ■ headings) -> blocks (content)

Usage: python3 tools/parse_notes.py <pdf_dir> <out_dir>
Expects book1.pdf .. book6.pdf in <pdf_dir>; writes book1.json .. book6.json.
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

BOOK_TITLES = {
    1: ("History & Culture (Indian and Andhra Pradesh)", "History & Culture"),
    2: ("Polity, Constitution, Governance, Society & International Relations", "Polity, Society & IR"),
    3: ("Indian and Andhra Pradesh Economy", "Economy"),
    4: ("Geography (India, World and Andhra Pradesh)", "Geography"),
    5: ("Science, Technology and Environment", "Science, Tech & Environment"),
    6: ("Current Affairs and Current Events", "Current Affairs"),
}

MUTED = 0x5A6B88
NAVY = 0x0F2557
BLUE = 0x1D4ED8
BROWN = 0x9A3412
PURPLE = 0x7C3AED
GREEN_HEAD = 0x166534
WHITE = 0xFFFFFF

# run flags
F_BOLD, F_ITALIC, F_MUTED = 1, 2, 4


def span_flags(s):
    f = 0
    if "Bold" in s["font"]:
        f |= F_BOLD
    if "Italic" in s["font"]:
        f |= F_ITALIC
    if s["color"] == MUTED:
        f |= F_MUTED
    return f


def add_run(runs, text, flags):
    if not text:
        return
    if runs and runs[-1][1] == flags:
        runs[-1][0] += text
    else:
        runs.append([text, flags])


def join_runs(a, b):
    """Append runs b to runs a with a single separating space."""
    if not b:
        return a
    if a and not a[-1][0].endswith(" ") and not b[0][0].startswith(" "):
        add_run(a, " ", a[-1][1])
    for t, f in b:
        add_run(a, t, f)
    return a


def clean_runs(runs):
    out = []
    for t, f in runs:
        t = re.sub(r"[  ]{2,}", " ", t)
        add_run(out, t, f)
    if out:
        out[0][0] = out[0][0].lstrip()
        out[-1][0] = out[-1][0].rstrip()
    out = [r for r in out if r[0]]
    # plain single run -> string (compact JSON)
    if len(out) == 1 and out[0][1] == 0:
        return out[0][0]
    return out


def runs_text(runs):
    return "".join(t for t, _ in runs)


def strip_marker(runs, marker):
    """Remove a leading bullet marker from the first run(s)."""
    while runs and not runs[0][0].strip():
        runs.pop(0)
    if runs:
        t = runs[0][0].lstrip()
        if t.startswith(marker):
            t = t[len(marker):].lstrip()
        runs[0][0] = t
        if not t:
            runs.pop(0)
    return runs


def line_info(line):
    spans = [s for s in line["spans"] if s["text"]]
    if not spans:
        return None
    text = "".join(s["text"] for s in spans)
    if not text.strip():
        return None
    first = next(s for s in spans if s["text"].strip())
    return {
        "x": line["bbox"][0],
        "y": line["bbox"][1],
        "y1": line["bbox"][3],
        "text": text.strip(),
        "size": round(first["size"], 1),
        "color": first["color"],
        "bold": "Bold" in first["font"],
        "italic": "Italic" in first["font"],
        "spans": spans,
    }


def is_badge_span(s):
    return round(s["size"], 1) == 6.5 and "Bold" in s["font"]


def extract_tables(page):
    """Return list of (bbox, header_is_bold, rows-of-runs)."""
    out = []
    try:
        tabs = page.find_tables()
    except Exception:
        return out
    if not tabs.tables:
        return out
    words = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    words.append(s)
    for t in tabs.tables:
        rows = []
        header_bold = True
        for ri, row in enumerate(t.rows):
            cells = []
            for cb in row.cells:
                if cb is None:
                    cells.append(None)
                    continue
                x0, y0, x1, y1 = cb
                runs = []
                prev_y = None
                for s in words:
                    cx = (s["bbox"][0] + s["bbox"][2]) / 2
                    cy = (s["bbox"][1] + s["bbox"][3]) / 2
                    if x0 - 1 <= cx <= x1 + 1 and y0 - 1 <= cy <= y1 + 1:
                        if prev_y is not None and abs(s["bbox"][1] - prev_y) > 2:
                            if runs and not runs[-1][0].endswith(" "):
                                add_run(runs, " ", runs[-1][1])
                        add_run(runs, s["text"], span_flags(s))
                        prev_y = s["bbox"][1]
                        if ri == 0 and "Bold" not in s["font"] and s["text"].strip():
                            header_bold = False
                cells.append(runs)
            rows.append(cells)
        # drop columns that are empty (None or blank) in every row
        ncol = max(len(r) for r in rows) if rows else 0
        keep = [
            c for c in range(ncol)
            if any(c < len(r) and r[c] and runs_text(r[c]).strip() for r in rows)
        ]
        rows = [[(r[c] if c < len(r) and r[c] else []) for c in keep] for r in rows]
        rows = [r for r in rows if any(runs_text(c).strip() for c in r)]
        if rows:
            out.append((tuple(t.bbox), header_bold, rows))
    return out


def parse_book(pdf_path, book_no):
    doc = pymupdf.open(pdf_path)
    title, short = BOOK_TITLES[book_no]
    book = {"id": book_no, "title": title, "short": short, "pages": doc.page_count, "units": []}

    unit = None
    row = None
    sec = None
    block = None  # last content block (for continuation)
    last_kind = None  # classification of the previous line
    pending_codes, pending_tags = [], []

    def ensure_unit():
        nonlocal unit
        if unit is None:
            unit = {"code": "", "title": short, "rows": []}
            book["units"].append(unit)
        return unit

    def new_row(page_no):
        nonlocal row, sec, block, pending_codes, pending_tags
        u = ensure_unit()
        row = {
            "codes": pending_codes, "tag": " ".join(pending_tags), "title": "",
            "sub": [], "pyq": "", "p1": page_no, "p2": page_no, "secs": [], "src": [],
        }
        pending_codes, pending_tags = [], []
        u["rows"].append(row)
        sec = None
        block = None
        return row

    def ensure_sec(page_no, title="Overview"):
        nonlocal sec, block
        if row is None:
            new_row(page_no)
            row["title"] = unit["title"] if unit else short
        if sec is None:
            sec = {"t": title, "badges": [], "p": page_no, "b": []}
            row["secs"].append(sec)
            block = None
        return sec

    def add_badges(text):
        if sec is None:
            return
        for token in ("APPSC", "other exams", "GROUP-II"):
            if token in text and token not in sec["badges"]:
                sec["badges"].append(token)

    for pno in range(1, doc.page_count):  # page 1 is the book's intro page
        page = doc[pno]
        page_no = pno + 1
        tables = extract_tables(page)
        tboxes = [tb for tb, _, _ in tables]

        items = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                li = line_info(l)
                if not li:
                    continue
                cx = (l["bbox"][0] + l["bbox"][2]) / 2
                cy = (l["bbox"][1] + l["bbox"][3]) / 2
                if any(x0 - 1 <= cx <= x1 + 1 and y0 - 1 <= cy <= y1 + 1 for x0, y0, x1, y1 in tboxes):
                    continue
                items.append((li["y"], li["x"], "line", li))
        for tb, hb, rows in tables:
            items.append((tb[1], tb[0], "table", (hb, rows)))
        items.sort(key=lambda it: (round(it[0], 0), it[1]))

        for _, _, kind, data in items:
            if kind == "table":
                hb, rows = data
                sec_ = ensure_sec(page_no)
                prev = sec_["b"][-1] if sec_["b"] else None
                cols = len(rows[0])
                # continuation of a table broken across pages
                if prev and prev.get("k") == "t" and last_kind == "table" and len(prev["h"]) == cols and not hb:
                    prev["r"].extend([[clean_runs(c) for c in r] for r in rows])
                else:
                    if hb and len(rows) > 1:
                        head, body = rows[0], rows[1:]
                    else:
                        head, body = [[] for _ in range(cols)], rows
                    sec_["b"].append({
                        "k": "t",
                        "h": [clean_runs(c) for c in head],
                        "r": [[clean_runs(c) for c in r] for r in body],
                    })
                block = None
                last_kind = "table"
                row["p2"] = page_no
                continue

            li = data
            text, size, color = li["text"], li["size"], li["color"]

            # running header / footer
            if color == MUTED and size in (7.2, 6.8) and (li["y"] < 35 or li["y"] > 800):
                continue
            # subject banner
            if color == WHITE and size == 12.0:
                continue

            if li["bold"] and color == NAVY and size == 9.4:  # UNIT heading
                if text.startswith(("UNIT", "ITEM")):
                    m = re.match(r"(?:UNIT|ITEM)\s+(\S+)\s*[•·]\s*(.*)", text)
                    code, utitle = (m.group(1), m.group(2)) if m else ("", text)
                    unit = {"code": code, "title": utitle, "rows": []}
                    book["units"].append(unit)
                    row = sec = block = None
                elif unit is not None and last_kind == "unit":
                    unit["title"] += " " + text
                last_kind = "unit"
                continue

            if li["bold"] and color == WHITE and size == 7.6:  # GROUP-I / + GROUP-II tag
                if row is not None and not row["secs"]:
                    row["tag"] = (row["tag"] + " " + text).strip()
                else:
                    pending_tags.append(text)
                continue

            if li["bold"] and color == NAVY and size == 8.4:  # row code
                if row is not None and not row["secs"]:
                    row["codes"].append(text)
                else:
                    pending_codes.append(text)
                continue

            if li["bold"] and color == NAVY and size == 10.2:  # row title
                if last_kind == "rowtitle" and row is not None:
                    row["title"] += " " + text
                else:
                    new_row(page_no)
                    row["title"] = text
                last_kind = "rowtitle"
                continue

            if color == MUTED and size == 7.8 and not li["italic"] and row is not None and not row["secs"]:
                if text.startswith("Group-II") or not row["sub"]:
                    row["sub"].append(text)
                else:
                    row["sub"][-1] += " " + text
                last_kind = "rowsub"
                continue

            if color == MUTED and size == 7.6 and text.startswith("PYQs on this row") and row is not None:
                row["pyq"] = text.split(":", 1)[1].strip()
                last_kind = "pyq"
                continue

            if color == MUTED and size == 7.0:  # Sources lines
                if row is None:
                    continue
                if text.startswith("Sources") or not row["src"]:
                    row["src"].append(text)
                else:
                    row["src"][-1] += " " + text
                last_kind = "src"
                continue

            # badge-only line (APPSC / other / exams / GROUP-II under a heading)
            if all(is_badge_span(s) for s in li["spans"] if s["text"].strip()):
                add_badges(text if text != "exams" else "other exams")
                if text in ("other", "exams") and sec is not None and "other exams" not in sec["badges"]:
                    sec["badges"].append("other exams")
                continue

            if li["bold"] and color == BLUE and size == 9.3:  # ■ subsection heading
                head = "".join(s["text"] for s in li["spans"] if not is_badge_span(s)).strip()
                badge_text = " ".join(s["text"] for s in li["spans"] if is_badge_span(s))
                if head.startswith("■"):
                    if row is None:
                        new_row(page_no)
                        row["title"] = unit["title"] if unit else short
                    sec = {"t": head.lstrip("■").strip(), "badges": [], "p": page_no, "b": []}
                    row["secs"].append(sec)
                    block = None
                elif sec is not None and last_kind == "sechead":
                    sec["t"] += " " + head
                add_badges(badge_text)
                last_kind = "sechead"
                row["p2"] = page_no
                continue

            if li["bold"] and color == GREEN_HEAD:  # "Universal angles"
                if row is None:
                    new_row(page_no)
                sec = {"t": text, "badges": [], "p": page_no, "b": [], "u": 1}
                row["secs"].append(sec)
                block = None
                last_kind = "sechead"
                continue

            # ---- content line ----
            runs = []
            for s in li["spans"]:
                add_run(runs, s["text"], span_flags(s))
            stripped = text.lstrip()
            x = li["x"]

            new_kind = None
            if stripped.startswith("•"):
                new_kind, runs = "b", strip_marker(runs, "•")
            elif stripped.startswith("–") and x > 40:
                new_kind, runs = "s", strip_marker(runs, "–")
            elif color == BROWN and stripped.startswith("Exam angle"):
                new_kind = "x"
            elif color == PURPLE and (stripped.startswith("See also") or stripped.startswith("Group-II")):
                new_kind = "a"
            elif x <= 36:
                new_kind = "p"

            if new_kind is None and block is not None and last_kind == "content":
                join_runs(block["_runs"], runs)
            else:
                if new_kind is None:
                    new_kind = {BROWN: "x", PURPLE: "a"}.get(color, "n" if (color == MUTED and li["italic"]) else "p")
                sec_ = ensure_sec(page_no)
                block = {"k": new_kind, "_runs": runs}
                sec_["b"].append(block)
            last_kind = "content"
            row["p2"] = page_no

    # finalize runs
    for u in book["units"]:
        for r in u["rows"]:
            r["title"] = re.sub(r"\s+", " ", r["title"]).strip()
            r["secs"] = [s for s in r["secs"] if s["b"]]
            # cross-reference lines before the first heading belong to the row, not a subsection
            if r["secs"] and r["secs"][0]["t"] == "Overview":
                first = r["secs"][0]
                if all(b.get("k") == "a" for b in first["b"]):
                    r["see"] = [clean_runs(b.pop("_runs")) for b in first["b"]]
                    r["secs"].pop(0)
            for s in r["secs"]:
                s["t"] = re.sub(r"\s+", " ", s["t"]).strip()
                for b in s["b"]:
                    if "_runs" in b:
                        b["x"] = clean_runs(b.pop("_runs"))
                s["b"] = [b for b in s["b"] if b.get("k") == "t" or b.get("x")]
    for u in book["units"]:
        u["rows"] = [r for r in u["rows"] if r["secs"] or r["title"]]
    book["units"] = [u for u in book["units"] if u["rows"]]
    return book


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    books = [int(a) for a in sys.argv[3:]] or range(1, 7)
    for n in books:
        book = parse_book(src / f"book{n}.pdf", n)
        (out / f"book{n}.json").write_text(json.dumps(book, ensure_ascii=False, separators=(",", ":")))
        rows = sum(len(u["rows"]) for u in book["units"])
        secs = sum(len(r["secs"]) for u in book["units"] for r in u["rows"])
        print(f"book{n}: units={len(book['units'])} rows={rows} subsections={secs}")


if __name__ == "__main__":
    main()
