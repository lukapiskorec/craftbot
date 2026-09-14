# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 16, Fable run, v04
#
# One square room (3.90 clear) in a boarded slat box, standing inside a
# row of 11 ring trusses whose outer chord ripples along the row. Every
# timber piece is a 30 x 120 framing slat (F) or a 24 x 120 board (B).
# Numbers come from Fable/concept.md (section cited inline); a constant
# marked "derived" is the Builder's and is explained in version_notes.md.
# v02: the outer chord gets a mitred vertex at each outline corner (the v01
# chamfer cut the inner chord's eave corner wherever d < 0.49); webs index
# their half-panel vertex through `mids`; R-24 and R-31 assertions added.
# v03: the corner-node web clip is skipped where the web's far end violates
# it (the apex; v02 cut the 22 apex webs to stubs) and every web is asserted
# to reach both its ends; stud splices per wall kind (gable studs and the
# door cripple B 3.25/7.80, Designer answer 5), no third cut anywhere.
# v04 (phase 2, structural review): chord spacers F 30 x 120 between the
# facing chord slats of adjacent rings, on the outer chord at every third
# outer vertex and on the inner top chords at every node (P2-01), and per
# roof slope X's of flat diagonals under the inner top chords in three-bay
# panels, halving joints at the crossings (P2-02). Sections 7 and 8.
#
# Axes: origin at the plan centre on the raft top, x across the trusses,
# y along the row, z up. Door in the -y wall.
#
# Run headless (renders + overlap check):
#   blender --background --python tools/render_views.py -- <this file> <abs out prefix>
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
for _m in (craftbot, g2, planes):
    importlib.reload(_m)

from mathutils import Vector
from craftbot_lib import box, prism_y
from planes import bar, sloped_member, hs, vx, vy, vz, Frame, frame_prism

# ------------------------------------------------------------------
# PARAMETERS (one block; everything below derives from these)

F = (0.030, 0.120)              # framing slat: thickness x depth (concept 3.2)
B = (0.024, 0.120)              # board (concept 3.2)
F_T, F_D = F
B_T, B_D = B
SLAT_MAX = 4.80                 # longest slat (concept 3.2)
MOD = 0.65                      # the one module: studs, joists, roof trusses, ring trusses (3.3)

RAFT_W, RAFT_T = 7.20, 0.25     # concrete raft, top at z = 0 (3.3.1)

# wall build-up, distances from the plan centre (3.3.3)
LAYERS = dict(bin=(1.950, 1.974), rin=(1.974, 2.004), stud=(2.004, 2.124),
              rout=(2.124, 2.154), bout=(2.154, 2.178))
ROOM_CLEAR = 2 * LAYERS["bin"][0]           # 3.90 (R-01)
WALL_OUT = LAYERS["bout"][1]                # 2.178
STUD_W = 2 * F_T                            # paired slats face to face, 60 wide (3.2)
CHORD_OFF = 1.5 * F_T                       # sandwich chord slat centres at +/-0.045: slats at 0.030..0.060, webs in the 60 gap (3.6)
STUD_POS = (0.0, MOD, -MOD, 2 * MOD, -2 * MOD, 3 * MOD, -3 * MOD)   # module studs (3.3.3)
FLOOR_TOP = F_D + B_T                       # 0.144 (3.3.2)
Z_BOARD_TOP = 9.63                          # top of the wall boards, band above (3.3.3, photo rule 4)
RAIL_K = range(1, 15)                       # rails at 0.65 k, k = 1..14 (3.3.3)
JOINTS = {"A": (3.25, 7.15), "B": (1.95, 5.85)}      # board joint patterns, on rail centres (3.3.3)
# stud splices on rail centres, the A and B slats of a pair at least one module apart (3.2, R-21, Designer answer 5):
# side walls k = 7, 14 / 4, 11; gable studs and the door cripple k = 7, 14 / 5, 12 (two splices per slat, no third cut)
SPLICE = {"side": {"A": (4.55, 9.10), "B": (2.60, 7.15)},
          "end": {"A": (4.55, 9.10), "B": (3.25, 7.80)}}
RAIL_CENTRES = [MOD * k for k in RAIL_K] + [Z_BOARD_TOP - F_D / 2]
for _sets in SPLICE.values():
    assert all(any(abs(c - r) < 1e-9 for r in RAIL_CENTRES) for c in _sets["A"] + _sets["B"]), _sets   # on a rail centre
    assert min(abs(a - b) for a in _sets["A"] for b in _sets["B"]) >= MOD - 1e-9, _sets              # staggered by a module

# door (3.3.8)
DOOR_W, DOOR_H = 1.00, 2.10
DOOR_HEAD = FLOOR_TOP + DOOR_H              # 2.244
HEADER = (DOOR_HEAD, DOOR_HEAD + F_D)       # four F on edge, 120 x 120
JACK_N = 4                                  # doubled jacks: 4 slats = 120 each side
LEDGE_Z = (0.25, 1.05, 1.85)                # ledges above the sill (3.3.8)

# box roof (3.3.6)
PITCH = 1.0 / 6.0
THETA = math.atan(PITCH)
COS, SIN = math.cos(THETA), math.sin(THETA)
QUEEN_X = 1.06
N_DECK = 19                                 # derived: whole boards from the eave to the apex
EAVE_X = N_DECK * F_D * COS                 # derived: 2.249, 0.011 clear of the ring leg face 2.26 (concept 2.28 hits the legs)
DECK_Y = 2.28                               # deck end, one piece per board (3.3.6)
TAIL_X = 2.22                               # derived: top chord tail end, 0.096 past the head plate, 0.01 clear of the brace plane
ROOF_T_Y = (0.0, MOD, -MOD, 2 * MOD, -2 * MOD, 3 * MOD - F_D / 2, -(3 * MOD - F_D / 2))
#   derived: the end trusses at +/-1.89, outer slat face flush with the inner board face (concept +/-1.95 sits inside the end wall)

# ring trusses (3.6)
N_RING = 11
RING_Y0 = -3.25
RING_X = 2.32                               # inner chord centreline, legs
RING_RISE = 0.387                           # 1:6 gable (2.32 / 6)
LEG_FACE = RING_X - F_D / 2                 # 2.26, inner face of the leg inner chord
PANEL_MAX = 0.80
D_MEAN, D_AMP, WAVE = 0.63, 0.30, 8.0
Z_H_OFF = 0.37                              # z_h = z_e - 0.37 (3.4)
LEG_SPLICE = {"A": (6, 12), "B": (4, 10)}   # inner leg chord splices at node indices, staggered by two panels (3.2); (3, 9) put 6 panels plus the corner mitre in one slat

# y-bracing (3.5)
BR_X = (2.230, 2.260)                       # derived: flat against the leg inner face 2.26 (concept 2.198..2.228 leaves 32 mm)
BR_Z0 = 0.15
TIE_LO = (5.95, 5.95 + F_D)
LAP_MARGIN = 0.04


# ------------------------------------------------------------------
# DERIVED LEVELS

def tc_under(x):
    """Box roof top chord underside: through the bottom chord's top outer arris at x = 2.124 (3.3.6)."""
    return Z_H + F_D + (LAYERS["stud"][1] - abs(x)) * PITCH


