# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 14 - Fable run, v09
# Becher study: timber coaling tower refurbished as a multi-storey home.
#
# v09: corners resolved (front boards run between the side walls inside,
# side boards start past the front boards outside), plinths 280 clear of
# the shed's north interior boards.
# v08 (phase 3, user review): no knee braces on the tower (not in the
# photo); exterior tower cladding as gapless horizontal boards against
# the infill walls, between the posts, in bands split by the slabs, the
# lowest band running down to the shed roof; interior cladding on every
# wall (shed, tower, head house), gable rows clipped to the rafter
# undersides; varied windows on storeys 1 and 2 (full height, small
# high, plain; six on the south face); stringers on both sides of every
# flight, posts under the ground landing; CLT strips meeting over the
# mid beam and covering the perimeter beams; a ladder from the deck to
# the head house door; outriggers 50 x 150 against real studs with a
# knee through the clapboard and a sloping board canopy; shed gable
# sticks removed, head house gable studs made 38 x 140; glass in every
# window and leaves in the doors.
#
# Axes: X along the tower (4 bays), Y across (2 bays), Z up, ground
# slab top at z = 0. All members are boxes or convex prisms.
# ------------------------------------------------------------------

import os
import sys
import math
import importlib

import bpy

_HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
for _d in (os.path.join(_HERE, "..", "..", "..", "tools"), os.path.join(_HERE, "..", "tools"), _HERE):
    _d = os.path.normpath(_d)
    if os.path.isfile(os.path.join(_d, "craftbot_lib.py")) and _d not in sys.path:
        sys.path.insert(0, _d)

import craftbot_lib as craftbot
import geometry2d as g2
import planes
import framing
for _m in (craftbot, g2, planes, framing):
    importlib.reload(_m)

from mathutils import Vector
from craftbot_lib import box, prism, prism_x, prism_y
from planes import sloped_member, vy, vz, Roof

# ------------------------------------------------------------------
# PARAMETERS

# tower grid (photo: about 4 bays by 2, heavy posts)
BAY = 2.4
NX, NY = 4, 2
POST = 0.25                       # square post, sawn heavy timber
PLINTH_H, PLINTH_W = 0.075, 0.28  # Architect's Handbook 4-13: base raised 25-76 mm; 280 clears the shed's north boards
GIRT = (0.20, 0.30)               # preserved perimeter girts: thickness (out of plane), depth
BRACE = 0.15                      # trestle cross braces, square

# storeys (London guide 5.4.1: 2.5 min clear; 3.0 storey gives 2.84 under a 100 slab + beam zone)
STOREY = 3.0
Z_L1 = 4.5                        # first slab top: clears the shed ridge (3.9) plus beam depth
N_UPPER = 3                       # slabs L1, L2, L3
CLT_T = 0.10                      # CLT Handbook table 5.1: 100 mm 3-layer spans 3.7 m, slab spans 2.4 m here
GLB = (0.222, 0.342)              # glulam ledger beams between posts: width (Handbook 4-9), depth (9 x 38)
SLAB_GAP = 0.025                  # slab notch clearance around the posts

# stairs (CMHC ch 17: rise 125-200, run 210-355, width 860; flight height max 3.7 m)
STAIR_W = 0.90
RISER, GOING = 0.20, 0.25         # upper flights: 15 risers per 3.0 m storey
G_RISER, G_GOING = 4.5 / 23, 0.23 # ground flight: 23 risers, two runs, landing between
STEP_D = 0.06                     # solid tread block thickness (CMHC: treads at least 38 mm)
STAIR_Y0 = 0.75                   # strip between the y = 0 and y = 2.4 post rows
LAND_L = 0.90                     # landing length (CMHC: at least 860 mm)
STRINGER = (0.05, 0.235)          # side stringers: thickness, depth (CMHC: 235 min)
LAND_POST = 0.09                  # posts under the ground landing

# shed (ground floor house), photo: one storey, low gable along X, kicked eave not modelled
SHED_X0, SHED_X1 = -1.2, NX * BAY + 1.2
SHED_Y0, SHED_Y1 = -1.5, NY * BAY + 0.3      # asymmetric about the tower, as in the photo
WALL_T, STUD_T = 0.14, 0.038                 # CMHC table 25: 38 x 140 at 600 (roof + one floor)
SPACING = 0.6
GRID0 = 0.3                                  # rafters / joists / studs at 0.3 + 0.6k: they miss the 2.4 post grid
PLATE_TOP = 2.8                              # top of the doubled top plate
CJ = (0.038, 0.184)                          # ceiling joists 38 x 184 (CMHC table 33 anchor), lapped over the mid beam
CJ_LAP = 0.15                                # half of the 300 max lap, each side of the beam line
MIDBEAM = (0.114, 0.235)                     # built-up 3 x 38 x 235 (CMHC fig 52)
RAF = (0.038, 0.184)                         # CMHC table 31: 38 x 184 at 600 spans 4.41 m at 1.5 kPa
PITCH = 4.0 / 12.0                           # 1:3, the CMHC threshold: ceiling joists tie the rafter feet
RIDGE_Y = 1.8                                # ridge 0.6 south of the mid post row, so no post hits the ridge board
RIDGE_B = (0.038, 0.235)
OVERHANG = 0.45
COLLAR = (0.038, 0.089)                      # 38 x 89 collar ties (CMHC ch 11)
COLLAR_Z = 3.35
BOARD = (0.184, 0.019)                       # 19 x 184 roof boards, closed, parallel to the eaves (CMHC fig 98)
HOLE_CL = 0.012                              # board clearance around a post

# stair hole in the shed ceiling and roof: the strip between the header and the ridge
HOLE_Y0 = 0.6                                # header outer face
HOLE_X0, HOLE_X1 = 3.3, 8.7                  # doubled trimmer rafters / joists at these grid lines

# terrace deck on the tower top (former bunker cap, now flat; CMHC low slope, fall not modelled)
Z_TERR_GIRT = 13.3                           # top of the top girts / beams
TJ = (0.038, 0.235)                          # roof joists 38 x 235 at 600 (CMHC table 29)
DECK_T = 0.038                               # deck boards 38 mm at 600 joist spacing (CMHC ch 26)
TERR_OVER = 0.9                              # eave / terrace overhang beyond the post faces
GUARD_H = 1.07                               # CMHC: 1070 mm above 1.8 m over grade

# head house (hoist house) on the east 2 x 2 bays, standing on the continued posts
HH_IX0 = 2                                   # first post column index of the head house (x = 4.8)
COLONNADE = 2.4                              # clear height of the open colonnade above the deck
HH_WALL_H = 2.4
HH_PITCH = 8.0 / 12.0
HH_RAF = (0.038, 0.140)
HH_FJ = (0.038, 0.184)                       # head house floor joists
HH_BOARD_T = 0.032                           # floor boards

# cladding (photo: horizontal planking on the shed and between the bunker posts, vertical on the head house)
CLAP_T, CLAP_ROW, CLAP_L = 0.019, 0.16, 3.6  # shed clapboard: thickness, exposure, board length
CB_W, CB_T = 0.14, 0.025                     # tower and head house exterior boards
IB_T = 0.019                                 # interior boards (same widths as the exterior they mirror)
GLASS_T = 0.024
DOOR_T = 0.045                               # Architect's Handbook 6-5: 44.4 mm wood door

# repairs
REPAIR_POSTS = [(0, 0), (4, 0), (4, 2), (2, 2)]   # (ix, iy) posts that get a new foot
REPAIR_H = 0.9
SPLICE = (0.012, 0.16, 0.6)                  # steel splice plates: thickness, width, length (two faces)

# ------------------------------------------------------------------
# DERIVED

def post_x(ix): return ix * BAY
def post_y(iy): return iy * BAY
X_END, Y_END = NX * BAY, NY * BAY

def z_slab_top(k): return Z_L1 + (k - 1) * STOREY          # k = 1..N_UPPER
def z_slab_under(k): return z_slab_top(k) - CLT_T
def z_beam(k):                                              # (bottom, top) of the glulam beams under slab k
    return z_slab_under(k) - GLB[1], z_slab_under(k)

S = PITCH
DV = RAF[1] * math.sqrt(1 + S * S)
Y_OUT_S, Y_OUT_N = SHED_Y0, SHED_Y1                          # plate outer faces = wall outer faces
RAF_TOP0 = PLATE_TOP + DV - S * WALL_T                       # underside meets the plate top at its inner face
ROOF_S = Roof("Shed_S", out=(0, -1), c=-Y_OUT_S, z0=RAF_TOP0, s=S)
ROOF_N = Roof("Shed_N", out=(0, 1), c=Y_OUT_N, z0=RAF_TOP0, s=S)
def roof_top(y): return ROOF_S.z(0, y) if y <= RIDGE_Y else ROOF_N.z(0, y)
def roof_under(y): return roof_top(y) - DV
RIDGE_Z = ROOF_S.z(0, RIDGE_Y)
BOARD_DZ = BOARD[1] * math.sqrt(1 + S * S)                   # roof board thickness measured vertically
def roof_boards_top(y): return roof_top(y) + BOARD_DZ
RUN_S, RUN_N = RIDGE_Y - Y_OUT_S, Y_OUT_N - RIDGE_Y
assert abs(RUN_S - RUN_N) < 1e-9, "ridge must sit on the shed centreline for equal pitches"

Z_BEAM1_BOT = z_beam(1)[0]
assert Z_BEAM1_BOT > roof_boards_top(BAY) + 0.05, "L1 beams must clear the shed roof at the mid post row"

