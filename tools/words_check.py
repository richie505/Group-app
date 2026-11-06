"""Checks a writer's packet of simple meanings (data/words/out/<n>.md), and builds APPSC Reader's dictionary.

    python3 tools/words_check.py <n>     (check one packet)
    python3 tools/words_check.py         (build app/src/reader/assets/simple.json from every packet)
"""
import json
import os
import re
import sys


def read(n):
    src = [l.split(" | ", 1)[0].strip() for l in open(f"data/words/in/{n}.md") if l.strip()]
    out = {}
    p = f"data/words/out/{n}.md"
    if os.path.exists(p):
        for l in open(p):
            if " | " in l:
                w, m = l.rstrip("\n").split(" | ", 1)
                out[w.strip()] = m.strip()
    return src, out


def problem(w, m):
    if m == "SKIP":
        return None
    if not m:
        return "empty"
    if "|" in m or "*" in m or "`" in m:
        return "markup or |"
    if len(m.split()) > 15:
        return f"{len(m.split())} words (15 at most)"
    if m.lower().startswith("it means"):
        return "starts with 'It means'"
    if re.search(rf"\b{re.escape(w)}\b", m, re.I):
        return "repeats the word"
    return None


def check(n):
    src, out = read(n)
    bad = 0
    missing = [w for w in src if w not in out]
    for w, m in out.items():
        if w not in src:
            print("not in the packet:", w); bad += 1
        elif (p := problem(w, m)):
            print(f"{w}: {p} -> {m}"); bad += 1
    print(f"packet {n}: {len(src)} words, {len(out)} written, missing {len(missing)}, problems {bad}"
          + (f" (first missing {missing[:5]})" if missing else ""))


def build():
    d, skip, bad, n = {}, 0, 0, 0
    while os.path.exists(f"data/words/in/{n}.md"):
        src, out = read(n)
        for w in src:
            m = out.get(w)
            if m is None:
                continue
            if m == "SKIP":
                skip += 1
            elif problem(w, m):
                bad += 1
            else:
                d[w] = m
        n += 1
    os.makedirs("app/src/reader/assets", exist_ok=True)
    json.dump(dict(sorted(d.items())), open("app/src/reader/assets/simple.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(d)} simple meanings; skipped {skip}; refused {bad}")


if __name__ == "__main__":
    check(sys.argv[1]) if len(sys.argv) > 1 else build()
