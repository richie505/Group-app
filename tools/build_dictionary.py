#!/usr/bin/env python3
"""Offline English dictionary for the app's "Meaning" look-up, built from WordNet 3.1.

WordNet (Princeton University, WordNet 3.1 licence - free to use and redistribute) is taken from the npm
package wordnet-db (https://registry.npmjs.org/wordnet-db/-/wordnet-db-3.1.14.tgz), dict/ folder.

For every word or phrase: its most common senses (up to 4), each "pos|definition|example": the part of speech
used most in WordNet's tagged texts first, then WordNet's frequency order.

Usage: python3 tools/build_dictionary.py <wordnet-db>/dict app/src/main/assets
Writes <assets>/dict/<letter>.tsv (a-z, "_" for the rest), sorted, one line per word:
"word<TAB>sense<TAB>sense...", so the app loads only the letter it needs.
"""
import re
import sys
from pathlib import Path

POS = {"noun": "n", "verb": "v", "adj": "adj", "adv": "adv"}
MAX_SENSES = 4


def synsets(dict_dir, pos):
    """offset -> (definition, first example)."""
    out = {}
    for line in (dict_dir / f"data.{pos}").read_text(encoding="latin-1").splitlines():
        if line.startswith(" ") or "|" not in line:
            continue
        head, gloss = line.split("|", 1)
        parts = [p.strip() for p in gloss.split(";")]
        definition = "; ".join(p for p in parts if not p.startswith('"')).strip()
        examples = [p.strip('" ') for p in parts if p.startswith('"')]
        out[head.split()[0]] = (definition, examples[0] if examples else "")
    return out


def main():
    dict_dir, assets = Path(sys.argv[1]), Path(sys.argv[2])
    words = {}
    for pos, tag in POS.items():
        data = synsets(dict_dir, pos)
        for line in (dict_dir / f"index.{pos}").read_text(encoding="latin-1").splitlines():
            if line.startswith(" "):
                continue
            f = line.split()
            lemma, n_synsets, n_ptr = f[0], int(f[2]), int(f[3])
            # how often this word is used as this part of speech in WordNet's tagged texts
            tagged = int(f[4 + n_ptr + 1])
            offsets = f[4 + n_ptr + 2:][:n_synsets]
            for rank, off in enumerate(offsets):
                if off in data:
                    d, ex = data[off]
                    words.setdefault(lemma, []).append((tag, d, ex, tagged, rank))
    lines = []
    for lemma in sorted(words):
        # the most used part of speech first (federal: the adjective, not the Civil War soldier),
        # each in WordNet's frequency order
        ranked = sorted(words[lemma], key=lambda x: (-x[3], x[0], x[4]))
        senses = []
        seen = set()
        for tag, d, ex, _, _ in ranked:
            if d in seen:
                continue
            seen.add(d)
            senses.append(f"{tag}|{d}|{ex}".replace("\t", " "))
        senses = senses[:MAX_SENSES]
        lines.append(lemma.replace("_", " ") + "\t" + "\t".join(senses))
    out = assets / "dict"
    out.mkdir(exist_ok=True)
    groups = {}
    for line in lines:
        c = line[0].lower()
        groups.setdefault(c if "a" <= c <= "z" else "_", []).append(line)
    for c, ls in groups.items():
        # sorted by the exact key the app searches with (lower case)
        ls.sort(key=lambda l: l.split("\t", 1)[0].lower())
        (out / f"{c}.tsv").write_text("\n".join(ls) + "\n", encoding="utf-8")
    size = sum(f.stat().st_size for f in out.glob("*.tsv"))
    print(f"{len(lines)} words in {len(groups)} files, {size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
