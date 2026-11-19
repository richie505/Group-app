"""APPSC Group 1 Prelims: APPSC Complete cut down to the official Group 1 Prelims syllabus (05-10-2018), shipped as
the "complete" app (it replaces APPSC Complete; same rows, pages and MCQ ids, so progress carries over).

- data/g1syl/leaves.json: the syllabus as 237 leaves (tools/g1syl_tree.py); Mental Ability left out (owner's choice)
- data/g1syl/sec-out-*.jsonl: every section's pages -> a leaf or "beyond" (checked by hand)
- beyond pages are hidden (empty, counted as read) and their MCQs removed; a section with nothing left is hidden
- data/g1syl/depth-out.jsonl: a new page + MCQs for each syllabus line that was thin
- exams.json: Group 1 Prelims only; Group 2 references dropped from codes and tags

    python3 tools/group1_build.py && python3 tools/build_plan_mcq.py app/src/group1/assets
"""
import collections, glob, hashlib, json, os, re, shutil

C = "app/src/complete/assets"
G = "app/src/group1/assets"
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
G1 = re.compile(r"^[A-G]-\d+$")

if os.path.exists(G):
    shutil.rmtree(G)
shutil.copytree(C, G)
LEAF = {x["leaf"]: x for x in J("data/g1syl/leaves.json")["leaves"]}
M = {}
for f in sorted(glob.glob("data/g1syl/sec-out-[0-9].jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            M[o["key"]] = o
DEPTH = collections.defaultdict(list)
if os.path.exists("data/g1syl/depth-out.jsonl"):
    for l in open("data/g1syl/depth-out.jsonl"):
        if l.strip():
            o = json.loads(l)
            DEPTH[o["host"]].append(o)


def bold_runs(t):
    """'a **b** c' -> [["a ",0],["b",1],[" c",0]]"""
    out = []
    for i, p in enumerate(re.split(r"\*\*", t)):
        if p:
            out.append([p, i % 2])
    return out


empty = J(f"{G}/empty.json")
hidden_rows, stats = set(), collections.Counter()
idx = J(f"{G}/index.json")
for b in range(1, 7):
    bk, m = J(f"{G}/book{b}.json"), J(f"{G}/mcq{b}.json")
    rows = [r for u in bk["units"] for r in u["rows"]]
    for i, r in enumerate(rows):
        o = M[f"{b}:{i}"]
        beyond = {int(j) for j, v in o["subs"].items() if v == "beyond"}
        for j in beyond:
            if j < len(r["secs"]):
                r["secs"][j]["empty"] = True
                empty["full"].append(f"{b}:{i}:{j}")
                stats["pages hidden"] += 1
        # a new page for a thin syllabus line, with its MCQs
        for d in DEPTH.get(f"{b}:{i}", []):
            r["secs"].append({"t": d["title"], "badges": [], "b": [{"k": "b", "x": bold_runs(x)} for x in d["bullets"]], "p": r["secs"][-1].get("p", 0)})
            j = len(r["secs"]) - 1
            o["subs"][str(j)] = d["leaf"]
            L, S = m["rows"].setdefault(str(i), []), m["subs"].setdefault(str(i), [])
            for q in d["mcqs"]:
                L.append({"id": "g1d" + hashlib.md5((q["s"] + "|".join(q["o"])).encode()).hexdigest()[:11], "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"]})
                S.append(j)
                stats["MCQs added"] += 1
            stats["pages added"] += 1
        whole = not [k for k, v in o["subs"].items() if v != "beyond"]
        L, S = m["rows"].get(str(i), []), m["subs"].get(str(i), [])
        keep = [(q, s) for q, s in zip(L, S) if not whole and s not in beyond]
        stats["MCQs removed"] += len(L) - len(keep)
        if str(i) in m["rows"]:
            m["rows"][str(i)], m["subs"][str(i)] = [q for q, _ in keep], [s for _, s in keep]
        if whole:
            hidden_rows.add((b, i))
        # Group 1 only: its own codes and tag
        r["codes"] = [c for c in r.get("codes", []) if G1.match(c)] or r.get("codes", [])[:1]
        r["tag"] = "GROUP-I"
        ir = idx["books"][b - 1]["rows"][i]
        ir["codes"], ir["tag"] = r["codes"], "GROUP-I"
        ir["q"] = len(m["rows"].get(str(i), []))
        ir["n"] = len(r["secs"])
        ir["leaves"] = sorted({v for v in o["subs"].values() if v != "beyond"})
        if whole:
            ir["hide"] = True
    idx["books"][b - 1]["pages"] = sum(1 for r in rows for x in r["secs"] if not x.get("empty"))
    W(f"{G}/book{b}.json", bk)
    W(f"{G}/mcq{b}.json", m)
W(f"{G}/empty.json", empty)
W(f"{G}/index.json", idx)
stats["sections hidden"] = len(hidden_rows)

# the syllabus tab: Group 1 Prelims only, the hidden sections left out
ex = [e for e in J(f"{G}/exams.json") if e["title"].startswith("Group 1")]
for e in ex:
    e["title"], e["sub"] = "Group 1 Prelims", "Paper I (General Studies) and Paper II (Science & Technology, Current Events)"
    for sj in e["subjects"]:
        for g in sj["groups"]:
            g["rows"] = [x for x in g["rows"] if tuple(x) not in hidden_rows]
W(f"{G}/exams.json", ex)
# the plan: hidden sections dropped from its days
plan = J(f"{G}/plan.json")
for d in plan["days"]:
    if d.get("rows"):
        d["rows"] = [x for x in d["rows"] if tuple(x["ref"]) not in hidden_rows]
W(f"{G}/plan.json", plan)
# links of removed MCQs
kept = {q["id"] for b in range(1, 7) for L in J(f"{G}/mcq{b}.json")["rows"].values() for q in L}
for f in ("notelinks.json", "mcqlinks.json", "solved.json"):
    o = J(f"{G}/{f}")
    W(f"{G}/{f}", {k: v for k, v in o.items() if k in kept or f == "mcqlinks.json"})
W(f"{G}/edition.json", {"edition": "complete", "name": "APPSC Group 1 Prelims"})
# coverage of every line, as shipped
cov = collections.Counter()
for b in range(1, 7):
    m = J(f"{G}/mcq{b}.json")
    for i, S in m["subs"].items():
        o = M[f"{b}:{i}"]
        for s in S:
            lf = o["subs"].get(str(s)) or (o["leaves"][0] if o["leaves"] else None)
            if lf and lf != "beyond":
                cov[lf] += 1
missing = [k for k in LEAF if not cov[k]]
print(dict(stats), f"| MCQs {len(kept)} | lines with no MCQ: {missing}")
