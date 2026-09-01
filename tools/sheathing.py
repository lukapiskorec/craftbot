"""Board sheathing on planar roof (or wall) facets, with the checks that
go with it.

Workflow (see experiments 11 and 13):

1. Describe every planar surface as a Facet: origin O on the rafter
   centre-plane, board direction U (parallel to the eave), outward
   normal N, `underside` = distance from O's plane to the sheathing
   underside (half the rafter depth) and `thick` = board thickness.
2. Build the outline loops of each facet TWICE as plane intersections
   (planes.isect): once with every roof plane offset to the underside,
   once offset to the top surface. Convert to facet (u, v) with
   Facet.uv(). Shared edges then match exactly between facets, and the
   two levels give mitred board ends at hips, valleys and ridges.
3. sheathe_facet() lays rows of boards from the eave up: joints only
   over rafters (`joint_points`), odd rows start with a half board, the
   last row is ripped rather than left as a sliver. Every board is a
   convex prism from an underside outline and a top outline whose
   vertices map corner to corner (make_board), so slanted ends become
   bevels and the overlap check stays exact.
4. drop_member() lowers hips / valleys that stand proud of the board
   plane; report_protrusions() lists every framing member whose corner
   still pokes through a sheathed area.

Provenance: Facet, drop_member, report_protrusions from Fable experiment
13; row layout with exact corner mapping (under_corner / uncross /
split_quad_u) from experiment 11, which superseded 13's square-end
fallback.
"""
import bpy
from mathutils import Matrix, Vector

import craftbot_lib as craftbot
from geometry2d import area, clip_u, line_isect, point_in_loops, scan_intervals, signed_area


class Facet:
    """One planar surface to be boarded.

    O : point on the rafter centre-plane (normally on the eave line)
    U : in-plane board direction (parallel to the eave)
    N : outward (upward) normal; V = N x U is up-slope, flipped so V.z >= 0
    underside : offset from the O plane to the board underside along N
    thick     : board thickness; top = underside + thick
    """

    def __init__(self, name, O, U, N, underside=0.0, thick=0.019):
        self.name = name
        self.O = Vector(O)
        self.N = Vector(N).normalized()
        U = Vector(U).normalized()
        V = self.N.cross(U).normalized()
        if V.z < 0:
            V, U = -V, -U
        self.U, self.V = U, V
        self.underside = underside
        self.thick = thick
        self.top = underside + thick

    def plane(self, offset=0.0):
        """(n, d) plane parallel to the facet, shifted `offset` along N."""
        return (self.N.copy(), self.N.dot(self.O) + offset)

    def uv(self, P):
        d = Vector(P) - self.O
        return (d.dot(self.U), d.dot(self.V))

    def xyz(self, u, v, h):
        return self.O + u * self.U + v * self.V + h * self.N


# ------------------------------------------------------------------
# ROW LAYOUT (2D, in facet u/v; v = 0 at the eave, rows go up-slope)


def scan_cross(loops, v_s):
    """Crossings of the scanline v = v_s with the outline edges, sorted
    by u: (u, loop index, edge index)."""
    out = []
    for li, loop in enumerate(loops):
        n = len(loop)
        for i in range(n):
            u0, v0 = loop[i]
            u1, v1 = loop[(i + 1) % n]
            if (v0 <= v_s < v1) or (v1 <= v_s < v0):
                t = (v_s - v0) / (v1 - v0)
                out.append((u0 + t * (u1 - u0), li, i))
    out.sort(key=lambda c: c[0])
    return out


def board_cuts(a, b, joints, row, board_len, min_board, stagger):
    """Joint positions (u) for a board run from a to b: joints land on
    the rafter positions `joints`, odd rows start with a `stagger`
    length so joints alternate between neighbouring rows, no board
    shorter than `min_board`."""
    cuts = []
    pos = a
    allowed = board_len if row % 2 == 0 else stagger
    while b - pos > allowed + 1e-6:
        cands = [j for j in joints if pos + min_board <= j <= pos + allowed]
        if not cands:
            break
        c = max(cands)
        if b - c < min_board:
            break
        cuts.append(c)
        pos = c
        allowed = board_len
    return cuts


def split_pair(under, top, joints, row, board_len, min_board, stagger):
    """Cut an (underside, top) outline pair at the same joint positions."""
    us = [p[0] for p in top]
    cuts = board_cuts(min(us), max(us), joints, row, board_len, min_board, stagger)
    out = []
    rest_u, rest_t = under, top
    for c in cuts:
        out.append((clip_u(rest_u, c, True), clip_u(rest_t, c, True)))
        rest_u, rest_t = clip_u(rest_u, c, False), clip_u(rest_t, c, False)
    out.append((rest_u, rest_t))
    return out


