# ------------------------------------------------------------------
# CRAFT BOT - Experiment 09 (Fable run) - CLT residential high-rise
# ------------------------------------------------------------------
# Multi-storey residential block in cross-laminated timber after the
# early-stage rules of "How to CLT" (Arkemi 2024):
#   * concrete podium ground floor (p. 41), 8 CLT storeys above
#     (6 regular + 2 attic storeys inside a 45 deg double-pitch roof)
#   * PLATFORM framing for all walls: one-storey wall panels 3.0 m high
#     (= master panel width), 240 mm slab laid over the wall, next wall
#     on the slab  ->  storey pitch 3.24 m
#   * BALLOON framed stair/lift core: continuous panels in two lifts of
#     <= 16 m ("longitudinal in core", p. 55); slabs butt against the core
#   * double-loaded 1.8 m corridor between two load-bearing walls so every
#     slab spans 5.34 m (< 7 m -> 240 mm, table p. 59); slab strips 2.4 m
#     wide (trailer limit 2.45 m), parting walls on slab joints
#   * thicknesses from the VII-VIII floor / light-floor rows: exterior
#     180, interior bearing 160, core 180, slab 240, roof 160
#   * roof panels bear on the eave knee wall, an attic knee wall, the
#     corridor walls extended to the roof and lean on each other at the
#     ridge ("pitched roof with supporting wall", p. 47); all spans < 7 m
#   * U-shaped double-flight stair, 18 x 180 mm risers / 290 mm going,
#     flights cut from thick CLT, landings 240 mm (reference images)
#
# Coordinates: X = ridge / corridor direction (gables at x = 0 and 33.6),
# Y = across the building (eaves at y = 0 and 13.2), Z up, ground = 0.
# Units: metres.  Every element is a convex solid (box or prism) so the
# renderer's separating-axis overlap check stays valid; openings are
# therefore modelled as pier / sill / lintel pieces of one panel.

import bpy
import math
import random
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

LX, LY = 33.6, 13.2                  # outer CLT faces
T_EXT, T_INT, T_CORE = 0.18, 0.16, 0.18
T_SLAB, T_ROOF = 0.24, 0.16
T_FAC, T_COV = 0.25, 0.30            # facade build-up / roof build-up outside the CLT
H_WALL, H_ST = 3.00, 3.24            # wall panel height, storey pitch
N_REG = 6                            # regular CLT storeys (1..6); 7 = attic 1, 8 = attic 2
SLAB_W = 2.40                        # slab strip width (transport)
PANEL_LMAX = 11.2                    # exterior wall panel length (<= 13.6 m trailer)

# podium (concrete)
Z1 = 3.96                            # CLT level 1 floor = 22 risers x 0.18
T_POD_WALL, T_POD_SLAB = 0.25, 0.40
Z_POD_TOP = Z1 - T_POD_SLAB          # 3.56 top of podium walls
BEAM_W, BEAM_D, COL = 0.40, 0.60, 0.40
T_GROUND = 0.30


def z_floor(k):
    """Finished CLT floor level of storey k (1..8)."""
    return Z1 + (k - 1) * H_ST


Z7 = z_floor(7)                      # attic 1 floor (roof reference)
Z8 = z_floor(8)                      # attic 2 floor

# corridor and interior bearing lines
Y_C0, Y_C1 = 5.54, 5.70              # south corridor wall (t = 0.16)
Y_C2, Y_C3 = 7.50, 7.66              # north corridor wall
Y_CJ0, Y_CJ1 = 5.62, 7.58            # slab joints on the wall centre lines
X_PW = 24.0                          # parting wall centre (on a slab joint)
T_PWL, PW_GAP = 0.10, 0.17           # double-CLT parting wall: 100 + 170 insulation + 100 (p. 61, VII-VIII light)
PW_LEAVES = [(X_PW - PW_GAP / 2 - T_PWL, X_PW - PW_GAP / 2), (X_PW + PW_GAP / 2, X_PW + PW_GAP / 2 + T_PWL)]
X_PW0, X_PW1 = PW_LEAVES[0][0], PW_LEAVES[1][1]   # outer faces 23.815 / 24.185
LEDGER_W, LEDGER_D = 0.12, 0.16      # timber ledger under slab edges that butt the balloon core
RIB_W, RIB_D = 0.10, 0.24            # glulam ribs under the attic-1 slab (ribbed panel, p. 56)
T_PART = 0.10                        # non-load-bearing stud partitions inside apartments
PART_DOOR_W = 0.90

# core (balloon framed, t = 0.18)
X_K0, X_K1 = 9.68, 16.60             # outer faces
Y_K0, Y_K1 = 3.24, 10.36
XI0, XI1 = X_K0 + T_CORE, X_K1 - T_CORE    # 9.86 .. 16.42 inner
YI0, YI1 = Y_K0 + T_CORE, Y_K1 - T_CORE    # 3.42 .. 10.18
Y_KC0, Y_KC1 = 5.52, 5.70            # core corridor walls (0.18, flush on corridor face)
Y_KC2, Y_KC3 = 7.50, 7.68
X_SV = 12.46                         # service room | lift A wall (x .. +0.18)
X_LD = 14.44                         # lift A | lift B divider
LIFT_A = (12.64, 14.44)
LIFT_B = (14.62, 16.42)
CORE_LIFTS = [(Z1, Z1 + 4 * H_ST), (Z1 + 4 * H_ST, 99.0)]   # balloon panel lifts (second clipped by roof)

# stair (in the north part of the core, flights along X)
RISER, GOING = 0.18, 0.29
FL_W, WELL = 1.20, 0.10              # flight width, well between flights
Y_S0 = Y_KC3                         # 7.68 stair well south face
Y_S1 = YI1                           # 10.18 north face
STEP_D = 0.36                        # solid depth under each tread (stepped soffit)
DOOR_W, DOOR_H = 1.00, 2.10
LIFT_DOOR_W = 0.90

# roof
PITCH = 45.0
E0 = 2.00                            # eave knee wall height above attic-1 floor (outer CLT face)
Y_RIDGE = LY / 2
OVH_E, OVH_G = 0.50, 0.40            # eave / gable overhang of the CLT roof panel
Y_KN = 1.24                          # attic knee wall outer face: roof underside = attic-2 floor level
TAN = math.tan(math.radians(PITCH))
SLOPE_N = 1.0 / math.cos(math.radians(PITCH))   # thickness along z per unit normal thickness


def z_roof(y):
    """Roof panel underside at y."""
    return Z7 + E0 + TAN * min(y, LY - y)


