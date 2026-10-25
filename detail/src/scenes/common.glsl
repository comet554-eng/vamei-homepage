#version 300 es
// 公共函数：哈希、梯度噪声、fbm、颜色空间、色调曲线、抖动与胶片颗粒
precision highp float;
precision highp int;
uniform vec2 uRes;    // 设备像素
uniform float uSeed;
uniform float uDbg;   // 调试视图
out vec4 fragColor;

#define PI 3.14159265359
#define TAU 6.28318530718

// ---------------- hashing ----------------
uint hu(uint x) { x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x; }
uint hu2(ivec2 p) { return hu(uint(p.x) * 0x9E3779B1u ^ hu(uint(p.y) + 0x632BE5ABu + uint(uSeed) * 0x85EBCA6Bu)); }
uint hu3(ivec3 p) { return hu(uint(p.x) * 0x9E3779B1u ^ hu(uint(p.y) * 0xC2B2AE35u ^ hu(uint(p.z) + 0x27D4EB2Fu + uint(uSeed) * 0x85EBCA6Bu))); }
const float INV32 = 1.0 / 4294967296.0;
float h1(ivec2 p) { return float(hu2(p)) * INV32; }
vec2 h2(ivec2 p) { uint a = hu2(p); return vec2(float(a), float(hu(a ^ 0x5bd1e995u))) * INV32; }
vec3 h3v(ivec2 p) { uint a = hu2(p); uint b = hu(a ^ 0x5bd1e995u); return vec3(float(a), float(b), float(hu(b ^ 0x68e31da4u))) * INV32; }
vec4 h4(ivec2 p) { uint a = hu2(p); uint b = hu(a ^ 0x5bd1e995u); uint c = hu(b ^ 0x68e31da4u); return vec4(float(a), float(b), float(c), float(hu(c ^ 0x1b56c4e9u))) * INV32; }
float hp(vec2 fc, float s) { return float(hu2(ivec2(fc) + ivec2(int(s) * 7919, int(s) * 104729))) * INV32; }

// ---------------- gradient noise ----------------
vec2 g2(ivec2 i) { uint a = hu2(i); return vec2(float(a), float(hu(a ^ 0x5bd1e995u))) * (2.0 * INV32) - 1.0; }
float noise(vec2 p) {
  vec2 fl = floor(p); ivec2 i = ivec2(fl); vec2 f = p - fl;
  vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  float a = dot(g2(i), f);
  float b = dot(g2(i + ivec2(1, 0)), f - vec2(1, 0));
  float c = dot(g2(i + ivec2(0, 1)), f - vec2(0, 1));
  float d = dot(g2(i + ivec2(1, 1)), f - vec2(1, 1));
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
vec3 g3(ivec3 i) { uint a = hu3(i); uint b = hu(a ^ 0x5bd1e995u); return vec3(float(a), float(b), float(hu(b ^ 0x68e31da4u))) * (2.0 * INV32) - 1.0; }
float noise3(vec3 p) {
  vec3 fl = floor(p); ivec3 i = ivec3(fl); vec3 f = p - fl;
  vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  float n000 = dot(g3(i), f);
  float n100 = dot(g3(i + ivec3(1, 0, 0)), f - vec3(1, 0, 0));
  float n010 = dot(g3(i + ivec3(0, 1, 0)), f - vec3(0, 1, 0));
  float n110 = dot(g3(i + ivec3(1, 1, 0)), f - vec3(1, 1, 0));
  float n001 = dot(g3(i + ivec3(0, 0, 1)), f - vec3(0, 0, 1));
  float n101 = dot(g3(i + ivec3(1, 0, 1)), f - vec3(1, 0, 1));
  float n011 = dot(g3(i + ivec3(0, 1, 1)), f - vec3(0, 1, 1));
  float n111 = dot(g3(i + ivec3(1, 1, 1)), f - vec3(1, 1, 1));
  return mix(mix(mix(n000, n100, u.x), mix(n010, n110, u.x), u.y),
             mix(mix(n001, n101, u.x), mix(n011, n111, u.x), u.y), u.z);
}
// value noise (cheaper, for 1D-ish ridges)
float vnoise(vec2 p) {
  vec2 fl = floor(p); ivec2 i = ivec2(fl); vec2 f = p - fl;
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(h1(i), h1(i + ivec2(1, 0)), u.x), mix(h1(i + ivec2(0, 1)), h1(i + ivec2(1, 1)), u.x), u.y);
}

