// ============ sky-night · 月光板面展示背景 1500×2400 ============
// 坐标：q.x ∈ [0,1]，q.y ∈ [0,ASP] 向下；v = 竖向比例
const float ASP = 3280.0 / 1500.0;      // 与板面展示屏 750×1640 对齐
const vec2 MOON = vec2(0.80, 0.115 * ASP);  // 右上角，避开左侧标题
const float MOON_R = 0.095;              // 直径 = 19% 画宽
const float VH = 0.905;                  // 底部山脊所用的地平线
const float FOC = 1.13;
uniform highp sampler3D uNoise3;
float PX;

float sq(float x) { return x * x; }
float remap(float v, float lo, float hi) { return clamp((v - lo) / (hi - lo), 0.0, 1.0); }
float tn2(vec2 p, float z) { return textureLod(uNoise3, vec3(p, z), 0.0).r; }   // 平铺 Perlin fbm，[0,1]

// ---------- 天空 ----------
vec3 skyBase(vec2 q) {
  float v = q.y / ASP;
  vec3 top = L(0x111327), mid = L(0x1A1C3D), low = L(0x2C2E57), hz = L(0x3E3A6C);
  vec3 c = crOk(top, top, mid, low, smoothstep(0.0, 0.62, v));
  c = mixOk(c, low, smoothstep(0.55, 0.85, v));
  c = mixOk(c, hz, smoothstep(0.78, 0.97, v));
  // 地平线下残余的一点暮粉
  c += L(0x8E5E86) * 0.05 * exp(-max(0.97 - v, 0.0) / 0.06);
  return c;
}

// ---------- 银河带（很淡） ----------
float bandCoord(vec2 q, out float along) {
  vec2 a = vec2(-0.05, 0.86 * ASP), b = vec2(1.05, 0.02 * ASP);
  vec2 ab = normalize(b - a);
  vec2 rel = q - a;
  along = dot(rel, ab);
  return dot(rel, vec2(-ab.y, ab.x));   // 距离带中心线（带符号）
}
vec3 milky(vec2 q, out float starBoost) {
  float along;
  float off = bandCoord(q, along);
  float w = 0.20 + 0.05 * sin(along * 3.1);
  float core = exp(-sq((off + 0.03 * sin(along * 5.0)) / w));
  float cl = tn2(q * vec2(0.9, 0.9) + vec2(0.31, 0.77), 0.21);
  float fine = tn2(q * 3.1 + vec2(0.13, 0.4), 0.61);
  float dust = smoothstep(0.50, 0.72, tn2(q * vec2(1.6, 1.6) + vec2(0.7, 0.2), 0.43)) * exp(-sq(off / (w * 0.45)));
  float glow = core * (0.55 + 0.7 * cl) * (0.8 + 0.4 * fine) * (1.0 - 0.45 * dust);
  starBoost = core * (0.6 + 0.8 * cl) * (1.0 - 0.6 * dust);
  return mix(L(0x7B76B8), L(0xC9B9D8), cl) * glow * 0.06;
}

