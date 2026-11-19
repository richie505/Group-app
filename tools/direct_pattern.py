"""APPSC's pattern for DIRECT single-answer questions (no statements, matching, A-R or ordering), from APPSC's own
papers and the app's whole PYQ bank, against Group 2's direct notes MCQs - per subject.

    python3 tools/direct_pattern.py      -> data/tricks/direct-pattern.json (+ summary)
"""
import collections, json, os, re, statistics, sys

sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T
import appsc_subjects as AS

ASK = [("who", r"^\s*who\b|\bwho (was|is|were|wrote|founded|built|led|headed|chaired|became)\b|\bby whom\b"),
       ("when / which year", r"\bwhen\b|\bwhich year\b|\bin which year\b|\byear\b.*\?$"),
       ("where / which place", r"\bwhere\b|\bwhich (place|city|state|district|country|river|region|site|town|village|port)\b|\blocated\b"),
       ("how many / how much", r"\bhow (many|much)\b|\bwhat (is|was) the (number|percentage|share|rate|amount)\b"),
       ("NOT / EXCEPT", r"\bnot\b|\bexcept\b|\bincorrect\b|\bodd one\b|\bfalse\b"),
       ("superlative / first", r"\b(first|largest|highest|longest|oldest|smallest|lowest|biggest|most|least|last)\b"),
       ("which body / scheme / act", r"\bwhich (body|organi[sz]ation|ministry|committee|commission|scheme|act|article|schedule|institution|agency)\b"),
       ("definition / concept", r"\b(is called|is known as|refers to|means|is defined|is the term|stands for)\b")]
ASKC = [(n, re.compile(p, re.I)) for n, p in ASK]


def ask(s):
    for n, rx in ASKC:
        if rx.search(s):
            return n
    return "other what / which"


def kind(o):
    t = o.strip()
    if re.fullmatch(r"[\d,.\s₹$%-]+(crore|lakh|million|billion|km|years?|days?|per ?cent|th|st|nd|rd|AD|BC|CE|BCE)?\.?", t, re.I):
        return "year" if re.fullmatch(r"(1[0-9]{3}|20[0-9]{2})\s*(AD|CE)?", t) else "number"
    if len(t.split()) <= 4 and t[:1].isupper():
        return "name"
    return "phrase" if len(t.split()) <= 9 else "sentence"


def nums(o):
    v = []
    for x in o:
        m = re.search(r"[\d][\d,]*(\.\d+)?", x)
        if not m:
            return None
        v.append(float(m.group(0).replace(",", "")))
    return v if len(set(v)) == 4 else None


def jacc(a, b):
    a, b = set(re.findall(r"[a-z]{3,}", a.lower())), set(re.findall(r"[a-z]{3,}", b.lower()))
    return len(a & b) / max(1, len(a | b))


