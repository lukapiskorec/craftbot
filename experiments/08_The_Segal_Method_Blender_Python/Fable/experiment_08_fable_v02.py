# ------------------------------------------------------------------
# CRAFT BOT - Experiment 08 (Fable run) - Segal Method two-storey house
# ------------------------------------------------------------------
# Post-and-beam timber frame house after Walter Segal's method (AJ special
# issue, 5 Nov 1986, J. Broome), following the building sequence of the
# source: foundations (10) -> structural frame (11) -> roof (12) ->
# floors (13) -> external walls (14) -> windows (15) -> stairs (18).
#
#   * tartan grid: 600 panel + 50 structural band = 0.65 m module
#   * structural bay 6 modules = 3.9 m post to post (3.85 m clear)
#   * cross-frames along Y at x = 0, 3.9, 7.8, 11.7, 14.3 (last = patio
#     frame); post lines y = 0, 3.9, 7.8; house 11.7 x 7.85 m + 2.6 m
#     covered patio on the east, all under one 15 deg pitched roof
#   * posts 50 x 150 on pad foundations, beams 50 x 200 bolted to both
#     post faces, joists 50 x 200 at every band on 50 x 50 bearers
#     (notched ends so undersides are flush, fig 50/51)
#   * double-height void over bay 2 south half, stair on its north edge
#   * infill walls: 12 ply / 50 core / 12 ply clamped between 50 x 25
#     battens on the bands; site-made glazing with mullions on the bands
#
# Coordinates: X = along the house (west -> east), Y = across (south ->
# north), Z up, ground at z = 0.  Units: metres.  Axis-aligned members
# are craftbot.place_element boxes; sloped members are convex prisms.

import bpy
import math
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

M = 0.65                 # module pitch (600 panel + 50 band)
BAND = 0.05              # structural band / joint width
PANEL = 0.60
FRAMES_X = [0.0, 3.9, 7.8, 11.7, 14.3]      # cross-frame lines
HOUSE_X1 = 11.7                              # east wall frame (patio beyond)
POST_Y = [0.0, 3.9, 7.8]                     # post lines across
Y_OUT = 7.85                                 # north outer face of wall core
POST_W, POST_D = 0.05, 0.15                  # post: 50 along X, 150 along Y
BEAM_D = 0.20                                # beams and joists 50 x 200
T = 0.05                                     # member thickness
BEARER = 0.05
PLY = 0.012
CORE = 0.05
BAT = 0.025                                  # clamping batten thickness
BOARD_T, BOARD_W = 0.022, 0.150              # t&g floor boards
DECK_W, DECK_GAP = 0.100, 0.010              # keruing patio deck
PAD = 0.60
PAD_SLAB = 0.05
PAD_DEPTH = 0.80
Z_POST0 = PAD_SLAB
Z_GF = 0.80                                  # ground floor framing underside
Z_UF = 3.40                                  # upper floor framing underside
FFL_G = Z_GF + BEAM_D + BOARD_T              # 1.022
FFL_U = Z_UF + BEAM_D + BOARD_T              # 3.622
PITCH = math.radians(15.0)
S = math.tan(PITCH)
Z_EAVE = 6.00                                # roof slab underside at y = 0
Y_RIDGE = 3.925                              # centre of the middle band
OVERHANG_Y = 0.60                            # beyond post outer faces
OVERHANG_X = 0.60                            # beyond outer roof beam faces
SLAB = BEAM_D / math.cos(PITCH)              # vertical depth of roof slab
BEARER_V = BEARER / math.cos(PITCH)
DECK_T = 0.018 / math.cos(PITCH)
KERB_H = 0.15
GLASS = 0.006
POST_OUT = 0.10                              # post projection outside core

# Void (double-height space): bay between frames 1 and 2, south half
VOID_X = (FRAMES_X[1], FRAMES_X[2])
VOID_Y = (0.0, POST_Y[1])

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
    if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
        return None
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
    if len(pts) < 3 or t1 - t0 < 1e-6:
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


def clip_rect(poly, a0, a1, b0, b1):
    poly = clip(poly, (a0, 0), (1, 0))
    poly = clip(poly, (a1, 0), (-1, 0))
    poly = clip(poly, (0, b0), (0, 1))
    poly = clip(poly, (0, b1), (0, -1))
    return poly


def strip(p, q, width, ext=0.0):
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x))
    a, b = p - d * ext, q + d * ext
    h = width / 2
    return [tuple(a - n * h), tuple(b - n * h), tuple(b + n * h), tuple(a + n * h)]


def bands(a0, a1):
    """Tartan bands [k*M, k*M + BAND] strictly inside (a0, a1)."""
    out = []
    k = math.floor(a0 / M) - 1
    while k * M < a1:
        b0 = k * M
        if b0 > a0 + 1e-6 and b0 + BAND < a1 - 1e-6:
            out.append((b0, b0 + BAND))
        k += 1
    return out


def slots(a0, a1):
    """Panel slots between the bands inside the clear range (a0, a1)."""
    edges = [a0]
    for b0, b1 in bands(a0, a1):
        edges += [b0, b1]
    edges.append(a1)
    return [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]


# Roof planes (vertical heights as functions of y)
def zu(y):
    """Underside of the roof slab (beams / joists)."""
    return Z_EAVE + S * (Y_RIDGE - abs(y - Y_RIDGE))


def zj(y):
    """Top of roof joists = deck underside."""
    return zu(y) + SLAB


def zd(y):
    return zj(y) + DECK_T


