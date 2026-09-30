#!/usr/bin/env python3
"""Build the app's MCQ files from the MCQ app's notes MCQs (the app's only question bank).

The MCQ app (github.com/richie505/groupsmcq) writes APPSC-style MCQs from the same six notes books,
one file per notes section chunk: tools/generated/b{book}/r{row}-c{chunk}.json, each with
"accepted": [{s, o, a, x, ty, tq, sec}]. Its notes files are identical to this app's, so a question's
book/row is this app's Section and "sec" names the Subsection.

The previous-year questions (PYQs) moved to the MCQ app; tools/build_mcq.py still builds them from the
PYQ Bank but its output is no longer shipped here.

Usage: python3 tools/build_notes_mcq.py <groupsmcq>/tools/generated app/src/main/assets
Writes <assets>/mcq1.json .. mcq6.json ({rows, units, subs}) and each row's question count ("q") in
index.json.
"""
import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

TAG_RE = re.compile(r"\s*\[[^\]]*\]\s*$")  # "Title  [APPSC, GROUP-II]" -> "Title"


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def qid(stem, options):
    # "n" prefix keeps notes-MCQ ids apart from PYQ ids in the saved answers
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


def match_sub(name, titles):
    """Index of the subsection named `name` in this row, or -1 (section level)."""
    if not name:
        return -1
    name = TAG_RE.sub("", name)
    keys = [norm(t) for t in titles]
    n = norm(name)
    if n in keys:
        return keys.index(n)
    best = difflib.get_close_matches(n, keys, n=1, cutoff=0.85)
    return keys.index(best[0]) if best else -1


def main():
    src, assets = Path(sys.argv[1]), Path(sys.argv[2])
    stats = Counter()
    counts = {}
    for b in range(1, 7):
        book = json.loads((assets / f"book{b}.json").read_text())
        rows_src = [r for u in book["units"] for r in u["rows"]]
        per_row = {}
        seen = set()
        files = sorted(src.glob(f"b{b}/r*-c*.json"),
                       key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.stem)))
        for f in files:
            d = json.loads(f.read_text())
            ri = d["row"]
            row = rows_src[ri]
            if TAG_RE.sub("", d["section"]) != row["title"]:
                sys.exit(f"{f}: section '{d['section']}' is not book {b} row {ri} '{row['title']}'")
            titles = [s["t"] for s in row["secs"]]
            for q in d["accepted"]:
                i = qid(q["s"], q["o"])
                if i in seen:
                    stats["duplicate"] += 1
                    continue
                seen.add(i)
                sub = match_sub(q.get("sec"), titles)
                stats["subsection" if sub >= 0 else "section only"] += 1
                out = {"id": i, "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"]}
                if q.get("tq"):
                    out["tq"] = q["tq"]
                per_row.setdefault(ri, []).append((sub, out))
        rows = {str(r): [q for _, q in qs] for r, qs in sorted(per_row.items())}
        subs = {str(r): [s for s, _ in qs] for r, qs in sorted(per_row.items())}
        (assets / f"mcq{b}.json").write_text(
            json.dumps({"rows": rows, "units": {}, "subs": subs}, ensure_ascii=False, separators=(",", ":")))
        counts[b] = {r: len(qs) for r, qs in per_row.items()}
        print(f"mcq{b}: rows={len(rows)} questions={sum(len(v) for v in rows.values())}")
    print(dict(stats))

    index_path = assets / "index.json"
    index = json.loads(index_path.read_text())
    for b in index["books"]:
        for ri, r in enumerate(b["rows"]):
            r["q"] = counts.get(b["id"], {}).get(ri, 0)
        b["uq"] = {}
    index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
