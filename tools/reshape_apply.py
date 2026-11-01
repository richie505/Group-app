"""Puts the rewritten MCQs (data/reshape/out/*.json, from tools/reshape_plan.py packets) into APPSC Complete (only).

    python3 tools/reshape_apply.py

An MCQ keeps its id (so its place, progress and links stay); its stem, options, key and explanation are replaced, the
old structured explanation (which talked about the old statements and options) is dropped, and "rs" records the new
shape. A rewrite is used only when it is a sound four-option MCQ with a key. Re-running it is harmless.
"""
import glob, json, re

APPS = ("app/src/complete/assets",)  # APPSC Complete only: the Prep app keeps its MCQs as they are


def valid(r):
    o = r.get("o")
    return (isinstance(r.get("s"), str) and len(r["s"].strip()) >= 10 and isinstance(o, list) and len(o) == 4
            and all(isinstance(x, str) and x.strip() for x in o) and len({x.strip().lower() for x in o}) == 4
            and isinstance(r.get("a"), int) and 0 <= r["a"] <= 3)


def main():
    new, bad = {}, 0
    for f in sorted(glob.glob("data/reshape/out/*.json")):
        try:
            d = json.load(open(f))
        except ValueError:
            print("unreadable", f)
            continue
        for i, r in d.items():
            if r.get("same"):
                continue
            if valid(r):
                new[i] = r
            else:
                bad += 1
    done = {}
    for A in APPS:
        n = 0
        for b in range(1, 7):
            p = f"{A}/mcq{b}.json"
            m = json.load(open(p))
            for qs in m["rows"].values():
                for q in qs:
                    r = new.get(q["id"])
                    if not r:
                        continue
                    q["s"], q["o"], q["a"] = r["s"].strip(), [x.strip() for x in r["o"]], r["a"]
                    q["x"] = (r.get("x") or "").strip()
                    for k in ("xs", "tq", "t"):
                        q.pop(k, None)
                    # extra notes stay only if they do not point at the old options / statements
                    q["xa"] = [x for x in q.get("xa", []) if not re.search(r"(?i)option\s*\(?\d|\bstatements?\s*\d|\(\d\)", x)]
                    if not q["xa"]:
                        q.pop("xa")
                    q["rs"] = r.get("shape", "")[:20]
                    n += 1
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        done[A] = n
    print(f"rewrites: {len(new)} usable, {bad} rejected; applied {done}")


if __name__ == "__main__":
    main()
