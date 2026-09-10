# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 15 (Koreni), Fable run, v01
#
# Three variations of a long house on the Koreni slope, each on its own
# copy of the terrain strip: A the bridge (y 0..20), B the cut (30..50),
# C the steps (60..80). Numbers trace to Fable/concept.md (section in
# brackets) and Fable/sources.md; "mine" marks Builder derivations
# recorded in version_notes.md.
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
import framing
for _m in (craftbot, g2, planes, framing):
    importlib.reload(_m)

from craftbot_lib import box, prism_x, prism_y
from framing import wall_along_x, wall_along_y, flight

EPS = 1e-6

# ------------------------------------------------------------------
# PARAMETERS

# terrain (concept 1.4): (x, z) knees of the ground profile; z depends on x only
GROUND = [(-6.0, 0.55), (0.0, 0.25), (26.0, -1.05), (50.0, -2.97), (100.0, -9.97)]
KNEES = [0.0, 26.0, 50.0]
SKIN_T = 0.30                                   # terrain skin thickness (1.5)
STRIP_X = (-6.0, 100.0)
STRIP_W = 20.0
Y_ORG = {"A": 0.0, "B": 30.0, "C": 60.0}         # strip origins (1.5)

# shared plan (2.1)
PAV_X, PAV_Y = (5.0, 11.0), (9.0, 15.0)
BAR_Y = (7.0, 13.0)
BAR_END = {"A": 71.0, "B": 66.0, "C": 66.0}
ROOF_END = {"A": 71.0, "B": 70.0, "C": 70.0}     # terrace roof end (B, C: 66..70 terrace)
SEGMENTS = [(11.0, 28.0, -1), (28.0, 44.0, +1), (44.0, 60.0, -1), (60.0, 71.0, +1)]  # (x0, x1, open side: -1 = ESE y_min, +1 = WNW y_max) (2.2)

# sections (2.3)
T_PAV = 0.25                                    # pavilion, box and plinth walls (CMHC Table 5)
T_RET = 0.30                                    # retaining stems
T_CLOSED = 0.20                                 # closed-side wall (concrete in B, C; steel-stud panel in A)
T_CORE = 0.20
CORE_H, CORE_LID = 2.70, 0.20
T_PART, PART_GAP = 0.10, 0.025
SLAB_G, GRAVEL, SLAB_S, SLAB_ROOF = 0.20, 0.15, 0.30, 0.20   # on ground / gravel / suspended / roof
PAVING = 0.15                                   # courtyard and sunken-strip paving, 150 below the floor (CMHC ch. 7)
INS_MIN, INS_SLOPE = 0.15, 0.02                 # roof insulation wedge (AHCD 5-15)
PARAPET_T, PARAPET_H = 0.20, 0.60               # above the roof slab top (AHCD 1-21)
FASCIA = 0.15                                   # C (AHCD 5-37)
CLEAR_H = 3.30
BEAM = (0.16, 0.33)                             # IPE 330 roof beams (width, depth)
FBEAM = (0.15, 0.30)                            # IPE 300 floor beams (A)
GIRDER = (0.30, 0.70)                           # A plate girders
GIRDER_Y = (7.3, 12.7)
COL = 0.24                                      # HEB 240
PLATE = (0.30, 0.03)                            # base / cap plates
POST = 0.15                                     # SHS 150
POST_IN = 0.10                                  # post centre inside the outer face
BAY = 4.0
MULL = (0.051, 0.152)                           # storefront mullion / transom (AHCD 6-6)
GLASS = 0.025
HEAD_GAP = 0.006
PANE_NOM = 4.0 / 3.0
FOOT_W, FOOT_T = 0.80, 0.40                     # strip footing
PAD_W, PAD_T = 1.80, 0.60                       # pad footing
FOOT_DEPTH = 1.20                               # underside below finished grade (CMHC Table 3)
STEP_MAX, RUN_MIN, RISER_T = 0.60, 0.60, 0.15   # stepped footings (CMHC Fig. 35)
LBASE_T = 0.40                                  # cantilever L-wall base thickness
GOING, STAIR_W, LANDING = 0.28, 1.20, 1.20
GUARD_H, BALU_T, BALU_H = 1.07, 0.019, 1.10
DOOR_W, DOOR_H = 0.90, 2.10
ENTRY_W, NIB = 0.95, 0.30
GARAGE = 2.40
WIN_STRIP = (1.5, 2.4)                          # closed-wall strip window sill / head above the floor (900 high) (mine)

# variation levels
A_FLOOR, A_BOX_FLOOR = 0.90, -3.30              # (3.1)
B_FLOOR = -2.60                                 # (4.1)
C_LEVELS = [(11.0, 29.0, -1.20), (29.0, 47.0, -2.55), (47.0, 66.0, -3.90)]   # (5.1)
C_SPLIT = {0: 27.0, 1: 45.0, 2: 55.0}           # slab on ground -> suspended (5.2, R-47)
PAV_FLOOR = 0.15
PAV_ROOF_TOP = 3.65
C_R1 = ((5.0, 3.40), (11.0, 3.90))              # folded roof plane R1 (top surface)
C_R2 = ((11.0, 3.90), (70.0, -0.93))            # plane R2 (top surface)
COURT_W = {"B": 2.0, "C": 1.5}                  # sunken strip width outside the glass line


# ------------------------------------------------------------------
# DERIVED FUNCTIONS


def lin(p, q, x):
    return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])


def zg(x):
    """Ground surface z(x), piecewise linear through GROUND (concept 1.4)."""
    for p, q in zip(GROUND, GROUND[1:]):
        if x <= q[0] + EPS:
            return lin(p, q, x)
    return lin(GROUND[-2], GROUND[-1], x)


def x_at_ground(z):
    """Downhill position where the ground reaches z (z(x) falls monotonically for x >= 0)."""
    for p, q in zip(GROUND, GROUND[1:]):
        if q[1] <= z <= p[1]:
            return p[0] + (z - p[1]) * (q[0] - p[0]) / (q[1] - p[1])
    return GROUND[-1][0]


def r1_top(x):
    return lin(*C_R1, x)


def r2_top(x):
    return lin(*C_R2, x)


def c_roof_top(x):
    return r1_top(x) if x <= 11.0 else r2_top(x)


def c_roof_under(x):
    return c_roof_top(x) - SLAB_ROOF


def cuts(x0, x1, breaks):
    pts = [x0] + sorted(b for b in breaks if x0 + EPS < b < x1 - EPS) + [x1]
    return list(zip(pts, pts[1:]))


def fn(v):
    return v if callable(v) else (lambda x: v)


def post_lines(x_end):
    """Post centres at 4 m from x = 11, first and last 0.10 inside the end faces (2.3)."""
    xs = [11.0 + POST_IN]
    x = 15.0
    while x < x_end - POST_IN - 0.5:
        xs.append(x)
        x += BAY
    xs.append(x_end - POST_IN)
    return xs


def open_side(x):
    for x0, x1, s in SEGMENTS:
        if x0 - EPS <= x < x1 - EPS:
            return s
    return SEGMENTS[-1][2]


def rects_minus(rects, hole):
    """Plan rectangles minus one rectangle, as rectangles (skin holes)."""
    hx0, hx1, hy0, hy1 = hole
    out = []
    for x0, x1, y0, y1 in rects:
        if hx0 >= x1 - EPS or hx1 <= x0 + EPS or hy0 >= y1 - EPS or hy1 <= y0 + EPS:
            out.append((x0, x1, y0, y1))
            continue
        cx0, cx1, cy0, cy1 = max(hx0, x0), min(hx1, x1), max(hy0, y0), min(hy1, y1)
        if cx0 - x0 > EPS:
            out.append((x0, cx0, y0, y1))
        if x1 - cx1 > EPS:
            out.append((cx1, x1, y0, y1))
        if cy0 - y0 > EPS:
            out.append((cx0, cx1, y0, cy0))
        if y1 - cy1 > EPS:
            out.append((cx0, cx1, cy1, y1))
    return out


CHECKS = []


def check(ok, text):
    CHECKS.append((bool(ok), text))


# ------------------------------------------------------------------
# VARIATION CONTEXT


