// Clean Excalidraw-style infographic from a brief JSON (brief2json.py): writes .excalidraw and .png.
//   node infographic.js in.json out.png out.excalidraw [in2 out2 ex2 ...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

function layout(brief, measure) {
  const W = 1600, PAD = 40, GAP = 30, COLW = (W - 2 * PAD - GAP) / 2;
  const FILLS = ['#a5d8ff', '#b2f2bb', '#ffd8a8', '#d0bfff', '#ffc9c9', '#c3fae8', '#fff3bf', '#eebefa'];
  const STROKES = ['#1971c2', '#2f9e44', '#e8590c', '#6741d9', '#e03131', '#0c8599', '#f08c00', '#9c36b5'];
  let seed = 1; const els = [];
  const base = (o) => Object.assign({ angle: 0, strokeColor: '#1e1e1e', backgroundColor: 'transparent', fillStyle: 'solid',
    strokeWidth: 2, strokeStyle: 'solid', roughness: 1, opacity: 100, seed: seed++, version: 1, versionNonce: seed,
    isDeleted: false, groupIds: [], boundElements: null, link: null, locked: false, updated: 1, frameId: null }, o);
  const rect = (x, y, w, h, o = {}) => els.push(base(Object.assign({ type: 'rectangle', id: 'e' + seed, x, y, width: w, height: h, roundness: { type: 3 } }, o)));
  const fontOf = (fam) => fam === 1 ? 'Virgil' : 'Helvetica';
  const wrap = (t, size, fam, maxw) => {
    const out = [];
    for (const para of String(t).split('\n')) {
      let line = '';
      for (const w of para.split(' ')) {
        const tryl = line ? line + ' ' + w : w;
        if (measure(tryl, size, fontOf(fam)) <= maxw || !line) line = tryl; else { out.push(line); line = w; }
      }
      out.push(line);
    }
    return out;
  };
  const text = (x, y, t, size, fam, maxw, o = {}) => {
    const lines = wrap(t, size, fam, maxw), lh = 1.25, h = Math.ceil(lines.length * size * lh);
    const w = Math.ceil(Math.max(...lines.map(l => measure(l, size, fontOf(fam)))));
    const s = lines.join('\n');
    els.push(base(Object.assign({ type: 'text', id: 'e' + seed, x, y, width: w, height: h, strokeWidth: 1, text: s, originalText: s,
      fontSize: size, fontFamily: fam, textAlign: 'left', verticalAlign: 'top', baseline: h - Math.round(size * 0.3), containerId: null, lineHeight: lh }, o)));
    return h;
  };
  // title
  const tl = wrap(brief.title, 46, 1, W - 2 * PAD - 60), th = tl.length * 46 * 1.25 + 50;
  rect(PAD, PAD, W - 2 * PAD, th, { backgroundColor: '#1e3a5f', strokeColor: '#1e3a5f' });
  text(PAD + 30, PAD + 25, brief.title, 46, 1, W - 2 * PAD - 60, { strokeColor: '#ffffff' });
  let y0 = PAD + th + GAP;
  // panels: tables span the width; bullet panels flow in two columns (shortest column first)
  const colY = [y0, y0];
  brief.panels.forEach((p, i) => {
    const fill = FILLS[i % FILLS.length], stroke = STROKES[i % STROKES.length];
    const isTable = p.table && p.table.rows.length;
    const n = String(i + 1);
    const measureBlock = (w) => {  // height of the panel body
      let h = 0;
      if (p.bullets) for (const b of p.bullets) h += wrap(b, 22, 2, w - 70).length * 22 * 1.25 + 12;
      return h;
    };
    if (isTable) {
      const y = Math.max(colY[0], colY[1]), w = W - 2 * PAD;
      const head = p.table.head, rows = p.table.rows, nc = head.length;
      const lens = head.map((_, c) => Math.max(...[head[c], ...rows.map(r => r[c] || '')].map(s => String(s).length)));
      const tot = lens.reduce((a, b) => a + Math.max(b, 8), 0);
      const cw = lens.map(l => Math.max(l, 8) / tot * (w - 40));
      // header bar
      const hh = 60;
      rect(PAD, y, w, hh, { backgroundColor: fill, strokeColor: stroke });
      text(PAD + 20, y + 14, n + '.  ' + (p.h || ''), 30, 1, w - 40, { strokeColor: '#1e1e1e' });
      let yy = y + hh + 10;
      const rowH = (r, size) => Math.max(...r.map((c, k) => wrap(c || '', size, 2, cw[k] - 24).length)) * size * 1.25 + 20;
      const all = [head, ...rows];
      all.forEach((r, ri) => {
        const isH = ri === 0, size = isH ? 22 : 21, h = rowH(r, size);
        let x = PAD + 20;
        r.forEach((c, k) => {
          rect(x, yy, cw[k], h, { backgroundColor: isH ? fill : (ri % 2 ? '#ffffff' : '#f8f9fa'), strokeColor: stroke, strokeWidth: 1, roundness: null });
          text(x + 12, yy + 10, c || '', size, isH ? 1 : 2, cw[k] - 24, { strokeColor: '#1e1e1e' });
          x += cw[k];
        });
        yy += h;
      });
      if (p.bullets && p.bullets.length) {
        yy += 10;
        for (const b of p.bullets) { text(PAD + 30, yy, '•', 22, 2, 20); yy += text(PAD + 55, yy, b, 22, 2, w - 80) + 12; }
      }
      colY[0] = colY[1] = yy + GAP;
    } else {
      const c = colY[0] <= colY[1] ? 0 : 1, x = PAD + c * (COLW + GAP), y = colY[c];
      const hl = wrap(n + '.  ' + (p.h || ''), 28, 1, COLW - 40), hh = hl.length * 28 * 1.25 + 26;
      const bh = measureBlock(COLW) + 20;
      rect(x, y, COLW, hh + bh, { backgroundColor: fill, strokeColor: stroke, opacity: 25 });
      rect(x, y, COLW, hh, { backgroundColor: fill, strokeColor: stroke });
      text(x + 20, y + 13, n + '.  ' + (p.h || ''), 28, 1, COLW - 40);
      let yy = y + hh + 14;
      for (const b of p.bullets) {
        els.push(base({ type: 'ellipse', id: 'e' + seed, x: x + 24, y: yy + 8, width: 10, height: 10, backgroundColor: stroke, strokeColor: stroke, strokeWidth: 1 }));
        yy += text(x + 48, yy, b, 22, 2, COLW - 70) + 12;
      }
      colY[c] = y + hh + bh + GAP;
    }
  });
  return els;
}

