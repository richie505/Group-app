"""App-made 'How many of the above statements are correct?' MCQs (UPSC style) -> APPSC style:
'Which of the above statements is/are correct?' with statement-combination options (e.g. '1 and 4 only').
The correct set comes from the option keyed (the count) and the explanation (which statements are right/wrong);
an MCQ whose set cannot be read for sure is left as it is (listed in data/howmany/unparsed.json).
Real UPSC PYQs keep their printed form.

    python3 tools/howmany_to_appsc.py [assets dir ...]   (default: app/src/complete/assets)
"""
import json, re, sys, random, os, itertools

W = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'none': 0, 'no': 0, 'all': None}
NUMS = r"\d(?:\s*(?:,|and|&)\s*\d)*"


def nums(t): return {int(d) for d in re.findall(r"\d", t)}


SETS = json.load(open("data/howmany/sets.json")) if os.path.exists("data/howmany/sets.json") else {}


def correct_set(q):
    n = len(re.findall(r"^\d\.", q["s"], re.M))
    if n < 2: return None, n
    if q["id"] in SETS: return set(SETS[q["id"]]["correct"]), n  # worked out statement by statement
    m = re.search(r"\b(one|two|three|four|five|none|no|all)\b", q["o"][q["a"]].lower())
    if not m: return None, n
    cnt = W[m.group(1)]; cnt = n if cnt is None else cnt
    if cnt == n: return set(range(1, n + 1)), n
    if cnt == 0: return set(), n
    x = q.get("x", "")
    head = x[:220]
    cands = []
    m = re.match(r"\W*(?:only\s+)?(?:one|two|three|four)\b[^(]{0,25}\((" + NUMS + r")\)", head, re.I)
    if m: cands.append(nums(m.group(1)))
    m = re.match(r"\W*(?:only\s+)?(?:statements?\s+)?(" + NUMS + r")\s+(?:are|is)\s+(?:correct|right|true)", head, re.I)
    if m: cands.append(nums(m.group(1)))
    m = re.match(r"\W*only\s+(?:one|two|three)\s+(?:is|are)\s+correct\s*\((?:statements?\s+)?(" + NUMS + r")\)", head, re.I)
    if m: cands.append(nums(m.group(1)))
    wrong = set()
    for m in re.finditer(r"(?:statements?\s+)?(" + NUMS + r")\s+(?:is|are)\s+(?:wrong|incorrect|false)", x, re.I):
        wrong |= nums(m.group(1))
    if wrong: cands.append(set(range(1, n + 1)) - wrong)
    good = [c for c in cands if len(c) == cnt and all(1 <= d <= n for d in c)]
    if good and all(c == good[0] for c in good): return good[0], n
    return None, n


def label(s, n):
    s = sorted(s)
    if not s: return "None of the above"
    if len(s) == n: return "All of the above" if n > 2 else "Both 1 and 2"
    if len(s) == 1: return f"{s[0]} only"
    if n == 2: return "Both 1 and 2"
    return (", ".join(map(str, s[:-1])) + f" and {s[-1]} only")


def options(cs, n, seed):
    rnd = random.Random(seed)
    allsets = [set(c) for k in range(0, n + 1) for c in itertools.combinations(range(1, n + 1), k)]
    # distractors: sets close to the key (one statement added, dropped or swapped), like APPSC's options
    near = [s for s in allsets if s != cs and len(s ^ cs) <= 2 and (len(s) >= 1 or len(cs) <= 1)]
    rnd.shuffle(near)
    picks = near[:3]
    rest = [s for s in allsets if s != cs and s not in picks and s]
    rnd.shuffle(rest)
    while len(picks) < 3: picks.append(rest.pop())
    opts = picks + [cs]
    opts.sort(key=lambda s: (len(s), sorted(s)) if s else (99, []))
    # APPSC: "None" / "All" go last
    return [label(s, n) for s in opts], [s == cs for s in opts].index(True)


def convert(q):
    cs, n = correct_set(q)
    if cs is None: return False
    o, a = options(cs, n, q["id"])
    q["s"] = re.sub(r"How many of the (statements|pairs) given above (?:is|are) ([^?\n]+)\?",
                    lambda m: f"Which of the {m.group(1)} given above is/are {m.group(2).strip()}?", q["s"], flags=re.I)
    q["s"] = re.sub(r"How many of the (?:above|following|given)\s+([\w-]+(?: [\w-]+)?)\s+(?:is|are|was|were|has|have)\s+([^?\n]+)\?",
                    lambda m: f"Which of the above {m.group(1)} is/are {m.group(2).strip()}?", q["s"], flags=re.I)
    q["s"] = re.sub(r"How many of the (?:above|following|given)\s+([\w-]+(?: [\w-]+)?)\s+([^?\n]+)\?",
                    lambda m: f"Which of the above {m.group(1)} {m.group(2).strip()}?", q["s"], flags=re.I)
    if "How many" in q["s"]:
        return False
    q["o"], q["a"] = o, a
    x = q.get("x", "")
    q["x"] = re.sub(r"^\W*(?:only\s+)?(?:one|two|three|four|five)\b\s*\((" + NUMS + r")\)\.?\s*", lambda m: label(cs, n) + ". ", x, flags=re.I)
    if q["x"] == x: q["x"] = f"{label(cs, n)}. " + x
    return True


if __name__ == "__main__":
    dirs = sys.argv[1:] or ["app/src/complete/assets"]
    for A in dirs:
        done, left = 0, []
        for b in range(1, 7):
            p = f"{A}/mcq{b}.json"; m = json.load(open(p))
            for v in m["rows"].values():
                for q in v:
                    if q.get("src") == "app" and re.search(r"how many of the", q["s"], re.I):
                        if convert(q): done += 1
                        else: left.append(q["id"])
            open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        os.makedirs("data/howmany", exist_ok=True)
        json.dump(left, open("data/howmany/unparsed.json", "w"))
        print(A, "converted", done, "left", len(left))
