# ------------------------------------------------------------------
# CRAFT BOT - Experiment 06 (Fable run) - Prouve 6x6 demountable house
# ------------------------------------------------------------------
# Timber-frame translation of Jean Prouve's "Pavillon 6x6" (1944) after
# the MONTAGE sequence of the input drawing:
#   1. platform 6 x 6 m, central A-frame portico ("portique axial")
#   2./3. two ridge beams pinned to the portico head, each carrying a
#         narrow gable panel at its far end
#   4. eave rails ("rives superieures") between the gable extremities
#   5. roof trays ("bacs de toiture") spanning ridge -> rail, bolted
#   6. ceilings, interchangeable 1 m facade panels, door, windows
#
# Coordinates: X = ridge direction (gable panels at x = 0 and x = 6),
# Y = across (eave walls at y = 0 and y = 6), Z up, ground at z = 0.
# Units: metres.  Axis-aligned members are craftbot.place_element boxes;
# sloped members (portico lattice, roof trays, bevelled rails, sloped
# wall tops) are convex prisms from a 2D profile, clipped by half-planes.

import bpy
import math
import importlib
from mathutils import Vector
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

L = W = 6.0                       # outer wall faces (the "6 x 6")
MOD = 1.0                         # facade module (6 panels per side)
DECK = 0.40                       # platform margin outside the walls (photos: walls stand inside the floor edge)
P0, P1 = -DECK, L + DECK          # platform extents (both axes)

# platform
FOOT = 0.40
Z_FOOT_TOP = 0.05
BEARER_W, BEARER_D = 0.09, 0.20
JOIST_W, JOIST_D = 0.047, 0.145
BOARD_T, BOARD_W = 0.022, 0.12
Z_BEARER1 = Z_FOOT_TOP + BEARER_D            # 0.25
Z_JOIST1 = Z_BEARER1 + JOIST_D               # 0.395
FFL = Z_JOIST1 + BOARD_T                     # 0.417 finished floor level
BEARER_Y = [P0 + 0.05, 1.5, 3.0, 4.5, P1 - 0.05]   # bearer centre lines (along X)
FOOT_X = [P0 + 0.30, 2.0, 4.0, P1 - 0.30]

# walls
POST = 0.10                                  # panel depth = corner post 100 x 100
POST_W = 0.06                                # intermediate posts 60 x 100 (slim dividers as in the photos)
H_EAVE = 2.30                                # post height above FFL = rail underside
CLAD_T, CLAD_H, CLAD_PITCH = 0.022, 0.09, 0.10   # horizontal boards, 10 mm shadow gap
LINING_T = 0.009                             # interior ply
Z_POST1 = FFL + H_EAVE

# eave rails (rives) and ridge beams
RAIL_W, RAIL_D = 0.08, 0.25
RAIL_Y0 = 0.01                               # rail sits on the post, 10 mm in from the outer face
Z_RAIL1 = Z_POST1 + RAIL_D                   # 2.55 above FFL, rail top at its inner edge
RIDGE_W, RIDGE_D = 0.10, 0.40                # lattice ridge girder: 100 x 60 chords, 45 x 100 web
RCHORD = 0.06
RWEB_STEP, RWEB_GAP = 0.35, 0.10
Z_RIDGE0 = FFL + 2.65                        # ridge beam underside
Z_RIDGE1 = Z_RIDGE0 + RIDGE_D                # 3.05 above FFL, top at the beam edges
OVH = 0.80                                   # tray overhang past the eave walls (covers the deck margin)
OVH_G = 1.00                                 # rail / ridge / tray overhang past the gable walls
YM = W / 2

# roof plane (tray underside): through the rail inner top edge and the
# ridge beam edge, mirrored about y = YM
Y_RAIL_IN = RAIL_Y0 + RAIL_W                 # 0.09
SLOPE = (Z_RIDGE1 - Z_RAIL1) / (YM - RIDGE_W / 2 - Y_RAIL_IN)


