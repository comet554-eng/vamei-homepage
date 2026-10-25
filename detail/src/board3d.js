// NUAGE 雪板 3D 产品渲染（three.js）。
// 用法：src/board3d.html?shot=hero|profile|layers|nose|base|top|debug  （nose 另有 &pass=depth）
// 由 tools/render.mjs 截图；画面画完后设置 window.__READY = true。
import * as THREE from 'three';

const Q = new URLSearchParams(location.search);
const SHOT = Q.get('shot') || 'debug';
const PASS = Q.get('pass') || 'color';
const qn = (k, d) => (Q.has(k) ? parseFloat(Q.get(k)) : d);

const ASSET = '../assets/src/';
const L = 1.55;            // 板长（米）
const WAIST = 0.252;       // 腰宽（米）

// ------------------------------------------------------------------ 小工具
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
function hash2(x, y) { let h = (x * 374761393 + y * 668265263) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function valueNoise(seed) {
  return (x, y) => {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    const h = (a, b) => hash2(a + seed * 131, b - seed * 71);
    return lerp(lerp(h(xi, yi), h(xi + 1, yi), u), lerp(h(xi, yi + 1), h(xi + 1, yi + 1), u), v);
  };
}

function loadImage(url) {
  return new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('load ' + url)); im.src = url; });
}
function readPixels(img) {
  const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0);
  return { canvas: c, ctx: g, id: g.getImageData(0, 0, c.width, c.height) };
}

// ------------------------------------------------------------------ 从透明通道量取板子轮廓
function measureOutline(id) {
  const { width: W, height: H, data } = id;
  const A = (r, x) => (x < 0 || x >= W) ? 0 : data[(r * W + x) * 4 + 3];
  const left = new Float64Array(H).fill(NaN), right = new Float64Array(H).fill(NaN);
  let rf = -1, rl = -1;
  for (let r = 0; r < H; r++) {
    let xl = -1, xr = -1;
    for (let x = 0; x < W; x++) if (A(r, x) >= 128) { xl = x; break; }
    if (xl < 0) continue;
    for (let x = W - 1; x >= xl; x--) if (A(r, x) >= 128) { xr = x; break; }
    left[r] = xl - 0.5 + (128 - A(r, xl - 1)) / Math.max(1, A(r, xl) - A(r, xl - 1));
    right[r] = xr + 0.5 + (A(r, xr) - 128) / Math.max(1, A(r, xr) - A(r, xr + 1));
    if (rf < 0) rf = r; rl = r;
  }
  const hwRaw = new Float64Array(H), cRaw = new Float64Array(H);
  for (let r = rf; r <= rl; r++) { hwRaw[r] = (right[r] - left[r]) / 2; cRaw[r] = (right[r] + left[r]) / 2; }
  // sigma 可以是函数：板身中段大幅平滑（去掉原图边缘的细小起伏），板头板尾处收小
  const gsmooth = (arr, sig) => {
    const out = new Float64Array(H);
    for (let r = rf; r <= rl; r++) {
      const sigma = typeof sig === 'function' ? sig(r) : sig, R = Math.ceil(sigma * 3);
      let s = 0, w = 0;
      for (let k = -R; k <= R; k++) { const rr = r + k; if (rr < rf || rr > rl) continue; const g = Math.exp(-k * k / (2 * sigma * sigma)); s += arr[rr] * g; w += g; }
      out[r] = s / w;
    }
    return out;
  };
  const hwS = gsmooth(hwRaw, (r) => lerp(2.0, 34, smoothstep(8, 280, Math.min(r - rf, rl - r)))), cS = gsmooth(cRaw, 24);
  // 板头/板尾：w² 对行号线性拟合（圆弧顶点），外推出真正的尖端
  const fit = (rows) => {
    let n = 0, sx = 0, sy = 0, sxx = 0, sxy = 0;
    for (const r of rows) { const y = hwRaw[r] * hwRaw[r]; n++; sx += r; sy += y; sxx += r * r; sxy += r * y; }
    const m = (n * sxy - sx * sy) / (n * sxx - sx * sx), b = (sy - m * sx) / n; return { m, b };
  };
  const rowsN = [], rowsT = [];
  for (let k = 1; k <= 12; k++) { rowsN.push(rf + k); rowsT.push(rl - k); }
  const fn = fit(rowsN), ft = fit(rowsT);
  const r0 = -fn.b / fn.m, r1 = -ft.b / ft.m;
  const samp = (arr, r) => { const rr = clamp(r, rf, rl); const i = Math.floor(rr), f = rr - i; return i >= rl ? arr[rl] : lerp(arr[i], arr[i + 1], f); };
  const hw = (r) => {
    const wn = Math.sqrt(Math.max(0, fn.m * r + fn.b)), wt = Math.sqrt(Math.max(0, ft.m * r + ft.b));
    const m = samp(hwS, r);
    if (r < (rf + rl) / 2) return lerp(wn, m, smoothstep(rf + 3, rf + 14, r));
    return lerp(wt, m, 1 - smoothstep(rl - 14, rl - 3, r));
  };
  const c = (r) => samp(cS, r);
  return { W, H, r0, r1, rf, rl, hw, c };
}

// ------------------------------------------------------------------ 贴图预处理：去掉边缘白边（内缩 + push-pull 填充）
function bleedFill(id, erode = 4) {
  const { width: W, height: H, data } = id;
  let m = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) m[i] = data[i * 4 + 3] >= 250 ? 1 : 0;
  // 方形腐蚀（可分离）
  const tmp = new Uint8Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { let v = 1; for (let k = -erode; k <= erode && v; k++) { const xx = x + k; if (xx < 0 || xx >= W || !m[y * W + xx]) v = 0; } tmp[y * W + x] = v; }
  const m2 = new Uint8Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { let v = 1; for (let k = -erode; k <= erode && v; k++) { const yy = y + k; if (yy < 0 || yy >= H || !tmp[yy * W + x]) v = 0; } m2[y * W + x] = v; }
  m = m2;
  // 金字塔
  const levels = [];
  let w = W, h = H, c = new Float32Array(W * H * 3), a = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) { a[i] = m[i]; c[i * 3] = data[i * 4]; c[i * 3 + 1] = data[i * 4 + 1]; c[i * 3 + 2] = data[i * 4 + 2]; }
  levels.push({ w, h, c, a });
  while (w > 1 || h > 1) {
    const nw = Math.max(1, Math.ceil(w / 2)), nh = Math.max(1, Math.ceil(h / 2));
    const nc = new Float32Array(nw * nh * 3), na = new Float32Array(nw * nh);
    for (let y = 0; y < nh; y++) for (let x = 0; x < nw; x++) {
      let sa = 0, sr = 0, sg = 0, sb = 0;
      for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
        const xx = 2 * x + dx, yy = 2 * y + dy; if (xx >= w || yy >= h) continue;
        const j = yy * w + xx, aa = a[j]; sa += aa; sr += c[j * 3] * aa; sg += c[j * 3 + 1] * aa; sb += c[j * 3 + 2] * aa;
      }
      const k = y * nw + x; na[k] = Math.min(1, sa);
      if (sa > 0) { nc[k * 3] = sr / sa; nc[k * 3 + 1] = sg / sa; nc[k * 3 + 2] = sb / sa; }
    }
    w = nw; h = nh; c = nc; a = na; levels.push({ w, h, c, a });
  }
  for (let l = levels.length - 2; l >= 0; l--) {
    const L0 = levels[l], L1 = levels[l + 1];
    for (let y = 0; y < L0.h; y++) for (let x = 0; x < L0.w; x++) {
      const k = y * L0.w + x, aa = L0.a[k]; if (aa >= 1) continue;
      const fx = clamp((x + 0.5) / 2 - 0.5, 0, L1.w - 1), fy = clamp((y + 0.5) / 2 - 0.5, 0, L1.h - 1);
      const x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(L1.w - 1, x0 + 1), y1 = Math.min(L1.h - 1, y0 + 1), tx = fx - x0, ty = fy - y0;
      for (let ch = 0; ch < 3; ch++) {
        const v = lerp(lerp(L1.c[(y0 * L1.w + x0) * 3 + ch], L1.c[(y0 * L1.w + x1) * 3 + ch], tx), lerp(L1.c[(y1 * L1.w + x0) * 3 + ch], L1.c[(y1 * L1.w + x1) * 3 + ch], tx), ty);
        L0.c[k * 3 + ch] = L0.c[k * 3 + ch] * aa + v * (1 - aa);
      }
      L0.a[k] = 1;
    }
  }
  const out = levels[0].c;
  for (let i = 0; i < W * H; i++) { data[i * 4] = out[i * 3]; data[i * 4 + 1] = out[i * 3 + 1]; data[i * 4 + 2] = out[i * 3 + 2]; data[i * 4 + 3] = 255; }
  return id;
}

