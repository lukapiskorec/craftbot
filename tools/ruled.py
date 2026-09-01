"""Bilinear (hyperbolic paraboloid) surfaces and the members that live on
them: studs / rafters along rulings, plate-like boards on best-fit
patches. For warped, twisted and leaning walls and roofs.

A Ruled surface is defined by two segments, A0-A1 (u = 0) and B0-B1
(u = 1); t runs along the segments. Rulings (constant t) are straight,
so a straight member can run along one exactly. Everything else on the
surface is only approximately planar: quad_frame() fits a plane per
patch and records the out-of-plane residual in RESIDUALS, so the run
can report how far each board is from flat. Fit per bay, never across
several bays of a twisted surface, and keep boards short stock.

Provenance: Fable experiment 07 (Gehry deconstruction).
"""
from mathutils import Vector

from geometry2d import inset
from planes import Frame, frame_prism, slab_clip, subtract

RESIDUALS = []   # (out-of-plane residual, name) for every surface_quad


class Ruled:
    """Bilinear surface between the segments A0-A1 (u = 0) and B0-B1
    (u = 1); `out` picks the sign of the normal."""

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
    `ext` at both ends, to be cut by `clips`). Section: d0..d1 along the
    local outward normal, w0..w1 along the surface in the +t sense.
    `holes` = [(p, n, clearance)] inside half-spaces of an opening the
    member must stay out of. Returns (pieces, frame, e3) where e3 is
    the +t side direction."""
    p0, p1 = S.P(t, 0), S.P(t, 1)
    e1 = (p1 - p0).normalized()
    n = S.normal(t, 0.5)
    e2 = (n - n.dot(e1) * e1).normalized()
    fr = Frame(p0, e1, e2)
    e3 = fr.n
    if e3.dot(S.dt(t, 0.5)) < 0:
        e3, w0, w1 = -e3, -w1, -w0
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
        o, _ = frame_prism(nm, coll, fr, poly, w0, w1)
        if o:
            objs.append(o)
    return objs, fr, e3


def quad_frame(S, t0, t1, u0, u1, name=""):
    """Best-fit frame of the surface patch [t0, t1] x [u0, u1] and its
    2D outline; appends the out-of-plane residual to RESIDUALS."""
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
    RESIDUALS.append((max(abs((q - c).dot(n)) for q in Q), name))
    return fr, pts


def surface_quad(name, coll, S, t0, t1, u0, u1, n0, n1, clips=(), holes=(), gap=0.0):
    """Plate-like member on the patch [t0, t1] x [u0, u1] of S, from n0
    to n1 along the patch normal, edges inset by `gap`, cut by `clips`
    and with convex `holes` subtracted. Returns the created objects."""
    fr, pts = quad_frame(S, t0, t1, u0, u1, name)
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
        o, _ = frame_prism(nm, coll, fr, poly, n0, n1)
        if o:
            objs.append(o)
    return objs


def surf_extent(S, planes, clear, depths=(0.0,), samples=100):
    """(t_min, t_max, u_min, u_max) bounding box of the surface samples
    (at the given normal depths) that lie inside the convex region
    `planes` = [(p, n)] expanded by `clear`; None if nothing does."""
    tmin, tmax, umin, umax = 2, -1, 2, -1
    for i in range(samples + 1):
        t = i / samples
        for j in range(samples + 1):
            u = j / samples
            for d in depths:
                q = S.P(t, u) + S.normal(t, u) * d
                if all((q - p).dot(n) >= -clear for p, n in planes):
                    tmin, tmax, umin, umax = min(tmin, t), max(tmax, t), min(umin, u), max(umax, u)
    if tmax < tmin:
        return None
    return tmin, tmax, umin, umax
