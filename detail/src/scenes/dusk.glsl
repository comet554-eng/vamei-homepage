// ============ sky-dusk · 首屏背景 1500×2700 ============
// 坐标：q.x ∈ [0,1]（宽），q.y ∈ [0,ASP] 向下；v = 竖向比例 [0,1]
const float ASP = 1.8;
const float VH = 0.752;          // 地平线（被山遮住）
const float FOC = 1.13;          // 云层透视焦距（以宽为 1）
const vec2 MOON = vec2(0.165, 0.315 * 1.8);   // 左侧、标题下方，避开标题和雪板
const float MOON_R = 0.052;
const vec2 SUN = vec2(0.30, 0.80 * 1.8);   // 太阳在地平线下（屏幕坐标）

float PX;   // 一个设备像素（q 单位）

// ---------- 天空渐变 ----------
vec3 skyBase(vec2 q) {
  float v = q.y / ASP;
  // 0.00 .. 0.80 共 9 个色标，间隔 0.1
  vec3 s0 = L(0x14163A), s1 = L(0x1F2150), s2 = L(0x33336B), s3 = L(0x544C8B), s4 = L(0x8476AF),
       s5 = L(0xB09FC8), s6 = L(0xD3A8C3), s7 = L(0xEBB2B9), s8 = L(0xF4C4B6), s9 = L(0xF7D2BE);
  float t = clamp(v, 0.0, 0.8999) / 0.1;
  int i = int(floor(t)); float f = t - float(i);
  vec3 a, b, c, d;
  if (i == 0)      { a = s0; b = s0; c = s1; d = s2; }
  else if (i == 1) { a = s0; b = s1; c = s2; d = s3; }
  else if (i == 2) { a = s1; b = s2; c = s3; d = s4; }
  else if (i == 3) { a = s2; b = s3; c = s4; d = s5; }
  else if (i == 4) { a = s3; b = s4; c = s5; d = s6; }
  else if (i == 5) { a = s4; b = s5; c = s6; d = s7; }
  else if (i == 6) { a = s5; b = s6; c = s7; d = s8; }
  else if (i == 7) { a = s6; b = s7; c = s8; d = s9; }
  else             { a = s7; b = s8; c = s9; d = s9; }
  vec3 col = crOk(a, b, c, d, f);
  // 落日方向的地平线余晖（偏左），以及右侧略冷
  float dx = q.x - SUN.x;
  float hz = exp(-max(VH - v, 0.0) / 0.075);
  col += L(0xFFC9A6) * 0.22 * hz * exp(-dx * dx / 0.18);
  col = mix(col, col * vec3(0.92, 0.95, 1.06), smoothstep(0.3, 1.0, q.x) * (1.0 - hz) * 0.5);
  return col;
}