// ------------------------------------------------------------------ 侧面板型（弯曲）：曲率积分，长度守恒
function makeProfile({ camber = 0.008, kickH = 0.05, kickLen = 0.155, delta = 0.035, T0 = 0.011, taper = 0.4, flat = false } = {}) {
  const D = L / 2, dc = D - kickLen, N = 3000, dd = D / N;
  const integrate = (kc, kk) => {
    const th = new Float64Array(N + 1), x = new Float64Array(N + 1), y = new Float64Array(N + 1);
    for (let i = 1; i <= N; i++) {
      const d = (i - 0.5) * dd;
      const k = flat ? 0 : lerp(-kc, kk, smoothstep(dc - delta, dc + delta, d));
      th[i] = th[i - 1] + k * dd;
      const tm = (th[i] + th[i - 1]) / 2;
      x[i] = x[i - 1] + Math.cos(tm) * dd; y[i] = y[i - 1] + Math.sin(tm) * dd;
    }
    let ymin = Infinity, imin = 0; for (let i = 0; i <= N; i++) if (y[i] < ymin) { ymin = y[i]; imin = i; }
    for (let i = 0; i <= N; i++) y[i] -= ymin;
    return { th, x, y, camber: y[0], tip: y[N], contact: imin * dd };
  };
  let kc = 2 * camber / (dc * dc), kk = 3.5, P = integrate(kc, kk);
  if (!flat) for (let it = 0; it < 40; it++) {
    if (camber > 0) kc *= camber / Math.max(1e-6, P.camber);
    kk *= Math.pow(kickH / Math.max(1e-6, P.tip), 0.7);
    P = integrate(kc, kk);
  }
  const at = (l) => {
    const d = l - D, ad = Math.abs(d), f = clamp(ad / dd, 0, N), i = Math.min(N - 1, Math.floor(f)), t = f - i;
    const x = lerp(P.x[i], P.x[i + 1], t), y = lerp(P.y[i], P.y[i + 1], t), th = lerp(P.th[i], P.th[i + 1], t);
    return d >= 0 ? { x, y, th } : { x: -x, y, th: -th };
  };
  const T = (l) => T0 * (1 - taper * smoothstep(dc - 0.12, D, Math.abs(l - D)));
  return { at, T, info: { camber: P.camber, tip: P.tip, contact: P.contact, kc, kk } };
}

// ------------------------------------------------------------------ 平面轮廓（米），按弧长采样
function makePlan(outTop, { K = 520 } = {}) {
  const pxToM = L / (outTop.r1 - outTop.r0);
  const waistPx = outTop.hw((outTop.r0 + outTop.r1) / 2) * 2;
  const wScale = WAIST / (waistPx * pxToM);
  const hwM = (l) => outTop.hw(outTop.r0 + clamp(l / L, 0, 1) * (outTop.r1 - outTop.r0)) * pxToM * wScale;
  // 两端加密的细网格
  const NF = 12000, fl = new Float64Array(NF + 1), fz = new Float64Array(NF + 1), arc = new Float64Array(NF + 1);
  for (let j = 0; j <= NF; j++) { fl[j] = L * (0.5 - 0.5 * Math.cos(Math.PI * j / NF)); fz[j] = (j === 0 || j === NF) ? 0 : hwM(fl[j]); }
  for (let j = 1; j <= NF; j++) arc[j] = arc[j - 1] + Math.hypot(fl[j] - fl[j - 1], fz[j] - fz[j - 1]);
  const P = [];
  let j = 0;
  for (let k = 0; k <= K; k++) {
    const s = arc[NF] * k / K;
    while (j < NF - 1 && arc[j + 1] < s) j++;
    const t = clamp((s - arc[j]) / Math.max(1e-12, arc[j + 1] - arc[j]), 0, 1);
    P.push({ l: lerp(fl[j], fl[j + 1], t), z: lerp(fz[j], fz[j + 1], t) });
  }
  P[0] = { l: 0, z: 0 }; P[K] = { l: L, z: 0 };
  for (let k = 0; k <= K; k++) {
    let tl, tz;
    if (k === 0) { tl = 0; tz = 1; } else if (k === K) { tl = 0; tz = -1; }
    else { tl = P[k + 1].l - P[k - 1].l; tz = P[k + 1].z - P[k - 1].z; const n = Math.hypot(tl, tz); tl /= n; tz /= n; }
    P[k].nl = -tz; P[k].nz = tl;   // 外法线 = 切线逆时针转 90°
  }
  // 闭合环：右半 0..K，左半 K-1..1（镜像）
  const loop = [];
  for (let k = 0; k <= K; k++) loop.push(P[k]);
  for (let k = K - 1; k >= 1; k--) loop.push({ l: P[k].l, z: -P[k].z, nl: P[k].nl, nz: -P[k].nz });
  return { P, K, loop, hwM, wScale, pxToM };
}

// UV 映射：板面（俯视）/板底（仰视）都不镜像
function makeUV(out, plan, { view = 'above', insetW = 0.03, insetPx = 9 } = {}) {
  const insetL = 2 * insetPx / (out.r1 - out.r0);
  const sgn = view === 'above' ? -1 : 1;
  return (l, z) => {
    const s = l / L;
    const r = out.r0 + (0.5 + (s - 0.5) * (1 - insetL)) * (out.r1 - out.r0);
    const hw = plan.hwM(l);
    const tau = hw > 1e-7 ? clamp(z / hw, -1, 1) * sgn : 0;
    const col = out.c(r) + tau * out.hw(r) * (1 - insetW);
    return [col / out.W, 1 - r / out.H];
  };
}

// ------------------------------------------------------------------ 网格构建
function toWorld(prof, l, z, h) {
  const p = prof.at(l), s = Math.sin(p.th), c = Math.cos(p.th);
  return [p.x - h * s, p.y + h * c, z];
}
function nToWorld(prof, l, nl, nz, nu) {
  const p = prof.at(l), s = Math.sin(p.th), c = Math.cos(p.th);
  const v = new THREE.Vector3(nl * c - nu * s, nl * s + nu * c, nz); return v.normalize();
}
function finishGeo(pos, nor, uv, idx) {
  // 按期望法线修正三角形绕序
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t], b = idx[t + 1], c = idx[t + 2];
    const ax = pos[a * 3], ay = pos[a * 3 + 1], az = pos[a * 3 + 2];
    const ux = pos[b * 3] - ax, uy = pos[b * 3 + 1] - ay, uz = pos[b * 3 + 2] - az;
    const vx = pos[c * 3] - ax, vy = pos[c * 3 + 1] - ay, vz = pos[c * 3 + 2] - az;
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    const en = [nor[a * 3] + nor[b * 3] + nor[c * 3], nor[a * 3 + 1] + nor[b * 3 + 1] + nor[c * 3 + 1], nor[a * 3 + 2] + nor[b * 3 + 2] + nor[c * 3 + 2]];
    if (nx * en[0] + ny * en[1] + nz * en[2] < 0) { idx[t + 1] = c; idx[t + 2] = b; }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}
