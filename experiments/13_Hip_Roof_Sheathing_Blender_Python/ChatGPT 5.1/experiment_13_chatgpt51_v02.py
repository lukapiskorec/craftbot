# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 13 - CHATGPT 5.1 - V02
# HIP ROOF WITH SHEATHING
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix
import importlib
import craftbot_lib as craftbot
importlib.reload(craftbot)


# ---------------------------------------------------------------------------
# BOARD GEOMETRY HELPERS
# ---------------------------------------------------------------------------

def create_board_between(name, p0, p1, normal, board_width, board_thickness):
    """
    Create a single rectangular wood board between points p0 and p1,
    lying on the roof plane with normal `normal`.

    Long axis (local Z) is along (p1 - p0).
    Board width (local X) is in-plane, perpendicular to length.
    Board thickness (local Y) is along the plane normal.
    """
    v0 = Vector(p0)
    v1 = Vector(p1)
    direction = v1 - v0
    length = direction.length
    if length <= 1e-6:
        return

    axis_z = direction.normalized()
    axis_y = Vector(normal).normalized()

    # Fallback if normal is parallel to direction
    if abs(axis_y.dot(axis_z)) > 0.999:
        axis_y = Vector((0.0, 0.0, 1.0))
        if abs(axis_y.dot(axis_z)) > 0.999:
            axis_y = Vector((0.0, 1.0, 0.0))

    axis_x = axis_y.cross(axis_z).normalized()
    axis_y = axis_z.cross(axis_x).normalized()

    R = Matrix((
        (axis_x.x, axis_y.x, axis_z.x),
        (axis_x.y, axis_y.y, axis_z.y),
        (axis_x.z, axis_y.z, axis_z.z),
    ))
    R4 = R.to_4x4()

    S = Matrix.Diagonal((
        board_width * 0.5,
        board_thickness * 0.5,
        length * 0.5,
        1.0,
    ))

    mid = (v0 + v1) * 0.5
    T = Matrix.Translation(mid)

    M_world = T @ R4 @ S

    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


def cover_quad_with_boards(
        name_prefix,
        P00, P10, P11, P01,
        board_width=0.15,
        board_thickness=0.02,
        start_index=0,
        xy_gaps=None):
    """
    Cover a planar quad P00-P10-P11-P01 (in that order) with parallel
    wood boards.

    Parameterization:
        u in [0,1] along P00->P10 and P01->P11  (board length direction)
        v in [0,1] from P00/P10 edge to P01/P11 edge (board width direction)

    Boards run along u (long direction). We subdivide [0,1] in v into
    N strips, where N is chosen so that the physical spacing in v is
    ~ board_width.

    If xy_gaps is provided, it must be a list of rectangles in world XY
    coordinates: (x_min, x_max, y_min, y_max). Boards are not created
    inside those rectangles; rows are split into multiple segments as needed.
    """
    P00 = Vector(P00)
    P10 = Vector(P10)
    P11 = Vector(P11)
    P01 = Vector(P01)

    normal = (P10 - P00).cross(P01 - P00)
    if normal.length <= 1e-6:
        return start_index
    normal.normalize()

    v_edge0 = P01 - P00
    v_edge1 = P11 - P10
    len_v0 = v_edge0.length
    len_v1 = v_edge1.length
    avg_len_v = 0.5 * (len_v0 + len_v1)

    if avg_len_v <= 1e-6:
        return start_index

    N = max(1, int(math.ceil(avg_len_v / board_width)))
    dv = 1.0 / N
    effective_width = avg_len_v / N

    idx = start_index

    for i in range(N):
        v = (i + 0.5) * dv

        side0 = P00.lerp(P01, v)
        side1 = P10.lerp(P11, v)

        # For this hip-roof setup, all points in the row share the same Y
        row_y = side0.y
        x0 = side0.x
        x1 = side1.x

        # Ensure x0 <= x1
        if x0 > x1:
            x0, x1 = x1, x0
            side0, side1 = side1, side0

        segments = [(0.0, 1.0)]

        if xy_gaps:
            for (gx0, gx1, gy0, gy1) in xy_gaps:
                # Normalise gap bounds
                if gx0 > gx1:
                    gx0, gx1 = gx1, gx0
                if gy0 > gy1:
                    gy0, gy1 = gy1, gy0

                # Does this row intersect the gap in Y?
                if not (gy0 <= row_y <= gy1):
                    continue

                # Does the row's X-span intersect the gap?
                if gx1 <= x0 or gx0 >= x1:
                    continue

                denom = (x1 - x0)
                if abs(denom) < 1e-9:
                    continue

                t0 = (max(gx0, x0) - x0) / denom
                t1 = (min(gx1, x1) - x0) / denom
                t0, t1 = sorted((t0, t1))

                new_segments = []
                for (a, b) in segments:
                    if b <= t0 or a >= t1:
                        new_segments.append((a, b))
                    else:
                        if a < t0:
                            new_segments.append((a, t0))
                        if b > t1:
                            new_segments.append((t1, b))
                segments = new_segments

        for (a, b) in segments:
            if b - a <= 1e-5:
                continue
            p0 = side0.lerp(side1, a)
            p1 = side0.lerp(side1, b)
            create_board_between(
                name=f"{name_prefix}_{idx:03d}",
                p0=p0,
                p1=p1,
                normal=normal,
                board_width=effective_width,
                board_thickness=board_thickness,
            )
            idx += 1

    return idx


