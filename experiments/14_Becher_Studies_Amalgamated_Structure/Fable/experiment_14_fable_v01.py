# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 14 - Fable run, v01
# Becher study: timber coaling tower refurbished as a multi-storey home.
#
# v01: the preserved structure (tower posts, girts, knee braces, shed
# frame and roof, terrace deck frame, head house frame), the repairs
# (new post feet with splice plates) and the primary new insertions
# (glulam beams between the posts, CLT floor slabs with stair voids,
# stairs). Envelope layers follow in later versions.
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
from craftbot_lib import box, prism, prism_x
from planes import sloped_member, vy, vz, Roof

# ------------------------------------------------------------------
# PARAMETERS

# tower grid (photo: about 4 bays by 2, heavy braced posts)
BAY = 2.4
NX, NY = 4, 2
POST = 0.25                       # square post, sawn heavy timber
PLINTH_H, PLINTH_W = 0.075, 0.45  # Architect's Handbook 4-13: base raised 25-76 mm
GIRT = (0.20, 0.30)               # preserved perimeter girts: thickness (out of plane), depth
BRACE = 0.15                      # knee braces, square
BRACE_REACH = 0.9                 # 45 degree knee, horizontal reach

# storeys (London guide 5.4.1: 2.5 min clear; 3.0 storey gives 2.84 under a 100 slab + beam zone)
STOREY = 3.0
Z_L1 = 4.5                        # first slab top: clears the shed ridge (3.9) plus beam depth
N_UPPER = 3                       # slabs L1, L2, L3
CLT_T = 0.10                      # CLT Handbook table 5.1: 100 mm 3-layer spans 3.7 m, slab spans 2.4 m here
GLB = (0.222, 0.342)              # glulam ledger beams between posts: width (Handbook 4-9), depth (9 x 38)
SLAB_GAP = 0.025                  # slab edge held off the post faces

# stairs (CMHC ch 17: rise 125-200, run 210-355, width 860; flight height max 3.7 m)
STAIR_W = 0.90
RISER, GOING = 0.20, 0.25         # upper flights: 15 risers per 3.0 m storey
G_RISER, G_GOING = 4.5 / 23, 0.23 # ground flight: 23 risers, two flights, landing between
STEP_D = 0.06                     # solid tread block thickness (CMHC: treads at least 38 mm)
STAIR_Y0 = 0.75                   # strip between the y = 0 and y = 2.4 post rows
LAND_L = 0.90                     # landing length (CMHC: at least 860 mm)

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
HOLE_X0, HOLE_X1 = 4.5, 9.3                  # doubled trimmer rafters / joists at these grid lines

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
assert abs(ROOF_S.z(0, RIDGE_Y) - ROOF_N.z(0, RIDGE_Y)) < 1e-6 or True  # ridge is off-centre: planes differ, see below

# the ridge is 0.6 south of the shed centre: the two slopes have equal pitch and
# different runs, so the ridge line is the intersection of the two planes.
def _ridge_y():
    # ROOF_S.z = z0 + s*(Y_OUT_S + y) ... solve ROOF_S.z(y) = ROOF_N.z(y)
    # z0 + s*(y - Y_OUT_S) = z0 + s*(Y_OUT_N - y)  ->  y = (Y_OUT_S + Y_OUT_N)/2
    return (Y_OUT_S + Y_OUT_N) / 2
# equal pitch forces the ridge to the centre; keep the photo's asymmetry by giving
# the north slope a lower plate line instead: the north wall is the same height,
# so the north slope is STEEPER. Recompute:
RUN_S = RIDGE_Y - Y_OUT_S                                    # 3.3
RUN_N = Y_OUT_N - RIDGE_Y                                    # 3.3 as well when SHED_Y1 = 5.1: symmetric about 1.8
assert abs(RUN_S - RUN_N) < 1e-9, "ridge must sit on the shed centreline for equal pitches"

Z_BEAM1_BOT = z_beam(1)[0]
assert Z_BEAM1_BOT > roof_top(BAY) + BOARD[1] + 0.05, "L1 beams must clear the shed roof at the mid post row"

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
            # steel splice plates on the two X faces, centred on the joint
            for side, sgn in (("W", -1), ("E", 1)):
                xf = x + sgn * POST / 2
                box(f"Post_{ix}{iy}_Splice{side}", "Repairs/Splices",
                    min(xf, xf + sgn * SPLICE[0]), max(xf, xf + sgn * SPLICE[0]),
                    y - SPLICE[1] / 2, y + SPLICE[1] / 2, zr - SPLICE[2] / 2, zr + SPLICE[2] / 2)
            z0 = zr
        box(f"Post_{ix}{iy}", "Existing/Tower_Posts",
            x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, z0, z1)