def horiz_edges(loops_t, loops_u, eps):
    """Outline edges of constant v (eaves, ridges, hole fronts) with
    their underside v: (v_top, u_min, u_max, v_under)."""
    out = []
    for li, loop in enumerate(loops_t):
        n = len(loop)
        for i in range(n):
            (u0, v0), (u1, v1) = loop[i], loop[(i + 1) % n]
            if abs(v0 - v1) < eps:
                lu = loops_u[li]
                (_, y0), (_, y1) = lu[i], lu[(i + 1) % n]
                out.append((v0, min(u0, u1), max(u0, u1), 0.5 * (y0 + y1)))
    return out


def under_corner(loops_u, corner, hedges, eps, u_ref):
    """Underside position of a top-outline corner (u, v, loop, edge):
    the same outline edge on the underside plane at the same row edge,
    or the underside position of a constant-v edge when the piece
    (centre u_ref) sits under one. Corners created by a cut in u
    (loop is None) keep their u."""
    u, v, li, ei = corner
    vu = v
    for (vt, ua, ub, vund) in hedges:
        if abs(vt - v) < eps and ua - eps <= u_ref <= ub + eps:
            vu = vund
            break
    if li is None:
        return (u, vu)
    loop = loops_u[li]
    (u0, v0), (u1, v1) = loop[ei], loop[(ei + 1) % len(loop)]
    if abs(v1 - v0) < 1e-9:
        return (u, vu)
    t = (vu - v0) / (v1 - v0)
    return (u0 + t * (u1 - u0), vu)


def uncross(loops_u, left, right, cl, cr):
    """Two underside corners of one row edge that crossed (the underside
    outline ends in an apex below this row): collapse both onto the
    apex of their two edge lines."""
    if left[0] <= right[0] + 1e-9:
        return left, right
    if cl[2] is None or cr[2] is None:
        m = 0.5 * (left[0] + right[0])
        return (m - 5e-5, left[1]), (m + 5e-5, right[1])
    la, lb = loops_u[cl[2]][cl[3]], loops_u[cl[2]][(cl[3] + 1) % len(loops_u[cl[2]])]
    ra, rb = loops_u[cr[2]][cr[3]], loops_u[cr[2]][(cr[3] + 1) % len(loops_u[cr[2]])]
    x = line_isect(la, lb, ra, rb)
    if x is None:
        m = 0.5 * (left[0] + right[0])
        return (m - 5e-5, left[1]), (m + 5e-5, right[1])
    return (x[0] - 5e-5, x[1]), (x[0] + 5e-5, x[1])


def split_quad_u(corners, cuts):
    """Split a trapezoid given as 4 corners (u, v, loop, edge) at the u
    values in `cuts`; cut corners carry loop = None."""
    pieces = [corners]
    for c in sorted(cuts):
        out = []
        for q in pieces:
            (u0, v0, l0, e0), (u1, _, l1, e1), (u2, v1, l2, e2), (u3, _, l3, e3) = q
            if u0 < c - 1e-4 and u1 > c + 1e-4 and u3 < c - 1e-4 and u2 > c + 1e-4:
                out.append([(u0, v0, l0, e0), (c, v0, None, None), (c, v1, None, None), (u3, v1, l3, e3)])
                out.append([(c, v0, None, None), (u1, v0, l1, e1), (u2, v1, l2, e2), (c, v1, None, None)])
            else:
                out.append(q)
        pieces = out
    return pieces


def row_pieces(loops_u, loops_t, v0, v1, eps=1e-5):
    """(underside, top) outline pairs covering the row v0..v1 of the top
    outline. The row is split into bands at every top-outline vertex so
    each band is a set of trapezoids; every top corner is mapped to the
    same outline edge on the underside plane, so board ends are mitred
    on the true cutting planes (hips, valleys, ridges, eaves, dormer
    cut-outs). Trapezoids are also cut at the ends of constant-v edges
    (dormer fronts) so the underside row edge never becomes slanted."""
    inner = sorted(set(v for loop in loops_t for (_, v) in loop if v0 + 2 * eps < v < v1 - 2 * eps))
    bands = [v0] + inner + [v1]
    hedges = horiz_edges(loops_t, loops_u, eps)
    pairs = []
    for b0, b1 in zip(bands[:-1], bands[1:]):
        if b1 - b0 < 2 * eps:
            continue
        lo, hi = scan_cross(loops_t, b0 + eps), scan_cross(loops_t, b1 - eps)
        if len(lo) != len(hi):
            mid = scan_intervals(loops_t, 0.5 * (b0 + b1))
            for (a, b) in mid:
                q = [(a, b0), (b, b0), (b, b1), (a, b1)]
                pairs.append((q, q))
            continue
        cuts = [u for (vt, ua, ub, _) in hedges if abs(vt - b0) < eps or abs(vt - b1) < eps for u in (ua, ub)]
        for j in range(0, len(lo) - 1, 2):
            quad = [(lo[j][0], b0, lo[j][1], lo[j][2]), (lo[j + 1][0], b0, lo[j + 1][1], lo[j + 1][2]),
                    (hi[j + 1][0], b1, hi[j + 1][1], hi[j + 1][2]), (hi[j][0], b1, hi[j][1], hi[j][2])]
            for piece in split_quad_u(quad, cuts):
                top = [(c[0], c[1]) for c in piece]
                u_ref = 0.25 * sum(c[0] for c in piece)
                under = [under_corner(loops_u, c, hedges, eps, u_ref) for c in piece]
                under[0], under[1] = uncross(loops_u, under[0], under[1], piece[0], piece[1])
                under[3], under[2] = uncross(loops_u, under[3], under[2], piece[3], piece[2])
                pairs.append((under, top))
    return pairs


