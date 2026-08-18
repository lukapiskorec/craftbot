# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 - CHATGPT 5.1 - V01
# HIP ROOF
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix

import importlib
import craftbot_lib as craftbot  # assumes craftbot_lib.py is on sys.path
importlib.reload(craftbot)


# ------------------------------------------------------------------
# UTILITIES
# ------------------------------------------------------------------

def create_prismatic_member(name, start, end,
                            width=0.038,   # ~38 mm
                            depth=0.184):  # ~184 mm
    """
    Create a rectangular prism-like element between two 3D points.

    Arguments:
        name  : Blender object name.
        start : (x, y, z) world coordinates at one end of the member.
        end   : (x, y, z) world coordinates at the other end of the member.
        width : cross-section size along local X (m).
        depth : cross-section size along local Y (m).

    The local Z axis of the cube is aligned along the member axis.
    """

    p0 = Vector(start)
    p1 = Vector(end)
    direction = p1 - p0
    length = direction.length

    if length == 0:
        # Degenerate case: skip
        return

    axis_z = direction.normalized()

    # Choose a stable 'up' vector to avoid degeneracy
    world_up = Vector((0.0, 0.0, 1.0))
    if abs(axis_z.dot(world_up)) > 0.99:
        world_up = Vector((0.0, 1.0, 0.0))

    # Build an orthonormal basis: axis_x, axis_y, axis_z
    axis_x = world_up.cross(axis_z).normalized()
    axis_y = axis_z.cross(axis_x).normalized()

    # Rotation matrix (columns are local axes in world space)
    R = Matrix((
        (axis_x.x, axis_y.x, axis_z.x),
        (axis_x.y, axis_y.y, axis_z.y),
        (axis_x.z, axis_y.z, axis_z.z),
    ))
    R4 = R.to_4x4()

    # The base cube in craftbot_lib is 2x2x2; we want:
    #   width  along local X  -> actual size = width
    #   depth  along local Y  -> actual size = depth
    #   length along local Z  -> actual size = length
    #
    # Since the cube is ±1 in each axis, the scale factor is half
    # of the desired physical dimension.
    S = Matrix.Diagonal((
        width / 2.0,
        depth / 2.0,
        length / 2.0,
        1.0
    ))

    # Translate to midpoint
    mid = (p0 + p1) * 0.5
    T = Matrix.Translation(mid)

    # World transform
    M_world = T @ R4 @ S

    # Place the element using the full transform matrix API
    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


# ------------------------------------------------------------------
# HIP ROOF GEOMETRY
# ------------------------------------------------------------------

