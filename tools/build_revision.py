#!/usr/bin/env python3
"""Revision notes: an exam-ready condensed copy of the six notes books, built only from the notes themselves.

Every fact kept is a sentence or clause of the notes (nothing is written new), so the revision copy can never
disagree with the notes. Per subsection:
  * "Exam angle" callouts are kept whole - they are what the exam asks.
  * Bullets and paragraphs keep the sentences that carry a key fact: a bold phrase, a number or a year.
    Long sentences keep only their clauses (split at ";") that carry one. Bullets with no key fact go.
  * Tables keep every row; each cell keeps its key-fact clauses.
  * Source tags ([GK], (CDI), (TH, 10 Aug 2026) ...), asides about what the sources say ("APP calls them ...",
    "Some notes add ...") and "Not in your sources" lines are dropped.
  * How much stays follows the plan's priority for the section: HIGH keeps clauses with a bold phrase or a
    number, MED those with a bold phrase (brackets without a number go), LIGHT only bold-and-number facts.
Output: <out>/rev{1..6}.json (the revision app's assets) in the same layout as book{n}.json (so the app reads it the same way), plus a
summary of words kept per book.

    python3 tools/build_revision.py app/src/main/assets app/src/revise/assets
"""
import json
import re
import sys
from pathlib import Path

CODES = {
    "CDI", "CDX", "APP", "APHQ", "TH", "IYB", "APPCA", "APSES", "ES", "SES", "VIS", "LENS", "LENSD", "CDCA",
    "BUD", "PYQ", "PYQs", "UPSC", "APPSC", "G1", "G2", "GS", "PT365", "CA", "NCERT", "APPSC-GS", "APPSC-G1",
    "APPSC-G2", "BPSC", "JPSC", "UPPSC", "MPPSC", "RPSC", "UKPSC", "CGPSC", "TNPSC", "KPSC", "OPSC", "HPSC",
    "HPPSC", "WBPSC", "TSPSC", "TGPSC", "MPSC", "GPSC", "APSC", "SSC", "CDS", "CAPF", "NDA", "UPPCS", "RAS",
    "LENSD", "AP", "SES", "ESI", "PIB", "GK",
}
NOTE_CODES = {"CDI", "CDX", "APP", "APHQ", "APPCA", "LENS", "LENSD", "CDCA", "VIS", "IYB", "TH", "PT365"}
MONTHS = {m.lower() for m in "Jan Feb Mar Apr May Jun Jul Aug Sep Sept Oct Nov Dec January February March April June "
          "July August September October November December".split()}
FILLER = {"key", "keys", "answer", "answers", "notes", "note", "highlights", "prelims", "mains", "paper", "part",
          "data", "list", "survey", "update", "updated", "edition", "official", "and", "&", "/", "-", "pp", "p",
          "i", "ii", "iii", "iv", "block", "unit", "ch", "chapter", "vol", "table", "box", "printed", "the", "of",
          "in", "issue", "monthly", "weekly", "daily", "summary", "explanation", "asked", "q&a", "provisional"}


def is_citation(piece: str) -> bool:
    words = [w for w in re.split(r"[\s,;]+", piece.strip()) if w]
    if not words:
        return True
    code = words[0].rstrip(".:'s").removesuffix("'")
    if words[0].strip(".:") not in CODES and code not in CODES:
        return False
    for w in words[1:]:
        x = w.lower().strip(".,:")
        if not x or x in FILLER or x in MONTHS or x.upper() in CODES or w.strip(".,:") in CODES:
            continue
        if re.fullmatch(r"\d{1,4}(st|nd|rd|th)?([-/]\d{1,4})?|block\d+|q\d|pp?\.?\d.*|g[12]|s\d+", x):
            continue
        return False
    return True


def names_source(text: str) -> bool:
    """An aside about the sources rather than about the subject ("APP calls them ...", "some notes add ...")."""
    if re.search(r"\b(some|other|older|coaching) (notes|sources|books)\b|\bnotes (say|add|give|call)|\bsources (say|differ|give)", text, re.I):
        return True
    return any(w.strip(".,:;'’()").removesuffix("'s") in NOTE_CODES for w in text.split()[:6])


