# Headless render harness for CraftBot experiments: runs an experiment
# script in background Blender, renders Workbench views with object
# outlines on (coplanar pieces stay distinguishable), saves the .blend and
# runs the separating-axis overlap check on every pair of members, prints
# the pair families (tools/triage.py) and the contact check (members that
# touch nothing, tools/check_contacts.py).
#
# Usage:
#   blender --background --python tools/render_views.py -- <experiment.py> <out_prefix>
#          [--lib <dir>]... [--views <views.py>] [--only 01,03] [--tol 1.0] [--no-check]
#          [--style workbench|cycles] [--samples 128] [--resolution 3072x3072]
#          [--isolate CollectionA,CollectionB]
# Cycles uses tools/cycles_style.py and CYCLES settings in the views file;
# selected views use the requested foundation state and get a settings JSON record.
#
#   <experiment.py>  script to execute (tools/ and its own folder are put on sys.path)
#   <out_prefix>     absolute path prefix: <prefix>_view_01.png ..., <prefix>.blend,
#                    <prefix>_pairs.txt (every penetrating pair, for triage)
#                    (Blender resolves relative paths against its own cwd)
#   --lib <dir>      extra sys.path entries (an experiment's input/ folder, a base script)
#   --views <file>   Python file defining VIEWS (and optionally COLORS, RESOLUTION);
#                    it is exec'd with `M` = the experiment's namespace and `Vector`
#                    in scope, so views can use model constants (M["z_floor"](3))
#   --only 01,03     render only the named views
#   --isolate A,B    render and frame only these collections and descendants
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
import json
import time
import argparse
import re
from mathutils import Vector

parser = argparse.ArgumentParser(description="Render a model .py or .blend; CLI options override the views file.")
parser.add_argument("model")
parser.add_argument("out_prefix")
parser.add_argument("--lib", action="append", default=[])
parser.add_argument("--views")
parser.add_argument("--only", help="Comma-separated base view names")
parser.add_argument("--tol", type=float, default=1.0)
parser.add_argument("--no-check", action="store_true")
parser.add_argument("--style", choices=["workbench", "cycles"], default="workbench")
parser.add_argument("--workbench-line-mask", action="store_true",
                    help="Flat white opaque surfaces with thin black object outlines for compositing")
parser.add_argument("--resolution", help="WIDTHxHEIGHT, e.g. 3072x3072")
parser.add_argument("--samples", type=int)
parser.add_argument("--palettes", help="Comma-separated: white,muted,washed,weathered")
parser.add_argument("--edges", choices=["none", "bevel", "both"], help="Render-time bevels reveal coplanar seams; both makes paired variants")
parser.add_argument("--edge-width", type=float, help="Bevel width in model units (meters in CraftBot), default .010")
parser.add_argument("--edge-darkness", type=float, help="Edge color multiplier, 0=black and 1=base color; default .22")
parser.add_argument("--edge-light-response", type=float, help="0=constant unlit edge, 1=fully lit edge; default 0.30")
parser.add_argument("--fill-strength", type=float, help="Neutral indirect environment fill; default .25, 0 reproduces dark undersides")
parser.add_argument("--glass-roughness", type=float, help="Default .015")
parser.add_argument("--glass-transmission", type=float, help="Default 1")
parser.add_argument("--glass-ior", type=float, help="Default 1.45")
parser.add_argument("--sun-rotation", type=float, help="Nishita rotation in degrees")
parser.add_argument("--sun-elevation", type=float, help="Sun elevation in degrees")
parser.add_argument("--sun-size", type=float, help="Sun diameter in degrees")
parser.add_argument("--sun-intensity", type=float)
parser.add_argument("--world-strength", type=float)
parser.add_argument("--exposure", type=float)
parser.add_argument("--noise-threshold", type=float)
parser.add_argument("--azimuth", type=float, help="Camera azimuth in degrees")
parser.add_argument("--elevation", type=float, help="Camera elevation; negative looks up from below")
parser.add_argument("--margin", type=float, help="Camera framing multiplier, default 1.16 for Cycles")
parser.add_argument("--hide", help="Comma-separated collection names to hide, including descendants")
parser.add_argument("--isolate", help="Comma-separated collection names to render exclusively, including descendants")
parser.add_argument("--foundation-collections", help="Comma-separated names; auto-detected if omitted")
parser.add_argument("--foundation", choices=["both", "hide", "show"], help="Default hide for Cycles; overrides a views-file preset when supplied")
parser.add_argument("--material-role", action="append", default=[], metavar="COLLECTION=ROLE",
                    help="Override automatic role: timber,cladding,concrete,metal,glass")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