Z_TERR_JTOP = Z_TERR_GIRT + TJ[1]
Z_DECK_TOP = Z_TERR_JTOP + DECK_T
Z_HH_GIRT = Z_DECK_TOP + COLONNADE                           # top of the head house floor girts
Z_HH_JTOP = Z_HH_GIRT + HH_FJ[1]
Z_HH_FLOOR = Z_HH_JTOP + HH_BOARD_T
Z_HH_PLATE = Z_HH_FLOOR + HH_WALL_H
HH_X0, HH_X1 = post_x(HH_IX0), X_END
HH_Y0, HH_Y1 = 0.0, Y_END
HH_S = HH_PITCH
HH_DV = HH_RAF[1] * math.sqrt(1 + HH_S * HH_S)
HH_RAF_TOP0 = Z_HH_PLATE + HH_DV - HH_S * WALL_T
HH_YOUT_S, HH_YOUT_N = HH_Y0 - POST / 2, HH_Y1 + POST / 2   # head house walls flush with the post outer faces
HH_ROOF_S = Roof("HH_S", out=(0, -1), c=-HH_YOUT_S, z0=HH_RAF_TOP0, s=HH_S)
HH_ROOF_N = Roof("HH_N", out=(0, 1), c=HH_YOUT_N, z0=HH_RAF_TOP0, s=HH_S)
HH_RIDGE_Y = (HH_YOUT_S + HH_YOUT_N) / 2
HH_RIDGE_Z = HH_ROOF_S.z(0, HH_RIDGE_Y)
HH_BOARD_DZ = BOARD[1] * math.sqrt(1 + HH_S * HH_S)
HX0, HX1 = HH_X0 - POST / 2, X_END + POST / 2                # head house wall outer faces in X

# ------------------------------------------------------------------
# 2D helpers

def split_spans(spans, holes_1d):
    """Intervals minus intervals."""
    out = spans
    for h0, h1 in holes_1d:
        new = []
        for a, b in out:
            if h0 < b - 1e-6 and h1 > a + 1e-6:
                if h0 > a + 1e-6:
                    new.append((a, h0))
                if h1 < b - 1e-6:
                    new.append((h1, b))
            else:
                new.append((a, b))
        out = new
    return out

def rect_minus(rect_poly, holes):
    """Convex pieces of a convex polygon minus axis-aligned rectangles."""
    pieces = [rect_poly]
    for hx0, hx1, hy0, hy1 in holes:
        out = []
        for p in pieces:
            xs = [q[0] for q in p]; ys = [q[1] for q in p]
            if max(xs) <= hx0 + 1e-9 or min(xs) >= hx1 - 1e-9 or max(ys) <= hy0 + 1e-9 or min(ys) >= hy1 - 1e-9:
                out.append(p)
                continue
            rest = p
            for (pt, n) in (((hx0, 0), (-1, 0)), ((hx1, 0), (1, 0)), ((0, hy0), (0, -1)), ((0, hy1), (0, 1))):
                side = g2.clip(rest, pt, n)
                if len(side) >= 3 and g2.area(side) > 1e-6:
                    out.append(side)
                rest = g2.clip(rest, pt, (-n[0], -n[1]))
                if len(rest) < 3:
                    break
        pieces = out
    return pieces

def clip_below_line(poly, ya, yb, z_fn, keep_above):
    """Clip a convex (y, z) polygon by the line through (ya, z_fn(ya)) and
    (yb, z_fn(yb)), keeping the side above it (keep_above) or below it. Pass
    yb on the slope side of a piecewise roof function."""
    za, zb = z_fn(ya), z_fn(yb)
    m = (zb - za) / (yb - ya)
    nrm = (-m, 1.0) if keep_above else (m, -1.0)                    # normal of the kept side
    return g2.clip(poly, (ya, za), nrm)

def board_rows(prefix, coll, along, a0, a1, b0, b1, z0, z1, row_h, holes, n0=0):
    """Gapless horizontal board rows on a wall zone b0..b1, from z0 to z1,
    each row split around the holes (a0, a1, z0, z1). Returns the count."""
    n = n0
    z = z0
    while z < z1 - 1e-6:
        zb = min(z + row_h, z1)
        cuts = [(ha0, ha1) for ha0, ha1, hz0, hz1 in holes if hz0 < zb - 1e-6 and hz1 > z + 1e-6]
        for a, b in split_spans([(a0, a1)], cuts):
            if along == "x":
                box(f"{prefix}_{n:03d}", coll, a, b, b0, b1, z, zb)
            else:
                box(f"{prefix}_{n:03d}", coll, b0, b1, a, b, z, zb)
            n += 1
        z = zb
    return n

def board_columns(prefix, coll, along, a0, a1, b0, b1, z0, z1, col_w, holes):
    """Gapless vertical boards (head house)."""
    n = 0
    a = a0
    while a < a1 - 1e-6:
        ab = min(a + col_w, a1)
        cuts = [(hz0, hz1) for ha0, ha1, hz0, hz1 in holes if ha0 < ab - 1e-6 and ha1 > a + 1e-6]
        for za, zb in split_spans([(z0, z1)], cuts):
            if along == "x":
                box(f"{prefix}_{n:03d}", coll, a, ab, b0, b1, za, zb)
            else:
                box(f"{prefix}_{n:03d}", coll, b0, b1, a, ab, za, zb)
            n += 1
        a = ab
    return n

def gable_pieces(prefix, coll, x0, x1, y0, y1, z0, z_lim_fn, ridge_y, stripes, along_y, holes=()):
    """Boards on a gable face x0..x1 (an x = const plane) above z0, bounded
    above by the roof line z = z_lim_fn(y) (two slopes meeting at ridge_y).
    `stripes` = list of (y_a, y_b) columns when along_y (vertical boards) or
    row height when not (horizontal rows). Each piece is split at the ridge,
    cut around the holes (y0, y1, z0, z1) and clipped to the roof line."""
    n = 0
    z_max = z_lim_fn(ridge_y)
    if along_y:
        cells = [(ya, yb, z0, z_max) for ya, yb in stripes]
    else:
        cells = []
        z = z0
        while z < z_max - 1e-6:
            zb = min(z + stripes, z_max)
            cells.append((y0, y1, z, zb))
            z = zb
    for ya, yb, za, zb in cells:
        for p in rect_minus(g2.rect(ya, yb, za, zb), list(holes)):
            for side in (-1, +1):
                q = g2.clip(p, (ridge_y, 0.0), (side, 0.0))          # the ridge side
                if len(q) < 3:
                    continue
                q = clip_below_line(q, ridge_y, ridge_y + side, z_lim_fn, False)
                if len(q) >= 3 and g2.area(q) > 1e-5:
                    prism_x(f"{prefix}_{n:03d}", coll, x0, x1, q)
                    n += 1
    return n

def sloped_x_member(name, coll, x0, x1, y0, y1, roof, depth, top_off=0.0):
    """Member along X whose (y, z) profile is a parallelogram with plumb sides at
    y0 / y1, top on the roof plane (offset top_off along z), `depth` measured
    perpendicular to the slope."""
    dv = depth * math.sqrt(1 + roof.s * roof.s)
    pts = [(y0, roof.z(0, y0) + top_off - dv), (y1, roof.z(0, y1) + top_off - dv),
           (y1, roof.z(0, y1) + top_off), (y0, roof.z(0, y0) + top_off)]
    return prism_x(name, coll, x0, x1, pts)

# ------------------------------------------------------------------
# BUILD

craftbot.clear_scene()

# --- foundation ---------------------------------------------------
box("Ground_Slab", "Foundation", SHED_X0 - 0.3, SHED_X1 + 0.3, SHED_Y0 - 0.3, SHED_Y1 + 0.3, -0.20, 0.0)
for ix in range(NX + 1):
    for iy in range(NY + 1):
        x, y = post_x(ix), post_y(iy)
        box(f"Plinth_{ix}{iy}", "Foundation/Plinths",
            x - PLINTH_W / 2, x + PLINTH_W / 2, y - PLINTH_W / 2, y + PLINTH_W / 2, 0.0, PLINTH_H)

# --- tower posts (preserved), with repaired feet -------------------
def post_top(ix):
    return Z_HH_GIRT if ix >= HH_IX0 else Z_TERR_GIRT

for ix in range(NX + 1):
    for iy in range(NY + 1):
        x, y = post_x(ix), post_y(iy)
        z0, z1 = PLINTH_H, post_top(ix)
        if (ix, iy) in REPAIR_POSTS:
            zr = z0 + REPAIR_H
            box(f"Post_{ix}{iy}_NewFoot", "Repairs/Post_Feet",
                x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, z0, zr)
            for side, sgn in (("W", -1), ("E", 1)):
                xf = x + sgn * POST / 2
                box(f"Post_{ix}{iy}_Splice{side}", "Repairs/Splices",
                    min(xf, xf + sgn * SPLICE[0]), max(xf, xf + sgn * SPLICE[0]),
                    y - SPLICE[1] / 2, y + SPLICE[1] / 2, zr - SPLICE[2] / 2, zr + SPLICE[2] / 2)
            z0 = zr
        box(f"Post_{ix}{iy}", "Existing/Tower_Posts",
            x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, z0, z1)

# --- preserved perimeter girts on the outer post faces -------------
GIRT_TOPS = [z_beam(k)[1] for k in range(1, N_UPPER + 1)] + [Z_TERR_GIRT]

def girt_run(name, coll, axis, a0, a1, b_face, sgn, ztop):
    z0, z1 = ztop - GIRT[1], ztop
    bb0, bb1 = sorted((b_face, b_face + sgn * GIRT[0]))
    if axis == "x":
        box(name, coll, a0, a1, bb0, bb1, z0, z1)
    else:
        box(name, coll, bb0, bb1, a0, a1, z0, z1)

for k, zt in enumerate(GIRT_TOPS):
    for side, y, sgn in (("S", 0.0, -1), ("N", Y_END, 1)):
        girt_run(f"Girt_L{k}_{side}", "Existing/Tower_Girts", "x",
                 -POST / 2 - GIRT[0], X_END + POST / 2 + GIRT[0], y + sgn * POST / 2, sgn, zt)
    for side, x, sgn in (("W", 0.0, -1), ("E", X_END, 1)):
        girt_run(f"Girt_L{k}_{side}", "Existing/Tower_Girts", "y",
                 -POST / 2, Y_END + POST / 2, x + sgn * POST / 2, sgn, zt)

for side, y, sgn in (("S", 0.0, -1), ("N", Y_END, 1)):
    girt_run(f"Girt_HH_{side}", "Existing/HeadHouse_Frame", "x",
             HH_X0 - POST / 2 - GIRT[0], X_END + POST / 2 + GIRT[0], y + sgn * POST / 2, sgn, Z_HH_GIRT)
for side, x, sgn in (("W", HH_X0, -1), ("E", X_END, 1)):
    girt_run(f"Girt_HH_{side}", "Existing/HeadHouse_Frame", "y",
             -POST / 2, Y_END + POST / 2, x + sgn * POST / 2, sgn, Z_HH_GIRT)

