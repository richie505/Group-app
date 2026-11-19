"""APPSC Group 1 Prelims: APPSC Complete cut down to the official Group 1 Prelims syllabus (05-10-2018), shipped as
the "complete" app (it replaces APPSC Complete; same rows, pages and MCQ ids, so progress carries over).

- data/g1syl/leaves.json: the syllabus as 237 leaves (tools/g1syl_tree.py); Mental Ability left out (owner's choice)
- data/g1syl/sec-out-*.jsonl: every section's pages -> a leaf or "beyond" (checked by hand)
- beyond pages are hidden (empty, counted as read) and their MCQs removed; a section with nothing left is hidden
- data/g1syl/depth-out.jsonl: a new page + MCQs for each syllabus line that was thin
- exams.json: Group 1 Prelims only; Group 2 references dropped from codes and tags

    python3 tools/group1_build.py && python3 tools/build_plan_mcq.py app/src/group1/assets
"""
import collections, glob, hashlib, json, os, random, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
# the notes MCQs in APPSC's pattern, the same passes as Group 2 (same MCQ ids): realign, retwist, direct, fixes
import notes_realign as _ra, notes_retwist as _rt, notes_direct as _nd, notes_fixes as _fx
_RA, (_RTP, _RTO), _ND, _FX = _ra.load(), _rt.load(), _nd.load(), _fx.load()
_RR = random.Random(7)
_G1P = _fx.load("data/g1pattern")  # Group 1-only notes MCQs brought to the pattern by hand (same format as the fixes)


def pattern(q):
    """a notes MCQ through APPSC's pattern, tagged "APPSC pattern · <type>" (as in Group 2)"""
    if q["id"].startswith("y"):
        return q
    if q["id"] in _RA:
        q = _ra.apply(q, _RA[q["id"]], _RR) or q
    q = _fx.apply(_fx.apply(_nd.apply(_rt.apply_all(q, _RTP, _RTO, _RR), _ND), _FX), _G1P)
    if q.get("k") in ("f", "u") or not q.get("o"):
        return q
    s_ = q["s"]
    t_ = ("Assertion–Reason" if re.search(r"assertion|\(A\).*\(R\)", s_, re.I | re.S) else
          "Matching" if _ra.NOT_SET.search(s_) and re.search(r"match|list|pair", s_, re.I) else
          "Order" if _ra.NOT_SET.search(s_) else
          "Statements" if re.search(r"(?m)^\s*\(?[1-4ivx]+[.)]\s", s_) else "Direct")
    return dict(q, tg=[x for x in (q.get("tg") or []) if not x.startswith("pattern:")] + ["pattern:" + t_])

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


def ITEM_CODE(leaf):
    """leaf "A1/3" -> APPSC Complete's code "A-1"; Paper II S&T items 18-22 are its F-1..F-5; current events G-1"""
    it = leaf.split("/")[0]
    if it.startswith("E"):
        return f"F-{int(it[1:]) - 17}"
    return "G-1" if it == "G" else f"{it[0]}-{it[1:]}"


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
                # the app hides a page whose only block is a "No MCQ ..." note (and counts it as read)
                r["secs"][j]["b"] = [{"k": "n", "x": [["No MCQ notes here: not in the Group 1 Prelims syllabus.", 0]]}]
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
        for j, x in enumerate(r["secs"]):  # pages that were already "No MCQ notes" placeholders: hidden too
            bb = x["b"]
            if len(bb) == 1 and bb[0].get("k") == "n" and str(bb[0]["x"][0][0]).startswith("No MCQ") and f"{b}:{i}:{j}" not in empty["full"]:
                empty["full"].append(f"{b}:{i}:{j}")
        whole = not [k for k, v in o["subs"].items() if v != "beyond"]
        L, S = m["rows"].get(str(i), []), m["subs"].get(str(i), [])
        keep = [(q, s) for q, s in zip(L, S) if not whole and s not in beyond]
        stats["MCQs removed"] += len(L) - len(keep)
        keep = [(pattern(q), s) for q, s in keep]
        if str(i) in m["rows"]:
            m["rows"][str(i)], m["subs"][str(i)] = [q for q, _ in keep], [s for _, s in keep]
        if whole:
            hidden_rows.add((b, i))
        # Group 1 only: its own codes and tag
        own = [c for c in r.get("codes", []) if G1.match(c)]
        if not own:  # a section that came from Group 2: the Group 1 Prelims items its pages teach
            own = sorted({ITEM_CODE(v) for v in o["subs"].values() if v != "beyond"})
        r["codes"] = own
        r["tag"] = "GROUP-I"
        ir = idx["books"][b - 1]["rows"][i]
        ir["codes"], ir["tag"] = r["codes"], "GROUP-I"
        g1 = re.search(r"G1 (\d+)", ir.get("pyq", ""))  # Group 1's own past-paper count only
        ir["pyq"] = f"G1 {g1.group(1)}" if g1 else ""
        ir["q"] = len(m["rows"].get(str(i), []))
        ir["n"] = len(r["secs"])
        ir["leaves"] = sorted({v for v in o["subs"].values() if v != "beyond"})
        if whole:
            ir["hide"] = True
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
