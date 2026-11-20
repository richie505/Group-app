"""Group 2's notes MCQs in Group 2's OWN paper style (Prelims 2017-24, Mains 2017-25: ~88% one-answer questions with
short options; statement sets ~4%, matching ~5%, A-R ~2%). Statement / matching / A-R MCQs beyond those shares were
rewritten by hand as one or two one-answer questions each: data/g2style/job-N.jsonl -> job-N.out.jsonl.

job-N.out.jsonl: {"id": "...", "q": [{"s", "o", "a", "x"}, {...optional second...}]}
expand(q): the MCQ as its rewritten question(s); the first keeps the MCQ's id (progress), a second gets its own id.
"""
import glob, hashlib, json, re

D = "data/g2style"


def load(d=D):
    out = {}
    for f in sorted(glob.glob(f"{d}/job-*.out.jsonl")):
        inp = {j["id"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                # Assertion-Reason and matching MCQs stay as they are (the owner's choice): only statement sets
                # and ordering questions take the Group 2 style
                if o.get("id") in inp and o.get("q") and inp[o["id"]].get("type") not in ("AR", "match"):
                    out[o["id"]] = (inp[o["id"]], o["q"])
    return out


def expand(q, OUT):
    """[q] unchanged, or its rewrite"""
    if q["id"] not in OUT:
        return [q]
    j, new = OUT[q["id"]]  # by id: the options fix (notes_options) and the stem layout may have touched it since
    res = []
    for k, n in enumerate(new[:2]):
        if len(n.get("o") or []) != 4 or not (0 <= n.get("a", -1) < 4):
            continue
        base = {x: v for x, v in q.items() if x not in ("s", "o", "a", "x", "xs", "xa", "tg")}
        nid = q["id"] if k == 0 else "g2s" + hashlib.md5((q["id"] + n["s"]).encode()).hexdigest()[:11]
        o, a = list(n["o"]), n["a"]
        # the key's position spread evenly (A-D equally often), except number options, which stay in their order
        if not all(re.search(r"\d", x) for x in o) and not re.search(r"\b(all|none|both|neither) of (the )?(above|these)\b", " ".join(o), re.I):
            t = int(hashlib.md5(nid.encode()).hexdigest(), 16) % 4
            o[a], o[t] = o[t], o[a]
            a = t
        res.append(dict(base, id=nid, s=n["s"], o=o, a=a, x=n.get("x", "")))
    return res or [q]
