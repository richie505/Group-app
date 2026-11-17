"""Complete: notes MCQs (the app's own) that may test the same fact as a PYQ of the same topic.
Writes data/pyqrepeat/cand.jsonl: {id, row, notes:{s,o,a}, pyqs:[{id,s,o,a,src,score}]} for helpers to judge.
Current-affairs / latest MCQs (ids "ca...", src "ca", tags updated/added) are never candidates.

    python3 tools/pyq_repeat_candidates.py [min score=0.3]
"""
import json, sys, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

A = "app/src/complete/assets"
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3


def text(q):
    ans = q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q.get("o", [])) else ""
    return f"{q['s']} {ans} {ans}"


def keep(q):
    return q["id"].startswith("ca") or q.get("src") == "ca" or {"updated", "added"} & set(q.get("tg", []))


docs = []
for b in range(1, 7):
    for r, qs in json.load(open(f"{A}/mcq{b}.json"))["rows"].items():
        for q in qs:
            docs.append(text(q))
vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, sublinear_tf=True).fit(docs)
out, stat = [], {"notes": 0, "protected": 0}
for b in range(1, 7):
    for r, qs in json.load(open(f"{A}/mcq{b}.json"))["rows"].items():
        py = [q for q in qs if q["id"].startswith("y")]
        nq = [q for q in qs if not q["id"].startswith("y")]
        stat["notes"] += len(nq)
        if not py or not nq:
            continue
        S = cosine_similarity(vec.transform([text(q) for q in nq]), vec.transform([text(q) for q in py]))
        for i, q in enumerate(nq):
            if keep(q):
                stat["protected"] += 1
                continue
            best = sorted(range(len(py)), key=lambda j: -S[i, j])[:3]
            best = [j for j in best if S[i, j] >= MIN]
            if best:
                f = lambda x: {k: x.get(k) for k in ("id", "s", "o", "a", "src")}
                out.append({"id": q["id"], "row": [b, int(r)], "notes": f(q),
                            "pyqs": [dict(f(py[j]), score=round(float(S[i, j]), 2)) for j in best]})
open("data/pyqrepeat/cand.jsonl", "w").write("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
print(stat, "candidates", len(out))
