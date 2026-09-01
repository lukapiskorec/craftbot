"""Planes, half-spaces and clipped members in 3D (needs Blender's mathutils).

Two plane representations are used, each where it reads best:

- half-space  (p, n): point + outward-of-cut normal; a member keeps the
  side (q - p) . n >= 0.  Built with hs(), vx()/vy()/vz(), cheek(),
  mitre_clip(), Roof.below()/above().  Consumed by frame_prism() clips.
- plane       (n, d): n . P = d, for isect() (three planes -> a point)
  when building outlines as plane intersections. plane_nd() converts a
  half-space, vplane() builds a vertical one.

Members
-------
member()         box between two points, section = width x depth, ends
                 square to the axis, optionally inset so no corner crosses
                 a bearing plane (trusses, braces, rafters on purlins).
sloped_member()  member in a vertical plane with a sloped top line, cut by
                 half-spaces: one call gives a common, jack or cripple
                 rafter, a hip, a joist or a fascia depending on the clips.
bar()            box along any segment with an explicit "up", extended and
                 clipped (plates and rails on warped walls).
frame_prism()    any convex polygon in a Frame, extruded across a thickness
                 and cut by half-spaces on both faces (true cheek cuts).

Provenance: member() from Fable experiments 01/02, Frame / frame_prism /
slab_coeffs / subtract / bar from 07, frame_prism cheek cuts, sloped_member,
Roof, cheek, mitre_clip from 11, isect / vplane from 13.
"""
import math

from mathutils import Matrix, Vector

import craftbot_lib as craftbot
from geometry2d import clip_lin


# ------------------------------------------------------------------
# HALF-SPACES AND PLANES


def hs(p, n):
    """Half-space (point, unit normal); members keep (q - p) . n >= 0."""
    return (Vector(p), Vector(n).normalized())


def vx(x, sign):
    """Half-space bounded by the plane x = const, keeping the `sign` side."""
    return hs((x, 0.0, 0.0), (sign, 0.0, 0.0))


def vy(y, sign):
    return hs((0.0, y, 0.0), (0.0, sign, 0.0))


def vz(z, sign):
    return hs((0.0, 0.0, z), (0.0, 0.0, sign))


def vertical_hs(p, d, h_out, offset=0.0):
    """Vertical half-space containing horizontal direction d through p,
    shifted by `offset` along the horizontal h_out, keeping the side away
    from h_out (an eave plane a set distance outside a wall face)."""
    dh = Vector((d[0], d[1], 0.0)).normalized()
    h = Vector(h_out)
    h = h - h.dot(dh) * dh
    h.z = 0.0
    h.normalize()
    return (Vector(p) + h * offset, -h)


def cheek(C, d, toward, t):
    """Vertical side face of a member of thickness `t` whose centre line
    runs through C along horizontal d, on the side of point `toward`.
    Clip a jack rafter with the cheek of the hip it lands on."""
    d = Vector((d[0], d[1], 0.0)).normalized()
    lat = Vector((-d.y, d.x, 0.0))
    if (Vector((toward[0], toward[1], 0.0)) - Vector((C[0], C[1], 0.0))).dot(lat) < 0:
        lat = -lat
    return hs(Vector((C[0], C[1], 0.0)) + lat * (t / 2), lat)


def mitre_clip(corner, d_self, d_other):
    """Half-space cutting a member that runs away from `corner` along
    d_self on the mitre line bisecting d_self and d_other (both pointing
    away from the corner); fascia and trim corners."""
    d_self = Vector((d_self[0], d_self[1], 0.0)).normalized()
    d_other = Vector((d_other[0], d_other[1], 0.0)).normalized()
    bis = d_self + d_other
    if bis.length < 1e-9:
        bis = Vector((-d_self.y, d_self.x, 0.0))
    n = Vector((-bis.y, bis.x, 0.0)).normalized()
    if n.dot(d_self) < 0:
        n = -n
    return hs((corner[0], corner[1], 0.0), n)


def plane_nd(half_space):
    """(n, d) plane form of a half-space (p, n): n . P = d."""
    p, n = half_space
    return (n.copy(), n.dot(p))


def vplane(axis, value):
    """Vertical plane x = value ('x') or y = value ('y') in (n, d) form."""
    n = Vector((1.0, 0.0, 0.0)) if axis == "x" else Vector((0.0, 1.0, 0.0))
    return (n, value)


