# Headless renderer for the Fable run of experiment 03 (VIPP shelter).
#
# Usage:
#   blender --background --python render_fable.py -- <experiment.py> <lib_dir> <out_prefix> [view,view,...]
#
# Renders Workbench (solid) views with object outlines on, so coplanar
# members stay distinguishable. Collections can be hidden per view for
# visibility. After rendering it runs a box-box (separating axis) overlap
# check on every pair of members and prints the penetrating pairs.

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
    "Foundation": (0.35, 0.35, 0.38, 1.0),
    "Floor_Framing": (0.62, 0.42, 0.24, 1.0),
    "Ground_Walls": (0.80, 0.58, 0.32, 1.0),
    "Interior_Walls": (0.85, 0.70, 0.45, 1.0),
    "Roof_Framing": (0.66, 0.46, 0.26, 1.0),
    "Loft_Boxes": (0.78, 0.55, 0.30, 1.0),
    "Shear_Panels": (0.75, 0.72, 0.55, 1.0),
    "Ground_Subfloor": (0.92, 0.84, 0.62, 1.0),
    "Roof_Deck": (0.92, 0.84, 0.62, 1.0),
    "Sheathing": (0.30, 0.30, 0.32, 1.0),
    "Glazing": (0.55, 0.80, 0.95, 1.0),
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


SKIN = ["Sheathing", "Glazing"]
UPPER = ["Roof_Framing", "Roof_Deck", "Loft_Boxes"] + SKIN

# View spec: azimuth/elevation in degrees, collections to hide, optional focus
# (center, radius) for close-ups.  Azimuth 0 = camera on +X (glazed end),
# 270 = camera on -Y looking at the front (glazed, no boxes) facade.
VIEWS = [
    dict(name="01", azim=300, elev=25, hide=[]),                      # front / glazed-end corner
    dict(name="02", azim=120, elev=25, hide=[]),                      # back / bathroom-end corner
    dict(name="03", azim=270, elev=0, hide=[]),                       # front elevation
    dict(name="04", azim=90, elev=89, hide=[]),                       # top
    dict(name="05", azim=300, elev=25, hide=SKIN),                    # frame only, front
    dict(name="06", azim=120, elev=25, hide=SKIN),                    # frame only, back
    dict(name="07", azim=90, elev=89, hide=SKIN + ["Roof_Deck"]),     # top, roof framing + box framing
    dict(name="08", azim=300, elev=30, hide=UPPER),                   # ground floor only
    dict(name="09", azim=90, elev=89, hide=UPPER + ["Ground_Walls"]), # plan: partitions + subfloor
    dict(name="10", azim=300, elev=30, hide=SKIN + ["Roof_Deck"], focus=(Vector((3.3, 4.0, 4.6)), 2.2)),   # hatch / box 1
    dict(name="11", azim=240, elev=30, hide=SKIN + ["Roof_Deck"], focus=(Vector((8.5, 3.9, 4.6)), 3.2)),   # light well / box 2
    dict(name="12", azim=320, elev=20, hide=[], focus=(Vector((11.5, 0.0, 2.6)), 2.2)),                     # glazed corner + ring beam
    dict(name="13", azim=60, elev=35, hide=SKIN + ["Roof_Deck", "Loft_Boxes"], focus=(Vector((8.5, 4.6, 4.0)), 2.8)),  # well rim + blocking
    dict(name="14", azim=300, elev=30, hide=UPPER, focus=(Vector((1.8, 2.0, 2.5)), 2.6)),                     # bathroom shear panels
    dict(name="15", azim=240, elev=10, hide=SKIN + ["Roof_Deck", "Loft_Boxes", "Ground_Walls", "Floors"], focus=(Vector((3.0, 0.6, 0.9)), 1.6)),  # floor blocking
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

    visible = [o for o in meshes
               if not any(c.name in view["hide"] for c in o.users_collection)]
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


# --- Overlap check: every member is a box, so test oriented boxes with the
# separating-axis theorem and report the minimum penetration depth. ---
def obb(o):
    M = o.matrix_world
    centre = M.translation.copy()
    axes, half = [], []
    for i in range(3):
        col = Vector((M[0][i], M[1][i], M[2][i]))
        half.append(col.length)
        axes.append(col.normalized())
    return centre, axes, half


def penetration(a, b):
    ca, aa, ha = a
    cb, ab, hb = b
    d = cb - ca
    tests = aa + ab + [x.cross(y) for x in aa for y in ab]
    depth = float("inf")
    for Lx in tests:
        if Lx.length < 1e-9:
            continue
        Lx = Lx.normalized()
        ra = sum(h * abs(Lx.dot(x)) for h, x in zip(ha, aa))
        rb = sum(h * abs(Lx.dot(x)) for h, x in zip(hb, ab))
        gap = abs(d.dot(Lx)) - ra - rb
        if gap >= 0:
            return 0.0
        depth = min(depth, -gap)
    return depth


boxes = [(o.name, obb(o)) for o in meshes]
TOL = 0.001
hits = []
for (na, a), (nb, b) in itertools.combinations(boxes, 2):
    if (a[0] - b[0]).length > sum(a[2]) + sum(b[2]):
        continue
    p = penetration(a, b)
    if p > TOL:
        hits.append((p, na, nb))
hits.sort(reverse=True)
print(f"OVERLAP CHECK: {len(boxes)} members, {len(hits)} penetrating pairs (> {TOL * 1000:.0f} mm)")
for p, na, nb in hits:
    print(f"  {p * 1000:6.1f} mm  {na}  x  {nb}")
print("DONE")
