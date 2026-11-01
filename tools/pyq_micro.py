"""Micro-level answer tricks: every trick tested separately inside each subject, question angle, syllabus unit and topic,
on the keyed APPSC questions (checked against UPSC / state-PSC questions of the same segment).

    python3 tools/pyq_micro.py      -> data/pyq/micro.json

A trick "works" in a segment when its pick is the key clearly more often than chance there (binomial p < 0.10, lift >= 1.2,
at least 12 cases); a "reverse trick" is an option kind that is the key clearly less often than chance (strike it).
"""
import json, math, re, sys
from collections import defaultdict

sys.path.insert(0, "tools")
from pyq_secrets import load, kind, neg  # noqa: E402

ANGLES = [
    ("NOT / INCORRECT / EXCEPT", lambda q: q["neg"]),
    ("Statements (consider the following)", lambda q: q["kind"] in ("statements", "statement options", "how many")),
    ("Match / pairs", lambda q: q["kind"] in ("match", "pairs")),
    ("Assertion-Reason", lambda q: q["kind"] == "assertion"),
    ("Order / sequence", lambda q: q["kind"] == "sequence"),
    ("Who (person)", lambda q: re.search(r"^\s*who\b|\bwho (?:was|is|were|among|of the|wrote|founded|built|led|headed|started|introduced|established|called)|\bwhose\b|\bby whom\b|\bauthor\b|\bfounder\b|\btitle\b", q["s"], re.I)),
    ("When (year / date / period)", lambda q: re.search(r"\bwhen\b|which year|in the year|\byear\b|which century|which period|\bdate\b|\bday\b", q["s"], re.I)),
    ("Where (place / location)", lambda q: re.search(r"\bwhere\b|located|situated|\bwhich (?:state|district|city|river|country|place|town|port|region|mountain|lake|hill)", q["s"], re.I)),
    ("How much (number / % / rank)", lambda q: re.search(r"\bhow (?:much|many)\b|percent|%|\brank\b|\bshare\b|\bnumber of\b|\bgrowth rate\b|\bcrore\b|\blakh\b", q["s"], re.I)),
    ("Scheme / policy / programme", lambda q: re.search(r"scheme|yojana|mission|programme|program|abhiyan|policy|initiative|portal", q["s"], re.I)),
    ("Article / Act / Amendment / Section", lambda q: re.search(r"\barticle\b|\bact\b|amendment|\bsection\b|\bschedule\b|\bpart [ivx]+\b|constitution", q["s"], re.I)),
    ("Definition / term / known as", lambda q: re.search(r"known as|is called|called as|refers to|\bterm\b|\bmeans\b|meaning|stands for|full form|also known|popularly", q["s"], re.I)),
    ("Superlative (first / largest / highest)", lambda q: re.search(r"\b(?:first|largest|smallest|highest|lowest|longest|biggest|oldest|earliest|most|least|maximum|minimum)\b", q["s"], re.I)),
    ("Which / what (other direct fact)", lambda q: True),
]


def angle(q):
    for name, f in ANGLES:
        if f(q):
            return name


def words(t):
    return set(re.findall(r"[a-z]{4,}", t.lower()))


def num(x):
    try:
        if not re.fullmatch(r"[\d.,%\s₹a-zA-Z/()-]*", x):
            return None
        v = re.sub(r"[^\d.]", "", x)
        return float(v) if v and v.count(".") <= 1 else None
    except ValueError:
        return None


def tricks(q):
    """Each trick: name -> (picked option indexes, number of options it chose among). Hit = key in picks."""
    o, out = q["o"], {}
    L = [len(x) for x in o]
    if L.count(max(L)) == 1:
        out["Longest option"] = [L.index(max(L))]
    if L.count(min(L)) == 1:
        out["Shortest option"] = [L.index(min(L))]
    W = [words(x) for x in o]
    sim = [sum(len(W[i] & W[j]) for j in range(4) if j != i) for i in range(4)]
    if max(sim) > 0 and sim.count(max(sim)) == 1:
        out["Centre option (shares most words with the others)"] = [sim.index(max(sim))]
    if min(sim) == 0 and sim.count(0) == 1 and max(sim) > 1:
        out["Odd-one-out option (shares no word with others)"] = [sim.index(0)]
    sw = words(q["s"])
    ov = [len(W[i] & sw) for i in range(4)]
    if max(ov) > 0 and ov.count(max(ov)) == 1:
        out["Echo option (repeats the question's words)"] = [ov.index(max(ov))]
    # two near-twins: one of them is the key
    best = None
    for i in range(4):
        for j in range(i + 1, 4):
            u = W[i] | W[j]
            if u and len(W[i] & W[j]) / len(u) >= 0.5:
                best = [i, j] if best is None else "many"
    if isinstance(best, list):
        out["Near-twin pair (two options alike; key is one of them)"] = best
    v = [num(x) for x in o]
    if all(x is not None for x in v) and len(set(v)) == 4:
        s = sorted(v)
        yrs = all(1000 <= x <= 2100 for x in v)
        tag = "year" if yrs else "number"
        out[f"Middle {tag}s (2nd or 3rd of four)"] = [v.index(s[1]), v.index(s[2])]
        out[f"Smallest {tag}"] = [v.index(s[0])]
        out[f"Largest {tag}"] = [v.index(s[3])]
    digits = [bool(re.search(r"\d", x)) for x in o]
    if sum(digits) == 1:
        out["Only option with a number/date"] = [digits.index(True)]
    for name, rx in [("'None of the above / these'", r"none of the above|none of these"), ("'Neither ... nor'", r"^neither\b"),
                     ("'Both'", r"^both\b"), ("'All of the above / all'", r"all of the above|all the above|^all\b")]:
        hit = [i for i, x in enumerate(o) if re.search(rx, x.strip().lower())]
        if hit:
            out[name] = hit
    for p in range(4):
        out[f"Option {p + 1}"] = [p]
    return out


