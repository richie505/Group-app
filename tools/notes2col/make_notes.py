"""APPSC Complete notes (book1-6.json, every line) as two-column A4 PDFs.

    python3 tools/notes2col/make_notes.py out_dir [book ...]   -> out_dir/bookN.html  (then tools/notes2col/pdf.js)
"""
import json, sys, html, os, re

A = "app/src/complete/assets"
TITLES = {1: "History & Culture", 2: "Polity & Governance", 3: "Economy", 4: "Geography",
          5: "Science, Technology & Environment", 6: "Current Affairs"}

def runs(x):
    return "".join(f"<b>{html.escape(t)}</b>" if b else html.escape(t) for t, b in x or [])

CSS = """
@page { size: A4; margin: 11mm 9mm 13mm 9mm; }
body { font-family: 'Noto Sans','DejaVu Sans',Arial,sans-serif; font-size: 8.3pt; line-height: 1.32; color: #111; margin: 0; }
.cover { page-break-after: always; padding-top: 75mm; text-align: center; }
.cover h1 { font-size: 26pt; color: #1e293b; margin: 0 0 4mm; } .cover h2 { font-size: 18pt; color: #1e3a8a; } .cover p { color: #475569; font-size: 10.5pt; }
.unit { page-break-before: always; }
h1.u { font-size: 12.5pt; color: #fff; background: #1e293b; padding: 5px 8px; border-radius: 4px; margin: 0 0 3mm; }
.cols { column-count: 2; column-gap: 6mm; column-rule: 0.6px solid #cbd5e1; }
h2.r { font-size: 10.2pt; color: #fff; background: #1e3a8a; padding: 3px 6px; border-radius: 3px; margin: 3mm 0 1mm; break-after: avoid; }
.meta { font-size: 7pt; color: #475569; margin: 0 0 1.5mm; }
h3.s { font-size: 9.2pt; color: #1e3a8a; border-bottom: 1.2px solid #1e3a8a; margin: 2.5mm 0 1mm; break-after: avoid; }
h4 { font-size: 8.6pt; color: #9a3412; margin: 1.8mm 0 0.6mm; break-after: avoid; }
ul { margin: 0 0 0.8mm; padding-left: 3.6mm; } li { margin: 0 0 0.5mm; }
.x { background: #fef3c7; border-left: 2.5px solid #f59e0b; padding: 1px 4px; margin: 0.8mm 0; }
.w { background: #fee2e2; border-left: 2.5px solid #ef4444; padding: 1px 4px; margin: 0.8mm 0; }
.p { color: #475569; font-style: italic; margin: 0.8mm 0; }
.n { color: #64748b; font-size: 6.6pt; margin: 0.6mm 0 1mm; }
table { border-collapse: collapse; width: 100%; margin: 1mm 0 1.5mm; font-size: 7.4pt; }
th, td { border: 0.6px solid #94a3b8; padding: 1.4px 3px; vertical-align: top; text-align: left; }
th { background: #e2e8f0; } tr { break-inside: avoid; }
table.wide { column-span: all; font-size: 7.2pt; }
"""

def build(b):
    book = json.load(open(f"{A}/book{b}.json"))
    out = [f"<html><head><meta charset='utf-8'><title>{html.escape(TITLES[b])}</title><style>{CSS}</style></head><body>",
           f"<div class='cover'><h1>APPSC Complete — Notes</h1><h2>{html.escape(TITLES[b])}</h2>"
           f"<p>Every line of the app's updated notes (book {b}), in two columns.</p>"
           "<p>★ yellow = most-asked angle · red = settled fact / trap · grey = sources</p></div>"]
    pieces = 0
    for u in book["units"]:
        rows = [r for r in u["rows"] if any(s["b"] for s in r["secs"])]
        if not rows: continue
        out.append(f"<div class='unit'><h1 class='u'>{html.escape(u['title'])}</h1><div class='cols'>")
        for r in rows:
            out.append(f"<h2 class='r'>{html.escape(r['title'])}</h2>")
            meta = " · ".join(x for x in [", ".join(r.get("codes") or []), r.get("tag", ""), ("Asked: " + r["pyq"]) if r.get("pyq") else ""] if x)
            if r.get("sub"): meta += (" · " if meta else "") + "; ".join(r["sub"])
            if meta: out.append(f"<div class='meta'>{html.escape(meta)}</div>")
            for s in r["secs"]:
                if not s["b"]: continue
                out.append(f"<h3 class='s'>{html.escape(s['t'])}</h3>")
                inul = False
                for bl in s["b"]:
                    k = bl["k"]
                    if k == "b":
                        if not inul: out.append("<ul>"); inul = True
                        out.append(f"<li>{runs(bl['x'])}</li>"); pieces += 1; continue
                    if inul: out.append("</ul>"); inul = False
                    if k == "h": out.append(f"<h4>{runs(bl['x'])}</h4>")
                    elif k == "x": out.append(f"<div class='x'>★ {runs(bl['x'])}</div>")
                    elif k == "s": out.append(f"<div class='w'>{runs(bl['x'])}</div>")
                    elif k == "p": out.append(f"<div class='p'>{runs(bl['x'])}</div>")
                    elif k == "n": out.append(f"<div class='n'>{runs(bl['x'])}</div>")
                    elif k == "t":
                        cls = " class='wide'" if len(bl["h"]) >= 5 else ""
                        t = f"<table{cls}><tr>" + "".join(f"<th>{runs(h) if isinstance(h, list) else html.escape(str(h))}</th>" for h in bl["h"]) + "</tr>"
                        for row in bl["r"]:
                            t += "<tr>" + "".join(f"<td>{runs(c)}</td>" for c in row) + "</tr>"
                        out.append(t + "</table>")
                    pieces += 1
                if inul: out.append("</ul>")
        out.append("</div></div>")
    out.append("</body></html>")
    return "".join(out), pieces

def check(b, h):
    """every text run of the notes must appear in the html"""
    book = json.load(open(f"{A}/book{b}.json")); body = html.unescape(re.sub(r"<[^>]+>", "", h)); miss = n = 0
    def chk(x):
        nonlocal miss, n
        for t, _ in x or []:
            t = t.strip()
            if t: n += 1; miss += t not in body
    for u in book["units"]:
        for r in u["rows"]:
            for s in r["secs"]:
                for bl in s["b"]:
                    if bl["k"] == "t":
                        for h_ in bl["h"]: chk(h_ if isinstance(h_, list) else [[str(h_), 0]])
                        for row in bl["r"]:
                            for c in row: chk(c)
                    else: chk(bl.get("x"))
    return n, miss

if __name__ == "__main__":
    od = sys.argv[1]; os.makedirs(od, exist_ok=True)
    for b in [int(x) for x in sys.argv[2:]] or range(1, 7):
        h, p = build(b)
        open(f"{od}/book{b}.html", "w").write(h)
        print(f"book{b}", p, "blocks; text pieces checked/missing:", *check(b, h))
