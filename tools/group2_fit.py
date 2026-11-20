"""Group 2: only what the official Group 2 syllabus asks. Applies the hand-checked decisions on the content once judged
"beyond the syllabus" (data/g2fit/job-N.out.jsonl): each page / MCQ either fits a leaf (kept, filed under it) or is
removed. Removed pages are hidden (counted as read), removed MCQs dropped, a section left with nothing is not listed.
Questions from Group 2's own papers are never removed (they were asked in Group 2).

    python3 tools/group2_build.py <start> && python3 tools/group2_fit.py && python3 tools/build_plan_mcq.py app/src/group2/assets
"""
import collections, glob, json, re

G = "app/src/group2/assets"
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
SUB, MCQ = {}, {}
for f in sorted(glob.glob("data/g2fit/job-*.out.jsonl")):
    inp = {j["key"]: j for j in map(json.loads, open(f.replace(".out", "")))}
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            t = inp[o["key"]]["title"]
            for j, v in o.get("subs", {}).items():
                SUB[(t, int(j))] = v
            MCQ.update(o.get("mcqs", {}))
# the second check (Nov 2026) of the removed PYQs: those that fit a line after all are kept, filed under it
for f in sorted(glob.glob("data/g2audit/pyq-*.out.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            # (old news filed as "current events" stays out: a 2001-2019 venue is not a current event)
            if o.get("d") and o["d"] != "remove" and not o["d"].startswith("P4.1") and MCQ.get(o["id"]) == "remove":
                MCQ[o["id"]] = o["d"]
syl = J(f"{G}/syllabus.json")
PAPER = {i for p in syl["papers"] for i in p["ids"]}
empty, idx, st = J(f"{G}/empty.json"), J(f"{G}/index.json"), collections.Counter()
hidden = set()
SEEN = set()
for b in range(1, 7):
    bk, m = J(f"{G}/book{b}.json"), J(f"{G}/mcq{b}.json")
    rows = [r for u in bk["units"] for r in u["rows"]]
    for i, r in enumerate(rows):
        for j, x in enumerate(r["secs"]):
            if SUB.get((r["title"], j)) == "remove":
                x["b"] = [{"k": "n", "x": [["No MCQ notes here: not in the Group 2 syllabus.", 0]]}]
                st["pages hidden"] += 1
            bb = x["b"]
            if len(bb) == 1 and bb[0].get("k") == "n" and str(bb[0]["x"][0][0]).startswith("No MCQ") and f"{b}:{i}:{j}" not in empty["full"]:
                empty["full"].append(f"{b}:{i}:{j}")
        L, S = m["rows"].get(str(i), []), m["subs"].get(str(i), [])
        keep = []
        for q, s in zip(L, S):
            # a notes MCQ that is an exact copy of one already kept (same question, same options): dropped
            dk = (re.sub(r"\W+", " ", q["s"].lower()).strip(), tuple(sorted(x.strip().lower() for x in q.get("o") or [])))
            if not q["id"].startswith("y") and dk in SEEN:
                st["notes MCQ copies dropped"] += 1
                continue
            SEEN.add(dk)
            d = MCQ.get(q["id"])
            if d == "remove" and q["id"] not in PAPER:
                st["MCQs removed"] += 1
                continue
            if d and d != "remove":
                q["lf"] = d
                st["MCQs refiled"] += 1
            keep.append((q, s))
        if str(i) in m["rows"]:
            m["rows"][str(i)], m["subs"][str(i)] = [q for q, _ in keep], [s for _, s in keep]
        shown = [x for x in r["secs"] if not (len(x["b"]) == 1 and x["b"][0].get("k") == "n" and str(x["b"][0]["x"][0][0]).startswith("No MCQ"))]
        ir = idx["books"][b - 1]["rows"][i]
        ir["q"] = len(keep)
        if not shown and not keep:
            ir["hide"] = True
            hidden.add((b, i))
    W(f"{G}/book{b}.json", bk)
    W(f"{G}/mcq{b}.json", m)
W(f"{G}/empty.json", empty)
W(f"{G}/index.json", idx)
st["sections hidden"] = len(hidden)
# the syllabus, the exams list and the plan without hidden sections; each leaf's MCQ count as shipped
cnt = collections.Counter(q.get("lf") for b in range(1, 7) for L in J(f"{G}/mcq{b}.json")["rows"].values() for q in L)
for sj in syl["subjects"]:
    for u in sj["units"]:
        for ph in u["phrases"]:
            for lf in ph["leaves"]:
                lf["rows"] = [x for x in lf["rows"] if tuple(x) not in hidden]
                lf["q"] = cnt.get(lf["code"], 0)
W(f"{G}/syllabus.json", syl)
ex = J(f"{G}/exams.json")
for e in ex:
    for sj in e["subjects"]:
        for g in sj["groups"]:
            g["rows"] = [x for x in g["rows"] if tuple(x) not in hidden]
# each section listed ONCE in a subject: under the line most of its MCQs are filed under; the other lines it covers
# show it as "Covered in"
lfc = collections.defaultdict(collections.Counter)
for b in range(1, 7):
    for r, L in J(f"{G}/mcq{b}.json")["rows"].items():
        for q in L:
            lfc[(b, int(r))][q.get("lf")] += 1
for e in ex:
    for sj in e["subjects"]:
        prim = {}
        for gi, g in enumerate(sj["groups"]):
            for x in g["rows"]:
                k, c = tuple(x), lfc[tuple(x)].get(g["code"], 0)
                if k not in prim or c > prim[k][0]:
                    prim[k] = (c, gi)
        for gi, g in enumerate(sj["groups"]):
            own = [x for x in g["rows"] if prim[tuple(x)][1] == gi]
            g["see"] = [x for x in g["rows"] if prim[tuple(x)][1] != gi][:3] if not own else []
            g["rows"] = own
W(f"{G}/exams.json", ex)
plan = J(f"{G}/plan.json")
for d in plan["days"]:
    if d.get("rows"):
        d["rows"] = [x for x in d["rows"] if tuple(x["ref"]) not in hidden]
W(f"{G}/plan.json", plan)
left = sum(cnt.values())
none = [lf["code"] for sj in syl["subjects"] for u in sj["units"] for ph in u["phrases"] for lf in ph["leaves"] if not cnt.get(lf["code"])]
print(dict(st), f"| MCQs {left} | still beyond (x): {cnt.get('x', 0)} | leaves with no MCQ: {none}")