experiment_path, out_prefix = args.model, os.path.abspath(args.out_prefix)
lib_dirs, views_file = args.lib, args.views
only_views = set(args.only.split(",")) if args.only else None
tol_mm, do_check, style = args.tol, not args.no_check, args.style
resolution = tuple(map(int, args.resolution.lower().split("x"))) if args.resolution else None
if resolution and (len(resolution) != 2 or min(resolution) <= 0):
    parser.error("--resolution must be positive WIDTHxHEIGHT")

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
for d in [TOOLS_DIR, os.path.dirname(os.path.abspath(experiment_path))] + lib_dirs:
    if d not in sys.path:
        sys.path.insert(0, d)

bpy.ops.wm.read_factory_settings(use_empty=True)
model = {"__name__": "__main__", "__file__": os.path.abspath(experiment_path)}
if experiment_path.lower().endswith(".blend"):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(experiment_path))
else:
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
CYCLES = {}
if views_file:
    spec = {"M": model, "Vector": Vector, "ARGS": args,
            "VIEWS": VIEWS, "COLORS": COLORS, "RESOLUTION": RESOLUTION}
    with open(views_file, encoding="utf-8") as f:
        exec(compile(f.read(), views_file, "exec"), spec)
    VIEWS, COLORS, RESOLUTION = spec["VIEWS"], spec["COLORS"], spec["RESOLUTION"]
    CYCLES = spec.get("CYCLES", {})
if style == "cycles":
    import cycles_style
    if not views_file:
        RESOLUTION = (3072, 3072)
        VIEWS = [dict(cycles_style.DEFAULT_VIEW, name="main", hide=[])]
    CYCLES = cycles_style.cli_settings(args, CYCLES)
    VIEWS = cycles_style.cli_views(args, VIEWS)
elif args.workbench_line_mask:
    if not views_file:
        import cycles_style
        RESOLUTION = (3072, 3072)
        VIEWS = [dict(cycles_style.DEFAULT_VIEW, name="main", hide=[])]
    adjusted = []
    for source_view in VIEWS:
        view = dict(source_view)
        for flag, key in (("azimuth", "azim"), ("elevation", "elev"), ("margin", "margin")):
            value = getattr(args, flag)
            if value is not None:
                view[key] = value
        if args.hide:
            view["hide"] = list(dict.fromkeys(view.get("hide", []) + args.hide.split(",")))
        if args.foundation == "hide":
            foundations = (args.foundation_collections.split(",") if args.foundation_collections else
                           [c.name for c in bpy.data.collections
                            if re.search(r"foundation|footing|plinth|podium", c.name, re.I)])
            base_hide = [name for name in view.get("hide", []) if name not in foundations]
            view["fit_hide"] = base_hide
            view["hide"] = base_hide + foundations
        adjusted.append(view)
    VIEWS = adjusted
if resolution:
    RESOLUTION = resolution
os.makedirs(os.path.dirname(os.path.abspath(out_prefix)), exist_ok=True)


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


if args.isolate:
    isolate_names = args.isolate.split(",")
    missing = [name for name in isolate_names if bpy.data.collections.get(name) is None]
    if missing:
        raise ValueError(f"Missing isolate collections: {missing}")
    isolated = set()
    for name in isolate_names:
        isolated.update(bpy.data.collections[name].all_objects)
    isolate_hidden = [obj.name for obj in meshes if obj not in isolated]
    for view in VIEWS:
        view["hide_objects"] = list(dict.fromkeys(view.get("hide_objects", []) + isolate_hidden))
        view["fit_hide_objects"] = list(dict.fromkeys(view.get("fit_hide_objects", []) + isolate_hidden))


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
if args.workbench_line_mask:
    sh.light = "FLAT"
    sh.color_type = "SINGLE"
    sh.single_color = (1.0, 1.0, 1.0)
    sh.show_cavity = False
    sh.show_specular_highlight = False
    sh.background_type = "VIEWPORT"
    sh.background_color = (1.0, 1.0, 1.0)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
