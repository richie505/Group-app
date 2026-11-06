"""Files the previous-year questions (data/pyq/all.jsonl, tools/pyq_parse.py) under the apps' topics and subsections.

    python3 tools/pyq_place.py

For each notes layout (the Prep app's, and APPSC Complete's, which APPSC One-liners shares) every usable PYQ gets
the topic (book, row) whose notes and whose existing MCQs it is closest to (TF-IDF: the notes text, and a vote of the
nearest MCQs already filed there), then the subsection that shares most of its words (onepager_app.best_match).
A PYQ close to no topic is outside the syllabus (mental ability, other states' affairs) and is left out; one that
repeats an MCQ already in the app is recorded as that MCQ's PYQ instead of being added twice.
Writes data/pyq/place-<layout>.json: {pyq id: [book, row, sub, score]} and {"dup": {pyq id: app MCQ id}}.
"""
import json, re, sys
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, "tools")
from onepager_app import best_match, block_text  # noqa: E402

def bank():
    """Lines of data/pyq/all.jsonl (tools/pyq_parse.py, or its committed gzip), then the papers read from Drive's
    scans (data/pyq/new/*.jsonl, data/pyq/new/INSTRUCTIONS.md), with the keys found in the official key files
    (data/pyq/keys/out/*.json) put on the questions that had none."""
    import glob, gzip, os
    keys = {}
    for f in sorted(glob.glob("data/pyq/keys/out/*.json")):
        keys.update(json.load(open(f)))
    src = open("data/pyq/all.jsonl") if os.path.exists("data/pyq/all.jsonl") else gzip.open("data/pyq/all.jsonl.gz", "rt")
    stem = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())[:80]
    lines, seen = [], {}
    for line in src:
        q = json.loads(line)
        k = keys.get(q["id"])
        if k is not None and q.get("a", -1) < 0 and isinstance(k.get("a"), int) and 0 <= k["a"] <= 3:
            q["a"], q["keyed"] = k["a"], k.get("how", "")
        lines.append(q)
        seen.setdefault(stem(q.get("s", "")), q)
    for f in sorted(glob.glob("data/pyq/new/*.jsonl")):
        if os.path.basename(f) in NOT_NEW:
            continue
        for line in open(f):
            if not line.strip():
                continue
            q = json.loads(line)
            was = seen.get(stem(q["s"]))
            if was is not None and len(stem(q["s"])) >= 30:  # already in the bank: give it the key if it had none
                if was.get("a", -1) < 0 <= q["a"] and sorted(map(stem, was.get("o", []))) == sorted(map(stem, q["o"])):
                    was["a"], was["keyed"] = [stem(o) for o in was["o"]].index(stem(q["o"][q["a"]])), q["id"]
                continue
            q["new"] = 1
            seen[stem(q["s"])] = q
            lines.append(q)
    for q in lines:
        yield json.dumps(q, ensure_ascii=False)


# read but not added: a key-only official PDF (no wrong options printed), a book of one-line facts
NOT_NEW = {"2019-12-fso-p1.jsonl", "ng-aph-a.jsonl", "ng-aph-b.jsonl"}



TELUGU = re.compile(r"[ఀ-౿]")
# the subject each Ghatna Chakra volume covers: its questions stay in that book (Environment: Science & Environment)
BOOK_OF = {"Indian History": [1], "Indian Polity and Governance": [2], "Economic and Social Development": [3],
           "General Geography": [4], "General Science": [5], "Environment and Ecology": [5, 4], "Current Events": None}
OWN_BOOK = {"AP History previous papers": [1]}  # a file whose questions all belong to one book


TCS = re.compile(r"^(?:\s*(?:Qu\b|Question Typ\b|ion Type\b|\d{1,3}(?=\s)|\d+/\d+\s+\d+/\d+/\d+,\s*\d+:\d+\s*[AP]M|Question Type\s*:\s*MCQ|"
                 r"Option Shuffling\s*:\s*(?:Yes|No)|Display Question Number\s*:\s*(?:Yes|No)|Is Question Mandatory\s*:\s*(?:Yes|No)|"
                 r"Single Line Question Option\s*:\s*(?:Yes|No)|Option Orientation\s*:\s*\w+|Negative [Mm]arks [Dd]isplay [Tt]ext\s*:\s*1/3|"
                 r"Minimum Instruction Time\s*:\s*\d+|(?:Response |Think )?Time\s*:\s*(?:N\.?A\.?|\d+/\d+)|Calculator\s*:\s*\w+))+", re.I)