// 顶/底面：内缩 d 的轮廓所围区域；hFn(l) 给出高度；up=true 法线朝上
function buildCap(plan, prof, { d, hFn, up = true, uvFn, cols = 28 }) {
  const pos = [], nor = [], uv = [], idx = [], { P, K } = plan;
  for (let k = 0; k <= K; k++) {
    const ql = P[k].l - P[k].nl * d, qz = Math.max(0, P[k].z - P[k].nz * d);
    const h = hFn(ql);
    const n = nToWorld(prof, ql, 0, 0, up ? 1 : -1);
    for (let j = 0; j <= cols; j++) {
      const z = -qz + 2 * qz * j / cols;
      pos.push(...toWorld(prof, ql, z, h)); nor.push(n.x, n.y, n.z);
      uv.push(...(uvFn ? uvFn(ql, z) : [ql / L, 0.5 + z / 0.4]));
    }
  }
  const C = cols + 1;
  for (let k = 0; k < K; k++) for (let j = 0; j < cols; j++) {
    const a = k * C + j, b = a + 1, c = a + C, e = c + 1;
    idx.push(a, c, b, b, c, e);
  }
  return finishGeo(pos, nor, uv, idx);
}
// 沿闭合轮廓挤出截面。strip: [{d, h0, hT, no, nu}]，h = h0 + hT*T(l)
function buildRing(plan, prof, strip, { uScale = 1 } = {}) {
  const pos = [], nor = [], uv = [], idx = [], loop = plan.loop, M = loop.length, S = strip.length;
  let acc = 0;
  for (let m = 0; m <= M; m++) {
    const p = loop[m % M];
    if (m > 0) { const q = loop[m - 1]; acc += Math.hypot(p.l - q.l, p.z - q.z); }
    for (let s = 0; s < S; s++) {
      const sp = strip[s];
      const l = p.l - p.nl * sp.d, z = p.z - p.nz * sp.d, h = sp.h0 + sp.hT * prof.T(l);
      pos.push(...toWorld(prof, l, z, h));
      const n = nToWorld(prof, l, p.nl * sp.no, p.nz * sp.no, sp.nu); nor.push(n.x, n.y, n.z);
      uv.push(acc * uScale, s / (S - 1));
    }
  }
  for (let m = 0; m < M; m++) for (let s = 0; s < S - 1; s++) {
    const a = m * S + s, b = a + 1, c = a + S, e = c + 1;
    idx.push(a, c, b, b, c, e);
  }
  return finishGeo(pos, nor, uv, idx);
}
const arcPts = (cd, ch, r, a0, a1, n, mapN) => {
  // 截面圆角：中心 (cd, ch)，法线角从 a0 到 a1（角度以 (out, up) 平面计，0=朝外，90=朝上）
  const out = [];
  for (let i = 0; i <= n; i++) {
    const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180, no = Math.cos(a), nu = Math.sin(a);
    out.push({ d: cd - r * no, h0: ch.h0 + r * nu, hT: ch.hT, no, nu });
  }
  return out;
};

// ------------------------------------------------------------------ 程序化贴图
function canvasTex(w, h, draw, { srgb = true, repeat = false } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h, c);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 16; t.needsUpdate = true;
  return t;
}
function roughnessTex(seed = 1, lo = 0.82, hi = 1.0) {
  return canvasTex(512, 512, (g, w, h) => {
    const id = g.createImageData(w, h), n1 = valueNoise(seed), n2 = valueNoise(seed + 7);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const v = 0.6 * n1(x / 90, y / 90) + 0.3 * n2(x / 23, y / 23) + 0.1 * hash2(x, y);
      const r = Math.round(255 * lerp(lo, hi, v)); const i = (y * w + x) * 4; id.data[i] = id.data[i + 1] = id.data[i + 2] = r; id.data[i + 3] = 255;
    }
    g.putImageData(id, 0, 0);
  }, { srgb: false, repeat: true });
}

// ------------------------------------------------------------------ 环境光（摄影棚柔光箱），按相机方位旋转
function makeEnv(renderer, { yaw = 0, key = 4.5, rim = 5, rimL = 0, top = 1.2, fill = 0.5, front = 0, back = 0, backPos = [0, 8, -12], backSize = [16, 3.5], extra = [], dome = [0.20, 0.17, 0.05], keyPos = [-9, 8, 9], rimPos = [12, 3, -6], rimLPos = [-12, 2, -7], frontPos = [-2, 3, 15] } = {}) {
  const s = new THREE.Scene();
  const grp = new THREE.Group(); s.add(grp);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { cTop: { value: new THREE.Color(0xE8E0F0).multiplyScalar(dome[0]) }, cMid: { value: new THREE.Color(0xB8A9CF).multiplyScalar(dome[1]) }, cBot: { value: new THREE.Color(0x2C2E57).multiplyScalar(dome[2]) } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'uniform vec3 cTop, cMid, cBot; varying vec3 vP; void main(){ float y = vP.y; vec3 c = y > 0.0 ? mix(cMid, cTop, smoothstep(0.0, 0.8, y)) : mix(cMid, cBot, smoothstep(0.0, 0.5, -y)); gl_FragColor = vec4(c, 1.0); }'
  });
  grp.add(new THREE.Mesh(new THREE.SphereGeometry(40, 64, 32), mat));
  // 柔光箱：边缘羽化的发光面
  const box = (w, h, color, inten, p, feather = 0.35) => {
    if (inten <= 0) return;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.ShaderMaterial({
      side: THREE.DoubleSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: { c: { value: new THREE.Color(color).multiplyScalar(inten) }, f: { value: feather } },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: 'uniform vec3 c; uniform float f; varying vec2 vUv; void main(){ vec2 d = min(vUv, 1.0 - vUv); float a = smoothstep(0.0, f * 0.5, d.x) * smoothstep(0.0, f * 0.5, d.y); gl_FragColor = vec4(c * a, 1.0); }'
    }));
    m.position.set(...p); m.lookAt(0, 0, 0); grp.add(m);
  };
  box(11, 8, 0xFFE9E4, key, keyPos, 0.6);
  box(2.4, 15, 0xB9B4FF, rim, rimPos, 0.5);
  box(2.0, 12, 0xE8C8D8, rimL, rimLPos, 0.5);
  box(14, 12, 0xE8E0F0, top, [0, 15, 0], 0.8);
  box(12, 7, 0xF3EFE4, front, frontPos, 0.9);
  box(16, 3, 0xE8A9B5, fill, [3, -5, 13], 0.7);
  box(backSize[0], backSize[1], 0xF3EFE4, back, backPos, 0.9);
  for (const x of extra) box(...x);
  grp.rotation.y = yaw;
  const pm = new THREE.PMREMGenerator(renderer);
  const rt = pm.fromScene(s, 0.015);
  pm.dispose();
  return rt.texture;
}

