"""Which Prep topic each ROCKET-sheet block belongs to (first step of merging the three apps' notes).

    python3 tools/merge_map.py <rocket assets dir> > work/merge/rocket_map.json
A block is one heading of a ROCKET page ("# 1. Basics" and its bullets / table). Each block is matched to the
Prep page (book, row, sec) whose text it shares most rare words with (TF-IDF cosine), within the Prep book that
covers the same subject. Output: [{"rb": rocket book, "rr": row, "rs": sec, "k": block no, "title", "md",
"to": [book, row, sec], "score", "alt": [[book, row, sec, score], ...]}]
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from structured_md import from_blocks
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

PREP = Path("app/src/main/assets")
# ROCKET book -> Prep books it may go to (by subject)
SUBJECT = {1: [1], 2: [2], 3: [3], 4: [4], 5: [5, 4]}


def rows_of(path):
    d = json.loads(Path(path).read_text())
    return [r for u in d["units"] for r in u["rows"]]


def page_md(s):
    md, _ = from_blocks(s["b"], inline_tables=True)
    return re.sub(r"(?m)^~~.*$", "", md).strip()


def blocks_of(md):
    """Split a page at its '# ' headings; text before the first heading is its own block."""
    out, cur = [], []
    for line in md.splitlines():
        if line.startswith("# ") and cur:
            out.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [b for b in out if re.search(r"[A-Za-z]{3}", b)]


def main():
    rocket = Path(sys.argv[1])
    prep_pages, prep_text = [], []
    for b in range(1, 7):
        for ri, r in enumerate(rows_of(PREP / f"book{b}.json")):
            for si, s in enumerate(r["secs"]):
                prep_pages.append((b, ri, si))
                prep_text.append(f"{r['title']} {s['t']} {s['t']} " + page_md(s))
    items = []
    for rb in range(1, 6):
        for ri, r in enumerate(rows_of(rocket / f"book{rb}.json")):
            for si, s in enumerate(r["secs"]):
                for k, md in enumerate(blocks_of(page_md(s))):
                    items.append({"rb": rb, "rr": ri, "rs": si, "k": k, "title": f"{r['title']} / {s['t']}", "md": md})
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=1, max_df=0.3, token_pattern=r"(?u)\b[A-Za-z0-9][A-Za-z0-9-]+\b")
    P = vec.fit_transform(prep_text)
    Q = vec.transform([f"{x['title']} {x['md']}" for x in items])
    sims = linear_kernel(Q, P)
    for x, row in zip(items, sims):
        allowed = SUBJECT[x["rb"]]
        cand = sorted(((row[j], prep_pages[j]) for j in range(len(prep_pages)) if prep_pages[j][0] in allowed), reverse=True)[:4]
        x["to"], x["score"] = list(cand[0][1]), round(float(cand[0][0]), 3)
        x["alt"] = [list(p) + [round(float(sc), 3)] for sc, p in cand[1:]]
    json.dump(items, sys.stdout, ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
