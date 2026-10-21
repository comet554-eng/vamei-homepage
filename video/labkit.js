/* 李财骑行实验室：按“页面配置”生成整集（画面 + 音效）
 * 页面类型：open 开场 / bars 横向柱状图 / list 编号清单 / draw 自定义 / end 实验结论 / next 下集预告
 *          step 教程步骤 / tools 工具清单 / mistakes 常见错误（第三季教程用）
 * 依赖 snowkit.js、licai-assets.js、licai-emo.js、licaikit.js
 */
var LAB = '李财骑行实验室';
function plain(t) { return t.replace(/\{[^}]*\}/g, ''); }
function noteDraw(lt, n) {
  if (lt < n.t) return;
  if (n.box) { var w = textW(plain(n.text), n.size || 44) + 50, a = clamp((lt - n.t) / .3, 0, 1); g.save(); g.globalAlpha = a * .55; g.fillStyle = '#F8DE7E'; g.fillRect(n.x - 20, n.y - (n.size || 44) * .75, w, (n.size || 44) * 1.5); g.restore(); }
  if (n.plain) txt(n.text, n.x, n.y, n.size || 34, n.col || C.sub, { font: BODY, a: clamp((lt - n.t) / .3, 0, 1), align: n.align });
  else typeText(n.text, n.x, n.y, n.size || 48, lt - n.t, { cps: 12, color: n.col, align: n.align });
  if (n.arrow) harrow(n.arrow[0], n.arrow[1], n.arrow[2], n.arrow[3], n.arrow[4], n.arrow[5], n.acol || C.red, (lt - n.t - .2) / .4);
  if (n.circle) hcircle(n.circle[0], n.circle[1], n.circle[2], n.circle[3], 3000 + n.circle[0], C.red, 4, (lt - n.t) / .4);
}
function emoDraw(lt, e) { if (e) cat(e.n, e.x, e.y, e.h, lt - (e.t == null ? 4 : e.t), { bob: e.bob }); }

