"""Measured answer patterns of the keyed APPSC previous-year questions: what the key says, by question shape,
keyword, option feature, subject and topic. Every number is a count from the papers, with its sample size.

    python3 tools/pyq_secrets.py      -> data/pyq/secrets.json
"""
import hashlib, json, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, "tools")
from pyq_place import bank, cleaned, usable  # noqa: E402
from pyq_apply import broken, keep, rank  # noqa: E402

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "a": 1, "b": 2, "c": 3, "d": 4, "e": 5}


def yid(q):
    return "y" + hashlib.sha1(q["id"].encode()).hexdigest()[:11]


def load(ranks=(0,)):
    bad = json.load(open("data/pyq/bad.json"))
    place = json.load(open("data/pyq/place-complete.json"))["place"]
    out = []
    for q in map(cleaned, bank()):
        if rank(q) not in ranks or q["a"] < 0 or not usable(q) or broken(q) or yid(q) in bad:
            continue
        p = place.get(q["id"])
        q["book"], q["row"] = (p[0], p[1]) if p and keep(q, p[3]) else (0, -1)
        out.append(q)
    return out


CODE_OPT = re.compile(r"^\s*(?:only\s+)?(?:\(?(?:[1-6]|i{1,3}|iv|v|vi|[a-f])\)?(?:\s*(?:,|and|&)\s*\(?(?:[1-6]|i{1,3}|iv|v|vi|[a-f])\)?)*)(?:\s+only)?\s*$|"
                      r"^\s*(?:both|neither|none|all)\b|^\s*only (?:one|two|three)\b|statement", re.I)


def kind(q):
    s = q["s"].lower()
    o = [x.lower() for x in q["o"]]
    if re.search(r"assertion|\(a\).{0,300}\(r\)|reason\s*\(r\)", s):
        return "assertion"
    if sum(bool(re.search(r"\b[a-d]\s*[-–.:]\s*(?:[1-5]|i{1,3}|iv)\b", x)) for x in o) >= 3:
        return "match"
    if re.search(r"chronolog|correct (?:order|sequence)|arrange|ascending|descending", s):
        return "sequence"
    if re.search(r"\bhow many\b", s):
        return "how many"
    if sum(bool(CODE_OPT.search(x)) and len(x) < 45 for x in o) >= 3:
        return "statements"
    if re.search(r"\bpairs?\b|match(?:ed|ing)?\b", s) and sum(bool(re.search(r"\s[–:-]\s|\s-\s|:", x)) for x in o) >= 3:
        return "pairs"
    if re.search(r"statements?|true|false|correct|incorrect|best describes", s) and sum(len(x) > 35 for x in o) >= 3:
        return "statement options"
    return "one-liner"


def neg(q):
    return bool(re.search(r"\b(?:not|incorrect|false|wrong(?:ly)?|except|untrue)\b", q["s"], re.I))


# ---------- match the following: does the key follow the "consensus" of the codes? ----------
def codes(o):
    pairs = re.findall(r"\b([A-Da-d])\s*[-–:)]?\s*\(?((?:[1-5])|(?:i{1,3}|iv|v))\)?", o)
    m = {}
    for k, v in pairs:
        m[k.upper()] = ROMAN.get(v.lower(), int(v) if v.isdigit() else 0)
    return m if len(m) >= 3 else None


def match_stats(qs):
    st = Counter()
    for q in qs:
        cs = [codes(o) for o in q["o"]]
        if any(c is None for c in cs):
            continue
        st["parsed"] += 1
        # consensus: each letter's most common number across the four codes; score each code by agreement
        letters = sorted(set().union(*cs))
        common = {L: Counter(c.get(L) for c in cs).most_common(1)[0][0] for L in letters}
        score = [sum(c.get(L) == common[L] for L in letters) for c in cs]
        best = max(score)
        if score.count(best) == 1:
            st["consensus unique"] += 1
            st["consensus right"] += score.index(best) == q["a"]
        # how many letters pin the answer: a pair that appears in only one code
        uniq = [sum(1 for L in letters if sum(c2.get(L) == c.get(L) for c2 in cs) == 1) for c in cs]
        st["answer has a unique pair"] += uniq[q["a"]] > 0
        # identity code (A-1 B-2 C-3 D-4) and reverse
        ident = [all(c.get(L) == i + 1 for i, L in enumerate(letters)) for c in cs]
        if any(ident):
            st["identity offered"] += 1
            st["identity right"] += ident[q["a"]]
        st[f"pos{q['a'] + 1}"] += 1
    return st


# ---------- statement sets: which statements the key calls true ----------
def stmt_split(s):
    marks = list(re.finditer(r"(?:^|\n|\s)\(?((?:[1-6])|(?:I{1,3}|IV|V|VI)|(?:[A-F])|(?:i{1,3}|iv|v|vi)|(?:[a-f]))[.)]\s+", s))
    if len(marks) < 2:
        st = re.split(r"statement\s*\(?([A-D1-4]|I{1,3})\)?\s*:", s, flags=re.I)
        return [x.strip() for x in st[2::2]] if len(st) >= 5 else []
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(s)
        out.append(s[m.end():end].strip())
    # cut the closing question ("Which of the above ...") off the last statement
    if out:
        out[-1] = re.split(r"\s(?:which|select|choose|how many|of the above|codes?\s*:)", out[-1], flags=re.I)[0]
    return [x for x in out if len(x) > 8]


