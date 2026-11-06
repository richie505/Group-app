"""MCQs for the new current affairs (15 Oct - 4 Nov 2026): the "New Current Affairs" page of each current-affairs topic.

    python3 tools/ca_mcq.py src            write data/camcq/in/<topic>.md: the page's items, numbered
    python3 tools/ca_mcq.py check <topic>  check data/camcq/out/<topic>.json
    python3 tools/ca_mcq.py add            add every checked topic's MCQs to APPSC Complete (mcq6.json, on the page)
<topic> is the topic's row in book 6 (Current Affairs). After add: python3 tools/build_plan_mcq.py, then rebuild
Group 2 (tools/group2_build.py) so it gets them too.
"""
import hashlib
import json
import os
import re
import sys

A = "app/src/complete/assets"
D = "data/camcq"
SHAPES = {"one-liner", "NOT", "statements", "match", "assertion", "sequence"}
J = lambda p: json.load(open(p))


def text(x):
    if x.get("k") == "t":
        return " | ".join("".join(r[0] for r in c) for c in x.get("h", [])) + "\n" + "\n".join(
            " | ".join("".join(r[0] for r in c) for c in row) for row in x.get("r", []))
    return "".join(r[0] for r in x.get("x", []))


def pages():
    """(topic row, page index, topic title, page title, [item text]) for each new current-affairs page"""
    bk = J(f"{A}/book6.json")
    flat = [r for u in bk["units"] for r in u["rows"]]
    for ri, r in enumerate(flat):
        for si, s in enumerate(r["secs"]):
            if "NEW CURRENT AFFAIRS" in s["t"].upper():
                items = [text(x).strip() for x in s["b"] if x.get("k") in ("b", "p", "t") and text(x).strip()]
                yield ri, si, r["title"], s["t"], items


def src():
    os.makedirs(f"{D}/in", exist_ok=True)
    os.makedirs(f"{D}/out", exist_ok=True)
    n = 0
    for ri, si, title, pt, items in pages():
        with open(f"{D}/in/{ri}.md", "w") as f:
            f.write(f"# TOPIC {ri}: {title}\n# PAGE: {pt}\n\n")
            for k, it in enumerate(items, 1):
                f.write(f"[{k}] {it}\n\n")
        n += len(items)
        print(ri, len(items), title[:70])
    print(f"{n} items")


def problems(ri):
    items = {int(m.group(1)): m.group(2) for m in re.finditer(r"^\[(\d+)\] (.+)$", open(f"{D}/in/{ri}.md").read(), re.M)}
    p = f"{D}/out/{ri}.json"
    if not os.path.exists(p):
        return ["no output file"], []
    try:
        qs = J(p)
    except Exception as e:
        return [f"not valid JSON: {e}"], []
    out, seen, per = [], set(), {}
    for i, q in enumerate(qs):
        w = f"MCQ {i + 1}"
        for k in ("item", "shape", "s", "o", "a", "x"):
            if k not in q:
                out.append(f"{w}: no {k}")
        if any(k not in q for k in ("item", "shape", "s", "o", "a", "x")):
            continue
        its = q["item"] if isinstance(q["item"], list) else [q["item"]]
        if not all(isinstance(t, int) and t in items for t in its):
            out.append(f"{w}: item {q['item']} is not an item of the packet")
        for t in its:
            per[t] = per.get(t, 0) + 1
        if q["shape"] not in SHAPES:
            out.append(f"{w}: shape {q['shape']!r} not one of {sorted(SHAPES)}")
        if not (isinstance(q["o"], list) and len(q["o"]) == 4 and all(isinstance(o, str) and o.strip() for o in q["o"])):
            out.append(f"{w}: needs 4 non-empty options")
        elif len({o.strip().lower() for o in q["o"]}) < 4:
            out.append(f"{w}: two options are the same")
        if not (isinstance(q["a"], int) and 0 <= q["a"] <= 3):
            out.append(f"{w}: a must be 0-3")
        if len(q["s"]) < 15 or len(q["x"]) < 15:
            out.append(f"{w}: stem or explanation too short")
        st = re.sub(r"\W+", " ", q["s"].lower()).strip()
        if st in seen:
            out.append(f"{w}: same stem as another MCQ")
        seen.add(st)
        if q["shape"] == "statements" and len(re.findall(r"^\s*\d\.\s", q["s"], re.M)) not in (2, 3):
            out.append(f"{w}: a statement MCQ has 2 or 3 numbered statements (one per line)")
        if re.search(r"\b(packet|item \d|the notes|source)\b", q["s"] + " " + q["x"], re.I):
            out.append(f"{w}: mentions the packet, the notes or a source")
    for t in items:
        if t not in per and not re.fullmatch(r"\s*\W*", items[t]):
            out.append(f"item {t}: no MCQ")
    return out, qs


def check(ri):
    out, qs = problems(ri)
    keys = [q.get("a") for q in qs]
    print(f"topic {ri}: {len(qs)} MCQs, keys {[keys.count(i) for i in range(4)]}, problems {len(out)}")
    for x in out:
        print("  -", x)


def add():
    m = J(f"{A}/mcq6.json")
    added = 0
    by = {ri: (si, pt) for ri, si, _, pt, _ in pages()}
    for f in sorted(os.listdir(f"{D}/out")):
        ri = int(f.split(".")[0])
        out, qs = problems(ri)
        if out:
            print(f"topic {ri}: {len(out)} problems, left out")
            continue
        si, pt = by[ri]
        items = {int(mm.group(1)): mm.group(2) for mm in re.finditer(r"^\[(\d+)\] (.+)$", open(f"{D}/in/{ri}.md").read(), re.M)}
        rows, subs = m["rows"].setdefault(str(ri), []), m["subs"].setdefault(str(ri), [-1] * len(m["rows"].get(str(ri), [])))
        have = {q["id"] for q in rows}
        for q in qs:
            its = q["item"] if isinstance(q["item"], list) else [q["item"]]
            qid = "cn" + hashlib.sha1(f"{ri}|{q['s']}".encode()).hexdigest()[:12]
            if qid in have:
                continue
            rows.append({"id": qid, "s": q["s"], "o": q["o"], "a": q["a"], "x": q["x"], "tq": q["shape"],
                         "n": [f"{items[t]} [Oct–Nov 2026 · {pt}]" for t in its], "src": "ca"})
            subs.append(si)
            added += 1
    open(f"{A}/mcq6.json", "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    idx = J(f"{A}/index.json")
    for ri, r in enumerate(idx["books"][5]["rows"]):
        r["q"] = len(m["rows"].get(str(ri), []))
    open(f"{A}/index.json", "w").write(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    print(f"{added} MCQs added")


if __name__ == "__main__":
    {"src": lambda: src(), "check": lambda: check(int(sys.argv[2])), "add": lambda: add()}[sys.argv[1]]()
