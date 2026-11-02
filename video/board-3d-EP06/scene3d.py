"""3D sample for 单板 EP.06: the same board carves three arcs at 30° / 45° / 70° edge angle (R = R_sc · cos θ).
Run with the bpy venv:  python scene3d.py OUTDIR [first last]   -> OUTDIR/f_00000.png ...
Ideal-carving geometry; flat snow for clarity (示意)."""
import sys, os, math
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FPS = 30
RSC = 7.0
ANG = [30, 45, 70]
COLS = [(0.45, 0.72, 1.0), (1.0, 0.80, 0.46), (0.92, 0.42, 0.36)]
PH = 3.5                     # seconds per carve
SWEEP = math.radians(150)    # arc swept per carve
T_TOP = 3 * PH               # then camera rises to a top view
DUR = T_TOP + 4.0
N = int(DUR * FPS)
first = int(sys.argv[2]) if len(sys.argv) > 2 else 0
last = int(sys.argv[3]) if len(sys.argv) > 3 else N

# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = os.environ.get("ENGINE", "CYCLES")
if sc.render.engine == "CYCLES":
    sc.cycles.device = "CPU"
    sc.cycles.samples = int(os.environ.get("SAMPLES", "24"))
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 2
    sc.cycles.diffuse_bounces = 1; sc.cycles.glossy_bounces = 1; sc.cycles.transmission_bounces = 0
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
    sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = 1440, 810
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.08, 0.16, 1); bg.inputs[1].default_value = 1.0
sc.view_settings.exposure = -0.3


def mat(name, col, rough=0.5, emit=0.0, metallic=0.0, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    if emit:
        p.inputs["Emission Color"].default_value = (*col, 1); p.inputs["Emission Strength"].default_value = emit
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
    return m


M_SNOW = mat("snow", (0.55, 0.62, 0.75), 0.85)
M_BOARD = mat("board", (0.95, 0.62, 0.22), 0.35)
M_BASE = mat("base", (0.08, 0.09, 0.11), 0.3)
M_BOOT = mat("boot", (0.18, 0.20, 0.26), 0.6)
M_BODY = mat("body", (0.88, 0.89, 0.92), 0.55)
M_TRAIL = [mat(f"trail{i}", c, 0.4, emit=2.5) for i, c in enumerate(COLS)]
M_RING = mat("ring", (0.75, 0.80, 0.88), 0.5, emit=0.6)

# snow: big plane with gentle noise displacement for texture
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
snow = bpy.context.object; snow.data.materials.append(M_SNOW)
nt = M_SNOW.node_tree
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 3.0; noise.inputs["Detail"].default_value = 8
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])

# sun
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(68), 0, math.radians(130)))
sun = bpy.context.object; sun.data.energy = 2.2; sun.data.color = (1.0, 0.85, 0.65); sun.data.angle = math.radians(3)


# ------------------------------------------------------------------ board with real sidecut (1.56 m, waist 0.25 m, tip 0.29 m)
def make_board():
    L, waist, tip = 1.56, 0.25, 0.29
    bm = bmesh.new()
    n = 60
    half = L / 2
    eff = 1.20 / 2                         # effective edge half-length
    sag = (tip - waist) / 2
    outline = []
    for i in range(n + 1):                 # right edge, nose -> tail
        x = half - L * i / n
        if abs(x) <= eff:
            y = waist / 2 + sag * (x / eff) ** 2
        else:                              # rounded tip
            u = (abs(x) - eff) / (half - eff)
            y = (tip / 2) * math.sqrt(max(0.0, 1 - u ** 2.2))
        outline.append((x, y))
    pts = outline + [(x, -y) for x, y in reversed(outline)]
    top = [bm.verts.new((x, y, 0.016 + 0.05 * max(0, (abs(x) - eff) / (half - eff)) ** 2)) for x, y in pts]
    bot = [bm.verts.new((x, y, 0.0 + 0.05 * max(0, (abs(x) - eff) / (half - eff)) ** 2)) for x, y in pts]
    ft = bm.faces.new(top); fb = bm.faces.new(list(reversed(bot)))
    k = len(pts)
    for i in range(k):
        bm.faces.new([top[i], top[(i + 1) % k], bot[(i + 1) % k], bot[i]])
    me = bpy.data.meshes.new("board"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("board", me); sc.collection.objects.link(ob)
    ob.data.materials.append(M_BOARD); ob.data.materials.append(M_BASE)
    for p in ob.data.polygons:
        p.material_index = 1 if p.normal.z < -0.5 else 0
        p.use_smooth = False
    return ob


board = make_board()


def cap(name, a, b, r, m, parent):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=24, location=(a + b) / 2)
    o = bpy.context.object; o.name = name
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    o.parent = parent
    for e in (a, b):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=e, segments=24, ring_count=12)
        s = bpy.context.object; s.data.materials.append(m); s.parent = parent
        for p in s.data.polygons:
            p.use_smooth = True
    return o


