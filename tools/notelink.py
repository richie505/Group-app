"""Each own MCQ of APPSC Complete -> the exact notes lines that state its answer (what the book icon shows).

    python3 tools/notelink.py show <book> <row>          the topic's notes, every line numbered (S:B, a table row S:B.R),
                                                         then its own MCQs (PYQs, ids "y", are left out)
    python3 tools/notelink.py check <links.json>         validate a packet's links (and its notes additions, dry)
    python3 tools/notelink.py apply <links.json>...      add the notes additions, then merge the links into
                                                         app/src/complete/assets/notelinks.json
    python3 tools/notelink.py preview <links.json>       each MCQ with the text of the lines it links

links.json:
    {"notes": [ {notes_fix append op}, ... ],             facts the notes lacked (optional; NOTES_APP=complete format)
     "links": [ {"book": 6, "id": "ca4cf9…", "lines": ["14:0:1", "14:0:2.3"]},          row:sec:block[.tablerow]
                {"book": 6, "id": "…", "lines": ["+0"]} ]}                              +k = the k-th notes addition
notelinks.json (in the app): {"<id>": ["book:row:sec:block[.tablerow]", ...]}
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from notes_fix import rows_of, text
from structured_md import from_blocks

A = "app/src/complete/assets"
OUT = f"{A}/notelinks.json"


def cell(c):
    return "".join(r[0] for r in (c if isinstance(c, list) else [[c, 0]]))


def line_text(book, ref):
    """ref "row:sec:block" or "row:sec:block.trow" -> its text (a table row with its head), or None."""
    d = book
    try:
        r, s, b = ref.split(":")
        bi, _, tr = b.partition(".")
        blk = rows_of(d)[int(r)]["secs"][int(s)]["b"][int(bi)]
        if tr != "":
            if blk["k"] != "t":
                return None
            row = blk["r"][int(tr)]
            return " | ".join(f"{cell(h)}: {cell(c)}" for h, c in zip(blk["h"], row))
        if blk["k"] == "t":
            return None  # a whole table is never a key line: link its row
        return text(blk)
    except (ValueError, IndexError, KeyError):
        return None


def show(b, r):
    d = json.load(open(f"{A}/book{b}.json"))
    row = rows_of(d)[r]
    print(f"=== NOTES {b}:{r} | {row['title']}")
    for si, s in enumerate(row["secs"]):
        print(f"## SUB {si} | {s['t']}")
        for bi, blk in enumerate(s["b"]):
            if blk["k"] == "t":
                print(f"[{r}:{si}:{bi}] TABLE head: " + " | ".join(cell(h) for h in blk["h"]))
                for ti, tr in enumerate(blk["r"]):
                    print(f"  [{r}:{si}:{bi}.{ti}] " + " | ".join(cell(c) for c in tr))
            else:
                print(f"[{r}:{si}:{bi}] {from_blocks([blk], inline_tables=True)[0]}")
    m = json.load(open(f"{A}/mcq{b}.json"))
    qs, subs = m["rows"].get(str(r), []), m["subs"].get(str(r), [])
    own = [(q, s) for q, s in zip(qs, subs or [-1] * len(qs)) if not q["id"].startswith("y")]
    print(f"\n=== OWN MCQs of {b}:{r} ({len(own)})")
    for q, s in own:
        opts = " | ".join(f"{'*' if i == q['a'] else ''}{o}" for i, o in enumerate(q["o"]))
        print(f"[{q['id']}] sub{s}\n  {q['s']}\n  {opts}\n  x: {q.get('x', '')}")


def notes_dry(ops, dry=True):
    tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(ops, tf, ensure_ascii=False); tf.close()
    r = subprocess.run([sys.executable, "tools/notes_fix.py", "apply", tf.name] + (["--dry"] if dry else []),
                       env={**os.environ, "NOTES_APP": "complete"}, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def check(path, quiet=False):
    d = json.load(open(path))
    ops, links = d.get("notes", []), d.get("links", [])
    bad = []
    if ops:
        rc, out = notes_dry(ops)
        if rc:
            bad.append(f"notes edits refused: {out}")
    books, mcqs = {}, {}
    for L in links:
        b = int(L["book"])
        bk = books.setdefault(b, json.load(open(f"{A}/book{b}.json")))
        if b not in mcqs:
            m = json.load(open(f"{A}/mcq{b}.json"))
            mcqs[b] = {q["id"] for qs in m["rows"].values() for q in qs}
        if L["id"] not in mcqs[b]:
            bad.append(f"{L['id']}: no such MCQ in book {b}")
        if L["id"].startswith("y"):
            bad.append(f"{L['id']}: PYQs are not linked")
        if not L.get("lines"):
            bad.append(f"{L['id']}: no lines")
        for ref in L.get("lines", []):
            if ref.startswith("+"):
                if not (ref[1:].isdigit() and int(ref[1:]) < len(ops)):
                    bad.append(f"{L['id']}: {ref} names no notes addition")
            elif line_text(bk, ref) is None:
                bad.append(f"{L['id']}: bad line {ref} (a whole table? link its row S:B.R)")
    ids = [L["id"] for L in links]
    bad += [f"{i}: linked twice" for i in {i for i in ids if ids.count(i) > 1}]
    if not quiet:
        print(f"{len(links)} MCQs linked, {len(ops)} notes additions" + (f"; PROBLEMS ({len(bad)}):\n  " + "\n  ".join(bad) if bad else "; all ok"))
    return bad


def resolve_new(ops):
    """After the notes additions are applied: each one's place (row:sec:block) in the notes."""
    places = []
    books = {}
    for op in ops:
        b = op["book"]
        d = books.setdefault(b, json.load(open(f"{A}/book{b}.json")))
        blocks = rows_of(d)[op["row"]]["secs"][op["sec"]]["b"]
        want = op["md"].lstrip("-* ").replace("**", "").strip()[:60]
        hit = [i for i, blk in enumerate(blocks) if blk["k"] != "t" and want[:40] in text(blk)]
        places.append(f"{op['row']}:{op['sec']}:{hit[-1]}" if hit else None)
    return places


