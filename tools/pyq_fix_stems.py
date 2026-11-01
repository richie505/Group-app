"""Repairs PYQs whose stem lost its opening line in the source ("Charter Act of 1813 2. General committee ... 3. ..."),
keeping every one of them:
- the same question in full elsewhere in the app (same four options): its full question text is used;
- the previous question's list run into this one ("... 5. Vanuatu 16. Diego Garcia is situated in"): the stem is
  the question after its own number;
- otherwise the lost "1." is put back, the statements go on lines of their own under "Consider the following:",
  with "Which of the above statements are correct?" when the question line is missing too.
Also strips scan marks from options ("✓" that gave the answer away, a stray "&" or quote).

    python3 tools/pyq_fix_stems.py
"""
import json, re, sys

sys.path.insert(0, "tools")
from pyq_apply import stem  # noqa: E402

ASK = re.compile(r"\?|\bselect\b|\bwhich\b|\bfind\b|\bhow many\b|\bchoose\b|\bcorrect\b|\barrange\b|\bidentify\b", re.I)


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def broken(q):
    s = q["s"]
    return (q["id"].startswith("y") and re.search(r"\s2\.\s", s) and not re.search(r"(?:^|\n)\s*1\.", s)
            and not re.match(r"(?i)\s*(?:consider|match|which|cop\b|with reference|arrange|assertion)", s))


HAND = {  # read by hand: the stem the source garbled
    "y60b65a58636": "NITI Aayog, which replaced the Planning Commission, was established through:",
}


def repair(q, same):
    if q["id"] in HAND:
        return HAND[q["id"]]
    if same:
        return same
    s = q["s"].strip()
    for m in re.finditer(r"\s(\d{1,3})\.\s+(?=[A-Z])", s):
        if int(m.group(1)) > 6 and not re.search(r"\s\d\.\s", s[m.end():]):
            return s[m.end():].strip()
    out = stem("Consider the following: 1. " + s)
    if not ASK.search(s):
        out += "\nWhich of the above statements are correct?"
    return out


def main():
    for app in ("main", "complete"):
        A = f"app/src/{app}/assets"
        index = json.load(open(f"{A}/index.json"))
        books = [json.load(open(f"{A}/mcq{b}.json")) for b in range(1, 7)]
        full = {}  # options -> a sound stem of the same question
        for m in books:
            for qs in m["rows"].values():
                for q in qs:
                    if not broken(q):
                        full.setdefault(tuple(norm(o) for o in q["o"]), q["s"])
        dropped = fixed = marks = 0
        for b, m in enumerate(books, 1):
            for k in list(m["rows"]):
                qs, subs = m["rows"][k], m["subs"].get(k)
                keep_q, keep_s = [], []
                for i, q in enumerate(qs):
                    o2 = [re.sub(r'^\s*(?:✓|&|")\s*', "", o) for o in q["o"]]
                    if o2 != q["o"]:
                        q["o"], marks = o2, marks + 1
                    if broken(q):
                        q["s"] = repair(q, full.get(tuple(norm(o) for o in q["o"])))
                        fixed += 1
                    keep_q.append(q)
                    if subs:
                        keep_s.append(subs[i])
                m["rows"][k] = keep_q
                if subs:
                    m["subs"][k] = keep_s
                index["books"][b - 1]["rows"][int(k)]["q"] = len(keep_q)
            json.dump(m, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        print(app, "stems repaired:", fixed, "options cleaned:", marks)


if __name__ == "__main__":
    main()
