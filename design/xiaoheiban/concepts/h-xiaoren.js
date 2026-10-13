// 「粉笔小人」h-xiaoren —— 整块纯黑留白，只在板头用粉笔画一个滑雪小人，板尾一行粉笔落款
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f } = require('./_kit');

const CH = { white: '#f2efe6', pink: '#f5a3b7', yellow: '#f7da74', blue: '#97d0f0' };
const defs = `<defs>
  <filter id="chalk" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.75" result="m"/>
    <feComposite in="SourceGraphic" in2="m" operator="in" result="tex"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="9" result="w"/>
    <feDisplacementMap in="tex" in2="w" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</defs>`;

// 滑雪小人（板头）
const rider = `<g transform="translate(640 6) scale(2.6)" fill="none" stroke="${CH.blue}" stroke-width="0.8" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="2" cy="-30" r="5"/><path d="M 1 -24 L -2 -8 M -2 -8 L -10 0 L -8 8 M -2 -8 L 6 -1 L 9 8 M 0 -19 L -12 -14 M 0 -19 L 12 -22"/>
  <path d="M -20 10 Q -6 14 20 7" stroke="${CH.pink}"/>
</g>`;
// 小人身后一道雪坡线 + 一片雪花 + 几粒雪
const scene = `<path d="M 520 96 C 560 92 600 104 640 86 S 700 70 730 58" fill="none" stroke="${CH.blue}" stroke-width="1.8" stroke-linecap="round"/>
<g stroke="${CH.white}" stroke-width="1.6" stroke-linecap="round">${[0, 60, 120].map(a => { const r = 9, dx = r * Math.cos(a * Math.PI / 180), dy = r * Math.sin(a * Math.PI / 180); return `<line x1="${f(600 - dx)}" y1="${f(-70 - dy)}" x2="${f(600 + dx)}" y2="${f(-70 + dy)}"/>`; }).join('')}</g>
<g fill="${CH.yellow}">${[[560, 78], [610, 70], [700, 30], [690, -100]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.7"/>`).join('')}</g>`;
// 板尾粉笔落款
const sign = `<text x="-690" y="104" font-family="'Long Cang'" font-size="20" fill="${CH.white}">VAMEI 小黑板</text>
<text x="-690" y="122" font-family="'Long Cang'" font-size="13" fill="${CH.white}" opacity="0.8">154 · 26/27</text>`;

fs.writeFileSync(path.join(__dirname, 'h-xiaoren.svg'), template(`${defs}<g filter="url(#chalk)">${rider}${scene}${sign}</g>`));
console.log('→ h-xiaoren.svg');
