// node tools/html_to_pdf.js <in.html> <out.pdf> <footer title>
const { chromium } = require('playwright');
(async () => {
  const [inp, out, title] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(inp));
  await p.waitForTimeout(500);
  await p.pdf({ path: out, format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '16mm', left: '14mm', right: '14mm' }, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="font-size:8px;color:#9ca3af;width:100%;text-align:center;font-family:Inter">${title} · <span class="pageNumber"></span> / <span class="totalPages"></span></div>` });
  await b.close();
})();
