"""Puts the 3-statement MCQs (data/m3/out/*.md, written per data/m3/INSTRUCTIONS.md) into APPSC Complete.

For each block: "Consider the following statements about <topic>: 1. 2. 3. Which of the statements given above
is/are correct?" (the pre-2022 APPSC pattern), four code options ("1 and 2 only" ...) with the key decided in
tools/m3_plan.py, and the three explanation lines. The merged MCQ takes the first one-fact MCQ's place; the three
originals are kept in data/m3/originals.json (and the "of" field), so nothing is lost and it can be undone.
A block that is missing, SKIPped or malformed leaves its three MCQs as they were.

    python3 tools/m3_build.py            (then tools/build_plan_mcq.py and tools/dup_report.py)
"""
import glob, json, os, random, re

A = "app/src/complete/assets"
CODES = ["1 only", "2 only", "3 only", "1 and 2 only", "2 and 3 only", "1 and 3 only", "1, 2 and 3"]
SETS = [{1}, {2}, {3}, {1, 2}, {2, 3}, {1, 3}, {1, 2, 3}]


def parse():
    blocks = {}
    for f in glob.glob("data/m3/out/*.md"):
        cur = None
        for line in open(f).read().split("\n"):
            m = re.match(r"^## M (m[0-9a-f]{12})", line)
            if m:
                cur = blocks.setdefault(m.group(1), {"st": {}, "why": {}})
                continue
            if cur is None:
                continue
            if line.startswith("TOPIC:"):
                cur["topic"] = line[6:].strip()
            elif re.match(r"^[123]\. ", line):
                cur["st"][int(line[0])] = line[3:].strip()
            elif re.match(r"^WHY[123]:", line):
                cur["why"][int(line[3])] = line[5:].strip()
    return blocks


def main():
    plan = json.load(open("data/m3/plan.json"))
    blocks = parse()
    rnd = random.Random(7)
    merged = {}
    for mid, p in plan.items():
        b = blocks.get(mid)
        if not b or b.get("topic", "").upper() == "SKIP" or len(b["st"]) != 3 or len(b["why"]) != 3:
            continue
        if any(len(b["st"][i]) < 12 or "?" in b["st"][i] for i in (1, 2, 3)):
            continue
        true = {i + 1 for i, t in enumerate(p["truth"]) if t}
        # an explanation that contradicts the key would mislead: leave such a block out
        if any(b["why"][i].lower().startswith("incorrect") == (i in true) for i in (1, 2, 3)):
            continue
        right = SETS.index(true)
        others = rnd.sample([i for i in range(7) if i != right], 3)
        opts = sorted([right] + others)
        topic = b["topic"].rstrip(":. ")
        stem = (f"Consider the following statements about {topic}:\n" +
                "\n".join(f"{i}. {b['st'][i]}" for i in (1, 2, 3)) +
                "\nWhich of the statements given above is/are correct?")
        merged[mid] = {
            "id": mid, "s": stem, "o": [CODES[i] for i in opts], "a": opts.index(right),
            "x": "\n".join(f"Statement {i}: {b['why'][i]}" for i in (1, 2, 3)), "src": "app (3 statements)", "of": p["ids"],
        }
    # into the books: the merged MCQ where its first original was; originals kept aside
    originals = {}
    if os.path.exists("data/m3/originals.json"):
        raise SystemExit("data/m3/originals.json exists: the merge is already applied (undo it first)")
    by_first = {m["of"][0]: m for m in merged.values()}
    gone = {i for m in merged.values() for i in m["of"][1:]}
    for bk in range(1, 7):
        path = f"{A}/mcq{bk}.json"
        d = json.load(open(path))
        for k, v in d["rows"].items():
            subs = d["subs"].get(k)
            nv, ns = [], []
            for i, q in enumerate(v):
                if q["id"] in by_first:
                    originals[q["id"]] = q
                    nv.append(by_first[q["id"]])
                    if subs is not None:
                        ns.append(plan[by_first[q["id"]]["id"]]["s"] if plan[by_first[q["id"]]["id"]]["s"] >= 0 else subs[i])
                elif q["id"] in gone:
                    originals[q["id"]] = q
                else:
                    nv.append(q)
                    if subs is not None:
                        ns.append(subs[i])
            d["rows"][k] = nv
            if subs is not None:
                d["subs"][k] = ns
        open(path, "w").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    json.dump(originals, open("data/m3/originals.json", "w"), ensure_ascii=False, separators=(",", ":"))
    # the notes index's per-section MCQ counts
    idx = json.load(open(f"{A}/index.json"))
    for b in idx["books"]:
        rows = json.load(open(f"{A}/mcq{b['id']}.json"))["rows"]
        for i, r in enumerate(b["rows"]):
            r["q"] = len(rows.get(str(i), []))
    open(f"{A}/index.json", "w").write(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(merged)} merged MCQs from {3 * len(merged)} one-fact MCQs; {len(plan) - len(merged)} blocks left as they were")


if __name__ == "__main__":
    main()