def isect(p1, p2, p3):
    """Intersection point of three (n, d) planes. Outline vertices built
    this way, once per offset level, make neighbouring pieces share an
    edge exactly."""
    M = Matrix((p1[0], p2[0], p3[0]))
    return M.inverted() @ Vector((p1[1], p2[1], p3[1]))


class Roof:
    """Roof plane z = z0 + s * (c - out . q) over the ground point q:
    `out` is the outward horizontal direction of the facet, `c` the
    outward distance of the line where z = z0 (the wall / plate line),
    `s` the slope (rise per horizontal run). Use it as the single source
    of truth for everything that meets that roof surface."""

    def __init__(self, name, out, c, z0, s):
        self.name = name
        self.out = Vector((out[0], out[1], 0.0)).normalized()
        self.c, self.z0, self.s = c, z0, s
        self.n = Vector((s * self.out.x, s * self.out.y, 1.0)).normalized()
        self.p = Vector((self.out.x * c, self.out.y * c, z0))

    def z(self, x, y):
        return self.z0 + self.s * (self.c - (self.out.x * x + self.out.y * y))

    def below(self, off=0.0):
        """Half-space under the plane shifted `off` along its normal."""
        return (self.p + self.n * off, -self.n)

    def above(self, off=0.0):
        return (self.p + self.n * off, self.n)

    def plane(self, off=0.0):
        """(n, d) form for isect()."""
        return (self.n.copy(), self.n.dot(self.p + self.n * off))


# ------------------------------------------------------------------
# FRAMES: a 2D polygon living in a 3D plane


class Frame:
    """Plane through o spanned by orthonormal u, v; n = u x v."""

    def __init__(self, o, u, v):
        self.o, self.u, self.v = Vector(o), Vector(u).normalized(), Vector(v).normalized()
        self.n = self.u.cross(self.v).normalized()

    def to2d(self, q):
        d = Vector(q) - self.o
        return (d.dot(self.u), d.dot(self.v))

    def point(self, a, b, t=0.0):
        return self.o + self.u * a + self.v * b + self.n * t

    def clip(self, poly, p, n):
        """Clip a 2D polygon by the 3D half-space (p, n) restricted to
        the plane (thickness ignored; see slab_clip for a slab)."""
        p, n = Vector(p), Vector(n)
        return clip_lin(poly, (self.o - p).dot(n), self.u.dot(n), self.v.dot(n))


def slab_coeffs(fr, p, n, t0, t1):
    """Line coefficients (c, ca, cb) in `fr` such that the WHOLE slab
    (extruded t0..t1 along fr.n) satisfies (q - p) . n >= 0 where
    c + ca*a + cb*b >= 0: the plane is shifted by the worst-case
    thickness term, so thick members never pierce it (square cut)."""
    p, n = Vector(p), Vector(n)
    dn = fr.n.dot(n)
    return (fr.o - p).dot(n) + min(t0 * dn, t1 * dn), fr.u.dot(n), fr.v.dot(n)


def slab_clip(fr, pts, p, n, t0, t1):
    return clip_lin(pts, *slab_coeffs(fr, p, n, t0, t1))


def frame_prism(name, coll, fr, pts, t0, t1, clips=()):
    """Convex prism: polygon `pts` in `fr`, extruded along fr.n from t0
    to t1, cut by 3D half-spaces [(p, n), ...]. The polygon is clipped
    separately at t0 and t1 so oblique planes give true bevel (cheek)
    cuts; if the two outlines end up with different vertex counts the
    cut falls back to a square cut across the whole thickness.
    Returns (obj, outline_at_t0); (None, []) if clipped away."""
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
            lo = slab_clip(fr, lo, p, n, t0, t1)
            if len(lo) < 3:
                return None, []
        hi = lo
    # mesh_prism wants the bottom ring counter-clockwise about fr.n
    area = sum(lo[i][0] * lo[(i + 1) % len(lo)][1] - lo[(i + 1) % len(lo)][0] * lo[i][1]
               for i in range(len(lo)))
    if area < 0:
        lo, hi = list(reversed(lo)), list(reversed(hi))
    obj = craftbot.mesh_prism(name, coll, [fr.point(a, b, t0) for a, b in lo],
                              [fr.point(a, b, t1) for a, b in hi])
    return obj, lo