def tc_top(x):
    """Top chord top face = deck underside plane (3.3.6)."""
    return tc_under(x) + F_D / COS


def plate_under(x):
    """Gable head plate underside (F flat, 30 under the deck)."""
    return tc_top(x) - F_T / COS


# ring outline and depth rule (3.6)

def ring_outline(z_e):
    P = [(-RING_X, 0.0), (-RING_X, z_e), (0.0, z_e + RING_RISE), (RING_X, z_e), (RING_X, 0.0)]
    runs, s = [], 0.0
    for k in range(4):
        (xa, za), (xb, zb) = P[k], P[k + 1]
        L = math.hypot(xb - xa, zb - za)
        d = ((xb - xa) / L, (zb - za) / L)
        runs.append(dict(a=(xa, za), d=d, n=(-d[1], d[0]), L=L, s0=s,
                         npan=math.ceil(L / PANEL_MAX - 1e-9)))
        s += L
    return runs, s


def run_pt(r, t, off=0.0):
    return (r["a"][0] + r["d"][0] * t + r["n"][0] * off, r["a"][1] + r["d"][1] * t + r["n"][1] * off)


def ring_depth(s, i):
    return D_MEAN + D_AMP * math.sin(2 * math.pi * s / WAVE + 2 * math.pi * i / N_RING)


def ring_nodes(z_e, i):
    """inner nodes [(s, (x, z), run)]; outer vertices [(s, (x, z))]: both feet, one half-panel vertex per panel
    and (v02) a mitred vertex at each outline corner on the corner bisector at the offset-polygon position,
    d(s_c, i) from both run lines; mids[j] = index in `outer` of panel j's half-panel vertex (webs land there)."""
    runs, S = ring_outline(z_e)
    inner, outer, mids = [], [(0.0, run_pt(runs[0], 0.0, ring_depth(0.0, i)))], []
    for k, r in enumerate(runs):
        if k > 0:
            n1, n2 = runs[k - 1]["n"], r["n"]
            f = ring_depth(r["s0"], i) / (1 + n1[0] * n2[0] + n1[1] * n2[1])
            outer.append((r["s0"], (r["a"][0] + (n1[0] + n2[0]) * f, r["a"][1] + (n1[1] + n2[1]) * f)))
        step = r["L"] / r["npan"]
        for j in range(r["npan"]):
            s = r["s0"] + j * step
            inner.append((s, run_pt(r, j * step), k))
            sm = s + step / 2
            mids.append(len(outer))
            outer.append((sm, run_pt(r, sm - r["s0"], ring_depth(sm, i))))
    inner.append((S, run_pt(runs[3], runs[3]["L"]), 3))
    outer.append((S, run_pt(runs[3], runs[3]["L"], ring_depth(S, i))))
    assert len(outer) == len(mids) + 2 + 3, (len(outer), len(mids))
    return runs, inner, outer, mids


def outer_faces(outer):
    """Segment directions and outward normals of the outer chord polyline, and its outer-face vertices."""
    Q = [o[1] for o in outer]
    dirs, norms = [], []
    for m in range(len(Q) - 1):
        dx, dz = Q[m + 1][0] - Q[m][0], Q[m + 1][1] - Q[m][1]
        L = math.hypot(dx, dz)
        dirs.append((dx / L, dz / L))
        norms.append((-dz / L, dx / L))
    face = []
    for m in range(len(Q)):
        n1, n2 = norms[max(m - 1, 0)], norms[min(m, len(norms) - 1)]
        f = (F_D / 2) / (1 + n1[0] * n2[0] + n1[1] * n2[1])
        face.append((Q[m][0] + (n1[0] + n2[0]) * f, Q[m][1] + (n1[1] + n2[1]) * f))
    return dirs, norms, face


def outer_size(z_e):
    """(W_out, H_out) over outer slat faces of all 11 trusses (3.6 size rule)."""
    H, X = 0.0, 0.0
    for i in range(N_RING):
        _, _, outer, _ = ring_nodes(z_e, i)
        _, _, face = outer_faces(outer)
        H = max(H, max(z for _, z in face))
        X = max(X, max(abs(x) for x, _ in face))
    return max(2 * X, 2 * (abs(RING_Y0) + F_D / 2)), H


# 2:1 rule (brief; 3.6): tune z_e only, z_h follows
_lo, _hi = 11.0, 12.8
for _ in range(60):
    _mid = (_lo + _hi) / 2
    _W, _H = outer_size(_mid)
    if _H - 2.0 * _W > 0:
        _hi = _mid
    else:
        _lo = _mid
Z_E = (_lo + _hi) / 2
Z_H = Z_E - Z_H_OFF
TIE_HI_TOP = tc_top(EAVE_X) - 0.01          # derived: 10 mm under the deck underside at the eave (concept 11.87 cuts the deck)
TIE_HI = (TIE_HI_TOP - F_D, TIE_HI_TOP)
BR_PANELS = ((BR_Z0, TIE_LO[0]), (TIE_LO[1], TIE_HI[0]))   # two panels per half row (3.5)

# ------------------------------------------------------------------
# SECTION-CHECKED CONSTRUCTORS (R-06: every timber piece is F or B)

PIECES = []


def check_section(sec, t, d, name, lap=False):
    want_t = sec[0] / 2 if lap else sec[0]
    assert abs(t - want_t) < 1e-6, (name, "thickness", t, sec)
    assert d <= sec[1] + 1e-6 and d > 0.02, (name, "depth", d, sec)
    PIECES.append(name)


def slat_box(name, coll, sec, x0, x1, y0, y1, z0, z1):
    dims = sorted((x1 - x0, y1 - y0, z1 - z0))
    check_section(sec, dims[0], dims[1], name)
    assert dims[2] <= SLAT_MAX + 1e-6, (name, "length", dims[2])
    obj = box(name, coll, x0, x1, y0, y1, z0, z1)
    assert obj is not None, name
    return obj


def slat_bar(name, coll, sec, p, q, up, w_off=0.0, out=None, ext=(0.0, 0.0), clips=(), lap=False):
    width = sec[0] / 2 if lap else sec[0]
    check_section(sec, width, sec[1], name, lap)
    obj = bar(name, coll, p, q, up, width, sec[1], w_off=w_off, out=out, ext=ext, clips=clips)[0]
    assert obj is not None, name
    return obj


def slat_sloped(name, coll, sec, p0, d, m, ztop, depth, width, s0, s1, clips=()):
    check_section(sec, min(depth, width), max(depth, width), name)
    obj = sloped_member(name, coll, p0, d, m, ztop, depth, width, s0, s1, clips)[0]
    assert obj is not None, name
    return obj


# ------------------------------------------------------------------
# WALL HELPERS. kind 'side': wall normal x, a runs along y; kind 'end': normal y, a runs along x.
# Layer rule (procedural-geometry): side wall layers run to their own outer face in y,
# end wall layers fit between the side walls' same layer.

def layer_zone(sgn, layer):
    r0, r1 = LAYERS[layer]
    return tuple(sorted((sgn * r0, sgn * r1)))


