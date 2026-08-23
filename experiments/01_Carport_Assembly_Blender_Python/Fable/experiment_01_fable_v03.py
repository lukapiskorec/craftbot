# ------------------------------------------------------------------
# EXPERIMENT 01 - Fable run, v03
# v02: purlins at true mid-slope (|y| = 1.4), struts steepened to ~42 deg
#      (base 150 mm above the tie beam), eave overhang 0.8 m.
# v03: commons bear on a horizontal raising plate carried by the projecting
#      tie-beam ends (as in the reference) instead of a tilted eave purlin;
#      longitudinal ridge braces king post -> ridge; struts 150 x 150.
# Timber-frame carport (4 bents / 3 bays, king-post trusses, purlins,
# common rafters) built from craftbot.place_element() boxes.
#
# Axes: X along the building (bents at x = 0, 3, 6, 9), Y across the
# span (posts at y = +-3.0), Z up, slab top at z = 0.  Units: metres.
#
# Assembly sequence (also the order of the code):
#   1 slab  2 posts  3 plates on post tops + longitudinal knee braces
#   4 tie beams across the plates, knee braces post->tie
#   5 king posts, principal rafters, struts (one truss per bent)
#   6 purlins on the principals, raising plates on the tie ends, ridge on
#     the king posts with ridge braces
#   7 common rafters over purlins and ridge, overhanging eaves and gables
# ------------------------------------------------------------------

import bpy
import math
import importlib
from mathutils import Vector, Matrix
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

BENT_X = [0.0, 3.0, 6.0, 9.0]      # bent positions along the building
HALF_SPAN = 3.0                    # post centre-line to ridge
POST_H = 2.6                       # slab top to post top
PITCH = math.radians(40.0)
T, C, S = math.tan(PITCH), math.cos(PITCH), math.sin(PITCH)

SLAB = dict(x=(-1.0, 10.0), y=(-4.0, 4.0), thick=0.15)
POST = (0.20, 0.20)                # width x, width y
PLATE = (0.20, 0.20)               # width (y), depth (z)
TIE = (0.20, 0.25)                 # width (x), depth (z)
TIE_END = HALF_SPAN + 0.45         # tie beam ends project past the posts
PRINCIPAL = (0.15, 0.20)           # width (x), depth perpendicular to slope
KING = (0.15, 0.15)
STRUT = (0.15, 0.15)
BRACE = (0.10, 0.15)
PURLIN = (0.15, 0.20)              # width along slope, depth perpendicular to slope
RAISING_PLATE = (0.20, 0.20)       # width (y), depth (z); horizontal, on the tie-beam ends
RIDGE_BRACE_LEG = 0.6              # ridge brace legs (king post face / ridge underside)
RIDGE = (0.15, 0.20)               # width (y), depth (z)
COMMON = (0.05, 0.15)              # width (x), depth perpendicular to slope
COMMON_SPACING = 0.6
GABLE_OVERHANG = 0.6               # last common rafter beyond the end bents
EAVE_OVERHANG = 0.8                # common rafter tail beyond post centre
PURLIN_Y = 1.4                     # mid-slope purlin position (|y|)
STRUT_BASE = 0.15                  # strut foot above the tie beam top (on the king post)

# derived levels
PLATE_TOP = POST_H + PLATE[1]                  # 2.80
TIE_TOP = PLATE_TOP + TIE[1]                   # 3.05
LONG_X = (BENT_X[0] - GABLE_OVERHANG - COMMON[0] / 2,
          BENT_X[-1] + GABLE_OVERHANG + COMMON[0] / 2)   # longitudinal member extent


def principal_underside_z(y):
    # underside of the principal rafters; foot corner on the tie beam at |y| = HALF_SPAN
    return TIE_TOP + (HALF_SPAN - abs(y)) * T


def common_underside_z(y):
    # underside of the common rafters = top of the purlins (two member depths above)
    return principal_underside_z(y) + (PRINCIPAL[1] + PURLIN[1]) / C


RIDGE_TOP = common_underside_z(RIDGE[0] / 2)   # commons bear on the ridge's top arrises
RIDGE_BOTTOM = RIDGE_TOP - RIDGE[1]

# raising plate on the tie beam top: outer top arris exactly on the commons' underside plane
RP_TOP = TIE_TOP + RAISING_PLATE[1]
RP_Y_OUT = (common_underside_z(0.0) - RP_TOP) / T      # |y| where the commons' plane is at RP_TOP
assert RP_Y_OUT <= TIE_END, "raising plate beyond the tie-beam end"
assert RP_Y_OUT - RAISING_PLATE[0] > HALF_SPAN + PRINCIPAL[1] * S, "raising plate hits the principal foot"

# ------------------------------------------------------------------
# COLLECTIONS


