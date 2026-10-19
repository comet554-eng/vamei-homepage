// 「板挂」l-bangua —— 后脚固定器内侧一块带插孔的软胶底座，插各种小挂件（类似洞洞鞋扣子）；底座里可埋 NFC
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f } = require('./_kit');

function binding(cx, flip) {
  const s = flip ? -1 : 1;
  return `<g transform="translate(${cx} 0)">
    <rect x="-62" y="-128" width="124" height="256" rx="34" fill="#2b2c2e" stroke="#454749" stroke-width="2"/>
    <rect x="-40" y="-104" width="80" height="208" rx="20" fill="#202123"/>
    <path d="M ${-58 * s} -118 Q ${-86 * s} 0 ${-58 * s} 118" fill="none" stroke="#3a3b3e" stroke-width="16" stroke-linecap="round"/>
    <rect x="-70" y="-62" width="140" height="22" rx="8" fill="#38393c"/><rect x="-70" y="40" width="140" height="22" rx="8" fill="#38393c"/>
  </g>`;
}
// 底座：2×4 个插孔
const BX = -150, BY = 0, W = 112, H = 150;
const holes = [];
for (const dx of [-26, 26]) for (const dy of [-54, -18, 18, 54]) holes.push([BX + dx, BY + dy]);
let base = `<rect x="${BX - W / 2}" y="${BY - H / 2}" width="${W}" height="${H}" rx="22" fill="#3d4652"/>
  <rect x="${BX - W / 2 + 4}" y="${BY - H / 2 + 4}" width="${W - 8}" height="${H - 8}" rx="18" fill="none" stroke="#4f5a68" stroke-width="2"/>`;
holes.forEach(([x, y]) => base += `<circle cx="${x}" cy="${y}" r="9" fill="#262c34"/>`);
// 挂件（插在部分孔里）
const charm = {
  flake: (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#97d0f0"/><g stroke="#fff" stroke-width="2.4" stroke-linecap="round">${[0, 60, 120].map(a => { const dx = 9 * Math.cos(a * Math.PI / 180), dy = 9 * Math.sin(a * Math.PI / 180); return `<line x1="${f(x - dx)}" y1="${f(y - dy)}" x2="${f(x + dx)}" y2="${f(y + dy)}"/>`; }).join('')}</g>`,
  peak: (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#f2efe6"/><path d="M ${x - 10} ${y + 7} L ${x - 2} ${y - 7} L ${x + 2} ${y - 1} L ${x + 6} ${y - 6} L ${x + 11} ${y + 7} Z" fill="#3d4652"/><path d="M ${x - 4} ${y - 3.5} L ${x - 2} ${y - 7} L ${x} ${y - 3.5} Z" fill="#fff"/>`,
  man: (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#f7da74"/><circle cx="${x}" cy="${y - 5}" r="4" fill="none" stroke="#3a2f12" stroke-width="2"/><path d="M ${x} ${y - 1} v 7 M ${x - 6} ${y + 2} h 12 M ${x} ${y + 6} l -4 5 M ${x} ${y + 6} l 4 5" stroke="#3a2f12" stroke-width="2" stroke-linecap="round" fill="none"/>`,
  heart: (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#f5a3b7"/><path d="M ${x} ${y + 8} C ${x - 14} ${y - 2} ${x - 6} ${y - 12} ${x} ${y - 4} C ${x + 6} ${y - 12} ${x + 14} ${y - 2} ${x} ${y + 8} Z" fill="#fff"/>`,
  num: (x, y) => `<rect x="${x - 15}" y="${y - 15}" width="30" height="30" rx="8" fill="#b4e09d"/><text x="${x}" y="${y + 5.5}" text-anchor="middle" font-family="'Inter Display'" font-weight="800" font-size="15" fill="#22301a">12</text>`,
  nfc: (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#1f2328" stroke="#f7da74" stroke-width="2"/><g fill="none" stroke="#f7da74" stroke-width="1.8" stroke-linecap="round">${[4, 8, 12].map(r => `<path d="M ${f(x - 4 + r * 0.7)} ${f(y - r * 0.7)} A ${r} ${r} 0 0 1 ${f(x - 4 + r * 0.7)} ${f(y + r * 0.7)}"/>`).join('')}</g>`,
};
const placed = [['flake', 0], ['peak', 2], ['man', 3], ['heart', 5], ['num', 6], ['nfc', 7]];
let charms = placed.map(([k, i]) => charm[k](...holes[i])).join('');
// 旁边散落的挂件，示意可换
const spare = [charm.flake(-20, -100), charm.heart(10, 96), charm.man(40, -96)].join('');
const label = `<text x="-690" y="104" font-family="'Long Cang'" font-size="20" fill="#f2efe6">VAMEI</text>`;
const body = `${binding(-270, false)}${binding(270, true)}${base}${charms}<g opacity=".55">${spare}</g>${label}`;
fs.writeFileSync(path.join(__dirname, 'l-bangua.svg'), template(body).replace(/<g id="inserts"[^]*?<\/g>/, ''));
console.log('→ l-bangua.svg');
