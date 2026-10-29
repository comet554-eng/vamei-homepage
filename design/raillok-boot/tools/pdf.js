// 把排版 html 打印成 PDF（页面尺寸取 html 里的 @page）
// usage: node tools/pdf.js <in.html> <out.pdf>
const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pathToFileURL(path.resolve(inp)).href);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
