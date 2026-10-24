"""Repairs the one-line explanation ("x") and takeaway ("tq") of statement MCQs renumbered by
tools/shuffle_statements.py: they may quote an option's old text ("Hence '1 and 2 only'"), which the
renumbering did not touch. Each such MCQ is matched to the merge that wrote it (work/mcqfull*/b<book>/out_*.jsonl,
by its set of statements), and x / tq are rebuilt from the merge's own text with the new numbering.

    python3 tools/shuffle_fix_x.py <assets dir> <book> [...]
"""
import glob, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shuffle_statements import STMT, renum, tidy


def bodies(stem):
    return [l[2:].strip() for l in stem.split("\n") if re.match(r"^\d\.\s", l)]


def main():
    A = Path(sys.argv[1])
    for book in map(int, sys.argv[2:]):
        merges = {}
        for f in glob.glob(f"work/mcqfull*/b{book}/out_*.jsonl"):
            for line in open(f):
                if line.strip():
                    o = json.loads(line)
                    if o.get("d") == "merge" and bodies(o.get("s", "")):
                        merges[frozenset(bodies(o["s"]))] = o
        m = json.load(open(A / f"mcq{book}.json"))
        fixed = missing = 0
        for qs in m["rows"].values():
            for q in qs:
                if not q.get("sh"):
                    continue
                now = bodies(q["s"])
                o = merges.get(frozenset(now))
                if not o:
                    missing += 1
                    continue
                old = bodies(o["s"])
                perm = {i + 1: now.index(b) + 1 for i, b in enumerate(old)}  # old number -> new number
                if len(o["o"]) != len(q["o"]):
                    missing += 1
                    continue
                for field in ("x", "tq"):
                    text = o.get(field, "")
                    if not text:
                        continue
                    # option texts first (longest first, as placeholders), then "Statement(s) n" phrases
                    order = sorted(range(len(o["o"])), key=lambda i: -len(o["o"][i]))
                    for i in order:
                        if re.search(r"\d", o["o"][i]):
                            text = text.replace(o["o"][i], f"\u0000{i}\u0000")
                    text = STMT.sub(lambda g: g.group(1) + tidy(renum(g.group(2), perm)), text)
                    text = re.sub("\u0000(\\d+)\u0000", lambda g: q["o"][int(g.group(1))], text)
                    q[field] = text
                fixed += 1
        (A / f"mcq{book}.json").write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        print(f"book {book}: {fixed} renumbered MCQs' x/tq rebuilt, {missing} without a matching merge")


if __name__ == "__main__":
    main()
