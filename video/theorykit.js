/* 李财骑行实验室 · 理论竖版（1080×1920，深色底、黑体、干净线条；先出画面、后期配音）
 * 依赖 snowkit.js、licai-assets.js、licai-emo.js、licaikit.js；在 licaikit 之后加载
 * 版式：左上角李财小头像 + 系列名 / 顶部话题 / 中间图示区 y 380~1180 / 字幕 y≈1300
 */
W = 1080; H = 1920; CX = W / 2;
var TH = { bg: '#11161d', bg2: '#18202a', line: '#2a3542', ink: '#eef2f6', sub: '#8d99a8', air: '#4cc3e6', roll: '#8d99a8', hot: '#ff9a3c', good: '#5fd39a', bad: '#ff5d5d' };
var SANS = '"Noto Sans SC",sans-serif';
// 深色底 + 极淡网格，替换手绘纸张
paper = function () {
  g.fillStyle = TH.bg; g.fillRect(0, 0, W, H);
  g.strokeStyle = 'rgba(255,255,255,.035)'; g.lineWidth = 1;
  for (var x = 60; x < W; x += 60) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
  for (var y = 60; y < H; y += 60) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
};
PAPER = TH.bg;
function tx(text, x, y, size, col, o) {
  o = o || {}; g.save(); g.font = (o.w || 700) + ' ' + size + 'px ' + SANS; g.fillStyle = col || TH.ink; g.textAlign = o.align || 'left'; g.textBaseline = 'middle';
  if (o.a != null) g.globalAlpha = o.a; g.fillText(text, x, y); var w = g.measureText(text).width; g.restore(); return w;
}
function txW(text, size, w) { g.save(); g.font = (w || 700) + ' ' + size + 'px ' + SANS; var r = g.measureText(text).width; g.restore(); return r; }
// 富文本一行：{h}高亮橙{/} {a}空气蓝{/} {g}绿{/} {r}红{/}
var TCOL = { h: 'hot', a: 'air', g: 'good', r: 'bad', s: 'sub' };
function richLine(text, x, y, size, o) {
  o = o || {}; var parts = [], col = o.col || TH.ink, i = 0, buf = '';
  while (i < text.length) { if (text[i] === '{') { if (buf) parts.push([buf, col]); buf = ''; var j = text.indexOf('}', i), t = text.slice(i + 1, j); col = t === '/' ? (o.col || TH.ink) : TH[TCOL[t]]; i = j + 1; continue; } buf += text[i++]; }
  if (buf) parts.push([buf, col]);
  var tot = parts.reduce(function (s, p) { return s + txW(p[0], size, o.w); }, 0), x0 = o.align === 'center' ? x - tot / 2 : x;
  parts.forEach(function (p) { x0 += tx(p[0], x0, y, size, p[1], { w: o.w, a: o.a }); });
  return tot;
}
var ease = function (k) { k = clamp(k, 0, 1); return 1 - Math.pow(1 - k, 3); };
var k01 = function (t, a, b) { return clamp((t - a) / (b - a), 0, 1); };
// 字幕：白字黑底，按标点折行
function thSub(text, lt, dur) {
  if (lt < 0 || lt > dur) return;
  var a = clamp(lt / .1, 0, 1) * clamp((dur - lt) / .1, 0, 1), size = 58, plain = text.replace(/\{[^}]*\}/g, ''), lines = [text];
  if (txW(plain, size) > 900) {
    var cut = -1, best = 1e9;
    for (var i = 0; i < text.length - 1; i++) if ('，、；：？！'.indexOf(text[i]) >= 0) { var d = Math.abs(text.slice(0, i).replace(/\{[^}]*\}/g, '').length - plain.length / 2); if (d < best) { best = d; cut = i + 1; } }
    if (cut < 0) cut = Math.ceil(text.length / 2);
    lines = [text.slice(0, cut), text.slice(cut)];
  }
  g.save(); g.globalAlpha = a;
  lines.forEach(function (l, i) {
    var y = 1330 + (i - (lines.length - 1) / 2) * 84, w = txW(l.replace(/\{[^}]*\}/g, ''), size) + 56;
    g.fillStyle = 'rgba(0,0,0,.55)'; g.beginPath(); g.roundRect(CX - 30 - w / 2, y - 42, w, 84, 14); g.fill();
    richLine(l, CX - 30, y + 2, size, { align: 'center' });
  });
  g.restore();
}
// 顶部：左上小头像 + 系列名，话题标题
function thHead(series, title, t) {
  var im = IMG.front || IMG.happy;
  g.save(); g.beginPath(); g.arc(110, 200, 46, 0, 6.283); g.fillStyle = '#f3ead6'; g.fill(); g.clip();
  if (im) { var s = 120 / Math.min(im.width, im.height); g.drawImage(im, 110 - im.width * s / 2, 194 - im.height * s / 2, im.width * s, im.height * s); }
  g.restore(); g.strokeStyle = TH.hot; g.lineWidth = 4; g.beginPath(); g.arc(110, 200, 46, 0, 6.283); g.stroke();
  tx(series, 172, 200, 34, TH.sub, { w: 400 });
  if (title) { var a = k01(t, title.t, title.t + .3); richLine(title.text, 70, 310, 72, { a: a }); g.save(); g.globalAlpha = a; g.fillStyle = TH.hot; g.fillRect(72, 360, 90 * ease(k01(t, title.t + .1, title.t + .5)), 8); g.restore(); }
}
function thFoot(text, a) { tx(text, 70, 1215, 26, TH.sub, { w: 400, a: a }); }
// 线段/箭头
function seg(x1, y1, x2, y2, col, lw) { g.save(); g.strokeStyle = col; g.lineWidth = lw || 4; g.lineCap = 'round'; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.restore(); }
function arrowTo(x1, y1, x2, y2, col, lw, k) {
  k = k == null ? 1 : k; if (k <= 0) return; var x = x1 + (x2 - x1) * k, y = y1 + (y2 - y1) * k, an = Math.atan2(y2 - y1, x2 - x1), hs = (lw || 4) * 3.5;
  seg(x1, y1, x, y, col, lw); g.save(); g.fillStyle = col; g.beginPath(); g.moveTo(x, y); g.lineTo(x - Math.cos(an - .45) * hs, y - Math.sin(an - .45) * hs); g.lineTo(x - Math.cos(an + .45) * hs, y - Math.sin(an + .45) * hs); g.closePath(); g.fill(); g.restore();
}
function card(x, y, w, h, a, col) { if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = TH.bg2; g.strokeStyle = col || TH.line; g.lineWidth = 3; g.beginPath(); g.roundRect(x, y, w, h, 22); g.fill(); g.stroke(); g.restore(); }

