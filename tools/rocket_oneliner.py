"""APPSC Rocket One-liners: one-line 4-option MCQs made, with no LLM, from every fact of the Rocket-style lecture
notes (data/lecrocket/<group1|group2>/<book>-<row>.json, tools/lecrocket.py), for Group 1 and Group 2 topics.

The app is APPSC Group 2's assets (app/src/group2/assets: all 927 topics, in its own order) with
  - Group 1's topics mapped onto them by title (every Group 1 topic is a Group 2 topic in another place), Group 1's
    pages by title within the topic; a page Group 2 blanks ("the same page is above") gets Group 1's notes back,
    and the 10 Group 1 pages Group 2 lacks are added at the end of their topic;
  - exams.json: Group 1 Prelims (Group 1's, rows remapped) + Group 2;
  - mcq1-6.json: only the Rocket one-liners, each under its notes page ("subs"); index.json counts; planmcq.json.
Pages both groups share give their MCQs once (ids are hashes of question + answer).

    python3 tools/rocket_oneliner.py            # writes app/src/rocketoneliner/assets
    python3 tools/rocket_oneliner.py sample 40  # also prints 40 random MCQs
"""
import collections, difflib, glob, hashlib, json, os, random, re, subprocess, sys

G1, G2, OUT = "app/src/group1/assets", "app/src/group2/assets", "app/src/rocketoneliner/assets"
R = "data/lecrocket"
MAXQ, MAXO = 140, 90

J = lambda p: json.load(open(p))
W = lambda p, o: open(p, "w").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))

# ---------------------------------------------------------------- text helpers

STOP = set("""a an the of and or in on at to for by with from as is are was were be been being it its this that these
those not no nor only all both none first last most least more less than into under over after before about between
which who whom what when where why how their there they them his her he she has have had also any each per via vs
other others such same new old one two three four five six seven eight nine ten india indian state states andhra
pradesh key detail details fact facts wrote founded capital headquarters meaning deity identify term where year
won""".split())
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"


def plain(t):
    return re.sub(r"\s+", " ", t.replace("**", "")).strip()


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", plain(t).lower())).strip()


def stem(w):
    w = w.lower()
    for suf in ("ies", "es", "s", "n", "an"):
        if len(w) > 5 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def cwords(t):
    """content words (stems) of a text, numbers included"""
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z'-]+|\d[\d.,]*", plain(t)):
        lw = w.lower().strip("'-.,")
        if lw.isdigit() or re.fullmatch(r"\d[\d.,]*", lw):
            out.add(lw.rstrip(".,"))
        elif len(lw) >= 4 and lw not in STOP:
            out.add(stem(lw))
    return out


def shares(a, b):
    """do two word sets share a word (a stem equal, or one a 5+ letter prefix of the other)"""
    if a & b:
        return True
    for x in a:
        for y in b:
            if len(x) >= 5 and len(y) >= 5 and (x.startswith(y) or y.startswith(x)):
                return True
    return False


def clean_term(t):
    t = plain(t).strip(" :–-—=→,;.")
    t = re.sub(r"^[\"'“‘]+|[\"'”’]+$", "", t).strip()
    while t.startswith("(") and t.endswith(")") and t.count("(") == 1:
        t = t[1:-1].strip()
    if t.count("(") != t.count(")"):  # a bracket the bold run cut in two
        t = re.sub(r"\s*\($|^\)\s*", "", t).strip()
        if t.count("(") != t.count(")"):
            t = t.replace("(", "").replace(")", "").strip()
    return t


def kind(t):
    t = t.strip()
    if re.fullmatch(r"(?:c\.\s*|~)?\d{3,4}s?(?:\s*(?:CE|BCE|AD|BC|B\.C\.|A\.D\.))?", t):
        return "year"
    if re.fullmatch(r"(?:c\.\s*)?\d{3,4}\s*[-–/]\s*\d{2,4}(?:\s*(?:CE|BCE|AD|BC))?", t):
        return "yrange"
    if re.search(r"\b" + MONTH + r"(?:\s|$|,)", t) and re.search(r"\d", t) and len(t) <= 32:
        return "date"
    if re.fullmatch(r"(?:Articles?|Art\.?|Sections?|Sec|Sec\.|Schedules?|Parts?|Rules?|Clauses?)\s+[\dA-Z][\w()\-–, ]{0,20}", t):
        return "law:" + t.split()[0].lower().rstrip("s.")[:3]
    if re.fullmatch(r"\d+(?:st|nd|rd|th)\s+(?:Amendment|Schedule|Finance Commission|Five[- ]Year Plan|Plan|Lok Sabha)\b.*", t) and len(t) < 40:
        return "ord:" + t.split()[1].lower()
    if re.fullmatch(r"[~≈<>]?\s*(?:₹|\$|Rs\.?|US\$|€|£)?\s*[\d][\d.,]*\s*[%°]?\s*[A-Za-z/²³.\- ]{0,22}", t) and len(t) <= 34:
        unit = re.sub(r"[\d.,~≈<>\s]+", " ", t).strip().lower()
        unit = re.sub(r"\s+", " ", unit)
        return "num:" + unit
    if re.match(r"[~≈<>]?\s*(?:₹|\$|Rs\.?\s|US\$|€|£)?\s*\d", t) and len(re.findall(r"\d+", t)) >= 2 and len(t) <= 40 \
            and len(re.sub(r"[^A-Za-z]", "", t)) <= len(t) * 0.5:
        return "num:mixed"  # "₹5 lakh – ₹10 lakh", "11.24 crore, 9.29%"
    if re.fullmatch(r"[A-Z][A-Z0-9&\-/.]{1,11}(?:\s*\(\d{4}\))?", t):
        return "acr"
    w = t.split()
    shape = "1" if len(w) == 1 else "2" if len(w) <= 3 else "4"
    if t[:1].isupper() or t[:1].isdigit():
        # people / places vs things (acts, schemes, bodies ...): never one for the other
        if any(x.strip(",.()").lower() in THINGS for x in w):
            return "thing:" + shape
        return "name:" + shape
    return "text:" + shape


