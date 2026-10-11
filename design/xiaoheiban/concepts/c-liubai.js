// 「留白点阵」c-liubai —— 亮油点阵（像点阵本），四角裁切线框出画布，一枚朱红「留白」印
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, C, ZH, LAT, text, hw } = require('./_kit');

// 1. 亮油点阵：10mm 间距，点径 1.6mm，只在侧光下看得见
function dots() {
  let s = '';
  for (let x = -760; x <= 760; x += 10) for (let y = -150; y <= 150; y += 10) {
    if (Math.abs(y) > hw(x) - 6) continue;
    s += `<circle cx="${x}" cy="${y}" r="0.8"/>`;
  }
  return `<g id="gloss-dots" fill="${C.GLOSS2}">${s}</g>`;
}

// 2. 裁切线：框出「画布」，像印刷品的角线
function cropMarks() {
  const X = 660, Y = 112, a = 16, g = 5;
  let s = '';
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
    const x = sx * X, y = sy * Y;
    s += `<path d="M ${x - sx * g} ${y} h ${-sx * a} M ${x} ${y - sy * g} v ${-sy * a}" />`;
    s += `<path d="M ${x + sx * g} ${y} h ${sx * 10} M ${x} ${y + sy * g} v ${sy * 10}" />`;
  }
  return `<g id="ink-crop" fill="none" stroke="${C.GREY}" stroke-width="0.9">${s}</g>`;
}

// 3. 朱红印章「留白」：方印，白文（字为底色镂空）
function seal(cx, cy, size) {
  const h = size / 2;
  return `<g id="ink-red-seal">
    <rect x="${cx - h}" y="${cy - h}" width="${size}" height="${size}" rx="2.2" fill="${C.RED}"/>
    <rect x="${cx - h + 2.2}" y="${cy - h + 2.2}" width="${size - 4.4}" height="${size - 4.4}" rx="1.2" fill="none" stroke="${C.BASE}" stroke-width="0.9"/>
    ${text(cx, cy - 1.5, '留', size * 0.4, { font: ZH, anchor: 'middle', fill: C.BASE })}
    ${text(cx, cy + size * 0.36, '白', size * 0.4, { font: ZH, anchor: 'middle', fill: C.BASE })}
  </g>`;
}

// 4. 品牌：板尾小字横排，像落款
function brand() {
  const x = -640, y = 98;
  return `<g id="ink-brand">
    ${text(x, y, 'VAMEI', 15, { weight: 600, ls: 4.2 })}
    ${text(x + 76, y, '小黑板', 8.5, { font: ZH, fill: C.GREY, ls: 1.5 })}
    ${text(x + 76, y - 12, '154 · 26/27', 6.5, { fill: C.GREY, ls: 0.8 })}
  </g>`;
}

const body = [dots(), cropMarks(), brand(), seal(626, -82, 30),
  text(640, 102, '留白处，由你来画', 6.5, { font: ZH, anchor: 'end', fill: C.GREY, ls: 1 })].join('\n');
fs.writeFileSync(path.join(__dirname, 'c-liubai.svg'), template(body));
console.log('→ c-liubai.svg');
