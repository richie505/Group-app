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
    """data/pyq/all.jsonl (tools/pyq_parse.py), or its committed gzip."""
    import gzip, os
    return open("data/pyq/all.jsonl") if os.path.exists("data/pyq/all.jsonl") else gzip.open("data/pyq/all.jsonl.gz", "rt")


TELUGU = re.compile(r"[ఀ-౿]")
# the subject each Ghatna Chakra volume covers: its questions stay in that book (Environment: Science & Environment)
BOOK_OF = {"Indian History": [1], "Indian Polity and Governance": [2], "Economic and Social Development": [3],
           "General Geography": [4], "General Science": [5], "Environment and Ecology": [5, 4], "Current Events": None}


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


def clean(t):
    t = LAST_TCS.sub("", TCS.sub("", t))
    t = re.sub(r"\s+\d+\s+Question Type\b.*$", "", t, flags=re.S)  # the next question's header run on
    t = re.sub(r"\babout:blank\b|[\x00-\x08\x0b-\x1f\x7f]", "", JUNK.sub("", t))
    t = re.sub(r"(?<=[a-z])- (?=[a-z])", "", t)  # a word the PDF split over two lines: "Sci- ence"
    t = re.sub(r"\s*\bQ\s?\d{1,3}\.(?:\s+[A-Za-z]{1,3}\b(?![.)]))*", " ", t)  # the book's question numbers and the letters around them
    t = re.sub(r"\s*\b\d{1,3}/\d{1,3}\s+\d{1,2}/\d{1,2}/\d{4}(?:,\s*\d{1,2}:\d{2}\s*[AP]M)?", " ", t)  # page n/N and print date
    return re.sub(r"\s{2,}", " ", t).strip()


def usable(q):
    """A question we can show: its text, four options, no OCR debris (Telugu mixed in, an option that is a question)."""
    s, o = q["s"], q["o"]
    if (MENTAL.search(s) and not q["file"].startswith("Ghatna")) or "COMPREHENSION" in q["s"]:
        return False
    if TCS_LEFT.search(s + " ".join(o)):
        return False
    if any(len(x) > 220 for x in o) or all(len(x) <= 1 for x in o):  # an option that ran into the next question; options A-D of a chart
        return False
    if len(s) < 15 or len(o) != 4 or any(not x.strip() for x in o):
        return False
    if TELUGU.search(s + " ".join(o)):
        return False
    if q["a"] < 0:  # no key: only clean ones (scans with no key often pick up the next question's lines)
        if any("?" in x or len(x) > 160 for x in o) or not re.search(r"[?:.]\s*$|_{2,}|\bis\s*$|\bwas\s*$", s):
            return False
    return True


def cleaned(line):
    q = json.loads(line)
    q["s"], q["o"], q["x"] = clean(q["s"]), [clean(o) for o in q["o"]], clean(q.get("x", ""))
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
