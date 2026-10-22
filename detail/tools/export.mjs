// 导出详情页：
//   out/sections/NN.jpg   每屏一张，1500 宽（2 倍）
//   out/taobao/NN-k.jpg   淘宝手机详情切片，1242 宽，每张高度不超过 1546
//   out/nuage-full.jpg    整页长图预览，750 宽
// 用法: node tools/export.mjs [src/page.html]
import { serve, launch } from './render.mjs';
import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = process.argv[2] || 'src/page.html';
const OUT = path.join(ROOT, 'out');
for (const d of ['sections', 'taobao']) { fs.rmSync(path.join(OUT, d), { recursive: true, force: true }); fs.mkdirSync(path.join(OUT, d), { recursive: true }); }

const srv = await serve(); const browser = await launch();
const url = `http://127.0.0.1:${srv.address().port}/${src}`;

async function open(scale) {
  const page = await browser.newPage({ viewport: { width: 750, height: 1400 }, deviceScaleFactor: scale });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto(url);
  await page.waitForFunction(() => window.__READY === true, null, { timeout: 180000 });
  return page;
}
const ids = page => page.$$eval('.screen', els => els.map(e => e.id));
// 只显示一屏再截图：整页太高时 Chromium 截图会出错，单屏不会
async function solo(page, id) {
  await page.evaluate(id => document.querySelectorAll('.screen').forEach(e => { e.style.display = e.id === id ? '' : 'none'; }), id);
  return page.$eval('#' + id, e => e.getBoundingClientRect().height);
}

// 每屏 2 倍
let page = await open(2);
for (const id of await ids(page)) {
  const h = await solo(page, id);
  await page.screenshot({ path: path.join(OUT, 'sections', `${id.slice(1)}.jpg`), type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: 750, height: h }, fullPage: true });
}
await page.close();

// 淘宝切片：1242 宽，单张高度 ≤ 1546
const S = 1242 / 750, MAXH = 1546 / S;
page = await open(S);
for (const id of await ids(page)) {
  const h = await solo(page, id), n = Math.ceil(h / MAXH);
  for (let k = 0; k < n; k++) {
    const y0 = Math.round((h * k) / n), y1 = Math.round((h * (k + 1)) / n);
    await page.screenshot({ path: path.join(OUT, 'taobao', `${id.slice(1)}-${k + 1}.jpg`), type: 'jpeg', quality: 90, clip: { x: 0, y: y0, width: 750, height: y1 - y0 }, fullPage: true });
  }
}
await page.close();

await browser.close(); srv.close();

// 整页 1 倍预览：Chromium 单张截图超过 16384px 会重复贴图，所以把 2 倍分屏图缩小后拼起来
const { execFileSync } = await import('child_process');
execFileSync('python3', ['-I', '-c', `
import sys, glob
from PIL import Image
files = sorted(glob.glob(sys.argv[1] + '/*.jpg'))
ims = [Image.open(f) for f in files]
ims = [im.resize((750, round(im.height * 750 / im.width)), Image.LANCZOS) for im in ims]
out = Image.new('RGB', (750, sum(im.height for im in ims)))
y = 0
for im in ims: out.paste(im, (0, y)); y += im.height
out.save(sys.argv[2], quality=85)
`, path.join(OUT, 'sections'), path.join(OUT, 'nuage-full.jpg')]);
console.log('exported to', OUT);