# windows
WIN_W, WIN_H, WIN_SILL = 1.20, 1.40, 0.90
KNEE_WIN = (0.90, 0.90, 0.80)        # w, h, sill in the 2 m attic knee wall
SHOP_W, SHOP_H, SHOP_SILL = 2.40, 2.40, 0.60
ENTRY_W, ENTRY_H = 1.80, 2.60
GLASS_T, LEAF_T = 0.02, 0.04
RNG = random.Random(9)

# collections
C_POD_W = "Podium/Podium_Walls"
C_POD_F = "Podium/Podium_Frame"
C_POD_S = "Podium/Podium_Slabs"
C_POD_ST = "Podium/Podium_Stairs"
C_EXT = "Structure/Exterior_Walls"
C_INT = "Structure/Interior_Walls"
C_KNEE = "Structure/Knee_Walls"
C_PART = "Structure/Partitions"
C_LEDGE = "Core/Ledgers"
C_RIB = "Floors/Ribs"
C_GABLE = "Structure/Gable_Walls"
C_CORE = "Core/Core_Walls"
C_CSLAB = "Core/Core_Slabs"
C_STAIR = "Core/Stairs"
C_LAND = "Core/Landings"
C_SLAB = "Floors/Slabs"
C_ROOF = "Roof/Roof_Panels"
C_COV = "Roof/Roof_Covering"
C_CLAD = "Facade/Cladding"
C_GLASS = "Openings/Glazing"
C_DOOR = "Openings/Doors"

# ------------------------------------------------------------------
# HELPERS


def get_collection(path):
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
    obj = craftbot.place_element(
        name=name,
        loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
        axis=(0, 0, 1), angle=0,
        scale=((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2),
    )
    return move_to(obj, coll)


def prism(name, coll, origin, u, v, pts, t0, t1):
    """Convex prism: polygon `pts` in the plane (origin, u, v), extruded
    along n = u x v from t0 to t1."""
    if len(pts) < 3:
        return None
    u, v = Vector(u), Vector(v)
    n = u.cross(v).normalized()
    o = Vector(origin)
    lo = [o + a * u + b * v + t0 * n for a, b in pts]
    hi = [o + a * u + b * v + t1 * n for a, b in pts]
    k = len(pts)
    faces = [tuple(reversed(range(k))), tuple(range(k, 2 * k))]
    for i in range(k):
        j = (i + 1) % k
        faces.append((i, j, k + j, k + i))
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in lo + hi], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return move_to(obj, coll)


def prism_x(name, coll, x0, x1, pts_yz):
    """(y, z) profile extruded along X."""
    return prism(name, coll, (0, 0, 0), (0, 1, 0), (0, 0, 1), pts_yz, x0, x1)


def prism_y(name, coll, y0, y1, pts_xz):
    """(x, z) profile extruded along Y."""
    return prism(name, coll, (0, 0, 0), (0, 0, 1), (1, 0, 0), [(z, x) for x, z in pts_xz], y0, y1)


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


def area(poly):
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
                         poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def wall_pieces(poly, openings):
    """Decompose a convex (u, z) polygon with rectangular openings
    (u0, u1, z0, z1) into convex pieces: full-height piers between
    opening columns, and sill / spandrel / lintel pieces within each
    column.  Openings sharing the same u-range form one column (e.g. the
    corridor openings of a balloon panel, one per storey); different
    columns must not overlap in u."""
    cols = {}
    for u0, u1, z0, z1 in openings:
        cols.setdefault((round(u0, 6), round(u1, 6)), []).append((z0, z1))
    keys = sorted(cols)
    for (a0, a1), (b0, b1) in zip(keys, keys[1:]):
        assert a1 <= b0 + 1e-6, f"overlapping opening columns {(a0, a1)} / {(b0, b1)}"
    pieces = []
    cur = None
    for u0, u1 in keys:
        left = poly if cur is None else clip(poly, (cur, 0), (1, 0))
        pieces.append(clip(left, (u0, 0), (-1, 0)))                # pier left of the column
        col = clip(clip(poly, (u0, 0), (1, 0)), (u1, 0), (-1, 0))
        zc = None
        for z0, z1 in sorted(cols[(u0, u1)]):
            part = col if zc is None else clip(col, (0, zc), (0, 1))
            pieces.append(clip(part, (0, z0), (0, -1)))             # sill / spandrel below the opening
            zc = z1
        pieces.append(clip(col, (0, zc), (0, 1)))                   # lintel above the last opening
        cur = u1
    pieces.append(poly if cur is None else clip(poly, (cur, 0), (1, 0)))
    return [p for p in pieces if len(p) >= 3 and area(p) > 1e-6]


def wall_along_x(prefix, coll, poly_xz, y0, y1, openings=()):
    """Wall in a plane y = const (profile in x, z)."""
    n = 0
    for p in wall_pieces(poly_xz, openings):
        prism_y(f"{prefix}_{n:02d}", coll, y0, y1, p)
        n += 1


def wall_along_y(prefix, coll, poly_yz, x0, x1, openings=()):
    """Wall in a plane x = const (profile in y, z)."""
    n = 0
    for p in wall_pieces(poly_yz, openings):
        prism_x(f"{prefix}_{n:02d}", coll, x0, x1, p)
        n += 1


def below_roof(poly_yz):
    """Clip a (y, z) polygon to the space under the roof underside."""
    poly = clip(poly_yz, (0, Z7 + E0), (TAN, -1.0))
    poly = clip(poly, (LY, Z7 + E0), (-TAN, -1.0))
    return poly


def tile_x(x0, x1, w=SLAB_W):
    n = max(1, math.ceil((x1 - x0) / w - 1e-6))
    s = (x1 - x0) / n
    return [(x0 + i * s, x0 + (i + 1) * s) for i in range(n)]


def glazing(name, opening, plane, u_axis):
    """Thin glass pane in the middle of a wall opening.  plane = (c0, c1)
    wall faces, u_axis = 'x' for walls along X."""
    u0, u1, z0, z1 = opening
    c = (plane[0] + plane[1]) / 2
    if u_axis == "x":
        box(name, C_GLASS, u0, u1, c - GLASS_T / 2, c + GLASS_T / 2, z0, z1)
    else:
        box(name, C_GLASS, c - GLASS_T / 2, c + GLASS_T / 2, u0, u1, z0, z1)