// ---------- 星空：三层（细尘 / 中等 / 亮星） ----------
vec3 stars(vec2 fc, float vis, float boost) {
  float RP = uRes.x / 1500.0;
  vec2 sp = fc / RP;
  vec3 acc = vec3(0.0);
  for (int layer = 0; layer < 3; layer++) {
    float cs = layer == 0 ? 7.0 : (layer == 1 ? 19.0 : 63.0);
    vec2 c = floor(sp / cs);
    vec4 r = h4(ivec2(c) + ivec2(layer * 9173, layer * 271));
    float prob = layer == 0 ? 0.05 + 0.45 * boost : (layer == 1 ? 0.09 + 0.16 * boost : 0.26);
    if (r.w > prob) continue;
    vec2 pos = (c + 0.25 + 0.5 * r.xy) * cs;
    vec2 dv = sp - pos;
    float d2 = dot(dv, dv);
    float b, sig;
    if (layer == 0)      { b = 0.03 + 0.10 * pow(r.z, 2.0); sig = 0.48; }
    else if (layer == 1) { b = 0.10 + 0.55 * pow(r.z, 2.5); sig = 0.55 + 0.2 * r.z; }
    else                 { b = 0.45 + 1.8 * pow(r.z, 2.0); sig = 0.7 + 0.45 * r.z; }
    float g = exp(-d2 / (2.0 * sig * sig));
    if (layer == 2) {
      g += exp(-sqrt(d2) / 3.0) * 0.05;
      // 最亮的几颗带极细的十字星芒
      float sp4 = exp(-abs(dv.x) * 1.4 - dv.y * dv.y * 2.5) + exp(-abs(dv.y) * 1.4 - dv.x * dv.x * 2.5);
      g += sp4 * 0.10 * smoothstep(0.82, 1.0, r.z);
    }
    float temp = fract(r.z * 7.31 + r.x * 3.1);
    vec3 tint = temp < 0.33 ? L(0xC9D4FF) : (temp < 0.8 ? L(0xF3EFE4) : L(0xFFD9C4));
    acc += tint * b * g;
  }
  return acc * vis;
}

