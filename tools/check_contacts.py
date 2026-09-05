"""Contact check: every member must touch something.

The overlap check is blind to absence: a tread with nothing under it, a
board nailed to nothing and a stud that stops short of its plate all pass
with zero pairs. This check lists every mesh object that has no other mesh
within `tol` of it (touching faces count as contact, so a joist on a girt
or a board on a rafter is fine).

The test is the separating-axis gap used by check_overlaps: for a pair
whose expanded bounding boxes overlap, the largest separation along the
candidate axes is a lower bound on the true distance; a pair with that
bound <= tol is taken as in contact. Convex members only, like the overlap
check. False "contact" for a pair that is close on every axis but not truly
touching is possible and harmless; a floating member is never hidden.

Usage (headless, on a saved model):
    blender --background model.blend --python tools/check_contacts.py -- [tolerance_mm] [ignore_prefix,...]

or imported after a scene is built:
    from check_contacts import find_floating, report_floating
    names = find_floating(meshes, tol=0.002, ignore=("Ground_Slab",))

Ground and foundation objects are the natural roots; anything that should
stand on the ground touches the slab or a plinth, so nothing needs to be
special-cased except objects that are meant to float (none, normally).

Provenance: proposed in the experiment 14 Fable run context audit after
three phase-3 review items (unsupported treads, 38 x 38 gable sticks,
unbacked boards) turned out to be floating geometry the overlap check
could not see.
"""
import itertools
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, __file__.rsplit("check_contacts.py", 1)[0] or ".")
from check_overlaps import hull


def _gap(a, b):
    """Largest separation along the candidate axes (>= 0 when disjoint;
    a lower bound on the distance), or a negative number when overlapping."""
    va, na, ea, _, _ = a
    vb, nb, eb, _, _ = b
    best = -float("inf")
    for ax in na + nb + [x.cross(y) for x in ea for y in eb]:
        if ax.length < 1e-9:
            continue
        ax = ax.normalized()
        pa = [v.dot(ax) for v in va]
        pb = [v.dot(ax) for v in vb]
        gap = max(min(pa) - max(pb), min(pb) - max(pa))
        if gap > best:
            best = gap
    return best


def find_floating(meshes=None, tol=0.002, ignore=()):
    """Names of mesh objects with no other mesh within `tol`. `ignore`
    lists name prefixes to leave out of the report (not out of the test:
    an ignored object still counts as a support for others)."""
    if meshes is None:
        meshes = [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) >= 4]
    hulls = [(o.name, hull(o)) for o in meshes]
    touched = {name: False for name, _ in hulls}
    for (name_a, a), (name_b, b) in itertools.combinations(hulls, 2):
        if touched[name_a] and touched[name_b]:
            continue
        if any(a[3][i] > b[4][i] + tol or b[3][i] > a[4][i] + tol for i in range(3)):
            continue
        if _gap(a, b) <= tol:
            touched[name_a] = touched[name_b] = True
    return [n for n, t in touched.items() if not t and not any(n.startswith(p) for p in ignore)]


def report_floating(names, n_members, tol=0.002, limit=None):
    print(f"CONTACT CHECK: {n_members} members, {len(names)} floating (nothing within {tol * 1000:.0f} mm)")
    for n in (names if limit is None else names[:limit]):
        print(f"  floating  {n}")
    if limit is not None and len(names) > limit:
        print(f"  ... {len(names) - limit} more")


def main():
    tol_mm, ignore = 2.0, ()
    if "--" in sys.argv:
        extra = sys.argv[sys.argv.index("--") + 1:]
        if extra:
            tol_mm = float(extra[0])
        if len(extra) > 1:
            ignore = tuple(extra[1].split(","))
    tol = tol_mm / 1000.0
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) >= 4]
    report_floating(find_floating(meshes, tol, ignore), len(meshes), tol)


if __name__ == "__main__":
    main()
