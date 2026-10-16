"""Checks reorganised topics (work/topic/b<book>/out_NNN.md) against their input.

    python3 tools/topic_check.py <book> [NNN]
Per topic: every number and gap line kept (gap lines the same number of times), nearly all bold terms kept,
every input subsection named in some "from:", the Universal angles page last, each page parses.
"""
import glob, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from restructure_check import problems, BOLD
from structured_md import to_blocks


def topics(text):
    """{row: (title, [(head, body)])} where head is the text after "## "."""
    out = {}
    for chunk in re.split(r"^=== ROW ", text, flags=re.M)[1:]:
        head, _, body = chunk.partition("\n")
        row, _, title = head.partition(" | ")
        secs = [(s.partition("\n")[0].strip(), s.partition("\n")[2].strip()) for s in re.split(r"^## ", body, flags=re.M)[1:]]
        out[int(row)] = (title.strip(), secs)
    return out


def parse_head(h):
    """'Title | from: S1, S3 | universal' -> (title, [1, 3], universal)"""
    parts = [p.strip() for p in h.split(" | ")]
    src = next((p for p in parts if p.startswith("from:")), "")
    return parts[0], [int(x) for x in re.findall(r"S(\d+)", src)], "universal" in parts[1:]


def check(old, new):
    p = []
    title_o, secs_o = old
    title_n, secs_n = new
    if title_o != title_n:
        p.append("topic title changed")
    # heading numbers ("# 4. Powers") are layout, not facts
    body_o = re.sub(r"(?m)^# \d+\.\s*", "# ", "\n".join(b for _, b in secs_o))
    body_n = re.sub(r"(?m)^# \d+\.\s*", "# ", "\n".join(b for _, b in secs_n))
    toks = set(re.findall(r"[a-z0-9]+", body_n.lower()))
    for x in problems(body_o, body_n):
        if x.startswith("bold terms lost"):
            # wording of a bold term may change (punctuation, order); lost only if its words are gone
            lost = [b for b in BOLD.findall(body_o) if not set(re.findall(r"[a-z0-9]+", b.lower())) <= toks]
            if len(lost) > max(1, len(set(BOLD.findall(body_o))) // 12):
                p.append(f"bold terms lost ({len(lost)}): " + "; ".join(sorted(set(lost))[:6]))
        else:
            p.append(x)
    go, gn = Counter(re.findall(r"!! (.*)", body_o)), Counter(re.findall(r"!! (.*)", body_n))
    if go != gn:
        p.append(f"gap lines differ ({sum(go.values())} -> {sum(gn.values())})")
    heads = [parse_head(h) for h, _ in secs_n]
    used = {k for _, f, _ in heads for k in f}
    missing = [k for k in range(len(secs_o)) if k not in used]
    if missing:
        p.append("input subsections in no from: " + ", ".join(f"S{k}" for k in missing))
    if any(k >= len(secs_o) for k in used):
        p.append("from: names an unknown subsection")
    had_u = any(h.endswith("| universal") for h, _ in secs_o)
    us = [i for i, (_, _, u) in enumerate(heads) if u]
    if had_u and us != [len(heads) - 1]:
        p.append("Universal angles page must be exactly one, and last")
    for (t, _, _), (_, b) in zip(heads, secs_n):
        if not t:
            p.append("page without a title")
        try:
            if not to_blocks(b, []):
                p.append(f"empty page: {t[:40]}")
        except Exception as e:
            p.append(f"page does not parse ({t[:40]}): {e}")
    return p


if __name__ == "__main__":
    book = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else None
    d = os.environ.get("TOPIC_DIR", "work/topic") + f"/b{book}"
    bad = total = 0
    for f in sorted(glob.glob(f"{d}/out_*.md")):
        n = f[-6:-3]
        if only and n != only:
            continue
        old, new = topics(open(f"{d}/in_{n}.md").read()), topics(open(f).read())
        for row in old:
            total += 1
            if row not in new:
                print(f"{n} ROW {row}: missing"); bad += 1; continue
            pr = check(old[row], new[row])
            if pr:
                bad += 1
                print(f"{n} ROW {row}: FAIL " + " | ".join(pr))
            else:
                print(f"{n} ROW {row}: OK ({len(old[row][1])} -> {len(new[row][1])} subsections)")
        for row in set(new) - set(old):
            print(f"{n} ROW {row}: unknown topic")
    print(f"{total - bad}/{total} topics pass")