class Var:
    NAMES = {"A": "A_Bridge", "B": "B_Cut", "C": "C_Steps"}

    def __init__(self, letter):
        self.L = letter
        self.yo = Y_ORG[letter]
        self.holes = []                          # plan rectangles cut out of the terrain skin (strip coords)
        self.n = {}

    def C(self, sub):
        return f"{self.NAMES[self.L]}/{self.L}_{sub}"

    def name(self, family):
        k = self.n.get(family, 0)
        self.n[family] = k + 1
        return f"{self.L}_{family}_{k:03d}"

    # --- primitives in strip coordinates -------------------------------
    def box(self, family, sub, x0, x1, y0, y1, z0, z1):
        return box(self.name(family), self.C(sub), x0, x1, y0 + self.yo, y1 + self.yo, z0, z1)

    def prism_y(self, family, sub, y0, y1, pts_xz):
        return prism_y(self.name(family), self.C(sub), y0 + self.yo, y1 + self.yo, pts_xz)

    def prism_x(self, family, sub, x0, x1, pts_yz):
        return prism_x(self.name(family), self.C(sub), x0, x1, [(y + self.yo, z) for y, z in pts_yz])

    def hole(self, x0, x1, y0, y1):
        self.holes.append((x0, x1, y0, y1))

    # --- footings ------------------------------------------------------
    def footing_x(self, family, x0, x1, yc, z_under, max_run=None, width=FOOT_W, thick=FOOT_T, breaks=()):
        """Strip footing along x under a wall centred on yc: runs stepped so no
        step exceeds STEP_MAX, undersides at z_under(x) at the downhill end of
        each run, risers RISER_T thick joining the runs (CMHC Fig. 35).
        Returns [(xa, xb, z_underside)]."""
        z_under = fn(z_under)
        runs = []
        for xa, xb in cuts(x0, x1, KNEES + list(breaks)):
            fall = z_under(xa) - z_under(xb)
            n = max(1, math.ceil(fall / STEP_MAX - 1e-9))
            if max_run:
                n = max(n, math.ceil((xb - xa) / max_run - 1e-9))
            L = (xb - xa) / n
            for k in range(n):
                a, b = xa + k * L, xa + (k + 1) * L
                runs.append((a, b, z_under(b)))
        # merge consecutive runs at the same level; a run shorter than RUN_MIN
        # (a break landing near a wall end) joins its neighbour at the lower underside
        merged = []
        for r in runs:
            if merged and (abs(merged[-1][2] - r[2]) < 1e-6 or r[1] - r[0] < RUN_MIN - EPS
                           or merged[-1][1] - merged[-1][0] < RUN_MIN - EPS):
                merged[-1] = (merged[-1][0], r[1], min(merged[-1][2], r[2]))
            else:
                merged.append(r)
        runs = merged
        y0, y1 = yc - width / 2, yc + width / 2
        for a, b, zu in runs:
            check(b - a >= RUN_MIN - EPS, f"{self.L} footing {family} run {b - a:.2f} m >= {RUN_MIN}")
            self.box(family, "Footings", a, b, y0, y1, zu, zu + thick)
        for (a, b, zu), (a2, b2, zu2) in zip(runs, runs[1:]):
            check(zu - zu2 <= STEP_MAX + EPS, f"{self.L} footing {family} step {zu - zu2:.2f} m <= {STEP_MAX}")
            self.box(family + "Riser", "Footings", b - RISER_T, b, y0, y1, zu2, zu)
        return runs

    def footing_y(self, family, xc, y0, y1, z_under, width=FOOT_W, thick=FOOT_T):
        zu = fn(z_under)(xc)
        self.box(family, "Footings", xc - width / 2, xc + width / 2, y0, y1, zu, zu + thick)
        return zu + thick

    # --- walls ---------------------------------------------------------
    def wall_x(self, family, sub, x0, x1, y0, y1, z_bot, z_top, openings=(), breaks=()):
        """Concrete wall along x as convex prism pieces: bottom / top may be
        functions of x (stepped footings, ground line, roof plane); pieces
        split at `breaks` and the KNEES; rectangular openings (x0, x1, z0, z1)."""
        z_bot, z_top = fn(z_bot), fn(z_top)
        n = 0
        for a, b in cuts(x0, x1, list(breaks) + KNEES + [11.0]):
            if z_top(a) - z_bot(a) < 1e-4 and z_top(b) - z_bot(b) < 1e-4:
                continue
            poly = [(a, z_bot(a)), (b, z_bot(b)), (b, z_top(b)), (a, z_top(a))]
            if z_top(a) - z_bot(a) < 1e-4:
                poly = [(a, z_bot(a)), (b, z_bot(b)), (b, z_top(b))]
            elif z_top(b) - z_bot(b) < 1e-4:
                poly = [(a, z_bot(a)), (b, z_bot(b)), (a, z_top(a))]
            ops = [(max(ox0, a), min(ox1, b), oz0, oz1) for ox0, ox1, oz0, oz1 in openings
                   if ox1 > a + EPS and ox0 < b - EPS]
            n += wall_along_x(self.name(family), self.C(sub), poly, y0 + self.yo, y1 + self.yo, ops)
        return n

    def wall_y(self, family, sub, x0, x1, y0, y1, z_bot, z_top, openings=()):
        poly = [(y0 + self.yo, z_bot), (y1 + self.yo, z_bot), (y1 + self.yo, z_top), (y0 + self.yo, z_top)]
        ops = [(oy0 + self.yo, oy1 + self.yo, oz0, oz1) for oy0, oy1, oz0, oz1 in openings]
        return wall_along_y(self.name(family), self.C(sub), poly, x0, x1, ops)

    def founded_wall_x(self, family, x0, x1, y0, y1, z_top, z_under, openings=(), breaks=(), max_run=None, sub="Concrete"):
        """Wall along x on a stepped strip footing: one wall piece per run,
        bottom on the run's top."""
        runs = self.footing_x(family + "Ftg", x0, x1, (y0 + y1) / 2, z_under, max_run, breaks=breaks)
        for a, b, zu in runs:
            self.wall_x(family, sub, a, b, y0, y1, zu + FOOT_T, z_top, openings, breaks)
        return runs

    def founded_wall_y(self, family, x0, x1, y0, y1, z_top, z_under, openings=(), sub="Concrete"):
        zt = self.footing_y(family + "Ftg", (x0 + x1) / 2, y0 - (FOOT_W - (x1 - x0)) / 2, y1 + (FOOT_W - (x1 - x0)) / 2, z_under)
        self.wall_y(family, sub, x0, x1, y0, y1, zt, z_top, openings)

    # --- slabs ---------------------------------------------------------
    def slab_x(self, family, sub, x0, x1, y0, y1, z_bot, z_top, breaks=()):
        """Slab / layer along x with sloped or flat faces, one convex prism per segment."""
        z_bot, z_top = fn(z_bot), fn(z_top)
        for a, b in cuts(x0, x1, list(breaks) + KNEES + [11.0]):
            self.prism_y(family, sub, y0, y1, [(a, z_bot(a)), (b, z_bot(b)), (b, z_top(b)), (a, z_top(a))])

    def floor_on_ground(self, family, x0, x1, y0, y1, z_top, holes=()):
        rects = [(x0, x1, y0, y1)]
        for h in holes:
            rects = rects_minus(rects, h)
        for rx0, rx1, ry0, ry1 in rects:
            self.box(family, "Slabs", rx0, rx1, ry0, ry1, z_top - SLAB_G, z_top)
            self.box(family + "Gravel", "Footings", rx0, rx1, ry0, ry1, z_top - SLAB_G - GRAVEL, z_top - SLAB_G)

    def floor_suspended(self, family, x0, x1, y0, y1, z_top, holes=(), thick=SLAB_S):
        rects = [(x0, x1, y0, y1)]
        for h in holes:
            rects = rects_minus(rects, h)
        for rx0, rx1, ry0, ry1 in rects:
            self.box(family, "Slabs", rx0, rx1, ry0, ry1, z_top - thick, z_top)

    # --- steel and glazing --------------------------------------------
    def post(self, x, y, z0, z1):
        self.box("Post", "Steel", x - POST / 2, x + POST / 2, y - POST / 2, y + POST / 2, z0, z1)

    def storefront(self, family, along, a0, a1, b_line, z0, z1, end_mullions=(True, True), n_panes=None):
        """AHCD storefront run from a0 to a1 on the line b (y for along='x',
        x for along='y'): sill transom on the slab top z0, head transom
        HEAD_GAP under the beam underside z1, mullions at pane joints, glass
        plates on the line. Runs that end at a post get no end mullion."""
        mw, md = MULL
        L = a1 - a0
        n = n_panes or max(1, int(round(L / PANE_NOM)))
        b0, b1 = b_line - md / 2, b_line + md / 2
        g0, g1 = b_line - GLASS / 2, b_line + GLASS / 2

        def rect(fam, p0, p1, bb0, bb1, zz0, zz1):
            if along == "x":
                self.box(fam, "Glazing", p0, p1, bb0, bb1, zz0, zz1)
            else:
                self.box(fam, "Glazing", bb0, bb1, p0, p1, zz0, zz1)
        zs1 = z0 + mw
        zh0 = z1 - HEAD_GAP - mw
        rect(family + "Sill", a0, a1, b0, b1, z0, zs1)
        rect(family + "Head", a0, a1, b0, b1, zh0, z1 - HEAD_GAP)
        joints = [a0 + L * k / n for k in range(n + 1)]
        edges = []
        for k, x in enumerate(joints):
            if k == 0:
                if end_mullions[0]:
                    rect(family + "Mull", x, x + mw, b0, b1, zs1, zh0)
                    edges.append(x + mw)
                else:
                    edges.append(x)
            elif k == n:
                if end_mullions[1]:
                    rect(family + "Mull", x - mw, x, b0, b1, zs1, zh0)
                    edges.append(x - mw)
                else:
                    edges.append(x)
            else:
                rect(family + "Mull", x - mw / 2, x + mw / 2, b0, b1, zs1, zh0)
                edges += [x - mw / 2, x + mw / 2]
        for k in range(n):
            rect(family + "Glass", edges[2 * k], edges[2 * k + 1], g0, g1, zs1, zh0)

    def balustrade(self, family, x0, x1, y0, y1, z0):
        self.box(family, "Glazing", x0, x1, y0, y1, z0, z0 + BALU_H)

    def guard(self, family, x0, x1, y0, y1, z0, h=GUARD_H):
        self.box(family, "Glazing", x0, x1, y0, y1, z0, z0 + h)

    # --- interior ------------------------------------------------------
    def core(self, family, x0, x1, y0, y1, z0, door, store=False):
        """Concrete core: four 200 walls CORE_H high, a 200 lid, one door
        opening 0.9 x 2.1 in the face `door` ('x0','x1','y0','y1') at its
        middle; core 1 gets the 1.2 x 2.5 store (two 100 walls 2.0 high)."""
        z1 = z0 + CORE_H
        t = T_CORE
        d0, d1 = DOOR_W, DOOR_H

        def op(c0, c1):
            m = (c0 + c1) / 2
            return [(m - d0 / 2, m + d0 / 2, z0, z0 + d1)]
        self.wall_x(family, "Cores", x0, x1, y0, y0 + t, z0, z1, op(x0 + t, x1 - t) if door == "y0" else ())
        self.wall_x(family, "Cores", x0, x1, y1 - t, y1, z0, z1, op(x0 + t, x1 - t) if door == "y1" else ())
        self.wall_y(family, "Cores", x0, x0 + t, y0 + t, y1 - t, z0, z1, op(y0 + t, y1 - t) if door == "x0" else ())
        self.wall_y(family, "Cores", x1 - t, x1, y0 + t, y1 - t, z0, z1, op(y0 + t, y1 - t) if door == "x1" else ())
        self.box(family + "Lid", "Cores", x0, x1, y0, y1, z1, z1 + CORE_LID)
        if store:                                  # LHDG 4.7.1: 3 m2, 2 m high, in the corner away from the door
            sx0, sx1 = x1 - t - 2.5, x1 - t
            sy0, sy1 = y1 - t - 1.2, y1 - t
            if door == "x1":
                sx0, sx1 = x0 + t, x0 + t + 2.5
            self.box(family + "Store", "Cores", sx0, sx0 + T_PART, sy0, sy1, z0, z0 + 2.0)
            self.box(family + "Store", "Cores", sx0, sx1, sy0, sy0 + T_PART, z0, z0 + 2.0)

    def partition_x(self, family, x, y0, y1, z0, z_top):
        """100 mm partition across the bar at x (from y0 to y1), a door in the middle,
        top PART_GAP under the structure above (carries nothing)."""
        m = (y0 + y1) / 2
        self.wall_y(family, "Cores", x - T_PART / 2, x + T_PART / 2, y0, y1, z0, z_top - PART_GAP,
                    [(m - DOOR_W / 2, m + DOOR_W / 2, z0, z0 + DOOR_H)])

    def stair_x(self, family, x_top, direction, y0, y1, z_top, z_bot, n_risers, z_min):
        """Straight solid flight descending from the floor edge x_top towards
        `direction` (+1/-1): n_risers - 1 tread blocks whose soffit is solid
        down to z_min; the last riser lands at z_bot. Returns the x of the
        bottom riser."""
        riser = (z_top - z_bot) / n_risers
        check(0.150 - EPS <= riser <= 0.165 + EPS, f"{self.L} stair {family} riser {riser * 1000:.1f} mm in 150..165")
        x_bot = x_top + direction * GOING * (n_risers - 1)
        # framing.flight rises towards `direction` from x_start = the bottom riser
        flight(self.name(family), self.C("Stairs"), x_bot, -direction, y0 + self.yo, y1 + self.yo, z_bot,
               n_risers, GOING, riser, 10.0, z_min)
        return x_bot, riser

    def flight_guard(self, family, x_top, x_bot, y0, y1, z_top, z_bot, z_ground):
        """Guard plate on one open side of a flight: vertical, from z_ground
        (the floor the flight stands on) to GUARD_H above the nosing line."""
        s = (z_top - z_bot) / abs(x_top - x_bot) * (1 if x_top > x_bot else -1)
        xa, xb = min(x_top, x_bot), max(x_top, x_bot)
        za = z_bot + GUARD_H + (s * (xa - x_bot))
        zb = z_bot + GUARD_H + (s * (xb - x_bot))
        self.prism_y(family, "Glazing", y0, y1, [(xa, z_ground), (xb, z_ground), (xb, zb), (xa, za)])

    # --- terrain -------------------------------------------------------
    def terrain(self):
        rects = [(STRIP_X[0], STRIP_X[1], 0.0, STRIP_W)]
        for h in self.holes:
            rects = rects_minus(rects, h)
        for x0, x1, y0, y1 in rects:
            for a, b in cuts(x0, x1, KNEES):
                self.prism_y("Skin", "Terrain", y0, y1,
                             [(a, zg(a) - SKIN_T), (b, zg(b) - SKIN_T), (b, zg(b)), (a, zg(a))])


