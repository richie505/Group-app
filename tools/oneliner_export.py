"""APPSC One-liners: the APPSC Complete MCQs that are not one-liners (tools/oneliner_kind.py), in batches for agents
that rewrite each as one-liner MCQs, one per fact (tools/oneliner_guide.md).

    python3 tools/oneliner_export.py [MCQs per batch=55]
-> work/oneliner/b<book>/in_NNN.md; agents write out_NNN.jsonl, checked by tools/oneliner_check.py.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from oneliner_kind import oneliner

A = "app/src/complete/assets"
per = int(sys.argv[1]) if len(sys.argv) > 1 else 55


def plain(t):
    return re.sub(r"\*\*|⚠\s*", "", t).strip()


for b in range(1, 7):
    rows = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
    m = json.load(open(f"{A}/mcq{b}.json"))
    items = []
    for r, qs in sorted(m["rows"].items(), key=lambda x: int(x[0])):
        for q in qs:
            if oneliner(q):
                continue
            opts = "\n".join(f"({i + 1}) {o}" for i, o in enumerate(q["o"]))
            facts = [plain(x) for x in q.get("xs", []) + q.get("xa", [])] or [plain(q.get("x", ""))]
            items.append(f"## Q {q['id']} | {rows[int(r)]['title']}\n{q['s'].strip()}\n{opts}\n"
                         f"Answer: ({q['a'] + 1}) {q['o'][q['a']]}\nFacts:\n" + "\n".join(f"- {f}" for f in facts if f))
    d = f"work/oneliner/b{b}"
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith("in_"):
            os.remove(f"{d}/{f}")
    for k in range(0, len(items), per):
        open(f"{d}/in_{k // per:03d}.md", "w").write("\n\n".join(items[k:k + per]) + "\n")
    print(f"book {b}: {len(items)} MCQs, {(len(items) + per - 1) // per} batches")
