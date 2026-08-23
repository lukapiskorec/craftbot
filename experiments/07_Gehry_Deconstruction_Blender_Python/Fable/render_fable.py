# Headless renderer for the Fable run of experiment 07 (Gehry deconstruction).
#
# Usage:
#   blender --background --python render_fable.py -- <experiment.py> <lib_dir> <out_prefix> [view,view,...]
#
# Renders Workbench (solid) views with object outlines on, so coplanar
# members stay distinguishable. Collections can be hidden per view for
# visibility. After rendering it runs a separating-axis overlap check on
# every pair of members (all members are convex: boxes or prisms) and
# prints the penetrating pairs.

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
    "Foundation": (0.45, 0.45, 0.48, 1.0),
    "Floor_Framing": (0.62, 0.42, 0.24, 1.0),
    "Floor_Boards": (0.92, 0.84, 0.62, 1.0),
    "Wall_Framing": (0.80, 0.58, 0.32, 1.0),
    "Roof_Framing": (0.66, 0.46, 0.26, 1.0),
    "Exterior_Sheathing": (0.90, 0.80, 0.55, 1.0),
    "Windows": (0.55, 0.80, 0.95, 1.0),
    "Gable_Sheathing": (0.90, 0.80, 0.55, 1.0),
    "Roof_Covering": (0.40, 0.42, 0.45, 1.0),
    "Deck_Foundation": (0.45, 0.45, 0.48, 1.0),
    "Deck_Framing": (0.62, 0.42, 0.24, 1.0),
    "Deck_Boards": (0.85, 0.74, 0.52, 1.0),
    "Wrap_Wall_Framing": (0.85, 0.55, 0.25, 1.0),
    "Wall_Cladding": (0.72, 0.70, 0.66, 1.0),
    "Wrap_Roof_Framing": (0.70, 0.45, 0.22, 1.0),
    "Roof_Boards": (0.60, 0.60, 0.58, 1.0),
    "Wrap_Openings": (0.55, 0.80, 0.95, 1.0),
    "Wrap_Doors": (0.55, 0.35, 0.20, 1.0),
    "Steps": (0.50, 0.50, 0.52, 1.0),
    "Frame": (0.75, 0.30, 0.20, 1.0),
    "Glass": (0.45, 0.85, 0.95, 1.0),
    "Cage": (0.55, 0.40, 0.25, 1.0),
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


def hidden_objects(hide):
    """Objects in a hidden collection or any of its descendants."""
    out = set()
    for coll in all_collections(scene.collection):
        if coll.name in hide:
            for c in all_collections(coll):
                out.update(c.objects)
    return out


SKIN = ["Wall_Cladding", "Roof_Boards", "Exterior_Sheathing", "Gable_Sheathing", "Roof_Covering",
        "Wrap_Openings", "Wrap_Doors", "Windows", "Glass"]
ROOFS = ["Roof_Boards", "Roof_Covering", "Gable_Sheathing"]

# View spec: azimuth/elevation in degrees, collections to hide, optional focus
# (center, radius).  Azimuth 0 = camera on +X (east), 90 = +Y (north),
# 180 = -X (west), 270 = -Y (south).  The wrap sits at the south-west.
VIEWS = [
    dict(name="01", azim=225, elev=25, hide=[]),                                   # south-west: both wings, corner
    dict(name="02", azim=300, elev=25, hide=[]),                                   # south-east: cube, east end wall
    dict(name="03", azim=150, elev=25, hide=[]),                                   # north-west: west wing north end
    dict(name="04", azim=45, elev=25, hide=[]),                                    # north-east: untouched old facades
    dict(name="05", azim=270, elev=89, hide=[]),                                   # roof plan
    dict(name="06", azim=270, elev=0, hide=[]),                                    # south elevation
    dict(name="07", azim=180, elev=0, hide=[]),                                    # west elevation
    dict(name="08", azim=225, elev=25, hide=SKIN),                                 # framing only, south-west
    dict(name="09", azim=225, elev=35, hide=ROOFS),                                # roofs off: rafters, trusses, studs
    dict(name="10", azim=290, elev=30, hide=[], focus=(Vector((4.9, -1.8, 3.4)), 1.7)),      # tilted cube
    dict(name="11", azim=255, elev=10, hide=[], focus=(Vector((1.5, -3.0, 2.0)), 1.7)),      # fractured south window
    dict(name="12", azim=195, elev=10, hide=[], focus=(Vector((-2.7, 1.0, 1.8)), 2.2)),      # west door + wedge window
    dict(name="13", azim=225, elev=30, hide=["Old_House"]),                        # wrap alone
    dict(name="14", azim=225, elev=20, hide=SKIN, focus=(Vector((-2.4, -2.8, 2.6)), 1.3)),   # corner post / valley
    dict(name="15", azim=45, elev=35, hide=["Old_House", "Roof_Boards"]),          # wrap from inside (old house off)
    dict(name="16", azim=300, elev=30, hide=SKIN, focus=(Vector((4.9, -1.8, 3.4)), 1.7)),    # cube framing into the rafters
    dict(name="17", azim=225, elev=-20, hide=[]),                                  # from below
    dict(name="18", azim=315, elev=15, hide=SKIN, focus=(Vector((7.3, -1.6, 2.0)), 2.2)),    # east end wall framing
    dict(name="19", azim=300, elev=35, hide=SKIN, focus=(Vector((5.6, -1.8, 3.6)), 2.4)),    # cube trimmers + cage legs
    dict(name="20", azim=250, elev=15, hide=SKIN, focus=(Vector((-2.4, -1.5, 2.2)), 2.2)),   # braces + eave blocking at the corner
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


# --- Overlap check: every member is a convex polyhedron (box or prism),
# so test pairs with the separating-axis theorem over face normals and
# edge cross products and report the minimum penetration depth. ---
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