def layer_extent(kind, layer):
    r0, r1 = LAYERS[layer]
    return (-r1, r1) if kind == "side" else (-r0, r0)


def wbox(name, coll, sec, kind, sgn, layer, a0, a1, z0, z1):
    b0, b1 = layer_zone(sgn, layer)
    if kind == "side":
        return slat_box(name, coll, sec, b0, b1, a0, a1, z0, z1)
    return slat_box(name, coll, sec, a0, a1, b0, b1, z0, z1)


def enforce_max(cuts, supports):
    """Split any piece longer than SLAT_MAX at the support nearest its midpoint."""
    cuts = sorted(cuts)
    changed = True
    while changed:
        changed = False
        for m in range(len(cuts) - 1):
            if cuts[m + 1] - cuts[m] > SLAT_MAX:
                mid = (cuts[m] + cuts[m + 1]) / 2
                inside = [c for c in supports if cuts[m] + 0.3 < c < cuts[m + 1] - 0.3]
                assert inside, ("no support to splice", cuts[m], cuts[m + 1])
                cuts.insert(m + 1, min(inside, key=lambda c: abs(c - mid)))
                changed = True
                break
    return cuts


def stud_slat(prefix, coll, kind, sgn, a0, a1, z0, top, splices):
    """One slat of a paired stud, split at its splice heights; `top` is a level z or a z(a) function (gable)."""
    z_top_min = min(top(a0), top(a1)) if callable(top) else top
    cuts = [z0] + [c for c in splices if z0 + 0.3 < c < z_top_min - 0.3] + [z_top_min]
    assert enforce_max(cuts, RAIL_CENTRES) == cuts, (prefix, "a third cut would be needed", cuts)   # R-21: two splices, no more
    for m in range(len(cuts) - 1):
        za, zb = cuts[m], cuts[m + 1]
        if m == len(cuts) - 2 and callable(top):
            b0, b1 = layer_zone(sgn, "stud")
            check_section(F, a1 - a0, b1 - b0, f"{prefix}_{m}")
            prism_y(f"{prefix}_{m}", coll, b0, b1, [(a0, za), (a1, za), (a1, top(a1)), (a0, top(a0))])
        else:
            wbox(f"{prefix}_{m}", coll, F, kind, sgn, "stud", a0, a1, za, zb)


def stud_pair(prefix, coll, kind, sgn, a_c, z0, top):
    for ab, (a0, a1) in (("A", (a_c - F_T, a_c)), ("B", (a_c, a_c + F_T))):
        stud_slat(f"{prefix}{ab}", coll, kind, sgn, a0, a1, z0, top, SPLICE[kind][ab])


def rails(prefix, coll, kind, sgn, layer, door=None):
    a0, a1 = layer_extent(kind, layer)
    zs = [(MOD * k - F_D / 2, MOD * k + F_D / 2) for k in RAIL_K]
    zs.append((FLOOR_TOP, FLOOR_TOP + F_D) if layer == "rin" else (0.0, F_D))   # bottom rail (3.3.3)
    zs.append((Z_BOARD_TOP - F_D, Z_BOARD_TOP))                                 # sill rail
    if kind == "side":
        zs.append((Z_H - F_D, Z_H))                                              # head rail under the level head plate
    for m, (z0, z1) in enumerate(zs):
        ranges = [(a0, a1)]
        if door is not None and z1 > FLOOR_TOP + 1e-6 and z0 < DOOR_HEAD - 1e-6:
            ranges = g2.split_range(a0, a1, [door])
        for q, (ra, rb) in enumerate(ranges):
            wbox(f"{prefix}_{m:02d}_{q}", coll, F, kind, sgn, layer, ra, rb, z0, z1)


RIP_MIN = 0.04                              # a remainder under 40 mm is shared by the last two boards (roof-framing skill)


def board_columns(a0, a1, w):
    n = int(math.floor((a1 - a0) / w + 1e-9))
    rem = (a1 - a0) - n * w
    edges = [a0 + w * k for k in range(n + 1)]
    if rem > 1e-6:
        if rem < RIP_MIN and n >= 1:
            edges[-1] = a0 + w * (n - 1) + (w + rem) / 2
        edges.append(a1)
    return list(zip(edges[:-1], edges[1:]))


def z_pieces(z0, z1, joints):
    cuts = [z0] + [c for c in joints if z0 + 1e-6 < c < z1 - 1e-6] + [z1]
    return list(zip(cuts[:-1], cuts[1:]))


def wall_boards(prefix, coll, kind, sgn, layer, z0, door=None):
    """Vertical boards, joints on rail centres, neighbours on alternate patterns (3.3.3, photo rule 6)."""
    a0, a1 = layer_extent(kind, layer)
    # a wall with a door starts its board columns at the jambs, so the rips land in the corners
    runs = [(a0, a1, z0, False)] if door is None else [
        (a0, door[0], z0, True), (door[0], door[1], DOOR_HEAD, False), (door[1], a1, z0, False)]
    n = 0
    for ra, rb, zb, from_end in runs:
        cols = board_columns(ra, rb, B_D)
        if from_end:
            cols = [(ra + rb - cb, ra + rb - ca) for ca, cb in cols]
        for ca, cb in cols:
            joints = JOINTS["A" if n % 2 == 0 else "B"]
            for m, (za, zc) in enumerate(z_pieces(zb, Z_BOARD_TOP, joints)):
                wbox(f"{prefix}_{n:03d}_{m}", coll, B, kind, sgn, layer, ca, cb, za, zc)
            n += 1


# ------------------------------------------------------------------
# BUILD

craftbot.clear_scene()

# 1. raft (3.3.1), the one non-timber element
box("Raft", "Foundation", -RAFT_W / 2, RAFT_W / 2, -RAFT_W / 2, RAFT_W / 2, -RAFT_T, 0.0)

# 2. floor (3.3.2): paired joists on the module running x, boards across running y
JOIST_X = LAYERS["stud"][0]
JOIST_Y = [-3 * MOD + MOD * k for k in range(7)]
for k, yc in enumerate(JOIST_Y):
    for ab, (y0, y1) in (("A", (yc - F_T, yc)), ("B", (yc, yc + F_T))):
        slat_box(f"Joist_{k}{ab}", "Floor/Joists", F, -JOIST_X, JOIST_X, y0, y1, 0.0, F_D)
for n, (xa, xb) in enumerate(board_columns(-JOIST_X, JOIST_X, B_D)):
    slat_box(f"FloorBoard_{n:03d}", "Floor/FloorBoards", B, xa, xb, -JOIST_X, JOIST_X, F_D, FLOOR_TOP)

