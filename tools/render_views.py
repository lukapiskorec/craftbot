# Headless render harness for CraftBot experiments: runs an experiment
# script in background Blender, renders Workbench views with object
# outlines on (coplanar pieces stay distinguishable), saves the .blend and
# runs the separating-axis overlap check on every pair of members.
#
# Usage:
#   blender --background --python tools/render_views.py -- <experiment.py> <out_prefix>
#          [--lib <dir>]... [--views <views.py>] [--only 01,03] [--tol 1.0] [--no-check]
#
#   <experiment.py>  script to execute (tools/ and its own folder are put on sys.path)
#   <out_prefix>     absolute path prefix: <prefix>_view_01.png ..., <prefix>.blend
#                    (Blender resolves relative paths against its own cwd)
#   --lib <dir>      extra sys.path entries (an experiment's input/ folder, a base script)
#   --views <file>   Python file defining VIEWS (and optionally COLORS, RESOLUTION);
#                    it is exec'd with `M` = the experiment's namespace and `Vector`
#                    in scope, so views can use model constants (M["z_floor"](3))
#   --only 01,03     render only the named views
#
# View spec (a list of dicts):
#   dict(name="01", azim=235, elev=25,       # camera direction in degrees:
#                                             # azim 0 = camera on +X, 90 = on +Y,
#                                             # 270 = camera south of the building looking north
#        hide=["Facade", "Roof"],            # collections (and their children) hidden
#        focus=(Vector((x, y, z)), radius),  # optional close-up
#        cut=("z", 4.3))                     # optional section: the camera near-clip plane
#                                             # is put on that world plane. True sections
#                                             # only at elev 0 (vertical) or +-89.9 (plan).
# Default: four orbit views at 30 deg elevation.
#
# COLORS maps collection names to (r, g, b, a) object colours; children
# inherit their parent's colour unless listed themselves.
#
# Provenance: the render_fable.py harnesses of the Fable runs (experiments
# 01-13); exp 09's version (colours, hide lists, focus, section cuts, SAT
# check) is the superset generalized here.

import bpy
import sys
import os
import math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
experiment_path, out_prefix = argv[0], argv[1]
lib_dirs, views_file, only_views, tol_mm, do_check = [], None, None, 1.0, True
i = 2
while i < len(argv):
    flag = argv[i]
    if flag == "--lib":
        lib_dirs.append(argv[i + 1]); i += 2
    elif flag == "--views":
        views_file = argv[i + 1]; i += 2
    elif flag == "--only":
        only_views = set(argv[i + 1].split(",")); i += 2
    elif flag == "--tol":
        tol_mm = float(argv[i + 1]); i += 2
    elif flag == "--no-check":
        do_check = False; i += 1
    else:
        raise SystemExit(f"unknown argument {flag}")

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
for d in [TOOLS_DIR, os.path.dirname(os.path.abspath(experiment_path))] + lib_dirs:
    if d not in sys.path:
        sys.path.insert(0, d)

bpy.ops.wm.read_factory_settings(use_empty=True)
model = {"__name__": "__main__", "__file__": os.path.abspath(experiment_path)}
with open(experiment_path, encoding="utf-8") as f:
    exec(compile(f.read(), experiment_path, "exec"), model)

scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == "MESH"]
if not meshes:
    print("No mesh objects generated, aborting render.")
    sys.exit(1)


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, max((hi - lo).length / 2, 0.001)


full_center, full_radius = bounds(meshes)

# --- Views and colours -------------------------------------------------------
VIEWS = [dict(name=f"{k:02d}", azim=a, elev=30, hide=[]) for k, a in enumerate((45, 135, 225, 315), 1)]
COLORS = {}
RESOLUTION = (1600, 1200)
if views_file:
    spec = {"M": model, "Vector": Vector, "VIEWS": VIEWS, "COLORS": COLORS, "RESOLUTION": RESOLUTION}
    with open(views_file, encoding="utf-8") as f:
        exec(compile(f.read(), views_file, "exec"), spec)
    VIEWS, COLORS, RESOLUTION = spec["VIEWS"], spec["COLORS"], spec["RESOLUTION"]


def all_collections(coll):
    yield coll
    for c in coll.children:
        yield from all_collections(c)


def colorize(coll, color):
    color = COLORS.get(coll.name, color)
    for o in coll.objects:
        o.color = color
    for c in coll.children:
        colorize(c, color)


for c in scene.collection.children:
    colorize(c, (0.7, 0.7, 0.7, 1.0))
for o in scene.collection.objects:            # objects left in the root collection
    o.color = COLORS.get("", (0.7, 0.7, 0.7, 1.0))


def hidden_objects(hide):
    out = set()
    for coll in all_collections(scene.collection):
        if coll.name in hide:
            for c in all_collections(coll):
                out.update(c.objects)
    return out


# --- Render settings ---------------------------------------------------------
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "OBJECT"
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_object_outline = True
sh.object_outline_color = (0.0, 0.0, 0.0)
sh.show_shadows = False
scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
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

for view in VIEWS:
    if only_views and view["name"] not in only_views:
        continue
    hide = view.get("hide", [])
    for coll in all_collections(scene.collection):
        coll.hide_render = coll.name in hide

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

    hidden = hidden_objects(hide)
    visible = [o for o in meshes if o not in hidden] or meshes
    if "focus" in view:
        cam_data.ortho_scale = 2 * radius * 1.05 / aspect
    else:
        # fit the projected bounding box of everything visible in this view
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
os.makedirs(os.path.dirname(os.path.abspath(out_prefix)), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=f"{out_prefix}.blend")

if do_check:
    from check_overlaps import find_overlaps, report
    tol = tol_mm / 1000.0
    report(find_overlaps(meshes, tol), len(meshes), tol, limit=80)
print("DONE")