// ------------------------------------------------------------------ 主流程
async function main() {
  const W = innerWidth, H = innerHeight, DPR = devicePixelRatio || 1;
  const renderer = new THREE.WebGLRenderer({ antialias: PASS !== 'depth', alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(DPR); renderer.setSize(W, H);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = qn('exp', 1.0);
  renderer.setClearColor(0x000000, 0);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const maxAniso = renderer.capabilities.getMaxAnisotropy();

  const [imTop, imBase] = await Promise.all([loadImage(ASSET + 'nuage-top@4x.png'), loadImage(ASSET + 'nuage-base@4x.png')]);
  const pxTop = readPixels(imTop), pxBase = readPixels(imBase);
  const outTop = measureOutline(pxTop.id), outBase = measureOutline(pxBase.id);
  const mkTex = (px) => {
    bleedFill(px.id); px.ctx.putImageData(px.id, 0, 0);
    const t = new THREE.CanvasTexture(px.canvas); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = maxAniso;
    t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; return t;
  };
  const texTop = mkTex(pxTop), texBase = mkTex(pxBase);
  const plan = makePlan(outTop);
  const ctx = { renderer, W, H, DPR, THREE, outTop, outBase, plan, texTop, texBase, maxAniso };

  const shot = SHOTS[SHOT];
  await shot(ctx);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  window.__READY = true;
}

// ------------------------------------------------------------------ 雪板
function boardMaterials(ctx, o = {}) {
  const rough = roughnessTex(3, 0.8, 1.0);
  rough.repeat.set(1, 4);
  const top = new THREE.MeshPhysicalMaterial({
    map: ctx.texTop, roughness: o.topRough ?? 0.42, roughnessMap: rough, metalness: o.topMetal ?? 0.0,
    clearcoat: o.clearcoat ?? 1.0, clearcoatRoughness: o.ccRough ?? 0.05, specularIntensity: 0.6, dithering: true,
  });
  const base = new THREE.MeshPhysicalMaterial({
    map: ctx.texBase, roughness: o.baseRough ?? 0.36, roughnessMap: rough, metalness: 0.0,
    clearcoat: 0.35, clearcoatRoughness: 0.28, specularIntensity: 0.55, dithering: true,
  });
  const side = new THREE.MeshPhysicalMaterial({ color: 0x1b1b24, roughness: 0.3, metalness: 0.0, clearcoat: 0.8, clearcoatRoughness: 0.12, dithering: true });
  const steel = new THREE.MeshPhysicalMaterial({ color: 0xd9d9e2, roughness: 0.25, metalness: 1.0, dithering: true });
  return { top, base, side, steel };
}
function buildBoard(ctx, prof, mats, o = {}) {
  const { plan, outTop, outBase } = ctx;
  const e = o.edgeW ?? 0.0026, eH = o.edgeH ?? 0.0022, bev = o.bevel ?? 0.0018, rc = 0.0005;
  const g = new THREE.Group();
  const uvTop = makeUV(outTop, plan, { view: 'above' });
  const uvBase = makeUV(outBase, plan, { view: o.baseView ?? 'below' });
  const top = new THREE.Mesh(buildCap(plan, prof, { d: bev, hFn: (l) => prof.T(l), up: true, uvFn: uvTop }), mats.top);
  const base = new THREE.Mesh(buildCap(plan, prof, { d: e, hFn: () => 0, up: false, uvFn: uvBase }), mats.base);
  const steelStrip = [
    { d: e, h0: 0, hT: 0, no: 0, nu: -1 },
    ...arcPts(rc, { h0: rc, hT: 0 }, rc, -90, 0, 4),
    { d: 0, h0: eH, hT: 0, no: 1, nu: 0 },
  ];
  const sideStrip = [
    { d: 0, h0: eH, hT: 0, no: 1, nu: 0 },
    ...arcPts(bev, { h0: -bev, hT: 1 }, bev, 0, 90, 6),
  ];
  const steel = new THREE.Mesh(buildRing(plan, prof, steelStrip), mats.steel);
  const side = new THREE.Mesh(buildRing(plan, prof, sideStrip), mats.side);
  for (const m of [top, base, steel, side]) { m.castShadow = true; m.receiveShadow = true; g.add(m); }
  g.userData = { top, base, steel, side };
  return g;
}

function placeLights(scene, cam, target, o = {}) {
  // 相机相对坐标：x=画面右，y=上，z=朝向相机
  cam.updateMatrixWorld();
  const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0).normalize();
  const up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1).normalize();
  const fwd = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 2).normalize().negate();
  const rel = (x, y, z) => target.clone().addScaledVector(right, x).addScaledVector(up, y).addScaledVector(fwd, -z);
  const hemi = new THREE.HemisphereLight(0xE8E0F0, 0x2C2E57, o.hemi ?? 0.45); scene.add(hemi);
  const key = new THREE.DirectionalLight(0xFFE9E4, o.key ?? 2.2); key.position.copy(rel(...(o.keyPos ?? [-3, 3.2, 2.4]))); key.target.position.copy(target);
  scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xB9B4FF, o.rim ?? 2.4); rim.position.copy(rel(...(o.rimPos ?? [3.5, 1.2, -2.5]))); rim.target.position.copy(target);
  scene.add(rim, rim.target);
  return { key, rim, hemi, rel };
}
function setShadow(light, center, radius, { size = 4096, bias = -0.0002, normalBias = 0.002, radiusBlur = 4 } = {}) {
  light.castShadow = true;
  const s = light.shadow; s.mapSize.set(size, size); s.bias = bias; s.normalBias = normalBias; s.radius = radiusBlur;
  const dir = new THREE.Vector3().subVectors(light.position, light.target.position).normalize();
  light.position.copy(center).addScaledVector(dir, radius * 3); light.target.position.copy(center);
  const c = s.camera; c.left = -radius; c.right = radius; c.top = radius; c.bottom = -radius; c.near = radius * 0.5; c.far = radius * 6; c.updateProjectionMatrix();
}
function camYaw(cam, target) { return Math.atan2(cam.position.x - target.x, cam.position.z - target.z); }

function shadowCatcher(size, opacity = 0.35) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.ShadowMaterial({ opacity, color: 0x15172E }));
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true; return m;
}
function project(cam, v, W, H) { const p = v.clone().project(cam); return [Math.round((p.x + 1) / 2 * W * 10) / 10, Math.round((1 - p.y) / 2 * H * 10) / 10]; }

