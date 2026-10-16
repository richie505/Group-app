"""Memory tricks for every notes page (tools/tricks_guide.md).

    python3 tools/tricks.py export [pages per batch=55]   -> work/tricks/in_NNN.md
    python3 tools/tricks.py check [NNN]
    python3 tools/tricks.py build                          -> app/src/main/assets/tricks{b}.json

An agent answers in work/tricks/out_NNN.jsonl: one line per page,
    {"page":"2:118:1","tricks":[{"type":"mnemonic","title":"..","text":"..","cue":"..","items":[..]}, ...],
     "recall":[{"q":"..","a":".."}]}
and a last line {"done":N} with N = the number of pages in the batch.
Asset: {"row:sec": {"t": [[type, title, text, cue, [items]], ...], "r": [[q, a], ...]}}.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks

A = "app/src/main/assets"
D = "work/tricks"
TYPES = ["mnemonic", "chunk", "number", "story", "contrast", "chain", "timeline", "place", "trap"]


def export(per=55):
    os.makedirs(D, exist_ok=True)
    for f in os.listdir(D):
        if f.startswith("in_"):
            os.remove(f"{D}/{f}")
    batch, n = [], 0
    for b in range(1, 7):
        rows = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        for ri, r in enumerate(rows):
            for si, s in enumerate(r["secs"]):
                md, _ = from_blocks(s["b"], inline_tables=True)
                batch.append(f"=== PAGE {b}:{ri}:{si} | {r['title']} > {s['t']}\n{md.strip()}")
                if len(batch) >= per:
                    open(f"{D}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
                    batch, n = [], n + 1
    if batch:
        open(f"{D}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
        n += 1
    print(f"{n} batches")


def pages(n):
    return re.findall(r"^=== PAGE (\d+:\d+:\d+) ", open(f"{D}/in_{n}.md").read(), re.M)


def initials(items):
    return "".join(w.strip()[0].upper() for w in items if w.strip())


def check(n):
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], []
    want, errs, got, done, seen = set(pages(n)), [], [], None, set()
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            errs.append(f"line {ln}: bad JSON ({e})"); continue
        if "done" in o:
            done = o["done"]; continue
        p = o.get("page")
        if p not in want:
            errs.append(f"line {ln}: {p} is not a page of this batch"); continue
        if p in seen:
            errs.append(f"line {ln}: {p} twice")
        seen.add(p)
        tr, rc = o.get("tricks", []), o.get("recall", [])
        if not isinstance(tr, list) or not 1 <= len(tr) <= 3:
            errs.append(f"line {ln}: {p} needs 1-3 tricks")
            tr = tr if isinstance(tr, list) else []
        if not isinstance(rc, list) or not 1 <= len(rc) <= 2:
            errs.append(f"line {ln}: {p} needs 1-2 recall questions")
            rc = rc if isinstance(rc, list) else []
        for t in tr:
            if t.get("type") not in TYPES:
                errs.append(f"line {ln}: {p} type must be one of {TYPES}")
            if not str(t.get("title", "")).strip() or not str(t.get("text", "")).strip():
                errs.append(f"line {ln}: {p} trick needs title and text")
            if t.get("type") == "mnemonic":
                cue, items = str(t.get("cue", "")), t.get("items", [])
                letters = re.sub(r"[^A-Za-z]", "", cue).upper()
                if not isinstance(items, list) or len(items) < 2:
                    errs.append(f"line {ln}: {p} mnemonic needs items (the things its letters stand for)")
                elif letters != initials(items):
                    errs.append(f"line {ln}: {p} mnemonic cue {cue!r} letters {letters} != initials of items {initials(items)}")
        for q in rc:
            if not str(q.get("q", "")).strip() or not str(q.get("a", "")).strip():
                errs.append(f"line {ln}: {p} recall needs q and a")
        got.append(o)
    missing = want - seen
    if missing:
        errs.append(f"{len(missing)} pages missing, e.g. {sorted(missing)[:3]}")
    if done != len(want):
        errs.append(f"last line must be {{\"done\":{len(want)}}}; got {done}")
    return errs, got


def build():
    out = {b: {} for b in range(1, 7)}
    bad = 0
    for f in sorted(os.listdir(D)):
        if not f.startswith("out_"):
            continue
        errs, got = check(f[4:7])
        if errs:
            bad += 1
            print(f"skip {f}: does not pass")
            continue
        for o in got:
            b, r, s = o["page"].split(":")
            out[int(b)][f"{r}:{s}"] = {
                "t": [[t["type"], t["title"].strip(), t["text"].strip(), str(t.get("cue", "")).strip(),
                       [str(x).strip() for x in t.get("items", [])]] for t in o["tricks"]],
                "r": [[q["q"].strip(), q["a"].strip()] for q in o["recall"]],
            }
    for b, m in out.items():
        open(f"{A}/tricks{b}.json", "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    print({b: len(m) for b, m in out.items()}, f"{bad} batches skipped")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(*map(int, sys.argv[2:]))
    elif cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, got = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1
                print(f"{n}: pass, {len(got)} pages")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "build":
        build()
