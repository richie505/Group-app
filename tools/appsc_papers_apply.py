"""Full official APPSC papers of other exams (data/appscpapers/*.json: Group 1 Prelims, Panchayat Secretary, Forest,
Lecturers... - their General Studies questions) added to APPSC Complete's MCQs as PYQs:
- each question goes into the best-matching section and subsection of its subject's book (TF-IDF over the section's
  titles, notes and MCQs), as "y" + id (a PYQ), source "<paper> · Q<n>";
- the older partial copies of the same exam's questions (same year, same question) are left out;
- question + answer papers (only the keyed answer printed) become question + answer cards.
Idempotent: the questions it added before are taken out first. Group 2 takes them from here (tools/group2_build.py).

    python3 tools/appsc_papers_apply.py [assets dir=app/src/complete/assets]
"""
import difflib, glob, hashlib, json, os, re, sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
TAG = "yQ"  # ids of the questions this tool adds (capital Q: never in an existing hex id)
BOOK = {"History": 1, "AP History & Culture": 1, "Polity": 2, "Indian Society": 2, "Economy": 3, "Geography": 4,
        "Science & Technology": 5, "Current Affairs": 6}
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def papers():
    out = []
    for f in sorted(glob.glob("data/appscpapers/*.json")):
        p = json.load(open(f))
        name = p.get("paper") or os.path.basename(f)[:-5]
        slug = os.path.basename(f)[:-5]
        for q in p.get("questions", []):
            qid = TAG + hashlib.md5(f"{slug}|{q['n']}".encode()).hexdigest()[:10]
            o = {"id": qid, "s": q["s"], "src": f"{name} · Q{q['n']}", "ap": 1, "x": q.get("x", "")}
            if "o" in q:
                o |= {"o": q["o"], "a": q["a"]}
                if q.get("deleted") or q["a"] < 0:
                    o |= {"k": "u", "cx": 1, "a": -1}
            else:
                o |= {"o": ["Knew it", "Did not know"], "a": 0, "k": "f", "at": q.get("answer", "")}
                if q.get("deleted") or not q.get("answer"):
                    o |= {"k": "u", "cx": 1}
            if q.get("deleted"):
                o["x"] = "Deleted by APPSC in the final key. " + o["x"]
            out.append((o, q.get("subject", "General Studies"), str(p.get("date", ""))[:4]))
    return out


new = papers()
m = {b: json.load(open(f"{A}/mcq{b}.json")) for b in range(1, 7)}
books = {b: json.load(open(f"{A}/book{b}.json")) for b in range(1, 7)}
# take out what this tool added before
for b in m:
    for r, qs in m[b]["rows"].items():
        subs = m[b]["subs"].get(r) or [-1] * len(qs)
        keep = [(q, s) for q, s in zip(qs, subs) if not q["id"].startswith(TAG)]
        m[b]["rows"][r] = [q for q, _ in keep]
        if r in m[b]["subs"]:
            m[b]["subs"][r] = [s for _, s in keep]
if new:
    # the places: every subsection of every section, as text
    docs, place = [], []
    for b in range(1, 7):
        rows = [r for u in books[b]["units"] for r in u["rows"]]
        for ri, row in enumerate(rows):
            qs = m[b]["rows"].get(str(ri), [])
            subs = m[b]["subs"].get(str(ri)) or [-1] * len(qs)
            for si, sec in enumerate(row["secs"]):
                text = [row["title"], sec["t"]] + ["".join(t for t, _ in bl.get("x") or []) for bl in sec["b"] if bl.get("x")]
                text += [q["s"] for q, s in zip(qs, subs) if s == si]
                docs.append(" ".join(text))
                place.append((b, ri, si))
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=1).fit(docs)
    D = vec.transform(docs)
    # older copies of the same exam's questions (same year in the source, nearly the same wording)
    years = {y for _, _, y in new if y}
    old = {}
    for b in m:
        for r, qs in m[b]["rows"].items():
            for q in qs:
                if q["id"].startswith("y") and any(y in (q.get("src") or "") for y in years):
                    old[q["id"]] = norm(q["s"])
    newn = [norm(o["s"]) for o, _, _ in new]
    copies = {i for i, s in old.items() if len(s) > 15 and any(abs(len(t) - len(s)) < 0.3 * len(s) and
              difflib.SequenceMatcher(None, s, t).ratio() > 0.85 for t in newn)}
    for b in m:
        for r, qs in m[b]["rows"].items():
            subs = m[b]["subs"].get(r) or [-1] * len(qs)
            keep = [(q, s) for q, s in zip(qs, subs) if q["id"] not in copies]
            m[b]["rows"][r] = [q for q, _ in keep]
            if r in m[b]["subs"]:
                m[b]["subs"][r] = [s for _, s in keep]
    Q = vec.transform([o["s"] + " " + (o.get("at") or (o["o"][o["a"]] if o.get("a", -1) >= 0 else "")) for o, _, _ in new])
    S = cosine_similarity(Q, D)
    for i, (o, subj, _) in enumerate(new):
        want = BOOK.get(subj)
        best = max((j for j in range(len(place)) if want is None or place[j][0] == want), key=lambda j: S[i, j])
        b, ri, si = place[best]
        m[b]["rows"].setdefault(str(ri), []).append(o)
        m[b]["subs"].setdefault(str(ri), [-1] * (len(m[b]["rows"][str(ri)]) - 1)).append(si)
    print(f"{A}: {len(new)} questions of {len(glob.glob('data/appscpapers/*.json'))} papers added; {len(copies)} older copies left out")
for b in m:
    open(f"{A}/mcq{b}.json", "w").write(json.dumps(m[b], ensure_ascii=False, separators=(",", ":")))
ix = json.load(open(f"{A}/index.json"))
for b, book in enumerate(ix["books"], 1):
    for ri, r in enumerate(book["rows"]):
        r["q"] = len(m[b]["rows"].get(str(ri), []))
open(f"{A}/index.json", "w").write(json.dumps(ix, ensure_ascii=False, separators=(",", ":")))