def door_leaf(name, opening, plane, u_axis):
    u0, u1, z0, z1 = opening
    c = (plane[0] + plane[1]) / 2
    if u_axis == "x":
        box(name, C_DOOR, u0, u1, c - LEAF_T / 2, c + LEAF_T / 2, z0, z1)
    else:
        box(name, C_DOOR, c - LEAF_T / 2, c + LEAF_T / 2, u0, u1, z0, z1)


def windows_on(u0, u1, forbidden, pitch=3.2, first=1.8, jitter=0.4, w=WIN_W, margin=0.6):
    """Seeded, slightly irregular window centres along a facade segment.
    Windows stay >= margin from segment ends and >= margin + w/2 from
    forbidden lines (interior wall junctions, panel joints)."""
    out = []
    c = u0 + first
    while c < u1 - margin:
        cc = c + RNG.uniform(-jitter, jitter)
        ok = cc - w / 2 >= u0 + margin and cc + w / 2 <= u1 - margin
        ok = ok and all(abs(cc - f) >= w / 2 + margin for f in forbidden)
        if ok:
            out.append(cc)
        c += pitch
    return out


# ------------------------------------------------------------------
# 1. PODIUM (concrete): ground slab, perimeter walls with shop windows
#    and two entrances on the corridor axis, columns + transfer beams
#    under the CLT bearing lines, concrete core walls, transfer slab.

box("Ground_Slab", C_POD_S, 0, LX, 0, LY, -T_GROUND, 0)

shop_s = [(c - SHOP_W / 2, c + SHOP_W / 2, SHOP_SILL, SHOP_SILL + SHOP_H)
          for c in (2.4, 7.2, 13.2, 20.4, 26.4, 31.2)]
wall_along_x("Podium_Wall_S", C_POD_W, rect(0, LX, 0, Z_POD_TOP), 0, T_POD_WALL, shop_s)
wall_along_x("Podium_Wall_N", C_POD_W, rect(0, LX, 0, Z_POD_TOP), LY - T_POD_WALL, LY, shop_s)
for o in shop_s:
    glazing(f"Shop_S_{o[0]:.1f}", o, (0, T_POD_WALL), "x")
    glazing(f"Shop_N_{o[0]:.1f}", o, (LY - T_POD_WALL, LY), "x")
entry = (Y_C1, Y_C2, 0, ENTRY_H)
shop_we = [(2.0, 4.4, SHOP_SILL, SHOP_SILL + SHOP_H), entry, (8.8, 11.2, SHOP_SILL, SHOP_SILL + SHOP_H)]
wall_along_y("Podium_Wall_W", C_POD_W, rect(T_POD_WALL, LY - T_POD_WALL, 0, Z_POD_TOP), 0, T_POD_WALL, shop_we)
wall_along_y("Podium_Wall_E", C_POD_W, rect(T_POD_WALL, LY - T_POD_WALL, 0, Z_POD_TOP), LX - T_POD_WALL, LX, shop_we)
for o in shop_we:
    if o is entry:
        door_leaf("Entrance_W", o, (0, T_POD_WALL), "y")
        door_leaf("Entrance_E", o, (LX - T_POD_WALL, LX), "y")
    else:
        glazing(f"Shop_W_{o[0]:.1f}", o, (0, T_POD_WALL), "y")
        glazing(f"Shop_E_{o[0]:.1f}", o, (LX - T_POD_WALL, LX), "y")

# transfer beams under the corridor walls and the parting wall, columns below
Z_BEAM0 = Z_POD_TOP - BEAM_D
for tag, yc in (("S", Y_CJ0), ("N", Y_CJ1)):
    box(f"Beam_{tag}_W", C_POD_F, T_POD_WALL, X_K0, yc - BEAM_W / 2, yc + BEAM_W / 2, Z_BEAM0, Z_POD_TOP)
    box(f"Beam_{tag}_E", C_POD_F, X_K1, LX - T_POD_WALL, yc - BEAM_W / 2, yc + BEAM_W / 2, Z_BEAM0, Z_POD_TOP)
    for xc in (4.8, 20.8, 24.0, 28.8):
        box(f"Column_{tag}_{xc:.1f}", C_POD_F, xc - COL / 2, xc + COL / 2, yc - COL / 2, yc + COL / 2, 0, Z_BEAM0)
box("Beam_PW_S", C_POD_F, X_PW - BEAM_W / 2, X_PW + BEAM_W / 2, T_POD_WALL, Y_CJ0 - BEAM_W / 2, Z_BEAM0, Z_POD_TOP)
box("Beam_PW_N", C_POD_F, X_PW - BEAM_W / 2, X_PW + BEAM_W / 2, Y_CJ1 + BEAM_W / 2, LY - T_POD_WALL, Z_BEAM0, Z_POD_TOP)
for yc in (2.8, 10.4):
    box(f"Column_PW_{yc:.1f}", C_POD_F, X_PW - COL / 2, X_PW + COL / 2, yc - COL / 2, yc + COL / 2, 0, Z_BEAM0)

# transfer slab (outside the core) - the CLT walls start on top of it
box("Transfer_Slab_S", C_POD_S, 0, LX, 0, Y_K0, Z_POD_TOP, Z1)
box("Transfer_Slab_N", C_POD_S, 0, LX, Y_K1, LY, Z_POD_TOP, Z1)
box("Transfer_Slab_W", C_POD_S, 0, X_K0, Y_K0, Y_K1, Z_POD_TOP, Z1)
box("Transfer_Slab_E", C_POD_S, X_K1, LX, Y_K0, Y_K1, Z_POD_TOP, Z1)

# ------------------------------------------------------------------
# 2. CORE - walls are continuous (balloon) from the podium to the roof.
#    Layout (plan, inner faces x 9.86..16.42, y 3.42..10.18):
#      y 3.42- 5.52  service room (W) | lift A | lift B   (lifts open N)
#      y 5.70- 7.50  corridor passing through the core (openings W / E)
#      y 7.68-10.18  stair well: floor landing (W) | 2 flights | mid landing (E)
#    The podium storey repeats the same walls in concrete.

