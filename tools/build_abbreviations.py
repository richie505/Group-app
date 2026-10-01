#!/usr/bin/env python3
"""Collect the short forms the notes define, for read-aloud: "Fiscal Deficit (FD)" and "CR (Critically Endangered)".

A definition counts when the capitals of the short form are the initials of the words next to it (small
words like "of", "and", "the" may be skipped; a word may give 2-3 letters, as in "Socio-Economic"). Each short
form keeps its most common meaning; a second meaning that the notes also use often is kept too, so the app
can choose between them from the words around (SC: Supreme Court or Scheduled Caste).

Usage: python3 tools/build_abbreviations.py app/src/main/assets
Writes <assets>/abbr.json: {"FD": ["Fiscal Deficit"], "SC": ["Supreme Court", "Scheduled Caste"], ...}
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SMALL = {"of", "and", "the", "for", "in", "on", "to", "&", "a", "an", "at", "by", "with"}
ACR = r"[A-Z][A-Z&]{1,9}s?"  # capitals, an optional plural s: FD, VCIC, PTGs


def letters(acr):
    return [c for c in acr if c.isupper() or c == "&"]


def match(words, acr):
    """Smallest run of words ending at the last word whose initials spell the short form."""
    target = [c for c in letters(acr) if c != "&"]
    if len(target) < 2:
        return None
    for start in range(len(words) - 1, max(-1, len(words) - len(target) - 6), -1):
        run = words[start:]
        if run[0].lower() in SMALL:
            continue
        if spell(run, target):
            return " ".join(run)
    return None


def spell(run, target):
    """Can the words, in order, give exactly the target letters (1-3 letters per word, small words optional)?"""
    def go(i, j):
        if j == len(target):
            return i == len(run)
        if i == len(run):
            return False
        w = run[i]
        if w.lower() in SMALL and go(i + 1, j):
            return True
        parts = [p for p in re.split(r"[-/]", w) if p]
        # whole word: first letter, optionally more capitals inside (e.g. "NITI", "MGNREGA" parts)
        k = j
        for p in parts:
            if k < len(target) and p[0].upper() == target[k]:
                k += 1
            else:
                break
        if k > j and go(i + 1, k):
            return True
        return False
    return go(0, 0)


def texts(assets):
    for b in range(1, 7):
        book = json.loads((assets / f"book{b}.json").read_text())
        for u in book["units"]:
            yield u["title"]
            for r in u["rows"]:
                yield r["title"]
                for s in r["secs"]:
                    yield s["t"]
                    for blk in s["b"]:
                        cells = [c for row in [blk["h"]] + blk["r"] for c in row] if blk["k"] == "t" else [blk["x"]]
                        for c in cells:
                            yield "".join(x[0] for x in c) if isinstance(c, list) else c


def main():
    assets = Path(sys.argv[1])
    found = defaultdict(Counter)
    for t in texts(assets):
        # "Full Words (ABBR)"
        for m in re.finditer(rf"((?:[\w'’&/-]+\s+){{1,10}}[\w'’&/-]+)\s*\(({ACR})\)", t):
            words = re.findall(r"[\w'’&/-]+", m.group(1))
            full = match(words, m.group(2))
            if full:
                found[m.group(2)][full] += 1
        # "ABBR (Full Words)"
        for m in re.finditer(rf"\b({ACR})\s*\(([A-Za-z][\w'’&/ -]{{3,80}})\)", t):
            words = re.findall(r"[\w'’&/-]+", m.group(2))
            if len(words) >= 2 and spell(words, [c for c in letters(m.group(1)) if c != "&"]):
                found[m.group(1)][" ".join(words)] += 1
    out = {}
    for acr, c in sorted(found.items()):
        # one meaning per spelling, ignoring case and hyphens
        merged = Counter()
        label = {}
        for full, n in c.most_common():
            k = re.sub(r"[\s-]+", " ", full.lower())
            merged[k] += n
            label.setdefault(k, full)
        best = merged.most_common()
        keep = [label[best[0][0]]]
        if len(best) > 1 and best[1][1] >= max(2, best[0][1] // 4):
            keep.append(label[best[1][0]])
        out[acr] = keep
    (assets / "abbr.json").write_text(json.dumps(out, ensure_ascii=False, indent=0, sort_keys=True))
    two = {k: v for k, v in out.items() if len(v) > 1}
    print(f"{len(out)} short forms defined in the notes; {len(two)} with two meanings")
    for k in ("SC", "ST", "FD", "WTO", "CR", "MP", "RE", "CDM", "PSP", "NH", "DM", "PR", "VCIC", "FAE"):
        print(f"  {k}: {out.get(k)}")
    print("two meanings:", list(two.items())[:30])


if __name__ == "__main__":
    main()