// ---------- 云层（透视云片 + 屏幕空间朝落日方向的光照步进） ----------
// 屏幕点 → 云片世界坐标
vec2 deckP(vec2 q, float alt, out float yu) {
  yu = max((VH - q.y / ASP) * ASP, 0.012);
  return vec2((q.x - 0.5) * alt / yu, FOC * alt / yu);
}
// 云形：域扭曲 fbm 定形 + 高频侵蚀边缘
float cloudShape(vec2 p, float cov, int oct, float warp, float soft) {
  vec2 w = vec2(fbm(p * 0.42 + vec2(1.3, 7.1), 3), fbm(p * 0.42 + vec2(8.4, 2.9), 3));
  p += w * warp;
  float n = fbmG(p, min(oct, 4), 0.52) * 2.3 + cov - 0.5;
  if (oct > 4) {
    float det = fbm(p * 5.3 + vec2(3.1, 9.4), oct - 4) * 2.3;
    n -= (1.0 - smoothstep(0.0, soft * 1.4, n)) * det * 0.30;
  }
  return smoothstep(0.0, soft, n);
}
// 高层 · 卷云（纤维状细丝，薄）
float deckA(vec2 q, int oct) {
  float yu; vec2 P = deckP(q, 2.2, yu);
  vec2 p = P * vec2(0.42, 1.25) + vec2(3.1, 0.0);
  float v = q.y / ASP;
  float band = smoothstep(0.22, 0.33, v) * (1.0 - smoothstep(0.50, 0.62, v));
  float side = mix(0.30, 1.0, smoothstep(0.10, 0.42, abs(q.x - 0.48)));
  float big = fbm(p * 0.33 + vec2(2.0, 5.0), 3) * 2.3;
  vec2 w = vec2(fbm(p * 0.7 + vec2(1.3, 7.1), 3), fbm(p * 0.7 + vec2(8.4, 2.9), 3));
  vec2 pf = p + w * 1.1;
  float fib = fbm(vec2(pf.x * 0.7, pf.y * 3.4), oct) * 2.3;
  float n = big * 0.75 + fib * 0.55 + band * side * 0.5 - 0.52;
  return smoothstep(0.0, 0.45, n) * band * side;
}
// 中层 · 层积云（主体，粉色底部）
float deckB(vec2 q, int oct) {
  float yu; vec2 P = deckP(q, 1.0, yu);
  vec2 p = P * vec2(1.25, 2.1) + vec2(-4.0, 1.0);
  float v = q.y / ASP;
  float big = fbm(p * 0.16 + vec2(9.1, 3.3), 3) * 2.2;
  float band = smoothstep(0.37, 0.50, v + fbm(p * 0.25 + 4.0, 2) * 0.06) * (1.0 - smoothstep(0.665, 0.715, v));
  float side = mix(0.30, 1.0, smoothstep(0.10, 0.40, abs(q.x - 0.5)));
  float cov = band * side * smoothstep(-0.5, 0.2, big);
  return cloudShape(p, cov * 0.72, oct, 1.9, 0.30) * cov;
}
// 地平线 · 低层薄云带
float deckC(vec2 q, int oct) {
  float yu; vec2 P = deckP(q, 0.35, yu);
  vec2 p = P * vec2(0.9, 0.5) + vec2(7.0, 0.0);
  float v = q.y / ASP;
  float band = smoothstep(0.645, 0.69, v) * (1.0 - smoothstep(0.735, 0.75, v));
  return cloudShape(p, band * 0.5, oct, 1.4, 0.5) * band * 0.75;
}

float deckD(int k, vec2 q, int oct) { return k == 0 ? deckA(q, oct) : (k == 1 ? deckB(q, oct) : deckC(q, oct)); }

vec4 cloudLayer(int k, vec2 q, vec3 sky) {
  float d = deckD(k, q, 6);
  if (d < 0.003) return vec4(0.0);
  vec2 ld = normalize(SUN - q);
  // 朝落日方向步进（屏幕空间），估计光学厚度
  float tau = 0.0;
  float st[4] = float[4](0.004, 0.009, 0.016, 0.027);
  for (int i = 0; i < 4; i++) tau += deckD(k, q + ld * st[i], 4);
  float T = exp(-tau * 1.0);
  float v = q.y / ASP;
  // 光色：越低越暖（桃色），越高越粉
  vec3 sunC = mix(L(0xF7A9BC), L(0xFFC9B0), smoothstep(0.42, 0.72, v)) * 1.05;
  vec3 amb = mixOk(sky, L(0x8277AD), 0.5) * 0.82;
  vec3 col = amb * (0.70 + 0.30 * (1.0 - d)) + sunC * (0.06 + 0.94 * T);
  // 银边：薄边缘、朝光方向
  col += sunC * 0.35 * T * (1.0 - d) * smoothstep(0.0, 0.3, d);
  // 远处云块融入地平线余晖
  float far = smoothstep(0.55, 0.74, v);
  col = mix(col, sky * 1.02, far * 0.45);
  float yu = max((VH - v) * ASP, 0.012);
  float thick = (k == 0 ? 1.1 : (k == 1 ? 3.4 : 2.5)) * (1.0 + 0.12 * FOC / yu);
  float a = 1.0 - exp(-d * thick);
  return vec4(col, a);
}

