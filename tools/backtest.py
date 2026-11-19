"""Backtest: can the rules (and the words of statements) learnt from the PYQ bank crack APPSC's 2023-25 papers?

Train: every statement of the app's PYQ bank (tools/pyq_corpus.py) except any that is (nearly) a statement of the
2023-25 APPSC papers. Test: the statements and statement-set questions of APPSC Group 1 Prelims 2023 / 2024 and Group 2
Prelims 2024 / Mains 2025, as if sitting them knowing nothing.

    python3 tools/backtest.py     -> data/tricks/backtest.json
"""
import collections, json, os, re, sys

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from scipy.sparse import hstack, csr_matrix

sys.path.insert(0, os.path.dirname(__file__))
import appsc_tricks as T
import pyq_corpus as PC

norm = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def test_set():
    St, Qs = [], []
    for f in T.PAPERS:
        p = json.load(open(f))
        ex, y = T.exam_of(f, p)
        if int(y) < 2023 or ex not in ("Group 1 Prelims", "Group 2 Prelims", "Group 2 Mains"):
            continue
        s, q = T.statements(f, p)
        St += [x for x in s if x["kind"] != "item"]
        Qs += [dict(qq, paper=os.path.basename(f)[:-5]) for qq in q]
    return St, Qs


def feats(texts, vec=None):
    R = csr_matrix(np.array([[1.0 if T.COMP[k].search(t) else 0.0 for k in T.R] for t in texts]))
    if vec is None:
        return R
    return hstack([R, vec.transform(texts)]).tocsr()


