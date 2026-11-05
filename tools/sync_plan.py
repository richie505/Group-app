"""APPSC Complete: the MCQ notes and the MCQs in step. For every MCQ fact (each statement of a 3-statement MCQ,
else the right answer), the subsection page that holds it; MCQs filed under a page that does not hold their fact
move to the page that does (same topic); facts no page holds are listed for writing (data/sync/in/*.md); notes lines
no MCQ of their topic tests are listed. Writes data/sync/plan.json.

    python3 tools/sync_plan.py
"""
import collections, json, os, re

A = "app/src/complete/assets"
N = "app/src/complete/mcqnotes"
STOP = set("""the and for with from that this which were was are is its their has have been into about what who whom
when where how not one two also only such than then them they there these those other more most some any all each both
under over after before between during within india indian state states andhra pradesh government first second third
main known called following correct statement statements consider select answer code codes given above below option
options true false incorrect pair pairs matched""".split())
CODE = re.compile(r"^(\d|[ivx]+|[a-d])(\s*(,|and|-)\s*(\d|[ivx]+|[a-d]))*( only)?$|both|neither|all of|none of", re.I)


def toks(t):
    """words as stems: no hyphens, first 5 letters ("Ardh-Magadhi" = "Ardha-Magadhi", "copper plate" = "copper-plate")"""
    out = set()
    for w in re.findall(r"[a-z][a-z\-]{2,}|\d[\d,.]*", t.lower()):
        if w in STOP:
            continue
        if w[0].isdigit():
            out.add(w.rstrip(".,"))
        else:
            for part in w.split("-"):
                if len(part) >= 3 and part not in STOP:
                    out.add(part[:5])
    return out


def txt(b):
    if "x" in b:
        return "".join(r[0] for r in b["x"])
    return " ".join(str(c) for c in re.findall(r'"([^"]+)"', json.dumps(b.get("r", ""), ensure_ascii=False)))


def facts(q):
    st = re.findall(r"^\s*\d\.\s+(.+)$", q["s"], re.M)
    why = dict(re.findall(r"^Statement (\d):\s*(?:Correct|Incorrect):\s*(.+)$", q.get("x", ""), re.M))
    if len(st) >= 2:
        return [(i + 1, s, why.get(str(i + 1), "")) for i, s in enumerate(st)]
    a = q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q["o"]) else ""
    return [(0, a if a and not CODE.search(a.strip()) else "", q.get("x", ""))]


def holds(unit, page):
    return len(unit & page) >= max(1, min(3, len(unit)) * 0.6)


def main():
    plan = {"moves": {}, "missing": [], "orphans": 0}
    os.makedirs("data/sync/in", exist_ok=True)
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        bk = json.load(open(f"{N}/book{b}.json"))
        rows = [r for u in bk["units"] for r in u["rows"]]
        for ri, qs in m["rows"].items():
            r = rows[int(ri)]
            subs = m["subs"].get(ri, [-1] * len(qs))
            pages = [toks(" ".join(txt(x) for x in s["b"])) for s in r["secs"]]
            if not pages:
                continue
            for q, si in zip(qs, subs):
                fs = facts(q)
                units = [toks(f[1] + " " + (f[2] if not f[1] else "")) or toks(q["s"]) for f in fs]
                score = [sum(len(u & P) for u in units) for P in pages]
                best = max(range(len(pages)), key=lambda i: score[i])
                cur = score[si] if 0 <= si < len(pages) else -1
                if score[best] > cur * 1.5 and score[best] >= 3:
                    plan["moves"][q["id"]] = [b, int(ri), best]
                    si = best
                for (n, s, why), u in zip(fs, units):
                    if u and not any(holds(u, P) for P in pages):
                        plan["missing"].append({"id": q["id"], "b": b, "r": int(ri), "page": si, "n": n,
                                                "topic": r["title"], "pagetitle": r["secs"][si]["t"] if 0 <= si < len(pages) else "",
                                                "q": q["s"] if not n else s, "answer": "" if n else s, "why": why})
    # the first run is the plan the writers worked from; later runs only report (data/sync/plan-after.json)
    out = "data/sync/plan.json" if not os.path.exists("data/sync/plan.json") else "data/sync/plan-after.json"
    json.dump(plan, open(out, "w"), ensure_ascii=False, indent=0)
    print(f"{len(plan['moves'])} MCQs to re-file; {len(plan['missing'])} facts to write into the notes")


if __name__ == "__main__":
    main()
