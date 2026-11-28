"""Reads the Unlock IAS question-paper PDFs (downloaded 28 Nov 2026 from unlockias.in: UPSC Prelims 1995-2026 with
answers; NDA, CDS, CAPF, EPFO and State PCS prelims papers, question paper only) into data/pyq/unlockias/out/<paper>.jsonl,
one question per line, in the form tools/pyq_add_new.py reads.

- English papers only (the Hindi / Marathi copies and the descriptive Mains papers are left out).
- UPSC year papers carry "Answer: (x)" after each question. The other PDFs print no key: the key is taken from the
  paper's own page on unlockias.in (it lists every question with "Answer: B: <option text>"); the page is saved in
  data/pyq/unlockias/pages/. The option is matched by its text first, then by its letter; where neither is certain
  the question is written without a key (a = -1). No explanation is copied.
- The four APPSC Group-I Prelims papers are skipped: the app has them from data/appscpapers/ with APPSC's final keys.
- English-language sections (NDA Part A, EPFO / CAPF grammar and comprehension) are left out.

    python3 tools/unlockias_parse.py <folder with pyq/ other-exam/ state-pcs/> [--no-fetch]
"""
import glob, html, json, os, re, sys, time, urllib.request

import fitz

SRC = sys.argv[1]
FETCH = "--no-fetch" not in sys.argv
OUT, PAGES = "data/pyq/unlockias/out", "data/pyq/unlockias/pages"
os.makedirs(OUT, exist_ok=True); os.makedirs(PAGES, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
norm = lambda t: re.sub(r"[^a-z0-9]+", "", str(t).lower())
JUNK = re.compile(r"^(UnlockIAS\b.*|www\.unlockias.*|\d+ / \d+|UPSC (19|20)\d\d)$")
OPT = re.compile(r"^\(([a-eA-E1-5])\)\s*(.*)$")
ENGLISH = re.compile(
    r"opposite in meaning|similar in meaning|nearest in meaning|synonym|antonym|underlined|No error|part of the sentence|"
    r"parts? of (a|the) sentence|jumbled|rearrange|sentence|fill in the blank|blank|idiom|phrase|preposition|passage|"
    r"______|\bspelt\b|spelling|one[- ]word|correct form|voice\b|indirect speech|direct speech|\barticle\b.*\bfill|"
    r"cloze|comprehension|ordering of words|grammatical", re.I)
MARK = re.compile(r"^(\d{1,2}[.)]|[IVXivx]{1,4}[.)]|\([ivxIVX]{1,4}\)|[A-Ea-e][.)]|List|Statement|Assertion|Reason|Codes?\b|"
                  r"Select|Which|Choose|How many|Reason|\(A\)|\(R\))")
NAMES = [(r"^upsc-prelims-(\d{4})$", "UPSC CSE Prelims {0}"), (r"^nda-(\d{4})-(i-ii|ii|i)-", "NDA {1} {0}"),
         (r"^cds-(\d{4})-(ii|i)-", "CDS {1} {0}"), (r"^capf-(\d{4})-", "CAPF (AC) {0}"),
         (r"^epfo-apfc-(\d{4})-", "UPSC EPFO APFC {0}"), (r"^epfo-eo-ao-(\d{4})-", "UPSC EPFO EO/AO {0}"),
         (r"^epfo-(\d{4})-", "UPSC EPFO {0}"), (r"^bpsc-(\d+)(?:st|nd|rd|th)-cce-(re-exam-)?(\d{4})-", "BPSC {0}th CCE (Pre) {2}"),
         (r"^gpsc-(\d{4})-", "GPSC (Pre) {0}"), (r"^hcs-(\d{4})-", "Haryana HCS (Pre) {0}"),
         (r"^kerala-kas-(\d{4})-", "Kerala KAS (Pre) {0}"), (r"^kpsc-(\d{4})-", "Karnataka KPSC (Pre) {0}"),
         (r"^manipur-psc-(\d{4})-", "Manipur PSC (Pre) {0}"), (r"^mizoram-psc-(\d{4})-", "Mizoram PSC (Pre) {0}"),
         (r"^mppsc-(\d{4})-", "M.P.P.C.S. (Pre) {0}"), (r"^mpsc-.*prelims-(\d{4})-", "Maharashtra MPSC (Pre) {0}"),
         (r"^nagaland-psc-(\d{4})-", "Nagaland PSC (Pre) {0}"), (r"^ras-(\d{4})-", "R.A.S./R.T.S. (Pre) {0}"),
         (r"^tnpsc-(\d{4})-", "TNPSC Group-I (Pre) {0}"), (r"^ukpsc-(\d{4})-", "Uttarakhand P.C.S. (Pre) {0}"),
         (r"^uppsc-(\d{4})-", "U.P.P.C.S. (Pre) {0}"), (r"^wbcs-(\d{4})-", "W.B.C.S. (Pre) {0}")]


def exam_name(slug):
    for rx, fmt in NAMES:
        m = re.match(rx, slug)
        if m:
            g = [x.upper() if x and re.fullmatch(r"[i-]+", x) else x for x in m.groups()]
            return fmt.format(*g).replace("I-II", "I & II"), re.search(r"(19|20)\d\d", slug).group(0)
    return slug, (re.search(r"(19|20)\d\d", slug) or [""])[0]


def join(lines):
    out = []
    for l in lines:
        if out and len(out[-1].split("\n")[-1]) >= 78 and not MARK.match(l):
            out[-1] += " " + l
        elif out and not MARK.match(l) and " | " not in l and " | " not in out[-1].split("\n")[-1] and not out[-1].rstrip().endswith((":", "?", ".", ";")):
            out[-1] += " " + l
        else:
            out.append(l)
    return "\n".join(out).strip()


def parse(pdf):
    """-> (url, [{n, s, o, letters, ans}])"""
    text = "\n".join(p.get_text() for p in fitz.open(pdf))
    url = re.search(r"https://www\.unlockias\.in/[a-z0-9-]+", text[:1500].replace("\n", ""))
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if l and not JUNK.match(l)]
    qs, cur = [], None
    for l in lines:
        m = re.match(r"^Q(\d{1,4})\.\s*(.*)$", l)
        if m and (cur is None or cur["n"] < int(m.group(1)) <= cur["n"] + 40):  # numbers can skip (dropped questions)
            cur = {"n": int(m.group(1)), "L": [m.group(2)] if m.group(2) else [], "ans": ""}
            qs.append(cur)
            continue
        if cur is None:
            continue
        a = re.match(r"^Answer:\s*\(([a-eA-E1-5])\)", l)
        if a:
            cur["ans"] = a.group(1); cur["done"] = True
            continue
        if cur.get("done"):
            continue  # the next question's subject line
        cur["L"].append(l)
    out = []
    for q in qs:
        L = q["L"]
        # the option block: the last run of (a)(b)(c)(d)[(e)] markers in order
        best = None
        for series in ("abcde", "ABCDE", "12345"):
            idx = [i for i, l in enumerate(L) if OPT.match(l) and OPT.match(l).group(1) == series[0]]
            for i0 in reversed(idx):
                pos, want = [i0], 1
                for i in range(i0 + 1, len(L)):
                    m = OPT.match(L[i])
                    if m and want < 5 and m.group(1) == series[want]:
                        pos.append(i); want += 1
                if len(pos) >= 4 and (best is None or i0 > best[1][0]):
                    best = (series, pos)
                if len(pos) >= 4:
                    break
        if not best:
            continue
        series, pos = best
        opts = []
        for k, i in enumerate(pos):
            end = pos[k + 1] if k + 1 < len(pos) else len(L)
            opts.append(join([OPT.match(L[i]).group(2)] + L[i + 1:end]).replace("\n", " ").strip())
        stem = join(L[:pos[0]])
        if len(opts) == 5 and not opts[4]:
            opts = opts[:4]
        out.append({"n": q["n"], "s": stem, "o": opts, "series": series, "ans": q["ans"]})
    return (url.group(0) if url else ""), out