JUNK = re.compile(r"\s*(?:CELL\s*:\s*\d+\s*)?(?:APPSC PYQS\s*)?(?:SHRESHTA|SHRESTHA|CHRESHTA)\s+ON[LU]\w*(?:\s+ACADEMY)?(?:\s*&\s*PUBLICATIONS?)?|"
                  r"\s*CELL\s*:\s*\d{10}|\s*Carpe Diem IAS")
# mental ability (reasoning, arithmetic, data interpretation) in the APPSC papers: no notes topic covers it
MENTAL = re.compile(r"\bcoded? as\b|code language|missing (?:number|term|letter)|in the following series|next (?:number|term) in the series|"
                    r"\baverage (?:marks|age|of the)\b|\bmedian of\b|find the (?:median|mode|mean)|\bmean of\b|percentage of marks|following table|"
                    r"in the table|bar (?:graph|chart)|pie[ -]chart|histogram|frequency (?:polygon|distribution|curve)|\bvenn\b|\bdiagram\b|::|"
                    r"\bseated\b|sitting (?:immediate|to the|on the|in a)|facing (?:north|south|east|west|the centre|towards)|\bsyllogism|"
                    r"\bhow is\b.*\brelated\b|related to term|letter-cluster|\bsimple interest\b|compound interest|\bprofit (?:of|per ?cent)|"
                    r"\bdice\b|hands of a clock|sturges|measures? of (?:centrality|central tendency|dispersion)|"
                    r"\b\d+\s*[x×*/÷+]\s*\d+\s*=|^find the (?:value|number|odd)|odd one out|\bwhich number\b|\bmarks (?:more|less) than\b|"
                    r"students (?:in|of) a class|\bdimensions of a\b|same calendar|day of the week|what day|leap year|\bclock\b.*\bangle", re.I)

LAST_TCS = re.compile(r"^.{0,400}(?:Orientation\s*:\s*Vertical|Shuffling\s*:\s*(?:Yes|No)|Mandatory\s*:\s*(?:Yes|No)|"
                      r"Option\s*:\s*(?:Yes|No)|Display Text\s*:\s*1/3|Instruction Time\s*:\s*\d+|Time\s*:\s*N\.?A\.?)", re.S)
TCS_LEFT = re.compile(r"Question Type|Shuffling|Display Text|Orientation\s*:|Instruction Time", re.I)


TCS_OPT = re.compile(TCS.pattern.replace(r"\d{1,3}(?=\s)|", ""), re.I)  # options: a leading number is the option ("1 and 2 only")


def clean(t, opt=False):
    t = LAST_TCS.sub("", (TCS_OPT if opt else TCS).sub("", t))
    t = re.sub(r"\s+\d+\s+Question Type\b.*$", "", t, flags=re.S)  # the next question's header run on
    t = re.sub(r"\babout:blank\b|[\x00-\x08\x0b-\x1f\x7f]", "", JUNK.sub("", t))
    t = re.sub(r"(?<=[a-z])- (?=[a-z])", "", t)  # a word the PDF split over two lines: "Sci- ence"
    t = re.sub(r"\s*\bQ\s?\d{1,3}\.(?:\s+[A-Za-z]{1,3}\b(?![.)]))*", " ", t)  # the book's question numbers and the letters around them
    t = re.sub(r"\s*\b\d{1,3}/\d{1,3}\s+\d{1,2}/\d{1,2}/\d{4}(?:,\s*\d{1,2}:\d{2}\s*[AP]M)?", " ", t)  # page n/N and print date
    return re.sub(r"\s{2,}", " ", t).strip()


