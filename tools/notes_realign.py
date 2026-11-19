"""Group 2's notes MCQs brought to APPSC's real pattern (APPSC: Cracked): how many statements of a set are true, how
often "None / Neither" is the key, and false statements built with APPSC's own traps per subject.

    python3 tools/notes_realign.py plan     -> data/realign/job-N.jsonl (which sets change, which statements flip)
    python3 tools/notes_realign.py check    validate data/realign/job-N.out.jsonl
Applied by tools/group2_build.py (apply(): the rewritten statements, then options + key rebuilt from the new truths).

job-N.out.jsonl (helpers): {"id": "...", "st": {"<label>": "<new statement text>", ...}, "x": "<new explanation>"}
"""
import collections, glob, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(__file__))
D = "data/realign"
# APPSC 2023-25 statement-set patterns (how many statements true), from APPSC: Cracked
TARGET = {2: [0.30, 0.40, 0.30], 3: [0.03, 0.14, 0.57, 0.26], 4: [0.06, 0.20, 0.31, 0.32, 0.11]}
TWISTS = {
    "Polity & Constitution": "a 'not' added or removed; the right thing in the wrong category (Fundamental Right vs DPSP, Schedule vs Part, Act vs Article); a wrong Article / Schedule number; the power given to the wrong office (President vs Governor, Lok Sabha vs Rajya Sabha)",
    "Economy": "a FLIPPED relation (raising CRR increases credit, a weaker rupee cuts exports); a changed number or rank; the wrong ministry / body",
    "Current Affairs": "a swapped venue / host country; the wrong organiser / ministry / body; a wrong edition or date",
    "Indian History": "the wrong person (ruler, author, founder, governor-general); the wrong place; the wrong date or order",
    "AP History & Culture": "the wrong person (king, poet, leader); the wrong place (capital, temple, inscription site); the wrong dynasty",
    "Geography": "a flipped direction (east/west-flowing, north/south, higher/lower); the wrong place (river, state, pass, port); the wrong type",
    "Science, Technology & Environment": "the wrong agency (ISRO vs DRDO, MoEFCC vs CPCB); a changed number; a flipped effect; the wrong category",
    "Indian Society": "a wrong year or number on an Act or scheme (POCSO 2012, JJ Act 2015, age limits); a stretched scope (beneficiaries)",
}
TRAP = re.compile(r"\b(only|all|every|any|never|always|entirely|solely|must|cannot|not|no|exclusively)\b", re.I)
NOT_SET = re.compile(r"\bmatch\b|list\s*-?\s*(i|ii|1|2)\b|\barrange\b|\bsequence\b|chronolog|correct order|\bpairs?\b", re.I)
STMT = re.compile(r"^(\s*\(?)([0-9]{1,2}|[a-h]|[ivx]{1,4}|[IVX]{1,4})([.)]\s+)(.+)$")


def parse(q):
    lines = q["s"].split("\n")
    st = [(i, m.group(2), m.group(4).strip()) for i, l in enumerate(lines) for m in [STMT.match(l)] if m]
    return lines, st


def truths(q, labels):
    """the statements' truth from the key option ("1 and 2 only" etc.); None if not readable"""
    import appsc_tricks as T
    sel = T.picked(q["o"][q["a"]], labels)
    return None if sel is None else {l: (l in sel) for l in labels}


def fmt(sub, labels):
    n = len(labels)
    s = [l for l in labels if l in sub]
    if not s:
        return f"Neither {labels[0]} nor {labels[1]}" if n == 2 else "None of the above"
    if len(s) == n:
        return f"Both {labels[0]} and {labels[1]}" if n == 2 else (", ".join(s[:-1]) + " and " + s[-1])
    if len(s) == 1:
        return f"{s[0]} only"
    return (", ".join(s[:-1]) + " and " + s[-1]) + " only"


def options(target, labels, rnd):
    """4 code options with the target among them (2 statements: APPSC's fixed four)"""
    import itertools
    if len(labels) == 2:
        subs = [{labels[0]}, {labels[1]}, set(labels), set()]
        return [fmt(x, labels) for x in subs], subs.index(set(target))
    allsubs = [set(c) for k in range(0, len(labels) + 1) for c in itertools.combinations(labels, k)]
    others = [x for x in allsubs if x != set(target) and (x or rnd.random() < 0.25)]
    others.sort(key=lambda x: (len(x ^ set(target)), rnd.random()))
    pick = others[:3]
    opts = pick + [set(target)]
    rnd.shuffle(opts)
    return [fmt(x, labels) for x in opts], opts.index(set(target))


