"""Complete: drops the notes MCQs that only repeat a PYQ of the same topic (data/pyqrepeat/job-*.out.jsonl,
verdict "drop"; judged by helpers from tools/pyq_repeat_candidates.py). Current-affairs / latest MCQs are never
dropped. Keeps mcq<b>.json rows and subs in step, the index "q" counts and notelinks.json; dropped MCQs go to
data/pyqrepeat/archive.jsonl (with their book, row and subsection) so they can be put back.
Idempotent: ids already gone are skipped. Then run tools/build_plan_mcq.py.

    python3 tools/pyq_repeat_apply.py [assets dir=app/src/complete/assets] [--dry]
"""
import glob, json, os, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
A = args[0] if args else "app/src/complete/assets"
dry = "--dry" in sys.argv
D = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))

drop = {}
for f in sorted(glob.glob("data/pyqrepeat/job-*.out.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            if o.get("verdict") == "drop":
                drop[o["id"]] = o
protect = lambda q: q["id"].startswith("ca") or q.get("src") == "ca" or {"updated", "added"} & set(q.get("tg", []))

index = json.load(open(f"{A}/index.json"))
gone, arc = set(), []
for b in range(1, 7):
    p = f"{A}/mcq{b}.json"
    m = json.load(open(p))
    changed = False
    for r, qs in m["rows"].items():
        subs = m["subs"].get(r) or [-1] * len(qs)
        out = [(q, s) for q, s in zip(qs, subs) if not (q["id"] in drop and not q["id"].startswith("y") and not protect(q))]
        if len(out) == len(qs):
            continue
        for q, s in zip(qs, subs):
            if (q, s) not in out:
                gone.add(q["id"])
                arc.append({"book": b, "row": int(r), "sub": s, "pyq": drop[q["id"]].get("pyq"), "why": drop[q["id"]].get("why"), "q": q})
        m["rows"][r] = [q for q, _ in out]
        if r in m["subs"]:
            m["subs"][r] = [s for _, s in out]
        index["books"][b - 1]["rows"][int(r)]["q"] = len(out)
        changed = True
    if changed and not dry:
        open(p, "w").write(D(m))
if not dry and gone:
    open(f"{A}/index.json", "w").write(D(index))
    nl = f"{A}/notelinks.json"
    if os.path.exists(nl):
        links = json.load(open(nl))
        open(nl, "w").write(D({k: v for k, v in links.items() if k not in gone}))
    if A.endswith("complete/assets"):
        with open("data/pyqrepeat/archive.jsonl", "a") as f:
            f.write("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in arc))
print(f"{A}: {len(gone)} notes MCQs {'would be ' if dry else ''}dropped as repeats of a PYQ ({len(drop)} judged drop)")
