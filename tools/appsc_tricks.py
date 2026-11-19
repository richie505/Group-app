"""APPSC elimination tricks, tested on APPSC's own papers (data/g2papers, data/appscpapers) and their keys.

Every statement whose truth the key fixes is pulled out:
  - "Consider the following statements: a./I./1. ..." + options like "a and b only" / "Both" / "Neither";
    the key's option says which statements are correct (or, for "... is/are incorrect?", which are wrong);
  - "Which of the following statements is (in)correct?" where each option is itself a statement.
Each trick ("a statement with an extreme word is usually wrong", ...) is then scored: how often a statement it fires on
was really wrong, per exam and year, against the base rate. Question-level patterns (answer positions, "All of the
above", "None of the above", 2-/3-/4-statement answers, Assertion-Reason, numeric options) are counted too.

    python3 tools/appsc_tricks.py          -> data/tricks/stats.json (+ a summary on stdout)
"""
import collections, glob, json, os, re

PAPERS = sorted(f for f in glob.glob("data/g2papers/*.json") + glob.glob("data/appscpapers/*.json") if "leaves" not in f)


def exam_of(f, p):
    n = os.path.basename(f)
    y = str(p.get("date", ""))[:4]
    if n.startswith("prelims-"):
        return "Group 2 Prelims", y
    if n.startswith("mains-"):
        return "Group 2 Mains", y
    if n.startswith("group2-"):
        return "Group 2 (old pattern)", y
    if n.startswith("group1-prelims"):
        return "Group 1 Prelims", y
    return "Other APPSC screening tests", y


LAB = r"(?:[a-h]|[A-H]|[ivx]{1,4}|[IVX]{1,4}|\d{1,2})"
STMT = re.compile(r"^\s*\(?(" + LAB + r")[.)]\s+(.+)$")
NEG = re.compile(r"\b(incorrect|incorrectly|not correct|not true|false|wrong|wrongly|NOT|odd)\b")


def norm_lab(x):
    x = x.strip("().")
    return x.upper() if re.fullmatch(r"[ivxIVX]+", x) else x.lower()


def picked(opt, labels):
    """The statement labels an option names (None when it names none it can be read as)."""
    t = opt.strip()
    lo = t.lower()
    if re.search(r"\bneither\b|\bnone\b", lo):
        return set()
    if re.search(r"\bboth\b", lo) and len(labels) == 2:
        return set(labels)
    if re.search(r"\ball\b", lo) and not re.search(r"\d|\b[ivx]+\b|\b[a-h]\b", lo.replace("all", "")):
        return set(labels)
    toks = set()
    for m in re.finditer(r"\b([IVX]{1,4}|[ivx]{1,4}|\d{1,2}|[a-hA-H])\b", t):
        x = norm_lab(m.group(1))
        if x in labels:
            toks.add(x)
    return toks or None


def statements(f, p):
    exam, year = exam_of(f, p)
    out, qlevel = [], []
    for q in p.get("questions", []):
        if "o" not in q or q.get("deleted") or q.get("a", -1) < 0 or q["a"] >= len(q["o"]):
            continue
        s, o, a = q["s"], q["o"], q["a"]
        lines = s.split("\n")
        st = [(norm_lab(m.group(1)), m.group(2).strip()) for m in (STMT.match(l) for l in lines) if m]
        tail = " ".join(l for l in lines if not STMT.match(l))
        is_match = bool(re.search(r"list\s*-?\s*(i|1)\b", s, re.I)) or sum(bool(re.search(r"[a-dA-D]\s*-\s*(I|1)\b", x)) for x in o) >= 2
        pairs = bool(re.search(r"\bpairs?\b.{0,60}\bmatched\b|\bmatched\b.{0,30}\bpairs?\b|\bpairs?\b.{0,40}\b(correct|incorrect)", s, re.I))
        base = {"exam": exam, "year": year, "paper": os.path.basename(f)[:-5], "n": q["n"], "subject": q.get("subject", "")}
        qlevel.append(dict(base, nopt=len(o), a=a, o=o, s=s, nst=len(st) if not is_match else 0, match=is_match))
        coded = len(st) >= 2 and sum(picked(x, [l for l, _ in st]) is not None for x in o) >= 3
        if len(st) >= 2 and not is_match and (re.search(r"statement", s, re.I) or pairs or coded):
            labels = [l for l, _ in st]
            if len(set(labels)) != len(labels):
                continue
            sel = picked(o[a], labels)
            if sel is None:
                continue
            neg = bool(NEG.search(tail.split("statement")[-1] if "statement" in tail else tail)) or \
                bool(re.search(r"\b(not|incorrectly|wrongly)\s+(correctly\s+)?(matched|paired)\b", tail, re.I))
            short = sum(len(t.split()) for _, t in st) / len(st) < 6
            for l, txt in st:
                true = (l in sel) != neg
                out.append(dict(base, text=txt, true=true, kind="item" if short and not pairs else ("pair" if pairs else "list"), nst=len(st)))
        elif not st and re.search(r"statement|pair", s, re.I) and (re.search(r"(which|identify|choose|select|find|pick).{0,50}(statement|following|pair).{0,50}(correct|true|incorrect|false|wrong|not|matched)", s, re.I)
                         or re.search(r"(identify|choose|select|find|pick|which).{0,20}(the\s+)?(in)?correct\s+(statement|pair|one)", s, re.I)) \
                and (sum(len(x) for x in o) / len(o) > 30 or re.search(r"pair", s, re.I)) and not re.search(r"\b(all|none|both) of (the )?(above|these|them)\b", " ".join(o), re.I):
            neg = bool(NEG.search(s)) or bool(re.search(r"\b(not|incorrectly|wrongly)\s+(correctly\s+)?(matched|paired)\b", s, re.I))
            for i, txt in enumerate(o):
                true = (i == a) != neg
                out.append(dict(base, text=txt, true=true, kind="option", nst=len(o)))
    return out, qlevel


