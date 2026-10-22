// 「粉笔抽象画」系列 i-chouxiang —— 整块纯黑留白，只在板头/板尾用粉笔随手画一个小场景
// node concepts/i-chouxiang.js → 生成 i1…i6 六个 SVG
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, rng } = require('./_kit');

const CH = { white: '#f2efe6', pink: '#f5a3b7', yellow: '#f7da74', blue: '#97d0f0', green: '#b4e09d' };
const defs = `<defs><filter id="chalk" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.75" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in" result="tex"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="9" result="w"/>
  <feDisplacementMap in="tex" in2="w" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
</filter></defs>`;
const W = 2.1; // 粉笔线宽 mm

// 火柴人：j = { head:[x,y], neck, hip, hl, hr(手), kl, kr(膝), fl, fr(脚) }，单位 mm，原点为图形中心
function stick(j, c, board = true, bc = CH.pink) {
  const L = (a, b) => `M ${f(a[0])} ${f(a[1])} L ${f(b[0])} ${f(b[1])}`;
  let d = [L(j.neck, j.hip), L(j.neck, j.hl), L(j.neck, j.hr), L(j.hip, j.kl), L(j.kl, j.fl), L(j.hip, j.kr), L(j.kr, j.fr)].join(' ');
  let s = `<circle cx="${f(j.head[0])}" cy="${f(j.head[1])}" r="12" fill="none" stroke="${c}" stroke-width="${W}"/>`;
  s += `<path d="${d}" fill="none" stroke="${c}" stroke-width="${W}" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (board) { // 脚下的板：沿两脚连线延长，带一点弧
    const [a, b] = [j.fl, j.fr], dx = b[0] - a[0], dy = b[1] - a[1], k = 0.75;
    const p0 = [a[0] - dx * k, a[1] - dy * k + 6], p1 = [b[0] + dx * k, b[1] + dy * k + 6], m = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 6];
    s += `<path d="M ${f(p0[0])} ${f(p0[1])} Q ${f(m[0])} ${f(m[1])} ${f(p1[0])} ${f(p1[1])}" fill="none" stroke="${bc}" stroke-width="${W + 0.4}" stroke-linecap="round"/>`;
  }
  return s;
}
const g = (x, y, s, inner, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">${inner}</g>`;
const flake = (x, y, r = 9, c = CH.white) => `<g stroke="${c}" stroke-width="1.6" stroke-linecap="round">${[0, 60, 120].map(a => { const dx = r * Math.cos(a * Math.PI / 180), dy = r * Math.sin(a * Math.PI / 180); return `<line x1="${f(x - dx)}" y1="${f(y - dy)}" x2="${f(x + dx)}" y2="${f(y + dy)}"/>`; }).join('')}</g>`;
const dots = (pts, c = CH.yellow) => `<g fill="${c}">${pts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.8"/>`).join('')}</g>`;
const wave = (d, c = CH.blue) => `<path d="${d}" fill="none" stroke="${c}" stroke-width="1.9" stroke-linecap="round"/>`;
const sign = (x = -690) => `<text x="${x}" y="104" font-family="'Long Cang'" font-size="20" fill="${CH.white}">VAMEI 小黑板</text>
<text x="${x}" y="122" font-family="'Long Cang'" font-size="13" fill="${CH.white}" opacity="0.8">154 · 26/27</text>`;
const note = (x, y, s, c = CH.white, size = 15) => `<text x="${x}" y="${y}" font-family="'Long Cang'" font-size="${size}" fill="${c}">${s}</text>`;

// 姿势库
const P = {
  ride:  { head: [2, -42], neck: [1, -30], hip: [-2, -6], hl: [-24, -20], hr: [26, -28], kl: [-14, 4], kr: [10, 4], fl: [-16, 18], fr: [18, 16] },
  carve: { head: [16, -38], neck: [10, -27], hip: [-4, -6], hl: [-12, 6], hr: [34, -22], kl: [-16, 2], kr: [10, 6], fl: [-18, 18], fr: [20, 14] },
  jump:  { head: [0, -44], neck: [0, -32], hip: [0, -10], hl: [-26, -46], hr: [26, -46], kl: [-14, -2], kr: [14, -2], fl: [-16, 8], fr: [16, 8] },
  fall:  { head: [-14, -34], neck: [-10, -22], hip: [0, 2], hl: [-22, 4], hr: [14, -38], kl: [16, -10], kr: [20, -8], fl: [32, 2], fr: [38, 4] },
  wave:  { head: [0, -42], neck: [0, -30], hip: [0, -6], hl: [-22, -12], hr: [20, -54], kl: [-10, 6], kr: [10, 6], fl: [-14, 18], fr: [14, 18] },
};

const designs = {
  // 1 慢慢滑：一个小人 + 雪坡
  'i1-huaxing': [g(640, 20, 2.3, stick(P.ride, CH.blue)), wave('M 520 100 C 580 96 620 104 660 88 S 710 72 735 62'), flake(590, -72), dots([[560, 80], [700, 34], [690, -100]])],
  // 2 刻滑：身体压下去，身后一道长长的弧线
  'i2-kehua': [g(620, 10, 2.3, stick(P.carve, CH.yellow), -12), wave('M 380 -40 C 450 60 520 90 600 60', CH.white), dots([[430, 10], [470, 40], [520, 70]], CH.white), flake(700, -90, 8, CH.blue)],
  // 3 跳台：腾空，下面三道速度线和地面
  'i3-tiaotai': [g(630, -10, 2.2, stick(P.jump, CH.pink, true, CH.yellow)), wave('M 560 110 L 610 70 L 720 70', CH.white),
    `<g stroke="${CH.white}" stroke-width="1.6" stroke-linecap="round"><line x1="560" y1="-40" x2="590" y2="-30"/><line x1="556" y1="-10" x2="590" y2="-6"/><line x1="560" y1="20" x2="592" y2="16"/></g>`, dots([[700, -100], [560, -90]])],
  // 4 摔了：屁股墩，头上冒星星，旁边写一句
  'i4-shuaile': [g(620, 50, 2.1, stick(P.fall, CH.green, true, CH.yellow)), 
    `<g fill="none" stroke="${CH.yellow}" stroke-width="1.6"><path d="M 562 -52 l 4 -10 l 4 10 l -10 -6 h 12 z"/><path d="M 612 -64 l 3 -8 l 3 8 l -8 -5 h 10 z"/></g>`,
    note(540, -86, '没事，再来！', CH.white, 20), wave('M 520 104 C 600 96 680 104 740 90')],
  // 5 两个人：一个滑在前面，一个在后面挥手，中间一道连线的雪
  'i5-jieban': [g(660, 10, 2.0, stick(P.ride, CH.blue)), g(-640, 10, 2.0, stick(P.wave, CH.pink, true, CH.blue)),
    wave('M -560 70 C -300 120 300 30 560 80', CH.white), note(-600, -90, '等等我！', CH.white, 17), dots([[-500, -60], [500, -70]])],
  // 6 雪人和小人：小人在板头滑，板尾一个粉笔雪人看着
  'i6-xueren': [g(650, 15, 2.1, stick(P.ride, CH.blue)),
    `<g fill="none" stroke="${CH.white}" stroke-width="${W}"><circle cx="-640" cy="40" r="26"/><circle cx="-640" cy="-6" r="17"/></g>
     <g fill="${CH.white}"><circle cx="-646" cy="-9" r="1.8"/><circle cx="-634" cy="-9" r="1.8"/></g>
     <path d="M -640 -4 l 10 3" stroke="${CH.yellow}" stroke-width="2" stroke-linecap="round"/>
     <path d="M -662 30 l -24 -16 M -618 30 l 24 -18" stroke="${CH.green}" stroke-width="1.8" stroke-linecap="round"/>
     <path d="M -652 -22 h 24 l -4 -16 h -16 z" fill="none" stroke="${CH.pink}" stroke-width="1.8"/>`,
    wave('M 540 100 C 600 92 650 104 735 70'), flake(-560, -80), flake(580, -90, 7, CH.blue)],
};

for (const [k, parts] of Object.entries(designs)) {
  const tailFree = !['i5-jieban', 'i6-xueren'].includes(k);
  const body = `${defs}<g filter="url(#chalk)">${parts.join('')}${sign(tailFree ? -690 : -170)}</g>`;
  fs.writeFileSync(path.join(__dirname, k + '.svg'), template(body));
  console.log('→', k + '.svg');
}
