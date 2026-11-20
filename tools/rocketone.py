"""RocketOne: Group 1 Prelims notes written ONLY from the NextGen Rocket Sheets and Rocket Current Affairs 2026.

    python3 tools/rocketone.py chunks              work/rocket/*.txt -> work/rocket/chunks/*.txt (+ jobs list)
    python3 tools/rocketone.py check-rows <chunk>  is every Rocket line of the chunk in data/rocketone/rows/<chunk>.jsonl?
    python3 tools/rocketone.py topics              rows -> work/rocket/topics/<job>.jsonl (one job per syllabus line or part of it)
    python3 tools/rocketone.py check-notes <file>  a notes file (data/rocketone/notes/*.json): format, and Rocket coverage
    python3 tools/rocketone.py build               notes -> app/src/rocketone/assets (books, index) + the lecture slides

The Rocket PDFs come from the owner's Drive (ids in data/notes2026/SOURCES-LOCAL.md), as text in work/rocket/ (pdftotext -layout).
"""
import glob, json, os, re, sys

W = "work/rocket"
ROWS = "data/rocketone/rows"
NOTES = "data/rocketone/notes"
SUBJECTS = [("aphist", "AP History", 0), ("indhist1", "Indian History", 0), ("indhist2", "Indian History", 131),
            ("polity1", "Indian Polity", 0), ("polity2", "Indian Polity", 119), ("economy", "Indian Economy", 0),
            ("apgeo", "AP Geography", 0), ("gengeo", "General Geography", 0), ("indgeo", "Indian Geography", 0),
            ("worldgeo", "World Geography", 0), ("society", "Indian Society", 0), ("environment", "Environment", 0),
            ("disaster", "Disaster Management", 0), ("physics", "Physics", 0), ("chemistry", "Chemistry", 0), ("biology", "Biology", 0)]
CA = [("ca1", 0), ("ca2", 227)]
JUNK = re.compile(r"nextgenias1@gmail|SUBSCRIBE to our YouTube", re.I)
NUM = re.compile(r"^\s*\d+\s*$")  # a number alone on a line: a wrapped table cell (a year), not a page number


def leaves():
    return json.load(open("data/g1syl/leaves.json"))


def pages(key):
    return open(f"{W}/{key}.txt", encoding="utf-8", errors="replace").read().split("\f")


def clean(p):
    return [l.rstrip() for l in p.split("\n") if l.strip() and not JUNK.search(l)]


def chunks():
    os.makedirs(f"{W}/chunks", exist_ok=True)
    for f in glob.glob(f"{W}/chunks/*.txt"):
        os.unlink(f)
    jobs = []

    def flush(name, buf, n):
        f = f"{name}-{n:02d}"
        open(f"{W}/chunks/{f}.txt", "w").write("\n".join(buf) + "\n")
        jobs.append(f)

    # the subject sheets: about 50 KB a chunk, cut where a sheet starts
    for name in dict.fromkeys(s[1] for s in SUBJECTS):
        slug = name.lower().replace(" ", "-")
        buf, size, n, sheet = [], 0, 1, 0
        for key, nm, off in SUBJECTS:
            if nm != name:
                continue
            for i, p in enumerate(pages(key)):
                L = clean(p)
                m = [re.search(r"ROCKET SHEET\s*#\s*(\d+)", l) for l in L]
                new = next((int(x.group(1)) for x in m if x), None)
                L = [l for l in L if not re.search(r"ROCKET SHEET\s*#\s*\d+", l)]
                if not L:
                    continue
                if buf and (size > 52000 or (new and size > 40000)):
                    flush(slug, buf, n)
                    buf, size, n = [], 0, n + 1
                if new:
                    sheet = new
                buf.append(f"\n=== {name} · Sheet #{sheet} · p.{i + 1 + off}")
                buf += L
                size += sum(len(l) + 1 for l in L if not NUM.match(l))
        if buf:
            flush(slug, buf, n)
    # Rocket Current Affairs: whole sheets, about 45 KB a chunk
    buf, size, n, sheet = [], 0, 1, 0
    for key, off in CA:
        for i, p in enumerate(pages(key)):
            L = clean(p)
            m = [re.search(r"ROCKET Current Affairs\s*#\s*(\d+)", l) for l in L]
            new = next((int(x.group(1)) for x in m if x), None)
            L = [l for l in L if not re.search(r"ROCKET Current Affairs\s*#\s*\d+", l)]
            if not L:
                continue
            if buf and ((new and size > 36000) or size > 50000):
                flush("ca", buf, n)
                buf, size, n = [], 0, n + 1
            if new:
                sheet = new
            buf.append(f"\n=== Rocket CA 2026 · Sheet #{sheet} · p.{i + 1 + off}")
            buf += L
            size += sum(len(l) + 1 for l in L if not NUM.match(l))
    if buf:
        flush("ca", buf, n)
    L = leaves()["leaves"]
    open(f"{W}/leaves.txt", "w").write("\n".join(f"{x['leaf']}\t{x['part'].split('· ')[-1]}\t{x['text']}" for x in L) + "\n")
    json.dump(jobs, open(f"{W}/jobs.json", "w"))
    for j in jobs:
        print(j, os.path.getsize(f"{W}/chunks/{j}.txt"))
    print(len(jobs), "chunks")