// ---------- 月亮：程序化月海、环形山、第谷辐射纹 ----------
float ell(vec2 p, vec2 c, vec2 r, float rot) {
  vec2 d = p - c;
  float cs = cos(rot), sn = sin(rot);
  d = vec2(cs * d.x + sn * d.y, -sn * d.x + cs * d.y) / r;
  return length(d);
}
float smin(float a, float b, float k) { float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0); return mix(b, a, h) - k * h * (1.0 - h); }
float mariaField(vec2 d0, vec3 n) {
  // 位置大致参照满月时肉眼所见（北在上）。椭圆平滑并集给出大形，域扭曲 + 多尺度噪声给出不规则轮廓
  vec2 wv = vec2(tn2(d0 * 0.8 + vec2(0.21, 0.63), 0.12), tn2(d0 * 0.8 + vec2(0.71, 0.33), 0.88)) - 0.5;
  vec2 wv2 = vec2(tn2(d0 * 2.2 + vec2(0.41, 0.13), 0.47), tn2(d0 * 2.2 + vec2(0.11, 0.93), 0.58)) - 0.5;
  vec2 d = d0 + wv * 0.19 + wv2 * 0.05;
  float e[13] = float[13](
    ell(d, vec2(-0.30, 0.50), vec2(0.36, 0.26), 0.12),   // 雨海
    ell(d, vec2(0.24, 0.42), vec2(0.19, 0.18), 0.0),     // 澄海
    ell(d, vec2(0.38, 0.12), vec2(0.25, 0.19), -0.35),   // 静海
    ell(d, vec2(0.72, 0.30), vec2(0.13, 0.105), 0.2),    // 危海
    ell(d, vec2(0.61, -0.12), vec2(0.13, 0.21), 0.25),   // 丰富海
    ell(d, vec2(0.41, -0.28), vec2(0.10, 0.10), 0.0),    // 酒海
    ell(d, vec2(-0.64, 0.14), vec2(0.27, 0.50), -0.15),  // 风暴洋
    ell(d, vec2(-0.42, -0.16), vec2(0.23, 0.19), 0.35),  // 风暴洋南部
    ell(d, vec2(-0.18, -0.34), vec2(0.21, 0.15), 0.1),   // 云海
    ell(d, vec2(-0.52, -0.40), vec2(0.10, 0.10), 0.0),   // 湿海
    ell(d, vec2(-0.03, 0.79), vec2(0.40, 0.07), 0.06),   // 冷海
    ell(d, vec2(0.02, 0.30), vec2(0.15, 0.09), 0.3),     // 汽海
    ell(d, vec2(-0.28, -0.08), vec2(0.13, 0.10), 0.0));  // 知海 / 岛海
  float f = 10.0;
  for (int i = 0; i < 13; i++) f = smin(f, e[i] * (i == 3 ? 0.92 : 1.0), i == 3 ? 0.02 : 0.07);
  float n1 = tn2(n.xy * 0.55 + n.z * 0.3 + vec2(0.4, 0.2), 0.37) - 0.5;
  float n2 = tn2(n.xy * 1.7 + n.z * 0.5 + vec2(0.1, 0.7), 0.83) - 0.5;
  float n3 = tn2(n.xy * 4.8 + n.z * 0.5 + vec2(0.3, 0.1), 0.19) - 0.5;
  float fld = (1.0 - f) * 1.1 - 0.05 + n1 * 0.36 + n2 * 0.12;
  float ew = 0.10 + 0.12 * tn2(n.xy * 1.2 + vec2(0.8, 0.3), 0.51);
  return smoothstep(-ew, ew, fld) * mix(1.0, 0.75, smoothstep(0.6, 0.9, d.y) * step(0.0, 0.0));
}
// 球面上的随机环形山（3D 单元格）：返回 (亮边, 暗底, 新鲜度)
vec3 craters(vec3 n, float sc, uint salt) {
  vec3 p = n * sc;
  ivec3 ip = ivec3(floor(p));
  vec3 res = vec3(0.0);
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    ivec3 c = ip + ivec3(x, y, z);
    uint h = hu3(c) ^ salt;
    vec3 o = vec3(float(h & 1023u), float((h >> 10) & 1023u), float((h >> 20) & 1023u)) / 1023.0;
    float r0 = float(hu(h) & 1023u) / 1023.0;
    if (r0 > 0.55) continue;
    float rad = 0.12 + 0.30 * r0 * r0;
    float d = length(p - (vec3(c) + o)) / rad;
    if (d > 1.6) continue;
    float fresh = float(hu(h ^ 0x9e37u) & 1023u) / 1023.0;
    float rim = exp(-sq((d - 1.0) / 0.16));
    float flo = 1.0 - smoothstep(0.55, 0.95, d);
    float ej = exp(-max(d - 1.0, 0.0) / 0.3) * step(1.0, d);
    res.x = max(res.x, rim * (0.35 + 0.65 * fresh * fresh) + ej * fresh * fresh * 0.5);
    res.y = max(res.y, flo * (1.0 - fresh) * 0.6);
    res.z = max(res.z, fresh * flo);
  }
  return res;
}
// 大环形山的辐射纹
float rays(vec3 n, vec3 c, float len, float seed) {
  float ang = acos(clamp(dot(n, c), -1.0, 1.0));
  vec3 t = normalize(cross(c, vec3(0.0, 0.0, 1.0)) + 1e-4);
  vec3 b = cross(c, t);
  vec3 pr = n - c * dot(n, c);
  float az = atan(dot(pr, b), dot(pr, t));
  float f = noise(vec2(az * 9.0 + seed, seed)) * 0.5 + noise(vec2(az * 23.0 + seed * 3.0, seed)) * 0.5;
  float streak = pow(clamp(f * 1.6 + 0.35, 0.0, 1.0), 6.0);
  return streak * exp(-ang / len) * smoothstep(0.02, 0.06, ang);
}
vec3 llToN(float lat, float lon) { lat = radians(lat); lon = radians(lon); return vec3(sin(lon) * cos(lat), sin(lat), cos(lon) * cos(lat)); }