def z_u(y):
    """Tray underside at y (both slopes)."""
    d = min(y, W - y)
    return Z_RAIL1 + SLOPE * (d - Y_RAIL_IN)


# portico (in the plane y = YM, legs spread along X)
LEG_T = 0.10                                 # lattice leg thickness in Y
CHORD_W = 0.06                               # chord width in the lattice plane
LEG_DEPTH = 0.30                             # chord centre-to-centre
DIAG_W = 0.045
FOOT_DX = 1.10                               # leg foot centre from the portico axis
HEAD_D = 0.15
Z_HEAD0 = Z_RIDGE0 - HEAD_D                  # top of the legs
HEAD_L = 0.80
GUSSET_T, GUSSET_L = 0.018, 1.00
SOLE_L, SOLE_T = 0.60, 0.04                  # sole plates under the leg feet

# roof trays
TRAY_W = 0.60
RIB_W, RIB_D = 0.045, 0.12
DECK_T = 0.018
CAP_T, CAP_W = 0.020, 0.25
FASCIA_T = 0.020
X_ROOF0, X_ROOF1 = -OVH_G, L + OVH_G
Y_EAVE = -OVH

# openings
WIN_W, WIN_H, WIN_SILL = 0.70, 1.30, 0.85
FR = 0.045                                   # window / door frame section
GLASS = 0.006
SHUT_T = 0.022
DOOR_W, DOOR_H, DOOR_T = 0.80, 2.05, 0.040

# collections
C_FOUND = "Foundation"
C_FLOOR = "Structure/Floor_Framing"
C_PORT = "Structure/Portico"
C_RIDGE = "Structure/Ridge_Beams"
C_GABLE = "Structure/Gable_Panels"
C_POSTS = "Structure/Wall_Posts"
C_RAILS = "Structure/Eave_Rails"
C_BOARDS = "Floors/Floor_Boards"
C_CLAD = "Facade/Cladding"
C_LINE = "Facade/Interior_Lining"
C_OPEN = "Facade/Openings"
C_TRAY = "Roof/Tray_Ribs"
C_DECK = "Roof/Tray_Decks"
C_COVER = "Roof/Covering"
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


def strip(p, q, width, ext=0.0):
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x))
    a, b = p - d * ext, q + d * ext
    h = width / 2
    return [tuple(a - n * h), tuple(b - n * h), tuple(b + n * h), tuple(a + n * h)]


def positions(a0, a1, spacing, thick):
    first, last = a0 + thick / 2, a1 - thick / 2
    pos = [first]
    p = first + spacing
    while p < last - spacing / 2:
        pos.append(p)
        p += spacing
    pos.append(last)
    return pos


BELOW_ROOF_S = [((Y_RAIL_IN, Z_RAIL1), (-SLOPE, 1.0))]        # z <= z_u(y), south half  (kept side: below)
BELOW_ROOF_N = [((W - Y_RAIL_IN, Z_RAIL1), (SLOPE, 1.0))]


def below_roof(poly):
    """Clip a (y, z) polygon to the space under the tray underside."""
    poly = clip(poly, (Y_RAIL_IN, Z_RAIL1), (SLOPE, -1.0))
    poly = clip(poly, (W - Y_RAIL_IN, Z_RAIL1), (-SLOPE, -1.0))
    return poly


def split_rows(rows, holes):
    """Split bands at the top/bottom of every hole so pieces beside a hole
    can be generated."""
    out = []
    for za, zb in rows:
        cuts = {za, zb}
        for _, _, ha, hb in holes:
            for h in (ha, hb):
                if za + 1e-6 < h < zb - 1e-6:
                    cuts.add(h)
        c = sorted(cuts)
        out += list(zip(c[:-1], c[1:]))
    return out


