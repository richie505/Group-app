"""Adds newly read PYQs (data/pyq/ocr2026/out/*.jsonl, data/pyq/ocr2026/INSTRUCTIONS.md) to APPSC Complete and APPSC
Group 2 WITHOUT rebuilding the PYQs already there (tools/pyq_apply.py rebuilds them all from the bank, which would undo
the key fixes and explanations made in the apps since). Only questions that are not already in the app are added.

For each app layout it reuses tools/pyq_place.py's matching: the topic whose notes and own MCQs are closest (TF-IDF),
then the subsection sharing most words. A question that repeats any MCQ already in the app (its own or a PYQ) or
another new question is dropped; one close to no topic (off the syllabus) is left out. Within a subsection the new
PYQs go first, as pyq_apply.py orders PYQs. Writes data/pyq/ocr2026/added-<app>.json (what went where, what was
dropped and why) and updates the app's mcq*.json, index.json counts and planmcq.json.

    python3 tools/pyq_add_new.py            # dry run: counts only
    python3 tools/pyq_add_new.py --apply
"""
import glob
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, "tools")
from onepager_app import best_match  # noqa: E402
from pyq_place import clean, usable, qtext, mcq_text, sec_text  # noqa: E402
from pyq_apply import stem as tidy_stem  # noqa: E402

APPS = {"complete": "app/src/complete/assets", "group2": "app/src/group2/assets"}
OWN_BOOK = {"ap-history": [1], "polity": [2], "economy": [3], "science-tech": [5]}  # whole books of one subject
DUP = 0.75   # stem+options similarity above which a question repeats one already in the app
NEAR = 0.08  # below this it shares nothing with any topic


def norm(t):
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


def new_questions():
    out, seen, dropped = [], set(), defaultdict(int)
    for f in sorted(glob.glob("data/pyq/ocr2026/out/*.jsonl")):
        for line in open(f):
            if not line.strip():
                continue
            q = json.loads(line)
            q["s"] = clean(q.get("s", ""))
            q["o"] = [re.sub(r"[✔✓✅]", "", clean(o, opt=True)).strip(" %'") for o in q.get("o", [])]
            q.setdefault("x", "")
            q["file"] = f"OCR2026 {q.get('book', '')}"
            a = q.get("a", -1)
            q["a"] = a if isinstance(a, int) and -1 <= a <= 3 else -1
            if not usable(q):
                dropped["unusable (garbled, not 4 options, no key and unclean)"] += 1
                continue
            k = norm(q["s"])[:80] + "|" + "|".join(sorted(norm(o) for o in q["o"]))
            if k in seen:
                dropped["repeated inside the new books"] += 1
                continue
            seen.add(k)
            out.append(q)
    return out, dropped


def to_mcq(q):
    src = re.sub(r"\s+", " ", q.get("exam") or q.get("src") or "State PSC").strip()[:60]
    o = {"id": "y" + hashlib.sha1(q["id"].encode()).hexdigest()[:11], "s": tidy_stem(q["s"]), "o": q["o"], "a": q["a"],
         "src": src}
    if q.get("x"):
        o["x"] = q["x"][:1500]
    if q["a"] < 0:
        o["k"], o["a"] = "u", -1
    if re.search(r"\bAPPSC\b|\bA\.?P\.?P\.?S\.?C\b", src, re.I):
        o["ap"] = 1
    return o


