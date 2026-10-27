"""One-page micro-theme notes: one syllabus topic (a notes row) on one landscape A4 page, in coloured boxes.

    python3 tools/onepager.py export <book> <row>[+<row>] [...] -> work/onepager/b<book>/r<row>.md (the topic's notes,
                                                                 with a related topic's after "+")
    python3 tools/onepager.py check <book> <row>              -> PASS / FAIL: the page plan r<row>.json (written by an
                                                                 agent, tools/onepager_guide.md) and whether it fits
    python3 tools/onepager.py pdf <out.pdf> <book>:<row> [...] -> the pages, in order, as one PDF
    python3 tools/onepager.py check-extra <book> <row> / pdf-extra ... -> the same for the additional one-pagers
        (work/onepager-extra, tools/onepager_extra_guide.md): what the topic's own notes have and its one-pager
        does not; a fact already on the one-pager fails the check

A page plan is {"title", "tag", "quote"?, "boxes": [{"type", "title", ...}]}; the box types are listed in
tools/onepager_guide.md. Pages are drawn as HTML and printed by Chromium (Playwright), which also measures the fit:
the text is set as large as fits (13 px, a little smaller at a time down to 8 px), so a page fills its sheet.
"""
import html, json, os, re, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

W = "work/onepager"
X = "work/onepager-extra"  # the additional one-pagers: what the full notes have and the one-pager does not
SUBJECT = {1: "History & Culture", 2: "Polity & Society", 3: "Economy", 4: "Geography", 5: "Science & Tech", 6: "Current Affairs"}
PALETTE = [  # (border / title, soft background)
    ("#1d4ed8", "#eff4ff"), ("#15803d", "#effaf2"), ("#c2410c", "#fff4ec"), ("#7c3aed", "#f5f0ff"),
    ("#0f766e", "#ecfbf8"), ("#be123c", "#fff0f3"), ("#a16207", "#fffaeb"), ("#0369a1", "#eef8fe"),
]
TYPES = {"bullets", "table", "timeline", "cards", "cycle", "flow", "hierarchy", "note"}


def rows_of(book):
    return [r for u in json.load(open(f"data/complete-full/book{book}.json"))["units"] for r in u["rows"]]


# ---------- export ----------

def export(book, refs):
    """refs: "7" or "7+5" (topic 7, with topic 5's notes added as related notes, for a topic whose own notes are thin)."""
    from topic_export import topic
    rows = rows_of(book)
    os.makedirs(f"{W}/b{book}", exist_ok=True)
    for ref in refs:
        ri, *more = [int(x) for x in str(ref).split("+")]
        text = topic(ri, rows[ri]) + "".join(f"\n\n=== RELATED NOTES (use only what belongs to this topic)\n{topic(m, rows[m])}"
                                             for m in more)
        open(f"{W}/b{book}/r{ri}.md", "w").write(text + "\n")
        print(f"{W}/b{book}/r{ri}.md: {rows[ri]['title']}" + (f" (+ related {more})" if more else ""))


# ---------- drawing ----------

def md(t):
    """**bold**, ==highlight== in plan text."""
    t = html.escape(str(t))
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)


