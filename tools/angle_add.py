"""Add MCQs written for missing exam angles (data/angle2) to APPSC Complete.

    python3 tools/angle_add.py <out.json> [--dry]
    out.json: {"new": [{"book": 1, "row": 5, "sub": 2, "s": "...", "o": ["..",".."], "a": 1, "x": "...",
                        "angle": "U0001 #2 Inscription -> ruler"}]}
New MCQs get id "g" + hash, src "app"; each is checked (4 options, a valid key, not a copy of an MCQ already there).
"""
import hashlib, json, re, sys
A = "app/src/complete/assets"
norm = lambda t: re.sub(r"\W+", " ", t.lower()).strip()


def main(path, dry):
    new = json.load(open(path))["new"]
    index = json.load(open(f"{A}/index.json"))
    byb, bad = {}, []
    for q in new:
        byb.setdefault(int(q["book"]), []).append(q)
    added = 0
    for b, qs in byb.items():
        p = f"{A}/mcq{b}.json"
        m = json.load(open(p))
        for q in qs:
            r = str(q["row"])
            if r not in m["rows"] or not (isinstance(q.get("a"), int) and len(q.get("o", [])) == 4 and 0 <= q["a"] < 4) or not q.get("s"):
                bad.append((q.get("s", "")[:50], "bad row/options/key")); continue
            rows = m["rows"][r]
            if any(norm(x["s"]) == norm(q["s"]) for x in rows):
                bad.append((q["s"][:50], "same stem already in topic")); continue
            qid = "g" + hashlib.sha1(f"{b}|{r}|{q['s']}".encode()).hexdigest()[:12]
            item = {"id": qid, "s": q["s"], "o": q["o"], "a": q["a"], "x": q.get("x", ""), "src": "app"}
            if r in m["subs"]:
                subs = m["subs"][r]; s = int(q.get("sub", -1))
                pos = max([i + 1 for i, x in enumerate(subs) if x <= s] or [len(subs)])
                rows.insert(pos, item); subs.insert(pos, s)
            else:
                rows.append(item)
            index["books"][b - 1]["rows"][int(r)]["q"] = len(rows)
            added += 1
        if not dry:
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    if not dry:
        open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        with open("data/angle2/added.jsonl", "a") as f:
            for q in new: f.write(json.dumps({"file": path, "angle": q.get("angle", ""), "s": q.get("s", "")[:80]}, ensure_ascii=False) + "\n")
    print(f"{added}/{len(new)} new MCQs {'would be ' if dry else ''}added" + (f"; refused: {bad}" if bad else ""))


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
