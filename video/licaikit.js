/* 李财系列 · 横版 1920×1080 手绘纸张风格工具库
 * 依赖：snowkit.js（audioKit、wavBase64、clamp/lerp/sm 等）、licai-assets.js（LICAI_IMG）
 * 风格：米黄纸 + 点阵、抖动手绘线、斜线填充柱子、逐字打出的标题、红笔批注
 */
W = 1920; H = 1080; CX = W / 2;
var PAPER = '#FEFBF2';
var C = {
  ink: '#3a332d', sub: '#8a8178', faint: '#b9b0a3', grid: '#e9e1cf',
  orange: '#E8894A', blue: '#5B8DD6', green: '#4FB386', purple: '#7B6BD0', gray: '#8c8478',
  red: '#D8463B', gold: '#E2AE36', brown: '#7a5a48', cream: '#f3ead6', pink: '#F08C8C'
};
var HAND = '"ZCOOL KuaiLe","Noto Sans SC",sans-serif';
var BODY = '"Noto Sans SC",sans-serif';
var IMG = {};

/* 随机数：每条线一个种子，画面稳定不抖 */
function rnd(seed) { var s = Math.sin(seed * 91.37 + 17.13) * 43758.5453; return s - Math.floor(s); }
function jit(seed, a) { return (rnd(seed) * 2 - 1) * a; }

/* ───────── 纸张 ───────── */
function paper() {
  g.fillStyle = PAPER; g.fillRect(0, 0, W, H);
  g.fillStyle = C.grid;
  for (var y = 30; y < H; y += 40) for (var x = 30; x < W; x += 40) { g.beginPath(); g.arc(x, y, 1.6, 0, 6.283); g.fill(); }
}

