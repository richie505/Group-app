"""Adds the previous-year questions to the apps' MCQs, each under its topic and subsection (tools/pyq_place.py).

    python3 tools/pyq_apply.py

Prep (app/src/main) uses data/pyq/place-prep.json; APPSC Complete data/pyq/place-complete.json.
(APPSC One-liners is left as it is: the user dropped that app.) Within a subsection the PYQs come first (APPSC,
then UPSC, then the state-PSC ones), then the app's own MCQs. A PYQ's id is "y" + a hash of its source id, the
same in every app, so a backup carries its answers across. Running it again first takes out the PYQs it added.
Questions with no published key are added unscored ("k": "u").
"""
import hashlib, json, os, re, subprocess, sys

sys.path.insert(0, "tools")
from pyq_place import cleaned, usable, bank  # noqa: E402

OTHER = re.compile(r"\b(?:in|of|from|to|at)\s+(?:the\s+)?(?:state of\s+)?(?:Uttar Pradesh|U\.\s?P\.|UP|Bihar|Madhya Pradesh|M\.\s?P\.|"
                   r"Rajasthan|Chhattisgarh|Uttarakhand|Uttaranchal|Jharkhand|Haryana|Himachal Pradesh)\b")


NEWS = re.compile(r"\b(?:film|movie|award(?:ed)?|prize|champion(?:ship)?|games|olympics?|cup|medal|CEO|summit|conference|elected|"
                  r"appointed|sworn|won|winner|tournament|festival|released|launched|unveiled|recently|book titled|author of the book)\b", re.I)


def stale(q):
    """Old news (an award, a summit, a film of 2004): not this year's current affairs and no syllabus fact."""
    years = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", q["s"])]
    return bool(years) and max(years) < 2022 and bool(NEWS.search(q["s"]))


def broken(q):
    """OCR leftovers in the options: the same option twice (numbers lost), the next question run in."""
    norm = [re.sub(r"[^a-z0-9]+", "", o.lower()) for o in q["o"]]
    return len(set(norm)) < 4 or any(re.search(r"consider the following|which of the following|^\W*$", o, re.I) for o in q["o"])


def keep(q, conf):
    """On the syllabus: close enough to a topic; not another state's own affairs; Current Events only if it is
    about a static topic (old news is not this year's current affairs)."""
    f = q["file"]
    if not usable(q) or broken(q) or (stale(q) and conf < 0.3):
        return False
    if f.startswith("Ghatna"):
        if OTHER.search(q["s"]):
            return False
        return conf >= (0.3 if "Current Events" in f else 0.15)
    return conf >= (0.15 if f.startswith("UPSC") else 0.10)


def rank(q):
    f = q["file"]
    return 0 if f.startswith(("APPSC", "AP History", "by")) else 1 if f.startswith("UPSC") else 2


def label(q):
    f, exam, year = q["file"], q.get("exam", ""), q.get("year", "")
    if q.get("new"):  # read from Drive's scans: its exam is written out ("APPSC Group-II 2011")
        return re.sub(r"\s*\(held[^)]*\)", "", exam)[:60]
    if f.startswith("UPSC"):
        return f"UPSC CSE Prelims {year}".strip()
    if f.startswith("Ghatna"):
        first = exam.split(";")[0].strip()
        more = exam.count(";")
        return (first if first and "Ghatna" not in first else "State PSC") + (f" +{more} more" if more else "")
    if f.startswith("AP History"):
        return "APPSC AP History PYQ"
    if f.startswith("APPSC Group-1"):
        return "APPSC Group-1 PYQ"
    if f.startswith("APPSC Group-2"):
        return "APPSC Group-2 PYQ"
    m = re.match(r"APPSC - (\d{4})-\d+ (.*)", exam)
    if m:
        name = re.sub(r"\s+in (?:A\.?P\.?|Andhra).*|\s*\($|\s+Vide.*", "", m.group(2)).strip()
        return re.sub(r"[\s\-–(,]+$", "", f"APPSC {m.group(1)} {name}"[:60])
    p = q.get("paper", "")
    y = re.search(r"(20\d\d|19\d\d)", p)
    return f"APPSC {y.group(1) + ' ' if y else ''}{'Group-1' if 'G1' in p or 'Group-1' in p or 'group 1' in p.lower() else 'Group-2' if 'G2' in p or 'Group2' in p else ''}".strip()


