"""Removes echo padding from reorganised topics: "**living will / advance directive** (**'living will'**)"
-> the parenthesised bold repeat goes when every word of it is already on the same line.

    python3 tools/topic_unpad.py <book>      (rewrites work/topic/b<book>/out_*.md in place)
A topic keeps its cleanup only if it still passes tools/topic_check.py.
"""
import glob, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from topic_check import topics, check

ECHO = re.compile(r" \(\*\*([^*()]+(?:\([^*()]*\))?[^*()]*)\*\*\)")


def toks(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def unpad_line(line):
    while True:
        for m in ECHO.finditer(line):
            rest = line[:m.start()] + line[m.end():]
            if toks(m.group(1)) <= toks(rest):
                line = rest
                break
        else:
            return line


book = sys.argv[1]
d = os.environ.get("TOPIC_DIR", "work/topic") + f"/b{book}"
total = 0
for f in sorted(glob.glob(f"{d}/out_*.md")):
    n = f[-6:-3]
    text = open(f).read()
    old = topics(open(f"{d}/in_{n}.md").read())
    chunks = re.split(r"(?m)^(?==== ROW )", text)
    out = []
    for c in chunks:
        new_c = "\n".join(unpad_line(l) for l in c.split("\n"))
        if new_c != c:
            t = topics(new_c)
            row = next(iter(t), None)
            if row is not None and row in old and not check(old[row], t[row]):
                total += sum(a != b for a, b in zip(c.split("\n"), new_c.split("\n")))
                c = new_c
        out.append(c)
    open(f, "w").write("".join(out))
print(f"book {book}: {total} lines unpadded")
