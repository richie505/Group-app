"""Group 2 previous-year questions that the app still lacks (from the OCR'd PYQ books in data/pyq/all.jsonl.gz:
the Shreshta APPSC Group-2 PYQ book, Group II-B 1991, Group 2 2011 AP History ...). The official papers
(data/g2papers) are all in the app already.

    python3 tools/pyqfill.py export     -> data/pyqfill/job-N.txt (the candidates no app MCQ matches, by text or options)
    python3 tools/pyqfill.py check N    -> checks data/pyqfill/job-N.out.jsonl
    python3 tools/pyqfill.py export all / check all N -> the same for every other exam in the bank (UPSC, APPSC's other
                                         exams, Group 1, state PSCs): data/pyqfill/all/, only what a Group 2 line covers
    python3 tools/pyqfill.py apply      -> adds the rebuilt questions to APPSC Complete's MCQs (the master of Group 2)
Then rebuild Group 2: python3 tools/group2_build.py 2026-11-16 && python3 tools/build_plan_mcq.py app/src/group2/assets
"""
import collections, difflib, glob, gzip, hashlib, json, os, re, sys

C = "app/src/complete/assets"
G2 = "app/src/group2/assets"
D = "data/pyqfill"
PER = 30
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def walk(x, out):
    if isinstance(x, dict):
        if "s" in x and "o" in x and "a" in x:
            out.append(x)
            return
        for v in x.values():
            walk(v, out)
    elif isinstance(x, list):
        for v in x:
            walk(v, out)


class Bank:
    """the Group 2 app's MCQs, for matching by question text or by options"""

    def __init__(self, folder=G2):
        self.q = []
        for b in range(1, 7):
            walk(J(f"{folder}/mcq{b}.json"), self.q)
        self.n = [norm(q["s"]) for q in self.q]
        self.head = {n[:80] for n in self.n}
        self.words, self.opts = collections.defaultdict(set), collections.defaultdict(set)
        for i, n in enumerate(self.n):
            for w in set(n.split()):
                if len(w) > 4:
                    self.words[w].add(i)
            for o in self.q[i]["o"]:
                if len(norm(o)) > 3:
                    self.opts[norm(o)].add(i)

    def has(self, s, opts=()):
        n = norm(s)
        if n[:80] in self.head:
            return True
        c = collections.Counter(i for w in set(n.split()) if len(w) > 4 for i in self.words.get(w, ()))
        if any(difflib.SequenceMatcher(None, n, self.n[i]).ratio() > 0.8 for i, _ in c.most_common(15)):
            return True
        os_ = [norm(o) for o in opts if len(norm(o)) > 3 and not re.fullmatch(r"[\d ]+", norm(o))]
        c = collections.Counter(i for o in os_ for i in self.opts.get(o, ()))
        return len(os_) >= 2 and bool(c) and c.most_common(1)[0][1] >= min(3, len(os_))


LEAVES = set(re.findall(r"\b([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):", open("data/g2syl/leaves.md").read()))
MA = re.compile(r"\b(average of|marks|ratio|series|next number|next term|coded|code language|odd one|day of the week|"
                r"clock|train|profit|interest|age of|sum of|digit|triangles|mirror image|blood relation|seating|"
                r"arrangement|direction|missing number|in the place of question mark)\b", re.I)


def export(everything=False):
    """the Group 2 PYQ books (default), or with "all" every other exam in the bank (UPSC, APPSC's other exams,
    Group 1, state PSCs): questions no Group 2 app MCQ matches, Mental Ability and unreadable ones left out"""
    global D
    D = D[:-4] if D.endswith("/all") else D
    bank = Bank()
    L = [json.loads(l) for l in gzip.open("data/pyq/all.jsonl.gz", "rt")]
    g2 = lambda x: re.search(r"group[- ]?(ii|2)\b", f"{x.get('exam')}{x.get('paper')}{x.get('source')}", re.I)
    G = [x for x in L if (not g2(x)) == everything]
    if everything:
        D = f"{D}/all"
        G = [x for x in G if len(x.get("o") or []) == 4 and not MA.search(x.get("s") or "")]
    todo = [x for x in G if len(norm(x.get("s"))) >= 15 and not bank.has(x["s"], x.get("o", []))]
    os.makedirs(D, exist_ok=True)
    for f in glob.glob(f"{D}/job-*.txt"):
        os.unlink(f)
    for k in range(0, len(todo), PER):
        part = todo[k:k + PER]
        txt = []
        for x in part:
            o = "\n".join(f"  ({i + 1}) {v}" for i, v in enumerate(x.get("o", [])))
            txt.append(f"## {x['id']} | {x.get('exam')} | key: ({x.get('answer')})\n{x['s']}\n{o}\nexplanation (OCR): {x.get('x', '')}")
        open(f"{D}/job-{k // PER + 1}.txt", "w").write("\n\n".join(txt) + "\n")
    print(f"{len(G)} candidate PYQs, {len(todo)} not in the Group 2 app -> {D}/job-1..{(len(todo) - 1) // PER + 1}")


