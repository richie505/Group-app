"""Subject-wise and topic-wise crackdown of APPSC papers (companion to tools/appsc_tricks.py).

Every question of the full papers is placed in its notes topic (Group 2 papers: the Group 2 app's sections, filed by the
official syllabus; other APPSC papers: APPSC Complete's sections). Per subject:
  - question-type mix and how it changed (2017-19 vs 2023-25),
  - the elimination rules measured inside the subject (vs the subject's own base rate),
  - NEW cue words: words / phrases in statements that, in this subject, go with false (or true) far more than usual,
  - statement-count patterns, the most asked topics (all years, and 2023-25), examples of how a false statement is built.

    python3 tools/appsc_subjects.py      -> data/tricks/subjects.json
"""
import collections, glob, hashlib, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T
import g2syl_lib as L

C, G = "app/src/complete/assets", "app/src/group2/assets"
AP_RX = re.compile(r"andhra|telugu|satavahana|ikshvaku|kakatiya|vijayanagara|reddi|vengi|eastern chalukya|qutb shahi|"
                   r"golconda|hyderabad|nizam|amaravati|nagarjunakonda|vishnukundin|pallava|rayalaseema|circars|"
                   r"krishnadevaraya|tirupati|visakhapatnam", re.I)
SUBJECTS = ["Indian History", "AP History & Culture", "Polity & Constitution", "Indian Society", "Economy",
            "Geography", "Science, Technology & Environment", "Current Affairs"]


def topic_of(title):
    if re.match(r"(Overview and data|Special topics|[A-Z][a-z]{2}[–-].*?20\d\d)\s*:", title):  # Current Affairs: the category
        title = title.split(":", 1)[1].strip()
        return re.split(r"\s[–-]\s", title)[0].strip()[:70] if " - " not in title else title.split(" - ")[0].strip() + " – " + title.split(" - ")[1].split(",")[0].strip()
    parts = re.split(r"\s[–-]\s", title)
    t = parts[0].strip()
    if len(t) < 18 and len(parts) > 1:  # "Andhra Pradesh – Physiography" keeps its second part
        t = t + " – " + parts[1].split(",")[0].strip()
    return t[:70]


def locate():
    loc = {}
    for A in (G, C):
        for b in range(1, 7):
            bk = json.load(open(f"{A}/book{b}.json"))
            rows = [(u["title"], r["title"]) for u in bk["units"] for r in u["rows"]]
            m = json.load(open(f"{A}/mcq{b}.json"))
            for r, qs in m["rows"].items():
                for q in qs:
                    if q["id"].startswith("y") and q["id"] not in loc:
                        loc[q["id"]] = ("g2" if A == G else "c", b) + rows[int(r)]
    return loc


def subject(where, qsubj):
    src, b, unit, row = where
    u = unit.lower()
    if src == "g2":
        if "social and cultural history" in u:
            return "AP History & Culture"
        if "indian history" in u:
            return "AP History & Culture" if AP_RX.search(row) else "Indian History"
        if "constitution" in u:
            return "Polity & Constitution"
        if "society" in u:
            return "Indian Society"
        if "economy" in u:
            return "Economy"
        if "geography" in u:
            return "Geography"
        if "science" in u:
            return "Science, Technology & Environment"
        if "current affairs" in u:
            return "Current Affairs"
    if b == 1:
        return "AP History & Culture" if AP_RX.search(row) or "AP History" in qsubj or "Andhra" in qsubj else "Indian History"
    if b == 2:
        return "Indian Society" if re.search(r"society|rights issues|liberali", u) or qsubj == "Indian Society" else "Polity & Constitution"
    return {3: "Economy", 4: "Geography", 5: "Science, Technology & Environment", 6: "Current Affairs"}[b]


STOP = set("""the a an of in on at to for by with from and or is are was were be been being this that these those it its as into than
then there their they he she his her which what who whom whose when where why how also has have had not no its such other more most
any all only can could may might will would shall should must under over about after before between during within without upon per
one two three four first second third india indian andhra pradesh state states statement statements following given above correct
incorrect act year years new made make used use known called name named both either neither nor each every among through via
iii ii i iv v""".split())


def words(t):
    t = t.lower()
    ws = re.findall(r"[a-z][a-z\-]{2,}", t)
    return [w for w in ws if w not in STOP]


def bigrams(t):
    ws = re.findall(r"[a-z][a-z\-]{1,}", t.lower())
    return [f"{a} {b}" for a, b in zip(ws, ws[1:]) if not (a in STOP and b in STOP)]


