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
  var lean = .1 + sl * .55 + tired * .22 + (o.lean || 0), Hp = [0, hipY];
  var Sh = [Hp[0] + Math.sin(lean) * 56, Hp[1] - Math.cos(lean) * 56];
  var Hd = [Sh[0] + Math.sin(lean) * 26 + 4, Sh[1] - Math.cos(lean) * 26];
  g.save(); g.translate(x, y); g.scale(dir * s, s); g.lineCap = 'round'; g.lineJoin = 'round';
  // 影子
  g.fillStyle = 'rgba(30,50,40,.18)'; g.beginPath(); g.ellipse(0, 4, 42, 8, -sl, 0, Math.PI * 2); g.fill();
  function leg(l, back) {
    g.strokeStyle = back ? TP.pants2 : TP.pants; g.lineWidth = 17;
    g.beginPath(); g.moveTo(Hp[0], Hp[1]); g.lineTo(Hp[0] + l.k[0], Hp[1] + l.k[1]); g.lineTo(Hp[0] + l.f[0], Hp[1] + l.f[1]); g.stroke();
    var fx = Hp[0] + l.f[0], fy = Hp[1] + l.f[1];
    g.save(); g.translate(fx, fy); g.rotate(-sl); g.fillStyle = o.boot ? (back ? mixHex(o.boot, '#000000', .2) : o.boot) : (back ? '#523826' : TP.boot); rrect(-10, -9, 28, 14, 6); g.fill(); g.restore();
  }
  function arm(i, back) {
    var sw = -walk * .55 * Math.sin(ph + i * Math.PI), a1 = sw + .05;
    if (o.wave && !back) a1 = Math.PI - .2 + Math.sin(t * 9) * .3;
    var E = [Sh[0] + Math.sin(a1) * 30, Sh[1] + Math.cos(a1) * 30], fa = a1 + (o.wave && !back ? .6 : .55);
    var Hn = [E[0] + Math.sin(fa) * 26, E[1] + Math.cos(fa) * 26];
    g.strokeStyle = o.jacket ? (back ? mixHex(o.jacket, '#000000', .15) : o.jacket) : (back ? TP.jacket2 : TP.jacket); g.lineWidth = 13 + (o.bulk || 0) * .3;
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
  var ps = o.packScale || 1; g.save(); g.translate((Hp[0] + Sh[0]) / 2 - Math.cos(lean) * (22 + 17 * (ps - 1)), (Hp[1] + Sh[1]) / 2 - Math.sin(lean) * (22 + 17 * (ps - 1)) - 4 - 20 * (ps - 1)); g.rotate(lean); g.scale(ps, ps);
  g.fillStyle = o.pack || TP.pack; rrect(-17, -32, 34, 58, 12); g.fill();
  g.fillStyle = TP.pack2; rrect(-17, 4, 34, 18, 7); g.fill();
  g.fillStyle = '#ffd166'; rrect(-6, -40, 18, 12, 5); g.fill();
  g.restore();
  // 身体
  g.strokeStyle = o.jacket || TP.jacket; g.lineWidth = 32 + (o.bulk || 0); g.beginPath(); g.moveTo(Hp[0], Hp[1] - 6); g.lineTo(Sh[0], Sh[1] + 6); g.stroke();
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
  g.save(); g.globalAlpha *= a == null ? 1 : a; g.fillStyle = TP.card; g.shadowColor = 'rgba(27,40,56,.14)'; g.shadowBlur = 40; g.shadowOffsetY = 10;
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

/* ═════════ 系列模板（EP.02 起使用）═════════ */
TAGC.b = COL.blue;
var HB = { blue: COL.blue, green: COL.green, amber: COL.amber, red: COL.red, ink: COL.ink, sub: COL.sub };
// 卡片类场景的背景：天空 + 云 + 一层白纱
function bgPlain(t, veil) { hikeSky(0); hikeClouds(t, .9, .14); g.fillStyle = 'rgba(255,255,255,' + (veil == null ? .42 : veil) + ')'; g.fillRect(0, 0, W, H); }
// 走路场景：o = { cam 相机速度, hy 地形, hx 小人屏幕 x, dusk, sun:[x,y], hiker:{...}, panel:[a,b], ridges 基线 }
function bgWalk(lt, o) {
  o = o || {};
  var sp = o.cam == null ? 150 : o.cam, cam = lt * sp, dusk = o.dusk || 0;
  var hy = o.hy || function (x) { return H * .64 + 16 * Math.sin(x * .004); };
  hikeSky(dusk);
  if (o.sun !== false) { var su = o.sun || [W * .82, H * .3]; hikeSun(su[0], su[1], 52, lt, dusk); }
  hikeClouds(lt + (o.seed || 0), 1 - dusk * .4, .14);
  if (o.birds) birds(lt, .9, 3, H * .2);
  hikeRidges(cam, dusk, o.ridges == null ? H * .54 : o.ridges);
  hikeGround(hy, cam, lt, { dusk: dusk, treeGap: o.treeGap || 260 });
  var hx = o.hx == null ? W * .36 : o.hx, ho = Object.assign({ s: 1.4, ph: lt * Math.PI * 2 * (o.cad || .9), t: lt, pole: true }, o.hiker || {});
  var J = o.noHiker ? null : hikerOn(hy, hx + cam, cam, ho);
  if (dusk > 0) { g.fillStyle = 'rgba(40,30,90,' + dusk * .25 + ')'; g.fillRect(0, 0, W, H); }
  if (o.panel) subPanel(win(lt, o.panel[0], o.panel[1], .3, .01));
  return { J: J, cam: cam, hy: hy };
}
function titleScene(lt, ep, extra) {
  hikeSky(0); hikeSun(W * .82, H * .5, 56, lt, 0); hikeClouds(lt + 8, 1, .14); birds(lt + 3, 1, 4, H * .44);
  hikeRidges(lt * 120, 0, H * .66);
  var hy = function (x) { return H * .8 + 22 * Math.sin(x * .004); };
  hikeGround(hy, lt * 120, lt, {});
  hikerOn(hy, CX + lt * 120, lt * 120, Object.assign({ s: 1.3, ph: lt * Math.PI * 2 * .85, t: lt, pole: true }, extra || {}));
  pill('徒步不难 · EP.' + ep, CX, H * .19, 40, COL.amber, '#fff', eout(lt / .3));
}
// 一列卡片：items = [[icon(x,y), 标题, 小字, 'v'|'x'|null, 颜色]]
function listCards(items, lt, o) {
  o = o || {};
  var y0 = o.y0 || H * .23, gap = o.gap || H * .135, ch = o.ch || H * .115, t0 = o.t0 == null ? .5 : o.t0, dt = o.dt || 1.2;
  items.forEach(function (it, i) {
    var a = eout((lt - t0 - i * dt) / .45); if (a <= 0) return; var y = y0 + i * gap;
    g.save(); g.globalAlpha = a; g.translate((1 - a) * 80, 0);
    card(W * .07, y, W * .86, ch, 36);
    g.fillStyle = it[4] ? it[4] + '22' : '#f2f7f4'; g.beginPath(); g.arc(W * .19, y + ch / 2, ch * .38, 0, Math.PI * 2); g.fill();
    if (it[0]) it[0](W * .19, y + ch / 2);
    var big = o.big || 48;
    if (it[2]) { label(it[1], W * .32, y + ch * .36, big, COL.ink, 900, 'left'); label(it[2], W * .32, y + ch * .72, 32, COL.sub, 700, 'left'); }
    else label(it[1], W * .32, y + ch / 2, big, COL.ink, 900, 'left');
    var m = sm((lt - t0 - i * dt - .5) / .3);
    if (it[3] === 'v') markV(W * .86, y + ch / 2, 26, m); else if (it[3] === 'x') markX(W * .86, y + ch / 2, 26, m);
    g.restore();
  });
}
function mottoCard(lt, rows, footer) {
  hikeSky(0); hikeClouds(lt + 160, 1, .3); birds(lt, .8, 3, H * .12);
  var a = eout(lt / .4), x = W * .08, y = H * .24, w = W * .84, h = H * .44;
  g.save(); g.globalAlpha = a; g.translate(0, (1 - a) * 50);
  card(x, y, w, h, 44);
  label('记住这几句', CX, y + 100, 50, COL.amber, 900);
  var cols = [COL.green, COL.amber, COL.blue];
  rows.forEach(function (r, i) {
    var ra = eout((lt - .8 - i * 1.2) / .35); if (ra <= 0) return; var ry = y + 250 + i * 230;
    g.save(); g.globalAlpha = a * ra; g.translate((1 - ra) * 40, 0); g.font = '700 38px ' + SANS; var pw = g.measureText(r[0]).width + 53;
    pill(r[0], x + 70 + pw / 2, ry - 44, 38, r[2] || cols[i % 3], '#fff');
    g.font = '900 56px ' + SANS; var sz = Math.min(56, 56 * (w - 140) / g.measureText(r[1]).width);
    label(r[1], x + 70, ry + 42, sz, COL.ink, 900, 'left'); g.restore();
  });
  g.restore();
  label(footer, CX, H * .75, 46, COL.sub, 700);
}
function endScene(lt, art) {
  var peak = function (x) { return H * .92 - 220 * Math.exp(-Math.pow((x - CX) / 300, 2)); };
  hikeSky(.25); hikeSun(W * .2, H * .7, 70, lt, .3); hikeRidges(0, .2, H * .82); birds(lt + 5, .9, 4, H * .58);
  hikeGround(peak, 0, lt, { treeGap: 180 });
  for (var i = 0; i < 3; i++) cloud(((lt * 30 + i * 420) % (W + 400)) - 200, H * (.9 + i * .04), .9, .9);
  flagPole(CX + 70, peak(CX + 70) + 6, 1, lt, COL.red);
  drawHiker(CX - 30, peak(CX - 30) + 12, Object.assign({ s: 1.3, wave: true, walk: 0, t: lt }, art || {}));
  pill('想看什么？评论区点题', CX, H * .55, 38, COL.amber, '#fff', eout((lt - 1.8) / .4));
}
function flagPole(x, y, s, t, c) {
  g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = '#5b4636'; g.lineWidth = 5; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, -90); g.stroke();
  g.fillStyle = c || COL.red; g.beginPath(); g.moveTo(0, -90);
  for (var i = 1; i <= 10; i++) g.lineTo(i * 5.5, -90 + Math.sin(t * 6 + i * .7) * 4 * (i / 10));
  for (i = 10; i >= 0; i--) g.lineTo(i * 5.5, -58 + Math.sin(t * 6 + i * .7) * 4 * (i / 10));
  g.closePath(); g.fill(); g.restore();
}
// 两栏对比卡：左红右绿（或自定）
function twoCards(lt, L, R, o) {
  o = o || {}; var y = o.y || H * .225, h = o.h || H * .45;
  [[L, W * .05, o.t0 || .3], [R, W * .52, (o.t0 || .3) + .5]].forEach(function (c) {
    var a = eout((lt - c[2]) / .4); if (a <= 0) return;
    g.save(); g.globalAlpha = a; g.translate(0, (1 - a) * 60); card(c[1], y, W * .43, h, 36);
    pill(c[0].title, c[1] + W * .215, y + 60, 36, c[0].color, '#fff');
    if (c[0].draw) { g.save(); rrect(c[1], y, W * .43, h, 36); g.clip(); c[0].draw(c[1] + W * .215, y + h * .5, lt); g.restore(); }
    if (c[0].note) label(c[0].note, c[1] + W * .215, y + h - 60, 38, c[0].color, 900);
    g.restore();
  });
}
function errorMark(l2, d) { markX(W * .88, H * .2, 40, win(l2, .3, d || 6, .2, .3)); }
function popText(text, x, y, size, color, lt) { if (lt < 0) return; var b = pop(lt); g.save(); g.translate(x, y); g.scale(b, b); label(text, 0, 0, size, color, 900); g.restore(); }
function bubble(text, x, y, size, color, lt) {
  if (lt < 0) return; var b = pop(lt); g.save(); g.translate(x, y); g.scale(b, b); g.font = '900 ' + size + 'px ' + SANS;
  var w = g.measureText(text).width + size * 1.2, h = size * 1.9; g.fillStyle = '#fff'; g.shadowColor = 'rgba(27,40,56,.15)'; g.shadowBlur = 16;
  rrect(-w / 2, -h / 2, w, h, h / 2); g.fill(); g.shadowBlur = 0; g.beginPath(); g.moveTo(-18, h / 2 - 2); g.lineTo(-30, h / 2 + 22); g.lineTo(4, h / 2 - 2); g.fill();
  label(text, 0, 2, size, color, 900); g.restore();
}