def panel_end(prefix, coll, x0, x1, y0, y1, z0, z_top, holes=(), rows=None):
    """Infill between two end-wall posts: horizontal pieces in the plane
    x = const, top clipped by the roof plane (or flat at z_top when
    rows is None and z_top is a number).  holes = [(ya, yb, za, zb)].
    rows: list of (za, zb) bands; default = cladding board rows."""
    if rows is None:
        rows = []
        z = z0
        top = max(z_u(y0), z_u(y1)) if z_top is None else z_top
        while z < top - 1e-6:
            rows.append((z, min(z + CLAD_H, top)))
            z += CLAD_PITCH
    n = 0
    for za, zb in split_rows(rows, holes):
        cols = [y0, y1]
        for ya, yb, ha, hb in holes:
            if ha < zb - 1e-6 and hb > za + 1e-6:
                cols += [max(ya, y0), min(yb, y1)]
        cols = sorted(set(cols))
        for i in range(len(cols) - 1):
            ca, cb = cols[i], cols[i + 1]
            if cb - ca < 1e-6:
                continue
            if any(ya <= ca + 1e-6 and cb <= yb + 1e-6 and ha < zb - 1e-6 and hb > za + 1e-6
                   for ya, yb, ha, hb in holes):
                continue
            poly = [(ca, za), (cb, za), (cb, zb), (ca, zb)]
            if z_top is None:
                poly = below_roof(poly)
            if len(poly) >= 3:
                prism_x(f"{prefix}_{n:02d}", coll, x0, x1, poly)
                n += 1


def panel_side(prefix, coll, along_x0, along_x1, y0, y1, z0, z1, holes=(), rows=None):
    """Infill between two side-wall posts (plane y = const), boxes only."""
    if rows is None:
        rows = []
        z = z0
        while z < z1 - 1e-6:
            rows.append((z, min(z + CLAD_H, z1)))
            z += CLAD_PITCH
    n = 0
    for za, zb in split_rows(rows, holes):
        cols = [along_x0, along_x1]
        for xa, xb, ha, hb in holes:
            if ha < zb - 1e-6 and hb > za + 1e-6:
                cols += [max(xa, along_x0), min(xb, along_x1)]
        cols = sorted(set(cols))
        for i in range(len(cols) - 1):
            ca, cb = cols[i], cols[i + 1]
            if cb - ca < 1e-6:
                continue
            if any(xa <= ca + 1e-6 and cb <= xb + 1e-6 and ha < zb - 1e-6 and hb > za + 1e-6
                   for xa, xb, ha, hb in holes):
                continue
            box(f"{prefix}_{n:02d}", coll, ca, cb, y0, y1, za, zb)
            n += 1


# ------------------------------------------------------------------
# 1. PLATFORM: footings, bearers along X, joists along Y @ 600, rim
#    joists, 22 x 120 floor boards along X

for j, yc in enumerate(BEARER_Y):
    for i, xc in enumerate(FOOT_X):
        box(f"Footing_{i}{j}", C_FOUND, xc - FOOT / 2, xc + FOOT / 2, yc - FOOT / 2, yc + FOOT / 2, -0.30, Z_FOOT_TOP)
    box(f"Bearer_{j}", C_FLOOR, P0, P1, yc - BEARER_W / 2, yc + BEARER_W / 2, Z_FOOT_TOP, Z_BEARER1)
for i, xc in enumerate(positions(P0, P1, 0.60, JOIST_W)):
    box(f"Joist_{i:02d}", C_FLOOR, xc - JOIST_W / 2, xc + JOIST_W / 2, P0 + JOIST_W, P1 - JOIST_W, Z_BEARER1, Z_JOIST1)
box("Rim_Joist_S", C_FLOOR, P0, P1, P0, P0 + JOIST_W, Z_BEARER1, Z_JOIST1)
box("Rim_Joist_N", C_FLOOR, P0, P1, P1 - JOIST_W, P1, Z_BEARER1, Z_JOIST1)
n, y = 0, P0
while y < P1 - 1e-6:
    yy = min(y + BOARD_W, P1)
    box(f"Floor_Board_{n:02d}", C_BOARDS, P0, P1, y, yy, Z_JOIST1, FFL)
    n += 1
    y = yy

