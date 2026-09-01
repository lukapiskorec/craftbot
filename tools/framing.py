"""Building-element generators on top of craftbot_lib: stud walls with
framed openings, sheet cladding and decks cut around holes, board floors,
walls with openings as convex pieces, sloped roof layers, stair flights,
halved braces.

Every generator takes a name `prefix` and a collection path, and creates
its members as `craftbot.box` / prisms so the overlap check stays exact.
Wall generators describe a wall by `along` ('x' or 'y'), its extent
a0..a1 along that axis and its thickness zone b0..b1 across; openings
are (aa, ab, z_sill, z_head) with z_sill = None for a door.

All dimensions are parameters; no module constants. Pass your stock
sizes (stud thickness, sheet size, board width) from the experiment
script so the whole model derives from one parameter block.

Provenance: stud_wall / clad / tile_sheets from Fable experiments 03 and
04, boards and roof_piece from 08, wall_along_* and flight from 09,
halved_brace from 02.
"""
from mathutils import Vector

import craftbot_lib as craftbot
from geometry2d import EPS, positions, split_range, tile, wall_pieces
from planes import member


def rect_fn(coll, along, b0, b1):
    """Box maker for a wall running along 'x' or 'y' with thickness
    zone b0..b1: rect(name, p0, p1, z0, z1[, bb0, bb1])."""
    def rect(name, p0, p1, z0, z1, bb0=b0, bb1=b1):
        if along == "x":
            return craftbot.box(name, coll, p0, p1, bb0, bb1, z0, z1)
        return craftbot.box(name, coll, bb0, bb1, p0, p1, z0, z1)
    return rect


# ------------------------------------------------------------------
# STUD WALLS


def stud_wall(prefix, coll, along, a0, a1, b0, b1, z0, z1, t, spacing,
              grid0=None, openings=(), lintel_d=0.15, double_top=False,
              nog_z=None, noggins=True):
    """Platform-framed stud wall: bottom plate (cut at doors), top plate
    (doubled if `double_top`), studs of thickness `t` on the grid
    grid0 + k*spacing with end studs flush, framed openings (jack + king
    studs, lintel of depth `lintel_d`, cripples above, sill + cripples
    below a window) and one row of noggins at nog_z (default: mid
    height) between the members actually placed.
    openings = [(aa, ab, z_sill | None, z_head)], aa..ab = clear opening."""
    rect = rect_fn(coll, along, b0, b1)
    doors = [(aa, ab) for aa, ab, zs, _ in openings if zs is None]
    for i, (sa, sb) in enumerate(split_range(a0, a1, doors)):
        rect(f"{prefix}_BottomPlate_{i}", sa, sb, z0, z0 + t)
    if double_top:
        rect(f"{prefix}_TopPlate_1", a0, a1, z1 - 2 * t, z1 - t)
        rect(f"{prefix}_TopPlate_2", a0, a1, z1 - t, z1)
        zt = z1 - 2 * t
    else:
        rect(f"{prefix}_TopPlate", a0, a1, z1 - t, z1)
        zt = z1 - t
    zs0 = z0 + t
    verticals = []
    for i, c in enumerate(positions(a0, a1, spacing, t, grid0)):
        if any(aa - 2.5 * t < c < ab + 2.5 * t for aa, ab, _, _ in openings):
            continue
        rect(f"{prefix}_Stud_{i:02d}", c - t / 2, c + t / 2, zs0, zt)
        verticals.append((c - t / 2, c + t / 2))
    for k, (aa, ab, zs, zh) in enumerate(openings):
        rect(f"{prefix}_Op{k}_JackL", aa - t, aa, zs0, zh)
        rect(f"{prefix}_Op{k}_KingL", aa - 2 * t, aa - t, zs0, zt)
        rect(f"{prefix}_Op{k}_JackR", ab, ab + t, zs0, zh)
        rect(f"{prefix}_Op{k}_KingR", ab + t, ab + 2 * t, zs0, zt)
        rect(f"{prefix}_Op{k}_Lintel", aa - t, ab + t, zh, zh + lintel_d)
        verticals += [(aa - 2 * t, aa - t), (ab + t, ab + 2 * t)]
        for j, c in enumerate(positions(aa - t, ab + t, spacing, t, grid0)[1:-1]):
            rect(f"{prefix}_Op{k}_Cripple_{j}", c - t / 2, c + t / 2, zh + lintel_d, zt)
        if zs is not None:
            rect(f"{prefix}_Op{k}_Sill", aa, ab, zs - t, zs)
            for j, c in enumerate(positions(aa, ab, spacing, t, grid0)[1:-1]):
                rect(f"{prefix}_Op{k}_SillCripple_{j}", c - t / 2, c + t / 2, zs0, zs - t)
    if not noggins:
        return
    zc = (zs0 + zt) / 2 if nog_z is None else nog_z
    verticals.sort()
    for i in range(len(verticals) - 1):
        pa, pb = verticals[i][1], verticals[i + 1][0]
        if pb - pa < 0.05:
            continue
        if any(aa - 2 * t <= pa + EPS and pb <= ab + 2 * t + EPS for aa, ab, _, _ in openings):
            continue          # the bay is the opening itself
        rect(f"{prefix}_Nog_{i:02d}", pa, pb, zc - t / 2, zc + t / 2)