LAND_W = (XI1 - XI0 - 8 * GOING) / 2         # 2.12 upper landings
X_L0 = XI0 + LAND_W                          # 11.98 flights start
X_L1 = XI1 - LAND_W                          # 14.30 mid landing starts
POD_RISERS = 11                              # podium flights (22 x 0.18 = 3.96)
LAND_W_P = (XI1 - XI0 - (POD_RISERS - 1) * GOING) / 2   # 1.83
Y_FA0, Y_FA1 = Y_S0, Y_S0 + FL_W             # flight A (south band, rises east)
Y_FB0, Y_FB1 = Y_S1 - FL_W, Y_S1             # flight B (north band, rises west)
STAIR_DOOR = (X_L0 - LAND_W / 2 - DOOR_W / 2, X_L0 - LAND_W / 2 + DOOR_W / 2)
SERV_DOOR = ((XI0 + X_SV) / 2 - DOOR_W / 2, (XI0 + X_SV) / 2 + DOOR_W / 2)
LIFT_DOOR_A = (sum(LIFT_A) / 2 - LIFT_DOOR_W / 2, sum(LIFT_A) / 2 + LIFT_DOOR_W / 2)
LIFT_DOOR_B = (sum(LIFT_B) / 2 - LIFT_DOOR_W / 2, sum(LIFT_B) / 2 + LIFT_DOOR_W / 2)
LEVELS = list(range(1, 9))                   # CLT storeys served by corridor / core doors


def core_wall_y(prefix, coll, x0, x1, y0, y1, z0, openings=(), lifts=CORE_LIFTS, top=None):
    """Balloon wall along Y (profile y,z) split into panel lifts; top
    follows the roof underside unless `top` is given."""
    for i, (za, zb) in enumerate(lifts):
        za = max(za, z0)
        poly = rect(y0, y1, za, min(zb, 99.0) if top is None else min(zb, top))
        poly = below_roof(poly)
        if len(poly) >= 3 and area(poly) > 1e-6:
            wall_along_y(f"{prefix}_L{i + 1}", coll, poly, x0, x1, openings)


def core_wall_x(prefix, coll, x0, x1, y0, y1, z0, openings=(), lifts=CORE_LIFTS, top=None):
    """Balloon wall along X (profile x,z); the top is flat at the lower
    roof intersection of the two faces, plus a sloped wedge on top."""
    z_top = top if top is not None else min(z_roof(y0), z_roof(y1))
    for i, (za, zb) in enumerate(lifts):
        za = max(za, z0)
        zb = min(zb, z_top)
        if zb - za > 1e-6:
            wall_along_x(f"{prefix}_L{i + 1}", coll, rect(x0, x1, za, zb), y0, y1, openings)
    if top is None:
        wedge = below_roof(rect(y0, y1, z_top, z_top + 1.0))
        if len(wedge) >= 3 and area(wedge) > 1e-6:
            prism_x(f"{prefix}_Wedge", coll, x0, x1, wedge)


def strips(u0, u1, cuts):
    """Split [u0, u1] at the given cut positions."""
    c = sorted({u0, u1, *[x for x in cuts if u0 < x < u1]})
    return list(zip(c[:-1], c[1:]))


CORR_OPEN = [(Y_C1, Y_C2, z_floor(k), z_floor(k) + DOOR_H) for k in LEVELS]
# west / east core walls: 3 balloon strips each <= 3 m wide
for tag, x0, x1 in (("W", X_K0, XI0), ("E", XI1, X_K1)):
    for j, (ya, yb) in enumerate(strips(Y_K0, Y_K1, [Y_C1, Y_C2])):
        ops = [o for o in CORR_OPEN if o[0] >= ya - 1e-6 and o[1] <= yb + 1e-6]
        core_wall_y(f"Core_{tag}_S{j + 1}", C_CORE, x0, x1, ya, yb, Z1, ops)
        # podium (concrete) below, corridor opening 2.6 m high at ground
        pod_ops = [(Y_C1, Y_C2, 0, ENTRY_H)] if ops else []
        wall_along_y(f"Podium_Core_{tag}_S{j + 1}", C_POD_W, rect(ya, yb, 0, Z_POD_TOP), x0, x1, pod_ops)

# south (lift back) and north (stair) walls: 3 strips of 2.19 m
for tag, y0, y1 in (("S", Y_K0, YI0), ("N", YI1, Y_K1)):
    for j, (xa, xb) in enumerate(strips(XI0, XI1, [XI0 + (XI1 - XI0) / 3, XI0 + 2 * (XI1 - XI0) / 3])):
        core_wall_x(f"Core_{tag}_S{j + 1}", C_CORE, xa, xb, y0, y1, Z1)
        box(f"Podium_Core_{tag}_S{j + 1}", C_POD_W, xa, xb, y0, y1, 0, Z_POD_TOP)

# core corridor walls (south: service + lift doors, north: stair door)
south_doors = [(SERV_DOOR[0], SERV_DOOR[1], z_floor(k), z_floor(k) + DOOR_H) for k in LEVELS] + \
              [(LIFT_DOOR_A[0], LIFT_DOOR_A[1], z_floor(k), z_floor(k) + DOOR_H) for k in LEVELS] + \
              [(LIFT_DOOR_B[0], LIFT_DOOR_B[1], z_floor(k), z_floor(k) + DOOR_H) for k in LEVELS]
north_doors = [(STAIR_DOOR[0], STAIR_DOOR[1], z_floor(k), z_floor(k) + DOOR_H) for k in LEVELS]
for j, (xa, xb) in enumerate(strips(XI0, XI1, [X_SV + T_CORE / 2, X_LD + T_CORE / 2])):
    ops = [o for o in south_doors if o[0] >= xa - 1e-6 and o[1] <= xb + 1e-6]
    core_wall_x(f"Core_CorrS_S{j + 1}", C_CORE, xa, xb, Y_KC0, Y_KC1, Z1, ops)
    pod = [(o[0], o[1], 0, DOOR_H) for o in ops]
    wall_along_x(f"Podium_Core_CorrS_S{j + 1}", C_POD_W, rect(xa, xb, 0, Z_POD_TOP), Y_KC0, Y_KC1, pod)
for j, (xa, xb) in enumerate(strips(XI0, XI1, [X_L0 + 0.8, X_L1 + 0.8])):
    ops = [o for o in north_doors if o[0] >= xa - 1e-6 and o[1] <= xb + 1e-6]
    core_wall_x(f"Core_CorrN_S{j + 1}", C_CORE, xa, xb, Y_KC2, Y_KC3, Z1, ops)
    pod = [(o[0], o[1], 0, DOOR_H) for o in ops]
    wall_along_x(f"Podium_Core_CorrN_S{j + 1}", C_POD_W, rect(xa, xb, 0, Z_POD_TOP), Y_KC2, Y_KC3, pod)
for o in south_doors + north_doors:
    plane = (Y_KC0, Y_KC1) if o in south_doors else (Y_KC2, Y_KC3)
    door_leaf(f"Door_Core_{o[0]:.2f}_{o[2]:.2f}", o, plane, "x")