/* ───────── 手绘线 ───────── */
// 一条抖动直线，k = 画出的比例
function hline(x1, y1, x2, y2, seed, color, lw, k) {
  k = k == null ? 1 : clamp(k, 0, 1); if (k <= 0) return;
  var len = Math.hypot(x2 - x1, y2 - y1), a = Math.min(4, len * .012);
  g.save(); g.strokeStyle = color || C.ink; g.lineWidth = lw || 3; g.lineCap = 'round'; g.lineJoin = 'round';
  for (var p = 0; p < 2; p++) {
    var n = Math.max(2, Math.round(len / 60)), pts = [];
    for (var i = 0; i <= n; i++) {
      var t = i / n, e = (i === 0 || i === n) ? .4 : 1;
      pts.push([lerp(x1, x2, t) + jit(seed + i * 3.1 + p * 50, a * e), lerp(y1, y2, t) + jit(seed + i * 5.7 + p * 50, a * e)]);
    }
    g.globalAlpha = p ? .35 : 1; g.lineWidth = (lw || 3) * (p ? .6 : 1);
    polyK(pts, k);
  }
  g.restore();
}
function polyK(pts, k) {
  var segs = pts.length - 1, upto = k * segs;
  g.beginPath(); g.moveTo(pts[0][0], pts[0][1]);
  for (var i = 1; i <= segs; i++) {
    if (i > upto) { var f = upto - (i - 1); if (f > 0) g.lineTo(lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)); break; }
    var m = i < segs ? [(pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2] : pts[i];
    g.quadraticCurveTo(pts[i][0], pts[i][1], m[0], m[1]);
  }
  g.stroke();
}
// 手绘矩形框
function hrect(x, y, w, h, seed, color, lw, k) {
  k = k == null ? 1 : k;
  var e = [[x, y, x + w, y], [x + w, y, x + w, y + h], [x + w, y + h, x, y + h], [x, y + h, x, y]];
  e.forEach(function (s, i) { hline(s[0] + jit(seed + i, 3), s[1] + jit(seed + i + 9, 3), s[2] + jit(seed + i + 4, 3), s[3] + jit(seed + i + 7, 3), seed + i * 11, color, lw, k * 4 - i); });
}
// 手绘圈（红笔圈重点），k = 画出比例
function hcircle(x, y, rx, ry, seed, color, lw, k) {
  k = k == null ? 1 : clamp(k, 0, 1); if (k <= 0) return;
  var pts = [], n = 28, a0 = -2.2 + jit(seed, .3), span = 6.283 * 1.12;
  for (var i = 0; i <= n; i++) { var a = a0 + span * i / n, r = 1 + jit(seed + i * 2.3, .05) + .06 * i / n; pts.push([x + Math.cos(a) * rx * r, y + Math.sin(a) * ry * r]); }
  g.save(); g.strokeStyle = color || C.red; g.lineWidth = lw || 4; g.lineCap = 'round'; polyK(pts, k); g.restore();
}
// 斜线填充的柱子（参考视频的招牌）
function hatchBar(x, y, w, h, color, seed, opt) {
  if (w <= 1) return; opt = opt || {};
  g.save();
  g.fillStyle = opt.fill || color; g.globalAlpha = opt.dashed ? .12 : .22; g.fillRect(x, y, w, h); g.globalAlpha = 1;
  g.beginPath(); g.rect(x, y, w, h); g.clip();
  g.strokeStyle = color; g.lineWidth = 3.2; g.lineCap = 'round';
  for (var s = -h; s < w + h; s += 15) { g.beginPath(); g.moveTo(x + s + jit(seed + s, 1.5), y + h); g.lineTo(x + s + h + jit(seed + s + 1, 1.5), y); g.stroke(); }
  g.restore();
  if (opt.dashed) { g.save(); g.setLineDash([9, 7]); g.strokeStyle = color; g.lineWidth = 3; g.strokeRect(x, y, w, h); g.restore(); }
  else hrect(x, y, w, h, seed, C.ink, 2.6);
}
// 手绘箭头（二次曲线）
function harrow(x1, y1, cx, cy, x2, y2, color, k, lw) {
  k = k == null ? 1 : clamp(k, 0, 1); if (k <= 0) return;
  var pts = []; for (var i = 0; i <= 20; i++) { var t = i / 20, u = 1 - t; pts.push([u * u * x1 + 2 * u * t * cx + t * t * x2, u * u * y1 + 2 * u * t * cy + t * t * y2]); }
  g.save(); g.strokeStyle = color || C.red; g.lineWidth = lw || 3.5; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); var upto = Math.floor(k * 20); g.moveTo(pts[0][0], pts[0][1]); for (i = 1; i <= upto; i++) g.lineTo(pts[i][0], pts[i][1]); g.stroke();
  if (k > .95) { var p = pts[20], q = pts[17], an = Math.atan2(p[1] - q[1], p[0] - q[0]), hs = 18;
    g.beginPath(); g.moveTo(p[0] - Math.cos(an - .45) * hs, p[1] - Math.sin(an - .45) * hs); g.lineTo(p[0], p[1]); g.lineTo(p[0] - Math.cos(an + .45) * hs, p[1] - Math.sin(an + .45) * hs); g.stroke(); }
  g.restore();
}
// 删除线（红笔划掉）
function strike(x1, y, x2, seed, k) { hline(x1, y + 4, x2, y - 6, seed, C.red, 6, k); }
// 大红叉
function bigX(x, y, s, k) { hline(x - s, y - s, x + s, y + s, 401, C.red, 9, k * 2); hline(x + s, y - s, x - s, y + s, 409, C.red, 9, k * 2 - 1); }
// 对勾
function tick(x, y, s, k, color) {
  k = clamp(k, 0, 1); if (k <= 0) return;
  g.save(); g.strokeStyle = color || C.green; g.lineWidth = 9; g.lineCap = 'round'; g.lineJoin = 'round';
  polyK([[x - s, y], [x - s * .3, y + s * .7], [x - s * .25, y + s * .65], [x + s, y - s * .8]], k); g.restore();
}
// 小皇冠
function crown(x, y, s, a) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.translate(x, y); g.scale(s, s); g.rotate(-.25);
  g.fillStyle = '#F6C945'; g.strokeStyle = C.ink; g.lineWidth = 2.5; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(-22, 12); g.lineTo(-24, -10); g.lineTo(-11, 2); g.lineTo(0, -16); g.lineTo(11, 2); g.lineTo(24, -10); g.lineTo(22, 12); g.closePath(); g.fill(); g.stroke();
  g.restore();
}
// 闪光小线（漫画里的“！”放射线）
function sparks(x, y, r, a, seed, color) {
  g.save(); g.globalAlpha = a; g.strokeStyle = color || C.gold; g.lineWidth = 5; g.lineCap = 'round';
  for (var i = 0; i < 3; i++) { var an = -1.9 + i * .55 + jit(seed + i, .1); g.beginPath(); g.moveTo(x + Math.cos(an) * r, y + Math.sin(an) * r); g.lineTo(x + Math.cos(an) * (r + 26), y + Math.sin(an) * (r + 26)); g.stroke(); }
  g.restore();
}
// 彩纸屑
function confetti(lt, n, seed) {
  if (lt < 0 || lt > 3.2) return;
  var cols = [C.orange, C.blue, C.green, C.purple, C.red, C.gold];
  g.save();
  for (var i = 0; i < n; i++) {
    var x0 = rnd(seed + i) * W, vy = 260 + rnd(seed + i * 3) * 260, y = -40 + vy * lt + 60 * lt * lt, x = x0 + Math.sin(lt * 3 + i) * 40;
    g.globalAlpha = clamp(3.2 - lt, 0, 1); g.fillStyle = cols[i % 6]; g.translate(x, y); g.rotate(lt * 4 + i); g.fillRect(-7, -3, 14, 6); g.setTransform(1, 0, 0, 1, 0, 0);
  }
  g.restore();
}
// 红色印章
function stamp(text, x, y, size, lt, rot) {
  if (lt < 0) return; var s = lt < .16 ? 2.2 - 1.2 * eout(lt / .16) : 1;
  g.save(); g.translate(x, y); g.rotate(rot == null ? -.12 : rot); g.scale(s, s); g.globalAlpha = clamp(lt / .1, 0, 1) * .92;
  g.font = size + 'px ' + HAND; var w = g.measureText(text).width + size * .9, h = size * 1.55;
  g.strokeStyle = C.red; g.lineWidth = 5; g.strokeRect(-w / 2, -h / 2, w, h); g.lineWidth = 2; g.strokeRect(-w / 2 + 7, -h / 2 + 7, w - 14, h - 14);
  g.fillStyle = C.red; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, 0, 2);
  g.restore();
}

