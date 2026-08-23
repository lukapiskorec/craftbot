# Headless renderer for the Fable run of experiment 09 (CLT high-rise).
#
# Usage:
#   blender --background --python render_fable.py -- <experiment.py> <lib_dir> <out_prefix> [view,view,...]
#
# Renders Workbench (solid) views with object outlines on, so coplanar
# panels stay distinguishable. Collections can be hidden per view, and a
# view can carry a section cut (`cut`): the camera near-clip plane is set
# to that world plane so plan sections / cross sections can be rendered
# without per-storey collections. After rendering it runs a separating-
# axis overlap check on every pair of members (all members are convex
# boxes or prisms) and prints the penetrating pairs.

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
model = {"__name__": "__main__"}
exec(compile(open(experiment_path).read(), experiment_path, "exec"), model)

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
    "Podium_Walls": (0.55, 0.55, 0.58, 1.0),
    "Podium_Frame": (0.45, 0.45, 0.48, 1.0),
    "Podium_Slabs": (0.62, 0.62, 0.65, 1.0),
    "Podium_Stairs": (0.50, 0.50, 0.53, 1.0),
    "Exterior_Walls": (0.85, 0.70, 0.45, 1.0),
    "Interior_Walls": (0.90, 0.80, 0.58, 1.0),
    "Knee_Walls": (0.80, 0.62, 0.40, 1.0),
    "Partitions": (0.86, 0.86, 0.82, 1.0),
    "Ledgers": (0.55, 0.32, 0.18, 1.0),
    "Ribs": (0.55, 0.32, 0.18, 1.0),
    "Gable_Walls": (0.85, 0.70, 0.45, 1.0),
    "Core_Walls": (0.78, 0.45, 0.25, 1.0),
    "Core_Slabs": (0.88, 0.72, 0.50, 1.0),
    "Stairs": (0.70, 0.40, 0.22, 1.0),
    "Landings": (0.80, 0.55, 0.32, 1.0),
    "Slabs": (0.92, 0.84, 0.62, 1.0),
    "Roof_Panels": (0.75, 0.58, 0.36, 1.0),
    "Roof_Covering": (0.35, 0.37, 0.40, 1.0),
    "Cladding": (0.60, 0.66, 0.58, 1.0),
    "Glazing": (0.55, 0.80, 0.95, 1.0),
    "Doors": (0.30, 0.45, 0.70, 1.0),
}


def colorize(coll, color):
    color = COLORS.get(coll.name, color)
    for o in coll.objects:
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
scene.render.resolution_x = 1800
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


M = model
SKIN = ["Facade", "Roof_Covering", "Openings"]
ENVELOPE = ["Facade", "Roof", "Openings"]
NOT_CORE = ["Podium", "Structure", "Floors", "Roof", "Facade", "Openings"]
Z_PLAN = M["z_floor"](3) + 1.3          # plan section through storey 3
Z_ATTIC = M["z_floor"](8) + 1.3         # plan section through attic 2

# View spec: azimuth/elevation in degrees (azimuth 0 = camera on +X,
# 90 = +Y, 270 = camera south of the building looking north), collections
# to hide, optional focus (center, radius), optional section cut
# (axis, value): the camera near-clip plane is placed on that world plane.
# The clip plane is perpendicular to the view direction, so cuts are true
# sections only for elev 0 (vertical sections) or 89.9 (plan sections).
VIEWS = [
    dict(name="01", azim=235, elev=25, hide=[]),                                   # south-west, full
    dict(name="02", azim=50, elev=25, hide=[]),                                    # north-east, full
    dict(name="03", azim=270, elev=0, hide=[]),                                    # south elevation
    dict(name="04", azim=180, elev=0, hide=[]),                                    # west gable elevation
    dict(name="05", azim=235, elev=28, hide=SKIN),                                 # CLT structure, roof panels on
    dict(name="06", azim=235, elev=28, hide=ENVELOPE),                             # walls, slabs, core
    dict(name="07", azim=270, elev=89.9, hide=[], cut=("z", Z_PLAN)),              # plan section storey 3
    dict(name="08", azim=270, elev=89.9, hide=[], cut=("z", Z_ATTIC)),             # plan section attic 2
    dict(name="09", azim=270, elev=0, hide=[], cut=("y", M["Y_FA1"] + 0.05)),      # cross section through the stair well (looking north)
    dict(name="10", azim=180, elev=0, hide=[], cut=("x", 13.5)),                   # long section through the core / lifts (looking east)
    dict(name="11", azim=230, elev=30, hide=NOT_CORE),                             # core only
    dict(name="12", azim=285, elev=35, hide=NOT_CORE + ["Core_Walls", "Core_Slabs"],
         focus=(Vector((13.14, 8.93, M["z_floor"](3) + 1.6)), 5.0)),               # stair close-up (from the corridor side), core walls off
    dict(name="13", azim=250, elev=35, hide=ENVELOPE, focus=(Vector((13.1, 6.6, M["Z7"] + 3.0)), 9.0)),  # attic / roof support close-up
    dict(name="14", azim=235, elev=-20, hide=[]),                                  # from below (podium, eaves)
    dict(name="15", azim=270, elev=89.9, hide=[], cut=("z", 2.2)),                 # plan section podium
    dict(name="16", azim=50, elev=25, hide=[], focus=(Vector((M["LX"], 8.8, M["Z8"] + 1.6)), 3.0)),   # east gable attic window close-up
    dict(name="17", azim=235, elev=-30, hide=ENVELOPE + ["Podium", "Structure", "Openings"],
         focus=(Vector((13.1, 6.6, M["z_floor"](4))), 7.0)),                       # core ledgers from below
    dict(name="18", azim=270, elev=0, hide=ENVELOPE + ["Openings"], cut=("y", 2.9),
         focus=(Vector((16.0, 5.0, M["Z7"] - 0.8)), 9.0)),                        # section y = 2.9 looking north: attic-1 ribbed floor, knee walls, partitions
    dict(name="19", azim=270, elev=-89.9, hide=ENVELOPE + ["Openings"], cut=("z", M["Z7"] - 0.55)),   # attic-1 slab from below: ribs, ledgers

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

    if "cut" in view:
        axis, value = view["cut"]
        d = (center - cam.location).normalized()
        p = Vector(cam.location)
        setattr(p, axis, value)
        cam_data.clip_start = max(0.01, (p - cam.location).dot(d))
    else:
        cam_data.clip_start = 0.01

    scene.render.filepath = f"{out_prefix}_view_{view['name']}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {scene.render.filepath}")

for coll in all_collections(scene.collection):
    coll.hide_render = False
cam_data.clip_start = 0.01
bpy.ops.wm.save_as_mainfile(filepath=f"{out_prefix}.blend")


# --- Overlap check: every member is a convex polyhedron (box or prism),
# so test pairs with the separating-axis theorem over face normals and
# edge cross products and report the minimum penetration depth. ---
def hull(o):
    Mw = o.matrix_world
    verts = [Mw @ v.co for v in o.data.vertices]
    R = Mw.to_3x3()
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
for p, name_a, name_b in hits[:80]:
    print(f"  {p * 1000:6.1f} mm  {name_a}  x  {name_b}")
print("DONE")
