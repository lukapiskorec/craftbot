# ------------------------------------------------------------------
# EXPERIMENT 02 - Fable run, v01
# "Gothic" hammer-beam timber carport (4 bents / 3 bays) built from
# craftbot.place_element() boxes.
#
# Axes: X along the building (bents at x = 0, 2.4, 4.8, 7.2), Y across
# the span (posts at y = +-2.6), Z up, slab top at z = 0.  Units: metres.
#
# Assembly sequence (also the order of the code):
#   1 slab
#   2 posts
#   3 hammer beams (split tie: two beams per bent, middle free) and the
#     hanging queen posts that carry their inner ends, knee braces
#     post -> hammer beam
#   4 eave plates along the building on the hammer beams, longitudinal
#     V knee braces post -> plate
#   5 collar between the queen posts, St Andrew's cross under the collar
#     (halving joint at the crossing), king post collar -> ridge
#   6 principal rafters foot on the eave plate, meeting at the ridge
#     piece that sits on the king post
#   7 purlins laid on the principals' backs (rotated to the slope)
#   8 common rafters over the purlins, overhanging eaves and gables
#   9 battens over the common rafters
# ------------------------------------------------------------------

import bpy
import math
import importlib
from mathutils import Vector, Matrix
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

BENT_X = [0.0, 2.4, 4.8, 7.2]      # bent positions along the building
POST_Y = 2.6                       # post centre line
POST_H = 3.3                       # slab top to post top (= hammer beam underside)
PITCH = math.radians(50.0)
T, C = math.tan(PITCH), math.cos(PITCH)

SLAB = dict(x=(-0.8, 8.0), y=(-3.4, 3.4), thick=0.15)
POST = (0.24, 0.24)                # x, y
HAMMER = (0.20, 0.25)              # width (x), depth (z)
HAMMER_END = 2.85                  # outer end of the hammer beam (|y|)
QUEEN = (0.20, 0.20)               # hanging queen post section
QUEEN_Y = 1.15                     # queen post centre line (|y|)
PENDANT_DROP = 0.35                # queen post hangs this far below the beam
FINIAL = (0.12, 0.10)              # pendant tip: side, height
PLATE = (0.20, 0.20)               # eave plate, width (y) x depth (z)
COLLAR = (0.20, 0.25)              # width (x), depth (z)
COLLAR_Z = 4.80                    # collar underside
KING = (0.20, 0.20)
PRINCIPAL = (0.15, 0.20)           # width (x), depth perpendicular to slope
RAFTER_TAIL = 3.05                 # principal rafter foot (|y|)
RIDGE = (0.20, 0.20)               # width (y), depth (z)
KNEE = (0.12, 0.15)                # knee braces (cross section)
LONG_BRACE = (0.12, 0.15)
LONG_BRACE_REACH = 0.8             # plate contact point from the post centre (x)
LONG_BRACE_FOOT = 2.55             # brace foot on the post (z)
KNEE_FOOT = 1.70                   # section knee brace foot on the post (z)
KNEE_HEAD_Y = 1.50                 # where it meets the hammer beam underside (|y|)
XBRACE = (0.12, 0.15)              # width (x), depth (in the bent plane)
XBRACE_FOOT_Z = 0.30               # foot centre above the hammer beam top (on the queen post)
XBRACE_HEAD_Y = 0.90               # head on the collar underside (|y|, opposite side)
PURLIN = (0.15, 0.15)              # width along slope x depth perpendicular to slope
PURLIN_Y = [0.9, 1.8, 2.8]         # purlin positions on the slope (|y|)
COMMON = (0.06, 0.12)              # width (x), depth perpendicular to slope
COMMON_SPACING = 0.6
COMMON_TAIL = 3.10                 # common rafter foot (|y|)
BATTEN = (0.05, 0.04)              # width along slope, thickness
BATTEN_SPACING = 0.35              # along the slope
GABLE_OVERHANG = 0.4               # roof beyond the end bents

