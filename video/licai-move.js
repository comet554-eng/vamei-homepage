/* 李财动起来：让表情贴纸“活”的动作工具（依赖 snowkit.js + licaikit.js）
 * catWarp  分条变形：脚底固定，上半身摇摆 / 腿部前后甩 / 挤压拉伸
 * catRide  骑车：踩踏起伏 + 上身随踏频晃 + 车轮转动叠加 + 扬尘 + 速度线
 * catRun   奔跑：跳跃弧线 + 落地挤压 + 甩腿 + 残影 + 扬尘
 * catSkate 滑板：手绘滑板（轮子会转）+ 身体前后压 + 可跳台
 * flipbook 多张表情按节拍切换（简易逐帧）
 * 坐标约定：(x, y) 为脚底中心，h 为图片高度
 */

// 分条绘制：o.dx(u) 返回高度 u（0 脚底 → 1 头顶）处的横向偏移；o.sx/o.sy 挤压拉伸；o.rot 绕脚底旋转
function catWarp(name, x, y, h, o) {
  o = o || {}; var im = IMG[name]; if (!im) return;
  var w = h * im.width / im.height, N = o.strips || 60, sh = im.height / N, dh = h / N;
  g.save(); g.translate(x, y); if (o.rot) g.rotate(o.rot);
  g.scale((o.flip ? -1 : 1) * (o.sx || 1), o.sy || 1); g.globalAlpha = o.a == null ? 1 : o.a;
  for (var i = 0; i < N; i++) {
    var u = 1 - (i + .5) / N, dx = o.dx ? o.dx(u) : 0;
    g.drawImage(im, 0, i * sh, im.width, sh, -w / 2 + dx, -h + i * dh, w, dh + .7);
  }
  g.restore();
}

// 扬尘：一团团手绘小云，age 秒后散开消失
function dustPuff(x, y, age, seed, s) {
  if (age < 0 || age > .9) return; s = s || 1;
  var k = age / .9, r = (14 + 26 * eout(k)) * s;
  g.save(); g.globalAlpha = (1 - k) * .75; g.fillStyle = '#F3E6CF'; g.strokeStyle = '#C9B08A'; g.lineWidth = 2.5;
  for (var i = 0; i < 3; i++) {
    var cx = x + (i - 1) * r * .8 + jit(seed + i, 4), cy = y - k * 22 * s - (i === 1 ? r * .4 : 0);
    g.beginPath(); g.arc(cx, cy, r * (i === 1 ? 1 : .75), 0, 6.283); g.fill(); g.stroke();
  }
  g.restore();
}
// 横向速度线（在 x 左侧拖出）
function speedLines(x, y, h, t, a, seed, len) {
  g.save(); g.globalAlpha = a; g.strokeStyle = C.sub; g.lineCap = 'round';
  for (var i = 0; i < 7; i++) {
    var yy = y - h / 2 + (i + .5) * h / 7 + jit(seed + i, 10), ph = (t * 2.4 + rnd(seed + i * 7)) % 1, L = (len || 180) * (.5 + rnd(seed + i * 3) * .6);
    var x1 = x - 40 - ph * 260; g.lineWidth = 3 + rnd(seed + i) * 3; g.globalAlpha = a * (1 - ph);
    g.beginPath(); g.moveTo(x1, yy); g.lineTo(x1 - L, yy); g.stroke();
  }
  g.restore();
}
// 会往后跑的路：地面线 + 路面短划 + 远处小树/云（视差）
function scrollGround(y, off, opt) {
  opt = opt || {};
  hline(0, y, W, y + 2, 51, C.ink, 5);
  g.save(); g.strokeStyle = C.gray; g.lineWidth = 6; g.lineCap = 'round';
  for (var x = -((off) % 160); x < W + 160; x += 160) { g.beginPath(); g.moveTo(x, y + 40); g.lineTo(x + 70, y + 40); g.stroke(); }
  g.restore();
  if (opt.trees === false) return;
  var o2 = off * .35;
  for (var i = -1; i < 7; i++) {
    var base = i * 360 - (o2 % 360), tx = base + 120, k = ((Math.floor(o2 / 360) + i) % 3 + 3) % 3;
    hline(tx, y, tx, y - 90, 60 + i, C.brown, 6);
    hcircle(tx, y - 130, 48 + k * 8, 52 + k * 8, 70 + k, C.green, 5);
  }
  var o3 = off * .12;
  for (var j = -1; j < 4; j++) { var cxx = j * 640 - (o3 % 640) + 300; hcircle(cxx, 300 + (j % 2) * 50, 70, 26, 80 + j, C.gray, 4); hcircle(cxx + 60, 288 + (j % 2) * 50, 46, 22, 90 + j, C.gray, 4); }
}

