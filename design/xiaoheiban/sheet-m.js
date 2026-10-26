// 拼「结构组合」设计稿：node sheet-m.js → png/结构组合设计稿.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const rd = n => fs.readFileSync(path.join(__dirname, 'concepts', n), 'utf8').replace(/width="[^"]*mm" height="[^"]*mm"/, '');
const C = [['orange', '荧光橙'], ['blue', '冰川蓝'], ['yellow', '柠檬黄']];
const W = 2400;
const html = `<html><head><style>
body{margin:0;background:#e9e7e2;font-family:'WenQuanYi Zen Hei',sans-serif;color:#1d1c1a;width:${W}px}
.w{padding:60px 80px 50px}
h1{font:600 46px 'Inter Display','WenQuanYi Zen Hei';margin:0 0 6px;letter-spacing:2px}
.sub{font-size:24px;color:#6b6862;margin-bottom:30px}
h2{font-size:30px;margin:34px 0 6px}
.d{font-size:22px;color:#6b6862;margin-bottom:8px}
svg{display:block;width:100%;height:auto}
.row{display:grid;grid-template-columns:1fr;gap:4px;margin-bottom:22px}
.tag{display:inline-block;width:22px;height:22px;border-radius:5px;vertical-align:-3px;margin-right:10px}
</style></head><body><div class="w">
<h1>VAMEI 小黑板 154 · 结构组合</h1>
<div class="sub">纯黑面材 + 360° 彩色包边 + 同色护角 + 板头金属挂孔 + 一体压纹止滑区 · 示意稿，尺寸以工厂打样为准</div>
${C.map(([k, n]) => `<div class="row"><h2><span class="tag" style="background:${{ orange: '#ff6a1a', blue: '#5cc8ff', yellow: '#ffd23f' }[k]}"></span>${n}</h2>
  ${rd(`m-zuhe-${k}.svg`)}${rd(`m-zuhe-${k}-side.svg`)}</div>`).join('')}
<h2>尺寸与位置</h2><div class="d">单位 mm · 侧视图纵向放大 3 倍，仅示意混合拱：两脚之间正拱，接触点外上翘</div>
${rd('m-zuhe-tech.svg')}
</div></body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: 1000 } });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(__dirname, 'png', '结构组合设计稿.png'), fullPage: true });
  await b.close(); console.log('ok');
})();