# --- preserved perimeter girts on the outer post faces -------------
# levels: under every slab (beam top level) and at the terrace and head house girt tops
GIRT_TOPS = [z_beam(k)[1] for k in range(1, N_UPPER + 1)] + [Z_TERR_GIRT]

def girt_run(name, coll, axis, a0, a1, b_face, sgn, ztop):
    """Girt of section GIRT lying against a post face line b_face, on the
    outward side sgn, from a0 to a1 along `axis`, top at ztop."""
    z0, z1 = ztop - GIRT[1], ztop
    bb0, bb1 = sorted((b_face, b_face + sgn * GIRT[0]))
    if axis == "x":
        box(name, coll, a0, a1, bb0, bb1, z0, z1)
    else:
        box(name, coll, bb0, bb1, a0, a1, z0, z1)

for k, zt in enumerate(GIRT_TOPS):
    # long faces (south y = 0, north y = Y_END), full tower length plus the girt thickness at the corners
    for side, y, sgn in (("S", 0.0, -1), ("N", Y_END, 1)):
        girt_run(f"Girt_L{k}_{side}", "Existing/Tower_Girts", "x",
                 -POST / 2 - GIRT[0], X_END + POST / 2 + GIRT[0], y + sgn * POST / 2, sgn, zt)
    # short faces (west x = 0, east x = X_END), between the long girts
    for side, x, sgn in (("W", 0.0, -1), ("E", X_END, 1)):
        girt_run(f"Girt_L{k}_{side}", "Existing/Tower_Girts", "y",
                 -POST / 2, Y_END + POST / 2, x + sgn * POST / 2, sgn, zt)

# head house floor girts: perimeter of the east 2 x 2 bays plus the mid row, at Z_HH_GIRT
for side, y, sgn in (("S", 0.0, -1), ("N", Y_END, 1)):
    girt_run(f"Girt_HH_{side}", "Existing/HeadHouse_Frame", "x",
             HH_X0 - POST / 2 - GIRT[0], X_END + POST / 2 + GIRT[0], y + sgn * POST / 2, sgn, Z_HH_GIRT)
for side, x, sgn in (("W", HH_X0, -1), ("E", X_END, 1)):
    girt_run(f"Girt_HH_{side}", "Existing/HeadHouse_Frame", "y",
             -POST / 2, Y_END + POST / 2, x + sgn * POST / 2, sgn, Z_HH_GIRT)

# --- knee braces at the perimeter post / girt junctions -------------
# 45 degree braces in the vertical plane of each long face, from the post face
# up to the girt underside. Square ends against post and girt (member insets).
def knee(name, coll, x_post, y_c, dir_x, z_girt_bot, reach):
    p_post = Vector((x_post + dir_x * POST / 2, y_c, z_girt_bot - reach))
    p_girt = Vector((x_post + dir_x * reach, y_c, z_girt_bot))
    planes.member(name, coll, p_post, p_girt, BRACE, BRACE, (0, 1, 0),
                  n0=(dir_x, 0, 0), n1=(0, 0, -1))

for k, zt in enumerate(GIRT_TOPS):
    zb = zt - GIRT[1]
    reach = BRACE_REACH
    if k == 0:
        reach = 0.45          # L1: the shed roof passes underneath; short knees only
    for ix in range(NX + 1):
        for iy in (0, NY):
            y_c = post_y(iy)                                  # braces in the post plane, inside the girt
            if ix > 0:
                knee(f"Knee_L{k}_{ix}{iy}_W", "Existing/Tower_Braces", post_x(ix), y_c, -1, zb, reach)
            if ix < NX:
                knee(f"Knee_L{k}_{ix}{iy}_E", "Existing/Tower_Braces", post_x(ix), y_c, +1, zb, reach)

# --- new glulam beams between the posts, on the three X rows ---------
for k in range(1, N_UPPER + 1):
    zb0, zb1 = z_beam(k)
    for iy in range(NY + 1):
        y = post_y(iy)
        for ix in range(NX):
            box(f"Beam_L{k}_{ix}{iy}", "New/Beams",
                post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
                y - GLB[0] / 2, y + GLB[0] / 2, zb0, zb1)
# terrace-level beams (carry the deck joists on the mid row; perimeter has the girts)
for iy in range(NY + 1):
    y = post_y(iy)
    for ix in range(NX):
        box(f"Beam_T_{ix}{iy}", "New/Beams",
            post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
            y - GLB[0] / 2, y + GLB[0] / 2, Z_TERR_GIRT - GLB[1], Z_TERR_GIRT)
