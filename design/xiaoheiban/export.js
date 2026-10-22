// 把概念稿导出成给工厂的生产文件：去掉孔位、取消裁切（底色铺满出血）、轮廓改成品红刀线
// 用法：node export.js concepts/h-xiaoren.svg 小黑板-粉笔小人-154
// 输出 export/<名>.svg（矢量）、export/<名>.pdf（1580×340mm，可直接用 Illustrator 打开另存 .ai）、export/<名>-200dpi.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [src, name] = process.argv.slice(2);
let svg = fs.readFileSync(path.resolve(src), 'utf8')
  .replace(/<g id="inserts"[^]*?<\/g>/, '')
  .replace('<g clip-path="url(#board)">', '<g id="artwork">')
  .replace(/<path d="([^"]+)" fill="none" stroke="#3a3a3a" stroke-width="2"\/>/,
    '<g id="dieline-刀线"><path d="$1" fill="none" stroke="#ff00ff" stroke-width="0.35"/></g>');
const out = n => path.join(__dirname, 'export', n);
fs.writeFileSync(out(name + '.svg'), svg);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const page = s => `<html><head><style>@page{size:1580mm 340mm;margin:0}html,body{margin:0}svg{display:block}</style></head><body>${s}</body></html>`;
  await p.setContent(page(svg)); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out(name + '.pdf'), width: '1580mm', height: '340mm', printBackground: true });
  const W = Math.round(1580 / 25.4 * 200), H = Math.round(340 / 25.4 * 200);
  const p2 = await b.newPage({ viewport: { width: W, height: H } });
  await p2.setContent(page(svg.replace(/width="[^"]*mm" height="[^"]*mm"/, `width="${W}" height="${H}"`)));
  await p2.evaluate(() => document.fonts.ready);
  await p2.screenshot({ path: out(name + '-200dpi.png'), clip: { x: 0, y: 0, width: W, height: H } });
  await b.close(); console.log('done', W, H);
})();