# ------------------------------------------------------------------
# SHEETS, BOARDS, PANELS


def clad(prefix, coll, along, a0, a1, b0, b1, z0, z1, sheet_w=1.22, sheet_l=2.44,
         holes=(), stagger=False):
    """Upright sheets (sheet_w along the wall, sheet_l tall) on a wall
    zone b0..b1, cut around holes [(aa, ab, za, zb)] column by column.
    Returns the number of pieces."""
    rect = rect_fn(coll, along, b0, b1)
    n = 0
    for ca, cb, za, zb in tile(a0, a1, z0, z1, sheet_w, sheet_l, holes, stagger):
        rect(f"{prefix}_{n:03d}", ca, cb, za, zb)
        n += 1
    return n


def tile_sheets(prefix, coll, x0, x1, y0, y1, z0, z1, sheet_l=2.44, sheet_w=1.22,
                holes=(), stagger=True):
    """Horizontal deck of sheets (long side along X, rows along Y
    staggered by half a sheet) between z0 and z1, cut around holes
    [(xa, xb, ya, yb)]. Returns the number of pieces."""
    n = 0
    for xa, xb, ya, yb in tile(x0, x1, y0, y1, sheet_l, sheet_w, holes, stagger):
        craftbot.box(f"{prefix}_{n:03d}", coll, xa, xb, ya, yb, z0, z1)
        n += 1
    return n


def boards(prefix, coll, x0, x1, y0, y1, z0, z1, w, gap=0.0, nogo=(), along="y"):
    """Floor / deck boards of width `w` with `gap` between them, running
    along 'y' (rows across X) or 'x' (rows across Y), each board split
    around the no-go rectangles [(xa, xb, ya, yb)] (posts, voids).
    Returns the number of pieces."""
    n = 0
    if along == "y":
        u0, u1, v0, v1 = x0, x1, y0, y1
        rects = [(xa, xb, ya, yb) for xa, xb, ya, yb in nogo]
    else:
        u0, u1, v0, v1 = y0, y1, x0, x1
        rects = [(ya, yb, xa, xb) for xa, xb, ya, yb in nogo]
    u = u0
    while u < u1 - EPS:
        ub = min(u + w, u1)
        spans = [(v0, v1)]
        for nu0, nu1, nv0, nv1 in rects:
            if nu0 < ub - EPS and nu1 > u + EPS:
                new = []
                for va, vb in spans:
                    if nv0 < vb - EPS and nv1 > va + EPS:
                        if nv0 > va + EPS:
                            new.append((va, nv0))
                        if nv1 < vb - EPS:
                            new.append((nv1, vb))
                    else:
                        new.append((va, vb))
                spans = new
        for va, vb in spans:
            if along == "y":
                craftbot.box(f"{prefix}_{n:03d}", coll, u, ub, va, vb, z0, z1)
            else:
                craftbot.box(f"{prefix}_{n:03d}", coll, va, vb, u, ub, z0, z1)
            n += 1
        u += w + gap
    return n


