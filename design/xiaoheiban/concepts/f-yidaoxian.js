// 「第一道线」f-yidaoxian —— 整块板只有一道刻滑轨迹，从板尾划到板头，其余全黑
// 线宽跟着「压刃」走：弯顶压得最重最宽，换刃处最细
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, C, ZH, LAT, text, rng } = require('./_kit');

// 四段三次贝塞尔：三个大小不一的弯
const P = [[-800, 96], [-640, 100], [-560, -70], [-400, -84]];
const segs = [P];
const next = (prev, c2, p) => { const [, , b, e] = prev; return [e, [2 * e[0] - b[0], 2 * e[1] - b[1]], c2, p]; };
segs.push(next(segs[0], [-170, 58], [-20, 58]));
segs.push(next(segs[1], [250, -60], [400, -62]));
segs.push(next(segs[2], [650, 64], [810, 22]));
const bz = (s, t) => [0, 1].map(i => (1 - t) ** 3 * s[0][i] + 3 * (1 - t) ** 2 * t * s[1][i] + 3 * (1 - t) * t * t * s[2][i] + t ** 3 * s[3][i]);
const pts = [];
segs.forEach(s => { for (let i = 0; i < 80; i++) pts.push(bz(s, i / 80)); });
pts.push(segs[3][3]);

// 变宽笔触：按局部斜率算压刃轻重
function ribbon(scale, seed, dy = 0) {
  const r = rng(seed), L = [], R = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    const dx = b[0] - a[0], dyy = b[1] - a[1], len = Math.hypot(dx, dyy);
    const slope = Math.abs(dyy / dx);
    const w = scale * (1.4 + 9.5 * Math.pow(1 - Math.min(1, slope / 1.0), 2.2)) * (0.92 + r() * 0.16);
    const nx = -dyy / len, ny = dx / len, [x, y] = pts[i];
    L.push(`${f(x + nx * w / 2)},${f(y + dy + ny * w / 2)}`);
    R.unshift(`${f(x - nx * w / 2)},${f(y + dy - ny * w / 2)}`);
  }
  return `M ${L.join(' L ')} L ${R.join(' L ')} Z`;
}
const r = rng(5);
let ink = `<path d="${ribbon(1, 1)}" fill="${C.INK}"/>`;
// 弯顶外侧扬起的雪沫：扇形散开，越远越小
function spray(i, dir) {
  const [cx, cy] = pts[i]; let s = '';
  for (let k = 0; k < 34; k++) {
    const d = 6 + Math.pow(r(), 1.4) * 40, a = (r() - 0.5) * 1.9;
    s += `<circle cx="${f(cx + Math.sin(a) * d * 1.9 + 8)}" cy="${f(cy + dir * (6 + Math.cos(a) * d * 0.6))}" r="${f(Math.max(0.5, 2.2 - d / 22) * (0.6 + r() * 0.6))}"/>`;
  }
  return s;
}
const apexes = []; for (let i = 20; i < pts.length - 20; i++) { const y = pts[i][1]; if (Math.abs(y) > 40 && Math.abs(y) >= Math.abs(pts[i - 1][1]) && Math.abs(y) > Math.abs(pts[i + 1][1])) apexes.push(i); }
ink += `<g fill="${C.INK}" opacity="0.85">${apexes.map(i => spray(i + 3, Math.sign(pts[i][1]))).join('')}</g>`;

const words = `<g id="ink-words">
  ${text(-690, -98, 'VAMEI', 14, { weight: 600, ls: 4.5 })}
  ${text(-690, -86, '小黑板 154 · 26/27', 6.5, { font: ZH, fill: C.GREY, ls: 1 })}
  ${text(680, 104, '第一道线，你来画', 7, { font: ZH, fill: C.GREY, anchor: 'end', ls: 1.4 })}
</g>`;
fs.writeFileSync(path.join(__dirname, 'f-yidaoxian.svg'), template(`<g id="ink-line">${ink}</g>\n${words}`));
console.log('→ f-yidaoxian.svg');