SOURCE_TALK = re.compile(r"\b(CDI|CDX|APP|APHQ|APPCA|LENS|LENSD|CDCA|VIS|IYB)(?:'s|’s)?(?:\s+(?:updated\s+)?notes?)?\s*(?::|says?|places?|puts?|gives?|calls?|lists?|dates?|adds?|has|wrongly|reads?|follows?|treats?|counts?|uses?)\b")


def talks_about_sources(text: str) -> bool:
    """A clause about what a source says ("CDI places the dynasty ...", "CDX says ..."), not about the subject."""
    return bool(SOURCE_TALK.search(text))


def strip_citations(text: str) -> str:
    def bracket(m):
        inner = m.group(1)
        pieces = [p for p in re.split(r";", inner)]
        keep = [p for p in pieces if not is_citation(p) and not (names_source(p) and len(p.split()) < 12)]
        if not keep:
            return ""
        return "(" + ";".join(keep).strip() + ")"
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\s?\(([^()]*)\)", lambda m: (" " if m.group(0).startswith(" ") else "") + bracket(m), text)
    text = re.sub(r"\[GK[^\]]*\]|\[[A-Z]{2,6}\]", "", text)
    return re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s{2,}", " ", text)).strip()


# --------------------------------------------------------------------------- facts said once per page

STOP = set("""a an the of in on at to for from by with and or but is are was were be been being it its this that these
those as into than then there their they he she his her them which who whom whose what when where how also only not no
any all each both more most other such same so very can could may might will would shall should must has have had
do does did under over after before between about against during up down out off again further once here why own
s same per via following correct incorrect given statements statement above below consider which true false regard
reference pairs pair matched match select code codes options option one two three four none answer asked""".split())


def content(text):
    """Content words and numbers of a piece of text (lower case, no stop words)."""
    words = re.findall(r"[a-z0-9][a-z0-9'-]*", text.lower().replace("’", "'"))
    return {w.removesuffix("'s").strip("'-") for w in words if w not in STOP and len(w) > 1} - {""}


class Seen:
    """What a revision page has already said: a clause most of whose words (and all its numbers) were said goes."""

    def __init__(self):
        self.words = set()
        self.keys = set()

    @staticmethod
    def key_phrases(rs):
        return {" ".join(sorted(content(t))) for t, f in rs if f & 1 and content(t)}

    def repeats(self, text, rs=None):
        w = content(text)
        if len(w) < 2:
            return False
        nums = {x for x in w if re.fullmatch(r"\d[\d.,-]*", x)}
        if not nums <= self.words:
            return False
        # every bold key phrase already given on this page: a restatement
        keys = self.key_phrases(rs) if rs else set()
        if keys and keys <= self.keys and len(w - self.words) <= 5:
            return True
        return len(w & self.words) >= 0.8 * len(w)

    def add(self, text, rs=None):
        self.words |= content(text)
        if rs:
            self.keys |= self.key_phrases(rs)


SEEN = Seen()

# --------------------------------------------------------------------------- runs

def runs(x):
    """Block text as runs [[text, flags]]."""
    if isinstance(x, str):
        return [[x, 0]]
    return [[t, f] for t, f in x]


def drop_muted(rs):
    return [[t, f] for t, f in rs if not (f & 4)]


def has_fact(rs, level="MED") -> bool:
    """HIGH: a bold phrase or a number; MED: a bold phrase; LIGHT: a bold phrase and a number."""
    bold = any(f & 1 and re.search(r"[A-Za-z0-9]", t) for t, f in rs)
    number = bool(re.search(r"\d", "".join(t for t, _ in rs)))
    return bold or number if level == "HIGH" else bold and number if level == "LIGHT" else bold


POINTERS = r"\s?\((?:see|details|more|as|cf\.?|also)\b[^()]*\)"


def drop_asides(rs, level):
    """Pointers ("(details below)", "(see table)") always go; below HIGH, brackets with no number go too."""
    out = []
    for t, f in rs:
        t = re.sub(POINTERS, "", t, flags=re.I)
        if not (f & 1) and level != "HIGH":
            t = re.sub(r"\s?\((?![^()]*\d)[^()]*\)", "", t)
        if t:
            out.append([t, f])
    return out


