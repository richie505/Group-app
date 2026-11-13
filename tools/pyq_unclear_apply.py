"""Folds the checked "unclear" PYQs (data/pyq/unclear/out-*.json, read from the scanned pages) back into the books'
output files (data/pyq/ocr2026/out/, data/pyq/vijeta/out/): a fixed item gets the corrected stem, options and key (or
flashcard answer) and loses its "unclear" flag; an unreadable item stays unclear (left out of the app); a dropped
item (mental ability) is removed. Then `python3 tools/pyq_add_new.py --apply` adds the fixed ones to the apps.

    python3 tools/pyq_unclear_apply.py
"""
import glob
import json
from collections import Counter, defaultdict


def main():
    where = {}
    for f in glob.glob("data/pyq/unclear/in-*.json"):
        for it in json.load(open(f)):
            where[it["id"]] = it["file"]
    res = {}
    for f in sorted(glob.glob("data/pyq/unclear/out-*.json")):
        for r in json.load(open(f)):
            res[r["id"]] = r
    by_file = defaultdict(dict)
    for i, r in res.items():
        by_file[where[i]][i] = r
    n = Counter()
    for path, fixes in by_file.items():
        out = []
        for line in open(path):
            if not line.strip():
                continue
            q = json.loads(line)
            r = fixes.get(q["id"])
            if r is None:
                out.append(q)
                continue
            st = r.get("status")
            if st == "fixed":
                if q.get("k") == "f":
                    q["s"], q["at"] = r.get("s", q["s"]), r.get("at", q.get("at", ""))
                else:
                    q["s"], q["o"], q["a"] = r["s"], r["o"], r["a"]
                q.pop("unclear", None)
                q["checked"] = "scan"
                n["fixed"] += 1
                out.append(q)
            elif st == "drop":
                n["dropped"] += 1
            else:
                q["unreadable"] = r.get("why", "")
                n["unreadable"] += 1
                out.append(q)
        with open(path, "w") as fh:
            for q in out:
                fh.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(dict(n), "of", len(res))


if __name__ == "__main__":
    main()
