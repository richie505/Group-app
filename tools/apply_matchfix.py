"""Apply hand-fixed layouts of garbled matching / pairs MCQ stems (data/matchfix.jsonl, written from
data/matchfix_todo.jsonl) to the apps' question banks, so the apps can draw them as List I / List II or pairs tables.
Only the stem's layout changes (same words, same item labels); options and keys are untouched. A stem is replaced
only where it still equals the garbled original, so re-running is safe.
    python3 tools/apply_matchfix.py"""
import glob, json, re

norm = lambda t: re.sub(r"\n\s*\n+", "\n", t).strip()

todo = {}
for l in open("data/matchfix_todo.jsonl"):
    x = json.loads(l); todo.setdefault(x["id"], set()).add(norm(x["s"]))
fix = {}
for l in open("data/matchfix.jsonl"):
    x = json.loads(l)
    if not x.get("skip") and x.get("s"):
        fix[x["id"]] = x["s"]
n = 0
for app in ("complete", "group1", "group2"):
    for f in sorted(glob.glob(f"app/src/{app}/assets/mcq[0-9].json")):
        m = json.load(open(f)); ch = 0
        for qs in m["rows"].values():
            for q in qs:
                if q["id"] in fix and norm(q["s"]) in todo.get(q["id"], ()) and q["s"] != fix[q["id"]]:
                    q["s"] = fix[q["id"]]; ch += 1
        if ch:
            json.dump(m, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
            n += ch
            print(f, ch)
print("stems fixed:", n, "of", len(fix), "fixes")
