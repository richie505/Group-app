"""Moves PYQs in APPSC Complete to the topic / subsection the placement check chose (data/pyq/refile/out/*.json:
{id: "b:r:k" | "drop"}). Run it last, after tools/pyq_apply.py, tools/arihant_apply.py and tools/pyq_fix_garbled.py
(they rebuild the PYQs where tools/pyq_place.py put them). Running it again changes nothing. Then run
tools/build_plan_mcq.py and tools/group2_build.py.
"""
import glob, json, re

A = "app/src/complete/assets"


def main():
    dec = {}
    for f in sorted(glob.glob("data/pyq/refile/out/*.json")):
        dec.update(json.load(open(f)))
    index = json.load(open(f"{A}/index.json"))
    valid = set()  # every "b:r:k" that exists
    for line in open("data/pyq/arihant/topics.txt"):
        br = line.split()[0]
        valid |= {f"{br}:{k}" for k in re.findall(r"(?:::|\|)\s*(\d+):", line)}
    books = {b: json.load(open(f"{A}/mcq{b}.json")) for b in range(1, 7)}
    where, taken = {}, {}
    for b, m in books.items():
        for r, qs in m["rows"].items():
            subs = m["subs"].get(r) or [-1] * len(qs)
            for q, s in zip(qs, subs):
                if q["id"] in dec:
                    where[q["id"]] = (b, int(r), s)
    moved = dropped = skipped = 0
    for qid, to in dec.items():
        if qid not in where:
            continue
        b, r, s = where[qid]
        if to != "drop":
            try:
                tb, tr, ts = map(int, to.split(":"))
            except ValueError:
                skipped += 1; continue
            if to not in valid or (tb, tr, ts) == (b, r, s):
                skipped += 1; continue
        m, k = books[b], str(r)
        i = next(i for i, q in enumerate(m["rows"][k]) if q["id"] == qid)
        q = m["rows"][k].pop(i)
        if m["subs"].get(k):
            m["subs"][k].pop(i)
        if to == "drop":
            dropped += 1; continue
        m = books[tb]; k = str(tr)
        qs = m["rows"].setdefault(k, []); subs = m["subs"].setdefault(k, [-1] * len(qs))
        # after the PYQs already in that subsection, before its own MCQs; else in subsection order
        at = None
        for j, (ps, pq) in enumerate(zip(subs, qs)):
            if ps == ts:
                if pq["id"].startswith("y"):
                    at = j + 1
                else:
                    at = j if at is None else at
                    break
        if at is None:
            at = next((j for j, ps in enumerate(subs) if (ps < 0, ps) > (ts < 0, ts)), len(qs))
        qs.insert(at, q); subs.insert(at, ts)
        moved += 1
    for b, m in books.items():
        for k, qs in m["rows"].items():
            index["books"][b - 1]["rows"][int(k)]["q"] = len(qs)
        json.dump(m, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    print(f"decisions {len(dec)}: moved {moved}, dropped {dropped}, skipped {skipped}")


if __name__ == "__main__":
    main()