/* ───────── 物品图标（约 100px 见方，s 缩放）───────── */
var ICO = {
  bottle: function (x, y, s, fill) { s = s || 1; fill = fill == null ? .8 : fill; g.save(); g.translate(x, y); g.scale(s, s);
    g.fillStyle = '#d7ecf8'; rrect(-24, -38, 48, 82, 14); g.fill(); g.save(); rrect(-24, -38, 48, 82, 14); g.clip(); g.fillStyle = '#6ec3f4'; g.fillRect(-24, 44 - 82 * fill, 48, 82 * fill); g.restore();
    g.strokeStyle = '#2f80ed'; g.lineWidth = 4; rrect(-24, -38, 48, 82, 14); g.stroke(); g.fillStyle = '#2f80ed'; rrect(-14, -54, 28, 18, 5); g.fill(); g.restore(); },
  food: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.rotate(-.25);
    g.fillStyle = '#ff9f1c'; rrect(-46, -18, 92, 36, 8); g.fill(); g.fillStyle = '#b5651d'; rrect(-30, -12, 60, 24, 5); g.fill();
    g.fillStyle = '#ffd166'; [[-18, 0], [0, -4], [16, 2]].forEach(function (p) { g.beginPath(); g.arc(p[0], p[1], 5, 0, Math.PI * 2); g.fill(); }); g.restore(); },
  jacket: function (x, y, s, c) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = c || '#2f80ed';
    g.beginPath(); g.moveTo(-20, -40); g.lineTo(-46, -26); g.lineTo(-56, 20); g.lineTo(-40, 24); g.lineTo(-34, -4); g.lineTo(-32, 44); g.lineTo(32, 44); g.lineTo(34, -4); g.lineTo(40, 24); g.lineTo(56, 20); g.lineTo(46, -26); g.lineTo(20, -40); g.quadraticCurveTo(0, -26, -20, -40); g.closePath(); g.fill();
    g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 3; g.beginPath(); g.moveTo(0, -30); g.lineTo(0, 44); g.stroke(); g.restore(); },
  lamp: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = '#3d4b5c'; g.lineWidth = 8; g.beginPath(); g.ellipse(0, 6, 44, 26, 0, Math.PI * 1.05, Math.PI * 1.95); g.stroke();
    g.fillStyle = '#ffb703'; rrect(-22, -4, 44, 30, 8); g.fill(); g.fillStyle = '#fff6b0'; g.beginPath(); g.arc(0, 11, 10, 0, Math.PI * 2); g.fill(); g.restore(); },
  power: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#3d4b5c'; rrect(-26, -40, 52, 80, 10); g.fill();
    g.fillStyle = '#12a679'; for (var i = 0; i < 3; i++) { rrect(-14, 18 - i * 18, 28, 12, 3); g.fill(); } g.fillStyle = '#ffd166'; g.beginPath(); g.moveTo(4, -32); g.lineTo(-8, -18); g.lineTo(2, -18); g.lineTo(-4, -6); g.lineTo(8, -22); g.lineTo(-2, -22); g.closePath(); g.fill(); g.restore(); },
  phone: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#1b2838'; rrect(-26, -44, 52, 88, 10); g.fill(); g.fillStyle = '#e4f3e1'; rrect(-21, -36, 42, 70, 5); g.fill();
    g.strokeStyle = '#f0473c'; g.lineWidth = 4; g.beginPath(); g.moveTo(-12, 22); g.quadraticCurveTo(10, 4, -4, -8); g.quadraticCurveTo(-14, -18, 10, -26); g.stroke(); g.fillStyle = '#2f80ed'; g.beginPath(); g.arc(-4, -8, 5, 0, Math.PI * 2); g.fill(); g.restore(); },
  aid: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#f0473c'; rrect(-40, -30, 80, 60, 12); g.fill(); g.fillStyle = '#fff'; g.fillRect(-7, -20, 14, 40); g.fillRect(-20, -7, 40, 14); g.fillStyle = '#c0392b'; g.fillRect(-14, -38, 28, 10); g.restore(); },
  whistle: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#ff9f1c'; g.beginPath(); g.arc(10, 6, 24, 0, Math.PI * 2); g.fill(); rrect(-40, -18, 52, 22, 6); g.fill(); g.fillStyle = '#1b2838'; g.beginPath(); g.arc(10, 6, 8, 0, Math.PI * 2); g.fill(); g.restore(); },
  hat: function (x, y, s, c) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = c || '#ffc23d'; g.beginPath(); g.ellipse(0, 12, 52, 14, 0, 0, Math.PI * 2); g.fill(); g.beginPath(); g.arc(0, 6, 30, Math.PI, 0); g.fill(); g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(-30, -2, 60, 8); g.restore(); },
  glasses: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#1b2838'; [-22, 22].forEach(function (d) { g.beginPath(); g.ellipse(d, 0, 18, 14, 0, 0, Math.PI * 2); g.fill(); }); g.strokeStyle = '#1b2838'; g.lineWidth = 5; g.beginPath(); g.moveTo(-6, -4); g.quadraticCurveTo(0, -10, 6, -4); g.stroke(); g.restore(); },
  sunscreen: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#ffd166'; rrect(-20, -34, 40, 74, 10); g.fill(); g.fillStyle = '#ff9f1c'; rrect(-10, -48, 20, 16, 4); g.fill(); g.fillStyle = '#fff'; label('SPF', 0, 2, 16, '#ff7a3d', 900); g.restore(); },
  idcard: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#e9eff4'; rrect(-40, -26, 80, 52, 8); g.fill(); g.fillStyle = '#8aa1b3'; g.beginPath(); g.arc(-18, -2, 11, 0, Math.PI * 2); g.fill(); g.fillRect(2, -10, 28, 6); g.fillRect(2, 4, 22, 6); g.restore(); },
  rain: function (x, y, s, t) { s = s || 1; t = t || 0; g.save(); g.translate(x, y); g.scale(s, s); cloudIcon(0, -10, '#9fb3c8'); g.strokeStyle = '#2f80ed'; g.lineWidth = 5; g.lineCap = 'round'; for (var i = 0; i < 4; i++) { var ph = (t * 1.5 + i * .27) % 1; g.globalAlpha = 1 - ph; g.beginPath(); g.moveTo(-30 + i * 20, 18 + ph * 30); g.lineTo(-36 + i * 20, 32 + ph * 30); g.stroke(); } g.restore(); },
  storm: function (x, y, s, t) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); cloudIcon(0, -10, '#6d7f94'); g.fillStyle = '#ffd166'; g.globalAlpha = .6 + .4 * Math.abs(Math.sin((t || 0) * 5)); g.beginPath(); g.moveTo(6, 6); g.lineTo(-14, 36); g.lineTo(0, 36); g.lineTo(-8, 62); g.lineTo(18, 26); g.lineTo(4, 26); g.lineTo(14, 6); g.closePath(); g.fill(); g.restore(); },
  wind: function (x, y, s, t) { s = s || 1; t = t || 0; g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = '#6ec3f4'; g.lineWidth = 7; g.lineCap = 'round';
    [[-14, 46], [6, 56], [26, 36]].forEach(function (r, i) { var o = Math.sin(t * 3 + i) * 6; g.beginPath(); g.moveTo(-46 + o, r[0] - 10); g.lineTo(r[1] - 46 + o + 30, r[0] - 10); g.arc(r[1] - 46 + o + 30, r[0] - 22, 12, Math.PI / 2, -Math.PI / 2 - .6, true); g.stroke(); }); g.restore(); },
  thermo: function (x, y, s, lvl, c) { s = s || 1; lvl = lvl == null ? .5 : lvl; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#e9eff4'; rrect(-11, -46, 22, 72, 11); g.fill(); g.beginPath(); g.arc(0, 32, 18, 0, Math.PI * 2); g.fill();
    g.fillStyle = c || '#f0473c'; g.beginPath(); g.arc(0, 32, 12, 0, Math.PI * 2); g.fill(); rrect(-5, 26 - 66 * lvl, 10, 66 * lvl + 8, 5); g.fill(); g.restore(); },
  pack: function (x, y, s, c) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = c || TP.pack; rrect(-34, -44, 68, 88, 20); g.fill(); g.fillStyle = TP.pack2; rrect(-26, 4, 52, 30, 10); g.fill(); g.strokeStyle = TP.pack2; g.lineWidth = 6; g.beginPath(); g.arc(0, -44, 14, Math.PI, 0); g.stroke(); g.restore(); },
  sock: function (x, y, s, c) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = c || '#8aa1b3'; g.beginPath(); g.moveTo(-14, -44); g.lineTo(14, -44); g.lineTo(14, 10); g.quadraticCurveTo(14, 34, 40, 34); g.quadraticCurveTo(52, 34, 48, 44); g.lineTo(-6, 44); g.quadraticCurveTo(-14, 44, -14, 30); g.closePath(); g.fill(); g.fillStyle = 'rgba(255,255,255,.4)'; g.fillRect(-14, -44, 28, 12); g.restore(); },
  pole: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.rotate(.35); g.strokeStyle = '#7d8ea3'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath(); g.moveTo(0, -30); g.lineTo(0, 52); g.stroke(); g.fillStyle = '#1b2838'; rrect(-8, -52, 16, 30, 6); g.fill(); g.strokeStyle = COL.amber; g.lineWidth = 4; g.beginPath(); g.moveTo(-4, -2); g.lineTo(4, -2); g.stroke(); g.restore(); },
  map: function (x, y, s) { s = s || 1; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#e4f3e1'; g.beginPath(); g.moveTo(-44, -30); g.lineTo(-14, -38); g.lineTo(14, -30); g.lineTo(44, -38); g.lineTo(44, 30); g.lineTo(14, 38); g.lineTo(-14, 30); g.lineTo(-44, 38); g.closePath(); g.fill(); g.strokeStyle = '#8fbf8a'; g.lineWidth = 3; g.stroke();
    g.strokeStyle = COL.red; g.lineWidth = 4; g.setLineDash([6, 5]); g.beginPath(); g.moveTo(-32, 20); g.quadraticCurveTo(-10, -20, 10, 8); g.quadraticCurveTo(24, 24, 32, -18); g.stroke(); g.restore(); },
  clock: function (x, y, s, h) { clockIcon(x, y, 40 * (s || 1), h == null ? 3 : h, 1); }
};
function cloudIcon(x, y, c) { g.fillStyle = c; [[-26, 4, 20], [0, -8, 28], [26, 4, 20]].forEach(function (b) { g.beginPath(); g.arc(x + b[0], y + b[1], b[2], 0, Math.PI * 2); g.fill(); }); g.fillRect(x - 46, y + 4, 92, 20); }
// 鞋（侧面，鞋头朝右）：type = sneaker | trail | mid | high
function shoe(x, y, s, type, col) {
  s = s || 1; g.save(); g.translate(x, y); g.scale(s, s);
  var hgt = { sneaker: 58, trail: 64, mid: 100, high: 130 }[type] || 64, c = col || { sneaker: '#f4f6f8', trail: '#ff7a3d', mid: '#8b6a4f', high: '#6b4a32' }[type];
  var lug = type !== 'sneaker';
  g.fillStyle = lug ? '#2b3440' : '#d9dee4'; rrect(-100, -14, 210, lug ? 26 : 18, 10); g.fill();
  if (lug) { g.fillStyle = '#2b3440'; for (var i = 0; i < 10; i++) { g.beginPath(); g.moveTo(-92 + i * 20, 10); g.lineTo(-84 + i * 20, 22); g.lineTo(-76 + i * 20, 10); g.closePath(); g.fill(); } }
  g.fillStyle = c; g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = 3;
  g.beginPath(); g.moveTo(-98, -12); g.lineTo(-96, -hgt); g.quadraticCurveTo(-80, -hgt - 10, -50, -hgt + 2); g.lineTo(-30, -hgt * .55); g.quadraticCurveTo(40, -62, 92, -30); g.quadraticCurveTo(112, -16, 104, -12); g.closePath(); g.fill(); g.stroke();
  if (type !== 'sneaker') { g.fillStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.moveTo(60, -40); g.quadraticCurveTo(96, -30, 104, -12); g.lineTo(60, -12); g.closePath(); g.fill(); }
  g.strokeStyle = type === 'sneaker' ? '#8aa1b3' : '#ffd166'; g.lineWidth = 4; g.lineCap = 'round';
  for (i = 0; i < (type === 'high' ? 6 : type === 'mid' ? 5 : 4); i++) { var lx = -40 + i * 16 - (type === 'high' || type === 'mid' ? 30 : 0) + i * 4, ly = -hgt * .55 - 4 + i * (hgt * .55 - 40) / 4; g.beginPath(); g.moveTo(lx - 8, ly - 6); g.lineTo(lx + 8, ly + 6); g.stroke(); }
  g.restore();
}
// 标准声音：o = { sec(t), chirps:[], steps:[[t0,t1,dt]], dings:[], ticks:[], wrongs:[], whoosh:[], riser:t, heart:[t0,t1] }
function hikeSound(K, c, DUR, o) {
  K.bed(o.start || 8, DUR, o.sec);
  var chirp = function (t0) { [0, .09, .2].forEach(function (d, i) { var os = c.createOscillator(), gg = c.createGain(); os.type = 'sine'; os.frequency.setValueAtTime(2600 + i * 300 + K.ar() * 400, t0 + d); os.frequency.exponentialRampToValueAtTime(4200 + K.ar() * 600, t0 + d + .06); gg.gain.setValueAtTime(0, t0 + d); gg.gain.linearRampToValueAtTime(.05, t0 + d + .01); gg.gain.exponentialRampToValueAtTime(.0001, t0 + d + .08); os.connect(gg); gg.connect(K.out); os.start(t0 + d); os.stop(t0 + d + .1); }); };
  (o.chirps || []).forEach(chirp);
  (o.steps || []).forEach(function (r) { for (var t = r[0]; t < r[1]; t += r[2]) K.noise(t, .09, .1, 'lowpass', 420); });
  (o.dings || []).forEach(K.ding); (o.ticks || []).forEach(K.tick); (o.wrongs || []).forEach(K.wrong); (o.whoosh || []).forEach(K.whoosh);
  if (o.heart) for (var t = o.heart[0]; t < o.heart[1]; t += .72) { K.tone(58, t, .22, .3); K.tone(52, t + .2, .26, .24); }
  if (o.riser) K.riser(o.riser - 1.4, o.riser, .12);
  if (o.outro) for (var i = 0; i < 3; i++) K.tone(880 + i * 110, o.outro + .8 + i * 1.2, .25, .07, 'triangle');
  if (o.extra) o.extra(K, c);
}
// 标准封面：o = { ep, l1, l2: [[字, 色]...], chips: [[字, 色]...], art(key, w, h) }
function hikeCover(key, w, h, o) {
  o.art(key, w, h);
  var fade = function (vert, k) {
    var fd = vert ? g.createLinearGradient(0, 0, 0, h * k) : g.createLinearGradient(0, 0, w * k, 0);
    fd.addColorStop(0, 'rgba(255,250,238,.97)'); fd.addColorStop(.78, 'rgba(255,250,238,.9)'); fd.addColorStop(1, 'rgba(255,250,238,0)');
    g.fillStyle = fd; vert ? g.fillRect(0, 0, w, h * k) : g.fillRect(0, 0, w * k, h);
  };
  var title = function (cx, y1, y2, size, subY, subSize, pillY, pillSize, maxW) {
    pill('徒步不难 · EP.' + o.ep, cx, pillY, pillSize, COL.amber, '#fff');
    g.font = '900 ' + size + 'px ' + SANS; var s1 = Math.min(size, size * maxW / g.measureText(o.l1).width);
    label(o.l1, cx, y1, s1, COL.ink, 900);
    var s2 = size * .86; g.font = '900 ' + s2 + 'px ' + SANS; var ws = o.l2.map(function (q) { return g.measureText(q[0]).width; }), tw = ws.reduce(function (a, b) { return a + b; }, 0);
    if (tw > maxW) { s2 *= maxW / tw; g.font = '900 ' + s2 + 'px ' + SANS; ws = o.l2.map(function (q) { return g.measureText(q[0]).width; }); tw = maxW; }
    var x = cx - tw / 2; o.l2.forEach(function (q, i) { label(q[0], x + ws[i] / 2, y2, s2, q[1], 900); x += ws[i]; });
    g.font = '700 ' + subSize + 'px ' + SANS; var cw = o.chips.map(function (c) { return g.measureText(c[0]).width + subSize * 1.4; }), gap = subSize * .6;
    var cxp = cx - (cw.reduce(function (a, b) { return a + b; }, 0) + gap * (cw.length - 1)) / 2; o.chips.forEach(function (c, i) { pill(c[0], cxp + cw[i] / 2, subY, subSize, c[1], '#fff'); cxp += cw[i] + gap; });
  };
  if (key === '9x16') { fade(true, .46); title(w / 2, h * .2, h * .28, 124, h * .355, 40, h * .11, 42, w * .86); }
  else if (key === '3x4') { fade(true, .48); title(w / 2, h * .16, h * .26, 116, h * .35, 38, h * .06, 40, w * .86); }
  else { fade(false, .6); var big = key === '16x9'; title(w * .28, h * .4, h * .55, big ? 108 : 86, h * .69, big ? 38 : 32, h * .24, big ? 38 : 34, w * .5); }
}
// 封面常用画面：山坡 + 小人；mx 为山顶的横向位置（竖版 .6，横版 .74）
function coverHill(key, w, h, hik, extra) {
  var mx = key === '9x16' || key === '3x4' ? .6 : .74;
  hikeSky(0); hikeSun(w * .82, h * .2, 70, 1, 0);
  for (var i = 0; i < 3; i++) cloud(w * (.12 + i * .34), h * (.12 + (i % 2) * .08), .8, .95);
  var oy = key === '9x16' ? h * .08 : key === '3x4' ? h * .06 : 0;
  g.save(); g.translate(0, oy);
  hikeRidges(200, 0, h * .62);
  var mw = Math.min(w, h) * .32, hy = function (x) { return h * .9 - h * .22 * Math.exp(-Math.pow((x - w * mx) / mw, 2)); };
  hikeGround(hy, 0, 1, { treeGap: 200 });
  flagPole(w * mx, hy(w * mx) + 6, 1.2, 1, COL.red);
  var xh = w * mx - mw * .75;
  hikerOn(hy, xh, 0, Object.assign({ s: 1.6, ph: 1.2, t: 0, pole: true }, hik || {}));
  if (extra) extra(xh, hy(xh), mx, hy);
  g.restore();
}

