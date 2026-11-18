"""Group 2's notes MCQs (one-liners) -> the exact notes lines that state their fact, so the book icon reads like a
PYQ's: "The correct answer is (1) Harisena." + why + "From your notes" with the line marked (tools/notelink.py form).

Offline, no API: each one-liner carries the sentence it was made from ("xs", else "x"). The notes line (a block,
or a table row) holding the answer's words and most of that sentence's key words is its line; the MCQ's own topic
first, then its book. A one-liner whose fact no line states keeps the app's own guess.

    python3 tools/oneliner_notelink.py [assets dir=app/src/group2/assets] [ids file: link only these, PYQs too]
"""
import json, math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from notes_match import STOP

A = sys.argv[1] if len(sys.argv) > 1 else "app/src/group2/assets"
# optional: a file of ids to (re)link whatever they are (e.g. PYQs whose linked line was merged away)
ONLY = set(open(sys.argv[2]).read().split()) if len(sys.argv) > 2 else None


# question words that say what is asked, not the fact
VAGUE = set("""year which what who whom when where called known name named refers refer following correct statement
statements true false regarding about related associated responsible considered mainly main primarily largely chiefly
used use term describe described describes wrote written write writer composed composer authored author founded
established set launched started introduced built constructed located situated held hosted given gave""".split())


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if (len(w) > 2 or w.isdigit()) and w not in STOP}


def runs(x):
    return "".join(t for t, _ in x or [])


def cell(c):
    return runs(c) if isinstance(c, list) else str(c)


def lines_of(book):
    """[(row, sec, ref "block" or "block.trow", words)] of a book (a table row with its head)."""
    out = []
    rows = [r for u in book["units"] for r in u["rows"]]
    for ri, row in enumerate(rows):
        for si, sec in enumerate(row["secs"]):
            for bi, bl in enumerate(sec["b"]):
                if bl.get("k") == "t":
                    head = " ".join(cell(h) for h in bl.get("h") or [])
                    for ti, tr in enumerate(bl.get("r") or []):
                        out.append((ri, si, f"{bi}.{ti}", words(" ".join(cell(c) for c in tr)), words(head)))
                elif bl.get("x"):
                    out.append((ri, si, str(bi), words(runs(bl["x"])), set()))
    return out


def main():
    links = json.load(open(f"{A}/notelinks.json"))
    added = tried = 0
    for b in range(1, 7):
        book = json.load(open(f"{A}/book{b}.json"))
        m = json.load(open(f"{A}/mcq{b}.json"))
        L = lines_of(book)
        by_word = {}
        for i, (_, _, _, ws, hw) in enumerate(L):
            for w in ws | hw:
                by_word.setdefault(w, []).append(i)
        n = len(L)
        idf = lambda w, n=n, bw=by_word: math.log((n + 1) / (len(bw.get(w, [])) + 1)) + 1
        for r, qs in m["rows"].items():
            subs = m["subs"].get(r) or [-1] * len(qs)
            for q, sub in zip(qs, subs):
                if ONLY is not None:
                    if q["id"] not in ONLY or q["id"] in links or q.get("k") in ("f", "u"):
                        continue
                elif q["id"].startswith("y") or q["id"] in links or q.get("k") in ("f", "u"):
                    continue
                if not (0 <= q.get("a", -1) < len(q.get("o") or [])):
                    continue
                tried += 1
                ans = words(q["o"][q["a"]])
                # the question's own key words (weighted by how rare they are in the notes), the answer on the line
                qw = words(q["s"]) - ans - VAGUE
                if not ans or not qw:
                    continue
                need = sum(idf(w) for w in qw)
                rare = min(ans, key=lambda w: len(by_word.get(w, [])) or 10 ** 9)
                best = None
                for i in by_word.get(rare, []):
                    ri, si, ref, ws, hw = L[i]
                    have = ws | hw
                    if not ans <= have:
                        continue
                    got = qw & have
                    cov = sum(idf(w) for w in got) / need
                    key = (round(cov, 2), str(ri) == r, si == sub, -len(ws))
                    if best is None or key > best[0]:
                        best = (key, ri, si, ref, len(got))
                # most of the question's weight on that one line, and at least two of its words (one if it has one)
                refs = []
                # an answer said all over the notes ("Andhra Pradesh", "India") needs nearly all the question
                common = all(len(by_word.get(w, [])) > 0.01 * n for w in ans)
                # or: a distinctive answer (on at most 5 lines of the book) on a line with a third of the question
                rare_ans = len(by_word.get(rare, [])) <= 5 and not common
                if best and ((best[0][0] >= (0.85 if common else 0.6) and best[4] >= min(2, len(qw)))
                             or (rare_ans and best[0][0] >= 0.3 and best[4] >= 1)):
                    refs.append((best[1], f"{b}:{best[1]}:{best[2]}:{best[3]}"))
                if refs:
                    row0 = refs[0][0]  # the app shows the lines of one topic
                    keep = list(dict.fromkeys(ref for ri, ref in refs if ri == row0))
                    links[q["id"]] = keep
                    added += 1
    open(f"{A}/notelinks.json", "w").write(json.dumps(links, ensure_ascii=False, separators=(",", ":")))
    print(f"{A}: {added} of {tried} notes MCQs linked to their notes line")


if __name__ == "__main__":
    main()
