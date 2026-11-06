"""Turns a unit written to the blueprint (data/blueprint/out/<unit>.md) into an app topic: each numbered section
(### n. TITLE) is a page; #### sub-sections are headings; bullets, numbered lists, tables and the boxes
(!TRAP 'T', !KEY 'K', !NUM 'M', !PAIR 'P', !BOX 'V', > note 'a') are the app's blocks.

    from blueprint_md import unit_pages
"""
import re

BOLD = re.compile(r"\*\*(.+?)\*\*")


def runs(t):
    out, pos = [], 0
    for m in BOLD.finditer(t):
        if m.start() > pos:
            out.append([t[pos:m.start()], 0])
        out.append([m.group(1), 1])
        pos = m.end()
    if pos < len(t):
        out.append([t[pos:], 0])
    return out or [["", 0]]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def title_case(t):
    small = {"and", "of", "the", "in", "on", "for", "to", "a", "an", "vs", "or", "by", "with", "at", "from"}
    words = t.split()
    out = []
    for i, w in enumerate(words):
        if w.isupper() and len(w) > 1 and not re.search(r"\d", w) and w.lower() not in {"ii", "iii", "iv", "vi"}:
            lw = w.lower()
            out.append(lw if (i and lw in small) else lw[:1].upper() + lw[1:])
        else:
            out.append(w)
    return " ".join(out)


BOX = {"!TRAP": "T", "!KEY": "K", "!NUM": "M", "!PAIR": "P", "!BOX": "V"}


def unit_pages(md):
    """(unit title, [(page title, blocks)])"""
    lines = md.split("\n")
    title = ""
    pages = []
    cur = None
    table = None

    def flush_table():
        nonlocal table
        if table and cur is not None:
            head, rows = table
            cur[1].append({"k": "t", "h": [runs(c) for c in head], "r": [[runs(c) for c in r] for r in rows]})
        table = None

    for line in lines:
        s = line.rstrip()
        if s.startswith("COVERAGE:"):
            continue
        if s.startswith("|"):
            if re.match(r"^\|[\s:|-]+\|$", s):
                continue
            if table is None:
                table = (cells(s), [])
            else:
                table[1].append(cells(s))
            continue
        flush_table()
        if not s.strip():
            continue
        if s.startswith("## "):
            title = title_case(s[3:].split(" | ", 1)[-1].strip())
        elif m := re.match(r"^### \d+\.\s*(.+)$", s):
            cur = (title_case(m.group(1).strip()), [])
            pages.append(cur)
        elif cur is None:
            continue
        elif m := re.match(r"^#{4,5}\s*(?:\d+(?:\.\d+)*\s+)?(.+)$", s):
            cur[1].append({"k": "h", "x": runs(m.group(1).strip())})
        elif (tag := s.split(" ", 1)[0]) in BOX:
            body = s.split(" ", 1)[1] if " " in s else ""
            if tag == "!PAIR":
                body = body.replace(" || ", "\n")
            cur[1].append({"k": BOX[tag], "x": runs(body)})
        elif s.startswith("> "):
            cur[1].append({"k": "a", "x": runs(s[2:])})
        elif m := re.match(r"^(\s{2,})[-*] (.+)$", s):
            cur[1].append({"k": "s", "x": runs(m.group(2))})
        elif m := re.match(r"^[-*] (.+)$", s):
            cur[1].append({"k": "b", "x": runs(m.group(1))})
        elif m := re.match(r"^\s*(\d+)\. (.+)$", s):
            cur[1].append({"k": "b", "x": runs(f"{m.group(1)}. {m.group(2)}")})
        else:
            cur[1].append({"k": "p", "x": runs(s.strip())})
    flush_table()
    return title, pages
