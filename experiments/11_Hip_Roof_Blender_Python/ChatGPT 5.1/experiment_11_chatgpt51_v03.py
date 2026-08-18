# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 - CHATGPT 5.1 - V03
# HIP ROOF
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix

import importlib
import craftbot_lib as craftbot
importlib.reload(craftbot)


def create_prismatic_member(name, start, end,
                            width=0.038,
                            depth=0.184):
    """
    Create a rectangular-prism element between two points using craftbot.place_element.

    Local Z axis is aligned with the member axis, local X/Y define the cross-section (width/depth).
    """
    p0 = Vector(start)
    p1 = Vector(end)
    direction = p1 - p0
    length = direction.length
    if length == 0:
        return

    axis_z = direction.normalized()

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

    S = Matrix.Diagonal((width / 2.0,
                         depth / 2.0,
                         length / 2.0,
                         1.0))

    mid = (p0 + p1) * 0.5
    T = Matrix.Translation(mid)

    M_world = T @ R4 @ S

    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


def build_main_hip_roof(length,
                        width,
                        plate_z,
                        slope_rise,
                        slope_run,
                        rafter_spacing,
                        plate_size,
                        rafter_size,
                        hip_extra_depth,
                        ridge_size):
    """
    Build the main hip roof with common rafters, jack rafters, hips,
    king rafters at each hip end, and ceiling joists.
    Returns a dict with key reference dimensions for further additions.
    """
    half_L = length * 0.5
    half_W = width * 0.5

    # Common rafter run is half the building width
    run_common = half_W
    ridge_height = run_common * (slope_rise / slope_run)

    ridge_len = max(length - width, 0.0)
    ridge_half = ridge_len * 0.5

    plate_w, plate_d = plate_size
    raf_w, raf_d = rafter_size
    ridge_w, ridge_d = ridge_size
    hip_w, hip_d = raf_w, raf_d + hip_extra_depth

    # ---------------- Plates ----------------
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

    # ---------------- Ridge ----------------
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

    # ---------------- Corners and ridge ends ----------------
    corner_NW = Vector((-half_L,  half_W, plate_z))
    corner_NE = Vector(( half_L,  half_W, plate_z))
    corner_SW = Vector((-half_L, -half_W, plate_z))
    corner_SE = Vector(( half_L, -half_W, plate_z))

    if ridge_len > 0.0:
        ridge_W = Vector((-ridge_half, 0.0, ridge_height))
        ridge_E = Vector(( ridge_half, 0.0, ridge_height))
    else:
        ridge_W = ridge_E = Vector((0.0, 0.0, ridge_height))

    hips = {
        "NW": (corner_NW, ridge_W),
        "SW": (corner_SW, ridge_W),
        "NE": (corner_NE, ridge_E),
        "SE": (corner_SE, ridge_E),
    }

    # ---------------- Hip rafters ----------------
    create_prismatic_member("Hip_NW", corner_NW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SW", corner_SW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_NE", corner_NE, ridge_E,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SE", corner_SE, ridge_E,
                            width=hip_w, depth=hip_d)

    # ---------------- Common rafters along N and S ----------------
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
        # Square/pyramidal case (not used for current T-roof, but kept for completeness)
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

        # No jacks / kings in this branch
        return dict(
            length=length,
            width=width,
            half_L=half_L,
            half_W=half_W,
            ridge_len=ridge_len,
            ridge_half=ridge_half,
            ridge_height=ridge_height,
            plate_z=plate_z,
            slope_rise=slope_rise,
            slope_run=slope_run,
            rafter_spacing=rafter_spacing,
            rafter_size=rafter_size,
        )

    # ---------------- Jack rafters to hips (N/S sides) ----------------
    eps = 1e-6

    # West of ridge -> hips NW/SW
    x = -half_L + rafter_spacing
    while x < -ridge_half - eps:
        hip_p0, hip_p1 = hips["NW"]
        t = (x - hip_p0.x) / (hip_p1.x - hip_p0.x)
        hip_pt_N = hip_p0.lerp(hip_p1, t)

        plate_N = (x, half_W, plate_z)
        create_prismatic_member(
            f"Jack_NW_N_{x:.2f}",
            start=plate_N,
            end=hip_pt_N,
            width=raf_w,
            depth=raf_d,
        )

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

    # East of ridge -> hips NE/SE
    x = ridge_half + rafter_spacing
    while x < half_L - eps:
        hip_p0, hip_p1 = hips["NE"]
        t = (x - hip_p0.x) / (hip_p1.x - hip_p0.x)
        hip_pt_N = hip_p0.lerp(hip_p1, t)

        plate_N = (x, half_W, plate_z)
        create_prismatic_member(
            f"Jack_NE_N_{x:.2f}",
            start=plate_N,
            end=hip_pt_N,
            width=raf_w,
            depth=raf_d,
        )

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

    # ---------------- Jack rafters to hips (W/E sides) ----------------
    # North half (y > 0)
    y = 0.0 + rafter_spacing
    while y < half_W - eps:
        hip_p0, hip_p1 = hips["NW"]
        t = (y - hip_p0.y) / (hip_p1.y - hip_p0.y)
        hip_pt_NW = hip_p0.lerp(hip_p1, t)

        plate_W = (-half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_NW_W_{y:.2f}",
            start=plate_W,
            end=hip_pt_NW,
            width=raf_w,
            depth=raf_d,
        )

        hip_p0_E, hip_p1_E = hips["NE"]
        t_e = (y - hip_p0_E.y) / (hip_p1_E.y - hip_p0_E.y)
        hip_pt_NE = hip_p0_E.lerp(hip_p1_E, t_e)

        plate_E = (half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_NE_E_{y:.2f}",
            start=plate_E,
            end=hip_pt_NE,
            width=raf_w,
            depth=raf_d,
        )

        y += rafter_spacing

    # South half (y < 0)
    y = -rafter_spacing
    while y > -half_W + eps:
        hip_p0, hip_p1 = hips["SW"]
        t = (y - hip_p0.y) / (hip_p1.y - hip_p0.y)
        hip_pt_SW = hip_p0.lerp(hip_p1, t)

        plate_W = (-half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_SW_W_{y:.2f}",
            start=plate_W,
            end=hip_pt_SW,
            width=raf_w,
            depth=raf_d,
        )

        hip_p0_E, hip_p1_E = hips["SE"]
        t_e = (y - hip_p0_E.y) / (hip_p1_E.y - hip_p0_E.y)
        hip_pt_SE = hip_p0_E.lerp(hip_p1_E, t_e)

        plate_E = (half_L, y, plate_z)
        create_prismatic_member(
            f"Jack_SE_E_{y:.2f}",
            start=plate_E,
            end=hip_pt_SE,
            width=raf_w,
            depth=raf_d,
        )

        y -= rafter_spacing

    # ---------------- King rafters at each hip end ----------------
    # Ridge end to centre of each short side (end wall)
    king_W_start = (-ridge_half, 0.0, ridge_height)
    king_W_end   = (-half_L,   0.0, plate_z)
    create_prismatic_member(
        "King_Rafter_W",
        start=king_W_start,
        end=king_W_end,
        width=raf_w,
        depth=raf_d,
    )

    king_E_start = ( ridge_half, 0.0, ridge_height)
    king_E_end   = ( half_L,   0.0, plate_z)
    create_prismatic_member(
        "King_Rafter_E",
        start=king_E_start,
        end=king_E_end,
        width=raf_w,
        depth=raf_d,
    )

    # ---------------- Ceiling joists across the building ----------------
    joist_z = plate_z - 0.18  # drop the joists slightly below the wall plates
    n_joists = max(int(width / rafter_spacing), 1)
    for i in range(n_joists + 1):
        t = i / max(n_joists, 1)
        y = -half_W + t * width
        create_prismatic_member(
            f"Ceiling_Joist_{i:02d}",
            start=(-half_L, y, joist_z),
            end=( half_L, y, joist_z),
            width=raf_w,
            depth=plate_d,
        )

    return dict(
        length=length,
        width=width,
        half_L=half_L,
        half_W=half_W,
        ridge_len=ridge_len,
        ridge_half=ridge_half,
        ridge_height=ridge_height,
        plate_z=plate_z,
        slope_rise=slope_rise,
        slope_run=slope_run,
        rafter_spacing=rafter_spacing,
        rafter_size=rafter_size,
    )


