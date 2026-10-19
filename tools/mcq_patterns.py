"""Answer-key patterns across all the app's MCQs: what the keyed option tends to look like.

    python3 tools/mcq_patterns.py [assets dir | past-paper dir with pyq1..6.json] [--appsc] > patterns.json
For every rule: how many MCQs it applies to and how often it picks the keyed answer (vs. the 25% of a blind guess).
A past-paper dir (pyq<n>.json lists) checks the same rules on real exam keys; --appsc keeps APPSC papers only.
"""
import json, re, sys
from collections import Counter, defaultdict

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/main/assets"
BOOKS = {1: "History", 2: "Polity", 3: "Economy", 4: "Geography", 5: "Science", 6: "Current Affairs"}

import os
qs = []
for b in BOOKS:
    f = f"{A}/mcq{b}.json" if os.path.exists(f"{A}/mcq{b}.json") else f"{A}/pyq{b}.json"
    m = json.load(open(f))
    seen = set()
    items = [q for v in list(m["rows"].values()) + list(m.get("units", {}).values()) for q in v
             if q["id"] not in seen and not seen.add(q["id"])]
    if "--appsc" in sys.argv:
        items = [q for q in items if q.get("ap")]
    for q in items:
        if len(q.get("o", [])) == 4 and 0 <= q.get("a", -1) < 4:
            qs.append((b, q))

R = {}


def rule(name, pick):
    """pick(q) -> option index the rule chooses, or None when it does not apply."""
    n = hit = 0
    by = Counter()
    for b, q in qs:
        p = pick(q)
        if p is None:
            continue
        n += 1
        if p == q["a"]:
            hit += 1
            by[b] += 1
    R[name] = {"applies": n, "hits": hit, "rate": round(100 * hit / n, 1) if n else 0}


def kind(q):
    s = q["s"].lower()
    o = " ".join(q["o"]).lower()
    if "assertion" in s and "reason" in s:
        return "assertion-reason"
    if re.search(r"\bmatch\b|list[- ]?i\b|correctly matched|correctly paired|pairs? given", s):
        return "match"
    if re.search(r"chronolog|correct order|sequence|arrange", s):
        return "order"
    if re.search(r"statements?", s) and re.search(r"\b(1|i)\b.*\b(2|ii)\b", s + o):
        return "statements"
    if re.search(r"\bnot\b|incorrect|false|wrong|except", s):
        return "negative"
    return "direct"


kinds = Counter(kind(q) for _, q in qs)
pos = Counter(q["a"] for _, q in qs)
pos_kind = defaultdict(Counter)
pos_book = defaultdict(Counter)
for b, q in qs:
    pos_kind[kind(q)][q["a"]] += 1
    pos_book[BOOKS[b]][q["a"]] += 1

# --- statement-code questions: which code is keyed
code_key = Counter()
code_seen = Counter()
nst = Counter()
for _, q in qs:
    if kind(q) != "statements":
        continue
    for i, o in enumerate(q["o"]):
        c = re.sub(r"\s+", " ", o.strip().lower())
        code_seen[c] += 1
        if i == q["a"]:
            code_key[c] += 1
codes = {c: {"offered": code_seen[c], "keyed": code_key[c], "rate": round(100 * code_key[c] / code_seen[c], 1)}
         for c in code_seen if code_seen[c] >= 150}


def stmt_numbers(o):
    o = o.lower()
    if re.search(r"\b(all|none|neither)\b", o):
        return None
    return set(re.findall(r"\b([1-6])\b", o))


def most_common_statements(q):
    """The option made of the statements that appear in most options (the 'frequency' trick)."""
    if kind(q) != "statements":
        return None
    sets = [stmt_numbers(o) for o in q["o"]]
    if any(s is None or not s for s in sets):
        return None
    freq = Counter(x for s in sets for x in s)
    score = [sum(freq[x] for x in s) / len(s) for s in sets]
    best = max(score)
    if score.count(best) > 1:
        return None
    return score.index(best)


rule("Statements: pick the option whose statements appear most often across the 4 options", most_common_statements)


def all_option(q):
    for i, o in enumerate(q["o"]):
        if re.fullmatch(r"\s*(all of the above|all the above|all of these|1, 2,? (and|&) 3|1, 2, 3 and 4|all (four|three|the four|the three)( statements)?|both 1 and 2|both i and ii)\.?\s*", o.lower()):
            return i
    return None


