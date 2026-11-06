"""Notes to the blueprint, step 1: for each blueprint unit (APPSC_Notes_Blueprint_G1-Prelims__G2.md, section 5),
a source packet for its writer: the unit's spec (rows, tier, page budget, keyword angles, latest-paper questions)
and every line the app's notes hold for its rows (APPSC Complete's full notes, then its MCQ notes), as
data/blueprint/src/<unit>.md. The unit's rows are matched to the app's topics by syllabus code.

    python3 tools/blueprint_src.py <blueprint.md> [U0001 U0275 ...]     (no units: all of them)
"""
import json
import re
import sys

A = "app/src/complete/assets"
N = "app/src/complete/mcqnotes"


def units(path):
    t = open(path).read()
    t = t[t.index("## 5. Unit blueprint"):]
    parts = re.split(r"\n#### (U\d{4}) \| ", t)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("\n### ")[0].strip()
        rows = re.search(r"\*\*Rows:\*\* (.*)", body)
        codes = re.findall(r"(?:^|; )([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+) - ", rows.group(1)) if rows else []
        out[parts[i]] = (body, codes)
    return out


def text(rs):
    return "".join(r[0] for r in rs)


def lines(sec):
    for x in sec["b"]:
        if x.get("k") == "t":
            head = " | ".join(text(c) for c in x.get("h", []))
            if head.strip(" |"):
                yield "| " + head + " |"
            for r in x.get("r", []):
                yield "| " + " | ".join(text(c) for c in r) + " |"
        elif "x" in x and x.get("k") != "n":
            t = text(x["x"]).strip()
            if t:
                yield ("## " if x["k"] == "h" else "- ") + t


def topics():
    idx = json.load(open(f"{A}/index.json"))
    by = {}
    for b in idx["books"]:
        for ri, r in enumerate(b["rows"]):
            for c in r["codes"]:
                by.setdefault(c, []).append((b["id"], ri))
    return by


if __name__ == "__main__":
    import os
    us = units(sys.argv[1])
    want = sys.argv[2:] or list(us)
    by = topics()
    books = {b: [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]] for b in range(1, 7)}
    mbooks = {b: [r for u in json.load(open(f"{N}/book{b}.json"))["units"] for r in u["rows"]] for b in range(1, 7)}
    os.makedirs("data/blueprint/src", exist_ok=True)
    for u in want:
        body, codes = us[u]
        rows = sorted({x for c in codes for x in by.get(c, [])})
        out = [f"# {u} | {body}", ""]
        for b, ri in rows:
            out.append(f"# NOTES OF APP TOPIC {b}:{ri} - {books[b][ri]['title']}")
            for s in books[b][ri]["secs"]:
                out.append(f"### {s['t']}")
                out += list(lines(s))
            out.append(f"# MCQ NOTES OF APP TOPIC {b}:{ri}")
            for s in mbooks[b][ri]["secs"]:
                ls = list(lines(s))
                if ls:
                    out.append(f"### {s['t']}")
                    out += ls
        open(f"data/blueprint/src/{u}.md", "w").write("\n".join(out) + "\n")
        print(u, rows, len(" ".join(out).split()), "words")


def ca_split(path):
    """current-affairs units: one packet per app topic (a period), <unit>-<k>.md, k = 1.. in topic order"""
    import os
    us = units(path)
    by = topics()
    books = {b: [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]] for b in range(1, 7)}
    mbooks = {b: [r for u in json.load(open(f"{N}/book{b}.json"))["units"] for r in u["rows"]] for b in range(1, 7)}
    for n in range(812, 830):
        u = f"U{n:04d}"
        body, codes = us[u]
        rows = sorted({x for c in codes for x in by.get(c, [])})
        for k, (b, ri) in enumerate(rows, 1):
            title = books[b][ri]["title"]
            out = [f"# {u}-{k} | {body}", "", f"**This packet is one period of the unit:** {title}. Write the unit's notes "
                   f"for this period only, keeping its title's period; no upper word limit (keep every MCQ fact).", ""]
            out.append(f"# NOTES OF APP TOPIC {b}:{ri} - {title}")
            for s in books[b][ri]["secs"]:
                out.append(f"### {s['t']}")
                out += list(lines(s))
            out.append(f"# MCQ NOTES OF APP TOPIC {b}:{ri}")
            for s in mbooks[b][ri]["secs"]:
                ls = list(lines(s))
                if ls:
                    out.append(f"### {s['t']}")
                    out += ls
            open(f"data/blueprint/src/{u}-{k}.md", "w").write("\n".join(out) + "\n")
            print(f"{u}-{k}", title[:40], len(" ".join(out).split()))
