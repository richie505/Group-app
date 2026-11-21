"""Fill the notes from the source library (docs/coverage-vs-sources.md): facts the sources give that the notes lack.
Edits APPSC Complete's notes (app/src/complete/assets), the master both Group 1 Prelims and Group 2 are built from.

    python3 tools/gapfill.py export            -> data/gapfill/job-N.txt (candidate terms with their source passages)
    python3 tools/gapfill.py find WORD ...     -> the notes pages that mention the words (for the helpers)
    python3 tools/gapfill.py check N           -> checks data/gapfill/job-N.out.jsonl
    python3 tools/gapfill.py apply             -> adds the lines (and MCQs) to the master notes
"""
import glob, hashlib, json, os, re, sys

C = "app/src/complete/assets"
D = "data/gapfill"
SRC = "data/notes2026/src"
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))


def plain(x):
    return "".join(str(r[0]) if isinstance(r, list) else str(r) for r in x)


def pages():
    """[(id "b:r:j", topic, page title, text)] of the master notes"""
    out = []
    for b in range(1, 7):
        rows = [r for u in J(f"{C}/book{b}.json")["units"] for r in u["rows"]]
        for i, r in enumerate(rows):
            for j, s in enumerate(r["secs"]):
                t = []
                for bl in s["b"]:
                    if bl.get("k") == "t":
                        t += [" | ".join(plain(c) for c in rr) for rr in [bl.get("h") or []] + (bl.get("r") or [])]
                    elif isinstance(bl.get("x"), list):
                        t.append(plain(bl["x"]))
                out.append((f"{b}:{i}:{j}", r["title"], s["t"], "\n".join(t)))
    return out


def find(words):
    ws = [w.lower() for w in words if len(w) > 2]
    hits = []
    for pid, topic, title, text in pages():
        low = (title + "\n" + text).lower()
        sc = sum(low.count(w) for w in ws) + 3 * sum(w in title.lower() for w in ws)
        if sc and all(w in low for w in ws[:1]):
            line = next((l for l in text.split("\n") if any(w in l.lower() for w in ws)), "")
            hits.append((sc, pid, topic, title, line))
    hits.sort(key=lambda x: -x[0])
    for sc, pid, topic, title, line in hits[:10]:
        print(f"{pid} | {topic[:70]} | {title[:60]} | {line[:160]}")
    if not hits:
        print("no page mentions it")


def export():
    cand = J(f"{D}/candidates.json")
    files = {s: sorted(glob.glob(f"{SRC}/{s}/*.txt")) for s in cand}
    for f in glob.glob(f"{D}/job-*.txt"):
        os.unlink(f)
    items = []
    for subj, L in sorted(cand.items()):
        texts = [(f, open(f, errors="ignore").read()) for f in files.get(subj, []) if not f.endswith(".ocr.txt") or True]
        # NextGen / Rocket / APPSC-branded first
        texts.sort(key=lambda x: 0 if re.search(r"nextgen|rocket|appsc", x[0]) else 1)
        for term, n in L:
            snips = []
            for f, t in texts:
                for m in re.finditer(re.escape(term), t):
                    a, z = max(0, m.start() - 300), min(len(t), m.end() + 300)
                    snips.append(f"[{os.path.basename(f)}] " + re.sub(r"\s+", " ", t[a:z]))
                    break
                if len(snips) >= 2:
                    break
            if snips:
                items.append(f"## term: {term}\nsubject: {subj}\nseen in the sources: {n} times\n" + "\n".join(snips))
    n, buf, size = 0, [], 0
    for it in items:
        if size + len(it) > 60000 and buf:
            n += 1
            open(f"{D}/job-{n}.txt", "w").write("\n\n".join(buf) + "\n")
            buf, size = [], 0
        buf.append(it)
        size += len(it)
    if buf:
        n += 1
        open(f"{D}/job-{n}.txt", "w").write("\n\n".join(buf) + "\n")
    print(f"{len(items)} terms in {n} jobs")


def check(n):
    want = re.findall(r"^## term: (.+)$", open(f"{D}/job-{n}.txt").read(), re.M)
    ids = {p[0] for p in pages()}
    got, bad = {}, []
    for k, l in enumerate(open(f"{D}/job-{n}.out.jsonl")):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
        except Exception as e:
            bad.append(f"line {k + 1}: not JSON ({e})")
            continue
        got[o.get("term")] = o
        d = o.get("d")
        if d not in ("add", "exists", "skip"):
            bad.append(f"{o.get('term')}: d must be add / exists / skip")
        if d == "add":
            if o.get("page") not in ids:
                bad.append(f"{o['term']}: page {o.get('page')} is not a notes page id")
            if not (o.get("line") or "").strip() or len(o["line"]) > 400:
                bad.append(f"{o['term']}: line missing or too long")
            q = o.get("mcq")
            if q and (len(q.get("o") or []) != 4 or not 0 <= q.get("a", -1) < 4 or not q.get("s") or not q.get("x")):
                bad.append(f"{o['term']}: mcq needs s, 4 options o, a 0-3 and x")
    miss = [t for t in want if t not in got]
    if miss:
        bad.append(f"terms not answered: {miss[:10]}{' ...' if len(miss) > 10 else ''}")
    print(f"{len(want)} terms, {len(got)} answered, {sum(o.get('d') == 'add' for o in got.values())} to add")
    for b in bad[:40]:
        print("  " + b)
    print("problems:", len(bad))


def bold_runs(t):
    return [[p, i % 2] for i, p in enumerate(re.split(r"\*\*", t)) if p]


def apply():
    adds = [json.loads(l) for f in sorted(glob.glob(f"{D}/job-*.out.jsonl")) for l in open(f) if l.strip()]
    adds = [o for o in adds if o.get("d") == "add"]
    books = {b: J(f"{C}/book{b}.json") for b in range(1, 7)}
    mcqs = {b: J(f"{C}/mcq{b}.json") for b in range(1, 7)}
    rows = {b: [r for u in bk["units"] for r in u["rows"]] for b, bk in books.items()}
    np = nq = 0
    for o in adds:
        b, i, j = map(int, o["page"].split(":"))
        sec = rows[b][i]["secs"][j]
        if any(plain(bl.get("x", [])) == o["line"].replace("**", "") for bl in sec["b"] if isinstance(bl.get("x"), list)):
            continue  # already added
        sec["b"].append({"k": "b", "x": bold_runs(o["line"])})
        np += 1
        q = o.get("mcq")
        if q:
            qid = "gf" + hashlib.md5((q["s"] + "|".join(q["o"])).encode()).hexdigest()[:10]
            L = mcqs[b]["rows"].setdefault(str(i), [])
            S = mcqs[b]["subs"].setdefault(str(i), [])
            if all(x["id"] != qid for x in L):
                L.append({"id": qid, "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"]})
                S.append(j)
                nq += 1
    for b in range(1, 7):
        W(f"{C}/book{b}.json", books[b])
        W(f"{C}/mcq{b}.json", mcqs[b])
    print(f"notes lines added: {np}, MCQs added: {nq}")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"export": lambda: export(), "find": lambda: find(a[1:]), "check": lambda: check(a[1]), "apply": lambda: apply()}[a[0]]()