// ---------- 体积层积云（3D 光线步进 + 可平铺纹理噪声） ----------
// 相机在原点看 +z；云层位于高度 YB..YT（km）。落日在左前方地平线下，照亮云底。
uniform highp sampler3D uNoise3;
const float YB = 1.4, YT = 4.7, TMAX = 42.0;
const vec3 SUND = vec3(-0.22, -0.17, 1.0);
float remap(float v, float lo, float hi) { return clamp((v - lo) / (hi - lo), 0.0, 1.0); }
float blob(vec2 a, vec2 c, vec2 r) { vec2 d = (a - c) / r; return exp(-dot(d, d)); }
// 覆盖率：远处层积云（随机）+ 左右两侧的积云塔（构图用），中间留空
float cuCov(vec3 p, out float tower) {
  float sx = 0.5 + FOC * p.x / p.z;
  vec2 a = vec2(sx, p.z);
  float w = textureLod(uNoise3, vec3(p.xz * 0.045 + vec2(0.37, 0.11), 0.31), 0.0).r;
  float w2 = textureLod(uNoise3, vec3(p.xz * 0.013 + vec2(0.71, 0.53), 0.67), 0.0).r;
  tower = max(blob(a, vec2(0.0, 6.4), vec2(0.21, 2.2)), 0.92 * blob(a, vec2(1.0, 6.9), vec2(0.19, 2.4)));
  tower *= 0.75 + 0.5 * remap(w, 0.3, 0.7);
  float deck = remap(w, 0.34, 0.66) * (0.45 + 0.8 * remap(w2, 0.35, 0.65));
  float side = smoothstep(0.12, 0.40, abs(sx - 0.5));
  float zr = smoothstep(3.4, 6.5, p.z) * (1.0 - smoothstep(22.0, 36.0, p.z));
  // 顶部 28% 留给标题：按屏幕高度收掉
  float vs = VH - FOC * p.y / p.z / ASP;
  float topClear = smoothstep(0.27, 0.34, vs);
  return clamp(max(deck * side * zr * 0.85, tower), 0.0, 1.0) * topClear;
}
// 返回带符号的「云内余量」：>0 在云内（只含大形，不含细节）
float cuBase(vec3 p, out float hn) {
  float tower;
  float cov = cuCov(p, tower);
  hn = 0.0;
  if (cov < 0.03) return -1.0;
  float h = (p.y - YB) / (YT - YB);
  float topH = mix(0.24, 0.98, clamp(tower, 0.0, 1.0));
  hn = h / topH;
  float prof = smoothstep(0.0, 0.05 / topH, hn) * (1.0 - smoothstep(0.55, 1.0, hn));
  vec4 n = textureLod(uNoise3, p * 0.15 + vec3(0.13, 0.0, 0.71), 0.0);
  float shape = n.r * 0.55 + n.g * 0.45;
  float thr = 0.78 - 0.42 * cov * (0.25 + 0.75 * prof);
  return shape - thr;
}
// detail=false：光照步进用的平滑密度；true：带菜花状细节位移的密度
float cuDen(vec3 p, bool detail) {
  float hn;
  float b = cuBase(p, hn);
  if (!detail) return clamp((b + 0.015) / 0.07, 0.0, 1.0);
  if (b < -0.075) return 0.0;
  float near = 1.0 - smoothstep(7.0, 16.0, p.z);
  vec4 e = textureLod(uNoise3, p * 0.50 + vec3(0.5, 0.2, 0.0), 0.0);
  float e3 = near > 0.0 ? textureLod(uNoise3, p * 1.9 + vec3(0.7, 0.3, 0.9), 0.0).b : 0.48;
  float hh = clamp(hn, 0.0, 1.0);
  // 顶部更多翻卷（向外鼓），底部更平、带一点絮状
  float disp = (e.b - 0.47) * mix(0.13, 0.19, hh) + (e3 - 0.47) * 0.075 * near + (e.a - 0.47) * 0.035;
  disp -= 0.03 * smoothstep(0.0, -0.06, b);            // 远离主体处少长碎云
  float v = b + disp;
  return clamp(v / 0.03, 0.0, 1.0);
}
float hg(float c, float g) { float g2 = g * g; return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * c, 1.5)); }
vec4 cumulus(vec2 q, vec3 sky, vec3 skyHz) {
  vec3 rd = normalize(vec3(q.x - 0.5, VH * ASP - q.y, FOC));
  if (rd.y < 0.03) return vec4(0.0, 0.0, 0.0, 1.0);
  float t0 = YB / rd.y, t1 = min(YT / rd.y, TMAX);
  if (t0 >= TMAX) return vec4(0.0, 0.0, 0.0, 1.0);
  // 自适应步长：粗步探测（无侵蚀密度），命中后退回一步改用细步
  float dtc = max((t1 - t0) / 56.0, 0.04);
  float jit = hp(q * uRes.x, 41.0);
  float t = t0 + dtc * jit;
  vec3 sd = normalize(SUND);
  float cth = dot(rd, sd);
  vec3 sunC = mix(L(0xF7A8BC), L(0xFFC0A6), smoothstep(0.50, 0.70, q.y / ASP)) * 9.0;
  vec3 ambTop = L(0x5F5B9E) * 0.40, ambBot = L(0xA987B6) * 0.44;
  vec3 acc = vec3(0.0); float T = 1.0;
  float ls0[5] = float[5](0.04, 0.10, 0.24, 0.55, 1.2);
  int fine = 0; float tGuard = -1.0;
  for (int i = 0; i < 480; i++) {
    if (t > t1 || T < 0.01) break;
    vec3 p = rd * t;
    if (fine <= 0) {
      float hn0;
      if (cuBase(p, hn0) > -0.075) {
        if (t > tGuard) { tGuard = t; t = max(t - dtc, t0); }
        fine = int(dtc / clamp(t * 0.004, 0.012, 0.2)) * 2 + 4;
        continue;
      }
      t += dtc;
      continue;
    }
    float dtf = clamp(t * 0.004, 0.012, 0.2);
    float d = cuDen(p, true);
    if (d > 0.002) {
      fine = int(dtc / dtf) + 4;
      float tau = 0.0, sacc = 0.0;
      for (int j = 0; j < 5; j++) { sacc += ls0[j]; tau += cuDen(p + sd * sacc, false) * ls0[j]; }
      float sigE = d * 26.0;
      vec3 Ls = vec3(0.0); float a = 1.0, b = 1.0, c = 1.0;
      for (int k = 0; k < 3; k++) {
        Ls += a * exp(-tau * 20.0 * b) * mix(hg(cth, 0.3 * c), hg(cth, -0.15 * c), 0.4);
        a *= 0.36; b *= 0.25; c *= 0.5;
      }
      float h = clamp((p.y - YB) / (YT - YB), 0.0, 1.0);
      vec3 amb = mix(ambBot, ambTop, smoothstep(0.1, 0.9, h));
      float powder = 1.0 - 0.45 * exp(-d * 5.0);
      vec3 S = (sunC * Ls * powder + amb) * sigE;
      float fog = 1.0 - exp(-t / 30.0);
      S = mix(S, skyHz * sigE * 0.95, fog);
      float Tr = exp(-sigE * dtf);
      acc += T * (S - S * Tr) / max(sigE, 1e-4);
      T *= Tr;
    } else {
      fine = fine > 0 && t > tGuard ? fine - 1 : fine;
    }
    t += dtf;
  }
  return vec4(acc, T);
}