/* thRun({ src, seed, series, title:{text,t}, lines, scenes:[[t0,t1,fn(lt,t)]], cues:[[名,秒,参数]], wind:fn(t)->0~1, cover }) */
function thRun(o) {
  var T = [0], S = [];
  o.scenes.forEach(function (sc) {
    S.push(function (lt, t) {
      g.save(); sc[2](lt, t); g.restore();
      thHead(o.series, o.title, t);
      o.lines.forEach(function (l) { thSub(l[2], t - l[0], l[1] - l[0]); });
    });
    T.push(sc[1]);
  });
  function sound(K, c, DUR) {
    // 低调的氛围铺底：Am F C G 长和弦
    var CH = [[220, 261.63, 329.63], [174.61, 220, 261.63], [196, 261.63, 329.63], [196, 246.94, 293.66]];
    for (var t = 0, i = 0; t < DUR; t += 4, i++) CH[i % 4].forEach(function (f, j) { K.tone(f, t, 4.6, .022 - j * .004, 'sine', K.music, 1.2); K.tone(f / 2, t, 4.4, .012, 'triangle', K.music, 1.0); });
    for (t = 0; t < DUR - 1; t += .5) K.tone(1760, t, .05, .004, 'sine', K.music);
    var mg = K.music.gain; mg.setValueAtTime(.9, 0); mg.setValueAtTime(.9, DUR - 1.5); mg.linearRampToValueAtTime(0, DUR);
    if (o.wind) K.wind(DUR, o.wind);
    var X = { tick: function (t) { K.tone(1500, t, .05, .02); }, pop: function (t) { K.tone(660, t, .1, .035); K.tone(990, t + .04, .12, .025); },
      ding: function (t) { K.tone(1318.5, t, .7, .045); }, whoosh: K.whoosh, rise: function (t, d) { K.riser(t, t + (d || .8), .02); },
      hit: function (t) { K.tone(110, t, .5, .12, 'sine'); K.noise(t, .3, .08, 'lowpass', 600); } };
    (o.cues || []).forEach(function (q) { if (q[1] < DUR - .2 && X[q[0]]) X[q[0]](q[1], q[2]); });
  }
  licaiRun({ T: T, S: S, seed: o.seed || 950, allText: o.src.replace(/[\x00-\x7f]/g, '') + '–～°≈×→↓↑“”！？²³½ρ·', audio: sound,
    cover: o.cover, encode: { b: '6M', maxrate: '9M', bufsize: '18M' } });
}
