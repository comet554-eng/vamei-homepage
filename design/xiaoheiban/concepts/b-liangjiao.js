// VAMEI 小黑板 154 · 概念 b-liangjiao「量角器」
// 功能性制图工具板面：固定器角度量角弧 + 站距刻度 + 边尺 + 标题栏。其余全部留白。
// 单位 mm，原点在板中心，+x 为板头（nose）。
const fs = require('fs');
const path = require('path');
const { geo, template } = require('../board.js');

// ---- 生产色（最多两个专色 + 一层亮油） ----
const CHALK = '#d6d1c6';   // 专色 1：暖粉笔灰
const RED = '#e04a2f';     // 专色 2：朱红（只用于零位 / 基准记号）
const GLOSS = '#242424';   // 亮油（局部 UV）在 #141414 哑光底上的模拟

const f = n => +(+n).toFixed(2);
const rad = d => d * Math.PI / 180;

// 板半宽（侧切段），用于检查边距
const hw = x => {
  const ax = Math.abs(x);
  if (ax <= 567) return 126 + (geo.R - Math.sqrt(geo.R * geo.R - ax * ax));
  return 148;
};

const text = (x, y, s, size, opt = {}) => {
  const { anchor = 'middle', weight = 500, fill = CHALK, rot = 0, ls = 0, family = 'Inter' } = opt;
  const tr = rot ? ` transform="rotate(${f(rot)} ${f(x)} ${f(y)})"` : '';
  return `<text x="${f(x)}" y="${f(y)}" font-family="${family}" font-feature-settings="'tnum' 1" font-size="${size}" font-weight="${weight}" letter-spacing="${ls}" text-anchor="${anchor}" fill="${fill}"${tr}>${s}</text>`;
};
const line = (x1, y1, x2, y2, w, col = CHALK) =>
  `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${col}" stroke-width="${w}" stroke-linecap="butt"/>`;

// ---- 1. 量角弧：每只脚上下两段，−30°…+30°，3° 一格（多数固定器底盘的调节步进），15° 标数 ----
// 约定：正角 = 脚尖朝板头。读数看脚尖一侧的弧，两侧弧都按“朝板头为 +”标注。
// 整圆与 0° 轴线做亮油（只在光下可见），油墨只印 ±30° 两段。
const R0 = 88;
function protractor(cx) {
  const A = 30;
  let ink = '', gloss = '';
  gloss += `<circle cx="${cx}" cy="0" r="${R0}" fill="none" stroke="${GLOSS}" stroke-width="1.2"/>`;
  gloss += line(cx, -R0, cx, R0, 1.2, GLOSS);
  for (const side of [-1, 1]) {  // -1 上边（y<0），+1 下边（y>0）
    const P = (a, r) => [cx + r * Math.sin(rad(a)), side * r * Math.cos(rad(a))];
    const [sx, sy] = P(-A - 1.5, R0), [ex, ey] = P(A + 1.5, R0);
    const sweep = side < 0 ? 1 : 0;
    ink += `<path d="M ${f(sx)} ${f(sy)} A ${R0} ${R0} 0 0 ${sweep} ${f(ex)} ${f(ey)}" fill="none" stroke="${CHALK}" stroke-width="0.8"/>`;
    for (let a = -A; a <= A; a += 3) {
      const major = a % 15 === 0;
      const len = a === 0 ? 9 : major ? 7 : 3.5;
      const [x1, y1] = P(a, R0), [x2, y2] = P(a, R0 - len);
      ink += line(x1, y1, x2, y2, major ? 0.8 : 0.6, a === 0 ? RED : CHALK);
      if (major) {
        const lab = a === 0 ? '0' : (a > 0 ? '+' : '−') + Math.abs(a);
        const rot = side < 0 ? a : -a;                         // 沿切线、保持正读
        const [bx, by] = P(a, R0 - 9 - (side < 0 ? 7.2 : 3.0)); // 上弧文字向下排，下弧文字向上排
        ink += text(bx, by, lab, 5.8, { rot, fill: a === 0 ? RED : CHALK });
      }
    }
  }
  return { ink, gloss };
}

// ---- 2. 站距刻度：两排孔中间的中线上，固定器底盘中心对准即可 ----
function stanceScale(sign) {
  let out = '';
  out += line(sign * 224, 0, sign * 316, 0, 0.6);
  for (let W = 460; W <= 620; W += 20) {
    const x = sign * W / 2;
    const major = (W - 460) % 40 === 0;
    const ref = W === 540;
    out += line(x, 0, x, major ? -6 : -3.5, major ? 0.8 : 0.6, ref ? RED : CHALK);
    if (major) out += text(x, 7.6, String(W), 5.8, { fill: ref ? RED : CHALK });
  }
  return out;
}