// 车轮转动：在图上车轮的位置叠加旋转的辐条残影；wh = [[u, v, rx, ry, tilt], ...] 以图片宽高为 1
function wheelSpin(name, x, y, h, wh, rot, a) {
  var im = IMG[name]; if (!im) return; var w = h * im.width / im.height;
  g.save(); g.lineCap = 'round';
  wh.forEach(function (q, qi) {
    var cx = x - w / 2 + q[0] * w, cy = y - h + q[1] * h, rx = q[2] * w, ry = q[3] * h;
    g.save(); g.translate(cx, cy); g.rotate(q[4] || 0); g.scale(1, ry / rx);
    g.globalAlpha = (a == null ? 1 : a) * (qi ? .5 : .85);
    for (var k = 0; k < 3; k++) {
      var a0 = rot + k * 2.094;
      g.strokeStyle = 'rgba(50,45,40,.8)'; g.lineWidth = 5;
      g.beginPath(); g.arc(0, 0, rx * .82, a0, a0 + 1.1); g.stroke();
      g.strokeStyle = 'rgba(255,255,255,.9)'; g.lineWidth = 4;
      g.beginPath(); g.arc(0, 0, rx * .55, a0 + 1, a0 + 1.7); g.stroke();
      g.strokeStyle = 'rgba(50,45,40,.6)'; g.lineWidth = 3;
      g.beginPath(); g.moveTo(Math.cos(a0) * rx * .12, Math.sin(a0) * rx * .12); g.lineTo(Math.cos(a0) * rx * .7, Math.sin(a0) * rx * .7); g.stroke();
    }
    g.restore();
  });
  g.restore();
}
// 两张骑车图的车轮位置
var WHEELS = {
  '戴头盔骑车': [[.666, .803, .105, .108, -.1], [.298, .722, .06, .1, -.15]],
  '骑车冲坡': [[.519, .799, .095, .1, -.3], [.281, .715, .055, .088, -.35]]
};

// 骑车：t 为本段时间；o.cad 踏频（圈/秒）、o.speed 地面速度（像素/秒，用于扬尘漂移）
function catRide(name, x, y, h, t, o) {
  o = o || {}; var cad = o.cad || 1.4, p = t * cad * 6.283;
  var bob = -Math.abs(Math.sin(p)) * h * .018, rock = Math.sin(p) * .02;
  var im = IMG[name]; if (!im) return; var w = h * im.width / im.height;
  // 扬尘（后轮处，往后飘）
  if (o.dust !== false) for (var d = 0; d < 4; d++) {
    var age = ((t * 4) % 1 + d) / 4; if (t - age < 0) continue;
    dustPuff(x - w * .3 - age * (o.speed || 500) * .6, y - 10, age, Math.floor(t * 4) - d, h / 600);
  }
  if (o.lines !== false) speedLines(x - w * .35, y - h * .5, h * .7, t, .6, 7, 200);
  g.save(); g.translate(x, y + bob); g.rotate(rock + (o.tilt || 0));
  catWarp(name, 0, 0, h, { dx: function (u) { return u > .42 ? (u - .42) * Math.sin(p) * h * .05 : 0; }, sy: 1 + Math.sin(p * 2) * .008 });
  wheelSpin(name, 0, 0, h, WHEELS[name] || [], t * (o.spin || 14));
  g.restore();
}

// 奔跑：o.hz 步频；o.hop 腾空高度；o.trail 残影
function catRun(name, x, y, h, t, o) {
  o = o || {}; var hz = o.hz || 3, ph = (t * hz) % 1, air = Math.sin(Math.PI * ph);
  var land = ph < .12 ? 1 - ph / .12 : 0, hop = (o.hop == null ? h * .12 : o.hop) * air;
  var sx = 1 + land * .1 - air * .04, sy = 1 - land * .12 + air * .05, leg = Math.sin(ph * 6.283);
  var im = IMG[name]; if (!im) return; var w = h * im.width / im.height;
  for (var d = 0; d < 4; d++) { var age = (ph + d) / hz; dustPuff(x - w * .25 - age * (o.speed || 600) * .5, y - 6, age, d * 17 + Math.floor(t * hz) - d, h / 420); }
  if (o.lines !== false) speedLines(x - w * .3, y - h * .5, h * .8, t, .55, 11, 220);
  var draw = function (xx, a) {
    catWarp(name, xx, y - hop, h, {
      a: a, sx: sx, sy: sy, flip: o.flip, rot: (o.lean || .06) + leg * .03,
      dx: function (u) { return u < .38 ? (.38 - u) * leg * h * .32 : (u - .38) * -leg * h * .04; }
    });
  };
  if (o.trail !== false) for (var k = 3; k >= 1; k--) draw(x - k * w * .16, .12 / k);
  draw(x, 1);
}

