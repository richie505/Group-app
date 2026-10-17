"""Checks structured MCQ explanations (guide: tools/expl_guide.md).

    python3 tools/expl_check.py <book> NNN
reads $EXPL_DIR/b<book>/in_NNN.md and out_NNN.md; prints one line per problem, then "<ok>/<n> MCQs pass".
out_NNN.md:
    Q <id>
    - solution bullet            (2-5: the answer and why, why the others are wrong)
    + additional bullet          (2-6: related facts from the same topic)
Rules checked: every MCQ once; bullet counts; balanced **bold**, bold in the solution; every number in a bullet
appears in the topic's notes or the question; the answer's key words in the solution; no gap lines.
"""
import os, re, sys

STOP = set("""only both neither none all above below statement statements correct incorrect given these those
the and with from that this which their they were have been into upon over under than then also about pair pairs
code codes option options following following: true false 1 2 3 4""".split())


def parse_in(text):
    """{id: (topic notes text, question text, answer option)}"""
    out = {}
    for block in re.split(r"(?m)^=== ROW ", text)[1:]:
        notes, _, qs = block.partition("=== MCQS")
        for q in re.split(r"(?m)^(?=Q \S+ \| page)", qs):
            m = re.match(r"Q (\S+) \| page", q)
            if not m:
                continue
            a = re.search(r"(?m)^Answer: \(\d+\) (.*)$", q)
            out[m.group(1)] = (notes, q, a.group(1) if a else "")
    return out


def parse_out(text):
    out, cur, dup = {}, None, []
    for line in text.splitlines():
        if line.startswith("Q "):
            cur = line[2:].strip().split()[0]
            if cur in out:
                dup.append(cur)
            out[cur] = ([], [])
        elif cur and line.startswith("- "):
            out[cur][0].append(line[2:].strip())
        elif cur and line.startswith("+ "):
            out[cur][1].append(line[2:].strip())
        elif line.strip():
            out.setdefault("__stray__", ([], []))[0].append(line)
    return out, dup


def nums(s):
    return set(re.findall(r"\d+(?:\.\d+)?", s.replace(",", "")))


def words(s):
    return {w for w in re.findall(r"[a-z][a-z\-']{3,}", s.lower()) if w not in STOP}


def check(src, got):
    notes, q, ans = src
    errs = []
    sol, add = got
    if not 2 <= len(sol) <= 5:
        errs.append(f"{len(sol)} solution bullets (need 2-5)")
    if not 2 <= len(add) <= 6:
        errs.append(f"{len(add)} additional bullets (need 2-6)")
    pool = nums(notes) | nums(q)
    for b in sol + add:
        if b.count("**") % 2:
            errs.append(f"unbalanced ** in: {b[:60]}")
        if len(b) > 400:
            errs.append(f"bullet over 400 characters: {b[:60]}")
        if "Not in your sources" in b or b.startswith("!!"):
            errs.append("gap line in an explanation")
        new = nums(b) - pool
        if new:
            errs.append(f"number(s) {sorted(new)} not in the notes or question: {b[:70]}")
    if sol and not any("**" in b for b in sol):
        errs.append("no **bold** in the solution")
    key = words(ans)
    if key and not key & words(" ".join(sol)):
        errs.append(f"answer '{ans[:50]}' not named in the solution")
    return errs


if __name__ == "__main__":
    book, n = sys.argv[1], sys.argv[2]
    d = os.environ.get("EXPL_DIR", "work/expl") + f"/b{book}"
    src = parse_in(open(f"{d}/in_{n}.md").read())
    path = f"{d}/out_{n}.md"
    got, dup = parse_out(open(path).read()) if os.path.exists(path) else ({}, [])
    ok = 0
    for d_ in dup:
        print(f"{n} Q {d_}: written twice")
    if "__stray__" in got:
        print(f"{n}: {len(got.pop('__stray__')[0])} line(s) outside the Q / - / + format")
    for k in got:
        if k not in src:
            print(f"{n} Q {k}: not in the input")
    for k, s in src.items():
        if k not in got:
            print(f"{n} Q {k}: missing")
            continue
        e = check(s, got[k])
        for x in e:
            print(f"{n} Q {k}: {x}")
        ok += not e
    print(f"{ok}/{len(src)} MCQs pass")