var PAGE = {
  open: function (o) { return { draw: function (lt) { openScene(lt, o.emo, o.l1, o.l2, o.ep, o.series || LAB); }, cues: [['pop', .15], ['ticks', .7, plain(o.l1).length, 10], ['ticks', 1.4, plain(o.l2).length, 8], ['pen', 2.0], ['ding', 2.4]] }; },
  bars: function (o) {
    var n = o.rows.length, dy = o.dy || Math.min(130, 560 / Math.max(1, n - 1 || 1)), y0 = o.y0 || 320, X0 = o.x0 || 560;
    var mx = o.max || Math.max.apply(null, o.rows.map(function (r) { return r.r ? r.r[1] : r.v; })), PX = (o.wmax || 880) / mx;
    var unit = o.unit || '', dp = o.dp || 0;
    var draw = function (lt) {
      header(lt, o.title, o.sub, o.col || C.blue);
      hline(X0, y0 - 60, X0, y0 + dy * (n - 1) + 60, 3101, C.ink, 3.5, (lt - .6) / .4);
      o.rows.forEach(function (r, i) {
        var y = y0 + i * dy, a = clamp((lt - .5 - i * .12) / .3, 0, 1); if (a <= 0) return;
        var lx = 110;
        if (r.ic) { g.save(); g.globalAlpha = a; bikeType(150, y - 6, .3, r.ic, 0, r.c); g.restore(); lx = 240; }
        txt(r.l, lx, r.s ? y - 14 : y, o.lsize || 42, r.hl ? C.red : C.ink, { a: a });
        if (r.s) txt(r.s, lx + 2, y + 24, 26, C.sub, { font: BODY, a: a });
        var k = eout((lt - 1.2 - i * (o.gap || .4)) / .8); if (k <= 0) return;
        var x1 = r.r ? X0 + r.r[0] * PX : X0, w = (r.r ? r.r[1] - r.r[0] : r.v) * PX * k;
        if (r.r) { g.save(); g.setLineDash([6, 8]); g.strokeStyle = C.faint; g.lineWidth = 2.5; g.beginPath(); g.moveTo(X0, y); g.lineTo(x1, y); g.stroke(); g.restore(); }
        hatchBar(x1, y - (o.bh || 30), w, (o.bh || 30) * 2, r.c || C.blue, 3110 + i * 7);
        var lab = r.txt ? r.txt : r.r ? (r.r[0] + '–' + r.r[1] + unit) : ((o.approx === false ? '' : '≈') + (r.v * k).toFixed(dp) + unit);
        if (k > .9 || !r.r) txt(lab, x1 + w + 18, y, o.vsize || 42, C.ink);
      });
      if (o.crown != null) { var cr = o.rows[o.crown], cv = cr.r ? cr.r[1] : cr.v; crown(X0 + cv * PX + 60, y0 + o.crown * dy - 46, .9, clamp((lt - 1.2 - n * (o.gap || .4) - .4) / .3, 0, 1)); }
      (o.notes || []).forEach(function (nt) { noteDraw(lt, nt); });
      emoDraw(lt, o.emo);
      if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1));
      if (o.extra) o.extra(lt);
    };
    var cues = o.rows.map(function (r, i) { return ['grow', 1.2 + i * (o.gap || .4)]; });
    if (o.crown != null) cues.push(['ding', 1.2 + n * (o.gap || .4) + .4]);
    return { draw: draw, cues: cues.concat(noteCues(o.notes)).concat(o.emo ? [['pop', o.emo.t == null ? 4 : o.emo.t]] : []) };
  },
  list: function (o) {
    return { draw: function (lt) { listPage(lt, o.title, o.sub || '', o.items, o.col || C.green, o.emo, o.opt || {}); (o.notes || []).forEach(function (nt) { noteDraw(lt, nt); }); if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1)); },
      cues: [['pop', .6]].concat(o.items.reduce(function (a, it, i) { var g0 = (o.opt && o.opt.gap) || 1.8; return a.concat([['pop', .8 + i * g0], ['ticks', 1.0 + i * g0, Math.min(12, plain(it[0]).length), 12]]); }, [])).concat(noteCues(o.notes)) };
  },
  draw: function (o) {
    return { draw: function (lt) { header(lt, o.title, o.sub, o.col || C.purple); o.fn(lt); (o.notes || []).forEach(function (nt) { noteDraw(lt, nt); }); emoDraw(lt, o.emo); if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1)); },
      cues: (o.cues || []).concat(noteCues(o.notes)).concat(o.emo ? [['pop', o.emo.t == null ? 4 : o.emo.t]] : []) };
  },
  end: function (o) {
    return { draw: function (lt) {
      header(lt, o.title || '实验结论', o.sub || '', C.green);
      o.items.forEach(function (t, i) { var y = 340 + i * 150, ct = lt - .8 - i * 1.4; if (ct < 0) return; numDot(i + 1, 170, y, ct, C.green); typeText(t, 250, y, 50, ct - .2, { cps: 14 }); });
      stamp(o.stampText || '实验结论', 1560, 900, 60, lt - (.8 + o.items.length * 1.4 + .4), -.1);
      cat(o.emo || '坏笑得意', 1600, 560, 420, lt - .6);
    }, cues: [['pop', .6]].concat(o.items.reduce(function (a, t, i) { return a.concat([['pop', .8 + i * 1.4], ['ticks', 1.0 + i * 1.4, Math.min(14, plain(t).length), 14]]); }, [])).concat([['stamp', .8 + o.items.length * 1.4 + .4]]) };
  },
  // 教程步骤：上方口诀进度条，左边示意图 fn，右边要点 lines，右下角李财
  step: function (o) {
    var keys = o.keys || [], lines = o.lines || [];
    return { draw: function (lt) {
      header(lt, '第 ' + o.n + ' 步：' + o.title, o.sub, o.col || C.orange);
      keys.forEach(function (k, i) {
        var x = 120 + i * 92, on = i + 1 === o.n, done = i + 1 < o.n, a = clamp((lt - .3 - i * .05) / .3, 0, 1);
        g.save(); g.globalAlpha = a; g.fillStyle = on ? (o.col || C.orange) : done ? C.green : C.cream;
        g.beginPath(); g.arc(x, 280, on ? 36 : 30, 0, 6.283); g.fill(); g.restore();
        txt(k, x, 283, on ? 40 : 32, on || done ? '#fff' : C.sub, { align: 'center', a: a });
      });
      o.fn(lt);
      lines.forEach(function (l, i) {
        var t = l.t == null ? 1.2 + i * 1.6 : l.t, ct = lt - t; if (ct < 0) return;
        var y = 400 + i * 120;
        numDot(i + 1, 1100, y, ct, o.col || C.orange);
        typeText(l.text, 1160, y - 4, l.size || 44, ct - .1, { cps: 14 });
        if (l.small) txt(l.small, 1162, y + 46, 30, C.sub, { font: BODY, a: clamp((ct - .8) / .3, 0, 1) });
      });
      (o.notes || []).forEach(function (nt) { noteDraw(lt, nt); });
      emoDraw(lt, o.emo);
      if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1));
    }, cues: (o.cues || []).concat(lines.map(function (l, i) { return ['ticks', (l.t == null ? 1.2 + i * 1.6 : l.t), Math.min(12, plain(l.text).length), 14]; })).concat(noteCues(o.notes)).concat(o.emo ? [['pop', o.emo.t == null ? 4 : o.emo.t]] : []) };
  },
  // 工具清单：items = [[名字, 小字, 画图函数(x, y, lt)], ...]，横排卡片
  tools: function (o) {
    var n = o.items.length, cw = Math.min(400, 1500 / n);
    return { draw: function (lt) {
      header(lt, o.title, o.sub, o.col || C.blue);
      o.items.forEach(function (it, i) {
        var ct = lt - .8 - i * 1.2; if (ct < 0) return;
        var x = 120 + i * cw + cw / 2, k = pop(ct);
        hrect(x - cw / 2 + 20, 320, cw - 40, 520, 4100 + i, C.ink, 3.5, clamp(ct / .4, 0, 1));
        g.save(); g.translate(x, 540); g.scale(k, k); it[2](0, 0, ct); g.restore();
        txt(it[0], x, 760, 46, C.ink, { align: 'center', a: clamp((ct - .2) / .3, 0, 1) });
        if (it[1]) txt(it[1], x, 812, 28, C.sub, { align: 'center', font: BODY, a: clamp((ct - .4) / .3, 0, 1) });
      });
      (o.notes || []).forEach(function (nt) { noteDraw(lt, nt); });
      emoDraw(lt, o.emo);
      if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1));
    }, cues: [['pop', .6]].concat(o.items.map(function (it, i) { return ['pop', .8 + i * 1.2]; })).concat(noteCues(o.notes)).concat(o.emo ? [['pop', o.emo.t == null ? 4 : o.emo.t]] : []) };
  },
  mistakes: function (o) {
    return { draw: function (lt) { mistakesPage(lt, o.title, o.items, o.emo, o.seed); if (o.foot) footnote(o.foot, clamp((lt - 1) / .3, 0, 1)); },
      cues: [['pop', .6]].concat(o.items.reduce(function (a, it, i) { return a.concat([['ticks', 1.0 + i * 2.2, Math.min(12, plain(it[0]).length), 12], ['wrong', 2.0 + i * 2.2], ['ding', 2.3 + i * 2.2]]); }, [])) };
  },
  next: function (o) {
    return { draw: function (lt) { nextScene(lt, o.emo, o.l1, o.l2, o.bk, o.bc); }, cues: [['ticks', .4, plain(o.l1).length, 10], ['ticks', 1.0, plain(o.l2).length, 10], ['bell', 1.4], ['stamp', 2.4], ['confetti', 2.0]] };
  }
};
function noteCues(notes) { return (notes || []).map(function (n) { return n.plain ? ['pop', n.t] : ['ticks', n.t, Math.min(16, plain(n.text).length), 12]; }); }

