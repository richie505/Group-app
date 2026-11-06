"""Exam-relevance audit of APPSC Complete (data/relevance/INSTRUCTIONS.md).

    python3 tools/relevance.py show <book> <row>        a topic's notes (block numbers) and its MCQs (ids, subsection)
    python3 tools/relevance.py drop <drops.json> [--dry] take MCQs out: {"drop": [{"book":1,"id":"n…","why":"…"}, …]}
    python3 tools/relevance.py restore <restore.json> [--dry]  put archived MCQs back:
        {"restore": [{"id":"n…","why":"…","fix":{"a":2,"x":"…"}}, …]}  ("fix" optional: any of s/o/a/x to correct)

Dropped MCQs are kept in data/relevance/archive.jsonl (with book, row, subsection and reason), never lost. PYQs
(ids starting "y") are never dropped. Note edits go through tools/notes_fix.py (NOTES_APP=complete).
"""
import json, os, subprocess, sys

A = "app/src/complete/assets"


def show(book, row):
    subprocess.run([sys.executable, "tools/notes_fix.py", "show", str(book), str(row)], env={**os.environ, "NOTES_APP": "complete"})
    m = json.load(open(f"{A}/mcq{book}.json"))
    qs, subs = m["rows"].get(str(row), []), m["subs"].get(str(row), [])
    print(f"\n=== MCQs of {book}:{row} ({len(qs)})")
    for q, s in zip(qs, subs or [-1] * len(qs)):
        opts = " | ".join(f"{'*' if i == q['a'] else ''}{o}" for i, o in enumerate(q["o"]))
        print(f"[{q['id']}] sub{s} {'PYQ ' + q.get('src', '') if q['id'].startswith('y') else ''}\n  {q['s']}\n  {opts}")


def drop(path, dry):
    want = {}
    for d in json.load(open(path))["drop"]:
        if not d["id"].startswith("y"):
            want.setdefault(int(d["book"]), {})[d["id"]] = d.get("why", "")
    n, out = 0, []
    for b, ids in want.items():
        p = f"{A}/mcq{b}.json"
        m = json.load(open(p))
        index = json.load(open(f"{A}/index.json"))
        for r, qs in m["rows"].items():
            subs = m["subs"].get(r) or [-1] * len(qs)
            keep = [(q, s) for q, s in zip(qs, subs) if q["id"] not in ids]
            for q, s in zip(qs, subs):
                if q["id"] in ids:
                    out.append({"book": b, "row": int(r), "sub": s, "why": ids[q["id"]], "q": q})
            if len(keep) != len(qs):
                m["rows"][r] = [q for q, _ in keep]
                if r in m["subs"]:
                    m["subs"][r] = [s for _, s in keep]
                index["books"][b - 1]["rows"][int(r)]["q"] = len(keep)
        if not dry:
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
            open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    if not dry:
        with open("data/relevance/archive.jsonl", "a") as f:
            for o in out:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    asked = sum(len(v) for v in want.values())
    print(f"{len(out)}/{asked} MCQs {'would be ' if dry else ''}dropped" + ("" if len(out) == asked else " (some ids not found)"))


def restore(path, dry):
    arc = {}
    for l in open("data/relevance/archive.jsonl"):
        r = json.loads(l)
        arc[r["q"]["id"]] = r
    done = set()
    if os.path.exists("data/relevance/restored.jsonl"):
        done = {json.loads(l)["id"] for l in open("data/relevance/restored.jsonl")}
    want = [d for d in json.load(open(path))["restore"] if d["id"] in arc and d["id"] not in done]
    miss = [d["id"] for d in json.load(open(path))["restore"] if d["id"] not in arc]
    byb = {}
    for d in want:
        byb.setdefault(arc[d["id"]]["book"], []).append(d)
    index = json.load(open(f"{A}/index.json"))
    log = []
    for b, ds in byb.items():
        p = f"{A}/mcq{b}.json"
        m = json.load(open(p))
        for d in ds:
            r = arc[d["id"]]
            q = dict(r["q"])
            for k, v in (d.get("fix") or {}).items():
                if k in ("s", "o", "a", "x"):
                    q[k] = v
            if d.get("fix"):
                q.pop("xs", None); q.pop("xa", None)  # per-option explanation bullets would be stale
            if not (isinstance(q["a"], int) and 0 <= q["a"] < len(q["o"])):
                miss.append(d["id"]); continue
            row = str(r["row"])
            qs = m["rows"].setdefault(row, [])
            if any(x["id"] == q["id"] for x in qs):
                continue
            if row in m["subs"]:
                subs = m["subs"][row]
                pos = max([i + 1 for i, s in enumerate(subs) if s <= r["sub"]] or [0])
                qs.insert(pos, q); subs.insert(pos, r["sub"])
            else:
                qs.append(q)
            index["books"][b - 1]["rows"][r["row"]]["q"] = len(qs)
            log.append({"id": q["id"], "book": b, "row": r["row"], "why": d.get("why", ""), "fixed": bool(d.get("fix"))})
        if not dry:
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    if not dry:
        open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        with open("data/relevance/restored.jsonl", "a") as f:
            for o in log:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"{len(log)} MCQs {'would be ' if dry else ''}restored" + (f"; not found/invalid: {miss}" if miss else ""))


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "restore":
        restore(sys.argv[2], "--dry" in sys.argv)
    else:
        drop(sys.argv[2], "--dry" in sys.argv)
