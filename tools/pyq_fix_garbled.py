"""Puts the hand-repaired question text of PYQs whose stem the scan mixed with junk (data/pyq/stemfix/out.json:
id -> {"s": repaired text or null, "note"}) into both apps. null: beyond repair, left as it is.

    python3 tools/pyq_fix_garbled.py
"""
import json

FIX = {k: v["s"] for k, v in json.load(open("data/pyq/stemfix/out.json")).items() if v.get("s")}
for app in ("main", "complete"):
    n = 0
    for b in range(1, 7):
        p = f"app/src/{app}/assets/mcq{b}.json"
        m = json.load(open(p))
        for qs in m["rows"].values():
            for q in qs:
                s = FIX.get(q["id"])
                if s and q["s"] != s:
                    q["s"], n = s, n + 1
        json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(app, "repaired:", n)
