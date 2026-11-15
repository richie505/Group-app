"""Mind-map PDFs of APPSC Complete's notes (every line kept), in the style of 'Mind Mapping Lectures':
a dark root box on the left (the topic), its subsections as blue boxes, and their headings, points and table rows
branching to the right.

    python3 tools/mindmap/make_mindmap.py out_dir book[:row,row,...] ...   -> out_dir/bookN.html (then pdf.js)
"""
import json, re, sys, html, os

A = "app/src/complete/assets"
TITLES = {1: "History & Culture", 2: "Polity & Governance", 3: "Economy", 4: "Geography",
          5: "Science, Technology & Environment", 6: "Current Affairs"}

def runs(x):
    """[[text, bold], ...] -> html"""
    out = []
    for t, b in x or []:
        t = html.escape(t)
        out.append(f"<b>{t}</b>" if b else t)
    return "".join(out)

def plain(x): return "".join(t for t, _ in x or [])

class N:
    def __init__(self, label, cls="", kids=None):
        self.label, self.cls, self.kids = label, cls, kids or []

def bullet_node(x):
    """'**Lead:** rest' -> node(lead) -> leaf(rest); else a leaf."""
    if x and x[0][1] and len(x) > 1:
        lead = x[0][0].strip()
        rest = x[1:]
        if lead.endswith(":") or lead.endswith("–") or (len(lead) <= 40 and plain(rest).lstrip().startswith(("–", "-", "→", ":", "="))):
            r = runs(rest).strip()
            r = re.sub(r"^(–|-|→|:|=)\s*", "", r)
            return N(html.escape(lead.rstrip(":–").strip()), "mid", [N(r, "leaf")])
    return N(runs(x), "leaf")

def table_node(bl):
    heads = [plain(h) for h in bl["h"]]
    node = N(" | ".join(html.escape(h) for h in heads), "thead")
    for row in bl["r"]:
        cells = [runs(c) for c in row]
        if not cells: continue
        first = cells[0] or "—"
        rest = []
        for i, c in enumerate(cells[1:], 1):
            if not re.sub("<[^>]+>", "", c).strip(): continue
            h = heads[i] if i < len(heads) else ""
            rest.append(N((f"<span class='hd'>{html.escape(h)}:</span> " if h and len(cells) > 2 else "") + c, "leaf"))
        node.kids.append(N(first, "mid", rest))
    return node

def sec_tree(sec):
    """A subsection as a node: its blocks, grouped under its headings."""
    root = N(html.escape(sec["t"]), "sub")
    cur = root
    for bl in sec["b"]:
        k = bl["k"]
        if k == "h":
            cur = N(runs(bl["x"]), "head"); root.kids.append(cur)
        elif k == "t":
            cur.kids.append(table_node(bl))
        elif k == "b":
            cur.kids.append(bullet_node(bl["x"]))
        elif k == "x":
            cur.kids.append(N("★ " + runs(bl["x"]), "leaf star"))
        elif k == "s":
            cur.kids.append(N(runs(bl["x"]), "leaf warn"))
        elif k == "p":
            cur.kids.append(N(runs(bl["x"]), "leaf note"))
        elif k == "n":
            root.kids.append(N(runs(bl["x"]), "leaf src"))
    return root

def render(n, depth=0):
    box = f"<div class='box {n.cls}'>{n.label}</div>"
    if not n.kids:
        return f"<div class='nd'>{box}</div>"
    kids = "".join(f"<div class='kid'>{render(k, depth + 1)}</div>" for k in n.kids)
    return f"<div class='nd'>{box}<div class='kids'>{kids}</div></div>"

