# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 12 - CHATGPT 5.1 - V02
# DORMER WINDOW
# ------------------------------------------------------------------

import bpy
import math
import importlib

import craftbot_lib as craftbot  # ensure this is on your Python path
from mathutils import Vector, Matrix

importlib.reload(craftbot)  # handy while iterating


# -------------------------------------------------------------------
# Helper: simple axis-aligned box
#   size = (sx, sy, sz) in WORLD units (full extents)
# -------------------------------------------------------------------
def box(name, center, size):
    cx, cy, cz = center
    sx, sy, sz = size
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        scale=(sx * 0.5, sy * 0.5, sz * 0.5),
    )


# -------------------------------------------------------------------
# Helper: sloping rafter box between two 3D points
#   E = eave point, R = ridge point (order does not matter)
#   section_y = width of timber (local Y)
#   section_z = depth of timber (local Z)
# -------------------------------------------------------------------
def rafter_between(name, E, R, section_y, section_z):
    v_e = Vector(E)
    v_r = Vector(R)
    direction = v_r - v_e
    length = direction.length
    if length == 0.0:
        return  # degenerate

    center = (v_e + v_r) * 0.5
    dir_norm = direction.normalized()

    # Local X will follow the rafter axis.
    q = dir_norm.to_track_quat('X', 'Z')
    R_mat = q.to_matrix().to_4x4()

    # Scale: half-length along X, section dims along Y/Z
    S_mat = Matrix.Diagonal(
        (length * 0.5, section_y * 0.5, section_z * 0.5, 1.0)
    )
    T_mat = Matrix.Translation(center)

    M_world = T_mat @ R_mat @ S_mat

    craftbot.place_element(
        name=name,
        matrix=M_world,
    )


