"""Cross-topic repeats left after the per-batch trim (each batch only saw its own topics).

    python3 tools/mcq_trim_xdup_export.py <book> [threshold]
Reads the imported app/src/main/assets/mcq<book>.json, finds pairs of MCQs in different topics that test
the same fact (stem + answer + explanation similarity), and writes work/mcqtrim/b<book>/xdup_in_NNN.md.
An agent answers in xdup_out_NNN.jsonl, one line per pair:
    {"p":12,"drop":"n1234abcd567"}   drop that MCQ (the pair tests one fact; keep the better / better-placed one)
    {"p":13,"drop":null}             keep both (different facts, or a different angle worth testing)
tools/mcq_trim_import.py drops the chosen ids when it rebuilds the book.
"""
import json, os, sys
from sklearn.feature_extraction.text import TfidfVectorizer

book = int(sys.argv[1])
thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
d = f"work/mcqtrim/b{book}"
notes = json.load(open(f"app/src/main/assets/book{book}.json"))
titles = [r["title"] for u in notes["units"] for r in u["rows"]]
mcq = json.load(open(f"app/src/main/assets/mcq{book}.json"))
qs = [(int(r), q) for r, lst in mcq["rows"].items() for q in lst]


def fact(q):
    return q["s"] + " " + q["o"][q["a"]] + " " + q.get("x", "")


X = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english", min_df=1).fit_transform([fact(q) for _, q in qs])
pairs = []
for s in range(0, X.shape[0], 2000):
    sim = (X[s:s + 2000] @ X.T).tocsr()
    for i in range(sim.shape[0]):
        a = s + i
        st, en = sim.indptr[i], sim.indptr[i + 1]
        for b, v in zip(sim.indices[st:en], sim.data[st:en]):
            if b > a and v >= thr and qs[a][0] != qs[b][0]:
                pairs.append((float(v), a, int(b)))
pairs.sort(reverse=True)


def show(k, a):
    r, q = qs[a]
    lines = [f"  {k} [{q['id']}] topic {r}: {titles[r]}", f"    {q['s']}"]
    lines += [f"    {'ABCD'[i]}) {o}" for i, o in enumerate(q["o"])]
    lines.append(f"    ANSWER: {'ABCD'[q['a']]}")
    return "\n".join(lines)


for f in os.listdir(d):
    if f.startswith("xdup_in_"):
        os.remove(f"{d}/{f}")
per, n = 150, 0
for k in range(0, len(pairs), per):
    chunk = [f"=== PAIR {k + i} (similarity {v:.2f})\n{show('A', a)}\n{show('B', b)}" for i, (v, a, b) in enumerate(pairs[k:k + per])]
    open(f"{d}/xdup_in_{n:03d}.md", "w").write("\n\n".join(chunk) + "\n")
    n += 1
print(f"book {book}: {len(qs)} MCQs, {len(pairs)} cross-topic pairs >= {thr} in {n} batches")