# mannequin in board-local coordinates: board long axis = x, toes toward +y (the turn centre side), z up
rig = bpy.data.objects.new("rig", None); sc.collection.objects.link(rig)
board.parent = rig
for fx in (-0.27, 0.27):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, 0.0, 0.08)); bt = bpy.context.object
    bt.scale = (0.12, 0.31, 0.12); bt.data.materials.append(M_BOOT); bt.parent = rig
hipL, hipR = Vector((-0.12, -0.02, 0.86)), Vector((0.12, -0.02, 0.86))
kneeL, kneeR = Vector((-0.24, 0.16, 0.50)), Vector((0.24, 0.16, 0.50))
cap("shinL", (-0.27, 0.0, 0.14), kneeL, 0.055, M_BODY, rig); cap("thighL", kneeL, hipL, 0.07, M_BODY, rig)
cap("shinR", (0.27, 0.0, 0.14), kneeR, 0.055, M_BODY, rig); cap("thighR", kneeR, hipR, 0.07, M_BODY, rig)
cap("torso", (0, -0.02, 0.88), (0, 0.06, 1.38), 0.13, M_BODY, rig)
cap("armL", (-0.16, 0.05, 1.33), (-0.50, 0.22, 1.02), 0.045, M_BODY, rig)
cap("armR", (0.16, 0.05, 1.33), (0.50, 0.22, 1.02), 0.045, M_BODY, rig)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.08, 1.58), segments=32, ring_count=16)
head = bpy.context.object; head.data.materials.append(M_BODY); head.parent = rig
for p in head.data.polygons:
    p.use_smooth = True


# ------------------------------------------------------------------ carve geometry
def arc_point(i, s):
    """carve i at fraction s in [0,1]: all carves start at the origin heading +x, turning left (centre at +y)."""
    R = RSC * math.cos(math.radians(ANG[i]))
    phi = SWEEP * s
    c = Vector((0, R, 0))
    p = c + Vector((R * math.sin(phi), -R * math.cos(phi), 0))
    tang = Vector((math.cos(phi), math.sin(phi), 0))
    return p, tang, R


def trail_mesh(i, s, name):
    R = arc_point(i, 0)[2]
    bm = bmesh.new()
    n = max(2, int(120 * s))
    w = 0.035
    vs = []
    for k in range(n + 1):
        p, tg, _ = arc_point(i, s * k / n)
        nrm = Vector((-tg.y, tg.x, 0))
        vs.append((bm.verts.new(p + nrm * w + Vector((0, 0, 0.004))), bm.verts.new(p - nrm * w + Vector((0, 0, 0.004)))))
    for k in range(n):
        bm.faces.new([vs[k][0], vs[k + 1][0], vs[k + 1][1], vs[k][1]])
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


trails = []
for i in range(3):
    me = trail_mesh(i, 0.001, f"trail{i}")
    ob = bpy.data.objects.new(f"trail{i}", me); sc.collection.objects.link(ob); ob.data.materials.append(M_TRAIL[i])
    trails.append(ob)

cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 32
cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(cam); sc.camera = cam


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def look(obj, target):
    d = (Vector(target) - obj.location)
    obj.rotation_mode = "QUATERNION"; obj.rotation_quaternion = d.to_track_quat("-Z", "Y")


def set_frame(f):
    t = f / FPS
    if t < T_TOP:
        i = int(t // PH); s = ease((t - i * PH) / PH) if True else 0
    else:
        i, s = 2, 1.0
    for j in range(3):
        sj = 1.0 if j < i else (s if j == i else 0.001)
        trail_mesh(j, max(sj, 0.001), f"trail{j}")
        trails[j].hide_render = (sj <= 0.001)
    p, tg, R = arc_point(i, s)
    th = math.radians(ANG[i]) * min(1.0, (t - i * PH) / 0.6 if t < T_TOP else 1.0) if t < T_TOP else math.radians(ANG[2])
    # board frame: x along tangent, roll toward the centre by the edge angle; lift so the inside edge touches snow
    yaw = math.atan2(tg.y, tg.x)
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = Euler((-th, 0, yaw), "ZYX") if False else (Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-th, 4, "X")).to_euler()
    rig.location = p + Vector((0, 0, 0.125 * math.sin(th)))
    rig.hide_render = t >= T_TOP + 0.5
    for o in rig.children:
        o.hide_render = rig.hide_render
    # camera: chase from outside-behind, then crane up to a top view of the three arcs
    nrm = Vector((-tg.y, tg.x, 0))
    chase = p - tg * 3.4 - nrm * 2.2 + Vector((0, 0, 1.5))
    top = Vector((2.6, 4.2, 21.0))
    k = ease((t - T_TOP) / 2.5)
    cam.location = chase.lerp(top, k)
    tgt = (p + Vector((0, 0, 0.6))).lerp(Vector((2.6, 4.6, 0)), k)
    look(cam, tgt)


meta = []
for f in range(first, min(last, N)):
    set_frame(f)
    sc.render.filepath = os.path.join(OUT, f"f_{f:05d}.png")
    bpy.ops.render.render(write_still=True)
print("frames", N)
