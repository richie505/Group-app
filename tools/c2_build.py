"""APPSC Complete 2.0's notes: data/c2/out/<n>.md (written from the MCQs, data/c2/INSTRUCTIONS.md) into
app/src/complete2/assets/book{1..6}.json. Every topic, page and page id stays as in APPSC Complete (so a Complete
backup restores here); only each page's text changes. A page with no MCQs says so; MCQs filed under a whole section
get a page of their own at the end of that section.

    python3 tools/c2_build.py
"""
import glob, json, os, re

SRC = "app/src/complete/assets"
DST = "app/src/complete2/assets"
EMPTY = [{"k": "n", "x": [["No MCQs on this subsection yet: nothing here to practise.", 4]]}]
WHOLE = "More from this topic's MCQs"


def runs(text):
    """'**Kalhana** — Rajatarangini' -> [["Kalhana", 1], [" — Rajatarangini", 0]]"""
    out = []
    for i, part in enumerate(text.split("**")):
        if part:
            out.append([part, 1 if i % 2 else 0])
    return out or [["", 0]]


def cells(line):
    line = line.strip().strip("|")
    return [runs(c.strip()) for c in line.split("|")]


def blocks(lines):
    out, i = [], 0
    while i < len(lines):
        l = lines[i].rstrip()
        s = l.strip()
        if not s:
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.fullmatch(r"\|?[\s:|-]+\|?", lines[i].strip()):
                    rows.append(cells(lines[i]))
                i += 1
            if len(rows) >= 2:
                out.append({"k": "t", "h": rows[0], "r": rows[1:]})
            elif rows:
                out.append({"k": "b", "x": [r for c in rows[0] for r in c + [[" · ", 0]]][:-1]})
            continue
        if s.startswith("###") or s.startswith("##") and not s.startswith("## SEC"):
            out.append({"k": "h", "x": runs(s.lstrip("#").strip())})
        elif re.match(r"^\s{2,}[-*•]\s", l):
            out.append({"k": "s", "x": runs(re.sub(r"^\s*[-*•]\s+", "", l))})
        elif re.match(r"^[-*•]\s", s):
            t = re.sub(r"^[-*•]\s+", "", s)
            r = runs(t)
            if t.startswith("★"):  # a fact a previous-year question asked
                r = [["★ ", 1]] + runs(t.lstrip("★ ").strip())
            out.append({"k": "b", "x": r})
        else:
            out.append({"k": "b", "x": runs(s)})
        i += 1
    return out


def parse_out():
    """'b:r:s' -> list of blocks."""
    pages = {}
    for f in sorted(glob.glob("data/c2/out/*.md"), key=lambda p: int(re.sub(r"\D", "", os.path.basename(p)) or 0)):
        cur, buf = None, []
        for line in open(f).read().split("\n") + ["## SEC END"]:
            m = re.match(r"^## SEC (\d+:\d+:-?\d+)", line)
            if m or line.startswith("# ROW"):
                if cur and buf:
                    b = blocks(buf)
                    if b:
                        pages[cur] = b
                cur, buf = (m.group(1) if m else None), []
            elif cur:
                buf.append(line)
    return pages


def pending():
    """Page ids of packets not written yet: those keep APPSC Complete's own text for now."""
    out = set()
    for f in glob.glob("data/c2/in/*.md"):
        if not os.path.exists(f.replace("/in/", "/out/")):
            out |= set(re.findall(r"^## SEC (\S+)", open(f).read(), re.M))
    return out


def main():
    os.makedirs(DST, exist_ok=True)
    pages = parse_out()
    wait = pending()
    done = empty = extra = kept = 0
    for b in range(1, 7):
        bk = json.load(open(f"{SRC}/book{b}.json"))
        ri = 0
        for u in bk["units"]:
            for r in u["rows"]:
                for si, s in enumerate(r["secs"]):
                    p = pages.get(f"{b}:{ri}:{si}")
                    if not p and f"{b}:{ri}:{si}" in wait:
                        kept += 1
                        continue
                    s["b"] = p if p else EMPTY
                    s.pop("cov", None)  # links to other pages' old text
                    done += bool(p)
                    empty += not p
                whole = pages.get(f"{b}:{ri}:-1")
                if whole:
                    r["secs"].append({"t": WHOLE, "badges": [], "p": r["secs"][-1].get("p", 0) if r["secs"] else 0, "b": whole})
                    extra += 1
                ri += 1
        json.dump(bk, open(f"{DST}/book{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"pages from MCQs: {done}, without MCQs: {empty}, whole-topic pages added: {extra}, old text kept (not written yet): {kept}")


if __name__ == "__main__":
    main()
