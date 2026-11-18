"""Lays out MCQ stems like a printed paper (every MCQ of an app):
- a line broken in the middle of a sentence ("Match the following\\nList-I with\\nList-II", "the other as\\nReason (R)")
  is joined back;
- statements / items run together on one line ("I. ... II. ... III. ...", "(a) ... (b) ...", "1. ... 2. ...") go one per
  line;
- a match question whose two lists were printed row by row ("A. Summer Solstice 1. 21st June B. Winter ...") is put back
  as List I (its items) then List II (its items).
Only the layout changes, never the words. Idempotent.

    python3 tools/mcq_layout.py [assets dir=app/src/complete/assets]   (python3 tools/mcq_layout.py --test)
"""
import json, re, sys

JOIN_END = re.compile(r"\b(match|with|as|and|the|of|is|are|labelled|labeled|one|other|from|to|in|following|between|that)\s*$", re.I)
FAMILIES = [
    ("roman", r"(?:I{1,3}|IV|V|VI)[.)]"),
    ("proman", r"\((?:i{1,3}|iv|v|vi)\)"),
    ("paren_a", r"\([a-f]\)"),
    ("paren_A", r"\([A-F]\)"),
    ("paren_1", r"\([1-6]\)"),
    ("dot_a", r"[a-f][.)]"),
    ("dot_A", r"[A-F][.)]"),
    ("dot_1", r"[1-6][.)]"),
    ("roman_l", r"(?:i{1,3}|iv|v|vi)[.)]"),
]
NOT_LIST = re.compile(r"\((A|R)\)")  # Assertion (A) / Reason (R) are not a list


def marks(line, pat):
    """positions of inline markers of one family preceded by a space (not at the line start)"""
    return [m.start() + 1 for m in re.finditer(r"(?<=\S) (" + pat + r") (?=\S)", line)]


def split_inline(line):
    for name, pat in FAMILIES:
        if name == "paren_A" and NOT_LIST.search(line) and not re.search(r"\(C\)", line):
            continue
        pos = marks(line, pat)
        # at least two items, and the first two in order (a then b, I then II, 1 then 2)
        items = [re.match(pat, line[p:]).group(0) for p in pos]
        if len(pos) >= 2 and ordered(items):
            out, last = [], 0
            for p in pos:
                out.append(line[last:p].rstrip())
                last = p
            out.append(line[last:])
            return [x for x in out if x.strip()]
    return [line]


ORDER = {k: i for i, k in enumerate(["i", "ii", "iii", "iv", "v", "vi"])}


def key(tok):
    t = tok.strip("().").lower()
    if t in ORDER:
        return ORDER[t]
    if t.isdigit():
        return int(t) - 1
    if len(t) == 1 and t.isalpha():
        return ord(t) - 97
    return None


def ordered(items):
    ks = [key(x) for x in items]
    return None not in ks and ks[:2] == [ks[0], ks[0] + 1]


def join_broken(lines):
    out = []
    for ln in lines:
        if out and JOIN_END.search(out[-1]) and ln.strip() and not re.match(r"\s*(\(?[a-fA-F1-6ivxIVX]{1,3}[.)]|\d+[.)])\s", ln):
            out[-1] = out[-1].rstrip() + " " + ln.strip()
        else:
            out.append(ln)
    return out


ITEM = re.compile(r"^\s*(\(?([A-Fa-f]|[1-6]|I{1,3}|IV|V|i{1,3}|iv|v)[.)]\)?)\s+(.*)$")


def fam(tok):
    t = tok.strip("().")
    if t.isdigit():
        return "num"
    if re.fullmatch(r"I{1,3}|IV|V|i{1,3}|iv|v", t):
        return "rom"
    return "let"


