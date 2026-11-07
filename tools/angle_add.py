"""Add MCQs written for missing exam angles (data/angle2) to APPSC Complete.

    python3 tools/angle_add.py <out.json> [--dry]
    out.json: {"new": [{"book": 1, "row": 5, "sub": 2, "s": "...", "o": ["..",".."], "a": 1, "x": "...",
                        "angle": "U0001 #2 Inscription -> ruler"}]}
    and/or "reword": [{"book": 1, "id": "n…", "s": "new stem in APPSC wording"}]  (stem only; options and key unchanged)
New MCQs get id "g" + hash, src "app"; each is checked (4 options, a valid key, not a copy of an MCQ already there).
"""
import hashlib, json, re, sys
A = "app/src/complete/assets"
norm = lambda t: re.sub(r"\W+", " ", t.lower()).strip()


def main(path, dry):
    d = json.load(open(path))
    if d.get("notes"):  # web-found facts added to the notes first (tools/notes_fix.py ops, APPSC Complete)
        import os, subprocess, tempfile
        tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(d["notes"], tf, ensure_ascii=False); tf.close()
        r = subprocess.run([sys.executable, "tools/notes_fix.py", "apply", tf.name] + (["--dry"] if dry else []),
                           env={**os.environ, "NOTES_APP": "complete"}, capture_output=True, text=True)
        print("notes: " + r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "notes: ?", end="; ")
        if r.returncode:
            print("\nnotes edits refused, nothing applied:\n" + r.stdout); return
        if not dry:
            with open("data/angle2/notes_added.jsonl", "a") as f:
                for o in d["notes"]: f.write(json.dumps({"file": path, **o}, ensure_ascii=False) + "\n")
    new = d.get("new", [])
    rw = d.get("reword", [])
    index = json.load(open(f"{A}/index.json"))
    byb, bad = {}, []
    for q in new:
        byb.setdefault(int(q["book"]), []).append(q)
    rwb = {}
    for q in rw:
        rwb.setdefault(int(q["book"]), {})[q["id"]] = q["s"]
        byb.setdefault(int(q["book"]), [])
    added = reworded = 0
    rlog = []
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
        want = rwb.get(b, {})
        for qs2 in m["rows"].values():
            for x in qs2:
                if x["id"] in want:
                    if x["id"].startswith("y"):
                        bad.append((x["id"], "PYQs are never reworded")); continue
                    rlog.append({"id": x["id"], "old": x["s"], "new": want[x["id"]]}); x["s"] = want[x["id"]]; reworded += 1
        miss = set(want) - {x["id"] for qs2 in m["rows"].values() for x in qs2}
        bad += [(i, "reword id not found") for i in miss]
        if not dry:
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    if not dry:
        open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        with open("data/angle2/reworded.jsonl", "a") as f:  # the old stems, so any rewording can be undone
            for o in rlog: f.write(json.dumps(o, ensure_ascii=False) + "\n")
        with open("data/angle2/added.jsonl", "a") as f:
            for q in new: f.write(json.dumps({"file": path, "angle": q.get("angle", ""), "s": q.get("s", "")[:80], **({"web": q["web"]} if q.get("web") else {})}, ensure_ascii=False) + "\n")
    print(f"{added}/{len(new)} new MCQs and {reworded}/{len(rw)} rewordings {'would be ' if dry else ''}applied" + (f"; refused: {bad}" if bad else ""))


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
