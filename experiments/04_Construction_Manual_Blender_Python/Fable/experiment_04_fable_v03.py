# ------------------------------------------------------------------
# CRAFT BOT - Experiment 04 (Fable run) - Prefabricated timber house, v03
# ------------------------------------------------------------------
# Single-storey timber-framed house after the FRIM "Construction Manual
# of Prefabricated Timber House" (1996), now following the manual's own
# plan: 7544 x 5714 platform on 12 posts, walls inset 112 mm, recessed
# verandah at the front-right corner with exposed columns and railings,
# main door from the verandah into living/dining, partitions BR1 / BR2,
# louvre windows, plywood beading over sheet joints, Fink trusses with
# 860 eaves, purlins, fibre-cement sheets, gable ply, entrance stair.
#
# Coordinates: X = length (platform 0..7.544), Y = width (0..5.714,
# verandah / door side at low Y), Z up, ground at z = 0.  Units: metres.
# Axis-aligned members are craftbot.place_element boxes; sloped members
# are convex prisms from a 2D profile (mitred / plumb cut joints).

import bpy
import math
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS (mm values from the manual, converted to m)

PL, PW = 7.544, 5.714             # platform (joist layout 7544 x 5714)
M = 0.61                          # planning grid
P = 0.047                         # plate / stud thickness
SD = 0.097                        # exterior stud depth 47 x 97
SDI = 0.072                       # partition stud depth 47 x 72
PLY_OUT, PLY_IN = 0.009, 0.006    # WBP 9 mm outside, MR 6 mm inside
T = PLY_OUT + SD + PLY_IN         # 0.112 exterior wall / base plate / binder
TI = 2 * PLY_IN + SDI             # 0.084 partition
SHEET_W, SHEET_L = 1.22, 2.44
BEAD_W, BEAD_T = 0.072, 0.009     # plywood beading 9 x 72
SKIRT_H = 0.10                    # plywood skirting 9 x 100

X0, X1 = T, PL - T                # exterior wall outer faces
Y0, Y1 = T, PW - T
XV, YV = 3.884, Y0 + 1.332        # verandah: open corner x > XV, y < YV
YP2 = 3.0                         # BR1 / BR2 partition centre line

# platform
FOOT = 0.60
Z_FOOT_TOP = 0.05
POST, POST_H = 0.12, 0.499
BEARER_W, BEARER_D = 0.06, 0.194
JOIST_W, JOIST_D = 0.047, 0.145
HEADER_T, HEADER_D = 0.02, 0.194
BOARD_T, BOARD_W = 0.022, 0.145
Z_POST_TOP = Z_FOOT_TOP + POST_H
Z_JOIST = Z_POST_TOP + BEARER_D
Z_BOARD = Z_JOIST + JOIST_D
FFL = Z_BOARD + BOARD_T                          # 0.910
POST_X = [X0, X0 + 2.44, X0 + 4.88, X0 + 7.32]   # 3 x 2440 under the wall lines
POST_Y = [0.157, PW / 2, PW - 0.157]             # 2 x 2700

# walls
PANEL_H = 2.745
Z_BASE = FFL
Z_PANEL0 = Z_BASE + P                            # 0.957
Z_PANEL1 = Z_PANEL0 + PANEL_H                    # 3.702
Z_BINDER1 = Z_PANEL1 + P                         # 3.749 exterior binder top
Z_BINDER1_INT = Z_PANEL1 + 0.022                 # 3.724 partition binder (25 clearance)
Z_NOG = Z_PANEL0 + SHEET_L                       # 3.397
Z_STRIP0 = Z_NOG                                 # 305 strip of the verandah "void" panels
LINTEL_D = 0.145
WIN_CLEAR, WIN_H, WIN_SILL = 1.079, 1.587, 0.90
FIXED_LOUVRE_H = 0.376
DOOR_W, DOOR_H, DOOR_T, DOOR_GAP = 0.84, 2.10, 0.04, 0.008
DOOR_W_INT = 0.77
Z_DOOR_HEAD = FFL + DOOR_GAP + DOOR_H + P        # 3.065
GLASS = 0.006
COL = 0.094                                      # exposed verandah column (2 x 47)
RAIL_H = 1.0
BALUSTER = 0.02

# roof
TR_T, TR_D = 0.035, 0.072
TR_SP = 1.22
RISE = 1.195
OVH = 0.86 - T                    # rafter tail 860 from the wall face = 0.748 past the platform edge
GABLE_OVH = 0.30
GUSSET = 0.009
GABLE_PLY = 0.006
PURLIN_W, PURLIN_T = 0.072, 0.035
PURLIN_SP = 0.73
SHEET_T = 0.006
FASCIA_T, FASCIA_D = 0.02, 0.145
BRACE_T, BRACE_W = 0.022, 0.097
NOG_W, NOG_D = 0.038, 0.05
CEIL_T = 0.006

ZB0 = Z_BINDER1
ZB1 = ZB0 + TR_D
YM = PW / 2
SLOPE = RISE / YM
TH = math.atan(SLOPE)
CT, ST = math.cos(TH), math.sin(TH)
DV = TR_D / CT
Z_RAFTER_TOP0 = ZB1 + DV

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
C_PART = "Structure/Partition_Framing"
C_ROOF = "Structure/Roof_Framing"
C_BOARDS = "Floors/Floor_Boards"
C_EXT = "Facade/Exterior_Sheathing"
C_INT = "Facade/Interior_Sheathing"
C_BEAD = "Facade/Beading"
C_OPEN = "Facade/Openings"
C_VER = "Facade/Verandah"
C_GABLE = "Roof/Gable_Sheathing"
C_COVER = "Roof/Roof_Covering"
C_CEIL = "Ceiling"
C_STAIR = "Stairs"

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
    """Profile in (y, z) extruded along X."""
    return prism(name, coll, (0, 0, 0), (0, 1, 0), (0, 0, 1), pts_yz, x0, x1)


