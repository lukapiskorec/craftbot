# Headless renderer for the Fable run of experiment 11 (T-shaped hip roof).
#
# Usage:
#   blender --background --python render_fable.py -- <experiment.py> <lib_dir> <out_prefix> [view,view,...]
#
# Renders Workbench (solid) views with object outlines on, so coplanar
# members / boards stay distinguishable. Collections can be hidden per
# view. After rendering it runs a separating-axis overlap check on every
# pair of members (all members are convex boxes or prisms) and prints the
# penetrating pairs (> 1 mm).

import bpy
import sys
import os
import math
import itertools
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
experiment_path, lib_dir, out_prefix = argv[0], argv[1], argv[2]
only_views = set(argv[3].split(",")) if len(argv) > 3 else None

sys.path.insert(0, lib_dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(experiment_path)))

bpy.ops.wm.read_factory_settings(use_empty=True)
exec(compile(open(experiment_path).read(), experiment_path, "exec"), {"__name__": "__main__"})

scene = bpy.context.scene


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, max((hi - lo).length / 2, 0.001)


meshes = [o for o in scene.objects if o.type == "MESH"]
if not meshes:
    print("No mesh objects generated, aborting render.")
    sys.exit(1)
full_center, full_radius = bounds(meshes)

# --- Per-collection object colours (Workbench OBJECT colour mode) ---
COLORS = {
    "Walls": (0.55, 0.55, 0.52, 1.0),
    "Ceiling": (0.78, 0.62, 0.40, 1.0),
    "RF_Main": (0.62, 0.42, 0.24, 1.0),
    "RF_Wing": (0.68, 0.46, 0.26, 1.0),
    "RF_Dormers": (0.75, 0.52, 0.30, 1.0),
    "SH_Main": (0.90, 0.80, 0.55, 1.0),
    "SH_Wing": (0.88, 0.78, 0.52, 1.0),
    "SH_Dormers": (0.92, 0.84, 0.60, 1.0),
    "FA_Cladding": (0.93, 0.92, 0.86, 1.0),
    "FA_Windows": (0.42, 0.30, 0.18, 1.0),
    "FA_Fascia": (0.95, 0.94, 0.90, 1.0),
}


def colorize(coll, color):
    color = COLORS.get(coll.name, color)
    for o in coll.objects:
        if o.name.startswith("Glass"):
            o.color = (0.70, 0.88, 0.98, 1.0)
        else:
            o.color = color
    for c in coll.children:
        colorize(c, color)


for c in scene.collection.children:
    colorize(c, (0.7, 0.7, 0.7, 1.0))

# --- Render settings ---
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "OBJECT"
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_object_outline = True
sh.object_outline_color = (0.0, 0.0, 0.0)
sh.show_shadows = False
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.world = bpy.data.worlds.new("World")
scene.world.color = (1.0, 1.0, 1.0)