def wall_along_x(prefix, coll, poly_xz, y0, y1, openings=()):
    """Solid wall (CLT / concrete) in a plane y = const: convex (x, z)
    profile minus rectangular openings (x0, x1, z0, z1), as convex prism
    pieces (piers, sills, lintels). Returns the number of pieces."""
    n = 0
    for p in wall_pieces(poly_xz, openings):
        craftbot.prism_y(f"{prefix}_{n:02d}", coll, y0, y1, p)
        n += 1
    return n


def wall_along_y(prefix, coll, poly_yz, x0, x1, openings=()):
    """Solid wall in a plane x = const: convex (y, z) profile minus
    rectangular openings (y0, y1, z0, z1)."""
    n = 0
    for p in wall_pieces(poly_yz, openings):
        craftbot.prism_x(f"{prefix}_{n:02d}", coll, x0, x1, p)
        n += 1
    return n


# ------------------------------------------------------------------
# PITCHED ROOF LAYERS


def roof_profile(y0, y1, lo, hi):
    """Plumb-cut parallelogram (y, z) profile between two height
    functions z = lo(y) and z = hi(y) (must not straddle a ridge)."""
    return [(y0, lo(y0)), (y1, lo(y1)), (y1, hi(y1)), (y0, hi(y0))]


def roof_piece(name, coll, x0, x1, y0, y1, lo, hi, y_ridge=None):
    """Roof-parallel member / deck piece between the height functions
    lo(y) and hi(y), extruded along X. A piece straddling y_ridge is
    split plumb at the ridge into two convex halves (name + '_s' / '_n')
    instead of branching on a float straddle test."""
    if y_ridge is not None and y0 < y_ridge - EPS and y1 > y_ridge + EPS:
        craftbot.prism_x(name + "_s", coll, x0, x1, roof_profile(y0, y_ridge, lo, hi))
        craftbot.prism_x(name + "_n", coll, x0, x1, roof_profile(y_ridge, y1, lo, hi))
        return None
    return craftbot.prism_x(name, coll, x0, x1, roof_profile(y0, y1, lo, hi))


# ------------------------------------------------------------------
# STAIRS


def flight(prefix, coll, x_start, direction, y0, y1, z_base, n_risers, going, riser,
           step_d, z_min=None):
    """Straight flight of n_risers - 1 solid tread blocks rising from
    z_base (the last riser lands on the landing / floor), each `going`
    long and `riser` high, `step_d` thick. direction = +1 rises towards
    +X. The stepped soffit never goes below z_min."""
    if z_min is None:
        z_min = z_base - step_d
    for i in range(n_risers - 1):
        xa = x_start + direction * going * i
        xb = xa + direction * going
        top = z_base + riser * (i + 1)
        craftbot.box(f"{prefix}_{i + 1:02d}", coll, min(xa, xb), max(xa, xb), y0, y1,
                     max(top - step_d, z_min), top)


# ------------------------------------------------------------------
# TIMBER JOINTS


def halved_brace(name, coll, p0, p1, width, depth, width_dir, n0, n1, cross_pt, lap_len, lap_side):
    """Brace from p0 to p1 as three boxes: full section at both ends and
    a half-width middle segment (the halving joint) of length lap_len
    centred on the point of the axis nearest cross_pt, kept on the
    `lap_side` (+1 / -1 along width_dir) so two crossing braces share
    the joint zone without overlapping (St Andrew's cross)."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0).normalized()
    w = Vector(width_dir).normalized()
    e2 = axis.cross(w)

    def inset(n):                          # same rule as member()
        n = Vector(n).normalized()
        reach = abs(w.dot(n)) * width / 2 + abs(e2.dot(n)) * depth / 2
        return reach / abs(axis.dot(n))
    q0 = p0 + axis * inset(n0)
    q1 = p1 - axis * inset(n1)
    mid = p0 + axis * (Vector(cross_pt) - p0).dot(axis)
    a, b = mid - axis * lap_len / 2, mid + axis * lap_len / 2
    member(name + "_lo", coll, q0, a, width, depth, w)
    member(name + "_hi", coll, b, q1, width, depth, w)
    offset = w * (lap_side * width / 4)
    member(name + "_lap", coll, a + offset, b + offset, width / 2, depth, w)
