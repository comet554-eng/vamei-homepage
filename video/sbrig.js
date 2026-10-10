/* sbrig.js — 单板小人：rider()（顺着雪板看，横截面视角）与 sbRider()（侧面视角），供单板各集与 snowkit.js 一起使用。 */
var RL = { ank: .25, shin: 1.0, thigh: 1.05, torso: 1.15, head: .37, headR: .21, uarm: .58, farm: .52 };
var RP = {
  ride: { shin: 22, thigh: -34, torso: 22, head: 12, uarm: 150, farm: 105 },
  low: { shin: 38, thigh: -84, torso: 38, head: 18, uarm: 145, farm: 100 },
  catchBack: { shin: 15, thigh: -40, torso: -10, head: -15, uarm: 205, farm: 198 },
  fallFwd: { shin: 30, thigh: -20, torso: 45, head: 20, uarm: 112, farm: 112 },
  sit: { shin: -25, thigh: -150, torso: -12, head: 40, uarm: 160, farm: 45 },
  sitPost: { shin: -25, thigh: -150, torso: -32, head: -40, uarm: 214, farm: 210 },
  sitFar: { shin: -80, thigh: -100, torso: -25, head: 15, uarm: 200, farm: 190 },
  sitPush: { shin: -25, thigh: -150, torso: -35, head: 20, uarm: 188, farm: 182 },
  kneel: { shin: 100, thigh: -5, torso: 22, head: 15, uarm: 140, farm: 95 },
  plank: { shin: 100, thigh: 55, torso: 86, head: 118, uarm: 180, farm: 90 },
  reach: { shin: 100, thigh: 30, torso: 75, head: 60, uarm: 160, farm: 160 }
};
var lerpPose = (a, b, k) => { const o = {}; for (const key in a) o[key] = lerp(a[key], b[key], k); return o; };
var withP = (p, ch) => Object.assign({}, p, ch);
function rider(F, th, pose, u, o = {}) {
  const facing = o.facing || 1, f0 = frameOf(th), fr = { d: [f0.d[0] * facing, f0.d[1] * facing], n: f0.n };
  const P = (s, h) => [F[0] + (fr.d[0] * s + fr.n[0] * h) * u, F[1] + (fr.d[1] * s + fr.n[1] * h) * u];
  const add = (p, deg, l) => { const v = dirOf(fr, deg); return [p[0] + v[0] * l * u, p[1] + v[1] * l * u]; };
  const sh = (p, k) => [p[0] + D[0] * k, p[1] + D[1] * k];
  const D = [-facing * .46 * u, -.3 * u]; // 指向画面深处的方向（雪板长度方向）
  const A = P(0, RL.ank + .03), K = add(A, pose.shin, RL.shin), Hp = add(K, pose.thigh, RL.thigh);
  const B = sh(Hp, .6), S = add(B, pose.torso, RL.torso), Hd = add(S, pose.head, RL.head), E = add(S, pose.uarm, RL.uarm), Hn = add(E, pose.farm, RL.farm);
  let piv = B;
  if (o.pivot === 'toe') piv = P(.34, 0); else if (o.pivot === 'heel') piv = P(-.34, 0); else if (Array.isArray(o.pivot)) piv = o.pivot;
  const ang = facing * (o.rot || 0) * D2R, ca = Math.cos(ang), sa = Math.sin(ang);
  const tf = p => [piv[0] + (p[0] - piv[0]) * ca - (p[1] - piv[1]) * sa, piv[1] + (p[0] - piv[0]) * sa + (p[1] - piv[1]) * ca];
  const J = { fr, P, A, K, Hp, B, S, Hd, E, Hn, D, u, facing, tf, pose };
  const col = c => o.mono || c;
  g.save(); g.globalAlpha = o.alpha == null ? 1 : o.alpha; g.lineCap = 'round'; g.lineJoin = 'round';
  g.translate(piv[0], piv[1]); g.rotate(ang); g.translate(-piv[0], -piv[1]);
  const seg = (a, b, w, c) => { g.strokeStyle = col(c); g.lineWidth = w * u; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };
  const poly = (pts, fill, stroke, lw) => { g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); if (fill) { g.fillStyle = col(fill); g.fill(); } if (stroke) { g.strokeStyle = col(stroke); g.lineWidth = lw * u; g.stroke(); } };
  // 雪板顶面（向画面深处延伸）
  const a0 = sh(P(-.34, .1), -.75), b0 = sh(P(.34, .1), -.75), c0 = sh(b0, 2.75), d0 = sh(a0, 2.75);
  poly([a0, b0, c0, d0], COL.boardTop, '#5a4fd6', .03);
  const boot = (off, dark) => {
    const Ao = sh(A, off), c = dirOf(fr, pose.shin), pf = dirOf(fr, pose.shin + 90);
    const Q = (ka, kb) => [Ao[0] + (pf[0] * ka + c[0] * kb) * u, Ao[1] + (pf[1] * ka + c[1] * kb) * u];
    seg(sh(P(-.27, .11), off), Q(-.27, .62), .07, dark ? '#1c2028' : '#2a2f3a');
    poly([sh(P(-.22, .1), off), sh(P(.3, .1), off), sh(P(.33, .19), off), Q(.2, .12), Q(.19, .45), Q(-.19, .45), Q(-.22, .05), sh(P(-.24, .16), off)], dark ? '#27384c' : COL.boot, '#1d2a38', .03);
    seg(sh(P(.04, .2), off), Q(.2, .16), .06, '#1d222b');
  };
  // 远侧的腿和手臂
  seg(sh(S, .3), sh(E, .3), .17, COL.jacket2); seg(sh(E, .3), sh(Hn, .3), .15, COL.jacket2);
  g.fillStyle = col(COL.pants2); g.beginPath(); g.arc(...sh(Hn, .3), .09 * u, 0, Math.PI * 2); g.fill();
  seg(sh(A, 1.2), sh(K, 1.2), .25, COL.pants2); seg(sh(K, 1.2), sh(Hp, 1.2), .28, COL.pants2);
  boot(1.2, true);
  seg(Hp, sh(Hp, 1.2), .32, COL.pants);
  // 近侧的腿
  seg(A, K, .26, COL.pants); seg(K, Hp, .3, COL.pants);
  boot(0, false);
  // 躯干、头
  seg(B, S, .48, COL.jacket);
  g.fillStyle = col('#ffffff'); g.strokeStyle = col(COL.pants); g.lineWidth = .05 * u;
  g.beginPath(); g.arc(Hd[0], Hd[1], RL.headR * u, 0, Math.PI * 2); g.fill(); g.stroke();
  const fv = dirOf(fr, pose.head + 90), fa = Math.atan2(fv[1], fv[0]);
  g.strokeStyle = col(COL.amber); g.lineWidth = .1 * u; g.beginPath(); g.arc(Hd[0], Hd[1], RL.headR * u * .78, fa - .55, fa + .55); g.stroke();
  // 近侧手臂
  seg(S, E, .18, '#ff8a4f'); seg(E, Hn, .16, '#ff8a4f');
  g.fillStyle = col(COL.pants); g.beginPath(); g.arc(Hn[0], Hn[1], .1 * u, 0, Math.PI * 2); g.fill();
  // 雪板截面（离镜头最近）
  const fa0 = sh(P(-.34, 0), -.75), fb0 = sh(P(.34, 0), -.75);
  poly([fa0, fb0, b0, a0], COL.board, COL.boardDark, .025);
  g.fillStyle = col('#c9d3de'); [fa0, fb0].forEach(p => { g.beginPath(); g.arc(p[0], p[1], .04 * u, 0, Math.PI * 2); g.fill(); });
  g.restore();
  J.toeEdge = tf(fb0); J.heelEdge = tf(fa0);
  return J;
}
var SP = {
  neutral: { hipS: .05, hipH: 1.45, lean: 6, armF: 112, armB: -118, look: .7 },
  tense: { hipS: -.28, hipH: 1.42, lean: -6, armF: 135, armB: -135, look: .1 },
  back: { hipS: -.62, hipH: 1.32, lean: -20, armF: 70, armB: -150, look: -.5 },
  fallen: { hipS: -1.25, hipH: .38, lean: -78, armF: 25, armB: -160, look: 0 },
  deep: { hipS: .1, hipH: 1.22, lean: 12, armF: 105, armB: -112, look: .8 },
  stand: { hipS: 0, hipH: 1.62, lean: 0, armF: 172, armB: -172, look: .4 },
  recoil: { hipS: -.42, hipH: 1.55, lean: -16, armF: 80, armB: -160, look: .9 },
  look: { hipS: .08, hipH: 1.4, lean: 8, armF: 95, armB: -125, look: 1 },
  lookBack: { hipS: -.35, hipH: 1.4, lean: -10, armF: 160, armB: -170, look: -1 }
};
var sbPlumb = th => { const k = Math.tan(th * D2R); return { hipS: -1.5 * k, hipH: 1.5, lean: -th, armF: 180 - th, armB: -(180 + th), look: .3 }; };
function sbJoints(F, th, p, u) {
  const fr = frameOf(th);
  const P = (s, h) => [F[0] + (fr.d[0] * s + fr.n[0] * h) * u, F[1] + (fr.d[1] * s + fr.n[1] * h) * u];
  const add = (q, deg, l) => { const v = dirOf(fr, deg); return [q[0] + v[0] * l * u, q[1] + v[1] * l * u]; };
  const Af = P(.55, .32), Ab = P(-.55, .32), Hc = P(p.hipS, p.hipH);
  const Hf = [Hc[0] + fr.d[0] * .17 * u, Hc[1] + fr.d[1] * .17 * u], Hb = [Hc[0] - fr.d[0] * .17 * u, Hc[1] - fr.d[1] * .17 * u];
  const S = add(Hc, p.lean, 1.15), Hd = add(S, p.lean, .4);
  const Sf = [S[0] + fr.d[0] * .24 * u, S[1] + fr.d[1] * .24 * u], Sb = [S[0] - fr.d[0] * .24 * u, S[1] - fr.d[1] * .24 * u];
  const Ef = add(Sf, p.armF, .55), Hnf = add(Ef, p.armF - 15, .5), Eb = add(Sb, p.armB, .55), Hnb = add(Eb, p.armB + 15, .5);
  const knee = (A, Hj, sign) => {
    const m = mid(A, Hj), dl = Math.hypot(Hj[0] - A[0], Hj[1] - A[1]) / u, b = Math.sqrt(Math.max(0, 1 - (dl / 2) ** 2)) * .55;
    return [m[0] + fr.d[0] * sign * b * u, m[1] + fr.d[1] * sign * b * u];
  };
  const Kf = knee(Af, Hf, 1), Kb = knee(Ab, Hb, -1);
  const parts = [[Hc, .4], [mid(Hc, S), .38], [Hd, .08], [mid(Af, Hf), .07], [mid(Ab, Hb), .07]];
  const com = parts.reduce((s, [q, w]) => [s[0] + q[0] * w, s[1] + q[1] * w], [0, 0]);
  const comS = ((com[0] - F[0]) * fr.d[0] + (com[1] - F[1]) * fr.d[1]) / u;
  return { fr, P, Af, Ab, Hc, Hf, Hb, Kf, Kb, S, Hd, Sf, Sb, Ef, Hnf, Eb, Hnb, com, comS, u, th, p };
}
function sbRider(F, th, p, u, o = {}) {
  const J = sbJoints(F, th, p, u), { P } = J, col = c => o.mono || c;
  g.save(); g.globalAlpha = o.alpha == null ? 1 : o.alpha; g.lineCap = 'round'; g.lineJoin = 'round';
  const seg = (a, b, w, c) => { g.strokeStyle = col(c); g.lineWidth = w * u; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };
  // 后手臂（在身体后面）
  seg(J.Sb, J.Eb, .17, COL.jacket2); seg(J.Eb, J.Hnb, .15, COL.jacket2);
  g.fillStyle = col(COL.pants2); g.beginPath(); g.arc(J.Hnb[0], J.Hnb[1], .09 * u, 0, Math.PI * 2); g.fill();
  // 雪板
  g.strokeStyle = col(COL.board); g.lineWidth = .12 * u;
  const t0 = P(-1.86, .26), t1 = P(-1.6, .05), n1 = P(1.6, .05), n0 = P(1.86, .26), tc = P(-1.8, .06), nc = P(1.8, .06);
  g.beginPath(); g.moveTo(...t0); g.quadraticCurveTo(tc[0], tc[1], t1[0], t1[1]); g.lineTo(...n1); g.quadraticCurveTo(nc[0], nc[1], n0[0], n0[1]); g.stroke();
  g.strokeStyle = col(COL.boardTop); g.lineWidth = .04 * u; g.beginPath(); g.moveTo(...P(-1.55, .1)); g.lineTo(...P(1.55, .1)); g.stroke();
  // 腿
  seg(J.Ab, J.Kb, .26, COL.pants); seg(J.Kb, J.Hb, .3, COL.pants);
  seg(J.Af, J.Kf, .26, COL.pants); seg(J.Kf, J.Hf, .3, COL.pants);
  seg(J.Hb, J.Hf, .34, COL.pants);
  // 鞋和固定器
  [[.55, J.Af], [-.55, J.Ab]].forEach(([s, A]) => {
    g.fillStyle = col('#2a2f3a'); const q = [P(s - .26, .1), P(s + .26, .1), P(s + .22, .2), P(s - .26, .26)];
    g.beginPath(); q.forEach((pt, i) => i ? g.lineTo(...pt) : g.moveTo(...pt)); g.closePath(); g.fill();
    g.fillStyle = col(COL.boot); const b = [P(s - .2, .12), P(s + .2, .12), P(s + .17, .38), P(s - .17, .38)];
    g.beginPath(); b.forEach((pt, i) => i ? g.lineTo(...pt) : g.moveTo(...pt)); g.closePath(); g.fill();
  });
  // 上身与头
  seg(J.Hc, J.S, .56, COL.jacket);
  seg(J.Sb, J.Sf, .3, COL.jacket);
  g.fillStyle = col('#ffffff'); g.strokeStyle = col(COL.pants); g.lineWidth = .05 * u;
  g.beginPath(); g.arc(J.Hd[0], J.Hd[1], .22 * u, 0, Math.PI * 2); g.fill(); g.stroke();
  // 护目镜：随视线偏向板头或板尾
  const gd = J.fr.d, off = p.look * .07 * u;
  g.save(); g.translate(J.Hd[0] + gd[0] * off, J.Hd[1] + gd[1] * off); g.rotate(Math.atan2(gd[1], gd[0]) + p.lean * D2R);
  g.fillStyle = col(COL.amber); rrect(-.15 * u, -.06 * u, .3 * u, .11 * u, .05 * u); g.fill(); g.restore();
  // 前手臂
  seg(J.Sf, J.Ef, .18, '#ff8a4f'); seg(J.Ef, J.Hnf, .16, '#ff8a4f');
  g.fillStyle = col(COL.pants); g.beginPath(); g.arc(J.Hnf[0], J.Hnf[1], .1 * u, 0, Math.PI * 2); g.fill();
  g.restore();
  return J;
}
function sbBalance(J, a = 1, labelOn = true) {
  const { P, u, com, comS } = J, ok = comS > -.3 && comS < .42, c = ok ? COL.green : COL.red, land = P(comS, .12);
  g.save(); g.globalAlpha = a * .25; g.strokeStyle = COL.green; g.lineWidth = .16 * u; g.lineCap = 'butt';
  g.beginPath(); g.moveTo(...P(-.28, .02)); g.lineTo(...P(.42, .02)); g.stroke(); g.globalAlpha = a;
  g.setLineDash([12, 10]); g.strokeStyle = c; g.lineWidth = 4; g.beginPath(); g.moveTo(com[0], com[1]); g.lineTo(land[0], land[1]); g.stroke(); g.setLineDash([]);
  g.fillStyle = '#fff'; g.strokeStyle = c; g.lineWidth = 5; g.beginPath(); g.arc(com[0], com[1], 17, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = c; g.beginPath(); g.moveTo(com[0], com[1]); g.arc(com[0], com[1], 17, -Math.PI / 2, 0); g.lineTo(com[0], com[1]); g.arc(com[0], com[1], 17, Math.PI / 2, Math.PI); g.closePath(); g.fill();
  g.beginPath(); g.arc(land[0], land[1], 11, 0, Math.PI * 2); g.fill();
  if (labelOn) { const lp = P(comS, -.6); label(ok ? '重心在两脚中间' : '重心跑到后脚上', lp[0], lp[1], 34, c, 700); }
  g.restore();
  return ok;
}
function sbPressure(J, center, a = 1, showNose = true) {
  const { P, u } = J; g.save(); g.globalAlpha = a; let noseM = 0;
  for (let i = 0; i < 13; i++) {
    const s = -1.5 + i * .25, m = Math.exp(-((s - center) ** 2) / (2 * .6 * .6));
    if (s > 1.0) noseM = Math.max(noseM, m);
    const len = .18 + m * .95, p1 = P(s, -.1 - len), p2 = P(s, -.08);
    const c = `rgb(${Math.round(lerp(156, 255, m))},${Math.round(lerp(195, 140, m))},${Math.round(lerp(230, 30, m))})`;
    g.strokeStyle = c; g.fillStyle = c; g.lineWidth = 6 + m * 6; g.lineCap = 'round';
    g.beginPath(); g.moveTo(...p1); g.lineTo(...p2); g.stroke();
    const v = [p2[0] - p1[0], p2[1] - p1[1]], vl = Math.hypot(...v), ux = v[0] / vl, uy = v[1] / vl, hs = 14 + m * 8;
    g.beginPath(); g.moveTo(p2[0] + ux * 6, p2[1] + uy * 6); g.lineTo(p2[0] - ux * hs - uy * hs * .7, p2[1] - uy * hs + ux * hs * .7); g.lineTo(p2[0] - ux * hs + uy * hs * .7, p2[1] - uy * hs - ux * hs * .7); g.closePath(); g.fill();
  }
  const lb = P(-.55, -1.4), lf = P(.55, -1.4); label('后脚', lb[0], lb[1], 34, COL.sub, 700); label('前脚', lf[0], lf[1], 34, COL.sub, 700);
  if (showNose && noseM < .15) {
    const c = P(1.25, .2); ring(c[0], c[1], .55 * u, COL.red, 1, true);
    const lp = P(1.25, 1.05); label('前脚没压力', lp[0], lp[1], 36, COL.red, 900);
  }
  g.restore();
}

function spray(J, t, amount) {
  if (amount < .02) return; const { P, fr, u } = J; g.save(); g.fillStyle = '#fff'; g.strokeStyle = '#c8d7e5'; g.lineWidth = 2;
  for (let i = 0; i < 26; i++) {
    const ph = (t * 1.6 + hash(i)) % 1, base = P(-1.7, .05), s = -(2.2 + hash(i + 3) * 2.5) * ph, h = (1.2 + hash(i + 7) * 1.6) * ph - 2.4 * ph * ph;
    const q = [base[0] + (fr.d[0] * s + fr.n[0] * h) * u, base[1] + (fr.d[1] * s + fr.n[1] * h) * u];
    g.globalAlpha = amount * (1 - ph) * .9; g.beginPath(); g.arc(q[0], q[1], 6 + hash(i + 11) * 10, 0, Math.PI * 2); g.fill(); g.stroke();
  }
  g.restore();
}
