/*
 * trailkit.js —《徒步不难》系列公用画面（在 snowkit.js 之后加载，复用它的字幕、转场、配乐与导出框架）
 * 普通脚本：函数都是全局的。侧面视角里人默认朝右走，"上坡"指地面往右升高。
 */
var TP = {
  skyTop: '#6ec3f4', skyBot: '#fff3d6', duskTop: '#3d3f7e', duskMid: '#f0875a', duskBot: '#ffcf8f',
  far: '#a9cfe3', mid: '#8cc7a6', near: '#69b083', grass: '#7cc576', grass2: '#58a861', soil: '#d8b07a', soil2: '#b98a55',
  jacket: '#ff7a3d', jacket2: '#e0602a', pants: '#3a5568', pants2: '#2b4050', pack: '#2f80ed', pack2: '#1f62c4',
  hat: '#ffc23d', skin: '#ffd6b3', boot: '#6b4a32', blush: '#ff9a8b',
  leaf: ['#5db36b', '#7cc576', '#4a9e5c'], pine: ['#3f8f63', '#4fa673'], trunk: '#9a6b45',
  flower: ['#ff6b8b', '#ffd166', '#ffffff', '#b48cff'], card: '#ffffff'
};
function mixHex(a, b, k) {
  var pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  var r = Math.round(lerp(pa >> 16, pb >> 16, k)), gg = Math.round(lerp((pa >> 8) & 255, (pb >> 8) & 255, k)), bb = Math.round(lerp(pa & 255, pb & 255, k));
  return 'rgb(' + r + ',' + gg + ',' + bb + ')';
}

