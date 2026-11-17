"""Group 2: the final section -> official-leaf map (data/g2syl/secmap-1..5.jsonl, then secmap-fix.jsonl overrides)
-> data/g2syl/secmap.json {"<Complete book>:<Complete row>": {"leaves": [...], "note": "...", "g2": "b:r", "title"}} and a coverage report data/g2syl/coverage.md."""
import json, glob, collections

L = {x["leaf"]: x for x in json.load(open("data/g2syl/leaves.json"))}
S = {(s["book"], s["row"]): s for s in map(json.loads, open("data/g2syl/sections.jsonl"))}
M = {}
for f in sorted(glob.glob("data/g2syl/secmap-[0-9].jsonl")) + ["data/g2syl/secmap-fix.jsonl"]:
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            assert all(c in L for c in o["leaves"]), o
            M[(o["book"], o["row"])] = {"leaves": o["leaves"], "note": o.get("note", "")}
assert set(M) == set(S)
# keyed by APPSC Complete rows (stable across Group 2 rebuilds): data/g2syl/rowmap.json, Group 2 row -> Complete row,
# as it was when the sections were mapped (data/g2syl/sections.jsonl uses Group 2 rows)
RM = json.load(open("data/g2syl/rowmap-at-mapping.json"))
json.dump({"%d:%d" % tuple(RM[f"{b}:{r}"]): dict(v, g2=f"{b}:{r}", title=S[(b, r)]["title"]) for (b, r), v in sorted(M.items())},
          open("data/g2syl/secmap.json", "w"), ensure_ascii=False, indent=0)
cov = collections.defaultdict(list)
for k, v in M.items():
    for c in v["leaves"]:
        cov[c].append(k)
md = ["# Group 2: official syllabus coverage", ""]
for c, x in L.items():
    secs = cov.get(c, [])
    md.append(f"- **{c}** {x['text']} — {len(secs)} sections, {sum(S[k]['pyqs'] for k in secs)} PYQs: " + "; ".join(S[k]["title"][:60] for k in secs[:4]))
md += ["", "## Beyond the official syllabus", ""] + [f"- {S[k]['title']} ({S[k]['pyqs']} PYQs) — {v['note']}" for k, v in sorted(M.items()) if not v["leaves"]]
open("data/g2syl/coverage.md", "w").write("\n".join(md) + "\n")
print(len(M), "sections;", sum(1 for v in M.values() if not v["leaves"]), "beyond the syllabus;", sum(1 for c in L if not cov.get(c)), "leaves without a section")
