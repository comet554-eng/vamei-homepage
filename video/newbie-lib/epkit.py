"""第6课起的通用结构：开头（实拍两段）→ 要领（演示，按字幕对齐）→ 原理（演示或原理镜头）→ 三个错误 → 练习（演示 → 实拍过关）→ 下一课（实拍）。
每集 ep.py 只需要写：SECTIONS、FOOT、PERF/SHOT_PERF/cam，再加
  KEYS = (镜头, [每句字幕开始时的表演时间..., 段尾表演时间])
  WHY  = [(镜头, 起, 止), ...]       每句字幕一段（少于字幕数时最后一段一直用到段尾）；镜头写 "F:名字" 表示用实拍
  MIST = [(镜头, 起, 止), ...]       三个错误
  DRILL = (镜头, 起, 止)
然后 plan = std_plan(globals())；music_hits = std_hits(globals())。"""
from epbase import pw


def _q(p, n=30):
    return round(p * n) / n


def std_plan(E):
    def plan():
        SEC, DUR, FPS = E["SEC"], E["DUR"], E.get("FPS", 30)
        out = []
        h0, h1, hs = SEC["hook"]; k0, k1, ks = SEC["keys"]; w0, w1, ws = SEC["why"]
        m0, m1, ms = SEC["mistakes"]; d0, d1, ds = SEC["drill"]; e0, e1, _ = SEC["end"]
        kshot, kp = E["KEYS"]
        for i in range(int(round(DUR * FPS))):
            t = i / FPS
            if t < h1:
                cut = hs[1][1] - 0.1 if len(hs) > 1 else h1
                out.append(("F", "hook0", t) if t < cut else ("F", "hook1", t - cut))
            elif t < k1:
                anchors = [(0.0, kp[0])] + [(s[1] - k0 + 0.2, kp[j]) for j, s in enumerate(ks)] + [(k1 - k0, kp[-1])]
                anchors = sorted(anchors)
                out.append(("R", kshot, _q(pw(anchors, t - k0))))
            elif t < w1:
                j = max([j for j, s in enumerate(ws) if t >= s[1] - 0.15] or [0])
                j = min(j, len(E["WHY"]) - 1)
                shot, a, b = E["WHY"][j]
                s0 = ws[j][1] - 0.15 if j > 0 else w0
                s1 = ws[j + 1][1] - 0.15 if j + 1 < len(E["WHY"]) and j + 1 < len(ws) else w1
                if shot.startswith("F:"):
                    out.append(("F", shot[2:], t - s0))
                else:
                    out.append(("R", shot, _q(pw([(s0, a), (s1, b)], t))))
            elif t < m1:
                j = max([j for j, s in enumerate(ms) if t >= s[1] - 0.15] or [0])
                shot, a, b = E["MIST"][j]
                s0 = ms[j][1] - 0.15 if j > 0 else m0
                s1 = ms[j + 1][1] - 0.15 if j + 1 < len(ms) else m1
                out.append(("R", shot, _q(pw([(s0 + 0.2, a), (s1 - 0.2, b)], t))))
            elif t < d1:
                cut = ds[1][1] - 0.1 if len(ds) > 1 else d1
                if t < cut:
                    shot, a, b = E["DRILL"]
                    out.append(("R", shot, _q(pw([(d0, a), (cut, b)], t))))
                else:
                    out.append(("F", "pass", t - cut))
            else:
                out.append(("F", "end", t - e0))
        return out
    return plan


def std_hits(E):
    def music_hits():
        SEC = E["SEC"]
        hits = [SEC[k][2][0][1] for k in ("keys", "why", "mistakes", "drill", "end")]
        sfx = [(SEC["hook"][2][-1][1] + 0.1, "boom")]
        sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
        sfx += [(s[1] + 0.6, "ding") for s in SEC["why"][2][1:]]
        sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
        return hits, sfx
    return music_hits


def std_overlay(E):
    """通用标注：
    STAMP = (开头印章文字)；CHIPS = [四个要领短名]；
    KEY_TAGS = [(标签文字, 颜色名, 图标 None|"v"|"x", [要画圈的关节名...]), ...]（每句要领一个）
    WHY_DRAW(c, t, K)：原理段自己画（图表等）
    MIST_LABS = [三个错误短名]；MIST_RINGS = [关节名, ...]
    DRILL_TAGS = (第一个, 第二个)；PASS_TAGS = (过关条件1, 过关条件2)；NEXT = 下一课名"""
    def overlay(c, t, fr, pts, K):
        from vert import W, GOLD, ICE, RED, GREEN, window, ramp, tag, ring, chips
        col = dict(GOLD=GOLD, ICE=ICE, RED=RED, GREEN=GREEN)
        SEC = E["SEC"]
        K.hook_title(c, t, E["NAME"], E.get("STAMP"), GOLD)
        k0, k1, ks = SEC["keys"]
        if k0 - 0.2 < t < k1 + 0.2:
            cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
            chips(c, [f"{'①②③④'[j]}{n}" for j, n in enumerate(E["CHIPS"])], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
            for j, (txt, cn, icon, rings) in enumerate(E["KEY_TAGS"]):
                a = window(t, *K.sec_window("keys", j), 0.3)
                if a <= 0:
                    continue
                tag(c, txt, col[cn], 120, 1340, a, 38, icon)
                if pts:
                    for q in rings:
                        if q in pts:
                            ring(c, *pts[q], 46, col[cn], a, t)
        w0, w1, ws = SEC["why"]
        if w0 - 0.2 < t < w1 + 0.2 and "WHY_DRAW" in E:
            E["WHY_DRAW"](c, t, K, pts)
        m0, m1, ms = SEC["mistakes"]
        if m0 - 0.2 < t < m1 + 0.2:
            for j in range(len(ms)):
                a = window(t, *K.sec_window("mistakes", j), 0.25)
                if a > 0:
                    tag(c, f"错误{j + 1}：{E['MIST_LABS'][j]}", RED, 60, 330, a, 44, "x")
                    q = E["MIST_RINGS"][j]
                    if pts and q in pts:
                        ring(c, *pts[q], 60, RED, a, t)
        d0, d1, ds = SEC["drill"]
        if d0 - 0.2 < t < d1 + 0.2:
            if t < ds[1][1]:
                a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
                tag(c, E["DRILL_TAGS"][0], GOLD, 110, 1340, a, 40)
                tag(c, E["DRILL_TAGS"][1], GREEN, 110, 1410, a * ramp(t, d0 + 1.6, d0 + 1.9), 40)
            else:
                K.stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
                a = window(t, ds[1][1] + 0.3, d1, 0.3)
                for j, s in enumerate(E["PASS_TAGS"]):
                    tag(c, s, GREEN, 90, 1120 + j * 76, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
        K.end_card(c, t, E["NEXT"], E.get("END_HEAD", "下一课"))
    return overlay