def roof_profile(y0, y1, lo, hi):
    """Plumb-cut parallelogram (y, z) profile between two roof-parallel
    height functions (must not straddle the ridge)."""
    return [(y0, lo(y0)), (y1, lo(y1)), (y1, hi(y1)), (y0, hi(y0))]


def roof_piece(name, coll, x0, x1, y0, y1, lo, hi):
    """A piece straddling the ridge is split plumb at the ridge into two
    convex halves (the ridge joist becomes a pair)."""
    if y0 < Y_RIDGE - 1e-6 and y1 > Y_RIDGE + 1e-6:
        prism_x(name + "_s", coll, x0, x1, roof_profile(y0, Y_RIDGE, lo, hi))
        prism_x(name + "_n", coll, x0, x1, roof_profile(Y_RIDGE, y1, lo, hi))
        return
    return prism_x(name, coll, x0, x1, roof_profile(y0, y1, lo, hi))


# ------------------------------------------------------------------
# 10. FOUNDATIONS: pad per post, capped by a paving slab

post_xy = [(x, y) for x in FRAMES_X for y in POST_Y]


def post_y_range(y):
    """Posts sit in the 50 band and project 100 outside / into the room."""
    if y == POST_Y[0]:
        return (-POST_OUT, BAND)                  # south: projects outside
    if y == POST_Y[-1]:
        return (Y_OUT - BAND, Y_OUT + POST_OUT)   # north: projects outside
    return (y - BAND, y + BAND * 2)               # middle: 3.85 .. 4.00


for i, (x, y) in enumerate(post_xy):
    yc = sum(post_y_range(y)) / 2
    box(f"Pad_{i:02d}", "Foundation", x - PAD / 2, x + PAD / 2, yc - PAD / 2, yc + PAD / 2, -PAD_DEPTH, 0.0)
    box(f"PadSlab_{i:02d}", "Foundation", x - PAD / 2, x + PAD / 2, yc - PAD / 2, yc + PAD / 2, 0.0, PAD_SLAB)

# ------------------------------------------------------------------
# 11. STRUCTURAL FRAME: posts, beams (floor + roof), joists on bearers


def beam_xs(fi, level):
    """x-ranges of the beams of frame fi: double at inner frames, single
    (inside) at end frames, except at roof level (outer beam carries the
    gable overhang outriggers)."""
    x = FRAMES_X[fi]
    inner = (x + POST_W / 2, x + POST_W / 2 + T)
    outer = (x - POST_W / 2 - T, x - POST_W / 2)
    if level == "roof" or 0 < fi < len(FRAMES_X) - 1:
        return [outer, inner]
    return [inner] if fi == 0 else [outer]


# Posts: from the pad slab to the underside of the roof slab
for i, (x, y) in enumerate(post_xy):
    y0, y1 = post_y_range(y)
    top = min(zu(y0), zu(y1))
    box(f"Post_{i:02d}", "Structure/Posts", x - POST_W / 2, x + POST_W / 2, y0, y1, Z_POST0, top)

# Floor beams (tie beams of the portal frames) at GF and UF level
Y_BEAM0, Y_BEAM1 = -POST_OUT, Y_OUT + POST_OUT
for fi in range(len(FRAMES_X)):
    for lvl, z0 in (("GF", Z_GF), ("UF", Z_UF)):
        for k, (bx0, bx1) in enumerate(beam_xs(fi, lvl)):
            box(f"Beam_{lvl}_F{fi}_{k}", "Structure/Beams", bx0, bx1, Y_BEAM0, Y_BEAM1, z0, z0 + BEAM_D)

# Roof beams: sloped, plumb cut at the ridge and at the overhang ends
Y_ROOF0, Y_ROOF1 = Y_BEAM0 - OVERHANG_Y, Y_BEAM1 + OVERHANG_Y
for fi in range(len(FRAMES_X)):
    for k, (bx0, bx1) in enumerate(beam_xs(fi, "roof")):
        roof_piece(f"RafterBeam_S_F{fi}_{k}", "Structure/Beams", bx0, bx1, Y_ROOF0, Y_RIDGE, zu, zj)
        roof_piece(f"RafterBeam_N_F{fi}_{k}", "Structure/Beams", bx0, bx1, Y_RIDGE, Y_ROOF1, zu, zj)

# Rim pieces in the post band of the gable frames (floor edge between the
# single/double beams, carries the sole plate of the gable walls)
for fi in (0, 3):
    x = FRAMES_X[fi]
    for lvl, z0 in (("GF", Z_GF), ("UF", Z_UF)):
        for k, (ya, yb) in enumerate(((BAND, POST_Y[1] - BAND), (POST_Y[1] + 2 * BAND, Y_OUT - BAND))):
            box(f"Rim_{lvl}_F{fi}_{k}", "Structure/Beams", x - POST_W / 2, x + POST_W / 2, ya, yb, z0, z0 + BEAM_D)

ALL_BANDS = bands(-0.1, Y_OUT + 0.1)         # 13 joist bands y = 0, 0.65 ... 7.8


