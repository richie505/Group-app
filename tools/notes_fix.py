"""Exact, checked edits to the notes (for fixing contradictions and gaps).

    python3 tools/notes_fix.py show <book> <row> [sec]      print a topic's notes (markdown form) with block numbers
    python3 tools/notes_fix.py apply <ops.json> [--dry]      apply edits; --dry only checks them

ops.json is a list of edits:
    {"book": 2, "row": 134, "sec": 8, "find": "Section 4A", "replace": "Section 18A"}
        replace text inside one block; "find" must occur exactly once in that subsection and lie
        within one formatting run (bold/plain), else the edit is refused
    {"book": 2, "row": 4, "sec": 1, "after": "anchor text", "md": "- **Objectives Resolution:** moved by **Nehru** ..."}
        insert new block(s) (markdown form of tools/structured_md.py) after the block containing "anchor text"
    {"book": 2, "row": 4, "sec": 1, "append": true, "md": "..."}  add block(s) at the end of the subsection
    {"book": 2, "row": 4, "sec": 1, "block": "anchor text", "md": "..."}
        replace the one block containing "anchor text" (a bullet, a gap line or a whole table) with the md
        (any number of blocks; "" deletes it)
MCQs keyed to a corrected fact are listed in work/notefix/mcq_fixes.jsonl (applied by tools/mcq_trim_import.py):
    {"book": 2, "id": "n1234abcd567", "find": "...", "replace": "..."}   or   {"book": 2, "id": "...", "drop": true}
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks, to_blocks


def rows_of(d):
    return [r for u in d["units"] for r in u["rows"]]


def text(b):
    if b["k"] == "t":
        cells = [c for row in [b["h"]] + b["r"] for c in row]
        return " | ".join("".join(r[0] for r in (c if isinstance(c, list) else [[c, 0]])) for c in cells)
    x = b["x"]
    return "".join(r[0] for r in x) if isinstance(x, list) else x


def runs_of(b):
    """Every list of runs in a block (a text block's x, or each table cell)."""
    if b["k"] == "t":
        for row in [b["h"]] + b["r"]:  # plain-string cells become one plain run so they can be edited too
            for i, c in enumerate(row):
                if isinstance(c, str):
                    row[i] = [[c, 0]]
        return [c for row in [b["h"]] + b["r"] for c in row]
    return [b["x"]] if isinstance(b["x"], list) else []


def plain_cells(b):
    """Table cells parsed from markdown come back as runs; keep one plain run as a string, as stored."""
    if b["k"] == "t":
        for row in [b["h"]] + b["r"]:
            for i, c in enumerate(row):
                if isinstance(c, list) and len(c) == 1 and c[0][1] == 0:
                    row[i] = c[0][0]
    return b


def show(book, row, sec=None):
    d = json.load(open(f"app/src/main/assets/book{book}.json"))
    r = rows_of(d)[row]
    print(f"=== {book}:{row} | {r['title']}")
    for si, s in enumerate(r["secs"]):
        if sec is not None and si != sec:
            continue
        print(f"## SUB {si} | {s['t']}")
        for bi, b in enumerate(s["b"]):
            md, _ = from_blocks([b], inline_tables=True)
            print(f"[{bi}] {md}")


def apply(path, dry):
    ops = json.load(open(path))
    books, errors, done = {}, [], 0
    for n, op in enumerate(ops):
        b = op["book"]
        d = books.setdefault(b, json.load(open(f"app/src/main/assets/book{b}.json")))
        try:
            s = rows_of(d)[op["row"]]["secs"][op["sec"]]
        except (IndexError, KeyError):
            errors.append(f"op {n}: no such row/sec {op.get('row')}.{op.get('sec')}")
            continue
        if "find" in op:
            plain = {(bi, ri, ci) for bi, blk in enumerate(s["b"]) if blk["k"] == "t"
                     for ri, row in enumerate([blk["h"]] + blk["r"]) for ci, c in enumerate(row) if isinstance(c, str)}
            hits = [(bi, rl, ri) for bi, blk in enumerate(s["b"]) for rl in runs_of(blk) for ri, run in enumerate(rl) if op["find"] in run[0]]
            whole = sum(text(blk).count(op["find"]) for blk in s["b"])
            if whole == 1 and len(hits) == 1:
                _, rl, ri = hits[0]
                rl[ri][0] = rl[ri][0].replace(op["find"], op["replace"])
            for bi, r_, ci in plain:  # cells that were plain strings stay plain strings
                blk = s["b"][bi]
                row = blk["h"] if r_ == 0 else blk["r"][r_ - 1]
                row[ci] = row[ci][0][0]
            if whole != 1:
                errors.append(f"op {n}: '{op['find']}' found {whole} times in {b}:{op['row']}.{op['sec']} (need exactly 1)")
                continue
            if len(hits) != 1:
                errors.append(f"op {n}: '{op['find']}' spans formatting runs; use a shorter find inside one run")
                continue
        elif "md" in op:
            new = [plain_cells(x) for x in to_blocks(op["md"], [])] if op["md"].strip() else []
            if "block" in op:
                at = [bi for bi, blk in enumerate(s["b"]) if op["block"] in text(blk)]
                if len(at) != 1:
                    errors.append(f"op {n}: block '{op['block']}' found in {len(at)} blocks (need 1)")
                    continue
                s["b"][at[0]:at[0] + 1] = new
            elif op.get("append"):
                s["b"].extend(new)
            else:
                at = [bi for bi, blk in enumerate(s["b"]) if op["after"] in text(blk)]
                if len(at) != 1:
                    errors.append(f"op {n}: anchor '{op['after']}' found in {len(at)} blocks (need 1)")
                    continue
                s["b"][at[0] + 1:at[0] + 1] = new
        else:
            errors.append(f"op {n}: needs find/replace or md")
            continue
        done += 1
    for e in errors:
        print(e)
    print(f"{done}/{len(ops)} edits ok" + (" (dry run)" if dry else ""))
    if not dry and not errors:
        for b, d in books.items():
            open(f"app/src/main/assets/book{b}.json", "w").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    return not errors


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        sys.exit(0 if apply(sys.argv[2], "--dry" in sys.argv) else 1)