cam_data = bpy.data.cameras.new("HeadlessCam")
cam_data.type = "ORTHO"
cam_data.clip_start = 0.01
cam_data.clip_end = full_radius * 40
cam = bpy.data.objects.new("HeadlessCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

aspect = min(scene.render.resolution_x, scene.render.resolution_y) / \
         max(scene.render.resolution_x, scene.render.resolution_y)


def all_collections(coll):
    yield coll
    for c in coll.children:
        yield from all_collections(c)


def hidden_objects(hide):
    out = set()
    for coll in all_collections(scene.collection):
        if coll.name in hide:
            for c in all_collections(coll):
                out.update(c.objects)
    return out


SKIN = ["Sheathing", "Facade"]
FRAME_ONLY = ["Sheathing", "Facade", "Walls"]
DORMER_ONLY = ["Sheathing", "Facade", "Walls", "Ceiling", "RF_Main", "RF_Wing"]

# Azimuth 0 = camera on +X (east), 90 = north, 180 = west, 270 = south.
VIEWS = [
    dict(name="01", azim=300, elev=28, hide=[]),                      # south-east: wing + E dormer
    dict(name="02", azim=60, elev=28, hide=[]),                       # north-east: N dormers
    dict(name="03", azim=210, elev=28, hide=[]),                      # south-west
    dict(name="04", azim=270, elev=89.9, hide=[]),                    # roof plan
    dict(name="05", azim=300, elev=28, hide=SKIN),                    # framing SE
    dict(name="06", azim=60, elev=28, hide=SKIN),                     # framing NE
    dict(name="07", azim=270, elev=89.9, hide=SKIN),                  # framing plan
    dict(name="08", azim=270, elev=89.9, hide=SKIN + ["Roof_Framing"]),   # ceiling / walls plan
    dict(name="09", azim=270, elev=0, hide=[]),                       # south elevation
    dict(name="10", azim=0, elev=0, hide=[]),                         # east elevation
    dict(name="11", azim=60, elev=30, hide=SKIN, focus=(Vector((2.1, 2.4, 5.0)), 2.6)),     # N dormer framing
    dict(name="12", azim=330, elev=30, hide=SKIN, focus=(Vector((5.4, 0.0, 5.0)), 2.6)),    # E dormer framing
    dict(name="13", azim=300, elev=35, hide=SKIN, focus=(Vector((2.5, -2.5, 5.5)), 3.0)),   # valley / ridge junction
    dict(name="14", azim=30, elev=35, hide=SKIN, focus=(Vector((6.5, 3.5, 3.5)), 2.0)),     # NE hip foot / eave
    dict(name="15", azim=240, elev=35, hide=SKIN, focus=(Vector((-0.5, -10.5, 5.0)), 2.8)), # wing S dormer
    dict(name="16", azim=60, elev=30, hide=[], focus=(Vector((2.1, 2.4, 5.0)), 2.6)),       # N dormer with boards
    dict(name="17", azim=300, elev=35, hide=[], focus=(Vector((2.5, -2.5, 5.5)), 3.0)),     # valley with boards
    dict(name="18", azim=60, elev=-30, hide=["Walls", "Facade", "Sheathing"]),              # from below: joists
    dict(name="19", azim=120, elev=35, hide=DORMER_ONLY, focus=(Vector((2.1, 2.4, 5.0)), 2.4)),  # N dormer alone
    dict(name="20", azim=40, elev=20, hide=DORMER_ONLY, focus=(Vector((2.1, 2.4, 5.0)), 2.4)),   # N dormer alone, front
    dict(name="21", azim=120, elev=35, hide=DORMER_ONLY + ["SH_Main"], focus=(Vector((2.1, 2.4, 5.0)), 2.4)),  # N dormer + its boards
]

for view in VIEWS:
    if only_views and view["name"] not in only_views:
        continue
    for coll in all_collections(scene.collection):
        coll.hide_render = coll.name in view["hide"]

    center, radius = view.get("focus", (full_center, full_radius))

    azim = math.radians(view["azim"])
    elev = math.radians(view["elev"])
    offset = Vector((
        math.cos(azim) * math.cos(elev),
        math.sin(azim) * math.cos(elev),
        math.sin(elev),
    )) * (full_radius * 4.0)
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

    hidden = hidden_objects(view["hide"])
    visible = [o for o in meshes if o not in hidden]
    if "focus" in view:
        cam_data.ortho_scale = 2 * radius * 1.05 / aspect
    else:
        R = cam.rotation_euler.to_matrix()
        Rinv = R.transposed()
        pts = [Rinv @ ((o.matrix_world @ Vector(c)) - cam.location)
               for o in visible for c in o.bound_box]
        w = max(p.x for p in pts) - min(p.x for p in pts)
        h = max(p.y for p in pts) - min(p.y for p in pts)
        cam_data.ortho_scale = max(w, h / aspect) * 1.05
        mid = Vector(((max(p.x for p in pts) + min(p.x for p in pts)) / 2,
                      (max(p.y for p in pts) + min(p.y for p in pts)) / 2, 0.0))
        cam.location = cam.location + R @ mid

    scene.render.filepath = f"{out_prefix}_view_{view['name']}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {scene.render.filepath}")

for coll in all_collections(scene.collection):
    coll.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=f"{out_prefix}.blend")


# --- Overlap check (SAT over face normals and edge cross products) ---
def hull(o):
    M = o.matrix_world
    verts = [M @ v.co for v in o.data.vertices]
    R = M.to_3x3()
    normals = []
    for p in o.data.polygons:
        n = (R @ p.normal).normalized()
        if not any(abs(abs(n.dot(m)) - 1) < 1e-6 for m in normals):
            normals.append(n)
    edges = []
    for e in o.data.edges:
        d = (verts[e.vertices[1]] - verts[e.vertices[0]]).normalized()
        if not any(abs(abs(d.dot(m)) - 1) < 1e-6 for m in edges):
            edges.append(d)
    lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
    return verts, normals, edges, lo, hi


def penetration(a, b):
    va, na, ea, _, _ = a
    vb, nb, eb, _, _ = b
    axes = na + nb + [x.cross(y) for x in ea for y in eb]
    depth = float("inf")
    for ax in axes:
        if ax.length < 1e-9:
            continue
        ax = ax.normalized()
        pa = [v.dot(ax) for v in va]
        pb = [v.dot(ax) for v in vb]
        gap = max(min(pa) - max(pb), min(pb) - max(pa))
        if gap >= 0:
            return 0.0
        depth = min(depth, -gap)
    return depth


hulls = [(o.name, hull(o)) for o in meshes]
TOL = 0.001
hits = []
for (name_a, a), (name_b, b) in itertools.combinations(hulls, 2):
    if any(a[3][i] > b[4][i] - TOL or b[3][i] > a[4][i] - TOL for i in range(3)):
        continue
    p = penetration(a, b)
    if p > TOL:
        hits.append((p, name_a, name_b))
hits.sort(reverse=True)
print(f"OVERLAP CHECK: {len(hulls)} members, {len(hits)} penetrating pairs (> {TOL * 1000:.0f} mm)")
for p, name_a, name_b in hits:
    print(f"  {p * 1000:6.1f} mm  {name_a}  x  {name_b}")
print("DONE")
