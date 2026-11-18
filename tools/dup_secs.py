"""A topic's subsection that is an exact copy of an earlier one (same title, same notes) is hidden: its notes become
the app's "No MCQ ..." empty page (the page indices stay, so read marks and links keep working), and its MCQs and
notes links move to the first copy.

    python3 tools/dup_secs.py [assets dir=app/src/complete/assets]
"""
import json, os, sys

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets"
EMPTY = [{"k": "n", "x": [["No MCQ notes here: the same page is above.", 0]]}]
hidden = moved = links = 0
nl_path = f"{A}/notelinks.json"
nl = json.load(open(nl_path)) if os.path.exists(nl_path) else {}
for b in range(1, 7):
    bk = json.load(open(f"{A}/book{b}.json"))
    m = json.load(open(f"{A}/mcq{b}.json"))
    rows = [r for u in bk["units"] for r in u["rows"]]
    remap = {}
    for ri, r in enumerate(rows):
        first = {}
        for si, s in enumerate(r.get("secs", [])):
            key = (s["t"], json.dumps(s["b"], sort_keys=True))
            if s["b"] == EMPTY:
                continue
            if key in first:
                remap[(ri, si)] = first[key]
                s["b"] = EMPTY
                hidden += 1
            else:
                first[key] = si
    for r, subs in m.get("subs", {}).items():
        for i, s in enumerate(subs):
            if (int(r), s) in remap:
                subs[i] = remap[(int(r), s)]
                moved += 1
    for qid, refs in nl.items():
        for i, ref in enumerate(refs):
            p = ref.split(":")
            if int(p[0]) == b and (int(p[1]), int(p[2])) in remap:
                p[2] = str(remap[(int(p[1]), int(p[2]))]); refs[i] = ":".join(p); links += 1
    open(f"{A}/book{b}.json", "w").write(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    open(f"{A}/mcq{b}.json", "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
if nl:
    open(nl_path, "w").write(json.dumps(nl, ensure_ascii=False, separators=(",", ":")))
print(f"{A}: {hidden} copied subsections hidden; {moved} MCQs and {links} notes links moved to the first copy")
