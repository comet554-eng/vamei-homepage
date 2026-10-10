/* skiwedge.js — 双板八字相关：俯视八字小人 topSkier()、正面迎面小人 frontV()、雪景背景。从 EP.03 抽出。 */
function skiGeom(x, y, wedge, s, tipGap) {
  const L = 230 * s, gap = (tipGap == null ? 30 : tipGap) * s, a = wedge * D2R, out = [];
  [-1, 1].forEach(side => {
    // 板头在前（画面下方），靠近中线；板尾在后，向两侧分开
    const dir = [-side * Math.sin(a), Math.cos(a)], tip = [x + side * (gap / 2 + 9 * s), y + L * .55], tail = [tip[0] - dir[0] * L, tip[1] - dir[1] * L];
    const m = [(tip[0] + tail[0]) / 2, (tip[1] + tail[1]) / 2];
    out.push({ side, tip, tail, mid: m, dir });
  });
  return out;
}
function topSkier(x, y, wedge, s, o = {}) {
  const sk = skiGeom(x, y, wedge, s, o.tipGap);
  g.save(); g.lineCap = 'round';
  sk.forEach(k => {
    g.strokeStyle = o.mono || COL.ski; g.lineWidth = 18 * s; g.beginPath(); g.moveTo(...k.tail); g.lineTo(...k.tip); g.stroke();
    if (o.press && o.press[k.side < 0 ? 0 : 1]) { g.strokeStyle = 'rgba(18,166,121,.5)'; g.lineWidth = 34 * s; g.beginPath(); g.moveTo(...k.tail); g.lineTo(...k.tip); g.stroke(); }
  });
  g.fillStyle = o.mono || COL.jacket; g.beginPath(); g.ellipse(x, y + 10 * s, 40 * s, 26 * s, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fff'; g.strokeStyle = COL.pants; g.lineWidth = 4 * s; g.beginPath(); g.arc(x, y + 14 * s, 17 * s, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = COL.amber; g.beginPath(); g.arc(x, y + 26 * s, 6 * s, 0, Math.PI * 2); g.fill();
  g.restore();
  return sk;
}
function topBg(scroll) {
  g.fillStyle = '#f7fafc'; g.fillRect(0, 0, W, H);
  g.strokeStyle = '#e3ebf2'; g.lineWidth = 3; for (let x = 40; x < W; x += 34) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
  for (let i = 0; i < 14; i++) { const side = i % 2 ? W - 36 : 36, y = ((i * 260 - scroll) % (H + 200) + H + 200) % (H + 200) - 100; g.fillStyle = '#cddbe6'; g.beginPath(); g.arc(side + (hash(i) - .5) * 20, y, 22 + hash(i + 3) * 8, 0, Math.PI * 2); g.fill(); }
  // 雪道上的痕迹，体现前进
  g.strokeStyle = '#e6edf3'; g.lineWidth = 6; for (let i = 0; i < 18; i++) { const x = 120 + (i * 173) % (W - 240), y = ((i * 211 - scroll) % H + H) % H; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 30, y + 10); g.stroke(); }
}
function sprayTop(k, s, t, amt) { // 板外侧被推开的雪
  if (amt < .02) return; g.save(); g.fillStyle = '#fff'; g.strokeStyle = '#c8d7e5'; g.lineWidth = 2;
  for (let i = 0; i < 10; i++) { const ph = (t * 1.4 + hash(i + k.side * 7)) % 1, along = .2 + hash(i + 3) * .7, bx = lerp(k.tail[0], k.tip[0], along), by = lerp(k.tail[1], k.tip[1], along);
    const x = bx + k.side * (20 + ph * 80) * s, y = by - ph * 30 * s; g.globalAlpha = amt * (1 - ph); g.beginPath(); g.arc(x, y, (5 + hash(i) * 7) * s, 0, Math.PI * 2); g.fill(); g.stroke(); }
  g.restore();
}

