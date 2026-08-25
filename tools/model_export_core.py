# ------------------------------------------------------------------
# CRAFT BOT - model export core (pure Python, no bpy)
#
# Shared by the Blender-side exporter (tools/export_model_json.py) and
# the batch driver (tools/export_all_models.py). Unit-tested without
# Blender in tools/tests/test_model_export_core.py.
# ------------------------------------------------------------------

import json
import re

# The unit cube emitted by craftbot_lib.place_element (2x2x2, centred at
# origin). Vertex and face order is identical across all lib versions.
UNIT_CUBE_VERTS = [
    (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0),
    (1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0),
]
UNIT_CUBE_FACES = [
    (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
    (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7),
]


def is_unit_cube(verts, faces, eps=1e-6):
    """True if the local-space mesh is exactly the place_element unit cube."""
    if len(verts) != 8 or len(faces) != 6:
        return False
    for v, ref in zip(verts, UNIT_CUBE_VERTS):
        if (abs(v[0] - ref[0]) > eps or abs(v[1] - ref[1]) > eps
                or abs(v[2] - ref[2]) > eps):
            return False
    for f, ref in zip(faces, UNIT_CUBE_FACES):
        if tuple(f) != ref:
            return False
    return True


def signed_volume(verts, faces):
    """Signed volume of a closed polygon mesh (fan-triangulated faces);
    negative means the faces wind inward. verts: flat [x, y, z, ...]."""
    total = 0.0
    for face in faces:
        for i in range(1, len(face) - 1):
            a, b, c = face[0], face[i], face[i + 1]
            ax, ay, az = verts[3 * a], verts[3 * a + 1], verts[3 * a + 2]
            bx, by, bz = verts[3 * b], verts[3 * b + 1], verts[3 * b + 2]
            cx, cy, cz = verts[3 * c], verts[3 * c + 1], verts[3 * c + 2]
            total += (ax * (by * cz - bz * cy)
                      + ay * (bz * cx - bx * cz)
                      + az * (bx * cy - by * cx)) / 6.0
    return total


def orient_outward(verts, faces):
    """Return faces wound so normals point outward. Some generators build
    prisms inside-out (consistent but reversed winding); those render as
    hollow shells in the viewer and shade dark in Blender."""
    if signed_volume(verts, faces) < 0:
        return [list(reversed(f)) for f in faces]
    return [list(f) for f in faces]


def rnd(x, nd=5):
    """Round to nd decimals; collapse to int when integral (smaller JSON)."""
    r = round(x, nd)
    i = int(r)
    return i if r == i else r


def build_model_dict(source, records):
    """
    Build the craftbot-model dict from exporter records.

    records: list of dicts in creation order, each either
      {"name", "collection", "kind": "box", "matrix": [12 floats, row-major 3x4]}
      {"name", "collection", "kind": "mesh", "verts": [x,y,z,...], "faces": [[i,...],...]}
    """
    collections = [""]
    coll_ids = {"": 0}
    boxes = []
    meshes = []
    for rec in records:
        coll = rec.get("collection", "")
        if coll not in coll_ids:
            coll_ids[coll] = len(collections)
            collections.append(coll)
        cid = coll_ids[coll]
        if rec["kind"] == "box":
            boxes.append([rec["name"], cid] + [rnd(x) for x in rec["matrix"]])
        else:
            meshes.append({
                "name": rec["name"],
                "collection": cid,
                "verts": [rnd(x) for x in rec["verts"]],
                "faces": orient_outward(rec["verts"], rec["faces"]),
            })
    return {
        "format": "craftbot-model",
        "version": 1,
        "source": source,
        "collections": collections,
        "boxes": boxes,
        "meshes": meshes,
    }


def dump_compact(d, path):
    """Write dict as compact JSON; return number of bytes written."""
    data = json.dumps(d, separators=(",", ":")).encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def _experiment_title(exp_id):
    """'01_Carport_Assembly_Blender_Python' -> '01 Carport Assembly'."""
    tokens = exp_id.split("_")
    while tokens and tokens[-1] in ("Blender", "Python"):
        tokens.pop()
    return " ".join(tokens)


def build_index(entries):
    """
    Build index.json dict from flat export entries:
      {"experiment", "agent", "v", "file", "elements", "bytes", "rationale"?}
    Experiments sorted by id, agents sorted by name ("ChatGPT 5.1" first),
    versions sorted by version string. A run carries "rationale" (relative
    path of the design rationale markdown) when any of its entries has one.
    """
    by_exp = {}
    for e in entries:
        runs = by_exp.setdefault(e["experiment"], {})
        runs.setdefault(e["agent"], []).append(e)
    experiments = []
    for exp_id in sorted(by_exp):
        runs = []
        for agent in sorted(by_exp[exp_id]):
            versions = sorted(by_exp[exp_id][agent], key=lambda e: e["v"])
            run = {
                "agent": agent,
                "versions": [{"v": e["v"], "file": e["file"],
                              "elements": e["elements"], "bytes": e["bytes"]}
                             for e in versions],
            }
            rationale = next((e["rationale"] for e in versions
                              if e.get("rationale")), None)
            if rationale:
                run["rationale"] = rationale
            runs.append(run)
        experiments.append({
            "id": exp_id,
            "title": _experiment_title(exp_id),
            "runs": runs,
        })
    return {"experiments": experiments}


VERSION_RE = re.compile(r"_v(\d+)\.py$")