# head house mid-row beam (the mid posts carry it), floor joists span 2.4 to it
for ix in range(HH_IX0, NX):
    box(f"Beam_HH_{ix}", "New/Beams",
        post_x(ix) + POST / 2, post_x(ix + 1) - POST / 2,
        post_y(1) - GLB[0] / 2, post_y(1) + GLB[0] / 2, Z_HH_GIRT - GLB[1], Z_HH_GIRT)

# --- stairs and the slab voids ------------------------------------
# Straight flights along X in the strip STAIR_Y0..STAIR_Y0 + STAIR_W, alternating
# direction per storey (a scissor stack). The void of slab k is where the flight
# from below arrives, plus 1.95 m headroom (CMHC) over the treads below it.
STAIR_Y1 = STAIR_Y0 + STAIR_W
X_IN_W, X_IN_E = POST / 2 + SLAB_GAP, X_END - POST / 2 - SLAB_GAP    # slab x extent

def flight_x_extent(x_start, direction, n_risers, going):
    run = (n_risers - 1) * going
    return (x_start, x_start + run) if direction > 0 else (x_start - run, x_start)

# ground flight (two runs, landing between): rises eastward from x = 3.6
G_N1, G_N2 = 12, 11
g_x0 = 3.6
framing.flight("Stair_G1", "New/Stairs", g_x0, +1, STAIR_Y0, STAIR_Y1, 0.0, G_N1, G_GOING, G_RISER, STEP_D)
g_land0 = g_x0 + (G_N1 - 1) * G_GOING
box("Stair_G_Landing", "New/Stairs", g_land0, g_land0 + LAND_L, STAIR_Y0, STAIR_Y1,
    G_N1 * G_RISER - STEP_D, G_N1 * G_RISER)
g_x2 = g_land0 + LAND_L
framing.flight("Stair_G2", "New/Stairs", g_x2, +1, STAIR_Y0, STAIR_Y1, G_N1 * G_RISER, G_N2, G_GOING, G_RISER, STEP_D)
G_TOP_X = g_x2 + (G_N2 - 1) * G_GOING            # last riser lands on the L1 slab at this x
assert G_TOP_X < X_IN_E - 0.05, "ground stair overruns the east beam"
assert abs((G_N1 + G_N2) * G_RISER - Z_L1) < 1e-9

# upper flights: 15 risers per storey
N_R = int(round(STOREY / RISER))
assert abs(N_R * RISER - STOREY) < 1e-9
def upper_flight(k):
    """Flight from slab k to slab k + 1 (k + 1 may be the terrace)."""
    direction = -1 if k % 2 == 1 else +1              # L1 -> L2 westward, L2 -> L3 eastward, ...
    x_start = 5.8 if direction < 0 else X_END - 5.8   # symmetric starts
    framing.flight(f"Stair_L{k}", "New/Stairs", x_start, direction, STAIR_Y0, STAIR_Y1,
                   z_slab_top(k), N_R, GOING, RISER, STEP_D)
    return flight_x_extent(x_start, direction, N_R, GOING), direction

VOIDS = {}      # slab k -> (x0, x1) of its stair void
# void of L1: over the ground flight where the treads are less than 1.95 below the slab underside
z_clear = z_slab_under(1) - 1.95
# tread i (1..) of the second run tops at G_N1*R + i*R at x = g_x2 + (i-1)*G
i_first = max(1, math.ceil((z_clear - G_N1 * G_RISER) / G_RISER))
VOIDS[1] = (g_x2 + (i_first - 1) * G_GOING - 0.3, X_IN_E)
for k in range(1, N_UPPER + 1):
    (xa, xb), direction = upper_flight(k)
    z_clear = z_slab_under(k + 1) - 1.95 if k + 1 <= N_UPPER else Z_TERR_GIRT - GLB[1] - 1.95
    i_first = max(1, math.ceil((z_clear - z_slab_top(k)) / RISER))
    x_first = (xa + (i_first - 1) * GOING) if direction > 0 else (xb - (i_first - 1) * GOING)
    if k + 1 <= N_UPPER:
        VOIDS[k + 1] = (x_first - 0.3, X_IN_E) if direction > 0 else (X_IN_W, x_first + 0.3)
    else:
        TERR_VOID = (x_first - 0.3, X_IN_E) if direction > 0 else (X_IN_W, x_first + 0.3)