def none_option(q):
    for i, o in enumerate(q["o"]):
        if re.fullmatch(r"\s*(none of the above|none of these|neither 1 nor 2|neither i nor ii|none)\.?\s*", o.lower()):
            return i
    return None


rule("'All of them' / 'Both' option, when offered, is the key", all_option)
rule("'None' / 'Neither' option, when offered, is the key", none_option)


def longest(q):
    if kind(q) in ("statements", "match", "order", "assertion-reason"):
        return None
    L = [len(o) for o in q["o"]]
    m = max(L)
    if L.count(m) > 1 or m < 12 or m < 1.25 * sorted(L)[-2]:
        return None
    return L.index(m)


def shortest(q):
    if kind(q) in ("statements", "match", "order", "assertion-reason"):
        return None
    L = [len(o) for o in q["o"]]
    m = min(L)
    if L.count(m) > 1 or m * 1.25 > sorted(L)[1]:
        return None
    return L.index(m)


rule("Clearly longest option (25%+ longer than the rest) is the key", longest)
rule("Clearly shortest option is the key", shortest)

ABS = re.compile(r"\b(only|always|never|all|none|every|entirely|exclusively|solely|completely|must|cannot|no one|any)\b", re.I)
HEDGE = re.compile(r"\b(may|can|generally|usually|mainly|mostly|largely|some|often|primarily|partly)\b", re.I)


def absolute_count(q):
    return [len(ABS.findall(o)) for o in q["o"]]


def avoid_absolute(q):
    """Absolute words ('only', 'always', 'never') sit mostly in wrong options: when exactly one option has none, pick it."""
    if kind(q) not in ("direct",):
        return None
    c = absolute_count(q)
    zero = [i for i, x in enumerate(c) if x == 0]
    return zero[0] if len(zero) == 1 else None


def hedge(q):
    if kind(q) not in ("direct",):
        return None
    h = [i for i, o in enumerate(q["o"]) if HEDGE.search(o)]
    return h[0] if len(h) == 1 else None


rule("Direct Qs: the only option WITHOUT an absolute word (only/always/never/all) is the key", avoid_absolute)
rule("Direct Qs: the only option with a hedge word (may/generally/mainly) is the key", hedge)

# absolute words: share of options carrying them that are keyed
abs_opt = [0, 0]
for _, q in qs:
    if kind(q) == "direct":
        for i, o in enumerate(q["o"]):
            if ABS.search(o):
                abs_opt[0] += 1
                abs_opt[1] += i == q["a"]


def nums(o):
    v = re.findall(r"-?\d+(?:\.\d+)?", o.replace(",", ""))
    return float(v[0]) if len(v) == 1 else None


def middle_number(q):
    """Numeric options: the key is rarely the smallest or the largest - pick a middle value."""
    v = [nums(o) for o in q["o"]]
    if any(x is None for x in v) or len(set(v)) < 4:
        return None
    order = sorted(range(4), key=lambda i: v[i])
    return order[1]  # second smallest; the stats below give both middles


rule("Number options: the 2nd-smallest value is the key", middle_number)
rule("Number options: the 3rd-smallest value is the key",
     lambda q: (lambda v: None if any(x is None for x in v) or len(set(v)) < 4 else sorted(range(4), key=lambda i: v[i])[2])(
         [nums(o) for o in q["o"]]))
num_rank = Counter()
for _, q in qs:
    v = [nums(o) for o in q["o"]]
    if any(x is None for x in v) or len(set(v)) < 4:
        continue
    order = sorted(range(4), key=lambda i: v[i])
    num_rank[order.index(q["a"])] += 1


def words(t):
    return {w for w in re.findall(r"[a-z]{4,}", t.lower())}


def look_alike(q):
    """Distractors are built from the key: the option sharing most words with the other three."""
    if kind(q) in ("statements", "match", "order", "assertion-reason"):
        return None
    W = [words(o) for o in q["o"]]
    if any(not w for w in W):
        return None
    sc = [sum(len(W[i] & W[j]) / max(1, len(W[i] | W[j])) for j in range(4) if j != i) for i in range(4)]
    best = max(sc)
    return sc.index(best) if sc.count(best) == 1 and best > 0 else None


