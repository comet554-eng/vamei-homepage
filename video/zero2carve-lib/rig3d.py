"""《单板从0到刻滑》3D 角色与场景（Blender bpy，代码建模）。
坐标：板长轴 = x（板头 +x），人面朝 +y（前刃一侧），z 向上；后摔倒向 -y，前摔倒向 +y。
姿势 = 一组参数（见 POSE0），关键帧之间平滑插值；腿用两段 IK 接到固定器上，手臂用 FK。"""
import math, os
import bpy, bmesh
from mathutils import Vector, Matrix

# ------------------------------------------------------------------ pose
POSE0 = dict(
    gx=0.0, gy=0.0,                             # 整体沿 x / y 的位移（推坡时沿 y 往下坡走）
    trail=0.0, ty0=0.0,                         # 雪痕：1 时显示，从 y=ty0 拉到板当前位置（宽 = 板长）
    tw=(), tn=0.0,                              # 多段雪痕：途经点 (x0,y0,x1,y1,...)，已走过 tn 个点，再连到板当前位置
    bx=0.0, by=0.0, bz=0.0, broll=0.0,          # 板中心、绕 x 轴横滚（>0 前刃抬起/后刃压雪）
    px=0.0, py=-0.02, pz=0.86, tilt=0.0,        # 骨盆中心；躯干后仰角（>0 往后倒，<0 往前扑）
    curl=0.0, neck=0.0,                         # 上背前弯（团身）、低头收下巴
    arm=12.0, ab=22.0, elb=20.0, fin=0.0,       # 手臂前举角（<0 往后伸）、外展、屈肘、小臂向内收
    knee=(0.0, 1.0, 0.25),                      # 膝盖朝向提示（世界方向）
    face=0.0,                                   # 头侧转（度），前摔时把脸让开
    twist=0.0,                                  # 上半身绕竖轴扭转（度，>0 胸口转向板头 +x）
    lfw=0.0, lfx=-0.26, lfy=0.0, lfz=0.13,      # 后脚（L）离开固定器的程度和位置（相对 gx 的世界坐标）
    yaw=0.0, yx=0.0, yy=0.0,                    # 整个人和板绕竖轴转（度），转轴在 (gx+yx, yy)
    slope=0.0,                                  # 雪坡角（度，>0 时 +y 方向是下坡）
)
THIGH, SHIN, UARM, FARM = 0.45, 0.44, 0.30, 0.28


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def interp(keys, t):
    """keys: [(t, dict)] 升序；未写的参数沿用上一帧。返回完整姿势。"""
    full, cur = [], dict(POSE0)
    for kt, d in keys:
        cur = dict(cur); cur.update(d); full.append((kt, cur))
    if t <= full[0][0]:
        return dict(full[0][1])
    for (t0, a), (t1, b) in zip(full, full[1:]):
        if t <= t1:
            k = ease((t - t0) / (t1 - t0))
            out = {}
            for n in a:
                if isinstance(a[n], tuple):
                    out[n] = tuple(x + (y - x) * k for x, y in zip(a[n], b[n]))
                else:
                    out[n] = a[n] + (b[n] - a[n]) * k
            return out
    return dict(full[-1][1])


def ik2(root, end, a, b, hint):
    d = end - root
    L = max(1e-4, min(d.length, a + b - 1e-3))
    dn = d.normalized()
    x = (a * a - b * b + L * L) / (2 * L)
    h = math.sqrt(max(0.0, a * a - x * x))
    p = Vector(hint) - dn * Vector(hint).dot(dn)
    p = p.normalized() if p.length > 1e-6 else Vector((0, 0, 1))
    return root + dn * x + p * h


