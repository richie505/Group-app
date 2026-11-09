"""Arihant "14000+ Objective General Studies" (Drive folder Arihant, 3 PDFs with a text layer) -> PYQ bank lines.

Each page has three columns of questions and, at the foot, the page's answer row ("1. (a) 2. (c) ...").
Only questions tagged with the exam they were asked in ("[UPPSC (Pre) 2010]") are previous-year questions: the
untagged ones are the book's own practice questions and are left out. Writes data/pyq/new/arihant.jsonl in the
format of data/pyq/new/INSTRUCTIONS.md (pyq_place.py drops the ones already in the bank).

    python3 tools/arihant_parse.py <dir with p1.pdf p2.pdf p3.pdf>
"""
import json, re, subprocess, sys
from collections import Counter

D = sys.argv[1]
W, H = 608.787, 772.314
TAG = re.compile(r"\[([^\[\]]*?(?:19|20)\d\d[^\[\]]*?)\]")
QN = re.compile(r"^\s{0,3}(\d{1,4})\.\s+(\S.*)$")
OPT = re.compile(r"\(([a-d])\)\s*")
ANS = re.compile(r"(\d{1,4})\.\s*\(([a-d])\)")


def words(pdf, page):
    out = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    return [(float(a), float(b), t, float(c)) for a, b, c, t in re.findall(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)"[^>]*>([^<]*)</word>', out)]


def gutters(ws, top, bottom):
    """the two empty vertical strips between the three columns (x where no word stands, between top and bottom)"""
    cover = [0] * int(W + 2)
    for x, y, t, x2 in ws:
        if top < y < bottom:
            for i in range(int(x), int(x2) + 1):
                cover[i] += 1
    gaps, i = [], 120
    while i < 500:
        if cover[i] <= 1:
            j = i
            while j < 500 and cover[j] <= 1:
                j += 1
            gaps.append((j - i, (i + j) / 2))
            i = j
        else:
            i += 1
    a = max((g for g in gaps if 150 < g[1] < 300), default=None)
    b = max((g for g in gaps if 330 < g[1] < 480), default=None)
    return [g[1] for g in (a, b) if g]


def crop(pdf, page, x, w, y=0, h=H):
    return subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-x", str(int(x)), "-y", str(int(y)),
                           "-W", str(int(w)), "-H", str(int(h)), "-layout", pdf, "-"], capture_output=True, text=True).stdout


def columns(ws):
    """the x where each of the page's columns starts: where its question numbers ("12.") stand"""
    xs = sorted(x for x, y, t in ws if re.fullmatch(r"\d{1,4}\.", t))
    starts = []
    for x in xs:
        if not starts or x - starts[-1][-1] > 60:
            starts.append([x])
        else:
            starts[-1].append(x)
    return [min(g) for g in starts if len(g) >= 2]


def page_parts(pdf, page):
    ws = words(pdf, page)
    if not ws:
        return [], {}
    # the answer row: the lowest lines with "n. (x)" pairs
    full = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", pdf, "-"], capture_output=True, text=True).stdout
    ans = {}
    for line in full.splitlines():
        pairs = ANS.findall(line)
        if len(pairs) >= 3 and len(pairs) * 8 > len(line.strip()) * 0.5:
            for n, l in pairs:
                ans[int(n)] = "abcd".index(l)
    # the answer row: one line with many "(x)" and "n." words; the columns are cut above it
    rows = Counter(round(y) for x, y, t, _ in ws if re.fullmatch(r"\([a-d]\)", t))
    nums = Counter(round(y) for x, y, t, _ in ws if re.fullmatch(r"\d{1,4}\.", t))
    keyy = min((y for y, c in rows.items() if c >= 5 and nums.get(y, 0) >= 3), default=H)
    g = gutters(ws, 45, keyy - 2)
    edges = [0] + g + [W]
    text_cols = [crop(pdf, page, edges[i], edges[i + 1] - edges[i], 0, keyy - 2) for i in range(len(edges) - 1)]
    return text_cols, ans


def questions(col):
    """(number, raw text) for each question begun in this column; text before the first number continues the last"""
    out, cur = [], None
    lead = []
    for line in col.splitlines():
        m = QN.match(line)
        if m and not OPT.match(m.group(2)):
            if cur:
                out.append(cur)
            cur = [int(m.group(1)), m.group(2)]
        elif cur:
            cur[1] += "\n" + line.strip()
        else:
            lead.append(line.strip())
    if cur:
        out.append(cur)
    return "\n".join(x for x in lead if x), out


def split(n, raw):
    tag = TAG.search(raw)
    if not tag:
        return None
    exam = re.sub(r"\s+", " ", tag.group(1)).strip()
    body = TAG.sub(" ", raw)
    parts = OPT.split(body)  # [stem, 'a', text, 'b', text, ...]
    if len(parts) != 9 or parts[1::2] != ["a", "b", "c", "d"]:
        return None
    clean = lambda t: re.sub(r"[ \t]+", " ", re.sub(r"\n\s*", " ", t)).strip()
    stem_lines = [l.strip() for l in parts[0].strip().splitlines() if l.strip()]
    # statements and list rows keep their own lines; wrapped sentences join
    s = ""
    for l in stem_lines:
        if re.match(r"^(?:[IVX]+\.|\d\.|[A-D]\.|Codes|List|Select|Which|Choose)", l) and s:
            s += "\n" + l
        else:
            s += (" " if s else "") + l
    opts = [clean(t) for t in parts[2::2]]
    if not s or any(not o or len(o) > 160 for o in opts):
        return None
    if re.search(r"\b(INDIAN|GEOGRAPHY|Objective GENERAL STUDIES|14000\+Q)\b", " ".join(opts)):
        return None
    yr = re.search(r"(19|20)\d\d", exam).group(0)
    return {"n": n, "exam": exam, "year": yr, "s": re.sub(r"[ \t]+", " ", s).strip(), "o": opts}


def main():
    out, stats = [], Counter()
    for part in ("p1", "p2", "p3"):
        pdf = f"{D}/{part}.pdf"
        pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
        chapter, last = 0, 0
        pending = []  # questions whose key is on a later page
        for p in range(1, pages + 1):
            cols, ans = page_parts(pdf, p)
            for c in cols:
                _, qs = questions(c)
                for n, raw in qs:
                    if n < last - 20:
                        chapter += 1
                    last = n
                    stats["questions"] += 1
                    q = split(n, raw)
                    if q is None:
                        stats["untagged or unreadable"] += 1
                        continue
                    q["id"] = f"arihant-{part}-{chapter}-{n}"
                    q["page"] = p
                    pending.append(q)
            keep = []
            for q in pending:
                if q["n"] in ans and p - q["page"] <= 2:
                    q["a"] = ans[q["n"]]
                    out.append(q)
                elif p - q["page"] >= 2:
                    stats["no key found"] += 1
                else:
                    keep.append(q)
            pending = keep
    with open("data/pyq/new/arihant.jsonl", "w") as f:
        for q in out:
            f.write(json.dumps({"id": q["id"], "exam": q["exam"], "paper": "General Studies", "year": q["year"],
                                "source": "Arihant 14000+ Objective General Studies (Drive: Arihant)", "file": "Arihant 14000 GS.md",
                                "n": q["n"], "s": q["s"], "o": q["o"], "a": q["a"], "x": ""}, ensure_ascii=False) + "\n")
    stats["written"] = len(out)
    print(dict(stats))


if __name__ == "__main__":
    main()