// 手绘滑板：rot 为板子倾角，wr 为轮子转角
function skateboard(x, y, len, rot, wr) {
  g.save(); g.translate(x, y); g.rotate(rot || 0); g.lineCap = 'round';
  var L = len / 2;
  g.strokeStyle = C.ink; g.lineWidth = 6;
  g.beginPath(); g.moveTo(-L - 26, -22); g.quadraticCurveTo(-L - 6, 2, -L + 20, 2); g.lineTo(L - 20, 2); g.quadraticCurveTo(L + 6, 2, L + 26, -22); g.stroke();
  g.strokeStyle = C.orange; g.lineWidth = 12; g.beginPath(); g.moveTo(-L + 10, -6); g.lineTo(L - 10, -6); g.stroke();
  [-L * .62, L * .62].forEach(function (wx, i) {
    hline(wx - 14, 10, wx + 14, 10, 300 + i, C.ink, 5);
    g.save(); g.translate(wx, 30); g.fillStyle = PAPER; g.strokeStyle = C.ink; g.lineWidth = 5;
    g.beginPath(); g.arc(0, 0, 17, 0, 6.283); g.fill(); g.stroke();
    g.rotate(wr || 0); g.lineWidth = 3; g.beginPath(); g.moveTo(-11, 0); g.lineTo(11, 0); g.moveTo(0, -11); g.lineTo(0, 11); g.stroke();
    g.restore();
  });
  g.restore();
}
// 滑板：o.jump = [起跳时刻, 时长, 高度]
function catSkate(name, x, y, h, t, o) {
  o = o || {}; var len = o.len || h * .7, jy = 0, jr = 0, sq = 0;
  if (o.jump) {
    var q = (t - o.jump[0]) / o.jump[1];
    if (q > 0 && q < 1) { jy = Math.sin(Math.PI * q) * o.jump[2]; jr = Math.sin(q * 6.283) * -.22; }
    if (q >= 1 && q < 1.35) sq = Math.sin((q - 1) / .35 * Math.PI) * .12;
    if (q > -.25 && q <= 0) sq = Math.sin((q + .25) / .25 * Math.PI) * .1;
  }
  var lean = Math.sin(t * 2.2) * .5;
  for (var d = 0; d < 3 && jy === 0; d++) { var age = ((t * 3 + d) % 3) / 3; dustPuff(x - len * .55 - age * 200, y + 44, age, 40 + d + Math.floor(t * 3), .6); }
  if (o.lines !== false) speedLines(x - len * .5, y - h * .45, h * .7, t, .5, 23, 200);
  g.save(); g.translate(x, y - jy); g.rotate(jr);
  catWarp(name, 0, -2, h, { sy: 1 - sq, sx: 1 + sq * .6, dx: function (u) { return u * lean * h * .06; } });
  skateboard(0, 0, len, 0, t * 12);
  g.restore();
}

// 逐帧：按 fps 在 names 间切换，每次切换带一点弹跳
function flipbook(names, x, y, h, t, fps, o) {
  o = o || {}; var i = Math.floor(t * fps), f = t * fps - i, name = names[i % names.length];
  var b = f < .25 ? 1 + Math.sin(f / .25 * Math.PI) * .06 : 1;
  catWarp(name, x, y, h, { sx: 2 - b, sy: b, dx: o.sway ? function (u) { return u * Math.sin(t * 6.283 * o.sway) * h * .05; } : null });
  return i;
}

// 逐帧动作（licai-seq.js）：(x, y) 为底线中心，h 为整组高度；o.once 播一遍后停在最后一帧；o.frame 直接指定帧
var SEQ_FRAMES = { '打招呼': [2, 3, 4, 5, 4, 3] };
// 画错的帧（坐着抬爪时底下还画着两只前爪 = 五只脚），播放时跳过；好帧少于 3 张的整组停用，改用静态图
var SEQ_BAD = {
  '挥手': [1, 2, 3, 4, 5, 6], '点头指向': [3, 4, 5, 6], '开心挥手': [1, 2, 3, 4, 5, 6], '摆爪否定': [0, 2, 4, 6],
  '举手': [2, 3, 4, 5, 6], '思考怀疑': [4], '放大镜': [1, 2, 3, 5, 6, 7], '抬头张望': [1, 2, 4, 5],
  '眺望': [0, 1, 2, 3, 4, 5, 6, 7], '偷笑': [3, 4, 6], '望远镜': [1], '拍照2': [0], '害羞捂脸': [1, 6]
};
var SEQ_FALLBACK = { '开心挥手': 'wave', '挥手': 'wave', '眺望': '期待星星眼' };
function seqGood(name) {
  var n = LICAI_SEQ[name].frames.length, bad = SEQ_BAD[name] || [], g = [];
  for (var i = 0; i < n; i++) if (bad.indexOf(i) < 0) g.push(i);
  return g;
}
function seqUsable(name) { return !!LICAI_SEQ[name] && seqGood(name).length >= 3; }

