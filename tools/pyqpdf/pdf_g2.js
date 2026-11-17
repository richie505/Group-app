// node tools/mindmap/pdf.js in.html out.pdf  (Playwright's Chromium)
const { chromium } = require('playwright');
(async () => {
  const [,, inp, out] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(inp), {waitUntil: 'load', timeout: 900000});
  await p.pdf({ path: out, format: 'A4', printBackground: true, outline: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:7px;width:100%;padding:0 10mm;display:flex;justify-content:space-between;color:#334155"><span>APPSC Group 2 — Previous Year Questions</span><span class="pageNumber"></span></div>' });
  await b.close();
})();
