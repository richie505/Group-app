"""Lecture slides (16:9, PowerPoint-sized pages) for one topic of the app's notes, as a PDF: everything on the topic's
pages, slide by slide, ready to teach from.

    python3 tools/lecture_pdf.py <assets dir> <book> <row> <out.pdf> [app name]
    e.g. python3 tools/lecture_pdf.py app/src/group1/assets 1 37 docs/lectures/pilot.pdf "APPSC Group 1 Prelims"

Each topic: a title slide (subject, syllabus lines it covers), the lesson plan (its parts), then every part's notes
(headings, every bullet, every table, the "remember" boxes), a recap of the key terms, and a quick check
of past questions with the answers on the slide after. Citations are left out (tools/lecture_clean.py): source lists, exam / paper tags, book names, "settled" source notes.
"""
import html, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lecture_clean as LC

_CACHE = {}


def J(p):
    if p not in _CACHE:
        _CACHE[p] = json.load(open(p))
    return _CACHE[p]


def build(A, B, R, OUT, APP="APPSC"):
    """writes OUT's .html (the slides); returns its path, or None for a hidden section"""
    if J(f"{A}/index.json")["books"][B - 1]["rows"][R].get("hide"):
        return None
    bk = J(f"{A}/book{B}.json")
    rows = [r for u in bk["units"] for r in u["rows"]]
    units = {id(r): u for u in bk["units"] for r in u["rows"]}
    row = rows[R]
    unit = units[id(row)]
    subject = J(f"{A}/index.json")["books"][B - 1].get("short") or bk.get("title", "")
    mq = J(f"{A}/mcq{B}.json")
    qs, subs = mq["rows"].get(str(R), []), mq["subs"].get(str(R), [])
    idx = J(f"{A}/index.json")["books"][B - 1]["rows"][R]

    # the syllabus lines this topic teaches (Group 1: leaves; Group 2: its syllabus codes)
    lines = []
    if os.path.exists("data/g1syl/leaves.json") and idx.get("leaves"):
        L = {x["leaf"]: x["text"] for x in J("data/g1syl/leaves.json")["leaves"]}
        lines = [L[c] for c in idx["leaves"] if c in L]
    elif os.path.exists(f"{A}/syllabus.json"):
        syl = J(f"{A}/syllabus.json")
        for sj in syl["subjects"]:
            for u in sj["units"]:
                for ph in u["phrases"]:
                    for lf in ph["leaves"]:
                        if [B, R] in lf["rows"]:
                            lines.append(lf["text"])


    def cl(x):
        """the runs without citations: [[text, bold], ...] (bold words that survive the cut stay bold)"""
        if isinstance(x, str):
            x = [[x, 0]]
        rr = [(str(r[0]), r[1]) if isinstance(r, list) and len(r) > 1 else (str(r[0] if isinstance(r, list) else r), 0) for r in x]
        t = "".join(a for a, _ in rr)
        c = LC.clean_text(t)
        if c == t:
            return [[a, b] for a, b in rr]
        out, pos = [], 0
        for a, b in rr:
            a = a.strip()
            if b and len(a) > 1:
                k = c.find(a, pos)
                if k >= 0:
                    out += [[c[pos:k], 0], [a, 1]]
                    pos = k + len(a)
        out.append([c[pos:], 0])
        return [r for r in out if r[0]]


    def runs(x, clean=True):
        if clean:
            x = cl(x)
        out = []
        for r in x:
            t, st = (r[0], r[1]) if isinstance(r, list) and len(r) > 1 else (r if isinstance(r, str) else r[0], 0)
            t = html.escape(str(t))
            out.append(f"<b>{t}</b>" if st else t)
        return "".join(out)


    def plain(x):
        return "".join(str(r[0]) if isinstance(r, list) else str(r) for r in x)


    def hidden(s):
        b = s["b"]
        return len(b) == 1 and b[0].get("k") == "n" and plain(b[0]["x"]).startswith("No MCQ")


    def is_source(bl):
        return bl.get("k") == "n" and re.match(r"\s*Sources?:", plain(bl.get("x", [])))


    # --- each block as (html, weight in lines) -----------------------------------------------------------------
    W = 92  # characters per line on a slide


    def lines_of(t):
        return max(1, -(-len(t) // W))


    def block(bl):
        k = bl["k"]
        if k == "h":
            return [("h", f"<div class='sub'>{runs(bl['x'])}</div>", 1.6)]
        if k == "t":
            head = bl.get("h") or []
            body = bl.get("r") or []
            ncol = max([len(head)] + [len(r) for r in body])
            cw = W * 0.95 / max(1, ncol)
            def rh(r):
                return max(lines_of(plain(c) if isinstance(c, list) else str(c)) * (W / max(cw, 10)) / (W / cw) for c in r) if r else 1
            out, chunk, wt = [], [], 0
            hh = "".join(f"<th>{runs(c)}</th>" for c in head)
            for r in body:
                w = max(-(-len(plain(c)) // int(max(cw, 8))) for c in r) if r else 1
                if chunk and wt + w > 9.5:
                    out.append(("t", chunk, wt))
                    chunk, wt = [], 0
                chunk.append(r)
                wt += w
            if chunk:
                out.append(("t", chunk, wt))
            res = []
            for _, ch, wt in out:
                trs = "".join("<tr>" + "".join(f"<td>{runs(c)}</td>" for c in r) + "</tr>" for r in ch)
                res.append(("t", f"<table>{'<tr>' + hh + '</tr>' if head else ''}{trs}</table>", wt + (1.3 if head else 0) + 0.6))
            return res
        if k == "b":
            return [("b", f"<li>{runs(bl['x'])}</li>", lines_of(plain(bl["x"])) + 0.35)]
        if k == "x":
            return [("x", f"<div class='box rem'><span>REMEMBER</span>{runs(bl['x'])}</div>", lines_of(plain(bl["x"])) + 0.9)]
        if k == "s":
            return [("x", f"<div class='box set'><span>SETTLED</span>{runs(bl['x'])}</div>", lines_of(plain(bl["x"])) + 0.9)]
        if k in ("n", "p"):
            if is_source(bl):
                return []
            return [("x", f"<div class='box note'><span>NOTE</span>{runs(bl['x'])}</div>", lines_of(plain(bl["x"])) + 0.9)]
        return []


    CAP = 12.5  # lines a slide holds
    slides = []


    def slide(kind, body, part="", sub=""):
        slides.append((kind, body, part, sub))


    # title
    syl = "".join(f"<li>{html.escape(x)}</li>" for x in lines[:8])
    slide("title", f"""<div class='kicker'>{html.escape(subject)} · {html.escape(unit['title'][:110])}</div>
    <h1>{html.escape(LC.clean_text(row['title']) or row['title'])}</h1>
    {'<div class="syl"><div class="lab">SYLLABUS LINES THIS LESSON COVERS</div><ul>' + syl + '</ul></div>' if syl else ''}
    <div class='foot'>{html.escape(APP)} · lecture notes</div>""")
    parts = [(j, s) for j, s in enumerate(row["secs"]) if not hidden(s) and s["b"]]
    # lesson plan
    plan = "".join(f"<li><span class='n'>{i + 1}</span>{html.escape(LC.clean_text(s['t']) or s['t'])}</li>" for i, (_, s) in enumerate(parts))
    slide("plan", f"<h2>Lesson plan</h2><ol class='plan'>{plan}</ol><div class='meta'>{len(parts)} parts · {len(qs)} MCQs in the app on this topic</div>")
    # every part: its blocks as data; the browser lays them out slide by slide, measuring what fits
    PARTS = []


    def item(bl):
        k = bl["k"]
        if k != "t" and (LC.drop_block(k, plain(bl.get("x", []))) or not plain(cl(bl.get("x", []))).strip()):
            return None
        if k == "h":
            return {"k": "h", "h": runs(bl["x"])}
        if k == "t":
            rows = [[runs(c) for c in r] for r in (bl.get("r") or [])]
            rows = [r for r in rows if any(c.strip() for c in r)]
            return {"k": "t", "head": [runs(c) for c in (bl.get("h") or [])], "rows": rows} if rows else None
        if k == "b":
            return {"k": "b", "h": runs(bl["x"])}
        if k == "x":
            return {"k": "x", "h": f"<div class='box rem'><span>REMEMBER</span>{runs(bl['x'])}</div>"}
        if k in ("n", "p") and not is_source(bl):
            return {"k": "x", "h": f"<div class='box note'><span>NOTE</span>{runs(bl['x'])}</div>"}
        return None


    for i, (j, s) in enumerate(parts):
        its = [x for x in map(item, s["b"]) if x]
        if its:
            PARTS.append({"title": LC.clean_text(s["t"]) or s["t"], "part": f"Part {i + 1} of {len(parts)}", "items": its})
    slide("parts", "")
    # recap: the key terms of each part (its bold words)
    rec = []
    for i, (j, s) in enumerate(parts):
        terms = []
        for bl in s["b"]:
            if bl["k"] in ("b", "x") and not LC.drop_block(bl["k"], plain(bl["x"])):
                for r in cl(bl["x"]):
                    t = r[0].strip(" :;,.⚠→") if isinstance(r, list) and len(r) > 1 and r[1] else ""
                    if 2 < len(t) < 40 and not any(t.lower() in x.lower() for x in terms):
                        terms.append(t)
        rec.append(f"<li><b>{html.escape(LC.clean_text(s['t']) or s['t'])}</b> — {html.escape(' · '.join(terms[:7]))}</li>")
    for k in range(0, len(rec), 8):
        slide("content", f"<h2>Recap{' (cont.)' if k else ''}</h2><ul class='pts recap'>{''.join(rec[k:k + 8])}</ul>", "Recap", "")
    # quick check: up to 6 past questions (APPSC first), answers on the next slide
    pyq = [q for q in qs if q["id"].startswith("y") and q.get("o") and 0 <= q.get("a", -1) < len(q["o"]) and len(q["o"]) == 4 and len(q["s"]) < 420]
    pyq.sort(key=lambda q: (0 if "APPSC" in (q.get("src") or "").upper() else 1, len(q["s"])))
    pick = pyq[:6]
    if pick:
        def qhtml(n, q, ans):
            st = html.escape(LC.clean_text(q["s"]) or q["s"]).replace("\n", "<br>")
            op = "".join(f"<li class='{'ok' if ans and k == q['a'] else ''}'>({k + 1}) {html.escape(LC.clean_text(o) or o)}</li>" for k, o in enumerate(q["o"]))
            return f"<div class='q'><div class='qs'><span class='n'>Q{n}</span>{st}</div><ol class='opts'>{op}</ol></div>"
        for k in range(0, len(pick), 2):
            two = pick[k:k + 2]
            slide("content", "<h2>Quick check</h2><div class='qs2'>" + "".join(qhtml(k + n + 1, q, False) for n, q in enumerate(two)) + "</div>", "Quick check", "")
            slide("content", "<h2>Quick check — answers</h2><div class='qs2'>" + "".join(qhtml(k + n + 1, q, True) for n, q in enumerate(two)) + "</div>", "Quick check", "")
    slide("end", f"<h1>Questions?</h1><div class='kicker'>{html.escape(row['title'])}</div><div class='foot'>Practise this topic's {len(qs)} MCQs in {html.escape(APP)}</div>")

    CSS = """
    @page { size: 13.333in 7.5in; margin: 0 }
    * { box-sizing: border-box }
    body { margin: 0; font-family: Inter, 'Noto Sans', 'Noto Sans Telugu', Arial, sans-serif; color: #1f2430 }
    section.s, div.s { width: 13.333in; height: 7.5in; position: relative; overflow: hidden; page-break-after: always; background: #fff }
    .s.title, .s.end { background: linear-gradient(135deg, #1e2a5a 0%, #2f3f8f 60%, #4458c4 100%); color: #fff; padding: 0.9in 1in }
    .s.title h1, .s.end h1 { font-size: 40px; line-height: 1.18; margin: 14px 0 22px; font-weight: 800; max-width: 11in }
    .kicker { font-size: 15px; letter-spacing: 1.5px; text-transform: uppercase; opacity: .8; font-weight: 600 }
    .syl { background: rgba(255,255,255,.1); border-radius: 12px; padding: 16px 22px; max-width: 11.3in }
    .syl .lab { font-size: 12px; letter-spacing: 1.5px; font-weight: 700; opacity: .75; margin-bottom: 6px }
    .syl ul { margin: 0; padding-left: 20px; font-size: 18px; line-height: 1.5 }
    .foot { position: absolute; bottom: .55in; left: 1in; font-size: 14px; opacity: .75 }
    .bar { position: absolute; top: 0; left: 0; right: 0; height: .5in; background: #1e2a5a; color: #fff; display: flex; align-items: center;
           padding: 0 .55in; font-size: 13px; letter-spacing: .5px; gap: 18px }
    .bar .p { font-weight: 700; color: #f6c453 }
    .bar .t { opacity: .85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
    .inner { position: absolute; top: .72in; left: .6in; right: .6in; bottom: .45in; display: flex; flex-direction: column }
    h2 { font-size: 30px; margin: 0 0 12px; color: #1e2a5a; font-weight: 800; border-left: 6px solid #f6a623; padding-left: 14px }
    h2 .cont { font-size: 16px; color: #8a90a6; font-weight: 600 }
    .body { font-size: 23px; line-height: 1.4; flex: 1; overflow: hidden }
    .sub { font-size: 23px; font-weight: 800; color: #2f3f8f; margin: 10px 0 4px }
    ul.pts { margin: 4px 0; padding-left: 24px }
    ul.pts li { margin: 4px 0 }
    ul.pts li::marker { color: #f6a623 }
    b { color: #13194a }
    table { border-collapse: collapse; width: 100%; font-size: 19px; line-height: 1.3; margin: 6px 0 8px }
    th { background: #2f3f8f; color: #fff; text-align: left; padding: 7px 10px; font-weight: 700 }
    th b { color: #fff }
    td { padding: 6px 10px; border-bottom: 1px solid #e3e6f0; vertical-align: top }
    tr:nth-child(even) td { background: #f5f7fc }
    .box { border-radius: 10px; padding: 10px 16px; margin: 10px 0; font-size: 21px; line-height: 1.38 }
    .box span { display: inline-block; font-size: 11.5px; font-weight: 800; letter-spacing: 1.2px; margin-right: 10px; padding: 2px 8px; border-radius: 5px }
    .rem { background: #fff6e5; border-left: 5px solid #f6a623 } .rem span { background: #f6a623; color: #fff }
    .set { background: #eaf6ee; border-left: 5px solid #2e9e5b } .set span { background: #2e9e5b; color: #fff }
    .note { background: #eef1fb; border-left: 5px solid #4458c4 } .note span { background: #4458c4; color: #fff }
    ol.plan { list-style: none; padding: 0; margin: 14px 0; columns: 2; column-gap: .5in; font-size: 23px }
    ol.plan li { display: flex; gap: 12px; align-items: flex-start; margin: 0 0 12px; break-inside: avoid }
    .n { flex: none; display: inline-flex; width: 30px; height: 30px; border-radius: 50%; background: #1e2a5a; color: #fff;
         align-items: center; justify-content: center; font-weight: 700; font-size: 14px; margin-right: 10px }
    .meta { color: #6b7185; font-size: 15px; margin-top: 8px }
    .recap li { font-size: 21px; margin: 12px 0 }
    .qs2 { display: grid; grid-template-columns: 1fr 1fr; gap: .35in }
    .q { background: #f7f8fc; border-radius: 12px; padding: 18px 22px; font-size: 23px; line-height: 1.38 }
    .qs { margin-bottom: 8px; display: flex }
    ol.opts { list-style: none; padding: 0; margin: 0 }
    ol.opts li { padding: 5px 10px; border-radius: 7px; margin: 3px 0; background: #fff; border: 1px solid #e3e6f0 }
    ol.opts li.ok { background: #e3f5ea; border-color: #2e9e5b; font-weight: 700; color: #1d6b3d }
    .src { color: #8a90a6; font-size: 14px; margin-top: 8px }
    .num { position: absolute; bottom: .18in; right: .5in; font-size: 12px; color: #9aa0b4 }
    .brand { position: absolute; bottom: .18in; left: .6in; font-size: 12px; color: #9aa0b4 }
    """
    out = []
    for n, (kind, body, part, sub) in enumerate(slides, 1):
        if kind == "parts":
            out.append("<div id='parts'></div>")
            continue
        if kind in ("title", "end"):
            out.append(f"<section class='s {kind}'>{body}</section>")
        else:
            bar = f"<div class='bar'><span class='p'>{html.escape(part or 'Lesson')}</span><span class='t'>{html.escape(row['title'])}</span></div>"
            out.append(f"<section class='s'>{bar}<div class='inner'>{body}</div><div class='brand'>{html.escape(APP)} · {html.escape(subject)}</div><div class='num'></div></section>")
    JS = """
    const P = %s, APP = %s, SUBJ = %s, TOPIC = %s;
    const host = document.getElementById('parts');
    function mk(cls, html) { const d = document.createElement('div'); if (cls) d.className = cls; if (html != null) d.innerHTML = html; return d; }
    function newSlide(p, cont) {
      const s = mk('s'); s.innerHTML = `<div class='bar'><span class='p'>${p.part}</span><span class='t'>${TOPIC}</span></div>
        <div class='inner'><h2>${p.title}<span class='cont'></span></h2><div class='body'></div></div>
        <div class='brand'>${APP} · ${SUBJ}</div><div class='num'></div>`;
      host.appendChild(s); return s.querySelector('.body');
    }
    const over = b => b.scrollHeight > b.clientHeight + 1;
    for (const p of P) {
      const made = []; let body = newSlide(p); made.push(body);
      const fresh = () => { body = newSlide(p); made.push(body); };
      let ul = null;
      for (let i = 0; i < p.items.length; i++) {
        const it = p.items[i];
        if (it.k === 'b') {
          if (!ul || ul.parentNode !== body || body.lastChild !== ul) { ul = document.createElement('ul'); ul.className = 'pts'; body.appendChild(ul); }
          const li = document.createElement('li'); li.innerHTML = it.h; ul.appendChild(li);
          if (over(body) && body.childNodes.length > 1 || over(body) && ul.childNodes.length > 1) {
            li.remove(); if (!ul.childNodes.length) ul.remove();
            const carry = body.lastChild && body.lastChild.classList && body.lastChild.classList.contains('sub') ? body.lastChild : null;
            fresh(); if (carry) body.appendChild(carry);
            ul = document.createElement('ul'); ul.className = 'pts'; body.appendChild(ul); ul.appendChild(li);
          }
          continue;
        }
        ul = null;
        if (it.k === 'h') { body.appendChild(mk('sub', it.h)); if (over(body) && body.childNodes.length > 1) { const h = body.lastChild; h.remove(); fresh(); body.appendChild(h); } continue; }
        if (it.k === 'x') { const d = mk(null, it.h).firstChild; body.appendChild(d); if (over(body) && body.childNodes.length > 1) { d.remove(); const carry = body.lastChild && body.lastChild.classList && body.lastChild.classList.contains('sub') ? body.lastChild : null; fresh(); if (carry) body.appendChild(carry); body.appendChild(d); } continue; }
        if (it.k === 't') {
          const head = it.head.length ? '<tr>' + it.head.map(c => `<th>${c}</th>`).join('') + '</tr>' : '';
          const newTable = () => { const t = document.createElement('table'); t.innerHTML = head; body.appendChild(t); return t.tBodies[0] || t; };
          let tb = newTable();
          for (const r of it.rows) {
            const tr = document.createElement('tr'); tr.innerHTML = r.map(c => `<td>${c}</td>`).join(''); tb.appendChild(tr);
            if (over(body) && (tb.querySelectorAll('td').length > r.length || body.childNodes.length > 1)) {
              tr.remove();
              const t = tb.closest('table'); let carry = null;
              if (!t.querySelector('td')) { t.remove(); carry = body.lastChild && body.lastChild.classList && body.lastChild.classList.contains('sub') ? body.lastChild : null; }
              fresh(); if (carry) body.appendChild(carry); tb = newTable(); tb.appendChild(tr);
            }
          }
        }
      }
      made.forEach((b, k) => { if (made.length > 1) b.parentNode.querySelector('.cont').textContent = ` (${k + 1}/${made.length})`; });
    }
    host.replaceWith(...host.childNodes);
    const all = document.querySelectorAll('section.s, div.s');
    all.forEach((s, k) => { const n = s.querySelector('.num'); if (n) n.textContent = `${k + 1} / ${all.length}`; });
    """ % (json.dumps(PARTS, ensure_ascii=False), json.dumps(html.escape(APP)), json.dumps(html.escape(subject)), json.dumps(html.escape(row["title"])))
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(out)}<script>{JS}</script></body></html>"
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    tmp = OUT[:-4] + ".html"
    open(tmp, "w").write(doc)
    return tmp


def render(pairs):
    """[(html, pdf)] rendered in one browser, 4 pages at a time"""
    import tempfile
    lst = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(pairs, lst)
    lst.close()
    subprocess.run(["node", "-e", """
const { chromium } = require('playwright');
(async () => { const L = JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8')); const b = await chromium.launch();
  let i = 0; const work = async () => { const p = await b.newPage();
    while (i < L.length) { const [h, o] = L[i++];
      await p.goto('file://' + require('path').resolve(h)); await p.waitForTimeout(150);
      await p.pdf({ path: o, width: '13.333in', height: '7.5in', printBackground: true, preferCSSPageSize: true }); }
    await p.close(); };
  await Promise.all([work(), work(), work(), work()]); await b.close(); })();""", lst.name], check=True)
    os.unlink(lst.name)


if __name__ == "__main__":
    A, B, R, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    h = build(A, B, R, OUT, sys.argv[5] if len(sys.argv) > 5 else "APPSC")
    if h:
        render([(h, OUT)])
        os.unlink(h)
        print(OUT)
