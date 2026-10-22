// 把板面 SVG 渲染成 PNG 预览。用法：node render.js 输入.svg [输出.png] [宽度px，默认 3000]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [inp, outArg, wArg] = process.argv.slice(2);
  const src = path.resolve(inp);
  const out = path.resolve(outArg || path.join(__dirname, 'png', path.basename(src, '.svg') + '.png'));
  const W = +(wArg || 3000), H = Math.round(W * 340 / 1580);
  let svg = fs.readFileSync(src, 'utf8').replace(/width="[^"]*mm" height="[^"]*mm"/, `width="${W}" height="${H}"`);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.setContent(`<html><body style="margin:0;background:#e9e7e2">${svg}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: W, height: H } });
  await browser.close();
  console.log('→', out);
})().catch(e => { console.error(e); process.exit(1); });