# reasoning / aptitude questions the keyword list above misses (statement-conclusion, data graphs, ages, dice)
APT = re.compile(r"conclusions? (?:among|numbered|I and II|A and B|follows?|is true|are true|given)|followed by (?:two|three) conclusions|"
 r"assumptions? (?:is|are) implicit|implicit in the statement|courses of action|coded as|code language|"
 r"next (?:term|number) in|missing (?:number|term|letter|figure)|blood relat|means\s*'?\s*[A-Z] is the (?:son|father|daughter|mother|brother|sister)|"
 r"facing (?:north|south|east|west)|odd one out|syllogism|related word pair|"
 r"\b[A-Z]\s*[<>≤≥]\s*[A-Z]\s*[<>≤≥]\s*[A-Z]\b|mirror image|water image|positions of the same die|face opposite|"
 r"(?:simple|compound) interest|study the following (?:graph|table|chart|data)|line graph shows|"
 r"work (?:in|alone in) \d+ days|cistern|present ages?|years? ago,? .{0,30}age|age is (?:half|twice|one)", re.I)
# a print timestamp left in an option by the PDF ("11/41 5/18/23, 5:08 PM")
STAMP = re.compile(r"\s*\d{1,3}/\d{1,3}\s+\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\s*")


def usable(q):
    """A question we can show: its text, four options, no OCR debris (Telugu mixed in, an option that is a question)."""
    s, o = q["s"], q["o"]
    if (MENTAL.search(s) and not q["file"].startswith("Ghatna")) or "COMPREHENSION" in q["s"]:
        return False
    if TCS_LEFT.search(s + " ".join(o)) or APT.search(s + " " + " ".join(o)):
        return False
    if any(len(x) > 220 for x in o) or all(len(x) <= 1 for x in o):  # an option that ran into the next question; options A-D of a chart
        return False
    if len(s) < 15 or len(o) != 4 or any(not x.strip() for x in o):
        return False
    if TELUGU.search(s + " ".join(o)):
        return False
    if q["a"] < 0 and not q.get("checked"):  # no key: only clean ones (scans with no key often pick up the next question's lines)
        if any("?" in x or len(x) > 160 for x in o) or not re.search(r"[?:.]\s*$|_{2,}|\bis\s*$|\bwas\s*$", s):
            return False
    return True


_FIXES = None


def fixes():
    """Hand-checked repairs of OCR'd questions (data/pyq/aph/out-*.json: the AP History book), by source id."""
    global _FIXES
    if _FIXES is None:
        import glob
        _FIXES = {}
        for f in sorted(glob.glob("data/pyq/aph/out-*.json")):
            _FIXES.update(json.load(open(f)))
    return _FIXES


def cleaned(line):
    q = json.loads(line)
    q["s"], q["o"], q["x"] = clean(q["s"]), [STAMP.sub(" ", clean(o, opt=True)).strip(" %") for o in q["o"]], clean(q.get("x", ""))
    f = fixes().get(q["id"])
    if f is not None:
        if not f.get("keep"):
            q["s"] = ""  # unrecoverable: not usable
        elif isinstance(f.get("o"), list) and len(f["o"]) == 4:
            q["s"], q["o"] = f.get("s") or q["s"], f["o"]
            q["a"] = f["a"] if isinstance(f.get("a"), int) and -1 <= f["a"] <= 3 else q["a"]
            q["x"] = f.get("x") or q["x"]
            q["checked"] = 1  # read by a person: no-key ones need not pass the OCR test
    return q


def qtext(q):
    ans = q["o"][q["a"]] if 0 <= q["a"] < len(q["o"]) else ""
    return " ".join([q["s"], " ".join(q["o"]), ans, ans, q.get("x", "")[:400]])


def mcq_text(q):
    return " ".join([q["s"], " ".join(q.get("o", [])), q.get("x", "")])


def sec_text(sec):
    return sec["t"] + " " + " ".join(block_text(b) for b in sec["b"])


def year_of(q):
    m = re.findall(r"(19\d\d|20\d\d)", q.get("year", "") + " " + q.get("exam", "") + " " + q.get("paper", ""))
    return max(map(int, m)) if m else 0