# derived levels
HAMMER_TOP = POST_H + HAMMER[1]                 # 3.55
PLATE_TOP = HAMMER_TOP + PLATE[1]               # 3.75
PLATE_OUT = POST_Y + PLATE[0] / 2               # 2.70, outer top edge of the plate
COLLAR_TOP = COLLAR_Z + COLLAR[1]               # 5.05
LONG_X = (BENT_X[0] - GABLE_OVERHANG, BENT_X[-1] + GABLE_OVERHANG)   # purlins / battens


def principal_underside_z(y):
    # principal rafter underside: bears on the outer top edge of the eave plate
    return PLATE_TOP + (PLATE_OUT - abs(y)) * T


def principal_top_z(y):
    return principal_underside_z(y) + PRINCIPAL[1] / C


def common_underside_z(y):
    # common rafters rest on the purlins that lie on the principals' backs
    return principal_top_z(y) + PURLIN[1] / C


RIDGE_TOP = common_underside_z(RIDGE[0] / 2)   # commons bear on the ridge's top arrises
RIDGE_BOTTOM = RIDGE_TOP - RIDGE[1]
QUEEN_TOP = principal_underside_z(QUEEN_Y + QUEEN[1] / 2)   # touches the rafter on its outer edge

assert principal_underside_z(HAMMER_END) > HAMMER_TOP, "rafter cuts into the hammer beam tail"
assert principal_top_z(RIDGE[0] / 2) < RIDGE_BOTTOM, "principal rafters hit the ridge piece"
assert COLLAR_TOP < principal_underside_z(QUEEN_Y - QUEEN[1] / 2), "collar hits the rafters"

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


def slope_member(name, coll, x0, x1, y, width, depth, side, z_of_underside, sign_y):
    # Member running along X (purlin / batten), lying on a sloped plane: its
    # underside is the plane z_of_underside(y); `width` is measured along the
    # slope, `depth` perpendicular to it.  sign_y = +1 for the +Y roof side.
    # Box centre is `depth/2` above the plane, measured perpendicular to it.
    n = Vector((0.0, sign_y * math.sin(PITCH), C))           # outward normal of the slope
    centre = Vector(((x0 + x1) / 2, y, z_of_underside(y))) + n * depth / 2
    # rotating about X by -P maps local Z (depth) onto the +Y slope normal, +P onto the -Y one
    obj = craftbot.place_element(name, loc=centre, axis=(1, 0, 0), angle=-sign_y * math.degrees(PITCH),
                                 scale=((x1 - x0) / 2, width / 2, depth / 2))
    link_to(obj, coll)
    return obj


# ------------------------------------------------------------------
# 1  SLAB

box("Slab", "Foundation",
    (SLAB["x"][0], SLAB["y"][0], -SLAB["thick"]),
    (SLAB["x"][1], SLAB["y"][1], 0.0))

# ------------------------------------------------------------------
# 2  POSTS

for i, bx in enumerate(BENT_X):
    for s, side in ((-1, "S"), (1, "N")):
        box(f"Post_{i + 1}{side}", "Posts",
            (bx - POST[0] / 2, s * POST_Y - POST[1] / 2, 0.0),
            (bx + POST[0] / 2, s * POST_Y + POST[1] / 2, POST_H))

# ------------------------------------------------------------------
# 3  HAMMER BEAMS, HANGING QUEEN POSTS, KNEE BRACES (per bent)

