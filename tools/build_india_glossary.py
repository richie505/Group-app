#!/usr/bin/env python3
"""Indian-context meanings for the Meaning card: the glossary (tools/data/india_glossary.tsv) and the
definitions the notes themselves give ("Absolute humidity: actual water vapour per unit volume of air").

A notes line counts as a definition when it starts with a short term followed by ":", "=", "means" or
"refers to". Terms with years or exam codes, and heading-like labels ("Exam angle", "Founder") are left out;
a single everyday word (penalty, exception) only counts when it is technical - not in the dictionary, or
with few dictionary senses - so selecting a common word does not bring up an unrelated fact.

Usage: python3 tools/build_india_glossary.py app/src/main/assets   (after tools/build_dictionary.py)
Writes <assets>/india.json: {"g": {term: meaning}, "n": {term: [[definition, "Book · Section"], ...]}}
"""
import json
import re
import sys
from pathlib import Path

LABELS = re.compile(r"^(exam angle|current relevance|ap angle|note|notes|criticism|sources?|example|examples|answer|first|last|"
                    r"latest|data|trap|traps|rule|key|why|how|then|now|also|but|size|period|author|work|theme|founder|mandate|"
                    r"members?|chair|chairperson|year|date|place|location|capital|headquarters|hq|status|result|outcome|ruler|"
                    r"dynasty|significance|features?|aim|aims|objective|objectives|function|functions|type|types|composition|"
                    r"tenure|removal|appointment|powers?|eligibility|exception|exceptions|penalty|protection|drivers|alliances|"
                    r"criticism and debates|debate|debates|context|background|impact|effects?|causes?|reasons?|issues?|"
                    r"challenges?|example|q|a|i|ii|iii|iv|v)$")
CODES = re.compile(r"\b(APPSC|UPSC|UPPSC|BPSC|MPPSC|RPSC|JPSC|TNPSC|PYQ|ES|SES|IYB|LENS|TH|CDI|APP|CDX|GK|key)\b")


def senses(assets):
    """word -> number of dictionary senses (from assets/dict)."""
    out = {}
    for f in (assets / "dict").glob("*.tsv"):
        for line in f.read_text(encoding="utf-8").splitlines():
            w, *s = line.split("\t")
            out[w.lower()] = len(s)
    return out


def forms(w):
    """The word and its likely dictionary forms."""
    out = {w}
    for suf, rep in (("iest", "y"), ("ies", "y"), ("est", ""), ("er", ""), ("es", ""), ("s", ""), ("ed", ""), ("ing", ""), ("ed", "e"), ("ing", "e")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            stem = w[: len(w) - len(suf)]
            out.add(stem + rep)
            if len(stem) > 2 and stem[-1] == stem[-2]:  # hottest -> hot
                out.add(stem[:-1])
    return out


def main():
    assets = Path(sys.argv[1])
    here = Path(__file__).parent
    glossary = {}
    for line in (here / "data" / "india_glossary.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        terms, meaning = line.split("\t", 1)
        for t in terms.split("|"):
            glossary[t.strip().lower()] = meaning.strip()

    dict_senses = senses(assets)
    notes = {}
    index = json.loads((assets / "index.json").read_text())["books"]
    for b in range(1, 7):
        book = json.loads((assets / f"book{b}.json").read_text())
        rows = [r for u in book["units"] for r in u["rows"]]
        for r in rows:
            where = f"{index[b - 1]['short']} · {r['title']}"
            for s in r["secs"]:
                for blk in s["b"]:
                    if blk["k"] == "t":
                        continue
                    runs = blk["x"] if isinstance(blk["x"], list) else [[blk["x"], 0]]
                    text = "".join(t for t, _ in runs)
                    m = re.match(r"^\s*([A-Z][\w'’\- ]{1,40}?)\s*(?:\(([^)]{1,40})\))?\s*(=|:| means | refers to | is defined as )\s*(.{12,260}?)(?:\.\s|;\s|$)", text)
                    if not m:
                        continue
                    term = m.group(1).strip()
                    key = term.lower()
                    words = key.split()
                    if len(words) > 4 or LABELS.match(key) or re.search(r"\d", term) or CODES.search(term):
                        continue
                    if words[0] in ("the", "not", "a", "an", "past", "origin", "sources", "source", "order", "functions",
                                    "primary", "main", "other", "some", "most", "first", "last", "latest", "current"):
                        continue
                    # a single word must be technical: not an everyday word or a form of one (hottest, ports)
                    if len(words) == 1 and any(dict_senses.get(f, 0) > 2 for f in forms(key)):
                        continue
                    definition = re.sub(r"\s*\[[^\]]*\]", "", m.group(4)).strip(" .;,")
                    if len(definition) < 12:
                        continue
                    entry = notes.setdefault(key, [])
                    if len(entry) < 2 and all(definition != d for d, _ in entry):
                        entry.append([definition, where])
                    # "Absolute humidity (AH): ..." - the short form too
                    if m.group(2) and re.fullmatch(r"[A-Z]{2,8}", m.group(2)):
                        notes.setdefault(m.group(2).lower(), [[definition, where]])

    (assets / "india.json").write_text(json.dumps({"g": glossary, "n": notes}, ensure_ascii=False, separators=(",", ":")))
    print(f"glossary {len(glossary)} terms, notes definitions {len(notes)} terms")


if __name__ == "__main__":
    main()