def main():
    S, _, _ = PC.corpus()
    te, tq = test_set()
    tn = {norm(x["text"])[:80] for x in te}
    tr = [x for x in S if norm(x["text"])[:80] not in tn]
    print(f"train {len(tr)} statements (bank minus the test papers), test {len(te)} statements of APPSC 2023-25")
    ytr = np.array([0 if x["true"] else 1 for x in tr])  # 1 = false
    yte = np.array([0 if x["true"] else 1 for x in te])
    base_te = yte.mean()
    out = {"train": len(tr), "test": len(te), "test_false": round(100 * base_te, 1)}
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=5, sublinear_tf=True, stop_words="english").fit([x["text"] for x in tr])
    models = {}
    for name, use_vec in (("rules", False), ("rules+words", True)):
        Xtr = feats([x["text"] for x in tr], vec if use_vec else None)
        Xte = feats([x["text"] for x in te], vec if use_vec else None)
        m = LogisticRegression(max_iter=2000, C=1.0 if use_vec else 10.0, class_weight=None).fit(Xtr, ytr)
        p = m.predict_proba(Xte)[:, 1]
        auc = roc_auc_score(yte, p)
        # statement calls: "false" when p > train false rate (calibrated threshold), also the confident subset
        thr = ytr.mean()
        acc = ((p > thr) == yte).mean()
        conf = np.abs(p - thr) > 0.15
        acc_conf = ((p[conf] > thr) == yte[conf]).mean() if conf.any() else 0
        models[name] = (m, use_vec, p)
        out[name] = {"auc": round(auc, 3), "acc": round(100 * acc, 1), "conf_share": round(100 * conf.mean(), 1), "acc_conf": round(100 * acc_conf, 1)}
        print(f"{name:12} AUC {auc:.3f}  statement accuracy {100 * acc:.1f}% (always-'true' baseline {100 * (1 - base_te):.1f}%)  "
              f"confident {100 * conf.mean():.0f}% of statements -> {100 * acc_conf:.1f}% right")
    if True:
        mr = LogisticRegression(max_iter=2000, C=10.0).fit(feats([x["text"] for x in tr]), ytr)
        coef = sorted(zip(T.R, mr.coef_[0]), key=lambda kv: -kv[1])
        out["weights"] = [(T.R[k][0], round(float(c), 2)) for k, c in coef]
        print("rule weights (log-odds of FALSE):", [(T.R[k][0][:25], round(float(c), 2)) for k, c in coef])
    # --- question level: statement sets of the test papers, pick the option the model likes best
    m, use_vec, p_all = models["rules+words"]
    pmap = {}
    for x, pv in zip(te, p_all):
        pmap.setdefault((x["paper"], x["n"]), []).append((x, pv))
    res = collections.Counter()
    elim = collections.Counter()
    for q in tq:
        key = (q["paper"], q["n"])
        if key not in pmap or q["nopt"] != 4:
            continue
        rows = pmap[key]
        if rows[0][0]["kind"] == "option":
            # each option is a statement; "which is correct" -> pick lowest p(false); "incorrect" -> highest
            neg = bool(T.NEG.search(q["s"])) or bool(re.search(r"\b(not|incorrectly|wrongly)\s+(correctly\s+)?(matched|paired)\b", q["s"], re.I))
            ps = [pv for _, pv in rows]
            if len(ps) != 4:
                continue
            pick = int(np.argmax(ps)) if neg else int(np.argmin(ps))
            worst = int(np.argmin(ps)) if neg else int(np.argmax(ps))
        else:
            lines = q["s"].split("\n")
            st = [(T.norm_lab(mm.group(1)), mm.group(2).strip()) for mm in (T.STMT.match(l) for l in lines) if mm]
            labels = [l for l, _ in st]
            if len(labels) != len(rows):
                continue
            tail = " ".join(l for l in lines if not T.STMT.match(l))
            neg = bool(T.NEG.search(tail.split("statement")[-1] if "statement" in tail else tail))
            pf = {l: pv for l, (_, pv) in zip(labels, rows)}
            scores = []
            for o in q["o"]:
                sel = T.picked(o, labels)
                if sel is None:
                    scores.append(-1e9)
                    continue
                ll = 0.0
                for l in labels:
                    is_true = (l in sel) != neg
                    pr = pf[l]
                    ll += np.log(max(1e-6, (1 - pr) if is_true else pr))
                scores.append(ll)
            if max(scores) < -1e8:
                continue
            pick = int(np.argmax(scores))
            worst = int(np.argmin(scores))
            # partial knowledge: you know ONE statement (each in turn); strike the options that contradict it, then
            # either guess among the rest or let the model pick among the rest
            sels = [T.picked(o, labels) for o in q["o"]]
            truth = {l: (l in (sels[q["a"]] or set())) != neg for l in labels}
            for l in labels:
                ok = [i for i, sel in enumerate(sels) if sel is not None and ((l in sel) != neg) == truth[l]]
                if not ok or q["a"] not in ok:
                    continue
                res["k1"] += 1
                res["k1_guess"] += 1 / len(ok)
                res["k1_left"] += len(ok)
                res["k1_model"] += max(ok, key=lambda i: scores[i]) == q["a"]
        res["questions"] += 1
        res["right"] += pick == q["a"]
        elim["n"] += 1
        elim["worst_wrong"] += worst != q["a"]
    if res["k1"]:
        k = res["k1"]
        print(f"knowing ONE statement: {res['k1_left'] / k:.2f} options left on average; guessing among them right "
              f"{100 * res['k1_guess'] / k:.0f}%, model picking among them right {100 * res['k1_model'] / k:.0f}%")
    out["questions"] = dict(res)
    out["elim"] = dict(elim)
    print(f"statement-set questions sat: {res['questions']}; model's pick right: {res['right']} "
          f"({100 * res['right'] / max(1, res['questions']):.0f}% vs 25% chance); "
          f"the option it ranks LAST is wrong {100 * elim['worst_wrong'] / max(1, elim['n']):.0f}% of the time")
    # expected marks with -1/3: answer the pick (no knowledge) on these questions
    n, r = res["questions"], res["right"]
    out["marks"] = round(r - (n - r) / 3, 1)
    print(f"marks if answered blind by the model: {out['marks']} out of {n} (chance-guessing expects 0)")
    json.dump(out, open("data/tricks/backtest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
