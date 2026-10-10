// 生成一集的全部封面尺寸：node video/covers.js <影片.html> <输出前缀>
// 例：node video/covers.js video/ski-ep01.html video/滑雪不难EP01-封面
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [film, prefix] = process.argv.slice(2);
const NAMES = { '9x16': '竖版9x16', '3x4': '竖版3x4', '16x9': '横版16x9', '4x3': '横版4x3' };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto('file://' + path.resolve(film) + '?render');
  await page.waitForFunction(() => window.FILM && window.FILM.ready, null, { timeout: 60000 });
  const covers = await page.evaluate(() => FILM.covers());
  for (const [k, url] of Object.entries(covers)) {
    const out = `${prefix}-${NAMES[k] || k}.jpg`;
    fs.writeFileSync(out, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
    console.log('→', out);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
