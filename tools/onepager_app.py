"""APPSC Complete and APPSC One-liners read the one-page notes (data/onepager/b<book>/r<row>.json,
tools/onepager.py) instead of Complete's full notes (kept in data/complete-full): every topic's one-pager, a
subsection per box in order (the exam corner last), and each MCQ under the box that shares most of its words
(those that match no box stay on the topic only, after the rest).

    python3 tools/onepager_app.py [complete|oneliner|all=both]

Writes into app/src/<app>/assets:
- book<b>.json: Complete's books with each topic's pages replaced by its boxes ("b:row:box").
- mcq<b>.json: the app's same MCQs in box order, each under its box (subs); index.json, planmcq.json.
- moved.json: Complete's page ids -> the topic's first box; its boxes count as read when all its old pages were;
  from the one page a topic of 2.71-2.74 ("x"), that page read = all its boxes read.
- notemoves.json: Complete's rounds and two more: own notes go to the end of the topic's last box.
- keyterms.json: key terms of the new pages (tools/build_key_terms.py).
"""
import json, math, os, re, shutil, subprocess, sys, tempfile
from collections import Counter

C, P = "data/complete-full", "data/onepager"
# the ids version each app moves its readers' marks to (once: keep it while the subsections stay one a box), and the
# version of its one page a topic before that (2.71-2.74), whose page "b:row:0" became the topic's subsections
VERSIONS = {"complete": "complete-boxes-1", "oneliner": "oneliner-boxes-1"}
ONE_PAGE = {"complete": "complete-onepager-1", "oneliner": "oneliner-onepager-1"}
STOP = set("""the a an of and or in on at to for by with from as is was are were be been its it this that these those
which who whom what when where why how not no than then also only first under over into about after before between
during per via vs all any each other more most less such same both either neither one two three his her their our
your has have had can may will would shall should must do does did done""".split())


def runs(t):
    """'**bold** text ==key fact==' -> [[text, flags]] (bold 1; a highlight is bold too)."""
    out = []
    for part in re.split(r"(\*\*.+?\*\*|==.+?==)", t):
        if not part:
            continue
        bold = part.startswith("**") or part.startswith("==")
        text = re.sub(r"\*\*|==", "", part) if bold else part
        if text:
            if out and out[-1][1] == int(bold):
                out[-1][0] += text
            else:
                out.append([text, int(bold)])
    return out or [["", 0]]


def plain(t):
    return re.sub(r"\*\*|==", "", t)


def box_blocks(b):
    """One box of a page plan as the app's blocks (its title is the subsection's title)."""
    out = []
    t = b["type"]
    if t == "bullets":
        out += [{"k": "b", "x": runs(i)} for i in b["items"]]
    elif t == "note":
        out += [{"k": "x", "x": runs(i)} for i in b["items"]]
    elif t == "table":
        out.append({"k": "t", "h": [runs(h) for h in b["head"]], "r": [[runs(c) for c in r] for r in b["rows"]]})
    elif t == "timeline":
        out += [{"k": "b", "x": [[plain(i["when"]), 1], [" — ", 0]] + runs(i["what"])} for i in b["items"]]
    elif t == "cards":
        for c in b["cards"]:
            out.append({"k": "b", "x": runs(f"**{plain(c['title'])}**")})
            out += [{"k": "s", "x": runs(l)} for l in c.get("lines", [])]
    elif t == "flow":
        n = len(b["steps"])
        out += [{"k": "b", "x": [[f"{i + 1}. ", 1]] + runs(s) + ([[" ↓", 4]] if i < n - 1 else [])} for i, s in enumerate(b["steps"])]
    elif t == "cycle":
        if b.get("centre"):
            out.append({"k": "p", "x": [["Centre: ", 4]] + runs(b["centre"])})
        out += [{"k": "b", "x": [[f"{i + 1}. ", 1]] + runs(s)} for i, s in enumerate(b["steps"])]
        out.append({"k": "n", "x": [["↻ and back to step 1", 4]]})
    elif t == "hierarchy":
        for i, l in enumerate(b["levels"]):
            x = [["▲ " if i == 0 else "▸ ", 4]] + runs(f"**{plain(l['name'])}**")
            if l.get("note"):
                x += [[" — ", 0]] + runs(l["note"])
            out.append({"k": "b", "x": x})
    return out


def box_text(b):
    parts = [b.get("title", "")]

    def walk(x):
        if isinstance(x, str):
            parts.append(x)
        elif isinstance(x, list):
            for i in x:
                walk(i)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k != "type":
                    walk(v)
    walk({k: v for k, v in b.items() if k != "title"})
    return plain(" ".join(parts))


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", t.lower()) if (len(w) > 2 or w.isdigit()) and w not in STOP]


