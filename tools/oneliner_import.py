"""Builds APPSC One-liners' MCQs (app/src/oneliner/assets): APPSC Complete's one-liners as they are, and every other
MCQ replaced, in its place, by the one-liners written for it (work/oneliner/b<book>/out_NNN.jsonl, passing
tools/oneliner_check.py). Explanations come from APPSC Complete, not written anew: a kept one-liner keeps its own;
a one-liner made from a longer MCQ gets the bullets of that MCQ's explanation about its fact (holding its answer, or
all its words and one more of the question's, never ones about option numbers), or none. Options are shuffled (fixed per question) so the key's place varies;
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


# explanation bullets about the source MCQ's options, keys or statement numbers, which mean nothing in a one-liner
OPTREF = re.compile(r"(?i)option\s*\(?\d\)?|\bstatements?\s*\d|\bonly (one|two|three)\b|\b[1-6](\s*(,|and)\s*[1-6])+\s*only\b|"
                    r"\bkeyed\b|\bthe key\b|\bA and R\b|\bR is\b|\bA is\b|\bpairs?\s*\d")


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if len(w) > 2}


def explain(s, o, a, src):
    """(solution, additional) bullets for a one-liner from its source MCQ's explanation."""
    plain = lambda t: re.sub(r"\*\*|⚠\s*", "", t).strip()
    # "Statement 1 correct:", "Statement B is wrong:", "A:", "II:" labels of the source MCQ mean nothing here; what
    # follows them is the (corrected) fact
    label = re.compile(r"^\s*(\*\*)?(Statement\s+[A-D1-6](\s+(is\s+)?(wrong|correct|right|true|false|incorrect))?|[A-DR1-6]|I{1,3}|IV)(\*\*)?\s*[:—–-]\s*")
    ans, qw = o[a].lower(), words(s + " " + o[a])
    aw = words(o[a])
    scored = []
    for b in src.get("xs", []) + src.get("xa", []):
        b = label.sub("", b)
        p = plain(b)
        if p and not OPTREF.search(p):
            has, n = ans in p.lower(), len(qw & words(p))
            # the answer itself, or every word of it with one more of the question's
            # (a figure must appear as it is: "15,000" is not "9,000")
            if (has and n >= 1) or (not re.search(r"\d", ans) and aw and aw <= words(p) and n >= len(aw) + 1):
                scored.append((not has, -n, b))
    scored.sort()
    picked = [b for _, _, b in scored[:3]]
    picked = [b[0].upper() + b[1:] if b[:1].islower() and not re.match(r"[a-z]+[A-Z-]", b) else b for b in picked]
    return picked[:1], picked[1:]


def shuffled(s, o, a, seed):
    order = list(range(4))
    random.Random(seed).shuffle(order)
    return [o[i] for i in order], order.index(a)


index = json.load(open(f"{C}/index.json"))
total = {"kept": 0, "made": 0, "repeat": 0, "no answer yet": 0, "made with explanation": 0}
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
                new = [(q["s"].strip(), q["o"], q["a"], q["id"], {k: q[k] for k in ("x", "xs", "xa", "tq") if q.get(k)})]
                total["kept"] += 1
            elif q["id"] in made:
                new = []
                for x in made[q["id"]]:
                    o, a = shuffled(x["s"], x["o"], x["a"], qid(x["s"], x["o"]))
                    xs, xa = explain(x["s"], x["o"], x["a"], q)
                    ex = {"xs": xs, "xa": xa, "x": " ".join(re.sub(r"\*\*|⚠\s*", "", b) for b in xs)} if xs else {}
                    total["made with explanation"] += bool(xs)
                    new.append((x["s"].strip(), o, a, qid(x["s"], x["o"]), {k: v for k, v in ex.items() if v}))
                total["made"] += len(new)
            else:
                total["no answer yet"] += 1
                continue
            for s, o, a, i, ex in new:
                key = norm(s) + "|" + norm(o[a])
                if key in seen:
                    total["repeat"] += 1
                    continue
                seen.add(key)
                out.append({"id": i, "s": s, "o": o, "a": a, **ex})
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
