"""Group 2's notes MCQs measured against APPSC's real pattern (APPSC: Cracked): per subject the question-type mix,
statement truth, statement-set answers, answer positions, All/None of the above, and how the trap words behave.

    python3 tools/notes_pattern.py [assets=app/src/group2/assets]   -> data/tricks/notes-pattern.json
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T
import appsc_subjects as AS

A = sys.argv[1] if len(sys.argv) > 1 and __name__ == "__main__" else "app/src/group2/assets"


def notes_mcqs():
    qs = []
    for b in range(1, 7):
        bk = json.load(open(f"{A}/book{b}.json"))
        rows = [(u["title"], r["title"]) for u in bk["units"] for r in u["rows"]]
        m = json.load(open(f"{A}/mcq{b}.json"))
        for r, L in m["rows"].items():
            for q in L:
                if q["id"].startswith("y") or not q.get("o") or not (0 <= q.get("a", -1) < len(q["o"])) or q.get("k") in ("f", "u"):
                    continue
                unit, row = rows[int(r)]
                qs.append(dict(n=len(qs), s=q["s"], o=q["o"], a=q["a"], subject="", id=q["id"], subj=AS.subject(("g2", b, unit, row), ""), b=b, r=int(r)))
    return qs


def qtype(q, kinds):
    k = kinds.get(q["n"])
    if k in ("list", "pair", "item"):
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


def profile(qs, S, Q):
    kinds = {}
    for x in S:
        kinds.setdefault(x["n"], x["kind"])
    by = {q["n"]: q for q in qs}
    out = {}
    for sj in AS.SUBJECTS + ["ALL"]:
        qq = [q for q in Q if sj == "ALL" or by[q["n"]]["subj"] == sj]
        ss = [x for x in S if (sj == "ALL" or by[x["n"]]["subj"] == sj) and x["kind"] != "item"]
        if not qq:
            continue
        mix = collections.Counter(qtype(q, kinds) for q in qq)
        n = len(qq)
        pos = collections.Counter(q["a"] for q in qq if q["nopt"] == 4)
        aoa = [q for q in qq if any(re.search(r"\ball (of )?(the )?(above|these|them)\b", x, re.I) for x in q["o"])]
        nota = [q for q in qq if any(re.search(r"\bnone of (the )?(above|these|them)\b|^\s*neither\b", x, re.I) for x in q["o"])]
        sets = collections.defaultdict(list)
        for x in S:
            if (sj == "ALL" or by[x["n"]]["subj"] == sj) and x["kind"] in ("list", "pair"):
                sets[x["n"]].append(x["true"])
        d3 = collections.Counter(sum(v) for v in sets.values() if len(v) == 3)
        d4 = collections.Counter(sum(v) for v in sets.values() if len(v) == 4)
        rules = {}
        for k in ("only", "but_not", "extreme", "negated", "by_institution", "exactnum", "year", "first", "ap"):
            h = [x for x in ss if T.COMP[k].search(x["text"])]
            if len(h) >= 20:
                rules[k] = [len(h), round(100 * sum(not x["true"] for x in h) / len(h))]
        out[sj] = {"q": n, "mix": {k: round(100 * v / n) for k, v in mix.items()}, "st": len(ss),
                   "false": round(100 * sum(not x["true"] for x in ss) / max(1, len(ss))),
                   "pos": [round(100 * pos[i] / max(1, sum(pos.values()))) for i in range(4)],
                   "aoa": [len(aoa), sum(bool(re.search(r"\ball (of )?(the )?(above|these|them)\b", q["o"][q["a"]], re.I)) for q in aoa)],
                   "nota": [len(nota), sum(bool(re.search(r"\bnone of (the )?(above|these|them)\b|^\s*neither\b", q["o"][q["a"]], re.I)) for q in nota)],
                   "d3": [d3[i] for i in range(4)], "d4": [d4[i] for i in range(5)], "rules": rules}
    return out


def main():
    qs = notes_mcqs()
    S, Q = T.statements("notes.json", {"questions": qs, "date": "2026"})
    notes = profile(qs, S, Q)
    # APPSC's own recent papers, same measure
    pq, PS, PQ = [], [], []
    for f in T.PAPERS:
        p = json.load(open(f))
        ex, y = T.exam_of(f, p)
        if int(y) < 2023 or ex not in ("Group 1 Prelims", "Group 2 Prelims", "Group 2 Mains"):
            continue
        s, q = T.statements(f, p)
        off = len(pq)
        loc = {}
        for qq in p["questions"]:
            sub = qq.get("subject", "")
            sj = {"History": "Indian History", "Polity": "Polity & Constitution", "Indian Constitution": "Polity & Constitution",
                  "Economy": "Economy", "Indian & AP Economy": "Economy", "Geography": "Geography", "Science & Technology": "Science, Technology & Environment",
                  "Current Affairs": "Current Affairs", "Indian Society": "Indian Society", "Social & Cultural History of AP": "AP History & Culture",
                  "AP History & Culture": "AP History & Culture"}.get(sub, sub)
            loc[qq["n"]] = off + len(loc)
            pq.append(dict(n=off + len(loc) - 1, subj=sj))
        for x in s:
            x["n"] = loc[x["n"]]
        for x in q:
            x["n"] = loc[x["n"]]
        PS += s
        PQ += q
    appsc = profile(pq, PS, PQ)
    json.dump({"notes": notes, "appsc": appsc}, open("data/tricks/notes-pattern.json", "w"), indent=1)
    for sj in notes:
        a, b = notes[sj], appsc.get(sj, {})
        print(f"\n== {sj}: notes {a['q']} q / APPSC 2023-25 {b.get('q', 0)} q")
        print("   mix   notes", a["mix"], "\n         appsc", b.get("mix"))
        print(f"   statements false: notes {a['false']}% ({a['st']})  appsc {b.get('false')}%  | positions notes {a['pos']} appsc {b.get('pos')}")
        print(f"   AoA notes {a['aoa']} appsc {b.get('aoa')} | NOTA notes {a['nota']} appsc {b.get('nota')}")
        print(f"   3-st true counts notes {a['d3']} appsc {b.get('d3')} | 4-st notes {a['d4']} appsc {b.get('d4')}")
        print(f"   rules (n, %false) notes {a['rules']}  appsc {b.get('rules')}")


if __name__ == "__main__":
    main()