# ---------------------------------------------------------------------------
# MAIN ROOF SHEATHING (N/S SLOPES + E/W HIP TRIANGLES)
# ---------------------------------------------------------------------------

def add_main_roof_board_sheathing(
        main_geom,
        board_width=0.15,
        board_thickness=0.02,
        dormer_gaps_xy=None,
        name_prefix="SheathMain"):
    """
    Sheath all visible surfaces of the main hip roof:
    - north slope (with dormer gaps, if given),
    - south slope,
    - east and west hip triangles.
    """

    half_L = main_geom["half_L"]
    half_W = main_geom["half_W"]
    plate_z = main_geom["plate_z"]
    ridge_height = main_geom["ridge_height"]
    ridge_half = main_geom["ridge_half"]

    NW = Vector((-half_L,  half_W, plate_z))
    NE = Vector(( half_L,  half_W, plate_z))
    SW = Vector((-half_L, -half_W, plate_z))
    SE = Vector(( half_L, -half_W, plate_z))

    RW = Vector((-ridge_half, 0.0, ridge_height))  # west ridge end
    RE = Vector(( ridge_half, 0.0, ridge_height))  # east ridge end

    index = 0

    # North slope – split around dormers
    index = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_N",
        P00=RW,
        P10=RE,
        P11=NE,
        P01=NW,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=index,
        xy_gaps=dormer_gaps_xy,
    )

    # South slope – full coverage
    index = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_S",
        P00=RE,
        P10=RW,
        P11=SW,
        P01=SE,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=index,
        xy_gaps=None,
    )

    # West hip triangle (ridge_W to NW/SW)
    index = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_W",
        P00=RW,
        P10=RW,
        P11=SW,
        P01=NW,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=index,
        xy_gaps=None,
    )

    # East hip triangle (ridge_E to NE/SE)
    cover_quad_with_boards(
        name_prefix=f"{name_prefix}_E",
        P00=RE,
        P10=RE,
        P11=NE,
        P01=SE,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=index,
        xy_gaps=None,
    )


# ---------------------------------------------------------------------------
# DORMER GEOMETRY + SHEATHING
# ---------------------------------------------------------------------------

def compute_dormer_geom(
        main_geom,
        origin=(0.0, 0.0, 0.0),
        width=2.0,
        depth=1.6,
        wall_height=1.2,
        roof_pitch_deg=35.0,
        stud_width=0.08,
        plate_thickness=0.04,
        overhang=0.20):
    """
    Compute key dormer geometry used for both:
    - dormer roof sheathing, and
    - defining the north-slope sheathing gap.
    """

    half_W = main_geom["half_W"]
    ridge_height = main_geom["ridge_height"]
    plate_z = main_geom["plate_z"]
    main_spacing = main_geom["rafter_spacing"]

    y_main_ridge = 0.0
    z_main_ridge = ridge_height

    main_tan = (ridge_height - plate_z) / half_W

    ox, oy, oz = origin

    # Support rafters at +/- 1.5 * spacing
    support_half = 1.5 * main_spacing
    width = stud_width + 2.0 * support_half
    half_w = width * 0.5

    front_y = oy
    back_y = oy - depth

    wall_base_z = oz
    wall_top_z = wall_base_z + wall_height
    top_plate_z = wall_top_z + plate_thickness * 0.5

    roof_pitch_rad = math.radians(roof_pitch_deg)
    m_dormer = math.tan(roof_pitch_rad)
    run = half_w + overhang
    rise = run * m_dormer
    ridge_z = top_plate_z + rise

    # Y where main roof equals dormer ridge height (valley/header line)
    y_ridge_back = y_main_ridge - (ridge_z - z_main_ridge) / main_tan

    x_support_L = ox - support_half
    x_support_R = ox + support_half

    x_eave_L = ox - half_w - overhang
    x_eave_R = ox + half_w + overhang

    return {
        "origin": origin,
        "width": width,
        "half_w": half_w,
        "front_y": front_y,
        "back_y": back_y,
        "y_ridge_back": y_ridge_back,
        "x_support_L": x_support_L,
        "x_support_R": x_support_R,
        "x_eave_L": x_eave_L,
        "x_eave_R": x_eave_R,
        "ridge_z": ridge_z,
        "top_plate_z": top_plate_z,
        "overhang": overhang,
    }


