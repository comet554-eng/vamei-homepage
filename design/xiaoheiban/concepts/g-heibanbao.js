// 「黑板报 · 雪季特刊」g-heibanbao —— 整块板是一期教室后墙的黑板报：彩色粉笔标题、花边、小栏目，留空栏给车主自己写
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, hw, rng } = require('./_kit');

const CH = { white: '#f2efe6', pink: '#f5a3b7', yellow: '#f7da74', blue: '#97d0f0', green: '#b4e09d' };
const KL = "'ZCOOL KuaiLe'", LC = "'Long Cang'", XW = "'ZCOOL XiaoWei'";
const t = (x, y, s, size, fill, font = LC, o = '') =>
  `<text x="${f(x)}" y="${f(y)}" font-family="${font}" font-size="${size}" fill="${fill}" ${o}>${s}</text>`;

// 粉笔质感：细颗粒镂空 + 轻微抖边；黑板上一层擦不干净的粉笔灰
const defs = `<defs>
  <filter id="chalk" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 1.75" result="m"/>
    <feComposite in="SourceGraphic" in2="m" operator="in" result="tex"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="9" result="w"/>
    <feDisplacementMap in="tex" in2="w" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="chalk-soft" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox">
    <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="6" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.55" result="m"/>
    <feComposite in="SourceGraphic" in2="m" operator="in"/>
  </filter>
  <filter id="dust" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.012 0.03" numOctaves="3" seed="21" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.4 -0.62"/>
  </filter>
  <pattern id="hatch-pink" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="3" height="5" fill="${CH.pink}" opacity="0.8"/></pattern>
  <pattern id="hatch-yellow" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)"><rect width="3" height="5" fill="${CH.yellow}" opacity="0.8"/></pattern>
  <pattern id="hatch-blue" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(40)"><rect width="3" height="5" fill="${CH.blue}" opacity="0.8"/></pattern>
  <pattern id="hatch-green" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><rect width="3" height="5" fill="${CH.green}" opacity="0.8"/></pattern>
</defs>`;
const dust = `<rect x="-790" y="-170" width="1580" height="340" filter="url(#dust)" opacity="0.10"/>`;

// 花边：沿上下板边一圈波浪线 + 圆点
function border() {
  let top = [], bot = [], dots = '';
  for (let x = -720; x <= 720; x += 4) {
    const e = hw(x) - 13, w = 2.6 * Math.sin(x / 7);
    top.push(`${x},${f(-e + w)}`); bot.push(`${x},${f(e - w)}`);
  }
  for (let x = -714; x <= 714; x += 28) dots += `<circle cx="${x}" cy="${f(-(hw(x) - 22))}" r="1.6"/><circle cx="${x + 14}" cy="${f(hw(x + 14) - 22)}" r="1.6"/>`;
  return `<polyline points="${top.join(' ')}" fill="none" stroke="${CH.pink}" stroke-width="1.6"/>
    <polyline points="${bot.join(' ')}" fill="none" stroke="${CH.blue}" stroke-width="1.6"/>
    <g fill="${CH.yellow}">${dots}</g>`;
}

// 大标题：空心字 + 斜线涂色，一个字一个颜色
function title() {
  const chars = [['雪', 'pink'], ['季', 'yellow'], ['特', 'blue'], ['刊', 'green']];
  let s = '';
  chars.forEach(([c, k], i) => {
    const x = -120 + i * 80, y = 30 + (i % 2 ? -6 : 4), rot = [-6, 4, -3, 6][i];
    const o = `text-anchor="middle" transform="rotate(${rot} ${x} ${y})"`;
    s += t(x, y, c, 86, `url(#hatch-${k})`, KL, o + ` stroke="${CH[k]}" stroke-width="3.2" stroke-linejoin="round"`);
  });
  return s;
}