for k in LEVELS:
    z = z_floor(k)
    door_leaf(f"Door_Core_W_{k}", (Y_C1, Y_C2, z, z + DOOR_H), (X_K0, XI0), "y")
    door_leaf(f"Door_Core_E_{k}", (Y_C1, Y_C2, z, z + DOOR_H), (XI1, X_K1), "y")

# lift / service partitions along Y (south part of the core)
for tag, x0 in (("Serv_LiftA", X_SV), ("LiftA_LiftB", X_LD)):
    core_wall_y(f"Core_{tag}", C_CORE, x0, x0 + T_CORE, YI0, Y_KC0, Z1)
    box(f"Podium_Core_{tag}", C_POD_W, x0, x0 + T_CORE, YI0, Y_KC0, 0, Z_POD_TOP)

# core slabs: corridor lobby, service room floor, stair floor landing
for k in LEVELS:
    z = z_floor(k)
    coll, t = (C_POD_S, T_POD_SLAB) if k == 1 else (C_CSLAB, T_SLAB)
    box(f"Core_Slab_Corr_{k}", coll, XI0, XI1, Y_KC1, Y_KC2, z - t, z)
    box(f"Core_Slab_Serv_{k}", coll, XI0, X_SV, YI0, Y_KC0, z - t, z)
    box(f"Landing_Floor_{k}", C_LAND if k > 1 else C_POD_S, XI0, X_L0 if k > 1 else XI0 + LAND_W_P, Y_S0, Y_S1, z - t, z)


def flight(prefix, coll, x_start, direction, y0, y1, z_base, n_risers, z_min=None):
    """n_risers - 1 solid tread blocks from z_base; the last riser lands
    on the landing.  direction = +1 rises towards +X.  The stepped
    soffit never goes below z_min (the slab the flight starts from)."""
    if z_min is None:
        z_min = z_base - T_SLAB
    for i in range(n_risers - 1):
        xa = x_start + direction * GOING * i
        xb = xa + direction * GOING
        top = z_base + RISER * (i + 1)
        box(f"{prefix}_{i + 1:02d}", coll, min(xa, xb), max(xa, xb), y0, y1, max(top - STEP_D, z_min), top)


def stair_storey(k, z0, n_risers, land_w, coll_s, coll_l):
    """Double-flight stair from level z0 up one storey."""
    x_a = XI0 + land_w
    x_b = XI1 - land_w
    z_mid = z0 + RISER * n_risers
    flight(f"Flight_A_{k}", coll_s, x_a, +1, Y_FA0, Y_FA1, z0, n_risers, z_min=max(z0 - T_SLAB, 0.0))
    box(f"Landing_Mid_{k}", coll_l, x_b, XI1, Y_S0, Y_S1, z_mid - T_SLAB, z_mid)
    flight(f"Flight_B_{k}", coll_s, x_b, -1, Y_FB0, Y_FB1, z_mid, n_risers)


stair_storey(0, 0.0, POD_RISERS, LAND_W_P, C_POD_ST, C_POD_ST)          # ground -> level 1
for k in range(1, 8):
    stair_storey(k, z_floor(k), 9, LAND_W, C_STAIR, C_LAND)             # level k -> k+1

# ------------------------------------------------------------------
# 3. STOREY WALLS (platform framed, one storey high) + FLOOR SLABS

X_JOINTS = [PANEL_LMAX, 2 * PANEL_LMAX]                      # exterior panel joints (11.2, 22.4)
APT_DOORS_S = [(4.4, 5.4), (19.6, 20.6), (28.2, 29.2)]       # apartment entrance doors (x)
APT_DOORS_N = APT_DOORS_S


def storey_windows(k):
    """Window openings (u0, u1, z0, z1) per facade for storey k."""
    z = z_floor(k)
    if k == 7:
        w, h, sill = KNEE_WIN
    else:
        w, h, sill = WIN_W, WIN_H, WIN_SILL
    win = {}
    for tag in ("S", "N"):
        cs = windows_on(T_EXT, LX - T_EXT, X_JOINTS + [X_PW], w=w)
        win[tag] = [(c - w / 2, c + w / 2, z + sill, z + sill + h) for c in cs]
    for tag in ("W", "E"):
        w, h, sill = WIN_W, WIN_H, WIN_SILL            # gables are full-height walls on every storey
        cs = windows_on(T_EXT, LY - T_EXT, [Y_C0, Y_C3], pitch=2.3, first=1.5, jitter=0.3, w=w)
        ops = [(c - w / 2, c + w / 2, z + sill, z + sill + h) for c in cs]
        if k == 7:                                     # attic 1: only in the middle gable piece between the knee lines
            ops = [o for o in ops if o[0] >= Y_KN + 0.3 and o[1] <= LY - Y_KN - 0.3]
        if k <= 7:
            ops.append((Y_RIDGE - WIN_W / 2, Y_RIDGE + WIN_W / 2, z + WIN_SILL, z + WIN_SILL + WIN_H))   # corridor end
        win[tag] = ops
    return win


def attic2_gable_windows(z):
    """Corridor-end window under the ridge + one per attic apartment,
    kept where the roof is at least 2.5 m above the attic-2 floor."""
    return [(c - WIN_W / 2, c + WIN_W / 2, z + WIN_SILL, z + WIN_SILL + WIN_H) for c in (4.4, Y_RIDGE, LY - 4.4)]


def parting_wall(prefix, poly_yz):
    """Double-CLT apartment-separating wall: two 100 mm leaves 170 mm apart."""
    for i, (xa, xb) in enumerate(PW_LEAVES):
        wall_along_y(f"{prefix}_Leaf{i + 1}", C_INT, poly_yz, xa, xb)


def partition_y(prefix, poly_yz, xc, y_door):
    """100 mm stud partition in a plane x = xc with a 0.9 m door; y_door is
    the jamb nearest the corridor."""
    z0 = min(p[1] for p in poly_yz)
    ya, yb = (y_door, y_door + PART_DOOR_W) if y_door < Y_RIDGE else (y_door - PART_DOOR_W, y_door)
    ops = [(ya, yb, z0, z0 + DOOR_H)]
    wall_along_y(prefix, C_PART, poly_yz, xc - T_PART / 2, xc + T_PART / 2, ops)
    door_leaf(f"Door_{prefix}", ops[0], (xc - T_PART / 2, xc + T_PART / 2), "y")


PARTITIONS = [(7.2, "S"), (21.6, "S"), (30.0, "S"), (7.2, "N"), (21.6, "N"), (30.0, "N")]


