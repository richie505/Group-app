#!/usr/bin/env python3
"""Convert 'APPSC Strategy + Restructured 90-Day Plan.pdf' into plan.json for the app.

Each plan row is linked to a notes row (book, row index) using the row codes, so the
app can open Day -> Topic -> Section -> Subsection -> content.

Usage: python3 tools/parse_plan.py <plan.pdf> <notes_json_dir> <out.json>
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

HEADER_RE = re.compile(r"DAY\s+(\d+)\s*\|\s*(\w{3}),\s*(\d{1,2}\s+\w{3}\s+\d{4})\s*\|\s*(.*)")
TIME_RE = re.compile(r"^\d{2}:\d{2}")
CODE_RE = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+")
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def iso(date_text):
    d, m, y = date_text.split()
    return f"{y}-{MONTHS[m]:02d}-{int(d):02d}"


def cells(row):
    return [re.sub(r"\s+", " ", c or "").strip() for c in row if c and c.strip()]


def load_notes_index(notes_dir):
    """code -> list of (book, row_seq); also per-book (p1, p2) for page lookups."""
    index, pages = {}, {}
    for n in range(1, 7):
        book = json.loads((notes_dir / f"book{n}.json").read_text())
        seq = 0
        for u in book["units"]:
            for r in u["rows"]:
                for c in r["codes"]:
                    index.setdefault(c, []).append((n, seq))
                pages.setdefault(n, []).append((r["p1"], r["p2"], seq))
                seq += 1
    return index, pages


def write_index(notes_dir, path):
    """Lightweight catalogue of all books/rows (no content) for list screens."""
    books = []
    for n in range(1, 7):
        book = json.loads((notes_dir / f"book{n}.json").read_text())
        units, rows = [], []
        for ui, u in enumerate(book["units"]):
            units.append({"code": u["code"], "title": u["title"]})
            for r in u["rows"]:
                rows.append({
                    "u": ui, "codes": r["codes"], "title": r["title"], "tag": r["tag"],
                    "pyq": r["pyq"], "p1": r["p1"], "p2": r["p2"], "n": len(r["secs"]),
                })
        books.append({"id": n, "title": book["title"], "short": book["short"],
                      "pages": book["pages"], "units": units, "rows": rows})
    path.write_text(json.dumps({"books": books}, ensure_ascii=False, separators=(",", ":")))


def day_type(phase, n):
    p = phase.upper()
    if "SUNDAY" in p:
        return "sunday"
    if "R2" in p or "REVISION" in p:
        return "revision"
    if "MOCK" in p:
        return "mock"
    return "study"


def main():
    plan_pdf, notes_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    index, _ = load_notes_index(notes_dir)
    doc = pymupdf.open(plan_pdf)

    days, cur, buffer = [], None, []
    last_style = None
    in_buffer = False

    for pno in range(7, doc.page_count):
        page = doc[pno]
        tabs = page.find_tables().tables
        tboxes = [t.bbox for t in tabs]
        items = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                text = "".join(s["text"] for s in l["spans"]).strip()
                if not text:
                    continue
                y = l["bbox"][1]
                if any(t[1] - 1 <= y <= t[3] + 1 for t in tboxes):
                    continue
                s = l["spans"][0]
                items.append((y, "line", (text, round(s["size"], 1), "Bold" in s["font"], "Italic" in s["font"])))
        for t in tabs:
            items.append((t.bbox[1], "table", t.extract()))
        items.sort(key=lambda it: it[0])

        for y, kind, data in items:
            if kind == "line":
                text, size, bold, italic = data
                if size == 8.0 and "Strategy + Restructured" in text:
                    continue  # footer
                if size == 14.0:
                    m = HEADER_RE.match(text)
                    if m:
                        n, dow, date, rest = m.groups()
                        parts = [p.strip() for p in rest.split("|")]
                        cur = {
                            "n": int(n), "date": iso(date), "dow": dow,
                            "phase": parts[0], "focus": " | ".join(parts[1:]),
                            "brief": [], "rows": [], "tasks": [],
                        }
                        days.append(cur)
                        last_style = "header"
                    elif text.startswith("FINAL BUFFER"):
                        in_buffer = True
                        cur = None
                        last_style = None
                    elif cur is not None and last_style == "header":
                        cur["focus"] = (cur["focus"] + " " + text).strip()
                    elif text.startswith("APPENDIX"):
                        in_buffer = False
                        cur = None
                    continue
                if cur is None:
                    continue
                if italic and "days to" in text:
                    cur["left"] = text
                    last_style = "left"
                    continue
                if text.startswith("Paper:"):
                    text = "Paper: " + re.split(r"[\\/]", text)[-1]
                # brief lines: 10.0 bold starts a line; 10.0 regular / 8.6 continue or add
                if size >= 9.5 and bold:
                    cur["brief"].append(text)
                    last_style = "brief"
                elif cur["brief"] and last_style in ("brief", "detail") and size >= 9.5:
                    cur["brief"][-1] += " " + text
                elif size < 9.5:
                    if last_style == "detail" and not re.match(r"^(Rows|Paper|Tick)", text):
                        cur["brief"][-1] += " " + text
                    else:
                        cur["brief"].append(text)
                    last_style = "detail"
                else:
                    cur["brief"].append(text)
                    last_style = "brief"
                continue

            # tables
            for raw in data:
                c = cells(raw)
                if not c:
                    continue
                if in_buffer:
                    if c[0] in ("Dates", "Book") or len(c) < 2:
                        continue
                    buffer.append({"dates": c[0], "work": " ".join(c[1:])})
                    continue
                if cur is None:
                    continue
                if c[0] in ("Row codes", "Time") or "____" in " ".join(c):
                    continue
                if TIME_RE.match(c[0]) and len(c) >= 2:
                    task = {"time": c[0], "block": c[1] if len(c) > 2 else "", "task": c[-1] if len(c) > 2 else c[1]}
                    cur["tasks"].append(task)
                elif CODE_RE.match(c[0]) and len(c) >= 4:
                    codes = [x.strip() for x in c[0].split(",") if x.strip()]
                    row = {"codes": codes, "topic": c[1], "p": c[2] if len(c) > 2 else ""}
                    if len(c) >= 5:
                        row["pyq"] = c[3]
                        row["pri"] = c[4]
                    ref = None
                    for code in codes:
                        if code in index:
                            ref = index[code][0]
                            break
                    if ref:
                        row["ref"] = list(ref)
                    cur["rows"].append(row)
                elif cur["tasks"] and not TIME_RE.match(c[0]):
                    cur["tasks"][-1]["task"] += " " + " ".join(c)
                elif cur["rows"] and len(c) <= 2:
                    # wrapped topic text of the previous row
                    cur["rows"][-1]["topic"] += " " + " ".join(c)

    for d in days:
        d["type"] = day_type(d["phase"] + " " + d["focus"], d["n"])
        d["brief"] = [re.sub(r"\s+", " ", b).strip() for b in d["brief"]]

    unresolved = [(d["n"], r["codes"]) for d in days for r in d["rows"] if "ref" not in r]
    plan = {
        "start": days[0]["date"] if days else "",
        "exam": "2027-01-03",
        "examLabel": "3 Jan 2027",
        "days": days,
        "buffer": buffer,
    }
    out.write_text(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
    write_index(notes_dir, out.parent / "index.json")
    print(f"days={len(days)} rows={sum(len(d['rows']) for d in days)} "
          f"tasks={sum(len(d['tasks']) for d in days)} buffer={len(buffer)} unresolved={len(unresolved)}")
    for u in unresolved[:15]:
        print("  unresolved", u)


if __name__ == "__main__":
    main()
