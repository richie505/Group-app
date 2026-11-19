"""Second pass: EVERY notes MCQ of Group 2 in APPSC's pattern (APPSC: Cracked), after tools/notes_realign.py.

  - every statement set not touched by the first pass: its false statements rebuilt with this subject's APPSC traps
    (kept when they already are one), and each subject's share of false statements moved toward APPSC's
    (History / AP History / Geography gentler, Polity / Economy / Society harsher);
  - Assertion-Reason: the answer mix moved toward APPSC's ("both true, R explains A" about half);
  - number options: the key a middle value about 60% of the time (APPSC 57-64%), not 82% (decoys changed by code).

    python3 tools/notes_retwist.py plan      -> data/retwist/job-N.jsonl
    python3 tools/notes_retwist.py check     validate data/retwist/job-N.out.jsonl
Applied by tools/group2_build.py through apply_all().
out lines: statement sets {"id", "st": {"<label>": "<text>"}, "x"};  Assertion-Reason {"id", "A": "...", "R": "...", "x"}
"""
import collections, glob, hashlib, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import notes_realign as NR

D = "data/retwist"
FALSE_TARGET = {"Indian History": 0.30, "AP History & Culture": 0.24, "Geography": 0.31, "Science, Technology & Environment": 0.38,
                "Current Affairs": 0.37, "Polity & Constitution": 0.47, "Economy": 0.50, "Indian Society": 0.50}
AR_TARGET = {"explains": 0.53, "both-not": 0.15, "A-true": 0.22, "A-false": 0.10}
ARX = re.compile(r"^\s*(Assertion\s*\(A\)\s*:?)\s*(.+)$", re.I | re.M)
RRX = re.compile(r"^\s*(Reason\s*\(R\)\s*:?)\s*(.+)$", re.I | re.M)


def ar_kind(t):
    t = t.lower()
    if "both" in t:
        return "both-not" if "not" in t else "explains"
    if re.search(r"\ba\b.*\b(true|correct)\b.*\br\b.*\b(false|incorrect)", t):
        return "A-true"
    if re.search(r"\ba\b.*\b(false|incorrect)\b.*\br\b.*\b(true|correct)", t):
        return "A-false"
    return None


