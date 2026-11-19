"""Hand-checked corrections of Group 2 notes MCQs whose answer looked wrong (explanation disagreeing with the key, or a
fact flagged by the pattern helpers): data/fixes/job-N.jsonl -> job-N.out.jsonl, applied last by tools/group2_build.py.

job-N.out.jsonl: {"id": "...", "s" / "o" / "a" / "x": <new full value, only if changed>, "note": "..."}
"""
import glob, json

D = "data/fixes"


def load(d=D):
    out = {}
    for f in sorted(glob.glob(f"{d}/job-*.out.jsonl")):
        inp = {j["id"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                if o.get("id") in inp:
                    out[o["id"]] = (inp[o["id"]], o)
    return out


def apply(q, FX):
    """the correction, only while the MCQ still has the options and key it was checked with"""
    if q["id"] not in FX:
        return q
    j, o = FX[q["id"]]
    if q.get("o") != j["o"] or q.get("a") != j["a"]:
        return q
    ch = {k: o[k] for k in ("s", "o", "a", "x") if k in o}
    if not ch:
        return q
    q = dict(q, **ch)
    return {k: v for k, v in q.items() if k not in ("xs", "xa")} if "x" in ch or "a" in ch else q