// ---------- 星 ----------
vec3 stars(vec2 fc, float vis) {
  if (vis <= 0.001) return vec3(0.0);
  float RP = uRes.x / 1500.0;          // 参考像素 → 设备像素
  vec2 sp = fc / RP;
  vec3 acc = vec3(0.0);
  for (int layer = 0; layer < 2; layer++) {
    float cs = layer == 0 ? 15.0 : 41.0;
    vec2 c = floor(sp / cs);
    vec4 r = h4(ivec2(c) + ivec2(layer * 9173, 0));
    float prob = layer == 0 ? 0.13 : 0.11;
    if (r.w > prob) continue;
    vec2 pos = (c + 0.25 + 0.5 * r.xy) * cs;
    float d2 = dot(sp - pos, sp - pos);
    float b = layer == 0 ? pow(r.z, 3.0) * 0.55 + 0.05 : pow(r.z, 2.0) * 1.6 + 0.25;
    float sig = layer == 0 ? 0.55 : 0.75 + 0.45 * r.z;
    float g = exp(-d2 / (2.0 * sig * sig));
    float halo = layer == 1 ? exp(-sqrt(d2) / 2.6) * 0.06 * r.z : 0.0;
    vec3 tint = mix(L(0xCFD8FF), L(0xFFE6D2), fract(r.z * 7.3));
    acc += tint * b * (g + halo);
  }
  return acc * vis;
}

