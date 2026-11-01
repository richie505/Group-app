"""Puts back the leading number the cleaning took off PYQ options ("1 and 2 only" had become "and 2 only",
"2 only" just "only"). Only options still exactly as that cleaning left them are changed; keys stay as they are.

    python3 tools/pyq_fix_options.py
"""
import hashlib, json, sys

sys.path.insert(0, "tools")
from pyq_place import clean, fixes  # noqa: E402


def main():
    raw = {}
    for line in open("data/pyq/all.jsonl"):
        q = json.loads(line)
        raw["y" + hashlib.sha1(q["id"].encode()).hexdigest()[:11]] = q
    fx = fixes()
    for app in ("main", "complete"):
        n = qn = 0
        for b in range(1, 7):
            p = f"app/src/{app}/assets/mcq{b}.json"
            m = json.load(open(p))
            for qs in m["rows"].values():
                for q in qs:
                    r = raw.get(q["id"])
                    if not r or r["id"] in fx or len(r["o"]) != len(q["o"]):
                        continue
                    hit = False
                    for i, ro in enumerate(r["o"]):
                        bad, good = clean(ro), clean(ro, opt=True)
                        if q["o"][i] == bad and bad != good:
                            q["o"][i] = good
                            n += 1
                            hit = True
                    qn += hit
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        print(app, "options restored:", n, "in", qn, "questions")


if __name__ == "__main__":
    main()