def subtract(fr, pts, holes, t0=0.0, t1=0.0):
    """Convex polygon minus a convex hole given as inside half-spaces
    [(p, n, clearance), ...]; returns convex pieces that never overlap
    (each clip takes the exact complement) and stay fully outside the
    hole over the slab thickness t0..t1."""
    pieces, rest = [], pts
    for p, n, cl in holes:
        p = Vector(p) - Vector(n) * cl
        c, ca, cb = slab_coeffs(fr, p, -Vector(n), t0, t1)
        outside = clip_lin(rest, c, ca, cb)
        if len(outside) >= 3:
            pieces.append(outside)
        rest = clip_lin(rest, -c, -ca, -cb)
        if len(rest) < 3:
            break
    return pieces


# ------------------------------------------------------------------
# MEMBERS


def member(name, coll, p0, p1, width, depth, width_dir, n0=None, n1=None, on_underside=False):
    """Prismatic box member from p0 to p1, section = `width` (along
    width_dir, projected square to the axis) x `depth`. The depth axis is
    forced to point up, so `on_underside=True` means p0 / p1 lie on the
    member's underside (a rafter given by its bearing line) rather than
    on its centre line. End faces are square to the axis; if a bearing
    plane normal n0 / n1 is given, that end is inset along the axis so
    no corner of the end face crosses the plane through p0 / p1 (the
    member then touches the bearing face on one edge). A scaled
    `place_element` cube, so the box-only overlap check stays exact."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0).normalized()
    e1 = Vector(width_dir)
    e1 = (e1 - axis * e1.dot(axis)).normalized()
    e2 = axis.cross(e1)
    if e2.z < 0:                       # keep the depth axis pointing up (right-handed: flip both)
        e1, e2 = -e1, -e2
    if on_underside:
        p0, p1 = p0 + e2 * depth / 2, p1 + e2 * depth / 2

    def inset(n):
        if n is None:
            return 0.0
        n = Vector(n).normalized()
        reach = abs(e1.dot(n)) * width / 2 + abs(e2.dot(n)) * depth / 2
        return reach / abs(axis.dot(n))

    q0 = p0 + axis * inset(n0)
    q1 = p1 - axis * inset(n1)
    length = (q1 - q0).length
    rot = Matrix((e1, e2, axis)).transposed()      # columns = local X, Y, Z
    ax, ang = rot.to_quaternion().to_axis_angle()
    if ax.length == 0:
        ax = Vector((0, 0, 1))
    obj = craftbot.place_element(name, loc=(q0 + q1) / 2, axis=ax, angle=math.degrees(ang),
                                 scale=(width / 2, depth / 2, length / 2))
    return craftbot.move_to(obj, coll)


def sloped_member(name, coll, p0, d, m, ztop, depth, width, s0, s1, clips=()):
    """Straight member in the vertical plane through ground point p0
    (x, y) along horizontal unit direction d. Its top line is
    z = ztop + m * s (s = horizontal distance from p0), `depth` is
    measured perpendicular to the top line, `width` across the plane.
    Plumb ends at s0 and s1 before clipping by `clips`. Build long and
    clip: with a facet's plane list one call yields a common, jack or
    cripple rafter, a hip (m = hip slope) or a joist (m = 0).
    Returns (obj, outline) like frame_prism."""
    d = Vector((d[0], d[1], 0.0)).normalized()
    fr = Frame((p0[0], p0[1], 0.0), d, (0.0, 0.0, 1.0))
    dv = depth * math.sqrt(1.0 + m * m)
    pts = [(s0, ztop + m * s0 - dv), (s1, ztop + m * s1 - dv),
           (s1, ztop + m * s1), (s0, ztop + m * s0)]
    return frame_prism(name, coll, fr, pts, -width / 2, width / 2, clips)


def bar(name, coll, p, q, up, width, depth, w_off=0.0, d_off=0.0, out=None, ext=(0.0, 0.0), clips=()):
    """Straight member from p to q. Section: `depth` along e3 (`up` made
    perpendicular to the axis), `width` along e2 = e3 x e1 (flipped so
    that e2 . out > 0 when `out` is given). Centre shifted by
    w_off * e2 + d_off * e3, extended by ext = (at p, at q), then cut by
    `clips`. Returns (obj, e1, e2, e3, centre-line point at p)."""
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
    obj, _ = frame_prism(name, coll, fr, pts, -width / 2, width / 2, clips)
    return obj, e1, e2, e3, p + c
