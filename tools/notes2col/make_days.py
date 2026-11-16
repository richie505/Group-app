"""Day-wise two-column notes PDFs following the app's 78-day plan (plan.json).
    python3 tools/notes2col/make_days.py out_dir   -> out_dir/Day-NN_....html + list.txt (then pdf_many.js)
"""
import json, sys, os, html, re
sys.path.insert(0, os.path.dirname(__file__))
from make_notes import CSS, render_row, A, TITLES

DCSS = CSS + """
.sched { page-break-after: always; }
.sched h1 { font-size: 20pt; color: #1e293b; margin: 0 0 2mm; } .sched .dt { font-size: 11pt; color: #1e3a8a; font-weight: 700; }
.sched .ph { display:inline-block; background:#1e3a8a; color:#fff; padding:2px 8px; border-radius:3px; font-size:9pt; margin:2mm 0; }
.sched table { font-size: 9pt; } .sched td, .sched th { padding: 3px 5px; } .sched p { font-size: 9.5pt; }
.pri { font-weight:700; } .HIGH { color:#b91c1c; } .MEDIUM { color:#b45309; } .LIGHT { color:#15803d; }
"""

def main(od):
    os.makedirs(od, exist_ok=True)
    plan = json.load(open(f"{A}/plan.json"))
    books = {b: [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]] for b in range(1, 7)}
    names = []; used = set()
    for d in plan["days"]:
        out = [f"<html><head><meta charset='utf-8'><title>Day {d['n']}</title><style>{DCSS}</style></head><body><div class='sched'>",
               f"<h1>Day {d['n']} of {len(plan['days'])}</h1><div class='dt'>{html.escape(d['dow'])} {html.escape(d['date'])} · {html.escape(d.get('left',''))}</div>",
               f"<div class='ph'>{html.escape(d.get('phase',''))} · {html.escape(d.get('focus',''))}</div>"]
        out += [f"<p>{html.escape(x)}</p>" for x in d.get("brief", [])]
        out.append("<h3 class='s'>Timetable</h3><table><tr><th>Time</th><th>Block</th><th>Task</th></tr>"
                   + "".join(f"<tr><td>{html.escape(t['time'])}</td><td><b>{html.escape(t['block'])}</b></td><td>{html.escape(t['task'])}</td></tr>" for t in d.get("tasks", [])) + "</table>")
        out.append("<h3 class='s'>Today's topics</h3><table><tr><th>#</th><th>Subject</th><th>Topic</th><th>Codes</th><th>Asked</th><th>Priority</th></tr>")
        for i, r in enumerate(d.get("rows", []), 1):
            out.append(f"<tr><td>{i}</td><td>{TITLES[r['ref'][0]]}</td><td>{html.escape(r['topic'])}</td><td>{html.escape(', '.join(r.get('codes') or []))}</td>"
                       f"<td>{html.escape(str(r.get('pyq','')))}</td><td class='pri {r.get('pri','')}'>{r.get('pri','')}</td></tr>")
        out.append("</table></div>")
        cur = None
        for r in d.get("rows", []):
            b, i = r["ref"]; used.add((b, i))
            if b != cur:
                if cur is not None: out.append("</div>")
                out.append(f"<div class='unit' style='page-break-before:auto'><h1 class='u'>{TITLES[b]}</h1><div class='cols'>"); cur = b
            render_row(books[b][i], out)
        if cur is not None: out.append("</div></div>")
        out.append("</body></html>")
        focus = re.sub(r"[^A-Za-z]+", "-", d.get("focus", "").title()).strip("-")[:40]
        name = f"Day-{d['n']:02d}_{d['date']}_{focus}"
        open(f"{od}/{name}.html", "w").write("".join(out)); names.append(name)
    tot = sum(len(v) for v in books.values())
    open(f"{od}/list.txt", "w").write("\n".join(names))
    print(len(names), "days;", len(used), "of", tot, "topics placed")

if __name__ == "__main__": main(sys.argv[1])