def build_T_wing(main_geom,
                 wing_length=6.0,
                 wing_width=6.0,
                 plate_z=0.0,
                 slope_rise=1.0,
                 slope_run=2.0,
                 rafter_spacing=0.6,
                 plate_size=(0.038, 0.140),
                 rafter_size=(0.038, 0.184)):
    """
    Build a simple gable-roofed wing attached on the south side of the main
    building, forming a T-shaped roof in plan.
    """
    half_L_main = main_geom["half_L"]
    half_W_main = main_geom["half_W"]

    half_Wx = wing_width * 0.5
    half_Ly = wing_length * 0.5

    # Plan position: centre of wing aligned with x=0, attaching at south wall
    center_x = 0.0
    center_y = -half_W_main - half_Ly

    plate_w, plate_d = plate_size
    raf_w, raf_d = rafter_size

    # Plates (east-west) at north and south edges of the wing
    y_N = center_y + half_Ly
    y_S = center_y - half_Ly

    create_prismatic_member(
        "Wing_Plate_N",
        start=(center_x - half_Wx, y_N, plate_z),
        end=(center_x + half_Wx, y_N, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Wing_Plate_S",
        start=(center_x - half_Wx, y_S, plate_z),
        end=(center_x + half_Wx, y_S, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # Gable-end plates (north-south)
    create_prismatic_member(
        "Wing_Plate_W",
        start=(center_x - half_Wx, y_S, plate_z),
        end=(center_x - half_Wx, y_N, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Wing_Plate_E",
        start=(center_x + half_Wx, y_S, plate_z),
        end=(center_x + half_Wx, y_N, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # Ridge along X (east-west)
    run = wing_length * 0.5
    ridge_height = run * (slope_rise / slope_run)
    ridge_start = (center_x - half_Wx, center_y, ridge_height)
    ridge_end   = (center_x + half_Wx, center_y, ridge_height)
    create_prismatic_member(
        "Wing_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Common rafters from north and south plates to ridge
    n_steps = max(int(wing_width / rafter_spacing), 1)
    for i in range(n_steps + 1):
        t = i / max(n_steps, 1)
        x = center_x - half_Wx + t * wing_width

        plate_N = (x, y_N, plate_z)
        plate_S = (x, y_S, plate_z)
        ridge_pt = (x, center_y, ridge_height)

        create_prismatic_member(
            f"Wing_Rafter_N_{i:02d}",
            start=plate_N,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )
        create_prismatic_member(
            f"Wing_Rafter_S_{i:02d}",
            start=plate_S,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )


def build_simple_dormer(main_geom,
                        dormer_width=3.0,
                        dormer_depth=2.0,
                        dormer_height=1.0,
                        plate_z=0.0,
                        slope_rise=1.0,
                        slope_run=2.0,
                        rafter_size=(0.038, 0.184)):
    """
    Build a small gable dormer on the north side of the main roof.
    This is a simplified geometric representation, not full structural framing.
    """
    half_L = main_geom["half_L"]
    half_W = main_geom["half_W"]
    ridge_height = main_geom["ridge_height"]

    raf_w, raf_d = rafter_size

    # Position dormer roughly centred in X on north slope
    center_x = 0.0
    base_y = half_W * 0.5  # centre of north slope
    wall_top_z = plate_z + dormer_height

    half_dorm_Wx = dormer_width * 0.5
    half_dorm_Ly = dormer_depth * 0.5

    # Top plates of dormer walls (front/back & sides)
    y_front = base_y + half_dorm_Ly
    y_back  = base_y - half_dorm_Ly

    create_prismatic_member(
        "Dormer_Plate_Front",
        start=(center_x - half_dorm_Wx, y_front, wall_top_z),
        end=(center_x + half_dorm_Wx, y_front, wall_top_z),
        width=raf_w,
        depth=raf_d,
    )
    create_prismatic_member(
        "Dormer_Plate_Back",
        start=(center_x - half_dorm_Wx, y_back, wall_top_z),
        end=(center_x + half_dorm_Wx, y_back, wall_top_z),
        width=raf_w,
        depth=raf_d,
    )
    create_prismatic_member(
        "Dormer_Plate_W",
        start=(center_x - half_dorm_Wx, y_back, wall_top_z),
        end=(center_x - half_dorm_Wx, y_front, wall_top_z),
        width=raf_w,
        depth=raf_d,
    )
    create_prismatic_member(
        "Dormer_Plate_E",
        start=(center_x + half_dorm_Wx, y_back, wall_top_z),
        end=(center_x + half_dorm_Wx, y_front, wall_top_z),
        width=raf_w,
        depth=raf_d,
    )

    # Dormer ridge (parallel to main ridge)
    run = dormer_depth * 0.5
    ridge_height_local = run * (slope_rise / slope_run)
    dormer_ridge_z = wall_top_z + ridge_height_local
    ridge_start = (center_x - half_dorm_Wx, base_y, dormer_ridge_z)
    ridge_end   = (center_x + half_dorm_Wx, base_y, dormer_ridge_z)
    create_prismatic_member(
        "Dormer_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Dormer rafters (front/back)
    n_steps = max(int(dormer_width / 0.6), 1)
    for i in range(n_steps + 1):
        t = i / max(n_steps, 1)
        x = center_x - half_dorm_Wx + t * dormer_width

        plate_front = (x, y_front, wall_top_z)
        plate_back  = (x, y_back, wall_top_z)
        ridge_pt    = (x, base_y, dormer_ridge_z)

        create_prismatic_member(
            f"Dormer_Rafter_F_{i:02d}",
            start=plate_front,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )
        create_prismatic_member(
            f"Dormer_Rafter_B_{i:02d}",
            start=plate_back,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )

    # Simple "valley-like" members tying dormer back towards main roof eave
    valley_y_main = half_W
    valley_z_main = plate_z  # main eave level
    left_top   = (center_x - half_dorm_Wx, y_back, wall_top_z)
    right_top  = (center_x + half_dorm_Wx, y_back, wall_top_z)
    left_base  = (center_x - half_dorm_Wx, valley_y_main, valley_z_main)
    right_base = (center_x + half_dorm_Wx, valley_y_main, valley_z_main)

    create_prismatic_member(
        "Dormer_Valley_L",
        start=left_top,
        end=left_base,
        width=raf_w,
        depth=raf_d * 1.25,
    )
    create_prismatic_member(
        "Dormer_Valley_R",
        start=right_top,
        end=right_base,
        width=raf_w,
        depth=raf_d * 1.25,
    )


def build_scene():
    # Main roof parameters
    length = 12.0   # along X – longer than before
    width = 6.0     # along Y
    plate_z = 0.0

    slope_rise = 1.0
    slope_run = 2.0   # steeper roof (1:2 instead of 1:3)
    rafter_spacing = 0.6

    plate_size = (0.038, 0.140)
    rafter_size = (0.038, 0.184)
    ridge_size = (0.038, 0.184)
    hip_extra_depth = 0.050

    # Main hip roof with king rafters + ceiling joists
    main_geom = build_main_hip_roof(
        length=length,
        width=width,
        plate_z=plate_z,
        slope_rise=slope_rise,
        slope_run=slope_run,
        rafter_spacing=rafter_spacing,
        plate_size=plate_size,
        rafter_size=rafter_size,
        hip_extra_depth=hip_extra_depth,
        ridge_size=ridge_size,
    )

    # South T-wing (simple gable roof)
    build_T_wing(
        main_geom=main_geom,
        wing_length=6.0,
        wing_width=6.0,
        plate_z=plate_z,
        slope_rise=slope_rise,
        slope_run=slope_run,
        rafter_spacing=rafter_spacing,
        plate_size=plate_size,
        rafter_size=rafter_size,
    )

    # North dormer (simplified, based on manual's dormer concept)
    build_simple_dormer(
        main_geom=main_geom,
        dormer_width=3.0,
        dormer_depth=2.0,
        dormer_height=1.0,
        plate_z=plate_z,
        slope_rise=slope_rise,
        slope_run=slope_run,
        rafter_size=rafter_size,
    )


if __name__ == "__main__":
    build_scene()
