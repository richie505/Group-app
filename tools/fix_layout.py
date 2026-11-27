"""Mechanical layout repairs of MCQ stems/options in the apps' question banks (complete, group1, group2). Only line
breaks, scraped page noise and OCR'd code letters change – never a word of the question, an option's meaning or the key.
    python3 tools/fix_layout.py            (writes, prints counts)
Repairs:
  blank      – blank lines between a stem's lines are collapsed
  noise      – scraped paper furniture: "(Common codes for English and Telugu Versions)", "GROUP-2 - 1 Held on (dd-mm-yyyy)"
  glued-q    – the question line glued to the last item ("3. Swamp deer Which of the above ...") goes onto its own line
  glued-1st  – the first item glued to the lead-in ("... countries? I. Gabon\\nII. Somalia") goes onto its own line
  codes      – OCR'd "l" for "I" in matching codes ("a-l b-II") when the other codes are Roman numerals
"""
import collections, glob, json, re

L = r"(?:[1-8]|[a-h]|[A-H]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI{0,3})"
Q = r"(?:Which of the|Which one of|Which among|How many|Select the correct|Choose the correct|Select correct|Arrange (?:the )?(?:above|following|these)|Codes?\s*[:–-])"


def fix_stem(s, c):
    t = s
    n = re.sub(r"\n[ \t]*\n+", "\n", t)
    if n != t: c["blank"] += 1; t = n
    n = re.sub(r"\s*\(Common codes for English and Telugu Versions?\)", "", t, flags=re.I)
    n = re.sub(r"\s*GROUP-?\s*\d\s*-\s*\d\s*Held on\s*\(\d{2}-\d{2}-\d{4}\)", "", n, flags=re.I)
    if n != t: c["noise"] += 1; t = n
    # question glued to an item line
    lines = t.split("\n"); ch = False
    for i, l in enumerate(lines):
        if re.match(r"\s*\(?%s[.)]\s" % L, l):
            m = re.search(r"(\S)[ \t]+(%s)" % Q, l)
            if m and m.start(2) > 6:
                lines[i] = l[:m.start(2)].rstrip() + "\n" + l[m.start(2):]; ch = True
    if ch: c["glued-q"] += 1; t = "\n".join(lines)
    # first item glued to the lead-in, when the second item starts its own line
    m = re.search(r"([:?.–-])[ \t]+(\(?(1|a|A|i|I)[.)][ \t][^\n]*\n\s*\(?(2|b|B|ii|II)[.)]\s)", t)
    if m:
        first, second = m.group(3), m.group(4)
        pair_ok = {("1", "2"), ("a", "b"), ("A", "B"), ("i", "ii"), ("I", "II")}
        if (first, second) in pair_ok:
            t = t[:m.start(2)].rstrip() + "\n" + t[m.start(2):]; c["glued-1st"] += 1
    return t




PAIR = re.compile(r"\(?([A-Ha-h1-8])\)?\s*[-–]\s*\(?([ivxIVXl1]{1,4}|[1-8]|[A-H])\)?")
ROMAN = {"l": "I", "1": "I", "ll": "II", "Il": "II", "lI": "II", "lll": "III", "lV": "IV", "Vl": "VI"}


def fix_options(o, c):
    """matching codes with Roman List II labels: OCR'd l/1 for I, a stray letter for the one missing List I letter,
    mixed-case List I letters – rebuilt as "a-I, b-II, c-III, d-IV" only when every option is a clean code"""
    parsed = []
    for x in o:
        ms = list(PAIR.finditer(x))
        rest = PAIR.sub("", x)
        if len(ms) < 3 or re.search(r"[^\s,;.]", rest):
            return o
        parsed.append([(m.group(1), m.group(2)) for m in ms])
    rights = [r for p in parsed for _, r in p]
    if sum(1 for r in rights if re.fullmatch(r"I{1,3}|IV|VI{0,3}", r)) < len(rights) / 2:
        return o  # List II is not Roman: leave
    lefts = collections.Counter(l.lower() for p in parsed for l, _ in p)
    n = max(len(p) for p in parsed)
    want = [chr(97 + i) for i in range(n)]
    lower = sum(1 for p in parsed for l, _ in p if l.islower()) >= sum(1 for p in parsed for l, _ in p if l.isupper())
    out = []
    for p in parsed:
        ls = [l.lower() for l, _ in p]
        miss = [w for w in want if w not in ls]
        extra = [l for l in ls if l not in want]
        if len(miss) == 1 and len(extra) == 1:
            ls = [miss[0] if l == extra[0] else l for l in ls]
        rs = [ROMAN.get(r, r) for _, r in p]
        if any(not re.fullmatch(r"I{1,3}|IV|VI{0,3}|V", r) for r in rs) or len(set(rs)) < len(rs) or len(set(ls)) < len(ls):
            return o  # still ambiguous (e.g. "d-1" could be I or II): left for a hand check
        out.append(", ".join(f"{l if lower else l.upper()}-{r}" for l, r in zip(ls, rs)))
    if out != o and [re.sub(r"\s", "", x) for x in out] != [re.sub(r"\s", "", x) for x in o]:
        c["codes"] += 1
        return out
    return o


if __name__ == "__main__":
    tot = collections.Counter()
    for app in ("complete", "group1", "group2"):
        for f in sorted(glob.glob(f"app/src/{app}/assets/mcq[0-9].json")):
            m = json.load(open(f)); c = collections.Counter()
            for qs in m["rows"].values():
                for q in qs:
                    s = fix_stem(q["s"], c)
                    if s != q["s"]: q["s"] = s
                    if q.get("o"):
                        o = fix_options(q["o"], c)
                        if o != q["o"]: q["o"] = o
            if c:
                json.dump(m, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
                print(f, dict(c)); tot.update(c)
    print("total", dict(tot))