def binom_p(k, n, p):
    """One-sided tail probability of k or more (or k or fewer) hits, normal approximation with continuity."""
    if n == 0:
        return 1.0
    mu, sd = n * p, math.sqrt(n * p * (1 - p)) or 1
    z = (abs(k - mu) - 0.5) / sd
    return 0.5 * math.erfc(z / math.sqrt(2))


def evaluate(qs, min_n=12):
    acc = defaultdict(lambda: [0, 0, 0.0])  # hits, cases, expected hits
    for q in qs:
        for name, picks in tricks(q).items():
            acc[name][0] += q["a"] in picks
            acc[name][1] += 1
            acc[name][2] += len(picks) / 4
    res = []
    for name, (k, n, e) in acc.items():
        if n < min_n:
            continue
        chance = e / n
        rate = k / n
        lift = rate / chance if chance else 0
        p = binom_p(k, n, chance)
        res.append({"trick": name, "hit": k, "n": n, "rate": round(rate, 3), "chance": round(chance, 3), "lift": round(lift, 2), "p": round(p, 4)})
    return res


def keyword_truth(qs):
    from pyq_secrets import statement_stats, option_truth
    _, _, kw, KW = statement_stats([q for q in qs if q["kind"] == "statements"])
    option_truth([q for q in qs if q["kind"] in ("statement options", "pairs")], kw, KW)
    return {k: list(v) for k, v in kw.items() if v[1]}


def main():
    A = load((0,))
    Oth = load((1, 2))
    for q in A + Oth:
        q["kind"], q["neg"] = kind(q), neg(q)
        q["angle"] = angle(q)
    titles, units = {}, {}
    for b in range(1, 7):
        ri = 0
        for u in json.load(open(f"app/src/complete/assets/book{b}.json"))["units"]:
            for r in u["rows"]:
                titles[(b, ri)] = r["title"]
                units[(b, ri)] = u.get("title", "")
                ri += 1
    out = {"all": evaluate(A), "angles": {}, "subjects": {}, "kw": {}}
    for name, _ in ANGLES:
        Q = [q for q in A if q["angle"] == name]
        out["angles"][name] = {"n": len(Q), "tricks": evaluate(Q), "others": evaluate([q for q in Oth if q["angle"] == name])}
    for b in range(1, 7):
        QB = [q for q in A if q["book"] == b]
        OB = [q for q in Oth if q["book"] == b]
        s = {"n": len(QB), "tricks": evaluate(QB), "others": evaluate(OB), "angles": {}, "units": {}, "topics": {},
             "kw": keyword_truth(QB + OB)}
        for name, _ in ANGLES:
            Q = [q for q in QB if q["angle"] == name]
            if len(Q) >= 15:
                s["angles"][name] = {"n": len(Q), "tricks": evaluate(Q, 10),
                                     "others": evaluate([q for q in OB if q["angle"] == name], 10)}
        for u in sorted({units[(q["book"], q["row"])] for q in QB}):
            Q = [q for q in QB if units[(q["book"], q["row"])] == u]
            if len(Q) >= 30:
                s["units"][u] = {"n": len(Q), "tricks": evaluate(Q, 10)}
        for key in sorted({(q["book"], q["row"]) for q in QB}):
            Q = [q for q in QB if (q["book"], q["row"]) == key]
            if len(Q) >= 25:
                s["topics"][titles[key]] = {"n": len(Q), "tricks": evaluate(Q, 10)}
        out["subjects"][str(b)] = s
    json.dump(out, open("data/pyq/micro.json", "w"), ensure_ascii=False, indent=1)
    # summary
    def good(res):
        return [f"{t['trick']} {t['hit']}/{t['n']}={t['rate']:.0%} (chance {t['chance']:.0%})" for t in res if t["p"] < 0.1 and t["lift"] >= 1.2]
    def bad(res):
        return [f"{t['trick']} {t['hit']}/{t['n']}={t['rate']:.0%}" for t in res if t["p"] < 0.1 and t["lift"] <= 0.75]
    print("ALL+", good(out["all"]), "\nALL-", bad(out["all"]))
    for b, s in out["subjects"].items():
        print(f"\n### {b} n={s['n']}\n +", good(s["tricks"]), "\n -", bad(s["tricks"]))
        for a, d in s["angles"].items():
            g, bb = good(d["tricks"]), bad(d["tricks"])
            if g or bb:
                print(f"   [{a} n={d['n']}] +{g} -{bb}")
        print("   units:", {u: (d["n"], good(d["tricks"]), bad(d["tricks"])) for u, d in s["units"].items() if good(d["tricks"]) or bad(d["tricks"])})
        print("   topics:", {u[:40]: (d["n"], good(d["tricks"])) for u, d in s["topics"].items() if good(d["tricks"])})


if __name__ == "__main__":
    main()