def floor_bay(fi, lvl, z0, band_filter=lambda b: True):
    """Joists between frames fi and fi+1 at floor level: bearer along each
    beam face, joist body between bearers, notched tongue over the bearer."""
    xa = FRAMES_X[fi] + POST_W / 2 + T          # inner beam face of frame fi
    xb = FRAMES_X[fi + 1] - POST_W / 2 - T      # outer beam face of frame fi+1
    coll = "Structure/Floor_Joists"
    kept = [b for b in ALL_BANDS if band_filter(b)]
    yb0, yb1 = kept[0][0], kept[-1][1]            # bearers only where joists are
    box(f"Bearer_{lvl}_B{fi}_W", coll, xa, xa + BEARER, yb0, yb1, z0, z0 + BEARER)
    box(f"Bearer_{lvl}_B{fi}_E", coll, xb - BEARER, xb, yb0, yb1, z0, z0 + BEARER)
    for k, (y0, y1) in enumerate(ALL_BANDS):
        if (y0, y1) not in kept:
            continue
        box(f"Joist_{lvl}_B{fi}_{k:02d}", coll, xa + BEARER, xb - BEARER, y0, y1, z0, z0 + BEAM_D)
        box(f"JoistEnd_{lvl}_B{fi}_{k:02d}_W", coll, xa, xa + BEARER, y0, y1, z0 + BEARER, z0 + BEAM_D)
        box(f"JoistEnd_{lvl}_B{fi}_{k:02d}_E", coll, xb - BEARER, xb, y0, y1, z0 + BEARER, z0 + BEAM_D)


for fi in range(4):
    floor_bay(fi, "GF", Z_GF)
for fi in range(3):
    if fi == 1:
        floor_bay(fi, "UF", Z_UF, lambda b: b[0] > VOID_Y[1] - 1e-6)   # void: keep bands from the middle line north
    else:
        floor_bay(fi, "UF", Z_UF)


def roof_bay(xa, xb, tag, bearer_w=True, bearer_e=True):
    coll = "Structure/Roof_Joists"
    for side, y0, y1 in (("S", Y_ROOF0, Y_RIDGE), ("N", Y_RIDGE, Y_ROOF1)):
        if bearer_w:
            roof_piece(f"RoofBearer_{tag}_{side}_W", coll, xa, xa + BEARER, y0, y1, zu, lambda y: zu(y) + BEARER_V)
        if bearer_e:
            roof_piece(f"RoofBearer_{tag}_{side}_E", coll, xb - BEARER, xb, y0, y1, zu, lambda y: zu(y) + BEARER_V)
    for k, (y0, y1) in enumerate(ALL_BANDS):
        j0 = xa + (BEARER if bearer_w else 0.0)
        j1 = xb - (BEARER if bearer_e else 0.0)
        roof_piece(f"RoofJoist_{tag}_{k:02d}", coll, j0, j1, y0, y1, zu, zj)
        if bearer_w:
            roof_piece(f"RoofJoistEnd_{tag}_{k:02d}_W", coll, xa, xa + BEARER, y0, y1, lambda y: zu(y) + BEARER_V, zj)
        if bearer_e:
            roof_piece(f"RoofJoistEnd_{tag}_{k:02d}_E", coll, xb - BEARER, xb, y0, y1, lambda y: zu(y) + BEARER_V, zj)


for fi in range(4):
    roof_bay(FRAMES_X[fi] + POST_W / 2 + T, FRAMES_X[fi + 1] - POST_W / 2 - T, f"B{fi}")
X_ROOF0 = FRAMES_X[0] - POST_W / 2 - T - OVERHANG_X
X_ROOF1 = FRAMES_X[-1] + POST_W / 2 + T + OVERHANG_X
roof_bay(X_ROOF0, FRAMES_X[0] - POST_W / 2 - T, "OW", bearer_w=False)       # west outriggers
roof_bay(FRAMES_X[-1] + POST_W / 2 + T, X_ROOF1, "OE", bearer_e=False)     # east outriggers

# Bracing: lapped X-braces in the undercroft (bays 1-2, 2-3 on both long
# sides), single diagonals in the wall core of the north-east bay (N3)
BR_W = 0.15


def brace(name, coll, p, q, y0, y1, bounds):
    poly = clip_rect(strip(p, q, BR_W, ext=0.3), *bounds)
    prism_y(name, coll, y0, y1, poly)


for fi in (1, 2):
    xa = FRAMES_X[fi] + POST_W / 2
    xb = FRAMES_X[fi + 1] - POST_W / 2
    zb, zt = Z_POST0 + 0.10, Z_GF - 0.05
    for side, (y0, y1) in (("S", (-POST_OUT - 2 * T, -POST_OUT)), ("N", (Y_OUT + POST_OUT, Y_OUT + POST_OUT + 2 * T))):
        ym = (y0 + y1) / 2
        brace(f"Brace_UC_{side}_B{fi}_a", "Structure/Bracing", (xa, zb), (xb, zt), y0, ym, (xa, xb, zb, zt))
        brace(f"Brace_UC_{side}_B{fi}_b", "Structure/Bracing", (xa, zt), (xb, zb), ym, y1, (xa, xb, zb, zt))

# ------------------------------------------------------------------
# 12. ROOF: ply deck with skylight openings, kerbs, glass, fascias

# Skylights: (x0, x1) clear between trimmers, (y0, y1) = clear between joists
SKYLIGHTS = [
    (4.375, 5.575, ALL_BANDS[1][1], ALL_BANDS[2][0]),
    (6.075, 7.275, ALL_BANDS[1][1], ALL_BANDS[2][0]),
    (4.375, 5.575, ALL_BANDS[3][1], ALL_BANDS[4][0]),
    (6.075, 7.275, ALL_BANDS[3][1], ALL_BANDS[4][0]),
    (8.275, 9.475, ALL_BANDS[8][1], ALL_BANDS[9][0]),
    (9.975, 11.175, ALL_BANDS[8][1], ALL_BANDS[9][0]),
]
holes_xy = []
for i, (x0, x1, y0, y1) in enumerate(SKYLIGHTS):
    coll = "Roof/Skylights"
    # trimmers between the joists (sloped, in the joist slab)
    roof_piece(f"Trimmer_{i}_W", "Structure/Roof_Joists", x0 - T, x0, y0, y1, zu, zj)
    roof_piece(f"Trimmer_{i}_E", "Structure/Roof_Joists", x1, x1 + T, y0, y1, zu, zj)
    kerb_top = lambda y: zj(y) + KERB_H
    roof_piece(f"Kerb_{i}_S", coll, x0 - T, x1 + T, y0 - BAND, y0, zj, kerb_top)
    roof_piece(f"Kerb_{i}_N", coll, x0 - T, x1 + T, y1, y1 + BAND, zj, kerb_top)
    roof_piece(f"Kerb_{i}_W", coll, x0 - T, x0, y0, y1, zj, kerb_top)
    roof_piece(f"Kerb_{i}_E", coll, x1, x1 + T, y0, y1, zj, kerb_top)
    roof_piece(f"SkyGlass_{i}", coll, x0 - T, x1 + T, y0 - BAND, y1 + BAND, kerb_top, lambda y: zj(y) + KERB_H + GLASS)
    holes_xy.append((x0 - T, x1 + T, y0 - BAND, y1 + BAND))


