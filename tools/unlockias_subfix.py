"""Unlock IAS PYQs that tools/unlockias_add.py left at section level (no subsection shared enough words with them):
each goes to the subsection of its section whose notes and MCQs are closest (TF-IDF), first among that
subsection's questions, as the other PYQs are filed. Idempotent. Run tools/unlockias_g2fields.py after it.

    python3 -X utf8 tools/unlockias_subfix.py
"""
import hashlib, json, sys

from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, "tools")
from pyq_place import sec_text  # noqa: E402

for app in ("complete", "group1", "group2"):
    A = f"app/src/{app}/assets"
    new = {"y" + hashlib.sha1(k.encode()).hexdigest()[:11] for k in json.load(open(f"data/pyq/unlockias/added-{app}.json"))["placed"]}
    moved = left = 0
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        rows = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        for r, qs in m["rows"].items():
            subs = m["subs"].get(r) or [-1] * len(qs)
            todo = [i for i, (q, s) in enumerate(zip(qs, subs)) if s < 0 and q["id"] in new]
            if not todo:
                continue
            secs = rows[int(r)]["secs"]
            docs = [sec_text(s) + " " + " ".join(q["s"] for q, sb in zip(qs, subs) if sb == j) for j, s in enumerate(secs)]
            ok = [j for j, d in enumerate(docs) if len(d) > 200]   # hidden / empty pages take none
            if not ok:
                left += len(todo); continue
            vec = TfidfVectorizer(stop_words="english", sublinear_tf=True).fit([docs[j] for j in ok] + [qs[i]["s"] for i in todo])
            D = vec.transform([docs[j] for j in ok])
            for i in todo:
                sim = (vec.transform([qs[i]["s"] + " " + " ".join(qs[i]["o"])]) @ D.T).toarray()[0]
                subs[i] = ok[int(sim.argmax())]; moved += 1
            order = sorted(range(len(qs)), key=lambda i: ((subs[i] < 0, subs[i]), not (i in todo), i))
            m["rows"][r] = [qs[i] for i in order]; m["subs"][r] = [subs[i] for i in order]
        open(f"{A}/mcq{b}.json", "w", encoding="utf8").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    print(app, "moved into a subsection", moved, "left at section level", left)