def page_answers(slug, url):
    """{n: (letter, text)} from the paper's page on the site"""
    f = f"{PAGES}/{slug}.html"
    if not os.path.exists(f):
        if not FETCH or not url:
            return {}
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print("  page not read:", url, str(e)[:60]); return {}
        open(f, "wb").write(data); time.sleep(0.5)
    t = open(f, encoding="utf8", errors="replace").read()
    t = t[:t.find("self.__next_f")] if "self.__next_f" in t else t
    ans = {}
    for m in re.finditer(r">Q(?:<!-- -->)?(\d{1,4})</span>(.*?)</li>", t, re.S):
        a = re.search(r"Answer(?:<!-- -->)?: (?:<!-- -->)?\(?([A-Ea-e1-5])\)?(?:<!-- -->)?(?::\s*(.*?))?</span>", m.group(2), re.S)
        if a:
            ans[int(m.group(1))] = (a.group(1).upper(), html.unescape(re.sub(r"<[^>]+>", "", a.group(2) or "")).strip())
    return ans


total = keyed = 0
for folder in ("pyq", "other-exam", "state-pcs"):
    for pdf in sorted(glob.glob(os.path.join(SRC, folder, "*.pdf"))):
        slug = os.path.basename(pdf)[:-4]
        if re.search(r"hindi|marathi", slug) or slug.startswith("appsc-") or (folder == "pyq" and not re.match(r"upsc-prelims-\d{4}$", slug)):
            continue
        url, qs = parse(pdf)
        exam, year = exam_name(slug)
        web = {} if folder == "pyq" else page_answers(slug, url)
        rows, nk, eng = [], 0, 0
        for q in qs:
            if folder != "pyq" and (ENGLISH.search(q["s"]) or (slug.startswith("nda-") and q["n"] <= 50)):
                eng += 1
                continue
            a = -1
            if q["ans"]:
                a = q["series"].find(q["ans"]) if q["ans"] in q["series"] else "abcde".find(q["ans"].lower())
            elif q["n"] in web:
                letter, txt = web[q["n"]]
                byt = [i for i, o in enumerate(q["o"]) if txt and norm(o) == norm(txt)]
                byl = "ABCDE".find(letter) if letter in "ABCDE" else "12345".find(letter)
                if len(byt) == 1 and byl != byt[0] and byl < len(q["o"]):
                    a = -1          # the page's letter and its option text disagree: no key
                elif len(byt) == 1:
                    a = byt[0]
                else:
                    a = byl         # the letter the page gives (its text is shortened or worded differently)
            if not 0 <= a < len(q["o"]):
                a = -1
            nk += a >= 0
            rows.append({"id": f"uias-{slug}-{q['n']}", "exam": exam, "year": year, "n": q["n"], "s": q["s"], "o": q["o"],
                         "a": a, "x": "", "book": "unlockias",
                         "source": "Unlock IAS question paper PDF" + ("" if folder == "pyq" else "; key from the paper's page on unlockias.in")})
        with open(f"{OUT}/{slug}.jsonl", "w", encoding="utf8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        total += len(rows); keyed += nk
        print(f"{slug}: {len(rows)} questions ({nk} with key), {eng} English-language left out, parsed {len(qs)}")
print(f"TOTAL {total} questions, {keyed} with key")
