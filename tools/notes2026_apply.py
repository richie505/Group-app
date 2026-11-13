"""Puts rebuilt notes (data/notes2026/<run>/notes/row-<N>.md, structured_md format with "=== <sub-section>" lines)
into APPSC Complete, with the validated PYQ keys and the MCQ -> sub-section / notes-line mapping.

    python3 tools/notes2026_apply.py build pilot       # md -> app blocks; numbered views pilot/numbered/row-N.txt
    python3 tools/notes2026_apply.py apply pilot       # writes book1.json rows, mcq1.json (keys, x, order), notelinks

mapping (data/notes2026/<run>/mapping-*.json, merged): {"<mcq id>": {"sub": <sub-section index>, "lines": ["<sec>:<block>[.<row>]", ...]}}
keys (data/notes2026/<run>/keys-*.jsonl): validated PYQs: a / at, x, outdated line.
"""
import glob
import json
import re
import sys

sys.path.insert(0, "tools")
from structured_md import to_blocks, from_blocks  # noqa: E402
import notelink as nl  # noqa: E402

BOOK = 1
A = "app/src/complete/assets"


def parse(md):
    secs, cur = [], None
    for line in md.splitlines():
        if line.startswith("=== "):
            cur = {"t": line[4:].strip(), "lines": []}
            secs.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    out = []
    for s in secs:
        blocks = to_blocks("\n".join(s["lines"]), [])
        out.append({"t": s["t"], "badges": [], "b": blocks})
    return out


def build(run):
    d = f"data/notes2026/{run}"
    new = {}
    for f in sorted(glob.glob(f"{d}/notes/row-*.md")):
        r = int(re.findall(r"\d+", f)[-1])
        new[r] = parse(open(f).read())
    json.dump(new, open(f"{d}/new-rows.json", "w"), ensure_ascii=False)
    import os
    os.makedirs(f"{d}/numbered", exist_ok=True)
    for r, secs in new.items():
        out = [f"=== NEW NOTES row {r}"]
        for si, s in enumerate(secs):
            out.append(f"## SUB {si} | {s['t']}")
            for bi, blk in enumerate(s["b"]):
                if blk["k"] == "t":
                    out.append(f"[{si}:{bi}] TABLE head: " + " | ".join(nl.cell(h) for h in blk["h"]))
                    out += [f"  [{si}:{bi}.{ti}] " + " | ".join(nl.cell(c) for c in tr) for ti, tr in enumerate(blk["r"])]
                else:
                    out.append(f"[{si}:{bi}] {from_blocks([blk], inline_tables=True)[0]}")
        open(f"{d}/numbered/row-{r}.txt", "w").write("\n".join(out) + "\n")
        print(f"row {r}: {len(secs)} sub-sections, {sum(len(s['b']) for s in secs)} blocks")


def line_ok(secs, ref):
    try:
        s, b = ref.split(":")
        bi, _, tr = b.partition(".")
        blk = secs[int(s)]["b"][int(bi)]
        if tr:
            return blk["k"] == "t" and int(tr) < len(blk["r"])
        return blk["k"] != "t"
    except (ValueError, IndexError, KeyError):
        return False


def apply(run):
    d = f"data/notes2026/{run}"
    new = {int(k): v for k, v in json.load(open(f"{d}/new-rows.json")).items()}
    mapping = {}
    for f in glob.glob(f"{d}/mapping-*.json"):
        mapping.update(json.load(open(f)))
    keys = {}
    for f in glob.glob(f"{d}/keys-*.jsonl"):
        for l in open(f):
            if l.strip():
                x = json.loads(l)
                keys[x["id"]] = x
    bk = json.load(open(f"{A}/book{BOOK}.json"))
    rows = [r for u in bk["units"] for r in u["rows"]]
    m = json.load(open(f"{A}/mcq{BOOK}.json"))
    links = json.load(open(f"{A}/notelinks.json"))
    problems = []
    for r, secs in new.items():
        old = rows[r]
        p = old["secs"][0].get("p", old.get("p1", 0)) if old["secs"] else old.get("p1", 0)
        for s in secs:
            s["p"] = p
        old["secs"] = secs
    # every MCQ of the rebuilt rows goes to the row and sub-section the mapping names (a move between these rows is
    # allowed when another row's notes answer it); PYQs first within a sub-section
    placed = {r: [] for r in new}
    for r in new:
        for q in m["rows"][str(r)]:
            if not isinstance(q, dict):
                continue
            mp = mapping.get(q["id"])
            tr, sub = r, len(new[r]) - 1
            if mp is None:
                problems.append(f"{q['id']}: not mapped")
            else:
                tr = int(mp.get("row", r)) if int(mp.get("row", r)) in new else r
                sub = int(mp["sub"])
                if not 0 <= sub < len(new[tr]):
                    problems.append(f"{q['id']}: sub {sub} out of range for row {tr}")
                    sub = len(new[tr]) - 1
                refs = [x for x in mp.get("lines", []) if line_ok(new[tr], x)]
                if refs:
                    links[q["id"]] = [f"{BOOK}:{tr}:{x}" for x in refs[:3]]
                else:
                    links.pop(q["id"], None)
            k = keys.get(q["id"])
            if k:
                if q.get("k") == "f":
                    q["at"] = k.get("at") or q.get("at", "")
                elif isinstance(k.get("a"), int) and -1 <= k["a"] < len(q["o"]):
                    q["a"] = k["a"]
                    if k["a"] >= 0 and q.get("k") == "u":
                        q.pop("k", None)
                xx = (k.get("outdated", "").strip() + "\n" if k.get("outdated") else "") + k.get("x", "").strip()
                if xx.strip():
                    q["x"] = xx.strip()
                    q.pop("xs", None)
                    q.pop("xa", None)
            placed[tr].append((sub, q))
    idx = json.load(open(f"{A}/index.json"))
    irows = idx["books"][BOOK - 1]["rows"]
    for r, lst in placed.items():
        lst.sort(key=lambda t: (t[0], 0 if t[1]["id"].startswith("y") else 1))
        m["rows"][str(r)] = [q for _, q in lst]
        m["subs"][str(r)] = [s for s, _ in lst]
        irows[r]["q"] = len(lst)
    open(f"{A}/index.json", "w").write(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    json.dump(bk, open(f"{A}/book{BOOK}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(m, open(f"{A}/mcq{BOOK}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(links, open(f"{A}/notelinks.json", "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    import subprocess
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", A], check=True)
    print(f"rows {sorted(new)} replaced; {len(mapping)} MCQs mapped; {len(keys)} PYQ keys applied; problems: {len(problems)}")
    for p in problems[:20]:
        print("  ", p)


if __name__ == "__main__":
    {"build": build, "apply": apply}[sys.argv[1]](sys.argv[2])
