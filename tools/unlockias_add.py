"""Adds the Unlock IAS papers' questions (tools/unlockias_parse.py -> data/pyq/unlockias/out/*.jsonl: UPSC Prelims
1995-2026, NDA, CDS, CAPF, EPFO and State PCS prelims) to APPSC Complete, Group 1 and Group 2 with
tools/pyq_add_new.py's own matching, so nothing already in the apps is rebuilt:

- a question that repeats any MCQ already in the app (TF-IDF of stem + options > 0.75, or the same opening words) is
  left out; so is one that repeats another new question (the earlier paper's copy is kept);
- mental ability / reasoning questions are left out (pyq_place.MENTAL); a question close to no topic of the notes
  (other States' own affairs, defence-service trivia) is left out as off the syllabus (NEAR);
- each one kept goes to its closest topic and subsection, first among that subsection's PYQs;
- Group 1 and Group 2 take only what Complete adds; Group 1's hidden sections take none.

Writes data/pyq/unlockias/added-<app>.json (what went where; what was left out and why).

    python3 -X utf8 tools/unlockias_add.py            # dry run: counts only
    python3 -X utf8 tools/unlockias_add.py --apply
"""
import glob, json, re, sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, "tools")
import pyq_add_new as P  # noqa: E402

OUT = "data/pyq/unlockias"
APPS = {"complete": "app/src/complete/assets", "group1": "app/src/group1/assets", "group2": "app/src/group2/assets"}
NEAR = 0.08
P.NEAR = NEAR

# pyq_add_new reads its own folders: point it at this one
_glob = glob.glob
P.glob.glob = lambda pat: sorted(_glob(f"{OUT}/out/*.jsonl")) if "ocr2026" in pat else []


# maths, reasoning and figure-based questions (the papers' aptitude parts): not General Studies, left out
MATH = re.compile(
    r"(LCM|HCF|H\.C\.F\.?|L\.C\.M\.?)|next (term|number|letter)|missing (term|number|letter)|"
    r"\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d?_X]+\s*,|sequence follows|alphanumeric series|simple interest|compound interest|"
    r"loss per ?cent|profit per ?cent|gain per ?cent|cost price|selling price|km/h|kmph|km per hour|"
    r"average (age|speed|weight|marks) of|find the (value|lcm|hcf|area|sum|number|ratio|least|greatest)|value of x|"
    r"x\s*[²³^]|[×÷√Σ]|is coded as|code language|odd (one|man) out|mirror image of|water image|blood relation|"
    r"how is .{1,30} related to|facing (north|south|east|west)|walks? \d+ ?(km|m|metres)|escalator|pipes? .{1,60} fill|"
    r"can (do|complete|finish) a (piece of )?work|in how many (days|ways|hours|minutes)|"
    r"how many (ways|triangles|squares|numbers between)|sum of (the )?(first|digits|two numbers)|divisible by|"
    r"remainder when|leaving a remainder|probability (that|of getting)|chance of passing|dice|pack of cards|"
    r"hands of a clock|angle between the hands|sitting in a (row|circle)|venn diagram|which number (will|should)|"
    r"perimeter of|area of (a|the) (circle|triangle|square|rectangle)|isosceles|present age|times as old|"
    r"shown in the figure|given figure|following figure|figure given|Directions\s*:|next (two|three|four|five) items|"
    r"speed of \d+|half the distance|volume doubles", re.I | re.S)


def among_new(new):
    """ids of new questions that repeat an earlier new question (order: UPSC by year, then the other papers)"""
    vec = TfidfVectorizer(sublinear_tf=True, token_pattern=r"(?u)\b[a-zA-Z0-9][a-zA-Z0-9]+\b")
    S = vec.fit_transform([q["s"] + " " + " ".join(q["o"]) for q in new])
    rep = {}
    for start in range(0, len(new), 1000):
        sim = (S[start:start + 1000] @ S.T).toarray()
        for j in range(sim.shape[0]):
            i = start + j
            sim[j, i:] = 0
            k = int(sim[j].argmax())
            if sim[j, k] > P.DUP and new[k]["id"] not in rep:
                rep[new[i]["id"]] = new[k]["id"]
    return rep


def main():
    apply = "--apply" in sys.argv
    new, dropped = P.new_questions()
    for q in new:
        q["file"] = "Unlock IAS"
        q["s"] = re.sub(r"^(\d{1,3}\.\s+|Question\s*:\s*)", "", q["s"])
    dropped["maths / reasoning / needs a figure"] = sum(1 for q in new if MATH.search(q["s"]))
    new = [q for q in new if not MATH.search(q["s"])]
    new.sort(key=lambda q: (not q["id"].startswith("uias-upsc"), q["id"].rsplit("-", 1)[0], q.get("n", 0)))
    rep = among_new(new)
    dropped["repeats another new question"] = len(rep)
    new = [q for q in new if q["id"] not in rep]
    print(f"read {len(new)} usable new questions; left out before matching: {dict(dropped)}")
    in_complete, where = None, {}
    for app, assets in APPS.items():
        cand = new if in_complete is None else [q for q in new if q["id"] in in_complete]
        P.G2_NEAR = NEAR
        placed, dup, off = P.place("group2" if app != "complete" else app, assets, cand)
        if app == "group1":   # hidden sections and hidden pages take no MCQs
            ix = json.load(open(f"{assets}/index.json"))
            hide = {(b + 1, r) for b, bk in enumerate(ix["books"]) for r, row in enumerate(bk["rows"]) if row.get("hide")}
            gone = [i for i, (b, r, _, _) in placed.items() if (b, r) in hide]
            for i in gone:
                off.append(i); placed.pop(i)
        if app == "complete":
            in_complete = set(placed)
        byq = {q["id"]: q for q in cand}
        keyed = sum(1 for p in placed if byq[p]["a"] >= 0)
        per = Counter(byq[p]["exam"].rsplit(" ", 1)[0] for p in placed)
        json.dump({"placed": placed, "dup_of": dup, "off_syllabus": off, "repeats_new": rep if app == "complete" else {},
                   "dropped": dropped}, open(f"{OUT}/added-{app}.json", "w"), ensure_ascii=False)
        print(f"{app}: add {len(placed)} ({keyed} with key), already in the app {len(dup)}, off the syllabus {len(off)}"
              + ("" if apply else "  [dry run]"))
        print("   by exam:", dict(per.most_common()))
        P.add(app, assets, cand, placed, apply)


if __name__ == "__main__":
    main()