// 解析式接触阴影：根据板底离地高度做多层模糊（板子静置在地面时使用）
// heightFn(l): 板子最低表面在 l 处离地高度；xFn(l): l 处在地面上的 x 坐标
function contactShadow(plan, { heightFn, xFn, x0 = -0.95, x1 = 0.95, z0 = -0.36, z1 = 0.36, res = 0.0015, layers = [[0.003, 2, 0.75], [0.02, 9, 0.45], [1.0, 34, 0.28]], color = '#15172E' } = {}) {
  const w = Math.round((x1 - x0) / res), h = Math.round((z1 - z0) / res);
  // l(x) 反查表
  const NL = 4000, lx = []; for (let i = 0; i <= NL; i++) { const l = L * i / NL; lx.push([xFn(l), l]); }
  lx.sort((a, b) => a[0] - b[0]);
  const lOfX = (x) => { let lo = 0, hi = lx.length - 1; if (x < lx[0][0] || x > lx[hi][0]) return -1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (lx[m][0] < x) lo = m; else hi = m; } const t = (x - lx[lo][0]) / Math.max(1e-9, lx[hi][0] - lx[lo][0]); return lerp(lx[lo][1], lx[hi][1], t); };
  const out = document.createElement('canvas'); out.width = w; out.height = h; const og = out.getContext('2d');
  const colHW = new Float32Array(w), colH = new Float32Array(w);
  for (let i = 0; i < w; i++) { const x = x0 + (i + 0.5) * res, l = lOfX(x); colHW[i] = l < 0 ? -1 : plan.hwM(l); colH[i] = l < 0 ? 1 : heightFn(l); }
  for (const [h0, blurPx, k] of layers) {
    const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const id = g.createImageData(w, h);
    for (let i = 0; i < w; i++) {
      if (colHW[i] < 0) continue; const a = Math.exp(-Math.max(0, colH[i]) / h0);
      for (let j = 0; j < h; j++) { const z = z0 + (j + 0.5) * res; if (Math.abs(z) < colHW[i]) { const q = (j * w + i) * 4; id.data[q + 3] = Math.round(255 * a); } }
    }
    g.putImageData(id, 0, 0);
    og.save(); og.filter = `blur(${blurPx}px)`; og.globalAlpha = k; og.drawImage(c, 0, 0); og.restore();
  }
  // 染色
  og.globalCompositeOperation = 'source-in'; og.fillStyle = color; og.fillRect(0, 0, w, h);
  const t = new THREE.CanvasTexture(out); t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, z1 - z0), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, toneMapped: false }));
  m.rotation.x = -Math.PI / 2; m.position.set((x0 + x1) / 2, 0.0003, (z0 + z1) / 2); m.renderOrder = -1;
  return m;
}
// 竖立的板：返回把板局部坐标(长度X/板面法线Y/宽Z)转到世界的四元数。face='top' 板面朝相机，'base' 板底朝相机
function standQuat(face, tiltDeg, turnDeg, yawDeg = 0) {
  const xw = new THREE.Vector3(0, -1, 0), yw = new THREE.Vector3(0, 0, face === 'top' ? 1 : -1);
  const zw = new THREE.Vector3().crossVectors(xw, yw);
  const q = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(xw, yw, zw));
  const turn = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), turnDeg * Math.PI / 180);   // 绕板长轴（竖直）转
  const tilt = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), -tiltDeg * Math.PI / 180);  // 画面内倾斜（正值顶部向右）
  const yaw = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), yawDeg * Math.PI / 180);    // 前后俯仰
  return tilt.multiply(yaw).multiply(turn).multiply(q);
}


async function flatShot(ctx, face) {
  const { renderer, W, H } = ctx;
  const scene = new THREE.Scene();
  const prof = makeProfile({ camber: 0.008, kickH: 0.05, T0: 0.0115, taper: 0.4 });
  const mats = boardMaterials(ctx);
  const b = buildBoard(ctx, prof, mats);
  const g = new THREE.Group(); g.add(b); scene.add(g);
  let heightFn;
  if (face === 'base') {
    // 翻面：板头板尾着地，中段悬空
    let top = 0; for (let i = 0; i <= 200; i++) { const l = L * i / 200; top = Math.max(top, prof.at(l).y + prof.T(l)); }
    b.rotation.x = Math.PI; b.position.y = top;
    heightFn = (l) => top - (prof.at(l).y + prof.T(l));
  } else heightFn = (l) => prof.at(l).y;
  const cs = contactShadow(ctx.plan, { heightFn, xFn: (l) => prof.at(l).x, layers: [[0.0025, 2, 0.85], [0.015, 8, 0.5], [1, 26, 0.3]] });
  g.add(cs);
  // 板底：板头在左下，vamei 字母正立；板面：板头在右上，月亮画面与 NUAGE 竖排字朝上
  g.rotation.y = qn('yaw', face === 'top' ? 215 : 35) * Math.PI / 180;
  const fov = qn('fov', 22), elev = qn('elev', 35) * Math.PI / 180;
  const cam = new THREE.PerspectiveCamera(fov, W / H, 0.3, 30);
  const dist = qn('dist', 2.85);
  const tgt = new THREE.Vector3(qn('tx', -0.075), 0.02, qn('tz', 0.03));
  cam.position.set(tgt.x, tgt.y + Math.sin(elev) * dist, tgt.z + Math.cos(elev) * dist); cam.lookAt(tgt);
  scene.environment = makeEnv(renderer, { yaw: camYaw(cam, tgt), key: qn('ek', 5), rim: qn('er', 6), rimL: 2, top: qn('et', 1.0), fill: 0.6, front: qn('ef', 1.2), back: qn('eb', 3.5), backPos: [qn('bx', 2), qn('by', 7), -11.5], dome: [0.22, 0.2, 0.3] });
  const Lg = placeLights(scene, cam, tgt, { key: qn('lk', 1.8), rim: qn('lr', 2.2), hemi: 0.35, keyPos: [-2.5, 3, 1.0], rimPos: [3, 1.2, -2.5] });
  renderer.render(scene, cam);
  const P = (l) => { const v = new THREE.Vector3(...toWorld(prof, l, 0, 0)); b.localToWorld(v); return project(cam, v, W, H); };
  console.warn('ANCHORS ' + JSON.stringify({ nose: P(0), tail: P(L), center: P(L / 2) }));
}


