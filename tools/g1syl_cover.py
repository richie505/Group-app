"""Group 1 Prelims: coverage of every syllabus leaf by APPSC Complete's subsections (data/g1syl/sec-out-*.jsonl)
-> data/g1syl/coverage.md and data/g1syl/coverage.json {leaf: {"subs": n, "mcqs": n, "pyqs": n}}."""
import collections, glob, json
A = "app/src/complete/assets"
L = json.load(open("data/g1syl/leaves.json"))["leaves"]
M = {}
for f in sorted(glob.glob("data/g1syl/sec-out-[0-9].jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l); M[o["key"]] = o
cov = {x["leaf"]: {"subs": 0, "mcqs": 0, "pyqs": 0, "where": []} for x in L}
beyond = {"subs": 0, "mcqs": 0, "sections": 0}
for b in range(1, 7):
    bk = json.load(open(f"{A}/book{b}.json")); m = json.load(open(f"{A}/mcq{b}.json"))
    rows = [r for u in bk["units"] for r in u["rows"]]
    for i, r in enumerate(rows):
        o = M[f"{b}:{i}"]; subs = m["subs"].get(str(i), []); L_ = m["rows"].get(str(i), [])
        if not o["leaves"]: beyond["sections"] += 1
        per = collections.Counter(); py = collections.Counter()
        for q, s in zip(L_, subs):
            per[s] += 1; py[s] += q["id"].startswith("y")
        for j, lf in o["subs"].items():
            j = int(j)
            if lf == "beyond":
                beyond["subs"] += 1; beyond["mcqs"] += per[j]; continue
            c = cov[lf]; c["subs"] += 1; c["mcqs"] += per[j]; c["pyqs"] += py[j]
            if len(c["where"]) < 4: c["where"].append(f"{b}:{i}:{j} {r['secs'][j]['t'][:50]}")
        if per[-1] and o["leaves"]:  # section-wide MCQs: the section's first leaf
            cov[o["leaves"][0]]["mcqs"] += per[-1]
json.dump(cov, open("data/g1syl/coverage.json", "w"), ensure_ascii=False, indent=0)
with open("data/g1syl/coverage.md", "w") as f:
    f.write(f"# Group 1 Prelims: syllabus coverage\n\nBeyond the syllabus (removed): {beyond}\n\n")
    for x in L:
        c = cov[x["leaf"]]
        f.write(f"- **{x['leaf']}** {x['text']} — {c['subs']} pages, {c['mcqs']} MCQs ({c['pyqs']} PYQs){'  ⚠ THIN' if c['subs'] < 2 or c['mcqs'] < 25 else ''}\n")
thin = [x for x in L if cov[x["leaf"]]["subs"] < 2 or cov[x["leaf"]]["mcqs"] < 25]
print("beyond", beyond, "| thin leaves", len(thin), "of", len(L))
for x in thin: print(" ", x["leaf"], x["text"][:60], cov[x["leaf"]]["subs"], cov[x["leaf"]]["mcqs"])
