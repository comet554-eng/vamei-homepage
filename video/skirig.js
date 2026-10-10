/* skirig.js — 双板小人（侧面视角），从 EP.01 抽出，供后续双板各集与 snowkit.js 一起使用。 */
COL.ski = COL.ski || '#2f80ed'; COL.pole = COL.pole || '#8a9bb0';
var L = { boot: .22, shin: 1.0, thigh: 1.05, torso: 1.15, neck: .16, headR: .21, uarm: .58, farm: .52, pole: 1.9 };
var POSES = {
  neutral: { shin: 24, thigh: -40, torso: 34, head: 14, uarm: 140, farm: 95, pole: 205 },
  tense: { shin: 14, thigh: -58, torso: 25, head: 6, uarm: 162, farm: 125, pole: 210 },
  back: { shin: 6, thigh: -80, torso: 16, head: -4, uarm: 188, farm: 165, pole: 218 },
  fallen: { shin: -30, thigh: -132, torso: -80, head: -88, uarm: 255, farm: 235, pole: 300 },
  stand: { shin: 3, thigh: -3, torso: 2, head: 4, uarm: 178, farm: 170, pole: 186 },
  recoil: { shin: -6, thigh: -15, torso: -20, head: -24, uarm: 122, farm: 62, pole: 160 },
  deep: { shin: 30, thigh: -56, torso: 40, head: 20, uarm: 138, farm: 92, pole: 205 },
  handsBack: { shin: 18, thigh: -52, torso: 26, head: 10, uarm: 196, farm: 178, pole: 220 }
};
var plumb = th => ({ shin: -th, thigh: -th, torso: -th, head: -th, uarm: 180 - th, farm: 172 - th, pole: 190 - th });
var lerpPose = (a, b, k) => { const o = {}; for (const key in a) o[key] = lerp(a[key], b[key], k); return o; };
function joints(F, th, pose, u) {
  const fr = frameOf(th);
  const P = (s, h) => [F[0] + (fr.d[0] * s + fr.n[0] * h) * u, F[1] + (fr.d[1] * s + fr.n[1] * h) * u];
  const add = (p, deg, l) => { const v = dirOf(fr, deg); return [p[0] + v[0] * l * u, p[1] + v[1] * l * u]; };
  const A = P(0, L.boot), K = add(A, pose.shin, L.shin), Hp = add(K, pose.thigh, L.thigh), S = add(Hp, pose.torso, L.torso);
  const Hd = add(S, pose.head, L.neck + L.headR), E = add(S, pose.uarm, L.uarm), Hn = add(E, pose.farm, L.farm), Pt = add(Hn, pose.pole, L.pole);
  const parts = [[mid(A, K), .12], [mid(K, Hp), .22], [mid(Hp, S), .46], [Hd, .08], [mid(S, Hn), .12]];
  const com = parts.reduce((s, [p, w]) => [s[0] + p[0] * w, s[1] + p[1] * w], [0, 0]);
  const ref = P(.1, 0), comS = ((com[0] - ref[0]) * fr.d[0] + (com[1] - ref[1]) * fr.d[1]) / u;
  return { fr, P, A, K, Hp, S, Hd, E, Hn, Pt, com, comS, th, pose, u, F };
}

