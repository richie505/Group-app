"""Find and trim OCR junk in PYQ text (scanned papers read Telugu or tick marks as
stray symbols, e.g. "Guntur 1. ¥", "Madhya Pradesh ® HAs", "Doppler effect 43901").

Only junk at the end of an option or question is cut, and only when the words
before it still carry the text; badly broken questions are reported, not guessed at."""
import re
from collections import Counter

SYMBOLS = re.compile(r"[@\\¥§~^®©€£¢]|[|](?=\S)|(?<=\S)[|]")
TICK = re.compile(r"\d\.[xv]|[xv]\d|\d[xv]")
WATERMARK = re.compile(r"4390\d{2,}\S*")  # a phone number stamped on scanned pages
OK_ALNUM = re.compile(
    r"\d+(st|nd|rd|th|s|km|kg|mw|gw|kw|cm|mm|m|g|ml|am|pm|ad|bc|bce|ce|x|d|gb|mb|hz|v)"
    r"|[A-Z]{1,6}-?\d+[A-Z]{0,3}|\d+[A-Z]{1,3}|[A-Z]\d[A-Z]\d|[A-Z][a-z]?\d{1,2}[A-Z]?[a-z]?\d?"
    r"|[A-Z]{1,4}-\d+|(G|C|P|Q|W|BRICS|SDG|NH|MIG|INS|IRS|INSAT|GSAT|PSLV|GSLV|COP|IPL)\d+", re.I)
CHEM = re.compile(r"(\d?([A-Z][a-z]?\d*)+)|\d+[A-Z][a-z]?\d+")
ELEMENTS = set("""H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se
Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf
Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am""".split())
KNOWN = {"igg", "iga", "igm", "ige", "igd", "lifi", "wifi", "xposat", "m1xchange", "mkiii", "mkii", "mkiv", "mkv",
         "ω2r", "phd", "ipv4", "ipv6", "mp3", "mp4", "covid", "sars"}
NUMBER = re.compile(r"\d+(\.\d+)?(o|oC|oN|oS|oE|oW|°[CNSEW]?|%|o\d+)?|\d+°\d*[NSEW]?")


def words(t):
    return re.findall(r"[a-z]+", t.lower())


