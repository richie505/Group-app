"""The whole PYQ bank of the app (APPSC Complete's ~40,000 PYQs: APPSC, UPSC, other State PSCs, SSC ...) as statements whose
truth the key fixes, to test the elimination rules on far more than APPSC's own papers - and a backtest: a model built
only from the bank WITHOUT the 2023-25 APPSC papers, scored on those papers as if sitting them.

    python3 tools/pyq_corpus.py      -> data/tricks/corpus.json (+ summary on stdout)
"""
import collections, glob, hashlib, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T
import appsc_subjects as AS
from g2syl_source import tier, year

C = "app/src/complete/assets"
TIERN = {"g2": "APPSC Group 2", "ap": "Other APPSC exams", "up": "UPSC", "ot": "Other State PSCs & exams"}


def corpus():
    qs, seen = [], set()
    for b in range(1, 7):
        bk = json.load(open(f"{C}/book{b}.json"))
        rows = [(u["title"], r["title"]) for u in bk["units"] for r in u["rows"]]
        m = json.load(open(f"{C}/mcq{b}.json"))
        for r, L in m["rows"].items():
            for q in L:
                if not q["id"].startswith("y") or not q.get("o") or not (0 <= q.get("a", -1) < len(q["o"])) or q.get("k") in ("f", "u"):
                    continue
                k = re.sub(r"\W+", "", q["s"].lower())[:200] + "|" + re.sub(r"\W+", "", q["o"][q["a"]].lower())
                if k in seen:
                    continue
                seen.add(k)
                unit, row = rows[int(r)]
                qs.append(dict(n=len(qs), s=q["s"], o=q["o"], a=q["a"], subject="", id=q["id"], src=q.get("src", ""),
                               tier=tier(q), yr=year(q) or 0, subj=AS.subject(("c", b, unit, row), ""), topic=AS.topic_of(row)))
    S, Q = T.statements("bank.json", {"questions": qs, "date": "2000"})
    by = {q["n"]: q for q in qs}
    for x in S + Q:
        q = by[x["n"]]
        x.update(tier=q["tier"], yr=q["yr"], subj=q["subj"], topic=q["topic"], id=q["id"])
    return [x for x in S if x["kind"] != "item"], Q, qs


def paper_ids():
    """ids of the full APPSC papers' questions as they sit in the bank (to keep the 2023-25 test papers out of training)"""
    import g2syl_lib as L
    ids = {}
    for f in T.PAPERS:
        slug = os.path.basename(f)[:-5]
        tag = L.PAPER_TAG.get(slug, (None,))[0]
        p = json.load(open(f))
        for q in p["questions"]:
            ids[f"y{tag}{q['n']:03d}" if tag else "yQ" + hashlib.md5(f"{slug}|{q['n']}".encode()).hexdigest()[:10]] = (slug, str(p.get("date", ""))[:4])
    return ids


def main():
    S, Q, qs = corpus()
    print(f"bank: {len(qs)} unique PYQs, {len(S)} statements with a known truth")
    out = {"n_pyq": len(qs), "n_st": len(S), "tiers": {}, "rules": {}, "subjects": {}}
    for t in TIERN:
        st = [x for x in S if x["tier"] == t]
        out["tiers"][t] = {"name": TIERN[t], "n": len(st), "false": round(100 * sum(not x["true"] for x in st) / max(1, len(st)), 1),
                           "pyq": sum(q["tier"] == t for q in qs)}
    base_all = sum(not x["true"] for x in S) / len(S)
    out["base"] = round(100 * base_all, 1)
    # --- every rule, every exam family
    for k, (title, _) in T.R.items():
        row = {"title": title}
        for t in list(TIERN) + ["all"]:
            st = [x for x in S if (t == "all" or x["tier"] == t) and T.COMP[k].search(x["text"])]
            row[t] = [len(st), round(100 * sum(not x["true"] for x in st) / max(1, len(st)), 1)]
        out["rules"][k] = row
        print(f"{title[:50]:50} " + "  ".join(f"{t}:{row[t][0]:5}/{row[t][1]:5}%" for t in list(TIERN) + ["all"]))
    # --- per subject: base, rules, cue words (n >= 20)
    for sj in AS.SUBJECTS:
        st = [x for x in S if x["subj"] == sj]
        if not st:
            continue
        base = sum(not x["true"] for x in st) / len(st)
        rules = {}
        for k, (title, _) in T.R.items():
            h = [x for x in st if T.COMP[k].search(x["text"])]
            if len(h) >= 25:
                rules[k] = {"title": title, "n": len(h), "pct": round(100 * sum(not x["true"] for x in h) / len(h), 1)}
        cnt = collections.defaultdict(lambda: [0, 0])
        for x in st:
            for w in set(AS.words(x["text"]) + AS.bigrams(x["text"])):
                cnt[w][0 if x["true"] else 1] += 1
        cues = []
        for w, (t_, f) in cnt.items():
            n = t_ + f
            if n < 20:
                continue
            z = (f / n - base) / math.sqrt(max(base * (1 - base), 0.01) / n)
            cues.append((w, n, f, round(100 * f / n), round(z, 2)))
        lf = sorted([c for c in cues if c[4] >= 2.5], key=lambda c: -c[4])[:18]
        lt = sorted([c for c in cues if c[4] <= -2.5], key=lambda c: c[4])[:12]
        out["subjects"][sj] = {"n": len(st), "base": round(100 * base, 1), "rules": rules, "lean_false": lf, "lean_true": lt}
        print(f"\n== {sj}: {len(st)} statements, {100 * base:.0f}% false")
        print("   rules", {k: (v["n"], v["pct"]) for k, v in rules.items()})
        print("   FALSE", [(c[0], c[1], c[3]) for c in lf])
        print("   TRUE ", [(c[0], c[1], c[3]) for c in lt])
    json.dump(out, open("data/tricks/corpus.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