# ------------------------------------------------------------------
# SHARED ELEMENTS


def pavilion(v, rear_wall=True, roof_top=PAV_ROOF_TOP, sloped=None):
    """Pavilion box (2.1): walls 250 on strip footings, floor slab on ground
    at +0.15, garage door 2.4 x 2.4 and entrance door 0.95 (nib 0.30) in the
    x = 5 face. The rear wall (x = 11) is built by the variation. `sloped`:
    roof top function of x (C), else flat slab at roof_top with a parapet."""
    x0, x1 = PAV_X
    y0, y1 = PAV_Y
    t = T_PAV
    z_under = lambda x: zg(x) - FOOT_DEPTH
    if sloped:
        top_at = lambda x: sloped(x) - SLAB_ROOF
    else:
        top_at = lambda x: roof_top - SLAB_ROOF
    # front wall x = 5 with the two doors (y positions mine: entry beside the garage door)
    ent = (y0 + t + NIB, y0 + t + NIB + ENTRY_W)
    gar = (ent[1] + NIB, ent[1] + NIB + GARAGE)
    check(gar[1] <= y1 - t, f"{v.L} pavilion garage door inside the front wall")
    v.founded_wall_y("PavFront", x0, x0 + t, y0, y1, top_at(x0 + t / 2), z_under,
                     [(ent[0], ent[1], PAV_FLOOR, PAV_FLOOR + DOOR_H), (gar[0], gar[1], PAV_FLOOR, PAV_FLOOR + GARAGE)])
    v.founded_wall_x("PavSideS", x0 + t, x1 - T_RET, y0, y0 + t, top_at, z_under)
    v.founded_wall_x("PavSideN", x0 + t, x1 - T_RET, y1 - t, y1, top_at, z_under)
    v.floor_on_ground("PavFloor", x0 + t, x1 - T_RET, y0 + t, y1 - t, PAV_FLOOR)
    check(PAV_FLOOR - zg(x0) >= 0.15 - EPS, f"{v.L} pavilion slab top {PAV_FLOOR - zg(x0):.2f} m above grade at x = 5 (>= 0.15)")
    v.hole(x0, x1, y0, y1)
    if not sloped:
        v.box("PavRoof", "Roof", x0, x1 - T_RET, y0, y1, roof_top - SLAB_ROOF, roof_top)
        # parapet 200 x 600 on three edges (the x = 11 edge belongs to the rear wall)
        v.box("PavParapet", "Roof", x0, x0 + PARAPET_T, y0, y1, roof_top, roof_top + PARAPET_H)
        v.box("PavParapet", "Roof", x0 + PARAPET_T, x1 - T_RET, y0, y0 + PARAPET_T, roof_top, roof_top + PARAPET_H)
        v.box("PavParapet", "Roof", x0 + PARAPET_T, x1 - T_RET, y1 - PARAPET_T, y1, roof_top, roof_top + PARAPET_H)