class Cleaner:
    def __init__(self, texts):
        self.vocab = Counter()
        for t in texts:
            self.vocab.update(words(t))

    def kind(self, tok):
        """2 = junk, 1 = unknown word (weak), 0 = fine."""
        if tok in ("|", "||", "°", "%"):
            return 0
        if SYMBOLS.search(tok) or WATERMARK.fullmatch(tok):
            return 2
        if TICK.fullmatch(tok.strip(".,")):
            return 2
        worst = 0
        for t in re.split(r"[-–/,()\[\]:;.'’\"“”!?*=+<>]+", tok):
            if not t or NUMBER.fullmatch(t) or re.fullmatch(r"\d+\^-?\d+", t):
                continue
            lw = t.lower()
            if lw in KNOWN or re.sub(r"^[a-z]?po", "po", lw) == "posat":
                continue
            m = re.fullmatch(r"\d+([a-z]{2,})", lw)
            if m and self.vocab[m.group(1)] >= 3:
                continue  # a number run into its unit ("250crores")
            if self.vocab[lw] >= 3 or re.fullmatch(r"[A-Z]{2,}s", t):
                continue
            if re.search(r"\d", t) and re.search(r"[A-Za-z]", t):
                if OK_ALNUM.fullmatch(t) or CHEM.fullmatch(t):
                    continue
                return 2
            parts = re.findall(r"[A-Z][a-z]?|\d+|.", t)
            if all(x in ELEMENTS or x.isdigit() for x in parts) and any(len(x) == 2 or x.isdigit() for x in parts):
                continue  # a chemical formula: ZnO, CuSO4
            if len(t) >= 8 and t.isalpha() and sum(c.isupper() for c in t) <= 2:
                worst = max(worst, 1)  # words run together by the scan ("forlnformationT"), still readable
                continue
            if re.match(r"[a-z]+[A-Z]", t) and not re.match(r"(e|i|m|x|n)[A-Z]", t):
                return 2
            if re.search(r"[a-z][A-Z]", t):
                segs = re.findall(r"[A-Z]*[a-z]+|[A-Z]+(?![a-z])", t)
                if any(len(s) <= 2 for s in segs[1:]) or re.match(r"[A-Z]{2}[a-z]", t):
                    return 2
            if t.isupper():
                continue  # abbreviations: NKC, CSCR
            if re.fullmatch(r"[a-z]{3,}", lw) and self.vocab[lw] <= 1 and not re.search(r"[aeiouy]", lw):
                return 2
            if re.fullmatch(r"[a-z]{2,}", lw) and self.vocab[lw] <= 1:
                worst = 1
        return worst

    def _tail_junk(self, tok):
        """A token that may sit in a junk tail: junk, unknown, bare punctuation/digits, or tiny."""
        k = self.kind(tok)
        if k:
            return True
        t = tok.strip(".,;:!?'\"()[]{}-–—")
        return not t or len(t) <= 2 or (t.isdigit() and len(t) <= 2)

    def _trigger(self, tok):
        """A token that on its own marks the start of a junk tail."""
        if self.kind(tok) == 2 or tok in ("*", "#", "»", "«", "{", "}", "{/"):
            return True
        return False

    def trim(self, text, keep_min=1):
        spans = [m for m in re.finditer(r"\S+", text)]
        toks = [m.group() for m in spans]
        if not toks:
            return text
        cut = None
        i = len(toks) - 1
        while i >= keep_min and (self._tail_junk(toks[i]) or self._trigger(toks[i])):
            if self._trigger(toks[i]):
                cut = i
            i -= 1
        if cut is None:
            return text
        # also drop the short digit/punctuation crumbs just before the first junk token ("Guntur 1. ¥")
        while cut > keep_min and re.fullmatch(r"\d?[.,;:|%*#&'\"-]{1,2}|\d", toks[cut - 1]):
            cut -= 1
        out = text[:spans[cut].start()].rstrip(" \t\n,;:-–—")
        # a junk token that starts with a real number keeps the number ("December 4&n0n6" -> "December 4")
        m = re.match(r"(\d{1,4})(?=[^\d.,][^\s]*\d)", toks[cut])
        if m and not re.search(r"\d", out):
            out += " " + m.group(1)
        # a garbled short answer ("I, WlandIV") is worth more whole than cut to a stub
        if len(out) <= 4 and len(text) - len(out) > len(out):
            return text
        return out

    def clean_question(self, q):
        """Trim junk tails in place; returns True if anything changed."""
        changed = False
        for key in ("s",):
            if "\xad" in q[key]:
                q[key] = q[key].replace("\xad", "")
                changed = True
        if any("\xad" in o for o in q["o"]):
            q["o"] = [o.replace("\xad", "") for o in q["o"]]
            changed = True
        opts = []
        for o in q["o"]:
            o = " ".join(t for t in o.split() if not WATERMARK.fullmatch(t)) or o
            new = self.trim(o)
            changed |= new != o
            opts.append(new)
        q["o"] = opts
        stoks = q["s"].split()
        # never cut more than a third of a question
        new = self.trim(q["s"], keep_min=max(3, len(stoks) * 2 // 3))
        if new != q["s"]:
            q["s"] = new
            changed = True
        return changed

    def level(self, q):
        """0 clean, 1 partly broken, 2 badly broken (the question or 2+ options unreadable)."""
        def score(p):
            s = w = 0
            for tok in p.split():
                k = self.kind(tok)
                s += k == 2
                w += k == 1
            return s, w
        st = score(q["s"])
        ops = [score(o) for o in q["o"]]
        strong = st[0] + sum(o[0] for o in ops)
        weak = st[1] + sum(o[1] for o in ops)
        if not (strong >= 2 or (strong >= 1 and weak >= 2)):
            return 0
        if st[0] >= 2 or sum(1 for o in ops if o[0]) >= 2 or strong >= 4:
            return 2
        return 1
