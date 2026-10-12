"""Applies MCQ trim answers: python3 tools/mcq_trim_import.py <book>

Rebuilds app/src/main/assets/mcq<book>.json from the untrimmed copy (saved once to
work/mcqtrim/b<book>/orig.json) and every batch that passes tools/mcq_trim_check.py, so it can be re-run
as batches come in. Updates each topic's question count ("q") in index.json.
"""
import hashlib, json, os, re, shutil, subprocess, sys
from collections import Counter

book = int(sys.argv[1])
d = f"work/mcqtrim/b{book}"
asset = f"app/src/main/assets/mcq{book}.json"
orig = f"{d}/orig.json"
if not os.path.exists(orig):
    shutil.copy(asset, orig)
mcq = json.load(open(orig))


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def qid(stem, options):  # as tools/build_notes_mcq.py
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


# stray words from other scripts left in a few generated options
FIXES = [(" בלבד", " only"), ("בלבד", "only"), ("Pegан", "Pegan"), ("完全 ", "Complete "), ("航空 ", "Air "), ("\u200b", ""), ("\u00ad", ""), ("\ufeff", ""), ("Children aged ani?", "Only children aged 0–3 years"), ("పోలవరం", "Polavaram"), ("treinta nine point three percent", "39.3 per cent")]


def clean(q):
    def fix(t):
        for a, b in FIXES:
            t = t.replace(a, b)
        return t
    return {**q, "s": relabel(fix(q["s"])), "o": [fix(o) for o in q["o"]], "x": fix(q.get("x", ""))}


def relabel(stem):
    """Match lists printed with a repeated label: "a. a. c. d." -> "a. b. c. d."; "a. List-II" -> "List-II"."""
    stem = re.sub(r"(?m)^(\s*)a\.\s+(List-II)", r"\1\2", stem)
    stem = re.sub(r"(?m)^\s*option_[a-d]\s*:.*$\n?", "", stem).rstrip()  # options printed inside the stem
    lines = stem.split("\n")
    labelled = [i for i, l in enumerate(lines) if re.match(r"\s*[a-d]\.\s", l)]
    for k in range(len(labelled) - 3):
        block = labelled[k:k + 4]
        if block[-1] - block[0] == 3 and [lines[i].lstrip()[0] for i in block] == ["a", "a", "c", "d"]:
            lines[block[1]] = re.sub(r"a\.", "b.", lines[block[1]], count=1)
    return "\n".join(lines)


decisions, why = {}, Counter()
done = 0
for f in sorted(os.listdir(d)):
    if not (f.startswith("out_") and f.endswith(".jsonl")):
        continue
    n = f[4:7]
    res = subprocess.run([sys.executable, "tools/mcq_trim_check.py", str(book), n], capture_output=True, text=True)
    if "FAIL" in res.stdout:
        print(f"skip {n} (fails the check)")
        continue
    done += 1
    for line in open(f"{d}/{f}"):
        if not line.strip():
            continue
        o = json.loads(line)
        if o["d"] == "merge":
            for i, q in enumerate(o["from"]):
                decisions[q] = o if i == 0 else {"d": "drop", "why": "merged"}
            why["merge"] += 1
        else:
            decisions[o["q"]] = o
            why[o["d"] if o["d"] == "keep" else "drop " + o.get("why", "").split()[0]] += 1

rows, subs = {}, {}
before = after = 0
for r, qs in mcq["rows"].items():
    out_q, out_s = [], []
    for j, q in enumerate(qs):
        before += 1
        o = decisions.get(f"Q{r}.{j}")
        sub = mcq["subs"][r][j]
        if o is None or o["d"] == "keep":
            out_q.append(clean(q))
            out_s.append(o.get("sub", sub) if o else sub)
        elif o["d"] == "merge":
            out_q.append(clean({"id": qid(o["s"], o["o"]), "s": o["s"], "o": o["o"], "a": o["a"], "x": o["x"], "tq": o.get("tq", "")}))
            out_s.append(o["sub"])
    if out_q:
        rows[r], subs[r] = out_q, out_s
        after += len(out_q)
# rescued "off" MCQs: filed under the topic whose notes hold their fact, unless they repeat one kept there
def words(q):
    return {w for w in re.findall(r"[a-z0-9]+", (q["s"] + " " + q["o"][q["a"]]).lower()) if len(w) > 2}


offs = {q for q, o in decisions.items() if o["d"] == "drop" and str(o.get("why", "")).startswith("off")}
moved = repeats = 0
for f in sorted(os.listdir(d)):
    if not (f.startswith("rescue_out_") and f.endswith(".jsonl")):
        continue
    for line in open(f"{d}/{f}"):
        if not line.strip():
            continue
        o = json.loads(line)
        to = o.get("to")
        if o.get("q") not in offs or not to or not re.fullmatch(r"\d+\.-?\d+", str(to)):
            continue
        r, j = map(int, o["q"][1:].split("."))
        tr, ts = (int(x) for x in str(to).split("."))
        q = clean(mcq["rows"][str(r)][j])
        target = rows.setdefault(str(tr), [])
        w = words(q)
        if any(len(w & words(k)) / max(1, len(w | words(k))) >= 0.6 for k in target):
            repeats += 1
            continue
        target.append(q)
        subs.setdefault(str(tr), []).append(ts)
        moved += 1
after += moved
if moved or repeats:
    why["rescued"] = moved
    why["rescue skipped (repeat)"] = repeats

# cross-topic repeats picked by tools/mcq_trim_xdup_export.py review
# (a drop is skipped when its pair partner is already dropped, so one copy of each fact always stays)
gone = set()
for f in sorted(os.listdir(d)):
    if not (f.startswith("xdup_out_") and f.endswith(".jsonl")):
        continue
    src = open(f"{d}/xdup_in_{f[9:12]}.md").read()
    pairs = {int(p): re.findall(r"\[(n[0-9a-f]+)\]", body)
             for p, body in re.findall(r"=== PAIR (\d+).*?\n(.*?)(?=\n=== PAIR |\Z)", src, re.S)}
    for line in open(f"{d}/{f}"):
        o = json.loads(line) if line.strip() else {}
        ids = pairs.get(o.get("p"), [])
        if o.get("drop") in ids and not any(i in gone for i in ids if i != o["drop"]):
            gone.add(o["drop"])
if gone:
    for r in list(rows):
        keep = [i for i, q in enumerate(rows[r]) if q["id"] not in gone]
        after -= len(rows[r]) - len(keep)
        rows[r], subs[r] = [rows[r][i] for i in keep], [subs[r][i] for i in keep]
    why["cross-topic repeat"] = len(gone)

json.dump({"rows": rows, "units": mcq["units"], "subs": subs}, open(asset, "w"), ensure_ascii=False, separators=(",", ":"))

index_path = "app/src/main/assets/index.json"
index = json.load(open(index_path))
for ri, row in enumerate(index["books"][book - 1]["rows"]):
    row["q"] = len(rows.get(str(ri), []))
open(index_path, "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
print(f"book {book}: {done} batches applied; {before} -> {after} MCQs; " + ", ".join(f"{k} {v}" for k, v in sorted(why.items())))
