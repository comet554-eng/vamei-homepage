/* 李财竖版短视频（1080×1920，先出画面、后期配音）
 * 依赖 snowkit.js、licai-assets.js、licai-emo.js、licaikit.js、licai-move.js；在 licaikit 之后加载
 * 版式：顶部固定话题标题 / 中间画面区 / 下方大字幕（= 配音稿，一行一句）
 * 抖音等平台右侧和底部有按钮和文案，重要内容放在 x 60~940、y 230~1450
 */
W = 1080; H = 1920; CX = W / 2;
var SUB_Y = 1330;
// 字幕：一句一条，按逗号自动折成两行；{r}红{/} 等颜色标记照用
function subLine(text, lt, dur) {
  if (lt < 0 || lt > dur) return;
  var a = clamp(lt / .12, 0, 1) * clamp((dur - lt) / .12, 0, 1), size = 66;
  var plainT = text.replace(/\{[^}]*\}/g, ''), lines = [text];
  if (textW(plainT, size) > 880) {
    var cut = -1, best = 1e9;
    for (var i = 0; i < text.length; i++) if ('，、；：？！'.indexOf(text[i]) >= 0 && i < text.length - 1) { var d = Math.abs(text.slice(0, i).replace(/\{[^}]*\}/g, '').length - plainT.length / 2); if (d < best) { best = d; cut = i + 1; } }
    if (cut < 0) cut = Math.ceil(text.length / 2);
    lines = [text.slice(0, cut), text.slice(cut)];
    var open = (lines[0].match(/\{([a-z])\}(?![^{]*\{\/\})/) || [])[1]; if (open) { lines[0] += '{/}'; lines[1] = '{' + open + '}' + lines[1]; }
  }
  g.save(); g.globalAlpha = a;
  lines.forEach(function (l, i) {
    var y = SUB_Y + (i - (lines.length - 1) / 2) * 92, w = textW(l.replace(/\{[^}]*\}/g, ''), size) + 60;
    g.fillStyle = 'rgba(255,253,246,.92)'; g.beginPath(); g.roundRect(CX - 30 - w / 2, y - 50, w, 100, 22); g.fill();
    typeText(l, CX - 30, y, size, 99, { cps: 999, align: 'center' });
  });
  g.restore();
}
// 顶部话题标题（盖章式出现后一直留着）
function topTitle(text, lt, small, ts) {
  // 小标题：大标题出现前先大字挂在上面当钩子，之后缩成一行小字
  if (small) { var m = eout(clamp((lt + .05) / .25, 0, 1)), sz = 96 - 50 * m; txt(small, CX - 30, 300 - 90 * m, sz, m < .5 ? C.ink : C.sub, { align: 'center', a: clamp(ts / .2, 0, 1) }); }
  if (lt < 0) return;
  var s = lt < .18 ? 1.6 - .6 * eout(lt / .18) : 1, size = 92, w = textW(text.replace(/\{[^}]*\}/g, ''), size);
  g.save(); g.translate(CX - 30, 300); g.scale(s, s); g.globalAlpha = clamp(lt / .1, 0, 1);
  typeText(text, 0, 0, size, 99, { cps: 999, align: 'center' });
  g.restore();
  hline(CX - 30 - w / 2, 362, CX - 30 + w / 2, 358, 77, C.red, 10, (lt - .15) / .3);
}
// 屏幕抖动（撞击时）
function shake(t, t0, amp) { var k = t - t0; if (k < 0 || k > .35) return; var d = amp * (1 - k / .35); g.translate(Math.sin(k * 90) * d, Math.cos(k * 77) * d); }
// “砰！”爆炸字
function bang(text, x, y, lt, size) {
  if (lt < 0 || lt > 1.4) return;
  var s = lt < .12 ? .4 + 1.0 * eout(lt / .12) : 1.4 - .4 * eout(Math.min(1, (lt - .12) / .2)), a = clamp((1.4 - lt) / .3, 0, 1);
  g.save(); g.translate(x, y); g.rotate(-.12); g.scale(s, s); g.globalAlpha = a;
  g.fillStyle = C.gold; g.beginPath();
  for (var i = 0; i < 24; i++) { var r = i % 2 ? size * .75 : size * 1.25, an = i / 24 * 6.283; g.lineTo(Math.cos(an) * r * 1.3, Math.sin(an) * r); }
  g.closePath(); g.fill(); g.strokeStyle = C.ink; g.lineWidth = 5; g.stroke();
  txt(text, 0, 4, size, C.red, { align: 'center' });
  g.restore();
}

/* shortRun({ src, seed, title:{text, t, small}, lines:[[开始秒, 结束秒, 字幕]], scenes:[[开始秒, 结束秒, fn(lt, t)]], cues:[[音效, 秒]], cover }) */
function shortRun(o) {
  var T = [0], S = [];
  o.scenes.forEach(function (sc) {
    S.push(function (lt, t) {
      g.save(); sc[2](lt, t); g.restore();
      if (o.title) topTitle(o.title.text, t - o.title.t, o.title.small, t);
      o.lines.forEach(function (l) { subLine(l[2], t - l[0], l[1] - l[0]); });
    });
    T.push(sc[1]);
  });
  function sound(K, c, DUR, TT) {
    var X = licaiSound(K, DUR), mg = K.music.gain;
    // 背景乐压低，给后期配音留位置
    mg.cancelScheduledValues(0); mg.setValueAtTime(o.music == null ? .32 : o.music, 0); mg.setValueAtTime(o.music == null ? .32 : o.music, DUR - 1.5); mg.linearRampToValueAtTime(0, DUR);
    (o.cues || []).forEach(function (q) { if (q[1] < DUR - .2) { if (X[q[0]]) X[q[0]](q[1]); else if (K[q[0]]) K[q[0]](q[1], q[2]); } });
  }
  licaiRun({ T: T, S: S, seed: o.seed || 900, allText: o.src.replace(/[\x00-\x7f]/g, '') + '–～°≈×→↓↑“”！？', audio: sound,
    cover: o.cover, encode: { b: '6M', maxrate: '9M', bufsize: '18M' } });
}
