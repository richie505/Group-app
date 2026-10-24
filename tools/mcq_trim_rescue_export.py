"""Second look at MCQs the trim dropped as "off" (not in their own topic's notes): another topic's notes may
hold the fact. For each such MCQ, shows the three best-matching subsections of other topics (their most
relevant notes lines). An agent answers in rescue_out_NNN.jsonl:
    {"q":"Q19.60","to":"20.3"}   file it under topic 20, subsection 3 (the notes there support it and its key)
    {"q":"Q19.62","to":null}     leave it dropped
tools/mcq_trim_import.py applies the moves (skipping ones that repeat an MCQ already in the target topic).

    python3 tools/mcq_trim_rescue_export.py <book> [MCQs per batch]
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks
from sklearn.feature_extraction.text import TfidfVectorizer

book = int(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 120
A = os.environ.get("TRIM_ASSETS", "app/src/main/assets")  # APPSC Complete: app/src/complete/assets
d = os.environ.get("TRIM_DIR", "work/mcqtrim") + f"/b{book}"
notes = json.load(open(f"{A}/book{book}.json"))
orig = f"{d}/orig.json"
mcq = json.load(open(orig if os.path.exists(orig) else f"{A}/mcq{book}.json"))
rows = [r for u in notes["units"] for r in u["rows"]]
subs = []
for ri, r in enumerate(rows):
    for si, s in enumerate(r["secs"]):
        md, _ = from_blocks(s["b"], inline_tables=True)
        subs.append((ri, si, f"{r['title']} > {s['t']}", [l for l in md.splitlines() if l.strip()]))

offs = []
for f in sorted(os.listdir(d)):
    if f.startswith("out_") and f.endswith(".jsonl"):
        for line in open(f"{d}/{f}"):
            if line.strip():
                o = json.loads(line)
                if o.get("d") == "drop" and str(o.get("why", "")).startswith("off"):
                    offs.append(o["q"])

V = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
S = V.fit_transform([t + "\n" + "\n".join(ls) for _, _, t, ls in subs])
words = lambda s: {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def show(label):
    r, j = map(int, label[1:].split("."))
    q = mcq["rows"][str(r)][j]
    text = q["s"] + " " + q["o"][q["a"]] + " " + q.get("x", "")
    sim = (V.transform([text]) @ S.T).toarray()[0]
    cands = [i for i in sim.argsort()[::-1] if subs[i][0] != r][:3]
    key = words(text)
    out = [f"[{label}] (from topic {r}: {rows[r]['title']})", q["s"]]
    out += [f"  {'ABCD'[i]}) {o}" for i, o in enumerate(q["o"])]
    out.append(f"  ANSWER: {'ABCD'[q['a']]}")
    if q.get("x"):
        out.append(f"  WHY: {q['x']}")
    for i in cands:
        ri, si, title, ls = subs[i]
        best = sorted(ls, key=lambda l: -len(words(l) & key))[:6]
        out.append(f"  --- candidate {ri}.{si} | {title} (match {sim[i]:.2f})")
        out += [f"    {l[:300]}" for l in best]
    return "\n".join(out)


for f in os.listdir(d):
    if f.startswith("rescue_in_"):
        os.remove(f"{d}/{f}")
n = 0
for k in range(0, len(offs), limit):
    open(f"{d}/rescue_in_{n:03d}.md", "w").write("\n\n".join(show(q) for q in offs[k:k + limit]) + "\n")
    n += 1
print(f"book {book}: {len(offs)} off-notes MCQs in {n} rescue batches")