def main():
    loc = locate()
    Q, S = [], []
    for f in T.PAPERS:
        p = json.load(open(f))
        slug = os.path.basename(f)[:-5]
        tag = L.PAPER_TAG.get(slug, (None,))[0]
        idq = (lambda n: f"y{tag}{n:03d}") if tag else (lambda n: "yQ" + hashlib.md5(f"{slug}|{n}".encode()).hexdigest()[:10])
        s, q = T.statements(f, p)
        for x in q + s:
            w = loc.get(idq(x["n"]))
            if not w:
                continue
            x["subj"] = subject(w, x.get("subject", ""))
            x["topic"] = topic_of(w[3])
        Q += [x for x in q if "subj" in x]
        S += [x for x in s if "subj" in x and x["kind"] != "item"]
    out = {}
    TYPES = ["direct", "statements", "which-statement", "matching", "assertion", "order"]
    st_q = {(x["paper"], x["n"]): x["kind"] for x in S}

    def qtype(q):
        k = st_q.get((q["paper"], q["n"]))
        if k in ("list", "pair"):
            return "statements"
        if k == "option":
            return "which-statement"
        if q["match"] or sum(bool(re.search(r"[a-dA-D]\s*-\s*[IVX1-4]+", x)) for x in q["o"]) >= 3:
            return "matching"
        if re.search(r"assertion|\(A\).*\(R\)", q["s"], re.I):
            return "assertion"
        if re.search(r"chronolog|sequence|arrange", q["s"], re.I):
            return "order"
        return "direct"

    for sj in SUBJECTS:
        qs = [q for q in Q if q["subj"] == sj]
        ss = [x for x in S if x["subj"] == sj]
        base = sum(not x["true"] for x in ss) / max(1, len(ss))
        old = [q for q in qs if q["year"] in ("2017", "2019")]
        new = [q for q in qs if q["year"] in ("2023", "2024", "2025")]
        mix = lambda L: {t: sum(qtype(q) == t for q in L) for t in TYPES}
        # rules inside the subject
        rules = {}
        for k, (title, _) in T.R.items():
            h = [x for x in ss if T.COMP[k].search(x["text"])]
            if len(h) >= 6:
                f = sum(not x["true"] for x in h)
                rules[k] = {"title": title, "n": len(h), "false": f, "pct": round(100 * f / len(h), 1)}
        # cue discovery: smoothed false rate vs subject base, n >= 5
        cnt = collections.defaultdict(lambda: [0, 0])
        for x in ss:
            for w in set(words(x["text"]) + bigrams(x["text"])):
                cnt[w][0 if x["true"] else 1] += 1
        cues = []
        for w, (t, f) in cnt.items():
            n = t + f
            if n < 5:
                continue
            r = (f + base * 2) / (n + 2)
            z = (f / n - base) / math.sqrt(max(base * (1 - base), 0.01) / n)
            cues.append((w, n, f, round(100 * f / n), round(z, 2)))
        lean_false = sorted([c for c in cues if c[4] >= 1.6], key=lambda c: -c[4])[:14]
        lean_true = sorted([c for c in cues if c[4] <= -1.6], key=lambda c: c[4])[:10]
        # statement-count patterns (list/pair sets in this subject)
        by = collections.defaultdict(list)
        for x in ss:
            if x["kind"] in ("list", "pair"):
                by[(x["paper"], x["n"])].append(x["true"])
        dist = {n: [sum(1 for v in by.values() if len(v) == n and sum(v) == k) for k in range(n + 1)] for n in (2, 3, 4)}
        # topics
        tall = collections.Counter(q["topic"] for q in qs if int(q["year"] or 0) >= 2017)
        tnew = collections.Counter(q["topic"] for q in new)
        tst = collections.defaultdict(lambda: [0, 0])
        for x in ss:
            tst[x["topic"]][0 if x["true"] else 1] += 1
        topics = [{"topic": t, "q17": n, "q23": tnew.get(t, 0),
                   "st": sum(tst[t]), "stf": tst[t][1]} for t, n in tall.most_common(14)]
        hot = [t for t, n in tnew.most_common(30) if n >= 2 and tall[t] - n <= n // 2][:6]  # mostly new in 2023-25
        # examples of false statements from recent papers, with what made them false (a cue that fires)
        ex = []
        for x in sorted([x for x in ss if not x["true"] and int(x["year"] or 0) >= 2023 and 35 < len(x["text"]) < 200],
                        key=lambda x: (x["paper"], x["n"])):
            ex.append({k: x[k] for k in ("exam", "year", "n", "text", "topic")})
        out[sj] = {"questions": len(qs), "q_old": len(old), "q_new": len(new), "mix_old": mix(old), "mix_new": mix(new),
                   "statements": len(ss), "base": round(100 * base, 1), "rules": rules,
                   "lean_false": lean_false, "lean_true": lean_true, "dist": dist, "topics": topics, "hot": hot,
                   "examples": ex[:40]}
        print(f"\n=== {sj}: {len(qs)} q ({len(old)} in 2017-19, {len(new)} in 2023-25), {len(ss)} statements, base {100 * base:.0f}% false")
        print("  mix old", mix(old), "new", mix(new))
        print("  rules", {k: (v["n"], v["pct"]) for k, v in rules.items()})
        print("  FALSE cues", [(c[0], c[1], c[3]) for c in lean_false])
        print("  TRUE cues", [(c[0], c[1], c[3]) for c in lean_true])
        print("  dist", dist)
        print("  topics", [(t["topic"][:40], t["q17"], t["q23"]) for t in topics[:8]], "hot", hot)
    json.dump(out, open("data/tricks/subjects.json", "w"), ensure_ascii=False, indent=1)
    # every false statement, for the trap anatomy (data/tricks/false-statements.jsonl; judged into twists by helpers)
    xs = {}
    for f in T.PAPERS:
        p = json.load(open(f))
        for q in p["questions"]:
            xs[(os.path.basename(f)[:-5], q["n"])] = q
    with open("data/tricks/false-statements.jsonl", "w") as fh:
        k = collections.Counter()
        for x in S:
            if x["true"]:
                continue
            q = xs[(x["paper"], x["n"])]
            k[(x["paper"], x["n"])] += 1
            fh.write(json.dumps({"id": f"{x['paper']}:{x['n']}:{k[(x['paper'], x['n'])]}", "subject": x["subj"], "topic": x["topic"],
                                 "exam": x["exam"], "year": x["year"], "statement": x["text"], "question": q["s"],
                                 "options": q.get("o"), "key": q.get("a"), "explanation": q.get("x", "")}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
