"""Lecture slides without citations: no source lists, no exam / paper tags ("APPSC G2 2024", "(UPPCS 2013)"), no
book names (PMF, NextGen, Rocket ...), no "exam angle" counts or "settled" source notes - the facts stay."""
import re

EXAMS = (r"APPSC|UPSC|UPPCS|UPPSC|UPSSSC|RAS|RPSC|IAS|CDS|NDA|JKPSC|JKSSB|JPSC|BPSC|MPPSC|MPSC|TNPSC|KPSC|HPSC|HPPSC|OPSC|TSPSC|"
         r"WBCS|WBPSC|SSC|CGL|CHSL|CAPF|CSE|CSAT|UKPSC|UKPCS|CGPSC|GPSC|PCS|PSC|RRB|NTPC|IBPS|SBI|LIC|AFCAT|ACF|TET|DSC|Sachivalayam|"
         r"Group[- ]?(?:I|II|III|IV|1|2|3|4)\b|G-?[12]\b|UP Lower|State PSC|Civil Services")
BOOKS = r"PMF|NextGen|Rocket(?= (?:Sheets?|notes|Indian|AP|Economy|Polity|Geography|History)\b| p\.)|Lucent|Laxmikanth|Spectrum(?= (?:Modern|A Brief|gives|says|p\.)|,)|Drishti|Vision IAS|OnlyIAS|Wikipedia|Britannica|New World Encyclopedia|gktoday|app notes|ClearIAS|Testbook|Adda247"
SUF = r"G-?[12]|Group[- ]?(?:I|II|III|IV|1|2|3|4)|GS|ASO|AEE|AE|EO|CPO|Pre|Prelims|Mains|Re-?exam|Screening|Paper[- ]?[IVX0-9]+|Lower|[A-Z]{2,5}"
# an exam is a citation only with a year / key / "PYQ" after it, or as an APPSC Group tag: "UPSC" alone (Article 315),
# "SBI", "NTPC", "LIC", "NDA", "CDS", "Civil Services", "Group 1" (a ranking group) are real content and stay
TAG = rf"(?:{EXAMS})(?:[ -](?:{SUF}))*"
EX = (rf"(?:AP Sachivalayam|APPSC[ -](?:{SUF})(?:[ -](?:{SUF}))*(?:[ ,]*\d{{4}})*(?:[ ,]*key)?"
      rf"|{TAG}(?:[ ,/]+{TAG})*[ ,]*\(?\d{{4}}(?:[-–/]\d{{2,4}})?\)?(?:[ ,]*(?:and |& )?\d{{4}})*(?:[ ,]*(?:answer key|key|PYQ|paper))*"
      rf"|{TAG}[ ,]+(?:answer key|key|PYQs?))")
EXR = re.compile(rf"\b{EX}(?![\w-])")
KEYNOTE = re.compile(r"\b(?:some |the |its |official |APPSC |old |question |most )*(?:keys?|(?:some|most|many|the|other) guides|quiz books|books and keys)\b[^.;]*\b(?:print|give|say|list|differ|wrong|call|put|mark|treat|keep|show|accept)|^\W*Sources differ", re.I)
TOK = re.compile(rf"\b{EX}(?![\w-])|\b(?:{BOOKS})\b|\bPYQs?\b|\bp\.\s?\d|×\d+\b(?!\s*(?:min|km|cm|mm|kg|m\b|%))|\(source:|\b(?:[Oo]fficial|app|answer|final|revised) keys?\b")


def _paren(m):
    """a bracket that cites goes; one that mixes a fact and a citation keeps the fact: (13 Nov; Spectrum gives 2 Nov)"""
    sp, a, body, b = m.groups()
    if re.fullmatch(r"\s*(?:State PSC|APPSC|APPSC key|old APPSC|AP)\s*", body):  # "(State PSC)" - a source tag
        return ""
    if not TOK.search(body) and not KEYNOTE.search(body):
        return m.group(0)
    keep = [x.strip() for x in re.split(r";\s*", body) if x.strip() and not TOK.search(x) and not KEYNOTE.search(x)]
    return f"{sp}{a}{'; '.join(keep)}{b}" if keep else ""


def clean_text(t):
    """one line of notes for a lecture: no citations, nothing left of the MCQ it came from ('' if nothing is left)"""
    c = _cite(t)
    return plain(c) if c else c


