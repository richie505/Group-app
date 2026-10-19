#!/usr/bin/env python3
"""Mind maps for the revision app: every notes page as a tree of its own facts, nothing reworded.

    python3 tools/build_mindmap.py app/src/main/assets app/src/revise/assets [book:rows ...]   e.g. 2:4 1:0-2
Each page's tree goes into rev<book>.json as the page's "m" (the app draws it in place of the text):
  * the page title is the centre; each heading of the page is a branch (text before the first heading too);
  * a bullet "Label: details; more" is a node "Label" with the details as leaves, split at ";";
    a bullet without a label is one node; its sub-bullets are its children;
  * a table row is a node (its first cell) with a leaf per other cell ("Column: value" when the table has
    more than two columns);
  * exam angles are kept whole as highlighted nodes; source tags ([GK], (CDI), ...) and gap lines go.
Node: {"x": runs, "k": "b" | "x" (exam angle) | "t" (table row), "c": [children]}
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_revision import clean  # noqa: E402


def rs(x):
    """runs as [[text, flags]] (a run may come without flags); muted asides out."""
    out = [[r[0], r[1] if len(r) > 1 else 0] for r in x]
    return [r for r in out if not r[1] & 4]


def plain(r):
    return "".join(t for t, _ in r)


def cut(r, pos):
    """Split runs at a character offset."""
    a, b, n = [], [], 0
    for t, f in r:
        if n + len(t) <= pos:
            a.append([t, f])
        elif n >= pos:
            b.append([t, f])
        else:
            a.append([t[: pos - n], f])
            b.append([t[pos - n:], f])
        n += len(t)
    return a, b


def split_semis(r):
    """Split runs at '; ' outside brackets."""
    text = plain(r)
    depth, cuts = 0, []
    for i, ch in enumerate(text):
        depth += ch in "(["
        depth -= ch in ")]"
        if ch == ";" and depth == 0:
            cuts.append(i)
    parts, rest, off = [], r, 0
    for c in cuts:
        a, rest = cut(rest, c - off)
        off = c
        parts.append(a)
    parts.append(rest)
    out = []
    for p in parts:
        p = clean([list(x) for x in p])
        if p and plain(p).strip(" ;"):
            p[0][0] = p[0][0].lstrip(" ;")
            out.append(p)
    return out


def bullet_node(runs):
    r = clean(rs(runs))
    if not r or not plain(r).strip():
        return None
    text = plain(r)
    m = re.match(r"^([^:]{2,60}):\s+", text)
    if m and r[0][1] & 1 and len(r[0][0]) >= m.end(1):  # a bold "Label:" opens the bullet
        label, rest = cut(r, m.end(1))
        rest[0][0] = rest[0][0].lstrip(": ") if rest else ""
        if rest and rest[0][0] == "":
            rest = rest[1:]
        leaves = split_semis(rest)
        return {"x": clean(label), "k": "b", "c": [{"x": x, "k": "b", "c": []} for x in leaves]}
    return {"x": r, "k": "b", "c": []}


def table_nodes(b):
    head = [plain(clean(rs(c))).strip() for c in b["h"]]
    out = []
    for row in b["r"]:
        cells = [clean(rs(c)) for c in row]
        if not cells or not plain(cells[0]).strip():
            continue
        kids = []
        for i, c in enumerate(cells[1:], start=1):
            if not plain(c).strip():
                continue
            label = head[i] if i < len(head) else ""
            if len(cells) > 2 and label:
                kids.append({"x": [[label + ": ", 1]] + c, "k": "b", "c": []})
            else:
                kids += [{"x": x, "k": "b", "c": []} for x in split_semis(c)]
        title = [[t, f | 1] for t, f in cells[0]]
        out.append({"x": title, "k": "t", "c": kids})
    return out


def page_map(blocks):
    branches, cur, last = [], None, None

    def branch(title):
        nonlocal cur, last
        cur = {"x": title, "k": "h", "c": []}
        branches.append(cur)
        last = None

    for b in blocks:
        k = b["k"]
        if k == "h":
            t = clean(rs(b["x"]))
            t[0][0] = re.sub(r"^\s*\d+\.\s*", "", t[0][0]) if t else ""
            branch([[plain(t).strip(), 1]])
            continue
        if cur is None:
            branch([["Key facts", 1]])
        if k == "t":
            cur["c"] += table_nodes(b)
            last = None
        elif k == "x":
            r = clean(rs(b["x"]))
            if r:
                cur["c"].append({"x": r, "k": "x", "c": []})
        elif k == "s" and last is not None:
            n = bullet_node(b["x"])
            if n:
                last["c"].append(n)
        else:
            if plain(rs(b.get("x", []))).lstrip().startswith("Not in your sources"):
                continue
            n = bullet_node(b.get("x", []))
            if n:
                cur["c"].append(n)
                last = n
    return [x for x in branches if x["c"]]


def rows_arg(a):
    book, _, spec = a.partition(":")
    rows = set()
    for part in spec.split(","):
        x, _, y = part.partition("-")
        rows |= set(range(int(x), int(y or x) + 1))
    return int(book), rows


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    picks = [rows_arg(a) for a in sys.argv[3:]] or [(b, None) for b in range(1, 7)]
    for book, only in picks:
        notes = json.loads((src / f"book{book}.json").read_text())
        rev = json.loads((dst / f"rev{book}.json").read_text())
        nrows = [r for u in notes["units"] for r in u["rows"]]
        rrows = [r for u in rev["units"] for r in u["rows"]]
        pages = nodes = 0
        for ri, (n, r) in enumerate(zip(nrows, rrows)):
            if only is not None and ri not in only:
                continue
            for s_n, s_r in zip(n["secs"], r["secs"]):
                assert s_n["t"] == s_r["t"], (book, ri, s_n["t"])
                s_r["m"] = page_map(s_n["b"])
                pages += 1

                def count(xs):
                    return sum(1 + count(x["c"]) for x in xs)
                nodes += count(s_r["m"])
        (dst / f"rev{book}.json").write_text(json.dumps(rev, ensure_ascii=False, separators=(",", ":")))
        print(f"book {book}: {pages} pages mapped, {nodes} nodes")


if __name__ == "__main__":
    main()