scene.world = bpy.data.worlds.new("World")
scene.world.color = (1.0, 1.0, 1.0)
render_records = []
if style == "cycles":
    import cycles_style
    cycles_style.setup(scene, CYCLES)
    # --only selects a base view and always includes its foundation-free partner.
    VIEWS = cycles_style.paired_views(VIEWS, only_views, CYCLES)
    only_views = None

cam_data = bpy.data.cameras.new("HeadlessCam")
cam_data.type = "ORTHO"
cam_data.clip_start = 0.01
cam_data.clip_end = full_radius * 40
cam = bpy.data.objects.new("HeadlessCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
base_matrices = {obj.name: obj.matrix_world.copy() for obj in meshes}
base_object_visibility = {obj.name: obj.hide_render for obj in meshes}

aspect = scene.render.resolution_y / scene.render.resolution_x

for view in VIEWS:
    if only_views and view["name"] not in only_views:
        continue
    hide = view.get("hide", [])
    for obj in meshes:
        obj.matrix_world = base_matrices[obj.name].copy()
        obj.hide_render = base_object_visibility[obj.name]
    if style == "cycles":
        cycles_style.apply_view(scene, meshes, view, CYCLES)
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

    # Keep exactly the same framing in each foundation on/off comparison.
    hidden = hidden_objects(view.get("fit_hide", hide))
    hidden.update(bpy.data.objects[name] for name in view.get("fit_hide_objects", [])
                  if bpy.data.objects.get(name))
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
        cam_data.ortho_scale = max(w, h / aspect) * max(1, aspect) * view.get("margin", 1.05)
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

    for name in view.get("hide_objects", []):
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError(f"Missing object in hide_objects: {name}")
        obj.hide_render = True
    for name, delta in view.get("move_objects", []):
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError(f"Missing object in move_objects: {name}")
        obj.matrix_world.translation += Vector(delta)

    scene.render.filepath = f"{out_prefix}_view_{view['name']}.png"
    started = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {scene.render.filepath}")
    if style == "cycles":
        render_records.append(cycles_style.record(scene, meshes, view, time.perf_counter() - started, CYCLES))
        with open(f"{out_prefix}_settings.json", "w", encoding="utf-8") as f:
            json.dump(dict(experiment=os.path.abspath(experiment_path), blender=bpy.app.version_string,
                           settings=CYCLES, renders=render_records), f, indent=2)

for coll in all_collections(scene.collection):
    coll.hide_render = False
for obj in meshes:
    obj.matrix_world = base_matrices[obj.name].copy()
    obj.hide_render = base_object_visibility[obj.name]
cam_data.clip_start = 0.01
os.makedirs(os.path.dirname(os.path.abspath(out_prefix)), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=f"{out_prefix}.blend")

if do_check:
    from check_overlaps import find_overlaps, report
    from check_contacts import find_floating, report_floating
    from triage import families, format_families
    tol = tol_mm / 1000.0
    hits = find_overlaps(meshes, tol)
    report(hits, len(meshes), tol, limit=80)
    # every pair, for the Builder's triage, and the family table (one row per cause)
    with open(f"{out_prefix}_pairs.txt", "w", encoding="utf-8") as f:
        f.write(f"{len(meshes)} members, {len(hits)} pairs (> {tol_mm:.0f} mm)\n")
        for p, a, b in hits:
            f.write(f"{p * 1000:8.1f} mm  {a}  x  {b}\n")
    print(format_families(families(hits)))
    # contact check: members that touch nothing (the overlap check cannot see them)
    report_floating(find_floating(meshes, 0.002), len(meshes), 0.002, limit=80)
print("DONE")
