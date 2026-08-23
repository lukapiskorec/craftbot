# ------------------------------------------------------------------
# CRAFT BOT - Experiment 07 (Fable run) - Gehry-style deconstruction - v02
# ------------------------------------------------------------------
# Starting point: the FRIM prefabricated timber house of experiment 04
# (7.32 x 5.49 m platform house, 47x97 stud panels, Fink trusses).
# Following the Gehry Residence (1978) the box is treated as a found
# object: its interior lining and ceiling are stripped (exposed studs
# and trusses), the south and west walls lose their sheathing and get
# large openings, and an L-shaped "wrap" is built around those two
# sides on a lower deck.  The wrap walls and roofs are hyperbolic
# paraboloids (ruled surfaces): every stud / rafter is a straight
# member along a ruling, every cladding board a straight tapered
# board along a ruling.  A tilted glazed cube pierces the south wrap
# roof; the wrap cladding is cut by skew planes into fractured windows.
#
# Coordinates as in experiment 04: X = length of the old house
# (0..7.32), Y = width (0..5.49, old south wall at y = 0), Z up,
# ground z = 0.  The wrap occupies y < 0 (south wing) and x < 0 (west
# wing).  Units: metres.  Every member is a convex prism.

import bpy
import math
import importlib
from mathutils import Vector, Matrix
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS - old house (experiment 04)

L, W = 7.32, 5.49
M = 0.61
P = 0.047
SD = 0.097
PLY_OUT, PLY_IN = 0.009, 0.006
WALL_T = PLY_OUT + SD + PLY_IN
SHEET_W, SHEET_L = 1.22, 2.44

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
POST_X = [0.30, 2.54, 4.78, 7.02]
POST_Y = [0.30, W / 2, W - 0.30]

PANEL_H = 2.745
Z_BASE = FFL
Z_PANEL0 = Z_BASE + P
Z_PANEL1 = Z_PANEL0 + PANEL_H
Z_BINDER1 = Z_PANEL1 + P                         # 3.749 eaves
Z_NOG = Z_PANEL0 + SHEET_L
LINTEL_D = 0.145
WIN_CLEAR, WIN_H, WIN_SILL = 1.079, 1.587, 0.90
GLASS = 0.006

TR_T, TR_D = 0.035, 0.072
TR_SP = 1.22
RISE = 1.195
OVH = 0.52
GABLE_OVH = 0.30
GUSSET = 0.009
GABLE_PLY = 0.006
PURLIN_W, PURLIN_T = 0.072, 0.035
SHEET_T = 0.006
FASCIA_T, FASCIA_D = 0.02, 0.145
BRACE_T, BRACE_W = 0.022, 0.097

ZB0 = Z_BINDER1
ZB1 = ZB0 + TR_D
YM = W / 2
SLOPE = RISE / YM
TH = math.atan(SLOPE)
CT, ST = math.cos(TH), math.sin(TH)
DV = TR_D / CT
Z_RAFTER_TOP0 = ZB1 + DV

# ------------------------------------------------------------------
# PARAMETERS - wrap (new)

Z_DECK = 0.55                 # wrap deck surface (360 below the old floor)
X_WRAP = -2.40                # inner stud face of the west wrap wall (at deck)
Y_WRAP = -2.80                # inner stud face of the south wrap wall (at deck)
LEAN_S, LEAN_W = 0.70, 0.70   # outward lean of the wall tops at their far ends
Z_TOP_C = 2.88                # rail top at the corner post
Z_TOP_S = 3.45                # rail top, south wall east end
Z_TOP_W = 4.20                # rail top, west wall north end (canopy rising to the street)
LIFT = 0.16                   # roof surface above the rail top (rafter 145 + play)
LIFT_C = 0.23                 # ... at the corner (valley rafter 190 + drop + play)
Z_LEDGE = 3.15                # ledger top on the old walls
LEDGE_D = 0.145
RAF_D = 0.145                 # wrap rafters 47 x 145
VAL_W, VAL_D, VAL_DROP = 0.07, 0.19, 0.01
OVH_W = 0.25                  # rafter tail past the rail outer face
BT, BW, GAP = 0.022, 0.145, 0.004      # cladding boards 22 x 145, 4 mm open joints
RAIL_W = 0.075                # rails / plates 47 x 75 (narrower than the studs
                              # because a straight rail cannot follow the twist)
CPOST = 0.12                  # corner post 120 x 120
DECK_X0, DECK_Y0 = -2.55, -2.95
X_LEDGE = PLY_OUT - P         # ledger outer face on the old west wall (-0.038)
Y_LEDGE = PLY_OUT - P

CUBE_H = 0.80                 # half size of the tilted cube (1.60 m cube)
CUBE_C = Vector((4.90, -1.80, 3.35))
CUBE_EULER = (math.radians(35), math.radians(20), math.radians(30))
CUBE_BAR = 0.07
CUBE_CLEAR_BOARD, CUBE_CLEAR_RAFTER = 0.03, 0.05

# collections
C_OH_FOUND = "Old_House/Foundation"
C_OH_FLOOR = "Old_House/Floor_Framing"
C_OH_BOARDS = "Old_House/Floor_Boards"
C_OH_WALL = "Old_House/Wall_Framing"
C_OH_ROOF = "Old_House/Roof_Framing"
C_OH_EXT = "Old_House/Exterior_Sheathing"
C_OH_OPEN = "Old_House/Windows"
C_OH_GABLE = "Old_House/Gable_Sheathing"
C_OH_COVER = "Old_House/Roof_Covering"
C_WR_FOUND = "Wrap/Deck_Foundation"
C_WR_DECK = "Wrap/Deck_Framing"
C_WR_DBOARD = "Wrap/Deck_Boards"
C_WR_WALL = "Wrap/Wrap_Wall_Framing"
C_WR_CLAD = "Wrap/Wall_Cladding"
C_WR_RAF = "Wrap/Wrap_Roof_Framing"
C_WR_RBOARD = "Wrap/Roof_Boards"
C_WR_OPEN = "Wrap/Wrap_Openings"
C_WR_STEP = "Wrap/Steps"
C_CUBE_FRAME = "Cube/Frame"
C_CUBE_GLASS = "Cube/Glass"

RESIDUALS = []   # (name, out-of-plane residual of a ruled quad) for reporting

# ------------------------------------------------------------------
# GENERIC HELPERS


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
    """Keep the part of convex 2D polygon with c + ca*a + cb*b >= 0."""
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


def clip(poly, p, n):
    """2D half-plane clip: keep (q - p) . n >= 0."""
    return clip_lin(poly, -(p[0] * n[0] + p[1] * n[1]), n[0], n[1])