def place(layout, assets):
    rows, rtext, secs = [], [], []
    for b in range(1, 7):
        book = json.load(open(f"{assets}/book{b}.json"))
        ri = 0
        for u in book["units"]:
            for r in u["rows"]:
                rows.append((b, ri))
                rtext.append(" ".join([r["title"], " ".join(r.get("sub", [])), r.get("pyq", "")] + [sec_text(s) for s in r["secs"]]))
                secs.append([sec_text(s) for s in r["secs"]])
                ri += 1
    rowix = {k: i for i, k in enumerate(rows)}
    mq, mrow = [], []
    for b in range(1, 7):
        for ri, qs in json.load(open(f"{assets}/mcq{b}.json"))["rows"].items():
            for q in qs:
                if q["id"].startswith("y"):  # a PYQ tools/pyq_apply.py added: not the app's own MCQ
                    continue
                mq.append(q)
                mrow.append(rowix[(b, int(ri))])
    mrow = np.array(mrow)
    pyq = [q for q in map(cleaned, bank()) if usable(q)]
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=400000,
                          token_pattern=r"(?u)\b[a-zA-Z0-9][a-zA-Z0-9]+\b")
    vec.fit(rtext + [mcq_text(q) for q in mq] + [qtext(q) for q in pyq])
    R = vec.transform(rtext)
    M = vec.transform([mcq_text(q) for q in mq])
    P = vec.transform([qtext(q) for q in pyq])
    # the stem alone, for spotting a repeat of an app MCQ
    S = vec.transform([q["s"] + " " + " ".join(q["o"]) for q in pyq])
    MS = vec.transform([q["s"] + " " + " ".join(q.get("o", [])) for q in mq])
    out, dup = {}, {}
    book_rows = defaultdict(list)
    for i, (b, _) in enumerate(rows):
        book_rows[b].append(i)
    for start in range(0, len(pyq), 2000):
        part = pyq[start:start + 2000]
        sn = (P[start:start + 2000] @ R.T).toarray()
        sm = (P[start:start + 2000] @ M.T).toarray()
        sd = (S[start:start + 2000] @ MS.T).toarray()
        for j, q in enumerate(part):
            d = sd[j].argmax()
            if sd[j, d] > 0.75:
                dup[q["id"]] = mq[d]["id"]
                continue
            top = np.argpartition(-sm[j], 25)[:25]
            vote = np.zeros(len(rows))
            np.add.at(vote, mrow[top], sm[j, top] ** 2)
            score = sn[j] / (sn[j].max() + 1e-9) * 0.4 + vote / (vote.max() + 1e-9) * 0.6
            allow = None
            for name, bks in BOOK_OF.items():
                if q["file"].startswith("Ghatna Chakra - " + name):
                    allow = bks
            for name, bks in OWN_BOOK.items():
                if q["file"].startswith(name):
                    allow = bks
            y = year_of(q)
            mask = np.ones(len(rows), bool)
            if allow:
                mask[:] = False
                for bk in allow:
                    mask[book_rows[bk]] = True
            if y and y < 2024:  # Current Affairs is this year's news: an older question goes to a static topic
                mask[book_rows[6]] = False
            score = np.where(mask, score, -1)
            k = int(score.argmax())
            # how sure: the nearest MCQ / notes similarity (below this the question is off the syllabus)
            conf = float(max(sm[j, top].max(), sn[j, k] * 1.5))
            if conf < 0.08:  # nothing in common with any topic
                continue
            sub = best_match(secs[k], [q if q["a"] >= 0 else dict(q, a=0, o=[" ".join(q["o"])])])[0]  # no key: all options
            out[q["id"]] = [rows[k][0], rows[k][1], sub, round(conf, 3)]
    json.dump({"place": out, "dup": dup}, open(f"data/pyq/place-{layout}.json", "w"))
    print(f"{layout}: {len(pyq)} usable, placed {len(out)}, repeats of app MCQs {len(dup)}, left out {len(pyq) - len(out) - len(dup)}")


if __name__ == "__main__":
    place("prep", "app/src/main/assets")
    place("complete", "app/src/complete/assets")