def skeleton(P):
    """姿势 -> 关节世界坐标。"""
    J = {}
    br = math.radians(P["broll"])
    Rb = Matrix.Rotation(br, 4, "X")
    B = Vector((P["bx"] + P["gx"], P["by"] + P["gy"], P["bz"]))
    J["board_m"] = Matrix.Translation(B) @ Rb
    up_b = (Rb @ Vector((0, 0, 1, 0))).xyz
    for side, fx in (("L", -0.26), ("R", 0.26)):
        J["ankle" + side] = B + (Rb @ Vector((fx, 0.0, 0.13, 0))).xyz
    free = Vector((P["lfx"] + P["gx"], P["lfy"] + P["gy"], P["lfz"]))
    J["ankleL"] = J["ankleL"].lerp(free, P["lfw"])
    J["bootL_m"] = Matrix.Translation(J["ankleL"] + (Rb @ Vector((0, 0.02, -0.04, 0))).xyz) @ Rb
    tl = math.radians(P["tilt"])
    Rt = Matrix.Rotation(math.radians(P["twist"]), 3, "Z")
    u = Vector((0, -math.sin(tl), math.cos(tl)))
    f = Rt @ Vector((0, math.cos(tl), math.sin(tl)))
    X = Rt @ Vector((1, 0, 0))
    pel = Vector((P["px"] + P["gx"], P["py"] + P["gy"], P["pz"]))
    J["pelvis"] = pel
    chest = pel + u * 0.30
    cu = math.radians(P["curl"])
    u2 = u * math.cos(cu) + f * math.sin(cu); f2 = f * math.cos(cu) - u * math.sin(cu)
    nb = chest + u2 * 0.24
    J["chest"], J["neck"] = chest, nb
    nk = math.radians(P["neck"])
    u3 = u2 * math.cos(nk) + f2 * math.sin(nk); f3 = f2 * math.cos(nk) - u2 * math.sin(nk)
    fa = math.radians(P["face"])
    f3r = f3 * math.cos(fa) + X * math.sin(fa)
    J["head"] = nb + u3 * 0.16
    J["head_m"] = Matrix((f3r.cross(u3), f3r, u3)).transposed().to_4x4()
    J["head_m"].translation = J["head"]
    for side, sx in (("L", -1), ("R", 1)):
        hip = pel + X * (0.12 * sx) - u * 0.02
        J["hip" + side] = hip
        J["knee" + side] = ik2(hip, J["ankle" + side], THIGH, SHIN, P["knee"])
        sh = nb - u2 * 0.05 + X * (0.19 * sx)
        J["sho" + side] = sh
        pa, ab = math.radians(P["arm"]), math.radians(P["ab"])
        dn = -u2
        d1 = (dn * math.cos(pa) + f2 * math.sin(pa)) * math.cos(ab) + X * (sx * math.sin(ab))
        d1.normalize()
        el = sh + d1 * UARM
        J["elb" + side] = el
        perp = f2 - d1 * f2.dot(d1)
        if perp.length < 1e-3:
            perp = u2 - d1 * u2.dot(d1)
        perp.normalize()
        fi = math.radians(P["fin"])
        perp = (perp * math.cos(fi) - X * (sx * math.sin(fi))).normalized()
        e = math.radians(P["elb"])
        d2 = (d1 * math.cos(e) + perp * math.sin(e)).normalized()
        J["hand" + side] = el + d2 * FARM
    # 整体转向（绕竖轴）+ 雪坡倾斜
    pv = Vector((P["gx"] + P["yx"], P["yy"] + P["gy"], 0))
    T = (Matrix.Rotation(math.radians(-P["slope"]), 4, "X") @ Matrix.Translation(pv)
         @ Matrix.Rotation(math.radians(P["yaw"]), 4, "Z") @ Matrix.Translation(-pv))
    for k in list(J):
        J[k] = (T @ J[k]) if isinstance(J[k], Matrix) else (T @ J[k])
    J["slope_m"] = Matrix.Rotation(math.radians(-P["slope"]), 4, "X")
    J["trails"] = []
    if P["trail"] > 0.5:
        cur = (P["gx"] + P["bx"], P["gy"] + P["by"])
        if P["tw"]:
            wp = [(P["tw"][i], P["tw"][i + 1]) for i in range(0, len(P["tw"]), 2)][:int(P["tn"] + 1e-6) + 1]
        else:
            wp = [(cur[0], P["ty0"])]
        pts = wp + [cur]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy)
            if L < 0.02:
                continue
            ang = math.atan2(dy, dx)
            wid = 1.45 * abs(math.sin(ang)) + 0.30 * abs(math.cos(ang))   # 板大致沿 x：横着推宽，顺着走窄
            J["trails"].append(J["slope_m"] @ Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, 0.004 + 0.001 * len(J["trails"])))
                               @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((L + 0.25, wid, 1, 1)))
    return J