for i, bx in enumerate(BENT_X):
    for s, side in ((-1, "S"), (1, "N")):
        qy_in = s * (QUEEN_Y - QUEEN[1] / 2)          # queen post face towards the centre
        qy_out = s * (QUEEN_Y + QUEEN[1] / 2)         # face towards the post
        # hammer beam: from the outer end to the queen post (tenoned into it)
        y_lo, y_hi = sorted((s * HAMMER_END, qy_out))
        box(f"Hammer_Beam_{i + 1}{side}", "Bents",
            (bx - HAMMER[0] / 2, y_lo, POST_H),
            (bx + HAMMER[0] / 2, y_hi, HAMMER_TOP))
        # hanging queen post: pendant below the beam, up to the principal rafter
        box(f"Queen_Post_{i + 1}{side}", "Bents",
            (bx - QUEEN[0] / 2, s * QUEEN_Y - QUEEN[1] / 2, POST_H - PENDANT_DROP),
            (bx + QUEEN[0] / 2, s * QUEEN_Y + QUEEN[1] / 2, QUEEN_TOP))
        box(f"Pendant_Finial_{i + 1}{side}", "Bents",
            (bx - FINIAL[0] / 2, s * QUEEN_Y - FINIAL[0] / 2, POST_H - PENDANT_DROP - FINIAL[1]),
            (bx + FINIAL[0] / 2, s * QUEEN_Y + FINIAL[0] / 2, POST_H - PENDANT_DROP))
        # knee brace: post inner face -> hammer beam underside
        member(f"Knee_Brace_{i + 1}{side}", "Bents",
               (bx, s * (POST_Y - POST[1] / 2), KNEE_FOOT),
               (bx, s * KNEE_HEAD_Y, POST_H),
               KNEE[0], KNEE[1], (1, 0, 0), n0=(0, 1, 0), n1=(0, 0, 1))

# ------------------------------------------------------------------
# 4  EAVE PLATES + LONGITUDINAL V BRACES

for s, side in ((-1, "S"), (1, "N")):
    box(f"Eave_Plate_{side}", "Plates_and_Braces",
        (BENT_X[0] - HAMMER[0] / 2, s * POST_Y - PLATE[0] / 2, HAMMER_TOP),
        (BENT_X[-1] + HAMMER[0] / 2, s * POST_Y + PLATE[0] / 2, PLATE_TOP))
    for i, bx in enumerate(BENT_X):
        for d, tag in ((-1, "W"), (1, "E")):
            if (i == 0 and d < 0) or (i == len(BENT_X) - 1 and d > 0):
                continue                       # no braces beyond the end posts
            member(f"Long_Brace_{i + 1}{side}{tag}", "Plates_and_Braces",
                   (bx + d * POST[0] / 2, s * POST_Y, LONG_BRACE_FOOT),
                   (bx + d * LONG_BRACE_REACH, s * POST_Y, HAMMER_TOP),
                   LONG_BRACE[0], LONG_BRACE[1], (0, 1, 0), n0=(1, 0, 0), n1=(0, 0, 1))

# ------------------------------------------------------------------
# 5  COLLAR, ST ANDREW'S CROSS, KING POST (per bent)


def halved_brace(name, coll, p0, p1, width, depth, width_dir, n0, n1, cross_pt, lap_len, lap_side):
    # Brace from p0 to p1 modelled as three boxes: full section at both ends and
    # a half-width middle segment (the halving joint) of length lap_len centred
    # on the point of the axis nearest cross_pt, kept on the `lap_side`
    # (+1 / -1 along width_dir) so the two crossing braces share the joint
    # zone without overlapping.
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0).normalized()
    w = Vector(width_dir).normalized()
    e2 = axis.cross(w)

    def inset(n):                          # same rule as member()
        n = Vector(n).normalized()
        reach = abs(w.dot(n)) * width / 2 + abs(e2.dot(n)) * depth / 2
        return reach / abs(axis.dot(n))
    q0 = p0 + axis * inset(n0)
    q1 = p1 - axis * inset(n1)
    mid = p0 + axis * (Vector(cross_pt) - p0).dot(axis)
    a, b = mid - axis * lap_len / 2, mid + axis * lap_len / 2
    member(name + "_lo", coll, q0, a, width, depth, w)
    member(name + "_hi", coll, b, q1, width, depth, w)
    offset = w * (lap_side * width / 4)
    member(name + "_lap", coll, a + offset, b + offset, width / 2, depth, w)