def tile(a0, a1, b0, b1, la, lb, holes, stagger=True):
    """Sheets la x lb tiling the rectangle, rows along b, staggered by la/2
    on odd rows, cut around rectangular holes (ha0, ha1, hb0, hb1)."""
    out = []
    row = 0
    b = b0
    while b < b1 - 1e-6:
        bb = min(b + lb, b1)
        cuts = {a0, a1}
        a = a0 + (la / 2 if (stagger and row % 2) else 0.0)
        while a < a1:
            if a > a0:
                cuts.add(a)
            a += la
        for ha0, ha1, hb0, hb1 in holes:
            if hb0 < bb - 1e-6 and hb1 > b + 1e-6:
                cuts.update([max(ha0, a0), min(ha1, a1)])
        c = sorted(cuts)
        for i in range(len(c) - 1):
            ca, cb = c[i], c[i + 1]
            if cb - ca < 1e-6:
                continue
            # split the cell by hole bottoms/tops
            zc = {b, bb}
            for ha0, ha1, hb0, hb1 in holes:
                if ha0 <= ca + 1e-6 and cb <= ha1 + 1e-6:
                    for h in (hb0, hb1):
                        if b + 1e-6 < h < bb - 1e-6:
                            zc.add(h)
            zc = sorted(zc)
            for j in range(len(zc) - 1):
                za, zb_ = zc[j], zc[j + 1]
                if any(ha0 <= ca + 1e-6 and cb <= ha1 + 1e-6 and hb0 <= za + 1e-6 and zb_ <= hb1 + 1e-6
                       for ha0, ha1, hb0, hb1 in holes):
                    continue
                out.append((ca, cb, za, zb_))
        b = bb
        row += 1
    return out


# deck sheets 2400 along X, 1200 along the slope (projected in plan)
SHEET_A, SHEET_B = 2.4, 1.2 * math.cos(PITCH)
n = 0
for side, y0, y1, flip in (("S", Y_ROOF0, Y_RIDGE, False), ("N", Y_RIDGE, Y_ROOF1, True)):
    cells = tile(X_ROOF0, X_ROOF1, 0.0, y1 - y0, SHEET_A, SHEET_B, [
        (hx0, hx1, (y1 - hy1 if flip else hy0 - y0), (y1 - hy0 if flip else hy1 - y0))
        for hx0, hx1, hy0, hy1 in holes_xy])
    for (ca, cb, ba, bb) in cells:
        ya, yb = (y1 - bb, y1 - ba) if flip else (y0 + ba, y0 + bb)
        roof_piece(f"Deck_{side}_{n:03d}", "Roof/Deck", ca, cb, ya, yb, zj, zd)
        n += 1

# fascias: eave boards (vertical) and gable boards along the slope
FASCIA = 0.025
box("Fascia_S", "Roof/Fascia", X_ROOF0, X_ROOF1, Y_ROOF0 - FASCIA, Y_ROOF0, zu(Y_ROOF0), zd(Y_ROOF0))
box("Fascia_N", "Roof/Fascia", X_ROOF0, X_ROOF1, Y_ROOF1, Y_ROOF1 + FASCIA, zu(Y_ROOF1), zd(Y_ROOF1))
for tag, x0, x1 in (("W", X_ROOF0 - FASCIA, X_ROOF0), ("E", X_ROOF1, X_ROOF1 + FASCIA)):
    roof_piece(f"Fascia_{tag}_S", "Roof/Fascia", x0, x1, Y_ROOF0 - FASCIA, Y_RIDGE, zu, zd)
    roof_piece(f"Fascia_{tag}_N", "Roof/Fascia", x0, x1, Y_RIDGE, Y_ROOF1 + FASCIA, zu, zd)

# ------------------------------------------------------------------
# 13. FLOORS: t&g boards along Y over joists and beams, cut around posts
#     and the void; keruing deck on the patio


def boards(prefix, coll, x0, x1, y0, y1, z0, z1, w, gap, nogo):
    n = 0
    x = x0
    while x < x1 - 1e-6:
        xb = min(x + w, x1)
        ys = [(y0, y1)]
        for nx0, nx1, ny0, ny1 in nogo:
            if nx0 < xb - 1e-6 and nx1 > x + 1e-6:
                new = []
                for ya, yb in ys:
                    if ny0 < yb - 1e-6 and ny1 > ya + 1e-6:
                        if ny0 > ya + 1e-6:
                            new.append((ya, ny0))
                        if ny1 < yb - 1e-6:
                            new.append((ny1, yb))
                    else:
                        new.append((ya, yb))
                ys = new
        for ya, yb in ys:
            box(f"{prefix}_{n:03d}", coll, x, xb, ya, yb, z0, z1)
            n += 1
        x += w + gap