def box(b, k):
    c, bg = PALETTE[k % len(PALETTE)]
    t, title = b["type"], md(b.get("title", ""))
    if t == "note":
        c, bg = "#b45309", "#fff7e0"
    body = ""
    if t in ("bullets", "note"):
        body = "<ul>" + "".join(f"<li>{md(i)}</li>" for i in b["items"]) + "</ul>"
    elif t == "table":
        head = "".join(f"<th>{md(h)}</th>" for h in b["head"])
        rows = "".join("<tr>" + "".join(f"<td>{md(x)}</td>" for x in r) + "</tr>" for r in b["rows"])
        body = f"<table><tr>{head}</tr>{rows}</table>"
    elif t == "timeline":
        body = "<div class=tl>" + "".join(f"<div class=ev><span class=when>{md(e['when'])}</span> {md(e['what'])}</div>"
                                         for e in b["items"]) + "</div>"
    elif t == "cards":
        body = "<div class=cards>" + "".join(
            f"<div class=card style='border-color:{c}'><div class=ct style='color:{c}'>{md(x['title'])}</div>"
            + "".join(f"<div class=cl>{md(l)}</div>" for l in x["lines"]) + "</div>" for x in b["cards"]) + "</div>"
    elif t == "flow":
        # short steps run left to right; longer ones go down, so no arrow is left at a line's end pointing at nothing
        across = sum(len(re.sub(r"\*\*|==", "", s)) for s in b["steps"]) + 4 * len(b["steps"]) <= 48
        arrow = "<span class=arr>➜</span>" if across else "<span class='arr down'>↓</span>"
        body = f"<div class='flow{'' if across else ' down'}'>" + arrow.join(
            f"<span class=step style='border-color:{c}'>{md(s)}</span>" for s in b["steps"]) + "</div>"
    elif t == "hierarchy":
        n = len(b["levels"])
        body = "<div class=hier>" + "".join(
            f"<div class=lvl style='width:{46 + 54 * i / max(1, n - 1):.0f}%;background:{c}{'' if i == 0 else hex(255 - 30 * i)[2:].rjust(2, '0')}'>"
            f"<b>{md(l['name'])}</b>{(' · ' + md(l['note'])) if l.get('note') else ''}</div>"
            for i, l in enumerate(b["levels"])) + "</div>"
    elif t == "cycle":
        steps = b["steps"]
        n = len(steps)
        import math
        nodes, R = [], 38
        for i, s in enumerate(steps):
            a = -math.pi / 2 + 2 * math.pi * i / n
            x, y = 50 + R * math.cos(a), 50 + R * math.sin(a)
            nodes.append(f"<div class=node style='left:{x:.1f}%;top:{y:.1f}%;border-color:{c}'>{md(s)}</div>")
        centre = f"<div class=centre style='color:{c}'>{md(b.get('centre', ''))}</div>" if b.get("centre") else ""
        body = (f"<div class=cyc><svg viewBox='0 0 100 100' preserveAspectRatio='none'><circle cx=50 cy=50 r={R} fill=none "
                f"stroke='{c}' stroke-width=0.8 stroke-dasharray='3 2'/></svg>{centre}{''.join(nodes)}</div>")
    # a long box of cards or table rows may run on into the next column (each card or row stays whole)
    split = " split" if (t == "cards" and len(b["cards"]) > 6) or (t == "table" and len(b["rows"]) > 12) else ""
    return (f"<section class='box{split}' style='border-color:{c};background:{bg}'><h3 style='background:{c}'>{title}</h3>"
            f"{body}</section>")


CSS = """
@page { size: 297mm 210mm; margin: 0 }
* { box-sizing: border-box }
html { --fs: 10.5px }
body { margin: 0; font-family: 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif; color: #1f2937; background: #fff }
.page { width: 297mm; height: 210mm; padding: 6mm 7mm 5mm; display: flex; flex-direction: column; overflow: hidden;
        page-break-after: always }
.head { display: flex; align-items: center; gap: 10px; border-bottom: 3px solid #ea580c; padding-bottom: 4px }
.num { background: #ea580c; color: #fff; font-weight: 800; font-size: 20px; border-radius: 8px; padding: 2px 10px }
.title { font-weight: 800; font-size: 19px; color: #111827; text-transform: uppercase; letter-spacing: .3px; flex: 1;
         line-height: 1.15 }
.tag { background: #fde7d8; color: #9a3412; font-weight: 700; font-size: 11px; border-radius: 14px; padding: 3px 10px;
       white-space: nowrap }
.quote { font-style: italic; color: #6d28d9; font-size: calc(var(--fs) * 1.05); text-align: center; margin: 3px 0 0 }
.cols { flex: 1; column-count: 3; column-gap: 4mm; column-fill: auto; margin-top: 4px; font-size: var(--fs);
        line-height: 1.32; overflow: hidden }
.box { break-inside: avoid; border: 1.6px solid; border-radius: 9px; margin: 0 0 3mm; padding: 0 6px 4px; overflow: hidden }
.box.split { break-inside: auto } .card, tr { break-inside: avoid }
.box h3 { margin: 0 -6px 3px; padding: 2px 8px; color: #fff; font-size: calc(var(--fs) * 1.05); letter-spacing: .3px;
          text-transform: uppercase }
ul { margin: 0; padding-left: 13px } li { margin: 1px 0 }
b { color: #111827 } mark { background: #fff2a8; padding: 0 1px; border-radius: 2px }
table { border-collapse: collapse; width: 100%; font-size: calc(var(--fs) * .95) }
th { background: rgba(0,0,0,.06); text-align: left } th, td { border: 1px solid rgba(0,0,0,.14); padding: 1.5px 4px;
     vertical-align: top }
.tl { border-left: 2px solid currentColor; margin-left: 5px; padding-left: 8px; color: inherit }
.ev { position: relative; margin: 2px 0 } .ev:before { content: ''; position: absolute; left: -12.5px; top: .45em;
      width: 7px; height: 7px; border-radius: 50%; background: #ea580c }
.when { font-weight: 800; color: #9a3412 }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4px }
.card { border: 1.2px solid; border-radius: 6px; padding: 2px 5px; background: #fff }
.ct { font-weight: 800 } .cl { margin-top: 1px }
.flow { display: flex; flex-wrap: wrap; align-items: center; gap: 3px }
.step { border: 1.4px solid; border-radius: 6px; padding: 1px 5px; background: #fff }
.arr { color: #ea580c; font-weight: 800 }
.flow.down { flex-direction: column; align-items: stretch; gap: 0 } .flow.down .step { text-align: center }
.arr.down { text-align: center; line-height: 1.05; font-size: 1.35em }
.hier { display: flex; flex-direction: column; align-items: center; gap: 2px; margin: 2px 0 }
.lvl { color: #fff; text-align: center; border-radius: 5px; padding: 2px 4px }
.lvl b { color: #fff }
.lvl mark, .lvl mark b { color: #111827 }
.cyc { position: relative; height: calc(var(--fs) * 17); margin: 4px 0 } .cyc svg { position: absolute; inset: 0;
       width: 100%; height: 100% }
.node { position: absolute; transform: translate(-50%, -50%); background: #fff; border: 1.4px solid; border-radius: 12px;
        padding: 1px 5px; max-width: 42%; text-align: center; font-size: calc(var(--fs) * .92) }
.centre { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-weight: 800; text-align: center;
          max-width: 40% }
.foot { font-size: 8px; color: #94a3b8; display: flex; justify-content: space-between; margin-top: 1mm }
"""


