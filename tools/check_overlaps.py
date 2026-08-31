"""Standalone interpenetration check for generated models.

Runs the separating-axis (SAT) overlap test used by the Fable experiment
harnesses over every pair of mesh objects in the scene: face normals plus
edge-direction cross products as candidate axes, with an AABB broad phase.
Valid for convex meshes (experiment members are boxes or convex prisms);
non-convex meshes can report false positives. Touching faces report zero
and are not listed.

Usage (headless, on a saved model):
    blender --background model.blend --python tools/check_overlaps.py -- [tolerance_mm]

Default tolerance is 1 mm. Can also be appended after any script that
builds the scene in the same Blender session.
"""
import itertools
import sys

import bpy
from mathutils import Vector


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


def main():
    tol_mm = 1.0
    if "--" in sys.argv:
        extra = sys.argv[sys.argv.index("--") + 1:]
        if extra:
            tol_mm = float(extra[0])
    tol = tol_mm / 1000.0

    meshes = [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) >= 4]
    hulls = [(o.name, hull(o)) for o in meshes]
    hits = []
    for (name_a, a), (name_b, b) in itertools.combinations(hulls, 2):
        if any(a[3][i] > b[4][i] - tol or b[3][i] > a[4][i] - tol for i in range(3)):
            continue
        p = penetration(a, b)
        if p > tol:
            hits.append((p, name_a, name_b))
    hits.sort(reverse=True)
    print(f"OVERLAP CHECK: {len(hulls)} members, {len(hits)} penetrating pairs (> {tol_mm:.0f} mm)")
    for p, name_a, name_b in hits:
        print(f"  {p * 1000:6.1f} mm  {name_a}  x  {name_b}")


main()
