"""Checks the writers' structure of each topic's full notes (data/structure/out/<n>.md, rules in
data/structure/INSTRUCTIONS.md).

    python3 tools/structure_check.py <n>     (one packet)
    python3 tools/structure_check.py         (all packets: a summary)
"""
import os
import re
import sys


def read_in(n):
    topics = {}
    cur = None
    for line in open(f"data/structure/in/{n}.md"):
        if line.startswith("T "):
            cur = line[2:].split(" | ")[0].strip()
            topics[cur] = 0
        elif re.match(r"^P\d+ ", line):
            topics[cur] += 1
    return topics


def read_out(n):
    out, cur = {}, None
    p = f"data/structure/out/{n}.md"
    if not os.path.exists(p):
        return out
    for line in open(p):
        line = line.rstrip("\n")
        if line.startswith("T "):
            cur = line[2:].split(" | ")[0].strip()
            out[cur] = []
        elif line.startswith("G ") and cur is not None:
            head, _, nums = line[2:].rpartition(" | ")
            out[cur].append((head.strip(), [int(x) for x in re.findall(r"\d+", nums)]))
    return out


def problems(pages, groups):
    p = []
    nums = [x for _, ns in groups for x in ns]
    if sorted(nums) != list(range(1, pages + 1)):
        missing = sorted(set(range(1, pages + 1)) - set(nums))
        dup = sorted({x for x in nums if nums.count(x) > 1})
        extra = sorted(set(nums) - set(range(1, pages + 1)))
        p.append(f"pages wrong: missing {missing} repeated {dup} not in topic {extra}")
    if not groups:
        p.append("no groups")
    elif len(groups) > 7 or (len(groups) == 1 and pages > 3):
        p.append(f"{len(groups)} groups (2 to 7; 1 only for 3 pages or fewer)")
    for h, ns in groups:
        w = len(h.split())
        if not 1 <= w <= 6 or re.search(r"[*#`|]|^\d", h):
            p.append(f"heading '{h}': 2 to 6 plain words")
        if not ns:
            p.append(f"heading '{h}' has no pages")
    return p


def check(n, quiet=False):
    src, out = read_in(n), read_out(n)
    bad = 0
    for t, pages in src.items():
        if t not in out:
            bad += 1
            if not quiet:
                print(f"{t}: missing")
            continue
        for pr in problems(pages, out[t]):
            bad += 1
            if not quiet:
                print(f"{t}: {pr}")
    if not quiet:
        print(f"packet {n}: {len(src)} topics, {len(out)} written, problems {bad}")
    return len(src), len(out), bad


if __name__ == "__main__":
    if len(sys.argv) > 1:
        check(sys.argv[1])
    else:
        n = 0
        while os.path.exists(f"data/structure/in/{n}.md"):
            t, w, b = check(n, quiet=True)
            print(f"packet {n}: {t} topics, {w} written, problems {b}")
            n += 1