def prism_y(name, coll, y0, y1, pts_xz):
    """Profile in (x, z) extruded along Y."""
    return prism(name, coll, (0, 0, 0), (1, 0, 0), (0, 0, 1), pts_xz, -y1, -y0)


def clip(poly, p, n):
    p, n = Vector(p), Vector(n)
    out = []
    for i in range(len(poly)):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % len(poly)])
        da, db = (a - p).dot(n), (b - p).dot(n)
        if da >= 0:
            out.append(tuple(a))
        if (da >= 0) != (db >= 0):
            out.append(tuple(a + (b - a) * (da / (da - db))))
    return out


def strip(p, q, width, ext=0.4):
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x))
    a, b = p - d * ext, q + d * ext
    h = width / 2
    return [tuple(a - n * h), tuple(b - n * h), tuple(b + n * h), tuple(a + n * h)]


def positions(a0, a1, spacing, thick, grid0=None):
    """Member centres: first/last flush with a0/a1, intermediate on the
    grid grid0 + k*spacing (none within half a spacing of the ends)."""
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


def split_range(a0, a1, cuts):
    """Sub-ranges of (a0, a1) outside the sorted cut intervals."""
    out, start = [], a0
    for ca, cb in sorted(cuts):
        if cb <= a0 or ca >= a1:
            continue
        if ca > start:
            out.append((start, ca))
        start = max(start, cb)
    if start < a1 - 1e-6:
        out.append((start, a1))
    return out


def rect_fn(coll, along, b0, b1):
    """Box maker for a wall running along 'x' or 'y' with thickness b0..b1."""
    def rect(name, p0, p1, z0, z1, bb0=b0, bb1=b1):
        if along == "x":
            return box(name, coll, p0, p1, bb0, bb1, z0, z1)
        return box(name, coll, bb0, bb1, p0, p1, z0, z1)
    return rect


def tile_sheets(prefix, coll, x0, x1, y0, y1, z0, z1):
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
    """Upright 1220 x 2440 sheets plus a top strip, cut around holes
    [(aa, ab, za, zb)] column by column."""
    rect = rect_fn(coll, along, b0, b1)
    cols = {a0, a1}
    a = a0 + SHEET_W
    while a < a1 - 1e-6:
        cols.add(a)
        a += SHEET_W
    for aa, ab, _, _ in holes:
        cols |= {aa, ab}
    cols = sorted(c for c in cols if a0 - 1e-9 <= c <= a1 + 1e-9)
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


def stud_wall(prefix, coll, along, a0, a1, b0, b1, z0, z1, grid0, openings=(), lintel_d=LINTEL_D):
    """Panel framing: bottom plate (cut at doors), single top plate, studs
    on the grid, noggings at the sheet joint, framed openings (jack +
    king studs, lintel, cripples, window sill).
    openings = [(aa, ab, z_sill | None, z_head)]."""
    rect = rect_fn(coll, along, b0, b1)
    doors = [(aa, ab) for aa, ab, zs, _ in openings if zs is None]
    for i, (sa, sb) in enumerate(split_range(a0, a1, doors)):
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
        rect(f"{prefix}_Op{k}_JackL", aa - P, aa, zs0, zh)
        rect(f"{prefix}_Op{k}_KingL", aa - 2 * P, aa - P, zs0, zt)
        rect(f"{prefix}_Op{k}_JackR", ab, ab + P, zs0, zh)
        rect(f"{prefix}_Op{k}_KingR", ab + P, ab + 2 * P, zs0, zt)
        rect(f"{prefix}_Op{k}_Lintel", aa - P, ab + P, zh, zh + lintel_d)
        verticals += [(aa - 2 * P, aa - P), (ab + P, ab + 2 * P)]
        for j, c in enumerate(positions(aa - P, ab + P, M, P, grid0)[1:-1]):
            rect(f"{prefix}_Op{k}_Cripple_{j}", c - P / 2, c + P / 2, zh + lintel_d, zt)
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


def beads(prefix, along, a0, a1, b_face, out_sign, z0, z1, holes):
    """Plywood beading 9 x 72 on the exterior face: horizontal at the base
    plate joint, the 2440 sheet joint and the binder joint; vertical at
    every 1220 sheet joint; all split around openings."""
    bb = (b_face, b_face + out_sign * BEAD_T)
    rect = rect_fn(C_BEAD, along, min(bb), max(bb))
    n = 0
    z_rows = [z0, z0 + SHEET_L, z1]
    for zc in z_rows:
        cuts = [(aa, ab) for aa, ab, za, zb in holes if za < zc + BEAD_W / 2 and zb > zc - BEAD_W / 2]
        for sa, sb in split_range(a0, a1, cuts):
            rect(f"{prefix}_H{n:02d}", sa, sb, zc - BEAD_W / 2, zc + BEAD_W / 2)
            n += 1
    a = a0 + SHEET_W
    while a < a1 - 1e-6:
        cuts = [(za, zb) for aa, ab, za, zb in holes if aa < a + BEAD_W / 2 and ab > a - BEAD_W / 2]
        for j in range(len(z_rows) - 1):
            za0, za1 = z_rows[j] + BEAD_W / 2, z_rows[j + 1] - BEAD_W / 2
            for sa, sb in split_range(za0, za1, cuts):
                rect(f"{prefix}_V{n:02d}", a - BEAD_W / 2, a + BEAD_W / 2, sa, sb)
                n += 1
        a += SHEET_W