// ------------------------------------------------------------------ 结构分层用的构件
function slabProf(prof, t, taper = 0.35) {
  const D = L / 2;
  return { at: prof.at, T: (l) => t * (1 - taper * smoothstep(D - 0.25, D, Math.abs(l - D))) };
}
// 通用板层：外轮廓内缩 d，厚 t；ring 可选一圈不同材质的边框（如 ABS 侧壁）
function buildSlab(ctx, prof, { d = 0, t, bev = 0.0008, taper = 0.35, topMat, sideMat, botMat, uvTop, uvBot, ringW = 0, ringMat }) {
  const { plan } = ctx, sp = slabProf(prof, t, taper), g = new THREE.Group();
  const add = (geo, mat) => { const m = new THREE.Mesh(geo, mat); m.castShadow = m.receiveShadow = true; g.add(m); return m; };
  const dTop = d + bev + ringW;
  add(buildCap(plan, sp, { d: dTop, hFn: (l) => sp.T(l), up: true, uvFn: uvTop }), topMat);
  if (botMat) add(buildCap(plan, sp, { d, hFn: () => 0, up: false, uvFn: uvBot }), botMat);
  const wall = [{ d, h0: 0, hT: 0, no: 1, nu: 0 }, ...arcPts(d + bev, { h0: -bev, hT: 1 }, bev, 0, 90, 4)];
  if (ringW > 0) wall.push({ d: dTop, h0: 0, hT: 1, no: 0, nu: 1 });
  add(buildRing(plan, sp, wall), ringMat || sideMat);
  return g;
}
// 钢刃：沿轮廓的矩形截面环
function buildEdgeLoop(ctx, prof, { d = 0, w = 0.004, h = 0.005, mat }) {
  const sp = { at: prof.at, T: () => h }, g = new THREE.Group();
  const strips = [
    [{ d, h0: 0, hT: 0, no: 1, nu: 0 }, { d, h0: h, hT: 0, no: 1, nu: 0 }],
    [{ d, h0: h, hT: 0, no: 0, nu: 1 }, { d: d + w, h0: h, hT: 0, no: 0, nu: 1 }],
    [{ d: d + w, h0: h, hT: 0, no: -1, nu: 0 }, { d: d + w, h0: 0, hT: 0, no: -1, nu: 0 }],
  ];
  for (const st of strips) { const m = new THREE.Mesh(buildRing(ctx.plan, sp, st, { uScale: 4 }), mat); m.castShadow = m.receiveShadow = true; g.add(m); }
  return g;
}
// 碳纤条：沿板长方向的细长条，zFn(l) 给出横向位置
function buildStrip(prof, zFn, { l0, l1, w = 0.006, t = 0.004, n = 160, mat }) {
  const pos = [], nor = [], uv = [], idx = [];
  const faces = [[-1, 1, 1, 1, 0, 1], [1, 1, 1, 0, 1, 0], [-1, 0, -1, 1, -1, 0]]; // (z端a, 高a, z端b, 高b, 法线z, 法线up)
  let base = 0;
  for (const [za, ha, zb, hb, nz, nu] of faces) {
    for (let i = 0; i <= n; i++) {
      const l = lerp(l0, l1, i / n), zc = zFn(l);
      // 两端收圆
      const e = Math.min(1, Math.min(l - l0, l1 - l) / 0.012), ww = w * (0.35 + 0.65 * Math.sqrt(Math.max(0, e)));
      for (const [zz, hh] of [[za, ha], [zb, hb]]) {
        pos.push(...toWorld(prof, l, zc + zz * ww / 2, hh * t));
        const nn = nToWorld(prof, l, 0, nz, nu); nor.push(nn.x, nn.y, nn.z); uv.push(i / n, zz > 0 ? 1 : 0);
      }
    }
    for (let i = 0; i < n; i++) { const a = base + i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
    base += (n + 1) * 2;
  }
  return finishGeo(pos, nor, uv, idx);
}
function weaveTex() {
  // 三轴玻纤：0° 与 ±45° 三组纤维束（可平铺）
  return canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = 'rgb(105,105,105)'; g.fillRect(0, 0, w, h);
    const P = 1024 / 12;
    g.lineCap = 'butt';
    const stroke = (alpha, width) => { g.strokeStyle = `rgba(255,255,255,${alpha})`; g.lineWidth = width; };
    for (let pass = 0; pass < 2; pass++) {
      stroke(pass ? 0.9 : 0.35, pass ? 2.2 : 9);
      for (let k = -24; k <= 36; k++) {
        g.beginPath(); g.moveTo(k * P, 0); g.lineTo(k * P + h, h); g.stroke();
        g.beginPath(); g.moveTo(k * P, 0); g.lineTo(k * P - h, h); g.stroke();
      }
      stroke(pass ? 0.95 : 0.4, pass ? 2.6 : 10);
      for (let k = 0; k <= 24; k++) { g.beginPath(); g.moveTo(0, k * P / 2 + P / 4); g.lineTo(w, k * P / 2 + P / 4); g.stroke(); }
    }
    const id = g.getImageData(0, 0, w, h);
    for (let i = 0; i < w * h; i++) { const v = id.data[i * 4] + (hash2(i % w, (i / w) | 0) - 0.5) * 18; id.data[i * 4] = id.data[i * 4 + 1] = id.data[i * 4 + 2] = clamp(v, 0, 255); }
    g.putImageData(id, 0, 0);
  }, { srgb: false, repeat: true });
}
function woodTex() {
  // 白杨木芯：纵向拼条，浅奶油色，细直纹
  return canvasTex(4096, 512, (g, w, h) => {
    const id = g.createImageData(w, h), R = rng(11), n1 = valueNoise(5), n2 = valueNoise(9);
    const strips = 15, tones = [];
    for (let i = 0; i < strips; i++) tones.push([lerp(218, 238, R()), lerp(200, 222, R()), lerp(160, 186, R())]);
    const seeds = []; for (let i = 0; i < strips; i++) seeds.push(R() * 1000);
    for (let y = 0; y < h; y++) {
      const sf = y / h * strips, si = Math.min(strips - 1, Math.floor(sf)), sv = sf - si;
      const tone = tones[si], sd = seeds[si];
      const glue = Math.min(sv, 1 - sv) < 0.018 ? 1 : 0;
      for (let x = 0; x < w; x++) {
        const u = x / w;
        const wave = n1(u * 6 + sd, sv * 2) * 3.0;
        const grain = Math.sin((sv * 26 + wave + n2(u * 40 + sd, sv * 8) * 0.6) * Math.PI * 2);
        const fine = Math.pow(Math.abs(grain), 10);
        const blot = n1(u * 3 + sd * 2, sv * 1.5 + 7) - 0.5;
        let k = 1 - 0.13 * fine + 0.06 * blot + (hash2(x, y) - 0.5) * 0.025;
        if (glue) k *= 0.82;
        const i = (y * w + x) * 4;
        id.data[i] = clamp(tone[0] * k, 0, 255); id.data[i + 1] = clamp(tone[1] * k, 0, 255); id.data[i + 2] = clamp(tone[2] * k * 0.98, 0, 255); id.data[i + 3] = 255;
      }
    }
    g.putImageData(id, 0, 0);
  });
}