def page_html(plan, number, foot="APPSC Complete · one-page notes"):
    head = (f"<div class=head><span class=num>{number:02d}</span><span class=title>{md(plan['title'])}</span>"
            f"<span class=tag>{md(plan.get('tag', ''))}</span></div>")
    quote = f"<div class=quote>“{md(plan['quote'])}”</div>" if plan.get("quote") else ""
    boxes = "".join(box(b, k) for k, b in enumerate(plan["boxes"]))
    return (f"<div class=page>{head}{quote}<div class=cols>{boxes}</div>"
            f"<div class=foot><span>{foot}</span><span>{number}</span></div></div>")


NODE = r"""
const {chromium} = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 1123, height: 794}});
  await p.goto('file://' + src);
  // per page: the largest text size (13 px down to 8 px) at which no box is cut off
  const fits = await p.evaluate(() => {
    const res = [];
    for (const page of document.querySelectorAll('.page')) {
      const cols = page.querySelector('.cols'); let fs = 13, ok = false;
      for (; fs >= 8; fs -= 0.25) {
        page.style.setProperty('--fs', fs + 'px');
        if (cols.scrollWidth <= cols.clientWidth + 1 && cols.scrollHeight <= cols.clientHeight + 1) { ok = true; break; }
      }
      cols.style.columnFill = 'balance';  // fitted: spread the boxes evenly over the three columns
      if (cols.scrollWidth > cols.clientWidth + 1) cols.style.columnFill = 'auto';
      res.push({fs: Math.max(fs, 8), ok});
    }
    return res;
  });
  if (out) await p.pdf({path: out, width: '297mm', height: '210mm', printBackground: true});
  console.log(JSON.stringify(fits)); await b.close();
})().catch(e => { console.error(e.message); process.exit(1); });
"""


def render(plans, out=None, foot="APPSC Complete · one-page notes"):
    """[(plan, number)] -> per page {fs, ok}; writes the PDF if out."""
    doc = f"<!doctype html><meta charset=utf-8><style>{CSS}</style>" + "".join(page_html(p, n, foot) for p, n in plans)
    with tempfile.TemporaryDirectory() as d:
        Path(d, "p.html").write_text(doc)
        Path(d, "r.js").write_text(NODE)
        env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
        r = subprocess.run(["node", f"{d}/r.js", f"{d}/p.html", out or ""], capture_output=True, text=True, env=env)
        if r.returncode:
            raise SystemExit(r.stderr)
        return json.loads(r.stdout.strip().splitlines()[-1])


# ---------- check ----------

def plan_text(plan):
    out = [plan["title"], plan.get("quote", "")]
    for b in plan["boxes"]:
        out.append(b.get("title", ""))
        for key in ("items", "steps", "head"):
            for x in b.get(key, []):
                out.append(x if isinstance(x, str) else " ".join(map(str, x.values())))
        out += [" ".join(map(str, r)) for r in b.get("rows", [])]
        for c in b.get("cards", []):
            out += [c["title"], *c["lines"]]
        for l in b.get("levels", []):
            out += [l["name"], l.get("note", "")]
        out.append(b.get("centre", ""))
    return re.sub(r"\*\*|==", "", " ".join(out))


