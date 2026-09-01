"""Smoke test of the Blender-dependent tools, run inside Blender:

    blender --background --python tools/tests/blender_smoke.py

Builds a small model that uses every kit (craftbot_lib, planes, ruled,
framing, sheathing), then asserts that the overlap check reports no
penetrating pairs and that each generator produced what it promised.
Fails with a traceback (non-zero exit) on any assertion.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))

import bpy
from mathutils import Vector

import craftbot_lib as craftbot
import geometry2d as g2
import planes
import ruled
import framing
import sheathing
from check_overlaps import find_overlaps, report

bpy.ops.wm.read_factory_settings(use_empty=True)
craftbot.clear_scene()


def n_mesh():
    return len([o for o in bpy.data.objects if o.type == "MESH"])


# --- craftbot_lib: box, prisms, nested collections --------------------------
craftbot.box("Slab", "Site/Foundation", -1, 7, -3, 3, -0.15, 0.0)
craftbot.prism_x("Gable_W", "Walls/Gable", -0.5, -0.4, [(-2, 0), (2, 0), (2, 2), (0, 3.2), (-2, 2)])
craftbot.prism_y("Wedge", "Walls/Gable", 2.0, 2.2, [(0, 0.5), (1, 0.5), (1, 1.0)])   # clockwise input
assert bpy.data.collections["Foundation"].objects.get("Slab") is not None
assert craftbot.box("Degenerate", "Site", 0, 0, 0, 1, 0, 1) is None
wedge = bpy.data.objects["Wedge"]
assert all(p.normal.length > 0.99 for p in wedge.data.polygons)
# outward normals: every face normal points away from the centroid
centre = sum((v.co for v in wedge.data.vertices), Vector()) / len(wedge.data.vertices)
for p in wedge.data.polygons:
    assert (p.center - centre).dot(p.normal) > 0, "prism face points inwards"

# --- planes: member with bearing insets, sloped_member with clips, bar -------
PLATE_TOP = 2.5
craftbot.box("Post_A", "Frame", 0.0, 0.15, -0.075, 0.075, 0.0, PLATE_TOP)
craftbot.box("Post_B", "Frame", 5.85, 6.0, -0.075, 0.075, 0.0, PLATE_TOP)
craftbot.box("Beam", "Frame", 0.0, 6.0, -0.075, 0.075, PLATE_TOP, PLATE_TOP + 0.2)
# knee brace: post face -> beam underside, both ends inset to the bearing planes
planes.member("Brace", "Frame", (0.15, 0.0, PLATE_TOP - 0.8), (0.95, 0.0, PLATE_TOP),
              0.08, 0.12, width_dir=(0, 1, 0), n0=(1, 0, 0), n1=(0, 0, -1))
# rafter pair: build long, clip at the ridge plane and seat on the plate
S = math.tan(math.radians(35))
for side, sgn in (("S", -1), ("N", 1)):
    obj, outline = planes.sloped_member(f"Rafter_{side}", "Roof", (3.0, sgn * 2.5), (0, -sgn), S,
                                        PLATE_TOP + 0.2 + 0.184 / math.cos(math.atan(S)), 0.184, 0.038,
                                        -0.4, 4.0, clips=[planes.vz(PLATE_TOP + 0.2, +1), planes.vy(0.0, sgn)])
    assert obj is not None and len(outline) >= 4
    # clipped on its own side of the ridge plane: s runs from the heel to the ridge (2.5), not beyond
    assert max(s_ for s_, _ in outline) < 2.5 + 1e-4 and min(s_ for s_, _ in outline) > -0.4 - 1e-4, outline
# hip-style member with a cheek cut against a "hip" running diagonally
hip_c, hip_d = (3.0, 0.0), (1, 1)
planes.sloped_member("Hip", "Roof", hip_c, hip_d, S / math.sqrt(2), PLATE_TOP + 0.5, 0.184, 0.038, 0.0, 2.0)
jack, _ = planes.sloped_member("Jack", "Roof", (3.5, -1.0), (0, 1), S, PLATE_TOP + 0.5 + 0.7 * S, 0.184, 0.038,
                               0.0, 3.0, clips=[planes.cheek(hip_c, hip_d, (3.5, -1.0), 0.038)])
assert jack is not None
b, e1, e2, e3, c = planes.bar("Rail", "Frame", (0, 1.0, 1.0), (6, 1.2, 1.3), (0, 0, 1), 0.1, 0.05,
                              ext=(0.1, 0.1), clips=[planes.vx(0.0, +1), planes.vx(6.0, -1)])
assert b is not None and abs(e1.dot(e2)) < 1e-5 and abs(e1.dot(e3)) < 1e-5   # mathutils is float32
mc = planes.mitre_clip((0, 0), (1, 0), (0, 1))
assert abs(mc[1].dot(Vector((1, 1, 0)).normalized())) < 1e-5        # mitre normal is the diagonal
P = planes.isect(planes.vplane("x", 1.0), planes.vplane("y", 2.0), (Vector((0, 0, 1)), 3.0))
assert (P - Vector((1, 2, 3))).length < 1e-5
roof = planes.Roof("R", (0, -1), 2.0, 2.5, 0.5)
assert abs(roof.z(0, -2.0) - 2.5) < 1e-5 and abs(roof.z(0, 0.0) - 3.5) < 1e-5

# --- ruled: leaning wall studs and a board on a twisted surface --------------
Sw = ruled.Ruled((8, 0, 0), (12, 0, 0), (8.3, 0, 2.5), (12.6, 0.2, 2.6), out=(0, -1, 0))
for i, t in enumerate((0.0, 0.5, 1.0)):
    objs, fr, e3 = ruled.ruling_member(f"WStud_{i}", "Wrap", Sw, t, 0.0, 0.1, -0.025, 0.025,
                                       clips=[planes.vz(0.0, +1), planes.vz(2.5, -1)], ext=0.3)
    assert len(objs) == 1
boards = ruled.surface_quad("WBoard", "Wrap", Sw, 0.05, 0.45, 0.2, 0.4, -0.03, -0.01, gap=0.005)
assert len(boards) == 1 and ruled.RESIDUALS[-1][0] < 0.05
assert ruled.surf_extent(Sw, [planes.vz(1.0, +1)], 0.0, samples=10) is not None

# --- framing: stud wall with openings, cladding, deck, boards, wall pieces ---
before = n_mesh()
framing.stud_wall("WallS", "Walls/WallS", "x", 0.0, 6.0, 4.0, 4.1, 0.0, 2.6, t=0.05, spacing=0.6,
                  openings=[(1.0, 2.0, 0.9, 2.1), (4.0, 4.9, None, 2.1)], double_top=True)
assert n_mesh() - before > 20
n = framing.clad("CladS", "Walls/WallS_Clad", "x", 0.0, 6.0, 4.1, 4.12, 0.0, 2.6,
                 holes=[(1.0, 2.0, 0.9, 2.1), (4.0, 4.9, 0.0, 2.1)])
assert n > 6
n = framing.tile_sheets("Deck", "Floors", 20.0, 26.0, -2.5, 2.5, 3.0, 3.02, holes=[(22, 23, -1, 1)])
assert n > 6
n = framing.boards("Board", "Floors", 20.0, 26.0, -2.5, 2.5, 3.02, 3.04, w=0.12, gap=0.005,
                   nogo=[(22, 23, -1, 1)])
assert n > 40
n = framing.wall_along_x("CLT", "Walls/CLT", g2.rect(0, 6, 0, 3), 6.0, 6.1,
                         openings=[(1, 2, 0.9, 2.1), (4, 5, 0, 2.1)])
assert n == 3 + 2 + 1, n            # piers, window sill + lintel, door lintel
zu = lambda y: 3.5 + 0.4 * (2.0 - abs(y))
framing.roof_piece("RoofDeck", "Roof", 20.0, 26.0, -2.0, 2.0, zu, lambda y: zu(y) + 0.02, y_ridge=0.0)
assert bpy.data.objects.get("RoofDeck_s") is not None and bpy.data.objects.get("RoofDeck_n") is not None
framing.flight("Stair", "Stairs", 8.0, +1, 3.0, 4.0, 0.0, 6, going=0.28, riser=0.17, step_d=0.15)
assert bpy.data.objects.get("Stair_05") is not None and bpy.data.objects.get("Stair_06") is None
framing.halved_brace("XBrace", "Frame", (10.0, 5.0, 0.0), (11.0, 5.0, 2.0), 0.1, 0.1, (0, 1, 0),
                     (0, 0, 1), (0, 0, -1), (10.5, 5.0, 1.0), 0.3, +1)
assert bpy.data.objects.get("XBrace_lap") is not None

# --- sheathing: two facets of a gable roof, mitred at the ridge --------------
Z0, W, X0, X1, T = 5.0, 2.0, 12.0, 16.0, 0.6
facets = {}
for side, sgn in (("S", -1), ("N", 1)):
    r = planes.Roof(side, (0, sgn), W, Z0, T)
    facets[side] = sheathing.Facet(side, r.p, (1, 0, 0), r.n, underside=0.092, thick=0.019)
loops = {}
for level, off in (("u", 0.092), ("t", 0.111)):
    pl = {k: facets[k].plane(off) for k in facets}
    for side, sgn in (("S", -1), ("N", 1)):
        eave = planes.vplane("y", sgn * (W + 0.3))
        pts = [planes.isect(pl[side], eave, planes.vplane("x", X0)),
               planes.isect(pl[side], eave, planes.vplane("x", X1)),
               planes.isect(pl[side], pl["S" if side == "N" else "N"], planes.vplane("x", X1)),
               planes.isect(pl[side], pl["S" if side == "N" else "N"], planes.vplane("x", X0))]
        loops[(side, level)] = [[facets[side].uv(p) for p in pts]]
joints = [Vector((x, 0, Z0)) for x in g2.positions(X0, X1, 0.6, 0.038)]
total = 0
for side in ("S", "N"):
    total += sheathing.sheathe_facet(facets[side], loops[(side, "u")], loops[(side, "t")], joints,
                                     "Sheathing", f"Board_{side}")
assert total > 20, total
# a ridge board standing proud gets dropped under the boards
craftbot.box("Ridge", "Roof", X0, X1, -0.025, 0.025, Z0 + T * W - 0.15, Z0 + T * W + 0.15)
dropped = sheathing.drop_member("Ridge", list(facets.values()))
assert dropped > 0.0
regions = [(facets[s], loops[(s, "u")]) for s in facets]
hits = sheathing.report_protrusions(["Ridge"], regions)
assert not hits, hits

# --- overlap check over everything ------------------------------------------
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
overlaps = find_overlaps(meshes, 0.001)
report(overlaps, len(meshes))
assert not overlaps, "penetrating pairs found"
print(f"SMOKE OK: {len(meshes)} elements, {total} boards")