# --- the tricks: each says "a statement like this is usually WRONG"
R = collections.OrderedDict([
    ("extreme", ("Extreme words", r"\b(always|never|all|none|no|only|solely|exclusively|entirely|completely|totally|every|any|must|mandatory|impossible|cannot|can not|not at all|whole|sole|invariably|without any)\b")),
    ("only", ("The word \"only\"", r"\bonly\b")),
    ("exactnum", ("Exact figures (not years)", r"(?<![\w.])(?!(1[0-9]{3}|20[0-9]{2})\b)\d[\d,.]*\s*(%|per ?cent|crore|lakh|million|billion|km|kg|mw|gw|hectare|sq|metres|meters|members|seats|times|years|days|states|districts)?")),
    ("year", ("A precise year or date", r"\b(1[0-9]{3}|20[0-9]{2})\b")),
    ("by_institution", ("\"launched / set up / implemented by\" a body", r"\b(launched|introduced|implemented|initiated|administered|set up|established|founded|formed|constituted|created|started|regulated|organi[sz]ed|released|published|conducted|funded)\s+(by|under)\b")),
    ("intl_org", ("A named international organisation", r"\b(UN|UNO|UNESCO|UNICEF|UNDP|UNEP|WHO|WTO|IMF|World Bank|ADB|AIIB|NDB|FAO|ILO|IUCN|WEF|OECD|ASEAN|SAARC|BRICS|G20|G7|IAEA|UNFCCC|ITU|WIPO|Interpol)\b")),
    ("constitution", ("\"The Constitution defines / provides / mentions ...\"", r"constitution\b.{0,40}\b(defines|define|provides|provide|prescribes|mentions|classifies|explicitly|lays down|exempts|specifies|guarantees)|according to the constitution|under article|article\s+\d+")),
    ("but_not", ("\"... but ... not ...\"", r"\bbut\b.*\bnot\b|\bnot\b.*\bbut\b")),
    ("because", ("A reason given (because / due to / hence / so)", r"\b(because|due to|owing to|as a result|therefore|hence|since|so that|thus|on account of|in order to)\b")),
    ("compare", ("A comparison (whereas / while / unlike / more than / higher than)", r"\b(whereas|while|unlike|higher than|lower than|more than|less than|larger than|smaller than|greater than|in contrast|compared|than)\b")),
    ("trend", ("A steady / continuous trend", r"\b(steadily|continuously|consistently|constantly|every year|throughout|ever since|uninterrupted)\b")),
    ("contemporary", ("\"X and Y were contemporaries\"", r"contemporar")),
    ("native", ("\"native / endemic / indigenous to\"", r"\b(native|endemic|indigenous)\b")),
    ("main", ("\"main / primary / chief aim\"", r"\b(main|mainly|primary|primarily|chief|chiefly|principal|largely|mostly|major) (objective|aim|purpose|goal|focus|function|reason|cause|role)?")),
    ("authority", ("A named office (President, Governor, Speaker, CM ...)", r"\b(president|governor|speaker|prime minister|chief minister|chairman|vice[- ]president|chief justice|attorney general|comptroller|election commission|finance commission|parliament|legislature|lok sabha|rajya sabha)\b")),
    ("binding", ("\"legally binding / mandatory / enforceable\"", r"\b(legally binding|binding|mandatory|compulsory|enforceable|obligatory)\b")),
    ("tax", ("\"tax-free / exempt\"", r"\b(tax[- ]free|exempt|exemption|no tax)\b")),
    ("hq", ("A headquarters city", r"head ?quarter|\bhq\b|headquartered")),
    ("first", ("\"first / largest / highest / oldest\" claims", r"\b(first|largest|highest|oldest|biggest|longest|smallest|lowest|earliest|last)\b")),
    ("multi", ("Two or more facts joined in one statement", r";|,\s*and\b|\band\b.*\band\b|\bas well as\b|\balso\b")),
    ("negated", ("A statement that itself says \"not / no\"", r"\b(not|no|never|neither|nor|did not|does not|was not|is not|cannot)\b")),
    ("ap", ("Andhra Pradesh-specific claims", r"\b(andhra|amaravati|visakhapatnam|vizag|tirupati|godavari|krishna|nellore|kurnool|kadapa|guntur|vijayawada|polavaram|srisailam|amaravathi|telugu|satavahana|ikshvaku|kakatiya|vijayanagara|eastern chalukya|reddy kingdom|AP\b)\b")),
])
COMP = {k: re.compile(v[1], re.I) for k, v in R.items()}