# 3. walls (3.3.3 to 3.3.5)
WALLS = (("E", "side", +1), ("W", "side", -1), ("N", "end", +1), ("S", "end", -1))
DOOR_CUT = (-DOOR_W / 2, DOOR_W / 2)
for side, kind, sgn in WALLS:
    door = DOOR_CUT if side == "S" else None
    # bottom plate on the raft (continuous under the door: the threshold step is 0.144 above the raft)
    a0, a1 = layer_extent(kind, "stud")
    wbox(f"Plate{side}", "Walls/Plates", F, kind, sgn, "stud", a0, a1, 0.0, F_T)
    # studs: module positions plus end studs; the end walls drop the +/-1.95 stud (it would collide with the end stud)
    top = Z_H - F_T if kind == "side" else plate_under
    end_c = a1 - STUD_W / 2
    positions = [p for p in STUD_POS if abs(p) < end_c - STUD_W] + [end_c, -end_c]
    for idx, a_c in enumerate(positions):
        if side == "S" and abs(a_c) < 1e-9:
            continue                     # the x = 0 stud becomes the door cripple
        stud_pair(f"Stud{side}{idx}", "Walls/Studs", kind, sgn, a_c, F_T, top)
    # rails both faces
    for layer in ("rin", "rout"):
        rails(f"Rail{side}{layer}", "Walls/Rails", kind, sgn, layer, door)
    # boards both faces: inner from the floor, outer from the raft
    wall_boards(f"Board{side}In", "Walls/BoardsIn", kind, sgn, "bin", FLOOR_TOP, door)
    wall_boards(f"Board{side}Out", "Walls/BoardsOut", kind, sgn, "bout", 0.0, door)
    # wall heads
    if kind == "side":
        wbox(f"HeadPlate{side}", "Walls/Plates", F, kind, sgn, "stud", a0, a1, Z_H - F_T, Z_H)
    else:
        yc = sgn * sum(LAYERS["stud"]) / 2
        for hx, sx in (("E", +1), ("W", -1)):
            # sloped head plate under the deck, over the side wall stud zone to x = +/-2.124
            slat_sloped(f"HeadPlate{side}{hx}", "Walls/Plates", F, (0.0, yc), (sx, 0.0), -PITCH, tc_top(0.0),
                        F_T, F_D, 0.0, LAYERS["stud"][1])
            # sloped head rails on both faces, top on the deck underside
            for layer in ("rin", "rout"):
                r0, r1 = LAYERS[layer]
                slat_sloped(f"HeadRail{side}{layer}{hx}", "Walls/Rails", F, (0.0, sgn * (r0 + r1) / 2), (sx, 0.0),
                            -PITCH, tc_top(0.0), F_D, F_T, 0.0, layer_extent(kind, layer)[1])
            # corner post: four slats from the side wall head plate up to the gable plate
            xs0 = sx * LAYERS["stud"][0]
            for m in range(4):
                xa, xb = sorted((xs0 + sx * F_T * m, xs0 + sx * F_T * (m + 1)))
                b0, b1 = layer_zone(sgn, "stud")
                check_section(F, F_T, F_D, f"CornerPost{side}{hx}_{m}")
                prism_y(f"CornerPost{side}{hx}_{m}", "Walls/Plates", b0, b1,
                        [(xa, Z_H), (xb, Z_H), (xb, plate_under(xb)), (xa, plate_under(xa))])

# door framing in the -y wall (3.3.8): kings are the module studs at +/-0.65, jacks doubled, header of four F, cripple above
JY0, JY1 = layer_zone(-1, "stud")
for jx, sx in (("E", +1), ("W", -1)):
    for m in range(JACK_N):
        xa, xb = sorted((sx * (DOOR_W / 2 + F_T * m), sx * (DOOR_W / 2 + F_T * (m + 1))))
        slat_box(f"Jack{jx}_{m}", "Walls/DoorFrame", F, xa, xb, JY0, JY1, F_T, DOOR_HEAD)
HEADER_X = DOOR_W / 2 + JACK_N * F_T                    # 0.62, on the jacks, between the kings
for m in range(4):
    slat_box(f"Header_{m}", "Walls/DoorFrame", F, -HEADER_X, HEADER_X, JY0 + F_T * m, JY0 + F_T * (m + 1), *HEADER)
stud_pair("CrippleS", "Walls/DoorFrame", "end", -1, 0.0, HEADER[1], plate_under)
assert abs(HEADER_X - (MOD - STUD_W / 2)) < 1e-9, "header must land between the king studs"   # R-19

# door leaf (3.3.8, section 4 external row): hung on the +x jamb, open 90 degrees into the room
LEAF_X1 = DOOR_W / 2
LEAF_Y0 = -LAYERS["rin"][1]                              # hinge stile against the jamb lining
LEAF_Y1 = LEAF_Y0 + DOOR_W
for n, (ya, yb) in enumerate(board_columns(LEAF_Y0, LEAF_Y1, B_D)):
    slat_box(f"DoorBoard_{n:02d}", "Door", B, LEAF_X1 - B_T, LEAF_X1, ya, yb, FLOOR_TOP, DOOR_HEAD)
LEDGE_X = (LEAF_X1 - B_T - F_T, LEAF_X1 - B_T)
ledges = [(FLOOR_TOP + z - F_D / 2, FLOOR_TOP + z + F_D / 2) for z in LEDGE_Z]
for m, (z0, z1) in enumerate(ledges):
    slat_box(f"DoorLedge_{m}", "Door", F, LEDGE_X[0], LEDGE_X[1], LEAF_Y0, LEAF_Y1, z0, z1)
for m in range(2):
    zlo, zhi = ledges[m][1], ledges[m + 1][0]
    xm = sum(LEDGE_X) / 2
    slat_bar(f"DoorBrace_{m}", "Door", F, (xm, LEAF_Y0, zlo), (xm, LEAF_Y1, zhi), (0, 0, 1), out=(1, 0, 0),
             ext=(0.3, 0.3), clips=[vz(zlo, +1), vz(zhi, -1), vy(LEAF_Y0, +1), vy(LEAF_Y1, -1)])

# 4. box roof (3.3.6): 7 shallow sandwich trusses, deck of F slats across them
X_HEEL = LAYERS["stud"][1]
for t, yt in enumerate(ROOF_T_Y):
    for ab, w_off in (("A", -CHORD_OFF), ("B", CHORD_OFF)):
        # slats at yt +/- (0.030 .. 0.060), webs in the 60 gap between them
        slat_box(f"RoofBC_{t}{ab}", "BoxRoof/RoofTrusses", F, -X_HEEL, X_HEEL,
                 yt + w_off - F_T / 2, yt + w_off + F_T / 2, Z_H, Z_H + F_D)
        for hx, sx in (("E", +1), ("W", -1)):
            apex = Vector((0.0, yt, tc_under(0.0) + F_D / 2 / COS))
            heel = Vector((sx * X_HEEL, yt, tc_under(X_HEEL) + F_D / 2 / COS))
            slat_bar(f"RoofTC_{t}{hx}{ab}", "BoxRoof/RoofTrusses", F, apex, heel, (0, 0, 1), w_off=w_off, out=(0, 1, 0),
                     ext=(0.3, 0.3), clips=[vx(0.0, sx), vx(sx * TAIL_X, -sx)])
    gap = (yt - F_T / 2, yt + F_T / 2)
    check_section(F, F_T, F_D, f"RoofKing_{t}")
    prism_y(f"RoofKing_{t}", "BoxRoof/RoofTrusses", *gap,
            [(-F_D / 2, Z_H), (F_D / 2, Z_H), (F_D / 2, tc_top(F_D / 2)), (0.0, tc_top(0.0)), (-F_D / 2, tc_top(F_D / 2))])
    for hx, sx in (("E", +1), ("W", -1)):
        xa, xb = sorted((sx * (QUEEN_X - F_D / 2), sx * (QUEEN_X + F_D / 2)))
        check_section(F, F_T, F_D, f"RoofQueen_{t}{hx}")
        prism_y(f"RoofQueen_{t}{hx}", "BoxRoof/RoofTrusses", *gap,
                [(xa, Z_H), (xb, Z_H), (xb, tc_top(xb)), (xa, tc_top(xa))])
        centre = Vector((0.0, yt, Z_H + F_D / 2))
        target = Vector((sx * QUEEN_X, yt, tc_under(QUEEN_X) + F_D / 2 / COS))
        below_top = hs((0.0, yt, tc_top(0.0)), (-sx * PITCH, 0.0, -1.0))
        slat_bar(f"RoofDiag_{t}{hx}", "BoxRoof/RoofTrusses", F, centre, target, (0, 0, 1), out=(0, 1, 0), ext=(0.3, 0.3),
                 clips=[vz(Z_H, +1), vx(sx * F_D / 2, sx), vx(sx * (QUEEN_X - F_D / 2), -sx), below_top])
