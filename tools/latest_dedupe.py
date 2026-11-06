"""The latestpyqs books (data/pyq/new/latest-*.jsonl) repeat many questions the apps already have, often as clean
copies of OCR-garbled bank ones. A book question is a repeat when its text is close (TF-IDF cosine >= 0.5) to a PYQ
already in Prep, Complete or Group 2; repeats are listed in data/pyq/latest/dup_of_app.json and left out. Run before
tools/pyq_place.py whenever the books' files change.

    python3 tools/latest_dedupe.py
"""
import json, os, sys
sys.path.insert(0, "tools")
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402

P = "data/pyq/latest/dup_of_app.json"
if os.path.exists(P):
    os.remove(P)  # list every book question while deciding
from pyq_place import bank  # noqa: E402
from pyq_apply import to_mcq  # noqa: E402

inapp = set()
for app in ["complete", "main", "group2"]:
    for b in range(1, 7):
        for qs in json.load(open(f"app/src/{app}/assets/mcq{b}.json"))["rows"].values():
            inapp.update(q["id"] for q in qs if q["id"].startswith("y"))
old, new = [], []
for line in bank():
    q = json.loads(line)
    (new if q["id"].startswith("latest") else old).append(q)
oldin = [q for q in old if to_mcq(q)["id"] in inapp]
T = lambda q: q["s"] + " " + " ".join(q.get("o", []))
v = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit([T(q) for q in old + new])
O, N = v.transform([T(q) for q in oldin]), v.transform([T(q) for q in new])
dup = []
for i in range(0, N.shape[0], 300):
    best = (N[i:i + 300] @ O.T).toarray().max(1)
    dup += [new[i + k]["id"] for k, b in enumerate(best) if b >= 0.5]
json.dump(sorted(dup), open(P, "w"))
print(f"book questions {len(new)}, already in the apps {len(dup)}, new {len(new) - len(dup)}")
