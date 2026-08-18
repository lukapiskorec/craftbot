# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 - CHATGPT 5.1 - V02
# HIP ROOF
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix

import importlib
import craftbot_lib as craftbot  # ensure this is on sys.path
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
        return

    axis_z = direction.normalized()

    # Choose a stable 'up' vector
    world_up = Vector((0.0, 0.0, 1.0))
    if abs(axis_z.dot(world_up)) > 0.99:
        world_up = Vector((0.0, 1.0, 0.0))

    axis_x = world_up.cross(axis_z).normalized()
    axis_y = axis_z.cross(axis_x).normalized()

    R = Matrix((
        (axis_x.x, axis_y.x, axis_z.x),
        (axis_x.y, axis_y.y, axis_z.y),
        (axis_x.z, axis_y.z, axis_z.z),
    ))
    R4 = R.to_4x4()

    S = Matrix.Diagonal((
        width / 2.0,
        depth / 2.0,
        length / 2.0,
        1.0
    ))

    mid = (p0 + p1) * 0.5
    T = Matrix.Translation(mid)

    M_world = T @ R4 @ S

    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


# ------------------------------------------------------------------
# HIP ROOF GEOMETRY
# ------------------------------------------------------------------

def build_simple_hip_roof(
        length=12.0,
        width=6.0,
        plate_z=0.0,
        slope_rise=1.0,
        slope_run=3.0,
        rafter_spacing=0.6,
        plate_size=(0.038, 0.140),
        rafter_size=(0.038, 0.184),
        hip_extra_depth=0.050,
        ridge_size=(0.038, 0.184)):
    """
    Build a rectangular hip roof:

    - Ridge along the long axis (X).
    - Four hips from ridge ends to plan corners.
    - Common rafters from long walls to the ridge.
    - Jack rafters from plates to hips on all sides.
    - Perimeter plates representing top wall plates.
    """

    # Basic plan dimensions
    half_L = length * 0.5
    half_W = width * 0.5

    # Common rafter geometry
    run_common = half_W
    ridge_height = run_common * (slope_rise / slope_run)

    ridge_len = max(length - width, 0.0)
    ridge_half = ridge_len * 0.5

    # ------------------------------------------------------------------
    # 1) Perimeter plates
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
    # 2) Ridge board
    # ------------------------------------------------------------------
    ridge_w, ridge_d = ridge_size

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
    corner_NW = Vector((-half_L,  half_W, plate_z))
    corner_NE = Vector(( half_L,  half_W, plate_z))
    corner_SW = Vector((-half_L, -half_W, plate_z))
    corner_SE = Vector(( half_L, -half_W, plate_z))

    if ridge_len > 0.0:
        ridge_W = Vector((-ridge_half, 0.0, ridge_height))
        ridge_E = Vector(( ridge_half, 0.0, ridge_height))
    else:
        ridge_W = ridge_E = Vector((0.0, 0.0, ridge_height))

    raf_w, raf_d = rafter_size
    hip_w, hip_d = raf_w, raf_d + hip_extra_depth

    hips = {
        "NW": (corner_NW, ridge_W),
        "SW": (corner_SW, ridge_W),
        "NE": (corner_NE, ridge_E),
        "SE": (corner_SE, ridge_E),
    }

    create_prismatic_member("Hip_NW", corner_NW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SW", corner_SW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_NE", corner_NE, ridge_E,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SE", corner_SE, ridge_E,
                            width=hip_w, depth=hip_d)

    # ------------------------------------------------------------------
    # 4) Common rafters along long sides (to ridge)
    # ------------------------------------------------------------------
    if ridge_len > 0.0:
        n_steps = max(int(ridge_len / rafter_spacing), 1)
        for i in range(n_steps + 1):
            t = i / max(n_steps, 1)
            x = -ridge_half + t * ridge_len

            plate_N = (x,  half_W, plate_z)
            plate_S = (x, -half_W, plate_z)
            ridge_pt = (x, 0.0, ridge_height)

            create_prismatic_member(
                f"Rafter_N_{i:02d}",
                start=plate_N,
                end=ridge_pt,
                width=raf_w,
                depth=raf_d,
            )
            create_prismatic_member(
                f"Rafter_S_{i:02d}",
                start=plate_S,
                end=ridge_pt,
                width=raf_w,
                depth=raf_d,
            )
    else:
        # Pyramid case: rafters from all sides to single apex
        apex = ridge_W
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

    # If there's no ridge, there is no "jack" concept – return early
    if ridge_len <= 0.0:
        return

    # ------------------------------------------------------------------
    # 5) Jack rafters along long sides (N & S) to hips
    # ------------------------------------------------------------------
    eps = 1e-6

    # NORTH/SOUTH – west segment -> hips NW / SW
    x = -half_L + rafter_spacing
    while x < -ridge_half - eps:
        # North to hip NW
        hip_p0, hip_p1 = hips["NW"]
        t = (x - hip_p0.x) / (hip_p1.x - hip_p0.x)
        hip_pt = hip_p0.lerp(hip_p1, t)

        plate_N = (x, half_W, plate_z)
        create_prismatic_member(
            f"Jack_NW_N_{x:.2f}",
            start=plate_N,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )

        # South to hip SW
        hip_p0_S, hip_p1_S = hips["SW"]
        t_s = (x - hip_p0_S.x) / (hip_p1_S.x - hip_p0_S.x)
        hip_pt_S = hip_p0_S.lerp(hip_p1_S, t_s)

        plate_S = (x, -half_W, plate_z)
        create_prismatic_member(
            f"Jack_SW_S_{x:.2f}",
            start=plate_S,
            end=hip_pt_S,
            width=raf_w,
            depth=raf_d,
        )

        x += rafter_spacing

    # NORTH/SOUTH – east segment -> hips NE / SE
    x = ridge_half + rafter_spacing
    while x < half_L - eps:
        # North to hip NE
        hip_p0, hip_p1 = hips["NE"]
        t = (x - hip_p0.x) / (hip_p1.x - hip_p0.x)
        hip_pt = hip_p0.lerp(hip_p1, t)

        plate_N = (x, half_W, plate_z)
        create_prismatic_member(
            f"Jack_NE_N_{x:.2f}",
            start=plate_N,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )

        # South to hip SE
        hip_p0_S, hip_p1_S = hips["SE"]
        t_s = (x - hip_p0_S.x) / (hip_p1_S.x - hip_p0_S.x)
        hip_pt_S = hip_p0_S.lerp(hip_p1_S, t_s)

        plate_S = (x, -half_W, plate_z)
        create_prismatic_member(
            f"Jack_SE_S_{x:.2f}",
            start=plate_S,
            end=hip_pt_S,
            width=raf_w,
            depth=raf_d,
        )

        x += rafter_spacing

    # ------------------------------------------------------------------
    # 6) Jack rafters along short sides (W & E) to hips
    # ------------------------------------------------------------------
    # WEST wall:  0 < y < +half_W -> hip NW;   -half_W < y < 0 -> hip SW
    y = 0.0 + rafter_spacing
    while y < half_W - eps:
        # West to hip NW
        hip_p0, hip_p1 = hips["NW"]
        t = (y - hip_p0.y) / (hip_p1.y - hip_p0.y)
        hip_pt = hip_p0.lerp(hip_p1, t)

        plate_W = (-half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_NW_W_{y:.2f}",
            start=plate_W,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )

        # East to hip NE
        hip_p0_E, hip_p1_E = hips["NE"]
        t_e = (y - hip_p0_E.y) / (hip_p1_E.y - hip_p0_E.y)
        hip_pt_E = hip_p0_E.lerp(hip_p1_E, t_e)

        plate_E = (half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_NE_E_{y:.2f}",
            start=plate_E,
            end=hip_pt_E,
            width=raf_w,
            depth=raf_d,
        )

        y += rafter_spacing

    y = -rafter_spacing
    while y > -half_W + eps:
        # West to hip SW
        hip_p0, hip_p1 = hips["SW"]
        t = (y - hip_p0.y) / (hip_p1.y - hip_p0.y)
        hip_pt = hip_p0.lerp(hip_p1, t)

        plate_W = (-half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_SW_W_{y:.2f}",
            start=plate_W,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )

        # East to hip SE
        hip_p0_E, hip_p1_E = hips["SE"]
        t_e = (y - hip_p0_E.y) / (hip_p1_E.y - hip_p0_E.y)
        hip_pt_E = hip_p0_E.lerp(hip_p1_E, t_e)

        plate_E = (half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_SE_E_{y:.2f}",
            start=plate_E,
            end=hip_pt_E,
            width=raf_w,
            depth=raf_d,
        )

        y -= rafter_spacing


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Example: 12 m × 6 m plan, 1:3 slope, rafters at 0.6 m o.c.
    build_simple_hip_roof(
        length=12.0,
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