def place(app, assets, new):
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
    allq, own, mrow = [], [], []
    for b in range(1, 7):
        m = json.load(open(f"{assets}/mcq{b}.json"))
        for key in ("rows", "units"):
            for ri, qs in m.get(key, {}).items():
                for q in qs:
                    if not isinstance(q, dict):
                        continue
                    allq.append(q)
                    if key == "rows" and not q["id"].startswith("y"):
                        own.append(q)
                        mrow.append(rowix[(b, int(ri))])
    mrow = np.array(mrow)
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=400000,
                          token_pattern=r"(?u)\b[a-zA-Z0-9][a-zA-Z0-9]+\b")
    vec.fit(rtext + [mcq_text(q) for q in own] + [qtext(q) for q in new])
    R, M, P = vec.transform(rtext), vec.transform([mcq_text(q) for q in own]), vec.transform([qtext(q) for q in new])
    S = vec.transform([q["s"] + " " + " ".join(q["o"]) for q in new])
    A = vec.transform([q.get("s", "") + " " + " ".join(q.get("o", [])) for q in allq])
    exact = {norm(q.get("s", ""))[:80] for q in allq if len(norm(q.get("s", ""))) >= 30}
    book_rows = defaultdict(list)
    for i, (b, _) in enumerate(rows):
        book_rows[b].append(i)
    placed, dup, off = {}, {}, []
    for start in range(0, len(new), 1000):
        part = new[start:start + 1000]
        sn = (P[start:start + 1000] @ R.T).toarray()
        sm = (P[start:start + 1000] @ M.T).toarray()
        sd = (S[start:start + 1000] @ A.T).toarray()
        for j, q in enumerate(part):
            d = int(sd[j].argmax())
            if sd[j, d] > DUP or norm(q["s"])[:80] in exact:
                dup[q["id"]] = allq[d]["id"]
                continue
            top = np.argpartition(-sm[j], 25)[:25]
            vote = np.zeros(len(rows))
            np.add.at(vote, mrow[top], sm[j, top] ** 2)
            score = sn[j] / (sn[j].max() + 1e-9) * 0.4 + vote / (vote.max() + 1e-9) * 0.6
            mask = np.ones(len(rows), bool)
            allow = OWN_BOOK.get(q.get("book", ""))
            if allow:
                mask[:] = False
                for bk in allow:
                    mask[book_rows[bk]] = True
            y = re.search(r"(19|20)\d\d", str(q.get("year") or q.get("exam") or ""))
            if y and int(y.group(0)) < 2024:  # old questions are not this year's current affairs
                mask[book_rows[6]] = False
            score = np.where(mask, score, -1)
            k = int(score.argmax())
            conf = float(max(sm[j, top].max(), sn[j, k] * 1.5))
            if conf < NEAR:
                off.append(q["id"])
                continue
            sub = best_match(secs[k], [q if q["a"] >= 0 else dict(q, a=0, o=[" ".join(q["o"])])])[0]
            placed[q["id"]] = [rows[k][0], rows[k][1], sub, round(conf, 3)]
    return placed, dup, off


def add(app, assets, new, placed, apply):
    byq = {q["id"]: q for q in new}
    by_row = defaultdict(list)
    for pid, (b, r, sub, _) in placed.items():
        by_row[(b, r)].append((sub, to_mcq(byq[pid])))
    if not apply:
        return
    index = json.load(open(f"{assets}/index.json"))
    for b in range(1, 7):
        path = f"{assets}/mcq{b}.json"
        m = json.load(open(path))
        rows = index["books"][b - 1]["rows"]
        for ri in range(len(rows)):
            extra = by_row.get((b, ri))
            if not extra:
                continue
            k = str(ri)
            qs, subs = m["rows"].get(k, []), m["subs"].get(k, [])
            subs = subs or [-1] * len(qs)
            have = {q["id"] for q in qs}
            extra = [(s, q) for s, q in extra if q["id"] not in have]
            cur = list(zip(subs, qs))
            order = sorted(set(s for s, _ in cur + extra), key=lambda s: (s < 0, s))
            merged = [x for s in order for x in [e for e in extra if e[0] == s] + [c for c in cur if c[0] == s]]
            m["rows"][k] = [q for _, q in merged]
            m["subs"][k] = [s for s, _ in merged]
            rows[ri]["q"] = len(merged)
        json.dump(m, open(path, "w"), ensure_ascii=False, separators=(",", ":"))
    open(f"{assets}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", assets], check=True)


def main():
    apply = "--apply" in sys.argv
    new, dropped = new_questions()
    print(f"read {len(new)} usable new questions; dropped: {dict(dropped)}")
    for app, assets in APPS.items():
        placed, dup, off = place(app, assets, new)
        json.dump({"placed": placed, "dup_of": dup, "off_syllabus": off, "dropped": dropped},
                  open(f"data/pyq/ocr2026/added-{app}.json", "w"), ensure_ascii=False)
        keyed = sum(1 for p in placed if next(q for q in new if q["id"] == p)["a"] >= 0)
        print(f"{app}: add {len(placed)} ({keyed} with key), already in the app {len(dup)}, off the syllabus {len(off)}"
              + ("" if apply else "  [dry run]"))
        add(app, assets, new, placed, apply)


if __name__ == "__main__":
    main()
