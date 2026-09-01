"""Pure 2D polygon and interval tools shared by the CraftBot kits.

No Blender dependency: points are (a, b) tuples, polygons are lists of
points, and everything runs (and is tested) in plain Python. The 3D
helpers in planes.py, framing.py and sheathing.py build on these.

Conventions
-----------
- Polygons are convex unless a function says otherwise; clipping keeps
  them convex. Winding is not required (area() is unsigned); the prism
  builders in craftbot_lib normalize it.
- A "hole" or "opening" is an axis-aligned rectangle (a0, a1, b0, b1).
- Intervals are (lo, hi) tuples with lo < hi.

Provenance: clip / strip / positions from the Fable runs of experiments
04-09, clip_lin / inset from 07, tile from 08, wall_pieces from 09,
board-layout scanline helpers from 11 and 13.
"""
import math

EPS = 1e-6


# ------------------------------------------------------------------
# HALF-PLANE CLIPPING (Sutherland-Hodgman, one edge at a time)


def clip_lin(poly, c, ca, cb):
    """Keep the part of convex polygon `poly` where c + ca*a + cb*b >= 0."""
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
    """Keep the part of convex polygon `poly` with (q - p) . n >= 0,
    i.e. the side of the line through `p` that normal `n` points to."""
    return clip_lin(poly, -(p[0] * n[0] + p[1] * n[1]), n[0], n[1])


def clip_rect(poly, a0, a1, b0, b1):
    """Intersect a convex polygon with the rectangle a0..a1 x b0..b1."""
    poly = clip(poly, (a0, 0), (1, 0))
    poly = clip(poly, (a1, 0), (-1, 0))
    poly = clip(poly, (0, b0), (0, 1))
    poly = clip(poly, (0, b1), (0, -1))
    return poly


def clip_u(poly, c, keep_left):
    """Clip a convex polygon against the vertical line a = c, keeping the
    side a <= c (keep_left) or a >= c."""
    out = []
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        inP = (P[0] <= c) if keep_left else (P[0] >= c)
        inQ = (Q[0] <= c) if keep_left else (Q[0] >= c)
        if inP:
            out.append(P)
        if inP != inQ:
            t = (c - P[0]) / (Q[0] - P[0])
            out.append((c, P[1] + t * (Q[1] - P[1])))
    return out


def inset(poly, d):
    """Shrink a convex polygon by `d` on every edge (any winding).
    Returns [] when the polygon vanishes."""
    sgn = 1.0 if signed_area(poly) > 0 else -1.0
    lines = []                                        # from the ORIGINAL edges
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        if L < 1e-12:
            continue
        nx, ny = -ey / L * sgn, ex / L * sgn          # inward normal
        lines.append(((a[0] + nx * d, a[1] + ny * d), (nx, ny)))
    for p, n in lines:
        poly = clip(poly, p, n)
        if len(poly) < 3:
            return []
    return poly


# ------------------------------------------------------------------
# POLYGON CONSTRUCTION AND MEASUREMENT


def rect(a0, a1, b0, b1):
    """Counter-clockwise rectangle polygon."""
    return [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]


