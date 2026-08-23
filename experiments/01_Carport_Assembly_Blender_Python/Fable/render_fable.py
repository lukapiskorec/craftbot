# Headless renderer + overlap checker for the Fable run of experiment 01.
#
# Usage:
#   blender --background --python render_fable.py -- <experiment.py> <lib_dir> <out_prefix> [view,view,...]
#
# Renders Workbench (solid) views with object outlines on, so coplanar members
# stay distinguishable.  Collections can be hidden per view.  Because every
# member is a scaled cube, a separating-axis test between all object pairs
# reports any real interpenetration (tolerance 1 mm) before rendering.

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
meshes = [o for o in scene.objects if o.type == "MESH"]
if not meshes:
    print("No mesh objects generated, aborting render.")
    sys.exit(1)


# --- OBB overlap check (separating axis theorem on scaled cubes) -----------
def obb(o):
    m = o.matrix_world
    centre = m.translation.copy()
    axes = [Vector(m.col[i][:3]) for i in range(3)]      # scaled local axes
    half = [a.length for a in axes]
    units = [a / a.length for a in axes]
    return centre, units, half


def penetration(a, b):
    """Minimum overlap over all 15 SAT axes (<= 0 means separated)."""
    ca, ua, ha = a
    cb, ub, hb = b
    d = cb - ca
    best = float("inf")
    for axis in ua + ub + [x.cross(y) for x in ua for y in ub]:
        if axis.length < 1e-9:
            continue
        axis = axis.normalized()
        ra = sum(h * abs(axis.dot(u)) for u, h in zip(ua, ha))
        rb = sum(h * abs(axis.dot(u)) for u, h in zip(ub, hb))
        overlap = ra + rb - abs(d.dot(axis))
        best = min(best, overlap)
        if best <= 0:
            return best
    return best


boxes = [(o.name, obb(o)) for o in meshes]
hits = []
for (na, a), (nb, b) in itertools.combinations(boxes, 2):
    if (a[0] - b[0]).length > sum(a[2]) + sum(b[2]):
        continue
    p = penetration(a, b)
    if p > 0.001:
        hits.append((p, na, nb))
hits.sort(reverse=True)
print(f"OVERLAP CHECK: {len(hits)} interpenetrating pairs (tol 1 mm) among {len(boxes)} members")
for p, na, nb in hits[:60]:
    print(f"  {p*1000:7.1f} mm  {na}  x  {nb}")


# --- Camera / shading ---------------------------------------------------------
def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, max((hi - lo).length / 2, 0.001)


full_center, full_radius = bounds(meshes)

COLORS = {
    "Foundation": (0.62, 0.62, 0.60, 1.0),
    "Structure_Posts": (0.55, 0.36, 0.20, 1.0),
    "Structure_Bents": (0.72, 0.48, 0.26, 1.0),
    "Roof_Longitudinal": (0.82, 0.60, 0.32, 1.0),
    "Roof_Rafters": (0.90, 0.76, 0.50, 1.0),
}


def colorize(coll, color):
    color = COLORS.get(coll.name, color)
    for o in coll.objects:
        o.color = color
    for c in coll.children:
        colorize(c, color)


for c in scene.collection.children:
    colorize(c, (0.7, 0.7, 0.7, 1.0))

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


# View spec: azimuth/elevation in degrees, collections to hide, optional focus
# (center, radius) for close-ups.  Building runs along X (0..9), span along Y.
VIEWS = [
    dict(name="01", azim=-35, elev=25, hide=[]),                       # like reference image 1
    dict(name="02", azim=215, elev=25, hide=[]),                       # like reference image 2
    dict(name="03", azim=0, elev=0.5, hide=[]),                        # gable elevation (from +X)
    dict(name="04", azim=-90, elev=0.5, hide=[]),                      # side elevation (from -Y)
    dict(name="05", azim=90, elev=89.0, hide=[]),                      # top
    dict(name="06", azim=-35, elev=25, hide=["Roof_Rafters"]),         # frame without commons
    dict(name="07", azim=-35, elev=25, hide=["Roof_Rafters", "Roof_Longitudinal"]),
    dict(name="08", azim=-60, elev=20, hide=[], focus=(Vector((0.0, -3.0, 2.9)), 1.6)),   # eave / post head
    dict(name="09", azim=-60, elev=20, hide=["Roof_Rafters"], focus=(Vector((0.0, -3.0, 2.9)), 1.6)),
    dict(name="10", azim=-20, elev=-12, hide=[], focus=(Vector((1.0, 0.0, 5.8)), 1.4)),   # apex / ridge from below
    dict(name="11", azim=-60, elev=15, hide=["Roof_Rafters"], focus=(Vector((1.5, -1.7, 4.3)), 1.6)),  # purlin / strut
    dict(name="12", azim=0, elev=0.5, hide=["Roof_Rafters"], focus=(Vector((0.0, 0.0, 4.3)), 3.6)),    # truss elevation
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

    if "focus" in view:
        cam_data.ortho_scale = 2 * radius * 1.05 / aspect
    else:
        R = cam.rotation_euler.to_matrix()
        Rinv = R.transposed()
        visible = [o for o in meshes if not any(c.name in view["hide"] for c in o.users_collection)]
        pts = [Rinv @ ((o.matrix_world @ Vector(c)) - cam.location)
               for o in visible for c in o.bound_box]
        w = max(p.x for p in pts) - min(p.x for p in pts)
        h = max(p.y for p in pts) - min(p.y for p in pts)
        cam_data.ortho_scale = max(w, h / aspect) * 1.05
        mid = Vector(((max(p.x for p in pts) + min(p.x for p in pts)) / 2,
                      (max(p.y for p in pts) + min(p.y for p in pts)) / 2, 0.0))
        cam.location = cam.location + R @ mid

    scene.render.filepath = f"{out_prefix}_blender_view_{view['name']}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {scene.render.filepath}")

for coll in all_collections(scene.collection):
    coll.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=f"{out_prefix}.blend")
print("DONE")