(async () => {
  const a = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent('<html><body></body></html>');
  const ff = (n, f) => `@font-face{font-family:"${n}";src:url(data:font/woff2;base64,${fs.readFileSync(path.join(__dirname, 'fonts', f)).toString('base64')}) format("woff2");}`;
  await page.addStyleTag({ content: ff('Virgil', 'Virgil.woff2') + ff('Cascadia', 'Cascadia.woff2') + '@font-face{font-family:"Helvetica";src:local("DejaVu Sans");}' });
  await page.evaluate(async () => { await document.fonts.load('20px Virgil'); await document.fonts.load('20px Helvetica'); await document.fonts.ready; });
  await page.addScriptTag({ path: path.join(__dirname, 'node_modules/@excalidraw/utils/dist/excalidraw-utils.min.js') });
  await page.addScriptTag({ content: 'window.__layout = ' + layout.toString() + ';' });
  for (let i = 0; i < a.length; i += 3) {
    const brief = JSON.parse(fs.readFileSync(a[i], 'utf8'));
    const r = await page.evaluate(async (brief) => {
      const cv = document.createElement('canvas').getContext('2d');
      const measure = (t, size, font) => { cv.font = `${size}px ${font}`; return cv.measureText(t).width; };
      const elements = window.__layout(brief, measure);
      const blob = await ExcalidrawUtils.exportToBlob({ elements, appState: { exportBackground: true, viewBackgroundColor: '#ffffff' },
        files: null, mimeType: 'image/png', exportPadding: 30, getDimensions: (w, h) => ({ width: w * 1.5, height: h * 1.5, scale: 1.5 }) });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let s = ''; for (let k = 0; k < buf.length; k++) s += String.fromCharCode(buf[k]);
      return { png: btoa(s), elements };
    }, brief);
    fs.writeFileSync(a[i + 1], Buffer.from(r.png, 'base64'));
    fs.writeFileSync(a[i + 2], JSON.stringify({ type: 'excalidraw', version: 2, source: 'appsc-group2', elements: r.elements,
      appState: { viewBackgroundColor: '#ffffff' }, files: {} }));
    console.log('wrote', a[i + 1]);
  }
  await browser.close();
})();
