"""Group 2's DIRECT notes MCQs (one answer, no statements / matching / A-R / order) brought to APPSC's pattern
(tools/direct_pattern.py -> data/tricks/direct-pattern.json):

 1. number options: APPSC's decoys sit close to the key (~5-8% away); ours ~15%. tighten() pulls far decoys towards
    the key, same side, same rounding (mechanical, in the build).
 2. the key as the clearly LONGEST option (ours 39%, APPSC 33%) and
 3. the key as the "family" option (shares most words with the decoys; ours 34%, APPSC 27%):
    helpers rewrite the DECOYS only (key and facts unchanged) - data/direct/job-N.jsonl -> job-N.out.jsonl.

    python3 tools/notes_direct.py plan | check
job-N.out.jsonl: {"id": "...", "o": {"<option index>": "<new decoy>", ...}, "x": "<new explanation, only if needed>"}
"""
import collections, glob, json, math, os, random, re, statistics, sys

sys.path.insert(0, os.path.dirname(__file__))
D = "data/direct"
NUM = re.compile(r"(\s*[₹$]?\s*)([\d,]+(?:\.\d+)?)(\s*(?:%|per ?cent|crore|lakh|km|million|billion|MW|GW|hectares?|sq km|tonnes?)?\.?\s*)", re.I)


def _num(x):
    m = NUM.fullmatch(x)
    return (m.group(1), float(m.group(2).replace(",", "")), m.group(3), m.group(2)) if m else None


def tighten(q):
    """four number options (not years, not small counts): decoys more than ~12% from the key pulled to ~5-9% from it,
    each staying on its own side of the key, so the key's rank among the options is unchanged"""
    o = q.get("o") or []
    a = q.get("a", -1)
    if len(o) != 4 or not (0 <= a < 4):
        return q
    ns = [_num(x) for x in o]
    if any(n is None for n in ns):
        return q
    v = [n[1] for n in ns]
    k = v[a]
    if len(set(v)) != 4 or k < 20 or all(1000 <= x <= 2100 and float(x).is_integer() for x in v):
        return q
    unit = {n[2].strip().lower() for n in ns}
    if len(unit) != 1:
        return q
    d = sorted(abs(x - k) / k for i, x in enumerate(v) if i != a)
    if statistics.median(d) <= 0.12:
        return q
    x = q.get("x", "") or ""
    if any(ns[i][3] in x for i in range(4) if i != a):
        return q  # the explanation argues from a decoy's value: leave it
    ints = all(float(t).is_integer() for t in v)
    dec = max((len(n[3].split(".")[1]) if "." in n[3] else 0) for n in ns)
    # rounding step: about 1% of the key, a 1 / 2 / 5 x power of ten, never finer than the original figures
    step = 10 ** math.floor(math.log10(max(k * 0.01, 1e-9)))
    if ints:
        step = max(step, 1)
    zeros = min(len(str(int(t))) - len(str(int(t)).rstrip("0")) for t in v) if ints else 0
    step = max(step, 10 ** min(zeros, max(0, int(math.log10(k)) - 1)))
    rank = sorted(range(4), key=lambda i: v[i])
    above = sorted([i for i in range(4) if v[i] > k], key=lambda i: v[i])
    below = sorted([i for i in range(4) if v[i] < k], key=lambda i: -v[i])
    new = list(v)
    for side, sgn in ((above, 1), (below, -1)):
        for j, i in enumerate(side):
            target = k * (1 + sgn * (0.05 + 0.035 * j))
            if abs(v[i] - k) <= abs(target - k):
                continue
            t = round(target / step) * step
            if t == k or (sgn > 0 and t <= k) or (sgn < 0 and t <= 0) or (sgn < 0 and t >= k):
                return q
            new[i] = t
    if len(set(new)) != 4 or sorted(range(4), key=lambda i: new[i]) != rank:
        return q
    d2 = 0 if ints and step >= 1 else max(dec, max(0, -int(math.floor(math.log10(step)))))
    out = list(o)
    for i in range(4):
        if new[i] != v[i]:
            s = f"{new[i]:,.{d2}f}" if "," in ns[i][3] or ("," in ns[a][3]) else f"{new[i]:.{d2}f}"
            out[i] = ns[i][0] + s + ns[i][2]
    if len(set(out)) != 4:
        return q
    return dict(q, o=out)