def plan():
    import notes_pattern as NP
    rnd = random.Random(2026)
    qs = NP.notes_mcqs()
    cand = collections.defaultdict(list)  # (n statements, true count) -> questions
    for q in qs:
        lines, st = parse(q)
        labels = [l for _, l, _ in st]
        if NOT_SET.search(q["s"]) or len(st) not in (2, 3, 4) or len(set(labels)) != len(labels) or not re.fullmatch(r"[0-9]", labels[0] or ""):
            continue
        tail = " ".join(l for i, l in enumerate(lines) if not STMT.match(l))
        if re.search(r"\b(incorrect|not correct|false|wrong|NOT)\b", tail):
            continue
        if not re.search(r"\b(correct|true)\b", tail, re.I):
            continue
        tr = truths(q, labels)
        if tr is None:
            continue
        q["_st"], q["_tr"] = st, tr
        cand[(len(st), sum(tr.values()))].append(q)
    jobs = []
    for n, dist in TARGET.items():
        pool = {k: v for (m, k), v in cand.items() if m == n}
        total = sum(len(v) for v in pool.values())
        want = {k: round(p * total) for k, p in enumerate(dist)}
        have = {k: len(pool.get(k, [])) for k in range(n + 1)}
        # move from the over-full counts to the short ones
        donors = sorted([k for k in have if have[k] > want[k]], key=lambda k: -(have[k] - want[k]))
        spare_all = sum(max(0, have[k] - want[k]) for k in have)
        need_all = sum(max(0, want[k] - have[k]) for k in have)
        scale = min(1.0, spare_all / max(1, need_all))
        needs = {k: int(max(0, want[k] - have[k]) * scale) for k in have}
        for k_to in range(n + 1):
            need = needs[k_to]
            for k_from in donors:
                if need <= 0:
                    break
                spare = have[k_from] - want[k_from]
                if spare <= 0:
                    continue
                take = min(spare, need)
                src = pool[k_from]
                rnd.shuffle(src)
                moved, pool[k_from] = src[:take], src[take:]
                have[k_from] -= take
                need -= take
                for q in moved:
                    tr = q["_tr"]
                    if k_to > k_from:  # correct some false statements
                        flip = rnd.sample([l for l, v in tr.items() if not v], k_to - k_from)
                    else:  # falsify true statements, those with APPSC's trap words first
                        trues = [l for l, v in tr.items() if v]
                        txt = {l: t for _, l, t in q["_st"]}
                        trues.sort(key=lambda l: (not TRAP.search(txt[l]), rnd.random()))
                        flip = trues[:k_from - k_to]
                    jobs.append({"id": q["id"], "subject": q["subj"], "b": q["b"], "r": q["r"], "question": q["s"], "options": q["o"], "key": q["a"],
                                 "explanation": q.get("x", ""), "truth": tr,
                                 "make_false": [l for l in flip if tr[l]], "make_true": [l for l in flip if not tr[l]],
                                 "twists": TWISTS.get(q["subj"], "")})
        print(f"{n}-statement sets: {total}; true-count now {dict(sorted({k: len(v) for k, v in cand.items() if True}.items()))if False else ''}want {want}")
    rnd.shuffle(jobs)
    os.makedirs(D, exist_ok=True)
    size = 300
    for i in range(0, len(jobs), size):
        with open(f"{D}/job-{i // size + 1}.jsonl", "w") as f:
            for j in sorted(jobs[i:i + size], key=lambda j: (j["b"], j["r"])):
                f.write(json.dumps(j, ensure_ascii=False) + "\n")
    print(f"{len(jobs)} MCQs to rewrite in {(len(jobs) + size - 1) // size} jobs;",
          collections.Counter((len(j["truth"]), len(j["make_false"]), len(j["make_true"])) for j in jobs).most_common())


def check():
    bad = 0
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        inp = {j["id"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        seen = set()
        for l in open(f):
            o = json.loads(l)
            j = inp.get(o.get("id"))
            ok = j is not None and o["id"] not in seen and set(o.get("st", {})) == set(j["make_false"] + j["make_true"]) and len(o.get("x", "")) > 20
            seen.add(o.get("id"))
            if not ok:
                bad += 1
                print(f"{f}: bad {l[:160]}")
        print(f"{f}: {len(seen)} of {len(inp)}; missing {len(set(inp) - seen)}")
        bad += len(set(inp) - seen)
    return bad


def apply(q, out, rnd):
    """the rewritten MCQ: new statement texts, options and key rebuilt from the new truths (None if it can't be)"""
    if NOT_SET.search(q["s"]):  # a matching / ordering question read as a statement set: keep it as it is
        return None
    lines, st = parse(q)
    labels = [l for _, l, _ in st]
    tr = truths(q, labels)
    if tr is None or not set(out["st"]) <= set(labels):
        return None
    for i, l, t in st:
        if l in out["st"]:
            m = STMT.match(lines[i])
            lines[i] = m.group(1) + m.group(2) + m.group(3) + out["st"][l].strip()
            tr[l] = not tr[l]
    target = {l for l, v in tr.items() if v}
    o, a = options(target, labels, rnd)
    return dict(q, s="\n".join(lines), o=o, a=a, x=out["x"], tq="statements")


def load():
    out = {}
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                out[o["id"]] = o
    return out


if __name__ == "__main__":
    {"plan": plan, "check": lambda: sys.exit(1 if check() else 0)}[sys.argv[1]]()
