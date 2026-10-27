// 三个更大胆的方向：n1 一线天（透明窗露木芯）、n2 蘸色（板头像蘸过颜料）、n3 剖面（板头像被切开，露出内部层）
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f, hw, rng } = require('./_kit');

// 木纹：沿板长方向拉伸的分形噪声，映射成白杨木的浅棕色
const woodFilter = (id, seed = 7, fy = 0.09) => `<filter id="${id}" x="-800" y="-200" width="1600" height="400" filterUnits="userSpaceOnUse">
  <feTurbulence type="fractalNoise" baseFrequency="0.0025 ${fy}" numOctaves="4" seed="${seed}"/>
  <feColorMatrix type="matrix" values="0.42 0 0 0 0.56  0.34 0 0 0 0.41  0.24 0 0 0 0.25  0 0 0 0 1"/>
</filter>`;
const sign = (x = -700, col = '#4a4a4a') => `<text x="${x}" y="110" font-family="'Inter Display'" font-weight="600" font-size="12" letter-spacing="4" fill="${col}">VAMEI</text>`;

// n1 一线天：中线一条 12mm 宽的透明窗，从板尾到板头，露出木芯
function yixiantian() {
  const x0 = -700, x1 = 700, w = 18;
  const win = `M ${x0} 0 Q ${x0} ${-w / 2} ${x0 + 30} ${-w / 2} L ${x1 - 30} ${-w / 2} Q ${x1} ${-w / 2} ${x1} 0 Q ${x1} ${w / 2} ${x1 - 30} ${w / 2} L ${x0 + 30} ${w / 2} Q ${x0} ${w / 2} ${x0} 0 Z`;
  return `<defs>${woodFilter('wood1')}<clipPath id="win1"><path d="${win}"/></clipPath></defs>
    <g clip-path="url(#win1)"><rect x="-720" y="-20" width="1440" height="40" filter="url(#wood1)"/>
      <rect x="-720" y="-20" width="1440" height="40" fill="url(#glass1)" opacity=".18"/></g>
    <path d="${win}" fill="none" stroke="#000" stroke-width="1.4"/>
    <path d="M ${x0 + 30} ${-w / 2 + 1.2} L ${x1 - 30} ${-w / 2 + 1.2}" stroke="#fff" stroke-opacity=".35" stroke-width=".8"/>
    <defs><linearGradient id="glass1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
    ${sign()}`;
}

// n2 蘸色：板头像倒着蘸进一桶橙色漆，往板中间流下几道漆痕
function zhanse() {
  const C = '#ff5a1f', X = 560, r = rng(3);
  let d = `M 800 -170 L ${X} -170 L ${X} -150`;
  // 沿 y 从上到下画蘸色边缘，夹几道往板中间（-x 方向）流的漆滴
  const drips = [[-112, 70, 7], [-48, 36, 6], [6, 118, 8], [64, 52, 6], [118, 24, 5]];
  let y = -150;
  for (const [dy, len, wd] of drips) {
    d += ` L ${X + (r() - 0.5) * 6} ${dy - wd - 6}`;
    d += ` C ${X} ${dy - wd} ${X - len + 10} ${dy - wd} ${X - len} ${dy} C ${X - len - 6} ${dy + wd + 3} ${X - len + 12} ${dy + wd + 1} ${X} ${dy + wd}`;
    y = dy + wd;
  }
  d += ` L ${X + 3} 170 L 800 170 Z`;
  return `<path d="${d}" fill="${C}"/>
    <path d="M ${X + 12} -160 Q ${X + 22} 0 ${X + 12} 160" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="5" stroke-linecap="round"/>
    ${sign(-700, '#5a5a5a')}`;
}

// n3 剖面：板头附近一道斜切口，切口外按层露出：玻纤、碳纤维、木芯、彩色板底
function poumian() {
  // 切口：一条斜线 x = a + k*y，往板头方向依次排各层
  const k = -0.42, a = 470;
  const band = (from, to) => { // 两条平行斜线之间的带状区域
    const y0 = -175, y1 = 175;
    return `M ${a + from + k * y0} ${y0} L ${a + to + k * y0} ${y0} L ${a + to + k * y1} ${y1} L ${a + from + k * y1} ${y1} Z`;
  };
  const L = [ // [起, 止, 填充, 名称]
    [0, 18, 'url(#glass3)', '玻纤'],
    [18, 30, 'url(#carbon3)', '碳纤维'],
    [30, 104, 'wood', '白杨木芯'],
    [104, 122, 'url(#glass3)', '玻纤'],
    [122, 400, '#ff5a1f', '烧结底'],
  ];
  let s = `<defs>${woodFilter('wood3', 11, 0.06)}
    <pattern id="glass3" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(${Math.atan(-k) * 57.3})">
      <rect width="6" height="6" fill="#d9dcd6"/><path d="M0 3h6M3 0v6" stroke="#b8bcb5" stroke-width="1.2"/></pattern>
    <pattern id="carbon3" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#2a2c2f"/>
      <path d="M0 0h4v4H0zM4 4h4v4H4z" fill="#3a3d41"/></pattern></defs>`;
  for (const [a0, a1, fill, name] of L) {
    if (fill === 'wood') s += `<clipPath id="w3c"><path d="${band(a0, a1)}"/></clipPath><g clip-path="url(#w3c)"><rect x="300" y="-180" width="500" height="360" filter="url(#wood3)"/></g>`;
    else s += `<path d="${band(a0, a1)}" fill="${fill}"/>`;
    s += `<path d="M ${a + a0 + k * -175} -175 L ${a + a0 + k * 175} 175" stroke="#000" stroke-opacity=".45" stroke-width="1"/>`;
  }
  // 各层小字，沿切口方向排在板的下沿附近
  const ang = Math.atan2(1, k) * 57.3; // 文字沿切口方向
  L.slice(0, 4).forEach(([a0, a1, , name], i) => {
    const cx = a + (a0 + a1) / 2 + k * 92, cy = 92;
    s += `<text x="${f(cx)}" y="${cy}" transform="rotate(${f(ang - 180)} ${f(cx)} ${cy})" text-anchor="middle" dominant-baseline="middle" font-family="'WenQuanYi Zen Hei'" font-size="${a1 - a0 > 20 ? 9 : 6.5}" fill="${i === 2 ? '#5b3f1f' : i === 1 ? '#9aa0a6' : '#55595e'}">${name}</text>`;
  });
  // 切口处的面材厚度高光，像真的被切开
  s += `<path d="M ${a + k * -175 - 2} -175 L ${a + k * 175 - 2} 175" stroke="#fff" stroke-opacity=".5" stroke-width="1.2"/>`;
  s += `<text x="680" y="10" text-anchor="middle" font-family="'Inter Display'" font-weight="800" font-size="16" letter-spacing="3" fill="#fff" fill-opacity=".9" transform="rotate(-90 680 10)">VAMEI</text>`;
  return s + sign(-700, '#5a5a5a');
}

const out = n => path.join(__dirname, n);
fs.writeFileSync(out('n1-yixiantian.svg'), template(yixiantian()));
fs.writeFileSync(out('n2-zhanse.svg'), template(zhanse()));
fs.writeFileSync(out('n3-poumian.svg'), template(poumian()));
console.log('ok');
