"""APPSC Lectures app (flavor "lectures"): every topic's lecture slides (tools/lecture_pdf.py) as HTML, shown in a
WebView subject-wise and topic-wise. Same slides as the PDFs, a few KB each.

    python3 tools/lecture_app.py   -> app/src/lectures/assets/lec/<g1|g2>/<book>/<row>.html + lec/index.json
"""
import glob, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
import lecture_pdf as LP

OUT = "app/src/lectures/assets/lec"
APPS = [("g1", "app/src/group1/assets", "APPSC Group 1 Prelims", "out/lectures/APPSC-Group1-Prelims-Lectures"),
        ("g2", "app/src/group2/assets", "APPSC Group 2", "out/lectures/APPSC-Group2-Lectures")]
SCREEN = """<meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'><style>
@media screen {
  /* one slide = one screen, laid out for this phone: text sized to the screen (and the phone's font size) */
  :root { --W: 100vw; --H: 100vh; --f: 16px } /* --W, --H, --f are set in pixels by START (no vw / vh: some WebViews give 0) */
  html, body { margin: 0; height: 100%; overflow: hidden; background: #0f1530; -webkit-tap-highlight-color: transparent }
  section.s, div.s { width: var(--W) !important; height: var(--H) !important; margin: 0; page-break-after: auto }
  .deck section.s, .deck div.s { display: none }
  /* the slide shown is pinned to the screen: no scroll position (a reload restores one) can move it away */
  .deck section.s.on, .deck div.s.on { display: block; position: fixed !important; left: 0; top: 0; z-index: 1 }
  #diag { position: fixed; z-index: 20; left: 8px; top: 8px; right: 60px; font: 12px monospace; color: #ffd; background: rgba(0,0,0,.6); padding: 6px; white-space: pre-wrap }
  .bar { height: calc(var(--f) * 2.1); font-size: calc(var(--f) * .7); padding: 0 64px 0 18px; gap: 10px }
  .inner { top: calc(var(--f) * 2.7); left: 58px; right: 58px; bottom: 26px; overflow: hidden }
  h2 { font-size: calc(var(--f) * 1.28); margin: 0 0 .5em; padding-left: 10px; border-left-width: 5px }
  h2 .cont { font-size: .6em }
  .body { font-size: var(--f) }
  .sub { font-size: 1.04em; margin: .45em 0 .15em }
  ul.pts { padding-left: 1.1em } ul.pts li { margin: .22em 0 }
  table { font-size: .86em } th, td { padding: .35em .5em }
  .box { font-size: .92em; padding: .45em .7em; margin: .45em 0 } .box span { font-size: .62em }
  .s.title, .s.end { padding: calc(var(--H) * .07) calc(var(--W) * .06) } .s.title h1, .s.end h1 { font-size: calc(var(--f) * 1.75); margin: .4em 0 .6em }
  .kicker { font-size: calc(var(--f) * .7) } .syl { padding: .7em 1em } .syl ul { font-size: calc(var(--f) * .92) }
  .syl .lab { font-size: calc(var(--f) * .6) } .foot { bottom: 30px; left: calc(var(--W) * .06); font-size: calc(var(--f) * .7) }
  ol.plan { font-size: var(--f); column-gap: 24px } ol.plan li { margin: 0 0 .5em } .n { width: 1.5em; height: 1.5em; font-size: .7em; margin-right: .5em }
  .meta { font-size: calc(var(--f) * .75) }
  .recap li { font-size: calc(var(--f) * .92); margin: .4em 0 }
  .q { font-size: calc(var(--f) * .92); padding: .7em .9em } .src { font-size: .65em }
  .qs2 { gap: 14px }
  .brand, .num { display: none }
  @media (orientation: portrait) { ol.plan { columns: 1 } .qs2 { grid-template-columns: 1fr } }
  /* the controls: close, previous, slide n of N, next; a progress line */
  #ctl button { position: fixed; z-index: 9; border: 0; border-radius: 50%; width: 48px; height: 48px; font-size: 26px; line-height: 48px;
    background: rgba(15,21,48,.55); color: #fff; padding: 0 }
  #ctl #cl { top: 4px; right: 8px; width: 42px; height: 42px; line-height: 42px; font-size: 20px; background: rgba(255,255,255,.18) }
  #ctl #pv { top: 50%; left: 6px; transform: translateY(-50%) } #ctl #nx { top: 50%; right: 6px; transform: translateY(-50%) }
  #ctl #pv, #ctl #nx { background: rgba(15,21,48,.28); color: #fff }
  #ctl #ct { position: fixed; z-index: 9; bottom: 6px; right: 14px; font: 600 12px Inter, Arial, sans-serif;
    color: #fff; background: rgba(15,21,48,.5); padding: 2px 10px; border-radius: 10px }
  #ctl #pg { position: fixed; z-index: 9; bottom: 0; left: 0; height: 4px; background: #f6a623; transition: width .2s }
  .s.title #x, .s.end #x { display: none }
}
</style>"""
DECK = r"""
(function () {
  // static slides (title, plan, recap, quick check) that overflow this screen are split, item by item
  function split(s) {
    const inner = s.querySelector('.inner'); const box = s.querySelector('.qs2, ul.recap, ol.plan');
    if (!inner || !box) return;
    const moved = [];
    while (inner.scrollHeight > inner.clientHeight + 1 && box.children.length > 1) moved.unshift(box.lastElementChild), box.lastElementChild.remove();
    if (!moved.length) return;
    const c = s.cloneNode(true); const cb = c.querySelector('.qs2, ul.recap, ol.plan');
    cb.innerHTML = ''; moved.forEach(m => cb.appendChild(m));
    s.after(c); split(c);
  }
  document.querySelectorAll('section.s').forEach(split);
  const all = [...document.querySelectorAll('section.s, div.s')], N = all.length;
  all.forEach((s, i) => { s.setAttribute('role', 'group'); s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', `Slide ${i + 1} of ${N}`); });
  document.documentElement.classList.add('deck');
  const ctl = document.createElement('div'); ctl.id = 'ctl';
  ctl.innerHTML = `<button id='cl' aria-label='Close lecture'>✕</button><button id='pv' aria-label='Previous slide'>‹</button>
    <span id='ct' role='status' aria-live='polite'></span><button id='nx' aria-label='Next slide'>›</button><div id='pg' aria-hidden='true'></div>`;
  document.body.appendChild(ctl);
  const A = window.Android, ct = ctl.querySelector('#ct'), pg = ctl.querySelector('#pg');
  const h = new URLSearchParams(location.hash.slice(1));
  // each slide's part of the notes ("Part 3 of 6" in its bar; 0: title, plan, recap, quick check)
  const partOf = all.map(s => { const m = ((s.querySelector('.bar') || {}).textContent || '').match(/Part (\d+) of/); return m ? +m[1] : 0; });
  const p0 = h.has('part') ? partOf.indexOf(+h.get('part')) : -1;
  let cur = h.has('end') ? N - 1 : p0 >= 0 ? p0 : Math.min(N - 1, Math.max(0, Math.round(parseFloat(h.get('p') || '0') * (N - 1))));
  function show(i) {
    all[cur].classList.remove('on'); cur = i; all[cur].classList.add('on');
    ct.textContent = `${cur + 1} / ${N}`; pg.style.width = `${(cur + 1) / N * 100}%`;
    try { history.replaceState(null, '', '#p=' + (N > 1 ? cur / (N - 1) : 0)); } catch (e) {}
    scrollTo(0, 0); diag();
    if (partOf[cur] && A && A.part) try { A.part(partOf[cur]); } catch (e) {}
  }
  // if the slide shown is still not on the screen, say what the screen reports (to fix it)
  function diag() {
    const r = all[cur].getBoundingClientRect(), bad = r.width < 100 || r.height < 100 || r.bottom < 50 || r.top > innerHeight - 50;
    let d = document.getElementById('diag');
    if (!bad) { if (d) d.remove(); return; }
    if (!d) { d = document.createElement('div'); d.id = 'diag'; document.body.appendChild(d); }
    d.textContent = `slide ${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)} | inner ${innerWidth}x${innerHeight} | client ${document.documentElement.clientWidth}x${document.documentElement.clientHeight} | laid ${window.__laid} | dpr ${devicePixelRatio} | scroll ${scrollY} | display ${getComputedStyle(all[cur]).display}`;
  }
  const next = () => cur < N - 1 ? show(cur + 1) : (A && A.next());
  const prev = () => cur > 0 ? show(cur - 1) : (A && A.prev());
  ctl.querySelector('#nx').onclick = e => { e.stopPropagation(); next(); };
  ctl.querySelector('#pv').onclick = e => { e.stopPropagation(); prev(); };
  ctl.querySelector('#cl').onclick = e => { e.stopPropagation(); A && A.close(); };
  // tap the left third for the previous slide, anywhere else for the next; or swipe; or the arrow keys
  let x0 = null, y0 = null, swiped = false;
  document.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; swiped = false; }, { passive: true });
  document.addEventListener('touchend', e => {
    if (x0 == null) return; const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) { swiped = true; dx < 0 ? next() : prev(); } x0 = null;
  }, { passive: true });
  document.addEventListener('click', e => { if (swiped || e.target.closest('button')) return; e.clientX < innerWidth * 0.3 ? prev() : next(); });
  document.addEventListener('keydown', e => {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); next(); }
    if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); prev(); }
  });
  // turned the phone: lay the slides out again for the new shape, at the same point of the lecture
  let t;
  addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => {
    const [w0, h0] = window.__laid || [0, 0], W = Math.max(innerWidth, document.documentElement.clientWidth), H = Math.max(innerHeight, document.documentElement.clientHeight);
    if (Math.abs(W - w0) > w0 * .08 || Math.abs(H - h0) > h0 * .08) location.reload(); }, 300); });
  all[cur].classList.add('on'); show(cur);
})();
"""
START = r"""
try { history.scrollRestoration = 'manual'; } catch (e) {}
(function start(tries) {
  // lay out only on a real, settled landscape screen; sizes in pixels (a WebView can report 0 x 0, a narrow or a
  // short screen while the phone turns, and some give 0 for vh units)
  const W = Math.max(innerWidth, document.documentElement.clientWidth), H = Math.max(innerHeight, document.documentElement.clientHeight);
  const ok = W > 240 && H > 200 && (!window.Android || W > H || tries > 60);
  if (!ok) return setTimeout(() => start(tries + 1), 50);
  const r = document.documentElement.style;
  r.setProperty('--W', W + 'px'); r.setProperty('--H', H + 'px');
  r.setProperty('--f', Math.round(Math.max(14, Math.min(27, Math.min(W * .024, H * .044)))) + 'px');
  window.__laid = [W, H];
  __layout(); __deck();
  // a sane layout has room on its slides; if not (the screen changed under us), lay out again
  const b = document.querySelector('.s .body');
  if (b && b.clientHeight < 120 && tries < 100) setTimeout(() => location.reload(), 300);
})(0);
"""
if os.path.exists(OUT):
    shutil.rmtree(OUT)
