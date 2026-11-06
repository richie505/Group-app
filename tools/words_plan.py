"""APPSC Reader's simple dictionary, step 1: the harder English words of the full notes (APPSC Complete's
book*.json), each in its dictionary form, with a line of the notes that uses it; written as packets for the
writers (data/words/in/<n>.md, rules in data/words/INSTRUCTIONS.md).

A word is kept when the notes write it in small letters (names of people and places are left out), it is in the
general dictionary (assets/dict) and it is not an everyday word (wordfreq Zipf below LIMIT).

    <venv with wordfreq>/python tools/words_plan.py
"""
import collections
import json
import os
import re

from wordfreq import zipf_frequency

A = "app/src/complete/assets"
LIMIT = 4.4
PER = 300
dict_words = set()
for f in os.listdir("app/src/main/assets/dict"):
    for line in open(f"app/src/main/assets/dict/{f}"):
        dict_words.add(line.split("\t", 1)[0].lower())


def base(w):
    """the dictionary form of w, or None"""
    cands = [w]
    if w.endswith("ies"): cands.append(w[:-3] + "y")
    if w.endswith("es"): cands += [w[:-1], w[:-2]]
    if w.endswith("s") and not w.endswith("ss"): cands.append(w[:-1])
    for s in ("ed", "ing", "er", "est"):
        if w.endswith(s):
            st = w[:-len(s)]
            cands += [st, st + "e"] + ([st[:-1] + "y"] if st.endswith("i") else []) + \
                     ([st[:-1]] if len(st) > 2 and st[-1] == st[-2] else [])
    if w.endswith("ly"): cands.append(w[:-2])
    # the shortest form in the dictionary that is still the same word ("accords" -> "accord")
    for c in cands:
        if c in dict_words and c != w and len(c) >= 4:
            return c
    return w if w in dict_words else None


def text(rs):
    return "".join(r[0] for r in rs)


def lines():
    for b in range(1, 7):
        for u in json.load(open(f"{A}/book{b}.json"))["units"]:
            for r in u["rows"]:
                for s in r["secs"]:
                    for x in s["b"]:
                        if x.get("k") == "t":
                            for row in [x.get("h", [])] + x.get("r", []):
                                for cell in row:
                                    yield text(cell)
                        elif "x" in x:
                            yield text(x["x"])


count = collections.Counter()
example = {}
for t in lines():
    for m in re.finditer(r"(?<![\w-])([a-z][a-z]{3,})(?![\w-])", t):
        w = m.group(1)
        b = base(w)
        if not b or zipf_frequency(b, "en") >= LIMIT or zipf_frequency(w, "en") >= LIMIT + 0.4:
            continue
        count[b] += 1
        if b not in example or len(t) < len(example[b]):
            if 20 <= len(t) <= 160:
                example[b] = t
words = sorted(count, key=lambda w: (-count[w], w))
os.makedirs("data/words/in", exist_ok=True)
for n in range(0, len(words), PER):
    with open(f"data/words/in/{n // PER}.md", "w") as f:
        for w in words[n:n + PER]:
            f.write(f"{w} | {example.get(w, '').replace('|', '/')}\n")
print(len(words), "words,", (len(words) + PER - 1) // PER, "packets; top:", words[:30])
