// 「结构组合」m-zuhe —— 纯黑面材 + 彩色 360° 包边 + 同色板头板尾护角 + 板头金属挂孔 + 后脚内侧一体压纹止滑区
// node concepts/m-zuhe.js → 生成三种配色俯视图、侧视图、尺寸标注图（SVG），再由 sheet-m.js 拼成设计稿
const fs = require('fs'), path = require('path');
const { geo } = require('../board.js');
const { f, hw } = require('./_kit');

const HALF = geo.L / 2;                 // 770
const BUMP = 45;                        // 护角从板端往里包 45mm
const HOLE = { x: HALF - 70, r: 5, R: 8.5 };   // 挂孔：距板头端 70mm，孔径 10，护圈外径 17
const GRIP = { x: -135, y: 0, w: 150, h: 112 }; // 止滑压纹区：后脚固定器内侧
const BG = '#e9e7e2';

function topView(c, { inserts = true } = {}) {
  const holes = inserts ? geo.inserts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4.5"/>`).join('') : '';
  // 压纹：同色调的弧形凸棱 + 一行压印字
  let ridges = '';
  for (let i = -6; i <= 6; i++) {
    const y = i * 8;
    ridges += `<path d="M ${GRIP.x - GRIP.w / 2 + 10} ${y} q ${GRIP.w / 4} ${-6} ${GRIP.w / 2 - 10} 0 t ${GRIP.w / 2 - 10} 0" fill="none" stroke="#262626" stroke-width="3.2" stroke-linecap="round"/>
      <path d="M ${GRIP.x - GRIP.w / 2 + 10} ${y - 1.2} q ${GRIP.w / 4} ${-6} ${GRIP.w / 2 - 10} 0 t ${GRIP.w / 2 - 10} 0" fill="none" stroke="#2f2f2f" stroke-width="0.9" stroke-linecap="round"/>`;
  }
  const grip = `<g clip-path="url(#grip-${c.key})">${ridges}</g>
    <rect x="${GRIP.x - GRIP.w / 2}" y="${-GRIP.h / 2}" width="${GRIP.w}" height="${GRIP.h}" rx="18" fill="none" stroke="#242424" stroke-width="1.5"/>`;
  // 挂孔：金属护圈 + 通孔（透出背景）
  const hole = `<circle cx="${HOLE.x}" cy="0" r="${HOLE.R}" fill="url(#metal-${c.key})" stroke="#7d8187" stroke-width="0.8"/>
    <circle cx="${HOLE.x}" cy="0" r="${HOLE.r}" fill="${BG}" stroke="#5c6066" stroke-width="0.8"/>`;
  // 护角：板端 45mm 内用品牌色，内侧一道接缝线
  const bump = s => {
    const x0 = s * (HALF - BUMP);
    return `<rect x="${s > 0 ? x0 : -HALF - 20}" y="-170" width="${BUMP + 20}" height="340" fill="${c.hex}"/>
      <path d="M ${x0} ${-hw(x0) - 2} Q ${x0 + s * 10} 0 ${x0} ${hw(x0) + 2}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="1.2"/>`;
  };
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-800 -175 1600 350" width="1600mm" height="350mm">
  <defs>
    <clipPath id="board-${c.key}"><path d="${geo.path}"/></clipPath>
    <clipPath id="grip-${c.key}"><rect x="${GRIP.x - GRIP.w / 2}" y="${-GRIP.h / 2}" width="${GRIP.w}" height="${GRIP.h}" rx="18"/></clipPath>
    <radialGradient id="metal-${c.key}" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#f4f5f6"/><stop offset=".55" stop-color="#b9bdc2"/><stop offset="1" stop-color="#8a8f95"/></radialGradient>
  </defs>
  <g clip-path="url(#board-${c.key})">
    <rect x="-800" y="-175" width="1600" height="350" fill="#141414"/>
    ${grip}${bump(1)}${bump(-1)}
  </g>
  <g fill="#000" stroke="#444" stroke-width="0.8">${holes}</g>
  <path d="${geo.path}" fill="none" stroke="${c.hex}" stroke-width="4.5"/>
  ${hole}
  <text x="${-HALF + BUMP + 30}" y="112" font-family="'Inter Display'" font-weight="600" font-size="13" letter-spacing="4" fill="#5a5a5a">VAMEI</text>
</svg>`;
}

// 侧视：混合拱示意（纵向放大 3 倍）
function sideView(c) {
  const k = 3, pts = [];
  for (let x = -HALF; x <= HALF; x += 5) {
    const ax = Math.abs(x);
    let y;
    if (ax <= 270) y = -4 * (1 - (x / 270) ** 2);                    // 两脚之间正拱 4mm
    else if (ax <= 567) y = 0.6 * ((ax - 270) / 297) ** 2;            // 脚外到接触点：轻微下沉（示意）
    else { const t = (ax - 567) / (HALF - 567); y = -46 * t ** 1.7; } // 板头板尾上翘 46mm
    pts.push([x, y * k]);
  }
  const top = pts.map(([x, y]) => `${x},${f(y - 12 * k / 3)}`).join(' ');
  const bot = pts.slice().reverse().map(([x, y]) => `${x},${f(y)}`).join(' ');
  const capL = pts.filter(([x]) => x <= -HALF + BUMP), capR = pts.filter(([x]) => x >= HALF - BUMP);
  const cap = arr => `<polyline points="${arr.map(([x, y]) => `${x},${f(y - 6)}`).join(' ')}" fill="none" stroke="${c.hex}" stroke-width="14" stroke-linecap="round"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-800 -175 1600 60" width="1600mm" height="60mm">
    <line x1="-800" y1="0" x2="800" y2="0" stroke="#b8b5ad" stroke-width="1" stroke-dasharray="6 5"/>
    <polygon points="${top} ${bot}" fill="${c.hex}"/>
    <polyline points="${pts.map(([x, y]) => `${x},${f(y - 12 * k / 3)}`).join(' ')}" fill="none" stroke="#141414" stroke-width="3"/>
    <polyline points="${pts.map(([x, y]) => `${x},${f(y)}`).join(' ')}" fill="none" stroke="#141414" stroke-width="3"/>
    ${cap(capL)}${cap(capR)}
  </svg>`.replace('viewBox="-800 -175 1600 60"', 'viewBox="-800 -150 1600 165"');
}

// 尺寸标注图
function techView() {
  const dim = (x1, y1, x2, y2, label, ty, anchor = 'middle') => `
    <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#d1462f" stroke-width="1"/>
    <line x1="${x1}" y1="${y1 - 5}" x2="${x1}" y2="${y1 + 5}" stroke="#d1462f" stroke-width="1"/>
    <line x1="${x2}" y1="${y2 - 5}" x2="${x2}" y2="${y2 + 5}" stroke="#d1462f" stroke-width="1"/>
    <text x="${(x1 + x2) / 2}" y="${ty}" text-anchor="${anchor}" font-family="'WenQuanYi Zen Hei'" font-size="11" fill="#d1462f">${label}</text>`;
  const note = (x, y, tx, ty, lines) => `<path d="M ${x} ${y} L ${tx} ${ty}" stroke="#2b2b2b" stroke-width="0.8" fill="none"/><circle cx="${x}" cy="${y}" r="2" fill="#2b2b2b"/>` +
    lines.map((l, i) => `<text x="${tx + 4}" y="${ty + 4 + i * 14}" font-family="'WenQuanYi Zen Hei'" font-size="11" fill="#2b2b2b">${l}</text>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-800 -230 1600 520" width="1600mm" height="520mm">
    <path d="${geo.path}" fill="#fff" stroke="#2b2b2b" stroke-width="1.6"/>
    <path d="${geo.path}" fill="none" stroke="#2b2b2b" stroke-width="0.6" transform="scale(0.985)" stroke-dasharray="4 3"/>
    <g fill="none" stroke="#9a978f" stroke-width="0.8">${geo.inserts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4.5"/>`).join('')}</g>
    <rect x="${HALF - BUMP}" y="-150" width="${BUMP}" height="300" fill="#ff6a1a" fill-opacity=".25" clip-path="url(#tb)"/>
    <rect x="${-HALF}" y="-150" width="${BUMP}" height="300" fill="#ff6a1a" fill-opacity=".25" clip-path="url(#tb)"/>
    <defs><clipPath id="tb"><path d="${geo.path}"/></clipPath></defs>
    <rect x="${GRIP.x - GRIP.w / 2}" y="${-GRIP.h / 2}" width="${GRIP.w}" height="${GRIP.h}" rx="18" fill="#2b2b2b" fill-opacity=".12" stroke="#2b2b2b" stroke-width="0.8"/>
    <circle cx="${HOLE.x}" cy="0" r="${HOLE.R}" fill="none" stroke="#2b2b2b" stroke-width="1"/><circle cx="${HOLE.x}" cy="0" r="${HOLE.r}" fill="none" stroke="#2b2b2b" stroke-width="1"/>
    ${dim(-HALF, -190, HALF, -190, '总长 1540', -197)}
    ${dim(-567, -168, 567, -168, '有效边 1134（接触点之间，挂孔和护角都在此范围外）', -175)}
    ${dim(HALF - BUMP, 172, HALF, 172, '护角 45', 190)}
    ${dim(HOLE.x, 150, HALF, 150, '70', 145)}
    ${dim(GRIP.x - GRIP.w / 2, 80, GRIP.x + GRIP.w / 2, 80, '止滑区 150', 98)}
    ${note(-HALF + 22, 40, -770, 222, ['板头/板尾护角：品牌色 TPU 软胶', '从板端往里包 45mm', '压板时一同成型或成型后粘接'])}
    ${note(GRIP.x, GRIP.h / 2, -380, 222, ['一体压纹止滑区：150×112mm，圆角 18', '面材压出 0.6–1.0mm 凸棱，同色黑', '位置：后脚固定器内侧'])}
    ${note(200, hw(200), 10, 222, ['360° 彩色包边', '边墙用品牌色 ABS/PU，整圈一色'])}
    ${note(HOLE.x, HOLE.R, 400, 222, ['板头挂孔：孔径 Ø10，护圈外径 Ø17', '不锈钢或黄铜护圈，中心距板头端 70mm', '孔壁环氧封边防进水，需做强度测试'])}
  </svg>`;
}

const COLORS = [
  { key: 'orange', name: '荧光橙', hex: '#ff6a1a' },
  { key: 'blue', name: '冰川蓝', hex: '#5cc8ff' },
  { key: 'yellow', name: '柠檬黄', hex: '#ffd23f' },
];
const out = n => path.join(__dirname, n);
for (const c of COLORS) {
  fs.writeFileSync(out(`m-zuhe-${c.key}.svg`), topView(c));
  fs.writeFileSync(out(`m-zuhe-${c.key}-side.svg`), sideView(c));
}
fs.writeFileSync(out('m-zuhe-tech.svg'), techView());
module.exports = { COLORS };
console.log('ok');