def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def link_to(obj, coll_name):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    get_collection(coll_name).objects.link(obj)


# ------------------------------------------------------------------
# GEOMETRY HELPERS (all members are place_element boxes)


def box(name, coll, lo, hi):
    # axis-aligned box from min corner lo to max corner hi
    lo, hi = Vector(lo), Vector(hi)
    obj = craftbot.place_element(name, loc=(lo + hi) / 2, axis=(0, 0, 1), angle=0,
                                 scale=(hi - lo) / 2)
    link_to(obj, coll)
    return obj


def member(name, coll, p0, p1, width, depth, width_dir, n0=None, n1=None, on_underside=False):
    # Prismatic member from p0 to p1, section = width (along width_dir) x depth.
    # End faces are cut square to the axis.  If a bearing-face normal n0 / n1
    # is given, that end is inset along the axis so no corner of the end face
    # crosses the bearing plane through p0 / p1 (it then touches on one edge).
    # on_underside=True: p0 / p1 lie on the member's underside (the face on the
    # -e2 side), not on its centre line.
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0).normalized()
    e1 = Vector(width_dir)
    e1 = (e1 - axis * e1.dot(axis)).normalized()
    e2 = axis.cross(e1)
    if e2.z < 0:                       # keep the depth axis pointing up (right-handed: flip both)
        e1, e2 = -e1, -e2
    if on_underside:
        p0, p1 = p0 + e2 * depth / 2, p1 + e2 * depth / 2

    def inset(n):
        if n is None:
            return 0.0
        n = Vector(n).normalized()
        reach = abs(e1.dot(n)) * width / 2 + abs(e2.dot(n)) * depth / 2
        return reach / abs(axis.dot(n))

    q0 = p0 + axis * inset(n0)
    q1 = p1 - axis * inset(n1)
    length = (q1 - q0).length
    rot = Matrix((e1, e2, axis)).transposed()      # columns = local X, Y, Z
    ax, ang = rot.to_quaternion().to_axis_angle()
    if ax.length == 0:
        ax = Vector((0, 0, 1))
    obj = craftbot.place_element(name, loc=(q0 + q1) / 2, axis=ax, angle=math.degrees(ang),
                                 scale=(width / 2, depth / 2, length / 2))
    link_to(obj, coll)
    return obj


# ------------------------------------------------------------------
# BUILD

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj)

# --- 1 Foundation ---------------------------------------------------
box("Slab", "Foundation", (SLAB["x"][0], SLAB["y"][0], -SLAB["thick"]),
    (SLAB["x"][1], SLAB["y"][1], 0.0))

# --- 2/3 Posts, longitudinal knee braces, plates --------------------
for i, x in enumerate(BENT_X):
    for side, sgn in (("L", -1), ("R", 1)):
        y = sgn * HALF_SPAN
        box(f"Post_{i+1}{side}", "Structure_Posts",
            (x - POST[0] / 2, y - POST[1] / 2, 0.0), (x + POST[0] / 2, y + POST[1] / 2, POST_H))
        # knee braces in the longitudinal plane (post face -> plate underside), 45 deg
        for dx, tag in ((-1, "W"), (1, "E")):
            if (i == 0 and dx < 0) or (i == len(BENT_X) - 1 and dx > 0):
                continue
            foot = Vector((x + dx * POST[0] / 2, y, POST_H - 0.8))
            head = Vector((x + dx * (POST[0] / 2 + 0.8), y, POST_H))
            member(f"Brace_{i+1}{side}_{tag}", "Structure_Posts", foot, head,
                   BRACE[0], BRACE[1], width_dir=(0, 1, 0), n0=(dx, 0, 0), n1=(0, 0, -1))

for side, sgn in (("L", -1), ("R", 1)):
    y = sgn * HALF_SPAN
    box(f"Plate_{side}", "Roof_Longitudinal",
        (LONG_X[0], y - PLATE[0] / 2, POST_H), (LONG_X[1], y + PLATE[0] / 2, PLATE_TOP))

