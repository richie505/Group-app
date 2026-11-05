"""APPSC Complete's full notes, cut down to what its MCQs test: each line (bullet, table row, exam corner) stays only
when it shares the facts of an MCQ of its topic (its question, answer, explanation, statements; for the 3-statement
MCQs also the one-fact MCQs they were made from). Headings stay above lines that stay. A page with nothing left
says so. The whole notes are kept unchanged in data/notes-archive/book*.json (the first run copies them there).

    python3 tools/trim_notes.py           (reads the archive, writes app/src/complete/assets/book*.json)
"""
import json, os, re, shutil, sys

A = "app/src/complete/assets"
ARCH = "data/notes-archive"
STOP = set("""the and for with from that this which were was are is its their has have been into about what who whom when
where how not one two also only such than then them they there these those other more most some any all each both
under over after before between during within upon onto by of in on to as at be it an or a india indian state states
andhra pradesh government first second third main known called following correct statement statements consider select
answer code codes given above below option options""".split())
EMPTY = [{"k": "n", "x": [["No MCQ asks about this page: nothing here to learn for the MCQs.", 4]]}]


def toks(t):
    return {w.strip(".,").replace(",", "") for w in re.findall(r"[a-z][a-z\-]{2,}|\d[\d,.]*", t.lower())} - STOP


def strong(w):
    return any(c.isdigit() for c in w) or len(w) >= 7


def text(runs):
    return "".join(r[0] for r in runs)


def main():
    if not os.path.exists(f"{ARCH}/book1.json"):
        for b in range(1, 7):
            shutil.copy(f"{A}/book{b}.json", f"{ARCH}/book{b}.json")
    originals = json.load(open("data/m3/originals.json")) if os.path.exists("data/m3/originals.json") else {}
    kept_all = total_all = 0
    for b in range(1, 7):
        book = json.load(open(f"{ARCH}/book{b}.json"))
        rows = json.load(open(f"{A}/mcq{b}.json"))["rows"]
        ri = 0
        for u in book["units"]:
            for r in u["rows"]:
                facts = []
                for q in rows.get(str(ri), []):
                    parts = [q["s"], q.get("x", "")] + [o for o in q["o"]] + q.get("n", []) + q.get("xa", [])
                    for oid in q.get("of", []):
                        o = originals.get(oid, {})
                        parts += [o.get("s", ""), o.get("x", "")] + ([o["o"][o["a"]]] if o and 0 <= o.get("a", -1) < len(o["o"]) else [])
                    f=set()
                    for p in parts:
                        f |= toks(p)
                    facts.append(f)

                def keep(t):
                    tt = toks(t)
                    need = min(3, len(tt))  # a short line ("Global South") needs all its words
                    if need == 0:
                        return False
                    for f in facts:
                        hit = tt & f
                        if len(hit) >= need and (len(hit) >= 2 or strong(next(iter(hit)))) or (
                                len(hit) >= 2 and any(strong(w) for w in hit)):
                            return True
                    return False

                for s in r["secs"]:
                    bl = s["b"]
                    keepset = set()
                    for i, blk in enumerate(bl):
                        if blk.get("k") not in ("h", "n", "t") and keep(text(blk.get("x", []))):
                            keepset.add(i)
                    for i, blk in enumerate(bl):
                        if blk.get("k") == "s" and i in keepset:
                            j = i - 1
                            while j >= 0 and bl[j].get("k") == "s":
                                j -= 1
                            if j >= 0 and bl[j].get("k") == "b":
                                keepset.add(j)
                    out, pend = [], None
                    for i, blk in enumerate(bl):
                        k = blk.get("k")
                        if k == "h":
                            pend = blk
                            continue
                        if k == "n":  # sources line, grey notes: not for MCQs
                            continue
                        if k == "t":
                            rws = [row for row in blk["r"] if keep(" ".join(text(c) for c in row))]
                            total_all += len(blk["r"])
                            if not rws:
                                continue
                            kept_all += len(rws)
                            nb = dict(blk, r=rws)
                        else:
                            total_all += 1
                            if i not in keepset:
                                continue
                            kept_all += 1
                            nb = blk
                        if pend is not None:
                            out.append(pend)
                            pend = None
                        out.append(nb)
                    s["b"] = out or EMPTY
                    s.pop("cov", None)
                ri += 1
        open(f"{A}/book{b}.json", "w").write(json.dumps(book, ensure_ascii=False, separators=(",", ":")))
    print(f"lines kept {kept_all:,} of {total_all:,} ({kept_all * 100 // max(1, total_all)}%)")




def empty_pages():
    """app/src/complete/assets/empty.json: the pages with nothing for the MCQs, in the MCQ notes ("mcq") and the trimmed
    full notes ("full"). The app hides them and counts them as read, so a topic can still be finished."""
    out = {}
    for key, path in (("mcq", "app/src/complete2/assets/book{}.json"), ("full", A + "/book{}.json")):
        ids = []
        for b in range(1, 7):
            ri = 0
            for u in json.load(open(path.format(b)))["units"]:
                for r in u["rows"]:
                    for si, s in enumerate(r["secs"]):
                        bl = s["b"]
                        if len(bl) == 1 and bl[0].get("k") == "n" and bl[0]["x"][0][0].startswith("No MCQ"):
                            ids.append(f"{b}:{ri}:{si}")
                    ri += 1
        out[key] = ids
    # a topic's page count is the larger of the two notes' (the MCQ notes add "More from this topic's MCQs" to some):
    # a page one set lacks is listed as empty there, so it counts as read
    idx = json.load(open(f"{A}/index.json"))
    for b in range(1, 7):
        counts = {}
        for key, path in (("mcq", "app/src/complete2/assets/book{}.json"), ("full", A + "/book{}.json")):
            counts[key] = [len(r["secs"]) for u in json.load(open(path.format(b)))["units"] for r in u["rows"]]
        for ri, row in enumerate(idx["books"][b - 1]["rows"]):
            n = max(counts["mcq"][ri], counts["full"][ri])
            row["n"] = n
            for key in ("mcq", "full"):
                out[key] += [f"{b}:{ri}:{si}" for si in range(counts[key][ri], n)]
    open(f"{A}/index.json", "w").write(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    open(f"{A}/empty.json", "w").write(json.dumps(out, separators=(",", ":")))
    print("empty pages:", {k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()
    empty_pages()