# deck, boards running y across the trusses, rows from the eave up the slope, last board plumb-cut at the ridge
for hx, sx in (("E", +1), ("W", -1)):
    fr = Frame((sx * EAVE_X, -DECK_Y, tc_top(EAVE_X)), (-sx * COS, 0.0, SIN), (0.0, 1.0, 0.0))
    t0, t1 = (-F_T, 0.0) if fr.n.z < 0 else (0.0, F_T)
    for k in range(N_DECK):
        a1 = (k + 1) * F_D + (0.01 if k == N_DECK - 1 else 0.0)
        check_section(F, F_T, F_D, f"Deck{hx}_{k:02d}")
        obj, _ = frame_prism(f"Deck{hx}_{k:02d}", "BoxRoof/RoofDeck", fr,
                             [(k * F_D, 0.0), (a1, 0.0), (a1, 2 * DECK_Y), (k * F_D, 2 * DECK_Y)], t0, t1, clips=[vx(0.0, sx)])
        assert obj is not None

# 5. ring trusses (3.6)
RING_SAMPLES = []
WEB_ENDS = []                               # (name, inner node, outer vertex) of every web, for the reach check (R-11)


def build_ring(i):
    y = RING_Y0 + MOD * i
    runs, inner, outer, mids = ring_nodes(Z_E, i)
    dirs, norms, _ = outer_faces(outer)
    P3 = lambda xz: Vector((xz[0], y, xz[1]))
    N3 = lambda n: Vector((n[0], 0.0, n[1]))
    coll_c, coll_w = "Ring/RingChords", "Ring/RingWebs"
    corner_n = {k: (N3(runs[k - 1]["d"]) + N3(runs[k]["d"])).normalized() for k in (1, 2, 3)}
    # inner chord: legs split at nodes (A and B staggered), top runs whole, mitred at the corners, feet on the raft
    for ab, w_off in (("A", -CHORD_OFF), ("B", CHORD_OFF)):
        for k, r in enumerate(runs):
            up = N3(r["n"])
            if k in (0, 3):
                step = r["L"] / r["npan"]
                zc = [0.0] + [j * step for j in LEG_SPLICE[ab]] + [Z_E]
                assert max(b - a for a, b in zip(zc[:-1], zc[1:])) <= SLAT_MAX, "leg slat over 4.80"
                corner = P3(runs[1]["a"]) if k == 0 else P3(runs[3]["a"])
                mitre = hs(corner, -corner_n[1]) if k == 0 else hs(corner, corner_n[3])
                for m in range(len(zc) - 1):
                    p, q = Vector((r["a"][0], y, zc[m])), Vector((r["a"][0], y, zc[m + 1]))
                    last = m == len(zc) - 2
                    slat_bar(f"RingIn_{i:02d}_{k}{ab}_{m}", coll_c, F, p, q, up, w_off=w_off, out=(0, 1, 0),
                             ext=(0.0, 0.3 if last else 0.0), clips=[vz(0.0, +1)] + ([mitre] if last else []))
            else:
                a, b = P3(r["a"]), P3(run_pt(r, r["L"]))
                slat_bar(f"RingIn_{i:02d}_{k}{ab}_0", coll_c, F, a, b, up, w_off=w_off, out=(0, 1, 0), ext=(0.3, 0.3),
                         clips=[hs(a, corner_n[k]), hs(b, -corner_n[k + 1])])
    # outer chord: one sandwich pair per segment, mitred on the bisector at every shared vertex (corner vertices included)
    Q = [P3(o[1]) for o in outer]
    bis = [None] + [(N3(dirs[m - 1]) + N3(dirs[m])).normalized() for m in range(1, len(Q) - 1)] + [None]
    for m in range(len(Q) - 1):
        clips = [vz(0.0, +1) if m == 0 else hs(Q[m], bis[m]),
                 vz(0.0, +1) if m == len(Q) - 2 else hs(Q[m + 1], -bis[m + 1])]
        for ab, w_off in (("A", -CHORD_OFF), ("B", CHORD_OFF)):
            slat_bar(f"RingOut_{i:02d}_{m:02d}{ab}", coll_c, F, Q[m], Q[m + 1], N3(norms[m]), w_off=w_off, out=(0, 1, 0),
                     ext=(0.3, 0.3), clips=clips)
    # webs: Warren zigzag inner node -> outer vertex -> next inner node, rising in y - 0.03..0, falling in 0..+0.03,
    # ends cut flush with the far face of the chord they land in

    def inner_clips(idx, k_own, far):
        """Clips at the inner node `idx` for a web on run k_own whose far end is the outer vertex `far`."""
        pn = inner[idx][1]
        n_own = runs[k_own]["n"]
        out = [hs(P3(pn) - N3(n_own) * F_D / 2, N3(n_own))]        # end flush with the own chord's inner face
        others = {inner[idx][2]} | ({inner[idx - 1][2]} if idx > 0 else set())
        for k in others - {k_own}:
            # corner node: stay inside the other run's outer face. Right at the eaves (the leg's face beside a slope
            # web, the slope's face above a leg web); at the apex the other slope's outer face extended passes under
            # the web body and cut the v02 webs to stubs, so the clip applies only when the far end lies inside it.
            # Without it the own inner-face clip bounds the end: past the apex node the web stays above the other
            # slope's inner face (the own face line rises past the ridge) and its corners sit under the other outer face.
            p_o, n_in = P3(pn) + N3(runs[k]["n"]) * F_D / 2, -N3(runs[k]["n"])
            if (far - p_o).dot(n_in) >= 0:
                out.append(hs(p_o, n_in))
        return out

    def outer_clips(m):
        return [hs(Q[m] + N3(n) * F_D / 2, -N3(n)) for n in (norms[m - 1], norms[m])]

    for j in range(len(inner) - 1):
        m, k_own = mids[j], inner[j][2]
        n0, n1 = P3(inner[j][1]), P3(inner[j + 1][1])
        slat_bar(f"RingWeb_{i:02d}_{j:02d}R", coll_w, F, n0, Q[m], (0, 0, 1), w_off=-F_T / 2, out=(0, 1, 0), ext=(0.2, 0.2),
                 clips=[vz(0.0, +1)] + inner_clips(j, k_own, Q[m]) + outer_clips(m))
        slat_bar(f"RingWeb_{i:02d}_{j:02d}F", coll_w, F, Q[m], n1, (0, 0, 1), w_off=F_T / 2, out=(0, 1, 0), ext=(0.2, 0.2),
                 clips=[vz(0.0, +1)] + inner_clips(j + 1, k_own, Q[m]) + outer_clips(m))
        WEB_ENDS.append((f"RingWeb_{i:02d}_{j:02d}R", n0, Q[m]))
        WEB_ENDS.append((f"RingWeb_{i:02d}_{j:02d}F", Q[m], n1))
    # R-10 samples: three half-panel vertices per truss sit at d(s, i) from the inner outline
    for m in (mids[5], mids[len(mids) // 2], mids[-6]):
        s, (qx, qz) = outer[m]
        r = next(rr for rr in runs if rr["s0"] - 1e-9 <= s <= rr["s0"] + rr["L"] + 1e-9)
        px, pz = run_pt(r, s - r["s0"])
        RING_SAMPLES.append((i, s, math.hypot(qx - px, qz - pz), ring_depth(s, i)))
    # v02 corner vertices: d(s_c, i) from both run lines meeting at the corner (the offset polygon's vertex)
    for k in (1, 2, 3):
        s_c = runs[k]["s0"]
        m = mids[sum(rr["npan"] for rr in runs[:k])] - 1        # the corner vertex precedes run k's first mid
        assert abs(outer[m][0] - s_c) < 1e-9
        qx, qz = outer[m][1]
        for rr in (runs[k - 1], runs[k]):
            dist = (qx - rr["a"][0]) * rr["n"][0] + (qz - rr["a"][1]) * rr["n"][1]
            RING_SAMPLES.append((i, s_c, dist, ring_depth(s_c, i)))
    return len(inner) - 1


N_PANELS = [build_ring(i) for i in range(N_RING)]
for i, s, got, want in RING_SAMPLES:
    assert abs(got - want) < 1e-6, ("depth rule", i, s, got, want)
# R-11: every web reaches both its ends. A web end is cut flush with the far face of the chord it lands in, so its
# nearest corner lies within about 0.08 of the node (0.06 chord half-depth plus the bevel); a stub cut short by a
# wrong clip (v02: 22 apex webs at 0.27 of 0.45) leaves one end more than 0.2 away. Both checks were blind to it.
WEB_REACH = 0.15
web_worst = 0.0
for name, end_a, end_b in WEB_ENDS:
    vs = [bpy.data.objects[name].matrix_world @ v.co for v in bpy.data.objects[name].data.vertices]
    reach = max(min((v - end_a).length for v in vs), min((v - end_b).length for v in vs))
    web_worst = max(web_worst, reach)
    assert reach <= WEB_REACH, ("web stub", name, reach, (end_b - end_a).length)
assert len(WEB_ENDS) == N_RING * 36 * 2, len(WEB_ENDS)

# 6. y-bracing (3.5): four X's per side in two panels per half row, halving joints, ties at the panel joints


def brace(prefix, sgn, y0, y1, z0, z1, rising, lap_side):
    xc = sgn * sum(BR_X) / 2
    p = Vector((xc, y0, z0 if rising else z1))
    q = Vector((xc, y1, z1 if rising else z0))
    L = (q - p).length
    e1 = (q - p) / L
    dy, dz = y1 - y0, z1 - z0
    cos_phi = abs(dy * dy - dz * dz) / (L * L)                # angle between the two diagonals of the X
    lap = F_D * (1 + cos_phi) / math.sqrt(1 - cos_phi * cos_phi) + LAP_MARGIN
    legs = [(RING_Y0 + MOD * i - y0) / dy * L for i in range(N_RING) if y0 + 1e-6 < RING_Y0 + MOD * i < y1 - 1e-6]
    splice = max(s for s in legs if s <= SLAT_MAX and abs(s - L / 2) > lap / 2 + 0.05)
    cuts = sorted({0.0, L / 2 - lap / 2, L / 2 + lap / 2, splice, L})
    assert max(b - a for a, b in zip(cuts[:-1], cuts[1:])) <= SLAT_MAX
    clips = [vy(y0, +1), vy(y1, -1), vz(z0, +1), vz(z1, -1)]
    for m, (sa, sb) in enumerate(zip(cuts[:-1], cuts[1:])):
        is_lap = abs((sa + sb) / 2 - L / 2) < 1e-6
        slat_bar(f"{prefix}_{m}", "Bracing", F, p + e1 * sa, p + e1 * sb, (0, 0, 1),
                 w_off=lap_side * F_T / 4 if is_lap else 0.0, out=(1, 0, 0),
                 ext=(0.3 if sa == 0.0 else 0.0, 0.3 if abs(sb - L) < 1e-9 else 0.0), clips=clips, lap=is_lap)
    return math.degrees(math.atan2(dz, dy))


BRACE_ANGLES = []
for bx, sgn in (("E", +1), ("W", -1)):
    for pi, (y0, y1) in enumerate(((RING_Y0, 0.0), (0.0, -RING_Y0))):
        for pz, (z0, z1) in enumerate(BR_PANELS):
            BRACE_ANGLES.append(brace(f"Brace{bx}_{pi}{pz}R", sgn, y0, y1, z0, z1, True, -1))
            BRACE_ANGLES.append(brace(f"Brace{bx}_{pi}{pz}F", sgn, y0, y1, z0, z1, False, +1))
    x0, x1 = sorted((sgn * BR_X[0], sgn * BR_X[1]))
    for tn, (z0, z1) in (("lo", TIE_LO), ("hi", TIE_HI)):
        for q, (ya, yb) in enumerate(((RING_Y0, 2 * MOD), (2 * MOD, -RING_Y0))):      # spliced on the leg at y = 1.30
            slat_box(f"Tie{bx}_{tn}{q}", "Bracing", F, x0, x1, ya, yb, z0, z1)
assert min(BRACE_ANGLES) >= 45.0, BRACE_ANGLES                                          # R-20, R-28

# 7. chord spacers (P2-01, structural review 5): F 30 x 120 between the facing chord slats of trusses i and i + 1,
# i = 0..9, (a) on the outer chord at every third outer vertex counted from the apex both ways (13 per bay, none at
# the feet), each between the two vertices at the same s, so inclined by the depth difference; (b) on the inner top
# chords at all seven nodes of the two top runs (both eave corners, four interior nodes, the apex). Depth 120 along
# the vertex's bisector normal, 30 along its tangent, ends cut flush with the chord faces y_i + 0.06, y_i+1 - 0.06.
SPACER_OUT_IDX = [20 + 3 * k for k in range(-6, 7)]     # outer vertices 2, 5, ..., 38 of 0..40 (20 = apex vertex)
SPACER_IN_IDX = list(range(15, 22))                       # inner nodes 15..21: W eave corner, 16, 17, apex 18, 19, 20, E eave corner
SPACER_FACE = CHORD_OFF + F_T / 2                         # 0.06: the chord slat's outer face
SPACER_ENDS = []                                          # (name, y0, y1, P0, P1, N) for the reach and flush checks


def bisector(n1, n2):
    return Vector((n1[0] + n2[0], 0.0, n1[1] + n2[1])).normalized()


def spacer(name, y0, y1, q0, q1, N, kink):
    """Spacer between the chord face y0 (truss i) and y1 (truss i + 1) at the vertex q0 / q1 (x, z) of each, depth
    along N. A true 30 x 120 bar bevelled at both ends by the face planes; the bevel measures 120 / cos(beta) on the
    face, so the axis is shifted inward by 60 (1 / cos(beta) - 1), plus 15 tan(kink / 2) so the flat outer face stays
    under both chord faces meeting at the vertex. Nothing rises above the chord's outer face (W_out, H_out unchanged);
    the inner edge is proud inside the truss depth by twice the shift, at most about 12 mm."""
    P0, P1 = Vector((q0[0], y0, q0[1])), Vector((q1[0], y1, q1[1]))
    T = Vector((N.z, 0.0, -N.x))
    beta = math.atan2(abs((P1 - P0).dot(N)), y1 - y0)
    shift = F_D / 2 * (1.0 / math.cos(beta) - 1.0) + F_T / 2 * math.tan(kink / 2)
    slat_bar(name, "Ring/RingSpacers", F, P0 - N * shift, P1 - N * shift, N, out=T, ext=(0.1, 0.1),
             clips=[vy(y0, +1), vy(y1, -1)])
    SPACER_ENDS.append((name, y0, y1, P0, P1, N))


for i in range(N_RING - 1):
    y_a, y_b = RING_Y0 + MOD * i + SPACER_FACE, RING_Y0 + MOD * (i + 1) - SPACER_FACE     # facing faces, 0.53 apart
    runs, inner_a, outer_a, _ = ring_nodes(Z_E, i)
    _, inner_b, outer_b, _ = ring_nodes(Z_E, i + 1)
    dirs_a, norms_a, _ = outer_faces(outer_a)
    dirs_b, norms_b, _ = outer_faces(outer_b)
    for m in SPACER_OUT_IDX:
        N = (bisector(norms_a[m - 1], norms_a[m]) + bisector(norms_b[m - 1], norms_b[m])).normalized()
        kink = max(math.acos(max(-1.0, min(1.0, d[m - 1][0] * d[m][0] + d[m - 1][1] * d[m][1]))) for d in (dirs_a, dirs_b))
        spacer(f"ChordSpacerO_{i:02d}_{m:02d}", y_a, y_b, outer_a[m][1], outer_b[m][1], N, kink)
    for j in SPACER_IN_IDX:
        assert inner_a[j][1] == inner_b[j][1]                 # the inner outline is the same for every truss
        k = inner_a[j][2]
        corner = inner_a[j - 1][2] != k                       # first node of a run: the corner mitre, bisector normal
        N = bisector(runs[k - 1]["n"], runs[k]["n"]) if corner else bisector(runs[k]["n"], runs[k]["n"])
        spacer(f"ChordSpacerI_{i:02d}_{j:02d}", y_a, y_b, inner_a[j][1], inner_b[j][1], N, 0.0)

# 8. roof-plane bracing (P2-02, structural review 6): per slope, X's of F 30 x 120 laid flat under the inner top
# chords (top face on the chord underside plane, 30 below it, 0.04 clear of the deck) in three-bay panels from truss
# 0 to truss 9 (bay 9..10 unbraced, the end truss held by the spacers). Each X is the rising and the falling diagonal
# of its panel, eave line to apex line, halving joint at the crossing as in the y-braces; ends mitred on the truss
# planes y_a, y_b against the next diagonal of the zigzag, cut plumb at the apex line x = 0 and at the leg inner face.
ROOF_PANELS = ((0, 3), (3, 6), (6, 9))
SLOPE_L = RING_X / COS                                    # inner top chord, eave node to apex node (2.352)
ROOF_LAYER = -(F_D / 2 + F_T / 2)                         # centreline of the 30 mm layer under the chord, along its normal


def roof_diag(prefix, sx, ia, ib, rising, lap_side):
    ya, yb = RING_Y0 + MOD * ia, RING_Y0 + MOD * ib
    n = Vector((sx * SIN, 0.0, COS))                      # outward normal of the slope
    u = Vector((sx * COS, 0.0, -SIN))                     # down the slope, apex to eave
    apex = Vector((0.0, 0.0, Z_E + RING_RISE))
    pt = lambda a, y: apex + u * a + n * ROOF_LAYER + Vector((0.0, y, 0.0))
    p = pt(SLOPE_L if rising else 0.0, ya)
    q = pt(0.0 if rising else SLOPE_L, yb)
    L = (q - p).length
    e1 = (q - p) / L
    dy = yb - ya
    cos_phi = abs(dy * dy - SLOPE_L * SLOPE_L) / (L * L)  # angle between the two diagonals of the X
    lap = F_D * (1 + cos_phi) / math.sqrt(1 - cos_phi * cos_phi) + LAP_MARGIN
    cuts = [0.0, L / 2 - lap / 2, L / 2 + lap / 2, L]
    assert L <= SLAT_MAX, L
    clips = [vy(ya, +1), vy(yb, -1), vx(0.0, sx), vx(sx * LEG_FACE, -sx)]
    for m, (sa, sb) in enumerate(zip(cuts[:-1], cuts[1:])):
        is_lap = m == 1
        slat_bar(f"{prefix}_{m}", "Ring/RoofBracing", F, p + e1 * sa, p + e1 * sb, n.cross(e1),
                 w_off=lap_side * F_T / 4 if is_lap else 0.0, out=n,
                 ext=(0.3 if m == 0 else 0.0, 0.3 if m == 2 else 0.0), clips=clips, lap=is_lap)
    return math.degrees(math.atan2(RING_X, abs(dy)))     # plan angle to the row


ROOF_ANGLES = []
for hx, sx in (("E", +1), ("W", -1)):
    for ia, ib in ROOF_PANELS:
        ROOF_ANGLES.append(roof_diag(f"RoofBrace{hx}_{ia}{ib}R", sx, ia, ib, True, -1))
        ROOF_ANGLES.append(roof_diag(f"RoofBrace{hx}_{ia}{ib}F", sx, ia, ib, False, +1))
assert min(ROOF_ANGLES) >= 45.0, ROOF_ANGLES                                            # P2-02 angle

# ------------------------------------------------------------------
# CHECKS ON THE GENERATED GEOMETRY

def world_bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


# R-02 on the outer chord faces (its definition); the whole ring (webs, spacers, roof bracing) must have the same bounds
chord_objs = list(bpy.data.collections["RingChords"].all_objects)
rx0, rx1, ry0, ry1, rz0, rz1 = world_bounds(chord_objs)
W_OUT = max(rx1 - rx0, ry1 - ry0)
H_OUT = rz1
RATIO = H_OUT / W_OUT
assert abs(RATIO - 2.0) <= 0.01, ("2:1 rule", W_OUT, H_OUT, RATIO)                     # R-02
assert abs((rx1 - rx0) - (ry1 - ry0)) <= 0.05, ("square plan", rx1 - rx0, ry1 - ry0)  # R-03
assert abs(rz0) < 1e-6, ("feet on the raft", rz0)                                     # R-09, R-29
ring_b = world_bounds(list(bpy.data.collections["Ring"].all_objects))
RING_DELTA = max(abs(ring_b[0] - rx0), abs(ring_b[1] - rx1), abs(ring_b[2] - ry0), abs(ring_b[3] - ry1), abs(ring_b[5] - rz1))
assert RING_DELTA < 1e-4, ("spacers or roof bracing change W_out or H_out", RING_DELTA)
# P2-01: 200 spacers, each spanning exactly the gap between the two chord faces (contact at both ends), every vertex on
# an end plane, the outer ones nowhere outside the chord's outer face at either end
assert len(SPACER_ENDS) == (N_RING - 1) * (len(SPACER_OUT_IDX) + len(SPACER_IN_IDX)) == 200, len(SPACER_ENDS)
SP_PROUD = -1.0
for name, y0, y1, P0, P1, N in SPACER_ENDS:
    o = bpy.data.objects[name]
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    assert abs(min(v.y for v in vs) - y0) < 1e-6 and abs(max(v.y for v in vs) - y1) < 1e-6, (name, "spacer short of a chord face")
    for v in vs:
        near0 = abs(v.y - y0) < 1e-6
        assert near0 or abs(v.y - y1) < 1e-6, (name, "spacer vertex off the end planes", v)
        off = (v - (P0 if near0 else P1)).dot(N)
        if name.startswith("ChordSpacerO"):
            SP_PROUD = max(SP_PROUD, off - F_D / 2)
            assert off <= F_D / 2 + 1e-6, (name, "outer spacer proud of the chord face", off)
        else:
            assert off >= -F_D / 2 - 1e-6, (name, "inner spacer below the chord underside", off)
# P2-02: 12 diagonals in 36 pieces, inside x = +/-2.26 and y_0..y_9, the underside at least 0.035 above the deck top
assert len(ROOF_ANGLES) == 12
roof_objs = list(bpy.data.collections["RoofBracing"].all_objects)
assert len(roof_objs) == 36, len(roof_objs)
bx0, bx1, by0, by1, bz0, bz1 = world_bounds(roof_objs)
assert -LEG_FACE - 1e-6 <= bx0 and bx1 <= LEG_FACE + 1e-6 and RING_Y0 - 1e-6 <= by0 and by1 <= RING_Y0 + 9 * MOD + 1e-6
ROOF_CLEAR = min((Z_E + RING_RISE * (1 - xs / RING_X) - (F_D / 2 + F_T) / COS) - (tc_top(xs) + F_T / COS)
                 for xs in (0.0, EAVE_X))
assert ROOF_CLEAR >= 0.035, ("roof diagonal into the deck", ROOF_CLEAR)
assert abs(ROOM_CLEAR - 3.90) < 1e-9                                                  # R-01
assert all(abs(RAFT_W - 7.20) < 1e-9 for _ in (0,)) and abs(RAFT_T - 0.25) < 1e-9     # R-07
all_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
assert world_bounds(all_meshes)[4] >= -RAFT_T - 1e-6                                  # R-12
assert abs(LEG_FACE - WALL_OUT - 0.082) < 1e-9                                        # R-13 gap box to legs
for xs in (0.0, EAVE_X):
    chord_face = Z_E + RING_RISE * (1 - xs / RING_X) - F_D / 2 / COS
    gap = chord_face - (tc_top(xs) + F_T)
    assert 0.06 <= gap <= 0.08, ("deck to ring chord", xs, gap)                        # R-13 deck clearance
assert EAVE_X < LEG_FACE and TAIL_X < BR_X[0] and BR_X[1] <= LEG_FACE
assert TAIL_X - X_HEEL <= 0.11                                                        # R-25
assert all(n == 36 for n in N_PANELS), N_PANELS                                       # 15 + 3 + 3 + 15 panels
assert (Z_E / 15) <= PANEL_MAX
assert TIE_HI[1] < tc_top(EAVE_X) and BR_PANELS[1][0] >= TIE_LO[1]
# R-24: floor boards span at most 0.65 between joists, deck boards at most 0.65 between roof trusses
assert max(b - a for a, b in zip(JOIST_Y[:-1], JOIST_Y[1:])) <= MOD + 1e-9
_rt = sorted(ROOF_T_Y)
assert max(b - a for a, b in zip(_rt[:-1], _rt[1:])) <= MOD + 1e-9
# R-31: every board touches every rail it crosses: the board layer is contiguous with its rail layer
assert abs(LAYERS["bin"][1] - LAYERS["rin"][0]) < 1e-9 and abs(LAYERS["rout"][1] - LAYERS["bout"][0]) < 1e-9
# R-21: no piece longer than 4.80 (largest vertex-to-vertex distance, 20 mm allowance for bevelled ends)
longest, longest_name = 0.0, ""
for o in all_meshes:
    if o.name == "Raft":
        continue
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    span = max((a - b).length for a in vs for b in vs)
    if span > longest:
        longest, longest_name = span, o.name
assert longest <= SLAT_MAX + 0.02, ("slat over 4.80", longest, longest_name, Z_E)
assert len(PIECES) == len(all_meshes) - 1, (len(PIECES), len(all_meshes))            # every timber piece went through the section check

print(f"Built experiment 16 v04: {len(all_meshes)} elements ({len(PIECES)} timber pieces + raft)")
print(f"  z_e = {Z_E:.4f}, z_h = {Z_H:.4f}, W_out = {W_OUT:.4f}, H_out = {H_OUT:.4f}, H/W = {RATIO:.4f}"
      f" (chord faces; whole ring differs by {RING_DELTA * 1000:.3f} mm)")
print(f"  spacers {len(SPACER_ENDS)} = 10 bays x ({len(SPACER_OUT_IDX)} outer + {len(SPACER_IN_IDX)} inner),"
      f" outer ends at most {SP_PROUD * 1000:.2f} mm proud of the chord face")
print(f"  roof diagonals {len(ROOF_ANGLES)} in {len(roof_objs)} pieces, plan angle {min(ROOF_ANGLES):.1f} deg,"
      f" underside {ROOF_CLEAR:.3f} above the deck")
print(f"  ring plan extents x {rx1 - rx0:.3f}, y {ry1 - ry0:.3f}; eave x = {EAVE_X:.4f}; ties hi {TIE_HI[0]:.3f}..{TIE_HI[1]:.3f}")
print(f"  brace angles {min(BRACE_ANGLES):.1f}..{max(BRACE_ANGLES):.1f} deg; longest piece {longest:.3f} m")
print(f"  {len(WEB_ENDS)} webs reach both ends within {web_worst:.3f} m (limit {WEB_REACH})")