// ---------- 月亮 ----------
vec4 moon(vec2 q, out vec3 glow) {
  vec2 d = (q - MOON) / MOON_R;
  float r = length(d);
  // 光晕：近处暖白、外圈带一点淡紫
  glow = L(0xFFF1E0) * (0.55 * exp(-max(r - 1.0, 0.0) * 4.0) * step(1.0, r) * 0.6 + 0.16 * exp(-max(r - 1.0, 0.0) / 1.4)) +
         L(0xC8B7E6) * 0.10 * exp(-max(r - 1.0, 0.0) / 4.5);
  float aa = PX / MOON_R;
  float m = 1.0 - smoothstep(1.0 - aa * 1.2, 1.0 + aa * 0.6, r);
  if (m <= 0.0) return vec4(0.0);
  float z = sqrt(max(1.0 - r * r, 0.0));
  vec3 n = vec3(d.x, -d.y, z);
  float mar = fbm3(n * 1.6 + vec3(2.0, 5.0, 1.0), 4);
  float maria = smoothstep(-0.02, 0.18, mar);
  float fine = fbm3(n * 9.0, 3);
  float alb = 1.0 - 0.17 * maria + 0.05 * fine;
  vec3 col = L(0xF6F1E6) * 1.28 * alb * (0.86 + 0.14 * pow(z, 0.5));
  col = mix(col, col * vec3(1.0, 0.94, 0.92), 0.25); // 落日余晖下略暖
  return vec4(col, m);
}

// ---------- 山脊（6 层剪影，自远而近，两两成组） ----------
// 每层：基线 v、峰高、频率、种子
vec4 RP0[6] = vec4[6](
  vec4(0.732, 0.062, 1.6, 11.0), vec4(0.752, 0.040, 2.1, 23.0),
  vec4(0.782, 0.060, 1.45, 37.0), vec4(0.803, 0.036, 2.4, 51.0),
  vec4(0.842, 0.070, 1.15, 71.0), vec4(0.872, 0.042, 1.9, 89.0));
