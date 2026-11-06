"""APPSC Reader on the blueprint notes: the same topics and pages as APPSC Complete (one page per numbered section),
for reading only. Run after tools/blueprint_build.py. Writes app/src/reader/assets:
- book*.json and index.json from APPSC Complete (no MCQ counts), keyterms.json (the same page ids)
- empty MCQ files, edition.json
- moved.json "reader-3": each page id of the Reader's earlier notes (reader-2) -> the new page in the same topic
  whose words match it best, so read marks and bookmarks stay near where they were
simple.json (the dictionary) is kept. Then run tools/reader_plan.py.

    python3 tools/reader_blueprint.py
"""
import collections
import json
import os
import re
import sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
R0 = "app/src/reader/assets"  # the earlier Reader notes (for moved.json)
R = sys.argv[2] if len(sys.argv) > 2 else R0
os.makedirs(R, exist_ok=True)
J = lambda p: json.load(open(p))
W = lambda p, o: json.dump(o, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
topic_of = J("data/blueprint/topic_of.json")


def flat(bk):
    return [r for u in bk["units"] for r in u["rows"]]


def words(sec):
    s = sec.get("t", "") + " " + " ".join("".join(r[0] for r in x.get("x", [])) for x in sec["b"])
    s += " " + " ".join("".join(r[0] for r in c) for x in sec["b"] if x.get("k") == "t"
                        for row in [x.get("h", [])] + x.get("r", []) for c in row)
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3]


moved, pages = {}, 0
for b in range(1, 7):
    old, new = flat(J(f"{R0}/book{b}.json")), J(f"{A}/book{b}.json")
    nf = flat(new)
    for ri, row in enumerate(old):
        t = topic_of[f"{b}:{ri}"]
        cs = [collections.Counter(words(s)) for s in nf[t]["secs"]]
        for si, s in enumerate(row["secs"]):
            ws = set(words(s))
            best = max(range(len(cs)), key=lambda i: sum(1 for w in ws if w in cs[i])) if cs else 0
            moved[f"{b}:{ri}:{si}"] = f"{b}:{t}:{best}"
    pages += sum(len(r["secs"]) for r in nf)
    W(f"{R}/book{b}.json", new)
    W(f"{R}/mcq{b}.json", {"rows": {}, "units": {}, "subs": {}})
idx = J(f"{A}/index.json")
for bi in idx["books"]:
    bi["uq"] = [0] * len(bi["uq"]) if isinstance(bi.get("uq"), list) else 0
    for r in bi["rows"]:
        r["q"] = 0
W(f"{R}/index.json", idx)
W(f"{R}/keyterms.json", J(f"{A}/keyterms.json"))
W(f"{R}/empty.json", {"mcq": [], "full": []})
W(f"{R}/edition.json", {"edition": "reader", "name": "APPSC Reader"})
W(f"{R}/moved.json", {"v": "reader-3", "m": {k: v for k, v in moved.items() if k != v}})
W(f"{R}/notemoves.json", [])
print(f"APPSC Reader: {sum(len(b['rows']) for b in idx['books'])} topics, {pages} pages; {len(moved)} old pages moved")
