// VAMEI 小黑板 154 板面轮廓（单位 mm，原点在板中心，x 沿板长，y 沿板宽）
// 依据 VAMEI 5.0-154 板型图：总长 1540，有效边 1134，腰宽 252，最宽 296（距板端 178），侧切 R7842.1
// 用法：node board.js            → 生成 template.svg（空白板面模板）
const fs = require('fs');
const path = require('path');

const L = 1540, EE = 1134, WAIST = 252, WMAX = 296, R = 7842.1, TIPW = 178;
const half = L / 2, ce = EE / 2;                       // ce：接触点到中心的距离
const sag = R - Math.sqrt(R * R - ce * ce);           // 侧切弧矢高
const wc = WAIST / 2 + sag;                            // 接触点半宽
const xw = half - TIPW;                                // 最宽点到中心的距离
const f = n => +n.toFixed(2);

// 轮廓：两段侧切直线 + 侧切圆弧 + 圆润板头（按 VAMEI 图纸取点：距板端 10mm 处半宽约 64，28mm 处约 107，178mm 处最宽 148）
function outlinePath() {
  const H = WMAX / 2;
  // 头端（s=1）上半边：从最宽点画到板端中心；y 取负为上半边
  const nose = (s, k) => [
    `C ${f(s * (xw + 70))} ${k * H} ${f(s * (half - 45))} ${k * 140} ${f(s * (half - 28))} ${k * 107}`,
    `C ${f(s * (half - 12))} ${k * 76} ${f(s * half)} ${k * 40} ${f(s * half)} 0`,
  ];
  // 尾端（反向）：从板端中心画回最宽点
  const tailIn = (s, k) => [
    `C ${f(s * half)} ${k * 40} ${f(s * (half - 12))} ${k * 76} ${f(s * (half - 28))} ${k * 107}`,
    `C ${f(s * (half - 45))} ${k * 140} ${f(s * (xw + 70))} ${k * H} ${f(s * xw)} ${k * H}`,
  ];
  return [
    `M ${-half} 0`, ...tailIn(-1, -1),
    `L ${f(-ce)} ${f(-wc)}`, `A ${R} ${R} 0 0 0 ${f(ce)} ${f(-wc)}`, `L ${f(xw)} ${-H}`,
    ...nose(1, -1),
    ...tailIn(1, 1),
    `L ${f(ce)} ${f(wc)}`, `A ${R} ${R} 0 0 0 ${f(-ce)} ${f(wc)}`, `L ${f(-xw)} ${H}`,
    ...nose(-1, 1), 'Z',
  ].join(' ');
}

// 固定器孔位：每只脚 2 排 × 6 孔，孔距 20，排距 40，内侧孔距中心 220（参考站距 540）
function inserts() {
  const pts = [];
  for (const s of [-1, 1]) for (let i = 0; i < 6; i++) for (const y of [-20, 20]) pts.push([s * (220 + 20 * i), y]);
  return pts;
}

const geo = { L, EE, WAIST, WMAX, R, TIPW, sag: f(sag), wc: f(wc), xw, path: outlinePath(), inserts: inserts(),
  stanceCenters: [-270, 270], contact: [-ce, ce] };

function template(body = '') {
  const holes = geo.inserts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4.5"/>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-790 -170 1580 340" width="1580mm" height="340mm">
  <defs><clipPath id="board"><path d="${geo.path}"/></clipPath></defs>
  <!-- 设计区：所有图案画在这个 g 里，会被板面轮廓裁切 -->
  <g clip-path="url(#board)">
    <rect x="-790" y="-170" width="1580" height="340" fill="#141414"/>
    ${body}
  </g>
  <!-- 固定器孔位（仅示意，生产文件里删除） -->
  <g id="inserts" fill="#000" stroke="#555" stroke-width="0.8">${holes}</g>
  <!-- 板面轮廓线 / 边墙示意 -->
  <path d="${geo.path}" fill="none" stroke="#3a3a3a" stroke-width="2"/>
</svg>`;
}

module.exports = { geo, template };
if (require.main === module) {
  fs.writeFileSync(path.join(__dirname, 'geometry.json'), JSON.stringify(geo, null, 2));
  fs.writeFileSync(path.join(__dirname, 'template.svg'), template());
  console.log('sag', geo.sag, 'contact half-width', geo.wc);
}