/* ───────── 天空、太阳、云、鸟 ───────── */
// dusk：0 白天 → 1 傍晚
function hikeSky(dusk) {
  dusk = dusk || 0;
  var gr = g.createLinearGradient(0, 0, 0, H);
  gr.addColorStop(0, mixHex(TP.skyTop, TP.duskTop, dusk));
  gr.addColorStop(.5, mixHex('#bfe6fb', TP.duskMid, dusk));
  gr.addColorStop(1, mixHex(TP.skyBot, TP.duskBot, dusk));
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
}
function hikeSun(x, y, r, t, dusk) {
  dusk = dusk || 0;
  glow(x, y, r * 3.2, dusk > .5 ? '255,140,80' : '255,220,120', .55);
  g.save(); g.translate(x, y); g.rotate((t || 0) * .25);
  g.strokeStyle = dusk > .5 ? 'rgba(255,170,90,.6)' : 'rgba(255,214,102,.7)'; g.lineWidth = r * .14; g.lineCap = 'round';
  for (var i = 0; i < 12; i++) { var a = i * Math.PI / 6, l0 = r * 1.3, l1 = r * (1.6 + .15 * Math.sin((t || 0) * 3 + i)); g.beginPath(); g.moveTo(Math.cos(a) * l0, Math.sin(a) * l0); g.lineTo(Math.cos(a) * l1, Math.sin(a) * l1); g.stroke(); }
  g.restore();
  g.fillStyle = mixHex('#ffd84d', '#ff8a4c', dusk); g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
}
function cloud(x, y, s, a) {
  g.save(); g.globalAlpha = a == null ? .95 : a; g.translate(x, y); g.scale(s, s);
  g.fillStyle = 'rgba(120,160,200,.18)'; g.beginPath(); g.ellipse(0, 34, 120, 18, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fff';
  [[-70, 10, 42], [-20, -12, 58], [40, -2, 50], [85, 16, 36], [0, 18, 48]].forEach(function (c) { g.beginPath(); g.arc(c[0], c[1], c[2], 0, Math.PI * 2); g.fill(); });
  g.fillRect(-95, 10, 200, 38);
  g.restore();
}
function hikeClouds(t, a, yMax) {
  yMax = yMax || .3;
  for (var i = 0; i < 5; i++) {
    var sp = 14 + hash(i + 2) * 22, x = ((hash(i) * (W + 500) + t * sp) % (W + 500)) - 250, y = H * (.06 + hash(i + 5) * yMax);
    cloud(x, y, .55 + hash(i + 8) * .5, a);
  }
}
function birds(t, a, n, y0) {
  a = a == null ? 1 : a; n = n || 4; y0 = y0 == null ? H * .2 : y0;
  g.save(); g.globalAlpha = a; g.strokeStyle = '#3d4b5c'; g.lineWidth = 4; g.lineCap = 'round'; g.lineJoin = 'round';
  for (var i = 0; i < n; i++) {
    var x = ((hash(i + 30) * W + t * (70 + hash(i) * 40)) % (W + 200)) - 100, y = y0 + hash(i + 40) * 160 + Math.sin(t * 1.3 + i) * 14;
    var f = Math.sin(t * 9 + i * 2) * 10, s = 14 + hash(i + 9) * 8;
    g.beginPath(); g.moveTo(x - s, y - f); g.quadraticCurveTo(x - s * .4, y - f * .3 - 4, x, y); g.quadraticCurveTo(x + s * .4, y - f * .3 - 4, x + s, y - f); g.stroke();
  }
  g.restore();
}
// 远山层：camX 越大，画面越往右走
function hikeRidges(camX, dusk, base) {
  dusk = dusk || 0; base = base == null ? H * .52 : base;
  function ridge(b, amp, seed, col, sp) {
    g.fillStyle = col; g.beginPath(); g.moveTo(-10, H);
    for (var x = -10; x <= W + 10; x += 20) {
      var xx = x + camX * sp;
      g.lineTo(x, b - amp * (.6 * Math.abs(Math.sin(xx * .0028 + seed)) + .3 * Math.abs(Math.sin(xx * .0071 + seed * 2)) + .1 * Math.sin(xx * .021 + seed * 3)));
    }
    g.lineTo(W + 10, H); g.closePath(); g.fill();
  }
  ridge(base, 330, 1.7, mixHex(TP.far, '#8a7fb0', dusk), .06);
  ridge(base + 90, 220, 4.4, mixHex(TP.mid, '#7a8f8e', dusk), .14);
}

/* ───────── 地面与植物 ───────── */
function roundTree(x, y, s, t, c) {
  var sway = Math.sin((t || 0) * 1.6 + x * .01) * 3 * s;
  g.fillStyle = TP.trunk; rrect(x - 7 * s, y - 60 * s, 14 * s, 62 * s, 5 * s); g.fill();
  var cols = c || TP.leaf;
  [[0, -105, 46, 0], [-30, -78, 34, 1], [30, -80, 36, 2], [0, -70, 38, 1]].forEach(function (b) {
    g.fillStyle = cols[b[3] % cols.length]; g.beginPath(); g.arc(x + b[0] * s + sway, y + b[1] * s, b[2] * s, 0, Math.PI * 2); g.fill();
  });
  g.fillStyle = 'rgba(255,255,255,.18)'; g.beginPath(); g.arc(x - 14 * s + sway, y - 120 * s, 16 * s, 0, Math.PI * 2); g.fill();
}
function pineTree(x, y, s, t) {
  var sway = Math.sin((t || 0) * 1.4 + x * .013) * 2 * s;
  g.fillStyle = TP.trunk; g.fillRect(x - 6 * s, y - 26 * s, 12 * s, 28 * s);
  for (var j = 0; j < 3; j++) {
    var w = (46 - j * 11) * s, yy = y - 20 * s - j * 34 * s;
    g.fillStyle = TP.pine[j % 2]; g.beginPath(); g.moveTo(x + sway * (j + 1) * .5, yy - 62 * s); g.lineTo(x - w, yy); g.lineTo(x + w, yy); g.closePath(); g.fill();
  }
}
function flowerAt(x, y, s, c, t) {
  var sw = Math.sin((t || 0) * 2.2 + x) * 3 * s;
  g.strokeStyle = TP.grass2; g.lineWidth = 3 * s; g.beginPath(); g.moveTo(x, y); g.lineTo(x + sw, y - 22 * s); g.stroke();
  g.fillStyle = c; for (var i = 0; i < 5; i++) { var a = i * Math.PI * 2 / 5; g.beginPath(); g.arc(x + sw + Math.cos(a) * 6 * s, y - 22 * s + Math.sin(a) * 6 * s, 5 * s, 0, Math.PI * 2); g.fill(); }
  g.fillStyle = '#ffb703'; g.beginPath(); g.arc(x + sw, y - 22 * s, 4 * s, 0, Math.PI * 2); g.fill();
}
function tuft(x, y, s) {
  g.strokeStyle = TP.grass2; g.lineWidth = 4 * s; g.lineCap = 'round';
  [-8, 0, 8].forEach(function (d, i) { g.beginPath(); g.moveTo(x + d * s, y); g.lineTo(x + d * 1.8 * s, y - (16 + i % 2 * 8) * s); g.stroke(); });
}
// 地面：hy(xw) 返回世界坐标 xw 处的屏幕 y；画面 x = xw - camX
function hikeGround(hy, camX, t, o) {
  o = o || {};
  var dusk = o.dusk || 0, X0 = o.x0 == null ? -10 : o.x0, X1 = o.x1 == null ? W + 10 : o.x1, YB = o.yb == null ? H + 10 : o.yb;
  g.save();
  var gr = g.createLinearGradient(0, H * .4, 0, H);
  gr.addColorStop(0, mixHex(TP.grass, '#6a8f6a', dusk)); gr.addColorStop(1, mixHex(TP.grass2, '#4b6b55', dusk));
  g.fillStyle = gr; g.beginPath(); g.moveTo(X0, YB);
  for (var x = X0; x <= X1; x += 8) g.lineTo(x, hy(x + camX));
  g.lineTo(X1, YB); g.closePath(); g.fill();
  // 树（在路后面）
  if (!o.noTrees) {
    var sp = o.treeGap || 260;
    for (var k = Math.floor((camX + X0 - 200) / sp); k <= (camX + X1 + 200) / sp; k++) {
      var xw = k * sp + hash(k + 3) * sp * .6, xs = xw - camX;
      if (hash(k + 11) < (o.treeDensity == null ? .55 : o.treeDensity)) {
        var sc = .8 + hash(k + 7) * .5;
        if (hash(k + 1) < .5) roundTree(xs, hy(xw) + 6, sc, t); else pineTree(xs, hy(xw) + 6, sc, t);
      }
    }
  }
  // 小路
  g.strokeStyle = mixHex(TP.soil, '#a8875f', dusk); g.lineWidth = 18; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); for (x = X0; x <= X1; x += 8) { var y = hy(x + camX) + 14; x > X0 ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
  g.strokeStyle = 'rgba(150,105,60,.35)'; g.lineWidth = 3;
  for (k = Math.floor(camX / 70); k <= (camX + W) / 70; k++) { var px = k * 70 + hash(k) * 30 - camX; g.beginPath(); g.moveTo(px, hy(px + camX) + 12); g.lineTo(px + 12, hy(px + camX) + 13); g.stroke(); }
  // 花和草
  if (!o.noFlowers) {
    for (k = Math.floor(camX / 90); k <= (camX + W) / 90; k++) {
      var fx = k * 90 + hash(k + 50) * 60 - camX, fy = hy(fx + camX) + 40 + hash(k + 60) * 70;
      if (hash(k + 70) < .45) flowerAt(fx, fy, .9 + hash(k) * .4, TP.flower[k % 4 < 0 ? 0 : k % 4], t); else tuft(fx, fy, 1);
    }
  }
  g.restore();
}
function slopeAt(hy, xw) { return Math.atan2(-(hy(xw + 6) - hy(xw - 6)), 12) / D2R; }

/* ───────── 背包小人（侧面） ───────── */
// o: s 缩放, ph 步伐相位, walk 步幅 0~1, slope 脚下坡度（度，正为上坡）, dir 朝向, tired 0~1, t 时间, jacket/pack/hat 颜色, wave 挥手, pole 登山杖, lamp 头灯
function drawHiker(x, y, o) {
  o = o || {};
  var s = o.s || 1, ph = o.ph || 0, walk = o.walk == null ? 1 : o.walk, sl = (o.slope || 0) * D2R, dir = o.dir || 1, tired = o.tired || 0, t = o.t || 0;
  var L1 = 46, L2 = 46, tn = Math.tan(sl);
  var legs = [0, 1].map(function (i) {
    var p = ph + i * Math.PI, th = walk * .42 * Math.sin(p) + .04, bend = walk * (.06 + .85 * Math.pow(Math.max(0, Math.cos(p)), 2)) + .03;
    var kx = Math.sin(th) * L1, ky = Math.cos(th) * L1, fx = kx + Math.sin(th - bend) * L2, fy = ky + Math.cos(th - bend) * L2;
    return { p: p, k: [kx, ky], f: [fx, fy] };
  });
  var hipY = Math.min.apply(null, legs.map(function (l) { return -l.f[0] * tn - l.f[1]; }));
  var lean = .1 + sl * .55 + tired * .22, Hp = [0, hipY];
  var Sh = [Hp[0] + Math.sin(lean) * 56, Hp[1] - Math.cos(lean) * 56];
  var Hd = [Sh[0] + Math.sin(lean) * 26 + 4, Sh[1] - Math.cos(lean) * 26];
  g.save(); g.translate(x, y); g.scale(dir * s, s); g.lineCap = 'round'; g.lineJoin = 'round';
  // 影子
  g.fillStyle = 'rgba(30,50,40,.18)'; g.beginPath(); g.ellipse(0, 4, 42, 8, -sl, 0, Math.PI * 2); g.fill();
  function leg(l, back) {
    g.strokeStyle = back ? TP.pants2 : TP.pants; g.lineWidth = 17;
    g.beginPath(); g.moveTo(Hp[0], Hp[1]); g.lineTo(Hp[0] + l.k[0], Hp[1] + l.k[1]); g.lineTo(Hp[0] + l.f[0], Hp[1] + l.f[1]); g.stroke();
    var fx = Hp[0] + l.f[0], fy = Hp[1] + l.f[1];
    g.save(); g.translate(fx, fy); g.rotate(-sl); g.fillStyle = back ? '#523826' : TP.boot; rrect(-10, -9, 28, 14, 6); g.fill(); g.restore();
  }
  function arm(i, back) {
    var sw = -walk * .55 * Math.sin(ph + i * Math.PI), a1 = sw + .05;
    if (o.wave && !back) a1 = Math.PI - .5 + Math.sin(t * 9) * .3;
    var E = [Sh[0] + Math.sin(a1) * 30, Sh[1] + Math.cos(a1) * 30], fa = a1 + (o.wave && !back ? .6 : .55);
    var Hn = [E[0] + Math.sin(fa) * 26, E[1] + Math.cos(fa) * 26];
    g.strokeStyle = back ? TP.jacket2 : TP.jacket; g.lineWidth = 13;
    g.beginPath(); g.moveTo(Sh[0], Sh[1]); g.lineTo(E[0], E[1]); g.lineTo(Hn[0], Hn[1]); g.stroke();
    if (o.pole && !o.wave) {
      var px = Hn[0] + 26 + sw * 10; g.strokeStyle = '#7d8ea3'; g.lineWidth = 4;
      g.beginPath(); g.moveTo(Hn[0], Hn[1] - 8); g.lineTo(px, -px * tn); g.stroke();
    }
    g.fillStyle = TP.skin; g.beginPath(); g.arc(Hn[0], Hn[1], 7, 0, Math.PI * 2); g.fill();
  }
  arm(1, true);
  leg(legs[1], true);
  // 背包
  g.save(); g.translate((Hp[0] + Sh[0]) / 2 - Math.cos(lean) * 22, (Hp[1] + Sh[1]) / 2 - Math.sin(lean) * 22 - 4); g.rotate(lean);
  g.fillStyle = o.pack || TP.pack; rrect(-17, -32, 34, 58, 12); g.fill();
  g.fillStyle = TP.pack2; rrect(-17, 4, 34, 18, 7); g.fill();
  g.fillStyle = '#ffd166'; rrect(-6, -40, 18, 12, 5); g.fill();
  g.restore();
  // 身体
  g.strokeStyle = o.jacket || TP.jacket; g.lineWidth = 32; g.beginPath(); g.moveTo(Hp[0], Hp[1] - 6); g.lineTo(Sh[0], Sh[1] + 6); g.stroke();
  g.strokeStyle = TP.pack2; g.lineWidth = 5; g.beginPath(); g.moveTo(Sh[0] - 6, Sh[1]); g.lineTo(Hp[0] + 2, Hp[1] - 12); g.stroke();
  leg(legs[0], false);
  // 头
  g.fillStyle = TP.skin; g.beginPath(); g.arc(Hd[0], Hd[1], 18, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#1b2838'; g.beginPath(); g.arc(Hd[0] + 9, Hd[1] - 1, 2.6, 0, Math.PI * 2); g.fill();
  g.fillStyle = TP.blush; g.globalAlpha = .7; g.beginPath(); g.arc(Hd[0] + 6, Hd[1] + 7, 4, 0, Math.PI * 2); g.fill(); g.globalAlpha = 1;
  g.strokeStyle = '#1b2838'; g.lineWidth = 2.4;
  if (tired > .5) { g.beginPath(); g.arc(Hd[0] + 12, Hd[1] + 8, 3, 0, Math.PI * 2); g.stroke(); }
  else { g.beginPath(); g.arc(Hd[0] + 9, Hd[1] + 6, 5, .2, 1.6); g.stroke(); }
  g.fillStyle = o.hat || TP.hat; g.beginPath(); g.ellipse(Hd[0] + 2, Hd[1] - 10, 27, 6, lean * .6, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.arc(Hd[0], Hd[1] - 11, 16, Math.PI, 0); g.fill();
  if (o.lamp) {
    g.fillStyle = '#fff6b0'; g.beginPath(); g.arc(Hd[0] + 15, Hd[1] - 8, 5, 0, Math.PI * 2); g.fill();
    g.save(); g.globalAlpha = o.lamp * .5; var lg = g.createLinearGradient(Hd[0], 0, Hd[0] + 300, 0); lg.addColorStop(0, 'rgba(255,246,176,.9)'); lg.addColorStop(1, 'rgba(255,246,176,0)');
    g.fillStyle = lg; g.beginPath(); g.moveTo(Hd[0] + 15, Hd[1] - 8); g.lineTo(Hd[0] + 300, Hd[1] + 90); g.lineTo(Hd[0] + 300, Hd[1] - 60); g.closePath(); g.fill(); g.restore();
  }
  arm(0, false);
  // 汗
  if (tired > .3) {
    g.fillStyle = '#6ec3f4';
    for (var i = 0; i < 3; i++) { var ph2 = (t * 1.4 + i / 3) % 1, dx = Hd[0] - 22 - i * 6, dy = Hd[1] - 6 + ph2 * 40; g.globalAlpha = (tired - .3) / .7 * (1 - ph2); g.beginPath(); g.moveTo(dx, dy - 9); g.quadraticCurveTo(dx + 6, dy, dx, dy + 4); g.quadraticCurveTo(dx - 6, dy, dx, dy - 9); g.fill(); }
    g.globalAlpha = 1;
  }
  g.restore();
  return { head: [x + dir * s * Hd[0], y + s * Hd[1]], hip: [x + dir * s * Hp[0], y + s * Hp[1]] };
}
// 在地形上走：返回小人的头部位置
function hikerOn(hy, xw, camX, o) {
  o = Object.assign({}, o || {}); o.slope = (o.dir || 1) * slopeAt(hy, xw);
  return drawHiker(xw - camX, hy(xw) + 12, o);
}

/* ───────── 图表与卡片 ───────── */
// 字幕底板：地面上的小字说明加一块半透明白底
function subPanel(a) { g.save(); g.globalAlpha = a == null ? 1 : a; g.fillStyle = 'rgba(255,255,255,.82)'; rrect(W * .06, H * .7, W * .88, H * .09, 34); g.fill(); g.restore(); }
function card(x, y, w, h, r, a) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.fillStyle = TP.card; g.shadowColor = 'rgba(27,40,56,.14)'; g.shadowBlur = 40; g.shadowOffsetY = 10;
  rrect(x, y, w, h, r || 36); g.fill(); g.restore();
}
// 海拔剖面：fn(k) 返回 0~1 的相对高度
function profile(fn, x, y, w, h, o) {
  o = o || {};
  var col = o.color || COL.green, N = 120, pts = [];
  for (var i = 0; i <= N; i++) { var k = i / N; pts.push([x + k * w, y + h - fn(k) * h]); }
  g.save();
  var gr = g.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, o.fill || 'rgba(18,166,121,.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.beginPath(); g.moveTo(x, y + h); pts.forEach(function (p) { g.lineTo(p[0], p[1]); }); g.lineTo(x + w, y + h); g.closePath(); g.fill();
  g.strokeStyle = col; g.lineWidth = o.lw || 7; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); pts.forEach(function (p, i) { i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]); }); g.stroke();
  // 上坡段加亮
  if (o.ups) {
    g.strokeStyle = o.upColor || COL.amber; g.lineWidth = (o.lw || 7) + 5;
    o.ups.forEach(function (u) { if (u[2] != null && u[2] <= 0) return; var k1 = lerp(u[0], u[1], u[2] == null ? 1 : u[2]); g.beginPath(); for (var j = 0; j <= 30; j++) { var kk = lerp(u[0], k1, j / 30); var px = x + kk * w, py = y + h - fn(kk) * h; j ? g.lineTo(px, py) : g.moveTo(px, py); } g.stroke(); });
  }
  if (o.base !== false) { g.strokeStyle = 'rgba(27,40,56,.18)'; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y + h); g.lineTo(x + w, y + h); g.stroke(); }
  if (o.prog != null) {
    var k2 = clamp(o.prog, 0, 1), px = x + k2 * w, py = y + h - fn(k2) * h;
    g.fillStyle = TP.jacket; g.strokeStyle = '#fff'; g.lineWidth = 5; g.beginPath(); g.arc(px, py, 16, 0, Math.PI * 2); g.fill(); g.stroke();
  }
  g.restore();
  return function (k) { return [x + k * w, y + h - fn(k) * h]; };
}
function signpost(x, y, lines, s, a) {
  s = s || 1; g.save(); g.globalAlpha = a == null ? 1 : a; g.translate(x, y); g.scale(s, s);
  g.fillStyle = '#8b5e3c'; g.fillRect(-9, -230, 18, 230);
  g.fillStyle = '#c98b55'; g.beginPath(); g.moveTo(-120, -220); g.lineTo(120, -220); g.lineTo(150, -180); g.lineTo(120, -140); g.lineTo(-120, -140); g.closePath(); g.fill();
  g.strokeStyle = '#8b5e3c'; g.lineWidth = 5; g.stroke();
  label(lines[0], 8, -180, 40, '#fff', 900);
  if (lines[1]) { g.fillStyle = '#c98b55'; rrect(-90, -126, 180, 62, 10); g.fill(); g.strokeStyle = '#8b5e3c'; g.stroke(); label(lines[1], 0, -95, 34, '#fff', 900); }
  g.restore();
}
// 小时钟
function clockIcon(x, y, r, hrs, a) {
  g.save(); g.globalAlpha = a == null ? 1 : a; g.fillStyle = '#fff'; g.strokeStyle = COL.ink; g.lineWidth = r * .12; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.stroke();
  var ah = (hrs / 12) * Math.PI * 2 - Math.PI / 2, am = (hrs % 1) * Math.PI * 2 - Math.PI / 2;
  g.lineCap = 'round'; g.lineWidth = r * .12; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ah) * r * .5, y + Math.sin(ah) * r * .5); g.stroke();
  g.strokeStyle = COL.red; g.lineWidth = r * .08; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(am) * r * .75, y + Math.sin(am) * r * .75); g.stroke();
  g.restore();
}
function sunIcon(x, y, r, a) { g.save(); g.globalAlpha = a == null ? 1 : a; g.strokeStyle = '#ffb703'; g.lineWidth = r * .18; g.lineCap = 'round'; for (var i = 0; i < 8; i++) { var an = i * Math.PI / 4; g.beginPath(); g.moveTo(x + Math.cos(an) * r * 1.3, y + Math.sin(an) * r * 1.3); g.lineTo(x + Math.cos(an) * r * 1.7, y + Math.sin(an) * r * 1.7); g.stroke(); } g.fillStyle = '#ffd166'; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.restore(); }
function moonIcon(x, y, r, a) { g.save(); g.globalAlpha = a == null ? 1 : a; glow(x, y, r * 2.4, '255,243,196', .35); g.fillStyle = '#fff3c4'; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.fillStyle = 'rgba(200,190,150,.45)'; [[-.3, -.2, .2], [.25, .2, .15], [.1, -.35, .1]].forEach(function (c) { g.beginPath(); g.arc(x + c[0] * r, y + c[1] * r, c[2] * r, 0, Math.PI * 2); g.fill(); }); g.restore(); }