def nums_in(opt, n):
    o = opt.lower().strip()
    if re.search(r"\bnone\b|neither|both .* (?:wrong|false|incorrect)", o):
        return set()
    if re.search(r"\ball\b|\bboth\b(?!.*(?:wrong|false|incorrect))", o):
        return set(range(1, n + 1))
    m = re.search(r"statement\s*\(?([a-d1-4])\)?\s*is (?:right|true|correct)", o)
    if m:
        return {ROMAN.get(m.group(1), int(m.group(1)) if m.group(1).isdigit() else 0)}
    m = re.search(r"only (one|two|three)", o)
    if m:
        return None
    found = re.findall(r"\b(iv|vi|v|i{1,3}|[1-6]|[a-f])\b", o)
    vals = {ROMAN.get(x, int(x) if x.isdigit() else 0) for x in found}
    return vals or None


def statement_stats(qs):
    st = Counter()
    kw_true = defaultdict(lambda: [0, 0])  # keyword -> [true, total]
    shapes = defaultdict(Counter)
    KW = {"only": r"\bonly\b", "all": r"\ball\b", "always": r"\balways\b", "never": r"\bnever\b", "must": r"\bmust\b",
          "every": r"\bevery\b", "any": r"\bany\b", "cannot / can not": r"\bcan ?not\b", "not": r"\bnot\b",
          "may / can": r"\b(?:may|can)\b(?! ?not)", "first": r"\bfirst\b", "largest / highest / most": r"\b(?:largest|highest|most|biggest)\b",
          "exclusively / solely / entirely": r"\b(?:exclusively|solely|entirely|completely|wholly)\b",
          "a number (figure, year, %)": r"\b\d[\d,.]*\b", "Article / Section": r"\b(?:article|section|schedule)\b",
          "recently / launched": r"\b(?:recently|launched|introduced)\b", "Andhra / AP": r"\bandhra|\bA\.P\.?\b"}
    for q in qs:
        S = stmt_split(q["s"])
        n = len(S)
        if not 2 <= n <= 6:
            continue
        ans = nums_in(q["o"][q["a"]], n)
        if ans is None:
            continue
        true = ans
        if any(t > n for t in true):
            continue
        negq = neg(q) and not re.search(r"\bnot correct\b.*\bcorrect\b", q["s"], re.I)
        if negq:  # "which is/are NOT correct": the code names the false ones
            true = set(range(1, n + 1)) - true
        st[f"{n} statements"] += 1
        shapes[n][f"{len(true)} of {n} true"] += 1
        for i, txt in enumerate(S, 1):
            for k, rx in KW.items():
                if re.search(rx, txt, re.I):
                    kw_true[k][0] += i in true
                    kw_true[k][1] += 1
            st["statements"] += 1
            st["true"] += i in true
    return st, {k: dict(v) for k, v in shapes.items()}, kw_true, KW


def option_truth(qs, kw_true, KW):
    """'Which statement is correct / NOT correct' and 'which pair is (in)correct': each option is a statement whose truth
    the key settles (the keyed one is the true one, or in a NOT question the false one)."""
    for q in qs:
        negq = neg(q)
        for i, x in enumerate(q["o"]):
            true = (i == q["a"]) != negq
            for k, rx in KW.items():
                if re.search(rx, x, re.I):
                    kw_true[k][0] += true
                    kw_true[k][1] += 1
            kw_true["(any statement)"][0] += true
            kw_true["(any statement)"][1] += 1


# ---------- options: features of the keyed option ----------
def words(t):
    return set(re.findall(r"[a-z]{4,}", t.lower()))


def option_stats(qs):
    st = Counter()
    for q in qs:
        o, a = q["o"], q["a"]
        L = [len(x) for x in o]
        if L.count(max(L)) == 1:
            st["longest n"] += 1; st["longest right"] += L.index(max(L)) == a
        if L.count(min(L)) == 1:
            st["shortest n"] += 1; st["shortest right"] += L.index(min(L)) == a
        # the option that shares most words with the other options (the "centre" of the four)
        W = [words(x) for x in o]
        sim = [sum(len(W[i] & W[j]) for j in range(4) if j != i) for i in range(4)]
        if max(sim) > 0 and sim.count(max(sim)) == 1:
            st["centre n"] += 1; st["centre right"] += sim.index(max(sim)) == a
        # the option that shares most words with the stem
        sw = words(q["s"])
        ov = [len(W[i] & sw) for i in range(4)]
        if max(ov) > 0 and ov.count(max(ov)) == 1:
            st["echo n"] += 1; st["echo right"] += ov.index(max(ov)) == a
        # numbers: rank of the keyed value
        try:
            v = [float(re.sub(r"[^\d.]", "", x)) for x in o]
            if len(set(v)) == 4 and all(re.fullmatch(r"[\d.,%\s₹a-zA-Z/()-]*", x) for x in o):
                r = sorted(v).index(v[a])
                yrs = all(1000 <= x <= 2100 for x in v)
                st[("year" if yrs else "number") + f" rank{r + 1}"] += 1
                st[("year" if yrs else "number") + " n"] += 1
                # "two close values": the keyed one is one of the two nearest each other
                s = sorted(v); gaps = [s[i + 1] - s[i] for i in range(3)]; k = gaps.index(min(gaps))
                st[("year" if yrs else "number") + " closepair"] += v[a] in (s[k], s[k + 1])
        except ValueError:
            pass
        # "All of the above" / "None" / "Both" shapes
        for name, rx in [("all of the above", r"all of the above|all the above"), ("none of the above", r"none of the above|none of these"),
                         ("both", r"^both\b"), ("neither", r"^neither\b")]:
            hit = [i for i, x in enumerate(o) if re.search(rx, x.strip().lower())]
            if hit:
                st[name + " n"] += 1; st[name + " right"] += a in hit
                if name == "all of the above" and hit[0] == 3:
                    st["all-last n"] += 1; st["all-last right"] += a == 3
    return st


