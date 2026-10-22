"""Which Prep current-affairs topic each CA-app page goes to, and which CA-app pages each Prep CA page repeats.

    python3 tools/ca_map.py <CA app assets dir> > work/merge/ca_map.json
The CA app (books 11-16: periods -> months -> 11 categories -> one page per news item) is the base for current
affairs; Prep's book 6 (18 syllabus topics) gives the layout. Each CA page goes to a Prep CA topic its category
allows, the one whose text it shares most rare words with (TF-IDF). Each Prep CA page gets its closest CA pages.
Output: {"ca": [{"b", "r", "s", "month", "cat", "title", "md", "to", "score"}],
         "prep": [{"r", "s", "title", "md", "near": [[ca index, score], ...]}]}
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from merge_map import rows_of, page_md
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

PREP = Path("app/src/main/assets")
# CA category -> the Prep book-6 topics (rows) it may go to
ALLOWED = {
    "Andhra Pradesh": [0, 1, 2, 3],
    "Polity & Governance": [4, 7],
    "Economy, Banking & Budget": [5, 7],
    "Schemes & Social Sector": [6, 7],
    "International Relations": [8, 9, 10],
    "Science, Tech, Space & Defence": [11],
    "Environment & Geography": [12],
    "Reports, Indices & Rankings": [13],
    "Awards, Persons & Appointments": [14, 17],
    "Sports": [15],
    "Important Days & Events": [16],
    # special topics
    "Budgets, Finance Commission & NITI Aayog": [1, 5, 7],
    "Awards & Honours": [14],
    "Environment": [12],
    "Polity, Elections & Society": [4],
    "Reports & Indices": [13],
}


def main():
    ca_dir = Path(sys.argv[1])
    prep_rows = rows_of(PREP / "book6.json")
    row_text = [r["title"] + " " + " ".join(s["t"] + " " + page_md(s) for s in r["secs"]) for r in prep_rows]
    ca = []
    for b in range(11, 17):
        d = json.loads((ca_dir / f"book{b}.json").read_text())
        gi = 0
        for u in d["units"]:
            for r in u["rows"]:
                for si, s in enumerate(r["secs"]):
                    ca.append({"b": b, "r": gi, "s": si, "month": u["title"], "cat": r["title"], "title": s["t"], "md": page_md(s)})
                gi += 1
    prep = [{"r": ri, "s": si, "title": s["t"], "md": page_md(s)} for ri, r in enumerate(prep_rows) for si, s in enumerate(r["secs"])]
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), max_df=0.3, token_pattern=r"(?u)\b[A-Za-z0-9][A-Za-z0-9-]+\b")
    vec.fit(row_text + [x["title"] + " " + x["md"] for x in ca])
    R = vec.transform(row_text)
    C = vec.transform([x["title"] + " " + x["title"] + " " + x["md"] for x in ca])
    P = vec.transform([x["title"] + " " + x["title"] + " " + x["md"] for x in prep])
    to_row = linear_kernel(C, R)
    for x, sims in zip(ca, to_row):
        allowed = ALLOWED.get(x["cat"], list(range(len(prep_rows))))
        best = max(allowed, key=lambda j: sims[j])
        x["to"], x["score"] = best, round(float(sims[best]), 3)
    near = linear_kernel(P, C)
    for x, sims in zip(prep, near):
        top = sorted(range(len(ca)), key=lambda j: -sims[j])[:5]
        x["near"] = [[j, round(float(sims[j]), 3)] for j in top]
    json.dump({"ca": ca, "prep": prep}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
