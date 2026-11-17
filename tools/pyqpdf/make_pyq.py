"""APPSC Complete's past-paper questions (PYQs, ids "y") as two-column A4 PDFs: one per subject (book), its units
and topics in the app's order; each topic's questions, then that topic's answers with explanations.

    python3 tools/pyqpdf/make_pyq.py out_dir      -> out_dir/<n>.html  (then node tools/pyqpdf/pdf.js in.html out.pdf)
"""
import json, sys, html, os

A = "app/src/complete/assets"
E = html.escape
TAGS = {"updated": "Updated to the latest", "disputed": "Disputed key", "added": "Option added", "outdated": "Outdated"}
CSS = """
@page { size: A4; margin: 11mm 9mm 13mm 9mm; }
body { font-family: 'Noto Sans','DejaVu Sans',Arial,sans-serif; font-size: 8.4pt; line-height: 1.32; color: #111; margin: 0; }
.cover { page-break-after: always; padding-top: 70mm; text-align: center; }
.cover h1 { font-size: 24pt; color: #1e293b; margin: 0 0 4mm; } .cover h2 { font-size: 17pt; color: #1e3a8a; }
.cover p { color: #475569; font-size: 10.5pt; } .toc { text-align: left; margin: 10mm auto 0; width: 150mm; font-size: 9pt; color: #334155; }
.unit { page-break-before: always; }
h1.u { font-size: 12.5pt; color: #fff; background: #1e293b; padding: 5px 8px; border-radius: 4px; margin: 0 0 3mm; }
.cols { column-count: 2; column-gap: 6mm; column-rule: 0.6px solid #cbd5e1; }
h2.r { font-size: 10pt; color: #fff; background: #1e3a8a; padding: 3px 6px; border-radius: 3px; margin: 3mm 0 1mm; break-after: avoid; }
.meta { font-size: 7pt; color: #475569; margin: 0 0 1.5mm; }
.q { break-inside: avoid; margin: 0 0 2mm; }
.q .s { white-space: pre-wrap; } .q .src { color: #64748b; font-size: 6.8pt; }
.o { margin: 0.3mm 0 0 3mm; }
h3.k { font-size: 9pt; color: #166534; border-bottom: 1.2px solid #166534; margin: 2.5mm 0 1mm; break-after: avoid; }
.a { margin: 0 0 1.3mm; font-size: 7.6pt; } .a b { color: #166534; } .a .x { color: #334155; } .a .t { color: #9a3412; font-weight: bold; }
"""


def answer(q):
    if q.get("k") == "f":
        return q.get("at") or "—"
    a = q.get("a", -1)
    return f"({a + 1}) {q['o'][a]}" if 0 <= a < len(q["o"]) else "No official key"


def book(b, idx, mcq):
    bk = idx["books"][b - 1]
    rows = mcq["rows"]
    n_all = sum(1 for qs in rows.values() for q in qs if q["id"].startswith("y"))
    out = [f"<html><head><meta charset='utf-8'><title>APPSC PYQs - {E(bk['short'])}</title><style>{CSS}</style></head><body>"]
    toc = []
    for ui, u in enumerate(bk["units"]):
        n = sum(1 for ri, r in enumerate(bk["rows"]) if r["u"] == ui for q in rows.get(str(ri), []) if q["id"].startswith("y"))
        toc.append(f"<div>{E(u['code'])} · {E(u['title'])} — {n} PYQs</div>")
    out.append(f"<div class='cover'><h1>APPSC Previous Year Questions</h1><h2>{E(bk['title'])}</h2>"
               f"<p>{n_all} PYQs, topic-wise as in the APPSC Complete app · each topic's answers and explanations follow its questions</p>"
               f"<div class='toc'>{''.join(toc)}</div></div>")
    for ui, u in enumerate(bk["units"]):
        topics = [(ri, r) for ri, r in enumerate(bk["rows"]) if r["u"] == ui]
        topics = [(ri, r, [q for q in rows.get(str(ri), []) if q["id"].startswith("y")]) for ri, r in topics]
        topics = [t for t in topics if t[2]]
        if not topics:
            continue
        out.append(f"<div class='unit'><h1 class='u'>{E(u['code'])} · {E(u['title'])}</h1><div class='cols'>")
        for ri, r, qs in topics:
            meta = " · ".join(x for x in [", ".join(r.get("codes") or []), f"{len(qs)} PYQs", ("Asked: " + r["pyq"]) if r.get("pyq") else ""] if x)
            out.append(f"<h2 class='r'>{E(r['title'])}</h2><div class='meta'>{E(meta)}</div>")
            for i, q in enumerate(qs, 1):
                opts = "" if q.get("k") == "f" else "".join(f"<div class='o'>({j + 1}) {E(o)}</div>" for j, o in enumerate(q["o"]))
                out.append(f"<div class='q'><b>{i}.</b> <span class='s'>{E(q['s'])}</span> <span class='src'>[{E(q.get('src', ''))}]</span>{opts}</div>")
            out.append("<h3 class='k'>Answers &amp; explanations</h3>")
            for i, q in enumerate(qs, 1):
                tg = " ".join(f"<span class='t'>[{TAGS[t]}]</span>" for t in q.get("tg", []) if t in TAGS)
                x = (q.get("x") or "").replace("\n", " ")
                out.append(f"<div class='a'><b>{i}. {E(answer(q))}</b> {tg} <span class='x'>{E(x)}</span></div>")
        out.append("</div></div>")
    out.append("</body></html>")
    return "".join(out), n_all


if __name__ == "__main__":
    od = sys.argv[1]
    os.makedirs(od, exist_ok=True)
    idx = json.load(open(f"{A}/index.json"))
    tot = 0
    for b in range(1, 7):
        h, n = book(b, idx, json.load(open(f"{A}/mcq{b}.json")))
        open(f"{od}/{b}.html", "w").write(h)
        tot += n
        print(b, n)
    print("total", tot)
