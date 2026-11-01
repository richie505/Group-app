"""APPSC micro tricks PDF: which answer tricks work in which subject, question angle, syllabus unit and topic
(data/pyq/micro.json, tools/pyq_micro.py).

    python3 tools/pyq_micro_pdf.py [out.pdf=pdfs/APPSC-Micro-Tricks.pdf]
"""
import html, json, os, subprocess, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "pdfs/APPSC-Micro-Tricks.pdf"
M = json.load(open("data/pyq/micro.json"))
BOOKS = {"1": "History & Culture", "2": "Polity, Governance & Society", "3": "Economy (India & AP)",
         "4": "Geography (India, World & AP)", "5": "Science, Technology & Environment", "6": "Current Affairs"}
E = html.escape
HOW = {
    "Longest option": "Pick the clearly longest option - here the examiner writes the right answer out in full and keeps decoys short.",
    "Shortest option": "Pick the clearly shortest option.",
    "Centre option (shares most words with the others)": "Pick the option that shares most words with the other three - decoys are made by changing one part of the key.",
    "Odd-one-out option (shares no word with others)": "Pick the one option that shares no word with the other three.",
    "Echo option (repeats the question's words)": "Pick the option that repeats the question's own words.",
    "Near-twin pair (two options alike; key is one of them)": "When two options are almost the same (one word differs), the key is one of those two - drop the other two.",
    "Middle numbers (2nd or 3rd of four)": "Among four numbers, keep the 2nd and 3rd largest; drop the extremes.",
    "Middle years (2nd or 3rd of four)": "Among four years, keep the middle two; drop the earliest and the latest.",
    "Smallest number": "the smallest number", "Largest number": "Pick the largest number.", "Smallest year": "the earliest year",
    "Largest year": "Pick the latest year.", "Only option with a number/date": "Pick the only option carrying a number or date.",
    "'None of the above / these'": "'None of the above'", "'Neither ... nor'": "'Neither ... nor'",
    "'Both'": "Pick 'Both'.", "'All of the above / all'": "Pick 'All of the above'.",
}


def conf(t, others=None):
    p = t["p"]
    tag = "solid" if p < 0.01 else "likely" if p < 0.05 else "hint"
    also = ""
    if others is not None:
        o = next((x for x in others if x["trick"] == t["trick"]), None)
        if o and o["n"] >= 10:
            same = (o["lift"] >= 1.1) if t["lift"] > 1 else (o["lift"] <= 0.9)
            also = " ✓" if same else ""
            if same and tag == "hint":
                tag = "likely"
    return tag, also


def good(res, others=None, strong_only=False):
    out = []
    for t in sorted(res, key=lambda x: x["p"]):
        if t["p"] < 0.1 and t["lift"] >= 1.2 and t["n"] >= 10:
            tag, also = conf(t, others)
            if strong_only and tag == "hint":
                continue
            out.append((t, tag, also))
    return out


def bad(res, others=None):
    out = []
    for t in sorted(res, key=lambda x: x["p"]):
        if t["p"] < 0.1 and t["lift"] <= 0.75 and t["n"] >= 10:
            tag, also = conf(t, others)
            out.append((t, tag, also))
    return out


def rows_good(items):
    if not items:
        return "<p class=none>No trick beats chance here - rely on the fact.</p>"
    r = []
    for t, tag, also in items:
        name = t["trick"]
        how = HOW.get(name, f"Lean to {name.lower()}." if name.startswith("Option") else name)
        if name.startswith("Option "):
            how = f"Between two survivors, prefer <b>{name.lower()}</b> - the key sits here more than its share."
        r.append(f"<tr><td>{how}</td><td><b>{t['rate']:.0%}</b></td><td>{t['chance']:.0%}</td><td>{t['hit']}/{t['n']}</td><td class={tag}>{tag}{also}</td></tr>")
    return "<table><tr><th>Trick that works here</th><th>key</th><th>chance</th><th>count</th><th>trust</th></tr>" + "".join(r) + "</table>"


