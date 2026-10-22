"""Checks merged topics (guide: tools/merge_guide.md) against their Prep pages and ROCKET blocks.

    python3 tools/merge_check.py <book> [NNN]
Per topic: every number and gap line of both sources kept, nearly all bold terms, every S and R named in some
"from:", the Universal angles page last, each page parses.
"""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from restructure_check import problems, BOLD
from structured_md import to_blocks
from topic_check import topics, parse_head


def split_in(text):
    """{row: (title, prep secs [(head, body)], rocket blocks [(head, body)])}"""
    out = {}
    for chunk in re.split(r"^=== ROW ", text, flags=re.M)[1:]:
        prep, _, rocket = chunk.partition("\n=== ROCKET")
        t = topics("=== ROW " + prep)
        row, (title, secs) = next(iter(t.items()))
        rk = [(s.partition("\n")[0].strip(), s.partition("\n")[2].strip()) for s in re.split(r"^## ", rocket, flags=re.M)[1:]]
        out[row] = (title, secs, rk)
    return out


def heads(h):
    parts = [p.strip() for p in h.split(" | ")]
    src = next((p for p in parts if p.startswith("from:")), "")
    return parts[0], [int(x) for x in re.findall(r"S(\d+)", src)], [int(x) for x in re.findall(r"R(\d+)", src)], "universal" in parts[1:]


def not_here(text):
    """{row: {R numbers the topic sent back}} from '=== NOT HERE: R8, R9' lines."""
    out = {}
    for chunk in re.split(r"^=== ROW ", text, flags=re.M)[1:]:
        row = int(chunk.partition(" | ")[0])
        m = re.search(r"^=== NOT HERE:(.*)$", chunk, flags=re.M)
        out[row] = {int(x) for x in re.findall(r"R(\d+)", m.group(1))} if m else set()
    return out


def check(old, new, sent_back=frozenset()):
    title_o, secs_o, rk = old
    title_n, secs_n = new
    p = []
    if title_o != title_n:
        p.append("topic title changed")
    strip = lambda s: re.sub(r"(?m)^# \d+\.\s*", "# ", re.sub(r"(?m)^~~.*$", "", s))
    body_o = strip("\n".join(b for _, b in secs_o) + "\n" + "\n".join(b for i, (_, b) in enumerate(rk) if i not in sent_back))
    body_n = strip("\n".join(b for _, b in secs_n))
    toks = set(re.findall(r"[a-z0-9]+", body_n.lower()))
    for x in problems(body_o, body_n):
        if x.startswith("bold terms lost"):
            lost = [b for b in BOLD.findall(body_o) if not set(re.findall(r"[a-z0-9]+", b.lower())) <= toks]
            if len(lost) > max(1, len(set(BOLD.findall(body_o))) // 15):
                p.append(f"bold terms lost ({len(lost)}): " + "; ".join(sorted(set(lost))[:6]))
        else:
            p.append(x)
    hs = [heads(h) for h, _ in secs_n]
    s_used = {k for _, s, _, _ in hs for k in s}
    r_used = {k for _, _, r, _ in hs for k in r} | set(sent_back)
    miss = [f"S{k}" for k in range(len(secs_o)) if k not in s_used] + [f"R{k}" for k in range(len(rk)) if k not in r_used]
    if miss:
        p.append("in no from: " + ", ".join(miss))
    if any(k >= len(secs_o) for k in s_used) or any(k >= len(rk) for k in r_used):
        p.append("from: names an unknown page or block")
    had_u = any(h.endswith("| universal") for h, _ in secs_o)
    us = [i for i, h in enumerate(hs) if h[3]]
    if had_u and us != [len(hs) - 1]:
        p.append("Universal angles page must be exactly one, and last")
    for (t, _, _, _), (_, b) in zip(hs, secs_n):
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
    d = os.environ.get("TOPIC_DIR", "work/merge") + f"/b{book}"
    bad = total = 0
    for f in sorted(glob.glob(f"{d}/out_*.md")):
        n = f[-6:-3]
        if only and n != only:
            continue
        out_text = open(f).read()
        old, back = split_in(open(f"{d}/in_{n}.md").read()), not_here(out_text)
        new = topics(re.sub(r"(?m)^=== NOT HERE:.*$", "", out_text))
        for row in old:
            total += 1
            if row not in new:
                print(f"{n} ROW {row}: missing"); bad += 1; continue
            pr = check(old[row], new[row], back.get(row, set()))
            if pr:
                bad += 1
                print(f"{n} ROW {row}: FAIL " + " | ".join(pr))
            else:
                print(f"{n} ROW {row}: OK ({len(old[row][1])} Prep pages + {len(old[row][2])} ROCKET blocks -> {len(new[row][1])} pages)")
    print(f"{total - bad}/{total} topics pass")
