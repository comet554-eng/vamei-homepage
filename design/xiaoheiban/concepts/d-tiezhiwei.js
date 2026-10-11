// 「贴纸位 / 雪场护照」d-tiezhiwei —— 板面是一本贴纸册：虚线贴纸位编号 01–12，攒雪场限定贴
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, C, ZH, LAT, text } = require('./_kit');

const ST = `fill="none" stroke="${C.GREY}" stroke-width="1" stroke-dasharray="4 3"`;
const num = (x, y, n, a = 'start') => text(x, y, String(n).padStart(2, '0'), 6.5, { fill: C.GREY, anchor: a, weight: 500, ls: 0.6 });
const circle = (x, y, r, n) => `<circle cx="${x}" cy="${y}" r="${r}" ${ST}/>` + num(x + r * 0.72, y - r * 0.72 - 2, n);
const rrect = (x, y, w, h, rx, n) => `<rect x="${x - w / 2}" y="${y - h / 2}" width="${w}" height="${h}" rx="${rx}" ${ST}/>` + num(x - w / 2 + 3, y - h / 2 - 3, n);
function hex(x, y, r, n) {
  const p = [...Array(6)].map((_, i) => { const a = Math.PI / 6 + i * Math.PI / 3; return `${f(x + r * Math.cos(a))},${f(y + r * Math.sin(a))}`; });
  return `<polygon points="${p.join(' ')}" ${ST}/>` + num(x + r * 0.55, y - r - 2, n);
}
// 贴纸位下方的小字栏：雪场 / 日期
const field = (x, y, w) => text(x, y, '雪场', 5.5, { font: ZH, fill: C.GREY }) +
  `<line x1="${x + 13}" y1="${y + 1}" x2="${x + w}" y2="${y + 1}" stroke="${C.GREY}" stroke-width="0.7"/>`;

const slots = [
  // 板尾：大圆 + 方 + 小圆 + 六角
  circle(-650, -40, 44, 1), field(-690, 22, 80),
  rrect(-566, 34, 56, 56, 8, 2),
  circle(-520, -78, 24, 3),
  hex(-470, -12, 34, 4),
  // 中段：长条 + 两个小圆（两脚之间，不被固定器挡住）
  rrect(0, -78, 210, 36, 18, 5),
  circle(-70, 18, 30, 6), circle(10, 30, 22, 7), rrect(80, 16, 58, 58, 6, 8),
  // 板头
  hex(470, 20, 34, 9),
  rrect(560, -60, 62, 62, 31, 10),
  circle(650, 30, 44, 11), field(612, 94, 80),
  circle(530, 88, 20, 12),
].join('\n');

const header = `<g id="ink-header">
  ${text(-650, 106, 'VAMEI', 13, { weight: 600, ls: 3.5 })}
  ${text(-585, 106, '小黑板 · 雪场护照', 7, { font: ZH, fill: C.GREY, ls: 1 })}
  ${text(-650, 118, '154 · 26/27 · 12 个贴纸位，一季一季攒满它', 5.5, { font: ZH, fill: C.GREY, ls: 0.6 })}
</g>`;

fs.writeFileSync(path.join(__dirname, 'd-tiezhiwei.svg'), template(`<g id="ink-slots">${slots}</g>\n${header}`));
console.log('→ d-tiezhiwei.svg');