# --- new glulam beams between the posts, on the three X rows ---------
for k in range(1, N_UPPER + 1):
    zb0, zb1 = z_beam(k)
    for iy in range(NY + 1):
        y = post_y(iy)
        for ix in range(NX):
            box(f"Beam_L{k}_{ix}{iy}", "New/Beams",
                post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
                y - GLB[0] / 2, y + GLB[0] / 2, zb0, zb1)
for iy in range(NY + 1):
    y = post_y(iy)
    for ix in range(NX):
        box(f"Beam_T_{ix}{iy}", "New/Beams",
            post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
            y - GLB[0] / 2, y + GLB[0] / 2, Z_TERR_GIRT - GLB[1], Z_TERR_GIRT)
for ix in range(HH_IX0, NX):
    box(f"Beam_HH_{ix}", "New/Beams",
        post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
        post_y(1) - GLB[0] / 2, post_y(1) + GLB[0] / 2, Z_HH_GIRT - GLB[1], Z_HH_GIRT)

# --- stairs, stringers and the slab voids -----------------------------
STAIR_Y1 = STAIR_Y0 + STAIR_W
X_IN_W, X_IN_E = POST / 2 + SLAB_GAP, X_END - POST / 2 - SLAB_GAP    # slab x extent
STR_Y = [(STAIR_Y0 - STRINGER[0], STAIR_Y0), (STAIR_Y1, STAIR_Y1 + STRINGER[0])]

def flight_x_extent(x_start, direction, n_risers, going):
    run = (n_risers - 1) * going
    return (x_start, x_start + run) if direction > 0 else (x_start - run, x_start)

def stringers(prefix, x_start, direction, n_risers, going, riser, z_base, z_floor):
    """Two side stringers: top line through the back-bottom corners of the
    treads (z_base - STEP_D at the foot, rising riser per going), depth
    STRINGER[1] perpendicular to the slope, feet cut level at z_floor, head
    plumb at the landing riser."""
    s = riser / going
    dv = STRINGER[1] * math.sqrt(1 + s * s)
    xa, xb = flight_x_extent(x_start, direction, n_risers, going)
    def z_top(x): return z_base - STEP_D + abs(x - x_start) * s
    poly = [(xa, z_top(xa)), (xb, z_top(xb)), (xb, z_top(xb) - dv), (xa, z_top(xa) - dv)]
    poly = g2.clip(poly, (0.0, z_floor), (0.0, 1.0))                  # feet on the floor
    for j, (ya, yb) in enumerate(STR_Y):
        prism_y(f"{prefix}_Stringer_{j}", "New/Stairs", ya, yb, poly)

# ground flight (two runs, landing between): rises eastward, lands 1.05 m short of the east wall
G_N1, G_N2 = 12, 11
G_LAND_X = X_IN_E - 1.05
g_x0 = G_LAND_X - ((G_N1 - 1) * G_GOING + LAND_L + (G_N2 - 1) * G_GOING)
framing.flight("Stair_G1", "New/Stairs", g_x0, +1, STAIR_Y0, STAIR_Y1, 0.0, G_N1, G_GOING, G_RISER, STEP_D)
stringers("Stair_G1", g_x0, +1, G_N1, G_GOING, G_RISER, 0.0, 0.0)
g_land0 = g_x0 + (G_N1 - 1) * G_GOING
Z_LAND = G_N1 * G_RISER
box("Stair_G_Landing", "New/Stairs", g_land0, g_land0 + LAND_L, STAIR_Y0, STAIR_Y1, Z_LAND - STEP_D, Z_LAND)
for i, (lx, ly) in enumerate(((g_land0 + 0.03, STAIR_Y0 + 0.03), (g_land0 + LAND_L - 0.03 - LAND_POST, STAIR_Y0 + 0.03),
                              (g_land0 + 0.03, STAIR_Y1 - 0.03 - LAND_POST), (g_land0 + LAND_L - 0.03 - LAND_POST, STAIR_Y1 - 0.03 - LAND_POST))):
    box(f"Stair_G_LandingPost_{i}", "New/Stairs", lx, lx + LAND_POST, ly, ly + LAND_POST, 0.0, Z_LAND - STEP_D)
g_x2 = g_land0 + LAND_L
framing.flight("Stair_G2", "New/Stairs", g_x2, +1, STAIR_Y0, STAIR_Y1, Z_LAND, G_N2, G_GOING, G_RISER, STEP_D)
stringers("Stair_G2", g_x2, +1, G_N2, G_GOING, G_RISER, Z_LAND, Z_LAND - STEP_D)
G_TOP_X = g_x2 + (G_N2 - 1) * G_GOING            # last riser lands on the L1 slab at this x
assert G_TOP_X < X_IN_E - 0.05, "ground stair overruns the east beam"
assert abs((G_N1 + G_N2) * G_RISER - Z_L1) < 1e-9

N_R = int(round(STOREY / RISER))
assert abs(N_R * RISER - STOREY) < 1e-9
def upper_flight(k):
    """Flight from slab k to slab k + 1 (k + 1 may be the terrace)."""
    direction = -1 if k % 2 == 1 else +1              # L1 -> L2 westward, L2 -> L3 eastward, ...
    x_start = 4.6 if direction < 0 else X_END - 5.0   # foot 0.95 m from the far wall, clear of the void below
    v0, v1 = VOIDS[k]
    foot = (x_start, x_start + GOING) if direction > 0 else (x_start - GOING, x_start)
    assert foot[1] <= v0 + 1e-9 or foot[0] >= v1 - 1e-9, f"flight L{k} foot {foot} inside void {VOIDS[k]}"
    framing.flight(f"Stair_L{k}", "New/Stairs", x_start, direction, STAIR_Y0, STAIR_Y1,
                   z_slab_top(k), N_R, GOING, RISER, STEP_D)
    stringers(f"Stair_L{k}", x_start, direction, N_R, GOING, RISER, z_slab_top(k), z_slab_top(k))
    return flight_x_extent(x_start, direction, N_R, GOING), direction

VOIDS = {}
z_clear = z_slab_under(1) - 1.95
i_first = max(1, math.ceil((z_clear - G_N1 * G_RISER) / G_RISER))
VOID_MARGIN = 0.1
VOIDS[1] = (g_x2 + (i_first - 1) * G_GOING - VOID_MARGIN, G_TOP_X)
for k in range(1, N_UPPER + 1):
    (xa, xb), direction = upper_flight(k)
    z_clear = z_slab_under(k + 1) - 1.95 if k + 1 <= N_UPPER else Z_TERR_GIRT - GLB[1] - 1.95
    i_first = max(1, math.ceil((z_clear - z_slab_top(k)) / RISER))
    x_first = (xa + (i_first - 1) * GOING) if direction > 0 else (xb - (i_first - 1) * GOING)
    if k + 1 <= N_UPPER:
        VOIDS[k + 1] = (x_first - VOID_MARGIN, xb) if direction > 0 else (xa, x_first + VOID_MARGIN)
    else:
        TERR_VOID = (x_first - VOID_MARGIN, xb) if direction > 0 else (xa, x_first + VOID_MARGIN)

# --- CLT slabs: one strip per bay in Y, from the outer edge of the perimeter
# beam to the centreline of the mid beam (the two strips meet there), notched
# around the interior posts (CNC cut, 25 mm clearance), holed by the stair void.
VOID_Y0, VOID_Y1 = HOLE_Y0, RIDGE_Y            # 0.6 .. 1.8, same strip as the shed roof hole
SLAB_Y = [(-GLB[0] / 2, post_y(1)), (post_y(1), Y_END + GLB[0] / 2)]
for k in range(1, N_UPPER + 1):
    z0, z1 = z_slab_under(k), z_slab_top(k)
    vx0, vx1 = VOIDS[k]
    for iy, (ya, yb) in enumerate(SLAB_Y):
        outline = g2.rect(X_IN_W, X_IN_E, ya, yb)
        holes = []
        for ix in range(1, NX):                                    # interior posts on both edges
            px = post_x(ix)
            holes.append((px - POST / 2 - SLAB_GAP, px + POST / 2 + SLAB_GAP, ya - 0.01, post_y(iy) + POST / 2 + SLAB_GAP))
            holes.append((px - POST / 2 - SLAB_GAP, px + POST / 2 + SLAB_GAP, post_y(iy + 1) - POST / 2 - SLAB_GAP, yb + 0.01))
        if iy == 0:
            holes.append((vx0, vx1, VOID_Y0, VOID_Y1))
        for j, p in enumerate(rect_minus(outline, holes)):
            prism(f"Slab_L{k}_{iy}_{j:02d}", "New/Slabs", (0, 0, 0), (1, 0, 0), (0, 1, 0), p, z0, z1)

# --- shed: ground floor house (preserved frame) ---------------------
SW = "Existing/Shed_Walls"
SHED_OPS = {                                  # (a0, a1, sill | None, head) per face, a = x or y
    "S": [(0.9, 2.1, 0.9, 2.1), (5.7, 6.9, 0.9, 2.1), (8.1, 9.3, 0.9, 2.1)],
    "N": [(3.3, 4.5, 0.9, 2.1), (6.9, 8.1, 0.9, 2.1)],
    "W": [(2.0, 3.2, 0.9, 2.1)],
    "E": [(1.0, 2.2, 0.9, 2.1), (3.0, 4.0, None, 2.1)],     # photo: window left, door right
}
framing.stud_wall("ShedWall_S", SW, "x", SHED_X0, SHED_X1, SHED_Y0, SHED_Y0 + WALL_T, 0.0, PLATE_TOP,
                  STUD_T, SPACING, grid0=GRID0, double_top=True, openings=SHED_OPS["S"])
framing.stud_wall("ShedWall_N", SW, "x", SHED_X0, SHED_X1, SHED_Y1 - WALL_T, SHED_Y1, 0.0, PLATE_TOP,
                  STUD_T, SPACING, grid0=GRID0, double_top=True, openings=SHED_OPS["N"])
framing.stud_wall("ShedWall_W", SW, "y", SHED_Y0 + WALL_T, SHED_Y1 - WALL_T, SHED_X0, SHED_X0 + WALL_T,
                  0.0, PLATE_TOP, STUD_T, SPACING, grid0=GRID0, double_top=True, openings=SHED_OPS["W"])
framing.stud_wall("ShedWall_E", SW, "y", SHED_Y0 + WALL_T, SHED_Y1 - WALL_T, SHED_X1 - WALL_T, SHED_X1,
                  0.0, PLATE_TOP, STUD_T, SPACING, grid0=GRID0, double_top=True, openings=SHED_OPS["E"])
