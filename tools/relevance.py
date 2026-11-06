"""Exam-relevance audit of APPSC Complete (data/relevance/INSTRUCTIONS.md).

    python3 tools/relevance.py show <book> <row>        a topic's notes (block numbers) and its MCQs (ids, subsection)
    python3 tools/relevance.py drop <drops.json> [--dry] take MCQs out: {"drop": [{"book":1,"id":"n…","why":"…"}, …]}

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


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(int(sys.argv[2]), int(sys.argv[3]))
    else:
        drop(sys.argv[2], "--dry" in sys.argv)
