// Render .excalidraw scenes to PNG in headless Chromium with @excalidraw/utils.
//   node tools/excalinfo/render.js in.excalidraw out.png [in2 out2 ...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const a = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent('<html><body></body></html>');
  const ff = (n, f) => `@font-face{font-family:"${n}";src:url(data:font/woff2;base64,${fs.readFileSync(path.join(__dirname, 'fonts', f)).toString('base64')}) format("woff2");}`;
  await page.addStyleTag({ content: ff('Virgil', 'Virgil.woff2') + ff('Cascadia', 'Cascadia.woff2') +
    '@font-face{font-family:"Helvetica";src:local("DejaVu Sans");}' });
  await page.evaluate(async () => { await document.fonts.load('20px Virgil'); await document.fonts.load('20px Helvetica'); await document.fonts.ready; });
  await page.addScriptTag({ path: path.join(__dirname, 'node_modules/@excalidraw/utils/dist/excalidraw-utils.min.js') });
  for (let i = 0; i < a.length; i += 2) {
    const scene = JSON.parse(fs.readFileSync(a[i], 'utf8'));
    const b64 = await page.evaluate(async (scene) => {
      const blob = await ExcalidrawUtils.exportToBlob({
        elements: scene.elements, appState: { exportBackground: true, viewBackgroundColor: '#ffffff', exportScale: 2 },
        files: null, mimeType: 'image/png', getDimensions: (w, h) => ({ width: w * 2, height: h * 2, scale: 2 }) });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let s = ''; for (let k = 0; k < buf.length; k++) s += String.fromCharCode(buf[k]);
      return btoa(s);
    }, scene);
    fs.writeFileSync(a[i + 1], Buffer.from(b64, 'base64'));
    console.log('wrote', a[i + 1]);
  }
  await browser.close();
})();
