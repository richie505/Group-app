#!/usr/bin/env python3
"""APPSC Revision: revision sheets built from the app's MCQs - the facts the questions actually test.

Every MCQ has an explanation that states the fact behind its answer. For each page of the notes, the revision
sheet is those facts, one bullet each, in the MCQs' order, with the answer in bold:
  * filler is dropped: "Statements 1 and 2 are correct.", "Hence option (b).", "So the answer is ...";
  * "Statement 3 is false because the Act created X, not Y" becomes "The Act created X, not Y.";
  * up to two sentences per question; a fact already given on the page (most of its words, all its numbers)
    is not repeated - many questions test the same fact;
  * the page's "Exam angle" lines from the notes come first;
  * a page with no questions gets its key facts from the notes instead (tools/build_revision.py);
  * each page keeps its most valuable facts (rare information, the answer stated, key terms, past-paper
    questions first) up to a budget set by the plan's priority for the section, shown in question order.
Pages and their order are those of the notes, so the 90-day plan, the MCQ practice and progress line up.

    python3 tools/build_revision_mcq.py app/src/main/assets app/src/revise/assets
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_revision import clean, condense_page, content, runs, text_of  # noqa: E402

FILLER = re.compile(
    r"^(?:hence|thus|therefore|so)?,?\s*(?:the\s+)?(?:correct\s+)?(?:answer|option|choice)\b.*$"
    r"|^(?:only\s+)?statements?\s+[\d,\sand]+\s+(?:is|are)\s+(?:both\s+)?(?:correct|incorrect|true|false|wrong|right)\.?$"
    r"|^(?:all|none|both|neither)\b[^.]{0,40}\b(?:statements?|pairs?|options?)\b[^.]*(?:correct|incorrect|true|false)\.?$"
    r"|^(?:pairs?|options?)\s+[\d,\s(a-d)and]+\s+(?:is|are)\s+(?:correctly|incorrectly|wrongly)?\s*(?:matched|correct|incorrect)\.?$"
    r"|^the (?:other|remaining) (?:statements?|options?|pairs?) (?:is|are) (?:correct|incorrect|true|false|wrong)\.?$",
    re.I,
)
REASON = re.compile(
    r"^(?:statements?|options?|pairs?|assertion|reason|choices?)\s*\(?[\da-dIVX]+\)?"
    r"(?:\s*(?:,|and)\s*\(?[\da-dIVX]+\)?)*\s+(?:is\s+|are\s+)?(?:both\s+)?(?:also\s+)?"
    r"(?:correctly matched|wrongly matched|incorrectly matched|not correct|incorrect|correct|true|false|wrong|right)"
    r"\s*(?:because|as|since|:|-|,)?\s*",
    re.I,
)
SENT = re.compile(r"(?<!\bArt)(?<!\bNo)(?<!\bvs)(?<!\bv)(?<!\bSec)(?<!\bDr)(?<!\bSt)(?<!\bc)(?<!\b[A-Z])\.\s+(?=[A-Z0-9\"“(])")


SENTENCES = 1  # fact sentences kept per question: the first one states the fact, the rest elaborate
IDF = {}


def facts_of(q):
    """The fact sentences of one MCQ's explanation, filler out, reasons turned into facts."""
    out = []
    for s in SENT.split(q.get("x", "").replace("\n", " ").strip()):
        s = s.strip().rstrip(".").strip()
        # "Statements 1 and 2 correctly state the conversion": a verdict, not a fact
        if re.match(r"(?:statements?|options?|pairs?)\s+[\da-dIVX,\sand]+\s+(?:correctly|incorrectly|wrongly)\b", s, re.I):
            continue
        # "...; Statement 3 is incorrect because X" in the middle: keep X
        s = re.sub(r"[;,]\s*(?:but\s+|while\s+)?(?:statements?|options?|pairs?)\s+\(?[\da-dIVX]+\)?(?:\s*(?:,|and)\s*\(?[\da-dIVX]+\)?)*"
                   r"\s+(?:is|are)\s+(?:also\s+)?(?:not\s+)?(?:correctly matched|wrongly matched|incorrectly matched|incorrect|correct|true|false|wrong)"
                   r"\s*(?:because|as|since|:|-)?\s*", "; ", s, flags=re.I)
        # "...; therefore statement 2 is incorrect" at the end: drop it
        s = re.sub(r"[;,]?\s*(?:and\s+)?(?:(?:therefore|hence|so|thus)\s*[;,]?\s*)+(?:and\s+)?(?:statements?|options?|pairs?)\s+[\da-dIVX,\sand]+\s+(?:is|are)\s+(?:not\s+)?\w+$", "", s, flags=re.I)
        if not s or FILLER.match(s + "."):
            continue
        m = REASON.match(s)
        if m:
            s = s[m.end():].strip()
            if not s or FILLER.match(s + "."):
                continue
            s = s[0].upper() + s[1:]
        if len(s.split()) < 4:
            continue
        out.append(s + ".")
        if len(out) == SENTENCES:
            break
    return out


def answer_of(q):
    a = q.get("a", -1)
    opts = q.get("o", [])
    t = opts[a] if 0 <= a < len(opts) else q.get("at", "")
    t = t.strip().rstrip(".")
    # option texts like "1 and 2 only" or "Both A and R are true" say nothing on their own
    if re.fullmatch(r"[\d,\sand]+(?:only)?|only|both.*|neither.*|all.*|none.*|[a-d]\)?.*only", t, re.I) or len(t) < 3:
        return ""
    return t