def plan():
    import notes_pattern as NP
    rnd = random.Random(4242)
    done = set(NR.load())
    qs = [q for q in NP.notes_mcqs() if q["id"] not in done]
    full = {q["id"]: q for q in qs}
    sets, ars = [], []
    for q in qs:
        if ARX.search(q["s"]) and RRX.search(q["s"]):
            k = ar_kind(q["o"][q["a"]])
            if k:
                ars.append((q, k))
            continue
        if NR.NOT_SET.search(q["s"]):
            continue
        lines, st = NR.parse(q)
        labels = [l for _, l, _ in st]
        if len(st) not in (2, 3, 4) or len(set(labels)) != len(labels) or not re.fullmatch(r"[0-9]", labels[0]):
            continue
        tail = " ".join(l for l in lines if not NR.STMT.match(l))
        if re.search(r"\b(incorrect|not correct|false|wrong|NOT)\b", tail) or not re.search(r"\b(correct|true)\b", tail, re.I):
            continue
        tr = NR.truths(q, labels)
        if tr is None:
            continue
        q["_st"], q["_tr"] = st, tr
        sets.append(q)
    # subject balance: how many statements to flip, over this subject's sets (both passes count toward the share)
    jobs = {q["id"]: {"type": "st", "id": q["id"], "subject": q["subj"], "b": q["b"], "r": q["r"], "question": q["s"], "options": q["o"],
                      "key": q["a"], "truth": q["_tr"], "retwist": [l for l, v in q["_tr"].items() if not v], "make_false": [], "make_true": [],
                      "twists": NR.TWISTS.get(q["subj"], "")} for q in sets}
    import notes_pattern as NP2
    allst = collections.defaultdict(lambda: [0, 0])
    import appsc_tricks as T
    S, _ = T.statements("n.json", {"questions": NP2.notes_mcqs(), "date": "2026"})
    subj_of = {q["n"]: q["subj"] for q in NP2.notes_mcqs()}
    for x in S:
        if x["kind"] in ("list", "pair"):
            allst[subj_of[x["n"]]][0] += 1
            allst[subj_of[x["n"]]][1] += not x["true"]
    for sj, (n, f) in allst.items():
        delta = round(FALSE_TARGET.get(sj, 0.4) * n - f)
        mine = [q for q in sets if q["subj"] == sj]
        rnd.shuffle(mine)
        moved = 0
        for q in mine:
            if moved >= abs(delta):
                break
            j = jobs[q["id"]]
            tr = q["_tr"]
            txt = {l: t for _, l, t in q["_st"]}
            if delta < 0:  # gentler: correct one false statement
                fl = [l for l, v in tr.items() if not v]
                if fl:
                    l = fl[0]
                    j["make_true"].append(l)
                    j["retwist"].remove(l)
                    moved += 1
            else:  # harsher: falsify one true statement (trap words first), keep at least one true in a set of 3+
                tl = sorted([l for l, v in tr.items() if v], key=lambda l: (not NR.TRAP.search(txt[l]), rnd.random()))
                if len(tl) >= 2:
                    j["make_false"].append(tl[0])
                    moved += 1
        print(f"{sj:36} statements {n:6}, false {100 * f / max(1, n):.0f}% -> target {100 * FALSE_TARGET.get(sj, 0.4):.0f}%: {moved} flips")
    # Assertion-Reason: move toward APPSC's answer mix
    by = collections.defaultdict(list)
    for q, k in ars:
        by[k].append(q)
    n = len(ars)
    want = {k: round(p * n) for k, p in AR_TARGET.items()}
    arjobs = []
    for k in ("A-false", "both-not", "A-true"):
        extra = len(by[k]) - want[k]
        if extra > 0:
            rnd.shuffle(by[k])
            for q in by[k][:extra]:
                arjobs.append({"type": "ar", "id": q["id"], "subject": q["subj"], "b": q["b"], "r": q["r"], "question": q["s"], "options": q["o"],
                               "key": q["a"], "from": k, "to": "explains"})
    print(f"Assertion-Reason: {n}; now {dict((k, len(v)) for k, v in by.items())}; want {want}; {len(arjobs)} to rewrite")
    alljobs = list(jobs.values())
    rnd.shuffle(alljobs)
    os.makedirs(D, exist_ok=True)
    size, k = 400, 0
    for i in range(0, len(alljobs), size):
        k += 1
        with open(f"{D}/job-{k}.jsonl", "w") as f:
            for j in sorted(alljobs[i:i + size], key=lambda j: (j["b"], j["r"])):
                f.write(json.dumps(j, ensure_ascii=False) + "\n")
    for i in range(0, len(arjobs), 300):
        k += 1
        with open(f"{D}/job-{k}.jsonl", "w") as f:
            for j in arjobs[i:i + 300]:
                f.write(json.dumps(j, ensure_ascii=False) + "\n")
    print(f"{len(alljobs)} statement sets ({sum(len(j['retwist']) for j in alljobs)} false statements to rebuild, "
          f"{sum(len(j['make_true']) for j in alljobs)} to correct, {sum(len(j['make_false']) for j in alljobs)} to falsify) + "
          f"{len(arjobs)} Assertion-Reason in {k} jobs")


def load():
    plan_, out = {}, {}
    for f in sorted(glob.glob(f"{D}/job-*.jsonl")):
        if f.endswith(".out.jsonl"):
            continue
        for l in open(f):
            j = json.loads(l)
            plan_[j["id"]] = j
        of = f.replace(".jsonl", ".out.jsonl")
        if os.path.exists(of):
            for l in open(of):
                if l.strip():
                    o = json.loads(l)
                    out[o["id"]] = o
    return plan_, out


def check():
    plan_, out = load()
    bad = 0
    for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")):
        inp = [json.loads(l) for l in open(f.replace(".out", ""))]
        got = {json.loads(l)["id"]: json.loads(l) for l in open(f) if l.strip()}
        for j in inp:
            o = got.get(j["id"])
            if o is None:
                bad += 1
                continue
            if j["type"] == "st":
                need = set(j["retwist"] + j["make_false"] + j["make_true"])
                if set(o.get("st", {})) != need or len(o.get("x", "")) < 20:
                    bad += 1
                    print("bad", f, j["id"])
            elif not (o.get("A") or o.get("R")) or len(o.get("x", "")) < 20:
                bad += 1
                print("bad", f, j["id"])
        print(f"{f}: {len(got)} of {len(inp)}")
    return bad


