# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 (Fable run) - V01
# T-SHAPED HIP ROOF, SITE-FRAMED, WITH GABLE DORMERS
# ------------------------------------------------------------------
# Source: CMHC "Canadian Wood-Frame House Construction", ch. 11-12
# (Figs. 83B hip roof, 85 stub joists, 87 valley, 88 dormer, 90 narrow
# gable projection, 98 closed board sheathing).
#
# Plan: main block 14.4 x 8.4 m (X by Y), south wing 8.4 x 7.2 m of the
# same width so both ridges are at one height and the two valleys run
# at 45 deg from the inside corners to the ridge junction (true T).
# Slope 9:12 (S = 0.75, >= 1:3 so collar ties, no ridge beam needed).
#
# Members (actual dressed sizes, metres):
#   commons / jacks 38 x 235 @ 600 (manual example: 4.7 m span)
#   hips, valleys, ridges 38 x 286 (= commons + 50 mm, Fig. 83B);
#   hips "dropped" 10 mm so the sheathing planes clear their top edges
#   ceiling joists 38 x 184 beside every rafter, lapped at the centre
#   bearing wall; stub joists at the hip ends (Fig. 85)
#   walls 38 x 140 studs @ 600, double top plate, plate top z = 2.7
#   dormers: 38 x 89 walls, 38 x 140 rafters, 38 x 184 ridge / valleys,
#   double 38 x 235 headers flush with the rafters (Fig. 88)
#
# Every rafter has a bird's mouth: heel over the outer wall face, seat
# = plate width. Because the overlap check needs convex solids each
# rafter is two prisms sharing the plumb heel face: body (seat upward)
# and tail (eave overhang 0.5 m, plumb cut).
#
# Coordinates: X east, Y north, Z up, ground z = 0. Axis-aligned
# members use craftbot.place_element boxes; sloped members are convex
# prisms cut by 3D half-spaces (true cheek cuts at hips and valleys).

import bpy
import math
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

S = 0.75                                # roof slope 9:12
TH = math.atan(S)
COS = math.cos(TH)
R2 = math.sqrt(2.0)
T = 0.038                               # member thickness
RAF_D, HIP_D, RIDGE_D = 0.235, 0.286, 0.286
JOIST_D, TIE_D = 0.184, 0.089
STUD_D = 0.140                          # wall thickness (38 x 140 studs)
MAIN_X, MAIN_Y = 7.2, 4.2               # main block: outer wall faces at +-
WING_X, WING_Y = 4.2, -11.4             # wing: outer faces x = +-4.2, south y = -11.4
Z_PL = 2.7                              # top of double top plate
SP = 0.6                                # rafter / joist / stud spacing
OV = 0.5                                # eave overhang (horizontal)
HAP = RAF_D / COS - S * STUD_D          # heel height above plate (seat = plate width)
Z_T0 = Z_PL + HAP                       # rafter top surface at the wall line
Z_R = Z_T0 + S * MAIN_Y                 # ridge surface (both ridges)
HIP_M = S / R2                          # hip / valley slope
HIP_DROP = S * (T / 2) / R2             # drop so the hip top corners meet the planes
BOARD_T = 0.019                         # roof board thickness (v02)
TIE_BELOW_RIDGE = 1.3

# dormer module (local coords: a across, s up-slope horizontal from the wall line)
D_HALF = 0.9                            # doubled rafter centres at a = +-0.9
D_WALL = 0.089
D_OUT = D_HALF + T / 2                  # wall outer face
D_IN = D_OUT - D_WALL                   # wall inner face
D_FRONT = 0.6                           # front wall outer face (s)
D_H = 1.1                               # board top at the front wall to top of top plate
D_RAF_D, D_RIDGE_D, D_VAL_D = 0.140, 0.184, 0.184
D_OV_SIDE, D_OV_FRONT = 0.2, 0.3
D_HAP = D_RAF_D / COS - S * D_WALL
D_TRIM = 0.3                            # trimmed commons at a = +-0.3
D_RO_HALF = 0.4                         # window rough opening half width
D_SILL = 0.25                           # sill top above the front bottom plate

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


def mesh_prism(name, coll, lo, hi):
    """Prism from two congruent polygon rings (lists of Vectors)."""
    k = len(lo)
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