def bold_answer(sentence, ans):
    """Runs of the sentence with the answer (if it is in there) in bold."""
    if ans:
        i = sentence.lower().find(ans.lower())
        if i >= 0:
            return [r for r in ([sentence[:i], 0], [sentence[i:i + len(ans)], 1], [sentence[i + len(ans):], 0]) if r[0]]
    return [[sentence, 0]]


BUDGET = {"HIGH": 0.35, "MED": 0.24, "LIGHT": 0.14}  # words kept, as a share of the page's notes, by plan priority
MIN_WORDS = 50


def notes_words(blocks):
    n = 0
    for b in blocks:
        cells = [c for row in [b["h"]] + b["r"] for c in row] if b["k"] == "t" else [b["x"]]
        n += sum(len(text_of(runs(c)).split()) for c in cells)
    return n


def value(c, keys):
    """A fact's worth: rare information, the answer in it, the page's key terms, a past-paper question."""
    _, f, ans, q = c
    w = content(f)
    info = sum(min(IDF.get(x, 1.0), 8.0) for x in w) / max(1.0, len(w)) ** 0.5
    low = f.lower()
    return (info + (2.0 if ans and ans.lower() in low else 0) + 1.5 * sum(1 for k in keys if k in low)
            + (1.5 if not str(q.get("id", "")).startswith("n") else 0))


class Said:
    """What a page has said: a fact whose distinctive words (weighted by rarity) were mostly said is a repeat."""

    def __init__(self):
        self.words = set()

    def repeats(self, text):
        w = content(text)
        if len(w) < 3:
            return False
        nums = {x for x in w if re.fullmatch(r"\d[\d.,-]*", x)}
        if not nums <= self.words:
            return False
        weight = sum(IDF.get(x, 1.0) for x in w)
        said = sum(IDF.get(x, 1.0) for x in w & self.words)
        return said >= 0.6 * weight

    def add(self, text):
        self.words |= content(text)


def words(blocks):
    return sum(len(text_of(runs(b["x"])).split()) for b in blocks if b["k"] != "t")


def main(assets, out):
    root, dest = Path(assets), Path(out)
    total_q = total_w = 0
    # rarity of words across all explanations: "act", "india" count little, "portfolio", "Canning" a lot
    import math
    docs = []
    for n in range(1, 7):
        for qs in json.loads((root / f"mcq{n}.json").read_text(encoding="utf-8"))["rows"].values():
            docs += [content(q.get("x", "")) for q in qs]
    df = {}
    for d in docs:
        for w in d:
            df[w] = df.get(w, 0) + 1
    IDF.update({w: math.log(len(docs) / c) for w, c in df.items()})
    plan = json.loads((root / "plan.json").read_text(encoding="utf-8"))
    pri = {tuple(r["ref"]): r.get("pri", "MED") for d in plan["days"] for r in d["rows"] if r.get("ref")}
    keyterms = json.loads((root / "keyterms.json").read_text(encoding="utf-8"))
    for n in range(1, 7):
        book = json.loads((root / f"book{n}.json").read_text(encoding="utf-8"))
        mcq = json.loads((root / f"mcq{n}.json").read_text(encoding="utf-8"))
        per_page = {}
        for r, qs in mcq["rows"].items():
            subs = mcq["subs"].get(r, [])
            for i, q in enumerate(qs):
                s = subs[i] if i < len(subs) else None
                if s is not None and s >= 0:
                    per_page.setdefault((int(r), s), []).append(q)
        index = -1
        nw = nq = 0
        for unit in book["units"]:
            for row in unit["rows"]:
                index += 1
                for si, sec in enumerate(row["secs"]):
                    said = Said()
                    blocks = []
                    for b in sec["b"]:  # the notes' exam angles first
                        if b["k"] == "x":
                            rs = clean(runs(b["x"]))
                            if rs:
                                blocks.append({"k": "x", "x": rs})
                                said.add(text_of(rs))
                    # candidate facts, best first, until the page's budget is used; then back in question order
                    cands = []
                    for qi, q in enumerate(per_page.get((index, si), [])):
                        ans = answer_of(q)
                        for f in facts_of(q):
                            cands.append((qi, f, ans, q))
                    keys = [k.lower() for k in keyterms.get(f"{n}:{index}:{si}", [])]
                    level = pri.get((n, index), "MED")
                    budget = max(MIN_WORDS, BUDGET[level] * notes_words(sec["b"]))
                    used, chosen = words(blocks), []
                    for c in sorted(cands, key=lambda c: -value(c, keys)):
                        if used >= budget:
                            break
                        if said.repeats(c[1]):
                            continue
                        said.add(c[1])
                        chosen.append(c)
                        used += len(c[1].split())
                    for qi, f, ans, q in sorted(chosen, key=lambda c: c[0]):
                        blocks.append({"k": "b", "x": bold_answer(f, ans)})
                        nq += 1
                    if not any(b["k"] == "b" for b in blocks):
                        # no questions on this page: its key facts from the notes (tools/build_revision.py)
                        blocks = condense_page(sec["b"], level, {})
                    sec["b"] = blocks
                    sec.pop("cov", None)
                    nw += words(blocks)
        (dest / f"rev{n}.json").write_text(json.dumps(book, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"book {n}: {nq:,} facts, {nw:,} words")
        total_q += nq
        total_w += nw
    print(f"all: {total_q:,} facts, {total_w:,} words")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
