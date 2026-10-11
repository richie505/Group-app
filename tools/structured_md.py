"""Structured notes: a small markdown form <-> the app's blocks.

    # Heading                 -> {"k": "h"}
    - **Label:** text         -> {"k": "b"}
      - text                  -> {"k": "s"}
    !! Not in your sources... -> the gap line (run flag 6), on a bullet or sub-bullet
    **x** bold, [GK] muted (flag 4)
Tables are kept as they are: "<<table N>>" stands for the page's N-th table block.
"""
import re

TOKEN = re.compile(r"(\*\*.+?\*\*|\[GK\])")


def runs(text):
    gap = text.startswith("!! ")
    if gap:
        return [[text[3:], 6]]
    out = []
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append([part[2:-2], 1])
        elif part == "[GK]":
            out.append([part, 4])
        else:
            out.append([part, 0])
    return out


def to_blocks(md, tables):
    blocks = []
    for line in md.splitlines():
        if not line.strip():
            continue
        m = re.match(r"<<table (\d+)>>\s*$", line.strip())
        if m:
            blocks.append(tables[int(m.group(1))])
            continue
        if line.startswith("# "):
            blocks.append({"k": "h", "x": runs(line[2:].strip())})
        elif re.match(r"\s{2,}- ", line):
            blocks.append({"k": "s", "x": runs(line.strip()[2:])})
        elif line.startswith("- "):
            blocks.append({"k": "b", "x": runs(line[2:].strip())})
        elif line.startswith("> "):
            blocks.append({"k": "x", "x": runs(line[2:].strip())})
        else:
            blocks.append({"k": "p", "x": runs(line.strip())})
    return blocks


def from_blocks(blocks):
    """A page as the markdown form (input for rewriting), tables as placeholders."""
    lines, tables = [], []
    for b in blocks:
        if b["k"] == "t":
            lines.append(f"<<table {len(tables)}>>")
            tables.append(b)
            continue
        text = ""
        for t, f in b["x"]:
            if f & 6 == 6 or f == 6:
                text += "!! " + t
            elif f & 1:
                text += f"**{t}**" if t.strip() else t
            elif f & 8:
                continue
            else:
                text += t
        prefix = {"h": "# ", "b": "- ", "s": "  - ", "x": "> "}.get(b["k"], "")
        lines.append(prefix + text.strip())
    return "\n".join(lines), tables