vec4 moon(vec2 q, out vec3 glow) {
  vec2 d = (q - MOON) / MOON_R;
  d.y = -d.y;
  float r = length(d);
  float rr = max(r - 1.0, 0.0);
  // 大而柔和的月晕 + 极淡的彩色光环
  glow = L(0xFFF3E6) * (0.30 * exp(-rr / 0.09) + 0.13 * exp(-rr / 0.45)) +
         L(0xB9AEE0) * 0.11 * exp(-rr / 1.6) + L(0x6E6AAE) * 0.04 * exp(-rr / 4.0);
  float ring = exp(-sq((r - 2.2) / 0.45));
  glow += (L(0xE8A9B5) * 0.007 + L(0xB8A9CF) * 0.005) * ring;
  float aa = PX / MOON_R;
  float m = 1.0 - smoothstep(1.0 - aa * 1.2, 1.0 + aa * 0.5, r);
  if (m <= 0.0) return vec4(0.0);
  float z = sqrt(max(1.0 - r * r, 0.0));
  vec3 n = vec3(d.x, d.y, z);
  float maria = mariaField(d, n);
  // 月海内部的明暗起伏
  float mt = tn2(n.xy * 1.7 + n.z * 0.4 + vec2(0.2, 0.6), 0.71);
  float hl = tn2(n.xy * 3.3 + n.z * 0.4 + vec2(0.5, 0.1), 0.13);
  vec3 cr1 = craters(n, 9.0, 0x1234u);
  vec3 cr2 = craters(n, 23.0, 0x5678u);
  vec3 cr3 = craters(n, 55.0, 0x9abcu);
  vec3 cr4 = craters(n, 120.0, 0xdef0u);
  float mt2 = tn2(n.xy * 5.5 + n.z * 0.4 + vec2(0.7, 0.3), 0.29);
  float alb = mix(1.0, 0.72 + 0.26 * (mt - 0.5) + 0.06 * (mt2 - 0.5), maria);
  alb *= 1.0 + (0.12 * (hl - 0.5) + 0.05 * (mt2 - 0.5)) * (1.0 - maria);
  float crB = cr1.x * 0.16 + cr2.x * 0.14 + cr3.x * 0.12 + cr4.x * 0.10;
  float crD = cr1.y * 0.08 + cr2.y * 0.06 + cr3.y * 0.05;
  alb += crB * (1.0 - 0.4 * maria) - crD * 0.7;
  // 第谷、哥白尼、开普勒、阿里斯塔克的亮斑与辐射纹
  vec3 ty = llToN(-43.3, -11.2), co = llToN(9.6, -20.1), ke = llToN(8.1, -38.0), ar = llToN(23.7, -47.4);
  alb += rays(n, ty, 0.6, 3.0) * 0.20 + (rays(n, co, 0.25, 7.0) * 0.14 + rays(n, ke, 0.18, 11.0) * 0.11) * (0.5 + 0.5 * maria);
  alb += 0.32 * exp(-sq(acos(clamp(dot(n, ty), -1.0, 1.0)) / 0.035));
  alb += 0.26 * exp(-sq(acos(clamp(dot(n, co), -1.0, 1.0)) / 0.035)) + 0.10 * exp(-acos(clamp(dot(n, co), -1.0, 1.0)) / 0.12);
  alb += 0.20 * exp(-sq(acos(clamp(dot(n, ke), -1.0, 1.0)) / 0.025)) + 0.08 * exp(-acos(clamp(dot(n, ke), -1.0, 1.0)) / 0.09);
  alb += 0.38 * exp(-sq(acos(clamp(dot(n, ar), -1.0, 1.0)) / 0.018));
  // 满月几乎无临边昏暗；略微压一点边缘
  float limb = 0.90 + 0.10 * pow(z, 0.35);
  vec3 hiC = L(0xF2EEE6), maC = L(0xD9D6D6);
  vec3 col = mix(hiC, maC, maria * 0.85) * alb * limb * 0.92;
  col = mix(col, col * vec3(1.02, 0.97, 1.0), 0.3);
  col = mix(col, hiC * 0.9, 0.07);   // 薄薄一层大气光幕
  return vec4(col, m);
}