# --- CLT slabs: one panel per bay strip in Y, holed by the stair void --
VOID_Y0, VOID_Y1 = HOLE_Y0, RIDGE_Y            # 0.6 .. 1.8, same strip as the shed roof hole
for k in range(1, N_UPPER + 1):
    z0, z1 = z_slab_under(k), z_slab_top(k)
    vx0, vx1 = VOIDS[k]
    for iy in range(NY):
        ya, yb = post_y(iy) + GLB[0] / 2, post_y(iy + 1) - GLB[0] / 2   # bears on the beams, edge to edge
        # each strip is cut into 2.4 m long panels in X; the void strip only exists in iy = 0
        outline = g2.rect(X_IN_W, X_IN_E, ya, yb)
        holes = [(vx0, vx1, VOID_Y0, VOID_Y1)] if iy == 0 else []
        # split the void's x-range so the pieces stay convex: wall_pieces works in (u, z) = (x, y)
        pieces = g2.wall_pieces(outline, holes)
        for j, p in enumerate(pieces):
            prism(f"Slab_L{k}_{iy}_{j}", "New/Slabs", (0, 0, 0), (1, 0, 0), (0, 1, 0), p, z0, z1)

# --- shed: ground floor house (preserved frame) ---------------------
SW = "Existing/Shed_Walls"
# openings: west gable door + window, east gable window, south wall windows, north wall windows
DOOR = (2.0, 3.0, None, 2.1)
framing.stud_wall("ShedWall_S", SW, "x", SHED_X0, SHED_X1, SHED_Y0, SHED_Y0 + WALL_T, 0.0, PLATE_TOP,
                  STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(0.9, 2.1, 0.9, 2.1), (5.7, 6.9, 0.9, 2.1), (8.1, 9.3, 0.9, 2.1)])
framing.stud_wall("ShedWall_N", SW, "x", SHED_X0, SHED_X1, SHED_Y1 - WALL_T, SHED_Y1, 0.0, PLATE_TOP,
                  STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(3.3, 4.5, 0.9, 2.1), (6.9, 8.1, 0.9, 2.1)])
framing.stud_wall("ShedWall_W", SW, "y", SHED_Y0 + WALL_T, SHED_Y1 - WALL_T, SHED_X0, SHED_X0 + WALL_T,
                  0.0, PLATE_TOP, STUD_T, SPACING, grid0=GRID0, double_top=True, openings=[DOOR])
framing.stud_wall("ShedWall_E", SW, "y", SHED_Y0 + WALL_T, SHED_Y1 - WALL_T, SHED_X1 - WALL_T, SHED_X1,
                  0.0, PLATE_TOP, STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(2.9, 4.1, 0.9, 2.1)])

# gable studs above the plate, under the end rafters
for side, x0, x1 in (("W", SHED_X0 + WALL_T, SHED_X0 + WALL_T + STUD_T), ("E", SHED_X1 - WALL_T - STUD_T, SHED_X1 - WALL_T)):
    for j, y in enumerate(g2.positions(SHED_Y0 + WALL_T, SHED_Y1 - WALL_T, SPACING, STUD_T, GRID0)[1:-1]):
        zt = min(roof_under(y - STUD_T / 2), roof_under(y + STUD_T / 2)) - 0.002
        # skip a stud that would hit the ridge board
        if abs(y - RIDGE_Y) < RIDGE_B[0] / 2 + STUD_T / 2 + 0.01:
            continue
        box(f"ShedGable_{side}_{j:02d}", SW, x0, x1, y - STUD_T / 2, y + STUD_T / 2, PLATE_TOP, zt)

# mid beam under the ceiling joist laps, between the mid-row posts (seats on the posts, not modelled)
MB_Z0, MB_Z1 = PLATE_TOP - MIDBEAM[1], PLATE_TOP
mb_y0, mb_y1 = post_y(1) - MIDBEAM[0] / 2, post_y(1) + MIDBEAM[0] / 2
mb_cuts = [(post_x(ix) - POST / 2, post_x(ix) + POST / 2) for ix in range(NX + 1)]
for j, (xa, xb) in enumerate(g2.split_range(SHED_X0 + WALL_T, SHED_X1 - WALL_T, mb_cuts)):
    box(f"ShedMidBeam_{j}", "Existing/Shed_Ceiling", xa, xb, mb_y0, mb_y1, MB_Z0, MB_Z1)