THINGS = set("""act acts bill scheme schemes yojana mission policy programme program project committee commission council
board bank fund party movement treaty agreement accord pact deal summit conference convention declaration report index
survey award prize day week year tax court tribunal authority agency corporation ministry department institute
institution university college society association league union organisation organization company exercise
operation satellite mission rocket vehicle system plan code rules rule order act, amendment war battle revolt revolution
temple fort cave caves stupa inscription edict river lake dam reservoir port airport corridor park sanctuary reserve
festival dance music painting style school sect dynasty empire kingdom script language law article section schedule
centre center campaign initiative portal app platform network grid zone""".split())


def family(k):
    return ("num" if k.startswith("num:") else "law" if k.startswith(("law:", "ord:")) else
            "yr" if k in ("year", "yrange") else "nm" if k.startswith(("name", "acr")) else
            "th" if k.startswith("thing") else "tx" if k.startswith("text") else k)


def compatible(ka, kb, loose):
    return ka == kb or (loose and family(ka) == family(kb))


def similar_size(a, b, loose):
    la, lb = len(a), len(b)
    wa, wb = len(a.split()), len(b.split())
    lo, hi = (0.4, 2.4) if not loose else (0.25, 4.0)
    if not (lo <= lb / max(la, 1) <= hi):
        return False
    return abs(wa - wb) <= max(2 if not loose else 4, wa)


def close_value(a, c, ka, loose):
    """years within a lifetime or so of each other, figures of about the same size (first passes only)"""
    if loose:
        return True
    if ka in ("year", "yrange"):
        ya, yc = re.search(r"\d{3,4}", a), re.search(r"\d{3,4}", c)
        if ya and yc:
            d = abs(int(ya.group()) - int(yc.group()))
            return d <= (80 if int(ya.group()) > 1500 else 400)
    if ka.startswith("num:"):
        try:
            va = float(re.search(r"\d[\d,]*\.?\d*", a).group().replace(",", ""))
            vc = float(re.search(r"\d[\d,]*\.?\d*", c).group().replace(",", ""))
            return va == 0 or vc == 0 or 0.1 <= vc / va <= 10
        except (AttributeError, ValueError):
            return True
    return True


