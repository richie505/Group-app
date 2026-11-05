"""APPSC Complete's MCQ notes in simple English: puts the writers' lines (data/simple/out/<n>.md) back into the notes.

Each line is checked against the original: the same bold terms (word for word), the same numbers, never more words,
no new bold. A line that fails keeps its original. The originals stay unchanged in app/src/complete2/assets; the
simple notes are written to app/src/complete/mcqnotes/book*.json (APPSC Complete's "MCQ notes").

    python3 tools/simple_build.py --check <n>     (a writer's check of one packet)
    python3 tools/simple_build.py                 (build the notes from every packet written)
"""
import collections
import json
import os
import re
import sys

SRC = "app/src/complete2/assets"
DST = "app/src/complete/mcqnotes"
BOLD = re.compile(r"\*\*(.+?)\*\*")
NUM = re.compile(r"\d[\d,.]*")


def words(t):
    return len(re.findall(r"[^\s—–→=|;:,()]+", t.replace("**", "")))


def runs(t):
    out, pos = [], 0
    for m in BOLD.finditer(t):
        if m.start() > pos:
            out.append([t[pos:m.start()], 0])
        out.append([m.group(1), 1])
        pos = m.end()
    if pos < len(t):
        out.append([t[pos:], 0])
    return out


def md(rs):
    return "".join(f"**{t}**" if s == 1 else t for t, s, *_ in rs)


def problem(old, new):
    """why a rewritten line is not allowed, or None"""
    if new.count("**") % 2:
        return "unbalanced **"
    if collections.Counter(BOLD.findall(old)) != collections.Counter(BOLD.findall(new)):
        return "bold changed"
    plain = lambda t: BOLD.sub(" ", t)
    if collections.Counter(n.rstrip(".,") for n in NUM.findall(plain(old))) != \
            collections.Counter(n.rstrip(".,") for n in NUM.findall(plain(new))):
        return "a number changed"
    if words(new) > words(old):
        return f"longer ({words(old)} -> {words(new)} words)"
    if not new.strip():
        return "empty"
    return None


def read(n):
    src = {}
    for line in open(f"data/simple/in/{n}.md"):
        if line.startswith("L"):
            i, t = line.rstrip("\n").split(" ", 1)
            src[i] = t
    out = {}
    path = f"data/simple/out/{n}.md"
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("L") and " " in line:
                i, t = line.rstrip("\n").split(" ", 1)
                out[i] = t.strip()
    return src, out


def check(n):
    src, out = read(n)
    bad = 0
    missing = [i for i in src if i not in out]
    for i, t in out.items():
        if i not in src:
            print("extra", i)
            bad += 1
        elif t != "=":
            p = problem(src[i], t)
            if p:
                bad += 1
                print(f"{i}: {p}\n  was: {src[i]}\n  now: {t}")
    print(f"packet {n}: {len(src)} lines, {len(out)} written, missing {len(missing)}, problems {bad}"
          + (f" (first missing {missing[:3]})" if missing else ""))


# facts corrected by hand (not by the writers, who keep every fact): line id -> the corrected line
FIXES = {
    # Babur is buried in Kabul; Humayun's Tomb is in Delhi (the PYQ's key was wrong)
    "L1:128:8:4": "**★ **Mughal emperor with no mausoleum in India — **Babur** (buried in Kabul)",
}


def build():
    new, kept, failed = {}, collections.Counter(), collections.Counter()
    n = 0
    while os.path.exists(f"data/simple/in/{n}.md"):
        src, out = read(n)
        for i, t in out.items():
            if i not in src or t == "=":
                continue
            p = problem(src[i], t)
            if p:
                failed[p.split(" (")[0]] += 1
            else:
                new[i] = t
        n += 1
    new.update(FIXES)
    os.makedirs(DST, exist_ok=True)
    total = changed = w0 = w1 = 0
    for b in range(1, 7):
        bk = json.load(open(f"{SRC}/book{b}.json"))
        ri = 0
        for u in bk["units"]:
            for r in u["rows"]:
                for si, s in enumerate(r["secs"]):
                    for bi, x in enumerate(s["b"]):
                        if x.get("k") in ("b", "s") and "x" in x:
                            total += 1
                            old = md(x["x"])
                            t = new.get(f"L{b}:{ri}:{si}:{bi}")
                            w0 += words(old)
                            if t:
                                x["x"] = runs(t)
                                changed += 1
                                w1 += words(t)
                            else:
                                w1 += words(old)
                ri += 1
        open(f"{DST}/book{b}.json", "w").write(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    print(f"{changed:,} of {total:,} lines in simple English; words {w0:,} -> {w1:,}; refused {dict(failed)}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        check(sys.argv[2])
    else:
        build()