def partitions(k, z, top_poly):
    """One partition per apartment; top_poly(y0, y1) -> (y, z) polygon."""
    for xc, side in PARTITIONS:
        if side == "S":
            y0, y1 = (T_EXT if k < 7 else Y_KN + T_EXT), Y_C0
            y_door = Y_C0 - 0.25 - PART_DOOR_W
        else:
            y0, y1 = Y_C3, (LY - T_EXT if k < 7 else LY - Y_KN - T_EXT)
            y_door = Y_C3 + 0.25 + PART_DOOR_W
        if k == 8:
            y0, y1 = (Y_KN, Y_C0) if side == "S" else (Y_C3, LY - Y_KN)
        partition_y(f"Partition_{side}_L{k}_{xc:.1f}", top_poly(y0, y1), xc, y_door)


def slab_regions(k):
    """Rectangles tiled by slab strips for the slab on top of storey k."""
    if k < 7:
        return [
            ("SW", 0, X_K0, 0, Y_CJ0), ("SC", X_K0, X_K1, 0, Y_K0), ("SE", X_K1, LX, 0, Y_CJ0),
            ("CW", 0, X_K0, Y_CJ0, Y_CJ1), ("CE", X_K1, LX, Y_CJ0, Y_CJ1),
            ("NW", 0, X_K0, Y_CJ1, LY), ("NC", X_K0, X_K1, Y_K1, LY), ("NE", X_K1, LX, Y_CJ1, LY),
        ]
    # attic-2 floor only between the knee walls
    return [
        ("SW", 0, X_K0, Y_KN, Y_CJ0), ("SC", X_K0, X_K1, Y_KN, Y_K0), ("SE", X_K1, LX, Y_KN, Y_CJ0),
        ("CW", 0, X_K0, Y_CJ0, Y_CJ1), ("CE", X_K1, LX, Y_CJ0, Y_CJ1),
        ("NW", 0, X_K0, Y_CJ1, LY - Y_KN), ("NC", X_K0, X_K1, Y_K1, LY - Y_KN), ("NE", X_K1, LX, Y_CJ1, LY - Y_KN),
    ]