/* ───────── 文字 ───────── */
// 逐字打出；{r}红{/} {o}橙{/} {b}蓝{/} {g}绿{/}
var TAGS = { r: 'red', o: 'orange', b: 'blue', g: 'green', p: 'purple', s: 'sub', n: 'brown' };
function rich(text, base) {
  var out = [], col = base, i = 0;
  while (i < text.length) {
    if (text[i] === '{') { var j = text.indexOf('}', i), tag = text.slice(i + 1, j); col = tag === '/' ? base : C[TAGS[tag]]; i = j + 1; continue; }
    out.push([text[i], col]); i++;
  }
  return out;
}
// 返回已打出的字数；lt = 距开始打字的时间
function typeText(text, x, y, size, lt, opt) {
  opt = opt || {}; if (lt < 0) return 0;
  var chars = rich(text, opt.color || C.ink), n = Math.min(chars.length, Math.floor(lt * (opt.cps || 16)) + 1);
  g.save(); g.font = (opt.weight ? opt.weight + ' ' : '') + size + 'px ' + (opt.font || HAND); g.textBaseline = 'middle'; g.textAlign = 'left';
  var ls = opt.ls == null ? size * .04 : opt.ls, total = 0, ws = chars.map(function (c) { var w = g.measureText(c[0]).width; total += w + ls; return w; });
  total -= ls; var x0 = opt.align === 'center' ? x - total / 2 : opt.align === 'right' ? x - total : x;
  for (var i = 0; i < n; i++) { g.fillStyle = chars[i][1]; g.fillText(chars[i][0], x0, y); x0 += ws[i] + ls; }
  g.restore();
  return { n: n, done: n >= chars.length, width: total, x: opt.align === 'center' ? x - total / 2 : x };
}
function txt(text, x, y, size, color, opt) {
  opt = opt || {}; g.save(); g.font = (opt.weight ? opt.weight + ' ' : '') + size + 'px ' + (opt.font || HAND);
  g.fillStyle = color || C.ink; g.textAlign = opt.align || 'left'; g.textBaseline = 'middle'; if (opt.a != null) g.globalAlpha = opt.a;
  g.fillText(text, x, y); var w = g.measureText(text).width; g.restore(); return w;
}
function textW(text, size, font) { g.save(); g.font = size + 'px ' + (font || HAND); var w = g.measureText(text).width; g.restore(); return w; }

/* 页眉：问题标题 + 彩色下划线 + 一行口径小字 + 右上角吉祥物（参考视频的版式） */
function header(lt, title, sub, ulColor) {
  var r = typeText(title, 96, 112, 70, lt, { cps: 18 });
  var tw = textW(title.replace(/\{[^}]*\}/g, ''), 70) + 30;
  if (r.done) hline(90, 160, 90 + tw, 162, 31, ulColor || C.orange, 7, (lt - title.length / 18) / .35);
  if (sub) txt(sub, 98, 206, 30, C.sub, { font: BODY, a: clamp((lt - .6) / .3, 0, 1) });
  mascot(W - 190, 120, .9);
}
function footnote(text, a) { txt(text, 96, H - 46, 22, C.sub, { font: BODY, a: a == null ? 1 : a }); }

/* 右上角吉祥物：圆框里的李财笑脸 + 一辆小手绘自行车 */
function mascot(x, y, s, face) {
  g.save(); g.translate(x, y); g.scale(s, s);
  var hm = IMG.helmet;
  if (hm && !face) { var hh = 190, ww = hh * hm.width / hm.height; g.drawImage(hm, -ww / 2, -hh / 2 + 10, ww, hh); g.restore(); return; }
  bike(0, 52, .52, 0, C.ink);
  g.save(); g.beginPath(); g.arc(0, -10, 64, 0, 6.283); g.fillStyle = PAPER; g.fill(); g.clip();
  var im = IMG[face || 'happy']; if (im) g.drawImage(im, -78, -86, 156, 156 * im.height / im.width);
  g.restore();
  hcircle(0, -10, 64, 64, 77, C.ink, 3.5);
  g.restore();
}