# ------------------------------------------------------------------ scene
def mat(name, col, rough=0.5, emit=0.0, metallic=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if emit:
        p.inputs["Emission Color"].default_value = (*col, 1); p.inputs["Emission Strength"].default_value = emit
    return m


class Scene:
    def __init__(self, w=1080, h=1920, samples=10, transparent=False):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = self.sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 3
        sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1; sc.cycles.transmission_bounces = 0
        sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
        sc.render.use_persistent_data = True
        sc.render.resolution_x, sc.render.resolution_y = w, h
        sc.render.film_transparent = transparent
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "Medium High Contrast"
        world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
        nt = world.node_tree
        bg = nt.nodes["Background"]
        grad = nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type = "LINEAR"
        coord = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.035, 0.06, 0.13, 1)
        ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (0.006, 0.01, 0.025, 1)
        mapr = nt.nodes.new("ShaderNodeMapRange"); mapr.inputs["From Min"].default_value = -0.3; mapr.inputs["From Max"].default_value = 0.6
        nt.links.new(coord.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], mapr.inputs["Value"])
        nt.links.new(mapr.outputs["Result"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
        bg.inputs[1].default_value = 1.0

        self.M = dict(
            snow=mat("snow", (0.55, 0.64, 0.80), 0.7),
            board=mat("board", (0.20, 0.50, 0.92), 0.30, coat=0.6),
            boardtop=mat("boardtop", (0.93, 0.95, 0.98), 0.4),
            base=mat("base", (0.05, 0.06, 0.09), 0.3),
            binding=mat("binding", (0.07, 0.08, 0.10), 0.5),
            boot=mat("boot", (0.12, 0.13, 0.16), 0.6),
            jacket=mat("jacket", (0.95, 0.62, 0.20), 0.6),
            pants=mat("pants", (0.11, 0.16, 0.32), 0.7),
            glove=mat("glove", (0.08, 0.08, 0.10), 0.6),
            helmet=mat("helmet", (0.94, 0.95, 0.97), 0.25, coat=0.8),
            goggle=mat("goggle", (0.30, 0.65, 1.0), 0.05, emit=0.4, metallic=0.6),
            pole=mat("pole", (0.25, 0.55, 1.0), 0.4, emit=3.0),
            trail=mat("trail", (0.92, 0.95, 1.0), 0.9),
        )
        snow_m = self.M["snow"].node_tree
        noise = snow_m.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 6.0; noise.inputs["Detail"].default_value = 6
        bump = snow_m.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
        snow_m.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        snow_m.links.new(bump.outputs["Normal"], snow_m.nodes["Principled BSDF"].inputs["Normal"])

        if not transparent:
            bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
            self.ground = bpy.context.object
            self.ground.data.materials.append(self.M["snow"])
            # 两侧的发光标杆（给速度感和空间参照）
            for k in range(-30, 60):
                for y in (-3.2, 3.2):
                    bpy.ops.mesh.primitive_cube_add(size=1, location=(k * 2.5, y, 0.02))
                    o = bpy.context.object; o.scale = (0.7, 0.06, 0.02); o.data.materials.append(self.M["pole"])
                    o.parent = self.ground
        else:
            # 透明底封面：只要一块接影子的地
            bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
            g = bpy.context.object; g.data.materials.append(self.M["snow"]); g.is_shadow_catcher = True
            self.ground = g

        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(10), math.radians(150)))
        sun = bpy.context.object; sun.data.energy = 0.7; sun.data.color = (1.0, 0.90, 0.78); sun.data.angle = math.radians(4)
        bpy.ops.object.light_add(type="AREA", location=(4, 6, 5))
        fill = bpy.context.object; fill.data.energy = 120; fill.data.size = 6; fill.data.color = (0.6, 0.75, 1.0)
        fill.rotation_euler = (Vector((0, 0, 0.8)) - fill.location).to_track_quat("-Z", "Y").to_euler()
        self.fill = fill
        bpy.ops.object.light_add(type="SPOT", location=(1.5, 2.5, 6))
        sp = bpy.context.object; sp.data.energy = 1400; sp.data.spot_size = math.radians(55); sp.data.spot_blend = 0.6
        sp.data.color = (1.0, 0.95, 0.88); sp.data.shadow_soft_size = 0.4
        self.spot = sp

        tm = mat("scrape", (0.66, 0.74, 0.88), 0.95)
        tn = tm.node_tree; nz = tn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40.0
        bp = tn.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5
        tn.links.new(nz.outputs["Fac"], bp.inputs["Height"]); tn.links.new(bp.outputs["Normal"], tn.nodes["Principled BSDF"].inputs["Normal"])
        self.trails = []
        for _ in range(5):
            bpy.ops.mesh.primitive_plane_add(size=1.0)
            o = bpy.context.object; o.hide_render = True; o.data.materials.append(tm); self.trails.append(o)
        self._build_body()
        cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 35
        self.cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(self.cam); sc.camera = self.cam

    # ---------------------------------------------------------------- body parts
    def _seg(self, name, r, m):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=1.0, vertices=20, end_fill_type="NOTHING")
        o = bpy.context.object; o.name = name; o.data.materials.append(m)
        for p in o.data.polygons:
            p.use_smooth = True
        o.rotation_mode = "QUATERNION"
        return o

    def _ball(self, name, r, m, seg=20):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2)
        o = bpy.context.object; o.name = name; o.data.materials.append(m)
        for p in o.data.polygons:
            p.use_smooth = True
        return o

    def _board_mesh(self):
        L, waist, tip = 1.56, 0.25, 0.29
        bm = bmesh.new(); n = 60; half = L / 2; eff = 0.60; sag = (tip - waist) / 2
        outline = []
        for i in range(n + 1):
            x = half - L * i / n
            if abs(x) <= eff:
                y = waist / 2 + sag * (x / eff) ** 2
            else:
                u = (abs(x) - eff) / (half - eff)
                y = (tip / 2) * math.sqrt(max(0.0, 1 - u ** 2.2))
            outline.append((x, y))
        pts = outline + [(x, -y) for x, y in reversed(outline)]
        lift = lambda x: 0.06 * max(0, (abs(x) - eff) / (half - eff)) ** 2
        top = [bm.verts.new((x, y, 0.018 + lift(x))) for x, y in pts]
        bot = [bm.verts.new((x, y, lift(x))) for x, y in pts]
        bm.faces.new(top); bm.faces.new(list(reversed(bot)))
        k = len(pts)
        for i in range(k):
            bm.faces.new([top[i], top[(i + 1) % k], bot[(i + 1) % k], bot[i]])
        me = bpy.data.meshes.new("board"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new("board", me); self.sc.collection.objects.link(ob)
        for m in ("board", "base", "boardtop"):
            ob.data.materials.append(self.M[m])
        for p in ob.data.polygons:
            c = p.center
            p.material_index = 1 if p.normal.z < -0.5 else (2 if p.normal.z > 0.5 and abs(c.x) < 0.45 and False else 0)
        ob.rotation_mode = "QUATERNION"
        return ob

    def _build_body(self):
        M = self.M
        self.board = self._board_mesh()
        self.parts = {}
        # 固定器 + 鞋：挂在板上
        for side, fx in (("L", -0.26), ("R", 0.26)):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, 0.0, 0.035)); b = bpy.context.object
            b.scale = (0.13, 0.27, 0.04); b.data.materials.append(M["binding"]); b.parent = self.board
            bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, 0.02, 0.09)); bt = bpy.context.object
            bt.scale = (0.12, 0.30, 0.10); bt.data.materials.append(M["boot"])
            if side == "R":
                bt.parent = self.board
            else:
                bt.location = (0, 0, 0); bt.rotation_mode = "QUATERNION"; self.bootL = bt
            m = bt.modifiers.new("bev", "BEVEL"); m.width = 0.03; m.segments = 3
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.10, 0.0, 0.022)); pad = bpy.context.object
        pad.scale = (0.14, 0.17, 0.008); pad.data.materials.append(M["binding"]); pad.parent = self.board
        P = self.parts
        for side in "LR":
            P["shin" + side] = self._seg("shin" + side, 0.062, M["pants"])
            P["thigh" + side] = self._seg("thigh" + side, 0.078, M["pants"])
            P["knee" + side] = self._ball("kneeB" + side, 0.066, M["pants"])
            P["hip" + side] = self._ball("hipB" + side, 0.08, M["pants"])
            P["ank" + side] = self._ball("ankB" + side, 0.062, M["pants"])
            P["uarm" + side] = self._seg("uarm" + side, 0.055, M["jacket"])
            P["farm" + side] = self._seg("farm" + side, 0.05, M["jacket"])
            P["sho" + side] = self._ball("shoB" + side, 0.07, M["jacket"])
            P["elb" + side] = self._ball("elbB" + side, 0.052, M["jacket"])
            P["hand" + side] = self._ball("hand" + side, 0.058, M["glove"])
        P["torso"] = self._seg("torso", 0.155, M["jacket"])
        P["pelv"] = self._ball("pelv", 0.152, M["pants"])
        P["chestB"] = self._ball("chestB", 0.155, M["jacket"])
        P["upper"] = self._seg("upper", 0.155, M["jacket"])
        P["neckS"] = self._seg("neckS", 0.055, M["binding"])
        # 头：头盔 + 雪镜（挂在一个空物体上）
        hd = bpy.data.objects.new("headE", None); self.sc.collection.objects.link(hd); hd.rotation_mode = "QUATERNION"
        self.head = hd
        h = self._ball("helmet", 0.135, M["helmet"], 28); h.parent = hd; h.location = (0, -0.01, 0.015); h.scale = (0.95, 1.05, 1.0)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.11, 0.0)); g = bpy.context.object
        g.scale = (0.2, 0.07, 0.075); g.data.materials.append(M["goggle"]); g.parent = hd
        m = g.modifiers.new("bev", "BEVEL"); m.width = 0.03; m.segments = 4
        bpy.ops.mesh.primitive_torus_add(major_radius=0.128, minor_radius=0.014, location=(0, 0, 0.0)); s = bpy.context.object
        s.data.materials.append(M["binding"]); s.parent = hd; s.scale = (1.0, 1.05, 1.0)
        self.extra = []

    def place(self, P):
        """把姿势写入场景，返回关节坐标。"""
        J = skeleton(P)
        bm = J["board_m"]
        self.board.location = bm.translation; self.board.rotation_quaternion = bm.to_quaternion()
        lb = J["bootL_m"]
        self.bootL.location = lb.translation; self.bootL.rotation_quaternion = lb.to_quaternion()
        sm = J["slope_m"]
        self.ground.rotation_mode = "QUATERNION"; self.ground.rotation_quaternion = sm.to_quaternion()
        for i, o in enumerate(self.trails):
            if i < len(J["trails"]):
                o.hide_render = False; o.matrix_world = J["trails"][i]
            else:
                o.hide_render = True
        pr = self.parts

        def seg(o, a, b, shrink=0.0):
            d = b - a
            o.location = (a + b) / 2
            o.rotation_quaternion = d.to_track_quat("Z", "Y")
            o.scale = (1, 1, max(0.01, d.length - shrink))

        for s in "LR":
            seg(pr["shin" + s], J["ankle" + s], J["knee" + s])
            seg(pr["thigh" + s], J["knee" + s], J["hip" + s])
            pr["knee" + s].location = J["knee" + s]; pr["hip" + s].location = J["hip" + s]; pr["ank" + s].location = J["ankle" + s]
            seg(pr["uarm" + s], J["sho" + s], J["elb" + s])
            seg(pr["farm" + s], J["elb" + s], J["hand" + s])
            pr["sho" + s].location = J["sho" + s]; pr["elb" + s].location = J["elb" + s]; pr["hand" + s].location = J["hand" + s]
        seg(pr["torso"], J["pelvis"], J["chest"])
        seg(pr["upper"], J["chest"], J["neck"] - (J["neck"] - J["chest"]).normalized() * 0.06)
        pr["pelv"].location = J["pelvis"]; pr["chestB"].location = J["chest"]
        seg(pr["neckS"], J["neck"], J["head"])
        tgt = J["pelvis"]
        self.spot.location = tgt + Vector((1.2, 2.0, 5.5))
        self.spot.rotation_mode = "QUATERNION"; self.spot.rotation_quaternion = (tgt - self.spot.location).to_track_quat("-Z", "Y")
        hm = J["head_m"]
        self.head.location = hm.translation; self.head.rotation_quaternion = hm.to_quaternion()
        return J

    def camera(self, pos, target, lens=35):
        self.cam.location = Vector(pos)
        self.cam.data.lens = lens
        d = Vector(target) - self.cam.location
        self.cam.rotation_mode = "QUATERNION"; self.cam.rotation_quaternion = d.to_track_quat("-Z", "Y")

    def project(self, pts):
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        out = {}
        for k, p in pts.items():
            v = world_to_camera_view(self.sc, self.cam, Vector(p))
            out[k] = (v.x, 1 - v.y, v.z)
        return out

    def render(self, path):
        self.sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
