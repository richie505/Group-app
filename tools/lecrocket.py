"""Lecture slides in the Rocket-sheet style (docs/lectures/rocket-style.md): every notes page rewritten as crisp
Fact | Key detail tables. Pages the two apps share are written once (by the page's content).

    python3 tools/lecrocket.py export      -> data/lecrocket/jobs/job-N.txt (Group 2's pages first)
    python3 tools/lecrocket.py check [N]   -> checks data/lecrocket/jobs/job-N.out.jsonl (all if no N)
    python3 tools/lecrocket.py assemble    -> data/lecrocket/<group1|group2>/<book>-<row>.json (read by tools/lecture_pdf.py)
"""
import glob, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lecture_clean as LC

D = "data/lecrocket/jobs"
GROUPS = ("group2", "group1")
LIMIT = 150000  # characters of notes per job


def pages():
    """[(hash, [(group, book, row, page)], topic title, page title, blocks)] in order, Group 2 first"""
    H, order = {}, []
    for g in GROUPS:
        A = f"app/src/{g}/assets"
        idx = json.load(open(f"{A}/index.json"))["books"]
        for b in range(1, 7):
            bk = json.load(open(f"{A}/book{b}.json"))
            rows = [r for u in bk["units"] for r in u["rows"]]
            for i, r in enumerate(rows):
                if idx[b - 1]["rows"][i].get("hide"):
                    continue
                for j, s in enumerate(r["secs"]):
                    bl = s["b"]
                    if not bl or (len(bl) == 1 and bl[0].get("k") == "n" and str(bl[0]["x"][0][0]).startswith("No MCQ")):
                        continue
                    h = hashlib.md5((s["t"] + json.dumps(bl, ensure_ascii=False, sort_keys=True)).encode()).hexdigest()[:12]
                    if h not in H:
                        H[h] = [h, [], r["title"], s["t"], bl]
                        order.append(h)
                    H[h][1].append((g, b, i, j))
    return [H[h] for h in order]


def md(x):
    """runs -> text with **bold**, citations out (the quiz wording is left for the rewrite to turn into facts)"""
    if isinstance(x, str):
        return x
    rr = [(str(r[0]), r[1]) if isinstance(r, list) and len(r) > 1 else (str(r[0] if isinstance(r, list) else r), 0) for r in x]
    t = "".join(a for a, _ in rr)
    c = LC._cite(t)
    out, pos = "", 0
    for a, b in rr:
        a = a.strip()
        if b and len(a) > 1:
            k = c.find(a, pos)
            if k >= 0:
                out += c[pos:k] + f"**{a}**"
                pos = k + len(a)
    return out + c[pos:]


def page_text(bl):
    L = []
    for b in bl:
        k = b.get("k")
        if k == "t":
            L.append("t: " + " | ".join(md(c) for c in b.get("h") or []))
            for r in b.get("r") or []:
                L.append("   row: " + " | ".join(md(c) for c in r))
            continue
        t = md(b.get("x", []))
        if not t.strip() or LC.drop_block(k, LC._cite("".join(str(r[0]) if isinstance(r, list) else str(r) for r in b.get("x", [])))):
            continue
        L.append(f"{k}: {t}")
    return "\n".join(L)


def export():
    os.makedirs(D, exist_ok=True)
    for f in glob.glob(f"{D}/job-*.txt"):
        os.unlink(f)
    n, buf, size = 0, [], 0
    def flush():
        nonlocal n, buf, size
        if buf:
            n += 1
            open(f"{D}/job-{n}.txt", "w").write("\n\n".join(buf) + "\n")
        buf, size = [], 0
    for h, where, topic, title, bl in pages():
        t = f"## page {h}\ntopic: {topic}\npage title: {title}\n{page_text(bl)}"
        if size + len(t) > LIMIT:
            flush()
        buf.append(t)
        size += len(t)
    flush()
    print(f"{n} jobs in {D}")


