"""RocketOne: the later steps of tools/rocketone.py (topics, check-notes, build)."""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from rocketone import W, ROWS, NOTES, leaves, coverage, strings

CA_UNITS = [
    "Andhra Pradesh - government decisions, schemes, appointments and administrative changes",
    "Andhra Pradesh - budget and Socio-Economic Survey",
    "Andhra Pradesh - projects, investments, MoUs, industry and infrastructure",
    "Andhra Pradesh - awards, GI tags, culture, sports and persons in news",
    "National - polity and governance: bills, acts, judgments, elections",
    "National - economy: Budget, Economic Survey, RBI, banking, key data",
    "National - schemes, missions, portals, apps and launches",
    "National - committees and commissions",
    "International - summits and conferences",
    "International - treaties, agreements and international organisations",
    "International - bilateral visits, defence exercises and geopolitics",
    "Science and technology - space, defence technology, health and biotech",
    "Environment - species, protected areas, energy and climate",
    "Reports and indices",
    "Awards and honours",
    "Sports",
    "Books and authors; important days, festivals and culture",
    "Persons in news - firsts, appointments and obituaries",
]
KINDS = {"b": 2, "x": 2, "h": 2, "t": 3}


def source_of(name):
    """the Rocket text a notes file must cover"""
    out = []
    for n in name.split("+"):
        if os.path.exists(f"{W}/chunks/{n}.txt"):
            out += open(f"{W}/chunks/{n}.txt").read().split("\n")
        elif os.path.exists(f"{W}/topics/{n}.jsonl"):
            for l in open(f"{W}/topics/{n}.jsonl"):
                r = json.loads(l)
                out.append(" ".join(r.get("c") or []) + " " + (r.get("t") or ""))
    return out


def check_notes(f):
    name = os.path.basename(f)[:-5]
    try:
        d = json.load(open(f))
    except Exception as e:
        print("NOT DONE: not valid JSON:", e)
        return False
    ok = {x["leaf"] for x in leaves()["leaves"]}
    bad = []
    lec = d.get("lectures")
    if not isinstance(lec, list) or not lec:
        bad.append("no lectures")
        lec = []
    for L in lec:
        t = L.get("title", "")
        if not t or len(t) > 80:
            bad.append(f"lecture title missing or over 80 characters: {t!r}")
        if "unit" in L:
            if not (isinstance(L["unit"], int) and 0 <= L["unit"] < len(CA_UNITS)):
                bad.append(f"{t}: unit must be 0-{len(CA_UNITS) - 1}")
        elif L.get("leaf") not in ok and not str(L.get("leaf", "")).startswith("X/"):
            bad.append(f"{t}: unknown leaf {L.get('leaf')!r}")
        if not L.get("parts"):
            bad.append(f"{t}: no parts")
        for P in L.get("parts") or []:
            if not P.get("t") or len(P["t"]) > 70:
                bad.append(f"{t}: part title missing or over 70 characters: {P.get('t')!r}")
            if not P.get("items"):
                bad.append(f"{t} / {P.get('t')}: no items")
            for it in P.get("items") or []:
                if not isinstance(it, list) or not it or it[0] not in KINDS or len(it) < KINDS[it[0]]:
                    bad.append(f"{t} / {P.get('t')}: bad item {json.dumps(it, ensure_ascii=False)[:90]}")
                    continue
                k = it[0]
                if k == "t":
                    if not isinstance(it[1], list) or not isinstance(it[2], list) or len(it) < 4:
                        bad.append(f"{t} / {P.get('t')}: table needs [\"t\", [headings], [[cells]...], \"src\"]")
                        continue
                    for r in it[2]:
                        if not isinstance(r, list) or len(r) != len(it[1]):
                            bad.append(f"{t} / {P.get('t')}: table row has {len(r) if isinstance(r, list) else '?'} cells, headings {len(it[1])}: {str(r)[:70]}")
                        elif any(len(c) > 260 for c in r):
                            bad.append(f"{t} / {P.get('t')}: table cell over 260 characters: {max(r, key=len)[:60]}...")
                else:
                    if not isinstance(it[1], str) or not it[1].strip():
                        bad.append(f"{t} / {P.get('t')}: empty text")
                    elif len(it[1]) > 420:
                        bad.append(f"{t} / {P.get('t')}: over 420 characters, split it: {it[1][:60]}...")
                    if k in ("b", "x") and len(it) < 3:
                        bad.append(f"{t} / {P.get('t')}: no src on: {it[1][:60]}")
    for c in d.get("corrections") or []:
        if not all(c.get(k) for k in ("title", "rocket", "src", "corrected", "checked", "kind")):
            bad.append(f"correction needs title, rocket, src, corrected, checked, kind: {str(c)[:80]}")
    for b in bad[:50]:
        print("FORMAT:", b)
    src = source_of(d.get("source") or name)
    blob = " ".join(strings(d))
    miss, total = coverage(src, blob, 0.6)
    for m in miss[:60]:
        print("NOT IN NOTES:", m[:170])
    pct = 100 * len(miss) / max(1, total)
    n = sum(len(P["items"]) for L in lec for P in L.get("parts") or [] if P.get("items"))
    print(f"{name}: {len(lec)} lectures, {n} items, {len(d.get('corrections') or [])} corrections, {len(bad)} format errors, "
          f"{len(miss)}/{total} Rocket lines not found ({pct:.1f}%)")
    good = not bad and pct <= 4
    print("OK" if good else "NOT DONE: fix the format errors; get the Rocket lines not found to 4% or less "
                            "(a line may stay unfound only if it is a repeat, a heading, or the wrong value of a correction)")
    return good


