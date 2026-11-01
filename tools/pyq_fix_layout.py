"""Puts PYQ lists on lines of their own where the source ran them into one line: "(i) ... (ii) ...",
"List-II i. ... ii. ...", "A. ... B. ...". A marker that only names an item in the sentence ("statements (A)
and (B) and choose") is left in place. Only PYQs (ids "y...") whose stem has such a run are touched.

    python3 tools/pyq_fix_layout.py
"""
import json, re

SETS = [["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], ["I", "II", "III", "IV", "V", "VI"],
        ["a", "b", "c", "d", "e", "f"], ["A", "B", "C", "D", "E", "F"], ["1", "2", "3", "4", "5", "6", "7"]]
ITEM = r"\(?(?:[1-7]|[a-fA-F]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI?)\s*[.)\-–]"
# a List / Column heading starts a line only when its items follow it ("List-B (Chairman) (a) ..."), so
# "Match List-A (Name) with List-B (Chairman) and select" stays one sentence
HEAD = re.compile(r"\s+((?:List|Column)\s*[-–]?\s*(?:I{1,2}|[AB12])\b(?:\s*\([^)]{0,60}\))?\s*[:.-]?(?=\s*" + ITEM + r")|"
                  r"Codes?\s*[:-]|Reason\s*\(R\)\s*:|Assertion\s*\(A\)\s*:|Statement\s*[-–]?\s*(?:I{1,2}|[12])\s*:|"
                  r"(?:Select|Choose|Find|Mark) the correct|Which of the (?:above|statements given above)|"
                  r"How many of the above|Inferences?\s*:|Conclusions?\s*:|Assumptions?\s*:)")


def mark_re(m):
    # "(ii)", "ii.", "ii)" before a word; not "(ii) and", "ii, iii" (a reference to the item)
    # not "B.C." / "A.D." (an abbreviation, not item B)
    return re.compile(rf"(?<![\w(])\(?{re.escape(m)}(?:[.)]|\s?[-–](?=\s))(?![A-Z]\.)\s*(?!\s*(?:and|or|&|,|only)\b)(?=\S)")


def runs(line):
    """Places (index) in the line where a list item starts: the markers of one set found in order."""
    cuts = set()
    for ms in SETS:
        pos, found = 0, []
        for m in ms:
            hit = None
            for x in mark_re(m).finditer(line, pos):
                if x.start() > 0 and not line[x.start() - 1].isspace():
                    continue
                hit = x
                break
            if not hit:
                break
            found.append(hit.start())
            pos = hit.end()
        if len(found) >= 2:
            cuts.update(p for p in found if p > 0)
    return cuts


def relayout(s):
    flat = re.sub(r"[ \t]*\n[ \t]*", " ", s).strip()
    # a heading right after an item's own marker ("1. Statement I:") stays with it
    flat = HEAD.sub(lambda x: x.group(0) if re.search(r"(?:^|\s)\(?\w{1,3}[.)]$", flat[:x.start()]) else "\n" + x.group(1), flat)
    out = []
    for line in flat.split("\n"):
        cuts = sorted(runs(line))
        prev = 0
        for c in cuts:
            out.append(line[prev:c].strip())
            prev = c
        out.append(line[prev:].strip())
    out = regroup([x for x in out if x])
    # a "Codes:" left hanging at the end (the codes are the options)
    while out and re.fullmatch(r"(?i)codes?\s*[:.\-–]?", out[-1]):
        out.pop()
    return "\n".join(out)


LETTER = re.compile(r"^\(?[A-Fa-f][.)]\s")
OTHER = re.compile(r"^\(?(?:[1-7]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI?)\s*[.)\-–]\s")


def regroup(lines):
    """A match table copied row by row ("A. x", "1. y", "B. z", "2. w"): List I's items, then List II's."""
    i = 0
    while i < len(lines):
        j = i
        while j + 1 < len(lines) and LETTER.match(lines[j]) and OTHER.match(lines[j + 1]):
            j += 2
        if j - i >= 6:  # three or more rows
            block = lines[i:j]
            rest = lines[j:]
            # a trailing List II item with no List I partner (5 items against 4)
            extra = []
            while rest and OTHER.match(rest[0]):
                extra.append(rest.pop(0))
            lines = lines[:i] + block[0::2] + block[1::2] + extra + rest
            # the List II heading that sat above the rows goes above its items
            for k in range(i - 1, max(-1, i - 3), -1):
                if re.match(r"(?i)(?:list|column)\s*[-–]?\s*(?:II|B|2)\b", lines[k]) and k + 1 < len(lines):
                    head = lines.pop(k)
                    first2 = next(n for n in range(k, len(lines)) if OTHER.match(lines[n]))
                    lines.insert(first2, head)
                    break
            i = j
        i += 1
    return lines


def needs(s):
    return any(len(runs(l)) >= 1 for l in s.split("\n")) or relayout(s) != s and bool(HEAD.search(s.replace("\n", " ")))


# read by hand: a scan leftover in the text, a key the book printed wrong (its key gave only the letter, unverified)
HAND = {
    "yd112107da2b": {"drop": " He of", "a": 0, "x": "Separate electorates for Muslims came with the Indian Councils Act, 1909; "
                     "dyarchy in the provinces with the Government of India Act, 1919; federation with the Government of India "
                     "Act, 1935; and discussion of the annual financial statement (budget) with the Indian Councils Act, 1892."},
}


def main():
    for app in ("main", "complete"):
        n = 0
        for b in range(1, 7):
            p = f"app/src/{app}/assets/mcq{b}.json"
            m = json.load(open(p))
            for qs in m["rows"].values():
                for q in qs:
                    h = HAND.get(q["id"])
                    if h:
                        q["s"] = q["s"].replace(h["drop"], "")
                        q["a"] = h["a"]
                        q["x"] = h["x"]
                    if q["id"].startswith("y") and needs(q["s"]):
                        new = relayout(q["s"])
                        if new != q["s"]:
                            q["s"] = new
                            n += 1
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        print(app, "PYQ stems laid out:", n)


if __name__ == "__main__":
    main()