def clip_lin(poly, c, ca, cb):
    """Keep the part of a convex 2D polygon with c + ca*a + cb*b >= 0."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = c + ca * a[0] + cb * a[1]
        db = c + ca * b[0] + cb * b[1]
        if da >= 0:
            out.append(a)
        if (da >= 0) != (db >= 0):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


class Frame:
    """Plane through o spanned by orthonormal u, v; n = u x v."""

    def __init__(self, o, u, v):
        self.o, self.u, self.v = Vector(o), Vector(u).normalized(), Vector(v).normalized()
        self.n = self.u.cross(self.v).normalized()

    def point(self, a, b, t=0.0):
        return self.o + self.u * a + self.v * b + self.n * t


def frame_prism(name, coll, fr, pts, t0, t1, clips=()):
    """Convex prism: polygon `pts` in `fr`, extruded along fr.n from t0 to
    t1, cut by 3D half-spaces [(p, n)]. The polygon is clipped separately
    at t0 and t1 so oblique planes give true bevel (cheek) cuts; if the
    two outlines end up with different vertex counts the cut falls back
    to a square cut across the whole thickness. Returns (obj, outline)."""
    lo = hi = list(pts)
    for p, n in clips:
        ca, cb = fr.u.dot(n), fr.v.dot(n)
        base, dn = (fr.o - p).dot(n), fr.n.dot(n)
        lo = clip_lin(lo, base + t0 * dn, ca, cb)
        hi = clip_lin(hi, base + t1 * dn, ca, cb)
        if len(lo) < 3 or len(hi) < 3:
            return None, []
    if len(lo) != len(hi):
        lo = list(pts)
        for p, n in clips:
            ca, cb = fr.u.dot(n), fr.v.dot(n)
            base, dn = (fr.o - p).dot(n), fr.n.dot(n)
            lo = clip_lin(lo, base + min(t0 * dn, t1 * dn), ca, cb)
            if len(lo) < 3:
                return None, []
        hi = lo
    obj = mesh_prism(name, coll, [fr.point(a, b, t0) for a, b in lo],
                     [fr.point(a, b, t1) for a, b in hi])
    return obj, lo


def member(name, coll, p0, d, m, ztop, depth, width, s0, s1, clips=()):
    """Straight member in the vertical plane through p0 (x, y) along the
    horizontal unit direction d. Top line z = ztop + m*s (s = horizontal
    distance from p0), depth measured perpendicular to the top line,
    width across the plane, plumb ends at s0 and s1 before clipping."""
    d = Vector((d[0], d[1], 0.0)).normalized()
    fr = Frame((p0[0], p0[1], 0.0), d, (0.0, 0.0, 1.0))
    dv = depth * math.sqrt(1.0 + m * m)
    pts = [(s0, ztop + m * s0 - dv), (s1, ztop + m * s1 - dv),
           (s1, ztop + m * s1), (s0, ztop + m * s0)]
    return frame_prism(name, coll, fr, pts, -width / 2, width / 2, clips)


def hs(p, n):
    return (Vector(p), Vector(n).normalized())


def vx(x, sign):
    return hs((x, 0.0, 0.0), (sign, 0.0, 0.0))


def vy(y, sign):
    return hs((0.0, y, 0.0), (0.0, sign, 0.0))


def vz(z, sign):
    return hs((0.0, 0.0, z), (0.0, 0.0, sign))


PLATE_TOP = vz(Z_PL, 1.0)


def cheek(C, d, toward):
    """Vertical side face of a 38 mm member whose centre line passes
    through C along d, on the side of point `toward`."""
    d = Vector((d[0], d[1], 0.0)).normalized()
    lat = Vector((-d.y, d.x, 0.0))
    if (Vector((toward[0], toward[1], 0.0)) - Vector((C[0], C[1], 0.0))).dot(lat) < 0:
        lat = -lat
    return hs(Vector((C[0], C[1], 0.0)) + lat * (T / 2), lat)


class Roof:
    """Roof plane z = z0 + s*(c - out.q); `out` = outward horizontal
    direction of the facet, so the plane rises inward."""

    def __init__(self, name, out, c, z0=Z_T0, s=S):
        self.name = name
        self.out = Vector((out[0], out[1], 0.0)).normalized()
        self.c, self.z0, self.s = c, z0, s
        self.n = Vector((s * self.out.x, s * self.out.y, 1.0)).normalized()
        self.p = Vector((self.out.x * c, self.out.y * c, z0))

    def z(self, x, y):
        return self.z0 + self.s * (self.c - (self.out.x * x + self.out.y * y))

    def below(self, off=0.0):
        return (self.p + self.n * off, -self.n)

    def above(self, off=0.0):
        return (self.p + self.n * off, self.n)


class Facet:
    """One roof facet: wall-line origin O (a = 0), eave direction A,
    inward direction Sd, rafter grid (a values), body clips (ridge face,
    hip / valley cheeks) and the eave plane for the tails."""

    def __init__(self, name, roof, O, A, Sd, grid, clips, coll, run=MAIN_Y):
        self.name, self.roof, self.coll, self.run = name, roof, coll, run
        self.O = Vector((O[0], O[1], 0.0))
        self.A = Vector((A[0], A[1], 0.0)).normalized()
        self.Sd = Vector((Sd[0], Sd[1], 0.0)).normalized()
        self.grid = list(grid)
        self.clips = list(clips)
        self.eave = hs(self.O - self.Sd * OV, self.Sd)
        self.skip = set()

    def pt(self, a, s):
        return self.O + self.A * a + self.Sd * s


def rafter(fac, a, name, extra=(), tail=True, depth=RAF_D):
    """Common / jack rafter of facet `fac` at eave position a. The body
    is cut by the facet clips (ridge, hips, valleys) and seated on the
    plate; a tail is added when the body still reaches the wall line."""
    p0 = fac.pt(a, 0.0)
    clips = fac.clips + list(extra) + [PLATE_TOP]
    obj, poly = member(name, fac.coll, p0, fac.Sd, S, Z_T0, depth, T, 0.0, fac.run + 1.0, clips)
    if obj is not None and tail and min(s for s, _ in poly) < 1e-4:
        member(name + "_tail", fac.coll, p0, fac.Sd, S, Z_T0, depth, T, -OV - 0.3, 0.0, [fac.eave])
    return obj


def hip_member(name, coll, C, d, body_clips, tail_clips, drop=HIP_DROP):
    ztop = Z_T0 - drop
    member(name, coll, C, d, HIP_M, ztop, HIP_D, T, 0.0, 12.0, list(body_clips) + [PLATE_TOP])
    member(name + "_tail", coll, C, d, HIP_M, ztop, HIP_D, T, -OV * R2 - 0.3, 0.0, list(tail_clips))


def wall(tag, coll, x0, x1, y0, y1):
    """Stud wall: bottom plate, studs @ 600 from the start + end stud,
    double top plate. Long axis picked from the extents."""
    along_x = (x1 - x0) > (y1 - y0)
    a0, a1 = (x0, x1) if along_x else (y0, y1)
    box(f"{tag}_BottomPlate", coll, x0, x1, y0, y1, 0.0, T)
    box(f"{tag}_TopPlate_1", coll, x0, x1, y0, y1, Z_PL - 2 * T, Z_PL - T)
    box(f"{tag}_TopPlate_2", coll, x0, x1, y0, y1, Z_PL - T, Z_PL)
    pos = [a0 + T / 2]
    k = 1
    while a0 + k * SP < a1 - T - 0.1:
        pos.append(a0 + k * SP)
        k += 1
    pos.append(a1 - T / 2)
    for i, a in enumerate(pos):
        if along_x:
            box(f"{tag}_Stud_{i:02d}", coll, a - T / 2, a + T / 2, y0, y1, T, Z_PL - 2 * T)
        else:
            box(f"{tag}_Stud_{i:02d}", coll, x0, x1, a - T / 2, a + T / 2, T, Z_PL - 2 * T)


# ------------------------------------------------------------------
# ROOF PLANES

MAIN_N = Roof("N", (0, 1), MAIN_Y)
MAIN_S = Roof("S", (0, -1), MAIN_Y)
MAIN_E = Roof("E", (1, 0), MAIN_X)
MAIN_W = Roof("W", (-1, 0), MAIN_X)
WING_E = Roof("wE", (1, 0), WING_X)
WING_W = Roof("wW", (-1, 0), WING_X)
WING_S = Roof("wS", (0, -1), -WING_Y)

RIDGE_END = MAIN_X - MAIN_Y             # 3.0: main ridge runs x = -3..3
WING_RIDGE_S = WING_Y + WING_X          # -7.2: wing ridge runs y = -7.2..0

# hip / valley centre lines (corner point, horizontal direction)
HIP_NE = ((MAIN_X, MAIN_Y), (-1, -1))
HIP_SE = ((MAIN_X, -MAIN_Y), (-1, 1))
HIP_NW = ((-MAIN_X, MAIN_Y), (1, -1))
HIP_SW = ((-MAIN_X, -MAIN_Y), (1, 1))
HIP_WSE = ((WING_X, WING_Y), (-1, 1))
HIP_WSW = ((-WING_X, WING_Y), (1, 1))
VAL_E = ((WING_X, -MAIN_Y), (-1, 1))
VAL_W = ((-WING_X, -MAIN_Y), (1, 1))

# ------------------------------------------------------------------
# FACETS (rafter grids: 0.6 m; hip-end facets offset by 0.3 so the
# dormer's doubled rafters at +-0.9 land on the grid)

grid_main = [SP * k for k in range(-11, 12)]
grid_off = [0.3 + SP * k for k in range(-7, 7)]                 # -3.9 .. 3.9
grid_wing_side = [-SP * k for k in range(1, 19) if abs(-SP * k - (-MAIN_Y)) > 1e-6]

FAC = {}
FAC["N"] = Facet("N", MAIN_N, (0, MAIN_Y), (1, 0), (0, -1), grid_main,
                 [vy(T / 2, 1), cheek(*HIP_NE, (0, 4)), cheek(*HIP_NW, (0, 4))],
                 "Roof_Framing/RF_Main")
FAC["S"] = Facet("S", MAIN_S, (0, -MAIN_Y), (1, 0), (0, 1),
                 [a for a in grid_main if abs(a) > 1e-6 and abs(abs(a) - WING_X) > 1e-6],
                 [vy(-T / 2, -1), cheek(*HIP_SE, (0, -4)), cheek(*HIP_SW, (0, -4)),
                  cheek(*VAL_E, (3, -1)), cheek(*VAL_W, (-3, -1))],
                 "Roof_Framing/RF_Main")
FAC["E"] = Facet("E", MAIN_E, (MAIN_X, 0), (0, 1), (-1, 0), grid_off,
                 [vx(RIDGE_END + T / 2, 1), cheek(*HIP_NE, (6, 0)), cheek(*HIP_SE, (6, 0))],
                 "Roof_Framing/RF_Main")
FAC["W"] = Facet("W", MAIN_W, (-MAIN_X, 0), (0, -1), (1, 0), grid_off,
                 [vx(-RIDGE_END - T / 2, -1), cheek(*HIP_NW, (-6, 0)), cheek(*HIP_SW, (-6, 0))],
                 "Roof_Framing/RF_Main")
FAC["wE"] = Facet("wE", WING_E, (WING_X, 0), (0, 1), (-1, 0), grid_wing_side,
                  [vx(T / 2, 1), cheek(*HIP_WSE, (3, -9)), cheek(*VAL_E, (3, -6))],
                  "Roof_Framing/RF_Wing", run=WING_X)
FAC["wW"] = Facet("wW", WING_W, (-WING_X, 0), (0, 1), (1, 0), grid_wing_side,
                  [vx(-T / 2, -1), cheek(*HIP_WSW, (-3, -9)), cheek(*VAL_W, (-3, -6))],
                  "Roof_Framing/RF_Wing", run=WING_X)
FAC["wS"] = Facet("wS", WING_S, (0, WING_Y), (-1, 0), (0, 1), grid_off,
                  [vy(WING_RIDGE_S - T / 2, -1), cheek(*HIP_WSE, (0, -10)), cheek(*HIP_WSW, (0, -10))],
                  "Roof_Framing/RF_Wing", run=WING_X)

# dormers: (tag, facet, centre a)
DORMERS = [("DN1", FAC["N"], -2.1), ("DN2", FAC["N"], 2.1),
           ("DE", FAC["E"], 0.0), ("DW", FAC["W"], 0.0), ("DS", FAC["wS"], 0.0)]
for tag, fac, ac in DORMERS:
    fac.skip.update([round(ac - D_TRIM, 4), round(ac + D_TRIM, 4)])

# ------------------------------------------------------------------
# 1. WALLS (context for the roof; no openings modelled)

WALLS = "Walls"
wall("Wall_N", WALLS, -MAIN_X, MAIN_X, MAIN_Y - STUD_D, MAIN_Y)
wall("Wall_SE", WALLS, WING_X, MAIN_X, -MAIN_Y, -MAIN_Y + STUD_D)
wall("Wall_SW", WALLS, -MAIN_X, -WING_X, -MAIN_Y, -MAIN_Y + STUD_D)
wall("Wall_E", WALLS, MAIN_X - STUD_D, MAIN_X, -MAIN_Y + STUD_D, MAIN_Y - STUD_D)
wall("Wall_W", WALLS, -MAIN_X, -MAIN_X + STUD_D, -MAIN_Y + STUD_D, MAIN_Y - STUD_D)
wall("Wall_WingE", WALLS, WING_X - STUD_D, WING_X, WING_Y + STUD_D, -MAIN_Y + STUD_D)
wall("Wall_WingW", WALLS, -WING_X, -WING_X + STUD_D, WING_Y + STUD_D, -MAIN_Y + STUD_D)
wall("Wall_WingS", WALLS, -WING_X, WING_X, WING_Y, WING_Y + STUD_D)
wall("Wall_Centre", WALLS, -MAIN_X + STUD_D, MAIN_X - STUD_D, -STUD_D / 2, STUD_D / 2)
# flush header across the wing opening (3 x 38 x 286), hung between the wing walls
box("Beam_WingOpening", WALLS, -WING_X + STUD_D, WING_X - STUD_D, -MAIN_Y, -MAIN_Y + 3 * T, Z_PL - HIP_D, Z_PL)

# ------------------------------------------------------------------
# 2. CEILING JOISTS (38 x 184, beside each rafter, Fig. 83 / 85)

CEIL = "Ceiling"
LAP = 0.2


def joist(name, p0, d, length, clips):
    member(name, CEIL, p0, d, 0.0, Z_PL + JOIST_D, JOIST_D, T, 0.0, length, clips)


for k, x in enumerate(grid_main):
    # north half: wall to 0.2 past the centre wall (lapped over it)
    joist(f"Joist_N_{k:02d}", (x + T, -LAP), (0, 1), MAIN_Y + LAP, [MAIN_N.below()])
    if abs(x) > WING_X + 1e-6:
        joist(f"Joist_S_{k:02d}", (x - T, -MAIN_Y), (0, 1), MAIN_Y + LAP, [MAIN_S.below()])
    else:
        # inside the wing opening: hung from the flush header
        joist(f"Joist_S_{k:02d}", (x - T, -MAIN_Y + 3 * T), (0, 1), MAIN_Y - 3 * T + LAP, [MAIN_S.below()])
    if abs(x) < WING_X - STUD_D - T:
        joist(f"Joist_Wing_{k:02d}", (x + T, WING_Y), (0, 1), -MAIN_Y - WING_Y, [WING_S.below()])

# stub joists beside the jack rafters of the hip ends (Fig. 85)
X_LAST = grid_main[-1] + T + T / 2          # outer face of the last full joist
for k, y in enumerate(grid_off):
    joist(f"StubJoist_E_{k:02d}", (X_LAST, y + T), (1, 0), MAIN_X - X_LAST, [MAIN_E.below()])
    joist(f"StubJoist_W_{k:02d}", (-X_LAST, y + T), (-1, 0), MAIN_X - X_LAST, [MAIN_W.below()])
for k, y in enumerate(grid_wing_side):
    if y < -MAIN_Y:
        x_last = grid_main[17] + T + T / 2  # joist beside x = 3.6
        joist(f"StubJoist_WingE_{k:02d}", (x_last, y - T), (1, 0), WING_X - x_last, [WING_E.below()])
        joist(f"StubJoist_WingW_{k:02d}", (-x_last, y - T), (-1, 0), WING_X - x_last, [WING_W.below()])

# ------------------------------------------------------------------
# 3. RIDGE BOARDS, HIPS, VALLEYS

RF_MAIN, RF_WING = "Roof_Framing/RF_Main", "Roof_Framing/RF_Wing"
Z_RIDGE_TOP = Z_R - S * T / 2 - 0.001    # just under the rafter top corners
box("Ridge_Main", RF_MAIN, -RIDGE_END - T / 2, RIDGE_END + T / 2, -T / 2, T / 2,
    Z_RIDGE_TOP - RIDGE_D, Z_RIDGE_TOP)
box("Ridge_Wing", RF_WING, -T / 2, T / 2, WING_RIDGE_S - T / 2, -T / 2,
    Z_RIDGE_TOP - RIDGE_D, Z_RIDGE_TOP)

E_N, E_S = vy(MAIN_Y + OV, -1), vy(-MAIN_Y - OV, 1)
E_E, E_W = vx(MAIN_X + OV, -1), vx(-MAIN_X - OV, 1)
E_WE, E_WW, E_WS = vx(WING_X + OV, -1), vx(-WING_X - OV, 1), vy(WING_Y - OV, 1)

hip_member("Hip_NE", RF_MAIN, *HIP_NE, [vx(RIDGE_END + T / 2, 1), vy(0, 1)], [E_N, E_E])
hip_member("Hip_SE", RF_MAIN, *HIP_SE, [vx(RIDGE_END + T / 2, 1), vy(0, -1)], [E_S, E_E])
hip_member("Hip_NW", RF_MAIN, *HIP_NW, [vx(-RIDGE_END - T / 2, -1), vy(0, 1)], [E_N, E_W])
hip_member("Hip_SW", RF_MAIN, *HIP_SW, [vx(-RIDGE_END - T / 2, -1), vy(0, -1)], [E_S, E_W])
hip_member("Hip_WingSE", RF_WING, *HIP_WSE, [vy(WING_RIDGE_S - T / 2, -1), vx(0, 1)], [E_WS, E_WE])
hip_member("Hip_WingSW", RF_WING, *HIP_WSW, [vy(WING_RIDGE_S - T / 2, -1), vx(0, -1)], [E_WS, E_WW])
# valleys sit on the plane intersection (corners fall below both planes)
hip_member("Valley_E", RF_WING, *VAL_E, [vy(-T / 2, -1), vx(T / 2, 1)], [E_S, E_WE], drop=0.001)
hip_member("Valley_W", RF_WING, *VAL_W, [vy(-T / 2, -1), vx(-T / 2, -1)], [E_S, E_WW], drop=0.001)

# ------------------------------------------------------------------
# 4. COMMON, HIP-JACK AND VALLEY-JACK RAFTERS

for fac in FAC.values():
    for i, a in enumerate(fac.grid):
        if round(a, 4) in fac.skip:
            continue
        rafter(fac, a, f"{fac.name}_Rafter_{i:02d}")

# collar ties 38 x 89 (slope >= 1:3), on the pairs not interrupted by
# dormers or valleys: main kings at x = +-3, wing commons
Z_TIE = Z_R - TIE_BELOW_RIDGE
for i, x in enumerate((-RIDGE_END, RIDGE_END)):
    member(f"CollarTie_Main_{i}", RF_MAIN, (x + T, -3.0), (0, 1), 0.0, Z_TIE, TIE_D, T, 0.0, 6.0,
           [MAIN_N.below(), MAIN_S.below()])
for i, y in enumerate([a for a in grid_wing_side if -MAIN_Y - 0.5 > a > WING_RIDGE_S - 1e-6]):
    member(f"CollarTie_Wing_{i}", RF_WING, (-4.0, y - T), (1, 0), 0.0, Z_TIE, TIE_D, T, 0.0, 8.0,
           [WING_E.below(), WING_W.below()])

# ------------------------------------------------------------------
# 5. GABLE DORMERS (Fig. 88): doubled rafters, double headers flush with
# the rafters, valley rafters in hangers, side studs on a bottom plate
# laid on the roof sheathing (sheathing-first method), rake overhang on
# blocking (Fig. 90).


def dormer(tag, fac, ac):
    coll = "Roof_Framing/RF_Dormers"
    roof, A, Sd = fac.roof, fac.A, fac.Sd

    def P(a, s):
        return fac.pt(ac + a, s)

    def Pz(a, s, h=0.0):
        q = P(a, s)
        return Vector((q.x, q.y, roof.z(q.x, q.y) + h / COS))

    # heights
    z_fb = roof.z(*P(0, D_FRONT)[:2]) + BOARD_T / COS       # board top at the front wall line
    z_dpt = z_fb + D_H                                       # top of dormer top plates
    z_dT0 = z_dpt + D_HAP                                    # dormer rafter top at the wall line
    z_dR = z_dT0 + S * D_OUT                                 # dormer ridge surface
    s_apex = (z_dR - Z_T0) / S                               # dormer ridge meets the main plane
    AO = A.dot(fac.O + A * ac)
    DR = {+1: Roof(tag + "_p", A, AO + D_OUT, z0=z_dT0),
          -1: Roof(tag + "_m", -A, -AO + D_OUT, z0=z_dT0)}

    # slope frame for members perpendicular to the rafters
    e_slope = (Sd * COS + Vector((0, 0, 1)) * math.sin(TH)).normalized()
    o_slope = Vector((P(0, 0).x, P(0, 0).y, Z_T0))
    fr_slope = Frame(o_slope, e_slope, roof.n)
    sgn = 1.0 if fr_slope.n.dot(A) > 0 else -1.0

    def slab(name, a0, a1, l0, l1, h0, h1, clips=()):
        t0, t1 = sorted((sgn * a0, sgn * a1))
        return frame_prism(name, coll, fr_slope, [(l0, h0), (l1, h0), (l1, h1), (l0, h1)], t0, t1, clips)

    def rect(name, a0, a1, s0, s1, z0, z1, c=coll):
        p, q = P(a0, s0), P(a1, s1)
        return box(name, c, min(p.x, q.x), max(p.x, q.x), min(p.y, q.y), max(p.y, q.y), z0, z1)

    l_f, l_apex = D_FRONT / COS, s_apex / COS
    a_in = D_HALF - T - T / 2                                # inner face of the inner double
    below_lower = hs(fr_slope.point(l_f - 2 * T, 0.0), -e_slope)
    above_upper = hs(fr_slope.point(l_apex + 2 * T, 0.0), e_slope)
    below_upper = hs(fr_slope.point(l_apex, 0.0), -e_slope)
    apex = P(0, s_apex)

    # doubled rafters (inner member of each pair; the outer one is on the grid)
    for sg in (1, -1):
        rafter(fac, ac + sg * (D_HALF - T), f"{tag}_DoubleRafter_{'p' if sg > 0 else 'm'}")
    # headers (2 x 38 x 235 flush with the rafters)
    for i in range(2):
        slab(f"{tag}_HeaderLow_{i}", -a_in, a_in, l_f - 2 * T + i * T, l_f - T + i * T, -RAF_D, 0.0, fac.clips)
        slab(f"{tag}_HeaderUp_{i}", -a_in, a_in, l_apex + i * T, l_apex + (i + 1) * T, -RAF_D, 0.0, fac.clips)
    # trimmed commons and the main-roof jacks between header and valley
    for sg in (1, -1):
        a = ac + sg * D_TRIM
        nm = f"{tag}_Trim_{'p' if sg > 0 else 'm'}"
        rafter(fac, a, nm + "_up", extra=[above_upper])
        rafter(fac, a, nm + "_low", extra=[below_lower])
        vck = cheek(apex, (sg * A.x - Sd.x, sg * A.y - Sd.y), P(sg * D_TRIM, s_apex - 0.05))
        rafter(fac, a, nm + "_jack", extra=[below_upper, vck], tail=False)
    # valley rafters: apex down to the inner doubled rafter (hangers)
    for sg in (1, -1):
        foot = P(sg * a_in, s_apex - a_in)
        d = (-sg * A + Sd) / R2
        member(f"{tag}_Valley_{'p' if sg > 0 else 'm'}", coll, foot, d, HIP_M,
               roof.z(foot.x, foot.y) - 0.001, D_VAL_D, T, 0.0, 3.0, [below_upper])

    # dormer ridge (38 x 184), end cut on the main sheathing
    s_rake = D_FRONT - D_OV_FRONT
    member(f"{tag}_Ridge", coll, P(0, s_rake), Sd, 0.0, z_dR - S * T / 2 - 0.001, D_RIDGE_D, T,
           0.0, s_apex - s_rake + 0.5, [roof.above(BOARD_T)])

    # dormer rafters 38 x 140: rake pair, front pair over the wall, then @ 600
    s_list = [s_rake + T / 2, D_FRONT + D_WALL / 2]
    k = 2
    while D_FRONT + (k - 1) * SP < s_apex - 0.15:
        s_list.append(D_FRONT + (k - 1) * SP)
        k += 1
    for i, s_i in enumerate(s_list):
        a_v = s_apex - s_i                                   # valley crossing (|a|)
        for sg in (1, -1):
            nm = f"{tag}_Rafter_{i:02d}_{'p' if sg > 0 else 'm'}"
            p0 = P(sg * D_OUT, s_i)
            d = -sg * A
            ridge_face = hs(P(sg * T / 2, s_i), -sg * A)
            vck = cheek(apex, (sg * A.x - Sd.x, sg * A.y - Sd.y), P(0, s_i))
            clips = [ridge_face, vck]
            full = a_v > D_OUT
            if full and i > 0:
                clips.append(vz(z_dpt, 1))
            member(nm, coll, p0, d, S, z_dT0, D_RAF_D, T, 0.0, D_OUT + 0.1, clips)
            if full:
                member(nm + "_tail", coll, p0, d, S, z_dT0, D_RAF_D, T, -D_OV_SIDE, 0.0,
                       [vck, roof.above(BOARD_T)])
        # collar tie on the interior pairs
        if 1 < i and a_v > D_OUT + 0.3:
            member(f"{tag}_CollarTie_{i:02d}", coll, P(-1.0, s_i + T), A, 0.0, z_dR - 0.25, TIE_D, T,
                   0.0, 2.0, [DR[1].below(), DR[-1].below()])
    # blocking between the rake pair and the front pair (Fig. 90)
    for j, a in enumerate((-0.8, -0.4, 0.4, 0.8)):
        member(f"{tag}_RakeBlock_{j}", coll, P(a, s_rake + T), Sd, 0.0, z_dT0 + S * (D_OUT - abs(a)),
               D_RAF_D, T, 0.0, D_FRONT + D_WALL / 2 - T / 2 - (s_rake + T))

    # side walls: bottom plate on the boards, studs, level top plate
    for sg in (1, -1):
        sd = "p" if sg > 0 else "m"
        a0, a1 = sg * D_IN, sg * D_OUT
        slab(f"{tag}_SideBottomPlate_{sd}", a0, a1, (D_FRONT + D_WALL) / COS, 3.5 / COS,
             BOARD_T, BOARD_T + T, [vz(z_dpt - T, -1)])
        member(f"{tag}_SideTopPlate_{sd}", coll, P(sg * (D_IN + D_OUT) / 2, D_FRONT + D_WALL), Sd, 0.0,
               z_dpt, T, D_WALL, 0.0, 3.5, [roof.above(BOARD_T)])
        s_j, j = D_FRONT + D_WALL + T / 2, 0
        while True:
            z_bot = roof.z(*P(0, s_j + T / 2)[:2]) + (BOARD_T + T) / COS
            if z_dpt - T - z_bot < 0.15:
                break
            member(f"{tag}_SideStud_{sd}_{j:02d}", coll, P(sg * (D_IN + D_OUT) / 2, s_j - T / 2), Sd, 0.0,
                   z_dpt - T, 2.0, D_WALL, 0.0, T, [roof.above(BOARD_T + T)])
            j += 1
            s_j = D_FRONT + j * SP
    # front (gable) wall
    slab(f"{tag}_FrontBottomPlate", -D_OUT, D_OUT, l_f, l_f + D_WALL, BOARD_T, BOARD_T + T)
    rect(f"{tag}_FrontTopPlate", -D_OUT, D_OUT, D_FRONT, D_FRONT + D_WALL, z_dpt - T, z_dpt)
    on_plate = [roof.above(BOARD_T + T)]
    z_pb = roof.z(*P(0, D_FRONT + D_WALL / 2)[:2]) + (BOARD_T + T) / COS
    z_sill = z_pb + D_SILL
    z_head = z_dpt - T - 0.140

    def fstud(name, a, z_top, clips=on_plate):
        member(name, coll, P(a - T / 2, D_FRONT), A, 0.0, z_top, 2.0, D_WALL, 0.0, T, clips)

    for sg in (1, -1):
        sd = "p" if sg > 0 else "m"
        fstud(f"{tag}_FrontCorner_{sd}", sg * (D_OUT - T / 2), z_dpt - T)
        fstud(f"{tag}_FrontKing_{sd}", sg * (D_RO_HALF + T + T / 2), z_dpt - T)
        fstud(f"{tag}_FrontJack_{sd}", sg * (D_RO_HALF + T / 2), z_head)
    fstud(f"{tag}_FrontCripple", 0.0, z_sill - T)
    rect(f"{tag}_WindowSill", -D_RO_HALF, D_RO_HALF, D_FRONT, D_FRONT + D_WALL, z_sill - T, z_sill)
    rect(f"{tag}_WindowHeader", -D_RO_HALF - T, D_RO_HALF + T, D_FRONT, D_FRONT + 2 * T, z_head, z_head + 0.140)
    # gable studs above the top plate, cut under the rafters / ridge
    gable_clips = [DR[1].below(-D_RAF_D), DR[-1].below(-D_RAF_D), vz(z_dR - S * T / 2 - 0.001 - D_RIDGE_D, -1)]
    for j, a in enumerate((-0.45, 0.0, 0.45)):
        member(f"{tag}_GableStud_{j}", coll, P(a - T / 2, D_FRONT), A, 0.0, z_dpt + 2.0, 2.0, D_WALL,
               0.0, T, gable_clips)
    return dict(tag=tag, fac=fac, ac=ac, s_apex=s_apex, z_dpt=z_dpt, z_dT0=z_dT0, z_dR=z_dR, DR=DR)


DORMER_GEOM = [dormer(tag, fac, ac) for tag, fac, ac in DORMERS]

print(f"[exp11 v01] Z_T0={Z_T0:.3f} Z_R={Z_R:.3f} HAP={HAP:.3f} dormer apex s={DORMER_GEOM[0]['s_apex']:.3f}")
print(f"[exp11 v01] objects: {len([o for o in bpy.data.objects if o.type == 'MESH'])}")