# ---------------------------------------------------------------------------------------------------------------
BOOKS = [(1, "History & Culture (Indian and Andhra Pradesh)", "History & Culture", "A"),
         (2, "Polity, Constitution, Governance, Society & International Relations", "Polity & Governance", "B"),
         (3, "Indian and Andhra Pradesh Economy", "Economy", "C"),
         (4, "Geography (India, World and Andhra Pradesh)", "Geography", "D"),
         (5, "Science, Technology and Environment", "Science, Tech & Environment", "E"),
         (6, "Current Affairs 2026", "Current Affairs", "G")]
X_BOOK = {"AP History": 1, "Indian History": 1, "Indian Polity": 2, "Indian Society": 2, "Indian Economy": 3,
          "AP Geography": 4, "General Geography": 4, "Indian Geography": 4, "World Geography": 4, "Environment": 5,
          "Disaster Management": 5, "Physics": 5, "Chemistry": 5, "Biology": 5}
MORE = "More from the Rocket Sheets"
APP = "RocketOne · Group 1 Prelims"
ASSETS = "app/src/rocketone/assets"
DATA = "data/rocketone/assets"  # the notes in the app's format (books, index): what the slides are made from


def subject_of(src):
    m = re.match(r"\s*([A-Za-z ]+?)\s*#", src or "")
    return m.group(1).strip() if m else ""


def sheet_of(src):
    m = re.search(r"#\s*(\d+)", src or "")
    return int(m.group(1)) if m else 0


def topics():
    """rows -> jobs of about 55 KB: a syllabus line (or several small ones of one syllabus item, or a part of a big one)"""
    by = {}
    for f in sorted(glob.glob(f"{ROWS}/*.jsonl")):
        for l in open(f):
            if not l.strip():
                continue
            r = json.loads(l)
            if r["leaf"] == "X":
                r["leaf"] = "X/" + (subject_of(r["src"]) or "Other")
            by.setdefault(r["leaf"], []).append(r)
    order = [x["leaf"] for x in leaves()["leaves"]]
    keys = [k for k in order if k in by] + sorted(k for k in by if k.startswith("X/"))
    os.makedirs(f"{W}/topics", exist_ok=True)
    for f in glob.glob(f"{W}/topics/*.jsonl"):
        os.unlink(f)
    jobs = []

    def write(name, rows):
        open(f"{W}/topics/{name}.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        jobs.append({"job": name, "kb": round(sum(len(json.dumps(r, ensure_ascii=False)) for r in rows) / 1000),
                     "rows": len(rows), "leaves": sorted({r["leaf"] for r in rows})})

    size = lambda rows: sum(len(json.dumps(r, ensure_ascii=False)) + 1 for r in rows)
    slug = lambda k: re.sub(r"[^A-Za-z0-9]+", "-", k).strip("-")
    pend, pitem = [], None
    for k in keys:
        rows = sorted(by[k], key=lambda r: (subject_of(r["src"]), sheet_of(r["src"])))
        item = k.split("/")[0]
        if size(rows) > 60000:
            if pend:
                write(f"{slug(pitem)}-g{len(jobs) + 1}", pend)
                pend = []
            part, n = [], 1
            for i, r in enumerate(rows):
                new_sheet = part and (subject_of(r["src"]), sheet_of(r["src"])) != (subject_of(part[-1]["src"]), sheet_of(part[-1]["src"]))
                if part and (size(part) > 55000 or (new_sheet and size(part) > 42000)):
                    write(f"{slug(k)}-p{n}", part)
                    part, n = [], n + 1
                part.append(r)
            if part:
                write(f"{slug(k)}-p{n}", part)
            continue
        if pend and (item != pitem or size(pend) + size(rows) > 60000):
            write(f"{slug(pitem)}-g{len(jobs) + 1}", pend)
            pend = []
        pend, pitem = pend + rows, item
    if pend:
        write(f"{slug(pitem)}-g{len(jobs) + 1}", pend)
    json.dump(jobs, open(f"{W}/topic-jobs.json", "w"), indent=0)
    for j in jobs:
        print(j["job"], j["kb"], "KB", j["rows"], "rows", " ".join(j["leaves"])[:90])
    print(len(jobs), "jobs;", sum(len(v) for v in by.values()), "rows;", len(keys), "syllabus lines with Rocket rows of", len(order))


