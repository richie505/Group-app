"""ROCKET MCQs into the merged topics: each follows its ROCKET block to the merged page that holds it.

    MERGE_ASSETS=app/src/complete/assets python3 tools/merge_mcqs.py <rocket assets dir> <book>
For every merged topic (work/merge/b<book>/out_*.md, imported): a ROCKET MCQ of a sheet page whose blocks went
into this topic is filed under the page whose "from:" names the block it is closest to (words shared with the
question, answer and explanation). An MCQ that repeats one already in the topic (same answer, most of the
question's words) is left out. Run after tools/topic_import.py (MERGE=1).
"""
import glob, json, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from merge_check import split_in, not_here, heads
from topic_check import topics

A = os.environ.get("MERGE_ASSETS", "app/src/complete/assets")


def words(s):
    return Counter(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2)


def overlap(a, b):
    return sum(min(c, b[w]) for w, c in a.items())


def key(q):
    return " ".join(sorted(words(q["s"]))), re.sub(r"\W", "", q["o"][q["a"]].lower())


def same(q, r):
    a, b = set(words(q["s"])), set(words(r["s"]))
    return re.sub(r"\W", "", q["o"][q["a"]].lower()) == re.sub(r"\W", "", r["o"][r["a"]].lower()) and \
        len(a & b) >= 0.7 * max(1, min(len(a), len(b)))


def main():
    rocket, book = sys.argv[1], int(sys.argv[2])
    allmap = json.load(open("work/merge/rocket_map.json"))
    rmap = [x for x in allmap if x["to"][0] == book]
    # every block of a ROCKET sheet page, wherever it went: an MCQ belongs to the block it is closest to
    page_blocks = {}
    for x in allmap:
        page_blocks.setdefault((x["rb"], x["rr"], x["rs"]), []).append(x)
    rmcq = {b: json.load(open(f"{rocket}/mcq{b}.json")) for b in range(1, 6)}
    mcq = json.load(open(f"{A}/mcq{book}.json"))
    d = f"work/merge/b{book}"
    added = dup = 0
    done = json.load(open(f"{d}/imported.json"))
    for f in sorted(glob.glob(f"{d}/out_*.md")):
        n = f[-6:-3]
        text = open(f).read()
        old, back = split_in(open(f"{d}/in_{n}.md").read()), not_here(text)
        new = topics(re.sub(r"(?m)^=== NOT HERE:.*$", "", text))
        for ri in new:
            if str(ri) not in done:
                continue
            blocks = [x for x in rmap if x["to"][1] == ri]  # R<n> = n-th block of this topic, as exported
            pages = [heads(h) for h, _ in new[ri][1]]
            page_words = [words(b) for _, b in new[ri][1]]
            qs, subs = mcq["rows"].setdefault(str(ri), []), mcq["subs"].setdefault(str(ri), [])
            # the ROCKET sheet pages behind this topic's blocks, and which R numbers each holds
            by_page = {}
            for r_no, x in enumerate(blocks):
                if r_no in back.get(ri, set()):
                    continue
                by_page.setdefault((x["rb"], x["rr"], x["rs"]), []).append(r_no)
            for (rb, rr, rs), r_nos in by_page.items():
                m = rmcq[rb]
                for q, sub in zip(m["rows"].get(str(rr), []), m["subs"].get(str(rr), [])):
                    if sub != rs:
                        continue
                    qw = words(q["s"] + " " + q["o"][q["a"]] + " " + q.get("x", ""))
                    home = max(page_blocks[(rb, rr, rs)], key=lambda x: overlap(qw, words(x["md"])))
                    if home["to"][:2] != [book, ri] or blocks.index(home) not in r_nos:
                        continue  # tests a block that went to another topic
                    r_best = blocks.index(home)
                    if any(same(q, o) for o in qs):
                        dup += 1
                        continue
                    cands = [j for j, (_, _, rs_, _) in enumerate(pages) if r_best in rs_] or list(range(len(pages)))
                    j = max(cands, key=lambda j: overlap(qw, page_words[j]))
                    qs.append(dict(q, src="rocket"))
                    subs.append(j)
                    added += 1
    open(f"{A}/mcq{book}.json", "w").write(json.dumps(mcq, ensure_ascii=False, separators=(",", ":")))
    print(f"book {book}: {added} ROCKET MCQs added, {dup} left out as repeats")


if __name__ == "__main__":
    main()