// 简笔画：雪花、小太阳、雪山、滑雪小人
const flake = (x, y, r, c) => [0, 60, 120].map(a => {
  const dx = r * Math.cos(a * Math.PI / 180), dy = r * Math.sin(a * Math.PI / 180);
  return `<line x1="${f(x - dx)}" y1="${f(y - dy)}" x2="${f(x + dx)}" y2="${f(y + dy)}"/>`;
}).join('') + `<circle cx="${x}" cy="${y}" r="${f(r * 0.18)}" fill="${c}"/>`;
function flakes() {
  const r = rng(3); let s = '';
  [[-470, -100], [-130, -105], [150, 106], [470, 98], [-320, 104], [300, -104], [690, -40], [-690, 60]].forEach(([x, y], i) => {
    const c = [CH.white, CH.blue, CH.white, CH.yellow][i % 4];
    s += `<g stroke="${c}" stroke-width="1.6" stroke-linecap="round">${flake(x, y, 7 + r() * 5, c)}</g>`;
  });
  return s;
}
function mountain() { // 板尾端：雪山 + 太阳
  return `<g stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M -748 40 L -700 -38 L -676 -6 L -652 -48 L -600 40" stroke="${CH.white}" stroke-width="2"/>
    <path d="M -712 -18 L -700 -38 L -688 -20 M -662 -30 L -652 -48 L -640 -28" stroke="${CH.white}" stroke-width="1.6"/>
    <circle cx="-610" cy="-70" r="13" stroke="${CH.yellow}" stroke-width="2"/>
    ${[...Array(8)].map((_, i) => { const a = i * Math.PI / 4; return `<line x1="${f(-610 + 18 * Math.cos(a))}" y1="${f(-70 + 18 * Math.sin(a))}" x2="${f(-610 + 25 * Math.cos(a))}" y2="${f(-70 + 25 * Math.sin(a))}" stroke="${CH.yellow}" stroke-width="1.8"/>`; }).join('')}
  </g>`;
}
function rider(x, y, s, c) { // 板头端：滑雪小人
  return `<g transform="translate(${x} ${y}) scale(${s})" fill="none" stroke="${c}" stroke-width="${f(2 / s)}" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="2" cy="-30" r="5"/><path d="M 1 -24 L -2 -8 M -2 -8 L -10 0 L -8 8 M -2 -8 L 6 -1 L 9 8 M 0 -19 L -12 -14 M 0 -19 L 12 -22"/>
    <path d="M -20 10 Q -6 14 20 7" stroke="${CH.pink}"/>
  </g>`;
}

// 栏目
function column(x, y, head, color, lines, w) {
  let s = t(x, y, head, 21, color, KL);
  s += `<path d="M ${x} ${y + 5} q ${w / 2} 4 ${w} 0" fill="none" stroke="${color}" stroke-width="1.4"/>`;
  lines.forEach((l, i) => { s += t(x, y + 28 + i * 22, l, 16.5, CH.white); });
  return s;
}
const tips = column(-570, -54, '滑雪小知识', CH.yellow,
  ['① 一害怕就往前压', '② 膝盖弯一点', '③ 眼睛看出口'], 110);
const honor = column(450, -66, '光荣榜', CH.pink,
  ['摔跤：', '同桌签名：', '下期预告：第一次刻滑'], 72);
const lines = `<g stroke="${CH.white}" stroke-width="1" stroke-dasharray="3 2.4" opacity="0.8">
  <line x1="504" y1="-32" x2="630" y2="-32"/><line x1="540" y1="-10" x2="650" y2="-10"/></g>`;

const masthead = `${t(0, -78, 'VAMEI 小黑板 · 第 26/27 期', 17, CH.white, XW, 'text-anchor="middle" letter-spacing="1.5"')}
  ${t(-104, 86, '主编：', 16, CH.white)}<line x1="-58" y1="88" x2="12" y2="88" stroke="${CH.white}" stroke-width="1" stroke-dasharray="3 2.4"/>
  ${t(24, 86, '日期：', 16, CH.white)}<line x1="68" y1="88" x2="116" y2="88" stroke="${CH.white}" stroke-width="1" stroke-dasharray="3 2.4"/>`;

const body = `${defs}${dust}
<g filter="url(#chalk)">${border()}${title()}${flakes()}${mountain()}${rider(690, 60, 1.6, CH.blue)}</g>
<g filter="url(#chalk-soft)">${masthead}${tips}${honor}${lines}</g>`;
fs.writeFileSync(path.join(__dirname, 'g-heibanbao.svg'), template(body));
console.log('→ g-heibanbao.svg');