mid_posts = [(x - POST_W / 2, x + POST_W / 2) + post_y_range(POST_Y[1]) for x in FRAMES_X[1:3]]
X_FLOOR0 = FRAMES_X[0] + POST_W / 2
X_FLOOR1 = HOUSE_X1 - POST_W / 2 - T
boards("Board_GF", "Floors/Floor_Boards", X_FLOOR0, X_FLOOR1, BAND, Y_OUT - BAND,
       Z_GF + BEAM_D, FFL_G, BOARD_W, 0.0, mid_posts)
void_nogo = (VOID_X[0] + POST_W / 2 + T, VOID_X[1] - POST_W / 2 - T, 0.0, VOID_Y[1])
boards("Board_UF", "Floors/Floor_Boards", X_FLOOR0, X_FLOOR1, BAND, Y_OUT - BAND,
       Z_UF + BEAM_D, FFL_U, BOARD_W, 0.0, mid_posts + [void_nogo])
boards("Deck_P", "Floors/Patio_Deck", HOUSE_X1 + POST_W / 2 + T, FRAMES_X[-1] - POST_W / 2, 0.0, Y_OUT,
       Z_GF + BEAM_D, FFL_G, DECK_W, DECK_GAP, [])

# ------------------------------------------------------------------
# 14/15. EXTERNAL WALLS + WINDOWS
#
# A wall is described by its band start coordinate `c` across (the core
# occupies [c, c + 0.05]) and the exterior side `out` (-1: exterior at
# lower coordinate).  Pieces are prisms in the (along, z) plane so their
# tops can follow the roof slope on the gable walls.


class Wall:
    def __init__(self, name, axis, c, out, gable):
        self.name, self.axis, self.c, self.out, self.gable = name, axis, c, out, gable

    def across(self, d0, d1):
        """Across-range from offsets measured from the core's exterior face
        (positive = inwards)."""
        if self.out < 0:
            return (self.c + d0, self.c + d1)
        return (self.c + BAND - d1, self.c + BAND - d0)

    def ztop(self, a, c0, c1):
        if self.gable:
            return zu(a)
        return min(zu(c0), zu(c1))

    def piece(self, name, coll, a0, a1, c0, c1, z0, z1):
        """z1 None = follow the roof underside."""
        if a1 - a0 < 1e-6:
            return
        if z1 is None:
            t0, t1 = self.ztop(a0, c0, c1), self.ztop(a1, c0, c1)
        else:
            t0 = t1 = z1
        if min(t0, t1) - z0 < 1e-6:
            return
        poly = [(a0, z0), (a1, z0), (a1, t1), (a0, t0)]
        if self.axis == "x":
            prism_y(name, coll, c0, c1, poly)
        else:
            prism_x(name, coll, c0, c1, poly)


LAYERS = dict(ext=(-PLY, 0.0), core=(0.0, CORE), int=(CORE, CORE + PLY),
              bat_ext=(-PLY - BAT, -PLY), bat_int=(CORE + PLY, CORE + PLY + BAT),
              lining=(-PLY, CORE + PLY), glass=(CORE / 2 - GLASS / 2, CORE / 2 + GLASS / 2),
              leaf=(CORE / 2 - 0.02, CORE / 2 + 0.02))


def rows_for(z0, z1, hole_z):
    if hole_z is None:
        return [(z0, z1)]
    return [(z0, hole_z[0]), (hole_z[1], z1)]


