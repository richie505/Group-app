"""Group 2 audit (Nov 2026), applied to the built Group 2 assets before tools/group2_fit.py:
- data/g2audit/thin-N.out.jsonl: a new notes page + MCQs for each thin syllabus line (added to its host section)
- data/g2audit/ca-out.jsonl: current affairs 15-20 Nov 2026 (pages + MCQs, in the latest current-affairs section)
The notes lines found out of date (data/g2audit/facts-N.out.jsonl) are corrected in APPSC Complete's notes, so both
apps get them: python3 tools/group2_audit.py facts. The removed PYQs judged to fit after all
(data/g2audit/pyq-N.out.jsonl) are kept by tools/group2_fit.py.

    python3 tools/group2_audit.py          (run by tools/group2_build.py)
    python3 tools/group2_audit.py facts    (once, after the facts jobs: edits app/src/complete/assets/book*.json)
"""
import glob, hashlib, json, os, re, sys

G = "app/src/group2/assets"
C = "app/src/complete/assets"
J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))


def bold_runs(t):
    return [[p, i % 2] for i, p in enumerate(re.split(r"\*\*", t)) if p]


def plain(x):
    return "".join(str(r[0]) if isinstance(r, list) else str(r) for r in x)


def tag(s):
    if re.search(r"\bnot\b|\bexcept\b", s, re.I):
        return "pattern:Direct"
    return "pattern:Direct"


def add_pages():
    adds = []  # (host section title or None, page title, bullets, mcqs, leaf)
    for f in sorted(glob.glob("data/g2audit/thin-*.out.jsonl")):
        inp = {j["leaf"]: j for j in map(json.loads, open(f.replace(".out", "")))}
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                adds.append((inp.get(o["leaf"], {}).get("host_section"), o["title"], o["bullets"], o["mcqs"], o["leaf"]))
    if os.path.exists("data/g2audit/ca-out.jsonl"):
        leaf = {"Andhra Pradesh": "P4.1.3", "National": "P4.1.2", "International": "P4.1.1"}
        for l in open("data/g2audit/ca-out.jsonl"):
            if l.strip():
                o = json.loads(l)
                adds.append(("CA", o["title"], o["bullets"], o["mcqs"], leaf.get(o.get("area"), "P4.1.2")))
    # current affairs 5-18 Nov 2026: the MCQs of the "Latest" pages (Group 2 had them only in the one-liner mode)
    import ca_latest as _cal
    inv = {tuple(v): k for k, v in J("data/g2syl/rowmap.json").items()}  # Complete row -> Group 2 "b:i"
    nq0 = 0
    for (cb, cr), L0 in _cal.mcqs().items():
        k = inv.get((cb, cr))
        if not k:
            continue
        b, i = map(int, k.split(":"))
        bk, m = J(f"{G}/book{b}.json"), J(f"{G}/mcq{b}.json")
        r = [x for u in bk["units"] for x in u["rows"]][i]
        L, S = m["rows"].setdefault(str(i), []), m["subs"].setdefault(str(i), [])
        have = {q["id"] for q in L}
        leaf = {lf: t for lf, t, _ in _cal.pages().get((cb, cr), [])}
        for t, q in L0:
            if q["id"] in have:
                continue
            j = next((n for n, x in enumerate(r["secs"]) if x["t"] == t), -1)
            lf = next((lf for lf, tt, _ in _cal.pages().get((cb, cr), []) if tt == t), "P4.1.2")
            L.append(dict(q, lf=lf, tg=["pattern:Direct"]))
            S.append(j)
            nq0 += 1
        W(f"{G}/mcq{b}.json", m)
    if not adds:
        return 0, nq0
    np = nq = 0
    for b in range(1, 7):
        bk, m, idx = J(f"{G}/book{b}.json"), J(f"{G}/mcq{b}.json"), J(f"{G}/index.json")
        rows = [r for u in bk["units"] for r in u["rows"]]
        title = {r["title"]: i for i, r in enumerate(rows)}
        ca = next((i for i, r in enumerate(rows) for s in r["secs"] if "New Current Affairs: 5–14 Nov 2026" in s["t"]), None) if b == 6 else None
        changed = False
        for host, t, bullets, mcqs, leaf in adds:
            i = ca if host == "CA" else title.get(host)
            if i is None or any(s["t"] == t for s in rows[i]["secs"]):
                continue
            r = rows[i]
            r["secs"].append({"t": t, "badges": [], "b": [{"k": "b", "x": bold_runs(x)} for x in bullets], "p": r["secs"][-1].get("p", 0)})
            j = len(r["secs"]) - 1
            L, S = m["rows"].setdefault(str(i), []), m["subs"].setdefault(str(i), [])
            for q in mcqs:
                if len(q.get("o") or []) != 4 or not (0 <= q.get("a", -1) < 4):
                    continue
                L.append({"id": "g2a" + hashlib.md5((q["s"] + "|".join(q["o"])).encode()).hexdigest()[:11], "s": q["s"], "o": q["o"],
                          "a": q["a"], "x": q.get("x", ""), "lf": leaf, "tg": [tag(q["s"])]})
                S.append(j)
                nq += 1
            idx["books"][b - 1]["rows"][i]["n"] = len(r["secs"])
            idx["books"][b - 1]["rows"][i]["q"] = len(L)
            np += 1
            changed = True
        if changed:
            W(f"{G}/book{b}.json", bk)
            W(f"{G}/mcq{b}.json", m)
            W(f"{G}/index.json", idx)
    return np, nq + nq0


def facts(pattern="data/g2audit/facts-*.out.jsonl"):
    """out-of-date notes lines corrected in APPSC Complete's notes (both apps are built from them)"""
    rowmap = J("data/g2syl/rowmap.json")  # Group 2 "b:i" -> Complete [b, r]
    upd = [json.loads(l) for f in sorted(glob.glob(pattern)) for l in open(f) if l.strip()]
    upd = [u for u in upd if u.get("new") and u["new"].strip() != u["text"].strip()]
    books = {b: J(f"{C}/book{b}.json") for b in range(1, 7)}
    rows = {b: [r for u in bk["units"] for r in u["rows"]] for b, bk in books.items()}
    done = miss = 0
    for u in upd:
        b, i, j = map(int, u["page"].split(":"))
        cb, cr = rowmap.get(f"{b}:{i}", [None, None])
        hit = False
        cand = [rows[cb][cr]] if cb else []
        cand += [r for bb in rows for r in rows[bb]]  # fall back to a search of every page
        for r in cand:
            for s in r["secs"]:
                for bl in s["b"]:
                    if bl.get("k") in ("b", "x", "s") and plain(bl["x"]).strip() == u["text"].strip():
                        bl["x"] = bold_runs(u["new"])
                        hit = True
            if hit:
                break
        done += hit
        miss += not hit
    for b, bk in books.items():
        W(f"{C}/book{b}.json", bk)
    print(f"notes lines updated: {done}, not found: {miss}")


if __name__ == "__main__":
    if sys.argv[1:] == ["facts"]:
        facts()
    elif sys.argv[1:] == ["facts", "group1"]:  # Group 1's own lines: its pages are APPSC Complete's
        facts("data/g1audit/facts-*.out.jsonl")
    else:
        print("audit pages / MCQs added: %d / %d" % add_pages())
