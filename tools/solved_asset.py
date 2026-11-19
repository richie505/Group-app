"""The worked solutions of the latest papers (data/solved/job-*.out.jsonl) as an app asset, keyed by each app's MCQ id:
solved.json = {id: {"m": method, "t": [tricks], "s": [steps], "k": [[key words, why]], "f": fact}}.
Option letters (a)-(d) become the app's numbers (1)-(4).

    python3 tools/solved_asset.py      -> app/src/complete/assets/solved.json, app/src/group2/assets/solved.json
"""
import glob, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import g2syl_lib as L

FILES = {"g1p24p1": "data/appscpapers/group1-prelims-2024-paper1.json", "g1p24p2": "data/appscpapers/group1-prelims-2024-paper2.json",
         "g2p24": "data/g2papers/prelims-2024.json", "g2m25p1": "data/g2papers/mains-2025-paper1.json", "g2m25p2": "data/g2papers/mains-2025-paper2.json"}
NUM = {"a": "1", "b": "2", "c": "3", "d": "4"}


def fix(t):
    t = re.sub(r"\(([a-d])\)", lambda m: f"({NUM[m.group(1)]})", t)
    return re.sub(r"\boption ([a-d])\b", lambda m: f"option {NUM[m.group(1)]}", t)


def main():
    out = {}
    for f in sorted(glob.glob("data/solved/job-*.out.jsonl")):
        for l in open(f):
            if not l.strip():
                continue
            o = json.loads(l)
            path = FILES[o["paper"]]
            slug = os.path.basename(path)[:-5]
            tag = L.PAPER_TAG.get(slug, (None,))[0]
            ids = [f"y{tag}{int(o['n']):03d}"] if tag else []
            ids.append("yQ" + hashlib.md5(f"{slug}|{o['n']}".encode()).hexdigest()[:10])
            rec = {"m": o.get("method", ""), "t": o.get("tricks", [])[:4], "s": [fix(x) for x in o.get("steps", [])],
                   "k": [[u["text"], u.get("why", "")] for u in o.get("underline", [])][:5], "f": o.get("fact", "")}
            for i in ids:
                out[i] = rec
    for A in ("app/src/complete/assets", "app/src/group2/assets"):
        ids = set()
        for b in range(1, 7):
            for qs in json.load(open(f"{A}/mcq{b}.json"))["rows"].values():
                ids |= {q["id"] for q in qs}
        mine = {k: v for k, v in out.items() if k in ids}
        open(f"{A}/solved.json", "w").write(json.dumps(mine, ensure_ascii=False, separators=(",", ":")))
        print(A, len(mine), "worked solutions")


if __name__ == "__main__":
    main()