def main():
    S, Q = [], []
    for f in PAPERS:
        p = json.load(open(f))
        s, q = statements(f, p)
        S += s
        Q += q
    os.makedirs("data/tricks", exist_ok=True)
    groups = ["Group 2 Prelims", "Group 2 Mains", "Group 1 Prelims", "Group 2 (old pattern)", "Other APPSC screening tests"]
    T_ = [x for x in S if x["kind"] != "item"]
    out = {"statements": len(T_), "items": len(S) - len(T_), "false_share": sum(not x["true"] for x in T_) / len(T_), "rules": {}, "byexam": {}}
    for g in groups:
        sg = [x for x in S if x["exam"] == g and x["kind"] != "item"]
        out["byexam"][g] = {"statements": len(sg), "false": sum(not x["true"] for x in sg),
                            "questions": len([q for q in Q if q["exam"] == g])}
    for k, (title, _) in R.items():
        hits = [x for x in S if x["kind"] != "item" and COMP[k].search(x["text"])]
        rows = []
        for g in groups:
            for y in sorted({x["year"] for x in hits if x["exam"] == g}, reverse=True):
                h = [x for x in hits if x["exam"] == g and x["year"] == y]
                if not h:
                    continue
                wrong = [x for x in h if not x["true"]]
                rows.append({"exam": g, "year": y, "right": len(wrong), "failed": len(h) - len(wrong), "total": len(h),
                             "pct": round(100 * len(wrong) / len(h), 1),
                             "refs": sorted({x["n"] for x in wrong})[:6]})
        base_exam = {g: sum(not x["true"] for x in S if x["exam"] == g and x["kind"] != "item") / max(1, len([x for x in S if x["exam"] == g and x["kind"] != "item"])) for g in groups}
        allw = [x for x in hits if not x["true"]]
        ex_right = [x for x in hits if not x["true"]][:3]
        ex_fail = [x for x in hits if x["true"]][:3]
        out["rules"][k] = {"title": title, "total": len(hits), "right": len(allw),
                           "pct": round(100 * len(allw) / max(1, len(hits)), 1), "rows": rows, "base": base_exam,
                           "ex_right": [{k2: x[k2] for k2 in ("exam", "year", "paper", "n", "text")} for x in ex_right],
                           "ex_fail": [{k2: x[k2] for k2 in ("exam", "year", "paper", "n", "text")} for x in ex_fail]}
    # --- question level
    ql = {}
    for g in groups:
        qs = [q for q in Q if q["exam"] == g]
        pos = collections.Counter(q["a"] for q in qs if q["nopt"] == 4)
        allabove = [q for q in qs if any(re.search(r"\ball (of )?(the )?(above|these|them)\b|^all\b", x, re.I) for x in q["o"])]
        allabove_right = [q for q in allabove if re.search(r"\ball (of )?(the )?(above|these|them)\b|^all\b", q["o"][q["a"]], re.I)]
        nota = [q for q in qs if any(re.search(r"\bnone of (the )?(above|these|them)\b|^none\b|\bneither\b", x, re.I) for x in q["o"])]
        nota_right = [q for q in nota if re.search(r"\bnone of (the )?(above|these|them)\b|^none\b|\bneither\b", q["o"][q["a"]], re.I)]
        ar = [q for q in qs if re.search(r"assertion|\(A\).*\(R\)|reason \(R\)", q["s"], re.I)]
        arc = collections.Counter()
        for q in ar:
            t = q["o"][q["a"]].lower()
            if "both" in t and ("correct explanation" in t or "explains" in t) and "not" not in t:
                arc["Both true, R explains A"] += 1
            elif "both" in t and "not" in t:
                arc["Both true, R does not explain A"] += 1
            elif re.search(r"\(a\) is (true|correct).*\(r\) is (false|not correct|incorrect)|a is true.*r is false", t):
                arc["A true, R false"] += 1
            elif re.search(r"\(a\) is (false|not correct|incorrect).*\(r\) is (true|correct)|a is false.*r is true", t):
                arc["A false, R true"] += 1
            else:
                arc["other"] += 1
        # statement-count questions: how many statements were correct
        st_by_q = collections.defaultdict(list)
        for x in S:
            if x["exam"] == g and x["kind"] == "list":
                st_by_q[(x["paper"], x["n"])].append(x["true"])
        dist = {}
        for n in (2, 3, 4):
            c = collections.Counter(sum(v) for v in st_by_q.values() if len(v) == n)
            dist[n] = {str(k): c[k] for k in range(n + 1)}
        # numeric options: is the key the middle value?
        mid = tot = 0
        for q in qs:
            nums = []
            for x in q["o"]:
                m = re.fullmatch(r"\s*[₹$]?\s*([\d,]+(?:\.\d+)?)\s*(%|per ?cent|crore|lakh|km|million|billion)?\.?\s*", x)
                nums.append(float(m.group(1).replace(",", "")) if m else None)
            if all(v is not None for v in nums) and len(set(nums)) == len(nums) == 4:
                order = sorted(range(4), key=lambda i: nums[i])
                tot += 1
                mid += order.index(q["a"]) in (1, 2)
        # longest option
        lr = lt = 0
        for q in qs:
            L = [len(x) for x in q["o"]]
            if len(L) == 4 and min(L) > 20 and L.count(max(L)) == 1:
                lt += 1
                lr += L.index(max(L)) == q["a"]
        ql[g] = {"questions": len(qs), "pos": {k: pos[k] for k in range(4)},
                 "allabove": [len(allabove), len(allabove_right)], "nota": [len(nota), len(nota_right)],
                 "ar": dict(arc), "ar_n": len(ar), "stdist": dist, "numeric": [tot, mid], "longest": [lt, lr],
                 "statement_qs": len(st_by_q)}
        mq = [q for q in qs if sum(bool(re.search(r"[a-dA-D]\s*-\s*[IVX1-4]+", x)) for x in q["o"]) >= 3]
        IDN = r"\s*[aA]\s*-\s*(I|1)\s*,\s*[bB]\s*-\s*(II|2)\s*,\s*[cC]\s*-\s*(III|3)\s*,\s*[dD]\s*-\s*(IV|4)\s*"
        ident = [q for q in mq if any(re.fullmatch(IDN, x) for x in q["o"])]
        ql[g]["matching"] = [len(mq), len(ident), len([q for q in ident if re.fullmatch(IDN, q["o"][q["a"]])])]
        ql[g]["chronology"] = len([q for q in qs if re.search(r"chronolog|sequence|arrange", q["s"], re.I)])
    out["questions"] = ql
    # --- weightage by subject, per paper
    w = collections.defaultdict(collections.Counter)
    for q in Q:
        w[f"{q['exam']} {q['year']}"][q["subject"] or "?"] += 1
    out["weightage"] = {k: dict(v) for k, v in w.items()}
    json.dump(out, open("data/tricks/stats.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(S)} statements with a known truth ({100 * out['false_share']:.0f}% false) from {len(Q)} questions")
    for g, v in out["byexam"].items():
        print(f"  {g}: {v['statements']} statements ({100 * v['false'] / max(1, v['statements']):.0f}% false), {v['questions']} questions")
    for k, r in out["rules"].items():
        print(f"{r['title'][:58]:58} fires {r['total']:4}  wrong {r['pct']:5}%")
    for g, v in ql.items():
        print(g, "pos", v["pos"], "all-above", v["allabove"], "nota", v["nota"], "AR", v["ar_n"], v["ar"], "num", v["numeric"], "long", v["longest"], "dist", v["stdist"])


if __name__ == "__main__":
    main()