def _cite(t):
    """one line of notes without its citations ('' if nothing is left)"""
    o = t
    # "exam keys give 1877 ..." is a teaching point: "exams give 1877 ..."
    t = re.sub(r"\bexam keys?\b(\s*\(\w+\))?", "exams", t)
    t = re.sub(r"\bthe app key puts\b", "the list has", t)
    if not TOK.search(t) and not KEYNOTE.search(t):
        return t
    t = re.sub(rf"^\s*(?:{BOOKS})(?: says)?\s*:\s*", "", t)  # "PMF: AP announced ..."
    t = re.sub(r"\s*×\d+\b(?!\s*(?:min|km|cm|mm|kg|m\b|%))", "", t)
    # a fact that only starts with a book's name: "NextGen lists four instruments: ..." -> "Four instruments: ..."
    t = re.sub(rf"^(\W*)(?:{BOOKS})(?:'s)?\s+(?:lists\s+|also lists\s+)?(?=[a-z])(?!says|calls|gives|has|puts|dates|writes)", r"\1", t)
    t = re.sub(r"\s*\(source:.*$", "", t, flags=re.I)
    t = re.sub(r"^\s*\d+\s+PYQs?\s*[:–-]\s*", "", t)  # "17 PYQs: ..."
    for _ in range(3):  # parentheses / brackets that cite (nested ones from the inside out)
        t = re.sub(r"(\s*)([\(\[])([^()\[\]]*)([\)\]])", _paren, t)
    # "... – asked in APPSC 2012", "as per the UPSC 2019 key"
    t = re.sub(rf"[,;:–—-]?\s*(?:as |was |were |is |also )?(?:asked|tested|seen|repeated|set|per|according to|as per|in)\s+(?:the\s+)?{EX}(?![\w-])[^.;]*", lambda m: "" if EXR.search(m.group(0)) else m.group(0), t)
    # clauses that only name a book ("; NextGen and Megasthenes give 1/4")
    parts = re.split(rf"(;\s+|,?\s+(?=(?:though|but|while|whereas)\s[^.;]*\b(?:{BOOKS})\b))", t)
    t = "".join(p for p in parts if not re.search(rf"\b(?:{BOOKS})\b", p))
    # side notes on keys and guides ("The APPSC keys wrongly printed ...", "keys usually give Barani"): the clause goes
    bits = re.split(r"((?<=[.!?;])\s+|,?\s+(?=(?:though|but|while|whereas)\s[^.;]*\b(?:keys?|guides|books)\b))", t)
    t = "".join(x for x in bits if not KEYNOTE.search(x)) if any(x.strip() and not KEYNOTE.search(x) for x in bits) else t
    t = EXR.sub("", t)
    # what is left on keys is a teaching point ("most keys give Calcutta ..."): say "exams"
    t = re.sub(r"\b(?:most |some |many )?books and keys\b", "most exams", t)
    t = re.sub(r"\b(?:the |official |final )?keys\b", "exams", t)
    t = re.sub(r"\b(?:the |a printed |official |final )key\b", "the exam answer", t)  # any exam tag left ("APPSC G2 2011 calls ...")
    t = re.sub(r"\bPYQs?\b", "", t)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\s+([,.;:)])", r"\1", t)
    t = re.sub(r"\(\s*\)|\[\s*\]", "", t)
    t = re.sub(r"^[\s,;:–—-]+|[\s,;–—-]+$", "", t)
    t = re.sub(r"([,;])\s*([,;.])", r"\2", t)
    t = re.sub(r"^\s*:\s*", "", t)
    if t == o.strip():
        return t
    if len(re.sub(r"[^A-Za-z]", "", t)) < 4:
        return ""
    i = next((n for n, ch in enumerate(t) if ch.isalpha()), None)
    return t[:i] + t[i].upper() + t[i + 1:] if i is not None and t[i].islower() and not re.match(r"[a-z]+[A-Z]", t[i:]) else t


# --- what is left of the MCQs a line was written from: answers, options, statement checks, exam labels ---------------
ANS = r"(?:\(?[a-d]\)?|\(?[A-D]\)?|[IVX]{1,4}|[1-4])"
QUIZ = re.compile(
    r"\(\s*[a-d]\s*\)\s*(?:is|are)\b|\b(?:all|both)(?: (?:are|four|three|of these|statements?))? (?:true|correct|false|wrong)\b|"
    r"\b(?:is|are|was) (?:false|true|correct|wrong|incorrect)\b|\bA and R\b|\bR (?:is |does not |not )?(?:the )?(?:correct )?expla|"
    r"\b(?:wrong|correct|incorrect|false|true) (?:statement|pair|option|answer|match)s?\b|\bthe answer\b|\boptions\b|\boption \(?[a-d1-4]\b|"
    r"\bonly (?:I|II|III|IV|1|2|3|4)\b|\bstatements? (?:[IVX1-4]|one|two|three)|\b(?:correctly|wrongly) (?:matched|paired)\b|"
    r"\bodd one\b|\bnone of the above\b|\ball of the above\b|\bkeyed\b|\bdistractor")