def bar_superstructure(v, floor, x_end, roof_top, closed_concrete=True, roof_top_fn=None, x_start=11.0,
                       high_bay=None):
    """Posts, edge beams, transverse roof beams, closed-side walls, storefront
    runs and the roof slab over the bar from x_start to the roof end (2.3).
    floor: slab top z, or a function of x (C). roof_top: z or function of x.
    high_bay (B): (x_wall0, x_wall1, roof_top_high): the first bay carries the
    pavilion roof level and a transverse concrete wall closes the step."""
    floor = fn(floor)
    top = fn(roof_top)
    under = lambda x: top(x) - SLAB_ROOF
    y0, y1 = BAR_Y
    bw, bd = BEAM
    x_house_end = BAR_END[v.L]
    xs = post_lines(x_end)
    # --- which side is glazed per x, and both sides over the terrace
    def glazed(x, s):
        if x >= x_house_end - EPS:
            return True
        return open_side(x) == s

    def beam_top(x):
        # arris bearing: beam top on the slab underside at the beam's downhill edge
        return under(x + bw / 2)

    # posts and transverse beams
    for x in xs:
        bt = beam_top(x)
        bb = bt - bd
        if x < x_house_end - EPS:
            check(bb - floor(x) >= CLEAR_H - 0.34, f"{v.L} beam underside at x = {x:.1f} is {bb - floor(x):.2f} above the floor")
        for s, y in ((-1, y0 + POST_IN), (+1, y1 - POST_IN)):
            if glazed(x, s):
                v.post(x, y, floor(x), bb)
        # transverse beam from the glazed side's edge beam inner face to the far outer face
        ya, yb = y0, y1
        if glazed(x, -1) and not glazed(x, +1):
            ya = y0 + POST_IN + bw / 2
        elif glazed(x, +1) and not glazed(x, -1):
            yb = y1 - POST_IN - bw / 2
        else:
            ya, yb = y0 + POST_IN + bw / 2, y1 - POST_IN - bw / 2
        v.box("RoofBeam", "Steel", x - bw / 2, x + bw / 2, ya, yb, bb, bt)
    # glazed runs: consecutive x-range where a side is glazed
    runs = []
    for x0, x1, s in SEGMENTS:
        a, b = max(x0, x_start), min(x1, x_house_end)
        if b > a + EPS:
            runs.append((a, b, s))
    for s in (-1, +1):
        sides = [(a, b, s) for a, b, ss in runs if ss == s]
        if x_end > x_house_end + EPS:
            sides.append((x_house_end, x_end, s))
        # merge runs that touch
        merged = []
        for a, b, ss in sorted(sides):
            if merged and abs(merged[-1][1] - a) < EPS:
                merged[-1] = (merged[-1][0], b)
            else:
                merged.append((a, b))
        for a, b in merged:
            y = y0 + POST_IN if s < 0 else y1 - POST_IN
            posts_in = [x for x in xs if a - EPS <= x <= b + EPS]
            # edge beam along the run over its posts (mine: the glazing head needs a beam)
            ea = posts_in[0] - bw / 2 if abs(posts_in[0] - a) < 0.2 else a
            eb = posts_in[-1] + bw / 2 if abs(posts_in[-1] - b) < 0.2 else b
            for pa, pb in zip([ea] + posts_in[1:-1], posts_in[1:-1] + [eb]):
                # one piece per post bay so the sloped roof (C) can step at each post
                xm = (pa + pb) / 2
                bt = beam_top(xm)
                if callable(roof_top):
                    v.prism_y("EdgeBeam", "Steel", y - bw / 2, y + bw / 2,
                              [(pa, beam_top(pa) - bd), (pb, beam_top(pb) - bd), (pb, beam_top(pb)), (pa, beam_top(pa))])
                else:
                    v.box("EdgeBeam", "Steel", pa, pb, y - bw / 2, y + bw / 2, bt - bd, bt)
            # storefront bays between transverse beam faces (no glass over the terrace)
            for pa, pb in zip(posts_in, posts_in[1:]):
                if pa >= x_house_end - EPS:
                    continue
                ga, gb = pa + bw / 2, min(pb - bw / 2, x_house_end)
                v.storefront("Glz", "x", ga, gb, y, floor(ga), beam_top(ga) - bd, (False, pb < x_house_end + EPS))
            # run ends beyond the first / last post (1 m glass bays to the closed wall end)
            if a < posts_in[0] - bw / 2 - 0.05 and a < x_house_end:
                v.storefront("Glz", "x", a, posts_in[0] - bw / 2, y, floor(a), beam_top(a) - bd, (True, False), 1)
            if b > posts_in[-1] + bw / 2 + 0.05 and posts_in[-1] < x_house_end - EPS:
                gb = min(b, x_house_end)
                if gb > posts_in[-1] + bw / 2 + 0.05:
                    v.storefront("Glz", "x", posts_in[-1] + bw / 2, gb, y, floor(gb), beam_top(gb) - bd, (False, True), 1)
    # closed walls: floor to roof, beam pockets, one strip window and one door per segment
    for x0, x1, s in SEGMENTS:
        a, b = max(x0, x_start), min(x1, x_house_end)
        if b <= a + EPS:
            continue
        ya, yb = (y1 - T_CLOSED, y1) if s < 0 else (y0, y0 + T_CLOSED)
        ops = [(x - bw / 2, x + bw / 2, beam_top(x) - bd, 99.0) for x in xs if a - EPS < x < b + EPS]
        bays = [(p, q) for p, q in zip([a] + [x for x in xs if a < x < b], [x for x in xs if a < x < b] + [b])]
        mid = max(bays, key=lambda pq: pq[1] - pq[0])
        wx0, wx1 = mid[0] + bw / 2 + 0.2, mid[1] - bw / 2 - 0.2
        zf = floor((wx0 + wx1) / 2)
        ops.append((wx0, wx1, zf + WIN_STRIP[0], zf + WIN_STRIP[1]))
        last = bays[-1]
        dx0 = last[1] - bw / 2 - 0.3 - DOOR_W
        if dx0 > last[0] + bw / 2 + 0.3 and zg(dx0) <= floor(dx0) + 0.02 and (last is not mid):
            ops.append((dx0, dx0 + DOOR_W, floor(dx0), floor(dx0) + DOOR_H))
        sub = "Concrete" if closed_concrete else "Steel"
        fam = "ClosedWall" if closed_concrete else "ClosedPanel"
        v.wall_x(fam, sub, a, b, ya, yb, floor, under, ops, breaks=[x + bw / 2 for x in xs] + [x - bw / 2 for x in xs])
    # roof slab, insulation, parapet or fascia
    if callable(roof_top):
        v.slab_x("RoofSlab", "Roof", x_start, x_end, y0, y1, under, top)
        v.slab_x("RoofIns", "Roof", x_start, x_end, y0, y1, top, lambda x: top(x) + INS_MIN)
        for ya, yb in ((y0 - FASCIA, y0), (y1, y1 + FASCIA)):
            v.slab_x("Fascia", "Roof", x_start, x_end, ya, yb, under, lambda x: top(x) + INS_MIN + 0.05)
        v.box("Fascia", "Roof", x_end, x_end + FASCIA, y0 - FASCIA, y1 + FASCIA, under(x_end), top(x_end) + INS_MIN + 0.05)
    else:
        rt = roof_top
        v.box("RoofSlab", "Roof", x_start, x_end, y0, y1, rt - SLAB_ROOF, rt)
        v.prism_x("RoofIns", "Roof", x_start, x_end,
                  [(y0 + PARAPET_T, rt), (y1 - PARAPET_T, rt), (y1 - PARAPET_T, rt + INS_MIN + INS_SLOPE * (y1 - y0 - 2 * PARAPET_T)),
                   (y0 + PARAPET_T, rt + INS_MIN)])
        v.box("Parapet", "Roof", x_start, x_end, y0, y0 + PARAPET_T, rt, rt + PARAPET_H)
        v.box("Parapet", "Roof", x_start, x_end, y1 - PARAPET_T, y1, rt, rt + PARAPET_H)
        v.box("Parapet", "Roof", x_end - PARAPET_T, x_end, y0 + PARAPET_T, y1 - PARAPET_T, rt, rt + PARAPET_H)
    return xs