// 山形：低频噪声过零处形成尖峰（凹形山腹），再叠加细碎岩脊
float peaks(float x, float f, float sd, int oct) {
  float n1 = noise(vec2(x * f, sd));
  float p = clamp(1.0 - abs(n1) * 1.9, 0.0, 1.0);
  p = p * p * (1.6 - 0.6 * p);
  float n2 = noise(vec2(x * f * 2.3 + 4.1, sd + 3.0));
  float p2 = clamp(1.0 - abs(n2) * 2.2, 0.0, 1.0); p2 *= p2;
  float h = max(p, p2 * 0.55) + 0.12 * fbm(vec2(x * f * 1.3, sd + 7.0), 2);
  if (oct > 2) {
    float r = ridged(vec2(x * f * 7.0, sd + 11.0), oct - 2);
    h += (r - 0.35) * 0.075 * (0.4 + h);
  }
  return h;
}
float crestN(int i, float x, int oct) {
  vec4 r = RP0[i];
  return r.x - r.y * peaks(x, r.z * 2.0, r.w, oct);
}
float crest(int i, float x) { return crestN(i, x, 7); }
// ---------- 光线步进雪山地形（三列山脉：近 / 中 / 远，山谷雾） ----------
float sq(float x) { return x * x; }
float rt(vec2 xz, float s, float o) {
  float r = textureLod(uNoise3, vec3(xz * s, o), 0.0).r;
  float k = clamp(1.0 - abs(r - 0.5) * 2.7, 0.0, 1.0);
  return k * k;
}
float terrH(vec2 xz, int lod) {
  float z = xz.y;
  float big = rt(xz, 0.021, 0.13);
  float big2 = rt(xz + vec2(11.0, 0.0), 0.034, 0.55);
  float mid = rt(xz + vec2(3.7, 1.1), 0.075, 0.41);
  float dt = 0.0;
  if (lod > 0) dt += rt(xz, 0.21, 0.77) * 0.05;
  if (lod > 1) dt += rt(xz, 0.62, 0.29) * 0.018;
  float e1 = exp(-sq((z - 4.3) / 0.75));
  float e2 = exp(-sq((z - 12.0) / 2.2));
  float e3 = smoothstep(22.0, 34.0, z);
  float rn = big2 * 0.80 + mid * 0.12 + dt;          // 近：大而圆润的雪岭
  float rm = big * 0.55 + big2 * 0.2 + mid * 0.2 + dt; // 中
  float rf = big * 0.64 + mid * 0.26 + dt * 1.5;      // 远：尖峰
  return -1.25 + e1 * (0.37 + 0.72 * rn) + e2 * (0.50 + 0.95 * rm) + e3 * (1.05 + 4.6 * rf);
}
vec3 terrN(vec3 p, float t) {
  float e = max(0.0009 * t, 0.002);
  float hx = terrH(p.xz + vec2(e, 0.0), 2) - terrH(p.xz - vec2(e, 0.0), 2);
  float hz = terrH(p.xz + vec2(0.0, e), 2) - terrH(p.xz - vec2(0.0, e), 2);
  return normalize(vec3(-hx, 2.0 * e, -hz));
}
vec3 terrShade(vec3 p, vec3 rd, float t, vec3 sky, vec3 skyHz) {
  vec3 n = terrN(p, t);
  vec3 ls = normalize(vec3(-0.62, 0.10, 0.78));         // 余晖：左后方、贴着地平线
  float dif = max(dot(n, ls), 0.0);
  float up = n.y;
  float steep = 1.0 - smoothstep(0.5, 0.85, up);
  vec3 alb = mix(vec3(0.94, 0.93, 0.98), L(0x5A5580) * 0.6, steep * 0.6);
  vec3 skyAmb = mix(L(0x2A2B60), L(0x7E77B8), 0.5 + 0.5 * up) * 0.5;
  vec3 sunC = L(0xFFB0B4) * 1.5;
  // 逆光边缘：法线与视线接近垂直且朝上 → 雪檐透光
  float edge = pow(1.0 - clamp(dot(n, -rd), 0.0, 1.0), 6.0) * smoothstep(0.2, 0.7, up);
  vec3 c = alb * (skyAmb + sunC * dif * 0.75) + L(0xF7B8C4) * edge * 0.55;
  // 大气透视（距离）+ 山谷雾（高度）
  float fogD = 1.0 - exp(-t / 24.0);
  float hf = exp(-max(p.y + 1.2, 0.0) / 0.28);
  vec3 fogC = mixOk(L(0x8E8AB5), skyHz, smoothstep(9.0, 45.0, t));
  vec3 mistC = mixOk(L(0xB8A6D0), L(0xEEC4CB), smoothstep(6.0, 30.0, t));
  c = mix(c, mistC, clamp(hf * (0.45 + 0.55 * smoothstep(1.5, 12.0, t)), 0.0, 0.9));
  c = mix(c, fogC, fogD * 0.94);
  return c;
}
// 沿视线步进，返回命中距离（未命中返回 -1），以及最近掠过信息
// best/tBest：视线在命中前「局部最近掠过」某条山脊的高度（以像素计）与距离
float terrMarch(vec3 rd, out float best, out float tBest) {
  float pxA = 1.0 / (uRes.x * FOC);
  float t = 0.6, tPrev = t;
  best = 1e9; tBest = 0.0;
  float r1 = 1e9, r2 = 1e9, t1 = 0.0, t2 = 0.0;   // 前一步、前两步
  float bLo = 0.0, bHi = 0.0;
  bool hit = false;
  for (int i = 0; i < 220; i++) {
    vec3 p = rd * t;
    float hgt = p.y - terrH(p.xz, t < 18.0 ? 1 : 0);
    if (hgt < 0.0) { hit = true; break; }
    float ratio = hgt / (t * pxA);
    if (r1 < r2 && r1 <= ratio && r1 < best) { best = r1; tBest = t1; bLo = t2; bHi = t; }
    r2 = r1; t2 = t1; r1 = ratio; t1 = t;
    tPrev = t;
    t += max(hgt * 0.42, 0.0012 * t);
    if (t > 90.0 || p.y > 3.6) break;
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
vec3 camRay(vec2 q) { return normalize(vec3(q.x - 0.5, VH * ASP - q.y, FOC)); }
// 返回 rgb + 覆盖率；用最近掠过点做剪影抗锯齿；山脊顶部加逆光雪檐
vec4 terrain(vec2 q, vec3 sky, vec3 skyHz) {
  vec3 rd = camRay(q);
  float best, tBest;
  float t = terrMarch(rd, best, tBest);
  if (t < 0.0) {
    if (best < 1.2) {
      vec3 pb = rd * tBest;
      return vec4(terrShade(pb, rd, tBest, sky, skyHz), clamp(1.0 - best / 1.2, 0.0, 1.0) * 0.98);
    }
    return vec4(0.0);
  }
  vec3 c = terrShade(rd * t, rd, t, sky, skyHz);
  if (best < 1.2 && tBest < t * 0.92) {
    vec3 cb = terrShade(rd * tBest, rd, tBest, sky, skyHz);
    c = mix(c, cb, clamp(1.0 - best / 1.2, 0.0, 1.0));
  }
  // 雪檐逆光：向上偏移 5px 再探一次；若越过山脊，则用其最近掠过高度换算本像素到山脊线的连续距离
  float rp = 1.0 / 1500.0;
  const float K = 5.0;
  float b2, tb2;
  float tu = terrMarch(camRay(q - vec2(0.0, K * rp)), b2, tb2);
  if ((tu < 0.0 || tu > t * 1.2) && tb2 < t * 1.2) {
    float pxScale = uRes.x / 1500.0;            // best 以设备像素计
    float below = K - b2 / pxScale;             // 本像素在山脊线下方多少参考像素
    float rim = exp(-max(below, 0.0) / 2.2) * smoothstep(-0.5, 0.8, below);
    float fogD = exp(-t / 20.0);
    vec3 pp = rd * t;
    float sunSide = 0.55 + 0.45 * smoothstep(0.5, -0.3, pp.x / pp.z);
    c = mix(c, L(0xF6BCC6) * 1.05, clamp(rim, 0.0, 1.0) * 0.72 * fogD * sunSide);
  }
  return vec4(c, 1.0);
}

// 前景雪坡
float slope(float x) {
  return 0.918 + 0.022 * x - 0.010 * sin(x * 2.4 + 0.6) + 0.003 * fbm(vec2(x * 6.0, 3.3), 3);
}

vec3 sceneColor(vec2 fc) {
  PX = 1.0 / uRes.x;
  vec2 q = fc / uRes.x;
  float v = q.y / ASP;
  vec3 sky = skyBase(q);
  vec3 col = sky;
  if (uDbg > 1.5) {
    vec3 skyHz = skyBase(vec2(q.x, 0.70 * ASP));
    if (v < 0.62) return col;
    vec4 tr = terrain(q, sky, skyHz);
    return mix(col, tr.rgb, tr.a);
  }
  if (uDbg > 0.5) {
    vec3 skyHz = skyBase(vec2(q.x, 0.70 * ASP));
    vec4 cu = cumulus(q, sky, skyHz);
    return col * cu.a + cu.rgb;
  }

  // 星：上部可见，越往下越淡
  float starVis = 1.0 - smoothstep(0.14, 0.36, v);
  vec3 mglow;
  vec4 mo = moon(q, mglow);
  float nearMoon = smoothstep(0.0, 0.25, length(q - MOON) - MOON_R);
  col += stars(fc, starVis * nearMoon);
  // 月亮
  col += mglow;
  col = mix(col, mo.rgb, mo.a);

  // 云：高 → 中 → 低（近的覆盖远的）
  {
    vec4 c = cloudLayer(2, q, sky); col = mix(col, c.rgb, c.a);
    float v0 = q.y / ASP;
    if (v0 > 0.22 && v0 < 0.74) {
      vec3 skyHz = skyBase(vec2(q.x, 0.70 * ASP));
      vec4 cu = cumulus(q, sky, skyHz);
      col = col * cu.a + cu.rgb;
    }
  }

  // 雪山：光线步进地形（远 / 中 / 近三列山脉 + 谷雾）
  if (v > 0.62) {
    vec3 skyHz = skyBase(vec2(q.x, 0.70 * ASP));
    vec4 tr = terrain(q, sky, skyHz);
    col = mix(col, tr.rgb, tr.a);
  }

  // 前景雪坡
  {
    float sy = slope(q.x);
    float ds = (slope(q.x + PX * 2.0) - slope(q.x - PX * 2.0)) / (PX * 4.0) * ASP;
    float dy = (v - sy) * ASP;
    float dist = dy / sqrt(1.0 + ds * ds);
    float cov = smoothstep(-PX * 0.8, PX * 0.8, dist);
    if (cov > 0.0) {
      float dd = max(dy, 0.0);
      // 透视地面坐标：越靠近坡顶越远
      float dz = 0.9 / (dd + 0.012);
      vec2 g = vec2((q.x - 0.5) * dz, dz);
      // 雪面：上部反射地平线余晖（偏粉），下部反射天顶（偏靛）
      vec3 sn = mixOk(L(0xBFAFD6), L(0x5E5A98), smoothstep(0.0, 0.17, dd));
      sn = mixOk(sn, L(0xF0C3CB), 0.55 * exp(-dd / 0.012));
      // 风蚀雪纹：高度场 → 用横向斜率做掠射光照
      vec2 gp = vec2(g.x * 1.6 + g.y * 0.35, g.y * 4.2);
      float e = 0.02;
      float h0 = fbm(gp, 4), hx = fbm(gp + vec2(e, 0.0), 4);
      float shade = clamp((hx - h0) / e * 0.9, -1.0, 1.0);
      float fade = smoothstep(0.004, 0.05, dd);
      sn *= 1.0 + shade * 0.10 * fade;
      sn = mix(sn, sn * mixOk(vec3(1.0), L(0xF6C7CF), 0.5) * 1.06, max(shade, 0.0) * fade * 0.5);
      // 底部与两角压暗，托住画面
      float vig = smoothstep(0.02, 0.16, dd) * (0.10 + 0.25 * sq(q.x - 0.5) * 4.0);
      sn *= 1.0 - vig;
      // 冰晶闪光：近处稍大、稀疏
      float RP = uRes.x / 1500.0;
      vec2 sp = fc / RP;
      float cs = 11.0;
      vec2 c = floor(sp / cs);
      vec4 r = h4(ivec2(c) + ivec2(777, 313));
      float near = smoothstep(0.0, 0.12, dd);
      if (r.w < 0.012 + 0.035 * near) {
        vec2 pos = (c + 0.3 + 0.4 * r.xy) * cs;
        vec2 dv = sp - pos;
        float d2 = dot(dv, dv);
        float sz = mix(0.3, 0.7, near);
        float b = pow(r.z, 3.0) * (0.6 + 1.4 * near);
        float spark = exp(-d2 / sz) + 0.18 * exp(-abs(dv.x) * 1.6 - dv.y * dv.y * 4.0) * step(0.85, r.z) + 0.18 * exp(-abs(dv.y) * 1.6 - dv.x * dv.x * 4.0) * step(0.85, r.z);
        sn += mix(L(0xFFE6E4), L(0xE2E4FF), fract(r.z * 5.1)) * b * spark * smoothstep(0.0, 0.02, dd);
      }
      col = mix(col, sn, cov);
    }
  }
  return col;
}