const mat2 ROT = mat2(0.80, 0.60, -0.60, 0.80);
float fbm(vec2 p, int oct) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 10; i++) { if (i >= oct) break; s += a * noise(p); p = ROT * p * 2.03 + vec2(13.7, -7.3); a *= 0.5; }
  return s;
}
float fbmG(vec2 p, int oct, float gain) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 10; i++) { if (i >= oct) break; s += a * noise(p); p = ROT * p * 2.03 + vec2(13.7, -7.3); a *= gain; }
  return s;
}
float fbm3(vec3 p, int oct) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 8; i++) { if (i >= oct) break; s += a * noise3(p); p = p * 2.02 + vec3(13.7, -7.3, 4.1); p.xy = ROT * p.xy; a *= 0.5; }
  return s;
}
// ridged multifractal (山脊)
float ridged(vec2 p, int oct) {
  float s = 0.0, a = 0.5, w = 1.0;
  for (int i = 0; i < 10; i++) {
    if (i >= oct) break;
    float n = 1.0 - abs(noise(p) * 1.6);
    n = n * n;
    s += a * n * w;
    w = clamp(n * 1.4, 0.0, 1.0);
    p = ROT * p * 2.07 + vec2(5.3, 1.7); a *= 0.5;
  }
  return s;
}

// ---------------- colour ----------------
vec3 hexc(int h) { return vec3(float((h >> 16) & 255), float((h >> 8) & 255), float(h & 255)) / 255.0; }
vec3 toLin(vec3 c) { return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c)); }
vec3 toSrgb(vec3 c) { c = max(c, 0.0); return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }
vec3 L(int h) { return toLin(hexc(h)); }
float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

vec3 lin2oklab(vec3 c) {
  vec3 lms = mat3(0.4122214708, 0.2119034982, 0.0883024619,
                  0.5363325363, 0.6806995451, 0.2817188376,
                  0.0514459929, 0.1073969566, 0.6299787005) * c;
  lms = pow(max(lms, 0.0), vec3(1.0 / 3.0));
  return mat3(0.2104542553, 1.9779984951, 0.0259040371,
              0.7936177850, -2.4285922050, 0.7827717662,
              -0.0040720468, 0.4505937099, -0.8086757660) * lms;
}
vec3 oklab2lin(vec3 c) {
  vec3 lms = mat3(1.0, 1.0, 1.0,
                  0.3963377774, -0.1055613458, -0.0894841775,
                  0.2158037573, -0.0638541728, -1.2914855480) * c;
  lms = lms * lms * lms;
  return mat3(4.0767416621, -1.2684380046, -0.0041960863,
              -3.3077115913, 2.6097574011, -0.7034186147,
              0.2309699292, -0.3413193965, 1.7076147010) * lms;
}
// 感知均匀的颜色插值（线性光输入输出）
vec3 mixOk(vec3 a, vec3 b, float t) { return oklab2lin(mix(lin2oklab(a), lin2oklab(b), t)); }
// Catmull-Rom 过等距色标（OKLab 空间），t∈[0,1]
vec3 crOk(vec3 a, vec3 b, vec3 c, vec3 d, float t) {
  vec3 p0 = lin2oklab(a), p1 = lin2oklab(b), p2 = lin2oklab(c), p3 = lin2oklab(d);
  float t2 = t * t, t3 = t2 * t;
  vec3 r = 0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3);
  return oklab2lin(r);
}

// 胶片肩部：k 以下保持不变，以上柔和压缩（逐通道 → 高光自然趋向白）
vec3 shoulder(vec3 x, float k) {
  vec3 y = k + (1.0 - k) * (1.0 - exp(-(x - k) / (1.0 - k)));
  return mix(x, y, step(vec3(k), x));
}

// 最终输出：色调曲线 → sRGB → 胶片颗粒 → 三角分布抖动
float GRAIN = 0.010;
vec3 finalize(vec3 lin, vec2 fc) {
  vec3 c = toSrgb(shoulder(max(lin, 0.0), 0.78));
  float l = clamp(dot(c, vec3(0.3, 0.59, 0.11)), 0.0, 1.0);
  // 颗粒：两层（单像素 + 2px 团簇）混合，亮部与暗部略少
  vec2 g = fc;
  float n1 = hp(g, 11.0) + hp(g, 23.0) - 1.0;
  float n2 = vnoise(g * 0.55 + 31.7) - 0.5;
  float grain = (n1 * 0.55 + n2 * 1.1) * GRAIN * (0.35 + 2.6 * l * (1.0 - l));
  c += grain;
  c += (hp(g, 3.0) + hp(g, 5.0) - 1.0) / 255.0;
  return clamp(c, 0.0, 1.0);
}

vec3 sceneColor(vec2 fc);