def wall_bay(wall, tag, a0, a1, storey, holes=(), floor_strip=True, core=True, trim=(0.0, 0.0)):
    """One bay of infill between two posts (clear range a0..a1 along the
    wall).  storey 'G' or 'U'.  holes: list of dicts(j0, j1, z0, z1, kind)
    with slot indices; kind in ('window', 'door', 'glazed')."""
    coll = f"Facade/{wall.name}"
    sl = slots(a0, a1)
    bd = bands(a0, a1)
    if storey == "G":
        z_fr, z_sole, z_int, z_top = Z_GF, Z_GF + BEAM_D, FFL_G, Z_UF
    else:
        z_fr, z_sole, z_int, z_top = Z_UF, Z_UF + BEAM_D, FFL_U, None
    z_core = z_sole + T
    # holes in along-coordinates
    H = []
    for h in holes:
        ha0, ha1 = sl[h["j0"]][0], sl[h["j1"]][1]
        hz1 = h["z1"]
        H.append(dict(a0=ha0, a1=ha1, z0=h["z0"], z1=hz1, kind=h["kind"]))

    def hole_at(sa0, sa1):
        for h in H:
            if h["a0"] <= sa0 + 1e-6 and sa1 <= h["a1"] + 1e-6:
                return h
        return None

    def zrows(z0, z1, h):
        if h is None:
            return [(z0, z1)]
        out = []
        if h["z0"] > z0 + 1e-6:
            out.append((z0, h["z0"]))
        if h["z1"] is not None and (z1 is None or h["z1"] < z1 - 1e-6):
            out.append((h["z1"], z1))
        return out

    n = 0
    # sole plate (in the band, on the floor framing) where no hole starts at floor
    sole_ranges = [(a0, a1)]
    for h in H:
        if h["z0"] <= z_int + 1e-6:
            new = []
            for ra, rb in sole_ranges:
                if h["a0"] > ra + 1e-6:
                    new.append((ra, h["a0"]))
                if h["a1"] < rb - 1e-6:
                    new.append((h["a1"], rb))
            sole_ranges = new
    for ra, rb in sole_ranges:
        wall.piece(f"Sole_{tag}_{n}", coll + "/Battens", ra, rb, *wall.across(0.0, CORE), z_sole, z_sole + T)
        n += 1
    # exterior ply: storey panels per slot + floor-zone strip (beam faces trimmed)
    for j, (sa0, sa1) in enumerate(sl):
        h = hole_at(sa0, sa1)
        for za, zb in zrows(z_sole, z_top, h):
            wall.piece(f"Ext_{tag}_{j}_{za:.2f}", coll + "/Cladding_Ext", sa0, sa1, *wall.across(*LAYERS["ext"]), za, zb)
        for za, zb in zrows(z_core, z_top, h):
            if core:
                wall.piece(f"Core_{tag}_{j}_{za:.2f}", coll + "/Core", sa0, sa1, *wall.across(*LAYERS["core"]), za, zb)
        ia0 = sa0 + trim[0] if j == 0 else sa0
        ia1 = sa1 - trim[1] if j == len(sl) - 1 else sa1
        for za, zb in zrows(z_int, z_top, h):
            wall.piece(f"Int_{tag}_{j}_{za:.2f}", coll + "/Cladding_Int", ia0, ia1, *wall.across(*LAYERS["int"]), za, zb)
    if floor_strip:
        wall.piece(f"ExtFloor_{tag}", coll + "/Cladding_Ext", a0 + T, a1 - T, *wall.across(*LAYERS["ext"]), z_fr, z_sole)
    # clamping battens on the bands, outside and inside, skipping holes
    for k, (b0, b1) in enumerate(bd):
        h = hole_at(b0, b1)
        for za, zb in zrows(z_sole, z_top, h):
            wall.piece(f"BatExt_{tag}_{k}_{za:.2f}", coll + "/Battens", b0, b1, *wall.across(*LAYERS["bat_ext"]), za, zb)
        for za, zb in zrows(z_int, z_top, h):
            wall.piece(f"BatInt_{tag}_{k}_{za:.2f}", coll + "/Battens", b0, b1, *wall.across(*LAYERS["bat_int"]), za, zb)
    # window / door / glazed-bay linings
    for hi, h in enumerate(H):
        ha0, ha1, hz0, hz1 = h["a0"], h["a1"], h["z0"], h["z1"]
        lc = wall.across(*LAYERS["lining"])
        gc = wall.across(*LAYERS["glass"])
        wc = coll + "/Windows"
        ja0 = ha0 + trim[0] if abs(ha0 - a0) < 1e-6 else ha0
        jb1 = ha1 - trim[1] if abs(ha1 - a1) < 1e-6 else ha1
        wall.piece(f"Jamb_{tag}_{hi}_a", wc, ja0, ha0 + T, *lc, hz0, hz1)
        wall.piece(f"Jamb_{tag}_{hi}_b", wc, ha1 - T, jb1, *lc, hz0, hz1)
        wall.piece(f"Sill_{tag}_{hi}", wc, ha0 + T, ha1 - T, *lc, hz0, hz0 + T)
        # head: flat, or following the roof when the hole reaches the roof
        if hz1 is None:
            head0 = lambda a: wall.ztop(a, *lc) - T
            # sloped head as a prism with both edges following the roof
            a_, b_ = ha0 + T, ha1 - T
            poly = [(a_, head0(a_)), (b_, head0(b_)), (b_, wall.ztop(b_, *lc)), (a_, wall.ztop(a_, *lc))]
            if wall.axis == "x":
                prism_y(f"Head_{tag}_{hi}", wc, lc[0], lc[1], poly)
            else:
                prism_x(f"Head_{tag}_{hi}", wc, lc[0], lc[1], poly)
            top_in = head0
        else:
            wall.piece(f"Head_{tag}_{hi}", wc, ha0 + T, ha1 - T, *lc, hz1 - T, hz1)
            top_in = lambda a: hz1 - T
        # mullions on the bands inside the hole
        cols = [ha0 + T]
        for b0, b1 in bd:
            if b0 > ha0 + 1e-6 and b1 < ha1 - 1e-6:
                tm = min(top_in(b0), top_in(b1))
                wall.piece(f"Mullion_{tag}_{hi}_{b0:.2f}", wc, b0, b1, *lc, hz0 + T, tm)
                cols += [b0, b1]
        cols.append(ha1 - T)
        # transoms: split the height so no pane is taller than 1.2 m
        for ci in range(0, len(cols), 2):
            ca, cb = cols[ci], cols[ci + 1]
            tm = min(top_in(ca), top_in(cb))
            hgt = tm - (hz0 + T)
            nrows = max(1, math.ceil(hgt / 1.25))
            levels = [hz0 + T]
            for r in range(1, nrows):
                zt = hz0 + T + hgt * r / nrows
                wall.piece(f"Transom_{tag}_{hi}_{ci}_{r}", wc, ca, cb, *lc, zt - T / 2, zt + T / 2)
                levels += [zt - T / 2, zt + T / 2]
            levels.append(tm)
            for r in range(0, len(levels), 2):
                if h["kind"] == "door" and r == 0:
                    wall.piece(f"Leaf_{tag}_{hi}_{ci}", wc, ca, cb, *wall.across(*LAYERS["leaf"]), levels[r], levels[r + 1])
                else:
                    wall.piece(f"Glass_{tag}_{hi}_{ci}_{r}", wc, ca, cb, *gc, levels[r], levels[r + 1])


S_WALL = Wall("South", "x", 0.0, -1, False)
N_WALL = Wall("North", "x", Y_OUT - BAND, +1, False)
W_WALL = Wall("West", "y", FRAMES_X[0] - POST_W / 2, -1, True)
E_WALL = Wall("East", "y", HOUSE_X1 - POST_W / 2, +1, True)