def add_dormer_board_sheathing(
        main_geom,
        dormer_geom,
        board_width=0.15,
        board_thickness=0.02,
        dormer_id=0,
        name_prefix="SheathDormer"):
    """
    Sheath the left and right dormer half-roofs using dormer_geom from
    compute_dormer_geom().
    """

    ox, oy, oz = dormer_geom["origin"]
    front_y = dormer_geom["front_y"]
    y_ridge_back = dormer_geom["y_ridge_back"]
    x_eave_L = dormer_geom["x_eave_L"]
    x_eave_R = dormer_geom["x_eave_R"]
    ridge_z = dormer_geom["ridge_z"]
    top_plate_z = dormer_geom["top_plate_z"]

    # Left roof plane
    P00_L = Vector((x_eave_L, y_ridge_back, top_plate_z))
    P10_L = Vector((x_eave_L, front_y,      top_plate_z))
    P11_L = Vector((ox,       front_y,      ridge_z))
    P01_L = Vector((ox,       y_ridge_back, ridge_z))

    # Right roof plane
    P00_R = Vector((x_eave_R, y_ridge_back, top_plate_z))
    P10_R = Vector((x_eave_R, front_y,      top_plate_z))
    P11_R = Vector((ox,       front_y,      ridge_z))
    P01_R = Vector((ox,       y_ridge_back, ridge_z))

    idx = 0
    idx = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_D{dormer_id}_L",
        P00=P00_L,
        P10=P10_L,
        P11=P11_L,
        P01=P01_L,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )

    cover_quad_with_boards(
        name_prefix=f"{name_prefix}_D{dormer_id}_R",
        P00=P00_R,
        P10=P10_R,
        P11=P11_R,
        P01=P01_R,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )


# ---------------------------------------------------------------------------
# T-WING SHEATHING (APPROXIMATE HIP ROOF)
# ---------------------------------------------------------------------------

def add_T_wing_board_sheathing(
        main_geom,
        wing_length=6.0,
        wing_width=6.0,
        board_width=0.15,
        board_thickness=0.02,
        name_prefix="SheathWing"):
    """
    Sheath the south T-wing hip roof. The wing is modelled as a
    symmetric hip attached to the south side of the main roof.
    """

    half_W_main = main_geom["half_W"]
    plate_z = main_geom["plate_z"]
    slope_rise = main_geom["slope_rise"]
    slope_run = main_geom["slope_run"]

    k = slope_rise / slope_run

    half_Lw = wing_length * 0.5    # along Y (south–north)
    half_Ww = wing_width * 0.5     # along X (east–west)

    # T-wing is centred at X=0, attached at y = -half_W_main
    y_north = -half_W_main
    y_south = y_north - wing_length

    SW = Vector((-half_Ww, y_south, plate_z))
    SE = Vector(( half_Ww, y_south, plate_z))
    NW = Vector((-half_Ww, y_north, plate_z))
    NE = Vector(( half_Ww, y_north, plate_z))

    ridge_height = plate_z + half_Ww * k

    ridge_len = max(wing_length - wing_width, 0.0)
    ridge_half = ridge_len * 0.5
    y_center = 0.5 * (y_south + y_north)

    RS = Vector((0.0, y_center - ridge_half, ridge_height))  # south ridge end
    RN = Vector((0.0, y_center + ridge_half, ridge_height))  # north ridge end

    idx = 0

    # North slope
    idx = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_N",
        P00=RS,
        P10=RN,
        P11=NE,
        P01=NW,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )

    # South slope
    idx = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_S",
        P00=RN,
        P10=RS,
        P11=SW,
        P01=SE,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )

    # West hip triangle
    idx = cover_quad_with_boards(
        name_prefix=f"{name_prefix}_W",
        P00=RS,
        P10=RS,
        P11=SW,
        P01=NW,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )

    # East hip triangle
    cover_quad_with_boards(
        name_prefix=f"{name_prefix}_E",
        P00=RN,
        P10=RN,
        P11=NE,
        P01=SE,
        board_width=board_width,
        board_thickness=board_thickness,
        start_index=idx,
    )


