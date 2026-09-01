# ------------------------------------------------------------------
# CRAFT BOT - Blender Python geometry functions
# V 2.0
#
# V 1.1 (experiments 01-13, `input/craftbot_lib.py`) had one function,
# `place_element`, which is unchanged here. V 2.0 adds the helpers that
# every Fable experiment script re-declared on top of it: nested
# collections, a box from corner coordinates, and convex prisms from a
# 2D profile. Higher-level kits live next to this file:
#
#   geometry2d.py   pure 2D polygon / interval tools (no Blender needed)
#   planes.py       half-spaces, plane frames, clipped members
#   ruled.py        bilinear (hypar) surfaces and members along rulings
#   framing.py      stud walls, sheet tiling, boards, walls with openings
#   sheathing.py    roof boards on planar facets, protrusion check
#   render_views.py headless render harness + overlap check
#
# Usage from an experiment script:
#   import sys; sys.path.insert(0, r"<repo>/tools")
#   import craftbot_lib as craftbot
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# MODULE IMPORTS

import bpy
import math
from mathutils import Matrix, Vector


# ------------------------------------------------------------------
# SCENE / COLLECTIONS


def clear_scene():
    """Remove every object from the current file (fresh start for a run)."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def get_collection(path):
    """Return (creating if needed) a nested collection given as 'A/B/C'.

    Collection names are global in Blender: a child called 'Cladding'
    under two different parents is the same collection. Prefix child
    names with their parent ('WallS/WallS_Cladding') to keep them apart.
    """
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
    """Unlink `obj` from every collection and link it into `coll`
    (a collection path string or a Collection)."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if isinstance(coll, str):
        coll = get_collection(coll)
    coll.objects.link(obj)
    return obj


# ------------------------------------------------------------------
# GEOMETRY CREATION


