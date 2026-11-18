"""Where a one-fact MCQ's fact is in the notes: the subsection (book row, sec) holding a notes line with the MCQ's answer
and most of its question's key words. Used to place one-liners where their fact is taught.

    from notes_match import NotesIndex; ix = NotesIndex(rows_of_book); ix.find(question, answer) -> (row, sec, score) | None
"""
import re

STOP = set("""the a an of in on at to for by with from and or is are was were be been which what who whom whose when where
why how this that these those it its as into than then there their they he she his her not no yes following given above
below one two first called known name named also only any all most more best during under over about after before between
india indian state states""".split())


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) > 2 and w not in STOP]


def runs(bl):
    return "".join(t for t, _ in bl.get("x") or [])


def block_lines(sec):
    out = [sec["t"]]
    for bl in sec["b"]:
        if bl.get("x"):
            out.append(runs(bl))
        for row in bl.get("r") or []:  # table rows
            out.append(" ".join("".join(t for t, _ in c) if isinstance(c, list) else str(c) for c in row))
    return out


class NotesIndex:
    def __init__(self, rows):
        self.lines = []  # (row, sec, set of words)
        self.by_word = {}
        for r, row in enumerate(rows):
            for s, sec in enumerate(row["secs"]):
                for ln in block_lines(sec):
                    ws = set(words(ln))
                    if not ws:
                        continue
                    i = len(self.lines)
                    self.lines.append((r, s, ws))
                    for w in ws:
                        self.by_word.setdefault(w, []).append(i)

    def find(self, q, a, prefer_row=None):
        aw = set(words(a))
        qw = set(words(q)) - aw
        if not aw or not qw:
            return None
        # candidate lines: those with the answer's rarest word
        rare = min(aw, key=lambda w: len(self.by_word.get(w, [])) or 10 ** 9)
        best = None
        for i in self.by_word.get(rare, []):
            r, s, ws = self.lines[i]
            if not aw <= ws:
                continue
            sc = len(qw & ws)
            key = (sc, r == prefer_row)
            if best is None or key > best[0]:
                best = (key, r, s)
        if best is None or best[0][0] < min(2, len(qw)):
            return None
        return best[1], best[2], best[0][0]