def apply(paths):
    cur = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for p in paths:
        if check(p, quiet=True):
            print(f"{p}: refused, run check"); continue
        d = json.load(open(p))
        ops = d.get("notes", [])
        new = []
        if ops:
            rc, out = notes_dry(ops, dry=False)
            if rc:
                print(f"{p}: notes edits refused: {out}"); continue
            new = resolve_new(ops)
            with open("data/notelink/notes_added.jsonl", "a") as f:
                for o in ops:
                    f.write(json.dumps({"file": p, **o}, ensure_ascii=False) + "\n")
        n = 0
        for L in d["links"]:
            refs = []
            for ref in L["lines"]:
                if ref.startswith("+"):
                    pl = new[int(ref[1:])]
                    if pl:
                        refs.append(f"{L['book']}:{pl}")
                else:
                    refs.append(f"{L['book']}:{ref}")
            if refs:
                cur[L["id"]] = refs; n += 1
        print(f"{p}: {n} MCQs linked, {len(ops)} notes additions")
    json.dump(cur, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def preview(path):
    d = json.load(open(path))
    books, ms = {}, {}
    for L in d["links"]:
        b = int(L["book"])
        bk = books.setdefault(b, json.load(open(f"{A}/book{b}.json")))
        if b not in ms:
            m = json.load(open(f"{A}/mcq{b}.json"))
            ms[b] = {q["id"]: q for qs in m["rows"].values() for q in qs}
        q = ms[b][L["id"]]
        print(f"\n[{q['id']}] {q['s']}\n  ANSWER: {q['o'][q['a']]}")
        for ref in L["lines"]:
            t = d["notes"][int(ref[1:])]["md"] + "  (NEW)" if ref.startswith("+") else line_text(bk, ref)
            print(f"  > {ref}: {t}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "show":
        show(int(sys.argv[2]), int(sys.argv[3]))
    elif c == "check":
        sys.exit(1 if check(sys.argv[2]) else 0)
    elif c == "apply":
        apply(sys.argv[2:])
    elif c == "preview":
        preview(sys.argv[2])
