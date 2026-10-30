"""Links between APPSC Complete's MCQs and the one-liners APPSC One-liners made from them, so a backup of either
app restores in the other (ProgressStore.restore).

    python3 tools/build_mcq_links.py

A one-liner kept as it was has the same id in both apps. A made one-liner (id "o...") came from one of its topic's
Complete MCQs that the One-liners app does not have: the one sharing most of its words (the answer's twice).
Writes mcqlinks.json into both apps' assets:
- app/src/oneliner/assets: {Complete MCQ id: [its one-liners' ids]};
- app/src/complete/assets: {one-liner id: [the Complete MCQ it came from]}.
"""
import json, math, re
from collections import Counter, defaultdict

C, O = "app/src/complete/assets", "app/src/oneliner/assets"
STOP = set("""the a an of and or in to for by with is was as at from on which who what when where how not no its it this that
these those be been are were has have had into under over also only first one two three following correct statement""".split())


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", t.lower()) if (len(w) > 2 or w.isdigit()) and w not in STOP]


def main():
    to_lines, to_mcq = defaultdict(list), {}
    tally = Counter()
    for b in range(1, 7):
        cm = json.load(open(f"{C}/mcq{b}.json"))["rows"]
        om = json.load(open(f"{O}/mcq{b}.json"))["rows"]
        for r, lines in om.items():
            mine = {q["id"] for q in lines}
            sources = [q for q in cm.get(r, []) if q["id"] not in mine]  # rewritten as one-liners
            bags = [Counter(words(q["s"] + " " + " ".join(q["o"]))) for q in sources]
            df = Counter(w for c in bags for w in c)
            idf = {w: math.log(1 + len(bags) / n) for w, n in df.items()}
            for q in lines:
                if not q["id"].startswith("o"):
                    tally["same question"] += 1
                    continue
                stem, ans = sorted(set(words(q["s"]))), sorted(set(words(q["o"][q["a"]])))
                best, at = 0.0, -1
                for i, c in enumerate(bags):
                    s = sum(idf[w] for w in stem if w in c) + 2 * sum(idf[w] for w in ans if w in c)
                    if s > best:
                        best, at = s, i
                if at < 0:
                    tally["no source found"] += 1
                    continue
                src = sources[at]["id"]
                to_lines[src].append(q["id"])
                to_mcq[q["id"]] = [src]
                tally["linked"] += 1
    json.dump(dict(sorted(to_lines.items())), open(f"{O}/mcqlinks.json", "w"), separators=(",", ":"))
    json.dump(dict(sorted(to_mcq.items())), open(f"{C}/mcqlinks.json", "w"), separators=(",", ":"))
    print(", ".join(f"{k} {v}" for k, v in tally.items()), f"; {len(to_lines)} Complete MCQs have one-liners")


if __name__ == "__main__":
    main()