def unzip_lists(lines):
    """List I / List II printed row by row: item lines alternate between two families -> each list in turn"""
    idx = [i for i, l in enumerate(lines) if ITEM.match(l)]
    if len(idx) < 6:
        return lines
    fams = [fam(ITEM.match(lines[i]).group(1)) for i in idx]
    if len(set(fams)) != 2 or any(fams[j] == fams[j + 1] for j in range(len(fams) - 1)):
        return lines
    if idx != list(range(idx[0], idx[0] + len(idx))):
        return lines
    a = [lines[i] for i, f in zip(idx, fams) if f == fams[0]]
    b = [lines[i] for i, f in zip(idx, fams) if f == fams[1]]
    head = lines[:idx[0]]
    tail = lines[idx[-1] + 1:]
    # "List II (Date)" left at the end of the head moves before the second list
    l2 = []
    if head and re.match(r"\s*List[- ]?II\b", head[-1], re.I) and len(head) >= 2 and re.match(r"\s*List[- ]?I\b(?!I)", head[-2], re.I):
        l2 = [head.pop()]
    return head + a + l2 + b + tail


def rows_to_lists(s):
    """A match question printed row by row across lines: List I letters (A. B. C. D.) and List II numbers
    (1. 2. 3. 4.) interleaved -> each item on its own line (unzip_lists then puts each list together)"""
    if not re.search(r"List[- ]?I", s, re.I):
        return s
    let = [m.start() for m in re.finditer(r"(?:(?<=\s)|^)[A-D]\. (?=\S)", s)]
    num = [m.start() for m in re.finditer(r"(?:(?<=\s)|^)[1-4]\. (?=\S)", s)]
    if len(let) < 3 or len(num) < 3:
        return s
    pos = sorted(set(let + num))
    marks_ = ["L" if p in let else "N" for p in pos]
    if any(marks_[i] == marks_[i + 1] for i in range(len(marks_) - 1)):
        return s  # already a list after a list, or not alternating
    head = s[:pos[0]].rstrip()
    parts = [s[p:q].strip() for p, q in zip(pos, pos[1:] + [len(s)])]
    tail = ""
    # a closing line after the last item ("Codes A B C D", "Select the correct answer...") stays at the end
    last = parts[-1].split("\n", 1)
    if len(last) == 2:
        parts[-1], tail = last[0].strip(), last[1].strip()
    lines = head.split("\n") + [x.replace("\n", " ") for x in parts] + ([tail] if tail else [])
    return "\n".join(lines)


def layout(s):
    if not s:
        return s
    s = rows_to_lists(s)
    lines = s.split("\n")
    lines = join_broken(lines)
    out = []
    for ln in lines:
        out += split_inline(ln)
    out = unzip_lists(out)
    t = "\n".join(x.rstrip() for x in out)
    return re.sub(r"\n{3,}", "\n\n", t)


def run(A):
    n = 0
    for b in range(1, 7):
        p = f"{A}/mcq{b}.json"
        m = json.load(open(p))
        for qs in m["rows"].values():
            for q in qs:
                t = layout(q["s"])
                if t != q["s"]:
                    q["s"] = t
                    n += 1
        open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    print(f"{A}: {n} MCQ stems laid out")


TESTS = [
    "Consider the following statements. I. The vernal equinox falls on 21st March. II. On equinox, the Sun is directly overhead at the equator. III. The changes in the day length after equinox result from the changes in the tilt of the Earth with respect to the Sun.\nWhich of the statements given above is/are correct?",
    "Match the following.\nList I (Phenomenon)\nList II (Date) A. Summer Solstice\n1. 21st June B. Winter Solstice\n2. 22nd December C. Vernal Equinox\n3. 23rd September D. Autumnal Equinox\n4. 21st March\nCodes A B C D",
    "Identify the correct pairs for Northern Hemisphere. I. Winter Solstice–22nd December II. Autumn Equinox–23rd September III. Summer Solstice–21st June IV. Spring Equinox–21st March\nChoose the correct answer from the codes given below.",
    "Match the following\nList I with\nList II (Northern Hemisphere):\nList I: (a) Winter solstice (b) Summer solstice (c) Vernal equinox (d) Autumnal equinox\nList II: I. December 22 II. June 21 III. March 21 IV. September 23",
    "Given below are two statements, one is labeled as\nAssertion (A) and the other as\nReason (R).\nAssertion (A) : Turkish invasions on India were successful.\nReason (R) : There was no political unity in North India.",
    "Who wrote 1.5 lakh verses and lived in the 2nd c. A.D.?",
]

if __name__ == "__main__":
    if "--test" in sys.argv:
        for t in TESTS:
            print(layout(t))
            print("-----")
    else:
        run(sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets")