/* 手绘自行车：rot = 车轮转角 */
function bike(x, y, s, rot, color) {
  g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = color || C.ink; g.lineCap = 'round'; g.lineJoin = 'round';
  var R = 62, rw = [-105, 30], fw = [105, 30];
  [rw, fw].forEach(function (w, wi) {
    g.lineWidth = 5; g.beginPath(); g.arc(w[0], w[1], R, 0, 6.283); g.stroke();
    g.lineWidth = 2; for (var i = 0; i < 6; i++) { var a = rot + i * Math.PI / 6; g.beginPath(); g.moveTo(w[0] - Math.cos(a) * R, w[1] - Math.sin(a) * R); g.lineTo(w[0] + Math.cos(a) * R, w[1] + Math.sin(a) * R); g.stroke(); }
    g.beginPath(); g.arc(w[0], w[1], 6, 0, 6.283); g.fillStyle = color || C.ink; g.fill();
  });
  var bb = [-10, 30], st = [-40, -50], ht = [75, -48];
  g.lineWidth = 7; g.strokeStyle = C.orange;
  g.beginPath(); g.moveTo(rw[0], rw[1]); g.lineTo(bb[0], bb[1]); g.lineTo(ht[0], ht[1]); g.lineTo(st[0], st[1]); g.lineTo(bb[0], bb[1]); g.moveTo(st[0], st[1]); g.lineTo(rw[0], rw[1]); g.stroke();
  g.strokeStyle = color || C.ink; g.lineWidth = 5;
  g.beginPath(); g.moveTo(ht[0], ht[1]); g.lineTo(fw[0], fw[1]); g.moveTo(ht[0], ht[1]); g.lineTo(ht[0] - 8, ht[1] - 28); g.lineTo(ht[0] + 22, ht[1] - 34); g.stroke();
  g.beginPath(); g.moveTo(st[0], st[1]); g.lineTo(st[0] - 6, st[1] - 20); g.stroke();
  g.lineWidth = 9; g.beginPath(); g.moveTo(st[0] - 26, st[1] - 22); g.lineTo(st[0] + 16, st[1] - 22); g.stroke();
  g.lineWidth = 4; g.beginPath(); g.arc(bb[0], bb[1], 14, 0, 6.283); g.stroke();
  var pa = rot * .5; g.beginPath(); g.moveTo(bb[0] + Math.cos(pa) * 26, bb[1] + Math.sin(pa) * 26); g.lineTo(bb[0] - Math.cos(pa) * 26, bb[1] - Math.sin(pa) * 26); g.stroke();
  g.restore();
}

/* 车型手绘图：road 公路车 / gravel 瓜车（砾石公路车） / mtb 山地车 / flat 平把公路 / fold 折叠车 / city 通勤车 */
function bikeType(x, y, s, type, rot, color) {
  rot = rot || 0; var fc = color || C.orange;
  var P = {
    road: { R: 62, tire: 4, wb: 104, bar: 'drop', frame: 'diamond' },
    gravel: { R: 61, tire: 8, wb: 106, bar: 'drop', frame: 'diamond', knob: 1 },
    mtb: { R: 60, tire: 11, wb: 108, bar: 'riser', frame: 'diamond', fork: 1 },
    flat: { R: 62, tire: 6, wb: 104, bar: 'flat', frame: 'diamond' },
    fold: { R: 38, tire: 6, wb: 82, bar: 'fold', frame: 'fold' },
    city: { R: 60, tire: 7, wb: 108, bar: 'city', frame: 'step', basket: 1, fender: 1 }
  }[type];
  g.save(); g.translate(x, y); g.scale(s, s); g.lineCap = 'round'; g.lineJoin = 'round';
  var ink = C.ink, R = P.R, rw = [-P.wb, 30], fw = [P.wb, 30], wy = 30;
  [rw, fw].forEach(function (w) {
    g.strokeStyle = ink; g.lineWidth = P.tire; g.beginPath(); g.arc(w[0], w[1], R, 0, 6.283); g.stroke();
    if (type === 'mtb' || P.knob) { var kn = P.knob ? 3 : 5; g.lineWidth = 2; for (var k = 0; k < (P.knob ? 32 : 24); k++) { var a = k / (P.knob ? 32 : 24) * 6.283; g.beginPath(); g.moveTo(w[0] + Math.cos(a) * (R + P.tire / 2), w[1] + Math.sin(a) * (R + P.tire / 2)); g.lineTo(w[0] + Math.cos(a) * (R + P.tire / 2 + kn), w[1] + Math.sin(a) * (R + P.tire / 2 + kn)); g.stroke(); } }
    g.lineWidth = 1.8; for (var i = 0; i < 6; i++) { var an = rot + i * Math.PI / 6; g.beginPath(); g.moveTo(w[0] - Math.cos(an) * (R - P.tire / 2), w[1] - Math.sin(an) * (R - P.tire / 2)); g.lineTo(w[0] + Math.cos(an) * (R - P.tire / 2), w[1] + Math.sin(an) * (R - P.tire / 2)); g.stroke(); }
    g.fillStyle = ink; g.beginPath(); g.arc(w[0], w[1], 5, 0, 6.283); g.fill();
    if (P.fender) { g.lineWidth = 4; g.strokeStyle = C.gray; g.beginPath(); g.arc(w[0], w[1], R + 8, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); }
  });
  var bb = [-8, wy], st, ht;
  g.strokeStyle = fc; g.lineWidth = type === 'mtb' ? 9 : 7;
  if (P.frame === 'diamond') {
    st = [-38, -50]; ht = [70, -46];
    g.beginPath(); g.moveTo(rw[0], rw[1]); g.lineTo(bb[0], bb[1]); g.lineTo(ht[0], ht[1]); g.lineTo(st[0], st[1]); g.lineTo(bb[0], bb[1]); g.moveTo(st[0], st[1]); g.lineTo(rw[0], rw[1]); g.stroke();
  } else if (P.frame === 'step') {
    st = [-40, -52]; ht = [72, -50];
    g.beginPath(); g.moveTo(rw[0], rw[1]); g.lineTo(bb[0], bb[1]); g.moveTo(st[0], st[1]); g.lineTo(bb[0], bb[1]); g.quadraticCurveTo(30, 20, ht[0], ht[1]); g.moveTo(st[0] + 4, st[1] + 10); g.lineTo(rw[0], rw[1]); g.stroke();
  } else {
    st = [-30, -46]; ht = [58, -40];
    g.beginPath(); g.moveTo(rw[0], rw[1]); g.lineTo(bb[0], bb[1]); g.lineTo(ht[0] - 6, ht[1] + 40); g.lineTo(ht[0], ht[1]); g.moveTo(-14, -4); g.lineTo(st[0], st[1]); g.moveTo(-10, 6); g.lineTo(rw[0], rw[1]); g.stroke();
    g.fillStyle = ink; g.beginPath(); g.arc(18, 12, 6, 0, 6.283); g.fill(); // 折叠铰链
  }
  // 前叉
  g.strokeStyle = ink; g.lineWidth = 5;
  if (P.fork) { g.lineWidth = 11; g.strokeStyle = '#555'; g.beginPath(); g.moveTo(ht[0], ht[1]); g.lineTo(lerp(ht[0], fw[0], .5), lerp(ht[1], fw[1], .5)); g.stroke(); g.lineWidth = 5; g.strokeStyle = ink; }
  g.beginPath(); g.moveTo(ht[0], ht[1]); g.lineTo(fw[0], fw[1]); g.stroke();
  // 车把
  var top = [ht[0] - 6, ht[1] - (type === 'fold' ? 52 : 26)];
  g.beginPath(); g.moveTo(ht[0], ht[1]); g.lineTo(top[0], top[1]); g.stroke();
  g.lineWidth = 5;
  if (P.bar === 'drop') { g.beginPath(); g.moveTo(top[0], top[1]); g.lineTo(top[0] + 26, top[1]); g.quadraticCurveTo(top[0] + 46, top[1] + 4, top[0] + 40, top[1] + 26); g.lineTo(top[0] + 26, top[1] + 30); g.stroke(); }
  else if (P.bar === 'city') { g.beginPath(); g.moveTo(top[0], top[1]); g.quadraticCurveTo(top[0] - 4, top[1] - 16, top[0] - 26, top[1] - 14); g.stroke(); }
  else { g.beginPath(); g.moveTo(top[0] - 2, top[1] - (P.bar === 'riser' ? 8 : 0)); g.lineTo(top[0] + 22, top[1] - (P.bar === 'riser' ? 8 : 0)); g.stroke(); }
  // 坐垫
  g.beginPath(); g.moveTo(st[0], st[1]); g.lineTo(st[0] - 5, st[1] - (type === 'fold' ? 34 : 20)); g.stroke();
  var sy = st[1] - (type === 'fold' ? 34 : 20); g.lineWidth = type === 'city' ? 12 : 8; g.beginPath(); g.moveTo(st[0] - 28, sy - 2); g.lineTo(st[0] + 14, sy - 2); g.stroke();
  // 车筐
  if (P.basket) { g.lineWidth = 3; g.strokeStyle = C.brown; g.strokeRect(fw[0] - 20, ht[1] - 52, 56, 40); for (var q = 0; q < 4; q++) { g.beginPath(); g.moveTo(fw[0] - 20 + q * 14, ht[1] - 52); g.lineTo(fw[0] - 20 + q * 14, ht[1] - 12); g.stroke(); } }
  // 牙盘与曲柄
  g.strokeStyle = ink; g.lineWidth = 4; g.beginPath(); g.arc(bb[0], bb[1], 13, 0, 6.283); g.stroke();
  var pa = rot * .5; g.beginPath(); g.moveTo(bb[0] + Math.cos(pa) * 24, bb[1] + Math.sin(pa) * 24); g.lineTo(bb[0] - Math.cos(pa) * 24, bb[1] - Math.sin(pa) * 24); g.stroke();
  g.restore();
}