# Rocket's own asides about where a line came from ("according to the source", "in cited PYQ"): not for a slide
_ASIDES = [(re.compile(x, re.I), y) for x, y in [
    (r"the source places the Kushanas as ", ""),
    (r"interpreted in source as probably", "probably"),
    (r"credited in source with", "credited with"),
    (r"\s*\(the comparison figure is truncated in the extracted text\)", ""),
    (r";?\s*exact height is not included in the extracted passage", ""),
    (r";?\s*developer not specified in the retrieved entry\.?", ""),
    (r";?\s*range not specified here", ""),
    (r"first discovered from source-mentioned fossil locality\.?", ""),
    (r"\s*\((Source )?PYQ distinction[^)]*\)", ""),
    (r"\s*\(capital PYQ:[^)]*\)", ""),
    (r"\s*\(PYQ-specific\)", ""),
    (r"\bPYQ note:", "Note:"),
    (r"Key PYQ association", "Key association"),
    (r"\s+in cited PYQ", ""),
    (r"\s+in cited convention", ""),
    (r"\bin cited (2024–25 )?data", lambda m: ("in " + m.group(1) + "data") if m.group(1) else ""),
    (r",?\s+according to (the )?source", ""),
    (r"\s+(stated )?in (the )?source('s classification| framework)?\b", ""),
    (r"\s*\(source\)", ""),
    (r";?\s*author not specified;?\s*", lambda m: "; " if m.group(0).strip().startswith(";") and m.group(0).strip().endswith(";") else ""),
    (r"^Author not specified;\s*", ""),
    (r"India's rank: not specified;\s*", ""),
    (r"^Not specified( here)?$", "—"),
]]


