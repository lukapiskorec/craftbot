"""Exact hidden-line removal for convex, non-intersecting solids.

Works in any orthographic view, axonometrics included. Every edge that
borders a front face is clipped against every front face of the other
members: the part of the edge inside a face's outline is removed when that
face is nearer to the viewer. A face that only touches the edge (same depth
within EPS) hides nothing, so flush joints keep their lines. Faces must be
wound outwards (`export_members.py` asserts it). Needs numpy.

    lines = visible_lines(members, right, up)      # [((x0, y0), (x1, y1)), ...]

`members` are dicts with 'verts' (3D points) and 'faces' (vertex index
lists), as written by `export_members.py`. Units are the members' units;
EPS suits model millimetres.

Provenance: experiment 16 fabrication set, after Blender Freestyle dropped
edges lying in or near a touching neighbour's face.
"""
import numpy as np

EPS = 0.02      # mm: depth tolerance, and the shortest segment kept


def _project(members, right, up):
    right, up = np.array(right, float), np.array(up, float)
    toward = np.cross(right, up)
    basis = np.stack([right, up, toward])
    faces, edges = [], []      # faces: (owner, 2D polygon, plane); edges: (owner, p, q) in view coordinates
    for owner, m in enumerate(members):
        verts = np.array(m['verts'], float) @ basis.T
        front_edges = set()
        for face in m['faces']:
            pts = verts[face]
            normal = np.cross(pts[1]-pts[0], pts[2]-pts[1])
            if normal[2] <= 1e-9*np.linalg.norm(normal):
                continue
            faces.append((owner, pts[:, :2], (pts[0], normal)))
            for a, b in zip(face, face[1:]+face[:1]):
                front_edges.add((min(a, b), max(a, b)))
        edges += [(owner, verts[a], verts[b]) for a, b in sorted(front_edges)]
    return faces, edges


def _inside_interval(p, d, poly, tolerance=0.):
    """Parameter interval of the segment p + t*d, t in 0..1, inside a convex
    counter-clockwise polygon (Cyrus-Beck)."""
    t0, t1 = 0.0, 1.0
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        ex, ey = b-a
        side = ex*(p[1]-a[1])-ey*(p[0]-a[0])       # > 0: p is inside this edge
        side += tolerance*np.hypot(ex,ey)
        slope = ex*d[1]-ey*d[0]
        if abs(slope) < 1e-12:
            if side < 0:
                return None
            continue
        t = -side/slope
        if slope > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t1-t0 < 1e-9:
            return None
    return t0, t1


def _coplanar_seams(owner, p, q, faces, groups):
    """Intervals internal to a flat surface of one logical element.

    Convex faces remain separate for occlusion. Only their shared linework
    dissolves; explicit line_group metadata may join parts of a single member.
    Unrelated members retain their physical joint boundaries.
    """
    direction=q-p
    midpoint=(p+q)/2
    own=[]
    for face_owner,poly,(origin,normal) in faces:
        if face_owner!=owner: continue
        unit=normal/np.linalg.norm(normal)
        if max(abs(np.dot(p-origin,unit)),abs(np.dot(q-origin,unit)))>EPS: continue
        span=_inside_interval(p[:2],direction[:2],poly,tolerance=EPS)
        if span is not None:
            delta=poly.mean(axis=0)-midpoint[:2]
            side=direction[0]*delta[1]-direction[1]*delta[0]
            own.append((unit,side,span))
    hidden=[]
    for face_owner,poly,(origin,normal) in faces:
        if groups[face_owner]!=groups[owner]: continue
        unit=normal/np.linalg.norm(normal)
        if max(abs(np.dot(p-origin,unit)),abs(np.dot(q-origin,unit)))>EPS: continue
        delta=poly.mean(axis=0)-midpoint[:2]
        side=direction[0]*delta[1]-direction[1]*delta[0]
        span=_inside_interval(p[:2],direction[:2],poly,tolerance=EPS)
        if span is None: continue
        for n,s,own_span in own:
            if np.dot(unit,n)>.999999 and side*s < -1e-8:
                # Both faces must border this same interval. A partial flat
                # join must not erase the exposed remainder of a long edge.
                overlap=(max(span[0],own_span[0]),min(span[1],own_span[1]))
                if overlap[1]>overlap[0]: hidden.append(overlap)
    return hidden


def visible_lines(members, right, up, *, crease_only=False):
    """Visible parts of every member edge in the view with axes `right` and `up`, as 2D segments."""
    faces, edges = _project(members, right, up)
    groups=[m.get('line_group') or ('member',i) for i,m in enumerate(members)]
    seam_faces={i:[f for f in faces if groups[f[0]]==group] for i,group in enumerate(groups)} if crease_only else {}
    owners = np.array([f[0] for f in faces])
    lo = np.array([f[1].min(axis=0) for f in faces])
    hi = np.array([f[1].max(axis=0) for f in faces])
    nearest = np.array([max(f[2][0][2], *(f[2][0][2]-(f[2][1][0]*(x-f[2][0][0])+f[2][1][1]*(y-f[2][0][1]))/f[2][1][2]
                                          for x, y in f[1])) for f in faces])
    lines = []
    for owner, p, q in edges:
        d = q-p
        if np.hypot(d[0], d[1]) < EPS:
            continue
        box_lo, box_hi = np.minimum(p, q), np.maximum(p, q)
        near = np.nonzero(((owners != owner) | bool(members[owner].get('self_occlude'))) & (lo[:, 0] < box_hi[0]) & (hi[:, 0] > box_lo[0])
                          & (lo[:, 1] < box_hi[1]) & (hi[:, 1] > box_lo[1]) & (nearest > box_lo[2]+EPS))[0]
        hidden = _coplanar_seams(owner,p,q,seam_faces[owner],groups) if crease_only else []
        for i in near:
            _, poly, (origin, normal) = faces[i]
            span = _inside_interval(p[:2], d[:2], poly)
            if span is None:
                continue
            mid = p+d*(span[0]+span[1])/2
            face_depth = origin[2]-(normal[0]*(mid[0]-origin[0])+normal[1]*(mid[1]-origin[1]))/normal[2]
            if face_depth > mid[2]+EPS:
                hidden.append(span)
        t, length = 0.0, np.hypot(d[0], d[1])
        for a, b in sorted(hidden)+[(1.0, 1.0)]:
            if (a-t)*length > EPS:
                lines.append((tuple((p+d*t)[:2]), tuple((p+d*a)[:2])))
            t = max(t, b)
    return lines
