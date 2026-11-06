"""MCQs to the latest APPSC pattern, and every exam angle of the notes asked (APPSC Complete, one subject at a time).

    python3 tools/mcq_fix.py unmerge <book>     the 3-statement MCQs made by the 2026 merge go back to their one-fact
                                                originals (data/m3/originals.json); unmerged.json lets the app carry
                                                answers given to the merged MCQ back to them
    python3 tools/mcq_fix.py packets <book>     data/mcqfix/in/<book>-<n>.md: per topic its exam angles, its MCQs by
                                                page, the MCQs to reshape (surplus shapes) and to cut (4+ statements)
    python3 tools/mcq_fix.py check <book>-<n>   check data/mcqfix/out/<book>-<n>.json
    python3 tools/mcq_fix.py apply <book>       reshape, cut and add (every checked packet) into mcq<book>.json
Then: python3 tools/build_plan_mcq.py; python3 tools/group2_build.py; python3 tools/build_plan_mcq.py app/src/group2/assets.
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, "tools")
import reshape_plan  # noqa: E402
from reshape_plan import shape  # noqa: E402

A = "app/src/complete/assets"
D = "data/mcqfix"
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
# the latest APPSC pattern (tools/mcq_audit.py: APPSC GS papers 2023-25)
LATEST = {"one-liner": .79, "statements": .10, "NOT": .05, "match": .04, "assertion": .01, "sequence": .01}
OWN = {"", "app", "ca", "rocket"}  # the app's own MCQs; PYQs stay as the exam set them
PER = 3  # topics per packet
SHAPES = {"one-liner", "NOT", "statements", "match", "assertion", "sequence"}


def words(t):
    return {w for w in re.findall(r"[a-z][a-z\-]{3,}|\d[\d,.]*", t.lower())}


def sec_text(s):
    out = [s.get("t", "")]
    for x in s["b"]:
        if x.get("k") == "t":
            out += ["".join(r[0] for r in c) for row in [x.get("h", [])] + x.get("r", []) for c in row]
        else:
            out.append("".join(r[0] for r in x.get("x", [])))
    return " ".join(out)


def flat(b):
    return [r for u in J(f"{A}/book{b}.json")["units"] for r in u["rows"]]


def unmerge(b):
    m, merged, orig = J(f"{A}/mcq{b}.json"), J(f"{A}/merged.json"), J("data/m3/originals.json")
    un = J(f"{A}/unmerged.json") if os.path.exists(f"{A}/unmerged.json") else {}
    rows = flat(b)
    n_m = n_o = 0
    for ri, qs in m["rows"].items():
        subs = m["subs"].get(ri, [-1] * len(qs))
        secs = [words(sec_text(s)) for s in rows[int(ri)]["secs"]]
        nq, ns = [], []
        for q, sb in zip(qs, subs):
            if q["id"] not in merged:
                nq.append(q), ns.append(sb)
                continue
            olds = merged.pop(q["id"])
            un[q["id"]] = olds
            n_m += 1
            for oid in olds:
                o = orig[oid]
                w = words(o["s"] + " " + " ".join(o["o"]) + " " + o.get("x", ""))
                best = max(range(len(secs)), key=lambda i: len(w & secs[i])) if secs else sb
                nq.append(o), ns.append(best)
                n_o += 1
        m["rows"][ri], m["subs"][ri] = nq, ns
    W(f"{A}/mcq{b}.json", m)
    W(f"{A}/merged.json", merged)
    W(f"{A}/unmerged.json", un)
    # the One-liners app's links to a merged MCQ go to its one-fact MCQs
    links = J(f"{A}/mcqlinks.json")
    for k, v in links.items():
        links[k] = [y for x in v for y in (un.get(x) or [x])]
    W(f"{A}/mcqlinks.json", links)
    print(f"book {b}: {n_m} merged MCQs back to {n_o} one-fact MCQs")


def own(q):
    return q.get("src", "") in OWN


def nstat(q):
    return len(re.findall(r"^\s*(?:\d|i{1,3}|iv|v|vi)[.)]\s", q["s"], re.M))


def unit_of(row):
    return row.get("unit") or ""


def packets(b):
    os.makedirs(f"{D}/in", exist_ok=True)
    os.makedirs(f"{D}/out", exist_ok=True)
    m, rows = J(f"{A}/mcq{b}.json"), flat(b)
    reshape_plan.TARGET[b] = LATEST
    plan = {}
    order = list(range(len(rows)))
    for k in range(0, len(order), PER):
        n = k // PER
        out = [f"# PACKET {b}-{n}\n"]
        for ri in order[k:k + PER]:
            r, qs = rows[ri], m["rows"].get(str(ri), [])
            subs = m["subs"].get(str(ri), [-1] * len(qs))
            u = unit_of(r).split("-")[0]
            mine = [q for q in qs if own(q)]
            todo = reshape_plan.plan_topic(mine, b)
            cut = [q["id"] for q in mine if shape(q) == "statements" and nstat(q) >= 4 and q["id"] not in todo]
            plan.update(todo)
            c = collections.Counter(shape(q) for q in qs)
            out.append(f"\n## TOPIC {ri}: {r['title']}")
            out.append(f"Notes: data/blueprint/out/{unit_of(r)}.md   Exam angles: the **Keywords** list in "
                       f"data/blueprint/src/{u}.md   (the notes' COVERAGE line maps each angle to its sections)")
            out.append(f"Now {len(qs)} MCQs: " + ", ".join(f"{s} {c[s]}" for s in sorted(c)))
            out.append("\n### MCQs by section (section = page; [P] = a past-paper question)")
            for si, s in enumerate(r["secs"]):
                on = [q for q, sb in zip(qs, subs) if sb == si]
                out.append(f"\n#### {si + 1}. {s['t']} ({len(on)} MCQs)")
                for q in on:
                    st = re.sub(r"\s+", " ", q["s"])[:150]
                    out.append(f"- {'[P] ' if not own(q) else ''}({shape(q)}) {st}")
            if todo:
                out.append("\n### RESHAPE (rewrite each into the shape named; same facts, same topic)")
                for q in mine:
                    if q["id"] in todo:
                        opts = " / ".join(f"({i + 1}) {o}" for i, o in enumerate(q["o"]))
                        out.append(f"[{q['id']}] TARGET: {todo[q['id']]} | NOW: {shape(q)} | {q['s']} || {opts} || "
                                   f"ANS {q['a'] + 1 if isinstance(q.get('a'), int) else '?'} || WHY: {q.get('x', '')}")
            if cut:
                out.append("\n### CUT (4 or more statements: rewrite with at most 3)")
                for q in mine:
                    if q["id"] in cut:
                        opts = " / ".join(f"({i + 1}) {o}" for i, o in enumerate(q["o"]))
                        out.append(f"[{q['id']}] {q['s']} || {opts} || ANS {q.get('a', 0) + 1} || WHY: {q.get('x', '')}")
        open(f"{D}/in/{b}-{n}.md", "w").write("\n".join(out).replace("\n\n\n", "\n\n") + "\n")
    print(f"book {b}: {(len(order) + PER - 1) // PER} packets, {len(plan)} MCQs to reshape")


def problems(name):
    b, n = name.split("-")
    src = open(f"{D}/in/{name}.md").read()
    ids = set(re.findall(r"^\[([A-Za-z0-9_-]+)\]", src, re.M))
    topics = {int(t) for t in re.findall(r"^## TOPIC (\d+):", src, re.M)}
    secs = {int(t): len(re.findall(r"^#### \d+\.", part, re.M)) for t, part in
            zip(re.findall(r"^## TOPIC (\d+):", src, re.M), re.split(r"^## TOPIC \d+:.*$", src, flags=re.M)[1:])}
    p = f"{D}/out/{name}.json"
    if not os.path.exists(p):
        return ["no output file"], None
    try:
        o = J(p)
    except Exception as e:
        return [f"not valid JSON: {e}"], None
    out = []

    def mcq(q, w, need_shape=True):
        for k in ("s", "o", "a", "x") + (("shape",) if need_shape else ()):
            if k not in q:
                out.append(f"{w}: no {k}")
                return
        if not (isinstance(q["o"], list) and len(q["o"]) == 4 and all(isinstance(x, str) and x.strip() for x in q["o"])):
            out.append(f"{w}: needs 4 non-empty options")
        elif len({x.strip().lower() for x in q["o"]}) < 4:
            out.append(f"{w}: two options are the same")
        if not (isinstance(q["a"], int) and 0 <= q["a"] <= 3):
            out.append(f"{w}: a must be 0-3")
        if need_shape and q["shape"] not in SHAPES:
            out.append(f"{w}: shape {q['shape']!r}")
        if need_shape and q["shape"] == "statements" and nstat(q) not in (2, 3):
            out.append(f"{w}: a statement MCQ has 2 or 3 numbered statements, one per line")
        if need_shape and q["shape"] == "statements" and re.match(r"\s*1\.", q["s"]):
            out.append(f"{w}: a statement set opens with what it is about (\"Consider the following statements about ...:\")")
        if re.search(r"select the correct answer using the code", q["s"], re.I):
            out.append(f"{w}: drop 'Select the correct answer using the code given below'")
        if re.search(r"\b(packet|the notes|source)\b", q["s"], re.I):
            out.append(f"{w}: mentions the packet, the notes or a source")

    for i, q in (o.get("reshape") or {}).items():
        if i not in ids:
            out.append(f"reshape {i}: not an id of the packet")
        elif not q.get("same"):
            mcq(q, f"reshape {i}")
    for i in ids:
        if i not in (o.get("reshape") or {}):
            out.append(f"{i}: listed to reshape or cut but not in 'reshape'")
    for k, q in enumerate(o.get("new") or []):
        w = f"new {k + 1}"
        if q.get("topic") not in topics:
            out.append(f"{w}: topic {q.get('topic')} not in the packet")
        elif not (isinstance(q.get("sec"), int) and 1 <= q["sec"] <= secs[q["topic"]]):
            out.append(f"{w}: sec must be a section number 1-{secs[q['topic']]}")
        if not q.get("angle"):
            out.append(f"{w}: no angle (the keyword number it tests)")
        mcq(q, w)
    for t in topics:
        if not any(q.get("topic") == t for q in o.get("new") or []):
            out.append(f"topic {t}: no new MCQs (every topic gets some: angles with fewer than 2 MCQs, empty sections)")
    return out, o


def check(name):
    out, o = problems(name)
    if o:
        c = collections.Counter(q.get("shape") for q in o.get("new", []))
        print(f"{name}: {len(o.get('reshape', {}))} reshaped, {len(o.get('new', []))} new {dict(c)}, problems {len(out)}")
    else:
        print(f"{name}: problems {len(out)}")
    for x in out[:40]:
        print("  -", x)


def apply(b):
    m = J(f"{A}/mcq{b}.json")
    where = {q["id"]: (ri, k) for ri, qs in m["rows"].items() for k, q in enumerate(qs)}
    n_r = n_n = 0
    for f in sorted(os.listdir(f"{D}/out")):
        name = f[:-5]
        if not name.startswith(f"{b}-"):
            continue
        out, o = problems(name)
        if out:
            print(f"{name}: {len(out)} problems, left out")
            continue
        for i, q in o.get("reshape", {}).items():
            if q.get("same") or i not in where:
                continue
            ri, k = where[i]
            old = m["rows"][ri][k]
            new = dict(old, s=q["s"], o=q["o"], a=q["a"], x=q["x"])
            for f2 in ("xs", "xa", "tq", "n"):  # the old explanations and notes of the old shape
                if f2 in new and f2 != "n":
                    new.pop(f2)
            m["rows"][ri][k] = new
            n_r += 1
        for q in o.get("new", []):
            ri = str(q["topic"])
            qid = "f" + hashlib.sha1(f"{b}|{ri}|{q['s']}".encode()).hexdigest()[:12]
            if any(x["id"] == qid for x in m["rows"].setdefault(ri, [])):
                continue
            m["rows"][ri].append({"id": qid, "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"], "src": "app",
                                  "tq": q["shape"]})
            m["subs"].setdefault(ri, [-1] * (len(m["rows"][ri]) - 1)).append(q["sec"] - 1)
            n_n += 1
    W(f"{A}/mcq{b}.json", m)
    idx = J(f"{A}/index.json")
    for ri, r in enumerate(idx["books"][b - 1]["rows"]):
        r["q"] = len(m["rows"].get(str(ri), []))
    W(f"{A}/index.json", idx)
    print(f"book {b}: {n_r} reshaped, {n_n} new")


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"unmerge": lambda: unmerge(int(sys.argv[2])), "packets": lambda: packets(int(sys.argv[2])),
     "check": lambda: check(sys.argv[2]), "apply": lambda: apply(int(sys.argv[2]))}[cmd]()