def skirting(prefix, along, a0, a1, b_face, out_sign, doors):
    bb = (b_face, b_face + out_sign * BEAD_T)
    rect = rect_fn(C_BEAD, along, min(bb), max(bb))
    for i, (sa, sb) in enumerate(split_range(a0, a1, doors)):
        rect(f"{prefix}_{i}", sa, sb, FFL, FFL + SKIRT_H)


def louvre_blades(prefix, along, a0, a1, b0, b1, z0, z1, n, width, tilt_deg):
    """n glass louvre blades between z0 and z1, hinge line centred in the
    frame depth b0..b1, tilted tilt_deg from vertical."""
    pitch = (z1 - z0) / n
    bc = (b0 + b1) / 2
    d = Vector((math.sin(math.radians(tilt_deg)), math.cos(math.radians(tilt_deg))))
    nrm = Vector((-d.y, d.x))
    for k in range(n):
        c = Vector((bc, z0 + k * pitch + pitch / 2))
        pts = [tuple(c + d * s + nrm * t) for s, t in
               ((-width / 2, -GLASS / 2), (width / 2, -GLASS / 2), (width / 2, GLASS / 2), (-width / 2, GLASS / 2))]
        if along == "x":
            prism_x(f"{prefix}_{k}", C_OPEN, a0, a1, pts)
        else:
            prism_y(f"{prefix}_{k}", C_OPEN, a0, a1, pts)


def window_unit(prefix, along, aa, ab, zs, zh, b0, b1):
    """Frame ex 47 x 112 (full wall depth), central mullion, 8 adjustable
    louvre leaves below and 3 fixed glass louvres above in each half."""
    rect = rect_fn(C_OPEN, along, b0, b1)
    rect(f"{prefix}_JambL", aa, aa + P, zs, zh)
    rect(f"{prefix}_JambR", ab - P, ab, zs, zh)
    rect(f"{prefix}_Head", aa + P, ab - P, zh - P, zh)
    rect(f"{prefix}_Sill", aa + P, ab - P, zs, zs + P)
    am = (aa + ab) / 2
    rect(f"{prefix}_Mullion", am - P / 2, am + P / 2, zs + P, zh - P)
    rect(f"{prefix}_Transom", aa + P, am - P / 2, zh - P - FIXED_LOUVRE_H - P / 2, zh - P - FIXED_LOUVRE_H + P / 2)
    rect(f"{prefix}_Transom2", am + P / 2, ab - P, zh - P - FIXED_LOUVRE_H - P / 2, zh - P - FIXED_LOUVRE_H + P / 2)
    z_tr = zh - P - FIXED_LOUVRE_H
    for half, (la, lb) in enumerate(((aa + P, am - P / 2), (am + P / 2, ab - P))):
        louvre_blades(f"{prefix}_Louvre{half}", along, la, lb, b0, b1, zs + P, z_tr - P / 2, 8, 0.14, 20)
        louvre_blades(f"{prefix}_Fixed{half}", along, la, lb, b0, b1, z_tr + P / 2, zh - P, 3, 0.11, 45)


def door_unit(prefix, along, aa, ab, zh, b0, b1, leaf_b0):
    rect = rect_fn(C_OPEN, along, b0, b1)
    rect(f"{prefix}_JambL", aa, aa + P, FFL, zh)
    rect(f"{prefix}_JambR", ab - P, ab, FFL, zh)
    rect(f"{prefix}_Head", aa + P, ab - P, zh - P, zh)
    rect(f"{prefix}_Leaf", aa + P, ab - P, FFL + DOOR_GAP, FFL + DOOR_GAP + DOOR_H, leaf_b0, leaf_b0 + DOOR_T)


def window_at(c):
    """Window between the grid studs at c and c + 1220: jacks inside them."""
    aa = c + P / 2 + P
    return (aa, aa + WIN_CLEAR, FFL + WIN_SILL, FFL + WIN_SILL + WIN_H)


def door_right_of_stud(c, clear):
    """Door whose right king stud is the grid stud at c."""
    ab = c - P / 2 - P
    return (ab - clear, ab, None, Z_DOOR_HEAD)