index = {"apps": []}
for key, A, name, pdfs in APPS:
    books = json.load(open(f"{A}/index.json"))["books"]
    app = {"key": key, "name": name, "subjects": []}
    for b in books:
        sj = {"id": b["id"], "title": b["title"], "short": b.get("short") or b["title"], "topics": []}
        units = [u["title"] for u in b["units"]]
        n = 0
        for r, info in enumerate(b["rows"]):
            if info.get("hide"):
                continue
            n += 1
            f = f"{OUT}/{key}/{b['id']}/{r}.html"
            os.makedirs(os.path.dirname(f), exist_ok=True)
            h = LP.build(A, b["id"], r, f[:-5] + ".pdf", name)
            doc = open(h).read().replace("</head>", SCREEN + "</head>", 1)
            # lay the slides out only once the screen has its real size (a WebView can start at 0 x 0, or still in
            # portrait while it turns): the layout script and the deck run from START, not as the page loads
            i0 = doc.index("<script>")
            i1 = doc.index("</script>", i0)
            doc = doc[:i0] + "<script>function __layout() {" + doc[i0 + 8:i1] + "}</script>" + doc[i1 + 9:]
            doc = doc.replace("</body>", "<script>function __deck() {" + DECK + "}" + START + "</script></body>", 1)
            if h != f:
                os.unlink(h)
            open(f, "w").write(doc)
            # its slide count, from the PDF made by tools/lecture_all.py
            pdf = glob.glob(f"{pdfs}/{b['id']:02d} */{n:03d} *.pdf")
            pages = 0
            if pdf:
                m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf[0]], capture_output=True, text=True).stdout)
                pages = int(m.group(1)) if m else 0
            sj["topics"].append({"n": n, "row": r, "title": info["title"], "unit": units[info.get("u", 0)] if units else "",
                                 "slides": pages, "q": info.get("q", 0), "file": f"lec/{key}/{b['id']}/{r}.html"})
        app["subjects"].append(sj)
    index["apps"].append(app)
    print(name, sum(len(s["topics"]) for s in app["subjects"]), "lectures")
json.dump(index, open(f"{OUT}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
tot = sum(os.path.getsize(os.path.join(d, x)) for d, _, fs in os.walk(OUT) for x in fs)
print(f"{tot / 1e6:.0f} MB of HTML")
