/* 李财骑行小课堂 · 竖版教程公用件（手绘 + 实拍相框），在 shortkit.js 之后加载
 * 实拍片段不在画布里画：画布只画相框和标注，成片由 tut-comp.py 按同一份镜头表用 ffmpeg 叠进相框
 */
var TFR = { W: { x: 60, y: 430, w: 960, h: 540 }, V: { x: 70, y: 430, w: 420, h: 746 } };
var tk01 = function (t, a, b) { return clamp((t - a) / (b - a), 0, 1); };
// shots: [[开始, 结束, 'W'|'V', 相框下的说明], ...]
function tutFrames(shots) {
  function frame(t) {
    var s = shots.find(function (x) { return t >= x[0] && t < x[1]; }); if (!s) return; var P = TFR[s[2]];
    g.save(); g.fillStyle = 'rgba(58,51,45,.18)'; g.fillRect(P.x - 8, P.y + 4, P.w + 30, P.h + 30);
    g.fillStyle = '#fff'; g.fillRect(P.x - 16, P.y - 16, P.w + 32, P.h + 32);
    g.fillStyle = '#3a332d'; g.fillRect(P.x, P.y, P.w, P.h); g.restore();
    hrect(P.x - 16, P.y - 16, P.w + 32, P.h + 32, 611, C.ink, 3, 1);
    [[P.x + 40, P.y - 18, -.25], [P.x + P.w - 40, P.y - 18, .22]].forEach(function (p) { g.save(); g.translate(p[0], p[1]); g.rotate(p[2]); g.fillStyle = 'rgba(232,200,120,.75)'; g.fillRect(-60, -18, 120, 36); g.restore(); });
    if (s[3]) { var k = clamp((t - s[0]) / .3, 0, 1), y = P.y + P.h + 62; txt(s[3], CX - 30, y, 50, C.ink, { align: 'center', a: k }); hline(CX - 30 - textW(s[3], 50) / 2, y + 38, CX - 30 + textW(s[3], 50) / 2, y + 36, 612, C.orange, 6, k); }
  }
  return function (list) { return list.map(function (sc) { return [sc[0], sc[1], function (lt, t) { sc[2](lt, t); frame(t); }]; }); };
}
function boxNote(x, y, w, h, seed, col, a) { if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = 'rgba(255,253,246,.95)'; g.fillRect(x, y, w, h); g.restore(); hrect(x, y, w, h, seed, col || C.ink, 3.5, a); }
// 开头预告：编号 + 关键词，右下角李财
function tutPreview(t, t0, keys, emo) {
  keys.forEach(function (k, i) { var ct = t - t0 - i * .5, y = 520 + i * (keys.length > 3 ? 140 : 170); if (ct < 0) return; numDot(i + 1, 140, y, ct, C.orange); txt(k, 210, y, keys.length > 3 ? 64 : 72, C.ink, { a: clamp(ct / .2, 0, 1) }); });
  if (emo) cat(emo, 830, 1020, 300, t - t0);
}
// 口诀：一排红章 + 李财
function tutSlogan(t, t0, keys, emo) {
  keys.forEach(function (k, i) { var ct = t - t0 - i * .9; if (ct < 0) return; stamp(k, 330, 540 + i * (keys.length > 3 ? 150 : 200), keys.length > 3 ? 76 : 90, ct, -.06 + i * .04); });
  cat(emo || '叉腰得意', 820, 900, 380, t - t0 + .8);
}
// 结尾：李财打招呼 + 气泡 + 关注
function tutEnd(lt, t, t0, bubble, follow) {
  cat('打招呼', 520, 790, 560, lt - .1);
  g.save(); g.globalAlpha = tk01(t, t0 + .6, t0 + .9); g.fillStyle = '#fff'; g.strokeStyle = C.ink; g.lineWidth = 5;
  g.beginPath(); g.roundRect(690, 450, 280, 140, 40); g.fill(); g.stroke(); g.beginPath(); g.moveTo(730, 588); g.lineTo(710, 640); g.lineTo(780, 588); g.fill(); g.stroke();
  txt(bubble, 830, 520, 40, C.orange, { align: 'center' }); g.restore();
  txt(follow || '关注李财，骑车少走弯路', 520, 1150, 44, C.sub, { align: 'center', a: tk01(t, t0 + 4.2, t0 + 4.6) });
}
// 简笔小人：关节用 [x, y]，col 线色
function stick(j, col, lw) {
  var c = col || C.ink, w = lw || 12;
  [[j.neck, j.hip], [j.neck, j.el1, j.h1], [j.neck, j.el2, j.h2], [j.hip, j.k1, j.f1], [j.hip, j.k2, j.f2]].forEach(function (p) { if (p.every(Boolean)) stickLine(p, c, w); });
  g.save(); g.fillStyle = c; g.beginPath(); g.arc(j.head[0], j.head[1], w * 2.4, 0, 6.283); g.fill(); g.restore();
}
// 两两对比卡：✗ 上 / ✓ 下
function tutCompare(t, t0, bad, badSub, good, goodSub) {
  boxNote(90, 460, 860, 300, 701, C.red, tk01(t, t0, t0 + .3));
  txt(bad, 140, 530, 58, C.ink, { a: tk01(t, t0 + .1, t0 + .4) }); bigX(840, 560, 60, tk01(t, t0 + 1.0, t0 + 1.3));
  txt(badSub, 140, 640, 38, C.red, { a: tk01(t, t0 + 1.4, t0 + 1.7) });
  boxNote(90, 800, 860, 260, 702, C.green, tk01(t, t0 + 2.2, t0 + 2.5));
  txt(good, 140, 870, 58, C.ink, { a: tk01(t, t0 + 2.3, t0 + 2.6) }); tick(840, 880, 50, tk01(t, t0 + 2.8, t0 + 3.1));
  txt(goodSub, 140, 970, 38, C.green, { a: tk01(t, t0 + 3.0, t0 + 3.3) });
}