# ---------------------------------------------------------------------------
# SCENE BUILDER INCLUDING SHEATHING
# ---------------------------------------------------------------------------

def build_scene_with_sheathing():
    """
    Build the original framing (main hip roof, T-wing, dormers) and
    then add board sheathing to all roof surfaces, with openings in
    the north slope where the dormers sit.
    """

    # --- Main hip roof parameters (same as original build_scene) ---
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

    # Three dormers along the north slope
    center_offsets = [
        -5.0 * rafter_spacing,
        0.0,
        5.0 * rafter_spacing,
    ]

    support_half = 1.5 * rafter_spacing

    # Clear a continuous band in the north slope where all dormers sit
    clear_min = min(cx - support_half for cx in center_offsets) + 0.05
    clear_max = max(cx + support_half for cx in center_offsets) - 0.05
    north_clear_range = (clear_min, clear_max)

    # South T-wing dimensions
    wing_length = 6.0
    wing_width = 6.0
    wing_half_x = wing_width * 0.5

    # Main hip roof framing
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

    # T-wing framing
    build_T_wing_rotated(
        main_geom=main_geom,
        wing_length=wing_length,
        wing_width=wing_width,
    )

    # Dormer parameters
    dormer_origin_y = half_W - 0.8
    dormer_stud_width = 0.08
    support_half = 1.5 * rafter_spacing
    dormer_width = dormer_stud_width + 2.0 * support_half

    dormer_depth = 1.6
    dormer_wall_height = 1.2
    dormer_roof_pitch = 35.0
    dormer_rafter_spacing = 0.40

    # Collect sheathing gaps for the north slope
    north_gaps_xy = []

    # Build dormers and their sheathing
    for d_id, cx in enumerate(center_offsets):
        origin = (cx, dormer_origin_y, 0.0)

        # Structural dormer
        build_dormer_on_north_slope(
            main_geom=main_geom,
            origin=origin,
            width=dormer_width,
            depth=dormer_depth,
            wall_height=dormer_wall_height,
            roof_pitch_deg=dormer_roof_pitch,
            stud_width=dormer_stud_width,
            rafter_spacing=dormer_rafter_spacing,
            dormer_id=d_id,
        )

        # Dormer geometry for sheathing and gap definition
        d_geom = compute_dormer_geom(
            main_geom=main_geom,
            origin=origin,
            width=dormer_width,
            depth=dormer_depth,
            wall_height=dormer_wall_height,
            roof_pitch_deg=dormer_roof_pitch,
            stud_width=dormer_stud_width,
            plate_thickness=0.04,
            overhang=0.20,
        )

        # Dormer roof sheathing
        add_dormer_board_sheathing(
            main_geom=main_geom,
            dormer_geom=d_geom,
            board_width=0.15,
            board_thickness=0.02,
            dormer_id=d_id,
            name_prefix="SheathDormer",
        )

        # Gap under this dormer on the north main slope:
        # bounded by support rafters and valley/header line.
        north_gaps_xy.append((
            d_geom["x_support_L"],
            d_geom["x_support_R"],
            d_geom["y_ridge_back"],
            d_geom["front_y"],
        ))

    # Restore full rafters between dormers on the north side
    gap_xs = []
    for i in range(len(center_offsets) - 1):
        gap_xs.append(0.5 * (center_offsets[i] + center_offsets[i + 1]))
    add_north_gap_rafters(main_geom, gap_xs)

    # Main roof sheathing (with dormer openings)
    add_main_roof_board_sheathing(
        main_geom=main_geom,
        board_width=0.15,
        board_thickness=0.02,
        dormer_gaps_xy=north_gaps_xy,
        name_prefix="SheathMain",
    )

    # T-wing sheathing
    add_T_wing_board_sheathing(
        main_geom=main_geom,
        wing_length=wing_length,
        wing_width=wing_width,
        board_width=0.15,
        board_thickness=0.02,
        name_prefix="SheathWing",
    )