function labRun(o) {
  var T = [0], S = [], CUE = [];
  o.pages.forEach(function (p) {
    var pg = PAGE[p.type](Object.assign({ ep: o.ep, series: o.series }, p)), t0 = T[T.length - 1];
    S.push(pg.draw); pg.cues.forEach(function (c) { CUE.push([c[0], t0 + c[1]].concat(c.slice(2))); });
    T.push(t0 + p.dur);
  });
  function sound(K, c, DUR, TT) {
    var X = licaiSound(K, DUR);
    for (var i = 1; i < TT.length - 1; i++) { X.whoosh(TT[i] - .08); X.ticks(TT[i], 8); }
    CUE.forEach(function (q) {
      var t = q[1]; if (t >= DUR - .2) return;
      if (q[0] === 'ticks') X.ticks(t, q[2], q[3]);
      else if (q[0] === 'confetti') { for (var j = 0; j < 6; j++) K.noise(t + j * .08, .1, .04, 'highpass', 5000); }
      else X[q[0]](t);
    });
    if (o.sound) o.sound(K, X, TT);
  }
  licaiRun({ T: T, S: S, seed: 600 + o.ep, allText: o.src.replace(/[\x00-\x7f]/g, '') + '–～°≈×→↓↑∝²³½“”！', audio: sound, cover: function (key, w, h) { epCover(key, w, h, Object.assign({ series: o.series || LAB, ep: o.ep }, o.cover)); }, encode: { b: '4M', maxrate: '6M', bufsize: '12M' } });
}