def rows_bad(items):
    if not items:
        return ""
    r = []
    for t, tag, also in items:
        name = t["trick"]
        what = HOW.get(name, name)
        if name in ("Longest option", "Shortest option", "Centre option (shares most words with the others)", "Echo option (repeats the question's words)",
                    "Odd-one-out option (shares no word with others)", "Only option with a number/date", "Largest number", "Largest year"):
            what = name.lower()
        if name.startswith("Option "):
            what = name.lower()
        if name.startswith("Near-twin"):
            what = "one of two near-twin options (the twins are a trap here)"
        if name.startswith("Middle"):
            what = name.lower().split(" (")[0]
        r.append(f"<tr><td>Strike <b>{E(what)}</b></td><td><b>{t['rate']:.0%}</b></td><td>{t['chance']:.0%}</td><td>{t['hit']}/{t['n']}</td><td class={tag}>{tag}{also}</td></tr>")
    return "<table class=rev><tr><th>Reverse trick - rarely the key here</th><th>key</th><th>chance</th><th>count</th><th>trust</th></tr>" + "".join(r) + "</table>"


def kw_table(kw):
    rows = []
    base = kw.get("(any statement)")
    for k, (t, n) in sorted(kw.items(), key=lambda x: x[1][0] / max(x[1][1], 1)):
        if k == "(any statement)" or n < 8:
            continue
        rate = t / n
        v = "<b class=f>suspect FALSE</b>" if rate <= 0.38 else "<b class=t>suspect TRUE</b>" if rate >= 0.66 else "no signal"
        rows.append(f"<tr><td>{E(k)}</td><td>{rate:.0%}</td><td>{t}/{n}</td><td>{v}</td></tr>")
    if not rows:
        return ""
    b = f" (any statement here is true {base[0] / base[1]:.0%})" if base else ""
    return f"<h4>Keywords inside statements{b}</h4><table><tr><th>statement contains</th><th>true</th><th>count</th><th>read it as</th></tr>{''.join(rows)}</table>"