def strip(p, q, width, ext=0.0):
    """Rectangle of `width` centred on the segment p-q, extended by `ext`
    beyond both ends (a diagonal brace before clipping to its bay)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    dx, dy = dx / L, dy / L
    nx, ny = -dy, dx
    ax, ay = p[0] - dx * ext, p[1] - dy * ext
    bx, by = q[0] + dx * ext, q[1] + dy * ext
    h = width / 2
    return [(ax - nx * h, ay - ny * h), (bx - nx * h, by - ny * h),
            (bx + nx * h, by + ny * h), (ax + nx * h, ay + ny * h)]


def signed_area(poly):
    """Shoelace area: positive for counter-clockwise polygons."""
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
                     poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def area(poly):
    return abs(signed_area(poly))


def line_isect(p0, p1, q0, q1):
    """Intersection of the infinite lines p0-p1 and q0-q1; None if parallel."""
    d1 = (p1[0] - p0[0], p1[1] - p0[1])
    d2 = (q1[0] - q0[0], q1[1] - q0[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-12:
        return None
    t = ((q0[0] - p0[0]) * d2[1] - (q0[1] - p0[1]) * d2[0]) / den
    return (p0[0] + t * d1[0], p0[1] + t * d1[1])


def point_in_loops(a, b, loops):
    """Even-odd test of point (a, b) against a list of polygon loops
    (outer loop plus holes)."""
    inside = False
    for loop in loops:
        n = len(loop)
        for i in range(n):
            a0, b0 = loop[i]
            a1, b1 = loop[(i + 1) % n]
            if (b0 <= b < b1) or (b1 <= b < b0):
                if a < a0 + (b - b0) / (b1 - b0) * (a1 - a0):
                    inside = not inside
    return inside


def scan_intervals(loops, b_s):
    """Even-odd intervals in `a` where the horizontal line b = b_s lies
    inside the region bounded by `loops` (outer loop plus holes)."""
    us = []
    for loop in loops:
        n = len(loop)
        for i in range(n):
            a0, b0 = loop[i]
            a1, b1 = loop[(i + 1) % n]
            if (b0 <= b_s < b1) or (b1 <= b_s < b0):
                t = (b_s - b0) / (b1 - b0)
                us.append(a0 + t * (a1 - a0))
    us.sort()
    return [(us[i], us[i + 1]) for i in range(0, len(us) - 1, 2)]


# ------------------------------------------------------------------
# INTERVALS: member spacing, cutting ranges around openings


def positions(a0, a1, spacing, thick, grid0=None):
    """Centre positions of repeated members (studs, joists, rafters)
    between a0 and a1: first and last flush with the ends, the others
    on the grid grid0 + k*spacing (grid0 defaults to a0). A grid member
    closer than half a spacing to the last one is dropped, so the run
    never ends with a sliver bay."""
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


def count_fit(length, module):
    """Number of whole modules in `length` and the remainder, without
    the int(round()) trap that silently drops a partial module."""
    n = int(math.floor(length / module + 1e-9))
    return n, length - n * module


def split_range(a0, a1, cuts):
    """Sub-ranges of (a0, a1) outside the cut intervals [(ca, cb), ...]
    (a bottom plate interrupted by doors)."""
    out, start = [], a0
    for ca, cb in sorted(cuts):
        if cb <= a0 or ca >= a1:
            continue
        if ca > start:
            out.append((start, ca))
        start = max(start, cb)
    if start < a1 - EPS:
        out.append((start, a1))
    return out


def strips(a0, a1, cuts):
    """Split [a0, a1] at the given cut positions (panel joints)."""
    c = sorted({a0, a1, *[x for x in cuts if a0 < x < a1]})
    return list(zip(c[:-1], c[1:]))


def split_rows(rows, holes):
    """Split bands [(b0, b1), ...] at the bottom / top of every hole
    (a0, a1, b0, b1) so pieces beside a hole can be generated."""
    out = []
    for ra, rb in rows:
        cuts = {ra, rb}
        for _, _, ha, hb in holes:
            for h in (ha, hb):
                if ra + EPS < h < rb - EPS:
                    cuts.add(h)
        c = sorted(cuts)
        out += list(zip(c[:-1], c[1:]))
    return out


# ------------------------------------------------------------------
# TILING: sheets and panels with rectangular holes


def tile(a0, a1, b0, b1, la, lb, holes=(), stagger=True):
    """Rectangles (ca, cb, ba, bb) of sheets la x lb tiling the rectangle
    a0..a1 x b0..b1: rows along b of height lb, cells of length la along
    a, odd rows shifted by la/2 when `stagger`, every cell cut around the
    holes (ha0, ha1, hb0, hb1). Cells inside a hole are omitted.

    Upright wall sheets: tile(a0, a1, z0, z1, sheet_w, sheet_l, holes, stagger=False)
    Floor / roof decks:  tile(x0, x1, y0, y1, sheet_l, sheet_w, holes)"""
    out = []
    row = 0
    b = b0
    while b < b1 - EPS:
        bb = min(b + lb, b1)
        cuts = {a0, a1}
        a = a0 + (la / 2 if (stagger and row % 2) else 0.0)
        while a < a1:
            if a > a0:
                cuts.add(a)
            a += la
        for ha0, ha1, hb0, hb1 in holes:
            if hb0 < bb - EPS and hb1 > b + EPS:
                cuts.update([max(ha0, a0), min(ha1, a1)])
        c = sorted(cuts)
        for i in range(len(c) - 1):
            ca, cb = c[i], c[i + 1]
            if cb - ca < EPS:
                continue
            zc = {b, bb}
            for ha0, ha1, hb0, hb1 in holes:
                if ha0 <= ca + EPS and cb <= ha1 + EPS:
                    for h in (hb0, hb1):
                        if b + EPS < h < bb - EPS:
                            zc.add(h)
            zc = sorted(zc)
            for j in range(len(zc) - 1):
                za, zb = zc[j], zc[j + 1]
                if any(ha0 <= ca + EPS and cb <= ha1 + EPS and hb0 <= za + EPS and zb <= hb1 + EPS
                       for ha0, ha1, hb0, hb1 in holes):
                    continue
                out.append((ca, cb, za, zb))
        b = bb
        row += 1
    return out


def wall_pieces(poly, openings):
    """Decompose a convex (u, z) polygon with rectangular openings
    (u0, u1, z0, z1) into convex pieces: full-height piers between
    opening columns, and sill / spandrel / lintel pieces within each
    column. Openings sharing the same u-range form one column (one
    window per storey on a balloon panel); different columns must not
    overlap in u. Pieces stay convex so the overlap check stays exact."""
    cols = {}
    for u0, u1, z0, z1 in openings:
        cols.setdefault((round(u0, 6), round(u1, 6)), []).append((z0, z1))
    keys = sorted(cols)
    for (a0, a1), (b0, b1) in zip(keys, keys[1:]):
        assert a1 <= b0 + EPS, f"overlapping opening columns {(a0, a1)} / {(b0, b1)}"
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
    return [p for p in pieces if len(p) >= 3 and area(p) > EPS]