WIN = lambda j0, j1, z0, z1: dict(j0=j0, j1=j1, z0=z0, z1=z1, kind="window")
DOOR = lambda j0, j1, z0, z1: dict(j0=j0, j1=j1, z0=z0, z1=z1, kind="door")
GLAZED_G = [dict(j0=0, j1=5, z0=FFL_G, z1=Z_UF, kind="glazed")]
GLAZED_U = [dict(j0=0, j1=5, z0=FFL_U, z1=None, kind="glazed")]

# eave bays along X (between post faces)
bay_x = [(FRAMES_X[i] + POST_W / 2, FRAMES_X[i + 1] - POST_W / 2) for i in range(3)]
# gable halves along Y (between post faces)
bay_y = [(BAND, POST_Y[1] - BAND), (POST_Y[1] + 2 * BAND, Y_OUT - BAND)]

# South wall
wall_bay(S_WALL, "S1G", *bay_x[0], "G", GLAZED_G, trim=(PLY, 0.0))
wall_bay(S_WALL, "S1U", *bay_x[0], "U", [WIN(1, 4, 4.50, 5.70)], trim=(PLY, 0.0))
wall_bay(S_WALL, "S2G", *bay_x[1], "G", GLAZED_G)
wall_bay(S_WALL, "S2U", *bay_x[1], "U", GLAZED_U)
wall_bay(S_WALL, "S3G", *bay_x[2], "G", [WIN(0, 2, 1.90, 3.10), DOOR(4, 5, FFL_G, 3.10)], trim=(0.0, PLY))
wall_bay(S_WALL, "S3U", *bay_x[2], "U", [WIN(1, 4, 4.50, 5.70)], trim=(0.0, PLY))
# North wall (bay 3 braced: no core, no windows)
wall_bay(N_WALL, "N1G", *bay_x[0], "G", [WIN(1, 2, 1.90, 3.10)], trim=(PLY, 0.0))
wall_bay(N_WALL, "N1U", *bay_x[0], "U", [WIN(2, 3, 4.50, 5.70)], trim=(PLY, 0.0))
wall_bay(N_WALL, "N2G", *bay_x[1], "G", [WIN(1, 4, 1.90, 3.10)])
wall_bay(N_WALL, "N2U", *bay_x[1], "U", [WIN(1, 4, 4.80, 5.70)])
wall_bay(N_WALL, "N3G", *bay_x[2], "G", [], core=False, trim=(0.0, PLY))
wall_bay(N_WALL, "N3U", *bay_x[2], "U", [], core=False, trim=(0.0, PLY))
# West gable
wall_bay(W_WALL, "W1G", *bay_y[0], "G", [WIN(1, 4, 1.90, 3.10)])
wall_bay(W_WALL, "W1U", *bay_y[0], "U", [WIN(1, 4, 4.50, 5.70)])
wall_bay(W_WALL, "W2G", *bay_y[1], "G", [WIN(1, 2, 1.90, 3.10)])
wall_bay(W_WALL, "W2U", *bay_y[1], "U", [WIN(1, 4, 4.50, 5.70)])
# East gable (floor zone = exposed double beam of frame 11.7)
wall_bay(E_WALL, "E1G", *bay_y[0], "G", GLAZED_G, floor_strip=False)
wall_bay(E_WALL, "E1U", *bay_y[0], "U", [WIN(1, 4, 4.50, 5.70)], floor_strip=False)
wall_bay(E_WALL, "E2G", *bay_y[1], "G", [WIN(1, 3, 1.90, 3.10)], floor_strip=False)
wall_bay(E_WALL, "E2U", *bay_y[1], "U", [WIN(1, 4, 4.50, 5.70)], floor_strip=False)

# Storey braces in the N3 core band (one diagonal per storey)
xa, xb = bay_x[2]
c0, c1 = N_WALL.across(0.0, CORE)
brace("Brace_N3_G", "Structure/Bracing", (xa, Z_GF + BEAM_D + T), (xb, Z_UF), c0, c1, (xa, xb, Z_GF + BEAM_D + T, Z_UF))
zt_n3 = zu(Y_OUT)
brace("Brace_N3_U", "Structure/Bracing", (xb, Z_UF + BEAM_D + T), (xa, zt_n3), c0, c1, (xa, xb, Z_UF + BEAM_D + T, zt_n3))

# ------------------------------------------------------------------
# 18. STAIRS: two sloped carriages with cleats and lapped treads, rising
#     east along the north edge of the void onto bay 3

RISE = FFL_U - FFL_G
N_RISERS = 14
RISER = RISE / N_RISERS
GOING = 0.25
TREAD_T = 0.05
X_TOP = VOID_X[1] - POST_W / 2 - T                 # beam face at the landing
X_BOT = X_TOP - (N_RISERS - 1) * GOING
Y_ST0 = VOID_Y[1] - BAND - 0.90                     # stair 0.9 wide against the middle joist line
CAR_W = 0.25
carr_lo = (X_BOT, FFL_G + RISER - TREAD_T - 0.10)
carr_hi = (X_TOP, FFL_U - TREAD_T - 0.10)
for side, (y0, y1) in (("S", (Y_ST0, Y_ST0 + T)), ("N", (Y_ST0 + 0.90 - T, Y_ST0 + 0.90))):
    poly = clip_rect(strip(carr_lo, carr_hi, CAR_W, ext=0.4), X_BOT - 0.3, X_TOP, FFL_G, FFL_U)
    prism_y(f"Carriage_{side}", "Stairs", y0, y1, poly)