def profile(Q):
    out = {}
    n = len(Q)
    if not n:
        return {}
    out["n"] = n
    out["ask"] = {k: round(100 * v / n) for k, v in collections.Counter(ask(q["s"]) for q in Q).most_common()}
    kinds = [tuple(sorted(set(kind(x) for x in q["o"]))) for q in Q]
    out["same_kind"] = round(100 * sum(len(k) == 1 for k in kinds) / n)
    out["opt_kind"] = {"/".join(k): round(100 * v / n) for k, v in collections.Counter(kinds).most_common(5)}
    pos = collections.Counter(q["a"] for q in Q)
    out["pos"] = [round(100 * pos[i] / n) for i in range(4)]
    # length: rank of the key among option lengths (0 = shortest, 3 = longest)
    lr = collections.Counter()
    for q in Q:
        L = [len(x) for x in q["o"]]
        if len(set(L)) == 4:
            lr[sorted(range(4), key=lambda i: L[i]).index(q["a"])] += 1
    out["key_len_rank"] = [round(100 * lr[i] / max(1, sum(lr.values()))) for i in range(4)]
    # numbers / years
    mid = tot = 0
    spread = []
    for q in Q:
        v = nums(q["o"])
        if v and all(kind(x) in ("number", "year") for x in q["o"]):
            tot += 1
            order = sorted(range(4), key=lambda i: v[i])
            mid += order.index(q["a"]) in (1, 2)
            k = v[q["a"]]
            if k:
                spread.append(statistics.median([abs(x - k) / abs(k) for i, x in enumerate(v) if i != q["a"]]))
    out["numeric"] = [tot, round(100 * mid / max(1, tot)), round(100 * statistics.median(spread), 1) if spread else None]
    # key vs decoys: does the key share more words with the decoys than they do with each other ("family" option)?
    fam = famn = 0
    for q in Q:
        o = q["o"]
        if any(kind(x) in ("number", "year") for x in o):
            continue
        sc = [sum(jacc(o[i], o[j]) for j in range(4) if j != i) for i in range(4)]
        if max(sc) > 0 and sc.count(max(sc)) == 1:
            famn += 1
            fam += sc.index(max(sc)) == q["a"]
    out["family_key"] = [famn, round(100 * fam / max(1, famn))]
    aoa = [q for q in Q if any(re.search(r"\ball (of )?(the )?(above|these)\b", x, re.I) for x in q["o"])]
    nota = [q for q in Q if any(re.search(r"\bnone of (the )?(above|these)\b", x, re.I) for x in q["o"])]
    out["aoa"] = [round(100 * len(aoa) / n, 1), round(100 * sum(bool(re.search(r"\ball (of )?(the )?(above|these)\b", q["o"][q["a"]], re.I)) for q in aoa) / max(1, len(aoa)))]
    out["nota"] = [round(100 * len(nota) / n, 1), round(100 * sum(bool(re.search(r"\bnone of (the )?(above|these)\b", q["o"][q["a"]], re.I)) for q in nota) / max(1, len(nota)))]
    out["stem_words"] = round(statistics.mean(len(q["s"].split()) for q in Q), 1)
    out["opt_words"] = round(statistics.mean(len(x.split()) for q in Q for x in q["o"]), 1)
    return out


def direct(Q, S):
    st = {x["n"] for x in S}
    out = []
    for q in Q:
        if q["n"] in st or q["nopt"] != 4 or q["match"]:
            continue
        s = q["s"]
        if re.search(r"assertion|\(A\).*\(R\)|chronolog|sequence|arrange|statement|list\s*-?\s*i\b", s, re.I):
            continue
        if sum(bool(re.search(r"[a-dA-D]\s*-\s*[IVX1-4]+", x)) for x in q["o"]) >= 3:
            continue
        if re.search(r"^\s*\(?[1-4ivx]+[.)]\s", s, re.M):
            continue
        out.append(q)
    return out


def main():
    import notes_pattern as NP
    import pyq_corpus as PC
    res = {}
    # APPSC's own papers 2017-25 (Group 1 / 2 Prelims and Mains)
    pq = []
    for f in T.PAPERS:
        p = json.load(open(f))
        ex, y = T.exam_of(f, p)
        if int(y) < 2017 or ex not in ("Group 1 Prelims", "Group 2 Prelims", "Group 2 Mains"):
            continue
        s, q = T.statements(f, p)
        pq += direct(q, s)
    res["APPSC papers 2017-25"] = profile(pq)
    # the whole PYQ bank (all exams)
    _, BQ, _ = PC.corpus()
    res["All PYQs in the app"] = profile(direct([q for q in BQ], []))
    # our direct notes MCQs, per subject
    qs = NP.notes_mcqs()
    S, Q = T.statements("n.json", {"questions": qs, "date": "2026"})
    by = {q["n"]: q for q in qs}
    dq = direct(Q, S)
    res["Notes MCQs (all)"] = profile(dq)
    for sj in AS.SUBJECTS:
        res[f"Notes · {sj}"] = profile([q for q in dq if by[q["n"]]["subj"] == sj])
    json.dump(res, open("data/tricks/direct-pattern.json", "w"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        if not v:
            continue
        print(f"\n== {k}: {v['n']} direct questions; stem {v['stem_words']} words, options {v['opt_words']} words")
        print("   asks:", v["ask"])
        print(f"   options all one kind {v['same_kind']}% {v['opt_kind']}; key position {v['pos']}; key length rank (short->long) {v['key_len_rank']}")
        print(f"   numbers: {v['numeric'][0]} q, key middle {v['numeric'][1]}%, decoys ~{v['numeric'][2]}% from key | 'family' option is key {v['family_key'][1]}% of {v['family_key'][0]}")
        print(f"   All of above {v['aoa']} | None of above {v['nota']}  (% of questions with it, % keyed)")


if __name__ == "__main__":
    main()
