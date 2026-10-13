// 「碰一碰」j-pengyipeng —— 纯黑板，板头一个粉笔小人高举芯片，旁边一行小字；芯片实际埋在小人手的位置下面
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f } = require('./_kit');
const CH = { white: '#f2efe6', pink: '#f5a3b7', yellow: '#f7da74', blue: '#97d0f0' };
const defs = `<defs><filter id="chalk" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.75" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in" result="tex"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="9" result="w"/>
  <feDisplacementMap in="tex" in2="w" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
</filter></defs>`;
// 小人（板头，x≈620），右手高举芯片
const S = 2.2, ox = 610, oy = 40, P = (x, y) => `${f(ox + x * S)} ${f(oy + y * S)}`;
const man = `<g fill="none" stroke="${CH.blue}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="${f(ox + 0 * S)}" cy="${f(oy - 42 * S)}" r="${12}"/>
  <path d="M ${P(0, -30)} L ${P(0, -6)} M ${P(0, -26)} L ${P(-20, -14)} M ${P(0, -26)} L ${P(16, -46)} M ${P(0, -6)} L ${P(-10, 6)} L ${P(-12, 18)} M ${P(0, -6)} L ${P(10, 6)} L ${P(12, 18)}"/>
</g>
<path d="M ${P(-26, 24)} Q ${P(0, 28)} ${P(26, 22)}" fill="none" stroke="${CH.pink}" stroke-width="2.5" stroke-linecap="round"/>`;
// 芯片：小方块 + 三道感应波
const cx = ox + 22 * S, cy = oy - 54 * S;
const chip = `<g fill="none" stroke="${CH.yellow}" stroke-width="2" stroke-linecap="round">
  <rect x="${f(cx - 9)}" y="${f(cy - 9)}" width="18" height="18" rx="3"/>
  <rect x="${f(cx - 4)}" y="${f(cy - 4)}" width="8" height="8" rx="1"/>
  ${[16, 24, 32].map(r => `<path d="M ${f(cx + r * 0.7)} ${f(cy - r * 0.7)} A ${r} ${r} 0 0 1 ${f(cx + r * 0.7)} ${f(cy + r * 0.7)}"/>`).join('')}
</g>`;
const words = `<text x="${f(ox - 150)}" y="-96" font-family="'Long Cang'" font-size="18" fill="${CH.white}">手机碰一碰，有惊喜</text>
<text x="-690" y="104" font-family="'Long Cang'" font-size="20" fill="${CH.white}">VAMEI 小黑板</text>
<text x="-690" y="122" font-family="'Long Cang'" font-size="13" fill="${CH.white}" opacity="0.8">154 · 26/27</text>`;
fs.writeFileSync(path.join(__dirname, 'j-pengyipeng.svg'), template(`${defs}<g filter="url(#chalk)">${man}${chip}${words}</g>`));
console.log('→ j-pengyipeng.svg');
