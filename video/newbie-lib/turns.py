"""转弯轨迹 → 关键帧（给 rig3d 的姿势参数用），第6课起的“落叶飘 / 换刃 / S弯 / 刻滑”都用它。
坐标：板头方向 yaw（度），yaw=0 板头朝 +x、人面朝下坡（+y）= 后刃横切；yaw=90 板头正对下坡（平板）；yaw=180 板头朝 -x、人面朝山上 = 前刃横切。
segs：("line", 米) 直线横切；("arc", 转角度数, 半径米) 转弯（转角 >0 往 yaw 变大的方向转）。"""
import math


def edge_for(yaw, emax=16.0, ramp=50.0):
    """离下坡线越远立刃越高；人面朝下坡（cos yaw > 0）用后刃（broll>0），面朝山上用前刃（broll<0）。"""
    cy = math.cos(math.radians(yaw))
    f = math.degrees(math.asin(min(1.0, abs(cy))))          # 板离下坡线的角度
    e = emax * min(1.0, f / ramp)
    return e if cy > 0 else -e


def path(segs, x0=0.0, y0=0.0, yaw0=0.0, v=2.0, t0=0.0, dt=0.2, emax=16.0, width=0.45, rise=0.0,
         twist_lead=25.0, base=None, edge_fn=None, skid=0.0, lean=0.0, switch=False):
    """沿 segs 匀速走，每 dt 秒一个关键帧。返回 (keys, 途经点 tw, 每段宽度 tws, 结束时刻, 每段起止时刻)。
    rise：起伏幅度（米），换刃（平板）时站高，弯中间压低。twist_lead：上身提前转向下一个弯的角度。"""
    keys, wp, tws, marks = [], [x0, y0], [], []
    x, y, yaw, t = x0, y0, yaw0, t0
    base = dict(base or {})
    n_wp = 0

    def pose(yaw_, turn_dir, prog=0.0):
        """prog：在这个弯里走了多少（0..1），用来算板尾外甩（skid，度）和身体往弯里倒（lean，度）。"""
        b = (edge_fn or edge_for)(yaw_ + (180.0 if switch else 0.0), emax)
        heel = b > 0
        k = math.sin(math.pi * prog) if turn_dir else 0.0
        sk = skid * k * turn_dir
        d = dict(gx=x, gy=y, yaw=yaw_ + sk + (180.0 if switch else 0.0), broll=b, tilt=(10 if heel else -12) * min(1, abs(b) / 6 + 0.2))
        if lean:
            kk = min(1.0, abs(b) / max(1.0, emax))
            d["tilt"] = (1 if heel else -1) * (4 + lean * kk)
            d["py"] = (-0.18 if heel else 0.18) * lean / 30 * kk
        far = min(1.0, abs(90 - yaw_) / 90)                 # 1 = 横着，0 = 平板
        d["pz"] = base.get("pz", 0.80) + rise * (1 - far) - rise * 0.5 * far - (0.18 * lean / 30 * min(1.0, abs(b) / max(1.0, emax)) if lean else 0.0)
        if turn_dir:
            d["twist"] = twist_lead * turn_dir * (1 if heel else -1) * 0.6
            d["face"] = d["twist"] * 1.2
        else:
            d["twist"] = 0.0; d["face"] = 0.0
        if switch:                                          # 反脚：看向板尾（行进方向）
            d["face"] = d["face"] - 60.0; d["twist"] = d["twist"] - 15.0
        return d

    for si, seg in enumerate(segs):
        ts = t
        if seg[0] == "line":
            L = seg[1]; n = max(1, int(round(L / v / dt)))
            for i in range(1, n + 1):
                x += math.cos(math.radians(yaw)) * L / n
                y += math.sin(math.radians(yaw)) * L / n
                t += L / v / n
                d = pose(yaw, 0)
                keys.append((t, d)); wp += [x, y]; tws.append(seg[2] if len(seg) > 2 else width)
        else:
            dphi, R = seg[1], seg[2]
            arc = abs(math.radians(dphi)) * R
            n = max(2, int(round(arc / v / dt)))
            for i in range(1, n + 1):
                step = dphi / n
                ym = yaw + step / 2
                ds = arc / n
                x += math.cos(math.radians(ym)) * ds
                y += math.sin(math.radians(ym)) * ds
                yaw += step; t += ds / v
                d = pose(yaw, 1 if dphi > 0 else -1, i / n)
                keys.append((t, d)); wp += [x, y]; tws.append(seg[3] if len(seg) > 3 else width)
        marks.append((ts, t))
    # tn：第 i 个关键帧时已经走过 i 个途经点（雪痕一段段画到当前位置）
    out = []
    for i, (tk, d) in enumerate(keys):
        d["tn"] = i
        out.append((tk, d))
    return out, tuple(wp), tuple(tws), t, marks


def fall(t0, kind="back", **at):
    """摔倒（后坐 / 前扑），接在任意关键帧后面。at：摔的位置（gx, gy, yaw 等，保持不变的就不写）。"""
    if kind == "back":
        return [(t0 + 0.4, dict(at, tilt=45, pz=0.45, py=-0.30, arm=-40, ab=25, elb=10)),
                (t0 + 0.9, dict(tilt=72, pz=0.18, py=-0.50, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))),
                (t0 + 1.4, dict())]
    return [(t0 + 0.4, dict(at, tilt=-60, pz=0.52, py=0.40, arm=80, elb=10, knee=(0.0, 1.0, -0.3))),
            (t0 + 0.9, dict(pz=0.32, py=0.80, tilt=-80, bz=0.12, arm=80, elb=60, neck=-30, knee=(0.0, 0.3, -1.0))),
            (t0 + 1.4, dict())]
