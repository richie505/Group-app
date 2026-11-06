"""Writes moved.json for an app whose notes were rebuilt with the same topics (row i stays row i in each book):
each old page id -> the new page of the same topic whose words match it best, so read marks and bookmarks stay
near where they were. Books whose topic count changed are left out (their pages are not moved).

    python3 tools/page_moves.py <old assets dir> <new assets dir> <version>
"""
import collections
import json
import re
import sys

OLD, NEW, V = sys.argv[1:4]
J = lambda p: json.load(open(p))


def flat(bk):
    return [r for u in bk["units"] for r in u["rows"]]


def words(sec):
    s = sec.get("t", "") + " " + " ".join("".join(r[0] for r in x.get("x", [])) for x in sec["b"])
    s += " " + " ".join("".join(r[0] for r in c) for x in sec["b"] if x.get("k") == "t"
                        for row in [x.get("h", [])] + x.get("r", []) for c in row)
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3]


moved, skipped = {}, []
for b in range(1, 7):
    old, new = flat(J(f"{OLD}/book{b}.json")), flat(J(f"{NEW}/book{b}.json"))
    if len(old) != len(new):
        skipped.append(b)
        continue
    for ri, (o, n) in enumerate(zip(old, new)):
        cs = [collections.Counter(words(s)) for s in n["secs"]]
        for si, s in enumerate(o["secs"]):
            ws = set(words(s))
            best = max(range(len(cs)), key=lambda i: sum(1 for w in ws if w in cs[i])) if cs else 0
            if f"{b}:{ri}:{si}" != f"{b}:{ri}:{best}":
                moved[f"{b}:{ri}:{si}"] = f"{b}:{ri}:{best}"
json.dump({"v": V, "m": moved}, open(f"{NEW}/moved.json", "w"), separators=(",", ":"))
print(f"{len(moved)} pages moved; books skipped (topic count changed): {skipped or 'none'}")