/* ───────── 正面：人迎着镜头滑来 ───────── */
var FV = {
  parallel: { wedge: 0, stance: .3, hipH: 1.55, kneeIn: .02, sway: 0, edge: 0 },
  pizza: { wedge: 1, stance: .42, hipH: 1.45, kneeIn: .1, sway: 0, edge: .8 },
  big: { wedge: 1, stance: .62, hipH: 1.38, kneeIn: .12, sway: 0, edge: 1 },
  knock: { wedge: 1, stance: .5, hipH: 1.35, kneeIn: .3, sway: 0, edge: 1 }
};
var lerpFV = (a, b, k) => { const o = {}; for (const key in a) o[key] = lerp(a[key], b[key], k); return o; };
function frontV(F, p, u, o = {}) {
  const col = c => o.mono || c, J = { u };
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.globalAlpha = o.alpha == null ? 1 : o.alpha;
  const seg = (a, b, w, c) => { g.strokeStyle = col(c); g.lineWidth = w * u; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };
  const poly = (pts, c) => { g.beginPath(); pts.forEach((q, i) => i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1])); g.closePath(); g.fillStyle = col(c); g.fill(); };
  const boots = [-1, 1].map(sd => [F[0] + sd * p.stance * u + p.sway * u * .3, F[1]]);
  // 雪板：板头朝镜头（画面下方）、更宽；板尾往远处（画面上方）
  boots.forEach((b, i) => {
    const sd = i ? 1 : -1, tipX = lerp(b[0], F[0] + sd * .12 * u, p.wedge), tip = [tipX, F[1] + 1.05 * u], tail = [b[0] + (b[0] - tipX) * .85, F[1] - .9 * u];
    const wn = .2 * u, wf = .12 * u, eg = p.edge * .07 * u * sd; // eg：立刃时露出内侧
    poly([[tail[0] - wf / 2 - eg, tail[1]], [tail[0] + wf / 2 - eg, tail[1]], [tip[0] + wn / 2 - eg, tip[1]], [tip[0] - wn / 2 - eg, tip[1]]], COL.ski);
    if (p.edge > .05) poly([[tail[0] - sd * wf / 2 - eg, tail[1]], [tail[0] - sd * wf / 2, tail[1] + .03 * u], [tip[0] - sd * wn / 2, tip[1] + .05 * u], [tip[0] - sd * wn / 2 - eg, tip[1]]], '#1d5fbf');
    J['tip' + i] = tip; J['tail' + i] = tail;
  });
  J.boots = boots;
  const hipC = [F[0] + p.sway * u, F[1] - p.hipH * u], hips = [[hipC[0] - .18 * u, hipC[1]], [hipC[0] + .18 * u, hipC[1]]];
  const knees = boots.map((b, i) => { const a = [b[0], b[1] - .4 * u], m = mid(a, hips[i]); return [m[0] - (i ? 1 : -1) * p.kneeIn * u, m[1]]; });
  J.knees = knees;
  // 雪杖
  const S = [hipC[0], hipC[1] - 1.1 * u], sh = [[S[0] - .28 * u, S[1]], [S[0] + .28 * u, S[1]]];
  const hands = sh.map((q, i) => [q[0] + (i ? 1 : -1) * .42 * u, q[1] + .8 * u]);
  hands.forEach((h, i) => seg(h, [h[0] + (i ? 1 : -1) * .35 * u, F[1] + .25 * u], .04, '#8a9bb0'));
  boots.forEach((b, i) => {
    const a = [b[0], b[1] - .4 * u];
    seg(a, knees[i], .26, COL.pants); seg(knees[i], hips[i], .3, COL.pants);
    poly([[b[0] - .15 * u, b[1] + .02 * u], [b[0] + .15 * u, b[1] + .02 * u], [b[0] + .13 * u, b[1] - .45 * u], [b[0] - .13 * u, b[1] - .45 * u]], COL.boot);
  });
  seg(hips[0], hips[1], .34, COL.pants);
  seg(hipC, S, .6, COL.jacket); seg(sh[0], sh[1], .32, COL.jacket);
  sh.forEach((q, i) => { const e = [q[0] + (i ? 1 : -1) * .3 * u, q[1] + .45 * u]; seg(q, e, .17, i ? '#ff8a4f' : COL.jacket2); seg(e, hands[i], .15, i ? '#ff8a4f' : COL.jacket2); g.fillStyle = col(COL.pants); g.beginPath(); g.arc(hands[i][0], hands[i][1], .1 * u, 0, Math.PI * 2); g.fill(); });
  const Hd = [S[0], S[1] - .4 * u]; J.Hd = Hd; J.hipC = hipC;
  g.fillStyle = col('#fff'); g.strokeStyle = col(COL.pants); g.lineWidth = .05 * u; g.beginPath(); g.arc(Hd[0], Hd[1], .22 * u, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = col(COL.amber); rrect(Hd[0] - .17 * u, Hd[1] - .06 * u, .34 * u, .13 * u, .06 * u); g.fill();
  g.restore();
  return J;
}
function snowFront(scroll) {
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#e2edf6'); gr.addColorStop(.35, '#f3f7fb'); gr.addColorStop(1, '#ffffff'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  for (let i = 0; i < 9; i++) { const x = 60 + i * 125 + (i % 2) * 30, y = H * .28 + (i % 3) * 22; g.fillStyle = '#c9d8e5'; for (let j = 0; j < 3; j++) { const w = 40 - j * 10, yy = y - j * 30; g.beginPath(); g.moveTo(x, yy - 48); g.lineTo(x - w, yy); g.lineTo(x + w, yy); g.closePath(); g.fill(); } }
  g.strokeStyle = '#e0e9f1'; g.lineWidth = 5;
  for (let i = 0; i < 26; i++) { const x = (i * 197) % W, y = H * .36 + (((i * 131) + scroll) % (H * .6)); const s = .5 + (y - H * .36) / (H * .6); g.beginPath(); g.moveTo(x, y); g.lineTo(x + 40 * s, y); g.stroke(); }
}