# ------------------------------------------------------------------
# 2. PORTICO: two lattice legs (60 x 100 chords 300 apart, 45 x 100
#    diagonals) in the plane y = 3, meeting under a 600 long head block
#    that carries the ridge beams.  Feet stand on the floor boards over
#    the centre bearer.

XC = L / 2
LEG_Y0, LEG_Y1 = YM - LEG_T / 2, YM + LEG_T / 2
for side, tag in ((-1, "W"), (1, "E")):
    foot = Vector((XC + side * FOOT_DX, FFL))
    apex = Vector((XC, Z_HEAD0 + 0.45))                     # centreline extended, cut back by the clips
    d = (apex - foot).normalized()
    nrm = Vector((-d.y, d.x))
    if nrm.x * side < 0:
        nrm = -nrm                                          # nrm points outward (away from the axis)
    clips = [((0, FFL + SOLE_T), (0, 1)), ((0, Z_HEAD0), (0, -1)), ((XC, 0), (side, 0))]
    box(f"Leg_{tag}_Sole", C_PORT, foot.x - SOLE_L / 2, foot.x + SOLE_L / 2, LEG_Y0, LEG_Y1, FFL, FFL + SOLE_T)
    for k, (off, cname) in enumerate(((LEG_DEPTH / 2, "Outer"), (-LEG_DEPTH / 2, "Inner"))):
        poly = strip(foot + nrm * off, apex + nrm * off, CHORD_W, ext=1.0)
        for p, nn in clips:
            poly = clip(poly, p, nn)
        prism_y(f"Leg_{tag}_Chord_{cname}", C_PORT, LEG_Y0, LEG_Y1, poly)
    # diagonals between the chord inner faces, zigzag; consecutive diagonals are bolted 100 mm apart on the chord (their 85 mm oblique footprints must not overlap)
    face_in, face_out = LEG_DEPTH / 2 - CHORD_W / 2, -(LEG_DEPTH / 2 - CHORD_W / 2)
    s, step, k = 0.12, 0.38, 0
    while True:
        a = foot + d * s + nrm * (face_out if k % 2 == 0 else face_in)
        b = foot + d * (s + step) + nrm * (face_in if k % 2 == 0 else face_out)
        if (foot + d * (s + step)).y > Z_HEAD0 + 0.3:
            break
        poly = strip(a, b, DIAG_W, ext=0.1)
        poly = clip(poly, foot + nrm * face_out, nrm)            # keep inside the chords
        poly = clip(poly, foot + nrm * face_in, -nrm)
        for p, nn in clips:
            poly = clip(poly, p, nn)
        if len(poly) >= 3:
            prism_y(f"Leg_{tag}_Diag_{k:02d}", C_PORT, LEG_Y0, LEG_Y1, poly)
        s += step + 0.10
        k += 1
box("Portico_Head", C_PORT, XC - HEAD_L / 2, XC + HEAD_L / 2, LEG_Y0, LEG_Y1, Z_HEAD0, Z_RIDGE0)

# ------------------------------------------------------------------
# 3. RIDGE BEAMS: 100 x 400 solid beams, west and east halves meeting
#    over the portico head, spliced with 18 mm ply gussets both faces;
#    top ridged to the roof plane so the trays bear flat.