def tidy(t):
    for rx, y in _ASIDES:
        t = rx.sub(y, t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t[:1].upper() + t[1:] if t[:1].islower() and not t.startswith(("pH", "mRNA", "e-", "i-", "eG", "iD", "tRNA", "rRNA")) else t


def _runs(t):
    t = tidy(t)
    out = []
    for i, p in enumerate(re.split(r"\*\*(.+?)\*\*", t)):
        if p:
            out.append([p, i % 2])
    return out or [["", 0]]


def _blocks(items):
    out = []
    for it in items:
        k = it[0]
        if k == "t":
            out.append({"k": "t", "h": [_runs(c) for c in it[1]], "r": [[_runs(str(c)) for c in r] for r in it[2]], "src": it[3] if len(it) > 3 else ""})
        elif k == "h":
            out.append({"k": "h", "x": _runs(it[1].replace("**", ""))})
        else:
            if re.fullmatch(r"\*\*[^*]+:\*\*", tidy(it[1])):  # a label whose fact was only an aside
                continue
            out.append({"k": k, "x": _runs(it[1]), "src": it[2] if len(it) > 2 else ""})
    return out


def collect():
    """every lecture of the notes files, placed: (book, unit title, order key, lecture)"""
    L = leaves()
    items = {x["code"]: x["text"] for x in L["items"]}
    lorder = {x["leaf"]: i for i, x in enumerate(L["leaves"])}
    out, corr = [], []
    for f in sorted(glob.glob(f"{NOTES}/*.json")):
        d = json.load(open(f))
        job = os.path.basename(f)[:-5]
        for n, lec in enumerate(d["lectures"]):
            if "unit" in lec:
                out.append((6, CA_UNITS[lec["unit"]], (lec["unit"], lec.get("sheet", 0), n), lec, ["G/2", "G/3"]))
            elif str(lec["leaf"]).startswith("X/"):
                sub = lec["leaf"][2:]
                out.append((X_BOOK.get(sub, 1), MORE, (999, sub, job, n), lec, []))
            else:
                leaf = lec["leaf"]
                item = leaf.split("/")[0]
                book = next(b for b, _, _, p in BOOKS if leaf.startswith(p)) if leaf[0] != "G" else 6
                out.append((book, items.get(item, item), (lorder[leaf], "", job, n), lec, [leaf]))
        for c in d.get("corrections") or []:
            corr.append({**c, "job": job})
    # a lecture of one or two lines is not a lecture: those of a subject become the parts of one "Short notes" lecture
    small = [x for x in out if x[0] != 6 and sum(len(p["items"]) for p in x[3]["parts"]) <= 2]
    out = [x for x in out if not any(x is y for y in small)]
    for b in sorted({x[0] for x in small}):
        mine = sorted([x for x in small if x[0] == b], key=lambda x: (x[2][0] == 999, x[2]))
        parts = [{"t": x[3]["title"][:70], "items": [it for p in x[3]["parts"] for it in p["items"]]} for x in mine]
        leaves_ = [l for x in mine for l in x[4]]
        out.append((b, "Short notes", (998, "", "", 0), {"title": "Short notes: single facts on other syllabus lines", "parts": parts}, leaves_[:8]))
    return out, corr


def build(*args):
    """notes -> the app's books and index, the lecture PDFs (subject-wise) and the app's slide decks"""
    import shutil, zipfile
    import lecture_pdf as LP
    lecs, corr = collect()
    for d in (DATA,):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    index = {"books": []}
    for b, title, short, _ in BOOKS:
        mine = sorted([x for x in lecs if x[0] == b], key=lambda x: (x[2][0] == 999, x[2]))
        units, rows, irows = [], [], []
        for _, ut, _, lec, lv in mine:
            if not units or units[-1]["title"] != ut:
                units.append({"code": "", "title": ut, "rows": []})
            secs = [{"t": p["t"], "badges": [], "b": _blocks(p["items"])} for p in lec["parts"]]
            units[-1]["rows"].append({"codes": [], "tag": "GROUP-I", "title": lec["title"], "secs": secs})
            irows.append({"u": len(units) - 1, "title": lec["title"], "leaves": lv, "q": 0})
        json.dump({"id": b, "title": title, "short": short, "units": units}, open(f"{DATA}/book{b}.json", "w"), ensure_ascii=False)
        json.dump({"rows": {}, "units": {}, "subs": {}}, open(f"{DATA}/mcq{b}.json", "w"))
        index["books"].append({"id": b, "title": title, "short": short, "units": [{"title": u["title"]} for u in units], "rows": irows})
        print(f"{short}: {len(irows)} lectures in {len(units)} units")
    json.dump(index, open(f"{DATA}/index.json", "w"), ensure_ascii=False)
    # the corrections made (not shown on the slides)
    with open("data/rocketone/CORRECTIONS.md", "w") as f:
        f.write("# RocketOne: where the Rocket material disagreed, and what the notes say instead\n\n"
                "The slides carry only the corrected line. `rocket-vs-rocket`: two Rocket lines contradicted each other; "
                "`rocket-vs-fact`: a Rocket line was wrong against the verified fact; `unverified`: doubtful, could not be "
                "verified, Rocket's line kept.\n\n")
        for kind in ("rocket-vs-rocket", "rocket-vs-fact", "unverified"):
            cs = [c for c in corr if c["kind"] == kind]
            f.write(f"## {kind} ({len(cs)})\n\n| Lecture | Rocket says | Sheet | Notes say | Checked against |\n|---|---|---|---|---|\n")
            cell = lambda s: str(s).replace("|", "/").replace("\n", " ")
            for c in cs:
                f.write(f"| {cell(c['title'])} | {cell(c['rocket'])} | {cell(c['src'])} | {cell(c['corrected'])} | {cell(c['checked'])} |\n")
            f.write("\n")
    print(len(corr), "corrections ->", "data/rocketone/CORRECTIONS.md")
    if "data" in args:
        return
    # lecture PDFs, subject-wise (as tools/lecture_all.py), then the app's decks (tools/lecture_app.py)
    root = "out/rocketone/RocketOne-Lectures"
    shutil.rmtree("out/rocketone", ignore_errors=True)
    safe = lambda t, n=80: re.sub(r"\s+", " ", re.sub(r"[\\/:*?\"<>|]", "-", t)).strip()[:n].rstrip(" .-")
    for bk in index["books"]:
        sub = f"{root}/{bk['id']:02d} {safe(bk['short'], 50)}"
        os.makedirs(sub, exist_ok=True)
        pairs = []
        for r, info in enumerate(bk["rows"]):
            pdf = f"{sub}/{r + 1:03d} {safe(info['title'])}.pdf"
            pairs.append((LP.build(DATA, bk["id"], r, pdf, APP), pdf))
        LP.render(pairs)
        for h, _ in pairs:
            os.unlink(h)
        print(f"{bk['short']}: {len(pairs)} PDFs", flush=True)
    with zipfile.ZipFile("out/rocketone/RocketOne-Lectures.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for d, _, fs in os.walk(root):
            for x in sorted(fs):
                zf.write(os.path.join(d, x), os.path.relpath(os.path.join(d, x), "out/rocketone"))
    import lecture_app as LA
    LA.export([("r1", DATA, APP, root)], f"{ASSETS}/lec",
              {"brand": "ROCKETONE", "headline": "Group 1 Prelims, slide by slide",
               "from": "Only from the NextGen Rocket Sheets and Rocket Current Affairs 2026"})