def terrace_balustrade(v, x0, x1, z_top):
    """19 mm glass 1.10 high on the three open edges of the far-end terrace (AHCD 3-15)."""
    y0, y1 = BAR_Y
    v.balustrade("Balustrade", x0, x1 - BALU_T, y0, y0 + BALU_T, z_top)
    v.balustrade("Balustrade", x0, x1 - BALU_T, y1 - BALU_T, y1, z_top)
    v.balustrade("Balustrade", x1 - BALU_T, x1, y0, y1, z_top)
    check(z_top - zg(x1) > 0.6, f"{v.L} terrace edge {z_top - zg(x1):.2f} m above ground at x = {x1} (balustrade needed > 0.6)")


# ------------------------------------------------------------------
# VARIATION A: THE BRIDGE (concept 3)


def build_A():
    v = Var("A")
    y0, y1 = BAR_Y
    F = A_FLOOR
    gw, gd = GIRDER
    g_top, g_bot = F - SLAB_G, F - SLAB_G - gd          # +0.70, 0.00
    roof_top = F + CLEAR_H + BEAM[1] + SLAB_ROOF        # +4.73
    check(abs(roof_top - 4.73) < 1e-6, "A roof slab top +4.73 (R-32)")
    pavilion(v)
    # rear wall at x = 11 (250): pavilion part to the bar roof underside (y 9..13),
    # to the pavilion roof underside (13..15), abutment wing y 7..9 to the slab top.
    xw0, xw1 = PAV_X[1] - T_PAV, PAV_X[1]
    z_under = lambda x: zg(x) - FOOT_DEPTH
    door_y = (9.4, 9.4 + DOOR_W)                        # door into the bar, beside the entry stair (mine)
    pockets = [(gy - gw / 2, gy + gw / 2, g_bot, g_top) for gy in GIRDER_Y]
    v.founded_wall_y("Abutment", xw0, xw1, y0, PAV_Y[0], F, z_under, [pockets[0]])
    v.founded_wall_y("PavRear", xw0, xw1, PAV_Y[0], y1, roof_top - SLAB_ROOF, z_under,
                     [(door_y[0], door_y[1], PAV_FLOOR, PAV_FLOOR + DOOR_H), pockets[1]])
    v.founded_wall_y("PavRearN", xw0, xw1, y1, PAV_Y[1], PAV_ROOF_TOP - SLAB_ROOF, z_under)
    v.box("PavParapet", "Roof", xw0, xw1, y1, PAV_Y[1], PAV_ROOF_TOP - SLAB_ROOF, PAV_ROOF_TOP + PARAPET_H)
    v.hole(xw0, xw1, y0, PAV_Y[0])
    # entry stair: five risers just inside the bar on a concrete pier (mine: the pier
    # replaces ground that is 0.3 m below the pavilion floor there)
    n_r = int(round((F - PAV_FLOOR) / 0.15))
    check(n_r == 5, "A entry stair five risers of 150 (R-23)")
    sx0 = PAV_X[1]
    sx1 = sx0 + GOING * (n_r - 1)
    sy = (door_y[0] - 0.15, door_y[0] - 0.15 + STAIR_W)
    v.box("EntryPier", "Concrete", sx0, sx1, sy[0], sy[1], zg(sx1) - FOOT_DEPTH, PAV_FLOOR)
    v.hole(sx0, sx1, sy[0], sy[1])
    v.stair_x("EntryStair", sx1, -1, sy[0], sy[1], F, PAV_FLOOR, n_r, PAV_FLOOR)
    # columns on pads with base and cap plates
    for x in (23.0, 35.0, 47.0):
        for gy in GIRDER_Y:
            zu = zg(x) - FOOT_DEPTH
            v.box("Pad", "Footings", x - PAD_W / 2, x + PAD_W / 2, gy - PAD_W / 2, gy + PAD_W / 2, zu, zu + PAD_T)
            v.box("BasePlate", "Steel", x - PLATE[0] / 2, x + PLATE[0] / 2, gy - PLATE[0] / 2, gy + PLATE[0] / 2,
                  zu + PAD_T, zu + PAD_T + PLATE[1])
            v.box("Column", "Steel", x - COL / 2, x + COL / 2, gy - COL / 2, gy + COL / 2,
                  zu + PAD_T + PLATE[1], g_bot - PLATE[1])
            v.box("CapPlate", "Steel", x - PLATE[0] / 2, x + PLATE[0] / 2, gy - PLATE[0] / 2, gy + PLATE[0] / 2,
                  g_bot - PLATE[1], g_bot)
            v.hole(x - COL / 2, x + COL / 2, gy - COL / 2, gy + COL / 2)
            check(zu + PAD_T < zg(x) - SKIN_T, f"A pad top at x = {x} below the skin")
    # lower box x 53..65: walls 250 to the girder underside, stepped footings on the long walls
    bx0, bx1 = 53.0, 65.0
    t = T_PAV
    box_z_under = lambda x: zg(x) - FOOT_DEPTH
    win = [(57.0, 58.2, A_BOX_FLOOR + 0.9, A_BOX_FLOOR + 2.1), (61.0, 62.2, A_BOX_FLOOR + 0.9, A_BOX_FLOOR + 2.1)]
    v.founded_wall_x("BoxWallS", bx0, bx1, y0, y0 + t, g_bot, box_z_under, win, max_run=3.0)
    v.founded_wall_x("BoxWallN", bx0, bx1, y1 - t, y1, g_bot, box_z_under, max_run=3.0)
    # upstands beside the girders closing the box under the slab edge
    for ya, yb in ((y0, GIRDER_Y[0] - gw / 2), (GIRDER_Y[1] + gw / 2, y1)):
        v.box("BoxUpstand", "Concrete", bx0, bx1, ya, yb, g_bot, g_top)
    door = (9.5, 9.5 + ENTRY_W, A_BOX_FLOOR, A_BOX_FLOOR + DOOR_H)
    v.founded_wall_y("BoxWallW", bx0, bx0 + t, y0 + t, y1 - t, g_bot, box_z_under)
    v.founded_wall_y("BoxWallE", bx1 - t, bx1, y0 + t, y1 - t, g_bot, box_z_under, [door])
    for xa, xb in ((bx0, bx0 + t), (bx1 - t, bx1)):
        v.box("BoxCrossUp", "Concrete", xa, xb, GIRDER_Y[0] + gw / 2, GIRDER_Y[1] - gw / 2, g_bot, g_top)
    v.hole(bx0, bx1, y0, y1)
    v.floor_suspended("BoxFloor", bx0 + t, bx1 - t, y0 + t, y1 - t, A_BOX_FLOOR)
    # girders: pocketed 250 into the x = 11 wall, over the cap plates and the box walls, cantilever to 71
    for k, gy in enumerate(GIRDER_Y):
        v.box("Girder", "Steel", xw0, BAR_END["A"], gy - gw / 2, gy + gw / 2, g_bot, g_top)
    check(g_bot - zg(11.0) >= 0.30 - EPS, f"A girder clearance at x = 11: {g_bot - zg(11.0):.2f} m (>= 0.30)")
    # transverse floor beams IPE 300 between the girders, tops flush with the girder tops
    fbw, fbd = FBEAM
    fx = [PAV_X[1] + fbw / 2] + [x for x in range(15, 68, 4)] + [BAR_END["A"] - fbw / 2]
    for x in fx:
        v.box("FloorBeam", "Steel", x - fbw / 2, x + fbw / 2, GIRDER_Y[0] + gw / 2, GIRDER_Y[1] - gw / 2, g_top - fbd, g_top)
    # bridge slab with the entry stair well and the dogleg void
    void = (53.4, 53.4 + 12 * GOING + GOING + LANDING, 9.4, 12.0)   # upper flight, one-tread lead, landing (AHCD 3-10)
    v.floor_suspended("BridgeSlab", PAV_X[1], BAR_END["A"], y0, y1, F,
                      [(sx0, sx1, sy[0], sy[1]), void], thick=SLAB_G)      # 200 on beams (3.2)
    # superstructure
    xs = bar_superstructure(v, F, ROOF_END["A"], roof_top, closed_concrete=False)
    terrace_balustrade(v, BAR_END["A"] - 6.0, BAR_END["A"], F)
    # cores (3.1): 1 entry (store), 2 kitchen, 3 study, 4 master ensuite, 5 box bathroom
    v.core("Core1", 11.2, 15.2, 10.6, y1 - T_CLOSED, F, "y0", store=True)
    v.core("Core2", 40.0, 43.0, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, F, "y1")
    v.core("Core3", 44.2, 47.2, y1 - T_CLOSED - 2.4, y1 - T_CLOSED, F, "y0")
    v.core("Core4", 61.5, 64.5, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, F, "y1")
    v.core("Core5", 61.75, 64.75, y0 + t, y0 + t + 2.4, A_BOX_FLOOR, "y1")
    roof_under = roof_top - SLAB_ROOF
    v.partition_x("Part", 48.333, y0 + MULL[1] / 2 + POST_IN, y1 - T_CLOSED, F, roof_under)   # study / guest
    v.partition_x("Part", 59.0 - 0.5, y0 + T_CLOSED, y1 - MULL[1] / 2 - POST_IN, F, roof_under)  # stair hall / master
    v.partition_x("BoxPart", 56.9, y0 + t, void[2], A_BOX_FLOOR, g_top)                       # hall / bedroom 2
    v.partition_x("BoxPart", 60.0, y0 + t, y1 - t, A_BOX_FLOOR, g_top)                        # bedroom 2 / 3
    # dogleg stair: upper flight (y 10.8..12.0) from the floor edge x = 53.4 down to the landing,
    # lower flight (y 9.4..10.6) back from the landing to the box floor
    rise = F - A_BOX_FLOOR
    n_tot = 26
    riser = rise / n_tot
    check(0.150 <= riser <= 0.165, f"A dogleg riser {riser * 1000:.1f} mm")
    z_land = F - 13 * riser
    x_up_top = void[0]
    x_up_bot = x_up_top + 12 * GOING                        # upper flight's arrival riser
    x_lo_top = x_up_bot + GOING                             # lower flight's top riser, one tread nearer the landing
    check(void[1] - x_lo_top >= LANDING - EPS, f"A landing depth {void[1] - x_lo_top:.2f} m >= 1.2")
    lane_up, lane_lo = (10.8, 12.0), (9.4, 10.6)
    v.stair_x("DoglegUp", x_up_top, +1, lane_up[0], lane_up[1], F, z_land, 13, A_BOX_FLOOR)
    v.stair_x("DoglegLo", x_lo_top, -1, lane_lo[0], lane_lo[1], z_land, A_BOX_FLOOR, 13, A_BOX_FLOOR)
    v.box("Landing", "Stairs", x_up_bot, void[1], void[2], void[3], A_BOX_FLOOR, z_land)
    x_lo_bot = x_lo_top - 12 * GOING
    check(x_lo_bot > bx0 + t + 0.3, f"A lower flight lands at x = {x_lo_bot:.2f}, clear of the box wall")
    # guards 1.07: around the void on the bridge floor, flight outer sides, well plate between the flights
    gt = BALU_T
    v.guard("VoidGuard", void[0] - gt, void[0], void[2] - gt, void[3] + gt, F)
    v.guard("VoidGuard", void[0], void[1], void[2] - gt, void[2], F)
    v.guard("VoidGuard", void[0], void[1], void[3], void[3] + gt, F)
    v.guard("VoidGuard", void[1], void[1] + gt, void[2] - gt, lane_up[0], F)
    v.flight_guard("FlightGuard", x_up_top, x_up_bot, lane_up[1] - gt, lane_up[1], F, z_land, z_land)
    v.flight_guard("FlightGuard", x_lo_top, x_lo_bot, lane_lo[0], lane_lo[0] + gt, z_land, A_BOX_FLOOR, A_BOX_FLOOR)
    v.prism_y("WellGuard", "Glazing", 10.7 - gt / 2, 10.7 + gt / 2,
              [(x_up_top, A_BOX_FLOOR), (void[1], A_BOX_FLOOR), (void[1], F + GUARD_H), (x_up_top, F + GUARD_H - 0.0)])
    v.terrain()
    return v


