# Headless CraftBot model exporter: executes an experiment script in
# background Blender and writes the resulting geometry as a compact
# craftbot-model JSON (see docs/superpowers/specs/2026-08-23-webgl-viewer-design.md).
#
# Usage:
#   blender --background --python tools/export_model_json.py -- <experiment.py> <lib_dir> <out.json>
#
# On success prints:  EXPORT OK <n_boxes> <n_meshes> <bytes>

import bpy
import sys
import os

argv = sys.argv[sys.argv.index("--") + 1:]
experiment_path, lib_dir, out_path = argv[0], argv[1], argv[2]

tools_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tools_dir)
sys.path.insert(0, lib_dir)
import model_export_core as core

os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

# Start from an empty scene (factory startup has default cube/camera/light)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Run the experiment script as __main__ (same pattern as run_experiment_headless.py)
exec(compile(open(experiment_path).read(), experiment_path, "exec"),
     {"__name__": "__main__"})


def collection_path(obj):
    """'Parent/Child' path of the first non-scene-root collection, or ''. """
    colls = [c for c in obj.users_collection
             if c is not bpy.context.scene.collection]
    if not colls:
        return ""
    coll = colls[0]
    # Build child -> parent map (bpy collections do not store their parent)
    parent_of = {}
    for c in bpy.data.collections:
        for child in c.children:
            parent_of[child.name] = c
    parts = [coll.name]
    seen = {coll.name}
    while parts[0] in parent_of:
        p = parent_of[parts[0]]
        if p.name in seen:
            break
        parts.insert(0, p.name)
        seen.add(p.name)
    return "/".join(parts)


records = []
skipped = 0
mesh_objects = sorted(
    [o for o in bpy.data.objects if o.type == "MESH"],
    key=lambda o: o.session_uid,  # creation order = construction sequence
)
for obj in mesh_objects:
    mesh = obj.data
    if len(mesh.polygons) == 0:
        print(f"WARNING: skipping {obj.name}: no faces")
        skipped += 1
        continue
    verts = [tuple(v.co) for v in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons]
    coll = collection_path(obj)
    if core.is_unit_cube(verts, faces):
        mw = obj.matrix_world
        matrix = list(mw[0][:]) + list(mw[1][:]) + list(mw[2][:])
        records.append({"name": obj.name, "collection": coll,
                        "kind": "box", "matrix": matrix})
    else:
        world_verts = []
        for v in mesh.vertices:
            co = obj.matrix_world @ v.co
            world_verts.extend((co.x, co.y, co.z))
        records.append({"name": obj.name, "collection": coll, "kind": "mesh",
                        "verts": world_verts, "faces": [list(f) for f in faces]})

if not records:
    print("EXPORT FAIL: no mesh objects generated")
    sys.exit(1)

repo_root = os.path.dirname(tools_dir)
try:
    source = os.path.relpath(experiment_path, repo_root).replace("\\", "/")
except ValueError:  # different drive
    source = os.path.basename(experiment_path)

model = core.build_model_dict(source, records)
n_bytes = core.dump_compact(model, out_path)
n_boxes = len(model["boxes"])
n_meshes = len(model["meshes"])
print(f"EXPORT OK {n_boxes} {n_meshes} {n_bytes}")
