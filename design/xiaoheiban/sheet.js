// 把六款板面拼成一张对比图：node sheet.js → png/对比图.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const items = [
  ['a-zhiri', 'A 值日黑板', '板子就是一块教室黑板：角上留「值日生」框，用油漆笔写下名字、第一次上雪的日期和雪场'],
  ['b-liangjiao', 'B 量角器', '工程图纸风：固定器位置印角度和站距刻度，新手装固定器照着调就行'],
  ['c-liubai', 'C 留白点阵', '亮油隐形点阵，对齐贴纸用；四角裁切线框出画布，一枚朱红「留白」印'],
  ['d-tiezhiwei', 'D 贴纸位 · 雪场护照', '12 个虚线贴纸位，去一个雪场贴一张限定贴，一季一季攒满'],
  ['e-denggao', 'E 等高线', '板头板尾是两座山的亮油等高线，中间那片雪坡全部留白'],
  ['f-yidaoxian', 'F 第一道线', '整块板只有一道刻滑轨迹，弯顶压刃最重、换刃处最细'],
];
const W = 2400;
const html = `<html><head><style>
body{margin:0;background:#e9e7e2;font-family:'WenQuanYi Zen Hei','Inter',sans-serif;color:#1d1c1a;width:${W}px}
h1{font:600 46px 'Inter Display','WenQuanYi Zen Hei';letter-spacing:4px;margin:60px 80px 6px}
.sub{margin:0 80px 30px;font-size:24px;color:#6b6862}
.row{margin:0 80px 46px}
.t{font-size:30px;font-weight:600;margin-bottom:4px}.d{font-size:22px;color:#6b6862;margin-bottom:10px}
.row div.svg svg{width:${W - 160}px;height:auto;display:block}
</style></head><body>
<h1>VAMEI 小黑板 154 · 板面方向</h1>
<div class="sub">1:1 毫米出图 · 哑光黑底 · 最多一层局部亮油 + 两个专色 · 孔位仅示意 · VAMEI 字样为占位字体</div>
${items.map(([k, t, d]) => `<div class="row"><div class="t">${t}</div><div class="d">${d}</div><div class="svg">${
  fs.readFileSync(path.join(__dirname, 'concepts', k + '.svg'), 'utf8').replace(/width="[^"]*mm" height="[^"]*mm"/, '')
    .replace(/id="board"/g, `id="board-${k}"`).replace(/url\(#board\)/g, `url(#board-${k})`)}</div></div>`).join('')}
</body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: 1000 } });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(__dirname, 'png', '对比图.png'), fullPage: true });
  await b.close(); console.log('→ png/对比图.png');
})();