def main(ranks=(0,), out_file="data/pyq/secrets.json"):
    qs = load(ranks)
    for q in qs:
        q["kind"], q["neg"] = kind(q), neg(q)
    out = {"n": len(qs), "kinds": Counter(q["kind"] for q in qs), "position": Counter(q["a"] + 1 for q in qs)}
    out["position_by_kind"] = {k: Counter(q["a"] + 1 for q in qs if q["kind"] == k) for k in out["kinds"]}
    out["neg"] = {"n": sum(q["neg"] for q in qs), "position": Counter(q["a"] + 1 for q in qs if q["neg"])}
    out["match"] = match_stats([q for q in qs if q["kind"] == "match"])
    out["statements"], out["statement_shapes"], kw, KW = statement_stats([q for q in qs if q["kind"] == "statements"])
    out["keyword_truth_sets"] = {k: list(v) for k, v in kw.items()}
    option_truth([q for q in qs if q["kind"] in ("statement options", "pairs")], kw, KW)
    out["keyword_truth"] = {k: list(v) for k, v in kw.items()}
    hm = Counter()
    for q in qs:
        if q["kind"] == "how many":
            hm[re.sub(r"[^a-z ]", "", q["o"][q["a"]].lower()).strip()[:20]] += 1
    out["how_many"] = hm
    out["neg_by_kind"] = {k: sum(1 for q in qs if q["kind"] == k and q["neg"]) for k in out["kinds"]}
    ar = Counter()
    for q in qs:
        if q["kind"] != "assertion":
            continue
        o = q["o"][q["a"]].lower()
        if re.search(r"both.*true", o) and re.search(r"not (?:the )?correct|not (?:a|the) (?:correct|right)", o): ar["both true, R not the explanation"] += 1
        elif re.search(r"both.*true", o): ar["both true, R explains A"] += 1
        elif re.search(r"\(?a\)? is true.*\(?r\)? is false|a is true and r is false|a is correct.*r is (?:false|wrong|incorrect)", o): ar["A true, R false"] += 1
        elif re.search(r"\(?a\)? is false.*\(?r\)? is true|a is false and r is true|a is (?:false|wrong|incorrect).*r is (?:true|correct)", o): ar["A false, R true"] += 1
        elif re.search(r"both.*false", o): ar["both false"] += 1
    out["assertion"] = ar
    out["options"] = option_stats(qs)
    out["options_oneliner"] = option_stats([q for q in qs if q["kind"] == "one-liner"])
    # subject-wise and topic-wise
    titles = {}
    for b in range(1, 7):
        ri = 0
        for u in json.load(open(f"app/src/complete/assets/book{b}.json"))["units"]:
            for r in u["rows"]:
                titles[(b, ri)] = (u.get("title", ""), r["title"]); ri += 1
    subj = {}
    for b in range(1, 7):
        Q = [q for q in qs if q["book"] == b]
        subj[b] = {"n": len(Q), "kinds": Counter(q["kind"] for q in Q), "position": Counter(q["a"] + 1 for q in Q),
                   "neg": sum(q["neg"] for q in Q), "options": option_stats(Q),
                   "units": Counter(titles[(q["book"], q["row"])][0] for q in Q).most_common(12),
                   "topics": Counter(titles[(q["book"], q["row"])][1] for q in Q).most_common(15)}
    out["subjects"] = subj
    json.dump(out, open(out_file, "w"), ensure_ascii=False, indent=1, default=dict)
    print(json.dumps({k: out[k] for k in ("n", "kinds", "position", "neg", "match", "statements", "statement_shapes", "assertion")}, default=dict))
    print("KW", json.dumps(out["keyword_truth"]))
    print("OPT", json.dumps(out["options"]))
    print("OPT1", json.dumps(out["options_oneliner"]))


if __name__ == "__main__":
    main()
    main((1, 2), "data/pyq/secrets-others.json")  # UPSC and the other state PSCs: to compare and to back small samples
