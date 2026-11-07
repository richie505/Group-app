"""How far the app's own MCQs (APPSC Complete) cover the blueprint keyword angles and the APPSC PYQ angles.

    python3 tools/angle_check.py            writes data/angle2/coverage.json and prints a summary
Rough, word-based: a keyword counts as covered when some own MCQ of the unit's app topics shares at least half of
its distinctive words (at least 2); an APPSC PYQ counts as covered when an own MCQ of its topic has TF-IDF cosine
>= 0.35 with it (stem + correct option). An agent check (data/angle2/INSTRUCTIONS.md) gives the real judgement.
"""
import glob, json, math, re, collections
A = "app/src/complete/assets"
STOP = set("the of and in to a an is was were which with by for on at as from that this are be or its it his her their following correct statements statement consider given select code above none both only one two three four not who what when where how".split())


def toks(t):
    return [w for w in re.findall(r"[a-z][a-z0-9\-]{2,}|\d{3,4}", t.lower()) if w not in STOP]


def shape(s):
    l = s.lower()
    if "assertion" in l: return "assertion"
    if re.search(r"match|pairs?\b|list[- ]?i\b", l): return "match"
    if re.search(r"chronolog|sequence|correct order", l): return "sequence"
    if re.search(r"statements?", l): return "statements"
    if re.search(r"\bnot\b|incorrect|false", l): return "NOT"
    return "one-liner"


bank = collections.defaultdict(list)
for f in glob.glob(f"{A}/mcq[0-9]*.json"):
    b = int(re.search(r"mcq(\d)", f).group(1))
    for r, qs in json.load(open(f))["rows"].items():
        for q in qs:
            bank[(b, int(r))].append(q)
units = []
for f in sorted(glob.glob("data/blueprint/src/U*.md")):
    t = open(f).read()
    spec = t.split("\n# NOTES OF APP TOPIC")[0]
    tops = [tuple(map(int, m)) for m in re.findall(r"^# NOTES OF APP TOPIC (\d):(\d+)", t, re.M)]
    kws = re.findall(r"^\s+\d+\. (.+)$", spec.split("**Keywords:**")[1].split("- **Latest")[0], re.M) if "**Keywords:**" in spec else []
    tier = (re.search(r"\*\*Tier:\*\* (\w+)", spec) or [None, "?"])[1]
    units.append((f.split("/")[-1][:-3], tier, tops, kws))
# document frequencies over own MCQs for idf
own_all = [q for qs in bank.values() for q in qs if not q["id"].startswith("y")]
df = collections.Counter(w for q in own_all for w in set(toks(q["s"] + " " + q["o"][q["a"]] if 0 <= q["a"] < len(q["o"]) else q["s"])))
N = len(own_all)
idf = lambda w: math.log((N + 1) / (df.get(w, 0) + 1)) + 1


def vec(q):
    t = q["s"] + " " + (q["o"][q["a"]] if isinstance(q["a"], int) and 0 <= q["a"] < len(q["o"]) else "")
    c = collections.Counter(toks(t))
    v = {w: n * idf(w) for w, n in c.items()}
    nn = math.sqrt(sum(x * x for x in v.values())) or 1
    return {w: x / nn for w, x in v.items()}


out = {"units": [], "topics": {}}
kw_tot = kw_cov = 0
tier_c = collections.defaultdict(lambda: [0, 0])
for u, tier, tops, kws in units:
    own = [q for t in tops for q in bank.get(t, []) if not q["id"].startswith("y")]
    owntext = [set(toks(q["s"] + " " + " ".join(q["o"]) + " " + q.get("x", ""))) for q in own]
    res = []
    for k in kws:
        kt = {w for w in toks(re.sub(r"\[.*?\]", "", k)) if df.get(w, 0) < 2000} or set(toks(k))
        need = max(2, len(kt) // 2) if len(kt) >= 2 else 1
        best = max((len(kt & ot) for ot in owntext), default=0)
        ok = best >= min(need, 4)
        res.append(ok)
        kw_tot += 1; kw_cov += ok; tier_c[tier][0] += 1; tier_c[tier][1] += ok
    out["units"].append({"u": u, "tier": tier, "topics": [f"{b}:{r}" for b, r in tops], "kw": len(kws), "cov": sum(res),
                         "missing": [k for k, ok in zip(kws, res) if not ok]})
sh_p, sh_o = collections.Counter(), collections.Counter()
py_tot = py_cov = 0
for (b, r), qs in bank.items():
    own = [q for q in qs if not q["id"].startswith("y")]
    ov = [vec(q) for q in own]
    aps = [q for q in qs if q["id"].startswith("y") and q.get("ap")]
    for q in own: sh_o[shape(q["s"])] += 1
    unc = []
    for p in aps:
        sh_p[shape(p["s"])] += 1
        pv = vec(p)
        best = max((sum(pv[w] * o.get(w, 0) for w in pv) for o in ov), default=0)
        py_tot += 1
        if best >= .35: py_cov += 1
        else: unc.append(p["id"])
    out["topics"][f"{b}:{r}"] = {"own": len(own), "appsc": len(aps), "appsc_uncovered": unc}
json.dump(out, open("data/angle2/coverage.json", "w"), ensure_ascii=False, indent=0)
print(f"blueprint keyword angles: {kw_cov}/{kw_tot} covered by own MCQs ({kw_cov/kw_tot:.0%})")
for t, (a, c) in sorted(tier_c.items()): print(f"  {t}: {c}/{a} ({c/a:.0%})")
print(f"APPSC PYQs with an own MCQ on the same angle: {py_cov}/{py_tot} ({py_cov/py_tot:.0%})")
tp, to = sum(sh_p.values()), sum(sh_o.values())
print("shape mix   APPSC PYQs   own MCQs")
for s in ["one-liner", "statements", "NOT", "match", "assertion", "sequence"]:
    print(f"  {s:11} {sh_p[s]/tp:6.0%}   {sh_o[s]/to:6.0%}")