# ---------------------------------------------------------------------------
# LOW-LEVEL MEMBER CREATION
# ---------------------------------------------------------------------------

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


def box(name, center, size):
    """Simple rectangular element aligned to global axes."""
    cx, cy, cz = center
    sx, sy, sz = size
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        scale=(sx * 0.5, sy * 0.5, sz * 0.5),
    )


def rafter_between(name, E, R, section_y, section_z):
    """Rafter element between two arbitrary points."""
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


def double_support_rafters_for_dormer(main_geom, x_positions, dormer_id):
    """
    For each x in x_positions on the north roof side, create a pair of
    full-length rafters (doubled rafters) from Plate_Long_N to Ridge_Board.
    """
    half_W = main_geom["half_W"]
    plate_z = main_geom["plate_z"]
    ridge_height = main_geom["ridge_height"]
    raf_w, raf_d = main_geom["rafter_size"]

    for idx, x in enumerate(x_positions):
        # First rafter
        start1 = (x, half_W, plate_z)
        end1 = (x, 0.0, ridge_height)
        create_prismatic_member(
            name=f"DormerSupport_D{dormer_id}_{idx}_A",
            start=start1,
            end=end1,
            width=raf_w,
            depth=raf_d,
        )

        # Second rafter offset slightly in X so it is visually distinct
        offset = 0.05 if x >= 0.0 else -0.05
        start2 = (x + offset, half_W, plate_z)
        end2 = (x + offset, 0.0, ridge_height)
        create_prismatic_member(
            name=f"DormerSupport_D{dormer_id}_{idx}_B",
            start=start2,
            end=end2,
            width=raf_w,
            depth=raf_d,
        )