def _num(x):
    m = re.fullmatch(r"(\s*[₹$]?\s*)([\d,]+(?:\.\d+)?)(\s*(?:%|per ?cent|crore|lakh|km|million|billion|years)?\.?\s*)", x)
    return (m.group(1), float(m.group(2).replace(",", "")), m.group(3), m.group(2)) if m else None


def _fmt(v, like):
    dec = len(like.split(".")[1]) if "." in like else 0
    s = f"{v:,.{dec}f}" if "," in like else f"{v:.{dec}f}"
    return s


def numbers(q):
    """number options with a middle key: about a quarter get a decoy moved past the key, so the key ends up an extreme"""
    o = q.get("o") or []
    if len(o) != 4 or not (0 <= q.get("a", -1) < 4):
        return q
    ns = [_num(x) for x in o]
    if any(n is None for n in ns) or len({n[1] for n in ns}) != 4:
        return q
    order = sorted(range(4), key=lambda i: ns[i][1])
    pos = order.index(q["a"])
    if pos not in (1, 2) or int(hashlib.md5(q["id"].encode()).hexdigest(), 16) % 100 >= 27:
        return q
    vals = [n[1] for n in ns]
    lo, hi = min(vals), max(vals)
    span = max(hi - lo, 1)
    years = all(1000 <= v <= 2100 and float(v).is_integer() for v in vals)
    x = q.get("x", "") or ""
    # move the decoys on the near side past the far end, so the key becomes the smallest (pos 1) or largest (pos 2)
    movers = order[:pos] if pos == 1 else order[pos + 1:]
    new = list(o)
    for k, i in enumerate(movers):
        if ns[i][3] in x:
            return q  # the explanation names this decoy: leave the question as it is
        if pos == 1:
            v = hi + span * (0.25 + 0.2 * k)
        else:
            v = lo - span * (0.25 + 0.2 * k)
        if years:
            v = round(v)
            if v > 2025 or v < 1000:
                return q
        if v <= 0:
            return q
        if not years and float(ns[i][1]).is_integer():
            v = round(v)
        new[i] = ns[i][0] + _fmt(v, ns[i][3]) + ns[i][2]
    if len(set(new)) != 4:
        return q
    return dict(q, o=new)


def apply_all(q, plan_, out, rnd):
    j, o = plan_.get(q["id"]), out.get(q["id"])
    if j and o:
        if j["type"] == "ar":
            s = q["s"]
            if o.get("A"):
                s = ARX.sub(lambda m: m.group(1) + " " + o["A"].strip(), s, count=1)
            if o.get("R"):
                s = RRX.sub(lambda m: m.group(1) + " " + o["R"].strip(), s, count=1)
            key = next((i for i, t in enumerate(q["o"]) if ar_kind(t) == "explains"), None)
            if key is not None:
                q = {k: v for k, v in dict(q, s=s, a=key, x=o["x"]).items() if k not in ("xs", "xa")}
        elif not NR.NOT_SET.search(q["s"]):
            lines, st = NR.parse(q)
            labels = [l for _, l, _ in st]
            tr = NR.truths(q, labels)
            if tr is not None and set(o.get("st", {})) <= set(labels):
                flips = set(j["make_false"] + j["make_true"])
                for i, l, t in st:
                    if l in o["st"]:
                        m = NR.STMT.match(lines[i])
                        lines[i] = m.group(1) + m.group(2) + m.group(3) + o["st"][l].strip()
                        if l in flips:
                            tr[l] = not tr[l]
                if o.get("truth"):
                    tr = {l: bool(o["truth"].get(l, tr[l])) for l in labels}
                nq = dict(q, s="\n".join(lines), x=o["x"])
                if flips or o.get("truth"):
                    opts, a = NR.options({l for l, v in tr.items() if v}, labels, rnd)
                    nq = dict(nq, o=opts, a=a)
                q = {k: v for k, v in nq.items() if k not in ("xs", "xa")}
    return numbers(q)


if __name__ == "__main__":
    {"plan": plan, "check": lambda: sys.exit(1 if check() else 0)}[sys.argv[1]]()