# ------------------------------------------------------------------
# VARIATION B: THE CUT (concept 4)


def build_B():
    v = Var("B")
    y0, y1 = BAR_Y
    F = B_FLOOR
    roof_top = F + CLEAR_H + BEAM[1] + SLAB_ROOF        # +1.23
    check(abs(roof_top - 1.23) < 1e-6, "B roof slab top +1.23 (R-40)")
    cw = COURT_W["B"]
    yr0, yr1 = y0 - cw, y1 + cw                          # retaining wall courtyard faces y = 5, 15
    x_cut1 = 46.0
    base_under = -3.55
    pav_court = F - PAVING                               # courtyard paving top -2.75
    pavilion(v)
    # end retaining wall = pavilion rear wall: one 300 wall at x = 11 from the base to the pavilion roof
    xw0, xw1 = PAV_X[1] - T_RET, PAV_X[1]
    H_end = PAV_FLOOR - base_under
    base_w = 0.6 * H_end
    v.box("EndWallBase", "Footings", xw0 - base_w + 0.15 * H_end, xw0 + 0.15 * H_end, yr0 - T_RET, yr1 + T_RET,
          base_under, base_under + LBASE_T)
    door_y = (11.6, 11.6 + DOOR_W)
    pav_under = PAV_ROOF_TOP - SLAB_ROOF
    v.wall_y("EndWall", "Concrete", xw0, xw1, yr0 - T_RET, y0, base_under + LBASE_T, zg(xw1))
    v.wall_y("EndWall", "Concrete", xw0, xw1, y0, PAV_Y[0], base_under + LBASE_T, pav_under)
    v.wall_y("EndWall", "Concrete", xw0, xw1, PAV_Y[0], y1, base_under + LBASE_T, pav_under,
             [(door_y[0], door_y[1], PAV_FLOOR, PAV_FLOOR + DOOR_H)])
    v.wall_y("EndWall", "Concrete", xw0, xw1, y1, PAV_Y[1], base_under + LBASE_T, pav_under)
    v.wall_y("EndWall", "Concrete", xw0, xw1, PAV_Y[1], yr1 + T_RET, base_under + LBASE_T, zg(xw1))
    v.box("PavParapet", "Roof", xw0, xw1, y1, PAV_Y[1], pav_under, PAV_ROOF_TOP + PARAPET_H)
    # side retaining walls y = 5 and 15 (stems 300 outside the courtyard face), tops on z(x), L bases
    for yc, sgn in ((yr0, -1), (yr1, +1)):
        s0, s1 = (yc - T_RET, yc) if sgn < 0 else (yc, yc + T_RET)
        H = zg(PAV_X[1]) - base_under
        bw_ = 0.6 * H
        toe = 0.15 * H
        b0, b1 = (yc - bw_ + toe, yc + toe) if sgn < 0 else (yc - toe, yc - toe + bw_)
        v.box("RetBase", "Footings", xw1, x_cut1, b0, b1, base_under, base_under + LBASE_T)
        v.wall_x("RetStem", "Concrete", xw1, x_cut1, s0, s1, base_under + LBASE_T, zg)
        check(zg(xw1) - pav_court <= 2.75 + EPS, f"B side wall retains {zg(xw1) - pav_court:.2f} m at x = 11 (<= 2.75, engineered L-wall, deviation ledger)")
    # courtyard paving 150 between the glass line and the stems, top -2.75
    for ya, yb in ((yr0, y0), (y1, yr1)):
        v.box("CourtSlab", "Slabs", xw1, x_cut1, ya, yb, pav_court - PAVING, pav_court)
    v.hole(xw0, x_cut1, yr0 - T_RET, yr1 + T_RET)
    # foundation walls 250 under both long faces: slab on ground 11..46, plinth 46..70 on stepped footings
    x_end = ROOF_END["B"]
    z_under_cut = lambda x: min(zg(x), pav_court) - FOOT_DEPTH
    for ya, yb in ((y0, y0 + T_PAV), (y1 - T_PAV, y1)):
        v.founded_wall_x("FndWall", xw1, x_cut1, ya, yb, F - SLAB_G, z_under_cut)
        v.founded_wall_x("Plinth", x_cut1, x_end, ya, yb, F - SLAB_S, lambda x: zg(x) - FOOT_DEPTH)
        v.hole(x_cut1, x_end, ya, yb)
    v.founded_wall_y("PlinthEnd", x_end - T_PAV, x_end, y0 + T_PAV, y1 - T_PAV, F - SLAB_S, lambda x: zg(x) - FOOT_DEPTH)
    v.hole(x_end - T_PAV, x_end, y0, y1)
    v.floor_on_ground("Floor", xw1, x_cut1, y0, y1, F)
    v.floor_suspended("Floor", x_cut1, x_end, y0, y1, F)
    x_free = x_at_ground(F - SLAB_S - 0.01)
    v.hole(x_cut1, x_free, y0, y1)
    check(F - pav_court >= 0.15 - EPS, "B floor 150 above the courtyard paving")
    # high bay over the entry stair (mine, see version_notes): pavilion roof level over x 11..15.28,
    # transverse concrete wall closing the step, corbel carrying the low roof's uphill edge
    bw = BEAM[0]
    xs_all = post_lines(x_end)
    x_step0 = xs_all[1] + bw / 2                          # 15.08
    x_step1 = x_step0 + T_CLOSED                         # 15.28
    high_top = PAV_ROOF_TOP
    v.wall_y("StepWall", "Concrete", x_step0, x_step1, y0, y1, F, high_top - SLAB_ROOF,
             [(9.0, 9.0 + DOOR_W, F, F + DOOR_H), (y0 + POST_IN - bw / 2, y0 + POST_IN + bw / 2, high_top - SLAB_ROOF - BEAM[1], high_top - SLAB_ROOF)])
    v.box("Corbel", "Concrete", x_step1, x_step1 + 0.2, y0, y1, roof_top - SLAB_ROOF - 0.2, roof_top - SLAB_ROOF)
    # high bay: post at 11.1, edge beam, transverse beam at 11.1, closed panel y_max, storefront y_min, roof, parapet
    hb_under = high_top - SLAB_ROOF
    bb = hb_under - BEAM[1]
    xp = xs_all[0]
    v.post(xp, y0 + POST_IN, F, bb)
    v.post(xs_all[1], y0 + POST_IN, F, bb)
    v.box("RoofBeam", "Steel", xp - bw / 2, xp + bw / 2, y0 + POST_IN + bw / 2, y1, bb, hb_under)
    v.box("RoofBeam", "Steel", xs_all[1] - bw / 2, xs_all[1] + bw / 2, y0 + POST_IN + bw / 2, y1, bb, hb_under)
    v.box("EdgeBeam", "Steel", xp - bw / 2, x_step0, y0 + POST_IN - bw / 2, y0 + POST_IN + bw / 2, bb, hb_under)
    v.storefront("Glz", "x", xp + bw / 2, xs_all[1] - bw / 2, y0 + POST_IN, F, bb, (False, False))
    v.wall_x("ClosedWall", "Concrete", xw1, x_step0, y1 - T_CLOSED, y1, F, hb_under,
             [(xp - bw / 2, xp + bw / 2, bb, 99.0), (xs_all[1] - bw / 2, xs_all[1] + bw / 2, bb, 99.0)])
    v.box("RoofSlab", "Roof", xw1, x_step1, y0, y1, hb_under, high_top)
    v.prism_x("RoofIns", "Roof", xw1, x_step1,
              [(y0 + PARAPET_T, high_top), (y1 - PARAPET_T, high_top), (y1 - PARAPET_T, high_top + INS_MIN + INS_SLOPE * (y1 - y0 - 2 * PARAPET_T)),
               (y0 + PARAPET_T, high_top + INS_MIN)])
    v.box("Parapet", "Roof", xw1, x_step1, y0, y0 + PARAPET_T, high_top, high_top + PARAPET_H)
    v.box("Parapet", "Roof", xw1, x_step1, y1 - PARAPET_T, y1, high_top, high_top + PARAPET_H)
    v.box("Parapet", "Roof", x_step1 - PARAPET_T, x_step1, y0 + PARAPET_T, y1 - PARAPET_T, high_top, high_top + PARAPET_H)
    v.box("PavParapet", "Roof", xw0, xw1, y0, PAV_Y[0], pav_under, PAV_ROOF_TOP + PARAPET_H)
    v.box("PavRoof", "Roof", PAV_X[0], xw0, PAV_Y[0], PAV_Y[1], pav_under, PAV_ROOF_TOP)
    # low bar from the step wall on: superstructure with the roof at +1.23
    bar_superstructure(v, F, x_end, roof_top, closed_concrete=True, x_start=x_step1)
    terrace_balustrade(v, BAR_END["B"], x_end, F)
    # entry stair: landing 1.2 inside the door at +0.15, 17 risers down along the closed WNW wall
    ly0, ly1 = y1 - T_CLOSED - STAIR_W, y1 - T_CLOSED
    lx0, lx1 = xw1, xw1 + LANDING
    v.box("Landing", "Stairs", lx0, lx1, ly0, ly1, F, PAV_FLOOR)
    n_r = 17
    x_bot, riser = v.stair_x("EntryStair", lx1, +1, ly0, ly1, PAV_FLOOR, F, n_r, F)
    check(abs(riser - 0.1618) < 0.001, f"B stair riser {riser * 1000:.1f} mm (R-37: 161.8)")
    v.guard("LandingGuard", lx0, lx1, ly0 - BALU_T, ly0, PAV_FLOOR)
    v.flight_guard("FlightGuard", lx1, x_bot, ly0 - BALU_T, ly0, PAV_FLOOR, F, F)
    # headroom over the flight under the low roof beam at x = 15: nosing line vs beam bottom
    x_chk = xs_all[1]
    z_nose = PAV_FLOOR - riser * (x_chk - lx1) / GOING
    check(bb - z_nose >= 2.1, f"B headroom at x = 15 under the high beam {bb - z_nose:.2f} m")
    # cores and partitions (4.1)
    v.core("Core1", 11.0, 15.0, 9.2, ly0, F, "y0", store=True)
    v.core("Core2", 39.0, 42.0, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, F, "y1")
    v.core("Core3", 45.0, 48.0, y1 - T_CLOSED - 2.4, y1 - T_CLOSED, F, "y0")
    v.core("Core4", 63.0, 66.0 - T_CLOSED, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, F, "y1")
    ru = roof_top - SLAB_ROOF
    v.partition_x("Part", 48.0, y0 + T_CLOSED, y1 - MULL[1] / 2 - POST_IN, F, ru)   # study / bedroom 2
    v.partition_x("Part", 54.0, y0 + T_CLOSED, y1 - MULL[1] / 2 - POST_IN, F, ru)   # bedroom 2 / 3
    v.partition_x("Part", 60.0, y0 + T_CLOSED, y1 - T_CLOSED, F, ru)                 # bedroom 3 / master
    v.terrain()
    return v


