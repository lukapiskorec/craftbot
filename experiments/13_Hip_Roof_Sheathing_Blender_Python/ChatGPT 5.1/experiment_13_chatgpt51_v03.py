# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 13 - CHATGPT 5.1 - V03
# HIP ROOF WITH BOARD SHEATHING
#
# Requires both `craftbot_lib.py` and `experiment_11_chatgpt51_v18.py` to run
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix
import importlib

import craftbot_lib as craftbot
import experiment_11_chatgpt51_v18 as base

importlib.reload(craftbot)
importlib.reload(base)


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
    axis_y = axis_z.cross(axis_x).normalized()  # ensure orthonormal basis

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
                    gy0, gy1 = gy1, gx0

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

    # Dormer position along Y:
    # front_y = front face / eave line
    # back_y  = intersection line with main roof (plan view)
    front_y = oy
    back_y = oy - depth

    wall_base_z = oz
    wall_top_z = wall_base_z + wall_height
    top_plate_z = wall_top_z + plate_thickness * 0.5

    # Dormer roof pitch
    roof_pitch_rad = math.radians(roof_pitch_deg)
    m_dormer = math.tan(roof_pitch_rad)
    run = half_w + overhang
    rise = run * m_dormer
    ridge_z = top_plate_z + rise

    # Y where the main roof equals the dormer ridge height
    # (header / valley line in plan)
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

    The dormer roof boards run from the front eave line (front_y)
    back to the intersection with the main roof (back_y). This prevents
    the dormer sheathing from running under the main roof into the
    interior.
    """

    ox, oy, oz = dormer_geom["origin"]
    front_y = dormer_geom["front_y"]
    back_y = dormer_geom["back_y"]
    x_eave_L = dormer_geom["x_eave_L"]
    x_eave_R = dormer_geom["x_eave_R"]
    ridge_z = dormer_geom["ridge_z"]
    top_plate_z = dormer_geom["top_plate_z"]

    # Left roof plane: from dormer eave at front_y back to the
    # intersection with the main roof at back_y.
    P00_L = Vector((x_eave_L, back_y,      top_plate_z))
    P10_L = Vector((x_eave_L, front_y,     top_plate_z))
    P11_L = Vector((ox,       front_y,     ridge_z))
    P01_L = Vector((ox,       back_y,      ridge_z))

    # Right roof plane (mirror of the left)
    P00_R = Vector((x_eave_R, back_y,      top_plate_z))
    P10_R = Vector((x_eave_R, front_y,     top_plate_z))
    P11_R = Vector((ox,       front_y,     ridge_z))
    P01_R = Vector((ox,       back_y,      ridge_z))

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

    # --- Dormer layout on the north slope ---
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

    # --- Main hip roof framing (imported from experiment_11) ---
    main_geom = base.build_main_hip_roof(
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

    # We rely on main_geom containing keys used by the sheathing routines
    # (half_L, half_W, plate_z, ridge_height, ridge_half, slope_rise, slope_run,
    #  rafter_spacing, etc.) – this is how build_main_hip_roof is defined
    # in experiment_11_chatgpt51_v18.py.

    # --- T-wing framing ---
    base.build_T_wing_rotated(
        main_geom=main_geom,
        wing_length=wing_length,
        wing_width=wing_width,
    )

    # --- Dormer framing & sheathing ---

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

    for d_id, cx in enumerate(center_offsets):
        origin = (cx, dormer_origin_y, 0.0)

        # Structural dormer
        base.build_dormer_on_north_slope(
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

        # Dormer roof sheathing for this dormer
        add_dormer_board_sheathing(
            main_geom=main_geom,
            dormer_geom=d_geom,
            board_width=0.15,      # keep dormer board width as before
            board_thickness=0.02,
            dormer_id=d_id,
            name_prefix="SheathDormer",
        )

        # Gap under this dormer on the north main slope:
        # bounded by the support rafters and the *back* of the dormer
        # in plan (back_y). The triangular area above each dormer
        # is left to the main roof sheathing.
        north_gaps_xy.append((
            d_geom["x_support_L"],
            d_geom["x_support_R"],
            d_geom["back_y"],
            d_geom["front_y"],
        ))

    # Restore full rafters between dormers on the north side
    gap_xs = []
    for i in range(len(center_offsets) - 1):
        gap_xs.append(0.5 * (center_offsets[i] + center_offsets[i + 1]))
    base.add_north_gap_rafters(main_geom, gap_xs)

    # --- Main roof sheathing (with dormer openings) ---
    # Use slightly narrower boards (0.12) on the large roof to avoid
    # visual overlap; dormers stay at 0.15 m.
    add_main_roof_board_sheathing(
        main_geom=main_geom,
        board_width=0.12,
        board_thickness=0.02,
        dormer_gaps_xy=north_gaps_xy,
        name_prefix="SheathMain",
    )

    # --- T-wing sheathing ---
    add_T_wing_board_sheathing(
        main_geom=main_geom,
        wing_length=wing_length,
        wing_width=wing_width,
        board_width=0.12,   # match large roof module
        board_thickness=0.02,
        name_prefix="SheathWing",
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build_scene_with_sheathing()