def near(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb or na == nb:
        return True
    if (len(na) >= 3 and re.search(r"\b" + re.escape(na) + r"\b", nb)) or (len(nb) >= 3 and re.search(r"\b" + re.escape(nb) + r"\b", na)):
        return True
    fa, fb = re.match(r"\W*(\d[\d.,]*)", plain(a)), re.match(r"\W*(\d[\d.,]*)", plain(b))
    if fa and fb and fa.group(1).rstrip(".,") == fb.group(1).rstrip(".,"):
        return True  # the same leading figure: "5.50%; CRR cut" / "5.50% (+25 bps)"
    da, db = re.findall(r"\d+", na), re.findall(r"\d+", nb)
    if da and db and min(len(set(da)), len(set(db))) >= 2 and (set(da) <= set(db) or set(db) <= set(da)):
        return True  # the same date or figures in other words: "17 Oct 1940" / "Gandhi on 17 October 1940"
    mon = lambda x: re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", r"\1", x)
    la, lb = re.sub(r"[\d\s]+", " ", mon(na)).split(), re.sub(r"[\d\s]+", " ", mon(nb)).split()
    if da and da == db and (la == lb or not la or not lb or set(la) <= {"ce", "ad", "bc", "bce", "c"} or set(lb) <= {"ce", "ad", "bc", "bce", "c"}):
        return True  # 1857 / 1857 CE, 2,880 km / 2880 km, Oct 1940 / October 1940
    if len(na) <= 80 and len(nb) <= 80:
        m = difflib.SequenceMatcher(None, na, nb)
        if m.real_quick_ratio() > 0.8 and max(m.ratio(), difflib.SequenceMatcher(None, nb, na).ratio()) > 0.8:
            return True
    return False


def cut(t, n):
    """t cut to n characters at a word, with an ellipsis"""
    if len(t) <= n:
        return t
    s = t[: n - 1].rsplit(" ", 1)[0].rstrip(",;:–- ")
    return s + "…"


def clauses(t):
    """a cell / bullet split into its clauses ("; " and sentence ends outside brackets)"""
    out, depth, cur = [], 0, ""
    i = 0
    while i < len(t):
        ch = t[i]
        cur += ch
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        elif depth == 0 and ch in ";." and i + 1 < len(t) and t[i + 1] == " ":
            if ch == ";" or not re.search(r"(?:\b[A-Z]|\b(?:c|no|vs|art|sec|st|dr|mr|govt|etc|e\.g|i\.e|approx|est|viz|cf))\.$", cur, re.I):
                out.append(cur.strip())
                cur = ""
        i += 1
    if cur.strip():
        out.append(cur.strip())
    return [c for c in out if c]


def sentences(t):
    """a bullet's sentences (". " outside brackets, not after an abbreviation or initial)"""
    out, cur = [], ""
    for c in clauses(t):
        cur = (cur + " " + c).strip() if cur else c
        if cur.endswith("."):
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


# terms no one should be asked for (they are not facts)
GENERIC = set("""yes no not only never all none both first last most least main major key important significant new old
large small high low more less note example examples also and or the a an must may can cannot shall should will would
need needs without with within same different higher lower increase decrease rise fall more fewer is are was were
true false correct wrong""".split())


def specificity(t):
    """how good a blank a bold term makes (None: none at all)"""
    c = clean_term(t)
    n = norm(c)
    if not n or len(c) < 2 or len(c) > 60 or n in GENERIC or all(w in STOP or w in GENERIC for w in n.split()):
        return None
    if re.search(r"[→←=|]", c) or c.count(",") >= 3:
        return None
    k = kind(c)
    s = 0
    if k in ("year", "yrange", "date") or k.startswith(("num:", "law:", "ord:")):
        s += 5
    elif k == "acr":
        s += 4
    elif k == "name":
        s += 3 + (1 if len(c.split()) <= 4 else 0)
    else:
        if len(c.split()) == 1 and len(c) < 5:
            return None  # a short common word is no fact
        s += 1 if len(c.split()) <= 4 else 0
    if len(c.split()) > 6:
        s -= 2
    return s


# ---------------------------------------------------------------- question wording

NOANSWER = {"none", "nil", "na", "n a", "yes", "no", "not applicable", "same", "all", "both", "neither", "", "do", "ditto", "see above"}
GENERIC_HEAD = {"key detail", "key details", "detail", "details", "fact", "facts", "feature", "features", "note", "notes",
                "remarks", "remark", "key fact", "key facts", "description", "about", "what", "content", "point",
                "particular", "particulars", "item", "items", "aspect", "highlights", "key point", "key points"}


def forward_q(a, h1, h2, ka):
    """question for "row a: column h2 = ?" """
    h = plain(h2).strip()
    hl = h.lower()
    A = cut(a, 100)
    if re.search(r"\b(author|writer|written by|composer|poet|composed by)\b", hl):
        return f"Who wrote {A}?"
    if re.search(r"\bfounders?\b|\bfounded by\b|\bestablished by\b", hl):
        return f"Who founded {A}?"
    if hl in ("capital", "capitals"):
        return f"Capital of {A}?"
    if hl in ("hq", "headquarters", "headquarter"):
        return f"Headquarters of {A}?"
    if hl in ("seat",):
        return f"Seat of {A}?"
    if hl in ("meaning", "means", "definition", "defined as"):
        return f"Meaning of {A}?"
    if hl in ("deity", "presiding deity"):
        return f"Deity of {A}?"
    if hl in ("winner", "winners", "won by", "awardee", "recipient", "recipients", "champion"):
        return f"{A} – who won?"
    if hl in ("year", "date", "when", "founded", "established", "launched", "year of", "dates", "period", "tenure"):
        return f"{A} – {'which year' if ka == 'year' else hl}?"
    if hl in ("location", "place", "site", "where", "venue", "located in", "located at", "found at", "region"):
        return f"Where is {A}?" if len(A) < 60 else f"{A} – where?"
    if hl in GENERIC_HEAD:
        return f"{A} – {h}?"
    return f"{A} – {h}?"


def reverse_q(b, h1):
    h = plain(h1).strip()
    hl = h.lower()
    B = cut(b, 115)
    if hl in ("year", "date", "when", "period", "years", "dates"):
        w = hl.rstrip("s")
        return f"{'On which' if w == 'date' else 'When' if w == 'when' else 'In which'}{'' if w == 'when' else ' ' + w}: {B}?"
    if hl in ("term", "terms", "concept", "word"):
        return f"Term for: {B}?"
    if hl in ("person", "ruler", "leader", "king", "who", "personality", "name", "people", "founder", "scientist"):
        return f"Who: {B}?"
    if hl in ("place", "site", "city", "state", "region", "location", "district", "town", "country"):
        return f"Which {hl}: {B}?"
    if hl in GENERIC_HEAD or len(hl) > 25 or "/" in hl:
        return f"Identify: {B}"
    return f"Which {hl}: {B}?"


# ---------------------------------------------------------------- pools of options


class Pool:
    """option candidates of one place (a table column, a page, a topic, a book), by kind"""

    def __init__(self):
        self.by = collections.defaultdict(list)
        self.seen = set()

    def add(self, t):
        t = clean_term(t)
        if not t or len(t) > MAXO:
            return
        n = norm(t)
        if not n or n in self.seen:
            return
        self.seen.add(n)
        self.by[kind(t)].append(t)

    def cands(self, k, loose, rnd, limit=400):
        if not loose:
            xs = self.by.get(k, [])
        else:
            xs = [x for kk, v in self.by.items() if kk != k and compatible(k, kk, True) for x in v]
        if len(xs) > limit:
            xs = rnd.sample(xs, limit)
        else:
            xs = list(xs)
            rnd.shuffle(xs)
        return xs


def distractors(ans, q, pools, seed, ignore=frozenset(), skip=frozenset()):
    """3 options like the answer (same kind, about its size) from the nearest pools, none with a word of the question
    (its column headings aside: ignore); [] if there are not 3 sound ones"""
    rnd = random.Random(seed)
    ka = kind(ans)
    qw = cwords(q) - ignore
    qnums = set(re.findall(r"\d+", q))
    if norm(ans) not in LABELS:
        skip = skip | LABELS  # a row label ("Source", "Members") is no option
    picked = []
    # same kind and size first (nearest pool first), then a kind of the same family, then a looser size
    for loose, size_loose in ((False, False), (True, False), (False, True)):
        for p in pools:
            if p is None:
                continue
            for c in p.cands(ka, loose, rnd):
                if len(picked) == 3:
                    return picked
                if not similar_size(ans, c, size_loose) or not close_value(ans, c, ka, size_loose):
                    continue
                if norm(c) in skip or near(c, ans) or any(near(c, x) for x in picked):
                    continue
                if shares(cwords(c), qw) or (set(re.findall(r"\d+", c)) & qnums):
                    continue
                picked.append(c)
            if len(picked) == 3:
                return picked
    return picked if len(picked) == 3 else []


# ---------------------------------------------------------------- MCQs of one page


def mcq(q, ans, ds, x):
    q = re.sub(r"\s+", " ", q).strip()
    i = "k" + hashlib.sha1((norm(q) + "|" + norm(ans)).encode()).hexdigest()[:11]
    opts = [ans] + ds
    order = list(range(4))
    random.Random(i).shuffle(order)
    return {"id": i, "s": q, "o": [opts[j] for j in order], "a": order.index(0), "x": x}


def giveaway(ans, q):
    """the answer (or its words) already stand in the question"""
    na = norm(ans)
    if na and re.search(r"\b" + re.escape(na) + r"\b", norm(q)):
        return True
    return shares(cwords(ans), cwords(q))


def window(pre, body, label=""):
    """body cut to fit one line after pre, around its blank, starting at a clause where it can"""
    room = MAXQ - len(pre)
    if len(body) <= room:
        return body
    k = body.index("_____")
    room2 = room - len(label) - 2
    starts = [0] + [m.end() for m in re.finditer(r"(?:[;.]\s|,\s|\s[–-]\s)", body) if m.end() <= k]
    s0 = next((x for x in starts if k - x <= room2 - 30), None)
    mid = False
    if s0 is None:  # no clause start near enough: a word start
        s0 = max(0, k - (room2 - 40))
        s0 = body.find(" ", s0) + 1 if s0 > 0 else 0
        mid = s0 > 0
    lead = (label if s0 > 0 and label else "") + ("…" if mid else "")
    out = body[s0:]
    room3 = room - len(lead) - 1
    if len(out) > room3:
        out = out[:room3].rsplit(" ", 1)[0].rstrip(",;:–- ") + "…"
    return lead + out


def blank_q(prefix, text, pools, seed, avoid=(), ignore=frozenset()):
    """blank the most specific bold term of text; (question, answer, distractors) or None"""
    cls = clauses(text)
    m = re.match(r"\s*\*\*([^*]{2,40})\*\*\s*[:–]", text)
    label = (plain(m.group(1)).rstrip(":") + ": ") if m else ""
    cand = []
    for ci, c in enumerate(cls):
        for t in re.findall(r"\*\*(.+?)\*\*", c):
            sp = specificity(t)
            if sp is None:
                continue
            ct = clean_term(t)
            if norm(ct) in avoid or norm(ct) in LABELS:
                continue
            # a label opening the bullet ("**Panjnad:** ...") is its subject: a blank of it last
            is_label = ci == 0 and m is not None and plain(t).rstrip(":") == plain(m.group(1)).rstrip(":")
            cand.append((-(sp - (2 if is_label else 0)), ci, ct, t))
    cand.sort(key=lambda x: (x[0], x[1]))
    full = plain(text)
    for _, ci, ct, t in cand[:4]:
        pt = plain(t)
        # the term once only, so the blank hides it
        if not ct or len(re.findall(re.escape(ct), full, re.I)) != 1:
            continue
        body = full.replace(ct, "_____", 1).rstrip(" ;,")
        rest = body.replace("_____", " ")
        if len(cwords(rest)) < 2 or len(rest.strip(" .;:,–-")) < 12:
            continue  # nothing left to say what is asked
        pre = (prefix + ": ") if prefix else ""
        q = pre + window(pre, body, label)
        if "_____" not in q or giveaway(ct, q.replace("_____", " ")):
            continue
        ds = distractors(ct, q, pools, seed + ct, ignore)
        if ds:
            return q, ct, ds
    return None


def number_blank(prefix, text, pools, seed, ignore=frozenset()):
    """blank a figure / year of a cell that has no bold term"""
    p = plain(text)
    for c in clauses(p):
        m = re.search(r"(?<![\w.])(?:₹\s*)?\d[\d.,]*(?:\s*(?:%|lakh crore|km|crore|lakh|million|billion|MW|GW|ha|m|sq km|CE|BCE|AD|BC))?(?![\w])", c)
        if not m or len(m.group(0)) < 2:
            continue
        ans = m.group(0).strip()
        body = (c[: m.start()] + "_____" + c[m.end():]).rstrip(" ;,")
        if len(cwords(body.replace("_____", " "))) < 2:
            continue
        pre = (prefix + ": ") if prefix else ""
        q = pre + window(pre, body)
        if "_____" not in q or giveaway(ans, q.replace("_____", " ")):
            continue
        ds = distractors(ans, q, pools, seed + ans, ignore)
        if ds:
            return q, ans, ds
    return None


LABELS = set()  # row labels many tables use ("Origin", "Significance", "Members"): main() fills it


def weak(a):
    """a row label that needs the table's heading to mean anything ("Origin", "Status", "As a source", "7")"""
    if len(plain(a)) <= 3 or norm(a) in LABELS:
        return True
    if "**" in a or re.search(r"\d", a):
        return False
    w = plain(a).split()
    return len(w) <= 4 and all(x[:1].islower() or i == 0 for i, x in enumerate(w))


def page_mcqs(blocks, title, pools_of, stats):
    """the MCQs of a Rocket page. pools_of(level, key) -> Pool (level: col/page/topic/book)"""
    out = []
    head = title
    for bi, b in enumerate(blocks):
        k = b.get("k")
        if k == "h":
            head = plain(b.get("x", "")) or title
            continue
        if k == "t":
            hh = [plain(h) for h in (b.get("h") or [])]
            rows = b.get("r") or []
            if not hh:
                hh = [""] * (len(rows[0]) if rows else 0)
            # a first column of serial numbers (1, 2, ii ...) is no fact: the next one names the row
            serial = len(hh) > 1 and rows and all(re.fullmatch(r"\(?[0-9ivxIVX]{1,4}[.)]?", plain(r[0]) or "-") for r in rows)
            if serial:
                hh = hh[1:]
                rows = [r[1:] for r in rows]
                b = {**b, "r": rows, "h": hh}
                blocks = blocks[:bi] + [b] + blocks[bi + 1:]
            for ri, r in enumerate(rows):
                stats["facts"] += 1
                cells = [c or "" for c in r]
                x = " – ".join(plain(c) for c in cells if plain(c).strip(" –-—"))
                made = row_mcqs(cells, hh, ri, bi, head, title, pools_of, x)
                if made:
                    out += made
                else:
                    stats["skipped"] += 1
                    stats["skipped table rows"] += 1
                    if os.environ.get("SKIPLOG"):
                        open(os.environ["SKIPLOG"], "a").write(json.dumps({"h": hh, "r": cells, "head": head}, ensure_ascii=False) + "\n")
            continue
        if k in ("b", "x"):
            t = b.get("x", "")
            if not plain(t):
                continue
            stats["facts"] += 1
            x = plain(t)
            seed = x
            made, used = [], set()
            cl = sentences(t)
            # a bullet: its key term; a long one (sentences with their own key terms): up to 3
            groups = [t] if len(cl) <= 1 or len(plain(t)) <= 160 else cl
            for g in groups[:6]:
                if len(made) >= 3:
                    break
                if "**" not in g:
                    continue
                gp = g
                m = re.match(r"\s*\*\*([^*]{2,40})\*\*\s*[:–]", cl[0])
                if g is not t and g is not cl[0] and m:
                    gp = f"**{m.group(1)}**: " + g  # a later sentence keeps the bullet's label
                r_ = blank_q("", gp, [pools_of("page", None), pools_of("topic", None), pools_of("book", None)], seed, used)
                if r_:
                    q, a, ds = r_
                    used.add(norm(a))
                    made.append(mcq(q, a, ds, x))
            if not made:
                r_ = number_blank("", t, [pools_of("page", None), pools_of("topic", None), pools_of("book", None)], seed)
                if r_:
                    made.append(mcq(r_[0], r_[1], r_[2], x))
            if made:
                out += made
            else:
                stats["skipped"] += 1
                stats["skipped bullets"] += 1
                if os.environ.get("SKIPLOG"):
                    open(os.environ["SKIPLOG"], "a").write(json.dumps({"b": t}, ensure_ascii=False) + "\n")
    return out


def row_mcqs(cells, hh, ri, bi, head, title, pools_of, x):
    a = cells[0]
    A = plain(a)
    ka = kind(clean_term(A)) if A else "text"
    ctx = (cut(head, 60) + ": " + A) if weak(a) and head and norm(head) != norm(A) else A
    seed = x
    out = []
    hw = frozenset().union(*(cwords(h) for h in hh)) if hh else frozenset()

    def col(ci):
        return pools_of("col", (bi, ci))

    def wide(ci):
        h = norm(hh[ci]) if ci < len(hh) else ""
        return [col(ci), pools_of("pagecol", h), pools_of("topiccol", h), pools_of("bookcol", h),
                pools_of("page", None), pools_of("topic", None)]

    def forward(ci):
        B = clean_term(cells[ci])
        if not B or len(B) > 70 or not A or norm(B) in NOANSWER:
            return None
        if ctx != A:  # a label under its heading: the plain form, no "Capital of ..."
            q = f"{ctx} – {hh[ci] if ci < len(hh) else 'detail'}?"
        else:
            q = forward_q(ctx, hh[0] if hh else "", hh[ci] if ci < len(hh) else "", kind(B))
        if len(q) > MAXQ or giveaway(B, q):
            return None
        ds = distractors(B, q, wide(ci), seed + str(ci), hw)
        return mcq(q, B, ds, x) if ds else None

    def reverse(ci):
        if not A or len(clean_term(A)) > 60 or weak(a):
            return None
        ans = clean_term(A)
        q = reverse_q(plain(cells[ci]), hh[0] if hh else "")
        if giveaway(ans, q):
            return None
        ds = distractors(ans, q, [col(0), pools_of("pagecol", norm(hh[0]) if hh else ""), pools_of("topiccol", norm(hh[0]) if hh else ""),
                                  pools_of("bookcol", norm(hh[0]) if hh else ""), pools_of("page", None), pools_of("topic", None)], seed + "r",
                         hw, LABELS)
        return mcq(q, ans, ds, x) if ds else None

    def blank(ci):
        pre = cut(ctx, 45) if A else cut(head, 45)
        if ci < len(hh) and hh[ci].lower() not in GENERIC_HEAD and len(hh[ci]) <= 25:
            pre += f" ({hh[ci].lower()})"
        r_ = blank_q(pre, cells[ci], [col(ci), pools_of("page", None), pools_of("topic", None), pools_of("book", None)], seed + str(ci),
                     avoid={norm(A)}, ignore=hw)
        if not r_:
            r_ = number_blank(pre, cells[ci], [col(ci), pools_of("page", None), pools_of("topic", None), pools_of("book", None)], seed + str(ci), hw)
        return mcq(*r_, x) if r_ else None

    n = len(cells)
    if n <= 1:
        return [m for m in [blank(0)] if m]
    if n == 2:
        B = plain(cells[1])
        tries = []
        if ka in ("year", "yrange", "date") and kind(clean_term(B)) not in ("year", "yrange", "date"):
            tries.append(lambda: reverse(1))
        if len(clean_term(B)) <= 70:
            tries.append(lambda: forward(1))
        tries += [lambda: blank(1), lambda: reverse(1) if ("**" in a or A[:1].isupper()) else None, lambda: blank(0)]
        for f in tries:
            m = f()
            if m:
                return [m]
        return []
    # 3+ columns: each column that holds its own short fact; a long one by a blank (one per row)
    long_done = False
    for ci in range(1, n):
        if not plain(cells[ci]):
            continue
        m = None
        if len(clean_term(cells[ci])) <= 70:
            m = forward(ci)
        if not m and not long_done:
            m = blank(ci)
            long_done = bool(m)
        if m:
            out.append(m)
    if not out:
        for f in (lambda: reverse(1), lambda: blank(0)):
            m = f()
            if m:
                out.append(m)
                break
    return out


# ---------------------------------------------------------------- the app's notes: Group 2's, with Group 1's pages


def book_rows(bk):
    return [r for u in bk["units"] for r in u["rows"]]


def is_dup_page(s):
    bl = s["b"]
    return len(bl) == 1 and bl[0].get("k") == "n" and str(bl[0]["x"][0][0]).startswith("No MCQ")


def build_notes():
    """(books, place map, notes stats): place[(group, book, row, page)] = (book, row, page) of this app"""
    books, place = {}, {}
    st = collections.Counter()
    added = collections.defaultdict(list)
    for b in range(1, 7):
        bk2, bk1 = J(f"{G2}/book{b}.json"), J(f"{G1}/book{b}.json")
        r2, r1 = book_rows(bk2), book_rows(bk1)
        at = {r["title"]: j for j, r in enumerate(r2)}
        for j, r in enumerate(r2):
            for k in range(len(r["secs"])):
                place[("group2", b, j, k)] = (b, j, k)
        for i, r in enumerate(r1):
            j = at[r["title"]]
            tgt = r2[j]["secs"]
            seen = collections.Counter()
            for k, s in enumerate(r["secs"]):
                seen[s["t"]] += 1
                hits = [kk for kk, x in enumerate(tgt) if x["t"] == s["t"]]
                if len(hits) >= seen[s["t"]]:
                    kk = hits[seen[s["t"]] - 1]
                    if is_dup_page(tgt[kk]) and not is_dup_page(s) and s["b"]:
                        tgt[kk] = s  # Group 2 shows it elsewhere; Group 1's topic needs it here
                        st["Group 2 blank pages given Group 1's notes"] += 1
                        added[b].append((j, kk, i, k))
                else:
                    tgt.append(s)
                    kk = len(tgt) - 1
                    st["Group 1 pages added"] += 1
                    added[b].append((j, kk, i, k))
                place[("group1", b, i, k)] = (b, j, kk)
        books[b] = bk2
    return books, place, st, added


def remap_exams(g1_to_g2):
    e1, e2 = J(f"{G1}/exams.json"), J(f"{G2}/exams.json")
    for e in e1:
        for sj in e["subjects"]:
            for g in sj["groups"]:
                g["rows"] = [list(g1_to_g2[tuple(x)]) for x in g["rows"]]
                if "see" in g:
                    g["see"] = [list(g1_to_g2[tuple(x)]) for x in g["see"]]
    return e1 + e2


# ---------------------------------------------------------------- main


def main(sample=0):
    books, place, nst, added = build_notes()
    g1_to_g2 = {}
    for b in range(1, 7):
        t2 = {r["title"]: j for j, r in enumerate(book_rows(books[b]))}
        for i, r in enumerate(book_rows(J(f"{G1}/book{b}.json"))):
            g1_to_g2[(b, i)] = (b, t2[r["title"]])
    titles = {(b, j, k): s["t"] for b in books for j, r in enumerate(book_rows(books[b])) for k, s in enumerate(r["secs"])}

    # every Rocket page at its place in this app (a page both groups share is one place, read once)
    at = collections.defaultdict(list)  # (b, row, sec) -> [blocks]
    seen = collections.defaultdict(set)
    for g in ("group2", "group1"):
        for f in sorted(glob.glob(f"{R}/{g}/*.json")):
            b, i = map(int, os.path.basename(f)[:-5].split("-"))
            for k, bl in J(f).items():
                p = place[(g, b, i, int(k))]
                h = hashlib.md5(json.dumps(bl, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                if h not in seen[p]:
                    seen[p].add(h)
                    at[p].append(bl)

    # row labels used by 4+ tables are labels, not names
    lab = collections.Counter()
    for bls in at.values():
        for bl in bls:
            for blk in bl:
                if blk.get("k") == "t":
                    lab.update({norm(r[0]) for r in blk.get("r") or [] if r and "**" not in r[0]})
    LABELS.update(l for l, n in lab.items() if n >= 4 and l)

    # option pools: a table's column, a page, a topic, a book (and the same column heading on a page / topic / book)
    P = collections.defaultdict(Pool)
    for (b, j, k), bls in at.items():
        for bl in bls:
            for blk in bl:
                if blk.get("k") == "t":
                    hh = [norm(h) for h in blk.get("h") or []]
                    for r in blk.get("r") or []:
                        for ci, c in enumerate(r):
                            h = hh[ci] if ci < len(hh) else ""
                            for lvl, key in (("pagecol", (b, j, k, h)), ("topiccol", (b, j, h)), ("bookcol", (b, h))):
                                P[(lvl, key)].add(c)
                            for t in re.findall(r"\*\*(.+?)\*\*", c):
                                if specificity(t) is not None:
                                    for lvl, key in (("page", (b, j, k)), ("topic", (b, j)), ("book", b)):
                                        P[(lvl, key)].add(t)
                elif blk.get("k") in ("b", "x"):
                    for t in re.findall(r"\*\*(.+?)\*\*", blk.get("x", "")):
                        if specificity(t) is not None:
                            for lvl, key in (("page", (b, j, k)), ("topic", (b, j)), ("book", b)):
                                P[(lvl, key)].add(t)

    stats = collections.Counter()
    rows = {b: collections.defaultdict(list) for b in range(1, 7)}
    ids = set()
    for (b, j, k) in sorted(at):
        for bl in at[(b, j, k)]:
            colp = {}

            def pools_of(level, key, b=b, j=j, k=k, bl=bl, colp=colp):
                if level == "col":
                    bi, ci = key
                    if key not in colp:
                        p = Pool()
                        for r in bl[bi].get("r") or []:
                            if ci < len(r):
                                p.add(r[ci])
                        colp[key] = p
                    return colp[key]
                if level == "page":
                    return P[("page", (b, j, k))]
                if level == "topic":
                    return P[("topic", (b, j))]
                if level == "book":
                    return P[("book", b)]
                if level == "pagecol":
                    return P[("pagecol", (b, j, k, key))]
                if level == "topiccol":
                    return P[("topiccol", (b, j, key))]
                if level == "bookcol":
                    return P[("bookcol", (b, key))]

            for q in page_mcqs(bl, titles[(b, j, k)], pools_of, stats):
                if q["id"] in ids:
                    stats["repeats left out"] += 1
                    continue
                ids.add(q["id"])
                rows[b][j].append((k, q))

    # ---- the assets
    os.makedirs(OUT, exist_ok=True)
    index = J(f"{G2}/index.json")
    total = 0
    for b in range(1, 7):
        rr, ss = {}, {}
        for j, qs in sorted(rows[b].items()):
            qs.sort(key=lambda x: x[0])  # in page order (stable: the page's own order within)
            rr[str(j)] = [q for _, q in qs]
            ss[str(j)] = [k for k, _ in qs]
        W(f"{OUT}/mcq{b}.json", {"rows": rr, "units": {}, "subs": ss})
        W(f"{OUT}/book{b}.json", books[b])
        info = index["books"][b - 1]
        info["uq"] = {}
        for j, r in enumerate(book_rows(books[b])):
            row = info["rows"][j]
            row["q"] = len(rr.get(str(j), []))
            row["n"] = len(r["secs"])
            row.pop("hide", None)  # Group 2 hides a Group 1 topic
            total += row["q"]
    W(f"{OUT}/index.json", index)
    W(f"{OUT}/exams.json", remap_exams(g1_to_g2))
    W(f"{OUT}/edition.json", {"edition": "oneliner", "name": "APPSC Rocket One-liners"})
    # pages Group 2 blanks, less those given Group 1's notes back
    emp = J(f"{G2}/empty.json")
    filled = {f"{b}:{j}:{kk}" for b, xs in added.items() for j, kk, _, _ in xs}
    W(f"{OUT}/empty.json", {"mcq": [], "full": [p for p in emp["full"] if p not in filled]})
    # key terms of the pages taken from Group 1
    kt, kt1 = J(f"{G2}/keyterms.json"), J(f"{G1}/keyterms.json")
    for b, xs in added.items():
        for j, kk, i, k in xs:
            if f"{b}:{i}:{k}" in kt1:
                kt[f"{b}:{j}:{kk}"] = kt1[f"{b}:{i}:{k}"]
    W(f"{OUT}/keyterms.json", kt)
    # the plan: Group 2's, with the Group 1 topic it leaves out (1:263, Gurjara-Pratiharas) beside its neighbours
    plan = J(f"{G2}/plan.json")
    planned = {tuple(r["ref"]) for d in plan["days"] for r in d["rows"] if r.get("ref")}
    for b in range(1, 7):
        for j, r in enumerate(book_rows(books[b])):
            if (b, j) in planned:
                continue
            for d in plan["days"]:
                refs = [x.get("ref") for x in d["rows"]]
                near_ = [n for n, x in enumerate(refs) if x and x[0] == b and abs(x[1] - j) <= 2]
                if near_:
                    tmpl = dict(d["rows"][near_[0]])
                    tmpl.update(ref=[b, j], topic=r["title"], codes=index["books"][b - 1]["rows"][j].get("codes", []))
                    d["rows"].insert(near_[0] + 1, tmpl)
                    stats["topics added to the plan"] += 1
                    break
    W(f"{OUT}/plan.json", plan)
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", OUT], check=True)
    pm = J(f"{OUT}/planmcq.json")
    for d, x in zip(plan["days"], pm):
        d["brief"] = [re.sub(r"Then today's MCQs \(all \d+ of them\)\.", f"Then today's MCQs (all {len(x)} of them).", s) for s in d["brief"]]
    W(f"{OUT}/plan.json", plan)

    for k_, v in nst.items():
        print(f"{k_}: {v}")
    print(f"facts {stats['facts']}, MCQs {total}, skipped {stats['skipped']} "
          f"(table rows {stats['skipped table rows']}, bullets/boxes {stats['skipped bullets']}), "
          f"repeats left out {stats['repeats left out']}, topics added to the plan {stats['topics added to the plan']}")
    for b in range(1, 7):
        print(f"book {b}: {sum(1 for _ in rows[b].values() for _ in _)} MCQs")
    if sample:
        allq = [(b, j, k, q) for b in rows for j, qs in rows[b].items() for k, q in qs]
        rnd = random.Random(sample)
        for b, j, k, q in rnd.sample(allq, sample):
            print(f"\n[{b}:{j}:{k}] {q['s']}")
            for n, o in enumerate(q["o"]):
                print(("  * " if n == q["a"] else "    ") + o)
            print("  x: " + q["x"][:200])


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[1]) if a[:1] == ["sample"] else 0)
