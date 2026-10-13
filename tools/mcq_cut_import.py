"""Applies MCQ coverage answers: python3 tools/mcq_cut_import.py <book>

Rebuilds app/src/main/assets/mcq<book>.json from the original copy (saved once to work/mcqcut/b<book>/orig.json)
and every batch that passes tools/mcq_cut_check.py; topics in batches not yet answered keep all their MCQs, so
it can be re-run as batches come in. Kept MCQs keep their ids; moved ones change page; new ones (written for an
important fact no MCQ tested) get an id from their text and go after the page's kept MCQs. Updates each topic's
question count ("q") in index.json and writes work/mcqcut/b<book>/coverage.json (facts per page).
"""
import hashlib, json, os, re, shutil, subprocess, sys

book = int(sys.argv[1])
d = f"work/mcqcut/b{book}"
asset = f"app/src/main/assets/mcq{book}.json"
orig = f"{d}/orig.json"
if not os.path.exists(orig):
    shutil.copy(asset, orig)
mcq = json.load(open(orig))


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def qid(stem, options):  # as tools/build_notes_mcq.py
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


plan = {}      # row -> list of (page, order, mcq)
coverage = {}  # "row:sub" -> facts
done = 0
for f in sorted(os.listdir(d)):
    if not (f.startswith("out_") and f.endswith(".jsonl")):
        continue
    n = f[4:7]
    res = subprocess.run([sys.executable, "tools/mcq_cut_check.py", str(book), n], capture_output=True, text=True)
    if "FAIL" in res.stdout:
        print(f"skip {n}: does not pass the check")
        continue
    done += 1
    for line in open(f"{d}/in_{n}.md"):
        if line.startswith("=== ROW "):
            plan.setdefault(int(line[8:].split(" |")[0]), [])
    for line in open(f"{d}/{f}"):
        if not line.strip():
            continue
        o = json.loads(line)
        r, sub = int(o["row"]), int(o["sub"])
        qs = mcq["rows"][str(r)] if str(r) in mcq["rows"] else []
        for q in o.get("keep", []):
            j = int(q.split(".")[1])
            plan[r].append((sub, j, qs[j]))
        for q, k in o.get("move", {}).items():
            j = int(q.split(".")[1])
            plan[r].append((k, j, qs[j]))
        for i, q in enumerate(o.get("new", [])):
            m = {"id": qid(q["s"], q["o"]), "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"], "tq": q.get("tq", "")}
            plan[r].append((sub, 10 ** 6 + i, m))
        coverage[f"{r}:{sub}"] = o.get("facts", [])

before = after = added = 0
for r, items in plan.items():
    before += len(mcq["rows"].get(str(r), []))
    items.sort(key=lambda t: (t[0], t[1]))
    mcq["rows"][str(r)] = [m for _, _, m in items]
    mcq["subs"][str(r)] = [s for s, _, _ in items]
    added += sum(1 for _, j, _ in items if j >= 10 ** 6)
total = sum(len(v) for v in mcq["rows"].values())

index = json.load(open("app/src/main/assets/index.json"))
for ri, row in enumerate(index["books"][book - 1]["rows"]):
    row["q"] = len(mcq["rows"].get(str(ri), []))
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
open(asset, "w").write(dump(mcq))
open("app/src/main/assets/index.json", "w").write(dump(index))
json.dump(coverage, open(f"{d}/coverage.json", "w"), ensure_ascii=False)
print(f"book {book}: {done} batches applied; topics decided {len(plan)}: {before} MCQs -> "
      f"{sum(len(mcq['rows'].get(str(r), [])) for r in plan)} ({added} new); book total {total}")