# ------------------------------------------------------------------
# VARIATION C: THE STEPS (concept 5)


def build_C():
    v = Var("C")
    y0, y1 = BAR_Y
    cw = COURT_W["C"]
    top, under = c_roof_top, c_roof_under
    pavilion(v, sloped=c_roof_top)
    # ridge wall at x = 11 (300): step retaining wall from -1.70 (R-43) up to the roof, y 5.2..15
    xw0, xw1 = PAV_X[1] - T_RET, PAV_X[1]
    L1 = C_LEVELS[0]
    door_y = (11.6, 11.6 + DOOR_W)
    wall_bot = L1[2] - 0.50                                # -1.70 (R-43)
    v.footing_y("RidgeFtg", (xw0 + xw1) / 2, y0 - cw - T_RET - (FOOT_W - T_RET) / 2, PAV_Y[1] + (FOOT_W - T_RET) / 2, lambda x: wall_bot - FOOT_T)
    v.wall_y("RidgeWall", "Concrete", xw0, xw1, y0 - cw - T_RET, y0, wall_bot, zg(xw1))
    v.wall_y("RidgeWall", "Concrete", xw0, xw1, y0, PAV_Y[1], wall_bot, under(xw0),
             [(door_y[0], door_y[1], PAV_FLOOR, PAV_FLOOR + DOOR_H)])
    v.hole(xw0, xw1, y0 - cw - T_RET, PAV_Y[1])
    # pavilion roof R1 over y 9..15 as a sloped prism (its downhill edge on the ridge wall)
    v.slab_x("PavRoof", "Roof", PAV_X[0], xw1, PAV_Y[0], PAV_Y[1], under, top)
    v.slab_x("PavRoofIns", "Roof", PAV_X[0], xw1, PAV_Y[0], PAV_Y[1], top, lambda x: top(x) + INS_MIN)
    for ya, yb in ((PAV_Y[0] - FASCIA, PAV_Y[0]), (PAV_Y[1], PAV_Y[1] + FASCIA)):
        v.slab_x("Fascia", "Roof", PAV_X[0], xw1, ya, yb, under, lambda x: top(x) + INS_MIN + 0.05)
    v.box("Fascia", "Roof", PAV_X[0] - FASCIA, PAV_X[0], PAV_Y[0] - FASCIA, PAV_Y[1] + FASCIA, under(PAV_X[0]), top(PAV_X[0]) + INS_MIN + 0.05)
    # levels
    x_end = ROOF_END["C"]

    def floor_at(x):
        for x0, x1, z in C_LEVELS:
            if x < x1 - EPS:
                return z
        return C_LEVELS[-1][2]
    for i, (x0, x1, F) in enumerate(C_LEVELS):
        xs_ = C_SPLIT[i]
        pav_top = F - PAVING
        x_next = x1 if i == 2 else x1
        # step retaining wall at the uphill end (29, 47): full width plus the courtyard returns,
        # top under the upper level's slab; at x = 11 the ridge wall does this
        if i > 0:
            Fu = C_LEVELS[i - 1][2]
            sw0, sw1 = x0 - T_RET, x0
            sb = F - 0.50
            s_prev = open_side(x0 - 0.5)                   # trench side of the level above at its end
            s_here = open_side(x0 + 0.5)
            ya = y0 - cw - T_RET if (s_prev < 0 or s_here < 0) else y0
            yb = y1 + cw + T_RET if (s_prev > 0 or s_here > 0) else y1
            v.footing_y("StepFtg", (sw0 + sw1) / 2, ya - (FOOT_W - T_RET) / 2, yb + (FOOT_W - T_RET) / 2, lambda x, sb=sb: sb - FOOT_T)
            up_under = Fu - (SLAB_S if C_SPLIT[i - 1] < x0 else SLAB_G)
            if ya < y0:
                v.wall_y("StepWall", "Concrete", sw0, sw1, ya, y0, sb, min(zg(sw0), up_under) if s_prev < 0 else zg(sw0))
            v.wall_y("StepWall", "Concrete", sw0, sw1, y0, y1, sb, up_under)
            if yb > y1:
                v.wall_y("StepWall", "Concrete", sw0, sw1, y1, yb, sb, min(zg(sw0), up_under) if s_prev > 0 else zg(sw0))
            v.hole(sw0, sw1, ya, yb)
        # trench (sunken strip) on the glazed side where the level is cut: paving 150 below the floor,
        # side retaining wall 300 on a 1.5 x 0.4 base, running out where the ground meets the paving
        for seg0, seg1, s in SEGMENTS:
            a, b = max(seg0, x0), min(seg1, x1)
            if b <= a + EPS:
                continue
            x_out = min(b, x_at_ground(pav_top))
            if x_out <= a + 0.3:
                continue
            if s < 0:
                py0, py1 = y0 - cw, y0
                st0, st1 = py0 - T_RET, py0
                bb0, bb1 = st0 - 1.5 + 0.15 * 1.5 + T_RET, st0 + 0.15 * 1.5 + T_RET
            else:
                py0, py1 = y1, y1 + cw
                st0, st1 = py1, py1 + T_RET
                bb0, bb1 = st1 - 0.15 * 1.5 - T_RET, st1 - 0.15 * 1.5 - T_RET + 1.5
            base_top = pav_top - PAVING - LBASE_T
            v.box("SideBase", "Footings", a, x_out, bb0, bb1, base_top - LBASE_T + LBASE_T - LBASE_T, base_top)
            v.wall_x("SideStem", "Concrete", a, x_out, st0, st1, base_top, zg)
            v.box("StripPaving", "Slabs", a, x_out, py0, py1, pav_top - PAVING, pav_top)
            v.hole(a, x_out, min(st0, y0), max(st1, y1))
            check(zg(a) - pav_top <= 1.5 + EPS, f"C side wall retains {zg(a) - pav_top:.2f} m at x = {a} (<= 1.50 free-standing)")
        # foundation / plinth walls 250 under both long faces and across the downhill end
        z_under_cut = lambda x, pt=pav_top: min(zg(x), pt) - FOOT_DEPTH
        z_under = lambda x: zg(x) - FOOT_DEPTH
        slab_under = lambda x, F=F, xs_=xs_: F - (SLAB_G if x < xs_ - EPS else SLAB_S)
        xa = x0 if i == 0 else x0
        xb = x_end if i == 2 else x1 - T_RET
        for ya, yb in ((y0, y0 + T_PAV), (y1 - T_PAV, y1)):
            v.founded_wall_x("FndWall", xa, xb, ya, yb, slab_under, lambda x, zc=z_under_cut: min(zc(x), zg(x) - FOOT_DEPTH),
                             breaks=[xs_, x_at_ground(pav_top)])
            v.hole(xa, xb, ya, yb)
        if i == 2:
            v.founded_wall_y("PlinthEnd", x_end - T_PAV, x_end, y0 + T_PAV, y1 - T_PAV, F - SLAB_S, z_under)
            v.hole(x_end - T_PAV, x_end, y0, y1)
        # floor slabs (R-47) and the hole under them where the ground would cut the structure
        v.floor_on_ground("Floor", xa, xs_, y0, y1, F)
        v.floor_suspended("Floor", xs_, xb, y0, y1, F)
        x_free = x_at_ground(min(F - SLAB_G - GRAVEL, F - SLAB_S) - 0.01)
        v.hole(xa, max(x_free, xs_), y0, y1)
        check(F - pav_top >= 0.15 - EPS, f"C L{i + 1} floor 150 above its strip paving")
        check(under(x1) - F >= CLEAR_H - EPS, f"C L{i + 1} clear height at its downhill end x = {x1}: {under(x1) - F:.2f} m (>= 3.30, R-45)")
    # superstructure: the whole bar from x = 11 to 70 under the folded plane R2
    xs = bar_superstructure(v, floor_at, x_end, c_roof_top, closed_concrete=True)
    terrace_balustrade(v, BAR_END["C"], x_end, C_LEVELS[-1][2])
    # stairs: three straight flights of 9 x 150 along the closed side, solid to the lower floor
    for i, (x0, x1, F) in enumerate(C_LEVELS):
        Fu = PAV_FLOOR if i == 0 else C_LEVELS[i - 1][2]
        s = open_side(x0 + 0.5)
        if s < 0:
            sy0, sy1 = y1 - T_CLOSED - STAIR_W, y1 - T_CLOSED
        else:
            sy0, sy1 = y0 + T_CLOSED, y0 + T_CLOSED + STAIR_W
        x_bot, riser = v.stair_x(f"Stair{i + 1}", x0, +1, sy0, sy1, Fu, F, 9, F)
        check(abs(riser - 0.150) < 1e-6, f"C stair {i + 1} riser 150")
        gy = (sy0 - BALU_T, sy0) if s < 0 else (sy1, sy1 + BALU_T)
        v.flight_guard("FlightGuard", x0, x_bot, gy[0], gy[1], Fu, F, F)
        # headroom over the top nosing under the roof beam at the nearest post line
        xp = min(xs, key=lambda x: abs(x - x0))
        beam_bot = under(xp + BEAM[0] / 2) - BEAM[1]
        z_nose = Fu - riser * max(0.0, xp - x0) / GOING
        check(beam_bot - z_nose >= 2.1, f"C stair {i + 1} headroom under the beam at x = {xp}: {beam_bot - z_nose:.2f} m")
    # cores and partitions (5.1)
    v.core("Core1", 11.0, 14.0, 9.2, y1 - T_CLOSED - STAIR_W, C_LEVELS[0][2], "y0", store=True)
    v.core("Core2", 40.0, 43.0, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, C_LEVELS[1][2], "y1")
    v.core("Core3", 51.0, 54.0, y1 - T_CLOSED - 2.4, y1 - T_CLOSED, C_LEVELS[2][2], "y0")
    v.core("Core4", 60.0, 63.0, y0 + T_CLOSED, y0 + T_CLOSED + 2.4, C_LEVELS[2][2], "y1")
    F3 = C_LEVELS[2][2]
    v.partition_x("Part", 54.5, y0 + MULL[1] / 2 + POST_IN, y1 - T_CLOSED, F3, under(54.5))   # master / bedroom 2
    v.partition_x("Part", 60.0 - 0.5, y0 + MULL[1] / 2 + POST_IN, y1 - T_CLOSED, F3, under(59.5))  # bedroom 2 / 3
    v.partition_x("Part", 44.0 - 0.3, y0 + T_CLOSED, y1 - MULL[1] / 2 - POST_IN, C_LEVELS[1][2], under(43.7))  # dining / study
    v.terrain()
    return v


# ------------------------------------------------------------------
# BUILD

craftbot.clear_scene()
VARS = [build_A(), build_B(), build_C()]

# terrain checks (R-02, R-03)
for x, z in ((-6, 0.55), (0, 0.25), (5, 0.0), (26, -1.05), (50, -2.97), (100, -9.97)):
    check(abs(zg(x) - z) < 1e-9, f"z({x}) = {zg(x):.2f}")

n_mesh = len([o for o in bpy.data.objects if o.type == "MESH"])
per = {}
for o in bpy.data.objects:
    if o.type == "MESH":
        per[o.name[0]] = per.get(o.name[0], 0) + 1
print(f"Built experiment 15 v01: {n_mesh} elements " + ", ".join(f"{k}: {n}" for k, n in sorted(per.items())))
fails = [t for ok, t in CHECKS if not ok]
print(f"CHECKS: {len(CHECKS)} evaluated, {len(fails)} failed")
for t in fails:
    print("  FAIL", t)
