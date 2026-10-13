// 「值日黑板」a-zhiri —— 板面就是一块教室黑板
// 用法：node concepts/a-zhiri.js  → 写出 concepts/a-zhiri.svg
const fs = require('fs');
const path = require('path');
const { geo, template } = require('../board.js');

// ---- 色板：底色 #141414（哑光），一层光油 UV，一个专色（粉笔白）----
const BASE = '#141414';
const CHALK = '#e2ded2';   // 专色 1：粉笔白（暖灰白，非纯白）
const GLOSS = '#202020';   // 局部光油 UV（同色调亮面），示意色

// ---- 小工具 ----
const f = n => +n.toFixed(2);
function rng(seed) { return () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }; }
const ZH = "'WenQuanYi Zen Hei'";
const LAT = "'Inter Display'";
function txt(x, y, s, size, o = {}) {
  const c = o.fill || CHALK;
  return `<text x="${f(x)}" y="${f(y)}" font-family="${o.font || ZH}" font-size="${size}"` +
    (o.weight ? ` font-weight="${o.weight}"` : '') +
    (o.anchor ? ` text-anchor="${o.anchor}"` : '') +
    (o.ls != null ? ` letter-spacing="${o.ls}"` : '') +
    ` fill="${c}"` +
    (o.bold ? ` stroke="${c}" stroke-width="${o.bold}" stroke-linejoin="round" paint-order="stroke"` : '') +
    `>${s}</text>`;
}
const line = (x1, y1, x2, y2, w = 1.1, extra = '') =>
  `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${CHALK}" stroke-width="${w}" stroke-linecap="butt"${extra}/>`;

// ============ 1. 光油层：黑板刚被擦过 —— 几道板擦弧（只在侧光下看得见）============
function eraserSwipes() {
  const r = rng(11);
  const out = [];
  // 手臂挥动的弧：圆心在板外，半径大；每道宽 ≈ 板擦宽 50mm
  // 一遍一遍往下擦：圆心都在下方（肩膀），每道略错开，像值日生刚擦完
  const arcs = [
    { cx: -90, cy: 690, R: 770, a0: -117, a1: -70, W: 50 },
    { cx: 60, cy: 770, R: 800, a0: -112, a1: -68, W: 48 },
    { cx: -40, cy: 860, R: 846, a0: -106, a1: -75, W: 50 },
    { cx: 110, cy: 960, R: 885, a0: -101, a1: -79, W: 42 },
  ];
  for (const A of arcs) {
    const lane = 1.25;
    const n = Math.round(A.W / lane);
    for (let i = 0; i < n; i++) {
      const o = (i / (n - 1) - 0.5) * A.W;
      const e = Math.abs(o) / (A.W / 2);             // 0 中线 → 1 边缘
      if (r() < e * e * 0.7) continue;
      const span = A.a1 - A.a0;
      const a0 = A.a0 + span * (0.02 + r() * 0.08 + e * 0.1);
      const a1 = A.a1 - span * (0.02 + r() * 0.08 + e * 0.1);
      const rad = A.R + o;
      const p = a => [A.cx + rad * Math.cos(a * Math.PI / 180), A.cy + rad * Math.sin(a * Math.PI / 180)];
      const [x0, y0] = p(a0), [x1, y1] = p(a1);
      // 断续的笔触：随机虚线，越靠边越稀
      const dash = [];
      for (let k = 0; k < 10; k++) dash.push(f(4 + r() * 40 * (1 - e * 0.7)), f(1 + r() * 10 * (0.4 + e)));
      const w = f(0.65 + r() * 0.55);
      out.push(`<path d="M ${f(x0)} ${f(y0)} A ${f(rad)} ${f(rad)} 0 0 1 ${f(x1)} ${f(y1)}" fill="none" stroke="${GLOSS}" stroke-width="${w}" stroke-dasharray="${dash.join(' ')}" stroke-dashoffset="${f(r() * 60)}"/>`);
    }
  }
  return `<g id="spot-uv-eraser">${out.join('')}</g>`;
}

// ============ 2. 值日栏（板头右上角，像黑板上用白漆画好的格子）============
function tianzige(x, y, s) {           // 田字格：实线外框 + 虚线十字
  const g = [];
  g.push(`<rect x="${f(x)}" y="${f(y)}" width="${s}" height="${s}" fill="none" stroke="${CHALK}" stroke-width="1.1"/>`);
  const d = ' stroke-dasharray="2.2 2.2"';
  g.push(line(x + s / 2, y + 2.2, x + s / 2, y + s - 2.2, 0.8, d));
  g.push(line(x + 2.2, y + s / 2, x + s - 2.2, y + s / 2, 0.8, d));
  return g.join('');
}

