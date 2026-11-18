"""Group 2 Current Affairs (official P4) one-liners in APPSC's angles - judged by helpers, applied by tools/group2_build.py.

    python3 tools/ca_angles.py build      data/caangle/job-N.jsonl: per Current Affairs section, its one-liners
                                          (all stay in Current Affairs: none moved, none removed)
    python3 tools/ca_angles.py check      validate data/caangle/job-N.out.jsonl

job-N.out.jsonl (helpers), one line each:
    {"id": "...", "v": "keep"}                                 a current-affairs fact at an APPSC angle
    {"id": "...", "v": "edit", "s": ..., "o": [4], "a": k, "x": ...}   same fact, asked at APPSC's headline angle
    {"new": {"row": "<g2 book:row>", "s": ..., "o": [4], "a": k, "x": ..., "angle": ...}}  a headline fact of the notes
                                                               with no one-liner yet
Rows are Group 2 rows of data/caangle/rowmap-at-caangle.json (-> APPSC Complete rows, stable across rebuilds).
"""
import collections, glob, json, os, re, sys

G = "app/src/group2/assets"
D = "data/caangle"
J = lambda p: json.load(open(p))


def rows_of(b):
    return [x for u in J(f"{G}/book{b}.json")["units"] for x in u["rows"]]


def build(n_jobs=10):
    os.makedirs(D, exist_ok=True)
    json.dump(J("data/g2syl/rowmap.json"), open(f"{D}/rowmap-at-caangle.json", "w"))
    ca = {}
    for b in range(1, 7):
        m = J(f"{G}/mcq{b}.json")
        for r, qs in m["rows"].items():
            v = [q for q in qs if q["id"].startswith("o") and q.get("lf", "").startswith("P4")]
            if v:
                ca[(b, int(r))] = v
    titles = {b: [x["title"] for x in rows_of(b)] for b in range(1, 7)}
    items = sorted(ca.items())
    per = sum(len(v) for _, v in items) / n_jobs
    jobs, cur, size = [], [], 0
    for k, v in items:
        if cur and size + len(v) > per * 1.15 and len(jobs) < n_jobs - 1:
            jobs.append(cur); cur, size = [], 0
        cur.append((k, v)); size += len(v)
    jobs.append(cur)
    for ji, job in enumerate(jobs, 1):
        with open(f"{D}/job-{ji}.jsonl", "w") as f:
            for (b, r), v in job:
                for q in v:
                    f.write(json.dumps({"id": q["id"], "section": f"{b}:{r}", "title": titles[b][r], "q": q["s"],
                                        "o": q["o"], "a": q["a"], "x": q.get("x", "")}, ensure_ascii=False) + "\n")
        print(f"job-{ji}: {len(job)} sections, {sum(len(v) for _, v in job)} one-liners")


def check():
    bad = 0
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        inp = [json.loads(l) for l in open(f.replace(".out", "")) if l.strip()]
        want = {x["id"]: x for x in inp}
        secs = {x["section"] for x in inp}
        seen, c = set(), collections.Counter()
        for n, l in enumerate(open(f), 1):
            if not l.strip():
                continue
            o = json.loads(l)
            if "new" in o:
                x = o["new"]
                ok = x.get("row") in secs and isinstance(x.get("o"), list) and len(x["o"]) == 4 and x.get("a") in range(4) and x.get("s")
                c["new"] += 1
            else:
                x = want.get(o.get("id"))
                v = o.get("v")
                ok = x is not None and o["id"] not in seen and v in ("keep", "edit")
                if ok and v == "edit":
                    ok = len(o.get("o") or []) == 4 and o.get("a") in range(4) and bool(o.get("s"))
                seen.add(o.get("id")); c[v] += 1
            if not ok:
                bad += 1; print(f"{f}:{n} bad: {l.strip()[:200]}")
        miss = set(want) - seen
        print(f"{f}: {dict(c)}; missing {len(miss)}")
        bad += len(miss)
    return bad


if __name__ == "__main__":
    {"build": build, "check": check}[sys.argv[1]]()