NUM = re.compile(r"\d+(?:[.,]\d+)?")
BAD = re.compile(r"\bNOT\b|\bTRUE\b|\bFALSE\b|\bExam (?:fact|angle)|\bStatement angle|\bA-R\b|\bPYQ|\(\s*[a-d]\s*\)\s*is\b")


def plain(b):
    if b.get("k") == "t":
        return " ".join(b.get("h", []) + [c for r in b.get("r", []) for c in r])
    return b.get("x", "")


def check_job(f):
    """problems of a job's output, per page"""
    want = {}
    for blk in open(f.replace(".out.jsonl", ".txt")).read().split("## page ")[1:]:
        h, rest = blk.split("\n", 1)
        body = "\n".join(l for l in rest.split("\n")[2:])
        want[h.strip()] = body
    got, bad = {}, {}
    for n, l in enumerate(open(f)):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
            got[o["h"]] = o["b"]
        except Exception as e:
            bad[f"line {n + 1}"] = f"not JSON: {e}"
    for h, body in want.items():
        if h not in got:
            bad[h] = "missing"
            continue
        bl, p = got[h], []
        if not isinstance(bl, list) or not bl:
            bad[h] = "empty"
            continue
        txt = ""
        for b in bl:
            if b.get("k") not in ("h", "t", "b", "x"):
                p.append(f"bad kind {b.get('k')}")
            if b.get("k") == "t":
                hh = b.get("h") or []
                if any(len(r) != len(hh) for r in b.get("r") or []) and hh:
                    p.append("table row with a different number of cells")
            txt += " " + plain(b)
        ins = re.sub(r"\*\*", "", body)
        nums = set(NUM.findall(ins))
        miss = [x for x in nums if x not in txt]
        if nums and len(miss) > max(1, len(nums) * 0.1):
            p.append(f"numbers lost: {miss[:8]}")
        bolds = {x.strip() for x in re.findall(r"\*\*([^*]{2,40})\*\*", body)}
        out = re.sub(r"\*\*", "", txt).lower()
        lost = [x for x in bolds if x.lower() not in out]
        if bolds and len(lost) > max(1, len(bolds) * 0.2):
            p.append(f"key terms lost: {lost[:8]}")
        q = BAD.search(txt) or LC.QUIZ.search(txt) or LC.TOK.search(txt)
        if q:
            p.append(f"quiz / citation wording: {q.group(0)!r}")
        if p:
            bad[h] = "; ".join(p)
    return len(want), bad


def check(which=None):
    fs = [f"{D}/job-{which}.out.jsonl"] if which else sorted(glob.glob(f"{D}/job-*.out.jsonl"), key=lambda x: int(re.search(r"(\d+)\.out", x).group(1)))
    tot = probs = 0
    for f in fs:
        if not os.path.exists(f):
            print(f, "not written yet")
            continue
        n, bad = check_job(f)
        tot += n
        probs += len(bad)
        print(f"{os.path.basename(f)}: {n} pages, {len(bad)} with problems")
        for h, why in list(bad.items())[:40] if which else []:
            print(f"  {h}: {why}")
    print(f"total {tot} pages, {probs} with problems")


def assemble():
    got = {}
    for f in glob.glob(f"{D}/job-*.out.jsonl"):
        for l in open(f):
            if l.strip():
                try:
                    o = json.loads(l)
                    got[o["h"]] = o["b"]
                except Exception:
                    pass
    topics, n = {}, 0
    for h, where, *_ in pages():
        if h in got:
            for g, b, i, j in where:
                topics.setdefault((g, b, i), {})[str(j)] = got[h]
                n += 1
    for (g, b, i), d in topics.items():
        os.makedirs(f"data/lecrocket/{g}", exist_ok=True)
        json.dump(d, open(f"data/lecrocket/{g}/{b}-{i}.json", "w"), ensure_ascii=False, indent=0)
    print(f"{n} pages of {len(topics)} topics written")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["export"]:
        export()
    elif a[:1] == ["check"]:
        check(a[1] if len(a) > 1 else None)
    elif a[:1] == ["assemble"]:
        assemble()
