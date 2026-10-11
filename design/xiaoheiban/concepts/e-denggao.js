// 「等高线」e-denggao —— 板头板尾是两座山的等高线（亮油），中间是留白的雪坡
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, C, ZH, LAT, text, rng } = require('./_kit');

// 一座山：一圈圈变形的同心环，越往外越淡
function mountain(cx, cy, seed, rings, step, fadeFrom) {
  const r = rng(seed), ph = [r() * 6.3, r() * 6.3, r() * 6.3];
  let s = '';
  for (let k = 1; k <= rings; k++) {
    const R0 = k * step, pts = [];
    for (let i = 0; i <= 120; i++) {
      const a = i / 120 * Math.PI * 2;
      const m = 1 + 0.16 * Math.sin(2 * a + ph[0] + k * 0.05) + 0.08 * Math.sin(3 * a + ph[1] + k * 0.11) + 0.05 * Math.sin(5 * a + ph[2] - k * 0.07);
      pts.push(`${f(cx + R0 * m * Math.cos(a) * 1.25)},${f(cy + R0 * m * Math.sin(a))}`);
    }
    const index = k % 5 === 0;
    const fade = k <= fadeFrom ? 1 : Math.max(0, 1 - (k - fadeFrom) / (rings - fadeFrom));
    s += `<polygon points="${pts.join(' ')}" fill="none" stroke="${index ? C.GLOSS2 : '#262626'}" stroke-width="${index ? 1.8 : 1.1}" opacity="${f(fade)}"/>`;
  }
  return s;
}

const gloss = `<g id="gloss-contours">${mountain(610, -36, 7, 26, 13, 12)}${mountain(-600, 44, 23, 24, 13, 11)}</g>`;
// 山顶：一个橙点 + 海拔式标注
const peaks = `<g id="ink-peaks">
  <circle cx="610" cy="-36" r="3.2" fill="${C.ORANGE}"/>
  ${text(618, -40, '▲ 154', 6.5, { fill: C.GREY, ls: 0.6 })}
  <circle cx="-600" cy="44" r="2.4" fill="${C.INK}"/>
  ${text(-592, 40, '26/27', 6.5, { fill: C.GREY, ls: 0.6 })}
</g>`;
const brand = `<g id="ink-brand">
  ${text(0, 104, 'VAMEI', 14, { weight: 600, ls: 4.5, anchor: 'middle' })}
  ${text(0, 116, '小黑板 · 中间这片雪坡，留给你', 6, { font: ZH, fill: C.GREY, anchor: 'middle', ls: 1 })}
</g>`;
fs.writeFileSync(path.join(__dirname, 'e-denggao.svg'), template([gloss, peaks, brand].join('\n')));
console.log('→ e-denggao.svg');
