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

# options with scan debris (data/pyq/stemfix/opts-out.json: id -> {"o", optional "s"} | {"same"} | {"broken"}):
# options cleaned in place, in the same order, keys unchanged
OPTS = {k: v for k, v in json.load(open("data/pyq/stemfix/opts-out.json")).items() if isinstance(v.get("o"), list) and len(v["o"]) == 4}
for app in ("main", "complete"):
    n = 0
    for b in range(1, 7):
        p = f"app/src/{app}/assets/mcq{b}.json"
        m = json.load(open(p))
        for qs in m["rows"].values():
            for q in qs:
                f = OPTS.get(q["id"])
                if f and len(q["o"]) == 4:
                    q["o"] = [o.strip() for o in f["o"]]
                    if f.get("s"):
                        q["s"] = f["s"]
                    n += 1
        json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(app, "options cleaned:", n)

# explanations for keys that time has overtaken (the exam's own key stays)
EXPLAIN = {
    "y0d63a80ec51": "Keyed as the 2018 paper had it: then Jupiter had the most known moons (79). Newer discoveries "
                    "have since given Saturn the most (over 140 since 2023), so a current paper would key Saturn.",
}
for app in ("main", "complete"):
    for b in range(1, 7):
        p = f"app/src/{app}/assets/mcq{b}.json"
        m = json.load(open(p))
        for qs in m["rows"].values():
            for q in qs:
                if q["id"] in EXPLAIN:
                    q["x"] = EXPLAIN[q["id"]]
        json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