for i, bx in enumerate(BENT_X):
    qy_in = QUEEN_Y - QUEEN[1] / 2
    box(f"Collar_{i + 1}", "Bents",
        (bx - COLLAR[0] / 2, -qy_in, COLLAR_Z), (bx + COLLAR[0] / 2, qy_in, COLLAR_TOP))
    box(f"King_Post_{i + 1}", "Bents",
        (bx - KING[0] / 2, -KING[1] / 2, COLLAR_TOP), (bx + KING[0] / 2, KING[1] / 2, RIDGE_BOTTOM))
    # St Andrew's cross: foot on one queen post just above the hammer beam,
    # head on the collar underside on the other side; halving joint where they cross
    foot = Vector((bx, qy_in, HAMMER_TOP + XBRACE_FOOT_Z))
    head = Vector((bx, -XBRACE_HEAD_Y, COLLAR_Z))
    d = (head - foot).normalized()
    phi = 2 * math.atan2(abs(d.z), abs(d.y))          # angle between the two braces
    lap = XBRACE[1] * (1 + math.cos(phi)) / math.sin(phi) + 0.04   # crossing zone + margin
    cross = foot + (head - foot) * (foot.y / (foot.y - head.y))    # centrelines cross at y = 0
    for s, side, lap_side in ((1, "S", -1), (-1, "N", 1)):
        halved_brace(f"X_Brace_{i + 1}{side}", "Bents",
                     (bx, s * qy_in, HAMMER_TOP + XBRACE_FOOT_Z),
                     (bx, -s * XBRACE_HEAD_Y, COLLAR_Z),
                     XBRACE[0], XBRACE[1], (1, 0, 0), (0, 1, 0), (0, 0, 1), cross, lap, lap_side)

# ------------------------------------------------------------------
# 6  PRINCIPAL RAFTERS + RIDGE PIECE

for i, bx in enumerate(BENT_X):
    for s, side in ((-1, "S"), (1, "N")):
        member(f"Principal_Rafter_{i + 1}{side}", "Bents",
               (bx, s * RAFTER_TAIL, principal_underside_z(RAFTER_TAIL)),
               (bx, s * RIDGE[0] / 2, principal_underside_z(RIDGE[0] / 2)),
               PRINCIPAL[0], PRINCIPAL[1], (1, 0, 0), n1=(0, 1, 0), on_underside=True)

box("Ridge", "Bents",
    (LONG_X[0], -RIDGE[0] / 2, RIDGE_BOTTOM), (LONG_X[1], RIDGE[0] / 2, RIDGE_TOP))

# ------------------------------------------------------------------
# 7  PURLINS (on the principals' backs, rotated to the slope)

for s, side in ((-1, "S"), (1, "N")):
    for k, py in enumerate(PURLIN_Y):
        slope_member(f"Purlin_{side}{k + 1}", "Purlins", LONG_X[0], LONG_X[1], s * py,
                     PURLIN[0], PURLIN[1], side, principal_top_z, s)

# ------------------------------------------------------------------
# 8  COMMON RAFTERS (over the purlins, meeting on the ridge piece)

n_common = int(round((BENT_X[-1] - BENT_X[0]) / COMMON_SPACING)) + 2
common_x = [BENT_X[0] - COMMON_SPACING / 2 + k * COMMON_SPACING for k in range(n_common)]
for k, cx in enumerate(common_x):
    for s, side in ((-1, "S"), (1, "N")):
        member(f"Common_Rafter_{k + 1:02d}{side}", "Common_Rafters",
               (cx, s * COMMON_TAIL, common_underside_z(COMMON_TAIL)),
               (cx, 0.0, common_underside_z(0.0)),
               COMMON[0], COMMON[1], (1, 0, 0), n1=(0, 1, 0), on_underside=True)

# ------------------------------------------------------------------
# 9  BATTENS (over the common rafters)


def batten_underside_z(y):
    return common_underside_z(y) + COMMON[1] / C


for s, side in ((-1, "S"), (1, "N")):
    slope_len = (COMMON_TAIL - BATTEN[0] / 2 - 0.05) * (1 / C)
    n_batten = int(slope_len / BATTEN_SPACING) + 1
    for k in range(n_batten):
        by = COMMON_TAIL - 0.05 - BATTEN[0] / 2 * C - k * BATTEN_SPACING * C
        if by < BATTEN[0]:
            break
        slope_member(f"Batten_{side}{k + 1:02d}", "Battens", LONG_X[0], LONG_X[1], s * by,
                     BATTEN[0], BATTEN[1], side, batten_underside_z, s)

print("Experiment 02 Fable v01: model generated")