def ext_wall(prefix, along, b0, b1, ext_lo, frame, ext, int_, grid0, openings=(),
             bead_ext=None, skirt_ext=None, skirt_cuts=()):
    """Exterior wall: zone b0..b1 (112), exterior face at b0 if ext_lo else
    b1; framing / exterior ply / interior ply extents along the wall."""
    if ext_lo:
        s0, s1 = b0 + PLY_OUT, b0 + PLY_OUT + SD
        e0, e1 = b0, b0 + PLY_OUT
        i0, i1 = b1 - PLY_IN, b1
        face_out, sign_out, face_in, sign_in = b0, -1, b1, 1
    else:
        s0, s1 = b1 - PLY_OUT - SD, b1 - PLY_OUT
        e0, e1 = b1 - PLY_OUT, b1
        i0, i1 = b0, b0 + PLY_IN
        face_out, sign_out, face_in, sign_in = b1, 1, b0, -1
    stud_wall(prefix, C_WALL, along, frame[0], frame[1], s0, s1, Z_PANEL0, Z_PANEL1, grid0, openings)
    holes = [(aa, ab, Z_PANEL0 if zs is None else zs, zh) for aa, ab, zs, zh in openings]
    doors = [(aa, ab) for aa, ab, zs, _ in openings if zs is None]
    clad(f"Ply_Ext_{prefix}", C_EXT, along, ext[0], ext[1], e0, e1, Z_PANEL0, Z_PANEL1, holes)
    clad(f"Ply_Int_{prefix}", C_INT, along, int_[0], int_[1], i0, i1, Z_PANEL0, Z_PANEL1, holes)
    be = bead_ext or ext
    se = skirt_ext or int_
    beads(f"Bead_{prefix}", along, be[0], be[1], face_out, sign_out, Z_PANEL0, Z_PANEL1, holes)
    skirting(f"Skirt_{prefix}", along, se[0], se[1], face_in, sign_in, doors + list(skirt_cuts))
    for k, (aa, ab, zs, zh) in enumerate(openings):
        if zs is None:
            leaf_b0 = (i0 - DOOR_T) if ext_lo else i1
            door_unit(f"Door_{prefix}", along, aa, ab, zh, b0, b1, leaf_b0)
        else:
            window_unit(f"Window_{prefix}{k}", along, aa, ab, zs, zh, b0, b1)


def partition(prefix, along, b0, b1, a0, a1, openings=(), skirt_cuts_a=(), skirt_cuts_b=()):
    """Non-load-bearing partition: 47 x 72 studs, 6 mm ply both sides,
    base plate 47 x 84, head binder 22 x 84 (clear of the trusses)."""
    s0, s1 = b0 + PLY_IN, b1 - PLY_IN
    rect = rect_fn(C_PART, along, b0, b1)
    doors = [(aa, ab) for aa, ab, zs, _ in openings if zs is None]
    for i, (sa, sb) in enumerate(split_range(a0, a1, doors)):
        rect(f"{prefix}_BasePlate_{i}", sa, sb, Z_BASE, Z_PANEL0)
    rect(f"{prefix}_HeadBinder", a0, a1, Z_PANEL1, Z_BINDER1_INT)
    stud_wall(prefix, C_PART, along, a0, a1, s0, s1, Z_PANEL0, Z_PANEL1, a0, openings, lintel_d=LINTEL_D)
    holes = [(aa, ab, Z_PANEL0, zh) for aa, ab, zs, zh in openings]
    clad(f"Ply_{prefix}_A", C_INT, along, a0, a1, b0, b0 + PLY_IN, Z_PANEL0, Z_PANEL1, holes)
    clad(f"Ply_{prefix}_B", C_INT, along, a0, a1, b1 - PLY_IN, b1, Z_PANEL0, Z_PANEL1, holes)
    skirting(f"Skirt_{prefix}_A", along, a0, a1, b0, -1, doors + list(skirt_cuts_a))
    skirting(f"Skirt_{prefix}_B", along, a0, a1, b1, 1, doors + list(skirt_cuts_b))
    for k, (aa, ab, zs, zh) in enumerate(openings):
        door_unit(f"Door_{prefix}{k}", along, aa, ab, zh, b0, b1, b1 - PLY_IN - DOOR_T)


# ------------------------------------------------------------------
# 1. FOUNDATION: 12 footings on 3 x 2440 / 2 x 2700 centres, posts 120 x 120

for i, x in enumerate(POST_X):
    for j, y in enumerate(POST_Y):
        box(f"Footing_{i}{j}", C_FOUND, x - FOOT / 2, x + FOOT / 2, y - FOOT / 2, y + FOOT / 2, -0.30, Z_FOOT_TOP)
        box(f"Post_{i}{j}", C_FOUND, x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, Z_FOOT_TOP, Z_POST_TOP)

# ------------------------------------------------------------------
# 2. PLATFORM 7544 x 5714: paired bearers, joists @610 under the stud
#    grid (+ one under the BR/LD partition), stiffeners, headers, T&G floor

for j, y in enumerate(POST_Y):
    for k, side in enumerate((-1, 1)):
        ya = y + side * POST / 2 + (0 if side > 0 else -BEARER_W)
        box(f"Bearer_{j}{'ab'[k]}", C_FLOOR, 0.0, PL, ya, ya + BEARER_W, Z_POST_TOP, Z_JOIST)
joist_x = positions(0.0, PL, M, JOIST_W, X0) + [XV + T / 2]   # extra joist under partition P1
joist_x.sort()
joists = []
for i, xc in enumerate(joist_x):
    box(f"Joist_{i:02d}", C_FLOOR, xc - JOIST_W / 2, xc + JOIST_W / 2, HEADER_T, PW - HEADER_T, Z_JOIST, Z_BOARD)
    joists.append((xc - JOIST_W / 2, xc + JOIST_W / 2))
for i in range(len(joists) - 1):
    xa, xb = joists[i][1], joists[i + 1][0]
    box(f"Stiffener_S_{i:02d}", C_FLOOR, xa, xb, 0.07, 0.12, Z_BOARD - 0.05, Z_BOARD)
    box(f"Stiffener_N_{i:02d}", C_FLOOR, xa, xb, PW - 0.12, PW - 0.07, Z_BOARD - 0.05, Z_BOARD)
    box(f"Stiffener_M_{i:02d}", C_FLOOR, xa, xb, PW / 2 - 0.025, PW / 2 + 0.025, Z_BOARD - 0.075, Z_BOARD)