def add_north_gap_rafters(main_geom, x_list):
    """
    Add full common rafters on the north side at specific x-positions.
    These are used to restore rafters between dormer windows.
    """
    half_W = main_geom["half_W"]
    plate_z = main_geom["plate_z"]
    ridge_height = main_geom["ridge_height"]
    raf_w, raf_d = main_geom["rafter_size"]

    for i, x in enumerate(x_list):
        start = (x, half_W, plate_z)
        end = (x, 0.0, ridge_height)
        create_prismatic_member(
            name=f"Rafter_N_Gap_{i}",
            start=start,
            end=end,
            width=raf_w,
            depth=raf_d,
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

    eps = 1e-6

    # -----------------------------
    # Jack rafters N/S – WEST SIDE
    # (shifted so they step outwards from ridge, mirroring east side)
    # -----------------------------
    x = -ridge_half - rafter_spacing
    while x > -half_L + eps:
        # North
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

        # South
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

        x -= rafter_spacing

    # Jack rafters N/S – EAST SIDE (unchanged, already aligned well)
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

    # W/E – north half
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

    # W/E – south half
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
# T-WING (SOUTH) – HIP ROOF WITH JACKS
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

    # --- HIP GEOMETRY AT SOUTH END ---
    corner_SW = Vector((-wing_half_X, y_south, plate_z))
    corner_SE = Vector(( wing_half_X, y_south, plate_z))

    # distance from south plate to start of ridge (hip run) equals half width
    y_ridge_start = y_south + wing_half_X
    hip_top = Vector((0.0, y_ridge_start, ridge_height_wing))

    # Wing ridge now runs from hip_top northwards to valley intersection
    ridge_start = hip_top
    ridge_end   = Vector((0.0, y_valley_top, ridge_height_wing))
    create_prismatic_member(
        "Wing_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Hip rafters from south corners to hip_top
    create_prismatic_member(
        "Wing_Hip_SW",
        start=corner_SW,
        end=hip_top,
        width=raf_w,
        depth=raf_d * 1.25,
    )
    create_prismatic_member(
        "Wing_Hip_SE",
        start=corner_SE,
        end=hip_top,
        width=raf_w,
        depth=raf_d * 1.25,
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

    # Wing common rafters and jack rafters (from W/E plates)
    n_steps = max(int(wing_length / rafter_spacing), 1)
    for i in range(n_steps + 1):
        t = i / max(n_steps, 1)
        y = y_north - t * wing_len_Y  # from north to south

        plate_E = ( wing_half_X, y, plate_z)
        plate_W = (-wing_half_X, y, plate_z)

        if y >= y_ridge_start:  # normal common rafters to ridge
            ridge_pt = (0.0, y, ridge_height_wing)
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
        else:
            # jack rafters bearing on hips (from W/E plates)
            hip_p0_E = corner_SE
            hip_p1_E = hip_top
            tE = (y - y_south) / max((y_ridge_start - y_south), 1e-6)
            tE = max(0.0, min(1.0, tE))
            hip_pt_E = hip_p0_E.lerp(hip_p1_E, tE)

            hip_p0_W = corner_SW
            hip_p1_W = hip_top
            tW = (y - y_south) / max((y_ridge_start - y_south), 1e-6)
            tW = max(0.0, min(1.0, tW))
            hip_pt_W = hip_p0_W.lerp(hip_p1_W, tW)

            create_prismatic_member(
                f"Wing_Jack_E_{i:02d}",
                start=plate_E,
                end=hip_pt_E,
                width=raf_w,
                depth=raf_d,
            )
            create_prismatic_member(
                f"Wing_Jack_W_{i:02d}",
                start=plate_W,
                end=hip_pt_W,
                width=raf_w,
                depth=raf_d,
            )

    # --- NEW SOUTH HIP JACK RAFTERS FROM SOUTH PLATE ---
    # Left half (to Wing_Hip_SW)
    x = -wing_half_X + rafter_spacing
    idx = 0
    while x < -1e-6:
        t = (x - corner_SW.x) / (hip_top.x - corner_SW.x)  # 0..1
        t = max(0.0, min(1.0, t))
        hip_pt = corner_SW.lerp(hip_top, t)
        start = (x, y_south, plate_z)
        create_prismatic_member(
            f"Wing_Jack_S_SW_{idx:02d}",
            start=start,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )
        x += rafter_spacing
        idx += 1

    # Right half (to Wing_Hip_SE)
    x = rafter_spacing
    idx = 0
    while x < wing_half_X - 1e-6:
        t = (x - corner_SE.x) / (hip_top.x - corner_SE.x)
        t = max(0.0, min(1.0, t))
        hip_pt = corner_SE.lerp(hip_top, t)
        start = (x, y_south, plate_z)
        create_prismatic_member(
            f"Wing_Jack_S_SE_{idx:02d}",
            start=start,
            end=hip_pt,
            width=raf_w,
            depth=raf_d,
        )
        x += rafter_spacing
        idx += 1

    # Central king rafter on the south hip
    create_prismatic_member(
        "Wing_King_S",
        start=(0.0, y_south, plate_z),
        end=hip_top,
        width=raf_w,
        depth=raf_d,
    )

    # Valleys connecting to main roof
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
# DORMER BUILDER – UPDATED HEADER BEAM
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
        rafter_spacing=0.40,
        num_dormer_jacks=3,
        dormer_id=0):

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

    # Side studs sit on main rafters at +/- 1.5 * spacing from center
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

    # y where main roof is at dormer ridge height (header / valley top line)
    y_ridge_back = y_main_ridge - (ridge_z - z_main_ridge) / main_tan

    bottom_L = Vector((x_left, back_y, z_back_roof))
    bottom_R = Vector((x_right, back_y, z_back_roof))

    # ---------------------------------------------------------------
    # 1. Side top plates
    # ---------------------------------------------------------------
    side_plate_center_y = (front_y + back_y) * 0.5
    for i, x_val in enumerate((x_left, x_right)):
        box(
            name=f"D{dormer_id}_Dormer_TopPlate_Side_{i}",
            center=(x_val, side_plate_center_y, top_plate_z),
            size=(stud_width, depth, plate_thickness),
        )

    # ---------------------------------------------------------------
    # 2. Dormer ridge
    # ---------------------------------------------------------------
    ridge_extension_y = 2.0 * rafter_width
    ridge_y_min = y_ridge_back - ridge_extension_y
    ridge_y_max = front_y
    ridge_len_y = ridge_y_max - ridge_y_min
    ridge_center_y = 0.5 * (ridge_y_min + ridge_y_max)

    box(
        name=f"D{dormer_id}_Dormer_Ridge",
        center=(ox, ridge_center_y, ridge_z),
        size=(rafter_width, ridge_len_y, rafter_depth),
    )

    # ---------------------------------------------------------------
    # 3. Dormer common rafters (dense, even spacing)
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
            name=f"D{dormer_id}_Dormer_Rafter_L_{i}",
            E=eave_left,
            R=ridge_point,
            section_y=rafter_width,
            section_z=rafter_depth,
        )
        rafter_between(
            name=f"D{dormer_id}_Dormer_Rafter_R_{i}",
            E=eave_right,
            R=ridge_point,
            section_y=rafter_width,
            section_z=rafter_depth,
        )

    # ---------------------------------------------------------------
    # 4. X-grid for main rafters + interior rafters to trim
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
    # 5. Single header beam (replacing double header)
    # ---------------------------------------------------------------
    x_header_left = x_support_left
    x_header_right = x_support_right
    header_center_x = 0.5 * (x_header_left + x_header_right)
    header_len_x = x_header_right - x_header_left
    header_y = y_ridge_back
    header_z = ridge_z

    main_rafter_width = main_geom["rafter_size"][0]
    main_rafter_depth = main_geom["rafter_size"][1]

    # Single, taller header similar to FrontSupportBeam
    box(
        name=f"D{dormer_id}_Dormer_Header",
        center=(header_center_x, header_y, header_z),
        size=(header_len_x, stud_depth, main_rafter_depth),
    )

    valley_top_L = Vector((header_center_x, header_y, ridge_z))
    valley_top_R = Vector((header_center_x, header_y, ridge_z))

    # ---------------------------------------------------------------
    # 6. Valley rafters (main roof)
    # ---------------------------------------------------------------
    rafter_between(
        name=f"D{dormer_id}_Dormer_Valley_L",
        E=bottom_L,
        R=valley_top_L,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )
    rafter_between(
        name=f"D{dormer_id}_Dormer_Valley_R",
        E=bottom_R,
        R=valley_top_R,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    # ---------------------------------------------------------------
    # 7. Dormer jack rafters from valleys to dormer ridge
    #    + top braces tying each pair of valley jacks
    # ---------------------------------------------------------------
    valley_brace_thickness = plate_thickness

    if num_dormer_jacks > 0:
        for j in range(num_dormer_jacks):
            t = (j + 1) / (num_dormer_jacks + 1.0)
            y_j = back_y + t * (y_ridge_back - back_y)

            # Interpolate along valley lines in Y
            if abs(valley_top_L.y - bottom_L.y) > 1e-6:
                tvL = (y_j - bottom_L.y) / (valley_top_L.y - bottom_L.y)
            else:
                tvL = 0.0
            if abs(valley_top_R.y - bottom_R.y) > 1e-6:
                tvR = (y_j - bottom_R.y) / (valley_top_R.y - bottom_R.y)
            else:
                tvR = 0.0

            P_valley_L = bottom_L.lerp(valley_top_L, tvL)
            P_valley_R = bottom_R.lerp(valley_top_R, tvR)
            P_ridge = Vector((ox, y_j, ridge_z))

            rafter_between(
                name=f"D{dormer_id}_Dormer_Valley_Jack_L_{j}",
                E=P_valley_L,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )
            rafter_between(
                name=f"D{dormer_id}_Dormer_Valley_Jack_R_{j}",
                E=P_valley_R,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )

            # valley top brace (slightly lower and shorter)
            brace_center_x = 0.5 * (P_valley_L.x + P_valley_R.x)
            brace_y = y_j - stud_depth
            brace_z = P_valley_L.z + 0.6 * (ridge_z - P_valley_L.z)
            brace_len_x = abs(P_valley_R.x - P_valley_L.x) * 0.48

            box(
                name=f"D{dormer_id}_Dormer_ValleyTopBrace_{j}",
                center=(brace_center_x, brace_y, brace_z),
                size=(brace_len_x, stud_depth, valley_brace_thickness),
            )

    # ---------------------------------------------------------------
    # 8. Front support beam on main roof plane
    # ---------------------------------------------------------------
    box(
        name=f"D{dormer_id}_Dormer_FrontSupportBeam",
        center=(ox, front_y, z_front_roof),
        size=(width, stud_depth, main_rafter_depth),
    )

    # ---------------------------------------------------------------
    # 9. Vertical side studs landing on rafters below
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
                name=f"D{dormer_id}_Dormer_SideStud_L_{i}",
                center=(x_left, y_pos, center_z_L),
                size=(stud_width, stud_depth, height_L),
            )

        # right
        top_R = ridge_z - m_dormer * (x_right - ox) - rafter_depth * 0.5
        height_R = max(0.0, top_R - bottom)
        if height_R > 0.0:
            center_z_R = bottom + 0.5 * height_R
            box(
                name=f"D{dormer_id}_Dormer_SideStud_R_{i}",
                center=(x_right, y_pos, center_z_R),
                size=(stud_width, stud_depth, height_R),
            )

    # ---------------------------------------------------------------
    # 10. Trimmed main rafters between supporting rafters
    # ---------------------------------------------------------------
    for idx, x_r in enumerate(interior_x):
        # Intersections with valleys in X
        candidates = []

        if abs(valley_top_L.x - bottom_L.x) > 1e-6:
            tL = (x_r - bottom_L.x) / (valley_top_L.x - bottom_L.x)
            if 0.0 <= tL <= 1.0:
                P_L = bottom_L.lerp(valley_top_L, tL)
                candidates.append((abs(P_L.x - x_r), P_L))

        if abs(valley_top_R.x - bottom_R.x) > 1e-6:
            tR = (x_r - bottom_R.x) / (valley_top_R.x - bottom_R.x)
            if 0.0 <= tR <= 1.0:
                P_R = bottom_R.lerp(valley_top_R, tR)
                candidates.append((abs(P_R.x - x_r), P_R))

        if not candidates:
            continue

        candidates.sort(key=lambda c: c[0])
        P_valley = candidates[0][1]

        ridge_pt = Vector((x_r, 0.0, ridge_height))
        eave_pt = Vector((x_r, y_eave, z_eave))

        # top segment – Dormer_TrimmedTop members
        create_prismatic_member(
            name=f"D{dormer_id}_Dormer_TrimmedTop_{idx}",
            start=ridge_pt,
            end=P_valley,
            width=main_rafter_width,
            depth=main_rafter_depth,
        )

        # bottom segment – Dormer_TrimmedBottom members
        H = Vector((x_r, front_y, z_front_roof))
        create_prismatic_member(
            name=f"D{dormer_id}_Dormer_TrimmedBottom_{idx}",
            start=eave_pt,
            end=H,
            width=main_rafter_width,
            depth=main_rafter_depth,
        )

    # ---------------------------------------------------------------
    # 11. Top braces tying dormer rafters
    # ---------------------------------------------------------------
    brace_thickness = plate_thickness
    z_brace = ridge_z - (ridge_z - top_plate_z) * 0.3

    clear_width = width - 2.0 * stud_width
    brace_width = 0.45 * clear_width

    for i, y_pos in enumerate(dormer_rafter_y_positions):
        brace_y = y_pos - stud_depth
        brace_y = max(min(brace_y, front_y), y_ridge_back)
        box(
            name=f"D{dormer_id}_Dormer_TopBrace_{i}",
            center=(ox, brace_y, z_brace),
            size=(brace_width, stud_depth, brace_thickness),
        )

    # ---------------------------------------------------------------
    # 12. Double the main rafters directly supporting this dormer
    # ---------------------------------------------------------------
    double_support_rafters_for_dormer(
        main_geom,
        x_positions=[x_left, x_right],
        dormer_id=dormer_id,
    )


# ---------------------------------------------------------------------------
# SCENE ASSEMBLY
# ---------------------------------------------------------------------------

def build_scene():
    # Main hip roof
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

    # Dormer positioning along X (three dormers)
    center_offsets = [
        -5.0 * rafter_spacing,
        0.0,
        5.0 * rafter_spacing,
    ]

    support_half = 1.5 * rafter_spacing

    # Clear a continuous band in the north slope where all three dormers live
    clear_min = min(cx - support_half for cx in center_offsets) + 0.05
    clear_max = max(cx + support_half for cx in center_offsets) - 0.05
    north_clear_range = (clear_min, clear_max)

    # South T-wing dimensions
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

    # Common dormer parameters
    dormer_origin_y = half_W - 0.8
    dormer_stud_width = 0.08
    support_half = 1.5 * rafter_spacing
    dormer_width = dormer_stud_width + 2.0 * support_half

    # Three dormers on the north side, evenly aligned to rafter grid
    for d_id, cx in enumerate(center_offsets):
        origin = (cx, dormer_origin_y, 0.0)
        build_dormer_on_north_slope(
            main_geom=main_geom,
            origin=origin,
            width=dormer_width,
            depth=1.6,
            wall_height=1.2,
            roof_pitch_deg=35.0,
            stud_width=dormer_stud_width,
            rafter_spacing=0.40,  # dense dormer rafters
            dormer_id=d_id,
        )

    # Add full rafters between dormers on the north side
    gap_xs = []
    for i in range(len(center_offsets) - 1):
        gap_xs.append(0.5 * (center_offsets[i] + center_offsets[i + 1]))
    add_north_gap_rafters(main_geom, gap_xs)


if __name__ == "__main__":
    #build_scene()
    build_scene_with_sheathing()