RY0, RY1 = YM - RIDGE_W / 2, YM + RIDGE_W / 2
TOP_CHORD = [(RY0, Z_RIDGE1 - RCHORD), (RY1, Z_RIDGE1 - RCHORD), (RY1, Z_RIDGE1), (YM, z_u(YM)), (RY0, Z_RIDGE1)]
ZW0, ZW1 = Z_RIDGE0 + RCHORD, Z_RIDGE1 - RCHORD          # web zone between the chord faces
# Each half: chords full length, a solid web block where the girder passes
# through the gable wall (so the open web does not leave holes in the
# facade), 45 mm end posts, and zigzag diagonals in the two open segments.
for tag, xa, xb, wall in (("W", X_ROOF0, XC, (0.0, POST)), ("E", XC, X_ROOF1, (L - POST, L))):
    box(f"Ridge_{tag}_BottomChord", C_RIDGE, xa, xb, RY0, RY1, Z_RIDGE0, Z_RIDGE0 + RCHORD)
    prism_x(f"Ridge_{tag}_TopChord", C_RIDGE, xa, xb, TOP_CHORD)
    box(f"Ridge_{tag}_WallBlock", C_RIDGE, wall[0], wall[1], RY0, RY1, ZW0, ZW1)
    for seg, (sa, sb) in enumerate(((xa, wall[0]), (wall[1], xb))):
        box(f"Ridge_{tag}_Post_{seg}0", C_RIDGE, sa, sa + DIAG_W, RY0, RY1, ZW0, ZW1)
        box(f"Ridge_{tag}_Post_{seg}1", C_RIDGE, sb - DIAG_W, sb, RY0, RY1, ZW0, ZW1)
        x, k = sa + DIAG_W + RWEB_GAP / 2, 0
        while x + RWEB_STEP < sb - DIAG_W - RWEB_GAP / 2:
            a = Vector((x, ZW0 if k % 2 == 0 else ZW1))
            b = Vector((x + RWEB_STEP, ZW1 if k % 2 == 0 else ZW0))
            poly = strip(a, b, DIAG_W, ext=0.1)
            for p, nn in (((0, ZW0), (0, 1)), ((0, ZW1), (0, -1)), ((sa + DIAG_W, 0), (1, 0)), ((sb - DIAG_W, 0), (-1, 0))):
                poly = clip(poly, p, nn)
            prism_y(f"Ridge_{tag}_Diag_{seg}{k:02d}", C_RIDGE, RY0, RY1, poly)
            x += RWEB_STEP + RWEB_GAP
            k += 1
for k, (ya, yb) in enumerate(((YM - RIDGE_W / 2 - GUSSET_T, YM - RIDGE_W / 2), (YM + RIDGE_W / 2, YM + RIDGE_W / 2 + GUSSET_T))):
    box(f"Ridge_Gusset_{k}", C_RIDGE, XC - GUSSET_L / 2, XC + GUSSET_L / 2, ya, yb, Z_RIDGE0, Z_RIDGE0 + 0.30)

# ------------------------------------------------------------------
# 4. GABLE PANELS at both ends: two 100 x 100 posts 1 m apart under the
#    ridge, head rail under the beam; west panel holds the door, east
#    panel a window.  (Cladding of the panel is part of the end walls.)

GY0, GY1 = YM - 0.5, YM + 0.5                   # post centres
for end, (xa, xb, ha, hb) in enumerate(((0.0, POST, CLAD_T, POST - LINING_T),
                                         (L - POST, L, L - POST + LINING_T, L - CLAD_T))):
    for k, yc in enumerate((GY0, GY1)):
        box(f"Gable_{end}_Post_{k}", C_GABLE, xa, xb, yc - POST / 2, yc + POST / 2, FFL, Z_RIDGE0)
    # head rail between the posts, inside the panel depth (cladding / lining pass over it)
    box(f"Gable_{end}_Head", C_GABLE, ha, hb, GY0 + POST / 2, GY1 - POST / 2, Z_RIDGE0 - POST, Z_RIDGE0)

# ------------------------------------------------------------------
# 5. WALL POSTS and EAVE RAILS: corner posts + posts on the 1 m module;
#    end-wall posts run up to the roof plane (sloped top); eave rails
#    80 x 250 on the side posts, bevelled top, 600 cantilever each end.

SIDE_POSTS = [(0.0, POST)] + [(k * MOD - POST_W / 2, k * MOD + POST_W / 2) for k in range(1, 6)] + [(L - POST, L)]
for j, (ya, yb) in enumerate(((0.0, POST), (W - POST, W))):
    for i, (xa, xb) in enumerate(SIDE_POSTS):
        box(f"Post_Side{j}_{i}", C_POSTS, xa, xb, ya, yb, FFL, Z_POST1)
    y0, y1 = (RAIL_Y0, Y_RAIL_IN) if j == 0 else (W - Y_RAIL_IN, W - RAIL_Y0)
    prism_x(f"Eave_Rail_{j}", C_RAILS, X_ROOF0, X_ROOF1,
            [(y0, Z_POST1), (y1, Z_POST1), (y1, z_u(y1)), (y0, z_u(y0))])