const SHOTS = {

  // 4. 板头微距：低机位，浅景深（景深与背景在 Python 里合成：需要 pass=color 和 pass=depth 两张）
  async nose(ctx) {
    const { renderer, W, H } = ctx;
    const scene = new THREE.Scene();
    const prof = makeProfile({ camber: 0.008, kickH: 0.05, T0: 0.0115, taper: 0.4 });
    const mats = boardMaterials(ctx, { ccRough: 0.03 });
    const b = buildBoard(ctx, prof, mats, { edgeW: 0.0026, edgeH: 0.0022, bevel: 0.0018 });
    const g = new THREE.Group(); g.add(b); scene.add(g);
    g.rotation.set(qn('rx', 0) * Math.PI / 180, qn('ry', 0) * Math.PI / 180, qn('rz', 0) * Math.PI / 180);
    const cam = new THREE.PerspectiveCamera(qn('fov', 36), W / H, 0.05, 10);
    cam.position.set(qn('cx', -0.12), qn('cy', 0.06), qn('cz', 0.24));
    const tgt = new THREE.Vector3(qn('tx', -0.6), qn('ty', 0.035), qn('tz', -0.05));
    cam.lookAt(tgt);
    if (PASS === 'depth') {
      const near = 0.05, far = 3.0;
      scene.overrideMaterial = new THREE.ShaderMaterial({
        uniforms: { near: { value: near }, far: { value: far } },
        vertexShader: 'varying float vZ; void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.0); vZ = -mv.z; gl_Position = projectionMatrix * mv; }',
        fragmentShader: 'uniform float near, far; varying float vZ; void main(){ float d = clamp((vZ - near) / (far - near), 0.0, 1.0) * 255.0; gl_FragColor = vec4(floor(d) / 255.0, fract(d), 0.0, 1.0); }',
        side: THREE.DoubleSide,
      });
      renderer.toneMapping = THREE.NoToneMapping; renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
      renderer.render(scene, cam);
    } else {
      renderer.toneMappingExposure = qn('exp', 0.82);
      scene.environment = makeEnv(renderer, { yaw: camYaw(cam, tgt), key: qn('ek', 3), rim: qn('er', 9), rimL: qn('erl', 6), top: qn('et', 1.0), fill: 0.3, front: qn('ef', 0.8), back: qn('eb', 2), backPos: [qn('bx', -2), qn('by', 5), -12], dome: [0.12, 0.1, 0.06] });
      const Lg = placeLights(scene, cam, tgt, { key: qn('lk', 1.6), rim: qn('lr', 3.5), hemi: 0.2, keyPos: [-1.5, 3, 1.5], rimPos: [2.5, 1.2, -2.5] });
      const rim2 = new THREE.DirectionalLight(0xB9B4FF, qn('lr2', 3.0)); rim2.position.copy(Lg.rel(-3, 0.8, -2.2)); rim2.target.position.copy(tgt); scene.add(rim2, rim2.target);
      // 逆光：板头后上方的暮粉色轮廓光
      const bl = new THREE.DirectionalLight(0xE8A9B5, qn('lbk', 3)); bl.position.copy(Lg.rel(qn('bkx', 0.4), qn('bky', 1.0), -3)); bl.target.position.copy(tgt); scene.add(bl, bl.target);
      renderer.render(scene, cam);
    }
    g.updateMatrixWorld(true); cam.updateMatrixWorld();
    const fp = new THREE.Vector3(...toWorld(prof, qn('fl', 0.105) * L, 0, prof.T(qn('fl', 0.105) * L))); g.localToWorld(fp);
    const vz = -fp.clone().applyMatrix4(cam.matrixWorldInverse).z;
    console.warn('FOCUS ' + JSON.stringify({ z: vz, px: project(cam, fp, W, H) }));
  },

  // 3. 结构爆炸图
  async layers(ctx) {
    const { renderer, W, H, plan, outTop, outBase } = ctx;
    const scene = new THREE.Scene();
    const prof = makeProfile({ camber: 0.006, kickH: 0.045, T0: 0.011, taper: 0.4 });
    const metalTop = new THREE.MeshPhysicalMaterial({ map: ctx.texTop, metalness: 0.45, roughness: 0.5, roughnessMap: roughnessTex(4, 0.85, 1), dithering: true });
    const topEdge = new THREE.MeshPhysicalMaterial({ color: 0xC9C3D3, metalness: 0.5, roughness: 0.4, dithering: true });
    const wv = weaveTex(); wv.repeat.set(L / 0.13, 0.4 / 0.13);
    const glass = new THREE.MeshPhysicalMaterial({ color: 0xFFFFFF, emissive: 0xE8E4F4, emissiveIntensity: qn('ge', 0.3), alphaMap: wv, transparent: true, opacity: 1, roughness: 0.3, metalness: 0, clearcoat: 0.6, side: THREE.DoubleSide, depthWrite: false, dithering: true });
    const glassEdge = new THREE.MeshPhysicalMaterial({ color: 0xEDEAF5, transparent: true, opacity: 0.55, roughness: 0.3, depthWrite: false, side: THREE.DoubleSide });
    const carbon = new THREE.MeshPhysicalMaterial({ color: 0x111116, roughness: 0.28, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.08, dithering: true });
    const wood = new THREE.MeshPhysicalMaterial({ map: woodTex(), roughness: 0.62, metalness: 0, dithering: true });
    const abs = new THREE.MeshPhysicalMaterial({ color: 0x1b1b24, roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.12, dithering: true });
    const steel = new THREE.MeshPhysicalMaterial({ color: 0xdedee6, roughness: 0.22, metalness: 1, dithering: true });
    const baseM = new THREE.MeshPhysicalMaterial({ map: ctx.texBase, roughness: 0.4, clearcoat: 0.3, clearcoatRoughness: 0.3, dithering: true });
    const baseEdge = new THREE.MeshPhysicalMaterial({ color: 0x2a2b45, roughness: 0.4 });
    const uvPlanar = (l, z) => [l / L, 0.5 + z / 0.4];
    const uvT = makeUV(outTop, plan, { view: 'above' }), uvB = makeUV(outBase, plan, { view: 'above' });
    const woodUV = (l, z) => [l / L, 0.5 + z / 0.31];
    // 各层：[id, 中文名, 构件, 厚度]
    const th = { top: 0.006, glass: 0.0035, str: 0.005, core: 0.02, edge: 0.006, base: 0.005 };
    const layers = [];
    layers.push(['topsheet', '金属磨砂板面', buildSlab(ctx, prof, { t: th.top, topMat: metalTop, sideMat: topEdge, uvTop: uvT, bev: 0.0012 }), th.top]);
    layers.push(['glass_top', '上层3轴玻纤', buildSlab(ctx, prof, { d: 0.002, t: th.glass, topMat: glass, sideMat: glassEdge, uvTop: uvPlanar, bev: 0.0006 }), th.glass]);
    const sg = new THREE.Group();
    for (let i = 0; i < 16; i++) {
      const f = -1 + (2 * i + 1) / 16;
      const m = new THREE.Mesh(buildStrip(prof, (l) => f * plan.hwM(l) * 0.8, { l0: 0.13 * L, l1: 0.87 * L, w: 0.0085, t: th.str, mat: carbon }), carbon);
      m.castShadow = m.receiveShadow = true; sg.add(m);
    }
    layers.push(['carbon', '16根碳纤条', sg, th.str]);
    layers.push(['core', '进口复合白杨木芯', buildSlab(ctx, prof, { d: 0.004, t: th.core, topMat: wood, sideMat: abs, ringMat: abs, ringW: 0.007, uvTop: woodUV, bev: 0.0015, taper: 0.5 }), th.core]);
    layers.push(['glass_bottom', '下层3轴玻纤', buildSlab(ctx, prof, { d: 0.002, t: th.glass, topMat: glass, sideMat: glassEdge, uvTop: uvPlanar, bev: 0.0006 }), th.glass]);
    layers.push(['edge', '奥地利钢刃', buildEdgeLoop(ctx, prof, { d: 0, w: 0.005, h: th.edge, mat: steel }), th.edge]);
    layers.push(['base', '高含碳烧结板底', buildSlab(ctx, prof, { d: 0.006, t: th.base, topMat: baseM, sideMat: baseEdge, uvTop: uvB, bev: 0.001 }), th.base]);
    const gap = qn('gap', 0.16);
    let y = 0; const root = new THREE.Group(); scene.add(root);
    const ys = [];
    for (let i = layers.length - 1; i >= 0; i--) { const [, , g, t] = layers[i]; g.position.y = y; ys[i] = y; root.add(g); y += t + gap; }
    root.position.y = -y / 2;
    root.rotation.y = qn('yaw', -52) * Math.PI / 180;   // 板头在左上：板面画面与板底 vamei 都接近正立
    // 正交相机，等轴测感
    const elev = qn('elev', 24) * Math.PI / 180, az = 0;
    const halfH = qn('zoom', 0.96), asp = W / H;
    const cam = new THREE.OrthographicCamera(-halfH * asp, halfH * asp, halfH, -halfH, 0.1, 40);
    const tgt = new THREE.Vector3(qn('tx', -0.19), qn('ty', 0), 0);
    cam.position.set(tgt.x + Math.sin(az) * Math.cos(elev) * 10, tgt.y + Math.sin(elev) * 10, tgt.z + Math.cos(az) * Math.cos(elev) * 10); cam.lookAt(tgt);
    scene.environment = makeEnv(renderer, { yaw: camYaw(cam, tgt), key: 5, rim: 8, rimL: 4, top: 1.2, fill: 0.6, front: 1.0, back: 2.5, backPos: [0, 6, -12], dome: [0.22, 0.2, 0.3] });
    const Lg = placeLights(scene, cam, tgt, { key: qn('lk', 2.0), rim: qn('lr', 2.6), hemi: 0.4, keyPos: [-2, 4, 1.2], rimPos: [3, 1.5, -2.5] });
    renderer.render(scene, cam);
    // 标注锚点：每层在画面上最左端（板头一侧）的轮廓点，所有层在同一竖列，适合左侧标签 + 水平引线
    scene.updateMatrixWorld(true);
    const anchors = []; let bb = [1e9, 1e9, -1e9, -1e9];
    layers.forEach(([id, name, g, t]) => {
      let best = null;
      const consider = (v) => { g.localToWorld(v); const q = project(cam, v, W, H); if (!best || q[0] < best[0]) best = q; bb = [Math.min(bb[0], q[0]), Math.min(bb[1], q[1]), Math.max(bb[2], q[0]), Math.max(bb[3], q[1])]; };
      if (id === 'carbon') {
        for (let i = 0; i < 16; i++) { const f = -1 + (2 * i + 1) / 16; for (const l of [0.13 * L, 0.87 * L]) consider(new THREE.Vector3(...toWorld(prof, l, f * plan.hwM(l) * 0.8, t * 0.5))); }
      } else for (const p of plan.loop) consider(new THREE.Vector3(...toWorld(prof, p.l, p.z, t * 0.5)));
      anchors.push({ id, name_cn: name, x: best[0], y: best[1] });
    });
    console.warn('BBOX ' + JSON.stringify(bb));
    console.warn('ANCHORS ' + JSON.stringify(anchors));
  },

  // 5/6. 平放的板：base = 板底朝上，top = 板面朝上；斜贯画面，相机约 35° 俯角
  async base(ctx) { return flatShot(ctx, 'base'); },
  async top(ctx) { return flatShot(ctx, 'top'); },

  // 1. 首屏双板：板面在左前，板底在右后，近乎竖直
  async hero(ctx) {
    const { renderer, W, H } = ctx;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    const scene = new THREE.Scene();
    const prof = makeProfile({ camber: 0.008, kickH: 0.05, T0: 0.0115, taper: 0.4 });
    const mats = boardMaterials(ctx);
    const A = buildBoard(ctx, prof, mats), B = buildBoard(ctx, prof, mats);
    // 把板子厚度中心大致移到原点（局部）
    const off = new THREE.Vector3(0, -0.02, 0);
    for (const b of [A, B]) b.children.forEach(m => m.position.copy(off));
    const gA = new THREE.Group(), gB = new THREE.Group(); gA.add(A); gB.add(B); scene.add(gA, gB);
    gA.quaternion.copy(standQuat('top', qn('tA', 8), qn('rA', 22), qn('pA', 0)));
    gB.quaternion.copy(standQuat('base', qn('tB', 12), qn('rB', -14), qn('pB', 0)));
    gA.position.set(qn('xA', -0.13), qn('yA', -0.06), qn('zA', 0.16));
    gB.position.set(qn('xB', 0.13), qn('yB', 0.07), qn('zB', -0.16));
    const fov = qn('fov', 26), dist = (1.55 / 0.85) / 2 / Math.tan(fov / 2 * Math.PI / 180);
    const cam = new THREE.PerspectiveCamera(fov, W / H, 0.5, 30);
    const tgt = new THREE.Vector3(0, qn('ty', 0), 0);
    cam.position.set(qn('cx', 0.35), qn('cy', -0.25), dist); cam.lookAt(tgt);
    scene.environment = makeEnv(renderer, { yaw: camYaw(cam, tgt), key: qn('ek', 5), rim: qn('er', 7), rimL: qn('erl', 3), top: 1.0, fill: qn('efl', 1.4), front: qn('ef', 1.6), dome: [0.22, 0.2, qn('eb', 0.35)] });
    scene.environmentIntensity = qn('ei', 1.0);
    const Lg = placeLights(scene, cam, tgt, { key: qn('lk', 2.0), rim: qn('lr', 2.6), hemi: 0.35, keyPos: [-3, 2.5, 2.2], rimPos: [3.2, 1.0, -2.6] });
    setShadow(Lg.key, new THREE.Vector3(0, 0, 0), 1.0, { radiusBlur: qn('blur', 10), bias: -0.0004, normalBias: 0.003 });
    if (qn('spot', 1)) {
      // 主光换成左上方的聚光灯（带距离衰减），让画面从左上到右下有自然的明暗过渡
      const sp = new THREE.SpotLight(0xFFE9E4, qn('ls', 20), 0, Math.PI / 5, 1.0, qn('decay', 2));
      sp.position.copy(Lg.rel(qn('spx', -0.7), qn('spy', 2.2), qn('spz', 3.0))); sp.target.position.copy(tgt.clone().add(new THREE.Vector3(0.1, -0.1, 0)));
      sp.castShadow = true; sp.shadow.mapSize.set(4096, 4096); sp.shadow.bias = -0.0004; sp.shadow.normalBias = 0.003; sp.shadow.radius = qn('blur', 16);
      sp.shadow.camera.near = 0.5; sp.shadow.camera.far = 8;
      scene.add(sp, sp.target);
      Lg.key.intensity = qn('lk2', 0.5); Lg.key.castShadow = false;
    }
    // 反光板：低位前方的暖粉补光，提亮朝下的板头
    const bounce = new THREE.DirectionalLight(0xF3D9DE, qn('lb', 0.9)); bounce.position.copy(Lg.rel(-0.5, -3, 2.5)); bounce.target.position.copy(tgt); scene.add(bounce, bounce.target);
    renderer.render(scene, cam);
  },

  // 2. 侧面板型：相机略高于板面，拱起 ×2.5 夸张
  async profile(ctx) {
    const { renderer, W, H } = ctx;
    const scene = new THREE.Scene();
    const prof = makeProfile({ camber: qn('camber', 0.024), kickH: 0.05, T0: 0.012, taper: 0.35 });
    console.warn('INFO profile', JSON.stringify(prof.info));
    const mats = boardMaterials(ctx);
    const b = buildBoard(ctx, prof, mats); scene.add(b);
    const span = 1.55 / 0.9, dist = 9;
    const elev = qn('elev', 7) * Math.PI / 180;
    const cam = new THREE.PerspectiveCamera(2 * Math.atan((span / 2) / dist) * 180 / Math.PI * (H / W), W / H, 1, 50);
    const tgt = new THREE.Vector3(0, qn('ty', 0.03), 0);
    cam.position.set(0, tgt.y + Math.sin(elev) * dist, Math.cos(elev) * dist); cam.lookAt(tgt);
    scene.environment = makeEnv(renderer, { yaw: camYaw(cam, tgt), key: 4, rim: 6 });
    const Lg = placeLights(scene, cam, tgt, { key: 1.6, rim: 2.2, keyPos: [-2, 4, 1.5], rimPos: [3, 1.5, -3] });
    const cs = contactShadow(ctx.plan, { heightFn: (l) => prof.at(l).y, xFn: (l) => prof.at(l).x, layers: [[0.002, 2, 0.8], [0.012, 7, 0.5], [1, 22, 0.25]] });
    scene.add(cs);
    renderer.render(scene, cam);
    const pts = {};
    const P = (l, h) => new THREE.Vector3(...toWorld(prof, l, 0, h));
    pts.nose_tip = project(cam, P(0, 0.006), W, H); pts.tail_tip = project(cam, P(L, 0.006), W, H);
    const c1 = L / 2 - prof.info.contact, c2 = L / 2 + prof.info.contact;
    pts.contact_nose = project(cam, P(c1, 0), W, H); pts.contact_tail = project(cam, P(c2, 0), W, H);
    pts.camber_peak_base = project(cam, P(L / 2, 0), W, H);
    console.warn('ANCHORS ' + JSON.stringify(pts));
  },
  // 调试：俯视两块板（板面 / 翻过来的板底），检查贴图方向
  async debug(ctx) {
    const { renderer, W, H } = ctx;
    const scene = new THREE.Scene();
    const prof = makeProfile({ flat: true, T0: 0.011 });
    const mats = boardMaterials(ctx);
    const a = buildBoard(ctx, prof, mats), b = buildBoard(ctx, prof, mats);
    a.position.z = -0.17; b.rotation.x = Math.PI; b.position.z = 0.17;
    scene.add(a, b);
    const asp = W / H, hh = 0.85;
    const cam = new THREE.OrthographicCamera(-hh * asp, hh * asp, hh, -hh, 0.1, 10);
    cam.position.set(0, 3, 0); cam.up.set(-1, 0, 0); cam.lookAt(0, 0, 0);
    scene.environment = makeEnv(renderer, { yaw: 0 });
    placeLights(scene, cam, new THREE.Vector3());
    renderer.render(scene, cam);
  },
};

main().catch(e => { console.error('FATAL', e && e.stack || e); });