def place_element(
        name,
        loc=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(1.0, 1.0, 1.0),
        euler=None,
        euler_order='XYZ',
        matrix=None,
    ):
    """
    Create (or replace) a cube called `name` and place it in the scene.

    You can control the transform in three different ways, in this order
    of priority:

    1) Full matrix (most explicit)
       - Pass `matrix` as a 4×4 world-space transform (mathutils.Matrix
         or a 4×4 nested sequence).
       - All other transform parameters (loc, axis, angle, scale, euler,
         euler_order) are ignored in this case.

    2) Euler angles (more convenient for many users)
       - Pass `euler=(rx, ry, rz)` in *radians* and optionally
         `euler_order='XYZ'` (or any valid Blender Euler order).
       - `loc` and `scale` are still used.

    3) Axis + angle (backwards compatible default)
       - If `matrix` is None and `euler` is None, the function falls
         back to the original behavior:
         * `axis` is the rotation axis in world space.
         * `angle` is the rotation angle in *degrees*.
         * `loc` and `scale` are used as before.

    Parameters
    ----------
    name : str
        Blender object name. Existing object with this name will be replaced.
    loc : 3-tuple or Vector
        World-space location of the object (translation).
    axis : 3-tuple or Vector
        Rotation axis in world space (used only if euler and matrix are None).
    angle : float
        Rotation angle in degrees (used only if euler and matrix are None).
    scale : 3-tuple or Vector
        Per-axis scale factors (half-extents: the base cube is 2 x 2 x 2).
    euler : 3-tuple or Vector, optional
        Rotation expressed as Euler angles in radians (rx, ry, rz).
        If not None, this overrides axis/angle.
    euler_order : str, optional
        Euler rotation order (e.g. 'XYZ', 'ZXY', etc.). Used only when
        `euler` is not None.
    matrix : Matrix or 4×4 nested sequence, optional
        World-space 4×4 transform matrix. If provided, this is assigned
        directly to obj.matrix_world and all other transform parameters
        are ignored.

    Returns
    -------
    obj : bpy.types.Object
        The newly created Blender object.
    """

    # ------------------------------------------------------------------
    # Coerce parameters to Vectors (kept for backwards compatibility)

    loc_vec = Vector(loc)
    axis_vec = Vector(axis)
    if axis_vec.length == 0:
        axis_vec = Vector((0.0, 0.0, 1.0))
    else:
        axis_vec.normalize()

    scale_vec = Vector(scale)

    # ------------------------------------------------------------------
    # Cube geometry in local space (size 2×2×2 centered at origin)

    verts = [
        Vector(( 1.0,  1.0, -1.0)),
        Vector(( 1.0, -1.0, -1.0)),
        Vector((-1.0, -1.0, -1.0)),
        Vector((-1.0,  1.0, -1.0)),
        Vector(( 1.0,  1.0,  1.0)),
        Vector(( 1.0, -1.0,  1.0)),
        Vector((-1.0, -1.0,  1.0)),
        Vector((-1.0,  1.0,  1.0)),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # ------------------------------------------------------------------
    # Create mesh and object

    # If an object with this name already exists, remove it so we can recreate
    if name in bpy.data.objects:
        old_obj = bpy.data.objects[name]
        bpy.data.objects.remove(old_obj, do_unlink=True)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # ------------------------------------------------------------------
    # Build world transform matrix and assign once

    # Highest priority: explicit world matrix
    if matrix is not None:
        # Accept either a mathutils.Matrix or any 4×4 sequence
        if isinstance(matrix, Matrix):
            M_world = matrix
        else:
            M_world = Matrix(matrix)

    else:
        # Translation
        T = Matrix.Translation(loc_vec)

        # Rotation from Euler angles (if provided)
        if euler is not None:
            from mathutils import Euler
            # Expect euler as (rx, ry, rz) in radians
            eul = Euler(euler, euler_order)
            R = eul.to_matrix().to_4x4()
        else:
            # Backwards-compatible axis + angle in degrees
            angle_rad = math.radians(angle)
            R = Matrix.Rotation(angle_rad, 4, axis_vec)

        # Scale
        S = Matrix.Diagonal((scale_vec.x, scale_vec.y, scale_vec.z, 1.0))

        # Combine: T * R * S (same as original order)
        M_world = T @ R @ S

    obj.matrix_world = M_world

    return obj


def box(name, coll, x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min / max corner coordinates, placed as a
    scaled `place_element` cube and moved into collection `coll`.
    Returns None (creates nothing) for a degenerate extent."""
    if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
        return None
    obj = place_element(
        name=name,
        loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
        axis=(0, 0, 1), angle=0,
        scale=((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2),
    )
    return move_to(obj, coll)


def mesh_prism(name, coll, lo, hi):
    """Mesh from two congruent polygon rings (lists of 3D points): `lo`
    is the bottom face, `hi` the top face, vertex i of both rings is the
    same edge of the solid. Slanted rings give bevelled / mitred ends.
    `lo` must run counter-clockwise when seen from the `hi` side, or the
    faces point inwards; `prism` normalizes the winding for you."""
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


def prism(name, coll, origin, u, v, pts, t0, t1):
    """Convex prism: 2D polygon `pts` (a, b) in the plane through `origin`
    spanned by `u`, `v`, extruded along n = u x v from t0 to t1.
    The profile is re-oriented counter-clockwise so every face points
    outwards whatever the caller's winding. Returns None if degenerate."""
    if len(pts) < 3 or t1 - t0 < 1e-6:
        return None
    u, v = Vector(u), Vector(v)
    n = u.cross(v).normalized()
    o = Vector(origin)
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    if area < 0:
        pts = list(reversed(pts))
    lo = [o + a * u + b * v + t0 * n for a, b in pts]
    hi = [o + a * u + b * v + t1 * n for a, b in pts]
    return mesh_prism(name, coll, lo, hi)


def prism_x(name, coll, x0, x1, pts_yz):
    """(y, z) profile extruded along X from x0 to x1."""
    return prism(name, coll, (0, 0, 0), (0, 1, 0), (0, 0, 1), pts_yz, x0, x1)


def prism_y(name, coll, y0, y1, pts_xz):
    """(x, z) profile extruded along Y from y0 to y1."""
    return prism(name, coll, (0, 0, 0), (0, 0, 1), (1, 0, 0), [(z, x) for x, z in pts_xz], y0, y1)