END_POST_Y = [1.0, 2.0, 4.0, 5.0]               # plus the gable posts at 2.5 / 3.5 and the corners
PLATE_D = 0.08                                   # sloped end-wall head plate, inside the panel depth
for end, (xa, xb, pa, pb) in enumerate(((0.0, POST, CLAD_T, POST - LINING_T),
                                         (L - POST, L, L - POST + LINING_T, L - CLAD_T))):
    for i, yc in enumerate(END_POST_Y):
        ya, yb = yc - POST_W / 2, yc + POST_W / 2
        prism_x(f"Post_End{end}_{i}", C_POSTS, xa, xb,
                [(ya, FFL), (yb, FFL), (yb, z_u(yb) - PLATE_D), (ya, z_u(ya) - PLATE_D)])
    # head plates from the eave rail inner face to the ridge beam, both slopes
    for k, (ya, yb) in enumerate(((Y_RAIL_IN, YM - RIDGE_W / 2), (YM + RIDGE_W / 2, W - Y_RAIL_IN))):
        prism_x(f"Head_Plate_End{end}_{k}", C_POSTS, pa, pb,
                [(ya, z_u(ya) - PLATE_D), (yb, z_u(yb) - PLATE_D), (yb, z_u(yb)), (ya, z_u(ya))])

# ------------------------------------------------------------------
# 6. FACADE PANELS: 22 mm horizontal boards (90 mm face, 100 pitch)
#    between the posts, 9 mm ply lining inside; windows with frames,
#    glass and open shutters; door in the west gable panel.

# side walls: module bays between post faces
SIDE_BAYS = [(SIDE_POSTS[i][1], SIDE_POSTS[i + 1][0]) for i in range(6)]
WIN_SIDE = {0: [1, 4], 1: [2, 5]}                 # window bays per side wall

for j, (wall_y0, lining_y0, cy0, cy1) in enumerate(((0.0, POST - LINING_T, 0.0, CLAD_T),
                                                     (W - POST, W - POST, W - CLAD_T, W))):
    for i, (xa, xb) in enumerate(SIDE_BAYS):
        holes = []
        if i in WIN_SIDE[j]:
            xm = (xa + xb) / 2
            wa, wb = xm - WIN_W / 2 - FR, xm + WIN_W / 2 + FR
            zs, zh = FFL + WIN_SILL - FR, FFL + WIN_SILL + WIN_H + FR
            holes = [(wa, wb, zs, zh)]
            fy0, fy1 = (CLAD_T, POST - LINING_T) if j == 0 else (W - POST + LINING_T, W - CLAD_T)
            p = f"Window_S{j}_{i}"
            box(f"{p}_JambL", C_OPEN, wa, wa + FR, fy0, fy1, zs, zh)
            box(f"{p}_JambR", C_OPEN, wb - FR, wb, fy0, fy1, zs, zh)
            box(f"{p}_Sill", C_OPEN, wa + FR, wb - FR, fy0, fy1, zs, zs + FR)
            box(f"{p}_Head", C_OPEN, wa + FR, wb - FR, fy0, fy1, zh - FR, zh)
            gy = (fy0 + fy1) / 2
            box(f"{p}_Glass", C_OPEN, wa + FR, wb - FR, gy - GLASS / 2, gy + GLASS / 2, zs + FR, zh - FR)
            # shutters: two leaves hinged on the jambs, open 90 degrees
            for k, (sx0, sx1) in enumerate(((wa - SHUT_T, wa), (wb, wb + SHUT_T))):
                if j == 0:
                    sy0, sy1 = -0.01 - WIN_W / 2, -0.01
                else:
                    sy0, sy1 = W + 0.01, W + 0.01 + WIN_W / 2
                box(f"{p}_Shutter_{k}", C_OPEN, sx0, sx1, sy0, sy1, zs + FR, zh - FR)
        panel_side(f"Clad_S{j}_{i}", C_CLAD, xa, xb, cy0, cy1, FFL, Z_POST1, holes)
        panel_side(f"Lining_S{j}_{i}", C_LINE, xa, xb, lining_y0, lining_y0 + LINING_T, FFL, Z_POST1, holes,
                   rows=[(FFL, Z_POST1)])