WIN = {}
for k in range(1, 9):
    z = z_floor(k)
    z_top = z + H_WALL
    win = storey_windows(k)
    WIN[k] = win
    door_ops = {
        "S": [(a, b, z, z + DOOR_H) for a, b in APT_DOORS_S],
        "N": [(a, b, z, z + DOOR_H) for a, b in APT_DOORS_N],
    }

    if k <= N_REG:
        # exterior walls, 3 panels per long facade, 1 per gable
        for tag, y0, y1 in (("S", 0, T_EXT), ("N", LY - T_EXT, LY)):
            for j, (xa, xb) in enumerate(strips(0, LX, X_JOINTS)):
                ops = [o for o in win[tag] if o[0] >= xa and o[1] <= xb]
                wall_along_x(f"Wall_{tag}_L{k}_P{j + 1}", C_EXT, rect(xa, xb, z, z_top), y0, y1, ops)
            for o in win[tag]:
                glazing(f"Glass_{tag}_L{k}_{o[0]:.2f}", o, (y0, y1), "x")
        for tag, x0, x1 in (("W", 0, T_EXT), ("E", LX - T_EXT, LX)):
            wall_along_y(f"Wall_{tag}_L{k}", C_EXT, rect(T_EXT, LY - T_EXT, z, z_top), x0, x1, win[tag])
            for o in win[tag]:
                glazing(f"Glass_{tag}_L{k}_{o[0]:.2f}", o, (x0, x1), "y")
        # parting wall (on the slab joint x = 24), corridor walls
        parting_wall(f"Parting_S_L{k}", rect(T_EXT, Y_C0, z, z_top))
        parting_wall(f"Parting_N_L{k}", rect(Y_C3, LY - T_EXT, z, z_top))
        partitions(k, z, lambda y0, y1: rect(y0, y1, z, z_top))
        for tag, y0, y1 in (("S", Y_C0, Y_C1), ("N", Y_C2, Y_C3)):
            for j, (xa, xb) in enumerate(((T_EXT, X_K0), (X_K1, X_PW0), (X_PW1, LX - T_EXT))):
                ops = [o for o in door_ops[tag] if o[0] >= xa and o[1] <= xb]
                wall_along_x(f"Corridor_{tag}_L{k}_P{j + 1}", C_INT, rect(xa, xb, z, z_top), y0, y1, ops)
            for o in door_ops[tag]:
                door_leaf(f"Door_{tag}_L{k}_{o[0]:.1f}", o, (y0, y1), "x")

    elif k == 7:
        # attic 1: 2.0 m eave knee walls + wedge to the roof, gable pieces,
        # attic knee walls at y = 1.24 carrying the attic-2 slab edge
        for tag, y0, y1 in (("S", 0, T_EXT), ("N", LY - T_EXT, LY)):
            for j, (xa, xb) in enumerate(strips(0, LX, X_JOINTS)):
                ops = [o for o in win[tag] if o[0] >= xa and o[1] <= xb]
                wall_along_x(f"Wall_{tag}_L7_P{j + 1}", C_EXT, rect(xa, xb, z, z + E0), y0, y1, ops)
            prism_x(f"Wall_{tag}_L7_Wedge", C_EXT, 0, LX, below_roof(rect(y0, y1, z + E0, z + E0 + 1.0)))
            for o in win[tag]:
                glazing(f"Glass_{tag}_L7_{o[0]:.2f}", o, (y0, y1), "x")
        for tag, x0, x1 in (("W", 0, T_EXT), ("E", LX - T_EXT, LX)):
            # south / north triangles up to the roof, middle box under the attic-2 slab
            wall_along_y(f"Gable_{tag}_L7_S", C_GABLE, below_roof(rect(T_EXT, Y_KN, z, z + 5.0)), x0, x1)
            wall_along_y(f"Gable_{tag}_L7_N", C_GABLE, below_roof(rect(LY - Y_KN, LY - T_EXT, z, z + 5.0)), x0, x1)
            ops = win[tag]
            wall_along_y(f"Gable_{tag}_L7_M", C_GABLE, rect(Y_KN, LY - Y_KN, z, z_top), x0, x1, ops)
            for o in ops:
                glazing(f"Glass_{tag}_L7_{o[0]:.2f}", o, (x0, x1), "y")
        for tag, y0 in (("S", Y_KN), ("N", LY - Y_KN - T_EXT)):
            for j, (xa, xb) in enumerate(((T_EXT, X_K0), (X_K0, X_K1), (X_K1, X_PW0), (X_PW1, LX - T_EXT))):
                box(f"Knee_{tag}_L7_P{j + 1}", C_KNEE, xa, xb, y0, y0 + T_EXT, z, z_top)
        # parting and corridor walls: top under the attic-2 slab, roof outside the knee line
        parting_wall("Parting_S_L7", below_roof(rect(T_EXT, Y_C0, z, z_top)))
        parting_wall("Parting_N_L7", below_roof(rect(Y_C3, LY - T_EXT, z, z_top)))
        partitions(7, z, lambda y0, y1: rect(y0, y1, z, z_top))
        for tag, y0, y1 in (("S", Y_C0, Y_C1), ("N", Y_C2, Y_C3)):
            for j, (xa, xb) in enumerate(((T_EXT, X_K0), (X_K1, X_PW0), (X_PW1, LX - T_EXT))):
                ops = [o for o in door_ops[tag] if o[0] >= xa and o[1] <= xb]
                wall_along_x(f"Corridor_{tag}_L7_P{j + 1}", C_INT, rect(xa, xb, z, z_top), y0, y1, ops)
            for o in door_ops[tag]:
                door_leaf(f"Door_{tag}_L7_{o[0]:.1f}", o, (y0, y1), "x")

    else:
        # attic 2: gable triangles, parting walls and corridor walls up to the roof
        for tag, x0, x1 in (("W", 0, T_EXT), ("E", LX - T_EXT, LX)):
            tri = below_roof(rect(Y_KN, LY - Y_KN, z, z + 9.0))
            ops = attic2_gable_windows(z)
            wall_along_y(f"Gable_{tag}_L8", C_GABLE, tri, x0, x1, ops)
            for o in ops:
                glazing(f"Glass_{tag}_L8_{o[0]:.2f}", o, (x0, x1), "y")
        parting_wall("Parting_S_L8", below_roof(rect(Y_KN, Y_C0, z, z + 9.0)))
        parting_wall("Parting_N_L8", below_roof(rect(Y_C3, LY - Y_KN, z, z + 9.0)))
        partitions(8, z, lambda y0, y1: below_roof(rect(y0, y1, z, z + 9.0)))
        for tag, y0, y1 in (("S", Y_C0, Y_C1), ("N", Y_C2, Y_C3)):
            zt = min(z_roof(y0), z_roof(y1))
            for j, (xa, xb) in enumerate(((T_EXT, X_K0), (X_K1, X_PW0), (X_PW1, LX - T_EXT))):
                ops = [o for o in door_ops[tag] if o[0] >= xa and o[1] <= xb]
                wall_along_x(f"Corridor_{tag}_L8_P{j + 1}", C_INT, rect(xa, xb, z, zt), y0, y1, ops)
                prism_x(f"Corridor_{tag}_L8_P{j + 1}_Wedge", C_INT, xa, xb, below_roof(rect(y0, y1, zt, zt + 1.0)))
            for o in door_ops[tag]:
                door_leaf(f"Door_{tag}_L8_{o[0]:.1f}", o, (y0, y1), "x")

    # floor slab on top of storey k (k = 1..7); the roof sits on storey 8
    if k <= 7:
        for tag, xa, xb, ya, yb in slab_regions(k):
            for i, (sa, sb) in enumerate(tile_x(xa, xb)):
                box(f"Slab_L{k + 1}_{tag}_{i + 1:02d}", C_SLAB, sa, sb, ya, yb, z_top, z_top + T_SLAB)
                if k == 6 and tag[0] in "SN":
                    # attic-1 floor as a ribbed panel: two glulam ribs per strip in the span
                    # direction (they carry the attic knee-wall line load at mid-span)
                    if tag[1] == "C":
                        ra, rb = (T_EXT, Y_K0) if tag[0] == "S" else (Y_K1, LY - T_EXT)
                    else:
                        ra, rb = (T_EXT, Y_C0) if tag[0] == "S" else (Y_C3, LY - T_EXT)
                    for j, f in enumerate((0.25, 0.75)):
                        xc = sa + f * (sb - sa)
                        if abs(xc - X_PW) < PW_GAP / 2 + T_PWL + RIB_W:
                            continue
                        box(f"Rib_L7_{tag}_{i + 1:02d}_{j + 1}", C_RIB, xc - RIB_W / 2, xc + RIB_W / 2, ra, rb, z_top - RIB_D, z_top)
        # ledgers under the slab edges that butt the balloon core (outer faces,
        # broken at the corridor walls) and under the core slab pieces inside
        zl0, zl1 = z_top - LEDGER_D, z_top
        for (ya, yb) in ((Y_K0, Y_C0), (Y_C1, Y_C2), (Y_C3, Y_K1)):
            box(f"Ledger_W_L{k + 1}_{ya:.2f}", C_LEDGE, X_K0 - LEDGER_W, X_K0, ya, yb, zl0, zl1)
            box(f"Ledger_E_L{k + 1}_{ya:.2f}", C_LEDGE, X_K1, X_K1 + LEDGER_W, ya, yb, zl0, zl1)
        box(f"Ledger_S_L{k + 1}", C_LEDGE, X_K0, X_K1, Y_K0 - LEDGER_W, Y_K0, zl0, zl1)
        if k < 7:
            box(f"Ledger_N_L{k + 1}", C_LEDGE, X_K0, X_K1, Y_K1, Y_K1 + LEDGER_W, zl0, zl1)
        box(f"Ledger_Corr_S_L{k + 1}", C_LEDGE, XI0, XI1, Y_KC1, Y_KC1 + LEDGER_W, zl0, zl1)
        box(f"Ledger_Corr_N_L{k + 1}", C_LEDGE, XI0, XI1, Y_KC2 - LEDGER_W, Y_KC2, zl0, zl1)
        box(f"Ledger_Serv_W_L{k + 1}", C_LEDGE, XI0, XI0 + LEDGER_W, YI0, Y_KC0, zl0, zl1)
        box(f"Ledger_Serv_E_L{k + 1}", C_LEDGE, X_SV - LEDGER_W, X_SV, YI0, Y_KC0, zl0, zl1)
        box(f"Ledger_Serv_S_L{k + 1}", C_LEDGE, XI0 + LEDGER_W, X_SV - LEDGER_W, YI0, YI0 + LEDGER_W, zl0, zl1)
        box(f"Ledger_Land_W_L{k + 1}", C_LEDGE, XI0, XI0 + LEDGER_W, Y_S0, Y_S1, zl0, zl1)
        box(f"Ledger_Land_S_L{k + 1}", C_LEDGE, XI0 + LEDGER_W, X_L0, Y_S0, Y_S0 + LEDGER_W, zl0, zl1)
        box(f"Ledger_Land_N_L{k + 1}", C_LEDGE, XI0 + LEDGER_W, X_L0, Y_S1 - LEDGER_W, Y_S1, zl0, zl1)