// ---- 3. 边尺：上边沿，中心为零，±550，5 mm 一格 ----
function edgeRuler() {
  const Y = -118, X = 550;
  let out = line(-X, Y, X, Y, 0.7);
  for (let x = -X; x <= X; x += 5) {
    const m100 = x % 100 === 0, m50 = x % 50 === 0, m10 = x % 10 === 0;
    const len = (m100 || Math.abs(x) === X) ? 8 : m50 ? 5.5 : m10 ? 4 : 2.5;
    out += line(x, Y, x, Y + len, m100 ? 0.8 : 0.6, x === 0 ? RED : CHALK);
    if (m100) out += text(x, Y + len + 6.4, String(Math.abs(x)), 5.8, { fill: x === 0 ? RED : CHALK });
  }
  return out;
}

// ---- 4. 标题栏：板头一侧右下角；最后一行“制图”留空，给骑手签名 ----
function titleBlock() {
  const x0 = 474, y0 = 76, w = 152, h1 = 22, h2 = 13, h3 = 14, h = h1 + h2 + h3;
  const c1 = 100;                      // 第一行分隔
  const c2 = [44, 92, 122];            // 第二行分隔
  const c3 = 26;                       // 第三行分隔
  let out = `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="none" stroke="${CHALK}" stroke-width="1"/>`;
  out += line(x0, y0 + h1, x0 + w, y0 + h1, 0.6);
  out += line(x0, y0 + h1 + h2, x0 + w, y0 + h1 + h2, 0.6);
  out += line(x0 + c1, y0, x0 + c1, y0 + h1, 0.6);
  for (const c of c2) out += line(x0 + c, y0 + h1, x0 + c, y0 + h1 + h2, 0.6);
  out += line(x0 + c3, y0 + h1 + h2, x0 + c3, y0 + h, 0.6);
  out += text(x0 + 7, y0 + 16, 'VAMEI', 14, { anchor: 'start', weight: 600, family: 'Inter Display', ls: 2.2 });
  out += text(x0 + c1 + (w - c1) / 2, y0 + 15, '小黑板', 9.5, { family: 'WenQuanYi Zen Hei', weight: 400, ls: 1 });
  const cells = [[0, 44, '154'], [44, 92, '26/27'], [92, 122, '1:1'], [122, w, 'mm']];
  for (const [a, b, s] of cells) out += text(x0 + (a + b) / 2, y0 + h1 + 9.1, s, 5.8);
  out += text(x0 + c3 / 2, y0 + h1 + h2 + 9.3, '制图', 5.6, { family: 'WenQuanYi Zen Hei', weight: 400, ls: 0.6 });
  return out;
}

// ---- 5. 技术要求（标题栏上方） ----
function notes() {
  const x0 = 474, y0 = 42, lh = 8;
  const CN = { family: 'WenQuanYi Zen Hei', weight: 400, anchor: 'start' };
  let out = text(x0, y0, '技术要求', 6.2, { ...CN, ls: 1.2 });
  ['1. 角度以脚尖朝板头为正。', '2. 底盘中心对准站距刻度。', '3. 未注区域留白，由你自由绘制。']
    .forEach((s, i) => { out += text(x0, y0 + 9 + i * lh, s, 5.6, CN); });
  return out;
}

// ---- 亮油层：中心线（点划线）+ 中心基准 ----
function glossLayer() {
  let g = `<line x1="-735" y1="0" x2="735" y2="0" stroke="${GLOSS}" stroke-width="1" stroke-dasharray="30 4 3 4"/>`;
  g += line(0, -14, 0, 14, 1, GLOSS);
  return g;
}

// ---- 按生产分色输出：亮油 / 专色 1 粉笔灰 / 专色 2 朱红 ----
const P1 = protractor(270), P2 = protractor(-270);
const inkAll = [P1.ink, P2.ink, stanceScale(1), stanceScale(-1), edgeRuler(), notes(), titleBlock()].join('');
const els = inkAll.match(/<(text|line|path|rect)[^>]*?(\/>|>[^<]*<\/text>)/g);
if (els.join('') !== inkAll) throw new Error('layer split lost elements');
const isRed = e => e.includes(RED);
const body = [
  `<g id="spot-uv-gloss">${glossLayer()}${P1.gloss}${P2.gloss}</g>`,
  `<g id="ink-1-chalk">${els.filter(e => !isRed(e)).join('')}</g>`,
  `<g id="ink-2-red">${els.filter(isRed).join('')}</g>`,
].join('\n');

const out = path.join(__dirname, 'b-liangjiao.svg');
fs.writeFileSync(out, template(body));
console.log('wrote', out, 'hw(0)=', hw(0).toFixed(1), 'hw(270)=', hw(270).toFixed(1), 'hw(550)=', hw(550).toFixed(1));