def split_runs(rs, pattern):
    """Split runs where [pattern] matches outside brackets (the match stays with the left piece)."""
    text = "".join(t for t, _ in rs)
    depth, inside = 0, []
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]" and depth:
            depth -= 1
        inside.append(depth > 0)
    cuts = [m.end() for m in re.finditer(pattern, text) if not inside[m.start()]]
    out, start = [], 0
    for end in cuts + [len(text)]:
        piece, pos = [], 0
        for t, f in rs:
            a, b = max(start, pos), min(end, pos + len(t))
            if a < b:
                piece.append([t[a - pos:b - pos], f])
            pos += len(t)
        if "".join(t for t, _ in piece).strip():
            out.append(piece)
        start = end
    return out


# sentence end: ". " not after an abbreviation or an initial
SENT = r"(?<!\bArt)(?<!\bArts)(?<!\bNo)(?<!\bvs)(?<!\bv)(?<!\bSec)(?<!\bDr)(?<!\bSt)(?<!\bMr)(?<!\bc)(?<!\bp)(?<!\bpp)(?<!\b[A-Z])\.\s+(?=[A-Z0-9\"“])"


def clean(rs):
    """Citations out, spaces tidy; drops empty runs."""
    text_runs = []
    for t, f in rs:
        if f & 1:
            t = re.sub(r"\[GK[^\]]*\]", "", t)
        else:
            lead = " " if t[:1].isspace() else ""
            tail = " " if t[-1:].isspace() else ""
            core = strip_citations(t)
            t = (lead + core + tail) if core else (" " if lead or tail else "")
        if t:
            text_runs.append([t, f])
    # join and tidy the seams
    out = []
    for t, f in text_runs:
        if out and out[-1][1] == f:
            out[-1][0] += t
        else:
            out.append([t, f])
    if out:
        out[0][0] = out[0][0].lstrip(" ;,")
        out[-1][0] = re.sub(r"[\s;,]+$", "", out[-1][0])
    for r in out:
        r[0] = re.sub(r"\s{2,}", " ", r[0])
        r[0] = re.sub(r"\(\s*\)", "", r[0])
    out = [r for r in out if r[0]]
    if out:
        whole = text_of(out)
        if whole.count("(") > whole.count(")"):
            out[-1][0] = re.sub(r"\s*\([^()]*$", "", out[-1][0])
            out = [r for r in out if r[0]]
    for a, b in zip(out, out[1:]):  # "1892 ." -> "1892."
        if re.match(r"\s*[.,;:)]", b[0]):
            a[0] = a[0].rstrip()
            b[0] = b[0].lstrip()
    return out


def text_of(rs):
    return "".join(t for t, _ in rs)


# --------------------------------------------------------------------------- choosing what stays

BUDGET = {"HIGH": 0.42, "MED": 0.30, "LIGHT": 0.18}  # share of a page's words kept, by plan priority
MIN_WORDS = 30  # a page this short or shorter keeps its key facts whole


def is_heading(b):
    """A sub-heading inside a page: a paragraph that is all bold ("Achievements - Indian Councils Act 1892.")."""
    if b["k"] != "p":
        return False
    rs = [r for r in runs(b["x"]) if r[0].strip()]
    return bool(rs) and all(f & 1 for _, f in rs) and len(text_of(rs).split()) <= 14


def units_of(blocks, level):
    """Every clause of a page as a candidate: (block, row, cell, runs). Tables: one unit per cell clause."""
    out = []
    for bi, b in enumerate(blocks):
        k = b["k"]
        if k == "t":
            for ri, row in enumerate(b["r"]):
                for ci, cell in enumerate(row[1:], start=1):
                    rs = clean(drop_asides(drop_muted(runs(cell)), level))
                    for c in split_runs(rs, r";\s"):
                        if not talks_about_sources(text_of(c)):
                            out.append((bi, ri, ci, c))
            continue
        if k == "s" and level == "LIGHT" or is_heading(b):
            continue
        rs = clean(drop_asides(drop_muted(runs(b["x"])), level))
        if k == "x":
            out.append((bi, None, None, rs))
            continue
        for sent in split_runs(rs, SENT):
            st = text_of(sent).strip()
            if st.startswith("Not in your sources") or names_source(st):
                continue
            for c in split_runs(sent, r";\s"):
                if not talks_about_sources(text_of(c)):
                    out.append((bi, None, None, c))
    return out