def inset(poly, d):
    """Shrink a convex 2D polygon (CCW) by d on every edge."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    sgn = 1.0 if area > 0 else -1.0
    for i in range(len(poly)):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % len(poly)])
        e = (b - a).normalized()
        nrm = Vector((-e.y, e.x)) * sgn          # inward normal
        poly = clip(poly, tuple(a + nrm * d), tuple(nrm))
        if len(poly) < 3:
            return []
    return poly


class Frame:
    """Plane through o spanned by orthonormal u, v; n = u x v."""

    def __init__(self, o, u, v):
        self.o, self.u, self.v = Vector(o), Vector(u).normalized(), Vector(v).normalized()
        self.n = self.u.cross(self.v).normalized()

    def to2d(self, q):
        d = Vector(q) - self.o
        return (d.dot(self.u), d.dot(self.v))

    def clip(self, poly, p, n):
        """Clip by the 3D half-space (q - p) . n >= 0 restricted to the plane."""
        p, n = Vector(p), Vector(n)
        return clip_lin(poly, (self.o - p).dot(n), self.u.dot(n), self.v.dot(n))

    def point(self, a, b, t=0.0):
        return self.o + self.u * a + self.v * b + self.n * t


def slab_clip(fr, pts, p, n, t0, t1):
    """Clip polygon `pts` (in fr, extruded t0..t1 along fr.n) so that the
    WHOLE slab satisfies (q - p) . n >= 0: the plane is shifted by the
    worst-case thickness term, so thick members never pierce it."""
    p, n = Vector(p), Vector(n)
    dn = fr.n.dot(n)
    return clip_lin(pts, (fr.o - p).dot(n) + min(t0 * dn, t1 * dn), fr.u.dot(n), fr.v.dot(n))


def frame_prism(name, coll, fr, pts, t0, t1, clips=()):
    """Convex prism: polygon `pts` in `fr`, extruded along fr.n from t0 to
    t1, after clipping by 3D half-spaces [(p, n)] (exact for the full
    thickness).  None if clipped away."""
    for p, n in clips:
        pts = slab_clip(fr, pts, p, n, t0, t1)
        if len(pts) < 3:
            return None
    lo = [fr.point(a, b, t0) for a, b in pts]
    hi = [fr.point(a, b, t1) for a, b in pts]
    return mesh_prism(name, coll, lo, hi)


def subtract(fr, pts, holes, t0=0.0, t1=0.0):
    """Convex polygon minus a convex hole given as inside half-spaces
    [(p, n, clearance)]; returns a list of convex pieces, each fully
    outside the hole over the slab thickness t0..t1."""
    pieces, rest = [], pts
    for p, n, cl in holes:
        p = Vector(p) - Vector(n) * cl
        outside = slab_clip(fr, rest, p, -Vector(n), t0, t1)
        if len(outside) >= 3:
            pieces.append(outside)
        rest = fr.clip(rest, p, n)
        if len(rest) < 3:
            break
    return pieces


def prism_x(name, coll, x0, x1, pts_yz):
    return frame_prism(name, coll, Frame((0, 0, 0), (0, 1, 0), (0, 0, 1)), pts_yz, x0, x1)


def strip2(p, q, width, ext=0.4):
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x))
    a, b = p - d * ext, q + d * ext
    h = width / 2
    return [tuple(a - n * h), tuple(b - n * h), tuple(b + n * h), tuple(a + n * h)]


def positions(a0, a1, spacing, thick, grid0=None):
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


def bar(name, coll, p, q, up, width, depth, w_off=0.0, d_off=0.0, out=None, ext=(0.0, 0.0)):
    """Straight member from p to q.  Section: `depth` along e3 (up made
    perpendicular to the axis), `width` along e2 = e3 x e1 (flipped so
    that e2 . out > 0).  Centre shifted by w_off e2 + d_off e3.
    Returns (obj, e1, e2, e3, centre-line point p)."""
    p, q = Vector(p), Vector(q)
    e1 = (q - p).normalized()
    e3 = Vector(up)
    e3 = (e3 - e3.dot(e1) * e1).normalized()
    e2 = e3.cross(e1)
    if out is not None and e2.dot(Vector(out)) < 0:
        e2 = -e2
    c = e2 * w_off + e3 * d_off
    length = (q - p).length
    fr = Frame(p + c, e1, e3)
    pts = [(-ext[0], -depth / 2), (length + ext[1], -depth / 2),
           (length + ext[1], depth / 2), (-ext[0], depth / 2)]
    obj = frame_prism(name, coll, fr, pts, -width / 2, width / 2)
    return obj, e1, e2, e3, p + c


class Ruled:
    """Bilinear (hyperbolic paraboloid) surface between the segments
    A0-A1 (u = 0) and B0-B1 (u = 1); t runs along the segments."""

    def __init__(self, A0, A1, B0, B1, out):
        self.A0, self.A1, self.B0, self.B1 = (Vector(v) for v in (A0, A1, B0, B1))
        self.out = Vector(out)

    def P(self, t, u):
        return (1 - u) * (self.A0 + t * (self.A1 - self.A0)) + u * (self.B0 + t * (self.B1 - self.B0))

    def dt(self, t, u):
        return (1 - u) * (self.A1 - self.A0) + u * (self.B1 - self.B0)

    def du(self, t, u):
        return (self.B0 - self.A0) + t * ((self.B1 - self.B0) - (self.A1 - self.A0))

    def normal(self, t, u):
        n = self.dt(t, u).cross(self.du(t, u)).normalized()
        return n if n.dot(self.out) > 0 else -n


def ruling_member(name, coll, S, t, d0, d1, w0, w1, clips=(), ext=0.5, holes=()):
    """Straight member along the ruling t of S (from u = 0 to u = 1 plus
    `ext` at both ends, to be cut by `clips`).  Section: d0..d1 along the
    local outward normal, w0..w1 along the surface in the +t sense.
    Returns (pieces, frame, e3) where e3 is the +t side direction."""
    p0, p1 = S.P(t, 0), S.P(t, 1)
    e1 = (p1 - p0).normalized()
    n = S.normal(t, 0.5)
    e2 = (n - n.dot(e1) * e1).normalized()
    fr = Frame(p0, e1, e2)
    e3 = fr.n
    if e3.dot(S.dt(t, 0.5)) < 0:
        e3, w0, w1 = -e3, -w1, -w0
        fr = Frame(p0, e1, e2)          # n unchanged, only the range flips
    length = (p1 - p0).length
    pts = [(-ext, d0), (length + ext, d0), (length + ext, d1), (-ext, d1)]
    for p, nn in clips:
        pts = slab_clip(fr, pts, p, nn, w0, w1)
        if len(pts) < 3:
            return [], fr, e3
    polys = subtract(fr, pts, holes, w0, w1) if holes else [pts]
    objs = []
    for k, poly in enumerate(polys):
        nm = name if len(polys) == 1 else f"{name}_{k}"
        o = frame_prism(nm, coll, fr, poly, w0, w1)
        if o:
            objs.append(o)
    return objs, fr, e3


def quad_frame(S, t0, t1, u0, u1):
    """Best-fit frame of the surface patch [t0,t1]x[u0,u1] and its 2D
    outline; records the out-of-plane residual."""
    Q = [S.P(t0, u0), S.P(t1, u0), S.P(t1, u1), S.P(t0, u1)]
    c = sum(Q, Vector()) / 4
    e1 = (Q[1] + Q[2] - Q[0] - Q[3]).normalized()
    e2r = (Q[2] + Q[3] - Q[0] - Q[1])
    n = e1.cross(e2r).normalized()
    if n.dot(S.normal((t0 + t1) / 2, (u0 + u1) / 2)) < 0:
        n = -n
    e2 = n.cross(e1)
    fr = Frame(c, e1, e2)
    pts = [fr.to2d(q) for q in Q]
    RESIDUALS.append(max(abs((q - c).dot(n)) for q in Q))
    return fr, pts


def surface_quad(name, coll, S, t0, t1, u0, u1, n0, n1, clips=(), holes=(), gap=0.0):
    """Plate-like member on the patch [t0,t1]x[u0,u1] of S, from n0 to n1
    along the patch normal, edges inset by `gap`, cut by `clips` and
    with convex `holes` subtracted.  Returns the created objects."""
    fr, pts = quad_frame(S, t0, t1, u0, u1)
    if gap:
        pts = inset(pts, gap)
    for p, nn in clips:
        pts = slab_clip(fr, pts, p, nn, n0, n1)
        if len(pts) < 3:
            return []
    polys = subtract(fr, pts, holes, n0, n1) if holes else [pts]
    objs = []
    for k, poly in enumerate(polys):
        nm = name if len(polys) == 1 else f"{name}_{k}"
        o = frame_prism(nm, coll, fr, poly, n0, n1)
        if o:
            objs.append(o)
    return objs


def vplane(p, d, h_out, offset=0.0):
    """Vertical plane containing direction d through p shifted by `offset`
    along the horizontal h_out; returns (point, inward normal)."""
    dh = Vector((d[0], d[1], 0.0)).normalized()
    h = Vector(h_out)
    h = (h - h.dot(dh) * dh)
    h.z = 0.0
    h.normalize()
    return (Vector(p) + h * offset, -h)


# ------------------------------------------------------------------
# OLD-HOUSE HELPERS (from experiment 04, trimmed)


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


def stud_wall(prefix, coll, along, a0, a1, b0, b1, z0, z1, grid0, openings=()):
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
        rect(f"{prefix}_Op{k}_JackL", aa - P, aa, zs0, zh)
        rect(f"{prefix}_Op{k}_KingL", aa - 2 * P, aa - P, zs0, zt)
        rect(f"{prefix}_Op{k}_JackR", ab, ab + P, zs0, zh)
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
    aa = c_left_stud + P / 2 + P
    return (aa, aa + WIN_CLEAR, FFL + WIN_SILL, FFL + WIN_SILL + WIN_H)


def window_unit(prefix, along, aa, ab, zs, zh, b0, b1):
    def rect(name, p0, p1, zz0, zz1, bb0=b0, bb1=b1):
        if along == "x":
            box(name, C_OH_OPEN, p0, p1, bb0, bb1, zz0, zz1)
        else:
            box(name, C_OH_OPEN, bb0, bb1, p0, p1, zz0, zz1)
    rect(f"{prefix}_JambL", aa, aa + P, zs, zh)
    rect(f"{prefix}_JambR", ab - P, ab, zs, zh)
    rect(f"{prefix}_Head", aa + P, ab - P, zh - P, zh)
    rect(f"{prefix}_Sill", aa + P, ab - P, zs, zs + P)
    gb = (b0 + b1) / 2 - GLASS / 2
    rect(f"{prefix}_Glass", aa + P, ab - P, zs + P, zh - P, gb, gb + GLASS)


# ==================================================================
# PART A - THE OLD HOUSE (experiment 04 box, stripped and opened)
# ==================================================================

# A1 foundation and platform
for i, x in enumerate(POST_X):
    for j, y in enumerate(POST_Y):
        box(f"OH_Footing_{i}{j}", C_OH_FOUND, x - FOOT / 2, x + FOOT / 2, y - FOOT / 2, y + FOOT / 2, -0.30, Z_FOOT_TOP)
        box(f"OH_Post_{i}{j}", C_OH_FOUND, x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, Z_FOOT_TOP, Z_POST_TOP)
for j, y in enumerate(POST_Y):
    for k, side in enumerate((-1, 1)):
        ya = y + side * POST / 2 + (0 if side > 0 else -BEARER_W)
        box(f"OH_Bearer_{j}{'ab'[k]}", C_OH_FLOOR, POST_X[0] - 0.20, POST_X[-1] + 0.20, ya, ya + BEARER_W, Z_POST_TOP, Z_JOIST)
joists = []
for i, xc in enumerate(positions(0.0, L, M, JOIST_W)):
    box(f"OH_Joist_{i:02d}", C_OH_FLOOR, xc - JOIST_W / 2, xc + JOIST_W / 2, HEADER_T, W - HEADER_T, Z_JOIST, Z_BOARD)
    joists.append((xc - JOIST_W / 2, xc + JOIST_W / 2))
for i in range(len(joists) - 1):
    xa, xb = joists[i][1], joists[i + 1][0]
    box(f"OH_Stiffener_S_{i:02d}", C_OH_FLOOR, xa, xb, 0.07, 0.12, Z_BOARD - 0.05, Z_BOARD)
    box(f"OH_Stiffener_N_{i:02d}", C_OH_FLOOR, xa, xb, W - 0.12, W - 0.07, Z_BOARD - 0.05, Z_BOARD)
    box(f"OH_Stiffener_M_{i:02d}", C_OH_FLOOR, xa, xb, W / 2 - 0.025, W / 2 + 0.025, Z_BOARD - 0.075, Z_BOARD)
box("OH_Header_Joist_S", C_OH_FLOOR, 0.0, L, 0.0, HEADER_T, FFL - HEADER_D, FFL)
box("OH_Header_Joist_N", C_OH_FLOOR, 0.0, L, W - HEADER_T, W, FFL - HEADER_D, FFL)
n, y = 0, HEADER_T
while y < W - HEADER_T - 1e-6:
    yy = min(y + BOARD_W, W - HEADER_T)
    box(f"OH_Floor_Board_{n:02d}", C_OH_BOARDS, 0.0, L, y, yy, Z_BOARD, FFL)
    n += 1
    y = yy

# A2 walls.  South and west walls get wide lintel-framed openings into
# the wrap (door type: bottom plate cut).  North/east keep their windows.
Z_OPEN_HEAD = Z_LEDGE - LEDGE_D                      # 3.005: lintel sits behind the wrap ledger
OPEN_S = (4 * M + P / 2 + P, 8 * M - P / 2 - P, None, Z_OPEN_HEAD)     # 4 bays on the south wall
OPEN_W = (WALL_T + 3 * M + P / 2 + P, WALL_T + 6 * M - P / 2 - P, None, Z_OPEN_HEAD)
WIN_N = [window_at(2 * M), window_at(8 * M)]
WIN_E = window_at(WALL_T + 3 * M)

XS0, XS1 = PLY_OUT, L - PLY_OUT
YS0, YS1 = WALL_T, W - WALL_T
stud_wall("OH_Wall_S", C_OH_WALL, "x", XS0, XS1, PLY_OUT, PLY_OUT + SD, Z_PANEL0, Z_PANEL1, 0.0, openings=[OPEN_S])
stud_wall("OH_Wall_N", C_OH_WALL, "x", XS0, XS1, W - PLY_OUT - SD, W - PLY_OUT, Z_PANEL0, Z_PANEL1, 0.0, openings=WIN_N)
stud_wall("OH_Wall_W", C_OH_WALL, "y", YS0, YS1, PLY_OUT, PLY_OUT + SD, Z_PANEL0, Z_PANEL1, WALL_T, openings=[OPEN_W])
stud_wall("OH_Wall_E", C_OH_WALL, "y", YS0, YS1, L - PLY_OUT - SD, L - PLY_OUT, Z_PANEL0, Z_PANEL1, WALL_T, openings=[WIN_E])

box("OH_Base_Plate_S_0", C_OH_WALL, 0.0, OPEN_S[0], 0.0, WALL_T, Z_BASE, Z_PANEL0)
box("OH_Base_Plate_S_1", C_OH_WALL, OPEN_S[1], L, 0.0, WALL_T, Z_BASE, Z_PANEL0)
box("OH_Base_Plate_N", C_OH_WALL, 0.0, L, W - WALL_T, W, Z_BASE, Z_PANEL0)
box("OH_Base_Plate_W_0", C_OH_WALL, 0.0, WALL_T, WALL_T, OPEN_W[0], Z_BASE, Z_PANEL0)
box("OH_Base_Plate_W_1", C_OH_WALL, 0.0, WALL_T, OPEN_W[1], W - WALL_T, Z_BASE, Z_PANEL0)
box("OH_Base_Plate_E", C_OH_WALL, L - WALL_T, L, WALL_T, W - WALL_T, Z_BASE, Z_PANEL0)
box("OH_Head_Binder_S", C_OH_WALL, 0.0, L, 0.0, WALL_T, Z_PANEL1, Z_BINDER1)
box("OH_Head_Binder_N", C_OH_WALL, 0.0, L, W - WALL_T, W, Z_PANEL1, Z_BINDER1)
box("OH_Head_Binder_W", C_OH_WALL, 0.0, WALL_T, WALL_T, W - WALL_T, Z_PANEL1, Z_BINDER1)
box("OH_Head_Binder_E", C_OH_WALL, L - WALL_T, L, WALL_T, W - WALL_T, Z_PANEL1, Z_BINDER1)

# A3 sheathing: only the two free facades keep their 9 mm ply; no lining
clad("OH_Ply_Ext_N", C_OH_EXT, "x", 0.0, L, W - PLY_OUT, W, Z_PANEL0, Z_PANEL1, WIN_N)
clad("OH_Ply_Ext_E", C_OH_EXT, "y", PLY_OUT, W - PLY_OUT, L - PLY_OUT, L, Z_PANEL0, Z_PANEL1, [WIN_E])
for k, wn in enumerate(WIN_N):
    window_unit(f"OH_Window_N{k}", "x", *wn, W - PLY_OUT - SD, W - PLY_OUT)
window_unit("OH_Window_E", "y", *WIN_E, L - PLY_OUT - SD, L - PLY_OUT)

# A4 roof trusses, bracing, purlins, sheets, gables (unchanged from exp 04)
truss_x = [GABLE_PLY] + [k * TR_SP - TR_T / 2 for k in range(1, 6)] + [L - GABLE_PLY - TR_T]


def zu_s(y):
    return ZB1 + SLOPE * y


def zu_n(y):
    return ZB1 + SLOPE * (W - y)


BELOW_S = ((0.0, ZB1), (SLOPE, -1.0))
BELOW_N = ((W, ZB1), (-SLOPE, -1.0))
ABOVE_CHORD = ((0.0, ZB1), (0.0, 1.0))
BELOW_S_TOP = ((0.0, ZB1 + DV), (SLOPE, -1.0))
BELOW_N_TOP = ((W, ZB1 + DV), (-SLOPE, -1.0))
ABOVE_CHORD_BOT = ((0.0, ZB0), (0.0, 1.0))
B1, B2 = (W / 3, ZB1), (2 * W / 3, ZB1)
T1, T2 = (YM / 2, zu_s(YM / 2)), (W - YM / 2, zu_n(W - YM / 2))
APEX = (YM, zu_s(YM))
RAFTER_S = [(-OVH, zu_s(-OVH)), (YM, zu_s(YM)), (YM, zu_s(YM) + DV), (-OVH, zu_s(-OVH) + DV)]
RAFTER_N = [(W + OVH, zu_n(W + OVH)), (YM, zu_n(YM)), (YM, zu_n(YM) + DV), (W + OVH, zu_n(W + OVH) + DV)]
WEBS = [
    ("W1", B1, T1, [((B1[0], 0), (-1, 0))]),
    ("W2", B1, APEX, [((B1[0], 0), (1, 0)), ((YM, 0), (-1, 0))]),
    ("W3", B2, APEX, [((B2[0], 0), (-1, 0)), ((YM, 0), (1, 0))]),
    ("W4", B2, T2, [((B2[0], 0), (1, 0))]),
]
web_polys = {}
for name, a, b, extra in WEBS:
    poly = strip2(a, b, TR_D)
    for p, nrm in [ABOVE_CHORD, BELOW_S, BELOW_N] + extra:
        poly = clip(poly, p, nrm)
    web_polys[name] = poly
GUSSETS = [
    ("Apex", (YM - 0.18, YM + 0.18), (APEX[1] - 0.14, APEX[1] + 0.10)),
    ("HeelS", (0.0, 0.15), (ZB0, ZB0 + 0.10)),
    ("HeelN", (W - 0.15, W), (ZB0, ZB0 + 0.10)),
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
    t = f"OH_Truss_{i}"
    prism_x(f"{t}_BottomChord", C_OH_ROOF, x0, x1, [(0.0, ZB0), (W, ZB0), (W, ZB1), (0.0, ZB1)])
    prism_x(f"{t}_RafterS", C_OH_ROOF, x0, x1, RAFTER_S)
    prism_x(f"{t}_RafterN", C_OH_ROOF, x0, x1, RAFTER_N)
    for name, poly in web_polys.items():
        prism_x(f"{t}_{name}", C_OH_ROOF, x0, x1, poly)
    faces = []
    if i > 0:
        faces.append((x0 - GUSSET, x0))
    if i < len(truss_x) - 1:
        faces.append((x1, x1 + GUSSET))
    for k, (ga, gb) in enumerate(faces):
        for name, poly in gusset_polys.items():
            prism_x(f"{t}_Gusset_{name}_{k}", C_OH_ROOF, ga, gb, poly)

X_IN0 = truss_x[0] + TR_T + GUSSET
X_IN1 = truss_x[-1] - GUSSET
XC = truss_x[3] + TR_T / 2


def roof_frame(south):
    if south:
        return (0.0, 0.0, ZB1), (1, 0, 0), (0, CT, ST)
    return (L, W, ZB1), (-1, 0, 0), (0, -CT, ST)


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
        va, vb = (YM - 0.15) / CT, 0.15 / CT
        pa, pb = ((ua, va), (ub, vb)) if end == 0 else ((ua, vb), (ub, va))
        poly = strip2(pa, pb, BRACE_W)
        poly = clip(poly, (ua, 0), (1, 0))
        poly = clip(poly, (ub, 0), (-1, 0))
        frame_prism(f"OH_Brace_Diag_{tag}{end}", C_OH_ROOF, Frame(o, u, v), poly, -BRACE_T, 0.0)
for k, yc in enumerate((B1[0] - 0.25, B2[0] + 0.25)):
    box(f"OH_Runner_BC_{k}", C_OH_ROOF, X_IN0, X_IN1, yc - BRACE_W / 2, yc + BRACE_W / 2, ZB1, ZB1 + BRACE_T)
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
    prism_x(f"OH_Runner_Web_{name}", C_OH_ROOF, X_IN0, X_IN1, pts)


def roof_pt(south, v, t):
    y = v * CT - t * ST
    z = Z_RAFTER_TOP0 + v * ST + t * CT
    return (y if south else W - y, z)


def v_at(y, t):
    return (y + t * ST) / CT


V_TAIL = v_at(-OVH, 0.0)
PURLIN_V = [V_TAIL + 0.08 + k * 0.67 for k in range(6)]
X_ROOF0, X_ROOF1 = -GABLE_OVH, L + GABLE_OVH
N_SHEETS = 8
SHEET_X = [X_ROOF0 + k * (X_ROOF1 - X_ROOF0) / N_SHEETS for k in range(N_SHEETS + 1)]
Z_SHEET0, Z_SHEET1 = PURLIN_T, PURLIN_T + SHEET_T
Y_EAVE = -OVH - 0.05
for south in (True, False):
    tag = "S" if south else "N"
    for k, vc in enumerate(PURLIN_V):
        pts = [roof_pt(south, vc + a, t) for a, t in
               ((-PURLIN_W / 2, 0), (PURLIN_W / 2, 0), (PURLIN_W / 2, PURLIN_T), (-PURLIN_W / 2, PURLIN_T))]
        prism_x(f"OH_Purlin_{tag}_{k}", C_OH_ROOF, X_ROOF0, X_ROOF1, pts)
    v_split = v_at(Y_EAVE, Z_SHEET0) + SHEET_L
    for k in range(N_SHEETS):
        for j, (y0, y1) in enumerate(((Y_EAVE, None), (None, YM))):
            va0 = v_at(y0, Z_SHEET0) if y0 is not None else v_split
            va1 = v_at(y0, Z_SHEET1) if y0 is not None else v_split
            vb0 = v_at(y1, Z_SHEET0) if y1 is not None else v_split
            vb1 = v_at(y1, Z_SHEET1) if y1 is not None else v_split
            pts = [roof_pt(south, va0, Z_SHEET0), roof_pt(south, vb0, Z_SHEET0),
                   roof_pt(south, vb1, Z_SHEET1), roof_pt(south, va1, Z_SHEET1)]
            prism_x(f"OH_Roof_Sheet_{tag}_{k}{j}", C_OH_COVER, SHEET_X[k], SHEET_X[k + 1], pts)
    t0, t1 = Z_SHEET1, Z_SHEET1 + SHEET_T
    pts = [roof_pt(south, v_at(YM, t0) - 0.25, t0), roof_pt(south, v_at(YM, t0), t0),
           roof_pt(south, v_at(YM, t1), t1), roof_pt(south, v_at(YM, t1) - 0.25, t1)]
    prism_x(f"OH_Ridge_Cap_{tag}", C_OH_COVER, X_ROOF0, X_ROOF1, pts)
    z_top = roof_pt(True, v_at(-OVH - FASCIA_T, Z_SHEET0), Z_SHEET0)[1]
    if south:
        box("OH_Fascia_S", C_OH_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, -OVH - FASCIA_T, -OVH, z_top - FASCIA_D, z_top)
    else:
        box("OH_Fascia_N", C_OH_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, W + OVH, W + OVH + FASCIA_T, z_top - FASCIA_D, z_top)
    for end, (xa, xb) in enumerate(((X_ROOF0 - FASCIA_T, X_ROOF0), (X_ROOF1, X_ROOF1 + FASCIA_T))):
        pts = [roof_pt(south, v_at(-OVH, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0 - FASCIA_D), Z_SHEET0 - FASCIA_D),
               roof_pt(south, v_at(YM, Z_SHEET0), Z_SHEET0),
               roof_pt(south, v_at(-OVH, Z_SHEET0), Z_SHEET0)]
        prism_x(f"OH_Barge_{tag}_{end}", C_OH_COVER, xa, xb, pts)
GABLE_MAIN = [(0.0, ZB0), (W, ZB0), (W, zu_n(W) + DV), (YM, zu_s(YM) + DV), (0.0, zu_s(0.0) + DV)]
GABLE_TAIL_S = [(-OVH, zu_s(-OVH)), (0.0, zu_s(0.0)), (0.0, zu_s(0.0) + DV), (-OVH, zu_s(-OVH) + DV)]
GABLE_TAIL_N = [(W + OVH, zu_n(W + OVH)), (W, zu_n(W)), (W, zu_n(W) + DV), (W + OVH, zu_n(W + OVH) + DV)]
for end, (xa, xb) in enumerate(((0.0, GABLE_PLY), (L - GABLE_PLY, L))):
    prism_x(f"OH_Gable_Ply_{end}_Main", C_OH_GABLE, xa, xb, GABLE_MAIN)
    prism_x(f"OH_Gable_Ply_{end}_TailS", C_OH_GABLE, xa, xb, GABLE_TAIL_S)
    prism_x(f"OH_Gable_Ply_{end}_TailN", C_OH_GABLE, xa, xb, GABLE_TAIL_N)

# ==================================================================
# PART B - THE WRAP
# ==================================================================

# B1 deck: 400 footings, 120 posts, 60x194 bearers, 47x145 joists @610,
# 22x145 boards; two rectangles (south wing, west wing)
Z_DJOIST = Z_DECK - BOARD_T                 # 0.528
Z_DBEAR = Z_DJOIST - JOIST_D                # 0.383
Z_DPOST = Z_DBEAR - BEARER_D                # 0.189
FOOT_W = 0.40


def deck_post(name, x, y):
    box(f"{name}_Footing", C_WR_FOUND, x - FOOT_W / 2, x + FOOT_W / 2, y - FOOT_W / 2, y + FOOT_W / 2, -0.30, Z_FOOT_TOP)
    box(f"{name}_Post", C_WR_FOUND, x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, Z_FOOT_TOP, Z_DPOST)


# south wing: bearers along X at y = -2.70 / -0.45, joists along Y
for k, yc in enumerate((-2.70, -0.45)):
    box(f"WR_Bearer_S{k}", C_WR_DECK, DECK_X0, L, yc - BEARER_W / 2, yc + BEARER_W / 2, Z_DPOST, Z_DBEAR)
    for i, x in enumerate((-2.30, 0.30, 2.54, 4.78, 7.02)):
        deck_post(f"WR_S{k}{i}", x, yc)
for i, xc in enumerate(positions(DECK_X0, L, M, JOIST_W, 0.0)):
    box(f"WR_Joist_S_{i:02d}", C_WR_DECK, xc - JOIST_W / 2, xc + JOIST_W / 2, DECK_Y0, 0.0, Z_DBEAR, Z_DJOIST)
n, y = 0, DECK_Y0
while y < -1e-6:
    yy = min(y + BOARD_W, 0.0)
    box(f"WR_Deck_Board_S_{n:02d}", C_WR_DBOARD, DECK_X0, L, y, yy, Z_DJOIST, Z_DECK)
    n += 1
    y = yy
# west wing: bearers along Y at x = -2.35 / -0.45, joists along X
for k, xc in enumerate((-2.35, -0.45)):
    box(f"WR_Bearer_W{k}", C_WR_DECK, xc - BEARER_W / 2, xc + BEARER_W / 2, 0.0, W, Z_DPOST, Z_DBEAR)
    for i, y in enumerate((0.30, W / 2, W - 0.30)):
        deck_post(f"WR_W{k}{i}", xc, y)
for i, yc in enumerate(positions(0.0, W, M, JOIST_W, 0.0)):
    box(f"WR_Joist_W_{i:02d}", C_WR_DECK, DECK_X0, 0.0, yc - JOIST_W / 2, yc + JOIST_W / 2, Z_DBEAR, Z_DJOIST)
n, x = 0, DECK_X0
while x < -1e-6:
    xx = min(x + BOARD_W, 0.0)
    box(f"WR_Deck_Board_W_{n:02d}", C_WR_DBOARD, x, xx, 0.0, W, Z_DJOIST, Z_DECK)
    n += 1
    x = xx

# B2 ruled surfaces.  Walls: u = 0 at the deck (plate bottom), u = 1 at
# the rail top, stud inner face.  Roofs: u = 0 at the ledger outer face,
# u = 1 at the wall top (rafter top surface); t = 0 is the shared valley.
CORNER = Vector((X_WRAP, Y_WRAP, 0.0))
WALL_S = Ruled((X_WRAP, Y_WRAP, Z_DECK), (L, Y_WRAP, Z_DECK),
               (X_WRAP, Y_WRAP, Z_TOP_C), (L, Y_WRAP - LEAN_S, Z_TOP_S), out=(0, -1, 0))
WALL_W = Ruled((X_WRAP, Y_WRAP, Z_DECK), (X_WRAP, W, Z_DECK),
               (X_WRAP, Y_WRAP, Z_TOP_C), (X_WRAP - LEAN_W, W, Z_TOP_W), out=(-1, 0, 0))
Z_ROOF_LEDGE = Z_LEDGE + LIFT
ROOF_S = Ruled((X_LEDGE, Y_LEDGE, Z_ROOF_LEDGE), (L, Y_LEDGE, Z_ROOF_LEDGE),
               (X_WRAP, Y_WRAP, Z_TOP_C + LIFT_C), (L, Y_WRAP - LEAN_S, Z_TOP_S + LIFT), out=(0, 0, 1))
ROOF_W = Ruled((X_LEDGE, Y_LEDGE, Z_ROOF_LEDGE), (X_LEDGE, W, Z_ROOF_LEDGE),
               (X_WRAP, Y_WRAP, Z_TOP_C + LIFT_C), (X_WRAP - LEAN_W, W, Z_TOP_W + LIFT), out=(0, 0, 1))

# B3 corner post, ledgers
box("WR_Corner_Post", C_WR_WALL, X_WRAP - CPOST, X_WRAP, Y_WRAP - CPOST, Y_WRAP, Z_DECK, Z_TOP_C)
box("WR_Ledger_S", C_WR_RAF, PLY_OUT, L, Y_LEDGE, PLY_OUT, Z_LEDGE - LEDGE_D, Z_LEDGE)
box("WR_Ledger_W", C_WR_RAF, X_LEDGE, PLY_OUT, Y_LEDGE, W, Z_LEDGE - LEDGE_D, Z_LEDGE)


# B4 wrap walls ---------------------------------------------------------
def wrap_wall(tag, S, openings, end_clips):
    """Studs along rulings, plate and rail as straight bars, tapered
    boards along the rulings.  openings = [(i_a, i_b, extra_planes, kind)]
    with stud indices i_a < i_b and kind 'window' or 'door'."""
    A, B = S.A0, S.A1
    length = (B - A).length
    up = ((S.du(0, 0.5) + S.du(1, 0.5)) / 2)
    # plate (u = 0 line is its bottom, flat on the deck) and rail (u = 1
    # line is its top, square to the average stud direction)
    _, e1p, e2p, e3p, cp = bar(f"WR_{tag}_Plate", C_WR_WALL, S.P(0, 0), S.P(1, 0), (0, 0, 1), RAIL_W, P,
                               w_off=SD / 2, d_off=P / 2, out=S.out)
    _, e1r, e2r, e3r, cr = bar(f"WR_{tag}_Rail", C_WR_WALL, S.P(0, 1), S.P(1, 1), up, RAIL_W, P,
                               w_off=SD / 2, d_off=-P / 2, out=S.out)
    plate_top = (cp + e3p * (P / 2), e3p)
    rail_bot = (cr - e3r * (P / 2), -e3r)
    clips = [plate_top, rail_bot]
    deck = (Vector((0, 0, Z_DECK)), Vector((0, 0, 1)))
    # stud parameters: 610 grid from the corner, last stud at the end
    ts = [c / length for c in positions(0.0, length, M, P)]
    ts[0], ts[-1] = 0.0, 1.0
    studs = {}
    for i, t in enumerate(ts):
        w0, w1 = (0.0, P) if i == 0 else ((-P, 0.0) if i == len(ts) - 1 else (-P / 2, P / 2))
        holes = ()
        for (ia, ib, extra, kind) in openings:
            if ia < i < ib:
                holes = [(p, n, 0.0) for p, n in extra]      # stud ends at the opening edge
        objs, fr, e3 = ruling_member(f"WR_{tag}_Stud_{i:02d}", C_WR_WALL, S, t, 0.0, SD, w0, w1,
                                     clips=clips, holes=holes)
        studs[i] = (fr, e3, w0, w1)

    def side_planes(ia, ib):
        """Inside half-spaces at the facing side faces of studs ia and ib."""
        fra, e3a, _, w1a = studs[ia]
        frb, e3b, w0b, _ = studs[ib]
        return [(fra.o + e3a * w1a, e3a), (frb.o + e3b * w0b, -e3b)]

    # boards along the rulings, nb per bay, tapered, 4 mm open joints
    for i in range(len(ts) - 1):
        ta, tb = ts[i], ts[i + 1]
        bay = (S.P(tb, 0) - S.P(ta, 0)).length
        nb = max(1, round(bay / (BW + GAP)))
        holes = ()
        for (ia, ib, extra, kind) in openings:
            if ia <= i < ib:
                holes = [(p, n, 0.0) for p, n in side_planes(ia, ib) + list(extra)]
        for k in range(nb):
            t0 = ta + (tb - ta) * k / nb
            t1 = ta + (tb - ta) * (k + 1) / nb
            surface_quad(f"WR_{tag}_Board_{i:02d}_{k}", C_WR_CLAD, S, t0, t1, 0.0, 1.0,
                         SD + GAP, SD + GAP + BT, gap=GAP / 2, holes=holes, clips=[deck] + end_clips)
    # openings: per-bay header / sill trimmers in the stud layer (between
    # the stud side faces, SD deep beyond the cut plane), glass per bay,
    # door leaf across the opening, 10 mm above the plate
    for k, (ia, ib, extra, kind) in enumerate(openings):
        sides = side_planes(ia, ib)
        for i in range(ia, ib):
            bay_sides = side_planes(i, i + 1)
            for j, (p, n) in enumerate(extra):
                band = [(p, -Vector(n)), (Vector(p) - Vector(n) * SD, n)] + bay_sides
                surface_quad(f"WR_{tag}_Op{k}_Trimmer_{j}_{i}", C_WR_WALL, S, ts[i], ts[i + 1], 0.0, 1.0, 0.0, SD,
                             clips=band)
            if kind == "window":
                surface_quad(f"WR_{tag}_Op{k}_Glass_{i}", C_WR_OPEN, S, ts[i], ts[i + 1], 0.0, 1.0,
                             SD / 2 - GLASS / 2, SD / 2 + GLASS / 2, clips=bay_sides + list(extra))
        if kind == "door":
            leaf_clips = sides + list(extra) + [(plate_top[0] + e3p * 0.01, e3p)]
            surface_quad(f"WR_{tag}_Op{k}_Leaf", C_WR_OPEN, S, ts[ia], ts[ib], 0.0, 1.0,
                         SD - 0.045, SD - 0.005, clips=leaf_clips, gap=0.01)
    return ts, studs, (e1r, e2r, e3r, cr)


# fractured openings (inside half-spaces in world space)
def hplane(x, y, z, nx, ny, nz):
    return (Vector((x, y, z)), Vector((nx, ny, nz)).normalized())


WIN_S_PLANES = [hplane(0.9, 0, 1.35, -0.30, 0, 1.0),       # sill plane, rising to the west
                hplane(0.9, 0, 2.45, 0.20, 0, -1.0)]       # head plane, rising to the east
WIN_W_PLANES = [hplane(0, -0.36, 1.60, 0, -0.45, 1.0),     # wedge window: sill falls northwards
                hplane(0, -0.36, 1.70, 0, 0.50, -1.0)]     # head rises northwards
DOOR_W_PLANES = [hplane(0, 0, Z_DECK + 2.10, 0, 0, -1.0)]  # head 2.10 above the deck
POST_FACE_S = (Vector((X_WRAP, 0, 0)), Vector((1, 0, 0)))     # boards stay east of the corner post
POST_FACE_W = (Vector((0, Y_WRAP, 0)), Vector((0, 1, 0)))     # ... and north of it
TS_S, STUDS_S, RAILBAR_S = wrap_wall("WallS", WALL_S, [(5, 8, WIN_S_PLANES, "window")], [POST_FACE_S])
TS_W, STUDS_W, RAILBAR_W = wrap_wall("WallW", WALL_W, [(4, 6, WIN_W_PLANES, "window"),
                                                    (7, 9, DOOR_W_PLANES, "door")], [POST_FACE_W])

# B5 wrap roofs ---------------------------------------------------------
# cube as inside half-spaces
CUBE_R = Matrix.Rotation(CUBE_EULER[2], 3, "Z") @ Matrix.Rotation(CUBE_EULER[1], 3, "Y") @ Matrix.Rotation(CUBE_EULER[0], 3, "X")
CUBE_AX = [Vector(CUBE_R.col[k]) for k in range(3)]
CUBE_PLANES = [(CUBE_C + ax * s * CUBE_H, -ax * s) for ax in CUBE_AX for s in (1, -1)]


def wrap_roof(tag, S, rail, other_corner_dir, ledger_plane, eave_h_out, cube=False):
    """Rafters along rulings t > 0 (t = 0 is the shared valley), tapered
    boards along the cross rulings, everything clipped by the ledger face
    and the eave plane (vertical, OVH_W past the rail outer face)."""
    e1r, e2r, e3r, cr = rail
    eave = vplane(cr + e2r * (RAIL_W / 2), e1r, eave_h_out, OVH_W)
    ledge = ledger_plane
    length = (S.A1 - S.A0).length
    ts = [c / length for c in positions(0.0, length, M, P)][1:]
    ts[-1] = 1.0
    for i, t in enumerate(ts, start=1):
        w0, w1 = (-P, 0.0) if t == 1.0 else (-P / 2, P / 2)
        holes = [(p, n, CUBE_CLEAR_RAFTER) for p, n in CUBE_PLANES] if cube else ()
        ruling_member(f"WR_{tag}_Rafter_{i:02d}", C_WR_RAF, S, t, -RAF_D, 0.0, w0, w1,
                      clips=[ledge, eave], holes=holes)
    # valley plane (vertical through the t = 0 ruling), keep this roof's side
    vdir = (S.P(0, 1) - S.P(0, 0)).normalized()
    vn = Vector((0, 0, 1)).cross(vdir).normalized()
    if vn.dot(S.P(0.5, 0.5) - S.P(0, 0.5)) < 0:
        vn = -vn
    valley = (S.P(0, 0), vn)
    span = max((S.P(t, 1) - S.P(t, 0)).length for t in (0.0, 1.0)) * 1.15
    nb = math.ceil(span / (BW + GAP))
    U_END = 1.15
    # board stock spans two rafter bays, joints on rafter centre lines,
    # odd rows start with a one-bay board (a 10 m board could not follow
    # the twist of the surface; short boards keep the out-of-plane error
    # below a millimetre)
    joints = [0.0] + ts
    for k in range(nb):
        u0 = U_END * k / nb
        u1 = U_END * (k + 1) / nb
        holes = [(p, n, CUBE_CLEAR_BOARD) for p, n in CUBE_PLANES] if cube else ()
        cuts = joints[(1 if k % 2 else 2)::2]
        edges = [0.0] + [c for c in cuts if c < 1.0 - 1e-6] + [1.0]
        for j in range(len(edges) - 1):
            surface_quad(f"WR_{tag}_Board_{k:02d}_{j}", C_WR_RBOARD, S, edges[j], edges[j + 1], u0, u1, GAP, GAP + BT,
                         clips=[ledge, eave, valley], gap=GAP / 2, holes=holes)
    return eave


LEDGE_S = (Vector((0, Y_LEDGE, 0)), Vector((0, -1, 0)))
LEDGE_W = (Vector((X_LEDGE, 0, 0)), Vector((-1, 0, 0)))
EAVE_S = wrap_roof("RoofS", ROOF_S, RAILBAR_S, None, LEDGE_S, (0, -1, 0), cube=True)
EAVE_W = wrap_roof("RoofW", ROOF_W, RAILBAR_W, None, LEDGE_W, (-1, 0, 0))

# valley rafter along the shared t = 0 ruling, top dropped 10 mm, from the
# ledger corner to the eave corner
v0, v1 = ROOF_S.P(0, 0), ROOF_S.P(0, 1)
e1 = (v1 - v0).normalized()
e3 = Vector((0, 0, 1))
e3 = (e3 - e3.dot(e1) * e1).normalized()
frv = Frame(v0 + e3 * (-VAL_D / 2 - VAL_DROP), e1, e3)
vlen = (v1 - v0).length
frame_prism("WR_Valley_Rafter", C_WR_RAF, frv,
            [(-0.5, -VAL_D / 2), (vlen + 1.5, -VAL_D / 2), (vlen + 1.5, VAL_D / 2), (-0.5, VAL_D / 2)],
            -VAL_W / 2, VAL_W / 2, clips=[LEDGE_S, LEDGE_W, EAVE_S, EAVE_W])

# B6 end walls (planar, in the planes x = L and y = W) ---------------------


def end_wall(tag, plane_axis, S_wall, S_roof):
    """Planar wall closing a wing end (plane x = L or y = W): vertical
    47x97 studs @610 from the old house outwards, 22x145 vertical boards
    outside, cut by the last wrap rafter / roof boards and by the leaning
    end stud of the wrap wall."""
    p0, p1 = S_roof.P(1, 0), S_roof.P(1, 1)
    e1 = (p1 - p0).normalized()
    nr = S_roof.normal(1, 0.5)
    nr = (nr - nr.dot(e1) * e1).normalized()
    under_rafter = (p0 - nr * RAF_D, -nr)
    below_boards = (p0 + nr * (GAP + BT - 0.002), -nr)
    nw = S_wall.normal(1, 0.5)
    wall_face = (S_wall.P(1, 0.5) + nw * (SD + GAP + BT + GAP), -nw)
    wall_stud_face = (S_wall.P(1, 0.5) - nw * 0.001, -nw)
    if plane_axis == "x":      # plane x = L, wall runs from y = -0.038 towards -Y
        def stud(name, c, clips):
            fr = Frame((L - SD, c, 0), (0, 0, 1), (1, 0, 0))           # n = +y
            return frame_prism(name, C_WR_WALL, fr, [(Z_DECK + P, 0), (Z_DECK + 5, 0), (Z_DECK + 5, SD), (Z_DECK + P, SD)],
                               -P / 2, P / 2, clips)

        def board(name, c0, c1, clips):
            fr = Frame((L + GAP, 0, 0), (0, 0, 1), (0, -1, 0))          # n = +x, b = -y
            return frame_prism(name, C_WR_CLAD, fr, [(Z_DECK, -c0), (Z_DECK, -c1), (Z_DECK + 5, -c1), (Z_DECK + 5, -c0)],
                               0.0, BT, clips)
        box(f"WR_{tag}_Plate", C_WR_WALL, L - SD, L, Y_WRAP - SD / 2 + RAIL_W / 2, Y_LEDGE, Z_DECK, Z_DECK + P)
        first, limit = Y_LEDGE - P / 2, Y_WRAP + 0.20
        board_limit = Y_WRAP - LEAN_S - SD - 0.2
    else:                      # plane y = W, wall runs from x = -0.038 towards -X
        def stud(name, c, clips):
            fr = Frame((c, W - SD, 0), (0, 0, 1), (0, 1, 0))           # n = -x
            return frame_prism(name, C_WR_WALL, fr, [(Z_DECK + P, 0), (Z_DECK + 5, 0), (Z_DECK + 5, SD), (Z_DECK + P, SD)],
                               -P / 2, P / 2, clips)

        def board(name, c0, c1, clips):
            fr = Frame((0, W + GAP, 0), (0, 0, 1), (1, 0, 0))           # n = +y, b = x
            return frame_prism(name, C_WR_CLAD, fr, [(Z_DECK, c0), (Z_DECK, c1), (Z_DECK + 5, c1), (Z_DECK + 5, c0)],
                               0.0, BT, clips)
        box(f"WR_{tag}_Plate", C_WR_WALL, X_WRAP - SD / 2 + RAIL_W / 2, X_LEDGE, W - SD, W, Z_DECK, Z_DECK + P)
        first, limit = X_LEDGE - P / 2, X_WRAP + 0.20
        board_limit = X_WRAP - LEAN_W - SD - 0.2
    cs = [first]
    c = -M
    while c > limit:
        cs.append(c)
        c -= M
    for i, c in enumerate(cs):
        stud(f"WR_{tag}_Stud_{i:02d}", c, [under_rafter, wall_stud_face])
    c0, k = 0.0, 0
    while c0 > board_limit:
        c1 = c0 - (BW + GAP)
        board(f"WR_{tag}_Board_{k:02d}", c0 - GAP / 2, c1 + GAP / 2, [below_boards, wall_face])
        c0 = c1
        k += 1


end_wall("EndE", "x", WALL_S, ROOF_S)
end_wall("EndN", "y", WALL_W, ROOF_W)

# B7 steps: old floor -> deck (inside the south opening) and ground -> deck (at the west door)
xo = (OPEN_S[0] + OPEN_S[1]) / 2
box("WR_Step_In", C_WR_STEP, xo - 0.60, xo + 0.60, -0.30, 0.0, Z_DECK, Z_DECK + 0.18)
yd = (WALL_W.P(TS_W[7], 0).y + WALL_W.P(TS_W[9], 0).y) / 2
x_face = X_WRAP - SD - GAP - BT - 0.01
box("WR_Step_Out_0", C_WR_STEP, x_face - 0.90, x_face, yd - 0.55, yd + 0.45, 0.0, 0.18)
box("WR_Step_Out_1", C_WR_STEP, x_face - 0.60, x_face, yd - 0.55, yd + 0.45, 0.18, 0.36)

# ==================================================================
# PART C - THE TILTED CUBE
# ==================================================================
h, b = CUBE_H, CUBE_BAR


def cube_pt(x, y, z):
    return CUBE_C + CUBE_AX[0] * x + CUBE_AX[1] * y + CUBE_AX[2] * z


# 12 edge bars 70 x 70 inset inside the cube surface.  Bars along axis 0
# run the full length and occupy the corner cells; bars along axes 1 and
# 2 are shortened by one bar width at each end so the three bars at a
# corner butt against each other.
k = 0
for ax in range(3):
    o1, o2 = (ax + 1) % 3, (ax + 2) % 3
    ext = h if ax == 0 else h - b
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            lo = [0.0, 0.0, 0.0]
            lo[ax] = -ext
            lo[o1] = s1 * (h - b / 2)
            lo[o2] = s2 * (h - b / 2)
            fr = Frame(cube_pt(*lo) - CUBE_AX[o1] * (b / 2), CUBE_AX[ax], CUBE_AX[o1])
            frame_prism(f"Cube_Bar_{k:02d}", C_CUBE_FRAME, fr, [(0, 0), (2 * ext, 0), (2 * ext, b), (0, b)], -b / 2, b / 2)
            k += 1
# glass on the faces that look up (normal z > -0.3), inset inside the bars
for ax in range(3):
    for s in (-1, 1):
        nrm = CUBE_AX[ax] * s
        if nrm.z < -0.3:
            continue
        o1, o2 = (ax + 1) % 3, (ax + 2) % 3
        c = CUBE_C + nrm * (h - b / 2)
        fr = Frame(c, CUBE_AX[o1], CUBE_AX[o2])
        e = h - b
        frame_prism(f"Cube_Glass_{ax}{'pn'[s < 0]}", C_CUBE_GLASS, fr,
                    [(-e, -e), (e, -e), (e, e), (-e, e)], -GLASS / 2, GLASS / 2)

corners = [cube_pt(sx * h, sy * h, sz * h) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
print("cube bbox x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
    min(c.x for c in corners), max(c.x for c in corners), min(c.y for c in corners),
    max(c.y for c in corners), min(c.z for c in corners), max(c.z for c in corners)))
print("max out-of-plane residual of ruled quads: %.1f mm" % (max(RESIDUALS) * 1000))
print("experiment_07_fable_v02: built", len([o for o in bpy.data.objects if o.type == "MESH"]), "members")