def _jacc(a, b):
    a, b = set(re.findall(r"[a-z]{3,}", a.lower())), set(re.findall(r"[a-z]{3,}", b.lower()))
    return len(a & b) / max(1, len(a | b))


def giveaways(q):
    """(longest, family): the key is clearly the longest option / clearly the family option"""
    o, a = q["o"], q["a"]
    L = [len(x) for x in o]
    rest = max(L[i] for i in range(4) if i != a)
    longest = L[a] > rest and L[a] >= 1.3 * rest and L[a] - rest >= 12
    sc = [sum(_jacc(o[i], o[j]) for j in range(4) if j != i) for i in range(4)]
    others = max(sc[i] for i in range(4) if i != a)
    family = sc[a] > 0.6 and sc[a] >= 1.5 * max(others, 0.01)
    return longest, family


def direct_notes():
    import appsc_tricks as T
    import direct_pattern as DP
    import notes_pattern as NP
    qs = NP.notes_mcqs()
    S, Q = T.statements("n.json", {"questions": qs, "date": "2026"})
    by = {q["n"]: q for q in qs}
    return [by[q["n"]] for q in DP.direct(Q, S)]


def plan():
    rnd = random.Random(2027)
    jobs = []
    dq = direct_notes()
    num = sum(tighten(q) is not q for q in dq)
    for q in dq:
        if any(_num(x) for x in q["o"]) or re.search(r"\b(all|none|both|neither) of (the )?(above|these)\b", " ".join(q["o"]), re.I):
            continue
        lo, fa = giveaways(q)
        if lo or fa:
            jobs.append({"id": q["id"], "subject": q["subj"], "b": q["b"], "r": q["r"], "question": q["s"], "options": q["o"], "key": q["a"],
                         "explanation": q.get("x", ""), "fix": [w for w, f in (("longest", lo), ("family", fa)) if f]})
    rnd.shuffle(jobs)
    os.makedirs(D, exist_ok=True)
    for f in glob.glob(f"{D}/job-*.jsonl"):
        if ".out." not in f:
            os.remove(f)
    size = 450
    for i in range(0, len(jobs), size):
        with open(f"{D}/job-{i // size + 1}.jsonl", "w") as f:
            for j in sorted(jobs[i:i + size], key=lambda j: (j["b"], j["r"])):
                f.write(json.dumps(j, ensure_ascii=False) + "\n")
    print(f"{len(dq)} direct notes MCQs; {num} number questions tightened in the build;",
          f"{len(jobs)} decoy rewrites in {(len(jobs) + size - 1) // size} jobs:", collections.Counter("+".join(j["fix"]) for j in jobs))


def check():
    bad = 0
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        inp = {j["id"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        got = set()
        for l in open(f):
            if not l.strip():
                continue
            o = json.loads(l)
            j = inp.get(o.get("id"))
            ok = j is not None and o["id"] not in got and isinstance(o.get("o"), dict) and all(
                k.isdigit() and int(k) != j["key"] and 0 <= int(k) < 4 and len(v.strip()) > 0 for k, v in o["o"].items())
            if ok:
                new = [o["o"].get(str(i), x) for i, x in enumerate(j["options"])]
                ok = len({x.strip().lower() for x in new}) == 4
            got.add(o.get("id"))
            if not ok:
                bad += 1
                print("bad", f, l[:160])
        print(f"{f}: {len(got)} of {len(inp)}")
        bad += len(set(inp) - got)
    return bad


def load():
    out = {}
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        inp = {j["id"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                if o.get("id") in inp:
                    out[o["id"]] = (inp[o["id"]], o)
    return out


def apply(q, OUT):
    """the helpers' decoys (only while the question's options and key are still the ones they rewrote), then tighten()"""
    if q["id"] in OUT:
        j, o = OUT[q["id"]]
        if q.get("o") == j["options"] and q.get("a") == j["key"]:
            q = dict(q, o=[o["o"].get(str(i), x) for i, x in enumerate(q["o"])])
            if o.get("x"):
                q = {k: v for k, v in dict(q, x=o["x"]).items() if k not in ("xs", "xa")}
    return tighten(q)


if __name__ == "__main__":
    {"plan": plan, "check": lambda: sys.exit(1 if check() else 0)}[sys.argv[1]]()
