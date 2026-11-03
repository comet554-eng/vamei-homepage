// 把 svg 渲染成 png
// usage: node tools/png.js <in.svg> <out.png> [scale] [背景色，不给就是透明底]
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [inp, out, scale = 3, bg] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: +scale });
  const svg = fs.readFileSync(inp, 'utf8');
  await page.setContent(`<html><body style="margin:0;background:${bg || 'transparent'}">${svg}</body></html>`);
  const el = await page.$('svg');
  await el.screenshot({ path: out, omitBackground: !bg });
  await browser.close();
})();