# ------------------------------------------------------------------
# BOARDS


def make_board(name, facet, under, top, coll):
    """Board solid from two outlines in facet u/v: `under` at the
    sheathing underside, `top` at the top surface. Vertex i of both
    outlines is the same board corner, so slanted ends become mitres."""
    if len(under) != len(top):
        under = top
    lo = [facet.xyz(u, v, facet.underside) for (u, v) in under]
    hi = [facet.xyz(u, v, facet.top) for (u, v) in top]
    if signed_area(top) < 0:          # (U, V, N) is right-handed: CCW in u/v = CCW about N
        lo, hi = list(reversed(lo)), list(reversed(hi))
    return craftbot.mesh_prism(name, coll, lo, hi)


def sheathe_facet(facet, loops_u, loops_t, joint_points, coll, prefix,
                  board_w=0.184, board_len=3.6, min_board=0.5, stagger=None, rip_min=0.04):
    """Cover the facet region (outer loop first, then hole loops, in
    facet u/v; even-odd rule) with rows of boards of width `board_w`
    starting at the eave (v_min). `loops_u` is the region at the board
    underside, `loops_t` at the top surface. Joints land on the u of the
    `joint_points` (3D rafter positions), odd rows start with a
    `stagger` board (default half length); a last row narrower than
    `rip_min` is ripped into the previous one. Returns the board count."""
    if stagger is None:
        stagger = 0.5 * board_len
    joints = sorted(set(round(facet.uv(p)[0], 4) for p in joint_points))
    vmin = min(v for loop in loops_t for (_, v) in loop)
    vmax = max(v for loop in loops_t for (_, v) in loop)
    idx = row = 0
    v0 = vmin
    while v0 < vmax - 1e-4:
        v1 = min(v0 + board_w, vmax)
        if vmax - v1 < rip_min:
            v1 = vmax
        for under, top in row_pieces(loops_u, loops_t, v0, v1):
            for bu, bt in split_pair(under, top, joints, row, board_len, min_board, stagger):
                if len(bt) < 3 or area(bt) < 1e-4 or area(bu) < 1e-6:
                    continue
                make_board(f"{prefix}_{idx:03d}", facet, bu, bt, coll)
                idx += 1
        row += 1
        v0 = v1
    return idx


# ------------------------------------------------------------------
# FRAME CORRECTIONS AND CHECKS


def drop_member(name, facets, clearance=0.002):
    """Lower the box member `name` (hip, valley, ridge) along its own
    depth axis until its top edge sits `clearance` under the sheathing
    underside of every facet in `facets` ("dropping the hip").
    Returns the applied drop in metres."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return 0.0
    M = obj.matrix_world
    axes = [M.col[i].xyz for i in range(3)]
    drop, drop_dir = 0.0, None
    for facet in facets:
        n = facet.N
        protrusion = sum(abs(a.dot(n)) for a in axes)
        excess = protrusion - facet.underside + clearance
        if excess <= 0.0:
            continue
        depth_axis = max(axes, key=lambda a: abs(a.normalized().dot(n))).normalized()
        if depth_axis.dot(n) < 0.0:
            depth_axis = -depth_axis
        drop = max(drop, excess / depth_axis.dot(n))
        drop_dir = depth_axis
    if drop > 0.0:
        obj.matrix_world = Matrix.Translation(-drop * drop_dir) @ obj.matrix_world
    return drop


def report_protrusions(frame_names, facet_regions, tol=0.001):
    """Print and return every framing member (by name) whose corner
    pokes more than `tol` through a sheathed area. facet_regions =
    [(facet, loops_uv)], loops in facet u/v at the underside level."""
    hits = []
    for name in frame_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        for facet, loops in facet_regions:
            heights = [(P - facet.O).dot(facet.N) for P in corners]
            if min(heights) > facet.underside:
                continue          # entirely above the boards (a dormer rafter tail)
            worst = 0.0
            for P, h in zip(corners, heights):
                if h > facet.underside + tol:
                    u, v = facet.uv(P)
                    if point_in_loops(u, v, loops):
                        worst = max(worst, h - facet.underside)
            if worst > 0.0:
                hits.append((name, facet.name, worst))
    print(f"[check] framing members poking through sheathing: {len(hits)}")
    for name, fname, h in sorted(hits, key=lambda x: -x[2]):
        print(f"[check]   {name:40s} {fname:10s} +{h * 1000:.1f} mm")
    return hits
