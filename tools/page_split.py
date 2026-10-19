"""Splits heavy notes pages into lighter ones at their own headings, for tools/topic_import.py.

    python3 tools/page_split.py <book> [rows e.g. 0-4,9]
writes $TOPIC_DIR (default work/split)/b<book>/in_000.md and out_000.md: every topic with a page over LIMIT
words that has 2+ headings ("# 1. Key facts"). Such a page becomes several pages of about TARGET words: its
heading blocks are packed in order, nothing is reworded or dropped, each new page renumbers its headings from 1
and is titled "<page title> — <its first heading>". A page without headings, a table-only page and the
Universal angles page stay as they are. Then: TOPIC_DIR=work/split IDS_VERSION=<v> python3 tools/topic_import.py <book>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from topic_export import topic

LIMIT, TARGET, TAIL = 220, 160, 45
A = "app/src/main/assets"


def nwords(md):
    md = re.sub(r"(?m)^\|[-| ]+\|$", "", md)
    return len(re.findall(r"[A-Za-z0-9]+", md))


def parts_of(body):
    """[(heading or None, text)] split at '# ' heading lines."""
    out, cur, head = [], [], None
    for line in body.splitlines():
        if line.startswith("# "):
            if cur or head is not None:
                out.append((head, "\n".join(cur)))
            head, cur = line, []
        else:
            cur.append(line)
    out.append((head, "\n".join(cur)))
    return [p for p in out if p[0] is not None or p[1].strip()]


def split_page(title, body):
    ps = parts_of(body)
    if nwords(body) <= LIMIT or sum(h is not None for h, _ in ps) < 2:
        return None
    groups, cur, w = [], [], 0
    for h, t in ps:
        n = nwords((h or "") + "\n" + t)
        if cur and w + n > TARGET and h is not None:
            groups.append(cur); cur, w = [], 0
        cur.append((h, t)); w += n
    if cur:
        if groups and sum(nwords((h or "") + t) for h, t in cur) < TAIL:
            groups[-1] += cur  # a short tail stays with the page before it
        else:
            groups.append(cur)
    if len(groups) < 2:
        return None
    pages = []
    for g in groups:
        heads = [re.sub(r"^#\s*(\d+\.\s*)?", "", h).strip() for h, _ in g if h]
        lines, k = [], 0
        for h, t in g:
            if h:
                k += 1
                lines.append(f"# {k}. " + re.sub(r"^#\s*(\d+\.\s*)?", "", h).strip())
            if t.strip():
                lines.append(t.strip("\n"))
        pages.append((f"{title} — {heads[0]}" if heads else title, "\n".join(lines)))
    return pages


def main():
    book = int(sys.argv[1])
    only = None
    if len(sys.argv) > 2:
        only = set()
        for part in sys.argv[2].split(","):
            a, _, b = part.partition("-")
            only |= set(range(int(a), int(b or a) + 1))
    notes = json.load(open(f"{A}/book{book}.json"))
    rows = [r for u in notes["units"] for r in u["rows"]]
    ins, outs, n_split, n_new = [], [], 0, 0
    for ri, r in enumerate(rows):
        if only is not None and ri not in only:
            continue
        src = topic(ri, r)
        chunks = re.split(r"(?m)^## ", src)
        out, changed = [chunks[0].rstrip()], False
        for si, ch in enumerate(chunks[1:]):
            head, _, body = ch.partition("\n")
            parts = [x.strip() for x in head.split(" | ")]  # "S3 | title [| universal]"
            t, universal = parts[1], "universal" in parts[2:]
            pages = None if universal else split_page(t, body.strip())
            if pages:
                changed, n_split, n_new = True, n_split + 1, n_new + len(pages)
                for pt, pb in pages:
                    out.append(f"## {pt} | from: S{si}\n{pb}")
            else:
                out.append(f"## {t} | from: S{si}" + (" | universal" if universal else "") + "\n" + body.strip())
        if changed:
            ins.append(src)
            outs.append("\n\n".join(out))
    d = os.environ.get("TOPIC_DIR", "work/split") + f"/b{book}"
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith(("in_", "out_")):
            os.remove(f"{d}/{f}")
    if ins:
        open(f"{d}/in_000.md", "w").write("\n\n".join(ins) + "\n")
        open(f"{d}/out_000.md", "w").write("\n\n".join(outs) + "\n")
    print(f"book {book}: {n_split} heavy pages -> {n_new} pages, in {len(ins)} topics")


if __name__ == "__main__":
    main()