function dutyCorner() {
  const g = [];
  const x0 = 512;                 // 左对齐线
  const lab = 8;                  // 标签字号（汉字字身约 7mm）
  const cell = 21;
  const col = x0 + 48;            // 填写区起点
  const xEnd = col + cell * 4;
  // 眉题：像老师每天写在黑板右上角的那一行
  g.push(txt(x0, -110, '小黑板', 6.4, { ls: 1.4, bold: 0.25 }));
  g.push(txt(xEnd, -110, '26/27 学年', 6.4, { anchor: 'end', bold: 0.25 }));
  g.push(line(x0, -105.5, xEnd, -105.5, 0.9));
  // 值日生 + 四个田字格
  const ty = -97;
  g.push(txt(x0, ty + cell / 2 + 2.9, '值日生', lab, { ls: 0.6, bold: 0.3 }));
  for (let i = 0; i < 4; i++) g.push(tianzige(col + i * cell, ty, cell));
  // 其余三栏：标签 + 下划线
  const rows = [
    { k: '第一次上雪', y: -56, date: true },
    { k: '雪场', y: -37 },
    { k: '摔跤', y: -18 },
  ];
  for (const R of rows) {
    g.push(txt(x0, R.y, R.k, lab, { ls: R.k.length === 2 ? 0.6 : 0, bold: 0.3 }));
    if (R.date) {
      const segs = [[col, col + 25, '年'], [col + 34, col + 47, '月'], [col + 56, col + 69, '日']];
      for (const [a, b, ch] of segs) {
        g.push(line(a, R.y + 2, b, R.y + 2, 0.9));
        g.push(txt(b + 1.2, R.y, ch, lab, { bold: 0.3 }));
      }
    } else {
      g.push(line(col, R.y + 2, xEnd, R.y + 2, 0.9));
    }
  }
  return `<g id="ink-chalk-duty">${g.join('')}</g>`;
}

// ============ 3. 板腰底边：粉笔槽 + 半截粉笔 + 一块板擦 ============
function chalkTray() {
  const g = [];
  const y = 110;                         // 槽沿（离腰部板边约 16mm）
  const xa = -128, xb = 128;
  g.push(line(xa, y, xb, y, 1.4));
  // 半截粉笔：国产粉笔是微锥形的 —— 左边粗头是平的断面（画出端面椭圆），右边细头被写秃成圆头
  const cx = -102, cl = 44, h0 = 8.6, h1 = 6.6;
  const b = y - 0.7, t0 = b - h0, t1 = b - h1;
  g.push(`<path d="M ${cx} ${f(t0)} L ${cx + cl - 4} ${f(t1)} C ${cx + cl} ${f(t1 - 0.1)} ${cx + cl + 1.6} ${f(t1 + 1.6)} ${cx + cl + 1.6} ${f(t1 + h1 / 2)} ` +
    `C ${cx + cl + 1.6} ${f(b - 1.4)} ${cx + cl} ${f(b)} ${cx + cl - 4} ${f(b)} L ${cx} ${f(b)} ` +
    `A 2.4 ${f(h0 / 2)} 0 0 1 ${cx} ${f(t0)} Z" fill="${CHALK}"/>`);
  // 端面：一道深色细缝勾出圆柱的截面
  g.push(`<path d="M ${cx} ${f(t0 + 0.4)} A 2.2 ${f(h0 / 2 - 0.4)} 0 0 1 ${cx} ${f(b - 0.4)}" fill="none" stroke="${BASE}" stroke-width="0.8"/>`);
  // 板擦（侧视）：把手两头有防滑凹口；底下是一层层叠起来的绒布
  const ex = 34, ew = 76, felt = 6, hand = 12;
  const ft = b - felt, hb = ft - 1.0, ht = hb - hand, hm = ht + hand * 0.52;
  const L = ex + 2, R = ex + ew - 2, rr = 3;
  g.push(`<path d="M ${L} ${f(hb)} L ${L} ${f(hm + 2.6)} Q ${L + 2.6} ${f(hm)} ${L} ${f(hm - 2.6)} L ${L} ${f(ht + rr)} Q ${L} ${f(ht)} ${L + rr} ${f(ht)} ` +
    `L ${R - rr} ${f(ht)} Q ${R} ${f(ht)} ${R} ${f(ht + rr)} L ${R} ${f(hm - 2.6)} Q ${R - 2.6} ${f(hm)} ${R} ${f(hm + 2.6)} L ${R} ${f(hb)} Z" ` +
    `fill="none" stroke="${CHALK}" stroke-width="1.1" stroke-linejoin="round"/>`);
  // 绒布：竖向褶子（线宽 1.0，间距 2.5，留空 1.5）
  const pleats = [];
  for (let x = ex + 0.5; x <= ex + ew - 0.4; x += 2.5) pleats.push(`M ${f(x)} ${f(ft)} V ${f(b)}`);
  g.push(`<path d="${pleats.join(' ')}" stroke="${CHALK}" stroke-width="1"/>`);
  g.push(line(ex, ft + 0.45, ex + ew, ft + 0.45, 0.9));
  return `<g id="ink-chalk-tray">${g.join('')}</g>`;
}

// ============ 4. 板尾：品牌（像黑板框角上的厂牌，安静地压在粉笔槽那条水平线上）============
function brand() {
  const g = [];
  const x = -644, y = 110;                       // 左端与板头值日栏右端（x=644）镜像对齐；基线与粉笔槽同高
  g.push(txt(x, y, 'VAMEI', 11, { font: LAT, weight: 600, ls: 2.6 }));
  g.push(txt(x + 58, y, '154', 11, { font: LAT, weight: 400, ls: 0.4 }));
  return `<g id="ink-chalk-brand">${g.join('')}</g>`;
}

const body = `${eraserSwipes()}
${dutyCorner()}
${chalkTray()}
${brand()}`;

const out = path.join(__dirname, 'a-zhiri.svg');
fs.writeFileSync(out, template(body));
console.log('→', out);