# end walls: bays between the corner, module, and gable posts
END_POSTS = sorted([(0.0, POST), (W - POST, W)] +
                   [(yc - POST_W / 2, yc + POST_W / 2) for yc in END_POST_Y] +
                   [(yc - POST / 2, yc + POST / 2) for yc in (GY0, GY1)])
END_BAYS = [(END_POSTS[i][1], END_POSTS[i + 1][0]) for i in range(len(END_POSTS) - 1)]
RIDGE_HOLE = (YM - RIDGE_W / 2, YM + RIDGE_W / 2, Z_RIDGE0, 99.0)

for end, (cx0, cx1, lx0, lx1, ox0, ox1) in enumerate(((0.0, CLAD_T, POST - LINING_T, POST, CLAD_T, POST - LINING_T),
                                                       (L - CLAD_T, L, L - POST, L - POST + LINING_T, L - POST + LINING_T, L - CLAD_T))):
    for i, (ya, yb) in enumerate(END_BAYS):
        holes = []
        gable_bay = abs((ya + yb) / 2 - YM) < 0.1
        if gable_bay:
            holes.append(RIDGE_HOLE)
            p = f"Gable_{end}"
            if end == 0:                                   # door
                da, db = YM - DOOR_W / 2 - FR, YM + DOOR_W / 2 + FR
                zh = FFL + DOOR_H + FR
                holes.append((da, db, FFL, zh))
                box(f"{p}_Door_JambL", C_OPEN, ox0, ox1, da, da + FR, FFL, zh)
                box(f"{p}_Door_JambR", C_OPEN, ox0, ox1, db - FR, db, FFL, zh)
                box(f"{p}_Door_Head", C_OPEN, ox0, ox1, da + FR, db - FR, zh - FR, zh)
                box(f"{p}_Door_Leaf", C_OPEN, ox1 - DOOR_T, ox1, da + FR, db - FR, FFL + 0.01, zh - FR)
            else:                                          # window
                wa, wb = YM - WIN_W / 2 - FR, YM + WIN_W / 2 + FR
                zs, zh = FFL + WIN_SILL - FR, FFL + WIN_SILL + WIN_H + FR
                holes.append((wa, wb, zs, zh))
                box(f"{p}_Win_JambL", C_OPEN, ox0, ox1, wa, wa + FR, zs, zh)
                box(f"{p}_Win_JambR", C_OPEN, ox0, ox1, wb - FR, wb, zs, zh)
                box(f"{p}_Win_Sill", C_OPEN, ox0, ox1, wa + FR, wb - FR, zs, zs + FR)
                box(f"{p}_Win_Head", C_OPEN, ox0, ox1, wa + FR, wb - FR, zh - FR, zh)
                gx = (ox0 + ox1) / 2
                box(f"{p}_Win_Glass", C_OPEN, gx - GLASS / 2, gx + GLASS / 2, wa + FR, wb - FR, zs + FR, zh - FR)
                for k, (sy0, sy1) in enumerate(((wa - SHUT_T, wa), (wb, wb + SHUT_T))):
                    box(f"{p}_Win_Shutter_{k}", C_OPEN, L + 0.01, L + 0.01 + WIN_W / 2, sy0, sy1, zs + FR, zh - FR)
        panel_end(f"Clad_E{end}_{i}", C_CLAD, cx0, cx1, ya, yb, FFL, None, holes)
        panel_end(f"Lining_E{end}_{i}", C_LINE, lx0, lx1, ya, yb, FFL, None, holes, rows=[(FFL, 9.0)])