def build_simple_hip_roof(
        length=8.0,
        width=6.0,
        plate_z=0.0,
        slope_rise=1.0,
        slope_run=3.0,
        rafter_spacing=0.6,
        plate_size=(0.038, 0.184),
        rafter_size=(0.038, 0.184),
        hip_extra_depth=0.050,
        ridge_size=(0.038, 0.184)):
    """
    Build a simple rectangular hip roof:

    - Ridge along the long axis (X).
    - Four hips from ridge ends to plan corners.
    - Common rafters from long walls to the ridge.
    - Perimeter plates representing top wall plates.

    Parameters are approximate and can be adapted to match
    your design or the span tables from the manual.
    """

    # Orient building so:
    #   X = length direction (long side)
    #   Y = width  direction (short side)
    half_L = length * 0.5
    half_W = width * 0.5

    # Compute ridge height from common rafter run and slope
    # Assume the run for common rafters is half the width
    # (rafters from long walls up to ridge at Y=0)
    run_common = half_W
    ridge_height = run_common * (slope_rise / slope_run)

    # Ridge length for a 'standard' hip: L_ridge = L - W
    ridge_len = max(length - width, 0.0)
    ridge_half = ridge_len * 0.5

    # ------------------------------------------------------------------
    # 1) Perimeter plates (top plates of exterior walls)
    # ------------------------------------------------------------------
    plate_w, plate_d = plate_size

    # Long side plates (parallel to X)
    create_prismatic_member(
        "Plate_Long_N",
        start=(-half_L,  half_W, plate_z),
        end=( half_L,  half_W, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Plate_Long_S",
        start=(-half_L, -half_W, plate_z),
        end=( half_L, -half_W, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # Short side plates (parallel to Y)
    create_prismatic_member(
        "Plate_Short_W",
        start=(-half_L, -half_W, plate_z),
        end=(-half_L,  half_W, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Plate_Short_E",
        start=( half_L, -half_W, plate_z),
        end=( half_L,  half_W, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # ------------------------------------------------------------------
    # 2) Ridge board (horizontal member at ridge height)
    # ------------------------------------------------------------------
    ridge_w, ridge_d = ridge_size

    # If ridge_len == 0, we have a pyramid roof; in that case, skip ridge
    if ridge_len > 0.0:
        ridge_start = (-ridge_half, 0.0, ridge_height)
        ridge_end   = ( ridge_half, 0.0, ridge_height)
        create_prismatic_member(
            "Ridge_Board",
            start=ridge_start,
            end=ridge_end,
            width=ridge_w,
            depth=ridge_d,
        )

    # ------------------------------------------------------------------
    # 3) Hip rafters
    # ------------------------------------------------------------------
    # Corners (top of walls)
    corner_NW = (-half_L,  half_W, plate_z)
    corner_NE = ( half_L,  half_W, plate_z)
    corner_SW = (-half_L, -half_W, plate_z)
    corner_SE = ( half_L, -half_W, plate_z)

    # Ridge endpoints for hips
    if ridge_len > 0.0:
        ridge_W = (-ridge_half, 0.0, ridge_height)
        ridge_E = ( ridge_half, 0.0, ridge_height)
    else:
        # Pyramid hip: single apex at center
        ridge_W = (0.0, 0.0, ridge_height)
        ridge_E = ridge_W

    hip_w, hip_d_base = rafter_size
    hip_d = hip_d_base + hip_extra_depth  # deeper than common rafters

    # Four hips
    create_prismatic_member("Hip_NW", corner_NW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SW", corner_SW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_NE", corner_NE, ridge_E,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SE", corner_SE, ridge_E,
                            width=hip_w, depth=hip_d)

    # ------------------------------------------------------------------
    # 4) Common rafters along long sides
    # ------------------------------------------------------------------
    # We place common rafters only where they connect directly to the ridge
    # (between -ridge_half and +ridge_half). Jack rafters to the hips
    # can be added using similar logic, but are omitted here for clarity.
    raf_w, raf_d = rafter_size

    if ridge_len > 0.0:
        # Number of rafter positions along the ridge
        n_steps = max(int(ridge_len / rafter_spacing), 1)
        for i in range(n_steps + 1):
            # x coordinate along ridge
            t = i / max(n_steps, 1)
            x = -ridge_half + t * ridge_len

            # North side common rafter
            plate_N = (x,  half_W, plate_z)
            ridge_pt = (x, 0.0, ridge_height)
            create_prismatic_member(
                f"Rafter_N_{i:02d}",
                start=plate_N,
                end=ridge_pt,
                width=raf_w,
                depth=raf_d,
            )

            # South side common rafter
            plate_S = (x, -half_W, plate_z)
            create_prismatic_member(
                f"Rafter_S_{i:02d}",
                start=plate_S,
                end=ridge_pt,
                width=raf_w,
                depth=raf_d,
            )
    else:
        # Pyramid roof: common rafters from all four sides to the apex
        apex = ridge_W  # same as ridge_E
        # North and south (long sides)
        n_steps_long = max(int(length / rafter_spacing), 1)
        for i in range(n_steps_long + 1):
            t = i / max(n_steps_long, 1)
            x = -half_L + t * length

            plate_N = (x,  half_W, plate_z)
            plate_S = (x, -half_W, plate_z)

            create_prismatic_member(
                f"Rafter_N_{i:02d}",
                start=plate_N,
                end=apex,
                width=raf_w,
                depth=raf_d,
            )
            create_prismatic_member(
                f"Rafter_S_{i:02d}",
                start=plate_S,
                end=apex,
                width=raf_w,
                depth=raf_d,
            )

        # East and west (short sides)
        n_steps_short = max(int(width / rafter_spacing), 1)
        for i in range(n_steps_short + 1):
            t = i / max(n_steps_short, 1)
            y = -half_W + t * width

            plate_W = (-half_L, y, plate_z)
            plate_E = ( half_L, y, plate_z)

            create_prismatic_member(
                f"Rafter_W_{i:02d}",
                start=plate_W,
                end=apex,
                width=raf_w,
                depth=raf_d,
            )
            create_prismatic_member(
                f"Rafter_E_{i:02d}",
                start=plate_E,
                end=apex,
                width=raf_w,
                depth=raf_d,
            )


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Example: 8 m × 6 m plan, 1:3 slope, rafters at 0.6 m o.c.
    build_simple_hip_roof(
        length=8.0,
        width=6.0,
        plate_z=0.0,
        slope_rise=1.0,
        slope_run=3.0,
        rafter_spacing=0.6,
        plate_size=(0.038, 0.140),
        rafter_size=(0.038, 0.184),
        hip_extra_depth=0.050,
        ridge_size=(0.038, 0.184),
    )