def stem_echo(q):
    """The option repeating a word of the question (that no other option has)."""
    if kind(q) in ("statements", "match", "order", "assertion-reason"):
        return None
    st = words(q["s"])
    hits = [i for i, o in enumerate(q["o"]) if words(o) & st]
    return hits[0] if len(hits) == 1 else None


rule("The option most like the other three (distractors are variations of the key)", look_alike)
rule("The only option that echoes a word of the question", stem_echo)


def ar_a(q):
    return 0 if kind(q) == "assertion-reason" else None


ar_text = Counter()
for _, q in qs:
    if kind(q) == "assertion-reason":
        k = q["o"][q["a"]].lower()
        if "both" in k and "not" in k:
            ar_text["Both true, R NOT the correct explanation"] += 1
        elif "both" in k:
            ar_text["Both true, R IS the correct explanation"] += 1
        elif re.search(r"a is true.*r is false|a is correct.*r is (in)?correct but|a is true but r", k):
            ar_text["A true, R false"] += 1
        elif re.search(r"a is false|a is incorrect", k):
            ar_text["A false, R true"] += 1
        else:
            ar_text["other"] += 1


def neg_pick(q):
    """NOT/incorrect questions: the option with an absolute word is the false one."""
    if kind(q) != "negative":
        return None
    c = absolute_count(q)
    have = [i for i, x in enumerate(c) if x]
    return have[0] if len(have) == 1 else None


rule("NOT/incorrect Qs: the only option with an absolute word is the key", neg_pick)

out = {
    "total": len(qs),
    "kinds": dict(kinds),
    "position": {f"({i + 1})": pos[i] for i in range(4)},
    "position_by_kind": {k: {f"({i + 1})": v[i] for i in range(4)} for k, v in pos_kind.items()},
    "position_by_book": {k: {f"({i + 1})": v[i] for i in range(4)} for k, v in pos_book.items()},
    "statement_codes": dict(sorted(codes.items(), key=lambda x: -x[1]["offered"])),
    "absolute_word_options_keyed_pct": round(100 * abs_opt[1] / abs_opt[0], 1),
    "number_rank_of_key": {["smallest", "2nd", "3rd", "largest"][k]: v for k, v in sorted(num_rank.items())},
    "assertion_reason_keys": dict(ar_text),
    "rules": R,
}


# --- whole strategies: a fixed procedure per question type, scored on this set -----------------------------
def by_code(q, prefs):
    low = [re.sub(r"\s+", " ", o.strip().lower().rstrip(".")) for o in q["o"]]
    for c in prefs:
        if c in low:
            return low.index(c)
    return None


def ar_explains(q):
    for i, o in enumerate(q["o"]):
        x = o.lower()
        if "both" in x and "not" not in x and ("explan" in x or "explain" in x):
            return i
    return None


def numeric_rank(q, k):
    v = [nums(o) for o in q["o"]]
    if any(x is None for x in v) or len(set(v)) < 4:
        return None
    return sorted(range(4), key=lambda i: v[i])[k]


APP_CODES = ["1, 2 and 4 only", "1, 2, 3 and 4", "1 and 2 only", "1, 2 and 3 only", "1, 2 and 3", "1 and 3 only", "1 only"]
REAL_CODES = ["1 and 3 only", "both 1 and 2", "2 only", "2 and 3 only", "only 1"]


def first(*xs):
    return next((x for x in xs if x is not None), None)


def app_strategy(q):
    k = kind(q)
    if k == "assertion-reason":
        return first(ar_explains(q), 0)
    if k in ("order", "match"):
        return 0
    if k == "statements":
        return first(by_code(q, APP_CODES), 3)
    if k == "negative":
        return first(neg_pick(q), 3)
    return first(numeric_rank(q, 2), avoid_absolute(q), longest(q), all_option(q), 1)


def real_strategy(q):
    k = kind(q)
    if k == "assertion-reason":
        return first(ar_explains(q), 0)
    if k == "statements":
        return first(by_code(q, REAL_CODES), all_option(q), 0)
    if k == "negative":
        return first(neg_pick(q), 3)
    return first(numeric_rank(q, 1), avoid_absolute(q), longest(q), all_option(q), 0)


out["strategies"] = {}
for name, f in (("app", app_strategy), ("real", real_strategy)):
    out["strategies"][name] = round(100 * sum(f(q) == q["a"] for _, q in qs) / len(qs), 1)
print(json.dumps(out, indent=1, ensure_ascii=False))
