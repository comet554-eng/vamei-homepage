// 用法: node tools/render.mjs <相对 detail/ 的 html 路径> <out.png> [--w 750] [--h 1000] [--scale 2] [--sel '#id'] [--transparent] [--full] [--query a=1] [--timeout 180000]
// 起一个本地静态服务器（根目录 = detail/），页面需在可以截图时设置 window.__READY = true。
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff' };
export function serve() {
  const srv = http.createServer((q, s) => {
    const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
    if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { s.writeHead(404); return s.end(); }
    s.writeHead(200, { 'Content-Type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' }); fs.createReadStream(f).pipe(s);
  });
  return new Promise(r => srv.listen(0, '127.0.0.1', () => r(srv)));
}
export async function launch() {
  return chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--font-render-hinting=none'] });
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const a = process.argv.slice(2);
  const opt = (k, d) => { const i = a.indexOf('--' + k); return i < 0 ? d : (a[i + 1] && !a[i + 1].startsWith('--') ? a[i + 1] : true); };
  const [src, out] = a;
  const w = +opt('w', 750), h = +opt('h', 1000), scale = +opt('scale', 2);
  const srv = await serve(); const browser = await launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  const rel = path.relative(ROOT, path.resolve(src)).split(path.sep).join('/');
  await page.goto(`http://127.0.0.1:${srv.address().port}/${rel}${opt('query', '') ? '?' + opt('query', '') : ''}`);
  await page.waitForFunction(() => window.__READY === true, null, { timeout: +opt('timeout', 180000) });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const shot = { path: out, omitBackground: !!opt('transparent', false) };
  if (opt('sel', '')) await page.locator(opt('sel')).screenshot(shot);
  else await page.screenshot({ ...shot, fullPage: !!opt('full', false) });
  console.log('rendered', out);
  await browser.close(); srv.close();
}