var BOOT_LEAN = 18;
function drawBoot(J, col, cutaway) {
  const { fr, P, A, u } = J;
  const c = dirOf(fr, BOOT_LEAN), pf = dirOf(fr, BOOT_LEAN + 90);
  const Q = (p, a, ka, b, kb) => [p[0] + (a[0] * ka + b[0] * kb) * u, p[1] + (a[1] * ka + b[1] * kb) * u];
  const pts = [P(-.38, .05), P(.64, .05), P(.68, .18), P(.46, .3), Q(A, pf, .26, c, .26), Q(A, pf, .24, c, .7), Q(A, pf, -.24, c, .7), Q(A, pf, -.3, c, .16), P(-.42, .22)];
  g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath();
  g.fillStyle = col(COL.boot); const a0 = g.globalAlpha;
  if (cutaway) g.globalAlpha = a0 * .38;
  g.fill(); g.globalAlpha = a0;
  g.strokeStyle = col('#22303f'); g.lineWidth = .045 * u; g.stroke();
  g.strokeStyle = col('#8fa3b8'); g.lineWidth = .035 * u;
  [.36, .56].forEach(k => { const p1 = Q(A, pf, .24, c, k), p2 = Q(A, pf, -.18, c, k); g.beginPath(); g.moveTo(...p1); g.lineTo(...p2); g.stroke(); });
  return { tongueTop: Q(A, pf, .24, c, .7), tongueMid: Q(A, pf, .25, c, .5), c, pf };
}
function drawSki(J, col) {
  const { P, u } = J;
  g.strokeStyle = col(COL.ski); g.lineWidth = .085 * u; g.lineCap = 'round';
  const a = P(-1.65, .04), b = P(1.72, .04), c1 = P(1.98, .05), tip = P(2.06, .26);
  g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.quadraticCurveTo(c1[0], c1[1], tip[0], tip[1]); g.stroke();
  g.strokeStyle = col('#1d5fbf'); g.lineWidth = .05 * u;
  const b1 = P(-.5, .1), b2 = P(.72, .1); g.beginPath(); g.moveTo(...b1); g.lineTo(...b2); g.stroke();
}
function drawSkier(F, th, pose, u, o = {}) {
  const J = joints(F, th, pose, u), { fr } = J;
  const col = c => o.mono || c;
  g.save(); g.globalAlpha = o.alpha == null ? 1 : o.alpha; g.lineCap = 'round'; g.lineJoin = 'round';
  const seg = (a, b, w, c) => { g.strokeStyle = col(c); g.lineWidth = w * u; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };
  const off = [-fr.d[0] * .08 * u - fr.n[0] * .01 * u, -fr.d[1] * .08 * u - fr.n[1] * .01 * u], sh = p => [p[0] + off[0], p[1] + off[1]];
  if (!o.noPoles) seg(sh(J.Hn), sh(J.Pt), .045, '#a5b3c4');
  seg(sh(J.S), sh(J.E), .17, COL.jacket2); seg(sh(J.E), sh(J.Hn), .15, COL.jacket2);
  seg(sh(J.A), sh(J.K), .25, COL.pants2); seg(sh(J.K), sh(J.Hp), .28, COL.pants2);
  if (!o.noSki) drawSki(J, col);
  seg(J.A, J.K, .26, COL.pants); seg(J.K, J.Hp, .3, COL.pants);
  J.boot = drawBoot(J, col, o.cutaway);
  seg(J.Hp, J.S, .46, COL.jacket);
  g.fillStyle = col('#ffffff'); g.strokeStyle = col(COL.pants); g.lineWidth = .05 * u;
  g.beginPath(); g.arc(J.Hd[0], J.Hd[1], L.headR * u, 0, Math.PI * 2); g.fill(); g.stroke();
  const fv = dirOf(fr, pose.head + 90), fa = Math.atan2(fv[1], fv[0]);
  g.strokeStyle = col(COL.amber); g.lineWidth = .1 * u; g.beginPath(); g.arc(J.Hd[0], J.Hd[1], L.headR * u * .78, fa - .55, fa + .55); g.stroke();
  seg(J.S, J.E, .18, '#ff8a4f'); seg(J.E, J.Hn, .16, '#ff8a4f');
  g.fillStyle = col(COL.pants); g.beginPath(); g.arc(J.Hn[0], J.Hn[1], .095 * u, 0, Math.PI * 2); g.fill();
  if (!o.noPoles) seg(J.Hn, J.Pt, .05, '#7d8ea3');
  g.restore();
  return J;
}

/* 重心与"平衡线"（垂直于雪面） */
function sprayTrail(J, t, amount) {
  if (amount < .02) return;
  const { P } = J; g.save(); g.fillStyle = '#ffffff'; g.strokeStyle = '#c8d7e5'; g.lineWidth = 2;
  for (let i = 0; i < 26; i++) {
    const ph = (t * 1.6 + hash(i)) % 1, base = P(-1.5, .05);
    const vx = -(2.2 + hash(i + 3) * 2.5), vy = 1.2 + hash(i + 7) * 1.6;
    const fr = J.fr, s = vx * ph * 1.0, h = vy * ph - 2.4 * ph * ph;
    const p = [base[0] + (fr.d[0] * s + fr.n[0] * h) * J.u, base[1] + (fr.d[1] * s + fr.n[1] * h) * J.u];
    g.globalAlpha = amount * (1 - ph) * .9; const r = 6 + hash(i + 11) * 10;
    g.beginPath(); g.arc(p[0], p[1], r, 0, Math.PI * 2); g.fill(); g.stroke();
  }
  g.restore();
}