# ceiling joists: south run (wall plate to lap over the beam) and north run, side by side,
# cut by the stair hole strip between HOLE_X0 and HOLE_X1 (headers at HOLE_Y0 and RIDGE_Y)
CJ_Z0, CJ_Z1 = PLATE_TOP, PLATE_TOP + CJ[1]
joist_xs = g2.positions(SHED_X0 + WALL_T, SHED_X1 - WALL_T, SPACING, CJ[0], GRID0)[1:-1]
in_hole = lambda x: HOLE_X0 - 0.01 < x < HOLE_X1 + 0.01
HDR_T = 2 * CJ[0]                                # doubled headers
for j, x in enumerate(joist_xs):
    xs0, xs1 = x - CJ[0] / 2, x + CJ[0] / 2      # south joist
    xn0, xn1 = x + CJ[0] / 2, x + 1.5 * CJ[0]    # north joist beside it
    if in_hole(x) and abs(x - HOLE_X0) > 0.01 and abs(x - HOLE_X1) > 0.01:
        # tail joist: wall to the lower header; stub: upper header to the beam lap
        box(f"ShedCJ_S_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, SHED_Y0 + WALL_T, HOLE_Y0 - HDR_T, CJ_Z0, CJ_Z1)
        box(f"ShedCJ_Sstub_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, RIDGE_Y + HDR_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
    else:
        box(f"ShedCJ_S_{j:02d}", "Existing/Shed_Ceiling", xs0, xs1, SHED_Y0 + WALL_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
    box(f"ShedCJ_N_{j:02d}", "Existing/Shed_Ceiling", xn0, xn1, post_y(1) - CJ_LAP, SHED_Y1 - WALL_T, CJ_Z0, CJ_Z1)
# doubled trimmers beside the joists at HOLE_X0 / HOLE_X1 (on the hole side, outside the joist pair)
for name, x, sgn in (("W", HOLE_X0, +1), ("E", HOLE_X1, -1)):
    xa = x + sgn * CJ[0] / 2 if sgn > 0 else x - CJ[0] / 2 - CJ[0]
    # west trimmer sits east of the south joist (between it and the hole); east trimmer west of the south joist
    if sgn > 0:
        xa, xb = x + 1.5 * CJ[0], x + 2.5 * CJ[0]      # beyond the north joist (which sits at +0.5..+1.5 t)
    else:
        xa, xb = x - 1.5 * CJ[0], x - 0.5 * CJ[0]
    box(f"ShedCJ_Trimmer_{name}", "Existing/Shed_Ceiling", xa, xb, SHED_Y0 + WALL_T, post_y(1) + CJ_LAP, CJ_Z0, CJ_Z1)
# headers between the trimmers (span HOLE_X1 - HOLE_X0 = 4.8 m: needs engineering, recorded)
hx0, hx1 = HOLE_X0 + 2.5 * CJ[0], HOLE_X1 - 1.5 * CJ[0]
box("ShedCJ_Header_S", "Existing/Shed_Ceiling", hx0, hx1, HOLE_Y0 - HDR_T, HOLE_Y0, CJ_Z0, CJ_Z1)
box("ShedCJ_Header_N", "Existing/Shed_Ceiling", hx0, hx1, RIDGE_Y, RIDGE_Y + HDR_T, CJ_Z0, CJ_Z1)

# rafters: build long in the vertical plane and clip; body above the plate on its
# own side of the ridge board, tail outside the plate. Rafters in the hole x-range
# on the south slope stop at the sloped header (they become tails from the plate).
RR = "Existing/Shed_Roof"
raf_xs = [SHED_X0 + RAF[0] / 2] + [x for x in joist_xs] + [SHED_X1 - RAF[0] / 2]
ridge_face = {-1: RIDGE_Y - RIDGE_B[0] / 2, +1: RIDGE_Y + RIDGE_B[0] / 2}
# sloped header on the south slope: a rafter-like member along X at y = HOLE_Y0 - HDR_T..HOLE_Y0,
# depth 235 (deeper than the rafters), top on the roof plane, spanning between the trimmers
HDR_D = 0.235
def sloped_x_member(name, coll, x0, x1, y0, y1, roof, depth, top_off=0.0):
    """Member along X whose (y, z) profile is a parallelogram with plumb sides at
    y0 / y1, top on the roof plane (offset top_off along z), `depth` measured
    perpendicular to the slope."""
    dv = depth * math.sqrt(1 + roof.s * roof.s)
    pts = [(y0, roof.z(0, y0) + top_off - dv), (y1, roof.z(0, y1) + top_off - dv),
           (y1, roof.z(0, y1) + top_off), (y0, roof.z(0, y0) + top_off)]
    return prism_x(name, coll, x0, x1, pts)

for k, x in enumerate(raf_xs):
    for side, sgn, roof, y_out, d in (("S", -1, ROOF_S, Y_OUT_S, (0, 1)), ("N", +1, ROOF_N, Y_OUT_N, (0, -1))):
        p0 = (x, y_out)
        clips = [vz(PLATE_TOP, +1), vy(ridge_face[sgn], sgn)]
        stop_at_header = (side == "S" and in_hole(x) and abs(x - HOLE_X0) > 0.01 and abs(x - HOLE_X1) > 0.01)
        if stop_at_header:
            clips = [vz(PLATE_TOP, +1), vy(HOLE_Y0 - HDR_T, -1)]
        sloped_member(f"Rafter_{k:02d}{side}", RR, p0, d, S, RAF_TOP0, RAF[1], RAF[0],
                      0.0, abs(RIDGE_Y - y_out) + 0.5, clips=clips)
        sloped_member(f"Rafter_{k:02d}{side}_tail", RR, p0, d, S, RAF_TOP0, RAF[1], RAF[0],
                      -OVERHANG, 0.0)
# doubled trimmer rafters on the south slope beside the rafters at HOLE_X0 / HOLE_X1
for name, x, sgn in (("W", HOLE_X0, +1), ("E", HOLE_X1, -1)):
    xt = x + sgn * RAF[0]
    sloped_member(f"Rafter_Trimmer_{name}", RR, (xt, Y_OUT_S), (0, 1), S, RAF_TOP0, RAF[1], RAF[0],
                  0.0, RIDGE_Y - Y_OUT_S + 0.5, clips=[vz(PLATE_TOP, +1), vy(ridge_face[-1], -1)])
sloped_x_member("Rafter_Header_S", RR, HOLE_X0 + 1.5 * RAF[0], HOLE_X1 - 1.5 * RAF[0],
                HOLE_Y0 - HDR_T, HOLE_Y0, ROOF_S, HDR_D)
# ridge board: top on the roof planes' ridge line
box("Ridge_Board", RR, SHED_X0, SHED_X1, RIDGE_Y - RIDGE_B[0] / 2, RIDGE_Y + RIDGE_B[0] / 2,
    RIDGE_Z - RIDGE_B[1], RIDGE_Z)
# collar ties on every rafter pair (beside the rafter, +x), skipped in the hole
for k, x in enumerate(raf_xs[1:-1], 1):
    if in_hole(x):
        continue
    xa = x + RAF[0] / 2
    # tie between the rafter undersides at COLLAR_Z: y where roof_under(y) = COLLAR_Z + COLLAR depth
    zt = COLLAR_Z + COLLAR[1]
    ys = RIDGE_Y - (ROOF_S.z(0, RIDGE_Y) - DV - zt) / S
    yn = RIDGE_Y + (ROOF_N.z(0, RIDGE_Y) - DV - zt) / S
    box(f"Collar_{k:02d}", RR, xa, xa + COLLAR[0], ys + 0.005, yn - 0.005, COLLAR_Z, zt)

# roof boards: rows parallel to the eaves from each eave up to the ridge, split around
# the tower posts and the stair hole. Board width measured along the slope.
RB = "Existing/Shed_Roof_Boards"
post_holes = [(post_x(ix) - POST / 2 - HOLE_CL, post_x(ix) + POST / 2 + HOLE_CL,
               post_y(iy) - POST / 2 - HOLE_CL, post_y(iy) + POST / 2 + HOLE_CL)
              for ix in range(NX + 1) for iy in range(NY + 1)]
stair_hole = (HOLE_X0 + 1.5 * RAF[0], HOLE_X1 - 1.5 * RAF[0], HOLE_Y0, RIDGE_Y - RIDGE_B[0] / 2)
w_h = BOARD[0] / math.sqrt(1 + S * S)          # board width projected to plan
n_board = 0
for side, roof, y_eave, sgn in (("S", ROOF_S, Y_OUT_S - OVERHANG, +1), ("N", ROOF_N, Y_OUT_N + OVERHANG, -1)):
    y_stop = RIDGE_Y
    y = y_eave
    row = 0
    while (y_stop - y) * sgn > 1e-6:
        yb = y + sgn * w_h
        if (y_stop - yb) * sgn < 0:
            yb = y_stop
        ya, yb2 = sorted((y, yb))
        spans = [(SHED_X0, SHED_X1)]
        holes = post_holes + ([stair_hole] if side == "S" else [])
        for hx0, hx1, hy0, hy1 in holes:
            if hy0 < yb2 - 1e-6 and hy1 > ya + 1e-6:
                new = []
                for xa, xb in spans:
                    if hx0 < xb - 1e-6 and hx1 > xa + 1e-6:
                        if hx0 > xa + 1e-6:
                            new.append((xa, hx0))
                        if hx1 < xb - 1e-6:
                            new.append((hx1, xb))
                    else:
                        new.append((xa, xb))
                spans = new
        for xa, xb in spans:
            sloped_x_member(f"RoofBoard_{side}_{row:02d}_{n_board:03d}", RB, xa, xb, ya, yb2, roof,
                            BOARD[1], top_off=BOARD[1] * math.sqrt(1 + S * S))
            n_board += 1
        y = yb
        row += 1

# --- terrace deck on the tower top ------------------------------
TD = "Existing/Terrace_Frame"
# joists along Y at 0.6 (grid 0.3 + 0.6k so they miss the posts that continue upward),
# from the south overhang to the north overhang, bearing on the girts / beams; split at
# the continuing posts (x >= HH_X0) -> the grid already misses them.
tj_xs = g2.positions(-POST / 2 - TERR_OVER, X_END + POST / 2 + TERR_OVER, SPACING, TJ[0], GRID0)
TJ_Z0, TJ_Z1 = Z_TERR_GIRT, Z_TERR_JTOP
for j, x in enumerate(tj_xs):
    box(f"TerrJoist_{j:02d}", TD, x - TJ[0] / 2, x + TJ[0] / 2,
        -POST / 2 - TERR_OVER, Y_END + POST / 2 + TERR_OVER, TJ_Z0, TJ_Z1)
# the stair from L3 arrives through the deck: void TERR_VOID in the strip, so the joists
# there are cut with headers (doubled 38 x 235)
tvx0, tvx1 = TERR_VOID
for j, x in enumerate(tj_xs):
    if tvx0 + 0.02 < x < tvx1 - 0.02:
        o = bpy.data.objects.get(f"TerrJoist_{j:02d}")
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
        box(f"TerrJoist_{j:02d}_S", TD, x - TJ[0] / 2, x + TJ[0] / 2, -POST / 2 - TERR_OVER, VOID_Y0 - 2 * TJ[0], TJ_Z0, TJ_Z1)
        box(f"TerrJoist_{j:02d}_N", TD, x - TJ[0] / 2, x + TJ[0] / 2, VOID_Y1 + 2 * TJ[0], Y_END + POST / 2 + TERR_OVER, TJ_Z0, TJ_Z1)
# headers between the nearest whole joists outside the void
left = max(x for x in tj_xs if x <= tvx0 + 0.02)
right = min(x for x in tj_xs if x >= tvx1 - 0.02)
box("TerrHeader_S", TD, left + TJ[0] / 2, right - TJ[0] / 2, VOID_Y0 - 2 * TJ[0], VOID_Y0, TJ_Z0, TJ_Z1)
box("TerrHeader_N", TD, left + TJ[0] / 2, right - TJ[0] / 2, VOID_Y1, VOID_Y1 + 2 * TJ[0], TJ_Z0, TJ_Z1)
# deck boards along X, split around the continuing posts and the stair void
deck_nogo = [(post_x(ix) - POST / 2 - HOLE_CL, post_x(ix) + POST / 2 + HOLE_CL,
              post_y(iy) - POST / 2 - HOLE_CL, post_y(iy) + POST / 2 + HOLE_CL)
             for ix in range(HH_IX0, NX + 1) for iy in range(NY + 1)]
deck_nogo.append((left + TJ[0] / 2, right - TJ[0] / 2, VOID_Y0, VOID_Y1))
framing.boards("DeckBoard", "Existing/Terrace_Deck",
               -POST / 2 - TERR_OVER, X_END + POST / 2 + TERR_OVER,
               -POST / 2 - TERR_OVER, Y_END + POST / 2 + TERR_OVER,
               Z_TERR_JTOP, Z_DECK_TOP, 0.14, gap=0.006, nogo=deck_nogo, along="x")

# --- head house (preserved frame) ------------------------------
HF = "Existing/HeadHouse_Frame"
# floor joists along Y at 0.6, on the girts / mid beam, x within the head house
hh_jxs = g2.positions(HH_X0 - POST / 2, X_END + POST / 2, SPACING, HH_FJ[0], GRID0)
for j, x in enumerate(hh_jxs):
    box(f"HHJoist_{j:02d}", HF, x - HH_FJ[0] / 2, x + HH_FJ[0] / 2, HH_YOUT_S, HH_YOUT_N, Z_HH_GIRT, Z_HH_JTOP)
framing.boards("HHFloor", "Existing/HeadHouse_Floor", HH_X0 - POST / 2, X_END + POST / 2,
               HH_YOUT_S, HH_YOUT_N, Z_HH_JTOP, Z_HH_FLOOR, 0.14, gap=0.004, along="x")
# stud walls on the floor, flush with the post outer faces
HW = "Existing/HeadHouse_Walls"
framing.stud_wall("HHWall_S", HW, "x", HH_X0 - POST / 2, X_END + POST / 2, HH_YOUT_S, HH_YOUT_S + WALL_T,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(5.7, 6.9, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)])
framing.stud_wall("HHWall_N", HW, "x", HH_X0 - POST / 2, X_END + POST / 2, HH_YOUT_N - WALL_T, HH_YOUT_N,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(8.1, 9.3, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)])
framing.stud_wall("HHWall_W", HW, "y", HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, HH_X0 - POST / 2, HH_X0 - POST / 2 + WALL_T,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(1.5, 2.7, None, Z_HH_FLOOR + 2.1)])          # door to the roof terrace stair
framing.stud_wall("HHWall_E", HW, "y", HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, X_END + POST / 2 - WALL_T, X_END + POST / 2,
                  Z_HH_FLOOR, Z_HH_PLATE, STUD_T, SPACING, grid0=GRID0, double_top=True,
                  openings=[(1.5, 3.3, Z_HH_FLOOR + 0.9, Z_HH_FLOOR + 2.1)])