box("Header_Joist_S", C_FLOOR, 0.0, PL, 0.0, HEADER_T, FFL - HEADER_D, FFL)
box("Header_Joist_N", C_FLOOR, 0.0, PL, PW - HEADER_T, PW, FFL - HEADER_D, FFL)
n, y = 0, HEADER_T
while y < PW - HEADER_T - 1e-6:
    yy = min(y + BOARD_W, PW - HEADER_T)
    box(f"Floor_Board_{n:02d}", C_BOARDS, 0.0, PL, y, yy, Z_BOARD, FFL)
    n += 1
    y = yy

# ------------------------------------------------------------------
# 3. EXTERIOR WALLS (zone 112, walls inset 112 from the platform edge).
#    Through walls: S (front, up to the verandah side wall), verandah back
#    wall, N (back).  Butting walls: W, E, verandah side wall.

P1_B0 = XV + (T - TI) / 2                              # partition P1 zone (84 centred in the 112 line)
P1_CUT = (P1_B0 - BEAD_T, P1_B0 + TI + BEAD_T)
P2_CUT = (YP2 - TI / 2 - BEAD_T, YP2 + TI / 2 + BEAD_T)
WIN_S = window_at(X0 + 2 * M)                          # BR1 front window
WIN_W = window_at(Y0 + 6 * M)                          # BR2 side window
WIN_E = window_at(Y0 + 5 * M)                          # living / dining side window
DOOR_MAIN = door_right_of_stud(X0 + 8 * M, DOOR_W + 2 * P)   # main door opposite the stair
WIN_VB = window_at(X0 + 9 * M)                         # living / dining verandah window

# front wall (y = Y0) from the west corner to the verandah side wall
ext_wall("S", "x", Y0, Y0 + T, True,
         frame=(X0 + PLY_OUT, XV + T - PLY_OUT), ext=(X0, XV + T), int_=(X0 + T - PLY_IN, XV),
         grid0=X0, openings=[WIN_S], skirt_ext=(X0 + T + BEAD_T, XV))
# verandah side wall (x = XV .. XV + T), exterior face toward the verandah (+x)
ext_wall("VS", "y", XV, XV + T, False,
         frame=(Y0 + T, YV - T), ext=(Y0 + PLY_OUT, YV - T), int_=(Y0 + T, YV),
         grid0=Y0, bead_ext=(Y0 + T, YV - T - BEAD_T), skirt_ext=(Y0 + T + BEAD_T, YV))
# verandah back wall (y = YV - T .. YV), exterior face toward the verandah (-y)
ext_wall("VB", "x", YV - T, YV, True,
         frame=(XV + PLY_OUT, X1 - PLY_OUT), ext=(XV + PLY_IN, X1), int_=(XV + PLY_IN, X1 - T),
         grid0=X0, openings=[DOOR_MAIN, WIN_VB], bead_ext=(XV + T + BEAD_T, X1 - T), skirt_cuts=[P1_CUT])
# back wall (y = Y1 - T .. Y1)
ext_wall("N", "x", Y1 - T, Y1, False,
         frame=(X0 + PLY_OUT, X1 - PLY_OUT), ext=(X0, X1), int_=(X0 + T - PLY_IN, X1 - T + PLY_IN),
         grid0=X0, skirt_ext=(X0 + T + BEAD_T, X1 - T - BEAD_T), skirt_cuts=[P1_CUT])
# west gable wall
ext_wall("W", "y", X0, X0 + T, True,
         frame=(Y0 + T, Y1 - T), ext=(Y0 + PLY_OUT, Y1 - PLY_OUT), int_=(Y0 + T, Y1 - T),
         grid0=Y0, openings=[WIN_W], skirt_ext=(Y0 + T + BEAD_T, Y1 - T - BEAD_T), skirt_cuts=[P2_CUT])
# east gable wall, from the verandah back wall to the back wall
ext_wall("E", "y", X1 - T, X1, False,
         frame=(YV, Y1 - T), ext=(YV - T + PLY_OUT, Y1 - PLY_OUT), int_=(YV, Y1 - T),
         grid0=Y0, openings=[WIN_E], skirt_ext=(YV + BEAD_T, Y1 - T - BEAD_T))

# base plates 47 x 112 and head binders 47 x 112
STAIR_BAY = (XV + T, X0 + 8 * M - P / 2 - P)          # open bay between the verandah wall and the first column
for i, (sa, sb) in enumerate(split_range(X0, X1, [STAIR_BAY])):
    box(f"Base_Plate_S_{i}", C_WALL, sa, sb, Y0, Y0 + T, Z_BASE, Z_PANEL0)
box("Base_Plate_N", C_WALL, X0, X1, Y1 - T, Y1, Z_BASE, Z_PANEL0)
box("Base_Plate_W", C_WALL, X0, X0 + T, Y0 + T, Y1 - T, Z_BASE, Z_PANEL0)
box("Base_Plate_E", C_WALL, X1 - T, X1, Y0 + T, Y1 - T, Z_BASE, Z_PANEL0)
box("Base_Plate_VS", C_WALL, XV, XV + T, Y0 + T, YV - T, Z_BASE, Z_PANEL0)
for i, (sa, sb) in enumerate(split_range(XV, X1 - T, [(DOOR_MAIN[0], DOOR_MAIN[1])])):
    box(f"Base_Plate_VB_{i}", C_WALL, sa, sb, YV - T, YV, Z_BASE, Z_PANEL0)