function seqDraw(name, t, fps, x, y, h, o) {
  o = o || {};
  if (!seqUsable(name)) { var fb = IMG[SEQ_FALLBACK[name] || 'wave']; if (fb) { var fw = h * fb.width / fb.height; g.save(); g.globalAlpha = o.a == null ? 1 : o.a; g.translate(x, y); g.scale(o.flip ? -1 : 1, 1); g.drawImage(fb, -fw / 2, -h, fw, h); g.restore(); } return 0; }
  if (!o.frames && o.frame == null) o.frames = (!o.once && SEQ_FRAMES[name]) || seqGood(name); if (!o.frames && o.frame == null && !o.once && SEQ_FRAMES[name]) o.frames = SEQ_FRAMES[name]; var S = LICAI_SEQ[name], n = S.frames.length;
  var i = o.frame != null ? o.frame : Math.floor(Math.max(0, t) * fps);
  if (o.frames) { var L = o.frames.length; i = o.frames[o.once ? Math.min(i, L - 1) : ((i % L) + L) % L]; }
  else i = o.once ? Math.min(i, n - 1) : ((i % n) + n) % n;
  var f = S.frames[i], im = IMG['seq:' + name + ':' + i]; if (!im) return i;
  var s = h / S.ref;
  g.save(); g.translate(x, y); if (o.rot) g.rotate(o.rot); g.scale((o.flip ? -1 : 1) * (o.sx || 1), o.sy || 1);
  g.globalAlpha = o.a == null ? 1 : o.a;
  g.drawImage(im, f.x * s, f.y * s, f.w * s, f.h * s);
  g.restore(); return i;
}

// 静态表情 → 逐帧动作的对照：[动作名, 帧率, 只播一遍, 高度系数]
var ANIM_RAW = {
  '期待星星眼': ['打招呼', 6, false, 1], '握拳加油': ['举手欢迎', 6, false, 1], '张开双臂': ['举手欢迎', 6, false, 1],
  '星星眼开心': ['打招呼', 6, false, 1], '跳起欢呼': ['蹦跳欢呼', 7, false, 1.1], '举旗欢呼': ['蹦跳欢呼', 7, false, 1.1], '唱歌跳舞': ['开心挥手', 6, false, 1],
  '震惊': ['吓一跳', 7, true, 1.1], '被吓一跳': ['吓一跳', 7, true, 1.1], '惊呆举爪': ['吓一跳', 7, true, 1.1],
  '趴地冲刺': ['跑步', 12, false, .9], '冲刺扬尘': ['跑步', 12, false, .9], '哭着狂奔': ['跑步', 12, false, .9],
  '炸毛生气': ['摆爪否定', 6, false, 1], '斜眼嫌弃': ['摆爪否定', 6, false, 1], '无语': ['摆爪否定', 6, false, 1],
  '叉腰自信': ['叉腰得意', 6, false, 1], '坏笑得意': ['叉腰得意', 6, false, 1],
  '灵光一闪': ['点头指向', 4, true, 1],
  '累瘫灵魂出窍': ['累瘫', 5, true, .9],
  '戴头盔骑车': ['侧面骑车', 12, false, 1],
  '拍手叫好': ['拍手', 6, false, 1], '托腮思考': ['思考怀疑', 4, false, 1], '托腮疑问': ['思考怀疑', 4, false, 1], '仰望星星': ['抬头张望', 4, false, 1]
};

// 只播一遍、停在最后一帧的动作（其余循环播放）
var SEQ_ONCE = ['探头','笑开','摔跟头','转身跑出','戴头盔','摘头盔','搭帐篷','吓一跳','累瘫','点头指向','画饼图','下车推车','摔倒爬起','发现脚印','捡树叶','撑伞','背包出发','背包出发2'];

var ANIM = {}; Object.keys(ANIM_RAW).forEach(function (k) { if (typeof LICAI_SEQ === 'undefined' || seqUsable(ANIM_RAW[k][0])) ANIM[k] = ANIM_RAW[k]; });