def ids(n):
    return [l.split(" | ")[0][3:].strip() for l in open(f"{D}/job-{n}.txt") if l.startswith("## ")]


def check(n):
    want = ids(n)
    got, bad = {}, []
    for k, l in enumerate(open(f"{D}/job-{n}.out.jsonl")):
        if l.strip():
            try:
                o = json.loads(l)
                got[o["id"]] = o
            except Exception as e:
                bad.append(f"line {k + 1}: not JSON ({e})")
    pages = set()
    for b in range(1, 7):
        rows = [r for u in J(f"{C}/book{b}.json")["units"] for r in u["rows"]]
        pages |= {f"{b}:{i}:{j}" for i, r in enumerate(rows) for j in range(len(r["secs"]))}
    for i in want:
        o = got.get(i)
        if not o:
            bad.append(f"{i}: missing")
            continue
        d = o.get("d")
        if d not in ("add", "exists", "skip", "beyond"):
            bad.append(f"{i}: d must be add / exists / beyond / skip")
        if d == "add" and D.endswith("/all") and o.get("leaf") not in LEAVES:
            bad.append(f"{i}: leaf {o.get('leaf')!r} is not a Group 2 syllabus leaf (data/g2syl/leaves.md)")
        if d == "add":
            q = o.get("mcq") or {}
            if not (q.get("s") and isinstance(q.get("o"), list) and len(q["o"]) == 4 and q.get("a") in (0, 1, 2, 3) and q.get("x")):
                bad.append(f"{i}: mcq needs s, 4 options o, a 0-3 and x")
            if not q.get("src"):
                bad.append(f"{i}: mcq needs src (the exam, e.g. 'APPSC Group 2 (2011)')")
            if o.get("page") not in pages:
                bad.append(f"{i}: page {o.get('page')!r} is not a notes page (b:r:j)")
            if re.search(r"Q\d+\.|\b\d\.\s*\(\d\)|SHRESHTA|ACADEMY", json.dumps(q)):
                bad.append(f"{i}: OCR noise left in the question")
        if d == "skip" and not o.get("why"):
            bad.append(f"{i}: skip needs why")
    print(f"job {n}: {len(want)} questions, problems: {len(bad)}")
    for b in bad[:40]:
        print("  " + b)


def apply():
    outs = [json.loads(l) for f in sorted(glob.glob("data/pyqfill/**/job-*.out.jsonl", recursive=True)) for l in open(f) if l.strip()]
    mcqs = {b: J(f"{C}/mcq{b}.json") for b in range(1, 7)}
    bank = Bank(C)
    n = dup = 0
    seen = set()  # two jobs can rebuild the same question
    for o in outs:
        if o.get("d") != "add":
            continue
        q = o["mcq"]
        if bank.has(q["s"]) or norm(q["s"])[:80] in seen:  # by the question (two can share four options)
            dup += 1
            continue
        seen.add(norm(q["s"])[:80])
        b, i, j = map(int, o["page"].split(":"))
        qid = "pq" + hashlib.md5((q["s"] + "|".join(q["o"])).encode()).hexdigest()[:10]
        L = mcqs[b]["rows"].setdefault(str(i), [])
        S = mcqs[b]["subs"].setdefault(str(i), [])
        if all(x["id"] != qid for x in L):
            L.append({"id": qid, "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"], "src": q["src"]})
            S.append(j)
            n += 1
    for b in range(1, 7):
        W(f"{C}/mcq{b}.json", mcqs[b])
    print(f"PYQs added: {n} (already there: {dup})")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[1:2] == ["all"]:  # the other exams' jobs: data/pyqfill/all/
        D, PER, a = f"{D}/all", 50, a[:1] + a[2:]
    {"export": lambda: export(D.endswith("/all")), "check": lambda: check(a[1]), "apply": apply}[a[0]]()
