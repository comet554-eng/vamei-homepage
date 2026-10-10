/*
 * snowkit.js —《滑雪不难》系列公用工具（EP.02 起使用）
 * 普通脚本（非模块）：这里声明的函数与 var 都是全局的，各集页面直接使用。
 * 一集页面需要提供：T（场景起点）、S（场景函数）、TX（字幕）、音频与封面，然后调用 kitRun(...)。
 */
var FPS = 30, W = 1080, H = 1920, CX = W / 2;
var cv, ctx, buf, bctx, g;
var SANS = '"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif';
var D2R = Math.PI / 180;
var COL = {
  ink: '#1b2838', sub: '#56677a', faint: 'rgba(27,40,56,.45)',
  red: '#f0473c', green: '#12a679', amber: '#ff9f1c', blue: '#2f80ed',
  jacket: '#ff7a3d', jacket2: '#d9602b', pants: '#26405e', pants2: '#1a2a3d',
  board: '#6a5cff', boardTop: '#8d84ff', boardDark: '#4b3fd1', boot: '#33475e'
};
var TAGC = { r: COL.red, g: COL.green, a: COL.amber };

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function lerp(a, b, k) { return a + (b - a) * k; }
function sm(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
function eout(x) { x = clamp(x, 0, 1); return 1 - (1 - x) * (1 - x); }
function ein(x) { x = clamp(x, 0, 1); return x * x; }
function hash(i) { var s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
function win(t, a, b, fi, fo) { fi = fi == null ? .3 : fi; fo = fo == null ? .3 : fo; return t < a || t > b ? 0 : Math.min(1, (t - a) / fi, (b - t) / fo); }
function pop(lt) { return lt < 0 ? 0 : lt < .18 ? eout(lt / .18) * 1.15 : 1 + .15 * Math.max(0, 1 - (lt - .18) / .15); }
function mid(a, b) { return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]; }
function frameOf(th) { var r = th * D2R; return { d: [Math.cos(r), Math.sin(r)], n: [Math.sin(r), -Math.cos(r)] }; }
function dirOf(fr, deg) { var r = deg * D2R, c = Math.cos(r), s = Math.sin(r); return [fr.n[0] * c + fr.d[0] * s, fr.n[1] * c + fr.d[1] * s]; }

/* ───────── 字幕 ───────── */
function parseRich(line, base) {
  var out = [], col = base, hl = false;
  for (var i = 0; i < line.length;) {
    if (line[i] === '{') { var j = line.indexOf('}', i), tag = line.slice(i + 1, j); if (tag === '/') { col = base; hl = false; } else { col = TAGC[tag] || base; hl = true; } i = j + 1; continue; }
    var ch = String.fromCodePoint(line.codePointAt(i)); out.push([ch, col, hl]); i += ch.length;
  }
  return out;
}
function drawCaption(b, t) {
  var lt = t - b.in; if (lt < 0 || t > b.out + .3) return;
  var outK = t > b.out ? 1 - (t - b.out) / .3 : 1;
  var size = b.size, lh = size * 1.32, ls = size * .04, st = b.st || (b.sub || b.note ? .02 : .045);
  g.font = b.w + ' ' + size + 'px ' + SANS; g.textAlign = 'center'; g.textBaseline = 'middle';
  var base = b.note ? COL.faint : b.sub ? COL.sub : COL.ink;
  var lines = b.text.split('\n'), y0 = b.y * H - (lines.length - 1) * lh / 2, k = 0;
  lines.forEach(function (line, li) {
    var chars = parseRich(line, base), ws = chars.map(function (c) { return g.measureText(c[0]).width; });
    var total = ws.reduce(function (s, v) { return s + v + ls; }, 0) - ls, x = W / 2 - total / 2;
    chars.forEach(function (c, ci) {
      var ct = lt - (k++) * st, cx = x + ws[ci] / 2; x += ws[ci] + ls;
      if (ct < 0) return;
      var e = eout(ct / .35), a = e * outK; if (a < .01) return;
      var y = y0 + li * lh + (1 - e) * size * .35;
      if (c[2]) { g.fillStyle = c[1]; g.globalAlpha = a * .16; g.fillRect(cx - ws[ci] / 2 - ls / 2 - .5, y + size * .02, ws[ci] + ls + 1, size * .42); }
      g.globalAlpha = a; g.fillStyle = c[1]; g.fillText(c[0], cx, y);
    });
  });
  g.globalAlpha = 1;
}

/* ───────── 小部件 ───────── */
function rrect(x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function label(text, x, y, size, color, w, align) { g.font = (w || 700) + ' ' + size + 'px ' + SANS; g.textAlign = align || 'center'; g.textBaseline = 'middle'; g.fillStyle = color; g.fillText(text, x, y); }
function pill(text, x, y, size, bg, fg, a) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.font = '700 ' + size + 'px ' + SANS; g.textAlign = 'center'; g.textBaseline = 'middle';
  var w = g.measureText(text).width + size * 1.4, h = size * 1.8;
  g.fillStyle = bg; rrect(x - w / 2, y - h / 2, w, h, h / 2); g.fill();
  g.fillStyle = fg; g.fillText(text, x, y + 1); g.restore();
  return w;
}
function arrow(x1, y1, x2, y2, color, w, hs) {
  w = w || 6; hs = hs || 22;
  g.strokeStyle = color; g.fillStyle = color; g.lineWidth = w; g.lineCap = 'round';
  var ang = Math.atan2(y2 - y1, x2 - x1);
  g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2 - Math.cos(ang) * hs * .6, y2 - Math.sin(ang) * hs * .6); g.stroke();
  g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - Math.cos(ang - .45) * hs, y2 - Math.sin(ang - .45) * hs); g.lineTo(x2 - Math.cos(ang + .45) * hs, y2 - Math.sin(ang + .45) * hs); g.closePath(); g.fill();
}
// 圆弧箭头：圆心 (cx,cy)，半径 r，从角 a0 到 a1（弧度，canvas 方向）
function arcArrow(cx, cy, r, a0, a1, color, w, hs) {
  w = w || 7; hs = hs || 24;
  g.strokeStyle = color; g.fillStyle = color; g.lineWidth = w; g.lineCap = 'round';
  var ccw = a1 < a0; g.beginPath(); g.arc(cx, cy, r, a0, a1 + (ccw ? .12 : -.12), ccw); g.stroke();
  var ex = cx + Math.cos(a1) * r, ey = cy + Math.sin(a1) * r, ta = a1 + (ccw ? -Math.PI / 2 : Math.PI / 2);
  g.beginPath(); g.moveTo(ex + Math.cos(ta) * hs * .5, ey + Math.sin(ta) * hs * .5);
  g.lineTo(ex - Math.cos(ta) * hs * .5 + Math.cos(ta + Math.PI / 2) * hs * .55, ey - Math.sin(ta) * hs * .5 + Math.sin(ta + Math.PI / 2) * hs * .55);
  g.lineTo(ex - Math.cos(ta) * hs * .5 - Math.cos(ta + Math.PI / 2) * hs * .55, ey - Math.sin(ta) * hs * .5 - Math.sin(ta + Math.PI / 2) * hs * .55);
  g.closePath(); g.fill();
}
function markX(x, y, s, a) { g.save(); g.globalAlpha = a == null ? 1 : a; g.fillStyle = COL.red; g.beginPath(); g.arc(x, y, s, 0, Math.PI * 2); g.fill(); g.strokeStyle = '#fff'; g.lineWidth = s * .22; g.lineCap = 'round'; var k = s * .42; g.beginPath(); g.moveTo(x - k, y - k); g.lineTo(x + k, y + k); g.moveTo(x + k, y - k); g.lineTo(x - k, y + k); g.stroke(); g.restore(); }
function markV(x, y, s, a, sc) { g.save(); g.globalAlpha = a == null ? 1 : a; g.translate(x, y); g.scale(sc || 1, sc || 1); g.fillStyle = COL.green; g.beginPath(); g.arc(0, 0, s, 0, Math.PI * 2); g.fill(); g.strokeStyle = '#fff'; g.lineWidth = s * .22; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(-s * .45, 0); g.lineTo(-s * .1, s * .35); g.lineTo(s * .5, -s * .35); g.stroke(); g.restore(); }
function ring(x, y, r, color, a, dashed) { g.save(); g.globalAlpha = a == null ? 1 : a; g.strokeStyle = color; g.lineWidth = 6; if (dashed) g.setLineDash([10, 8]); g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke(); g.restore(); }
function glow(x, y, r, rgb, a) { g.save(); g.globalAlpha = a; var gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(' + rgb + ',.85)'); gr.addColorStop(1, 'rgba(' + rgb + ',0)'); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.restore(); }
// 一排步骤标签：当前步高亮，已完成的打勾
function stepChips(items, y, cur, a, size) {
  size = size || 34; g.save(); g.globalAlpha = a == null ? 1 : a; g.font = '700 ' + size + 'px ' + SANS;
  var gap = 18, ws = items.map(function (t) { return g.measureText(t).width + size * 1.3; });
  var total = ws.reduce(function (s, v) { return s + v; }, 0) + gap * (items.length - 1), x = W / 2 - total / 2;
  items.forEach(function (t, i) {
    var w = ws[i], h = size * 1.8, done = i < cur, now = i === cur;
    g.fillStyle = now ? COL.amber : done ? '#dcf5ec' : 'rgba(255,255,255,.85)'; rrect(x, y - h / 2, w, h, h / 2); g.fill();
    if (!now && !done) { g.strokeStyle = '#d3dee8'; g.lineWidth = 3; g.stroke(); }
    label(t, x + w / 2, y + 1, size, now ? '#fff' : done ? COL.green : COL.sub, 700);
    x += w + gap;
  });
  g.restore();
}

/* ───────── 雪景 ───────── */
function drawSky(shift, tint) {
  shift = shift || 0;
  var gr = g.createLinearGradient(0, 0, 0, H);
  gr.addColorStop(0, '#cfe1f0'); gr.addColorStop(.55, '#eef4f9'); gr.addColorStop(1, '#f8fbfd');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  function ridge(base, amp, seed, colr, sp) {
    g.fillStyle = colr; g.beginPath(); g.moveTo(-10, H);
    for (var x = -10; x <= W + 10; x += 30) {
      var xx = x + shift * sp;
      g.lineTo(x, base - amp * (.55 * Math.abs(Math.sin(xx * .0031 + seed)) + .3 * Math.abs(Math.sin(xx * .0077 + seed * 2)) + .15 * Math.sin(xx * .019 + seed * 3)));
    }
    g.lineTo(W + 10, H); g.closePath(); g.fill();
  }
  ridge(H * .5, Math.min(300, H * .16), 1.3, '#dbe7f1', .02);
  ridge(H * .56, Math.min(220, H * .12), 4.1, '#e6eef5', .05);
  if (tint) { g.fillStyle = tint; g.fillRect(0, 0, W, H); }
}
function drawSnowfall(t, a, n) {
  a = a == null ? 1 : a; n = n || 70;
  g.save(); g.fillStyle = '#ffffff';
  for (var i = 0; i < n; i++) {
    var r = 3 + hash(i) * 5, sp = 60 + hash(i + 50) * 90;
    var x = ((hash(i + 9) * W + Math.sin(t * .7 + i) * 30 - t * 25) % W + W) % W;
    var y = ((hash(i + 3) * H + t * sp) % (H * .7));
    g.globalAlpha = a * (.5 + hash(i + 7) * .5); g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }
  g.restore();
}
function drawSlope(F, th, scroll, o) {
  scroll = scroll || 0; o = o || {};
  var fr = frameOf(th), Lg = 3600;
  var p1 = [F[0] - fr.d[0] * Lg, F[1] - fr.d[1] * Lg], p2 = [F[0] + fr.d[0] * Lg, F[1] + fr.d[1] * Lg];
  var gr = g.createLinearGradient(F[0], F[1], F[0] - fr.n[0] * 900, F[1] - fr.n[1] * 900);
  gr.addColorStop(0, '#ffffff'); gr.addColorStop(1, '#dde8f2');
  g.fillStyle = gr; g.beginPath(); g.moveTo(p1[0], p1[1]); g.lineTo(p2[0], p2[1]); g.lineTo(p2[0], p2[1] + 4000); g.lineTo(p1[0], p1[1] + 4000); g.closePath(); g.fill();
  g.strokeStyle = '#c3d4e4'; g.lineWidth = 4; g.beginPath(); g.moveTo(p1[0], p1[1]); g.lineTo(p2[0], p2[1]); g.stroke();
  g.strokeStyle = '#d6e2ed'; g.lineWidth = 4; g.lineCap = 'round';
  var sp = 150, off = ((scroll % sp) + sp) % sp;
  for (var k = -16; k <= 16; k++) {
    var s = k * sp - off, dep = 26 + (Math.abs(k) % 3) * 18;
    var a = [F[0] + fr.d[0] * s - fr.n[0] * dep, F[1] + fr.d[1] * s - fr.n[1] * dep];
    g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(a[0] + fr.d[0] * 34, a[1] + fr.d[1] * 34); g.stroke();
  }
  if (!o.noProps) {
    var tsp = 1100, toff = ((scroll % tsp) + tsp) % tsp;
    for (k = -3; k <= 3; k++) {
      s = k * tsp - toff + 420; var b = [F[0] + fr.d[0] * s, F[1] + fr.d[1] * s];
      g.fillStyle = '#a9c0d1';
      for (var j = 0; j < 3; j++) { var w = 70 - j * 16, y = b[1] - 40 - j * 52; g.beginPath(); g.moveTo(b[0], y - 80); g.lineTo(b[0] - w, y); g.lineTo(b[0] + w, y); g.closePath(); g.fill(); }
      g.fillStyle = '#8aa1b3'; g.fillRect(b[0] - 9, b[1] - 42, 18, 42);
    }
    var psp = 520, poff = ((scroll % psp) + psp) % psp;
    for (k = -6; k <= 6; k++) {
      s = k * psp - poff + 130; b = [F[0] + fr.d[0] * s, F[1] + fr.d[1] * s];
      g.strokeStyle = COL.amber; g.lineWidth = 9; g.beginPath(); g.moveTo(b[0], b[1]); g.lineTo(b[0], b[1] - 110); g.stroke();
    }
  }
}
function speedLines(F, th, t, speed, a) {
  a = a == null ? 1 : a; if (speed < .05) return;
  var fr = frameOf(th);
  g.save(); g.strokeStyle = '#9fb6ca'; g.lineCap = 'round';
  for (var i = 0; i < 16; i++) {
    var h = 60 + hash(i) * 560, period = 2600;
    var s = (((hash(i + 20) * period - t * 1700 * (.6 + hash(i + 5) * .8)) % period) + period) % period - period / 2;
    var len = 80 + speed * 160, p = [F[0] + fr.d[0] * s + fr.n[0] * h, F[1] + fr.d[1] * s + fr.n[1] * h];
    g.globalAlpha = a * speed * .55; g.lineWidth = 5;
    g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(p[0] + fr.d[0] * len, p[1] + fr.d[1] * len); g.stroke();
  }
  g.restore();
}
function burst(cx, cy, lt, n, spd) {
  n = n || 46; spd = spd || 1; if (lt < 0 || lt > 1.6) return;
  g.save();
  for (var i = 0; i < n; i++) {
    var a = -Math.PI * (.1 + hash(i) * .8), v = (300 + hash(i + 4) * 700) * spd;
    var x = cx + Math.cos(a) * v * lt, y = cy + Math.sin(a) * v * lt + 900 * lt * lt;
    g.globalAlpha = Math.max(0, 1 - lt / 1.6) * .95; g.fillStyle = '#ffffff'; g.strokeStyle = '#c8d7e5'; g.lineWidth = 2;
    var r = 6 + hash(i + 9) * 14; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.stroke();
  }
  g.restore();
}
function makeScroll(vfn, t0, t1) { var st = 1 / 240, arr = [0], s = 0; for (var t = t0; t < t1; t += st) { s += vfn(t) * st; arr.push(s); } return function (t) { return arr[clamp(Math.floor((t - t0) / st), 0, arr.length - 1)]; }; }

/* ───────── 声音工具 ───────── */
function audioKit(c, seed) {
  var SR = c.sampleRate, s0 = seed || 7, K = {};
  K.ar = function () { s0 = (s0 * 16807) % 2147483647; return s0 / 2147483647; };
  K.out = c.createGain(); K.out.gain.value = .55;
  var comp = c.createDynamicsCompressor(); comp.threshold.value = -16; comp.ratio.value = 3.5;
  K.out.connect(comp); comp.connect(c.destination);
  var ir = c.createBuffer(2, SR * 2.2 | 0, SR);
  for (var ch = 0; ch < 2; ch++) { var d = ir.getChannelData(ch); for (var i = 0; i < d.length; i++) d[i] = (K.ar() * 2 - 1) * Math.pow(1 - i / d.length, 3); }
  var conv = c.createConvolver(); conv.buffer = ir; K.rv = c.createGain(); K.rv.gain.value = .35; K.rv.connect(conv); conv.connect(K.out);
  K.nb = c.createBuffer(1, SR * 2, SR); var nd = K.nb.getChannelData(0); for (i = 0; i < nd.length; i++) nd[i] = K.ar() * 2 - 1;
  K.music = c.createGain(); K.music.connect(K.out); K.music.connect(K.rv);
  K.noise = function (t0, dur, vol, type, freq, dest, q) {
    var s = c.createBufferSource(); s.buffer = K.nb; var f = c.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q || .8;
    var gg = c.createGain(); gg.gain.setValueAtTime(vol, t0); gg.gain.exponentialRampToValueAtTime(.0008, t0 + dur);
    s.connect(f); f.connect(gg); gg.connect(dest || K.out); s.start(t0, K.ar() * 1.5); s.stop(t0 + dur + .05);
  };
  K.tone = function (f, t0, dur, vol, type, dest, att) {
    var o = c.createOscillator(), gg = c.createGain(); o.type = type || 'sine'; o.frequency.value = f;
    gg.gain.setValueAtTime(0, t0); gg.gain.linearRampToValueAtTime(vol, t0 + (att || .01)); gg.gain.exponentialRampToValueAtTime(.0001, t0 + dur);
    o.connect(gg); gg.connect(dest || K.out); o.start(t0); o.stop(t0 + dur + .05);
  };
  K.kick = function (t0, v) { v = v || 1; var o = c.createOscillator(), gg = c.createGain(); o.frequency.setValueAtTime(130, t0); o.frequency.exponentialRampToValueAtTime(42, t0 + .16); gg.gain.setValueAtTime(.8 * v, t0); gg.gain.exponentialRampToValueAtTime(.001, t0 + .28); o.connect(gg); gg.connect(K.music); o.start(t0); o.stop(t0 + .3); };
  K.hat = function (t0, v) { K.noise(t0, .045, .09 * (v || 1), 'highpass', 7000, K.music); };
  K.clap = function (t0, v) { v = v || 1; K.noise(t0, .14, .22 * v, 'bandpass', 1500, K.music, 1.2); K.noise(t0 + .012, .12, .14 * v, 'bandpass', 1300, K.music, 1.2); };
  K.thud = function (t0, v) { v = v || 1; K.noise(t0, .9, .9 * v, 'lowpass', 900); var o = c.createOscillator(), gg = c.createGain(); o.frequency.setValueAtTime(120, t0); o.frequency.exponentialRampToValueAtTime(38, t0 + .2); gg.gain.setValueAtTime(1.1 * v, t0); gg.gain.exponentialRampToValueAtTime(.001, t0 + .35); o.connect(gg); gg.connect(K.out); o.start(t0); o.stop(t0 + .4); K.noise(t0 + .05, 1.2, .3 * v, 'bandpass', 2500); };
  K.wrong = function (t0) { K.tone(160, t0, .16, .12, 'square'); K.tone(150, t0 + .17, .22, .12, 'square'); };
  K.ding = function (t0) { K.tone(1318.5, t0, .9, .1); K.tone(1975.5, t0 + .08, 1.0, .07); };
  K.tick = function (t0) { K.tone(1250, t0, .08, .03); };
  K.whoosh = function (t0) {
    var s = c.createBufferSource(); s.buffer = K.nb; var f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 1.5;
    f.frequency.setValueAtTime(500, t0); f.frequency.exponentialRampToValueAtTime(3500, t0 + .35);
    var gg = c.createGain(); gg.gain.setValueAtTime(.0001, t0); gg.gain.exponentialRampToValueAtTime(.16, t0 + .15); gg.gain.exponentialRampToValueAtTime(.0005, t0 + .4);
    s.connect(f); f.connect(gg); gg.connect(K.out); s.start(t0, K.ar()); s.stop(t0 + .45);
  };
  K.riser = function (t0, t1, vol) {
    var s = c.createBufferSource(); s.buffer = K.nb; s.loop = true; var f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 2;
    f.frequency.setValueAtTime(400, t0); f.frequency.exponentialRampToValueAtTime(6000, t1 - .05);
    var gg = c.createGain(); gg.gain.setValueAtTime(.0001, t0); gg.gain.exponentialRampToValueAtTime(vol, t1 - .1); gg.gain.linearRampToValueAtTime(0, t1);
    s.connect(f); f.connect(gg); gg.connect(K.out); s.start(t0); s.stop(t1 + .05);
  };
  // 风声：level(t) 返回 0~1
  K.wind = function (dur, level) {
    var w = c.createBufferSource(); w.buffer = K.nb; w.loop = true; var f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = .6;
    var gg = c.createGain(); gg.gain.value = 0; w.connect(f); f.connect(gg); gg.connect(K.out); w.start(0);
    for (var i = 0; i <= dur * 20; i++) { var t = i / 20, v = level(t); gg.gain.linearRampToValueAtTime(v * .5, t); f.frequency.linearRampToValueAtTime(300 + v * 1400, t); }
  };
  // 系列统一的背景音乐：C G Am F，100 BPM；section(t) 返回 verse / tense / build / chorus / outro
  K.bed = function (start, end, section) {
    var beat = .6, bar = 2.4, CH = [[130.81, 164.81, 196, 261.63], [98, 146.83, 196, 246.94], [110, 164.81, 220, 261.63], [87.31, 130.81, 174.61, 220]];
    for (var t = start, i = 0; t < end - .5; t += bar, i++) {
      var chd = CH[i % 4], sec = section(t);
      chd.forEach(function (f) {
        [-4, 4].forEach(function (det) {
          var o = c.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f; o.detune.value = det;
          var lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = sec === 'chorus' ? 1500 : 900;
          var gg = c.createGain(); gg.gain.setValueAtTime(0, t); gg.gain.linearRampToValueAtTime(.038, t + .35); gg.gain.setValueAtTime(.038, t + bar - .3); gg.gain.linearRampToValueAtTime(0, t + bar + .2);
          o.connect(lp); lp.connect(gg); gg.connect(K.music); o.start(t); o.stop(t + bar + .3);
        });
      });
      for (var b = 0; b < 4; b += 2) K.tone(chd[0] / 2, t + b * beat, beat * 1.8, .22, 'triangle', K.music, .02);
      for (b = 0; b < 4; b++) {
        var bt = t + b * beat;
        if (sec === 'verse') { if (b % 2 === 0) K.kick(bt, .8); K.hat(bt + beat / 2, .7); }
        if (sec === 'tense') { K.kick(bt, .9); K.hat(bt + beat / 2); }
        if (sec === 'build') { K.kick(bt, .8); K.hat(bt + beat / 2); K.hat(bt + beat / 4, .6); K.hat(bt + beat * .75, .6); }
        if (sec === 'chorus' || sec === 'outro') { if (!(sec === 'outro' && bt > end - 6)) K.kick(bt, sec === 'outro' ? .6 : .9); K.hat(bt + beat / 2); if (b % 2 === 1 && sec === 'chorus') K.clap(bt, .8); }
        if (sec === 'chorus' || sec === 'outro' || sec === 'verse') {
          var arp = [chd[1] * 2, chd[2] * 2, chd[3] * 2, chd[2] * 2], vol = sec === 'verse' ? .035 : .055;
          K.tone(arp[b % 4], bt, .35, vol, 'triangle', K.music, .005);
          if (sec !== 'verse') K.tone(arp[(b + 2) % 4], bt + beat / 2, .3, vol * .8, 'triangle', K.music, .005);
        }
      }
    }
    CH[0].forEach(function (f) { K.tone(f * 2, end - 3.2, 3.2, .04, 'triangle'); });
    K.noise(start, 1.8, .35, 'highpass', 4500); K.kick(start, 1.2);
    var mg = K.music.gain; mg.setValueAtTime(0, 0); mg.setValueAtTime(0, start - .1); mg.linearRampToValueAtTime(1, start + .05); mg.setValueAtTime(1, end - 3); mg.linearRampToValueAtTime(0, end);
  };
  return K;
}
function wavBase64(b) {
  var ch = b.numberOfChannels, len = b.length, sr = b.sampleRate, bytes = 44 + len * ch * 2;
  var ab = new ArrayBuffer(bytes), v = new DataView(ab);
  function str(o, s) { for (var i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); }
  str(0, 'RIFF'); v.setUint32(4, bytes - 8, true); str(8, 'WAVE'); str(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true);
  v.setUint16(22, ch, true); v.setUint32(24, sr, true); v.setUint32(28, sr * ch * 2, true); v.setUint16(32, ch * 2, true); v.setUint16(34, 16, true);
  str(36, 'data'); v.setUint32(40, len * ch * 2, true);
  var data = []; for (var i = 0; i < ch; i++) data.push(b.getChannelData(i));
  var o = 44; for (i = 0; i < len; i++) for (var k = 0; k < ch; k++) { v.setInt16(o, clamp(data[k][i], -1, 1) * 32767, true); o += 2; }
  var u8 = new Uint8Array(ab), s = ''; for (i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  return btoa(s);
}

/* ───────── 运行框架：场景 + 推入转场 + 字幕 + 导出接口 ───────── */
var COVER_SIZES = { '9x16': [1080, 1920], '3x4': [1080, 1440], '16x9': [1920, 1080], '4x3': [1440, 1080] };
function coverCanvas(key, draw) {
  var sz = COVER_SIZES[key], saved = [W, H, CX];
  W = sz[0]; H = sz[1]; CX = W / 2;
  var c = document.createElement('canvas'); c.width = W; c.height = H; g = c.getContext('2d');
  draw(key, W, H);
  W = saved[0]; H = saved[1]; CX = saved[2]; g = ctx;
  return c.toDataURL('image/jpeg', .95);
}
function kitRun(opt) {
  var RENDER = /render/.test(location.search);
  if (RENDER) document.body.classList.add('render');
  cv = document.getElementById('c'); ctx = cv.getContext('2d'); g = ctx;
  buf = document.createElement('canvas'); buf.width = W; buf.height = H; bctx = buf.getContext('2d');
  var T = opt.T, S = opt.S, TX = opt.TX, DUR = T[T.length - 1], TR = .4;
  function drawScene(i, t) { g.save(); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.setLineDash([]); S[i](t - T[i], t); g.restore(); }
  function sceneIndex(t) { for (var i = 0; i < S.length; i++) if (t < T[i + 1]) return i; return S.length - 1; }
  function drawFrame(t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    var i = sceneIndex(t), lt = t - T[i];
    if (i > 0 && lt < TR) {
      var k = sm(lt / TR);
      g = ctx; ctx.save(); ctx.translate(-k * W * .35, 0); drawScene(i - 1, t); ctx.restore();
      g = bctx; bctx.setTransform(1, 0, 0, 1, 0, 0); drawScene(i, t);
      g = ctx; ctx.save(); ctx.globalAlpha = k; ctx.drawImage(buf, (1 - k) * W * .5, 0); ctx.restore();
    } else { g = ctx; drawScene(i, t); }
    g = ctx;
    TX.forEach(function (b) { drawCaption(b, t); });
    if (t > DUR - .4) { ctx.globalAlpha = (t - (DUR - .4)) / .4; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
  }
  var weights = [400, 500, 700, 900];
  var all = TX.map(function (b) { return b.text; }).join('') + (opt.allText || '') + '滑雪不难·EP.0123456789单板双板下集评论区说%°?？!！';
  function audio() {
    var c = new OfflineAudioContext(2, Math.ceil(48000 * DUR), 48000), K = audioKit(c, opt.seed);
    TX.forEach(function (b) { if (!b.sub && !b.note && b.in > 0) K.tick(b.in); });
    for (var i = 1; i < T.length - 1; i++) K.whoosh(T[i] - .05);
    opt.audio(K, c, DUR);
    return c.startRendering().then(wavBase64);
  }
  function preview() {
    drawFrame(0);
    ctx.fillStyle = 'rgba(27,40,56,.55)'; ctx.fillRect(0, 0, W, H);
    g = ctx; label('▶  点击播放', CX, H * .5, 56, '#fff', 700);
    var playing = false;
    cv.addEventListener('click', function () {
      if (playing) return; playing = true;
      var ac = new (window.AudioContext || window.webkitAudioContext)();
      audio().then(function (b64) {
        var bin = atob(b64), u8 = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
        return ac.decodeAudioData(u8.buffer);
      }).then(function (ab) {
        var src = ac.createBufferSource(); src.buffer = ab; src.connect(ac.destination);
        var t0 = ac.currentTime + .1; src.start(t0);
        (function loop() { var t = ac.currentTime - t0; if (t >= 0) drawFrame(Math.min(t, DUR - 1 / FPS)); if (t < DUR) requestAnimationFrame(loop); else playing = false; })();
      });
    });
  }
  Promise.race([
    Promise.all(weights.map(function (w) { return document.fonts.load(w + ' 64px "Noto Sans SC"', all); })),
    new Promise(function (r) { setTimeout(r, 20000); })
  ]).then(function () { return document.fonts.ready; }).catch(function () {}).then(function () {
    window.FILM = {
      ready: true, frames: Math.round(DUR * FPS), fps: FPS,
      encode: opt.encode || { b: '4.5M', maxrate: '7M', bufsize: '14M' },
      fontStatus: function () { return weights.map(function (w) { return w + ':' + document.fonts.check(w + ' 64px "Noto Sans SC"', '滑雪单板'); }).join(' '); },
      render: function (i, q) { drawFrame(i / FPS); return cv.toDataURL('image/jpeg', q || .93); },
      cover: function () { return coverCanvas('9x16', opt.cover); },
      covers: function () { var o = {}; Object.keys(COVER_SIZES).forEach(function (k) { o[k] = coverCanvas(k, opt.cover); }); return o; },
      renderAudio: audio,
      debug: opt.debug
    };
    if (!RENDER) preview();
  });
}