# ------------------------------------------------------------------
# 7. ROOF TRAYS: 600 wide trays of two 45 x 120 ribs and an 18 mm deck,
#    ridge to eave, plumb cut at both ends; ridge cap, fascia, barge boards.


def tray_profile(south, y_lo, y_hi, t0, t1):
    """(y, z) parallelogram between plumb lines y_lo..y_hi, from normal-ish
    height t0 to t1 above the tray underside (measured vertically)."""
    ys = (y_lo, y_hi) if south else (W - y_lo, W - y_hi)
    return [(ys[0], z_u(ys[0]) + t0), (ys[1], z_u(ys[1]) + t0), (ys[1], z_u(ys[1]) + t1), (ys[0], z_u(ys[0]) + t1)]


n_trays = int(round((X_ROOF1 - X_ROOF0) / TRAY_W))
for south in (True, False):
    tag = "S" if south else "N"
    for k in range(n_trays):
        xa = X_ROOF0 + k * TRAY_W
        xb = xa + TRAY_W
        prism_x(f"Tray_{tag}_{k:02d}_RibA", C_TRAY, xa, xa + RIB_W, tray_profile(south, Y_EAVE, YM, 0.0, RIB_D))
        prism_x(f"Tray_{tag}_{k:02d}_RibB", C_TRAY, xb - RIB_W, xb, tray_profile(south, Y_EAVE, YM, 0.0, RIB_D))
        prism_x(f"Tray_{tag}_{k:02d}_Deck", C_DECK, xa, xb, tray_profile(south, Y_EAVE, YM, RIB_D, RIB_D + DECK_T))
    prism_x(f"Ridge_Cap_{tag}", C_COVER, X_ROOF0, X_ROOF1,
            tray_profile(south, YM - CAP_W, YM, RIB_D + DECK_T, RIB_D + DECK_T + CAP_T))
    # fascia on the plumb-cut tray ends
    z_top = z_u(Y_EAVE) + RIB_D + DECK_T
    if south:
        box("Fascia_S", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, Y_EAVE - FASCIA_T, Y_EAVE, z_u(Y_EAVE) - 0.02, z_top)
    else:
        box("Fascia_N", C_COVER, X_ROOF0 - FASCIA_T, X_ROOF1 + FASCIA_T, W - Y_EAVE, W - Y_EAVE + FASCIA_T, z_u(Y_EAVE) - 0.02, z_top)
    for end, (xa, xb) in enumerate(((X_ROOF0 - FASCIA_T, X_ROOF0), (X_ROOF1, X_ROOF1 + FASCIA_T))):
        prism_x(f"Barge_{tag}_{end}", C_COVER, xa, xb, tray_profile(south, Y_EAVE, YM, -0.02, RIB_D + DECK_T))

# ------------------------------------------------------------------
# 8. CEILING: 9 mm ply under the tray ribs, between the rail inner face
#    and the ridge beam, in 1 m panels along X inside the end walls

CEIL_X = [POST] + [k * MOD for k in range(1, 6)] + [L - POST]
for south in (True, False):
    tag = "S" if south else "N"
    for i in range(len(CEIL_X) - 1):
        prism_x(f"Ceiling_{tag}_{i}", C_CEIL, CEIL_X[i], CEIL_X[i + 1],
                tray_profile(south, Y_RAIL_IN, YM - RIDGE_W / 2, -LINING_T, 0.0))

# ------------------------------------------------------------------
# 9. ENTRANCE STEP at the west door: two timber block steps

box("Step_0", C_STAIR, P0 - 0.60, P0, YM - 0.6, YM + 0.6, 0.0, FFL / 2)
box("Step_1", C_STAIR, P0 - 0.30, P0, YM - 0.6, YM + 0.6, FFL / 2, FFL)

print("experiment_06_fable_v06: built", len([o for o in bpy.data.objects if o.type == "MESH"]), "members")
