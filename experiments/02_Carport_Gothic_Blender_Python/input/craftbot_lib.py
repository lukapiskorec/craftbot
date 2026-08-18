# ------------------------------------------------------------------
# CRAFT BOT - Blender Python geometry functions
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# MODULE IMPORTS

import bpy
import math
from mathutils import Matrix, Vector



# ------------------------------------------------------------------
# GEOMETRY CREATION


def place_element(name, loc=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                  angle=0.0, scale=(1.0, 1.0, 1.0)):
    """
    Create (or replace) a cube called `name` and place it in the scene
    with a transform defined by loc / axis / angle / scale.

    Parameters
    ----------
    name : str
        Blender object name. Existing object with this name will be replaced.
    loc : 3-tuple or Vector
        World-space location of the object (translation).
    axis : 3-tuple or Vector
        Rotation axis in world space.
    angle : float
        Rotation angle in degrees.
    scale : 3-tuple or Vector
        Per-axis scale factors.
    """

    # ------------------------------------------------------------------
    # Coerce parameters to Vectors

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

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # ------------------------------------------------------------------
    # Build TRS matrix and assign once

    angle_rad = math.radians(angle)

    S = Matrix.Diagonal((scale_vec.x, scale_vec.y, scale_vec.z, 1.0))
    R = Matrix.Rotation(angle_rad, 4, axis_vec)
    T = Matrix.Translation(loc_vec)

    obj.matrix_world = T @ R @ S

    return obj

