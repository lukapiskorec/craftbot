# ------------------------------------------------------------------
# CRAFT BOT - Blender Python geometry functions
# V 1.1
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# MODULE IMPORTS

import bpy
import math
from mathutils import Matrix, Vector



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
        Per-axis scale factors.
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


