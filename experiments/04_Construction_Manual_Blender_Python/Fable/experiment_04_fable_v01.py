# ------------------------------------------------------------------
# CRAFT BOT - Experiment 04 (Fable run) - Prefabricated timber house
# ------------------------------------------------------------------
# Single-storey timber-framed house after the FRIM "Construction Manual
# of Prefabricated Timber House" (1996): platform on 120x120 posts,
# 47x97 stud panels 2745 high on a 610 mm grid, 9/6 mm plywood sheathing
# outside/inside, Fink trusses of 35x72 members @ 1220 with plywood
# gussets, purlins, fibre-cement roof sheets, gable ply, entrance stair.
#
# Coordinates: X = length (0..7.32, gable walls at the ends),
# Y = width (0..5.49, door wall at y = 0), Z up, ground at z = 0.
# Units: metres.  Axis-aligned members are craftbot.place_element boxes;
# sloped members (truss, purlins, sheets, stringers, braces) are convex
# prisms built from a 2D profile so that joints can be mitred/plumb cut.

import bpy
import math
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS (mm values from the manual, converted to m)

L, W = 7.32, 5.49                 # outer wall faces (12 x 9 modules of 610)
M = 0.61                          # planning grid
P = 0.047                         # plate / stud thickness
SD = 0.097                        # stud depth (47 x 97 "thicker" panel)
PLY_OUT, PLY_IN = 0.009, 0.006    # WBP 9 mm outside, MR 6 mm inside
WALL_T = PLY_OUT + SD + PLY_IN    # 0.112 = base plate / head binder width
SHEET_W, SHEET_L = 1.22, 2.44

# platform
FOOT = 0.60                       # concrete footing 600 x 600
Z_FOOT_TOP = 0.05                 # footing top 50 mm above ground
POST, POST_H = 0.12, 0.499
BEARER_W, BEARER_D = 0.06, 0.194
JOIST_W, JOIST_D = 0.047, 0.145
HEADER_T, HEADER_D = 0.02, 0.194
BOARD_T, BOARD_W = 0.022, 0.145
Z_POST_TOP = Z_FOOT_TOP + POST_H                 # 0.549
Z_JOIST = Z_POST_TOP + BEARER_D                  # 0.743
Z_BOARD = Z_JOIST + JOIST_D                      # 0.888
FFL = Z_BOARD + BOARD_T                          # 0.910 finished floor level
POST_X = [0.30, 2.54, 4.78, 7.02]
POST_Y = [0.30, W / 2, W - 0.30]

# walls
PANEL_H = 2.745
Z_BASE = FFL                                     # base plate 47 x 112
Z_PANEL0 = Z_BASE + P                            # 0.957 bottom of bottom plate
Z_PANEL1 = Z_PANEL0 + PANEL_H                    # 3.702 top of top plate
Z_BINDER1 = Z_PANEL1 + P                         # 3.749 head binder top = eaves
Z_NOG = Z_PANEL0 + SHEET_L                       # sheet joint / nogging centre 3.397
LINTEL_D = 0.145
WIN_CLEAR, WIN_H, WIN_SILL = 1.079, 1.587, 0.90  # 1055 unit + play, 1587 high, sill 900
DOOR_W, DOOR_H, DOOR_T, DOOR_GAP = 0.84, 2.10, 0.04, 0.008
DOOR_CLEAR = DOOR_W + 2 * P
Z_DOOR_HEAD = FFL + DOOR_GAP + DOOR_H + P        # 3.065 lintel underside
GLASS = 0.006

# roof
TR_T, TR_D = 0.035, 0.072         # truss members 35 x 72
TR_SP = 1.22
RISE = 1.195
OVH = 0.52                        # rafter tail overhang
GABLE_OVH = 0.30                  # purlin cantilever past the gable trusses
GUSSET = 0.009
GABLE_PLY = 0.006
PURLIN_W, PURLIN_T = 0.072, 0.035 # laid flat on the rafters
SHEET_T = 0.006                   # fibre-cement sheet (corrugation not modelled)
FASCIA_T, FASCIA_D = 0.02, 0.145
BRACE_T, BRACE_W = 0.022, 0.097
NOG_W, NOG_D = 0.038, 0.05        # ceiling noggings 38 x 50
CEIL_T = 0.006

ZB0 = Z_BINDER1                   # bottom chord underside (on the head binder)
ZB1 = ZB0 + TR_D                  # bottom chord top
YM = W / 2
SLOPE = RISE / YM
TH = math.atan(SLOPE)
CT, ST = math.cos(TH), math.sin(TH)
DV = TR_D / CT                    # vertical thickness of a rafter
Z_RAFTER_TOP0 = ZB1 + DV          # rafter top surface at the outer wall face

# stairs
RISER, RUN = 0.182, 0.23
N_RISE = 5
STR_W, STR_D = 0.06, 0.219
TREAD_T, TREAD_D = 0.047, 0.25
LEDGER = 0.05