LABEL = re.compile(
    r"^\W*(?:⚠\s*)?(?:Statement (?:angle|check|set|trap)s?|Angles?|Traps?|Statements?|A-?R|Assertion[- ]Reason|(?:Wrong|Correct|Odd) (?:pair|one out|match)s?|"
    r"Match(?: drill| angle)?|Matching|Trap|Order(?: angle)?|Sequence|Exam angle|Angle|Calculation angle|Disputed(?: key)?|Not true)\s*(?:\([^)]*\))?\s*[:–-]\s*", re.I)


def plain(t):
    """a lecture line without the MCQ it came from: no answers ("(b) is false -> a, c, d", "= IV, I, II, III"), no wrong
    options ("- not Vijnaneshvara, Narada or Jimutavahana"), no statement checks (✓ / ✗), no exam labels"""
    o = t
    if len(re.findall("[✓✗]", t)) >= 2:  # a statement check, item by item
        return ""
    t = LABEL.sub("", t)
    # the verdict at the end: "-> A and R true, R not the explanation", "- both true", "; all four correct"
    t = re.sub(r"\s*(?:→|=>|[–—;,])\s*(?:both|all|A and R|A,? R|A|R)\b[^.;]*?\b(?:true|false|correct|wrong|explanation|explains)\b[^.;]*", "", t)
    # brackets about the exam: "(AP recruitment)", "(asked twice)", "(options: ...)"
    t = re.sub(r"\s*\([^()]*\b(?:recruitment|exam|papers?|questions?|asked|options?|answers?|keys?|PSC|APPSC|statements?)\b[^()]*\)", "", t, flags=re.I)
    # the answer at the end: "-> a, c, d", "= IV, I, II, III", "-> \"only I\"", "-> (c)"
    t = re.sub(rf"\s*(?:→|=>|=|:)\s*[\"“]?(?:only |both |all )?{ANS}(?:\s*(?:,|and|&|–|-)\s*{ANS})*[\"”]?\s*(?=[.;]?\s*$)", "", t)
    t = re.sub(r"\s*(?:→|=>)\s*[\"“][^\"”]{1,30}[\"”]\s*(?=[.;)]?\s*$)", "", t)
    # the wrong options: "- not A, B or C" / "; not A or B"
    t = re.sub(r"\s*(?:[–—]|;|,)\s*not\s+(?:the\s+|a\s+|an\s+)?[^.;()]*?(?:\b(?:or|nor)\b|,\s*not\b)[^.;()]*", "", t)
    # statement checks: "X ✓, Y ✗ (Bombay)" -> X
    t = re.sub(r"[^,;:.]*✗(?:\s*\([^)]*\))?", "", t)
    t = t.replace("✓", "")
    # clauses that only work the answer out: "all true", "so (b) is false", "both true, R explains A"
    bits = re.split(r"(;\s+|\s+[–—]\s+|,\s+(?=so\b|hence\b|thus\b)|\.\s+)", t)
    keep = []
    for i in range(0, len(bits), 2):
        c = bits[i]
        if QUIZ.search(c):
            continue
        if keep:
            keep.append(bits[i - 1])
        keep.append(c)
    t = "".join(keep)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\s+([,.;:)])", r"\1", t)
    t = re.sub(r"[,;:\s–—-]+([.)]?)\s*$", r"\1", t).strip()
    t = re.sub(r"\(\s*\)", "", t).strip()
    if t != o.strip():
        if len(re.sub(r"[^A-Za-z]", "", t)) < 12:
            return ""
        i = next((n for n, ch in enumerate(t) if ch.isalpha()), None)
        if i is not None and t[i].islower() and not re.match(r"[a-z]+[A-Z]", t[i:]):
            t = t[:i] + t[i].upper() + t[i + 1:]
        if t and t[-1] not in ".?!)\"”":
            t += "."
    return t


def drop_block(kind, text):
    """whole blocks a lecture leaves out"""
    if kind == "p":
        return True
    if kind == "n" and re.match(r"\s*(Sources?|No MCQ)", text, re.I):
        return True
    if kind == "s":  # "Settled: some keys print ..." - a note on sources
        return True
    if kind == "x" and re.match(r"\s*(Exam angle|Most asked|Asked|PYQ)", text, re.I):
        return True
    return False