// ---------- 下三分之一：体积薄云（高积云 / 高层云），月光照顶、暮粉照底 ----------
const float CB = 1.7, CT = 2.25;
const vec3 MOOND = vec3(0.0, 1.064, 1.13);
float clCov(vec3 p) {
  float w = textureLod(uNoise3, vec3(p.xz * 0.05 + vec2(0.17, 0.61), 0.44), 0.0).r;
  float w2 = textureLod(uNoise3, vec3(p.xz * 0.016 + vec2(0.52, 0.23), 0.12), 0.0).r;
  float c = remap(w, 0.36, 0.64) * (0.4 + 0.9 * remap(w2, 0.3, 0.7));
  float zr = smoothstep(3.6, 6.0, p.z) * (1.0 - smoothstep(30.0, 52.0, p.z));
  return clamp(c, 0.0, 1.0) * zr;
}
float clBase(vec3 p) {
  float cov = clCov(p);
  if (cov < 0.03) return -1.0;
  float h = (p.y - CB) / (CT - CB);
  float prof = smoothstep(0.0, 0.35, h) * (1.0 - smoothstep(0.5, 1.0, h));
  vec4 n = textureLod(uNoise3, p * vec3(0.085, 0.30, 0.23) + vec3(0.33, 0.1, 0.27), 0.0);
  float shape = n.r * 0.6 + n.g * 0.4;
  return shape - (0.80 - 0.40 * cov * (0.2 + 0.8 * prof));
}
float clDen(vec3 p, bool detail) {
  float b = clBase(p);
  if (!detail) return clamp((b + 0.01) / 0.10, 0.0, 1.0);
  if (b < -0.07) return 0.0;
  vec4 e = textureLod(uNoise3, p * vec3(0.30, 0.9, 0.8) + vec3(0.5, 0.2, 0.0), 0.0);
  float v = b + (e.b - 0.47) * 0.16 + (e.a - 0.47) * 0.06;
  return clamp(v / 0.14, 0.0, 1.0);
}
float hg(float c, float g) { float g2 = g * g; return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * c, 1.5)); }
vec4 clouds(vec2 q, vec3 sky) {
  vec3 rd = normalize(vec3(q.x - 0.5, VH * ASP - q.y, FOC));
  if (rd.y < 0.02) return vec4(0.0, 0.0, 0.0, 1.0);
  float t0 = CB / rd.y, t1 = min(CT / rd.y, 60.0);
  if (t0 >= 60.0) return vec4(0.0, 0.0, 0.0, 1.0);
  const int N = 40;
  float dt = (t1 - t0) / float(N);
  float t = t0 + dt * hp(q * uRes.x, 41.0);
  vec3 md = normalize(MOOND);
  float cth = dot(rd, md);
  vec3 moonC = L(0xDCD6F2) * 1.1, pinkC = L(0xEFA9BC) * 0.75;
  vec3 ambTop = L(0x22244C) * 0.55, ambBot = L(0x3A3062) * 0.5;
  vec3 acc = vec3(0.0); float T = 1.0;
  for (int i = 0; i < N; i++) {
    vec3 p = rd * t;
    float d = clDen(p, true);
    if (d > 0.002) {
      float tau = 0.0, sacc = 0.0;
      for (int j = 0; j < 4; j++) { float ls = 0.05 * pow(2.0, float(j)); sacc += ls; tau += clDen(p + md * sacc, false) * ls; }
      // 下方（来自地平线下的暮光）：朝下步进
      float taub = clDen(p - vec3(0.0, 0.08, 0.0), false) * 0.08 + clDen(p - vec3(0.0, 0.2, 0.0), false) * 0.12;
      float sig = d * 3.6;
      float Lm = exp(-tau * 5.0) * mix(hg(cth, 0.55), hg(cth, -0.1), 0.4) + 0.25 * exp(-tau * 2.0) * 0.08;
      float h = clamp((p.y - CB) / (CT - CB), 0.0, 1.0);
      vec3 S = (moonC * Lm + pinkC * exp(-taub * 7.0) * (1.0 - h) * (1.0 - d * 0.8) + mix(ambBot, ambTop, h)) * sig;
      float fog = 1.0 - exp(-t / 40.0);
      S = mix(S, sky * sig, fog * 0.8);
      float Tr = exp(-sig * dt);
      acc += T * (S - S * Tr) / max(sig, 1e-4);
      T *= Tr;
      if (T < 0.02) break;
    }
    t += dt;
  }
  return vec4(acc, T);
}