# ------------------------------------------------------------------
# 4. ROOF - 160 mm CLT panels 2.29 m wide running eave -> ridge on each
#    slope, plumb-cut at the eave and the ridge (the two slopes lean on
#    each other over the corridor walls), 300 mm build-up on top.

Z_E = Z7 + E0


def slope_profile(south, t0, t1, y_lo, y_hi):
    """(y, z) parallelogram of a layer between normal offsets t0..t1
    above the roof underside, cut plumb at y_lo and y_hi."""
    d0, d1 = t0 * SLOPE_N, t1 * SLOPE_N          # vertical offsets
    if south:
        line = lambda y: Z_E + TAN * y
    else:
        line = lambda y: Z_E + TAN * (LY - y)
    return [(y_lo, line(y_lo) + d0), (y_hi, line(y_hi) + d0), (y_hi, line(y_hi) + d1), (y_lo, line(y_lo) + d1)]


ROOF_X0, ROOF_X1 = -OVH_G, LX + OVH_G
RW_W = 0.90                                   # roof window width (along X)
RW_Y = {7: (0.45, 1.15), 8: (2.35, 3.20)}     # roof window y-bands: attic 1 skylight, attic 2 window (sill ~1.1 m)


def roof_layer(prefix, coll, south, t0, t1, xa, xb, y_lo, y_hi, windows):
    """One roof panel (or its covering) between xa..xb, cut around the
    roof windows [(x0, x1, y0, y1)] that fall inside the panel."""
    prof = slope_profile(south, t0, t1, y_lo, y_hi)
    ws = sorted(w for w in windows if w[0] >= xa - 1e-6 and w[1] <= xb + 1e-6)
    if not ws:
        prism_x(prefix, coll, xa, xb, prof)
        return
    cur, n = xa, 0
    for x0, x1, y0, y1 in ws:
        if x0 - cur > 1e-6:
            prism_x(f"{prefix}_{n:02d}", coll, cur, x0, prof); n += 1
        lo = clip(prof, (0, y0) if False else (y0, 0), (-1, 0))     # y <= y0 (eave side)
        hi = clip(prof, (y1, 0), (1, 0))                            # y >= y1 (ridge side)
        if south:
            prism_x(f"{prefix}_{n:02d}", coll, x0, x1, lo); n += 1
            prism_x(f"{prefix}_{n:02d}", coll, x0, x1, hi); n += 1
        else:
            prism_x(f"{prefix}_{n:02d}", coll, x0, x1, lo); n += 1
            prism_x(f"{prefix}_{n:02d}", coll, x0, x1, hi); n += 1
        cur = x1
    if xb - cur > 1e-6:
        prism_x(f"{prefix}_{n:02d}", coll, cur, xb, prof)


ROOF_PANELS = tile_x(ROOF_X0, ROOF_X1)
ROOF_WIN = {True: [], False: []}
for i, (xa, xb) in enumerate(ROOF_PANELS):
    xc = (xa + xb) / 2
    over_core = X_K0 - 0.3 < xc < X_K1 + 0.3
    if xa < 0 or xb > LX or over_core or abs(xc - X_PW) < 0.8:
        continue                                                   # overhang panels, core, parting wall
    for k, (ya, yb) in RW_Y.items():
        if (i + k) % 2:                                            # alternate panels per level
            continue
        for south in (True, False):
            y0, y1 = (ya, yb) if south else (LY - yb, LY - ya)
            ROOF_WIN[south].append((xc - RW_W / 2, xc + RW_W / 2, y0, y1))

for i, (xa, xb) in enumerate(ROOF_PANELS):
    roof_layer(f"Roof_S_{i + 1:02d}", C_ROOF, True, 0, T_ROOF, xa, xb, -OVH_E, Y_RIDGE, ROOF_WIN[True])
    roof_layer(f"Roof_N_{i + 1:02d}", C_ROOF, False, 0, T_ROOF, xa, xb, Y_RIDGE, LY + OVH_E, ROOF_WIN[False])
    roof_layer(f"Roof_Covering_S_{i + 1:02d}", C_COV, True, T_ROOF, T_ROOF + T_COV, xa, xb, -OVH_E, Y_RIDGE, ROOF_WIN[True])
    roof_layer(f"Roof_Covering_N_{i + 1:02d}", C_COV, False, T_ROOF, T_ROOF + T_COV, xa, xb, Y_RIDGE, LY + OVH_E, ROOF_WIN[False])
for south in (True, False):
    for x0, x1, y0, y1 in ROOF_WIN[south]:
        tag = "S" if south else "N"
        prism_x(f"Roof_Glass_{tag}_{x0:.2f}_{y0:.2f}", C_GLASS, x0, x1,
                slope_profile(south, T_ROOF + T_COV / 2 - GLASS_T / 2, T_ROOF + T_COV / 2 + GLASS_T / 2, y0, y1))

# ------------------------------------------------------------------
# 5. FACADE - 250 mm insulation + ventilated cladding outside the CLT,
#    one band per storey (covers the slab edge), same window openings,
#    gable bands clipped by the roof.  The podium stays exposed concrete.

for k in range(1, 9):
    z = z_floor(k)
    win = WIN[k]
    if k <= N_REG:
        band = (z, z + H_ST)
    elif k == 7:
        band = (z, z + H_ST)            # attic 1 band: eave part clipped by the roof below
    else:
        band = (z, z + 9.0)             # attic 2: gable bands only, clipped by the roof
    if k <= 7:
        for tag, y0, y1 in (("S", -T_FAC, 0), ("N", LY, LY + T_FAC)):
            zt = band[1] if k < 7 else z_roof(y0 if tag == "S" else y1)   # roof underside at the outer face
            wall_along_x(f"Clad_{tag}_L{k}", C_CLAD, rect(-T_FAC, LX + T_FAC, z, zt), y0, y1, win[tag])
    for tag, x0, x1 in (("W", -T_FAC, 0), ("E", LX, LX + T_FAC)):
        poly = rect(0, LY, band[0], band[1])
        if k >= 7:
            poly = below_roof(poly)
        ops = win[tag] if k < 8 else attic2_gable_windows(z)
        wall_along_y(f"Clad_{tag}_L{k}", C_CLAD, poly, x0, x1, ops)

print("Experiment 09 (Fable) model generated:", len(bpy.data.objects), "objects")
