"""Checks rewritten pages against the originals: every number and gap line kept, tables kept, nearly all bold terms.

    python3 tools/restructure_check.py 2            -> report for all out_NNN.md
    python3 tools/restructure_check.py 2 007        -> one batch
Facts inside source citations ("(TH, 26 Jan 2026)", "(IYB 2026)", [GK]) may go with them.
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))

SOURCES = r"(?:TH|APP|CDI|CDX|LENSD|LENS|IYB|UPSC notes|APPCA|APSES|VIS|ES|PIB|Laxmikanth|GK)"
CITE = re.compile(r"\((?:[^()]*;\s*)?" + SOURCES + r"\b[^()]*\)|\[GK\]")
NUM = re.compile(r"\d+(?:[.,:/]\d+)*")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def pages(text):
    out = {}
    for chunk in re.split(r"^=== ", text, flags=re.M)[1:]:
        head, _, body = chunk.partition("\n")
        out[head.split(" | ")[0].strip()] = (head, body.strip())
    return out


def norm(s):
    s = s.replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^\w₹%:./,'-]+", " ", s.lower()).strip()


def problems(old, new):
    p = []
    plain_old = CITE.sub(" ", old)
    flat_new = norm(new.replace("**", ""))
    new_nums = set(NUM.findall(new.replace("**", "")))
    for n in set(NUM.findall(plain_old.replace("**", ""))):
        if n not in new_nums and n + ".0" not in new_nums and not (len(n) == 1 and re.search(r"\b" + n + r"\b", new)):
            p.append(f"number {n}")
    gaps_old = re.findall(r"!! (.*)", old)
    for g in gaps_old:
        if "!! " + g.strip() not in new:
            p.append(f"gap line changed: {g[:60]}")
    for t in re.findall(r"<<table \d+>>", old):
        if new.count(t) != 1:
            p.append(f"{t} missing or repeated")
    bold = {norm(b) for b in BOLD.findall(CITE.sub(" ", old)) if len(norm(b)) > 2}
    lost = [b for b in bold if b not in flat_new]
    if bold and len(lost) > max(1, len(bold) // 12):
        p.append(f"bold terms lost ({len(lost)}/{len(bold)}): " + "; ".join(sorted(lost)[:6]))
    return p


if __name__ == "__main__":
    book = sys.argv[1]
    d = f"work/restructure/{os.environ.get('RS_PREFIX', 'b')}{book}"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    bad = total = 0
    for f in sorted(glob.glob(f"{d}/out_*.md")):
        n = f[-6:-3]
        if only and n != only:
            continue
        old, new = pages(open(f"{d}/in_{n}.md").read()), pages(open(f).read())
        for pid in old:
            total += 1
            if pid not in new:
                print(f"{n} {pid}: page missing"); bad += 1; continue
            pr = problems(old[pid][1], new[pid][1])
            if pr:
                bad += 1
                print(f"{n} {pid}: " + " | ".join(pr))
        for pid in set(new) - set(old):
            print(f"{n} {pid}: unknown page")
    print(f"{total - bad}/{total} pages pass")