// ---------- 底部雪岭（光线步进，月光） ----------
float rt(vec2 xz, float s, float o) {
  float r = textureLod(uNoise3, vec3(xz * s, o), 0.0).r;
  float k = clamp(1.0 - abs(r - 0.5) * 2.7, 0.0, 1.0);
  return k * k;
}
float terrH(vec2 xz, int lod) {
  float z = xz.y;
  float big2 = rt(xz + vec2(11.0, 0.0), 0.034, 0.55);
  float big = rt(xz, 0.021, 0.13);
  float mid = rt(xz + vec2(3.7, 1.1), 0.075, 0.41);
  float dt = 0.0;
  if (lod > 0) dt += rt(xz, 0.21, 0.77) * 0.05;
  if (lod > 1) dt += rt(xz, 0.62, 0.29) * 0.018;
  float e1 = exp(-sq((z - 4.0) / 0.8));
  float e3 = smoothstep(12.0, 22.0, z);
  float rn = big2 * 0.8 + mid * 0.12 + dt;
  float rf = big * 0.6 + mid * 0.3 + dt * 1.5;
  return -1.0 + e1 * (0.48 + 0.55 * rn) + e3 * (0.55 + 1.6 * rf);
}
vec3 camRay(vec2 q) { return normalize(vec3(q.x - 0.5, VH * ASP - q.y, FOC)); }
float terrMarch(vec3 rd, out float best, out float tBest) {
  float pxA = 1.0 / (uRes.x * FOC);
  float t = 0.6, tPrev = t;
  best = 1e9; tBest = 0.0;
  float r1 = 1e9, r2 = 1e9, t1 = 0.0, t2 = 0.0, bLo = 0.0, bHi = 0.0;
  bool hit = false;
  for (int i = 0; i < 200; i++) {
    vec3 p = rd * t;
    float hgt = p.y - terrH(p.xz, 1);
    if (hgt < 0.0) { hit = true; break; }
    float ratio = hgt / (t * pxA);
    if (r1 < r2 && r1 <= ratio && r1 < best) { best = r1; tBest = t1; bLo = t2; bHi = t; }
    r2 = r1; t2 = t1; r1 = ratio; t1 = t;
    tPrev = t;
    t += max(hgt * 0.42, 0.0012 * t);
    if (t > 80.0 || p.y > 1.5) break;
  }
  if (!hit && r1 < best) { best = r1; tBest = t1; bLo = t2; bHi = t; }
  if (best < 12.0) {
    float lo = max(bLo, 0.3), hi = bHi;
    for (int k = 0; k < 10; k++) {
      float m1 = lo + (hi - lo) / 3.0, m2 = hi - (hi - lo) / 3.0;
      vec3 p1 = rd * m1, p2 = rd * m2;
      float q1 = (p1.y - terrH(p1.xz, 2)) / (m1 * pxA);
      float q2 = (p2.y - terrH(p2.xz, 2)) / (m2 * pxA);
      if (q1 < q2) hi = m2; else lo = m1;
    }
    float tm = 0.5 * (lo + hi);
    vec3 pmn = rd * tm;
    best = max((pmn.y - terrH(pmn.xz, 2)) / (tm * pxA), 0.0);
    tBest = tm;
  }
  if (!hit) return -1.0;
  float a = tPrev, b = t;
  for (int k = 0; k < 6; k++) {
    float m = 0.5 * (a + b);
    vec3 pm = rd * m;
    if (pm.y - terrH(pm.xz, 2) < 0.0) b = m; else a = m;
  }
  return b;
}
vec3 terrShade(vec3 p, vec3 rd, float t, vec3 skyHz) {
  float e = max(0.0009 * t, 0.002);
  float hx = terrH(p.xz + vec2(e, 0.0), 2) - terrH(p.xz - vec2(e, 0.0), 2);
  float hz = terrH(p.xz + vec2(0.0, e), 2) - terrH(p.xz - vec2(0.0, e), 2);
  vec3 n = normalize(vec3(-hx, 2.0 * e, -hz));
  vec3 lm = normalize(vec3(0.0, 0.55, 1.0));           // 月亮：正前上方
  float dif = max(dot(n, lm), 0.0);
  float up = n.y;
  vec3 alb = mix(vec3(0.92, 0.92, 0.98), L(0x3A3860) * 0.6, (1.0 - smoothstep(0.5, 0.85, up)) * 0.6);
  vec3 amb = mix(L(0x101231), L(0x2C2E57), 0.5 + 0.5 * up) * 0.55;
  vec3 c = alb * (amb + L(0xC9C3E6) * mix(0.16, 0.07, smoothstep(6.0, 16.0, t)) * dif);
  float fogD = 1.0 - exp(-t / 14.0);
  float hf = exp(-max(p.y + 1.0, 0.0) / 0.25);
  c = mix(c, L(0x2E2F5C), clamp(hf * 0.7, 0.0, 0.8));
  c = mix(c, skyHz, fogD * 0.9);
  return c;
}
vec4 terrain(vec2 q, vec3 skyHz) {
  vec3 rd = camRay(q);
  float best, tBest;
  float t = terrMarch(rd, best, tBest);
  if (t < 0.0) {
    if (best < 1.2) return vec4(terrShade(rd * tBest, rd, tBest, skyHz), clamp(1.0 - best / 1.2, 0.0, 1.0) * 0.98);
    return vec4(0.0);
  }
  vec3 c = terrShade(rd * t, rd, t, skyHz);
  if (best < 1.2 && tBest < t * 0.92) c = mix(c, terrShade(rd * tBest, rd, tBest, skyHz), clamp(1.0 - best / 1.2, 0.0, 1.0));
  // 月光雪檐：贴近山脊线的一条淡亮边
  float rp = 1.0 / 1500.0;
  float b2, tb2;
  float tu = terrMarch(camRay(q - vec2(0.0, 5.0 * rp)), b2, tb2);
  if ((tu < 0.0 || tu > t * 1.2) && tb2 < t * 1.2) {
    float below = 5.0 - b2 / (uRes.x / 1500.0);
    float rim = exp(-max(below, 0.0) / 2.0) * smoothstep(-0.5, 0.8, below);
    c = mix(c, L(0xB9AEDC) * 0.75, clamp(rim, 0.0, 1.0) * 0.55 * exp(-t / 12.0));
  }
  return vec4(c, 1.0);
}