# (gable studs removed at the user's request; the gable boards are nailed to the end rafters and the plate)

# mid beam under the ceiling joist laps, between the mid-row posts
MB_Z0, MB_Z1 = PLATE_TOP - MIDBEAM[1], PLATE_TOP
mb_y0, mb_y1 = post_y(1) - MIDBEAM[0] / 2, post_y(1) + MIDBEAM[0] / 2
mb_cuts = [(post_x(ix) - POST / 2, post_x(ix) + POST / 2) for ix in range(NX + 1)]
for j, (xa, xb) in enumerate(g2.split_range(SHED_X0 + WALL_T, SHED_X1 - WALL_T, mb_cuts)):
    box(f"ShedMidBeam_{j}", "Existing/Shed_Ceiling", xa, xb, mb_y0, mb_y1, MB_Z0, MB_Z1)

# ceiling joists beside the rafters (CMHC fig 83)
CJ_Z0, CJ_Z1 = PLATE_TOP, PLATE_TOP + CJ[1]
joist_xs = g2.positions(SHED_X0 + WALL_T, SHED_X1 - WALL_T, SPACING, CJ[0], GRID0)[1:-1]
in_hole = lambda x: HOLE_X0 - 0.01 < x < HOLE_X1 + 0.01
on_edge = lambda x: abs(x - HOLE_X0) < 0.01 or abs(x - HOLE_X1) < 0.01
HDR_T = 2 * CJ[0]
t = CJ[0]
for j, x in enumerate(joist_xs):
    xs0, xs1 = x - 1.5 * t, x - 0.5 * t
    xn0, xn1 = x + 0.5 * t, x + 1.5 * t
    if in_hole(x) and not on_edge(x):
        box(f"ShedCJ_S_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, SHED_Y0 + WALL_T, HOLE_Y0 - HDR_T, CJ_Z0, CJ_Z1)
        box(f"ShedCJ_Sstub_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, RIDGE_Y + HDR_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
    else:
        box(f"ShedCJ_S_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, SHED_Y0 + WALL_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
    box(f"ShedCJ_N_{j:02d}", "Existing/Shed_Ceiling", xn0, xn1, post_y(1) - CJ_LAP, SHED_Y1 - WALL_T, CJ_Z0, CJ_Z1)
CJ_TRIM = {"W": (HOLE_X0 + 2.5 * t, HOLE_X0 + 3.5 * t), "E": (HOLE_X1 - 3.5 * t, HOLE_X1 - 2.5 * t)}
RAF_TRIM = {"W": HOLE_X0 + 2.0 * t, "E": HOLE_X1 - 2.0 * t}
for name, (xa, xb) in CJ_TRIM.items():
    box(f"ShedCJ_Trimmer_{name}", "Existing/Shed_Ceiling", xa, xb, SHED_Y0 + WALL_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
hx0, hx1 = CJ_TRIM["W"][1], CJ_TRIM["E"][0]
box("ShedCJ_Header_S", "Existing/Shed_Ceiling", hx0, hx1, HOLE_Y0 - HDR_T, HOLE_Y0, CJ_Z0, CJ_Z1)
box("ShedCJ_Header_N", "Existing/Shed_Ceiling", hx0, hx1, RIDGE_Y, RIDGE_Y + HDR_T, CJ_Z0, CJ_Z1)

# rafters
RR = "Existing/Shed_Roof"
raf_xs = [SHED_X0 + RAF[0] / 2] + [x for x in joist_xs] + [SHED_X1 - RAF[0] / 2]
ridge_face = {-1: RIDGE_Y - RIDGE_B[0] / 2, +1: RIDGE_Y + RIDGE_B[0] / 2}
HDR_D = 0.235
for k, x in enumerate(raf_xs):
    for side, sgn, roof, y_out, d in (("S", -1, ROOF_S, Y_OUT_S, (0, 1)), ("N", +1, ROOF_N, Y_OUT_N, (0, -1))):
        p0 = (x, y_out)
        clips = [vz(PLATE_TOP, +1), vy(ridge_face[sgn], sgn)]
        if side == "S" and in_hole(x) and not on_edge(x):
            clips = [vz(PLATE_TOP, +1), vy(HOLE_Y0 - HDR_T, -1)]
        sloped_member(f"Rafter_{k:02d}{side}", RR, p0, d, S, RAF_TOP0, RAF[1], RAF[0],
                      0.0, abs(RIDGE_Y - y_out) + 0.5, clips=clips)
        sloped_member(f"Rafter_{k:02d}{side}_tail", RR, p0, d, S, RAF_TOP0, RAF[1], RAF[0],
                      -OVERHANG, 0.0)
for name, xt in RAF_TRIM.items():
    sloped_member(f"Rafter_Trimmer_{name}", RR, (xt, Y_OUT_S), (0, 1), S, RAF_TOP0, RAF[1], RAF[0],
                  0.0, RIDGE_Y - Y_OUT_S + 0.5, clips=[vz(PLATE_TOP, +1), vy(ridge_face[-1], -1)])
RHX0, RHX1 = RAF_TRIM["W"] + RAF[0] / 2, RAF_TRIM["E"] - RAF[0] / 2
sloped_x_member("Rafter_Header_S", RR, RHX0, RHX1, HOLE_Y0 - HDR_T, HOLE_Y0, ROOF_S, HDR_D)
RIDGE_DROP = RIDGE_B[0] / 2 * S
RIDGE_BOT = RIDGE_Z - RIDGE_B[1] - RIDGE_DROP
box("Ridge_Board", RR, SHED_X0, SHED_X1, RIDGE_Y - RIDGE_B[0] / 2, RIDGE_Y + RIDGE_B[0] / 2,
    RIDGE_BOT, RIDGE_Z - RIDGE_DROP)
for k, x in enumerate(raf_xs[1:-1], 1):
    if in_hole(x):
        continue
    xa = x + RAF[0] / 2
    zt = COLLAR_Z + COLLAR[1]
    ys = RIDGE_Y - (ROOF_S.z(0, RIDGE_Y) - DV - zt) / S
    yn = RIDGE_Y + (ROOF_N.z(0, RIDGE_Y) - DV - zt) / S
    box(f"Collar_{k:02d}", RR, xa, xa + COLLAR[0], ys + 0.005, yn - 0.005, COLLAR_Z, zt)

# roof boards, split around the tower posts and the stair hole
RB = "Existing/Shed_Roof_Boards"
post_holes = [(post_x(ix) - POST / 2 - HOLE_CL, post_x(ix) + POST / 2 + HOLE_CL,
               post_y(iy) - POST / 2 - HOLE_CL, post_y(iy) + POST / 2 + HOLE_CL)
              for ix in range(NX + 1) for iy in range(NY + 1)]
stair_hole = (RHX0, RHX1, HOLE_Y0, RIDGE_Y - RIDGE_B[0] / 2)
w_h = BOARD[0] / math.sqrt(1 + S * S)
n_board = 0
for side, roof, y_eave, sgn in (("S", ROOF_S, Y_OUT_S - OVERHANG, +1), ("N", ROOF_N, Y_OUT_N + OVERHANG, -1)):
    y = y_eave
    row = 0
    while (RIDGE_Y - y) * sgn > 1e-6:
        yb = y + sgn * w_h
        if (RIDGE_Y - yb) * sgn < 0:
            yb = RIDGE_Y
        ya, yb2 = sorted((y, yb))
        holes = post_holes + ([stair_hole] if side == "S" else [])
        cuts = [(hx0_, hx1_) for hx0_, hx1_, hy0, hy1 in holes if hy0 < yb2 - 1e-6 and hy1 > ya + 1e-6]
        for xa, xb in split_spans([(SHED_X0, SHED_X1)], cuts):
            sloped_x_member(f"RoofBoard_{side}_{row:02d}_{n_board:03d}", RB, xa, xb, ya, yb2, roof,
                            BOARD[1], top_off=BOARD_DZ)
            n_board += 1
        y = yb
        row += 1

# --- terrace deck on the tower top ------------------------------
TD = "Existing/Terrace_Frame"
tj_xs = g2.positions(-POST / 2 - TERR_OVER, X_END + POST / 2 + TERR_OVER, SPACING, TJ[0], GRID0)
TJ_Z0, TJ_Z1 = Z_TERR_GIRT, Z_TERR_JTOP
tvx0, tvx1 = TERR_VOID
for j, x in enumerate(tj_xs):
    if tvx0 + 0.02 < x < tvx1 - 0.02:
        box(f"TerrJoist_{j:02d}_S", TD, x - TJ[0] / 2, x + TJ[0] / 2, -POST / 2 - TERR_OVER, VOID_Y0 - 2 * TJ[0], TJ_Z0, TJ_Z1)
        box(f"TerrJoist_{j:02d}_N", TD, x - TJ[0] / 2, x + TJ[0] / 2, VOID_Y1 + 2 * TJ[0], Y_END + POST / 2 + TERR_OVER, TJ_Z0, TJ_Z1)
    else:
        box(f"TerrJoist_{j:02d}", TD, x - TJ[0] / 2, x + TJ[0] / 2,
            -POST / 2 - TERR_OVER, Y_END + POST / 2 + TERR_OVER, TJ_Z0, TJ_Z1)
left = max(x for x in tj_xs if x <= tvx0 + 0.02)
right = min(x for x in tj_xs if x >= tvx1 - 0.02)
box("TerrHeader_S", TD, left + TJ[0] / 2, right - TJ[0] / 2, VOID_Y0 - 2 * TJ[0], VOID_Y0, TJ_Z0, TJ_Z1)
box("TerrHeader_N", TD, left + TJ[0] / 2, right - TJ[0] / 2, VOID_Y1, VOID_Y1 + 2 * TJ[0], TJ_Z0, TJ_Z1)
deck_nogo = [(post_x(ix) - POST / 2 - HOLE_CL, post_x(ix) + POST / 2 + HOLE_CL,
              post_y(iy) - POST / 2 - HOLE_CL, post_y(iy) + POST / 2 + HOLE_CL)
             for ix in range(HH_IX0, NX + 1) for iy in range(NY + 1)]
deck_nogo.append((tvx0, tvx1, VOID_Y0, VOID_Y1))
framing.boards("DeckBoard", "Existing/Terrace_Deck",
               -POST / 2 - TERR_OVER, X_END + POST / 2 + TERR_OVER,
               -POST / 2 - TERR_OVER, Y_END + POST / 2 + TERR_OVER,
               Z_TERR_JTOP, Z_DECK_TOP, 0.14, gap=0.006, nogo=deck_nogo, along="x")

# --- head house (preserved frame) ------------------------------
HF = "Existing/HeadHouse_Frame"
hh_jxs = g2.positions(HX0, HX1, SPACING, HH_FJ[0], GRID0)
for j, x in enumerate(hh_jxs):
    box(f"HHJoist_{j:02d}", HF, x - HH_FJ[0] / 2, x + HH_FJ[0] / 2, HH_YOUT_S, HH_YOUT_N, Z_HH_GIRT, Z_HH_JTOP)
framing.boards("HHFloor", "Existing/HeadHouse_Floor", HX0, HX1, HH_YOUT_S, HH_YOUT_N, Z_HH_JTOP, Z_HH_FLOOR,
               0.14, gap=0.004, along="x")
HW = "Existing/HeadHouse_Walls"
HH_OPS = {
    "S": [(5.7, 6.9, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)],
    "N": [(8.1, 9.3, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)],
    "W": [(1.5, 2.7, None, Z_HH_FLOOR + 2.1)],               # door to the terrace ladder
    "E": [(1.5, 3.3, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)],
}
framing.stud_wall("HHWall_S", HW, "x", HX0, HX1, HH_YOUT_S, HH_YOUT_S + WALL_T, Z_HH_FLOOR, Z_HH_PLATE,
                  STUD_T, SPACING, grid0=GRID0, double_top=True, openings=HH_OPS["S"])
framing.stud_wall("HHWall_N", HW, "x", HX0, HX1, HH_YOUT_N - WALL_T, HH_YOUT_N, Z_HH_FLOOR, Z_HH_PLATE,
                  STUD_T, SPACING, grid0=GRID0, double_top=True, openings=HH_OPS["N"])
framing.stud_wall("HHWall_W", HW, "y", HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, HX0, HX0 + WALL_T,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True, openings=HH_OPS["W"])
framing.stud_wall("HHWall_E", HW, "y", HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, HX1 - WALL_T, HX1,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True, openings=HH_OPS["E"])
HR = "Existing/HeadHouse_Roof"
hh_raf_xs = [HX0 + HH_RAF[0] / 2] + g2.positions(HX0, HX1, SPACING, HH_RAF[0], GRID0)[1:-1] + [HX1 - HH_RAF[0] / 2]
HH_RIDGE_B = (0.038, 0.184)
hh_ridge_face = {-1: HH_RIDGE_Y - HH_RIDGE_B[0] / 2, +1: HH_RIDGE_Y + HH_RIDGE_B[0] / 2}
for k, x in enumerate(hh_raf_xs):
    for side, sgn, roof, y_out, d in (("S", -1, HH_ROOF_S, HH_YOUT_S, (0, 1)), ("N", +1, HH_ROOF_N, HH_YOUT_N, (0, -1))):
        sloped_member(f"HHRafter_{k:02d}{side}", HR, (x, y_out), d, HH_S, HH_RAF_TOP0, HH_RAF[1], HH_RAF[0],
                      0.0, abs(HH_RIDGE_Y - y_out) + 0.5, clips=[vz(Z_HH_PLATE, +1), vy(hh_ridge_face[sgn], sgn)])
        sloped_member(f"HHRafter_{k:02d}{side}_tail", HR, (x, y_out), d, HH_S, HH_RAF_TOP0, HH_RAF[1], HH_RAF[0],
                      -0.3, 0.0)
HH_RIDGE_DROP = HH_RIDGE_B[0] / 2 * HH_S
HH_RIDGE_BOT = HH_RIDGE_Z - HH_RIDGE_B[1] - HH_RIDGE_DROP
box("HH_Ridge", HR, HX0, HX1, HH_RIDGE_Y - HH_RIDGE_B[0] / 2, HH_RIDGE_Y + HH_RIDGE_B[0] / 2,
    HH_RIDGE_BOT, HH_RIDGE_Z - HH_RIDGE_DROP)
for k, x in enumerate(hh_raf_xs[1:-1], 1):
    xa = x + HH_RAF[0] / 2
    box(f"HHTie_{k:02d}", HR, xa, xa + 0.038, HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, Z_HH_PLATE, Z_HH_PLATE + 0.140)
# gable studs, 38 x 140 in the wall zone (v01-v07 had 38 x 38 sticks here), under the end rafters
def hh_roof_under(y):
    r = HH_ROOF_S if y <= HH_RIDGE_Y else HH_ROOF_N
    return r.z(0, y) - HH_DV
for side, x0, x1 in (("W", HX0, HX0 + WALL_T), ("E", HX1 - WALL_T, HX1)):
    for j, y in enumerate(g2.positions(HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, SPACING, STUD_T, GRID0)[1:-1]):
        if abs(y - HH_RIDGE_Y) < HH_RIDGE_B[0] / 2 + STUD_T / 2 + 0.01:
            continue
        zt = min(hh_roof_under(y - STUD_T / 2), hh_roof_under(y + STUD_T / 2)) - 0.002
        box(f"HHGable_{side}_{j:02d}", HW, x0, x1, y - STUD_T / 2, y + STUD_T / 2, Z_HH_PLATE, zt)

# ==================================================================
# ENVELOPE

# --- shed outriggers (photo: a row of projecting beam ends under the south
# eave carrying a narrow canopy). 50 x 150, each bolted to the side of a real
# stud or king stud (on the side away from the window), passing through both
# claddings, sloping top for the canopy, a 50 x 100 knee at 45 degrees from
# the outrigger underside through the clapboard to a foot lapped on the same
# stud inside the cavity.
OR = "Existing/Shed_Outriggers"
OUTRIG = (0.05, 0.15)
OUTRIG_Z0 = 2.45                                 # underside: above the window lintels (2.25)
OUTRIG_TOP_IN, OUTRIG_TOP_OUT = 2.60, 2.52       # sloping top: at the inner end / at the tip
OUTRIG_REACH, OUTRIG_IN = 0.9, 0.3
Y_TIP, Y_IN = SHED_Y0 - OUTRIG_REACH, SHED_Y0 + WALL_T + OUTRIG_IN
KNEE_B = (0.05, 0.10)                            # knee section: width (x), depth
KNEE_REACH = 0.55                                # knee meets the outrigger underside this far out
KNEE_FOOT_Y = SHED_Y0 + WALL_T - 0.05            # foot inside the cavity; its end corners stay 15 mm off the interior boards

def outrig_top(y):
    return OUTRIG_TOP_IN + (OUTRIG_TOP_OUT - OUTRIG_TOP_IN) * (Y_IN - y) / (Y_IN - Y_TIP)

# candidate studs on the south wall: regular studs on the grid (skipped in the
# opening zones exactly as stud_wall does) and the king studs beside each opening
_s_ops = SHED_OPS["S"]
_regular = [c for c in g2.positions(SHED_X0, SHED_X1, SPACING, STUD_T, GRID0)
            if not any(aa - 2.5 * STUD_T < c < ab + 2.5 * STUD_T for aa, ab, _, _ in _s_ops)]
_studs = [(c, 0) for c in _regular]                                   # (centre, allowed side: 0 = either)
for aa, ab, _, _ in _s_ops:
    _studs.append((aa - 1.5 * STUD_T, -1))                            # king left: outrigger on its west
    _studs.append((ab + 1.5 * STUD_T, +1))                            # king right: outrigger on its east
OUTRIG_TARGETS = [0.9 + 1.2 * i for i in range(8)]
OUTRIG_XS = []
for tx in OUTRIG_TARGETS:
    c, side = min(_studs, key=lambda sc: abs(sc[0] - tx))
    if side == 0:
        side = 1 if tx >= c else -1
    xc = c + side * (STUD_T / 2 + OUTRIG[0] / 2)
    assert not any(aa - 2 * STUD_T - 1e-6 < xc < ab + 2 * STUD_T + 1e-6 for aa, ab, _, _ in _s_ops), xc
    OUTRIG_XS.append(xc)
OUTRIG_HOLES, KNEE_HOLES, OUTRIG_HOLES_IN = [], [], []
for i, xc in enumerate(OUTRIG_XS):
    xa, xb = xc - OUTRIG[0] / 2, xc + OUTRIG[0] / 2
    prism_x(f"Outrigger_{i:02d}", OR, xa, xb,
            [(Y_TIP, OUTRIG_Z0), (Y_IN, OUTRIG_Z0), (Y_IN, OUTRIG_TOP_IN), (Y_TIP, OUTRIG_TOP_OUT)])
    # knee: from the foot inside the cavity up to the outrigger underside at KNEE_REACH
    y_top = SHED_Y0 - KNEE_REACH
    z_foot = OUTRIG_Z0 - (KNEE_FOOT_Y - y_top)
    planes.member(f"Outrigger_{i:02d}_Knee", OR, (xc, KNEE_FOOT_Y, z_foot), (xc, y_top, OUTRIG_Z0),
                  KNEE_B[0], KNEE_B[1], (1, 0, 0), n0=None, n1=(0, 0, -1))
    OUTRIG_HOLES.append((xa - 0.01, xb + 0.01, OUTRIG_Z0 - 0.01, OUTRIG_TOP_IN + 0.01))
    OUTRIG_HOLES_IN.append((xa - 0.01, xb + 0.01, OUTRIG_Z0 - 0.01, OUTRIG_TOP_IN + 0.01))
    # the knee crosses the clapboard between y = SHED_Y0 - CLAP_T and SHED_Y0
    hz = KNEE_B[1] / 2 * math.sqrt(2) + 0.01
    z_at_wall = OUTRIG_Z0 - (SHED_Y0 - y_top)
    KNEE_HOLES.append((xa - 0.01, xb + 0.01, z_at_wall - hz, z_at_wall + CLAP_T + hz))
# canopy: 19 x 184 boards along X on the sloping outrigger tops, from the tip
# to the clapboard face, split at every second outrigger
CANOPY_X = [(OUTRIG_XS[0] - OUTRIG[0] / 2 - 0.1, OUTRIG_XS[3]), (OUTRIG_XS[3], OUTRIG_XS[6]),
            (OUTRIG_XS[6], OUTRIG_XS[-1] + OUTRIG[0] / 2 + 0.1)]
slope_c = (OUTRIG_TOP_IN - OUTRIG_TOP_OUT) / (Y_IN - Y_TIP)
w_c = BOARD[0] / math.sqrt(1 + slope_c * slope_c)
dz_c = BOARD[1] * math.sqrt(1 + slope_c * slope_c)
y = Y_TIP
row = 0
while y < SHED_Y0 - CLAP_T - 1e-6:
    yb = min(y + w_c, SHED_Y0 - CLAP_T)
    for j, (xa, xb) in enumerate(CANOPY_X):
        prism_x(f"Canopy_{row:02d}_{j}", "Existing/Shed_Outriggers", xa, xb,
                [(y, outrig_top(y)), (yb, outrig_top(yb)), (yb, outrig_top(yb) + dz_c), (y, outrig_top(y) + dz_c)])
    y = yb
    row += 1

# --- shed clapboards: 19 x 160 exposure rows, staggered 3.6 m boards, cut
# around the openings, the outriggers and the knees (framing.clad = tile rows).
CLAP_Z0 = 0.05
CLAP_ZTOP = PLATE_TOP - S * (WALL_T + CLAP_T) - 0.005   # under the rafter tails at the cladding face
SC = "New/Cladding_Shed"
def op_holes(ops, z_floor):
    return [(a0, a1, z_floor if zs is None else zs, zh) for a0, a1, zs, zh in ops]
framing.clad("Clap_S", SC, "x", SHED_X0 - CLAP_T, SHED_X1 + CLAP_T, SHED_Y0 - CLAP_T, SHED_Y0, CLAP_Z0, CLAP_ZTOP,
             sheet_w=CLAP_L, sheet_l=CLAP_ROW, holes=op_holes(SHED_OPS["S"], 0.0) + OUTRIG_HOLES + KNEE_HOLES, stagger=True)
framing.clad("Clap_N", SC, "x", SHED_X0 - CLAP_T, SHED_X1 + CLAP_T, SHED_Y1, SHED_Y1 + CLAP_T, CLAP_Z0, CLAP_ZTOP,
             sheet_w=CLAP_L, sheet_l=CLAP_ROW, holes=op_holes(SHED_OPS["N"], 0.0), stagger=True)
framing.clad("Clap_W", SC, "y", SHED_Y0, SHED_Y1, SHED_X0 - CLAP_T, SHED_X0, CLAP_Z0, PLATE_TOP,
             sheet_w=CLAP_L, sheet_l=CLAP_ROW, holes=op_holes(SHED_OPS["W"], 0.0), stagger=True)
framing.clad("Clap_E", SC, "y", SHED_Y0, SHED_Y1, SHED_X1, SHED_X1 + CLAP_T, CLAP_Z0, PLATE_TOP,
             sheet_w=CLAP_L, sheet_l=CLAP_ROW, holes=op_holes(SHED_OPS["E"], 0.0), stagger=True)
# gable clapboards above the plate, clipped by the roof top surface (the rake is flush)
gable_pieces("ClapGable_W", SC, SHED_X0 - CLAP_T, SHED_X0, SHED_Y0 - CLAP_T, SHED_Y1 + CLAP_T, PLATE_TOP,
             roof_boards_top, RIDGE_Y, CLAP_ROW, along_y=False)
gable_pieces("ClapGable_E", SC, SHED_X1, SHED_X1 + CLAP_T, SHED_Y0 - CLAP_T, SHED_Y1 + CLAP_T, PLATE_TOP,
             roof_boards_top, RIDGE_Y, CLAP_ROW, along_y=False)

# --- shed interior boards: the same rows on the inner faces, up to the plate,
# then gable rows clipped under the rafters, holed at the ridge board.
CI = "New/Cladding_Interior"
SY_IN_S, SY_IN_N = SHED_Y0 + WALL_T, SHED_Y1 - WALL_T
SX_IN_W, SX_IN_E = SHED_X0 + WALL_T, SHED_X1 - WALL_T
board_rows("ShedIn_S", CI, "x", SX_IN_W, SX_IN_E, SY_IN_S, SY_IN_S + IB_T, CLAP_Z0, PLATE_TOP, CLAP_ROW,
           op_holes(SHED_OPS["S"], 0.0) + OUTRIG_HOLES_IN)
board_rows("ShedIn_N", CI, "x", SX_IN_W, SX_IN_E, SY_IN_N - IB_T, SY_IN_N, CLAP_Z0, PLATE_TOP, CLAP_ROW,
           op_holes(SHED_OPS["N"], 0.0))
MB_HOLE = (mb_y0 - 0.005, mb_y1 + 0.005, MB_Z0 - 0.005, PLATE_TOP + 0.01)        # the mid beam bears on the gable walls
board_rows("ShedIn_W", CI, "y", SY_IN_S + IB_T, SY_IN_N - IB_T, SX_IN_W, SX_IN_W + IB_T, CLAP_Z0, PLATE_TOP, CLAP_ROW,
           op_holes(SHED_OPS["W"], 0.0) + [MB_HOLE])
board_rows("ShedIn_E", CI, "y", SY_IN_S + IB_T, SY_IN_N - IB_T, SX_IN_E - IB_T, SX_IN_E, CLAP_Z0, PLATE_TOP, CLAP_ROW,
           op_holes(SHED_OPS["E"], 0.0) + [MB_HOLE])
ridge_hole = (RIDGE_Y - RIDGE_B[0] / 2 - 0.005, RIDGE_Y + RIDGE_B[0] / 2 + 0.005, RIDGE_BOT - 0.005, 99.0)
gable_pieces("ShedInGable_W", CI, SX_IN_W, SX_IN_W + IB_T, SY_IN_S + IB_T, SY_IN_N - IB_T, PLATE_TOP,
             lambda y: roof_under(y) - 0.002, RIDGE_Y, CLAP_ROW, along_y=False, holes=[ridge_hole])
gable_pieces("ShedInGable_E", CI, SX_IN_E - IB_T, SX_IN_E, SY_IN_S + IB_T, SY_IN_N - IB_T, PLATE_TOP,
             lambda y: roof_under(y) - 0.002, RIDGE_Y, CLAP_ROW, along_y=False, holes=[ridge_hole])

# --- tower infill walls: platform stud walls on each slab, inside the post
# line. Storeys 1 and 2: explicit varied openings (full height = None sill);
# the top storey carries the clerestory band on all four faces.
IW = "New/Infill_Walls"
GZ = "New/Glazing"
W_OFF0 = GLB[0] / 2 + SLAB_GAP                     # 0.136: wall zone starts here, measured from the post row
CLERE_SILL = 1.5
FULL_HEAD = 2.6                                    # full-height window head above the slab (lintel + plate above)
WINDOWS = {                                        # (a0, a1, sill | None, head), relative to the slab top
    (1, "S"): [(0.6, 1.8, 0.85, 2.25), (2.85, 4.35, None, FULL_HEAD), (7.7, 9.1, 0.85, 2.25)],
    (2, "S"): [(1.0, 1.9, 1.5, 2.3), (5.25, 6.75, None, FULL_HEAD), (7.9, 8.9, 0.85, 2.25)],
    (1, "N"): [(2.85, 4.35, None, FULL_HEAD), (7.7, 8.9, 0.85, 2.25)],
    (2, "N"): [(0.6, 1.8, 0.85, 2.25), (5.5, 6.4, 1.5, 2.3)],
    (1, "W"): [(2.95, 4.15, None, FULL_HEAD)],
    (2, "W"): [(0.7, 1.9, 0.85, 2.25)],
    (1, "E"): [(0.7, 1.9, 0.85, 2.25)],
    (2, "E"): [(3.2, 4.0, 1.5, 2.3)],
}
TOWER_HOLES = {"S": [], "N": [], "W": [], "E": []}  # absolute (a0, a1, z0, z1) per face, for the claddings

def infill_openings(k, face, a_posts):
    z_top = z_slab_top(k)
    if k == N_UPPER:
        return [(a_posts[i] + POST / 2 + 0.3, a_posts[i + 1] - POST / 2 - 0.3, z_top + CLERE_SILL, z_top + 2.35)
                for i in range(len(a_posts) - 1)]
    return [(a0, a1, None if zs is None else z_top + zs, z_top + zh) for a0, a1, zs, zh in WINDOWS[(k, face)]]

TOWER_WALLS = []                                   # (k, face, along, a0, a1, b0, b1, z0, z1, ops)
for k in range(1, N_UPPER + 1):
    z0 = z_slab_top(k)
    z1 = z_slab_under(k + 1) if k < N_UPPER else Z_TERR_GIRT
    xs = [post_x(ix) for ix in range(NX + 1)]
    ys = [post_y(iy) for iy in range(NY + 1)]
    Y_MID_A, Y_MID_B = post_y(1) - GLB[0] / 2 - SLAB_GAP, post_y(1) + GLB[0] / 2 + SLAB_GAP
    walls = [("S", "x", X_IN_W, X_IN_E, W_OFF0, W_OFF0 + WALL_T, infill_openings(k, "S", xs)),
             ("N", "x", X_IN_W, X_IN_E, Y_END - W_OFF0 - WALL_T, Y_END - W_OFF0, infill_openings(k, "N", xs))]
    for face, b0, b1 in (("W", X_IN_W, X_IN_W + WALL_T), ("E", X_IN_E - WALL_T, X_IN_E)):
        ops = infill_openings(k, face, ys)
        walls.append((face + "0", "y", W_OFF0 + WALL_T, Y_MID_A, b0, b1, [o for o in ops if o[1] <= Y_MID_A]))
        walls.append((face + "1", "y", Y_MID_B, Y_END - W_OFF0 - WALL_T, b0, b1, [o for o in ops if o[0] >= Y_MID_B]))
    for face, along, a0, a1, b0, b1, ops in walls:
        for oa, ob, _, _ in ops:
            assert a0 + 2 * STUD_T <= oa and ob + 2 * STUD_T <= a1, f"opening {oa, ob} outside wall {face} L{k}"
        framing.stud_wall(f"Infill_L{k}_{face}", IW, along, a0, a1, b0, b1, z0, z1, STUD_T, SPACING,
                          grid0=GRID0, openings=ops, lintel_d=0.15)
        TOWER_HOLES[face[0]] += op_holes(ops, z0)
        TOWER_WALLS.append((k, face, along, a0, a1, b0, b1, z0, z1, ops))
        for j, (oa, ob, zs, zh) in enumerate(ops):
            bm = (b0 + b1) / 2
            zs = z0 if zs is None else zs
            if along == "x":
                box(f"Glass_L{k}_{face}_{j}", GZ, oa, ob, bm - GLASS_T / 2, bm + GLASS_T / 2, zs, zh)
            else:
                box(f"Glass_L{k}_{face}_{j}", GZ, bm - GLASS_T / 2, bm + GLASS_T / 2, oa, ob, zs, zh)

# --- tower exterior cladding: gapless horizontal boards 25 x 140 against the
# outer face of the infill walls, between the posts, in bands split by the
# slabs (the slab edges show as floor bands, the beams sit outside the boards).
# The lowest band runs down to the shed roof and closes the former open zone;
# on the W/E faces its rows are cut to the roof slope.
TC = "New/Cladding_Tower"
CL_B = (W_OFF0 - CB_T, W_OFF0)                      # board zone measured from the post row, inward
BANDS = [(None, z_slab_under(1))] + [(z_slab_top(k), z_slab_under(k + 1) if k < N_UPPER else Z_TERR_GIRT)
                                     for k in range(1, N_UPPER + 1)]
for kb, (z0, z1) in enumerate(BANDS):
    for ix in range(NX):
        a0, a1 = post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2
        zs = roof_boards_top(CL_B[1]) + 0.002 if z0 is None else z0
        board_rows(f"TowerClad_S_B{kb}_{ix}", TC, "x", a0, a1, CL_B[0], CL_B[1], zs, z1, CB_W, TOWER_HOLES["S"])
        zn = roof_boards_top(Y_END - CL_B[1]) + 0.002 if z0 is None else z0
        board_rows(f"TowerClad_N_B{kb}_{ix}", TC, "x", a0, a1, Y_END - CL_B[1], Y_END - CL_B[0], zn, z1, CB_W, TOWER_HOLES["N"])
    for iy in range(NY):
        a0, a1 = post_y(iy) + POST / 2, post_y(iy + 1) - POST / 2
        a0 = max(a0, CL_B[1])                                   # past the S front boards at the corner
        a1 = min(a1, Y_END - CL_B[1])                           # and the N ones
        for face, b0, b1 in (("W", CL_B[0], CL_B[1]), ("E", X_END - CL_B[1], X_END - CL_B[0])):
            if z0 is not None:
                board_rows(f"TowerClad_{face}_B{kb}_{iy}", TC, "y", a0, a1, b0, b1, z0, z1, CB_W, TOWER_HOLES[face])
            else:
                # rows from the lowest roof point in the bay, cut to the roof slope
                z_lo = min(roof_boards_top(a0), roof_boards_top(a1)) + 0.002
                n = 0
                z = z_lo
                while z < z1 - 1e-6:
                    zb = min(z + CB_W, z1)
                    for side in (-1, +1):
                        q = g2.clip(g2.rect(a0, a1, z, zb), (RIDGE_Y, 0.0), (side, 0.0))
                        if len(q) < 3:
                            continue
                        rf = ROOF_S if side < 0 else ROOF_N
                        q = clip_below_line(q, RIDGE_Y, RIDGE_Y + side, lambda yy, rf=rf: rf.z(0, yy) + BOARD_DZ + 0.002, True)
                        if len(q) >= 3 and g2.area(q) > 1e-5:
                            prism_x(f"TowerClad_{face}_B{kb}_{iy}_{n:03d}", TC, b0, b1, q)
                            n += 1
                    z = zb

# --- tower interior boards: the same rows on the inner face of every wall segment
for (k, face, along, a0, a1, b0, b1, z0, z1, ops) in TOWER_WALLS:
    if along == "x":
        bb = (b1, b1 + IB_T) if face == "S" else (b0 - IB_T, b0)
        board_rows(f"TowerIn_L{k}_{face}", CI, "x", a0 + WALL_T, a1 - WALL_T, bb[0], bb[1], z0, z1, CB_W, op_holes(ops, z0))
    else:
        bb = (b1, b1 + IB_T) if face[0] == "W" else (b0 - IB_T, b0)
        aa0 = a0 + IB_T if face.endswith("0") else a0            # past the S / N interior boards
        aa1 = a1 - IB_T if face.endswith("1") else a1
        board_rows(f"TowerIn_L{k}_{face}", CI, "y", aa0, aa1, bb[0], bb[1], z0, z1, CB_W, op_holes(ops, z0))

# --- trestle relic: the photo's conveyor leg east of the shed --------------
TR = "Existing/Trestle"
X_TR = SHED_X1 + 1.5
TR_YS = (1.2, 3.6)
TR_TOP = Z_TERR_GIRT + 0.6
for j, y in enumerate(TR_YS):
    box(f"Trestle_Plinth_{j}", "Foundation/Plinths", X_TR - PLINTH_W / 2, X_TR + PLINTH_W / 2,
        y - PLINTH_W / 2, y + PLINTH_W / 2, 0.0, PLINTH_H)
    box(f"Trestle_Post_{j}", TR, X_TR - POST / 2, X_TR + POST / 2, y - POST / 2, y + POST / 2, PLINTH_H, TR_TOP)
TR_LEVELS = GIRT_TOPS + [TR_TOP]
for k, zt in enumerate(TR_LEVELS):
    for side, sgn in (("W", -1), ("E", +1)):
        girt_run(f"Trestle_Girt_L{k}_{side}", TR, "y", TR_YS[0] - POST / 2, TR_YS[1] + POST / 2,
                 X_TR + sgn * POST / 2, sgn, zt)
TR_BAYS = [(PLINTH_H + 0.15, TR_LEVELS[0] - GIRT[1])] + \
          [(TR_LEVELS[k], TR_LEVELS[k + 1] - GIRT[1]) for k in range(len(TR_LEVELS) - 1)]
ya, yb = TR_YS[0] + POST / 2, TR_YS[1] - POST / 2
for k, (z_lo, z_hi) in enumerate(TR_BAYS):
    if z_hi - z_lo < 1.0:
        continue
    phi = 2 * math.atan2(yb - ya, z_hi - z_lo)
    lap = BRACE * (1 + math.cos(phi)) / math.sin(phi) + 0.05
    centre = ((ya + yb) / 2, (z_lo + z_hi) / 2)
    framing.halved_brace(f"Trestle_Cross_L{k}_A", TR, (X_TR, ya, z_lo), (X_TR, yb, z_hi), BRACE, BRACE,
                         (1, 0, 0), (0, 1, 0), (0, -1, 0), (X_TR, centre[0], centre[1]), lap, +1)
    framing.halved_brace(f"Trestle_Cross_L{k}_B", TR, (X_TR, yb, z_lo), (X_TR, ya, z_hi), BRACE, BRACE,
                         (1, 0, 0), (0, -1, 0), (0, 1, 0), (X_TR, centre[0], centre[1]), lap, -1)
TIE = (0.10, 0.20)
TIE_X0 = X_END + POST / 2 + GIRT[0]
for j, y in enumerate(TR_YS):
    box(f"Trestle_Tie_{j}", TR, TIE_X0, X_TR - POST / 2 - GIRT[0], y - TIE[0] / 2, y + TIE[0] / 2,
        Z_TERR_GIRT - TIE[1], Z_TERR_GIRT)

# --- terrace guard: 90 x 90 posts at 1.2 m, top rail at 1.07 (CMHC), mid rail
GU = "New/Guards"
GP, RAIL = 0.09, (0.04, 0.09)
DX0, DX1 = -POST / 2 - TERR_OVER, X_END + POST / 2 + TERR_OVER
DY0, DY1 = -POST / 2 - TERR_OVER, Y_END + POST / 2 + TERR_OVER
INSET = 0.05
def guard_line_z(prefix, along, a0, a1, b_c, z_top):
    pos = g2.positions(a0, a1, 1.2, GP)
    zr = z_top + GUARD_H - RAIL[0]
    for i, a in enumerate(pos):
        if along == "x":
            box(f"{prefix}_Post_{i:02d}", GU, a - GP / 2, a + GP / 2, b_c - GP / 2, b_c + GP / 2, z_top, zr)
        else:
            box(f"{prefix}_Post_{i:02d}", GU, b_c - GP / 2, b_c + GP / 2, a - GP / 2, a + GP / 2, z_top, zr)
    if along == "x":
        box(f"{prefix}_TopRail", GU, a0 - GP / 2, a1 + GP / 2, b_c - RAIL[1] / 2, b_c + RAIL[1] / 2, zr, zr + RAIL[0])
    else:
        box(f"{prefix}_TopRail", GU, b_c - RAIL[1] / 2, b_c + RAIL[1] / 2, a0 + GP / 2, a1 - GP / 2, zr, zr + RAIL[0])
    zm = z_top + 0.5
    for i in range(len(pos) - 1):
        pa, pb = pos[i] + GP / 2, pos[i + 1] - GP / 2
        if along == "x":
            box(f"{prefix}_MidRail_{i:02d}", GU, pa, pb, b_c - GP / 2, b_c + GP / 2, zm, zm + RAIL[0])
        else:
            box(f"{prefix}_MidRail_{i:02d}", GU, b_c - GP / 2, b_c + GP / 2, pa, pb, zm, zm + RAIL[0])

guard_line_z("Guard_S", "x", DX0 + INSET + GP / 2, DX1 - INSET - GP / 2, DY0 + INSET + GP / 2, Z_DECK_TOP)
guard_line_z("Guard_N", "x", DX0 + INSET + GP / 2, DX1 - INSET - GP / 2, DY1 - INSET - GP / 2, Z_DECK_TOP)
guard_line_z("Guard_W", "y", DY0 + INSET + GP / 2 + GP, DY1 - INSET - GP / 2 - GP, DX0 + INSET + GP / 2, Z_DECK_TOP)
guard_line_z("Guard_E", "y", DY0 + INSET + GP / 2 + GP, DY1 - INSET - GP / 2 - GP, DX1 - INSET - GP / 2, Z_DECK_TOP)

def void_guard(prefix, x0, x1, z_top, landing_side):
    g_off = INSET + GP / 2
    for name, y_c in (("S", VOID_Y0 - g_off), ("N", VOID_Y1 + g_off)):
        guard_line_z(f"{prefix}_{name}", "x", x0 - g_off, x1 + g_off, y_c, z_top)
    x_end = x0 - g_off if landing_side > 0 else x1 + g_off
    guard_line_z(f"{prefix}_End", "y", VOID_Y0 - g_off + GP, VOID_Y1 + g_off - GP, x_end, z_top)

for k in range(1, N_UPPER + 1):
    vx0, vx1 = VOIDS[k]
    lands_east = (k == 1) or (k % 2 == 1)
    void_guard(f"VoidGuard_L{k}", vx0, vx1, z_slab_top(k), +1 if lands_east else -1)
void_guard("VoidGuard_T", TERR_VOID[0], TERR_VOID[1], Z_DECK_TOP, -1 if N_UPPER % 2 == 1 else +1)

# --- head house cladding: gapless vertical boards outside and inside, gables
# cut to the roof (outside: board top surface; inside: rafter underside),
# the inside gables holed at the ridge board; roof boards on the rafters.
HC = "New/Cladding_HeadHouse"
HHC_Z0 = Z_HH_GIRT                               # above the exposed floor girts
HHC_ZTOP = Z_HH_PLATE - HH_S * (WALL_T + CB_T) - 0.005
hh_top_of = lambda y: (HH_ROOF_S if y <= HH_RIDGE_Y else HH_ROOF_N).z(0, y) + HH_BOARD_DZ
board_columns("HHClad_S", HC, "x", HX0 - CB_T, HX1 + CB_T, HH_YOUT_S - CB_T, HH_YOUT_S, HHC_Z0, HHC_ZTOP, CB_W, op_holes(HH_OPS["S"], Z_HH_FLOOR))
board_columns("HHClad_N", HC, "x", HX0 - CB_T, HX1 + CB_T, HH_YOUT_N, HH_YOUT_N + CB_T, HHC_Z0, HHC_ZTOP, CB_W, op_holes(HH_OPS["N"], Z_HH_FLOOR))
def columns(a0, a1, w):
    out, a = [], a0
    while a < a1 - 1e-6:
        out.append((a, min(a + w, a1)))
        a += w
    return out
for side, x0, x1 in (("W", HX0 - CB_T, HX0), ("E", HX1, HX1 + CB_T)):
    gable_pieces(f"HHClad_{side}", HC, x0, x1, HH_YOUT_S, HH_YOUT_N, HHC_Z0, hh_top_of, HH_RIDGE_Y,
                 columns(HH_YOUT_S, HH_YOUT_N, CB_W), along_y=True, holes=op_holes(HH_OPS[side], Z_HH_FLOOR))
# interior: on the inner faces, floor to plate on the long walls, up to the rafters on the gables
HY_IN_S, HY_IN_N = HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T
HX_IN_W, HX_IN_E = HX0 + WALL_T, HX1 - WALL_T
board_columns("HHIn_S", CI, "x", HX_IN_W, HX_IN_E, HY_IN_S, HY_IN_S + IB_T, Z_HH_FLOOR, Z_HH_PLATE, CB_W, op_holes(HH_OPS["S"], Z_HH_FLOOR))
board_columns("HHIn_N", CI, "x", HX_IN_W, HX_IN_E, HY_IN_N - IB_T, HY_IN_N, Z_HH_FLOOR, Z_HH_PLATE, CB_W, op_holes(HH_OPS["N"], Z_HH_FLOOR))
hh_ridge_hole = (HH_RIDGE_Y - HH_RIDGE_B[0] / 2 - 0.005, HH_RIDGE_Y + HH_RIDGE_B[0] / 2 + 0.005, HH_RIDGE_BOT - 0.005, 99.0)
for side, x0, x1 in (("W", HX_IN_W, HX_IN_W + IB_T), ("E", HX_IN_E - IB_T, HX_IN_E)):
    gable_pieces(f"HHIn_{side}", CI, x0, x1, HY_IN_S + IB_T, HY_IN_N - IB_T, Z_HH_FLOOR,
                 lambda y: hh_roof_under(y) - 0.002, HH_RIDGE_Y, columns(HY_IN_S + IB_T, HY_IN_N - IB_T, CB_W),
                 along_y=True, holes=op_holes(HH_OPS[side], Z_HH_FLOOR) + [hh_ridge_hole])
# roof boards
HB = "New/Roofing"
w_hh = BOARD[0] / math.sqrt(1 + HH_S * HH_S)
for side, roof, y_eave, sgn in (("S", HH_ROOF_S, HH_YOUT_S - 0.3, +1), ("N", HH_ROOF_N, HH_YOUT_N + 0.3, -1)):
    y = y_eave
    row = 0
    while (HH_RIDGE_Y - y) * sgn > 1e-6:
        yb = y + sgn * w_hh
        if (HH_RIDGE_Y - yb) * sgn < 0:
            yb = HH_RIDGE_Y
        ya, yb2 = sorted((y, yb))
        sloped_x_member(f"HHRoofBoard_{side}_{row:02d}", HB, HX0, HX1, ya, yb2, roof, BOARD[1], top_off=HH_BOARD_DZ)
        y = yb
        row += 1

# --- ladder from the deck to the head house door (W gable), stiles 60 x 90
# leaning on the floor girt face, rungs 30 mm square at 300 mm
LD = "New/Ladder"
LADDER_TOP_Z = Z_HH_GIRT - 0.05                     # leans on the girt, the floor is one step above
LADDER_X_TOP = HX0 - GIRT[0]                        # the girt's outer face
LADDER_ANGLE = math.radians(75)
LADDER_RUN = (LADDER_TOP_Z - Z_DECK_TOP) / math.tan(LADDER_ANGLE)
LADDER_YS = (2.0, 2.6)                             # inside the door (1.5..2.7), north of the deck void guard (y 1.94)
STILE = (0.06, 0.09)
for j, y in enumerate(LADDER_YS):
    planes.member(f"Ladder_Stile_{j}", LD, (LADDER_X_TOP - LADDER_RUN, y, Z_DECK_TOP), (LADDER_X_TOP, y, LADDER_TOP_Z),
                  STILE[0], STILE[1], (0, 1, 0), n0=(0, 0, 1), n1=(-1, 0, 0))
n_rungs = int((LADDER_TOP_Z - Z_DECK_TOP) / 0.3)
for i in range(1, n_rungs + 1):
    f = i * 0.3 / (LADDER_TOP_Z - Z_DECK_TOP)
    cx = LADDER_X_TOP - LADDER_RUN + f * LADDER_RUN
    cz = Z_DECK_TOP + f * (LADDER_TOP_Z - Z_DECK_TOP)
    box(f"Ladder_Rung_{i:02d}", LD, cx - 0.015, cx + 0.015, LADDER_YS[0] + STILE[0] / 2, LADDER_YS[1] - STILE[0] / 2,
        cz - 0.015, cz + 0.015)

# --- fixtures: glass in the shed and head house windows, leaves in the doors
DR = "New/Doors"
def fixtures(prefix, ops, along, b0, b1, z_floor):
    bm = (b0 + b1) / 2
    for j, (a0, a1, zs, zh) in enumerate(ops):
        if zs is None:
            t_, coll, name = DOOR_T, DR, f"{prefix}_Door_{j}"
            zs = z_floor
        else:
            t_, coll, name = GLASS_T, GZ, f"{prefix}_Glass_{j}"
        if along == "x":
            box(name, coll, a0, a1, bm - t_ / 2, bm + t_ / 2, zs, zh)
        else:
            box(name, coll, bm - t_ / 2, bm + t_ / 2, a0, a1, zs, zh)
fixtures("Shed_S", SHED_OPS["S"], "x", SHED_Y0, SHED_Y0 + WALL_T, 0.0)
fixtures("Shed_N", SHED_OPS["N"], "x", SHED_Y1 - WALL_T, SHED_Y1, 0.0)
fixtures("Shed_W", SHED_OPS["W"], "y", SHED_X0, SHED_X0 + WALL_T, 0.0)
fixtures("Shed_E", SHED_OPS["E"], "y", SHED_X1 - WALL_T, SHED_X1, 0.0)
fixtures("HH_S", HH_OPS["S"], "x", HH_YOUT_S, HH_YOUT_S + WALL_T, Z_HH_FLOOR)
fixtures("HH_N", HH_OPS["N"], "x", HH_YOUT_N - WALL_T, HH_YOUT_N, Z_HH_FLOOR)
fixtures("HH_W", HH_OPS["W"], "y", HX0, HX0 + WALL_T, Z_HH_FLOOR)
fixtures("HH_E", HH_OPS["E"], "y", HX1 - WALL_T, HX1, Z_HH_FLOOR)

# --- steel seat brackets under every beam end at a post (Handbook 4-10) ------
ST = "New/Connections"
SEAT_T, SEAT_L, SEAT_LEG, SEAT_IN = 0.012, 0.15, 0.10, 0.03
def seat(name, axis, a_face, dir_a, b0, b1, z_beam_bot):
    a_in = a_face + dir_a * SEAT_L
    a_leg = a_face + dir_a * SEAT_T
    box(name + "_Plate", ST, min(a_face, a_in), max(a_face, a_in), b0, b1, z_beam_bot - SEAT_T, z_beam_bot)
    box(name + "_Leg", ST, min(a_face, a_leg), max(a_face, a_leg), b0, b1, z_beam_bot - SEAT_T - SEAT_LEG, z_beam_bot - SEAT_T)

for o in list(bpy.data.objects):
    if o.name.startswith("Beam_") and o.type == "MESH":
        lo = [o.matrix_world @ Vector(c) for c in o.bound_box]
        x0, x1 = min(p.x for p in lo), max(p.x for p in lo)
        y0, y1 = min(p.y for p in lo), max(p.y for p in lo)
        zb = min(p.z for p in lo)
        seat(f"Seat_{o.name}_W", "x", x0, +1, y0 + SEAT_IN, y1 - SEAT_IN, zb)
        seat(f"Seat_{o.name}_E", "x", x1, -1, y0 + SEAT_IN, y1 - SEAT_IN, zb)

n = len([o for o in bpy.data.objects if o.type == "MESH"])
print(f"Built experiment 14 v09: {n} elements; L1 slab top {Z_L1}, terrace deck {Z_DECK_TOP:.3f}, "
      f"head house floor {Z_HH_FLOOR:.3f}, ridge {HH_RIDGE_Z:.3f}; ground stair lands at x = {G_TOP_X:.2f}; "
      f"outriggers at {[round(x, 3) for x in OUTRIG_XS]}")