# collections
C_FOUND = "Structure/Foundation"
C_FLOOR = "Structure/Floor_Framing"
C_WALL = "Structure/Wall_Framing"
C_ROOF = "Structure/Roof_Framing"
C_BOARDS = "Floors/Floor_Boards"
C_EXT = "Facade/Exterior_Sheathing"
C_INT = "Facade/Interior_Sheathing"
C_OPEN = "Facade/Openings"
C_GABLE = "Roof/Gable_Sheathing"
C_COVER = "Roof/Roof_Covering"
C_CEIL = "Ceiling"
C_STAIR = "Stairs"

# ------------------------------------------------------------------
# HELPERS


def get_collection(path):
    """Return (creating if needed) a nested collection 'A/B/C'."""
    parent = bpy.context.scene.collection
    for name in path.split("/"):
        child = parent.children.get(name)
        if child is None:
            child = bpy.data.collections.get(name)
            if child is None:
                child = bpy.data.collections.new(name)
            parent.children.link(child)
        parent = child
    return parent


def move_to(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_collection(coll).objects.link(obj)
    return obj


def box(name, coll, x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max corners."""
    obj = craftbot.place_element(
        name=name,
        loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
        axis=(0, 0, 1), angle=0,
        scale=((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2),
    )
    return move_to(obj, coll)


def prism(name, coll, origin, u, v, pts, t0, t1):
    """Convex prism: 2D polygon `pts` in the plane (origin, u, v), extruded
    along n = u x v from t0 to t1.  Used for every sloped member."""
    u, v = Vector(u), Vector(v)
    n = u.cross(v).normalized()
    o = Vector(origin)
    lo = [o + a * u + b * v + t0 * n for a, b in pts]
    hi = [o + a * u + b * v + t1 * n for a, b in pts]
    k = len(pts)
    verts = lo + hi
    faces = [tuple(reversed(range(k))), tuple(range(k, 2 * k))]
    for i in range(k):
        j = (i + 1) % k
        faces.append((i, j, k + j, k + i))
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return move_to(obj, coll)


def prism_x(name, coll, x0, x1, pts_yz):
    """Prism with a (y, z) profile extruded along X from x0 to x1."""
    return prism(name, coll, (0, 0, 0), (0, 1, 0), (0, 0, 1), pts_yz, x0, x1)


def clip(poly, p, n):
    """Keep the part of convex polygon `poly` with (q - p) . n >= 0."""
    p, n = Vector(p), Vector(n)
    out = []
    for i in range(len(poly)):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % len(poly)])
        da, db = (a - p).dot(n), (b - p).dot(n)
        if da >= 0:
            out.append(tuple(a))
        if (da >= 0) != (db >= 0):
            t = da / (da - db)
            out.append(tuple(a + (b - a) * t))
    return out


def strip(p, q, width, ext=0.4):
    """Rectangle of `width` around segment p-q, extended by `ext` at both
    ends (to be cut back by clip planes)."""
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x))
    a, b = p - d * ext, q + d * ext
    h = width / 2
    return [tuple(a - n * h), tuple(b - n * h), tuple(b + n * h), tuple(a + n * h)]


def positions(a0, a1, spacing, thick, grid0=None):
    """Member centres: first and last flush with a0/a1, intermediate ones
    on the grid grid0 + k*spacing, dropping any within half a spacing of
    the end members."""
    if grid0 is None:
        grid0 = a0
    first, last = a0 + thick / 2, a1 - thick / 2
    pos = [first]
    k = math.ceil((first + spacing / 2 - grid0) / spacing - 1e-9)
    p = grid0 + k * spacing
    while p < last - spacing / 2:
        pos.append(p)
        p += spacing
    pos.append(last)
    return pos


def tile_sheets(prefix, coll, x0, x1, y0, y1, z0, z1):
    """Cover a horizontal rectangle with sheets, long side along X, rows
    staggered by half a sheet, last sheet of each row clipped."""
    n, row, y = 0, 0, y0
    while y < y1 - 1e-6:
        yy = min(y + SHEET_W, y1)
        x = x0
        first_len = SHEET_L if row % 2 == 0 else SHEET_L / 2
        while x < x1 - 1e-6:
            xx = min(x + (first_len if x == x0 else SHEET_L), x1)
            box(f"{prefix}_{n:03d}", coll, x, xx, y, yy, z0, z1)
            n += 1
            x = xx
        y = yy
        row += 1


def clad(prefix, coll, along, a0, a1, b0, b1, z0, z1, holes=()):
    """Vertical sheathing on a wall: 1220 wide sheets stood upright in a
    2440 row plus a top strip; sheets are cut around rectangular holes
    [(aa, ab, za, zb)].  along = 'x' or 'y', b0..b1 = sheet thickness."""

    def rect(name, p0, p1, zz0, zz1):
        if along == "x":
            box(name, coll, p0, p1, b0, b1, zz0, zz1)
        else:
            box(name, coll, b0, b1, p0, p1, zz0, zz1)

    cols = {a0, a1}
    a = a0 + SHEET_W
    while a < a1 - 1e-6:
        cols.add(a)
        a += SHEET_W
    for aa, ab, _, _ in holes:
        cols |= {aa, ab}
    cols = sorted(cols)
    n = 0
    for i in range(len(cols) - 1):
        ca, cb = cols[i], cols[i + 1]
        rows = {z0, z1}
        if z0 + SHEET_L < z1 - 1e-6:
            rows.add(z0 + SHEET_L)
        col_holes = [(za, zb) for aa, ab, za, zb in holes if aa <= ca + 1e-6 and cb <= ab + 1e-6]
        for za, zb in col_holes:
            rows |= {max(za, z0), min(zb, z1)}
        rows = sorted(rows)
        for j in range(len(rows) - 1):
            ra, rb = rows[j], rows[j + 1]
            if any(za <= ra + 1e-6 and rb <= zb + 1e-6 for za, zb in col_holes):
                continue
            rect(f"{prefix}_{n:02d}", ca, cb, ra, rb)
            n += 1


def stud_wall(prefix, coll, along, a0, a1, b0, b1, z0, z1, grid0, openings=(), z_floor=None):
    """Panel framing between z0 (bottom of bottom plate) and z1 (top of
    top plate): plates, studs on the 610 grid, noggings at the sheet
    joint, and framed openings (jack + king studs, lintel 97 x 145,
    cripples, window sill).  openings = [(aa, ab, z_sill | None, z_head)];
    doors (z_sill None) cut the bottom plate between the jack studs."""

    def rect(name, p0, p1, zz0, zz1):
        if along == "x":
            box(name, coll, p0, p1, b0, b1, zz0, zz1)
        else:
            box(name, coll, b0, b1, p0, p1, zz0, zz1)

    doors = sorted((aa, ab) for aa, ab, zs, _ in openings if zs is None)
    segs, start = [], a0
    for aa, ab in doors:
        segs.append((start, aa))
        start = ab
    segs.append((start, a1))
    for i, (sa, sb) in enumerate(segs):
        rect(f"{prefix}_BottomPlate_{i}", sa, sb, z0, z0 + P)
    rect(f"{prefix}_TopPlate", a0, a1, z1 - P, z1)
    zs0, zt = z0 + P, z1 - P
    verticals = []
    for i, c in enumerate(positions(a0, a1, M, P, grid0)):
        if any(aa - 2.5 * P < c < ab + 2.5 * P for aa, ab, _, _ in openings):
            continue
        rect(f"{prefix}_Stud_{i:02d}", c - P / 2, c + P / 2, zs0, zt)
        verticals.append((c - P / 2, c + P / 2))
    for k, (aa, ab, zs, zh) in enumerate(openings):
        zj = zs0   # jacks stand on the bottom plate ends (only the part between them is cut)
        rect(f"{prefix}_Op{k}_JackL", aa - P, aa, zj, zh)
        rect(f"{prefix}_Op{k}_KingL", aa - 2 * P, aa - P, zs0, zt)
        rect(f"{prefix}_Op{k}_JackR", ab, ab + P, zj, zh)
        rect(f"{prefix}_Op{k}_KingR", ab + P, ab + 2 * P, zs0, zt)
        rect(f"{prefix}_Op{k}_Lintel", aa - P, ab + P, zh, zh + LINTEL_D)
        verticals += [(aa - 2 * P, aa - P), (ab + P, ab + 2 * P)]
        for j, c in enumerate(positions(aa - P, ab + P, M, P, grid0)[1:-1]):
            rect(f"{prefix}_Op{k}_Cripple_{j}", c - P / 2, c + P / 2, zh + LINTEL_D, zt)
        if zs is not None:
            rect(f"{prefix}_Op{k}_Sill", aa, ab, zs - P, zs)
            for j, c in enumerate(positions(aa, ab, M, P, grid0)[1:-1]):
                rect(f"{prefix}_Op{k}_SillCripple_{j}", c - P / 2, c + P / 2, zs0, zs - P)
    verticals.sort()
    for i in range(len(verticals) - 1):
        pa, pb = verticals[i][1], verticals[i + 1][0]
        if pb - pa < 0.05:
            continue
        if any(aa - 2 * P <= pa + 1e-6 and pb <= ab + 2 * P + 1e-6 for aa, ab, _, _ in openings):
            continue
        rect(f"{prefix}_Nog_{i:02d}", pa, pb, Z_NOG - P / 2, Z_NOG + P / 2)


def window_at(c_left_stud):
    """Window opening in the two bays right of the grid stud at c: the
    king studs coincide with the grid studs, jacks inside them."""
    aa = c_left_stud + P / 2 + P
    return (aa, aa + WIN_CLEAR, FFL + WIN_SILL, FFL + WIN_SILL + WIN_H)


# ------------------------------------------------------------------
# 1. FOUNDATION: 12 concrete footings, 120 x 120 posts in U-straps

for i, x in enumerate(POST_X):
    for j, y in enumerate(POST_Y):
        box(f"Footing_{i}{j}", C_FOUND, x - FOOT / 2, x + FOOT / 2, y - FOOT / 2, y + FOOT / 2, -0.30, Z_FOOT_TOP)
        box(f"Post_{i}{j}", C_FOUND, x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, Z_FOOT_TOP, Z_POST_TOP)

# ------------------------------------------------------------------
# 2. PLATFORM: paired bearers each side of the posts, joists @610 across
#    Y, stiffeners in notches, header joists, T&G strip flooring

for j, y in enumerate(POST_Y):
    for k, side in enumerate((-1, 1)):
        ya = y + side * POST / 2 + (0 if side > 0 else -BEARER_W)
        box(f"Bearer_{j}{'ab'[k]}", C_FLOOR, POST_X[0] - 0.20, POST_X[-1] + 0.20, ya, ya + BEARER_W, Z_POST_TOP, Z_JOIST)
joists = []
for i, xc in enumerate(positions(0.0, L, M, JOIST_W)):
    box(f"Joist_{i:02d}", C_FLOOR, xc - JOIST_W / 2, xc + JOIST_W / 2, HEADER_T, W - HEADER_T, Z_JOIST, Z_BOARD)
    joists.append((xc - JOIST_W / 2, xc + JOIST_W / 2))
for i in range(len(joists) - 1):
    xa, xb = joists[i][1], joists[i + 1][0]
    box(f"Stiffener_S_{i:02d}", C_FLOOR, xa, xb, 0.07, 0.12, Z_BOARD - 0.05, Z_BOARD)
    box(f"Stiffener_N_{i:02d}", C_FLOOR, xa, xb, W - 0.12, W - 0.07, Z_BOARD - 0.05, Z_BOARD)
    box(f"Stiffener_M_{i:02d}", C_FLOOR, xa, xb, W / 2 - 0.025, W / 2 + 0.025, Z_BOARD - 0.075, Z_BOARD)
box("Header_Joist_S", C_FLOOR, 0.0, L, 0.0, HEADER_T, FFL - HEADER_D, FFL)
box("Header_Joist_N", C_FLOOR, 0.0, L, W - HEADER_T, W, FFL - HEADER_D, FFL)
n, y = 0, HEADER_T
while y < W - HEADER_T - 1e-6:
    yy = min(y + BOARD_W, W - HEADER_T)
    box(f"Floor_Board_{n:02d}", C_BOARDS, 0.0, L, y, yy, Z_BOARD, FFL)
    n += 1
    y = yy

# ------------------------------------------------------------------
# 3. WALLS: base plates 47 x 112, panel framing, head binders 47 x 112.
#    Long walls run the full length; gable walls sit between them.

WIN_S = window_at(2 * M)
DOOR_AB = 10 * M - P / 2 - P            # right jack against the grid stud at 6.10
DOOR = (DOOR_AB - DOOR_CLEAR, DOOR_AB, None, Z_DOOR_HEAD)
WIN_N = [window_at(2 * M), window_at(8 * M)]
WIN_E = window_at(WALL_T + 3 * M)

XS0, XS1 = PLY_OUT, L - PLY_OUT          # stud zone of the long walls
YS0, YS1 = WALL_T, W - WALL_T            # stud zone of the gable walls
stud_wall("Wall_S", C_WALL, "x", XS0, XS1, PLY_OUT, PLY_OUT + SD, Z_PANEL0, Z_PANEL1, 0.0,
          openings=[WIN_S, DOOR], z_floor=FFL)
stud_wall("Wall_N", C_WALL, "x", XS0, XS1, W - PLY_OUT - SD, W - PLY_OUT, Z_PANEL0, Z_PANEL1, 0.0,
          openings=WIN_N)
stud_wall("Wall_W", C_WALL, "y", YS0, YS1, PLY_OUT, PLY_OUT + SD, Z_PANEL0, Z_PANEL1, WALL_T)
stud_wall("Wall_E", C_WALL, "y", YS0, YS1, L - PLY_OUT - SD, L - PLY_OUT, Z_PANEL0, Z_PANEL1, WALL_T,
          openings=[WIN_E])

box("Base_Plate_S_0", C_WALL, 0.0, DOOR[0], 0.0, WALL_T, Z_BASE, Z_PANEL0)
box("Base_Plate_S_1", C_WALL, DOOR[1], L, 0.0, WALL_T, Z_BASE, Z_PANEL0)
box("Base_Plate_N", C_WALL, 0.0, L, W - WALL_T, W, Z_BASE, Z_PANEL0)
box("Base_Plate_W", C_WALL, 0.0, WALL_T, WALL_T, W - WALL_T, Z_BASE, Z_PANEL0)
box("Base_Plate_E", C_WALL, L - WALL_T, L, WALL_T, W - WALL_T, Z_BASE, Z_PANEL0)
box("Head_Binder_S", C_WALL, 0.0, L, 0.0, WALL_T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_N", C_WALL, 0.0, L, W - WALL_T, W, Z_PANEL1, Z_BINDER1)
box("Head_Binder_W", C_WALL, 0.0, WALL_T, WALL_T, W - WALL_T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_E", C_WALL, L - WALL_T, L, WALL_T, W - WALL_T, Z_PANEL1, Z_BINDER1)

# ------------------------------------------------------------------
# 4. SHEATHING: 9 mm WBP ply outside, 6 mm MR ply inside, cut around
#    the openings; exterior sheets overlap at the corners along X.

holes_S = [WIN_S, (DOOR[0], DOOR[1], Z_PANEL0, Z_DOOR_HEAD)]
clad("Ply_Ext_S", C_EXT, "x", 0.0, L, 0.0, PLY_OUT, Z_PANEL0, Z_PANEL1, holes_S)
clad("Ply_Ext_N", C_EXT, "x", 0.0, L, W - PLY_OUT, W, Z_PANEL0, Z_PANEL1, WIN_N)
clad("Ply_Ext_W", C_EXT, "y", PLY_OUT, W - PLY_OUT, 0.0, PLY_OUT, Z_PANEL0, Z_PANEL1)
clad("Ply_Ext_E", C_EXT, "y", PLY_OUT, W - PLY_OUT, L - PLY_OUT, L, Z_PANEL0, Z_PANEL1, [WIN_E])
XI0, XI1 = WALL_T - PLY_IN, L - WALL_T + PLY_IN
clad("Ply_Int_S", C_INT, "x", XI0, XI1, WALL_T - PLY_IN, WALL_T, Z_PANEL0, Z_PANEL1, holes_S)
clad("Ply_Int_N", C_INT, "x", XI0, XI1, W - WALL_T, W - WALL_T + PLY_IN, Z_PANEL0, Z_PANEL1, WIN_N)
clad("Ply_Int_W", C_INT, "y", YS0, YS1, WALL_T - PLY_IN, WALL_T, Z_PANEL0, Z_PANEL1)
clad("Ply_Int_E", C_INT, "y", YS0, YS1, L - WALL_T, L - WALL_T + PLY_IN, Z_PANEL0, Z_PANEL1, [WIN_E])

# ------------------------------------------------------------------
# 5. DOOR AND WINDOWS: 47 x 97 frames in the rough openings, flush door
#    leaf 840 x 2100 x 40, one glass pane per window (louvres simplified)


def window_unit(prefix, along, aa, ab, zs, zh, b0, b1):
    def rect(name, p0, p1, zz0, zz1, bb0=b0, bb1=b1):
        if along == "x":
            box(name, C_OPEN, p0, p1, bb0, bb1, zz0, zz1)
        else:
            box(name, C_OPEN, bb0, bb1, p0, p1, zz0, zz1)
    rect(f"{prefix}_JambL", aa, aa + P, zs, zh)
    rect(f"{prefix}_JambR", ab - P, ab, zs, zh)
    rect(f"{prefix}_Head", aa + P, ab - P, zh - P, zh)
    rect(f"{prefix}_Sill", aa + P, ab - P, zs, zs + P)
    gb = (b0 + b1) / 2 - GLASS / 2
    rect(f"{prefix}_Glass", aa + P, ab - P, zs + P, zh - P, gb, gb + GLASS)


window_unit("Window_S", "x", *WIN_S, PLY_OUT, PLY_OUT + SD)
for k, wn in enumerate(WIN_N):
    window_unit(f"Window_N{k}", "x", *wn, W - PLY_OUT - SD, W - PLY_OUT)
window_unit("Window_E", "y", *WIN_E, L - PLY_OUT - SD, L - PLY_OUT)

da, db = DOOR[0], DOOR[1]
box("Door_JambL", C_OPEN, da, da + P, PLY_OUT, PLY_OUT + SD, FFL, Z_DOOR_HEAD)
box("Door_JambR", C_OPEN, db - P, db, PLY_OUT, PLY_OUT + SD, FFL, Z_DOOR_HEAD)
box("Door_Head", C_OPEN, da + P, db - P, PLY_OUT, PLY_OUT + SD, Z_DOOR_HEAD - P, Z_DOOR_HEAD)
box("Door_Leaf", C_OPEN, da + P, db - P, PLY_OUT + SD - DOOR_T, PLY_OUT + SD, FFL + DOOR_GAP, FFL + DOOR_GAP + DOOR_H)

# ------------------------------------------------------------------
# 6. ROOF TRUSSES: Fink (W) trusses of 35 x 72 members @ 1220, gable
#    trusses inset by the 6 mm gable ply; 9 mm ply gussets both faces.

truss_x = [GABLE_PLY] + [k * TR_SP - TR_T / 2 for k in range(1, 6)] + [L - GABLE_PLY - TR_T]


def zu_s(y):
    return ZB1 + SLOPE * y            # south rafter underside


def zu_n(y):
    return ZB1 + SLOPE * (W - y)      # north rafter underside


BELOW_S = ((0.0, ZB1), (SLOPE, -1.0))           # z <= south rafter underside
BELOW_N = ((W, ZB1), (-SLOPE, -1.0))
ABOVE_CHORD = ((0.0, ZB1), (0.0, 1.0))
BELOW_S_TOP = ((0.0, ZB1 + DV), (SLOPE, -1.0))  # z <= south rafter top
BELOW_N_TOP = ((W, ZB1 + DV), (-SLOPE, -1.0))
ABOVE_CHORD_BOT = ((0.0, ZB0), (0.0, 1.0))

B1, B2 = (W / 3, ZB1), (2 * W / 3, ZB1)                      # bottom chord panel points
T1, T2 = (YM / 2, zu_s(YM / 2)), (W - YM / 2, zu_n(W - YM / 2))  # mid-rafter points
APEX = (YM, zu_s(YM))
RAFTER_S = [(-OVH, zu_s(-OVH)), (YM, zu_s(YM)), (YM, zu_s(YM) + DV), (-OVH, zu_s(-OVH) + DV)]
RAFTER_N = [(W + OVH, zu_n(W + OVH)), (YM, zu_n(YM)), (YM, zu_n(YM) + DV), (W + OVH, zu_n(W + OVH) + DV)]
WEBS = [  # (name, from, to, extra clip)  -- outer webs cut at the node, inner webs at node + apex
    ("W1", B1, T1, [((B1[0], 0), (-1, 0))]),
    ("W2", B1, APEX, [((B1[0], 0), (1, 0)), ((YM, 0), (-1, 0))]),
    ("W3", B2, APEX, [((B2[0], 0), (-1, 0)), ((YM, 0), (1, 0))]),
    ("W4", B2, T2, [((B2[0], 0), (1, 0))]),
]
web_polys = {}
for name, a, b, extra in WEBS:
    poly = strip(a, b, TR_D)
    for p, nrm in [ABOVE_CHORD, BELOW_S, BELOW_N] + extra:
        poly = clip(poly, p, nrm)
    web_polys[name] = poly

# gusset plates: rectangle around each node, clipped to the truss outline
GUSSETS = [
    ("Apex", (YM - 0.18, YM + 0.18), (APEX[1] - 0.14, APEX[1] + 0.10)),
    ("HeelS", (0.0, 0.15), (ZB0, ZB0 + 0.10)),
    ("HeelN", (W - 0.15, W), (ZB0, ZB0 + 0.10)),
    ("B1", (B1[0] - 0.125, B1[0] + 0.125), (ZB0, ZB0 + 0.20)),
    ("B2", (B2[0] - 0.125, B2[0] + 0.125), (ZB0, ZB0 + 0.20)),
    ("T1", (T1[0] - 0.20, T1[0] + 0.20), (T1[1] - 0.18, T1[1] + DV + 0.3)),
    ("T2", (T2[0] - 0.20, T2[0] + 0.20), (T2[1] - 0.18, T2[1] + DV + 0.3)),
]
gusset_polys = {}
for name, (ya, yb), (za, zb) in GUSSETS:
    poly = [(ya, za), (yb, za), (yb, zb), (ya, zb)]
    for p, nrm in (ABOVE_CHORD_BOT, BELOW_S_TOP, BELOW_N_TOP):
        poly = clip(poly, p, nrm)
    gusset_polys[name] = poly

for i, x0 in enumerate(truss_x):
    x1 = x0 + TR_T
    t = f"Truss_{i}"
    prism_x(f"{t}_BottomChord", C_ROOF, x0, x1, [(0.0, ZB0), (W, ZB0), (W, ZB1), (0.0, ZB1)])
    prism_x(f"{t}_RafterS", C_ROOF, x0, x1, RAFTER_S)
    prism_x(f"{t}_RafterN", C_ROOF, x0, x1, RAFTER_N)
    for name, poly in web_polys.items():
        prism_x(f"{t}_{name}", C_ROOF, x0, x1, poly)
    faces = []
    if i > 0:
        faces.append((x0 - GUSSET, x0))
    if i < len(truss_x) - 1:
        faces.append((x1, x1 + GUSSET))
    for k, (ga, gb) in enumerate(faces):
        for name, poly in gusset_polys.items():
            prism_x(f"{t}_Gusset_{name}_{k}", C_ROOF, ga, gb, poly)

# ------------------------------------------------------------------
# 7. ROOF BRACING (22 x 97): diagonal braces under the rafters from the
#    gable-truss apex to the heel of the centre truss (both slopes, both
#    ends), bottom-chord runners and web runners along the building.

X_IN0 = truss_x[0] + TR_T + GUSSET          # inner gusset face of the west gable truss
X_IN1 = truss_x[-1] - GUSSET
XC = truss_x[3] + TR_T / 2                   # centre truss


def roof_frame(south):
    """(origin, u, v) of a roof-plane frame whose v axis runs up the slope
    from the rafter underside at the outer wall face; n = u x v points
    out of the roof."""
    if south:
        return (0.0, 0.0, ZB1), (1, 0, 0), (0, CT, ST)
    return (L, W, ZB1), (-1, 0, 0), (0, -CT, ST)


def y_to_v(y):
    return y / CT


for south in (True, False):
    o, u, v = roof_frame(south)
    tag = "S" if south else "N"
    for end in (0, 1):
        if end == 0:
            ua, ub = X_IN0, XC - TR_T / 2 - GUSSET
        else:
            ua, ub = XC + TR_T / 2 + GUSSET, X_IN1
        if not south:
            ua, ub = L - ub, L - ua
        va, vb = y_to_v(YM - 0.15), y_to_v(0.15)
        if end == 0:
            pa, pb = (ua, va), (ub, vb)
        else:
            pa, pb = (ua, vb), (ub, va)
        poly = strip(pa, pb, BRACE_W)
        poly = clip(poly, (ua, 0), (1, 0))
        poly = clip(poly, (ub, 0), (-1, 0))
        prism(f"Brace_Diag_{tag}{end}", C_ROOF, o, u, v, poly, -BRACE_T, 0.0)

for k, yc in enumerate((B1[0] - 0.25, B2[0] + 0.25)):
    box(f"Runner_BC_{k}", C_ROOF, X_IN0, X_IN1, yc - BRACE_W / 2, yc + BRACE_W / 2, ZB1, ZB1 + BRACE_T)
for name, a, b in (("W1", B1, T1), ("W4", B2, T2)):
    a, b = Vector(a), Vector(b)
    mid = (a + b) / 2
    d = (b - a).normalized()
    nrm = Vector((-d.y, d.x))
    if nrm.dot(Vector((0 if name == "W1" else W, ZB1)) - mid) < 0:
        nrm = -nrm
    pts = [tuple(mid + d * s + nrm * t) for s, t in
           ((-BRACE_W / 2, TR_D / 2), (BRACE_W / 2, TR_D / 2),
            (BRACE_W / 2, TR_D / 2 + BRACE_T), (-BRACE_W / 2, TR_D / 2 + BRACE_T))]
    prism_x(f"Runner_Web_{name}", C_ROOF, X_IN0, X_IN1, pts)

# ------------------------------------------------------------------
# 8. PURLINS, ROOF SHEETS, RIDGE, FASCIA AND BARGE BOARDS


def roof_pt(south, v, t):
    """(y, z) of a point at slope distance v from the outer wall face and
    height t normal to the rafter top plane."""
    y = v * CT - t * ST
    z = Z_RAFTER_TOP0 + v * ST + t * CT
    return (y if south else W - y, z)


def v_at(y, t):
    """Slope coordinate of the plumb line through y at normal height t."""
    return (y + t * ST) / CT


V_TAIL = v_at(-OVH, 0.0)
V_APEX = v_at(YM, 0.0)
PURLIN_V = [V_TAIL + 0.08 + k * 0.67 for k in range(6)]
X_ROOF0, X_ROOF1 = -GABLE_OVH, L + GABLE_OVH
N_SHEETS = 8
SHEET_X = [X_ROOF0 + k * (X_ROOF1 - X_ROOF0) / N_SHEETS for k in range(N_SHEETS + 1)]
Z_SHEET0, Z_SHEET1 = PURLIN_T, PURLIN_T + SHEET_T
Y_EAVE = -OVH - 0.05                         # sheet overhang past the fascia

for south in (True, False):
    tag = "S" if south else "N"
    for k, vc in enumerate(PURLIN_V):
        pts = [roof_pt(south, vc + a, t) for a, t in
               ((-PURLIN_W / 2, 0), (PURLIN_W / 2, 0), (PURLIN_W / 2, PURLIN_T), (-PURLIN_W / 2, PURLIN_T))]
        prism_x(f"Purlin_{tag}_{k}", C_ROOF, X_ROOF0, X_ROOF1, pts)
    v_split = v_at(Y_EAVE, Z_SHEET0) + SHEET_L
    for k in range(N_SHEETS):
        for j, (y0, y1) in enumerate(((Y_EAVE, None), (None, YM))):
            va0 = v_at(y0, Z_SHEET0) if y0 is not None else v_split
            va1 = v_at(y0, Z_SHEET1) if y0 is not None else v_split
            vb0 = v_at(y1, Z_SHEET0) if y1 is not None else v_split
            vb1 = v_at(y1, Z_SHEET1) if y1 is not None else v_split
            pts = [roof_pt(south, va0, Z_SHEET0), roof_pt(south, vb0, Z_SHEET0),
                   roof_pt(south, vb1, Z_SHEET1), roof_pt(south, va1, Z_SHEET1)]
            prism_x(f"Roof_Sheet_{tag}_{k}{j}", C_COVER, SHEET_X[k], SHEET_X[k + 1], pts)
    # ridge capping
    t0, t1 = Z_SHEET1, Z_SHEET1 + SHEET_T
    pts = [roof_pt(south, v_at(YM, t0) - 0.25, t0), roof_pt(south, v_at(YM, t0), t0),
           roof_pt(south, v_at(YM, t1), t1), roof_pt(south, v_at(YM, t1) - 0.25, t1)]
    prism_x(f"Ridge_Cap_{tag}", C_COVER, X_ROOF0, X_ROOF1, pts)
    # fascia on the rafter tails, top under the roof sheets
    z_top = roof_pt(True, v_at(-OVH, Z_SHEET0), Z_SHEET0)[1]
    if south:
        box("Fascia_S", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, -OVH - FASCIA_T, -OVH, z_top - FASCIA_D, z_top)
    else:
        box("Fascia_N", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, W + OVH, W + OVH + FASCIA_T, z_top - FASCIA_D, z_top)
    # barge boards along the gable overhang, plumb cut at ridge and tail
    for end, (xa, xb) in enumerate(((X_ROOF0 - FASCIA_T, X_ROOF0), (X_ROOF1, X_ROOF1 + FASCIA_T))):
        pts = [roof_pt(south, v_at(-OVH, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0), Z_SHEET0),
               roof_pt(south, v_at(-OVH, Z_SHEET0), Z_SHEET0)]
        prism_x(f"Barge_{tag}_{end}", C_COVER, xa, xb, pts)

# ------------------------------------------------------------------
# 9. GABLE ENDS: 6 mm ply on the outer face of the end trusses (centre
#    pentagon over the wall + the two rafter-tail parallelograms)

GABLE_MAIN = [(0.0, ZB0), (W, ZB0), (W, zu_n(W) + DV), (YM, zu_s(YM) + DV), (0.0, zu_s(0.0) + DV)]
GABLE_TAIL_S = [(-OVH, zu_s(-OVH)), (0.0, zu_s(0.0)), (0.0, zu_s(0.0) + DV), (-OVH, zu_s(-OVH) + DV)]
GABLE_TAIL_N = [(W + OVH, zu_n(W + OVH)), (W, zu_n(W)), (W, zu_n(W) + DV), (W + OVH, zu_n(W + OVH) + DV)]
for end, (xa, xb) in enumerate(((0.0, GABLE_PLY), (L - GABLE_PLY, L))):
    prism_x(f"Gable_Ply_{end}_Main", C_GABLE, xa, xb, GABLE_MAIN)
    prism_x(f"Gable_Ply_{end}_TailS", C_GABLE, xa, xb, GABLE_TAIL_S)
    prism_x(f"Gable_Ply_{end}_TailN", C_GABLE, xa, xb, GABLE_TAIL_N)

# ------------------------------------------------------------------
# 10. CEILING: 38 x 50 noggings between the bottom chords @610, 6 mm ply
#     under the chords between the interior wall faces

for i in range(len(truss_x) - 1):
    xa, xb = truss_x[i] + TR_T, truss_x[i + 1]
    for k in range(9):
        yc = M / 2 + k * M
        box(f"Ceiling_Nog_{i}_{k}", C_CEIL, xa, xb, yc - NOG_W / 2, yc + NOG_W / 2, ZB0, ZB0 + NOG_D)
tile_sheets("Ceiling_Ply", C_CEIL, WALL_T, L - WALL_T, WALL_T, W - WALL_T, ZB0 - CEIL_T, ZB0)

# ------------------------------------------------------------------
# 11. ENTRANCE STAIR: concrete landing, two 60 x 219 stringers leaning on
#     the header joist, 47 x 250 treads on 50 x 50 ledgers

XD = (da + db) / 2
Y_LAND0 = -(N_RISE - 1) * RUN - 0.04 - 0.36
box("Landing", C_STAIR, XD - 0.65, XD + 0.65, Y_LAND0, Y_LAND0 + 0.60, -0.10, 0.0)
str_slope = RISER / RUN
z_top0 = Z_BOARD                      # stringer top at the floor-board underside
d_vert = STR_D / math.cos(math.atan(str_slope))
y_foot = -(N_RISE - 1) * RUN - 0.04 - 0.08
y_bot_hits = -(z_top0 - d_vert) / str_slope
STRINGER = [(0.0, z_top0), (0.0, z_top0 - d_vert), (y_bot_hits, 0.0), (y_foot, 0.0), (y_foot, z_top0 + str_slope * y_foot)]
sx = [(XD - DOOR_CLEAR / 2 - STR_W, XD - DOOR_CLEAR / 2), (XD + DOOR_CLEAR / 2, XD + DOOR_CLEAR / 2 + STR_W)]
for k, (xa, xb) in enumerate(sx):
    prism_x(f"Stringer_{k}", C_STAIR, xa, xb, STRINGER)
for k in range(1, N_RISE):
    zt = FFL - (N_RISE - k) * RISER
    yf = -(N_RISE - k) * RUN - 0.04
    box(f"Tread_{k}", C_STAIR, sx[0][1], sx[1][0], yf, yf + TREAD_D, zt - TREAD_T, zt)
    for j, xa in enumerate((sx[0][1], sx[1][0] - LEDGER)):
        box(f"Ledger_{k}_{j}", C_STAIR, xa, xa + LEDGER, yf + 0.035, yf + 0.215, zt - TREAD_T - LEDGER, zt - TREAD_T)

print("experiment_04_fable_v01: built", len([o for o in bpy.data.objects if o.type == "MESH"]), "members")
