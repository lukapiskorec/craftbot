# Headless CraftBot runner: executes an experiment script in background Blender
# and renders orbit views of the result with the Workbench engine.
#
# Usage:
#   blender --background --python run_experiment_headless.py -- <experiment.py> <lib_dir> [out_dir]
#
# If out_dir is omitted, renders go to <repo_root>/outputs/<experiment_name>/.

import bpy
import sys
import os
import math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
experiment_path, lib_dir = argv[0], argv[1]
if len(argv) > 2:
    out_dir = argv[2]
else:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    experiment_name = os.path.splitext(os.path.basename(experiment_path))[0]
    out_dir = os.path.join(repo_root, "outputs", experiment_name)

os.makedirs(out_dir, exist_ok=True)
sys.path.insert(0, lib_dir)

# Start from an empty scene (factory startup has default cube/camera/light)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Run the experiment script as __main__
exec(compile(open(experiment_path).read(), experiment_path, "exec"), {"__name__": "__main__"})

# --- Frame the generated geometry ---
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    print("No mesh objects generated, aborting render.")
    sys.exit(1)

pts = []
for o in meshes:
    for c in o.bound_box:
        pts.append(o.matrix_world @ Vector(c))
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
center = (lo + hi) / 2
# Bounding sphere radius: guarantees the whole model fits from any view direction
radius = max((hi - lo).length / 2, 0.001)

# --- Render settings: Workbench = fast, looks like the solid viewport ---
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "OBJECT"
scene.display.shading.show_cavity = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("World")
scene.world.color = (1.0, 1.0, 1.0)

# --- Camera: orthographic (parallel) view, sized to fit the bounding sphere ---
cam_data = bpy.data.cameras.new("HeadlessCam")
cam_data.type = "ORTHO"
FIT_MARGIN = 1.05
# With sensor_fit AUTO, ortho_scale spans the larger resolution dimension;
# divide by the aspect ratio so the smaller dimension also covers the sphere.
aspect = min(scene.render.resolution_x, scene.render.resolution_y) / \
         max(scene.render.resolution_x, scene.render.resolution_y)
cam_data.ortho_scale = 2 * radius * FIT_MARGIN / aspect
cam_data.clip_start = 0.01
cam_data.clip_end = radius * 20
cam = bpy.data.objects.new("HeadlessCam", cam_data)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam

dist = radius * 4.0
elev = math.radians(30)
for i, azim_deg in enumerate((45, 135, 225, 315), start=1):
    azim = math.radians(azim_deg)
    offset = Vector((
        math.cos(azim) * math.cos(elev),
        math.sin(azim) * math.cos(elev),
        math.sin(elev),
    )) * dist
    cam.location = center + offset
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(out_dir, f"view_{i}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {scene.render.filepath}")

# Save the .blend so the model itself is preserved too
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "model.blend"))
print("DONE")