def stem(s):
    """Statements, lists and assertion/reason on lines of their own."""
    s = re.sub(r"\s+(Statement\s*\(?(?:A|I|1)\)?\s*:|Assertion\s*\(A\)|Reason\s*\(R\)|Assertion\s*:|Reason\s*:|List[- ]I{1,2}\b)", r"\n\1", s)
    for marks in (["1", "2", "3", "4", "5", "6"], ["I", "II", "III", "IV", "V", "VI"], ["A", "B", "C", "D", "E"], ["a", "b", "c", "d", "e"]):
        pats = [re.compile(rf"(?<=\s)\(?{m}[.)]\s") for m in marks]
        if pats[0].search(s) and pats[1].search(s):
            for p in pats:
                s = p.sub(lambda x: "\n" + x.group(0), s, count=1)
    s = re.sub(r"\s+(Which of the (?:above|statements|following (?:statements?|pairs?) (?:given above )?)|Select the correct|"
               r"How many of the|Choose the correct|Codes?\s*:)", r"\n\1", s) if "\n" in s else s
    return re.sub(r"[ \t]+\n", "\n", s).strip()


def to_mcq(q):
    o = {"id": "y" + hashlib.sha1(q["id"].encode()).hexdigest()[:11], "s": stem(q["s"]), "o": q["o"], "a": q["a"],
         "src": label(q)}
    if q.get("x"):
        o["x"] = q["x"][:1500]
    if q["a"] < 0:
        o["k"], o["a"] = "u", -1
    if rank(q) == 0:
        o["ap"] = 1
    return o


def apply(app, layout):
    A = f"app/src/{app}/assets"
    pyq = {q["id"]: q for q in map(cleaned, bank())}
    place = json.load(open(f"data/pyq/place-{layout}.json"))["place"]
    bad = json.load(open("data/pyq/bad.json")) if os.path.exists("data/pyq/bad.json") else {}  # the audit's garbled / misfiled ones
    import glob
    bad = set(bad) | {i for f in glob.glob("data/pyq/apt/out-*.json") for i in json.load(open(f))} | {x["id"] for f in glob.glob("data/relevance/pyq-*.json") for x in json.load(open(f))["exclude"]}  # aptitude ones (data/pyq/apt)
    # only PYQs a person or the audit has read: those already in the apps (data/pyq/audited.json), the papers read
    # from Drive's scans, and the APPSC questions given their official key (both audited, data/pyq/aph/out-*.json)
    audited = set(json.load(open("data/pyq/audited.json")))
    by_row = {}
    for pid, (b, r, sub, conf) in place.items():
        q = pyq[pid]
        if keep(q, conf) and to_mcq(q)["id"] not in bad and (to_mcq(q)["id"] in audited or (rank(q) == 0 and (q.get("new") or "keyed" in q))):
            by_row.setdefault((b, r), []).append((sub, rank(q), pid))
    index = json.load(open(f"{A}/index.json"))
    added = 0
    for b in range(1, 7):
        mcq = json.load(open(f"{A}/mcq{b}.json"))
        rows = index["books"][b - 1]["rows"]
        for ri in range(len(rows)):
            k = str(ri)
            qs, subs = mcq["rows"].get(k, []), mcq["subs"].get(k, [])
            own = [(s, q) for q, s in zip(qs, subs or [-1] * len(qs)) if not q["id"].startswith("y")]
            new = [(s, to_mcq(pyq[p])) for s, _, p in sorted(by_row.get((b, ri), []))]
            added += len(new)
            order = sorted(set(s for s, _ in own + new), key=lambda s: (s < 0, s))
            merged = [(s, q) for s in order for s, q in [x for x in new if x[0] == s] + [x for x in own if x[0] == s]]
            if merged:
                mcq["rows"][k] = [q for _, q in merged]
                mcq["subs"][k] = [s for s, _ in merged]
            rows[ri]["q"] = len(merged)
        json.dump(mcq, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    if app != "main":
        subprocess.run([sys.executable, "tools/build_plan_mcq.py", A], check=True)
    print(f"{app}: {added} PYQs added")


if __name__ == "__main__":
    apply("main", "prep")
    apply("complete", "complete")
