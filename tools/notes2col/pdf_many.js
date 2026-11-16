// node tools/notes2col/pdf_many.js dir  -> dir/<name>.pdf for every name in dir/list.txt
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = process.argv[2]; const names = fs.readFileSync(path.join(dir, 'list.txt'), 'utf8').split('\n').filter(Boolean);
  const b = await chromium.launch(); const p = await b.newPage();
  for (const n of names) {
    await p.goto('file://' + path.resolve(dir, n + '.html'), { waitUntil: 'load', timeout: 900000 });
    await p.pdf({ path: path.join(dir, n + '.pdf'), format: 'A4', printBackground: true, outline: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: `<div style="font-size:7px;width:100%;padding:0 10mm;display:flex;justify-content:space-between;color:#334155"><span>APPSC Complete — ${n.split('_').slice(0,2).join(' · ')}</span><span class="pageNumber"></span></div>` });
    console.log(n);
  }
  await b.close();
})();