def items(plan):
    """The page's facts one by one: a bullet, a table row, a timeline entry, a card line, a step or a level."""
    out = []
    for b in plan["boxes"]:
        for x in b.get("items", []):
            out.append(x if isinstance(x, str) else " ".join(map(str, x.values())))
        out += [x for x in b.get("steps", [])]
        out += [" ".join(map(str, r)) for r in b.get("rows", [])]
        for c in b.get("cards", []):
            out += [f"{c['title']} {l}" for l in c["lines"]]
        out += [f"{l['name']} {l.get('note', '')}" for l in b.get("levels", [])]
    return [re.sub(r"\*\*|==", "", x) for x in out]


STOPW = set("the and of in to a for by with is was as at from or an be are its it this that on not no also only".split())


def fact_words(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if (len(w) > 2 or w.isdigit()) and w not in STOPW}


def overlap(extra, main):
    """Facts of the additional page that the one-pager already has: most of a line's words on one of its lines."""
    got = [fact_words(x) for x in items(main)]
    out = []
    for x in items(extra):
        w = fact_words(x)
        if len(w) >= 3 and any(len(w & g) >= 0.7 * len(w) for g in got):
            out.append(x)
    return out


def check(book, ri, extra=False):
    errs = []
    try:
        plan = json.load(open(f"{X if extra else W}/b{book}/r{ri}.json"))
    except Exception as e:
        print(f"FAIL: plan not readable: {e}")
        return False
    notes = open(f"{W}/b{book}/r{ri}.md").read()
    if extra:  # the topic's own notes only: a neighbour's are its own additional page
        notes = notes.split("\n=== RELATED NOTES")[0]
    flat = re.sub(r"[^a-z0-9]+", " ", notes.lower())
    if not plan.get("title") or not isinstance(plan.get("boxes"), list):
        errs.append("needs title and boxes")
    for k, b in enumerate(plan.get("boxes", [])):
        t = b.get("type")
        need = {"bullets": "items", "note": "items", "table": "rows", "timeline": "items", "cards": "cards",
                "cycle": "steps", "flow": "steps", "hierarchy": "levels"}.get(t)
        if t not in TYPES:
            errs.append(f"box {k + 1}: unknown type {t!r}")
        elif not b.get(need):
            errs.append(f"box {k + 1} ({t}): needs {need}")
        if not b.get("title"):
            errs.append(f"box {k + 1}: needs a title")
    lo = 3 if extra else 5
    if not lo <= len(plan.get("boxes", [])) <= 11:
        errs.append(f"{len(plan.get('boxes', []))} boxes: use {lo}-11")
    if errs:
        print("FAIL:\n" + "\n".join(errs))
        return False
    # facts: every figure must be in the notes; names (capitalised words) mostly
    text = plan_text(plan)
    nums = {n for n in re.findall(r"\d[\d,.]*\d|\d", text)}
    bad_n = sorted(n for n in nums if re.sub(r"[^0-9]+", " ", n).strip() not in re.sub(r"[^0-9]+", " ", notes))
    # names: capitalised words (a hyphenated name is checked part by part); plain words that start a cell or a line
    # ("Collects", "Exam") are not names, so a few unknown ones are let through
    names = {p for w in re.findall(r"\b[A-Z][a-zA-Z-]{3,}\b", text) for p in w.split("-") if len(p) > 3}
    bad_w = sorted(w for w in names if f" {w.lower()} " not in f" {flat} " and w.lower() not in flat)
    if bad_n:
        errs.append("figures not in the notes: " + ", ".join(bad_n[:15]))
    if len(bad_w) > 6:
        errs.append("names not in the notes: " + ", ".join(bad_w[:15]))
    if extra:
        same = overlap(plan, json.load(open(f"{W}/b{book}/r{ri}.json")))
        if same:
            errs.append("already on the one-pager (leave out or give only what it lacks): " + " | ".join(same[:8]))
    fit = render([(plan, 1)])[0]
    if not fit["ok"]:
        errs.append("does not fit one page even at 8 px: cut the longest boxes")
    if errs:
        print("FAIL:\n" + "\n".join(errs))
        return False
    print(f"PASS: {len(plan['boxes'])} boxes, text at {fit['fs']} px" + (f"; check these names: {', '.join(bad_w)}" if bad_w else ""))
    return True


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), sys.argv[3:])
    elif cmd in ("check", "check-extra"):
        check(int(sys.argv[2]), int(sys.argv[3]), extra=cmd == "check-extra")
    elif cmd in ("pdf", "pdf-extra"):
        plans = []
        for n, ref in enumerate(sys.argv[3:], 1):
            b, r = ref.split(":")
            plans.append((json.load(open(f"{X if cmd == 'pdf-extra' else W}/b{b}/r{r}.json")), n))
        print(render(plans, os.path.abspath(sys.argv[2]),
                     "APPSC Complete · additional one-page notes" if cmd == "pdf-extra" else "APPSC Complete · one-page notes"))