vec3 sceneColor(vec2 fc) {
  PX = 1.0 / uRes.x;
  vec2 q = fc / uRes.x;
  float v = q.y / ASP;
  vec3 sky = skyBase(q);
  vec3 col = sky;

  // 月光让周围天空变亮、星星变少
  float dm = length(q - MOON) / MOON_R;
  float moonWash = exp(-max(dm - 1.0, 0.0) / 1.6);
  float boost;
  vec3 mw = milky(q, boost);
  col += mw * (1.0 - moonWash * 0.9);
  float starVis = (1.0 - 0.95 * moonWash) * (1.0 - smoothstep(0.80, 0.93, v));
  vec4 cl = (v > 0.52 && v < 0.92) ? clouds(q, sky) : vec4(0.0, 0.0, 0.0, 1.0);
  col += stars(fc, starVis * cl.a, boost);

  vec3 glow;
  vec4 mo = moon(q, glow);
  col += glow;
  col = mix(col, mo.rgb, mo.a);

  // 薄云（体积）
  col = col * cl.a + cl.rgb;

  // 底部 10%：暗色雪岭
  if (v > 0.84) {
    vec3 skyHz = skyBase(vec2(q.x, 0.9 * ASP));
    vec4 tr = terrain(q, skyHz);
    col = mix(col, tr.rgb, tr.a);
  }
  return col;
}
