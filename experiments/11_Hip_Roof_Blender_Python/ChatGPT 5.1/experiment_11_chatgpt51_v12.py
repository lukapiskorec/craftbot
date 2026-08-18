# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 - CHATGPT 5.1 - V12
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
    """Rectangular member between two points, oriented along the segment."""
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


# ---------------------------------------------------------------------------
# MAIN HIP ROOF
# ---------------------------------------------------------------------------

def build_main_hip_roof(length,
                        width,
                        plate_z,
                        slope_rise,
                        slope_run,
                        rafter_spacing,
                        plate_size,
                        rafter_size,
                        hip_extra_depth,
                        ridge_size,
                        north_clear_range=None,
                        south_clear_half_x=None):

    half_L = length * 0.5
    half_W = width * 0.5
    k = slope_rise / slope_run

    run_common = half_W
    ridge_height = run_common * k

    ridge_len = max(length - width, 0.0)
    ridge_half = ridge_len * 0.5

    plate_w, plate_d = plate_size
    raf_w, raf_d = rafter_size
    ridge_w, ridge_d = ridge_size
    hip_w, hip_d = raf_w, raf_d + hip_extra_depth

    # Plates
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

    # Ridge
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

    # Corners
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

    # Hip rafters
    create_prismatic_member("Hip_NW", corner_NW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SW", corner_SW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_NE", corner_NE, ridge_E,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SE", corner_SE, ridge_E,
                            width=hip_w, depth=hip_d)

    # Common rafters N/S
    if ridge_len > 0.0:
        n_steps = max(int(ridge_len / rafter_spacing), 1)
        for i in range(n_steps + 1):
            t = i / max(n_steps, 1)
            x = -ridge_half + t * ridge_len

            skip_N = False
            if north_clear_range is not None:
                x_min, x_max = north_clear_range
                if x_min < x < x_max:
                    skip_N = True

            skip_S = False
            if south_clear_half_x is not None:
                if abs(x) <= south_clear_half_x + 1e-6:
                    skip_S = True

            ridge_pt = (x, 0.0, ridge_height)

            if not skip_N:
                plate_N = (x, half_W, plate_z)
                create_prismatic_member(
                    f"Rafter_N_{i:02d}",
                    start=plate_N,
                    end=ridge_pt,
                    width=raf_w,
                    depth=raf_d,
                )

            if not skip_S:
                plate_S = (x, -half_W, plate_z)
                create_prismatic_member(
                    f"Rafter_S_{i:02d}",
                    start=plate_S,
                    end=ridge_pt,
                    width=raf_w,
                    depth=raf_d,
                )

    # Jack rafters around hips
    eps = 1e-6

    # N/S - west of ridge
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

    # N/S - east of ridge
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

    # W/E - north half
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

    # W/E - south half
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

    # King rafters on short ends
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

    # Ceiling joists spanning Y (short direction)
    joist_z = plate_z - 0.18
    n_joists = max(int(length / rafter_spacing), 1)
    for i in range(n_joists + 1):
        t = i / max(n_joists, 1)
        x = -half_L + t * length
        create_prismatic_member(
            f"Ceiling_Joist_{i:02d}",
            start=(x, -half_W, joist_z),
            end=(x,  half_W, joist_z),
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
        plate_size=plate_size,
    )


# ---------------------------------------------------------------------------
# T-WING (SOUTH) – RIDGE EXTENDED TO VALLEY INTERSECTION
# ---------------------------------------------------------------------------

