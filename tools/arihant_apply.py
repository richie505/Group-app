"""Adds the checked Arihant PYQs (tools/arihant_parse.py -> data/pyq/new/arihant.jsonl, placed by tools/pyq_place.py
into data/pyq/arihant/place.json, checked by agents into data/pyq/arihant/out/<packet>.json) to APPSC Complete.

Each PYQ goes into its subsection after the PYQs already there and before the app's own MCQs. The checkers' verdicts
are applied: "key" (a corrected key), "fix" (repaired text), "move" (another topic / subsection), "drop" (left out).
Nothing already in the app changes. Run it again after tools/pyq_apply.py (which rebuilds the PYQs from the bank and
does not know these verdicts). APPSC Group 2 does not take these PYQs (tools/group2_build.py skips the ids in
data/pyq/arihant/applied.json).

    python3 tools/arihant_apply.py [packet ...]     (default: every packet checked so far)
"""
import glob, json, os, sys

sys.path.insert(0, "tools")
from pyq_apply import to_mcq  # noqa: E402

A = "app/src/complete/assets"
D = "data/pyq/arihant"


def main(packets):
    place = json.load(open(f"{D}/place.json"))["place"]
    if os.path.exists(f"{D}/place2.json"):  # the second round: questions the first dedupe wrongly took for repeats
        place.update(json.load(open(f"{D}/place2.json"))["place"])
    bank = {}
    for line in open("data/pyq/new/arihant.jsonl"):
        q = json.loads(line)
        bank[q["id"]] = q
    files = [f"{D}/out/{p}.json" for p in packets] if packets else sorted(glob.glob(f"{D}/out/*.json"))
    verdict = {}
    for f in files:
        verdict.update(json.load(open(f)))
    add, stats = {}, {"ok": 0, "key": 0, "fix": 0, "move": 0, "drop": 0}
    for pid, v in verdict.items():
        if pid not in bank or pid not in place:
            continue
        kind = v.get("v", "ok")
        stats[kind] = stats.get(kind, 0) + 1
        if kind == "drop":
            continue
        q = dict(bank[pid], new=1)
        if "a" in v:
            q["a"] = int(v["a"]) - 1
        if v.get("s"):
            q["s"] = v["s"]
        if isinstance(v.get("o"), list) and len(v["o"]) == 4:
            q["o"] = v["o"]
        b, r, s = place[pid][:3]
        if v.get("to"):
            b, r, s = map(int, v["to"].split(":"))
        if not (0 <= q["a"] <= 3):
            continue
        add.setdefault((b, r), []).append((s, to_mcq(q)))
    index = json.load(open(f"{A}/index.json"))
    applied = set(json.load(open(f"{D}/applied.json"))) if os.path.exists(f"{D}/applied.json") else set()
    added = 0
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        have = {q["id"] for qs in m["rows"].values() for q in qs}
        for (bb, r), new in add.items():
            if bb != b:
                continue
            k = str(r)
            qs, subs = m["rows"].get(k, []), m["subs"].get(k, [])
            subs = subs or [-1] * len(qs)
            pairs = list(zip(subs, qs))
            for s, q in new:
                if q["id"] in have:
                    continue
                # after the PYQs already in that subsection, before its own MCQs
                at = None
                for i, (ps, pq) in enumerate(pairs):
                    if ps == s:
                        at = i + 1 if pq["id"].startswith("y") else (at if at is not None else i)
                        if not pq["id"].startswith("y"):
                            break
                if at is None:  # no question in that subsection yet: in subsection order
                    at = next((i for i, (ps, _) in enumerate(pairs) if (ps < 0, ps) > (s < 0, s)), len(pairs))
                pairs.insert(at, (s, q))
                have.add(q["id"])
                applied.add(q["id"])
                added += 1
            m["rows"][k] = [q for _, q in pairs]
            m["subs"][k] = [s for s, _ in pairs]
            index["books"][b - 1]["rows"][r]["q"] = len(pairs)
        json.dump(m, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    json.dump(sorted(applied), open(f"{D}/applied.json", "w"))
    print(f"checked {len(verdict)}: {stats}; added {added} PYQs to APPSC Complete (all Arihant PYQs in the app: {len(applied)})")


if __name__ == "__main__":
    main(sys.argv[1:])
