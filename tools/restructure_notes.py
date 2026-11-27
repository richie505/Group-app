"""Group 1 Prelims / Group 2 apps: each notes page shown as its restructured (Rocket-style) version – short headings,
crisp points and Fact / Key-detail tables with the key terms in bold – the same content the lecture slides were made
from (data/lecrocket/<group1|group2>/<book>-<row>.json: {"<page>": [{"k": "h"|"b", "x": "**bold** text"} |
{"k": "t", "h": [...], "r": [[...]]}]}). Pages keep their place (title, index), so every MCQ still links to its page;
pages without a restructured version stay as they were.
    python3 tools/restructure_notes.py          (run after tools/group1_build.py / group2_build.py)"""
import json, os, re

APPS = {"group1": "app/src/group1/assets", "group2": "app/src/group2/assets"}
J = lambda p: json.load(open(p))


def runs(t):
    return [[p, i % 2] for i, p in enumerate(re.split(r"\*\*", str(t).replace("⚠", "").strip())) if p]


def block(b):
    if b["k"] == "t":
        return {"k": "t", "h": [runs(c) for c in b.get("h") or []], "r": [[runs(c) for c in r] for r in b.get("r") or []]}
    return {"k": b["k"], "x": runs(b["x"])}


for app, A in APPS.items():
    n = 0
    for B in range(1, 7):
        p = f"{A}/book{B}.json"
        bk = J(p)
        rows = [r for u in bk["units"] for r in u["rows"]]
        for R, row in enumerate(rows):
            f = f"data/lecrocket/{app}/{B}-{R}.json"
            if not os.path.exists(f):
                continue
            for k, bl in J(f).items():
                k = int(k)
                if k < len(row["secs"]) and bl:
                    row["secs"][k]["b"] = [block(b) for b in bl]
                    row["secs"][k]["rk"] = 1
                    n += 1
        json.dump(bk, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(app, n, "pages restructured")
