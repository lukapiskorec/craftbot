# Headless renderer for the Fable run of experiment 06 (Prouve 6x6 cabanon).
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
    "Portico": (0.20, 0.30, 0.75, 1.0),
    "Ridge_Beams": (0.25, 0.60, 0.35, 1.0),
    "Gable_Panels": (0.55, 0.65, 0.40, 1.0),
    "Wall_Posts": (0.80, 0.58, 0.32, 1.0),
    "Eave_Rails": (0.25, 0.60, 0.35, 1.0),
    "Floor_Boards": (0.92, 0.84, 0.62, 1.0),
    "Cladding": (0.72, 0.52, 0.36, 1.0),
    "Interior_Lining": (0.92, 0.90, 0.84, 1.0),
    "Openings": (0.55, 0.80, 0.95, 1.0),
    "Tray_Ribs": (0.66, 0.46, 0.26, 1.0),
    "Tray_Decks": (0.78, 0.66, 0.46, 1.0),
    "Covering": (0.40, 0.42, 0.45, 1.0),
    "Ceiling": (0.90, 0.88, 0.80, 1.0),
    "Stairs": (0.70, 0.50, 0.30, 1.0),
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


SKIN = ["Facade", "Roof", "Ceiling"]
ROOF_ALL = ["Roof", "Ceiling"]

# View spec: azimuth/elevation in degrees, collections to hide, optional focus
# (center, radius).  Azimuth 0 = camera on +X (east gable), 270 = camera on -Y
# (south eave wall), 180 = camera on -X (west gable with the door).
VIEWS = [
    dict(name="01", azim=215, elev=25, hide=[]),                                   # south-west corner (door gable)
    dict(name="02", azim=40, elev=25, hide=[]),                                    # north-east corner
    dict(name="03", azim=270, elev=0, hide=[]),                                    # south elevation
    dict(name="04", azim=180, elev=0, hide=[]),                                    # west gable elevation (door)
    dict(name="05", azim=270, elev=89, hide=[]),                                   # roof plan
    dict(name="06", azim=215, elev=25, hide=SKIN),                                 # frame only, south-west
    dict(name="07", azim=40, elev=25, hide=SKIN),                                  # frame only, north-east
    dict(name="08", azim=270, elev=0, hide=SKIN + ["Wall_Posts", "Gable_Panels", "Eave_Rails", "Stairs"]),  # portico elevation
    dict(name="09", azim=270, elev=89, hide=["Covering", "Ceiling", "Tray_Decks"]), # tray rib layout plan
    dict(name="10", azim=215, elev=25, hide=ROOF_ALL + ["Facade", "Wall_Posts", "Eave_Rails", "Gable_Panels"]),  # platform + portico + ridge
    dict(name="11", azim=215, elev=-25, hide=[]),                                  # from below
    dict(name="12", azim=200, elev=15, hide=[], focus=(Vector((-0.2, 3.0, 1.5)), 1.9)),      # door gable close-up
    dict(name="13", azim=300, elev=15, hide=SKIN, focus=(Vector((3.0, 3.0, 2.8)), 1.0)),    # portico head / ridge splice
    dict(name="14", azim=300, elev=15, hide=SKIN, focus=(Vector((0.0, 0.0, 2.8)), 1.0)),    # eave rail / corner detail
    dict(name="15", azim=215, elev=25, hide=ROOF_ALL + ["Cladding", "Stairs"]),   # walls with lining, roof off
    dict(name="16", azim=250, elev=25, hide=["Roof", "Ceiling", "Cladding", "Interior_Lining", "Openings"], focus=(Vector((3.0, 3.0, 1.8)), 2.0)),  # portico lattice
    dict(name="17", azim=215, elev=35, hide=ROOF_ALL + ["Facade", "Wall_Posts", "Eave_Rails", "Gable_Panels", "Floors", "Stairs", "Portico", "Ridge_Beams"]),  # joists and bearers
    dict(name="18", azim=290, elev=20, hide=[], focus=(Vector((1.5, 0.0, 1.5)), 1.2)),      # shuttered window close-up
    dict(name="19", azim=250, elev=20, hide=SKIN + ["Wall_Posts", "Gable_Panels"], focus=(Vector((1.5, 3.0, 2.9)), 1.3)),  # lattice ridge girder
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
