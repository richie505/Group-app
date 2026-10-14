"""Gap fill for pages with notes but few MCQs (2.48): restore MCQs from the bank, write none.

The pool is every MCQ in the full bank (work/mcqtrim/b<book>/orig.json, 64,729 MCQs before the trim, and
work/mcqcut/b<book>/orig.json) that is not in the app now. Each thin page gets candidates from the pool:
first the same topic (row), ranked by word overlap with the page's notes, then the closest from the book.

    python3 tools/mcq_gap.py export [min_words=40] [max_mcqs=2] [pages per batch=25] [candidates=20]
        writes work/mcqgap/in_NNN.md: each page's notes, its MCQs, and pool candidates labelled P<n>
    python3 tools/mcq_gap.py check [NNN]
    python3 tools/mcq_gap.py apply
        files every passing batch's chosen candidates under their page; updates index.json counts

An agent answers in work/mcqgap/out_NNN.jsonl, one line per page (tools/mcq_gap_guide.md):
    {"book":2,"row":70,"sub":4,"facts":[{"f":"...","by":["Q70.37","P3"]}],"add":["P3","P8"]}
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from collections import Counter
from structured_md import from_blocks
from notes_fix import text
from mcq_cut_export import question

A = "app/src/main/assets"
D = "work/mcqgap"
STOP = set("the of and to in a is was for by on with as at from that which an or be are were it its this his "
           "their under also into not all has have had".split())


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP and len(w) > 2}


def load(b):
    notes = json.load(open(f"{A}/book{b}.json"))
    return [r for u in notes["units"] for r in u["rows"]], json.load(open(f"{A}/mcq{b}.json"))


def pool(b, mcq):
    """{id: (row, mcq)} for bank MCQs not in the app."""
    live = {q["id"] for v in mcq["rows"].values() for q in v}
    out = {}
    for src in (f"work/mcqtrim/b{b}/orig.json", f"work/mcqcut/b{b}/orig.json"):
        for r, qs in json.load(open(src))["rows"].items():
            for q in qs:
                if q["id"] not in live:
                    out.setdefault(q["id"], (int(r), q))
    return out


def qtext(q):
    return " ".join([q["s"], q["o"][q["a"]], q.get("x", "")])


def export(min_words=40, max_mcqs=2, per=25, cands=20):
    os.makedirs(D, exist_ok=True)
    for f in os.listdir(D):
        if f.startswith("in_") or f == "cands.json":
            os.remove(f"{D}/{f}")
    pages, labels = [], {}
    for b in range(1, 7):
        rows, mcq = load(b)
        pl = pool(b, mcq)
        pw = {i: words(qtext(q)) for i, (_, q) in pl.items()}
        for ri, r in enumerate(rows):
            subs, qs = mcq["subs"].get(str(ri), []), mcq["rows"].get(str(ri), [])
            c = Counter(subs)
            for si, s in enumerate(r["secs"]):
                if len(" ".join(text(x) for x in s["b"]).split()) < min_words or c[si] > max_mcqs:
                    continue
                md, _ = from_blocks(s["b"], inline_tables=True)
                nw = words(md + " " + s["t"])
                score = lambda i: len(pw[i] & nw) / (1 + len(pw[i])) ** 0.5
                same = sorted((i for i, (rr, _) in pl.items() if rr == ri), key=score, reverse=True)
                same = [i for i in same if score(i) > 0][:cands]
                rest = sorted((i for i, (rr, _) in pl.items() if rr != ri), key=score, reverse=True)
                pick = same + rest[:max(0, cands - len(same)) // 2]
                js = [j for j, k in enumerate(subs) if k == si]
                part = [f"=== BOOK {b} ROW {ri} SUB {si} | {r['title']} > {s['t']}", "--- notes ---", md,
                        f"--- MCQs already on this page ({len(js)}) ---"]
                part += [question(f"Q{ri}.{j}", qs[j]) for j in js]
                part.append(f"--- candidates from the bank ({len(pick)}) ---")
                key = f"{b}:{ri}:{si}"
                labels[key] = {}
                for n, i in enumerate(pick, 1):
                    labels[key][f"P{n}"] = i
                    part.append(question(f"P{n}", pl[i][1]))
                pages.append("\n".join(part))
    for n in range(0, len(pages), per):
        open(f"{D}/in_{n // per:03d}.md", "w").write("\n\n".join(pages[n:n + per]) + "\n")
    json.dump(labels, open(f"{D}/cands.json", "w"))
    print(f"{len(pages)} pages, {(len(pages) + per - 1) // per} batches")


def pages_of(n):
    out, key = {}, None
    for line in open(f"{D}/in_{n}.md"):
        m = re.match(r"=== BOOK (\d) ROW (\d+) SUB (\d+) \|", line)
        if m:
            key = tuple(map(int, m.groups()))
            out[key] = set()
        m = re.match(r"\[((?:Q\d+\.\d+)|(?:P\d+))\]", line)
        if m:
            out[key].add(m.group(1))
    return out


def check(n):
    pg, errs, done, add = pages_of(n), [], set(), 0
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], 0
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
            key = (int(o["book"]), int(o["row"]), int(o["sub"]))
        except Exception as e:
            errs.append(f"line {ln}: bad line ({e})")
            continue
        if key not in pg:
            errs.append(f"line {ln}: page {key} not in batch")
            continue
        if key in done:
            errs.append(f"line {ln}: page {key} twice")
        done.add(key)
        adds = o.get("add", [])
        for p in adds:
            if not re.fullmatch(r"P\d+", p) or p not in pg[key]:
                errs.append(f"line {ln}: {p} is not a candidate of page {key}")
        if not o.get("facts"):
            errs.append(f"line {ln}: page {key} lists no facts")
        ok = {q for q in pg[key] if q.startswith("Q")} | set(adds)
        for f in o.get("facts", []):
            if f.get("by") and not set(f["by"]) <= ok:
                errs.append(f"line {ln}: fact cites an MCQ that is neither on the page nor added: "
                            f"{str(f.get('f'))[:50]}")
        add += len(adds)
    miss = [k for k in pg if k not in done]
    if miss:
        errs.append(f"{len(miss)} pages without a line: {miss[:6]}")
    return errs, add


def apply():
    labels = json.load(open(f"{D}/cands.json"))
    adds = {}
    for f in sorted(os.listdir(D)):
        if f.startswith("out_"):
            n = f[4:7]
            if check(n)[0]:
                print(f"skip {n}: does not pass")
                continue
            for line in open(f"{D}/{f}"):
                if line.strip():
                    o = json.loads(line)
                    adds.setdefault(o["book"], []).append(o)
    index = json.load(open(f"{A}/index.json"))
    total, gaps = 0, []
    for b, items in sorted(adds.items()):
        rows, mcq = load(b)
        pl = pool(b, mcq)
        for o in items:
            r, si = str(o["row"]), o["sub"]
            qs, subs = mcq["rows"].setdefault(r, []), mcq["subs"].setdefault(r, [])
            have = {q["id"] for q in qs}
            at = max((j + 1 for j, k in enumerate(subs) if k <= si), default=0)
            for p in o.get("add", []):
                i = labels[f"{b}:{r}:{si}"][p]
                if i in have or i not in pl:
                    continue
                qs.insert(at, pl[i][1])
                subs.insert(at, si)
                have.add(i)
                pl.pop(i)
                at += 1
                total += 1
            for fct in o.get("facts", []):
                if not fct.get("by"):
                    gaps.append(f"book {b} row {r} sub {si}: {fct.get('f')}")
        for ri, row in enumerate(index["books"][b - 1]["rows"]):
            row["q"] = len(mcq["rows"].get(str(ri), []))
        open(f"{A}/mcq{b}.json", "w").write(json.dumps(mcq, ensure_ascii=False, separators=(",", ":")))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    open(f"{D}/untested.txt", "w").write("\n".join(gaps) + "\n")
    print(f"restored {total} MCQs; {len(gaps)} important facts with no MCQ in the bank (work/mcqgap/untested.txt)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(*map(int, sys.argv[2:]))
    elif cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, add = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1
                print(f"{n}: pass, {add} restored")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "apply":
        apply()
