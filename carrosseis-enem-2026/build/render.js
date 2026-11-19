const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  const slugs = JSON.parse(fs.readFileSync('slugs.json'));
  const only = process.argv[2];
  for (const s of slugs) {
    if (only && !s.startsWith(only)) continue;
    await page.goto('file://' + path.resolve(s + '.html'));
    await page.evaluate(() => document.fonts.ready);
    // Ajusta cada tarja para caber na largura (máx. 210px de fonte)
    await page.evaluate(() => {
      document.querySelectorAll('.tarja').forEach(t => {
        let fs = 200; t.style.fontSize = fs + 'px';
        while (t.offsetWidth > 930 && fs > 80) { fs -= 2; t.style.fontSize = fs + 'px'; }
      });
    });
    const out = path.resolve('..', s);
    fs.mkdirSync(out, { recursive: true });
    const els = await page.$$('section.slide');
    for (let i = 0; i < els.length; i++) {
      await els[i].screenshot({ path: `${out}/slide-${String(i + 1).padStart(2, '0')}.png` });
    }
    const overflow = await page.$$eval('section.slide', ss => ss.map((s, i) => {
      const r = s.getBoundingClientRect();
      let m = 0;
      s.querySelectorAll('.body,.boxes,.stats,.note,.bigline,.ctitle,.csub,.endq').forEach(e => {
        const q = e.getBoundingClientRect(); if (q.bottom > m) m = q.bottom;
      });
      return [i + 1, Math.round(m - r.top)];
    }).filter(x => x[1] > 1250));
    console.log(s, els.length, 'overflow:', JSON.stringify(overflow));
  }
  await browser.close();
})();