/* 通用声音：轻快背景乐 + 常用音效（每集复用） */
function licaiSound(K, DUR) {
  var CH = [[261.63, 329.63, 392], [246.94, 293.66, 392], [220, 261.63, 329.63], [220, 261.63, 349.23]], BASS = [130.81, 98, 110, 87.31];
  for (var t = .2, i = 0; t < DUR - 1; t += 2, i++) {
    var ch = CH[i % 4];
    K.tone(BASS[i % 4], t, 1.0, .09, 'sine', K.music, .01); K.tone(BASS[i % 4], t + 1, .9, .07, 'sine', K.music, .01);
    [0, 1, 2, 1, 0, 2, 1, 2].forEach(function (n, j) { K.tone(ch[n] * 2, t + j * .25, .3, j % 2 ? .02 : .03, 'triangle', K.music, .004); });
    if (i % 2 === 1) K.tone(ch[2] * 4, t + 1.75, .5, .012, 'sine', K.music);
    for (var b = 0; b < 4; b++) K.hat(t + b * .5 + .25, .35);
  }
  var mg = K.music.gain; mg.setValueAtTime(.8, 0); mg.setValueAtTime(.8, DUR - 2.5); mg.linearRampToValueAtTime(0, DUR);
  return {
    ticks: function (t0, n, cps) { for (var i = 0; i < n; i++) K.tone(1800 + K.ar() * 600, t0 + i / (cps || 18), .025, .018, 'square'); },
    pop: function (t) { K.tone(520, t, .08, .07, 'sine'); K.tone(880, t + .05, .12, .06, 'sine'); },
    pen: function (t, d) { K.noise(t, d || .35, .05, 'bandpass', 3200, null, 1.4); },
    coin: function (t) { K.tone(2637, t, .18, .035); K.tone(3951, t + .02, .22, .025); },
    bell: function (t) { for (var i = 0; i < 2; i++) { K.tone(2093, t + i * .18, .5, .05); K.tone(2793, t + i * .18, .45, .03); } },
    grow: function (t, d) { K.riser(t, t + (d || .8), .03); },
    ding: function (t) { K.ding(t); }, wrong: function (t) { K.wrong(t); }, whoosh: function (t) { K.whoosh(t); },
    stamp: function (t) { K.thud(t, .5); K.ding(t + .05); }
  };
}