# --- 4/5 Bents: tie beam, braces, king post, principal rafters, struts
for i, x in enumerate(BENT_X):
    coll = "Structure_Bents"
    box(f"TieBeam_{i+1}", coll, (x - TIE[0] / 2, -TIE_END, PLATE_TOP), (x + TIE[0] / 2, TIE_END, TIE_TOP))
    box(f"KingPost_{i+1}", coll, (x - KING[0] / 2, -KING[1] / 2, TIE_TOP),
        (x + KING[0] / 2, KING[1] / 2, RIDGE_BOTTOM))

    for side, sgn in (("L", -1), ("R", 1)):
        # principal rafter: underside from the tie beam arris at |y| = HALF_SPAN
        # up to the king post face (head inset so its top corner touches the post)
        foot = Vector((x, sgn * HALF_SPAN, principal_underside_z(HALF_SPAN)))
        head = Vector((x, sgn * KING[1] / 2, principal_underside_z(KING[1] / 2)))
        member(f"Principal_{i+1}{side}", coll, foot, head, PRINCIPAL[0], PRINCIPAL[1],
               width_dir=(1, 0, 0), n0=None, n1=(0, -sgn, 0), on_underside=True)
        # strut: king post face near the base -> principal underside below the purlin
        s0 = Vector((x, sgn * KING[1] / 2, TIE_TOP + STRUT_BASE))
        s1 = Vector((x, sgn * PURLIN_Y, principal_underside_z(PURLIN_Y)))
        member(f"Strut_{i+1}{side}", coll, s0, s1, STRUT[0], STRUT[1], width_dir=(1, 0, 0),
               n0=(0, -sgn, 0), n1=(0, sgn * S, C))     # rafter underside normal
        # knee brace in the bent plane: post inner face -> tie beam underside
        b0 = Vector((x, sgn * (HALF_SPAN - POST[1] / 2), POST_H - 0.8))
        b1 = Vector((x, sgn * (HALF_SPAN - POST[1] / 2 - 0.8), PLATE_TOP))
        member(f"TieBrace_{i+1}{side}", coll, b0, b1, BRACE[0], BRACE[1], width_dir=(1, 0, 0),
               n0=(0, -sgn, 0), n1=(0, 0, -1))

# --- 6 Longitudinal roof members: purlins (tilted), eave purlins, ridge
for side, sgn in (("L", -1), ("R", 1)):
    z_top = principal_underside_z(PURLIN_Y) + PRINCIPAL[1] / C     # principal top surface
    normal = Vector((0, sgn * S, C))                                # roof-plane normal
    centre = Vector((0, sgn * PURLIN_Y, z_top)) + normal * PURLIN[1] / 2
    p0 = Vector((LONG_X[0], centre.y, centre.z))
    p1 = Vector((LONG_X[1], centre.y, centre.z))
    member(f"Purlin_{side}", "Roof_Longitudinal", p0, p1, PURLIN[0], PURLIN[1],
           width_dir=(0, sgn * C, -S))                              # width along the slope
    # raising plate: horizontal, on the projecting tie-beam ends, carries the common rafters
    y_in, y_out = sgn * (RP_Y_OUT - RAISING_PLATE[0]), sgn * RP_Y_OUT
    box(f"RaisingPlate_{side}", "Roof_Longitudinal",
        (LONG_X[0], min(y_in, y_out), TIE_TOP), (LONG_X[1], max(y_in, y_out), RP_TOP))

box("Ridge", "Roof_Longitudinal", (LONG_X[0], -RIDGE[0] / 2, RIDGE_BOTTOM),
    (LONG_X[1], RIDGE[0] / 2, RIDGE_TOP))

# ridge braces: king post face -> ridge underside, 45 deg, longitudinal plane
for i, x in enumerate(BENT_X):
    for dx, tag in ((-1, "W"), (1, "E")):
        if (i == 0 and dx < 0) or (i == len(BENT_X) - 1 and dx > 0):
            continue
        foot = Vector((x + dx * KING[0] / 2, 0.0, RIDGE_BOTTOM - RIDGE_BRACE_LEG))
        head = Vector((x + dx * (KING[0] / 2 + RIDGE_BRACE_LEG), 0.0, RIDGE_BOTTOM))
        member(f"RidgeBrace_{i+1}_{tag}", "Structure_Bents", foot, head, BRACE[0], BRACE[1],
               width_dir=(0, 1, 0), n0=(dx, 0, 0), n1=(0, 0, -1))

# --- 7 Common rafters over purlins and ridge --------------------------
n_rafters = int(round((LONG_X[1] - LONG_X[0] - COMMON[0]) / COMMON_SPACING)) + 1
for k in range(n_rafters):
    x = LONG_X[0] + COMMON[0] / 2 + k * COMMON_SPACING
    for side, sgn in (("L", -1), ("R", 1)):
        y_tail = sgn * (HALF_SPAN + EAVE_OVERHANG)
        tail = Vector((x, y_tail, common_underside_z(y_tail)))
        apex = Vector((x, 0.0, common_underside_z(0.0)))
        # head inset so the pair meets on the ridge plane with their top corners
        member(f"Rafter_{k+1:02d}{side}", "Roof_Rafters", tail, apex, COMMON[0], COMMON[1],
               width_dir=(1, 0, 0), n0=None, n1=(0, -sgn, 0), on_underside=True)

print(f"Built carport: {len(bpy.data.objects)} elements, ridge top z = {RIDGE_TOP:.3f} m")