def box_order(plan, qs):
    """Each MCQ's box: most shared words (rarer words on the page count more, the answer's twice); -1 if none."""
    bw = [Counter(words(box_text(b))) for b in plan["boxes"]]
    df = Counter(w for c in bw for w in c)
    idf = {w: math.log(1 + len(bw) / n) for w, n in df.items()}
    exam = [b["type"] == "note" for b in plan["boxes"]]
    out = []
    for q in qs:
        stem, ans = sorted(set(words(q["s"]))), sorted(set(words(q["o"][q["a"]])))  # sorted: the same sums every run
        best, where = 0.0, -1
        for i, c in enumerate(bw):
            s = sum(idf[w] for w in stem if w in c) + 2 * sum(idf[w] for w in ans if w in c)
            s *= 0.8 if exam[i] else 1  # the exam corner repeats the boxes: a content box wins a tie
            if s > best:
                best, where = s, i
        out.append(where)
    return out


def is_gap(b):
    x = b.get("x")
    return b.get("k") != "h" and isinstance(x, list) and "".join(r[0] for r in x if r and isinstance(r[0], str)).lstrip().startswith("Not in your sources")


def build(app):
    O, VERSION = f"app/src/{app}/assets", VERSIONS[app]
    moved = json.load(open(f"{C}/moved.json"))
    m, g, src, notes, expand, to_last = {}, set(), {}, {}, {}, {}
    placed = Counter()
    index = json.load(open(f"{O}/index.json"))  # the app's MCQ counts
    for bk in range(1, 7):
        book = json.load(open(f"{C}/book{bk}.json"))
        mcq = json.load(open(f"{O}/mcq{bk}.json"))
        ri = 0
        for u in book["units"]:
            for row in u["rows"]:
                plan = json.load(open(f"{P}/b{bk}/r{ri}.json"))
                new = f"{bk}:{ri}:0"
                olds = [f"{bk}:{ri}:{si}" for si in range(len(row["secs"]))]
                boxes = [f"{bk}:{ri}:{k}" for k in range(len(plan["boxes"]))]
                for si, s in enumerate(row["secs"]):
                    for k, b in enumerate(s["b"]):
                        if is_gap(b):
                            notes[f"{bk}:{ri}:{si}#{k}"] = f"{new}#-1"
                    if si:
                        notes[f"{bk}:{ri}:{si}#-1"] = f"{new}#-1"
                m.update({o: new for o in olds})
                g.update(olds)
                src.update({k: olds for k in boxes})  # read when all the old pages were
                expand[new] = boxes  # the one page of 2.71-2.74: read, all its subsections are
                to_last[f"{new}#-1"] = f"{boxes[-1]}#-1"  # own notes close the topic: its last subsection
                quote = [{"k": "p", "x": [[plain(plan["quote"]), 2]]}] if plan.get("quote") else []
                row["secs"] = [{"t": plain(b.get("title", "")), "badges": [], "p": row.get("p1", 0), "b": (quote if k == 0 else []) + box_blocks(b)}
                               for k, b in enumerate(plan["boxes"])]
                qs = mcq["rows"].get(str(ri))
                if qs:
                    where = box_order(plan, qs)
                    key = {id(q): (w if w >= 0 else len(plan["boxes"]), n) for n, (q, w) in enumerate(zip(qs, where))}
                    mcq["rows"][str(ri)] = sorted(qs, key=lambda q: key[id(q)])
                    mcq["subs"][str(ri)] = [w for w in sorted(where, key=lambda w: w if w >= 0 else len(plan["boxes"]))]  # -1: the topic only
                    placed.update("matched" if w >= 0 else "unmatched" for w in where)
                index["books"][bk - 1]["rows"][ri]["n"] = len(plan["boxes"])
                ri += 1
        json.dump(book, open(f"{O}/book{bk}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        json.dump(mcq, open(f"{O}/mcq{bk}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        print(f"{app} book {bk}: {ri} topics")
    # pages of the Prep app that Complete had moved: on to the topic's page
    m.update({k: m.get(v, v) for k, v in moved["m"].items()})
    json.dump({"v": VERSION, "m": m, "g": sorted(g | set(moved.get("g", []))), "r": src, "x": {ONE_PAGE[app]: expand}},
              open(f"{O}/moved.json", "w"), separators=(",", ":"))
    rounds = json.load(open(f"{C}/notemoves.json")) + [{"id": ONE_PAGE[app], "m": notes}, {"id": VERSION, "m": to_last}]
    json.dump(rounds, open(f"{O}/notemoves.json", "w"), separators=(",", ":"))
    open(f"{O}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", O], check=True)
    # key terms: the glossary and short forms of the main assets, read on the new pages
    with tempfile.TemporaryDirectory() as d:
        for f in ("india.json", "abbr.json"):
            shutil.copy(f"app/src/main/assets/{f}", d)
        shutil.copytree("app/src/main/assets/dict", f"{d}/dict")
        for bk in range(1, 7):
            shutil.copy(f"{O}/book{bk}.json", d)
        subprocess.run([sys.executable, "tools/build_key_terms.py", d], check=True, stdout=subprocess.DEVNULL)
        shutil.copy(f"{d}/keyterms.json", f"{O}/keyterms.json")
    print(f"{app}: MCQs under a box: {placed['matched']}, after the boxes: {placed['unmatched']}; "
          f"{len(m)} page ids moved, {len(notes)} own-note places")


if __name__ == "__main__":
    for a in VERSIONS if (sys.argv[1:] or ["all"])[0] == "all" else sys.argv[1:]:
        build(a)
