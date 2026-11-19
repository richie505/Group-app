"""How many questions of the latest APPSC papers were already in the app's PYQ bank (asked earlier in some exam):
per question the closest earlier PYQ (same question >= 0.5 cosine, same fact area >= 0.35), and per subject counts.

    python3 tools/pyq_reflect.py     -> data/solved/reflect.json
"""
import collections, hashlib, json, os, re, sys
STMT = re.compile(r"^\s*\(?(?:[a-h]|[A-H]|[ivx]{1,4}|[IVX]{1,4}|\d{1,2})[.)]\s+(.+)$")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.dirname(__file__))
from g2syl_source import tier, year
import g2syl_lib as L

P = [("g1p24p1", "data/appscpapers/group1-prelims-2024-paper1.json", 2024), ("g1p24p2", "data/appscpapers/group1-prelims-2024-paper2.json", 2024),
     ("g2p24", "data/g2papers/prelims-2024.json", 2024), ("g2m25p1", "data/g2papers/mains-2025-paper1.json", 2025),
     ("g2m25p2", "data/g2papers/mains-2025-paper2.json", 2025)]
C = "app/src/complete/assets"
doc = lambda s, a: re.sub(r"\s+", " ", s) + " " + a


def main():
    own = set()
    for code, f, y in P:
        slug = os.path.basename(f)[:-5]
        tag = L.PAPER_TAG.get(slug, (None,))[0]
        for q in json.load(open(f))["questions"]:
            own.add(f"y{tag}{q['n']:03d}" if tag else "yQ" + hashlib.md5(f"{slug}|{q['n']}".encode()).hexdigest()[:10])
    bank = []
    for b in range(1, 7):
        for qs in json.load(open(f"{C}/mcq{b}.json"))["rows"].values():
            for q in qs:
                if q["id"].startswith("y") and q["id"] not in own and q.get("o") and 0 <= q.get("a", -1) < len(q["o"]):
                    bank.append(q)
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, ngram_range=(1, 2)).fit([doc(q["s"], q["o"][q["a"]]) for q in bank])
    BM = vec.transform([doc(q["s"], q["o"][q["a"]]) for q in bank])
    by = [year(q) or 0 for q in bank]
    out = {"questions": {}, "subjects": {}}
    tn = {"g2": "APPSC Group 2", "ap": "APPSC", "up": "UPSC", "ot": "Other exams"}
    for code, f, Y in P:
        qs = [q for q in json.load(open(f))["questions"] if q.get("o")]
        S = cosine_similarity(vec.transform([doc(q["s"], q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q["o"]) else "") for q in qs]), BM)
        for i, q in enumerate(qs):
            best, bj = 0, None
            for j in S[i].argsort()[::-1][:40]:
                if by[j] and by[j] < Y:
                    best, bj = float(S[i, j]), j
                    break
            lvl = "same" if best >= 0.5 else "area" if best >= 0.35 else "new"
            rec = {"level": lvl, "score": round(best, 2)}
            if bj is not None and lvl != "new":
                b = bank[bj]
                rec |= {"src": b.get("src", ""), "tier": tn.get(tier(b), "Other"), "year": by[bj], "q": b["s"][:220], "ans": b["o"][b["a"]][:80]}
            # statement sets: each statement on its own (a set mixes several facts, which hides a repeat)
            sts = [m.group(1).strip() for m in (STMT.match(l) for l in q["s"].split("\n")) if m]
            sts = [t for t in sts if len(t.split()) >= 4]
            if len(sts) >= 2:
                SS = cosine_similarity(vec.transform(sts), BM)
                hits = []
                for si, t in enumerate(sts):
                    for j in SS[si].argsort()[::-1][:40]:
                        if by[j] and by[j] < Y:
                            if SS[si, j] >= 0.4:
                                hits.append({"st": t[:160], "src": bank[j].get("src", ""), "tier": tn.get(tier(bank[j]), "Other"), "year": by[j], "score": round(float(SS[si, j]), 2)})
                            break
                rec["st_total"], rec["st_hit"] = len(sts), len(hits)
                rec["st_hits"] = hits[:3]
                if hits and lvl == "new":
                    lvl = rec["level"] = "part"
                    rec |= {"src": hits[0]["src"], "tier": hits[0]["tier"], "year": hits[0]["year"]}
            out["questions"][f"{code}:{q['n']}"] = rec
            sj = q.get("subject") or "General"
            k = f"{code}|{sj}"
            d = out["subjects"].setdefault(k, collections.Counter())
            d["total"] += 1
            d[rec["level"]] += 1
            if lvl != "new":
                d["from " + rec["tier"]] += 1
    out["subjects"] = {k: dict(v) for k, v in out["subjects"].items()}
    json.dump(out, open("data/solved/reflect.json", "w"), ensure_ascii=False, indent=1)
    for k, v in sorted(out["subjects"].items()):
        print(f"{k:55} total {v['total']:3}  same {v.get('same', 0):3}  area {v.get('area', 0):3}  part {v.get('part', 0):3}  "
              + " ".join(f"{a}:{b}" for a, b in v.items() if a.startswith("from")))


if __name__ == "__main__":
    main()
