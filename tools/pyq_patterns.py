"""Pattern statistics of the PYQs (APPSC vs UPSC vs state PSC): question types, signal words, answer shapes,
subject and topic spread. Writes data/pyq/patterns.json (the tricks PDF is written from it).

    python3 tools/pyq_patterns.py
"""
import json, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, "tools")
from pyq_place import cleaned, usable, bank  # noqa: E402
from pyq_apply import rank, keep  # noqa: E402

TYPES = [
    ("Assertion-Reason", r"assertion|\(A\).*\(R\)|reason \(R\)"),
    ("Match the following", r"\bmatch\b|list[- ]?i\b|correctly matched|correctly paired|pairs? (?:is|are) (?:not )?correct|following pairs"),
    ("How many statements/pairs", r"\bhow many\b"),
    ("Statement-based (consider the following)", r"consider the following|following statements?|statements? (?:is|are) (?:correct|true|incorrect|not)|which of the (?:above|statements)"),
    ("Chronological / sequence", r"chronolog|correct (?:order|sequence)|arrange|ascending|descending|from north to south|from west to east|earliest to"),
    ("Negative (NOT / incorrect / false)", r"\bnot\b|incorrect|false|wrongly|except|untrue"),
    ("Superlative / first / largest", r"\b(?:first|largest|smallest|highest|lowest|longest|biggest|oldest|earliest|most|least|maximum|minimum|top)\b"),
    ("Who / person", r"^\s*who\b|\bwho (?:was|is|among|wrote|founded|headed|propounded)"),
    ("When / year / date", r"\b(?:when|which year|in the year)\b"),
    ("Where / place", r"\bwhere\b|located|situated|which (?:state|district|city|river|country)"),
    ("Article / Schedule / Amendment number", r"\barticle\b|\bschedule\b|amendment|\bpart [ivx]+\b"),
    ("Scheme / programme / mission", r"scheme|yojana|mission|programme|abhiyan|policy"),
    ("Definition / term / known as", r"known as|is called|refers to|term|means|meaning|stands for|full form"),
    ("Fill in the blank", r"_{2,}|\.{4,}|-{3,}"),
    ("Data / number fact", r"\b(?:percentage|per cent|%|how much|how many (?!of the))\b"),
]
EXTREME = r"\b(?:only|always|never|all|none|every|entirely|completely|solely|exclusively|must|cannot|any|wholly|absolutely)\b"
HEDGE = r"\b(?:may|might|can|generally|usually|mostly|some|often|sometimes|largely|mainly|primarily)\b"

ANSWER_SHAPES = [
    ("All of the above / 1,2,3 all", r"all of the above|^(?:1|i|a)\s*,\s*(?:2|ii|b)\s*(?:,\s*(?:3|iii|c))?\s*and\s*(?:3|4|iii|iv|c|d)$|^all\b"),
    ("None of the above / neither", r"none of the above|neither|^none\b"),
    ("Both", r"^both\b"),
    ("Only one item", r"^only (?:one|\w+)$|^(?:1|2|3|4|i|ii|iii|iv|a|b|c|d) only$|^only (?:1|2|3|4|i|ii|iii|iv)$"),
    ("Two items", r"^(?:\w+) and (?:\w+)(?: only)?$|^(?:only )?(?:1|2|3|i|ii|iii) and (?:2|3|4|ii|iii|iv)(?: only)?$"),
]


def main():
    qs = [q for q in map(cleaned, bank()) if usable(q)]
    place = json.load(open("data/pyq/place-complete.json"))["place"]
    titles = {}
    for b in range(1, 7):
        bk = json.load(open(f"app/src/complete/assets/book{b}.json")); ri = 0
        for u in bk["units"]:
            for r in u["rows"]:
                titles[(b, ri)] = (u["title"] if "title" in u else "", r["title"]); ri += 1
    groups = {0: "APPSC", 1: "UPSC", 2: "State PSC"}
    out = {}
    for g, gname in groups.items():
        G = [q for q in qs if rank(q) == g]
        A = [q for q in G if q["a"] >= 0]
        types = Counter(); tbook = defaultdict(Counter); ex = defaultdict(list)
        ext_correct = Counter(); hedge_correct = Counter(); pos = Counter(); shapes = Counter(); shape_total = Counter()
        longest = 0; words = Counter(); book = Counter(); topic = Counter(); nopts_len = []
        for q in G:
            s = q["s"]; low = s.lower()
            p = place.get(q["id"])
            b = p[0] if p and keep(q, p[3]) else 0
            book[b] += 1
            if b:
                topic[titles[(p[0], p[1])][1]] += 1
            matched = False
            for name, rx in TYPES:
                if re.search(rx, low, re.I | re.M):
                    types[name] += 1; tbook[b][name] += 1; matched = True
                    if len(ex[name]) < 6 and q["a"] >= 0 and len(s) < 300:
                        ex[name].append([s, q["o"], q["a"]])
            if not matched:
                types["Direct one-liner (what/which)"] += 1; tbook[b]["Direct one-liner (what/which)"] += 1
                if len(ex["Direct one-liner (what/which)"]) < 6 and q["a"] >= 0:
                    ex["Direct one-liner (what/which)"].append([s, q["o"], q["a"]])
            words.update(w for w in re.findall(r"\b(?:not|incorrect|correct|true|false|only|all|none|both|first|largest|recently|launched|"
                                                r"established|founded|headquarters|article|amendment|scheme|consider|match|which|who|when|where|"
                                                r"chronological|recently|2023|2024|2025|andhra|india)\b", low))
        for q in A:
            pos[q["a"]] += 1
            ans = q["o"][q["a"]].strip().lower()
            # options with extreme / hedge words: how often is such an option the answer?
            for i, o in enumerate(q["o"]):
                if re.search(EXTREME, o, re.I):
                    ext_correct["total"] += 1; ext_correct["correct"] += i == q["a"]
                if re.search(HEDGE, o, re.I):
                    hedge_correct["total"] += 1; hedge_correct["correct"] += i == q["a"]
            for name, rx in ANSWER_SHAPES:
                present = [i for i, o in enumerate(q["o"]) if re.search(rx, o.strip().lower())]
                if present:
                    shape_total[name] += 1; shapes[name] += q["a"] in present
            # longest option correct?
            L = [len(o) for o in q["o"]]
            if L.count(max(L)) == 1:
                nopts_len.append(L.index(max(L)) == q["a"])
        out[gname] = {
            "count": len(G), "answered": len(A), "types": types.most_common(), "types_by_book": {str(k): v.most_common() for k, v in tbook.items()},
            "examples": ex, "answer_position": [pos[i] for i in range(4)],
            "extreme_option": dict(ext_correct), "hedge_option": dict(hedge_correct),
            "answer_shapes": {k: [shapes[k], shape_total[k]] for k in shape_total},
            "longest_option_correct": [sum(nopts_len), len(nopts_len)],
            "signal_words": words.most_common(40), "books": book.most_common(), "topics": topic.most_common(80),
        }
        print(gname, len(G), types.most_common(6), [pos[i] for i in range(4)], dict(ext_correct), dict(hedge_correct),
              {k: [shapes[k], shape_total[k]] for k in shape_total}, sum(nopts_len), len(nopts_len))
    json.dump(out, open("data/pyq/patterns.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