IDF = {}  # word -> rarity across the book's pages (common words like "act", "india" count little)
KEYS = []  # the page's key terms (lower case)


def score(unit, kind, tested):
    """How much a clause is worth in the exam: rare words the page's MCQs/PYQs test, its key terms, bold phrases."""
    rs = unit[3]
    text = text_of(rs)
    w = content(text)
    if not w:
        return 0.0
    bold_words = sum(len(t.split()) for t, f in rs if f & 1 and re.search(r"[A-Za-z0-9]", t))
    bold = min(3.0, bold_words / 2)
    nums = min(2, len(re.findall(r"\b\d[\d,.]*\b", text)))
    hit = sum(tested.get(x, 0) * IDF.get(x, 1.0) for x in w)
    low = text.lower()
    keys = sum(1 for k in KEYS if k in low)
    return 2.0 * hit / len(w) ** 0.5 + 1.2 * bold + 0.4 * nums + 1.5 * keys


def choose(blocks, level, tested):
    """The clauses that stay, by score, until the page's word budget is used; repeats skipped."""
    units = units_of(blocks, level)
    total = sum(len(text_of(u[3]).split()) for u in units)
    budget = max(MIN_WORDS, BUDGET[level] * total)
    order = sorted(range(len(units)), key=lambda i: -score(units[i], blocks[units[i][0]]["k"], tested) / max(4, len(text_of(units[i][3]).split())) ** 0.5)
    seen, chosen, used = Seen(), set(), 0
    # exam angles first, always
    for i, u in enumerate(units):
        if blocks[u[0]]["k"] == "x":
            chosen.add(i)
            used += len(text_of(u[3]).split())
            seen.add(text_of(u[3]), u[3])
    for i in order:
        if i in chosen:
            continue
        u = units[i]
        n = len(text_of(u[3]).split())
        if used >= budget:
            break
        if score(u, blocks[u[0]]["k"], tested) <= 0 or not has_fact(u[3], "HIGH"):
            continue
        if seen.repeats(text_of(u[3]), u[3]):
            continue
        chosen.add(i)
        used += n
        seen.add(text_of(u[3]), u[3])
    if not chosen:
        # a page of plain prose (no bold phrase, no number): its best sentences up to the budget
        used = 0
        for i in order:
            if used >= budget:
                break
            if score(units[i], "", tested) > 0 and not seen.repeats(text_of(units[i][3]), units[i][3]):
                chosen.add(i)
                used += len(text_of(units[i][3]).split())
                seen.add(text_of(units[i][3]), units[i][3])
    return units, chosen


def join_clauses(parts):
    out = []
    for c in parts:
        c = clean(c)
        if not c:
            continue
        if out:
            last = out[-1][0].rstrip()
            out[-1][0] = last.rstrip(";") + ("; " if not re.search(r"[.!?:]$", last) else " ")
        out.extend(c)
    return out


def merge_tables(blocks):
    """Tables with the same heading on one page become one (the notes often repeat a table from two sources)."""
    out, first = [], {}
    for b in blocks:
        if b["k"] == "t":
            key = tuple(text_of(c).strip().lower() for c in b["h"])
            if key in first:
                have = {text_of(r[0]).strip().lower() for r in first[key]["r"]}
                for r in b["r"]:
                    name = text_of(r[0]).strip().lower()
                    if name in have:  # same row label: add the new clauses to that row
                        row = next(x for x in first[key]["r"] if text_of(x[0]).strip().lower() == name)
                        for ci in range(1, min(len(row), len(r))):
                            if text_of(r[ci]).strip():
                                row[ci] = join_clauses([row[ci], r[ci]]) if text_of(row[ci]).strip() else r[ci]
                    else:
                        first[key]["r"].append(r)
                        have.add(name)
                continue
            first[key] = b
        out.append(b)
    return out


