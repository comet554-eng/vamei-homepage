"""每集 ep.py 共用的东西：字幕按阅读速度排时间、分段线性时间映射、帧的缓存键。不依赖 bpy/cairo。"""


def plain(s):
    for m in ("{b|", "{w|", "{r|", "{g|", "}", "\n"):
        s = s.replace(m, "")
    return s


def seq(items, t0=0.3, gap=0.3, cps=4.4):
    out, t = [], t0
    for it in items:
        s, md = (it, 0) if isinstance(it, str) else it
        d = max(md, len(plain(s)) / cps + 0.25 * (s.count("，") + s.count("、")) + 0.6, 2.4)
        out.append((s, t, t + d)); t += d + gap
    return out


def timeline(sections):
    """sections: [(名字, 开头留白, 字幕, 结尾留白)] -> SUBS, SEC{name: (t0, t1, subs)}, DUR"""
    subs, sec, t = [], {}, 0.0
    for name, lead, items, tail in sections:
        S = seq(items, t0=t + lead)
        end = S[-1][2] + tail
        sec[name] = (t, end, S)
        subs += S; t = end
    return subs, sec, t


def pw(anchors, t):
    """分段线性：anchors [(out_t, perf_t)]"""
    if t <= anchors[0][0]:
        return anchors[0][1]
    for (a0, p0), (a1, p1) in zip(anchors, anchors[1:]):
        if t <= a1:
            return p0 + (p1 - p0) * (t - a0) / max(1e-6, a1 - a0)
    return anchors[-1][1]


def key(shot, p):
    return f"{shot}_{int(round(p * 60)):04d}"


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
