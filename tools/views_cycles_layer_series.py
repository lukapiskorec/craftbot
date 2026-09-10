"""Four matched presentation views using the web viewer's layer classifier."""

from collections import Counter

import bpy

import layers
from presentation_facades import facade_for, facade_hint
from views_cycles_study import CYCLES as BASE


RESOLUTION = (3072, 3072)
CYCLES = dict(BASE, edges="none", foundation="hide", fill_strength=.25,
              glass_roughness=.015, glass_transmission=1., glass_ior=1.45)
CYCLES["foundation_collections"] = []


def collection_path(obj):
    """Match export_model_json.py so layers.py sees the same classification input."""
    collections = [c for c in obj.users_collection if c is not bpy.context.scene.collection]
    if not collections:
        return ""
    collection = collections[0]
    parent_of = {}
    for parent in bpy.data.collections:
        for child in parent.children:
            parent_of[child.name] = parent
    parts = [collection.name]
    seen = {collection.name}
    while parts[0] in parent_of:
        parent = parent_of[parts[0]]
        if parent.name in seen:
            break
        parts.insert(0, parent.name)
        seen.add(parent.name)
    return "/".join(parts)


objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
active_objects = set(objects)
if ARGS.isolate:
    active_objects = set()
    for collection_name in ARGS.isolate.split(","):
        collection = bpy.data.collections.get(collection_name)
        if collection:
            active_objects.update(obj for obj in collection.all_objects if obj.type == "MESH")
    if not active_objects:
        raise ValueError(f"No mesh objects found in isolate collections: {ARGS.isolate}")
experiment_id = layers.experiment_of(M["__file__"])
records = []
for obj in objects:
    path = collection_path(obj)
    records.append(dict(obj=obj, collection=path,
                        layer=layers.classify(experiment_id, path, obj.name)))

active_records = [record for record in records if record["obj"] in active_objects]
model_records = [record for record in active_records if record["layer"] != layers.FOUND] or active_records
points = [record["obj"].matrix_world @ Vector(corner)
          for record in model_records for corner in record["obj"].bound_box]
bounds_xy = (min(point.x for point in points), max(point.x for point in points),
             min(point.y for point in points), max(point.y for point in points))

facade_counts = Counter()
hint_counts = Counter()
for record in active_records:
    if record["layer"] not in (layers.CLAD_EXT, layers.CLAD_INT):
        continue
    obj = record["obj"]
    center = obj.matrix_world @ (sum((Vector(corner) for corner in obj.bound_box), Vector()) / 8)
    text = f'{record["collection"]}|{obj.name}'
    hinted = facade_hint(text)
    record["facade"] = facade_for(text, (center.x, center.y), bounds_xy)
    facade_counts[record["facade"]] += 1
    hint_counts["named" if hinted else "position"] += 1

foundations = [record["obj"].name for record in active_records if record["layer"] == layers.FOUND]
south_east = [record["obj"].name for record in active_records
              if record.get("facade") in ("south", "east")]
south_west = [record["obj"].name for record in active_records
              if record.get("facade") in ("south", "west")]
show_foundation = ARGS.foundation == "show"
base_foundations = [] if show_foundation else foundations
frame_layers = (layers.FRAME, layers.FOUND) if show_foundation else (layers.FRAME,)
not_frame = [record["obj"].name for record in active_records if record["layer"] not in frame_layers]

above = bool(globals().get("PRESENTATION_ABOVE", False))
if above:
    CYCLES["camera_background_srgb"] = (.57647, .66275, .75686)
common = dict(palette="washed", azim=305, elev=25 if above else -25, margin=1.16,
              sun_rotation=-160, sun_elevation=45, fit_hide=[])
if above:
    roofs = [record["obj"].name for record in active_records if record["layer"] == layers.ROOF]
    VIEWS = [
        dict(common, name="01_roof_on_full", hide_objects=base_foundations),
        dict(common, name="02a_roof_on_open_south_east",
             hide_objects=list(dict.fromkeys(base_foundations + south_east))),
        dict(common, name="02b_roof_on_open_south_west",
             hide_objects=list(dict.fromkeys(base_foundations + south_west))),
        dict(common, name="03_roof_off_full",
             hide_objects=list(dict.fromkeys(base_foundations + roofs))),
        dict(common, name="04a_roof_off_open_south_east",
             hide_objects=list(dict.fromkeys(base_foundations + roofs + south_east))),
        dict(common, name="04b_roof_off_open_south_west",
             hide_objects=list(dict.fromkeys(base_foundations + roofs + south_west))),
        dict(common, name="05_exposed_frame", hide_objects=not_frame),
    ]
else:
    VIEWS = [
        dict(common, name="01_full", hide_objects=base_foundations),
        dict(common, name="02a_open_south_east",
             hide_objects=list(dict.fromkeys(base_foundations + south_east))),
        dict(common, name="02b_open_south_west",
             hide_objects=list(dict.fromkeys(base_foundations + south_west))),
        dict(common, name="03_exposed_frame", hide_objects=not_frame),
    ]

layer_counts = Counter(record["layer"] for record in active_records)
print("LAYER_SERIES", experiment_id,
      "mode=" + ("above" if above else "below"),
      "foundation=" + ("show" if show_foundation else "hide"),
      "active=" + str(len(active_records)),
      "layers=" + ",".join(f"{name}:{layer_counts[name]}" for name in layers.LAYERS),
      "facades=" + ",".join(f"{name}:{facade_counts[name]}" for name in ("south", "east", "west", "north")),
      "facade_source=" + ",".join(f"{name}:{hint_counts[name]}" for name in ("named", "position")),
      flush=True)
