"""Rewrites the Current Affairs (book 6) entry of APPSC Complete's index.json from its book6 / mcq6.

    python3 tools/ca_index.py [assets=app/src/complete/assets]
"""
import json, sys
from pathlib import Path

A = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets")
book = json.load(open(A / "book6.json"))
mcq = json.load(open(A / "mcq6.json"))
index = json.load(open(A / "index.json"))
entry = index["books"][5]
entry["units"] = [{"code": u.get("code", ""), "title": u["title"]} for u in book["units"]]
entry["rows"], gi = [], 0
for ui, u in enumerate(book["units"]):
    for r in u["rows"]:
        entry["rows"].append({"u": ui, "codes": r.get("codes", []), "title": r["title"], "tag": r.get("tag", ""),
                              "pyq": r.get("pyq", ""), "p1": r.get("p1", 0), "p2": r.get("p2", 0),
                              "n": len(r["secs"]), "q": len(mcq["rows"].get(str(gi), []))})
        gi += 1
entry["pages"] = sum(r["n"] for r in entry["rows"])
entry["uq"] = {}
(A / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