def main():
    sec = [f"""<h1>APPSC Micro Tricks</h1>
<p class=sub>Which answer trick works <b>in which subject, which kind of question, which syllabus unit and which topic</b> - measured on
the Commission's own keys. A trick that shows "no signal" across the whole paper can be strong inside one corner of it and useless or
even wrong in another; this book gives each corner its own rules.</p>
<div class=box><b>How to read the tables.</b> <b>key</b> = how often the trick's pick was the official answer there; <b>chance</b> = what blind
guessing gives; <b>count</b> = hits / questions where the trick applied. <b>trust</b>: <span class=solid>solid</span> = could hardly be luck
(p &lt; 0.01); <span class=likely>likely</span> = p &lt; 0.05, or a weaker result that the same corner of UPSC / other state papers repeats (✓);
<span class=hint>hint</span> = suggestive only. A <b>reverse trick</b> is an option kind that is rarely the key there - strike it first.<br>
<b>Rule of use:</b> facts first; tricks only to choose between options you could not eliminate. With 1/3 negative marking, guess only after
striking at least one option.</div>"""]
    # universal
    a = M["all"]
    sec.append("<h2>1. Rules that hold across the whole APPSC paper</h2>" + rows_good(good(a)) + rows_bad(bad(a)))
    # by angle
    parts = ["<h2>2. By kind of question (all subjects)</h2>"]
    for name, d in M["angles"].items():
        g, b = good(d["tricks"], d["others"]), bad(d["tricks"], d["others"])
        if g or b:
            parts.append(f"<h3>{E(name)} <span class=n>({d['n']} APPSC questions)</span></h3>" + rows_good(g) + rows_bad(b))
    sec.append("".join(parts))
    # by subject
    for bk, s in M["subjects"].items():
        if not s["n"]:
            continue
        parts = [f"<h2>{int(bk) + 2}. {E(BOOKS[bk])} <span class=n>({s['n']} keyed APPSC questions)</span></h2>",
                 "<h3>Across the subject</h3>", rows_good(good(s["tricks"], s["others"])), rows_bad(bad(s["tricks"], s["others"]))]
        for an, d in s["angles"].items():
            g, b = good(d["tricks"], d["others"]), bad(d["tricks"], d["others"])
            if g or b:
                parts.append(f"<h3>{E(an)} questions <span class=n>({d['n']})</span></h3>" + rows_good(g) + rows_bad(b))
        units = [(u, d) for u, d in s["units"].items() if good(d["tricks"]) or bad(d["tricks"])]
        if units:
            parts.append("<h3>Unit by unit (syllabus units)</h3>")
            for u, d in units:
                parts.append(f"<h4>{E(u)} <span class=n>({d['n']})</span></h4>" + rows_good(good(d["tricks"])) + rows_bad(bad(d["tricks"])))
        topics = [(u, d) for u, d in s["topics"].items() if good(d["tricks"]) or bad(d["tricks"])]
        if topics:
            parts.append("<h3>Micro-topics with a pattern of their own</h3>")
            for u, d in topics:
                parts.append(f"<h4>{E(u)} <span class=n>({d['n']})</span></h4>" + rows_good(good(d["tricks"])) + rows_bad(bad(d["tricks"])))
        parts.append(kw_table(s.get("kw", {})))
        sec.append("".join(parts))
    sec.append("""<h2>9. What does NOT work - folk tricks the keys disprove</h2><ul>
<li><b>"Avoid 'only' / 'all' / 'always'"</b> - in APPSC such statements are true about as often as any other; check the fact.</li>
<li><b>"When in doubt, C"</b> - option 3 is not favoured overall; the favoured position changes by subject and question kind (tables above).</li>
<li><b>"The answer is never the obvious one"</b> - APPSC keys the standard textbook answer; the straight code A-1 B-2 C-3 D-4 is used too.</li>
<li><b>"Pick one of the two closest numbers"</b> - no edge (48% against 50% chance).</li>
<li><b>Blind guessing</b> - zero expected gain with 1/3 negative marking.</li></ul>""")
    css = """@page{size:A4;margin:14mm 12mm}body{font-family:'Noto Sans','DejaVu Sans',sans-serif;font-size:9.6pt;color:#1d1d1f;line-height:1.4}
h1{font-size:22pt;margin:0 0 4pt;color:#14532d}h2{font-size:14pt;color:#14532d;border-bottom:2px solid #14532d;padding-bottom:2pt;margin-top:16pt;page-break-after:avoid}
h3{font-size:11pt;margin:9pt 0 2pt;color:#0b3d91;page-break-after:avoid}h4{font-size:9.6pt;margin:7pt 0 2pt;color:#444;page-break-after:avoid}
.sub{color:#555}.box{background:#effaf3;border-left:4px solid #14532d;padding:7pt 10pt;margin:8pt 0}
table{border-collapse:collapse;width:100%;margin:3pt 0 5pt;font-size:8.8pt;page-break-inside:avoid}td,th{border:1px solid #cdd;padding:2.5pt 5pt;text-align:left;vertical-align:top}
th{background:#e7f3ec}table.rev th{background:#fbeaea}td:nth-child(n+2){white-space:nowrap}.n{color:#888;font-size:8.5pt;font-weight:400}
.solid{color:#0a7a2f;font-weight:700}.likely{color:#1d4ed8;font-weight:700}.hint{color:#a66300}.t{color:#0a7a2f}.f{color:#b00020}.none{color:#888;font-style:italic;margin:2pt 0}"""
    doc = f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{''.join(sec)}</body></html>"
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    h = os.path.abspath(OUT.replace(".pdf", ".html"))
    open(h, "w").write(doc)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('file://{h}');await p.pdf({{path:'{os.path.abspath(OUT)}',format:'A4',printBackground:true}});await b.close();}})();")
    subprocess.run(["node", "-e", js], check=True)
    os.remove(h)
    print(OUT)


if __name__ == "__main__":
    main()
