"""Second round of the ROCKET merge: the blocks a topic sent back ("=== NOT HERE") go to the topic they fit.

    python3 tools/merge_reroute.py triage
        -> work/merge2/triage_<book>.md: every sent-back block (id, the topic that sent it back, the likeliest
           topics, its text) and work/merge2/topics.md (every topic of books 1-5, as <book>:<row> | title)
        an agent answers in work/merge2/triage_<book>.out, one line per block:
            <id> -> <book>:<row>     the block belongs to that topic
            <id> -> drop              not in the APPSC syllabus (general science, world trivia), or already in
                                      the notes word for word
    python3 tools/merge_reroute.py build [words per batch=9000]
        -> work/merge/rocket_map2.json (every block; a rerouted one has its new "to" and "r2": 1) and
           work/merge2/b<book>/in_NNN.md, in tools/merge_export.py's form, from the merged notes as they are now.
Then the same agents (tools/merge_guide.md), TOPIC_DIR=work/merge2 python3 tools/merge_check.py, and
MERGE=1 TOPIC_DIR=work/merge2 tools/topic_import.py; ROCKET MCQs with
ROUND2=1 MERGE_MAP=work/merge/rocket_map2.json TOPIC_DIR=work/merge2 tools/merge_mcqs.py.
"""
import glob, json, os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from merge_check import not_here
from topic_export import topic

A = os.environ.get("MERGE_ASSETS", "app/src/complete/assets")
W = "work/merge2"


def rows_of(book):
    return [r for u in json.load(open(f"{A}/book{book}.json"))["units"] for r in u["rows"]]


def sent_back(m):
    """map index -> the (book, row) that sent it back."""
    out = {}
    for b in range(1, 6):
        mine = defaultdict(list)
        for i, x in enumerate(m):
            if x["to"][0] == b:
                mine[x["to"][1]].append(i)
        for f in glob.glob(f"work/merge/b{b}/out_*.md") + glob.glob(f"work/merge/b{b}_pilot/out_*.md"):
            for ri, rs in not_here(open(f).read()).items():
                for r in rs:
                    if r < len(mine[ri]):
                        out[mine[ri][r]] = (b, ri)
    return out


def triage():
    m = json.load(open("work/merge/rocket_map.json"))
    back = sent_back(m)
    titles = {b: [r["title"] for r in rows_of(b)] for b in range(1, 6)}
    os.makedirs(W, exist_ok=True)
    with open(f"{W}/topics.md", "w") as f:
        for b in range(1, 6):
            f.write(f"# Book {b}\n" + "".join(f"{b}:{ri} | {t}\n" for ri, t in enumerate(titles[b])))
    per = defaultdict(list)
    for i, (b, ri) in sorted(back.items()):
        x = m[i]
        cands = []
        for ab, ar, _, sc in x.get("alt", []):
            if (ab, ar) != (b, ri) and (ab, ar) not in [c[:2] for c in cands] and ab <= 5:
                cands.append((ab, ar, sc))
        lines = [f"## B{i} | {x['title']}", f"sent back by {b}:{ri} | {titles[b][ri]}"]
        lines += [f"maybe {ab}:{ar} | {titles[ab][ar]}" for ab, ar, _ in cands[:4]]
        per[b].append("\n".join(lines) + "\n" + x["md"].strip())
    for b, items in per.items():
        open(f"{W}/triage_{b}.md", "w").write("\n\n".join(items) + "\n")
        print(f"book {b}: {len(items)} blocks -> {W}/triage_{b}.md")


def build(limit=9000):
    m = json.load(open("work/merge/rocket_map.json"))
    back = sent_back(m)
    moves, drops, bad = {}, 0, []
    for f in sorted(glob.glob(f"{W}/triage_*.out")):
        for line in open(f):
            g = re.match(r"\s*B?(\d+)\s*->\s*(drop|(\d+):(\d+))", line)
            if not g:
                continue
            i = int(g.group(1))
            if i not in back:
                bad.append(f"B{i} was not sent back")
            elif g.group(2) == "drop":
                drops += 1
            else:
                moves[i] = (int(g.group(3)), int(g.group(4)))
    missing = [i for i in back if i not in moves and not any(
        re.match(rf"\s*B?{i}\s*->", l) for f in glob.glob(f"{W}/triage_*.out") for l in open(f))]
    if bad or missing:
        print("\n".join(bad) + (f"\nno answer for {len(missing)} blocks: " + ", ".join(f"B{i}" for i in missing[:20])
                                if missing else ""))
        sys.exit(1)
    for i, (b, ri) in moves.items():
        m[i] = dict(m[i], to=[b, ri, 0], r2=1)
    json.dump(m, open("work/merge/rocket_map2.json", "w"), ensure_ascii=False)
    for b in range(1, 6):
        rows = rows_of(b)
        by_row = defaultdict(list)
        for x in m:
            if x.get("r2") and x["to"][0] == b:
                by_row[x["to"][1]].append(x)
        d = f"{W}/b{b}"
        os.makedirs(d, exist_ok=True)
        for f in glob.glob(f"{d}/in_*.md"):
            os.remove(f)
        batches, cur, words = [], [], 0
        for ri in sorted(by_row):
            rk = [f"## R{n} | {x['title']}\n{x['md'].strip()}" for n, x in enumerate(by_row[ri])]
            text = topic(ri, rows[ri]) + "\n\n=== ROCKET\n\n" + "\n\n".join(rk)
            w = len(text.split())
            if cur and words + w > limit:
                batches.append(cur)
                cur, words = [], 0
            cur.append(text)
            words += w
        if cur:
            batches.append(cur)
        for k, bt in enumerate(batches):
            open(f"{d}/in_{k:03d}.md", "w").write("\n\n".join(bt) + "\n")
        print(f"book {b}: {sum(len(v) for v in by_row.values())} blocks into {len(by_row)} topics, {len(batches)} batches")
    print(f"{len(moves)} blocks rerouted, {drops} left out")


if __name__ == "__main__":
    if sys.argv[1] == "triage":
        triage()
    else:
        build(int(sys.argv[2]) if len(sys.argv) > 2 else 9000)
