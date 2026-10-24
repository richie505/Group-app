"""Builds APPSC One-liners' MCQs (app/src/oneliner/assets): APPSC Complete's one-liners as they are, and every other
MCQ replaced, in its place, by the one-liners written for it (work/oneliner/b<book>/out_NNN.jsonl, passing
tools/oneliner_check.py). No explanations. Options are shuffled (fixed per question) so the key's place varies;
a one-liner repeating one already in its topic is left out. Also writes index.json (topic MCQ counts) and
planmcq.json (tools/build_plan_mcq.py).

    python3 tools/oneliner_import.py
"""
import glob, hashlib, json, os, random, re, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from oneliner_kind import oneliner

C, O = "app/src/complete/assets", "app/src/oneliner/assets"


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def qid(s, o):
    return "o" + hashlib.sha1((norm(s) + "|" + "|".join(sorted(norm(x) for x in o))).encode()).hexdigest()[:11]


def shuffled(s, o, a, seed):
    order = list(range(4))
    random.Random(seed).shuffle(order)
    return [o[i] for i in order], order.index(a)


index = json.load(open(f"{C}/index.json"))
total = {"kept": 0, "made": 0, "repeat": 0, "no answer yet": 0}
for b in range(1, 7):
    made = {}
    for f in sorted(glob.glob(f"work/oneliner/b{b}/out_*.jsonl")):
        n = f[-9:-6]
        if "PASS" not in subprocess.run([sys.executable, "tools/oneliner_check.py", str(b), n], capture_output=True, text=True).stdout:
            print(f"book {b}: batch {n} skipped (fails the check)")
            continue
        for line in open(f):
            if line.strip():
                x = json.loads(line)
                if "skip" not in x:
                    made.setdefault(x["q"], []).append(x)
    m = json.load(open(f"{C}/mcq{b}.json"))
    rows, subs = {}, {}
    for r, qs in m["rows"].items():
        out, out_s, seen = [], [], set()
        for q, sub in zip(qs, m["subs"][r]):
            if oneliner(q):
                new = [(q["s"].strip(), q["o"], q["a"], q["id"])]
                total["kept"] += 1
            elif q["id"] in made:
                new = []
                for x in made[q["id"]]:
                    o, a = shuffled(x["s"], x["o"], x["a"], qid(x["s"], x["o"]))
                    new.append((x["s"].strip(), o, a, qid(x["s"], x["o"])))
                total["made"] += len(new)
            else:
                total["no answer yet"] += 1
                continue
            for s, o, a, i in new:
                key = norm(s) + "|" + norm(o[a])
                if key in seen:
                    total["repeat"] += 1
                    continue
                seen.add(key)
                out.append({"id": i, "s": s, "o": o, "a": a})
                out_s.append(sub)
        if out:
            rows[r], subs[r] = out, out_s
    os.makedirs(O, exist_ok=True)
    json.dump({"rows": rows, "units": {}, "subs": subs}, open(f"{O}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    for ri, row in enumerate(index["books"][b - 1]["rows"]):
        row["q"] = len(rows.get(str(ri), []))
    print(f"book {b}: {sum(map(len, rows.values()))} one-liners")
open(f"{O}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
subprocess.run([sys.executable, "tools/build_plan_mcq.py", O], check=True)
print(", ".join(f"{k} {v}" for k, v in total.items()))
