"""Statement MCQs written by the MCQ trim's merges mostly answer "1 and 2 only" (the false statement was
usually written last). This renumbers their statements in a random order (fixed per question), so the right
answer varies, and rewrites the options, explanation and takeaway to the new numbers.

    python3 tools/shuffle_statements.py <assets dir> <book> [...]
Only questions not in the untrimmed bank (work/mcqfull/b<book>/orig.json) are touched, and only when the
stem has lines "1. ... 2. ..." and every option is made of statement numbers ("1 and 3 only", "2 only",
"1, 2 and 3", "Both 1 and 2", "Neither 1 nor 2"); count questions ("Only two") and match lists are left.
Running it again does nothing (it marks the questions it renumbered with "sh": 1).
"""
import json, random, re, sys
from collections import Counter
from pathlib import Path

OPT = re.compile(r"^(?:Both |Neither |All of |None of )?[\d ,and&nor]+(?: only)?$|^(?:Both|Neither) .*$")
STMT = re.compile(r"((?:[Ss]tatements?|[Pp]airs?|[Ii]tems?)\s+)((?:\d\s*(?:,\s*|\s+and\s+|\s+&\s+|\s+or\s+|\s+nor\s+))*\d)")


def renum(text, perm):
    return re.sub(r"\b\d\b", lambda m: str(perm.get(int(m.group()), int(m.group()))), text)


def tidy(option):
    """'3 and 1 only' -> '1 and 3 only' (numbers in order, same wording)."""
    nums = sorted(re.findall(r"\b\d\b", option))
    it = iter(nums)
    return re.sub(r"\b\d\b", lambda m: next(it), option)


def shuffle(q):
    lines = q["s"].split("\n")
    idx = [i for i, l in enumerate(lines) if re.match(r"^\d\.\s", l)]
    n = len(idx)
    if n < 2 or n > 6 or [int(lines[i][0]) for i in idx] != list(range(1, n + 1)) or idx != list(range(idx[0], idx[0] + n)):
        return False
    if not all(OPT.match(o.strip()) and re.search(r"\d", o) for o in q["o"]):
        return False
    rng = random.Random(q["id"])
    # a new order (not the old one), preferring one whose answer is not "1 and 2 only"
    perms = []
    for _ in range(12):
        order = list(range(1, n + 1))
        rng.shuffle(order)
        p = {old: new for new, old in enumerate(order, 1)}  # old number -> new number
        if order != sorted(order):
            perms.append(p)
    if not perms:
        return False
    perm = next((p for p in perms if tidy(renum(q["o"][q["a"]], p)) != "1 and 2 only"), perms[0])
    body = {perm[int(lines[i][0])]: lines[i][2:].lstrip() for i in idx}
    for k, i in enumerate(idx, 1):
        lines[i] = f"{k}. {body[k]}"
    q["s"] = "\n".join(lines)
    q["o"] = [tidy(renum(o, perm)) for o in q["o"]]
    for f in ("x", "tq"):
        if q.get(f):
            q[f] = STMT.sub(lambda m: m.group(1) + tidy(renum(m.group(2), perm)), q[f])
    q["sh"] = 1
    return True


def main():
    A = Path(sys.argv[1])
    for book in map(int, sys.argv[2:]):
        orig = Path(f"work/mcqfull/b{book}/orig.json")
        old = {q.get("id") for v in json.load(open(orig))["rows"].values() for q in v} if orig.exists() else set()
        m = json.load(open(A / f"mcq{book}.json"))
        done, ans = 0, Counter()
        for qs in m["rows"].values():
            for q in qs:
                if q.get("id") in old or q.get("sh"):
                    continue
                if shuffle(q):
                    done += 1
                    ans[q["o"][q["a"]]] += 1
        (A / f"mcq{book}.json").write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        print(f"book {book}: {done} statement MCQs renumbered; answers now {ans.most_common(5)}")


if __name__ == "__main__":
    main()