// 风：横向的流线
function windLines(t, a, y0, y1, n) {
  a = a == null ? 1 : a; y0 = y0 == null ? H * .2 : y0; y1 = y1 == null ? H * .7 : y1; n = n || 14;
  g.save(); g.strokeStyle = '#ffffff'; g.lineCap = 'round';
  for (var i = 0; i < n; i++) {
    var y = lerp(y0, y1, hash(i + 3)), len = 120 + hash(i) * 200, x = ((hash(i + 7) * (W + 600) + t * (900 + hash(i + 1) * 500)) % (W + 600)) - 300;
    g.globalAlpha = a * (.35 + hash(i + 5) * .4); g.lineWidth = 4 + hash(i + 2) * 4;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + len * .5, y - 12 * Math.sin(t * 3 + i), x + len, y); g.stroke();
  }
  g.restore();
}
// 雨
function rainFall(t, a, n) {
  a = a == null ? 1 : a; n = n || 90;
  g.save(); g.strokeStyle = 'rgba(120,170,220,.8)'; g.lineWidth = 3; g.lineCap = 'round';
  for (var i = 0; i < n; i++) { var x = hash(i) * (W + 200) - 100, y = ((hash(i + 4) * H + t * (1400 + hash(i + 2) * 600)) % (H + 100)) - 50; g.globalAlpha = a * (.4 + hash(i + 8) * .5); g.beginPath(); g.moveTo(x, y); g.lineTo(x - 10, y + 40); g.stroke(); }
  g.restore();
}
// T 恤：wet 0~1 湿透程度
function tee(x, y, s, col, wet, t) {
  s = s || 1; wet = wet || 0; g.save(); g.translate(x, y); g.scale(s, s);
  g.fillStyle = col; g.beginPath(); g.moveTo(-34, -60); g.lineTo(-80, -40); g.lineTo(-96, 0); g.lineTo(-64, 12); g.lineTo(-56, -6); g.lineTo(-56, 70); g.lineTo(56, 70); g.lineTo(56, -6); g.lineTo(64, 12); g.lineTo(96, 0); g.lineTo(80, -40); g.lineTo(34, -60); g.quadraticCurveTo(0, -36, -34, -60); g.closePath(); g.fill();
  if (wet > 0) {
    g.save(); g.clip(); g.fillStyle = 'rgba(30,60,110,' + .35 * wet + ')';
    [[-20, 10, 46], [24, 30, 40], [0, -24, 30], [-30, 50, 26]].forEach(function (b) { g.beginPath(); g.arc(b[0], b[1], b[2] * (.6 + .4 * wet), 0, Math.PI * 2); g.fill(); }); g.restore();
    g.fillStyle = '#6ec3f4';
    for (var i = 0; i < 4; i++) { var ph = ((t || 0) * 1.2 + i / 4) % 1, dx = -40 + i * 26, dy = 74 + ph * 50; g.globalAlpha = wet * (1 - ph); g.beginPath(); g.moveTo(dx, dy - 10); g.quadraticCurveTo(dx + 7, dy, dx, dy + 5); g.quadraticCurveTo(dx - 7, dy, dx, dy - 10); g.fill(); }
  }
  g.restore();
}
// 顶部字幕底板：天色暗的时候用
function topPanel(a) { g.save(); g.globalAlpha = a == null ? 1 : a; g.fillStyle = 'rgba(255,255,255,.82)'; rrect(W * .04, H * .075, W * .92, H * .12, 40); g.fill(); g.restore(); }
