// Render a manual HTML to an A4 PDF: node tools/pyqdecode_pdf.js <in.html> <out.pdf> "<footer title>"
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, out, title] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto('file://' + path.resolve(inp), { waitUntil: 'load', timeout: 0 });
  await pg.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true, outline: true, tagged: false,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="font-family:DejaVu Sans,sans-serif;font-size:7pt;width:100%;text-align:center;color:#666">${title} · <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
    margin: { top: '14mm', bottom: '16mm', left: '13mm', right: '13mm' }, timeout: 0 });
  await b.close();
})();
