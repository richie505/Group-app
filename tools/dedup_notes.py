#!/usr/bin/env python3
"""Remove facts the notes repeat on more than one page, keep each in its topic's home, and move the MCQs.

The six notes books repeat many facts on several pages: a table row restated as a bullet two
subsections later, a Polity fact retold in History, a current-affairs number given again in the
economy book. This keeps each repeated fact once and cuts the other copies:

  * Units compared: each sentence (or ';' clause) of a paragraph, bullet or exam-angle block, and each
    table row. Units shorter than 6 content words, and lead-ins ending in ':', are never cut.
  * A unit X is a copy of a unit Y on another subsection when >= 80% of X's content words are in Y and
    every number in X is in Y (so X adds nothing Y does not say).
  * Which copy stays: when only X is inside Y, Y stays (it says more). When the two say the same, the one
    whose section/subsection titles share more words with it stays (its topic's home); a tie keeps the
    one read first in the 90-day plan.
  * A paragraph loses only the copied sentences; a block or table with nothing left goes. A bullet keeps
    its text if sub-bullets under it stay. Subsections are never deleted (ids "book:row:sec" stay valid
    for the plan, progress and bookmarks): one emptied this way shows only its "Also covered in" links.
  * Each subsection that lost text gets "cov": [[book,row,sec], ...], the subsections that now hold it,
    shown as "Also covered in" links at its end.
  * MCQs: a question whose stem+answer is about a cut unit moves to the subsection that kept the fact;
    near-identical questions (same stem and correct answer) are then kept once. index.json counts are
    updated.

Usage: python3 tools/dedup_notes.py app/src/main/assets [--dry-run]
Re-running finds only what is left to cut.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

STOP = set("""the a an of and in to for on by with as at from is are was were be been being it its this that these
those which or their his her who whom into under over than then also not no only all any each has have had
can may will would should shall such other more most some about after before between during while where when
what how why so if but per via both either one two three first second new under upto""".split())
CITATION = re.compile(
    r"\[[^\]]*\]|\((?:[^()]*\b(?:TH|IE|PIB|IYB|LENS|LENSD|VIS|CDI|CDX|APP|APHQ|APPCA|CDCA|PT365|ES|SES|APSES|BUD|GK|NCERT"
    r"|APPSC|UPSC|PYQ|G1|G2|GS|key|match|Block\d+)\b[^()]*)\)")
PRONOUN = re.compile(r"^\W*(?:It|Its|This|These|They|Their|Them|He|His|She|Her|Such|The latter|The former|Both|Here|There)\b")
ABBREV = re.compile(r"(?:\b(?:Dr|Mr|Mrs|Ms|St|No|Nos|Art|Arts|Sec|Secs|vs|viz|i\.e|e\.g|etc|Govt|Co|Ltd|Rs|Jr|Sr|Prof|Gen|Lt|Col|Mt|Ft|Hon|Smt|Shri|Sri|cf|approx|est|Fig|Vol|Ch|pp|p)|\b[A-Z])\.$")
SPLIT = re.compile(r"(?<=[.;])\s+(?=[A-Z0-9\"'(])")


def run_list(x):
    """Block text or table cell -> [[text, flags], ...]."""
    if isinstance(x, str):
        return [[x, 0]]
    return [[r[0], r[1]] for r in x]


def plain(x):
    return "".join(r[0] for r in run_list(x))


def words(text):
    t = CITATION.sub(" ", text).lower().replace(",", "")
    return [w for w in re.findall(r"[a-z0-9.]+", t) if w.strip(".") and w.strip(".") not in STOP]


def content(text):
    ws = [w.strip(".") for w in words(text)]
    return frozenset(ws), frozenset(w for w in ws if any(c.isdigit() for c in w))


def sentences(text):
    """(start, end) spans of the sentences / ';' clauses, not splitting after Dr. / Art. / A."""
    spans, start = [], 0
    for m in SPLIT.finditer(text):
        if ABBREV.search(text[start:m.start()]):
            continue
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return [(a, b) for a, b in spans if text[a:b].strip()]


def cut(runs, spans):
    """Runs with the character spans removed; tidies the joins and the ending."""
    text = "".join(r[0] for r in runs)
    keep = [True] * len(text)
    for a, b in spans:
        # take the whitespace after the cut sentence too
        while b < len(text) and text[b] == " ":
            b += 1
        for i in range(a, b):
            keep[i] = False
    out, pos = [], 0
    for t, f in runs:
        piece = "".join(c for i, c in enumerate(t) if keep[pos + i])
        pos += len(t)
        if piece:
            if out and out[-1][1] == f:
                out[-1][0] += piece
            else:
                out.append([piece, f])
    # a clause cut at the end leaves "...;" -> "..."
    while out and not out[-1][0].strip():
        out.pop()
    if out:
        out[-1][0] = out[-1][0].rstrip()
        if out[-1][0].endswith((";", ",")):
            out[-1][0] = out[-1][0][:-1] + "."
    return out


def main():
    assets = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv
    books = {b: json.loads((assets / f"book{b}.json").read_text()) for b in range(1, 7)}
    rows = {b: [r for u in bk["units"] for r in u["rows"]] for b, bk in books.items()}

    plan = json.loads((assets / "plan.json").read_text())
    first_day = {}
    for day in plan["days"]:
        for x in day.get("rows", []):
            if "ref" in x:
                first_day.setdefault(tuple(x["ref"]), day["n"])

    # ---- units -------------------------------------------------------------------------------
    units = []  # dict(loc=(b,r,s), blk, kind ('s' sentence/'r' row), span|row, words, nums, order)
    for b in range(1, 7):
        for ri, r in enumerate(rows[b]):
            for si, s in enumerate(r["secs"]):
                topic = content(r["title"] + " " + " ".join(r.get("sub", [])) + " " + s.get("t", ""))[0]
                for bi, blk in enumerate(s["b"]):
                    if blk["k"] == "t":
                        for rr, row in enumerate(blk["r"]):
                            text = " ".join(plain(c) for c in row)
                            w, n = content(text)
                            if len(w) >= 6:
                                units.append(dict(loc=(b, ri, si), blk=bi, row=rr, w=w, n=n, topic=topic, text=text))
                    elif blk["k"] in "pbsx":
                        text = plain(blk["x"])
                        for a, e in sentences(text):
                            piece = text[a:e]
                            w, n = content(piece)
                            if len(w) >= 6 and not piece.rstrip().endswith(":"):
                                units.append(dict(loc=(b, ri, si), blk=bi, span=(a, e), w=w, n=n, topic=topic, text=piece))
    for i, u in enumerate(units):
        b, r, s = u["loc"]
        u["order"] = (first_day.get((b, r), 999), b, r, s, u["blk"], i)
    print(f"units: {len(units)}")

    # ---- candidate pairs: share most of the rarer words ----------------------------------------
    df = Counter(w for u in units for w in u["w"])
    index = defaultdict(list)
    for i, u in enumerate(units):
        for w in u["w"]:
            if df[w] <= 300:
                index[w].append(i)
    copies = {}  # removed unit -> kept unit
    pairs = 0
    for i in sorted(range(len(units)), key=lambda i: units[i]["order"]):
        u = units[i]
        rare = [w for w in u["w"] if df[w] <= 300]
        if len(rare) < 2:
            continue
        hits = Counter(j for w in rare for j in index[w] if j != i)
        need = max(2, int(0.6 * len(rare) + 0.999))
        for j, c in hits.items():
            if c < need:
                continue
            v = units[j]
            if v["loc"] == u["loc"]:
                continue
            pairs += 1
            u_in_v = inside(u, v, df)
            v_in_u = inside(v, u, df)
            if not (u_in_v or v_in_u):
                continue
            if u_in_v and v_in_u:
                su, sv = len(u["w"] & u["topic"]), len(v["w"] & v["topic"])
                drop = i if (sv, -_o(v)) > (su, -_o(u)) else j
            else:
                drop = i if u_in_v else j
            keep = j if drop == i else i
            if drop in copies or keep in copies:
                continue
            # a table row goes only when another table says it; prose may go when a table says it
            if "row" in units[drop] and "row" not in units[keep]:
                continue
            copies[drop] = keep
    # keep a sentence the next sentence leans on ("... Act was passed. It created ...")
    spans_cut = defaultdict(set)
    for x in copies:
        if "span" in units[x]:
            spans_cut[(units[x]["loc"], units[x]["blk"])].add(units[x]["span"])
    for d in list(copies):
        u = units[d]
        if "span" not in u:
            continue
        b, r, s = u["loc"]
        text = plain(rows[b][r]["secs"][s]["b"][u["blk"]]["x"])
        spans = sentences(text)
        cut_spans = spans_cut[(u["loc"], u["blk"])]
        later = [sp for sp in spans if sp[0] > u["span"][0]]
        if later and later[0] not in cut_spans and PRONOUN.match(text[later[0][0]:later[0][1]]):
            del copies[d]
    print(f"candidate pairs checked: {pairs}; copies to cut: {len(copies)}")

    # ---- cut ---------------------------------------------------------------------------------
    by_block = defaultdict(list)
    for d, k in copies.items():
        u = units[d]
        by_block[(u["loc"], u["blk"])].append(d)
    cov = defaultdict(Counter)
    for d, k in copies.items():
        cov[units[d]["loc"]][units[k]["loc"]] += 1

    words_before = sum(len(u["text"].split()) for u in units)
    cut_words = sum(len(units[d]["text"].split()) for d in copies)
    print(f"words in units: {words_before}; cut: {cut_words} ({cut_words / words_before:.1%})")
    per_book = Counter(units[d]["loc"][0] for d in copies)
    print("cut units per book:", dict(sorted(per_book.items())))

    if dry:
        import random
        random.seed(3)
        for d in random.sample(list(copies), 25):
            k = copies[d]
            print(f"\nCUT  {units[d]['loc']} {units[d]['text'][:160]}\nKEEP {units[k]['loc']} {units[k]['text'][:160]}")
        return

    for (loc, bi), ds in by_block.items():
        b, r, s = loc
        blk = rows[b][r]["secs"][s]["b"][bi]
        if blk["k"] == "t":
            drop = {units[d]["row"] for d in ds}
            blk["r"] = [row for i, row in enumerate(blk["r"]) if i not in drop]
            if not blk["r"]:
                blk["gone"] = True
        else:
            runs = cut(run_list(blk["x"]), [units[d]["span"] for d in ds])
            if any(c.isalnum() for t, _ in runs for c in t):
                blk["x"] = runs
            else:
                blk["gone"] = True
    for b in range(1, 7):
        for ri, r in enumerate(rows[b]):
            for si, s in enumerate(r["secs"]):
                bl = s["b"]
                for i, blk in enumerate(bl):
                    # a bullet stays as a heading while sub-bullets under it stay
                    if blk.get("gone") and blk["k"] == "b" and i + 1 < len(bl) and bl[i + 1]["k"] == "s" and not bl[i + 1].get("gone"):
                        del blk["gone"]
                s["b"] = [x for x in bl if not x.get("gone")]
                if (b, ri, si) in cov:
                    old = [tuple(x) for x in s.get("cov", [])]
                    new = [k for k, _ in cov[(b, ri, si)].most_common()]
                    s["cov"] = [list(x) for x in dict.fromkeys(old + new)][:4]
    for b, bk in books.items():
        (assets / f"book{b}.json").write_text(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))

    move_mcqs(assets, units, copies)


def inside(x, y, df):
    """x says nothing y does not: 80% of its words, all its numbers and every rare word are in y."""
    missing = x["w"] - y["w"]
    return len(missing) <= 0.2 * len(x["w"]) and x["n"] <= y["w"] and all(df[w] > 40 for w in missing)


def _o(u):
    return u["order"][0] * 10 ** 7 + u["order"][1] * 10 ** 5 + u["order"][2] * 10 ** 2 + u["order"][3]


def move_mcqs(assets, units, copies):
    mcq = {b: json.loads((assets / f"mcq{b}.json").read_text()) for b in range(1, 7)}
    cut_at = defaultdict(list)
    for d, k in copies.items():
        cut_at[units[d]["loc"]].append(d)
    moved = 0
    plan = {b: {} for b in range(1, 7)}  # b -> row -> list of (sub, q)
    for b, m in mcq.items():
        for r, qs in m["rows"].items():
            for q, s in zip(qs, m["subs"][r]):
                plan[b].setdefault(int(r), []).append([s, q])
    arrivals = []
    for b in range(1, 7):
        for r in list(plan[b]):
            stay = []
            for s, q in plan[b][r]:
                ds = cut_at.get((b, r, s), [])
                dest = None
                if ds:
                    w = content(q["s"] + " " + q["o"][q["a"]])[0] if 0 <= q["a"] < len(q["o"]) else content(q["s"])[0]
                    best = max(ds, key=lambda d: len(units[d]["w"] & w))
                    if len(units[best]["w"] & w) >= max(3, 0.5 * len(units[best]["w"])):
                        dest = units[copies[best]]["loc"]
                if dest:
                    arrivals.append((dest, q))
                    moved += 1
                else:
                    stay.append([s, q])
            plan[b][r] = stay
    for (b, r, s), q in arrivals:
        plan[b].setdefault(r, []).append([s, q])
    # near-identical questions: same stem words and same correct answer
    seen, dupes = set(), 0
    for b in range(1, 7):
        for r in sorted(plan[b]):
            keep = []
            for s, q in plan[b][r]:
                ans = q["o"][q["a"]] if 0 <= q["a"] < len(q["o"]) else ""
                key = (" ".join(sorted(content(q["s"])[0])), " ".join(sorted(content(ans)[0])))
                if key in seen:
                    dupes += 1
                    continue
                seen.add(key)
                keep.append([s, q])
            plan[b][r] = keep
    print(f"MCQs moved to where the fact stays: {moved}; near-identical MCQs dropped: {dupes}")
    counts = {}
    for b, m in mcq.items():
        rs = {r: v for r, v in sorted(plan[b].items()) if v}
        m["rows"] = {str(r): [q for _, q in v] for r, v in rs.items()}
        m["subs"] = {str(r): [s for s, _ in v] for r, v in rs.items()}
        counts[b] = {r: len(v) for r, v in rs.items()}
        (assets / f"mcq{b}.json").write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    index_path = assets / "index.json"
    index = json.loads(index_path.read_text())
    for bk in index["books"]:
        for ri, r in enumerate(bk["rows"]):
            r["q"] = counts.get(bk["id"], {}).get(ri, 0)
    index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    print("MCQs now:", sum(sum(v.values()) for v in counts.values()))


if __name__ == "__main__":
    main()
