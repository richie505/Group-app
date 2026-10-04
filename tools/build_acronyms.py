#!/usr/bin/env python3
"""Build assets/acronyms.json from tools/data/acronyms.tsv: what each short form in the notes stands for.

The list was checked against how the notes use each of the 2,247 short forms that appear 3+ times (the
rest are nearly always defined right where they are used). A short form with several meanings lists each
with the words that pick it (CWC: Child Welfare Committee on a page about juveniles and adoption, Central
Water Commission on one about rivers and dams, Congress Working Committee in history); "-" means say it
as it is (names, labels, words in capitals such as FIRST).

Usage: python3 tools/build_acronyms.py app/src/main/assets
Writes {"CWC": [["Child Welfare Committee", ["child", ...]], ...], ...}; the app picks a meaning in
data/SpeechText.kt (meaning).
"""
import json
import sys
from pathlib import Path


def main():
    assets = Path(sys.argv[1])
    out = {}
    for line in (Path(__file__).parent / "data" / "acronyms.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        acr, meaning = parts[0], parts[1]
        words = [w.strip() for w in parts[2].split(",") if w.strip()] if len(parts) > 2 else []
        out.setdefault(acr, []).append([meaning, words])
    (assets / "acronyms.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    many = sum(1 for v in out.values() if len(v) > 1)
    print(f"{len(out)} short forms ({many} with more than one meaning)")


if __name__ == "__main__":
    main()