box("Head_Binder_S", C_WALL, X0, X1, Y0, Y0 + T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_N", C_WALL, X0, X1, Y1 - T, Y1, Z_PANEL1, Z_BINDER1)
box("Head_Binder_W", C_WALL, X0, X0 + T, Y0 + T, Y1 - T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_E", C_WALL, X1 - T, X1, Y0 + T, Y1 - T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_VS", C_WALL, XV, XV + T, Y0 + T, YV - T, Z_PANEL1, Z_BINDER1)
box("Head_Binder_VB", C_WALL, XV, X1 - T, YV - T, YV, Z_PANEL1, Z_BINDER1)

# ------------------------------------------------------------------
# 4. VERANDAH: exposed columns on the truss lines, "void" panel top rail
#    with 305 ply strips both faces, railings 47 x 97 with 20 x 20 balusters

COL_X = [X0 + 8 * M, X0 + 10 * M]                    # 4.992, 6.212 (under trusses)
for i, xc in enumerate(COL_X):
    box(f"Ver_Column_S{i}", C_VER, xc - COL / 2, xc + COL / 2, Y0 + PLY_OUT, Y0 + PLY_OUT + SD, Z_PANEL0, Z_PANEL1 - P)
box("Ver_Column_SE", C_VER, X1 - T, X1 - PLY_OUT, Y0 + PLY_OUT, Y0 + T, Z_PANEL0, Z_PANEL1 - P)   # corner, inside the strips
box("Ver_Column_E", C_VER, X1 - PLY_OUT - SD, X1 - PLY_OUT, YV - T - COL, YV - T, Z_PANEL0, Z_PANEL1 - P)
box("Ver_TopRail_S", C_VER, XV + T, X1 - T, Y0 + PLY_OUT, Y0 + PLY_OUT + SD, Z_PANEL1 - P, Z_PANEL1)
box("Ver_TopRail_E", C_VER, X1 - PLY_OUT - SD, X1 - PLY_OUT, Y0 + T, YV - T, Z_PANEL1 - P, Z_PANEL1)
box("Ver_Strip_S_out", C_VER, XV + T, X1, Y0, Y0 + PLY_OUT, Z_STRIP0, Z_PANEL1)
box("Ver_Strip_S_in", C_VER, XV + T + BEAD_T, X1 - T, Y0 + T - PLY_IN, Y0 + T, Z_STRIP0, Z_PANEL1)
box("Ver_Strip_E_out", C_VER, X1 - PLY_OUT, X1, Y0 + PLY_OUT, YV - T, Z_STRIP0, Z_PANEL1)
box("Ver_Strip_E_in", C_VER, X1 - T, X1 - T + PLY_IN, Y0 + T, YV - T, Z_STRIP0, Z_PANEL1)
# railings: bays between columns along the front (except the stair bay) and the east side
RAIL_BAYS = [("x", COL_X[0] + COL / 2, COL_X[1] - COL / 2), ("x", COL_X[1] + COL / 2, X1 - T),
             ("y", Y0 + T, YV - T - COL)]
for i, (along, a0, a1) in enumerate(RAIL_BAYS):
    if along == "x":
        rect = rect_fn(C_VER, "x", Y0 + PLY_OUT, Y0 + PLY_OUT + SD)
        rect_b = rect_fn(C_VER, "x", Y0 + T / 2 - BALUSTER / 2, Y0 + T / 2 + BALUSTER / 2)
    else:
        rect = rect_fn(C_VER, "y", X1 - PLY_OUT - SD, X1 - PLY_OUT)
        rect_b = rect_fn(C_VER, "y", X1 - T / 2 - BALUSTER / 2, X1 - T / 2 + BALUSTER / 2)
    rect(f"Ver_Rail_{i}", a0, a1, FFL + RAIL_H - P, FFL + RAIL_H)
    nb = int((a1 - a0) / 0.10)
    for k in range(nb):
        c = a0 + (a1 - a0) * (k + 0.5) / nb
        rect_b(f"Ver_Baluster_{i}_{k:02d}", c - BALUSTER / 2, c + BALUSTER / 2, Z_PANEL0, FFL + RAIL_H - P)

# ------------------------------------------------------------------
# 5. PARTITIONS: P1 between bedrooms and living/dining (x = XV line,
#    continuing the verandah side wall), P2 between BR1 and BR2

DOOR_BR1 = (YV + 0.40, YV + 0.40 + DOOR_W_INT + 2 * P, None, Z_DOOR_HEAD)
DOOR_BR2 = (YP2 + 0.60, YP2 + 0.60 + DOOR_W_INT + 2 * P, None, Z_DOOR_HEAD)
partition("P1", "y", P1_B0, P1_B0 + TI, YV, Y1 - T, openings=[DOOR_BR1, DOOR_BR2], skirt_cuts_a=[P2_CUT])
partition("P2", "x", YP2 - TI / 2, YP2 + TI / 2, X0 + T, P1_B0)

# ------------------------------------------------------------------
# 6. ROOF TRUSSES: Fink trusses 35 x 72 @ 1220 on the stud grid, bottom
#    chord over the full platform width (bears on the whole binder), rafter
#    tails 860 from the wall face; 9 mm ply gussets both faces.

truss_x = [X0 + GABLE_PLY] + [X0 + k * TR_SP - TR_T / 2 for k in range(1, 6)] + [X1 - GABLE_PLY - TR_T]


def zu_s(y):
    return ZB1 + SLOPE * y


def zu_n(y):
    return ZB1 + SLOPE * (PW - y)


BELOW_S = ((0.0, ZB1), (SLOPE, -1.0))
BELOW_N = ((PW, ZB1), (-SLOPE, -1.0))
ABOVE_CHORD = ((0.0, ZB1), (0.0, 1.0))
BELOW_S_TOP = ((0.0, ZB1 + DV), (SLOPE, -1.0))
BELOW_N_TOP = ((PW, ZB1 + DV), (-SLOPE, -1.0))
ABOVE_CHORD_BOT = ((0.0, ZB0), (0.0, 1.0))

B1, B2 = (PW / 3, ZB1), (2 * PW / 3, ZB1)
T1, T2 = (YM / 2, zu_s(YM / 2)), (PW - YM / 2, zu_n(PW - YM / 2))
APEX = (YM, zu_s(YM))
RAFTER_S = [(-OVH, zu_s(-OVH)), (YM, zu_s(YM)), (YM, zu_s(YM) + DV), (-OVH, zu_s(-OVH) + DV)]
RAFTER_N = [(PW + OVH, zu_n(PW + OVH)), (YM, zu_n(YM)), (YM, zu_n(YM) + DV), (PW + OVH, zu_n(PW + OVH) + DV)]
WEBS = [
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

GUSSETS = [
    ("Apex", (YM - 0.18, YM + 0.18), (APEX[1] - 0.14, APEX[1] + 0.10)),
    ("HeelS", (0.0, 0.15), (ZB0, ZB0 + 0.10)),
    ("HeelN", (PW - 0.15, PW), (ZB0, ZB0 + 0.10)),
    ("B1", (B1[0] - 0.125, B1[0] + 0.125), (ZB0, ZB0 + 0.20)),
    ("B2", (B2[0] - 0.125, B2[0] + 0.125), (ZB0, ZB0 + 0.20)),
]
gusset_polys = {}
for name, node in (("T1", T1), ("T2", T2)):
    d = Vector((CT, ST)) if name == "T1" else Vector((-CT, ST))
    nrm = Vector((-d.y, d.x))
    if nrm.y < 0:
        nrm = -nrm
    c = Vector(node) + nrm * (TR_D / 2)
    gusset_polys[name] = [tuple(c + d * a + nrm * b) for a, b in
                          ((-0.225, -TR_D / 2 - 0.11), (0.225, -TR_D / 2 - 0.11), (0.225, TR_D / 2), (-0.225, TR_D / 2))]
for name, (ya, yb), (za, zb) in GUSSETS:
    poly = [(ya, za), (yb, za), (yb, zb), (ya, zb)]
    for p, nrm in (ABOVE_CHORD_BOT, BELOW_S_TOP, BELOW_N_TOP):
        poly = clip(poly, p, nrm)
    gusset_polys[name] = poly

for i, x0 in enumerate(truss_x):
    x1 = x0 + TR_T
    t = f"Truss_{i}"
    prism_x(f"{t}_BottomChord", C_ROOF, x0, x1, [(0.0, ZB0), (PW, ZB0), (PW, ZB1), (0.0, ZB1)])
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
# 7. ROOF BRACING 22 x 97: diagonal braces under the rafters (gable apex
#    to the heel of the centre truss, both slopes, both ends), bottom-chord
#    runners, web runners.

X_IN0 = truss_x[0] + TR_T + GUSSET
X_IN1 = truss_x[-1] - GUSSET
XC = truss_x[3] + TR_T / 2


def roof_frame(south):
    if south:
        return (0.0, 0.0, ZB1), (1, 0, 0), (0, CT, ST)
    return (PL, PW, ZB1), (-1, 0, 0), (0, -CT, ST)


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
            ua, ub = PL - ub, PL - ua
        va, vb = y_to_v(YM - 0.15), y_to_v(0.15)
        pa, pb = ((ua, va), (ub, vb)) if end == 0 else ((ua, vb), (ub, va))
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
    if nrm.dot(Vector((0 if name == "W1" else PW, ZB1)) - mid) < 0:
        nrm = -nrm
    pts = [tuple(mid + d * s + nrm * t) for s, t in
           ((-BRACE_W / 2, TR_D / 2), (BRACE_W / 2, TR_D / 2),
            (BRACE_W / 2, TR_D / 2 + BRACE_T), (-BRACE_W / 2, TR_D / 2 + BRACE_T))]
    prism_x(f"Runner_Web_{name}", C_ROOF, X_IN0, X_IN1, pts)

# ------------------------------------------------------------------
# 8. PURLINS @730, ROOF SHEETS, RIDGE, FASCIA, BARGE BOARDS


def roof_pt(south, v, t):
    y = v * CT - t * ST
    z = Z_RAFTER_TOP0 + v * ST + t * CT
    return (y if south else PW - y, z)


def v_at(y, t):
    return (y + t * ST) / CT


V_TAIL = v_at(-OVH, 0.0)
V_APEX = v_at(YM, 0.0)
PURLIN_V = [V_TAIL + 0.08 + k * PURLIN_SP for k in range(6)]
X_ROOF0, X_ROOF1 = X0 - GABLE_OVH, X1 + GABLE_OVH
N_SHEETS = 8
SHEET_X = [X_ROOF0 + k * (X_ROOF1 - X_ROOF0) / N_SHEETS for k in range(N_SHEETS + 1)]
Z_SHEET0, Z_SHEET1 = PURLIN_T, PURLIN_T + SHEET_T
Y_EAVE = -OVH - 0.05

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
    t0, t1 = Z_SHEET1, Z_SHEET1 + SHEET_T
    pts = [roof_pt(south, v_at(YM, t0) - 0.25, t0), roof_pt(south, v_at(YM, t0), t0),
           roof_pt(south, v_at(YM, t1), t1), roof_pt(south, v_at(YM, t1) - 0.25, t1)]
    prism_x(f"Ridge_Cap_{tag}", C_COVER, X_ROOF0, X_ROOF1, pts)
    z_top = roof_pt(True, v_at(-OVH - FASCIA_T, Z_SHEET0), Z_SHEET0)[1]
    if south:
        box("Fascia_S", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, -OVH - FASCIA_T, -OVH, z_top - FASCIA_D, z_top)
    else:
        box("Fascia_N", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, PW + OVH, PW + OVH + FASCIA_T, z_top - FASCIA_D, z_top)
    for end, (xa, xb) in enumerate(((X_ROOF0 - FASCIA_T, X_ROOF0), (X_ROOF1, X_ROOF1 + FASCIA_T))):
        pts = [roof_pt(south, v_at(-OVH, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0), Z_SHEET0),
               roof_pt(south, v_at(-OVH, Z_SHEET0), Z_SHEET0)]
        prism_x(f"Barge_{tag}_{end}", C_COVER, xa, xb, pts)

# ------------------------------------------------------------------
# 9. GABLE ENDS: 6 mm ply on the outer face of the end trusses

GABLE_MAIN = [(0.0, ZB0), (PW, ZB0), (PW, zu_n(PW) + DV), (YM, zu_s(YM) + DV), (0.0, zu_s(0.0) + DV)]
GABLE_TAIL_S = [(-OVH, zu_s(-OVH)), (0.0, zu_s(0.0)), (0.0, zu_s(0.0) + DV), (-OVH, zu_s(-OVH) + DV)]
GABLE_TAIL_N = [(PW + OVH, zu_n(PW + OVH)), (PW, zu_n(PW)), (PW, zu_n(PW) + DV), (PW + OVH, zu_n(PW + OVH) + DV)]
for end, (xa, xb) in enumerate(((X0, X0 + GABLE_PLY), (X1 - GABLE_PLY, X1))):
    prism_x(f"Gable_Ply_{end}_Main", C_GABLE, xa, xb, GABLE_MAIN)
    prism_x(f"Gable_Ply_{end}_TailS", C_GABLE, xa, xb, GABLE_TAIL_S)
    prism_x(f"Gable_Ply_{end}_TailN", C_GABLE, xa, xb, GABLE_TAIL_N)

# ------------------------------------------------------------------
# 10. CEILING: noggings 38 x 50 @610 between the bottom chords, 6 mm ply
#     under the chords over the rooms and the verandah

for i in range(len(truss_x) - 1):
    xa, xb = truss_x[i] + TR_T, truss_x[i + 1]
    k, yc = 0, Y0 + M / 2
    while yc < Y1 - M / 4:
        box(f"Ceiling_Nog_{i}_{k}", C_CEIL, xa, xb, yc - NOG_W / 2, yc + NOG_W / 2, ZB0, ZB0 + NOG_D)
        k += 1
        yc += M
tile_sheets("Ceiling_Ply_W", C_CEIL, X0 + T, XV, Y0 + T, Y1 - T, ZB0 - CEIL_T, ZB0)
tile_sheets("Ceiling_Ply_E", C_CEIL, XV, X1 - T, YV, Y1 - T, ZB0 - CEIL_T, ZB0)
tile_sheets("Ceiling_Ply_Ver", C_CEIL, XV + T, X1 - T, Y0 + T, YV - T, ZB0 - CEIL_T, ZB0)

# ------------------------------------------------------------------
# 11. ENTRANCE STAIR into the verandah bay opposite the main door

XD = (STAIR_BAY[0] + STAIR_BAY[1]) / 2
Y_LAND0 = -(N_RISE - 1) * RUN - 0.04 - 0.36
box("Landing", C_STAIR, XD - 0.65, XD + 0.65, Y_LAND0, Y_LAND0 + 0.60, -0.10, 0.0)
str_slope = RISER / RUN
z_top0 = Z_BOARD
d_vert = STR_D / math.cos(math.atan(str_slope))
y_foot = -(N_RISE - 1) * RUN - 0.04 - 0.08
y_bot_hits = -(z_top0 - d_vert) / str_slope
STRINGER = [(0.0, z_top0), (0.0, z_top0 - d_vert), (y_bot_hits, 0.0), (y_foot, 0.0), (y_foot, z_top0 + str_slope * y_foot)]
STAIR_W = 0.80
sx = [(XD - STAIR_W / 2 - STR_W, XD - STAIR_W / 2), (XD + STAIR_W / 2, XD + STAIR_W / 2 + STR_W)]
for k, (xa, xb) in enumerate(sx):
    prism_x(f"Stringer_{k}", C_STAIR, xa, xb, STRINGER)
for k in range(1, N_RISE):
    zt = FFL - (N_RISE - k) * RISER
    yf = -(N_RISE - k) * RUN - 0.04
    box(f"Tread_{k}", C_STAIR, sx[0][1], sx[1][0], yf, yf + TREAD_D, zt - TREAD_T, zt)
    for j, xa in enumerate((sx[0][1], sx[1][0] - LEDGER)):
        box(f"Ledger_{k}_{j}", C_STAIR, xa, xa + LEDGER, yf + 0.035, yf + 0.215, zt - TREAD_T - LEDGER, zt - TREAD_T)

print("experiment_04_fable_v03: built", len([o for o in bpy.data.objects if o.type == "MESH"]), "members")