def condense_page(blocks, level, tested):
    units, chosen = choose(blocks, level, tested)
    keep = {}
    for i in sorted(chosen):
        bi, ri, ci, rs = units[i]
        keep.setdefault(bi, []).append((ri, ci, rs))
    # a sub-heading stays when something between it and the next sub-heading stays
    heading = None
    for bi, b in enumerate(blocks):
        if is_heading(b):
            heading = bi
        elif bi in keep and heading is not None:
            keep.setdefault(heading, [])
            heading = None
    out = []
    for bi, b in enumerate(blocks):
        if bi not in keep:
            continue
        if is_heading(b):
            out.append({"k": "p", "x": clean(runs(b["x"]))})
            continue
        if b["k"] == "t":
            cells = {}
            for ri, ci, rs in keep[bi]:
                cells.setdefault(ri, {}).setdefault(ci, []).append(rs)
            rows = []
            for ri in sorted(cells):
                row = b["r"][ri]
                rows.append([clean(runs(row[0]))] + [join_clauses(cells[ri].get(ci, [])) for ci in range(1, len(row))])
            out.append({"k": "t", "h": [clean(runs(c)) for c in b["h"]], "r": rows})
        else:
            rs = join_clauses([rs for _, _, rs in keep[bi]])
            if rs and not re.search(r"[.!?)\]\"”]$", rs[-1][0]):
                rs[-1][0] += "."
            if rs:
                out.append({"k": b["k"], "x": rs})
    return merge_tables(out)


def words(blocks):
    n = 0
    for b in blocks:
        if b["k"] == "t":
            for row in [b["h"]] + b["r"]:
                for c in row:
                    n += len(text_of(runs(c)).split())
        else:
            n += len(text_of(runs(b["x"])).split())
    return n


def main(assets: str, out: str):
    root = Path(assets)
    dest = Path(out)
    # priority of each section from the 90-day plan; sections the plan does not list count as MED
    plan = json.loads((root / "plan.json").read_text(encoding="utf-8"))
    pri = {tuple(r["ref"]): r.get("pri", "MED") for d in plan["days"] for r in d["rows"] if r.get("ref")}
    total_in = total_out = 0
    for n in range(1, 7):
        book = json.loads((root / f"book{n}.json").read_text(encoding="utf-8"))
        mcq = json.loads((root / f"mcq{n}.json").read_text(encoding="utf-8"))
        # rarity of each word across the book's pages
        import math
        pages = [content(json.dumps(sec["b"], ensure_ascii=False)) for u in book["units"] for r in u["rows"] for sec in r["secs"]]
        df = {}
        for pw in pages:
            for w in pw:
                df[w] = df.get(w, 0) + 1
        IDF.clear()
        IDF.update({w: math.log(len(pages) / c) / math.log(len(pages)) for w, c in df.items()})
        keyterms = json.loads((root / "keyterms.json").read_text(encoding="utf-8"))
        tested = {}  # (row, sec) -> word -> weight: what the page's questions ask (correct option, explanation)
        for r, qs in mcq["rows"].items():
            subs = mcq["subs"].get(r, [])
            for qi, q in enumerate(qs):
                if qi >= len(subs) or subs[qi] is None or subs[qi] < 0:
                    continue
                a = q.get("a", -1)
                text = " ".join([q.get("s", ""), q.get("x", ""), q["o"][a] if 0 <= a < len(q.get("o", [])) else q.get("at", "")])
                weight = 2 if "ap" in q or not str(q.get("id", "")).startswith("n") else 1
                bag = tested.setdefault((int(r), subs[qi]), {})
                for w in content(text):
                    bag[w] = bag.get(w, 0) + weight
        win = wout = 0
        index = -1  # rows are numbered across the whole book, as in the app
        for unit in book["units"]:
            for row in unit["rows"]:
                index += 1
                level = pri.get((n, index), "MED")
                row["pri"] = level
                for si, sec in enumerate(row["secs"]):
                    before = words(sec["b"])
                    bag = tested.get((index, si), {})
                    KEYS[:] = [k.lower() for k in keyterms.get(f"{n}:{index}:{si}", [])]
                    top = max(bag.values(), default=1)
                    blocks = condense_page(sec["b"], level, {w: v / top for w, v in bag.items()})
                    sec["b"] = blocks
                    win += before
                    wout += words(blocks)
        (dest / f"rev{n}.json").write_text(json.dumps(book, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"book {n}: {win:,} -> {wout:,} words ({wout * 100 // max(win, 1)}%)")
        total_in += win
        total_out += wout
    print(f"all: {total_in:,} -> {total_out:,} words ({total_out * 100 // total_in}%)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