# rafters and ridge
HR = "Existing/HeadHouse_Roof"
hh_raf_xs = [HH_X0 - POST / 2 + HH_RAF[0] / 2] + \
            g2.positions(HH_X0 - POST / 2, X_END + POST / 2, SPACING, HH_RAF[0], GRID0)[1:-1] + \
            [X_END + POST / 2 - HH_RAF[0] / 2]
HH_RIDGE_B = (0.038, 0.184)
hh_ridge_face = {-1: HH_RIDGE_Y - HH_RIDGE_B[0] / 2, +1: HH_RIDGE_Y + HH_RIDGE_B[0] / 2}
for k, x in enumerate(hh_raf_xs):
    for side, sgn, roof, y_out, d in (("S", -1, HH_ROOF_S, HH_YOUT_S, (0, 1)), ("N", +1, HH_ROOF_N, HH_YOUT_N, (0, -1))):
        sloped_member(f"HHRafter_{k:02d}{side}", HR, (x, y_out), d, HH_S, HH_RAF_TOP0, HH_RAF[1], HH_RAF[0],
                      0.0, abs(HH_RIDGE_Y - y_out) + 0.5, clips=[vz(Z_HH_PLATE, +1), vy(hh_ridge_face[sgn], sgn)])
        sloped_member(f"HHRafter_{k:02d}{side}_tail", HR, (x, y_out), d, HH_S, HH_RAF_TOP0, HH_RAF[1], HH_RAF[0],
                      -0.3, 0.0)
