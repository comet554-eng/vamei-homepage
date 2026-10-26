"""《单板从0到刻滑》3D 第二版画风：白天雪山场景 + 一体成型的人物（Skin 修改器 + 细分）+ 带高背和绑带的固定器。
骨架和姿势沿用 rig3d.skeleton()，接口和 rig3d.Scene 一样（place / camera / project / render），可以直接替换。"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from rig3d import POSE0, interp, skeleton, ease, mat


def _smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def _bevel(o, w, seg=3):
    m = o.modifiers.new("bev", "BEVEL"); m.width = w; m.segments = seg; m.limit_method = "ANGLE"
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
        sc.view_settings.view_transform = "Filmic"
        sc.view_settings.look = "Medium High Contrast"
        sc.view_settings.exposure = -0.4

        # 天空：物理天空（白天、太阳偏低一点，雪面有长一点的影子）
        world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
        nt = world.node_tree; bg = nt.nodes["Background"]
        sky = nt.nodes.new("ShaderNodeTexSky")
        try:
            sky.sky_type = "NISHITA"
            sky.sun_elevation = math.radians(28); sky.sun_rotation = math.radians(140)
            sky.altitude = 2000; sky.air_density = 1.2; sky.dust_density = 0.6
        except Exception:
            pass
        nt.links.new(sky.outputs["Color"], bg.inputs["Color"]); bg.inputs[1].default_value = 0.16

        M = self.M = dict(
            snow=mat("snow", (0.80, 0.86, 0.96), 0.55),
            mount=mat("mount", (0.80, 0.86, 0.95), 0.8),
            rock=mat("rock", (0.30, 0.34, 0.42), 0.9),
            tree=mat("tree", (0.10, 0.22, 0.20), 0.9),
            board=mat("board", (0.10, 0.45, 0.85), 0.25, coat=0.8),
            boardtop=mat("boardtop", (0.95, 0.96, 0.98), 0.35, coat=0.6),
            edge=mat("edge", (0.55, 0.58, 0.62), 0.25, metallic=0.9),
            base=mat("base", (0.04, 0.05, 0.07), 0.3),
            binding=mat("binding", (0.10, 0.11, 0.13), 0.45),
            strap=mat("strap", (0.95, 0.62, 0.20), 0.5),
            boot=mat("boot", (0.06, 0.065, 0.08), 0.55),
            sole=mat("sole", (0.05, 0.05, 0.06), 0.8),
            jacket=mat("jacket", (0.80, 0.16, 0.02), 0.55),
            pants=mat("pants", (0.04, 0.06, 0.14), 0.75),
            glove=mat("glove", (0.07, 0.07, 0.09), 0.5),
            helmet=mat("helmet", (0.95, 0.96, 0.98), 0.2, coat=1.0),
            goggle=mat("goggle", (0.35, 0.70, 1.0), 0.02, metallic=0.8, coat=1.0),
            frame=mat("frame", (0.08, 0.09, 0.11), 0.4),
            skin=mat("skin", (0.86, 0.66, 0.54), 0.6),
            pole=mat("pole", (0.95, 0.35, 0.25), 0.5),
        )
        sn = M["snow"].node_tree
        noise = sn.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 3.0; noise.inputs["Detail"].default_value = 8
        bump = sn.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
        sn.links.new(noise.outputs["Fac"], bump.inputs["Height"]); sn.links.new(bump.outputs["Normal"], sn.nodes["Principled BSDF"].inputs["Normal"])
        sn.nodes["Principled BSDF"].inputs["Subsurface Weight"].default_value = 0.15

        if not transparent:
            bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0))
            self.ground = bpy.context.object; self.ground.data.materials.append(M["snow"])
            self._scenery()
        else:
            bpy.ops.mesh.primitive_plane_add(size=40)
            g = bpy.context.object; g.data.materials.append(M["snow"]); g.is_shadow_catcher = True
            self.ground = g

        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(62), 0, math.radians(140)))
        sun = bpy.context.object; sun.data.energy = 2.6; sun.data.color = (1.0, 0.98, 0.95); sun.data.angle = math.radians(1.5)
        self.spot = None

        tm = mat("scrape", (0.84, 0.89, 0.98), 0.95)
        tn = tm.node_tree; nz = tn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30.0
        bp = tn.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6
        tn.links.new(nz.outputs["Fac"], bp.inputs["Height"]); tn.links.new(bp.outputs["Normal"], tn.nodes["Principled BSDF"].inputs["Normal"])
        self.trails = []
        for _ in range(5):
            bpy.ops.mesh.primitive_plane_add(size=1.0)
            o = bpy.context.object; o.hide_render = True; o.data.materials.append(tm); self.trails.append(o)
        self._build_body()
        cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 35
        self.cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(self.cam); sc.camera = self.cam

    # ---------------------------------------------------------------- 远山和树（都挂在地面上，跟着坡一起转）
    def _scenery(self):
        rnd = random.Random(7)
        M = self.M
        # 远山：几座大锥体，噪声位移出山脊
        tex = bpy.data.textures.new("mtn", "CLOUDS"); tex.noise_scale = 0.9
        for i in range(9):
            ang = math.radians(-70 + i * 18 + rnd.uniform(-6, 6))
            d = rnd.uniform(70, 110)
            x, y = d * math.sin(ang), -d * math.cos(ang)
            r = rnd.uniform(26, 42); hgt = rnd.uniform(22, 38)
            bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r, depth=hgt, location=(x, y, hgt / 2 - 3))
            o = bpy.context.object
            sb = o.modifiers.new("sub", "SUBSURF"); sb.levels = 1; sb.render_levels = 1
            dm = o.modifiers.new("disp", "DISPLACE"); dm.texture = tex; dm.strength = 6
            o.data.materials.append(M["mount"]); _smooth(o); o.parent = self.ground
        # 雪道两边的树（低多边形松树，用实例）
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=1.0, depth=2.2, location=(0, 0, 1.6))
        t1 = bpy.context.object
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.75, depth=1.8, location=(0, 0, 2.6))
        t2 = bpy.context.object
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=0.8, location=(0, 0, 0.4))
        t3 = bpy.context.object
        for o in (t1, t2):
            o.data.materials.append(M["tree"])
        t3.data.materials.append(M["rock"])
        bpy.ops.object.select_all(action="DESELECT")
        for o in (t1, t2, t3):
            o.select_set(True)
        bpy.context.view_layer.objects.active = t1; bpy.ops.object.join()
        tree = bpy.context.object; tree.hide_render = True; tree.hide_viewport = True
        for k in range(160):
            side = -1 if k % 2 else 1
            x = rnd.uniform(-60, 60); y = side * rnd.uniform(9, 30)
            if abs(y) < 9:
                continue
            inst = bpy.data.objects.new(f"tree{k}", tree.data); self.sc.collection.objects.link(inst)
            s = rnd.uniform(0.8, 1.6); inst.scale = (s, s, s * rnd.uniform(0.9, 1.3)); inst.location = (x, y, 0)
            inst.parent = self.ground
        # 雪道边的小旗杆（给近处的空间感）
        for k in range(-20, 40):
            for y in (-6.5, 6.5):
                bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=1.2, location=(k * 4.0, y, 0.6))
                o = bpy.context.object; o.data.materials.append(M["pole"]); o.parent = self.ground

    # ---------------------------------------------------------------- 人
    def _skin_mesh(self, name, nverts, edges, radii, m):
        me = bpy.data.meshes.new(name)
        me.from_pydata([(0, 0, 0.1 * i) for i in range(nverts)], edges, [])
        o = bpy.data.objects.new(name, me); self.sc.collection.objects.link(o)
        bpy.context.view_layer.objects.active = o
        sk = o.modifiers.new("skin", "SKIN"); sk.use_smooth_shade = True; sk.branch_smoothing = 0.6
        sv = me.skin_vertices[0].data
        for i, r in enumerate(radii):
            sv[i].radius = r if isinstance(r, tuple) else (r, r)
        sv[0].use_root = True
        sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
        o.data.materials.append(m)
        return o

    def _build_board(self):
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
        lift = lambda x: 0.07 * max(0, (abs(x) - eff) / (half - eff)) ** 2
        top = [bm.verts.new((x, y, 0.016 + lift(x))) for x, y in pts]
        mid = [bm.verts.new((x, y, 0.004 + lift(x))) for x, y in pts]
        bot = [bm.verts.new((x, y, lift(x))) for x, y in pts]
        ft = bm.faces.new(top); bm.faces.new(list(reversed(bot)))
        k = len(pts)
        for i in range(k):
            f1 = bm.faces.new([top[i], top[(i + 1) % k], mid[(i + 1) % k], mid[i]]); f1.material_index = 0
            f2 = bm.faces.new([mid[i], mid[(i + 1) % k], bot[(i + 1) % k], bot[i]]); f2.material_index = 2
        me = bpy.data.meshes.new("board"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new("board", me); self.sc.collection.objects.link(ob)
        for mname in ("board", "base", "edge"):
            ob.data.materials.append(self.M[mname])
        for p in ob.data.polygons:
            if p.normal.z < -0.5:
                p.material_index = 1
        # 板面图案：一条白色宽带 + 一条橙色细带（贴在板面上的薄片）
        for x0, wdt, mm in ((-0.05, 0.22, "boardtop"), (0.18, 0.05, "strap")):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(x0, 0, 0.0172))
            s = bpy.context.object; s.scale = (wdt, 0.25, 1); s.data.materials.append(self.M[mm]); s.parent = ob
        ob.rotation_mode = "QUATERNION"
        return ob

    def _binding(self, fx):
        """固定器：底板 + 高背 + 两条绑带。挂在板上。"""
        M = self.M
        bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, 0.0, 0.026)); b = bpy.context.object
        b.scale = (0.13, 0.27, 0.02); b.data.materials.append(M["binding"]); _bevel(b, 0.008); b.parent = self.board
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.075, depth=0.26, location=(fx, -0.11, 0.17))
        hb = bpy.context.object; hb.scale = (1.0, 0.45, 1.0); hb.rotation_euler = (math.radians(-12), 0, 0)
        hb.data.materials.append(M["binding"]); hb.parent = self.board; _smooth(hb)
        for y, z, ang in ((0.13, 0.115, 25), (0.0, 0.205, -35)):      # 脚尖绑带、脚踝绑带
            bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, y, z))
            st = bpy.context.object; st.scale = (0.15, 0.06, 0.03); st.rotation_euler = (math.radians(ang), 0, 0)
            _bevel(st, 0.012); st.data.materials.append(M["strap"]); st.parent = self.board
        return b

    def _boot(self, name):
        """雪鞋：圆头鞋身 + 高筒，原点在脚踝。"""
        M = self.M
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, -0.075)); f = bpy.context.object
        f.scale = (0.115, 0.30, 0.09); _bevel(f, 0.04, 4); f.data.materials.append(M["boot"])
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, -0.12)); s = bpy.context.object
        s.scale = (0.12, 0.31, 0.025); _bevel(s, 0.01); s.data.materials.append(M["sole"])
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.07, depth=0.20, location=(0, -0.01, 0.04)); c = bpy.context.object
        c.scale = (0.95, 1.1, 1.0); c.data.materials.append(M["boot"]); _smooth(c)
        e = bpy.data.objects.new(name, None); self.sc.collection.objects.link(e); e.rotation_mode = "QUATERNION"
        for o in (f, s, c):
            o.parent = e
        return e

    def _build_body(self):
        M = self.M
        self.board = self._build_board()
        for fx in (-0.26, 0.26):
            self._binding(fx)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.10, 0.0, 0.019)); pad = bpy.context.object
        pad.scale = (0.12, 0.15, 0.004); pad.data.materials.append(M["binding"]); pad.parent = self.board
        self.bootR = self._boot("bootR"); self.bootL = self._boot("bootL")
        # 裤子：髋-膝-踝两条腿 + 骨盆
        # 顶点：0 骨盆 1 左髋 2 左膝 3 左踝 4 右髋 5 右膝 6 右踝
        self.legs = self._skin_mesh("legs", 7, [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)],
                                    [0.12, 0.10, 0.078, 0.07, 0.10, 0.078, 0.07], M["pants"])
        # 上衣：骨盆-胸-颈，肩-肘-腕
        # 0 腰 1 胸 2 颈 3 左肩 4 左肘 5 左腕 6 右肩 7 右肘 8 右腕
        self.coat = self._skin_mesh("coat", 9, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (2, 6), (6, 7), (7, 8)],
                                    [0.165, 0.19, 0.085, 0.092, 0.078, 0.066, 0.092, 0.078, 0.066], M["jacket"])
        self.gloves = []
        for s in "LR":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, segments=20, ring_count=10); g = bpy.context.object
            g.scale = (0.9, 1.25, 0.8); g.data.materials.append(M["glove"]); _smooth(g); g.rotation_mode = "QUATERNION"
            self.gloves.append(g)
        # 头：下巴（皮肤）+ 头盔 + 雪镜（弧形）+ 镜框
        hd = bpy.data.objects.new("headE", None); self.sc.collection.objects.link(hd); hd.rotation_mode = "QUATERNION"; self.head = hd
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105, segments=28, ring_count=14, location=(0, 0.01, -0.03)); fc = bpy.context.object
        fc.data.materials.append(M["skin"]); _smooth(fc); fc.parent = hd
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.135, segments=32, ring_count=16, location=(0, -0.01, 0.025)); h = bpy.context.object
        h.scale = (0.95, 1.08, 0.92); h.data.materials.append(M["helmet"]); _smooth(h); h.parent = hd
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.122, depth=0.075, location=(0, 0.0, 0.0)); gg = bpy.context.object
        bm = bmesh.new(); bm.from_mesh(gg.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < 0.03], context="VERTS")
        bm.to_mesh(gg.data); bm.free()
        sol = gg.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.012
        gg.scale = (1.0, 1.04, 1.0); gg.location = (0, -0.005, 0.005); gg.data.materials.append(M["goggle"]); _smooth(gg); gg.parent = hd
        bpy.ops.mesh.primitive_torus_add(major_radius=0.128, minor_radius=0.01, location=(0, 0, 0.0)); s = bpy.context.object
        s.scale = (1.0, 1.06, 1.6); s.data.materials.append(M["frame"]); s.parent = hd

    def place(self, P):
        J = skeleton(P)
        bm = J["board_m"]
        self.board.location = bm.translation; self.board.rotation_quaternion = bm.to_quaternion()
        rot = bm.to_quaternion()
        self.bootR.location = J["ankleR"]; self.bootR.rotation_quaternion = rot
        self.bootL.location = J["ankleL"]; self.bootL.rotation_quaternion = J["bootL_m"].to_quaternion()
        sm = J["slope_m"]
        self.ground.rotation_mode = "QUATERNION"; self.ground.rotation_quaternion = sm.to_quaternion()
        for i, o in enumerate(self.trails):
            if i < len(J["trails"]):
                o.hide_render = False; o.matrix_world = J["trails"][i]
            else:
                o.hide_render = True
        up = (J["neck"] - J["pelvis"]).normalized()
        legs = [J["pelvis"] - up * 0.02, J["hipL"], J["kneeL"], J["ankleL"] + up * 0.05, J["hipR"], J["kneeR"], J["ankleR"] + up * 0.05]
        for i, v in enumerate(legs):
            self.legs.data.vertices[i].co = v
        coat = [J["pelvis"] + up * 0.04, J["chest"] + up * 0.04, J["neck"], J["shoL"], J["elbL"], J["handL"] - (J["handL"] - J["elbL"]).normalized() * 0.06,
                J["shoR"], J["elbR"], J["handR"] - (J["handR"] - J["elbR"]).normalized() * 0.06]
        for i, v in enumerate(coat):
            self.coat.data.vertices[i].co = v
        self.legs.data.update(); self.coat.data.update()
        for g, s in zip(self.gloves, "LR"):
            d = (J["hand" + s] - J["elb" + s]).normalized()
            g.location = J["hand" + s]; g.rotation_quaternion = d.to_track_quat("Y", "Z")
        hm = J["head_m"]
        self.head.location = hm.translation; self.head.rotation_quaternion = hm.to_quaternion()
        return J

    def camera(self, pos, target, lens=35, dof=None):
        self.cam.location = Vector(pos); self.cam.data.lens = lens
        d = Vector(target) - self.cam.location
        self.cam.rotation_mode = "QUATERNION"; self.cam.rotation_quaternion = d.to_track_quat("-Z", "Y")
        self.cam.data.dof.use_dof = dof is not None
        if dof is not None:
            self.cam.data.dof.focus_distance = d.length; self.cam.data.dof.aperture_fstop = dof

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