CSS = """
@page { size: A4; margin: 10mm 8mm 12mm 8mm; }
body { font-family: 'Noto Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 8.4pt; color: #111; margin: 0; }
.cover { page-break-after: always; padding-top: 70mm; text-align: center; }
.cover h1 { font-size: 24pt; color: #1e293b; } .cover p { color: #475569; font-size: 11pt; }
.topic { page-break-before: always; }
.thead1 { display:flex; align-items:center; gap: 6mm; margin: 0 0 4mm; }
.troot { background: #1e293b; color: #fff; font-size: 15pt; font-weight: 700; padding: 8px 14px; border-radius: 6px; max-width: 120mm; }
.tmeta { background: #6b8fc7; color:#fff; font-size: 9.5pt; padding: 6px 10px; border-radius: 6px; max-width: 70mm; }
.map { margin: 0 0 6mm; }
/* tree: box on the left, children stacked on the right joined by a bracket line */
.nd { display: flex; align-items: center; }
.kids { display: flex; flex-direction: column; justify-content: center; margin-left: 14px; position: relative; }
.kid { position: relative; padding: 2px 0 2px 14px; break-inside: avoid; }
.kid::before { content: ''; position: absolute; left: 0; top: 50%; width: 14px; border-top: 1px solid #333; }
.kid::after { content: ''; position: absolute; left: 0; top: 0; bottom: 0; border-left: 1px solid #333; }
.kid:first-child::after { top: 50%; } .kid:last-child::after { bottom: 50%; }
.kid:only-child::after { display: none; }
.kids::before { content: ''; position: absolute; left: -14px; top: 50%; width: 14px; border-top: 1px solid #333; }
.box { border-radius: 4px; padding: 3px 6px; line-height: 1.28; }
.box.sub { background: #1e3a8a; color: #fff; font-weight: 700; font-size: 9.6pt; max-width: 40mm; padding: 6px 8px; }
.box.head { background: #dbe4f3; color: #0f172a; font-weight: 700; max-width: 38mm; border: 1px solid #94a3b8; }
.box.thead { background: #e2e8f0; color: #1e293b; font-weight: 700; max-width: 36mm; border: 1px solid #94a3b8; font-size: 7.8pt; }
.box.mid { background: #fff; border: 1px solid #64748b; max-width: 40mm; font-weight: 600; }
.box.leaf { background: #f8fafc; border-bottom: 1px solid #94a3b8; border-radius: 0; max-width: 92mm; padding: 2px 4px; }
.box.star { background: #fef3c7; border: 1px solid #f59e0b; border-radius: 4px; }
.box.warn { background: #fee2e2; border: 1px solid #f87171; border-radius: 4px; }
.box.note { background: #f1f5f9; color: #475569; font-style: italic; }
.box.src { background: none; border: none; color: #64748b; font-size: 6.8pt; max-width: 100mm; }
.hd { color: #475569; font-weight: 600; }
"""

def build(b, rf=None):
    book = json.load(open(f"{A}/book{b}.json"))
    rows = [(u, r) for u in book["units"] for r in u["rows"]]
    out = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>",
           f"<div class='cover'><h1>APPSC Mind-Map Notes</h1><h1 style='font-size:18pt;color:#1e3a8a'>{html.escape(TITLES[b])}</h1>"
           f"<p>Every line of APPSC Complete's notes (book {b}) as mind maps — one map per subsection.</p>"
           "<p>★ = most-asked angle · red = settled / trap · grey = sources</p></div>"]
    n = 0
    for ri, (u, r) in enumerate(rows):
        if rf is not None and ri not in rf: continue
        secs = [s for s in r["secs"] if s["b"]]
        if not secs: continue
        meta = " · ".join(x for x in [", ".join(r.get("codes") or []), r.get("tag", ""), ("Asked: " + r["pyq"]) if r.get("pyq") else ""] if x)
        out.append(f"<div class='topic'><div class='thead1'><div class='troot'>{html.escape(r['title'])}</div>"
                   + (f"<div class='tmeta'>{html.escape(meta)}</div>" if meta else "") + "</div>")
        for s in secs:
            out.append(f"<div class='map'>{render(sec_tree(s))}</div>")
            n += 1
        out.append("</div>")
    out.append("</body></html>")
    return "".join(out), n

if __name__ == "__main__":
    od = sys.argv[1]; os.makedirs(od, exist_ok=True)
    for spec in sys.argv[2:]:
        b, _, rs = spec.partition(":")
        rf = {int(x) for x in rs.split(",")} if rs else None
        h, n = build(int(b), rf)
        name = f"book{b}" + ("-pilot" if rf else "")
        open(f"{od}/{name}.html", "w").write(h)
        print(name, n, "maps")