/* 李财图片：弹出入场 + 呼吸 */
function cat(name, x, y, h, lt, opt) {
  opt = opt || {};
  // 有对应逐帧动作的表情（licai-move.js 的 ANIM）自动换成动作；封面（noPop + bob:false）保持静态
  var an = typeof ANIM !== 'undefined' && !(opt.noPop && opt.bob === false) && !opt.still ? ANIM[name] : null;
  if (!an && typeof LICAI_SEQ !== 'undefined' && LICAI_SEQ[name] && !(opt.noPop && opt.bob === false)) an = [name, 7, typeof SEQ_ONCE !== 'undefined' && SEQ_ONCE.indexOf(name) >= 0, 1];
  if (an && lt >= 0 && IMG['seq:' + an[0] + ':0']) {
    var b0 = opt.noPop ? 1 : pop(lt);
    seqDraw(an[0], lt, an[1], x, y + h / 2, h * an[3], { once: an[2], flip: opt.flip, sx: b0, sy: b0, a: opt.a });
    return;
  }
  var im = IMG[name]; if (!im || lt < 0) return;
  var b = opt.noPop ? 1 : pop(lt), bob = opt.bob === false ? 0 : Math.sin(lt * 3.2) * 6, w = h * im.width / im.height;
  g.save(); g.translate(x, y + bob); g.scale(b * (opt.flip ? -1 : 1), b); if (opt.rot) g.rotate(opt.rot);
  g.globalAlpha = opt.a == null ? 1 : opt.a;
  g.drawImage(im, -w / 2, -h / 2, w, h); g.restore();
}
// 圆框头像（来自角色设定图的小表情）
function badge(name, x, y, r, lt, seed) {
  var im = IMG[name]; if (!im || lt < 0) return; var b = pop(lt);
  g.save(); g.translate(x, y); g.scale(b, b);
  g.beginPath(); g.arc(0, 0, r, 0, 6.283); g.fillStyle = PAPER; g.fill(); g.save(); g.clip();
  var s = r * 2.25 / Math.min(im.width, im.height); g.drawImage(im, -im.width * s / 2, -im.height * s / 2, im.width * s, im.height * s); g.restore();
  hcircle(0, 0, r, r, seed || 5, C.ink, 4); g.restore();
}

/* ───────── 运行框架：硬切 + 导出接口 ───────── */
var COVER_SIZES = { '9x16': [1080, 1920], '3x4': [1080, 1440], '16x9': [1920, 1080], '4x3': [1440, 1080] };
function coverCanvas(key, draw) {
  var sz = COVER_SIZES[key], saved = [W, H, CX];
  W = sz[0]; H = sz[1]; CX = W / 2;
  var c = document.createElement('canvas'); c.width = W; c.height = H; g = c.getContext('2d');
  draw(key, W, H);
  W = saved[0]; H = saved[1]; CX = saved[2]; g = ctx;
  return c.toDataURL('image/jpeg', .95);
}
function licaiRun(opt) {
  var RENDER = /render/.test(location.search);
  if (RENDER) document.body.classList.add('render');
  cv = document.getElementById('c'); ctx = cv.getContext('2d'); g = ctx;
  var T = opt.T, S = opt.S, DUR = T[T.length - 1];
  function sceneIndex(t) { for (var i = 0; i < S.length; i++) if (t < T[i + 1]) return i; return S.length - 1; }
  function drawFrame(t) {
    g = ctx; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    var i = sceneIndex(t); paper(); g.save(); S[i](t - T[i], t); g.restore();
    if (t > DUR - .5) { ctx.globalAlpha = (t - (DUR - .5)) / .5; ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
  }
  function audio() {
    var c = new OfflineAudioContext(2, Math.ceil(48000 * DUR), 48000), K = audioKit(c, opt.seed);
    opt.audio(K, c, DUR, T);
    return c.startRendering().then(wavBase64);
  }
  function preview() {
    drawFrame(0); ctx.fillStyle = 'rgba(58,51,45,.5)'; ctx.fillRect(0, 0, W, H);
    txt('▶  点击播放', CX, H / 2, 64, '#fff', { align: 'center' });
    var playing = false;
    cv.addEventListener('click', function () {
      if (playing) return; playing = true;
      var ac = new (window.AudioContext || window.webkitAudioContext)();
      audio().then(function (b64) { var bin = atob(b64), u8 = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); return ac.decodeAudioData(u8.buffer); })
        .then(function (ab) {
          var src = ac.createBufferSource(); src.buffer = ab; src.connect(ac.destination); var t0 = ac.currentTime + .1; src.start(t0);
          (function loop() { var t = ac.currentTime - t0; if (t >= 0) drawFrame(Math.min(t, DUR - 1 / FPS)); if (t < DUR) requestAnimationFrame(loop); else playing = false; })();
        });
    });
  }
  var SRCS = Object.assign({}, LICAI_IMG, typeof LICAI_EMO === 'undefined' ? {} : LICAI_EMO);
  if (typeof LICAI_SEQ !== 'undefined') Object.keys(LICAI_SEQ).forEach(function (n) { LICAI_SEQ[n].frames.forEach(function (f, j) { SRCS['seq:' + n + ':' + j] = f.src; }); });
  var imgs = Object.keys(SRCS).map(function (k) { return new Promise(function (r) { var im = new Image(); im.onload = function () { IMG[k] = im; r(); }; im.onerror = r; im.src = SRCS[k]; }); });
  var all = opt.allText + '0123456789%≈?？!！·，。：、=+';
  Promise.race([
    Promise.all([document.fonts.load('64px "ZCOOL KuaiLe"', all), document.fonts.load('400 64px "Noto Sans SC"', all), document.fonts.load('700 64px "Noto Sans SC"', all)].concat(imgs)),
    new Promise(function (r) { setTimeout(r, 25000); })
  ]).then(function () { return document.fonts.ready; }).catch(function () {}).then(function () {
    window.FILM = {
      ready: true, frames: Math.round(DUR * FPS), fps: FPS, size: [W, H],
      encode: opt.encode || { b: '8M', maxrate: '12M', bufsize: '20M' },
      fontStatus: function () { return 'kuaile:' + document.fonts.check('64px "ZCOOL KuaiLe"', '李财') + ' noto:' + document.fonts.check('400 64px "Noto Sans SC"', '李财') + ' imgs:' + Object.keys(IMG).length; },
      render: function (i, q) { drawFrame(i / FPS); return cv.toDataURL('image/jpeg', q || .93); },
      cover: function () { return coverCanvas('16x9', opt.cover); },
      covers: function () { var o = {}; Object.keys(COVER_SIZES).forEach(function (k) { o[k] = coverCanvas(k, opt.cover); }); return o; },
      renderAudio: audio, seek: drawFrame
    };
    if (!RENDER) preview();
  });
}