def build_T_wing_rotated(main_geom,
                         wing_length=6.0,
                         wing_width=6.0):
    half_L = main_geom["half_L"]
    half_W = main_geom["half_W"]
    ridge_height_main = main_geom["ridge_height"]
    plate_z = main_geom["plate_z"]
    slope_rise = main_geom["slope_rise"]
    slope_run = main_geom["slope_run"]
    rafter_spacing = main_geom["rafter_spacing"]
    rafter_size = main_geom["rafter_size"]
    plate_size = main_geom["plate_size"]

    k = slope_rise / slope_run
    raf_w, raf_d = rafter_size
    plate_w, plate_d = plate_size

    wing_half_X = wing_width * 0.5
    wing_len_Y = wing_length

    y_north = -half_W
    y_south = -half_W - wing_len_Y

    ridge_height_wing = plate_z + wing_half_X * k

    # Main south roof plane
    Pm1 = Vector((-half_L, -half_W, plate_z))
    Pm2 = Vector(( half_L, -half_W, plate_z))
    Pm3 = Vector(( 0.0,    0.0,    ridge_height_main))
    n_main = (Pm2 - Pm1).cross(Pm3 - Pm1)
    d_main = -n_main.dot(Pm1)

    # Intersection of wing ridge height with main south plane
    z_ridge = ridge_height_wing
    y_valley_top = -(n_main.z * z_ridge + d_main) / n_main.y
    valley_top = Vector((0.0, y_valley_top, z_ridge))

    # Wing ridge from valley intersection to south gable
    ridge_start = (0.0, y_south, ridge_height_wing)
    ridge_end   = (0.0, y_valley_top, ridge_height_wing)
    create_prismatic_member(
        "Wing_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Wing plates
    create_prismatic_member(
        "Wing_Plate_E",
        start=( wing_half_X, y_south, plate_z),
        end=( wing_half_X, y_north, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Wing_Plate_W",
        start=(-wing_half_X, y_south, plate_z),
        end=(-wing_half_X, y_north, plate_z),
        width=plate_w,
        depth=plate_d,
    )
    create_prismatic_member(
        "Wing_Plate_S",
        start=(-wing_half_X, y_south, plate_z),
        end=( wing_half_X, y_south, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # Wing common rafters
    n_steps = max(int(wing_length / rafter_spacing), 1)
    for i in range(n_steps + 1):
        t = i / max(n_steps, 1)
        y = y_north - t * wing_len_Y
        ridge_pt = (0.0, y, ridge_height_wing)

        plate_E = ( wing_half_X, y, plate_z)
        plate_W = (-wing_half_X, y, plate_z)

        create_prismatic_member(
            f"Wing_Rafter_E_{i:02d}",
            start=plate_E,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )
        create_prismatic_member(
            f"Wing_Rafter_W_{i:02d}",
            start=plate_W,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )

    # Valleys
    valley_bottom_E = Vector(( wing_half_X, -half_W, plate_z))
    valley_bottom_W = Vector((-wing_half_X, -half_W, plate_z))

    create_prismatic_member(
        "Valley_E",
        start=valley_top,
        end=valley_bottom_E,
        width=raf_w,
        depth=raf_d * 1.25,
    )
    create_prismatic_member(
        "Valley_W",
        start=valley_top,
        end=valley_bottom_W,
        width=raf_w,
        depth=raf_d * 1.25,
    )

    # Valley jacks from main ridge to valleys
    n_jacks = 4
    for j in range(1, n_jacks + 1):
        s = j / (n_jacks + 1)
        vE = valley_top.lerp(valley_bottom_E, s)
        ridge_pt = Vector((vE.x, 0.0, ridge_height_main))
        create_prismatic_member(
            f"Valley_Jack_E_{j:02d}",
            start=ridge_pt,
            end=vE,
            width=raf_w,
            depth=raf_d,
        )
    for j in range(1, n_jacks + 1):
        s = j / (n_jacks + 1)
        vW = valley_top.lerp(valley_bottom_W, s)
        ridge_pt = Vector((vW.x, 0.0, ridge_height_main))
        create_prismatic_member(
            f"Valley_Jack_W_{j:02d}",
            start=ridge_pt,
            end=vW,
            width=raf_w,
            depth=raf_d,
        )

    # New central valley jack from main ridge to the Wing_Ridge / valley intersection
    center_ridge_pt = Vector((0.0, 0.0, ridge_height_main))
    create_prismatic_member(
        "Valley_Jack_Center",
        start=center_ridge_pt,
        end=valley_top,
        width=raf_w,
        depth=raf_d,
    )

    # Wing-side valley jacks between Wing_Ridge and valleys
    n_wing_jacks = 4
    for j in range(1, n_wing_jacks + 1):
        s = j / (n_wing_jacks + 1)
        vE = valley_top.lerp(valley_bottom_E, s)
        rE = Vector((0.0, vE.y, ridge_height_wing))
        create_prismatic_member(
            f"Wing_Valley_Jack_E_{j:02d}",
            start=rE,
            end=vE,
            width=raf_w,
            depth=raf_d,
        )

        vW = valley_top.lerp(valley_bottom_W, s)
        rW = Vector((0.0, vW.y, ridge_height_wing))
        create_prismatic_member(
            f"Wing_Valley_Jack_W_{j:02d}",
            start=rW,
            end=vW,
            width=raf_w,
            depth=raf_d,
        )

    # Ceiling joists in the wing, running W–E
    joist_z = plate_z - 0.18
    n_wing_joists = max(int(wing_length / rafter_spacing), 1)
    for i in range(n_wing_joists + 1):
        t = i / max(n_wing_joists, 1)
        y = y_south + t * wing_len_Y
        create_prismatic_member(
            f"Wing_Ceiling_Joist_{i:02d}",
            start=(-wing_half_X, y, joist_z),
            end=( wing_half_X, y, joist_z),
            width=raf_w,
            depth=plate_d,
        )


# ---------------------------------------------------------------------------
# SMALL HELPERS FOR DORMER
# ---------------------------------------------------------------------------

def box(name, center, size):
    cx, cy, cz = center
    sx, sy, sz = size
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        scale=(sx * 0.5, sy * 0.5, sz * 0.5),
    )


def rafter_between(name, E, R, section_y, section_z):
    v_e = Vector(E)
    v_r = Vector(R)
    direction = v_r - v_e
    length = direction.length
    if length == 0.0:
        return

    center = (v_e + v_r) * 0.5
    dir_norm = direction.normalized()

    q = dir_norm.to_track_quat('X', 'Z')
    R_mat = q.to_matrix().to_4x4()

    S_mat = Matrix.Diagonal(
        (length * 0.5, section_y * 0.5, section_z * 0.5, 1.0)
    )
    T_mat = Matrix.Translation(center)

    M_world = T_mat @ R_mat @ S_mat

    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


# ---------------------------------------------------------------------------
# DORMER ON NORTH SLOPE – ALIGNED TO MAIN RAFTERS AND TRIMMED COMMONS
# ---------------------------------------------------------------------------

def build_dormer_on_north_slope(
        main_geom,
        origin=(0.0, 0.0, 0.0),
        width=2.0,
        depth=1.6,
        wall_height=1.2,
        roof_pitch_deg=35.0,
        stud_width=0.08,
        stud_depth=0.04,
        plate_thickness=0.04,
        rafter_width=0.05,
        rafter_depth=0.08,
        overhang=0.20,
        rafter_spacing=0.40,      # denser / original spacing
        num_dormer_jacks=3):

    half_W = main_geom["half_W"]
    ridge_height = main_geom["ridge_height"]
    plate_z = main_geom["plate_z"]
    ridge_half = main_geom["ridge_half"]
    main_spacing = main_geom["rafter_spacing"]

    y_main_ridge = 0.0
    z_main_ridge = ridge_height
    y_eave = half_W
    z_eave = plate_z

    main_tan = (ridge_height - plate_z) / half_W

    def z_on_main_roof(y):
        return z_main_ridge - main_tan * (y - y_main_ridge)

    ox, oy, oz = origin

    # Side studs must land on main rafters at +/- 1.5 * spacing
    support_half = 1.5 * main_spacing
    width = stud_width + 2.0 * support_half
    half_w = width * 0.5

    front_y = oy
    back_y = oy - depth

    wall_base_z = oz
    wall_top_z = wall_base_z + wall_height
    top_plate_z = wall_top_z + plate_thickness * 0.5

    x_left = ox - support_half
    x_right = ox + support_half

    roof_pitch_rad = math.radians(roof_pitch_deg)
    m_dormer = math.tan(roof_pitch_rad)
    run = half_w + overhang
    rise = run * m_dormer
    ridge_z = top_plate_z + rise

    z_front_roof = z_on_main_roof(front_y)
    z_back_roof = z_on_main_roof(back_y)

    # y where main roof is at dormer ridge height (double header / valley top line)
    y_ridge_back = y_main_ridge - (ridge_z - z_main_ridge) / main_tan

    bottom_L = Vector((x_left, back_y, z_back_roof))
    bottom_R = Vector((x_right, back_y, z_back_roof))

    # ---------------------------------------------------------------
    # 1. Front window framing
    # ---------------------------------------------------------------
    stud_center_z = wall_base_z + wall_height * 0.5

    window_width = width * 0.6
    window_height = wall_height * 0.6
    sill_height = wall_height * 0.25

    w_half = window_width * 0.5
    x_win_left = ox - w_half + stud_width * 0.5
    x_win_right = ox + w_half - stud_width * 0.5

    for i, x_jamb in enumerate((x_win_left, x_win_right)):
        box(
            name=f"Dormer_Window_Jamb_{i}",
            center=(x_jamb, front_y, stud_center_z),
            size=(stud_width, stud_depth, wall_height),
        )

    sill_z = wall_base_z + sill_height
    header_z = sill_z + window_height

    box(
        name="Dormer_Window_Sill",
        center=(ox, front_y, sill_z),
        size=(window_width, stud_depth, plate_thickness),
    )
    box(
        name="Dormer_Window_Header",
        center=(ox, front_y, header_z),
        size=(window_width, stud_depth, plate_thickness),
    )

    # ---------------------------------------------------------------
    # 2. Top plates
    # ---------------------------------------------------------------
    box(
        name="Dormer_TopPlate_FB_0",
        center=(ox, front_y, top_plate_z),
        size=(width, stud_depth, plate_thickness),
    )

    side_plate_center_y = (front_y + back_y) * 0.5
    for i, x_val in enumerate((x_left, x_right)):
        box(
            name=f"Dormer_TopPlate_Side_{i}",
            center=(x_val, side_plate_center_y, top_plate_z),
            size=(stud_width, depth, plate_thickness),
        )

    # ---------------------------------------------------------------
    # 3. Dormer ridge
    # ---------------------------------------------------------------
    ridge_extension_y = 2.0 * rafter_width
    ridge_y_min = y_ridge_back - ridge_extension_y
    ridge_y_max = front_y
    ridge_len_y = ridge_y_max - ridge_y_min
    ridge_center_y = 0.5 * (ridge_y_min + ridge_y_max)

    box(
        name="Dormer_Ridge",
        center=(ox, ridge_center_y, ridge_z),
        size=(rafter_width, ridge_len_y, rafter_depth),
    )

    # ---------------------------------------------------------------
    # 4. Dormer common rafters (denser, even spacing)
    # ---------------------------------------------------------------
    num_rafters = max(3, int(depth / rafter_spacing) + 2)
    dormer_rafter_y_positions = []

    for i in range(num_rafters):
        t = min(i * rafter_spacing, depth)
        y_pos = front_y - t
        dormer_rafter_y_positions.append(y_pos)

        eave_z = top_plate_z
        eave_left = (ox - half_w - overhang, y_pos, eave_z)
        eave_right = (ox + half_w + overhang, y_pos, eave_z)
        ridge_point = (ox, y_pos, ridge_z)

        rafter_between(
            name=f"Dormer_Rafter_L_{i}",
            E=eave_left,
            R=ridge_point,
            section_y=rafter_width,
            section_z=rafter_depth,
        )
        rafter_between(
            name=f"Dormer_Rafter_R_{i}",
            E=eave_right,
            R=ridge_point,
            section_y=rafter_width,
            section_z=rafter_depth,
        )

    # ---------------------------------------------------------------
    # 5. X-grid for main rafters + interior rafters to trim
    # ---------------------------------------------------------------
    x_positions = []
    n_main_steps = int(main_geom["ridge_len"] / main_spacing)
    for i in range(n_main_steps + 1):
        x = -ridge_half + i * main_spacing
        x_positions.append(x)

    x_support_left = x_left
    x_support_right = x_right
    interior_x = [x for x in x_positions if x_support_left < x < x_support_right]

    # ---------------------------------------------------------------
    # 6. Upper double header between supporting rafters
    # ---------------------------------------------------------------
    x_header_left = x_support_left
    x_header_right = x_support_right
    header_center_x = 0.5 * (x_header_left + x_header_right)
    header_len_x = x_header_right - x_header_left
    header_y = y_ridge_back
    header_z = ridge_z

    header_offset = stud_depth * 0.3

    box(
        name="Dormer_DoubleHeader_A",
        center=(header_center_x, header_y - header_offset, header_z),
        size=(header_len_x, stud_depth, rafter_depth),
    )
    box(
        name="Dormer_DoubleHeader_B",
        center=(header_center_x, header_y + header_offset, header_z),
        size=(header_len_x, stud_depth, rafter_depth),
    )

    valley_top_L = Vector((header_center_x, header_y, ridge_z))
    valley_top_R = Vector((header_center_x, header_y, ridge_z))

    # ---------------------------------------------------------------
    # 7. Valley rafters (main roof)
    # ---------------------------------------------------------------
    main_rafter_width = main_geom["rafter_size"][0]
    main_rafter_depth = main_geom["rafter_size"][1]

    rafter_between(
        name="Dormer_Valley_L",
        E=bottom_L,
        R=valley_top_L,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )
    rafter_between(
        name="Dormer_Valley_R",
        E=bottom_R,
        R=valley_top_R,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    # ---------------------------------------------------------------
    # 8. Dormer jack rafters from valleys to dormer ridge
    # ---------------------------------------------------------------
    if num_dormer_jacks > 0:
        for j in range(num_dormer_jacks):
            t = (j + 1) / (num_dormer_jacks + 1.0)
            y_j = back_y + t * (y_ridge_back - back_y)

            if abs(valley_top_L.y - bottom_L.y) > 1e-6:
                tv = (y_j - bottom_L.y) / (valley_top_L.y - bottom_L.y)
            else:
                tv = 0.0

            P_valley_L = bottom_L.lerp(valley_top_L, tv)
            P_valley_R = bottom_R.lerp(valley_top_R, tv)

            P_ridge = Vector((ox, y_j, ridge_z))

            rafter_between(
                name=f"Dormer_Valley_Jack_L_{j}",
                E=P_valley_L,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )
            rafter_between(
                name=f"Dormer_Valley_Jack_R_{j}",
                E=P_valley_R,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )

    # ---------------------------------------------------------------
    # 9. Front support beam on main roof plane
    # ---------------------------------------------------------------
    box(
        name="Dormer_FrontSupportBeam",
        center=(ox, front_y, z_front_roof),
        size=(width, stud_depth, main_rafter_depth),
    )

    # ---------------------------------------------------------------
    # 10. Vertical side studs landing on rafters below
    # ---------------------------------------------------------------
    for i, y_pos in enumerate(dormer_rafter_y_positions):
        z_main_y = z_on_main_roof(y_pos)
        bottom = z_main_y + main_rafter_depth * 0.5

        # left
        top_L = ridge_z + m_dormer * (x_left - ox) - rafter_depth * 0.5
        height_L = max(0.0, top_L - bottom)
        if height_L > 0.0:
            center_z_L = bottom + 0.5 * height_L
            box(
                name=f"Dormer_SideStud_L_{i}",
                center=(x_left, y_pos, center_z_L),
                size=(stud_width, stud_depth, height_L),
            )

        # right
        top_R = ridge_z - m_dormer * (x_right - ox) - rafter_depth * 0.5
        height_R = max(0.0, top_R - bottom)
        if height_R > 0.0:
            center_z_R = bottom + 0.5 * height_R
            box(
                name=f"Dormer_SideStud_R_{i}",
                center=(x_right, y_pos, center_z_R),
                size=(stud_width, stud_depth, height_R),
            )

    # ---------------------------------------------------------------
    # 11. Trimmed main rafters between supporting rafters
    #     - top segments: main ridge -> valley
    #     - bottom segments: Plate_Long_N -> Dormer_FrontSupportBeam
    # ---------------------------------------------------------------
    for idx, x_r in enumerate(interior_x):
        if x_r < 0.0:
            V0 = bottom_L
            V1 = valley_top_L
        else:
            V0 = bottom_R
            V1 = valley_top_R

        if abs(V1.x - V0.x) < 1e-6:
            continue

        t = (x_r - V0.x) / (V1.x - V0.x)
        if t < 0.0 or t > 1.0:
            continue

        P_valley = V0.lerp(V1, t)

        ridge_pt = Vector((x_r, 0.0, ridge_height))
        eave_pt = Vector((x_r, y_eave, z_eave))

        # top segment
        create_prismatic_member(
            name=f"Dormer_TrimmedTop_{idx}",
            start=ridge_pt,
            end=P_valley,
            width=main_rafter_width,
            depth=main_rafter_depth,
        )

        # bottom segment now ends at front support beam
        H = Vector((x_r, front_y, z_front_roof))
        create_prismatic_member(
            name=f"Dormer_TrimmedBottom_{idx}",
            start=eave_pt,
            end=H,
            width=main_rafter_width,
            depth=main_rafter_depth,
        )

    # ---------------------------------------------------------------
    # 12. Top braces tying dormer rafters
    # ---------------------------------------------------------------
    brace_thickness = plate_thickness
    z_brace = ridge_z - (ridge_z - top_plate_z) * 0.3

    clear_width = width - 2.0 * stud_width
    brace_width = 0.45 * clear_width

    for i, y_pos in enumerate(dormer_rafter_y_positions):
        brace_y = y_pos - stud_depth
        brace_y = max(min(brace_y, front_y), y_ridge_back)
        box(
            name=f"Dormer_TopBrace_{i}",
            center=(ox, brace_y, z_brace),
            size=(brace_width, stud_depth, brace_thickness),
        )


# ---------------------------------------------------------------------------
# SCENE ASSEMBLY
# ---------------------------------------------------------------------------

def build_scene():
    # Larger main roof so dormer fits proportionally
    length = 18.0
    width = 9.0
    plate_z = 0.0

    slope_rise = 1.0
    slope_run = 2.0
    rafter_spacing = 0.6

    plate_size = (0.038, 0.140)
    rafter_size = (0.038, 0.184)
    ridge_size = (0.038, 0.184)
    hip_extra_depth = 0.050

    half_W = width * 0.5

    # Dormer origin close to north eave
    dormer_origin_y = half_W - 0.8
    dormer_origin = (0.0, dormer_origin_y, 0.0)
    dormer_stud_width = 0.08

    # Make dormer side studs sit on main rafters at +/- 1.5 * spacing
    support_half = 1.5 * rafter_spacing
    dormer_width = dormer_stud_width + 2.0 * support_half

    # North roof clearance: remove only rafters strictly between supports
    north_clear_range = (-support_half + 0.05, support_half - 0.05)

    # T-wing dimensions (south)
    wing_length = 6.0
    wing_width = 6.0
    wing_half_x = wing_width * 0.5

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
        north_clear_range=north_clear_range,
        south_clear_half_x=wing_half_x,
    )

    build_T_wing_rotated(
        main_geom=main_geom,
        wing_length=wing_length,
        wing_width=wing_width,
    )

    # Dormer with original, denser rafter spacing (0.40)
    build_dormer_on_north_slope(
        main_geom=main_geom,
        origin=dormer_origin,
        width=dormer_width,
        depth=1.6,
        wall_height=1.2,
        roof_pitch_deg=35.0,
        stud_width=dormer_stud_width,
        rafter_spacing=0.40,  # back to denser spacing
    )


if __name__ == "__main__":
    build_scene()
