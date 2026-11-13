// 把 panel.html（右侧色卡栏）打印成和线稿同尺寸的 PDF
// usage: node tools/panel.js <out.pdf>
const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const out = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pathToFileURL(path.join(__dirname, 'panel.html')).href);
  await page.evaluate(() => document.fonts.ready);
  // 页面尺寸取 panel.html 里的 @page
  await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