# -------------------------------------------------------------------
# Main dormer + host roof constructor
# -------------------------------------------------------------------
def build_dormer_with_host_roof(
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
        # main roof parameters
        main_roof_pitch_deg=35.0,
        main_run_to_back=2.0,
        main_run_to_eave=4.0,
        main_roof_width_factor=2.0,
        main_rafter_spacing_x=0.40,
        main_rafter_width=0.07,
        main_rafter_depth=0.10,
):
    """
    Build a doghouse dormer plus a simple main roof around it.

    origin: (x, y, z) of the bottom-center of the dormer FRONT wall.
    Units are Blender units (typically meters if scene uses metric).
    """

    ox, oy, oz = origin

    # Basic derived values for dormer
    half_w = width * 0.5
    front_y = oy
    back_y = oy - depth

    wall_base_z = oz
    wall_top_z = wall_base_z + wall_height
    top_plate_z = wall_top_z + plate_thickness * 0.5

    # ----------------------------------------------------------------
    # 1. Corner studs (4)
    # ----------------------------------------------------------------
    x_left = ox - half_w + stud_width * 0.5
    x_right = ox + half_w - stud_width * 0.5
    stud_center_z = wall_base_z + wall_height * 0.5

    corners = [
        (x_left,  front_y),
        (x_right, front_y),
        (x_left,  back_y),
        (x_right, back_y),
    ]

    for i, (cx, cy) in enumerate(corners):
        box(
            name=f"Dormer_Stud_{i}",
            center=(cx, cy, stud_center_z),
            size=(stud_width, stud_depth, wall_height),
        )

    # ----------------------------------------------------------------
    # 2. Front window framing
    # ----------------------------------------------------------------
    window_width = width * 0.6
    window_height = wall_height * 0.6
    sill_height = wall_height * 0.25

    w_half = window_width * 0.5
    x_win_left = ox - w_half + stud_width * 0.5
    x_win_right = ox + w_half - stud_width * 0.5

    # Jamb studs (front wall)
    for i, x_jamb in enumerate((x_win_left, x_win_right)):
        box(
            name=f"Dormer_Window_Jamb_{i}",
            center=(x_jamb, front_y, stud_center_z),
            size=(stud_width, stud_depth, wall_height),
        )

    # Sill and header
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

    # ----------------------------------------------------------------
    # 3. Top plates (front/back + sides)
    # ----------------------------------------------------------------
    # Front & back plates running in X
    for i, y_val in enumerate((front_y, back_y)):
        box(
            name=f"Dormer_TopPlate_FB_{i}",
            center=(ox, y_val, top_plate_z),
            size=(width, stud_depth, plate_thickness),
        )

    # Side plates running in Y
    side_plate_center_y = (front_y + back_y) * 0.5
    for i, x_val in enumerate((x_left, x_right)):
        box(
            name=f"Dormer_TopPlate_Side_{i}",
            center=(x_val, side_plate_center_y, top_plate_z),
            size=(stud_width, depth, plate_thickness),
        )

    # ----------------------------------------------------------------
    # 4. Ridge beam for dormer
    # ----------------------------------------------------------------
    roof_pitch_rad = math.radians(roof_pitch_deg)
    run = half_w + overhang
    rise = run * math.tan(roof_pitch_rad)
    ridge_z = top_plate_z + rise

    ridge_center = (ox, side_plate_center_y, ridge_z)
    box(
        name="Dormer_Ridge",
        center=ridge_center,
        size=(rafter_width, depth, rafter_depth),
    )

    # ----------------------------------------------------------------
    # 5. Dormer common rafters (left & right at each Y position)
    # ----------------------------------------------------------------
    num_rafters = max(2, int(depth / rafter_spacing) + 1)
    dormer_rafter_y_positions = []

    for i in range(num_rafters):
        # Clamp last rafter exactly to back wall
        t = min(i * rafter_spacing, depth)
        y_pos = front_y - t

        dormer_rafter_y_positions.append(y_pos)

        # Eaves sit on top of plates, at outer side of walls
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

    # ----------------------------------------------------------------
    # 6. Optional: small gable studs in front/back (above header)
    # ----------------------------------------------------------------
    gable_base_z = header_z + plate_thickness
    gable_top_z = ridge_z - rafter_depth * 0.5
    gable_height = max(0.0, gable_top_z - gable_base_z)
    if gable_height > 0.0:
        gable_center_z = gable_base_z + gable_height * 0.5

        # Simple center stud front & back
        for i, y_val in enumerate((front_y, back_y)):
            box(
                name=f"Dormer_Gable_Stud_{i}",
                center=(ox, y_val, gable_center_z),
                size=(stud_width, stud_depth, gable_height),
            )

    # ----------------------------------------------------------------
    # 7. Main roof rafters (host roof)
    # ----------------------------------------------------------------
    main_pitch_rad = math.radians(main_roof_pitch_deg)
    main_tan = math.tan(main_pitch_rad)

    # Position of main ridge behind dormer along -Y
    # We specify distance from ridge to dormer back wall (positive).
    y_main_ridge = back_y - main_run_to_back

    # Choose ridge height so that the main roof plane passes through
    # the dormer top plates at the back wall (x = ox, y = back_y).
    z_main_ridge = top_plate_z + main_run_to_back * main_tan

    # Eaves further down the slope towards +Y
    y_eave = y_main_ridge + main_run_to_eave
    z_eave = z_main_ridge - main_run_to_eave * main_tan

    # Span of main roof in X
    main_half_width = width * main_roof_width_factor
    x_min = ox - main_half_width
    x_max = ox + main_half_width

    num_main_rafters = max(2, int((x_max - x_min) / main_rafter_spacing_x) + 1)

    for i in range(num_main_rafters):
        x_pos = x_min + i * main_rafter_spacing_x
        ridge_point = (x_pos, y_main_ridge, z_main_ridge)
        eave_point = (x_pos, y_eave, z_eave)

        rafter_between(
            name=f"MainRoof_Rafter_{i}",
            E=eave_point,
            R=ridge_point,
            section_y=main_rafter_width,
            section_z=main_rafter_depth,
        )

    # ----------------------------------------------------------------
    # 8. Valley rafters connecting dormer to main ridge
    # ----------------------------------------------------------------
    # Dormer roof slope in X is tan(roof_pitch)
    m_dormer = math.tan(roof_pitch_rad)

    # Left valley: intersection of main roof and left dormer roof
    x_valley_left = x_left
    z_bottom_L = ridge_z + m_dormer * (x_valley_left - ox)
    # y from main roof plane
    y_bottom_L = y_main_ridge - (z_bottom_L - z_main_ridge) / main_tan

    # Top point on main ridge where it meets the dormer roof plane
    x_top_L = ox + (z_main_ridge - ridge_z) / m_dormer
    top_L = (x_top_L, y_main_ridge, z_main_ridge)
    bottom_L = (x_valley_left, y_bottom_L, z_bottom_L)

    rafter_between(
        name="Valley_Rafter_Left",
        E=bottom_L,
        R=top_L,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    # Right valley: intersection of main roof and right dormer roof
    x_valley_right = x_right
    z_bottom_R = ridge_z - m_dormer * (x_valley_right - ox)
    y_bottom_R = y_main_ridge - (z_bottom_R - z_main_ridge) / main_tan

    x_top_R = ox - (z_main_ridge - ridge_z) / m_dormer
    top_R = (x_top_R, y_main_ridge, z_main_ridge)
    bottom_R = (x_valley_right, y_bottom_R, z_bottom_R)

    rafter_between(
        name="Valley_Rafter_Right",
        E=bottom_R,
        R=top_R,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    # ----------------------------------------------------------------
    # 9. Vertical side studs from dormer top plates to dormer rafters
    # ----------------------------------------------------------------
    # Top of plate and underside of rafter (same for all rafters)
    top_of_plate_z = top_plate_z + plate_thickness * 0.5

    # Left side: rafter centerline height at x_left, minus half depth
    z_raf_center_left = ridge_z + m_dormer * (x_left - ox)
    z_raf_under_left = z_raf_center_left - rafter_depth * 0.5
    side_stud_height_left = max(0.0, z_raf_under_left - top_of_plate_z)

    # Right side: similar but mirrored slope
    z_raf_center_right = ridge_z - m_dormer * (x_right - ox)
    z_raf_under_right = z_raf_center_right - rafter_depth * 0.5
    side_stud_height_right = max(0.0, z_raf_under_right - top_of_plate_z)

    if side_stud_height_left > 0.0 and side_stud_height_right > 0.0:
        z_center_left = top_of_plate_z + side_stud_height_left * 0.5
        z_center_right = top_of_plate_z + side_stud_height_right * 0.5

        for i, y_pos in enumerate(dormer_rafter_y_positions):
            # Left side stud under each dormer rafter
            box(
                name=f"Dormer_SideStud_L_{i}",
                center=(x_left, y_pos, z_center_left),
                size=(stud_width, stud_depth, side_stud_height_left),
            )
            # Right side stud
            box(
                name=f"Dormer_SideStud_R_{i}",
                center=(x_right, y_pos, z_center_right),
                size=(stud_width, stud_depth, side_stud_height_right),
            )

    # ----------------------------------------------------------------
    # 10. Horizontal top braces tying dormer rafters
    # ----------------------------------------------------------------
    brace_thickness = plate_thickness
    # Somewhere between top plate and ridge
    z_brace = ridge_z - (ridge_z - top_plate_z) * 0.3
    brace_width = width - stud_width  # inside the side studs

    for i, y_pos in enumerate(dormer_rafter_y_positions):
        box(
            name=f"Dormer_TopBrace_{i}",
            center=(ox, y_pos, z_brace),
            size=(brace_width, stud_depth, brace_thickness),
        )


# -------------------------------------------------------------------
# Execute with a reasonable default
# -------------------------------------------------------------------
build_dormer_with_host_roof(
    origin=(0.0, 0.0, 0.0),
    width=2.0,
    depth=1.6,
    wall_height=1.2,
    roof_pitch_deg=35.0,
)