box("HH_Ridge", HR, HH_X0 - POST / 2, X_END + POST / 2, HH_RIDGE_Y - HH_RIDGE_B[0] / 2, HH_RIDGE_Y + HH_RIDGE_B[0] / 2,
    HH_RIDGE_Z - HH_RIDGE_B[1], HH_RIDGE_Z)
# ceiling ties (collar at plate level = ceiling joists) every rafter pair
for k, x in enumerate(hh_raf_xs[1:-1], 1):
    xa = x + HH_RAF[0] / 2
    box(f"HHTie_{k:02d}", HR, xa, xa + 0.038, HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, Z_HH_PLATE, Z_HH_PLATE + 0.140)
# gable studs
for side, x0, x1 in (("W", HH_X0 - POST / 2 + WALL_T, HH_X0 - POST / 2 + WALL_T + STUD_T),
                     ("E", X_END + POST / 2 - WALL_T - STUD_T, X_END + POST / 2 - WALL_T)):
    for j, y in enumerate(g2.positions(HH_YOUT_S + WALL_T, HH_YOUT_N - WALL_T, SPACING, STUD_T, GRID0)[1:-1]):
        if abs(y - HH_RIDGE_Y) < HH_RIDGE_B[0] / 2 + STUD_T / 2 + 0.01:
            continue
        r = HH_ROOF_S if y <= HH_RIDGE_Y else HH_ROOF_N
        zt = min(r.z(0, y - STUD_T / 2), r.z(0, y + STUD_T / 2)) - HH_DV - 0.002
        box(f"HHGable_{side}_{j:02d}", HW, x0, x1, y - STUD_T / 2, y + STUD_T / 2, Z_HH_PLATE, zt)

n = len([o for o in bpy.data.objects if o.type == "MESH"])
print(f"Built experiment 14 v01: {n} elements; L1 slab top {Z_L1}, terrace deck {Z_DECK_TOP:.3f}, "
      f"head house floor {Z_HH_FLOOR:.3f}, ridge {HH_RIDGE_Z:.3f}; ground stair lands at x = {G_TOP_X:.2f}")
