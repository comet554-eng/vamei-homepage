// 「板擦止滑垫」k-banca —— 后脚固定器内侧贴一块「黑板擦」形状的止滑垫，前脚旁贴两根「粉笔头」
// 板擦里可以埋 NFC：芯片在上表面，一碰就读，不用进热压
const fs = require('fs'), path = require('path');
const { template } = require('../board.js');
const { f } = require('./_kit');

// 固定器示意（俯视）：底盘 + 高背
function binding(cx, flip) {
  const s = flip ? -1 : 1;
  return `<g transform="translate(${cx} 0)">
    <rect x="-62" y="-128" width="124" height="256" rx="34" fill="#2b2c2e" stroke="#454749" stroke-width="2"/>
    <rect x="-40" y="-104" width="80" height="208" rx="20" fill="#202123"/>
    <path d="M ${-58 * s} -118 Q ${-86 * s} 0 ${-58 * s} 118" fill="none" stroke="#3a3b3e" stroke-width="16" stroke-linecap="round"/>
    <rect x="-70" y="-62" width="140" height="22" rx="8" fill="#38393c"/>
    <rect x="-70" y="40" width="140" height="22" rx="8" fill="#38393c"/>
    <circle cx="0" cy="0" r="30" fill="none" stroke="#4a4c4f" stroke-width="2"/>
  </g>`;
}

// 板擦：木色背 + 灰色毛毡边 + 凸起防滑条 + VAMEI 烫印 + NFC 位置
function eraser(cx, cy) {
  const W = 130, H = 62;
  let ribs = '';
  for (let i = -5; i <= 5; i++) ribs += `<rect x="${cx + i * 9 - 2.2}" y="${cy - 18}" width="4.4" height="36" rx="2.2" fill="#c9a77c"/>`;
  return `<g>
    <rect x="${cx - W / 2 - 4}" y="${cy - H / 2 - 4}" width="${W + 8}" height="${H + 8}" rx="12" fill="#8e8b86"/>
    <rect x="${cx - W / 2}" y="${cy - H / 2}" width="${W}" height="${H}" rx="10" fill="#b9946a"/>
    ${ribs}
    <rect x="${cx - 26}" y="${cy - 9}" width="52" height="18" rx="4" fill="#b9946a"/>
    <text x="${cx}" y="${cy + 4.5}" text-anchor="middle" font-family="'Inter Display'" font-weight="700" font-size="11" letter-spacing="2.5" fill="#6f4f2c">VAMEI</text>
    <g fill="none" stroke="#6f4f2c" stroke-width="1.4" stroke-linecap="round">
      ${[5, 9, 13].map(r => `<path d="M ${f(cx + 46 + r * 0.7)} ${f(cy - r * 0.7)} A ${r} ${r} 0 0 1 ${f(cx + 46 + r * 0.7)} ${f(cy + r * 0.7)}"/>`).join('')}
    </g>
  </g>`;
}
// 粉笔头：圆头长条，带一点粉笔灰
function chalk(x, y, len, rot, col) {
  return `<g transform="translate(${x} ${y}) rotate(${rot})">
    <rect x="${-len / 2}" y="-8" width="${len}" height="16" rx="8" fill="${col}"/>
    <rect x="${-len / 2 + 6}" y="-3" width="${len - 20}" height="3" rx="1.5" fill="#fff" opacity=".35"/>
    <ellipse cx="${len / 2 - 4}" cy="0" rx="4" ry="7.5" fill="#fff" opacity=".45"/>
  </g>`;
}
const body = `${binding(-270, false)}${binding(270, true)}
  ${eraser(-140, 0)}
  ${chalk(150, -78, 64, -8, '#f5a3b7')}${chalk(150, -48, 56, 4, '#f7da74')}
  <text x="-690" y="104" font-family="'Long Cang'" font-size="20" fill="#f2efe6">VAMEI 小黑板</text>`;
fs.writeFileSync(path.join(__dirname, 'k-banca.svg'), template(body).replace(/<g id="inserts"[^]*?<\/g>/, ''));
console.log('→ k-banca.svg');