/* ───────── 每集通用的页面组件 ───────── */
function paw(x, y, s, a, col) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.translate(x, y); g.scale(s, s); g.fillStyle = col || C.pink;
  g.beginPath(); g.ellipse(0, 8, 15, 12, 0, 0, 6.283); g.fill();
  [[-15, -10], [-5, -18], [6, -18], [16, -10]].forEach(function (p) { g.beginPath(); g.ellipse(p[0], p[1], 5.5, 7, 0, 0, 6.283); g.fill(); });
  g.restore();
}
function cross(x, y, s, k) { hline(x - s, y - s, x + s, y + s, 701 + x, C.red, 7, k * 2); hline(x + s, y - s, x - s, y + s, 709 + x, C.red, 7, k * 2 - 1); }
function coin(x, y, s, a, ch) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.translate(x, y); g.scale(s, s);
  g.beginPath(); g.arc(0, 0, 30, 0, 6.283); g.fillStyle = '#F3C75A'; g.fill(); g.lineWidth = 3; g.strokeStyle = '#a77a1c'; g.stroke();
  g.beginPath(); g.arc(0, 0, 23, 0, 6.283); g.lineWidth = 1.5; g.stroke();
  txt(ch || '财', 0, 2, 30, '#7a5410', { align: 'center' });
  g.restore();
}
// 圆点编号
function numDot(n, x, y, lt, col) {
  if (lt < 0) return; g.save(); g.translate(x, y); g.scale(pop(lt), pop(lt)); g.fillStyle = col || C.red;
  g.beginPath(); g.arc(0, 0, 38, 0, 6.283); g.fill(); txt(String(n), 0, 3, 50, '#fff', { align: 'center' }); g.restore();
}
// 开场页：左边李财，右边两行标题
function openScene(lt, emo, l1, l2, ep, series) {
  cat(emo, 520, 560, 820, lt - .15);
  typeText(l1, 1000, 380, 110, lt - .7, { cps: 10 });
  var n2 = l2.replace(/\{[^}]*\}/g, '').length, z2 = Math.min(150, 150 * 860 / textW(l2.replace(/\{[^}]*\}/g, ''), 150)), r = typeText(l2, 1000, 540, z2, lt - 1.4, { cps: 8 });
  if (r.done) hline(1000, 632, 1000 + r.width, 630, 12, C.orange, 9, (lt - 1.4 - n2 / 8) / .4);
  txt((series || '李财骑行记') + ' · 第 ' + ep + ' 集', 1004, 720, 44, C.sub, { a: clamp((lt - 2.6) / .4, 0, 1) });
  sparks(1000 + r.width + 60, 470, 30, clamp((lt - 2.4) / .2, 0, 1), 3);
}
// 下集预告页
function nextScene(lt, emo, l1, l2, bk, bc) {
  cat(emo, 540, 560, 820, lt - .1);
  txt('下集', 1004, 330, 56, C.sub, { a: clamp(lt / .3, 0, 1) });
  typeText(l1, 1000, 450, 120, lt - .4, { cps: 10 });
  typeText(l2, 1000, 600, 120, lt - 1.0, { cps: 10 });
  bikeType(1250, 830, .9, bk || 'flat', lt * 4, bc || C.green);
  stamp('下期见', 1640, 830, 70, lt - 2.4);
  confetti(lt - 2.0, 70, 9);
}
// 封面：标题两行 + 卖点一行 + 李财 + 可选插画
function epCover(key, w, h, o) {
  paper();
  var vert = h > w;
  if (vert) {
    var s = w / 1080;
    txt((o.series || '李财骑行记') + ' · 第 ' + o.ep + ' 集', 80 * s, 140 * s, 46 * s, C.sub);
    var av = w - 140 * s, y1 = Math.min(150 * s, 150 * s * av / textW(o.l1, 150 * s)), y2 = Math.min(170 * s, 170 * s * av / textW(o.l2, 170 * s));
    txt(o.l1, 80 * s, 290 * s, y1, C.ink);
    txt(o.l2, 80 * s, 470 * s, y2, C.orange);
    hline(90 * s, 580 * s, 90 * s + textW(o.l2, y2), 576 * s, 12, C.orange, 12 * s);
    txt(o.sub, 86 * s, 670 * s, 52 * s, C.ink);
    var ch = Math.min(h - 980 * s, 1000 * s);
    if (o.art) o.art(540 * s, 820 * s, .8 * s, true);
    cat(o.emo, w * .5, h - ch / 2 - 20 * s, ch, 1, { noPop: true, bob: false });
  } else {
    var s2 = h / 1080, q = key === '4x3';
    var es = o.emoScale || 1; cat(o.emo, q ? w * .25 : h * .38, h * .5, h * (q ? .72 : .86) * es, 1, { noPop: true, bob: false });
    var x = w * (q ? .5 : .44);
    txt((o.series || '李财骑行记') + ' · 第 ' + o.ep + ' 集', x, 190 * s2, 44 * s2, C.sub);
    var avail = w - x - 50 * s2, z1 = Math.min(140 * s2, 140 * s2 * avail / textW(o.l1, 140 * s2)), z2 = Math.min(170 * s2, 170 * s2 * avail / textW(o.l2, 170 * s2));
    txt(o.l1, x, 340 * s2, z1, C.ink);
    txt(o.l2, x, 520 * s2, z2, C.orange);
    hline(x + 10 * s2, 630 * s2, x + textW(o.l2, z2), 626 * s2, 12, C.orange, 12 * s2);
    txt(o.sub, x, 730 * s2, (q ? 46 : 56) * s2, C.ink);
    if (o.art) o.art(x + (q ? 300 : 380) * s2, 900 * s2, (q ? .7 : .8) * s2, false);
  }
}
// 简笔小人（灰色线条），关节坐标由调用方给出
function stickLine(pts, col, lw) { g.save(); g.strokeStyle = col || C.ink; g.lineWidth = lw || 9; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (var i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.stroke(); g.restore(); }
// 两段式腿的反解：髋 h、脚 f、大腿 a、小腿 b，返回膝盖位置（膝盖朝 dir 一侧）
function knee(h, f, a, b, dir) {
  var dx = f[0] - h[0], dy = f[1] - h[1], d = Math.min(Math.hypot(dx, dy), a + b - .01), an = Math.atan2(dy, dx);
  var c = Math.acos(clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1));
  var t = an + (dir || -1) * c; return [h[0] + Math.cos(t) * a, h[1] + Math.sin(t) * a];
}
// “三个错误”页：items = [[错误, 正确做法], ...]
function mistakesPage(lt, title, items, emo, seed) {
  header(lt, title, '', C.red);
  items.forEach(function (p, i) {
    var y = 360 + i * 190, ct = lt - .8 - i * 2.2; if (ct < 0) return;
    numDot(i + 1, 170, y, ct, C.red);
    var r = typeText(p[0], 250, y - 14, 58, ct - .2, { cps: 12 });
    if (ct > 1.2) strike(240, y - 10, 250 + r.width + 12, (seed || 1500) + i, (ct - 1.2) / .3);
    if (ct > 1.5) { tick(270, y + 58, 18, (ct - 1.5) / .3); txt(p[1], 310, y + 58, 36, C.green, { a: clamp((ct - 1.6) / .3, 0, 1) }); }
  });
  cat(emo, 1540, 660, 520, lt - .6);
}
// 编号清单页：items = [[主句（可带颜色标记）, 小字], ...]
function listPage(lt, title, sub, items, col, emo, opt) {
  opt = opt || {};
  header(lt, title, sub, col);
  var dy = opt.dy || 190, gap = opt.gap || 1.8;
  items.forEach(function (t, i) {
    var y = (opt.y0 || 360) + i * dy, ct = lt - .8 - i * gap; if (ct < 0) return;
    numDot(i + 1, 170, y, ct, col);
    typeText(t[0], 250, y - 16, opt.size || 58, ct - .2, { cps: 12 });
    if (t[1]) txt(t[1], 254, y + 48, 36, C.sub, { font: BODY, a: clamp((ct - .9) / .3, 0, 1) });
  });
  if (emo) cat(emo, opt.cx || 1500, opt.cy || 640, opt.ch || 560, lt - .6);
}
