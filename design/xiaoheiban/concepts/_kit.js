// 板面概念稿共用的小工具：取色、文字、板面半宽
const { geo } = require('../board.js');
const f = n => +n.toFixed(2);
const C = {
  BASE: '#141414',      // 哑光黑底
  GLOSS: '#232323',     // 局部亮油（同色调），示意色
  GLOSS2: '#2c2c2c',    // 亮油加重（计曲线等）
  INK: '#e4e0d6',       // 专色 1：暖白
  GREY: '#8d8a84',      // 专色 1 的网点灰（或第二专色）
  RED: '#c63b2c',       // 专色 2：朱红
  ORANGE: '#e2642a',
};
const ZH = "'WenQuanYi Zen Hei'", LAT = "'Inter Display'";
function text(x, y, s, size, o = {}) {
  return `<text x="${f(x)}" y="${f(y)}" font-family="${o.font || LAT}" font-size="${size}"` +
    (o.weight ? ` font-weight="${o.weight}"` : '') + (o.anchor ? ` text-anchor="${o.anchor}"` : '') +
    (o.ls != null ? ` letter-spacing="${o.ls}"` : '') + (o.rot ? ` transform="rotate(${o.rot} ${f(x)} ${f(y)})"` : '') +
    ` fill="${o.fill || C.INK}">${s}</text>`;
}
// 板面在 x 处的半宽（近似，用于排版避让）
function hw(x) {
  const ax = Math.abs(x), half = geo.L / 2;
  if (ax <= 567) return geo.WAIST / 2 + (geo.R - Math.sqrt(geo.R * geo.R - ax * ax));
  if (ax <= geo.xw) return 146.5 + (ax - 567) / (geo.xw - 567) * 1.5;
  const t = (ax - geo.xw) / (half - geo.xw);           // 板头圆弧：粗略插值
  return 148 * Math.sqrt(Math.max(0, 1 - Math.pow(t, 2.6)));
}
function rng(seed) { return () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }; }
module.exports = { f, C, ZH, LAT, text, hw, rng };
