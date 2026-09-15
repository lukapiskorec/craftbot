"""Full-face bearing checks for explicit horizontal convex member/support faces.

Unlike check_contacts, this checks a required footprint on a specified seat,
not proximity to any member. check_bearing() takes ordered world-space XYZ
polygons and runs without Blender. check_pairs() extracts explicit mesh face
indices from a Blender scene. Sloping, concave and degenerate faces are rejected.
No load capacity, anchorage, whole-building load path or automatic seat selection
is inferred. Check each adjacent interface in a bearing stack separately.

    blender --background model.blend --python-exit-code 1 \
        --python tools/check_bearing.py -- bearings.json [--tol-mm 0.001]

JSON: {"bearings": [{"member": "Post", "member_face": 0,
                     "support": "Sole", "support_face": 1}]}
Indices refer to mesh polygons, not vertices. Each selected member face is the
full required footprint; do not select an entire beam underside when only an
end seat is required. Subdivide that face or use check_bearing() on the explicitly
specified required polygon. Apply modifiers before checking scene faces.

Provenance: experiment 16 GPT-6 v02's foot assertion caught up to 0.753 mm
unsupported at each edge despite zero overlaps and zero floating members.
"""
import argparse
import json
import math
import sys

from geometry2d import area, clip, signed_area


def _horizontal_face(points, tol):
    points = [tuple(p) for p in points]
    if len(points) < 3 or any(len(p) != 3 or not all(math.isfinite(v) for v in p) for p in points):
        raise ValueError("a face needs at least three finite XYZ vertices")
    heights = [p[2] for p in points]
    if max(heights) - min(heights) > tol:
        raise ValueError("only horizontal planar faces are supported")
    poly = [(p[0], p[1]) for p in points]
    if area(poly) <= tol*tol:
        raise ValueError("degenerate bearing face")
    if signed_area(poly) < 0:
        poly.reverse()
    edges = []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        if length <= tol:
            raise ValueError("duplicate or degenerate face edge")
        inward = (-dy/length, dx/length)
        if any((v[0]-p[0])*inward[0] + (v[1]-p[1])*inward[1] < -tol for v in poly):
            raise ValueError("faces must be convex with vertices in boundary order")
        edges.append((p, inward))
    return poly, sum(heights)/len(heights), edges


def check_bearing(foot, seat, tol=1e-6):
    """Check full containment and coplanarity of ordered horizontal convex XYZ faces, returning a metric report in metres and square metres.

    tol is numerical face/contact precision, not permission for a shorter seat.
    gap is foot height minus seat height (negative means penetration).
    max_edge_overhang is the largest outward distance across any seat edge's
    supporting line, not the Euclidean distance to a polygon corner.
    supported_area and coverage are zero when the faces are not coplanar within
    tol; otherwise they measure the XY intersection of the actual polygons.
    Invalid or unsupported geometry raises ValueError rather than passing.
    """
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be a finite positive number")
    footprint, foot_z, _ = _horizontal_face(foot, tol)
    _, seat_z, edges = _horizontal_face(seat, tol)
    intersection = footprint
    overhang = 0.0
    for point, normal in edges:
        overhang = max(overhang, max(-((v[0]-point[0])*normal[0] +
                                     (v[1]-point[1])*normal[1]) for v in footprint))
        intersection = clip(intersection, point, normal)
    gap = foot_z - seat_z
    required_area = area(footprint)
    supported_area = min(required_area, area(intersection)) if abs(gap) <= tol else 0.0
    return dict(ok=abs(gap) <= tol and overhang <= tol, gap=gap,
                required_area=required_area, supported_area=supported_area,
                coverage=supported_area/required_area, max_edge_overhang=overhang)


def _mesh_face(objects, name, index, downward):
    obj = objects.get(name)
    if obj is None or obj.type != "MESH":
        raise ValueError(f"mesh object not found: {name}")
    if any(m.show_viewport for m in obj.modifiers):
        raise ValueError(f"apply modifiers before checking {name}")
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(obj.data.polygons):
        raise ValueError(f"invalid face index for {name}: {index}")
    face = obj.data.polygons[index]
    normal = obj.matrix_world.to_3x3().inverted().transposed() @ face.normal
    if (downward and normal.z >= 0) or (not downward and normal.z <= 0):
        raise ValueError(f"{name}: expected a {'downward' if downward else 'upward'} bearing face")
    return [tuple(obj.matrix_world @ obj.data.vertices[i].co) for i in face.vertices]


def check_pairs(pairs, objects=None, tol=1e-6):
    """Check explicit Blender member/support face pairs, returning named reports with failures for missing or unsupported geometry.

    Each dict requires member, member_face, support and support_face. No object
    naming convention or nearest-support inference is used. objects defaults to
    bpy.data.objects; member faces must point down and support faces up.
    """
    if objects is None:
        import bpy
        objects = bpy.data.objects
    reports = []
    for pair in pairs:
        report = dict(pair)
        try:
            if pair["member"] == pair["support"]:
                raise ValueError("a member cannot be its own support")
            foot = _mesh_face(objects, pair["member"], pair["member_face"], True)
            seat = _mesh_face(objects, pair["support"], pair["support_face"], False)
            report.update(check_bearing(foot, seat, tol))
        except (KeyError, ValueError, TypeError) as exc:
            report.update(ok=False, error=str(exc))
        reports.append(report)
    return reports


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="JSON object with a nonempty bearings list")
    parser.add_argument("--tol-mm", type=float, default=0.001)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else None)
    try:
        with open(args.manifest, encoding="utf-8") as handle:
            pairs = json.load(handle)["bearings"]
        if not isinstance(pairs, list) or not pairs or not all(isinstance(p, dict) for p in pairs):
            raise ValueError("bearings must be a nonempty list of pair objects")
        if not math.isfinite(args.tol_mm) or args.tol_mm <= 0:
            raise ValueError("--tol-mm must be finite and positive")
        reports = check_pairs(pairs, tol=args.tol_mm/1000)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    failures = sum(not r["ok"] for r in reports)
    print(f"BEARING CHECK: {len(reports)} explicit pairs, {failures} failed")
    for report in reports:
        if not report["ok"]:
            print(json.dumps(report, sort_keys=True))
    if failures:
        raise RuntimeError(f"{failures} bearing checks failed")


if __name__ == "__main__":
    _main()