for k in range(1, N_RISERS):
    zt = FFL_G + RISER * k
    x0 = X_TOP - (N_RISERS - k) * GOING
    box(f"Tread_{k:02d}", "Stairs", x0, x0 + GOING, Y_ST0 + T, Y_ST0 + 0.90 - T, zt - TREAD_T, zt)
    box(f"Cleat_{k:02d}_S", "Stairs", x0, x0 + GOING, Y_ST0 + T, Y_ST0 + 2 * T, zt - TREAD_T - T, zt - TREAD_T)
    box(f"Cleat_{k:02d}_N", "Stairs", x0, x0 + GOING, Y_ST0 + 0.90 - 2 * T, Y_ST0 + 0.90 - T, zt - TREAD_T - T, zt - TREAD_T)

# stair handrail on the open (south) side: balusters bolted to the carriage face
RAIL_H = 0.90
y0, y1 = Y_ST0 - T, Y_ST0
rail_lo = (X_BOT + GOING / 2, FFL_G + RISER + RAIL_H)
rail_hi = (X_TOP, FFL_U + RAIL_H)
rail_poly = clip_rect(strip(rail_lo, rail_hi, 0.10, ext=0.2), X_BOT, X_TOP, 0, 10)
prism_y("StairRail", "Balustrade", y0, y1, rail_poly)
slope_r = (rail_hi[1] - rail_lo[1]) / (rail_hi[0] - rail_lo[0])
for k in (1, 5, 9, 13):
    zt = FFL_G + RISER * k
    x0 = X_TOP - (N_RISERS - k) * GOING + GOING / 2 - T / 2
    z_rail_under = rail_lo[1] + slope_r * (x0 - rail_lo[0]) - 0.05 / math.cos(math.atan(slope_r)) - 0.002
    box(f"StairBaluster_{k:02d}", "Balustrade", x0, x0 + T, y0, y1, max(zt - 0.25, FFL_G), z_rail_under)

# upper-floor balustrade on the void edges
def balustrade(prefix, along, a0, a1, c0, c1, z_floor, axis):
    """Posts 50 x 50 on the bands, continuous top rail on the posts, mid
    rail segments between the posts (members lap, fig 76-81)."""
    bd = bands(a0, a1)
    for k, (b0, b1) in enumerate(bd):
        if axis == "x":
            box(f"{prefix}_Post_{k}", "Balustrade", b0, b1, c0, c1, z_floor, z_floor + 0.95)
        else:
            box(f"{prefix}_Post_{k}", "Balustrade", c0, c1, b0, b1, z_floor, z_floor + 0.95)
    edges = [a0] + [e for b in bd for e in b] + [a1]
    segs = [(a0, a1, "Top", (z_floor + 0.95, z_floor + 1.05))]
    segs += [(edges[i], edges[i + 1], f"Mid{i // 2}", (z_floor + 0.45, z_floor + 0.50)) for i in range(0, len(edges), 2)]
    for ra, rb, name, zr in segs:
        if axis == "x":
            box(f"{prefix}_Rail_{name}", "Balustrade", ra, rb, c0, c1, *zr)
        else:
            box(f"{prefix}_Rail_{name}", "Balustrade", c0, c1, ra, rb, *zr)


balustrade("Bal_Void_N", "x", VOID_X[0] + POST_W / 2, VOID_X[1] - POST_W / 2, POST_Y[1], POST_Y[1] + BAND, FFL_U, "x")
balustrade("Bal_Void_W", "y", BAND, POST_Y[1] - BAND, VOID_X[0] - POST_W / 2, VOID_X[0] + POST_W / 2, FFL_U, "y")
balustrade("Bal_Void_E", "y", BAND, Y_ST0 - T, VOID_X[1] - POST_W / 2, VOID_X[1] + POST_W / 2, FFL_U, "y")

# patio balustrade (east edge, north edge; south edge with the step opening)
XP0, XP1 = HOUSE_X1 + POST_W / 2, FRAMES_X[-1] - POST_W / 2
STEP_X = (12.40, 13.30)
balustrade("Bal_Patio_E1", "y", BAND, POST_Y[1] - BAND, XP1 - T, XP1, FFL_G, "y")
balustrade("Bal_Patio_E2", "y", POST_Y[1] + 2 * BAND, Y_OUT - BAND, XP1 - T, XP1, FFL_G, "y")
balustrade("Bal_Patio_N", "x", XP0, XP1, Y_OUT - T, Y_OUT, FFL_G, "x")
balustrade("Bal_Patio_S1", "x", XP0, STEP_X[0], 0.0, T, FFL_G, "x")
balustrade("Bal_Patio_S2", "x", STEP_X[1], XP1, 0.0, T, FFL_G, "x")

# patio steps: keruing treads on posts (fig 77), descending south
N_STEP = 5
STEP_R = FFL_G / N_STEP
STEP_G = 0.275
for k in range(1, N_STEP):
    zt = FFL_G - STEP_R * k
    ya = -STEP_G * k
    box(f"Step_{k}", "Stairs", STEP_X[0], STEP_X[1], ya, ya + 0.25, zt - TREAD_T, zt)
    for s, xs in enumerate((STEP_X[0] + 0.05, STEP_X[1] - 0.10)):
        box(f"StepPost_{k}_{s}", "Stairs", xs, xs + T, ya + 0.1, ya + 0.15, PAD_SLAB, zt - TREAD_T)
        box(f"StepPad_{k}_{s}", "Foundation", xs - 0.125, xs + 0.175, ya, ya + 0.25, 0.0, PAD_SLAB)

print("Experiment 08 Fable v02: members =", len([o for o in bpy.data.objects if o.type == "MESH"]))