WORD = re.compile(r"[A-Za-z0-9₹%][A-Za-z0-9₹%'’.,/-]*")


def toks(s):
    out = set()
    for w in WORD.findall(s):
        w = w.strip(".,'’/-").lower().replace("’", "'")
        if len(w) >= 4 or any(c.isdigit() for c in w):
            out.add(w)
    return out


def coverage(src_lines, blob, need=0.7):
    """Rocket lines whose words are not (mostly) in the output text"""
    have = toks(blob)
    miss, total = [], 0
    for l in src_lines:
        if l.startswith("=== ") or not l.strip():
            continue
        t = toks(l)
        if len(t) < 2:
            continue
        total += 1
        if len(t & have) / len(t) < need:
            miss.append(l.strip())
    return miss, total


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def check_rows(chunk):
    src = open(f"{W}/chunks/{chunk}.txt").read().split("\n")
    f = f"{ROWS}/{chunk}.jsonl"
    ok = {x["leaf"] for x in leaves()["leaves"]} | {"X"}
    rows, bad = [], 0
    for n, l in enumerate(open(f), 1):
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except Exception as e:
            print(f"line {n}: not JSON ({e})")
            bad += 1
            continue
        if r.get("leaf") not in ok:
            print(f"line {n}: unknown leaf {r.get('leaf')!r}")
            bad += 1
        if not r.get("src") or not r.get("topic") or not (r.get("t") or r.get("c")):
            print(f"line {n}: needs src, topic and t or c")
            bad += 1
        if r.get("c") and r.get("h") and len(r["h"]) != len(r["c"]):
            print(f"line {n}: {len(r['h'])} headings but {len(r['c'])} cells")
            bad += 1
        rows.append(r)
    miss, total = coverage(src, " ".join(s for r in rows for s in strings(r)))
    for m in miss[:60]:
        print("NOT IN OUTPUT:", m[:160])
    pct = 100 * len(miss) / max(1, total)
    print(f"{chunk}: {len(rows)} rows, {bad} format errors, {len(miss)}/{total} Rocket lines not found ({pct:.1f}%)")
    print("OK" if not bad and pct <= 3 else "NOT DONE: fix the errors; get the lines not found to 3% or less")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "chunks":
        chunks()
    elif cmd == "check-rows":
        check_rows(sys.argv[2])
    else:
        import rocketone_build as RB
        getattr(RB, cmd.replace("-", "_"))(*sys.argv[2:])
