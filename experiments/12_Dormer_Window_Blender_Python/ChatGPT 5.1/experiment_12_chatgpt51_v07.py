# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 12 - CHATGPT 5.1 - V07
# DORMER WINDOW
# ------------------------------------------------------------------

import bpy
import math
import importlib

import craftbot_lib as craftbot  # ensure this is on your Python path
from mathutils import Vector, Matrix

importlib.reload(craftbot)  # convenient when iterating in Blender


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
# Helper: sloping member between two 3D points
#   E = one endpoint, R = other endpoint
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

    # Local X follows the member axis.
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
        # jack rafters on dormer / valley
        num_dormer_jacks=3,
        # trimmed centre rafters (magenta in diagram)
        num_trimmed_center_rafters=3,
):
    """
    Build a doghouse dormer plus a simple main roof around it.

    origin: (x, y, z) of the bottom-center of the dormer FRONT wall.
    Units are Blender units (typically metres if the scene uses metric).
    """

    ox, oy, oz = origin

    # ---------------------------------------------------------------
    # Base dormer dimensions
    # ---------------------------------------------------------------
    half_w = width * 0.5
    front_y = oy
    back_y = oy - depth

    wall_base_z = oz
    wall_top_z = wall_base_z + wall_height
    top_plate_z = wall_top_z + plate_thickness * 0.5

    x_left = ox - half_w + stud_width * 0.5
    x_right = ox + half_w - stud_width * 0.5

    # Dormer roof geometry
    roof_pitch_rad = math.radians(roof_pitch_deg)
    m_dormer = math.tan(roof_pitch_rad)
    run = half_w + overhang
    rise = run * m_dormer
    ridge_z = top_plate_z + rise

    # ---------------------------------------------------------------
    # Main roof geometry
    # ---------------------------------------------------------------
    main_pitch_rad = math.radians(main_roof_pitch_deg)
    main_tan = math.tan(main_pitch_rad)

    # Main ridge behind dormer along -Y
    y_main_ridge = back_y - main_run_to_back
    z_main_ridge = top_plate_z + main_run_to_back * main_tan

    # Eaves further downslope (+Y)
    y_eave = y_main_ridge + main_run_to_eave
    z_eave = z_main_ridge - main_run_to_eave * main_tan

    def z_on_main_roof(y):
        """Z on main roof plane for any given y."""
        return z_main_ridge - main_tan * (y - y_main_ridge)

    z_front_roof = z_on_main_roof(front_y)
    z_back_roof = z_on_main_roof(back_y)

    # ----------------------------------------------------------------
    # Valley helper geometry (before we actually place anything)
    # ----------------------------------------------------------------
    # Valley feet: intersection of main roof plane with line y = back_y
    z_bottom = z_back_roof
    bottom_L = Vector((x_left, back_y, z_bottom))
    bottom_R = Vector((x_right, back_y, z_bottom))

    # Provisional valley tops at main ridge (used for interpolation)
    top_L_prov = Vector((
        ox + (z_main_ridge - ridge_z) / m_dormer,
        y_main_ridge,
        z_main_ridge,
    ))
    top_R_prov = Vector((
        ox - (z_main_ridge - ridge_z) / m_dormer,
        y_main_ridge,
        z_main_ridge,
    ))

    def intersect_segment_with_z(p0, p1, z_target):
        """Linear interpolate along segment p0->p1 to reach z=z_target."""
        z0 = p0.z
        z1 = p1.z
        if abs(z1 - z0) < 1e-6:
            return Vector((p0.x, p0.y, z_target))
        t = (z_target - z0) / (z1 - z0)
        return p0.lerp(p1, t)

    # Intersection of valleys with horizontal plane z = ridge_z
    top_L = intersect_segment_with_z(bottom_L, top_L_prov, ridge_z)
    top_R = intersect_segment_with_z(bottom_R, top_R_prov, ridge_z)

    # Common Y of these intersections (where valleys hit extended dormer ridge)
    y_ridge_back = float(top_L.y)
    z_header_roof = z_on_main_roof(y_ridge_back)

    # ----------------------------------------------------------------
    # 1. Front window framing and basic studs
    #    (Back corner studs removed as requested)
    # ----------------------------------------------------------------
    stud_center_z = wall_base_z + wall_height * 0.5

    # Front jamb studs
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
    # 2. Top plates (FRONT ONLY – back plate removed)
    # ----------------------------------------------------------------
    box(
        name="Dormer_TopPlate_FB_0",
        center=(ox, front_y, top_plate_z),
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
    # 3. Dormer ridge (extended upslope until it meets the large roof)
    # ----------------------------------------------------------------
    ridge_y_min = y_ridge_back  # where ridge hits the main roof
    ridge_y_max = front_y
    ridge_len_y = ridge_y_max - ridge_y_min
    ridge_center_y = (ridge_y_min + ridge_y_max) * 0.5

    box(
        name="Dormer_Ridge",
        center=(ox, ridge_center_y, ridge_z),
        size=(rafter_width, ridge_len_y, rafter_depth),
    )

    # ----------------------------------------------------------------
    # 4. Dormer common rafters (left & right at each Y position)
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
    # 5. Gable stud FRONT ONLY (back gable stud removed)
    # ----------------------------------------------------------------
    gable_base_z = header_z + plate_thickness
    gable_top_z = ridge_z - rafter_depth * 0.5
    gable_height = max(0.0, gable_top_z - gable_base_z)
    if gable_height > 0.0:
        gable_center_z = gable_base_z + gable_height * 0.5
        box(
            name="Dormer_Gable_Stud_0",
            center=(ox, front_y, gable_center_z),
            size=(stud_width, stud_depth, gable_height),
        )

    # ----------------------------------------------------------------
    # 6. Main roof rafters (host roof)
    #    - aligned with dormer studs
    #    - split below dormer into lower + upper (trimmed)
    #    - doubled rafters at x_left and x_right
    # ----------------------------------------------------------------
    main_half_width = width * main_roof_width_factor

    x_positions = set()
    x_positions.add(x_left)
    x_positions.add(x_right)

    # extend to left
    x = x_left - main_rafter_spacing_x
    while x >= ox - main_half_width:
        x_positions.add(x)
        x -= main_rafter_spacing_x

    # extend to right
    x = x_right + main_rafter_spacing_x
    while x <= ox + main_half_width:
        x_positions.add(x)
        x += main_rafter_spacing_x

    x_positions = sorted(x_positions)

    double_offset = main_rafter_width * 0.35  # small side-by-side offset

    for i, x_pos in enumerate(x_positions):
        ridge_point = (x_pos, y_main_ridge, z_main_ridge)
        eave_point = (x_pos, y_eave, z_eave)

        # Rafters that directly support the dormer (at its sides) are doubled.
        if abs(x_pos - x_left) < 1e-6 or abs(x_pos - x_right) < 1e-6:
            for k, dx in enumerate((-double_offset, double_offset)):
                x_off = x_pos + dx
                ridge_off = (x_off, y_main_ridge, z_main_ridge)
                eave_off = (x_off, y_eave, z_eave)
                rafter_between(
                    name=f"MainRoof_RafterSupport_{i}_{k}",
                    E=eave_off,
                    R=ridge_off,
                    section_y=main_rafter_width,
                    section_z=main_rafter_depth,
                )
            continue

        # Rafters under dormer centre are split: lower + upper (trimmed)
        if x_left < x_pos < x_right:
            # lower part: eave -> dormer front header line
            front_pt = (x_pos, front_y, z_front_roof)
            rafter_between(
                name=f"MainRoof_RafterLower_{i}",
                E=eave_point,
                R=front_pt,
                section_y=main_rafter_width,
                section_z=main_rafter_depth,
            )

            # upper part: from double header (y_ridge_back) -> main ridge
            header_pt = (x_pos, y_ridge_back, z_header_roof)
            rafter_between(
                name=f"MainRoof_RafterUpper_{i}",
                E=header_pt,
                R=ridge_point,
                section_y=main_rafter_width,
                section_z=main_rafter_depth,
            )
        else:
            # full rafter
            rafter_between(
                name=f"MainRoof_Rafter_{i}",
                E=eave_point,
                R=ridge_point,
                section_y=main_rafter_width,
                section_z=main_rafter_depth,
            )

    # ----------------------------------------------------------------
    # 7. EXTRA trimmed centre rafters (magenta in reference)
    #    Explicitly add a few cut rafters inside the dormer width,
    #    even if they do not coincide with the global rafter spacing.
    # ----------------------------------------------------------------
    if num_trimmed_center_rafters > 0:
        for j in range(num_trimmed_center_rafters):
            t = (j + 1) / (num_trimmed_center_rafters + 1.0)
            x_cut = x_left + t * (x_right - x_left)

            # lower trimmed piece: eave -> dormer front
            eave_pt = (x_cut, y_eave, z_eave)
            front_pt = (x_cut, front_y, z_front_roof)
            rafter_between(
                name=f"Trimmed_RafterLower_{j}",
                E=eave_pt,
                R=front_pt,
                section_y=main_rafter_width,
                section_z=main_rafter_depth,
            )

            # upper trimmed piece: double header -> main ridge
            header_pt = (x_cut, y_ridge_back, z_header_roof)
            ridge_pt = (x_cut, y_main_ridge, z_main_ridge)
            rafter_between(
                name=f"Trimmed_RafterUpper_{j}",
                E=header_pt,
                R=ridge_pt,
                section_y=main_rafter_width,
                section_z=main_rafter_depth,
            )

    # ----------------------------------------------------------------
    # 8. Valley rafters – trimmed where they hit the extended dormer ridge
    # ----------------------------------------------------------------
    valley_top_L = top_L  # already on z = ridge_z
    valley_top_R = top_R

    rafter_between(
        name="Valley_Rafter_Left",
        E=bottom_L,
        R=valley_top_L,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    rafter_between(
        name="Valley_Rafter_Right",
        E=bottom_R,
        R=valley_top_R,
        section_y=main_rafter_width,
        section_z=main_rafter_depth,
    )

    # ----------------------------------------------------------------
    # 9. Double header at valley/ridge intersection (spanning across rafters)
    #    Supports the back end of the dormer ridge and crosses multiple rafters.
    # ----------------------------------------------------------------
    # Find first rafters left and right of the dormer opening
    x_header_left = max(x for x in x_positions if x < x_left)
    x_header_right = min(x for x in x_positions if x > x_right)

    header_center_x = 0.5 * (x_header_left + x_header_right)
    header_len_x = x_header_right - x_header_left
    header_y = y_ridge_back
    header_z = ridge_z

    header_offset = stud_depth * 0.3

    box(
        name="Dormer_DoubleHeader_A",
        center=(header_center_x, header_y - header_offset, header_z),
        size=(header_len_x, stud_depth, main_rafter_depth),
    )
    box(
        name="Dormer_DoubleHeader_B",
        center=(header_center_x, header_y + header_offset, header_z),
        size=(header_len_x, stud_depth, main_rafter_depth),
    )

    # ----------------------------------------------------------------
    # 10. Jack rafters between extended Dormer_Ridge and Valley_Rafters
    # ----------------------------------------------------------------
    if num_dormer_jacks > 0:
        for j in range(num_dormer_jacks):
            t = (j + 1) / (num_dormer_jacks + 1.0)
            # Y between back_y and y_ridge_back
            y_j = back_y + t * (y_ridge_back - back_y)

            # Point on left valley at y_j
            if abs(valley_top_L.y - bottom_L.y) > 1e-6:
                tv = (y_j - bottom_L.y) / (valley_top_L.y - bottom_L.y)
            else:
                tv = 0.0
            P_valley_L = bottom_L.lerp(valley_top_L, tv)
            P_valley_R = bottom_R.lerp(valley_top_R, tv)

            # Corresponding point on extended dormer ridge
            P_ridge = Vector((ox, y_j, ridge_z))

            rafter_between(
                name=f"Dormer_Jack_L_{j}",
                E=P_valley_L,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )
            rafter_between(
                name=f"Dormer_Jack_R_{j}",
                E=P_valley_R,
                R=P_ridge,
                section_y=rafter_width,
                section_z=rafter_depth,
            )

    # ----------------------------------------------------------------
    # 11. Lower front support beam for the dormer
    # ----------------------------------------------------------------
    box(
        name="Dormer_FrontSupportBeam",
        center=(ox, front_y, z_front_roof),
        size=(width, stud_depth, main_rafter_depth),
    )

    # ----------------------------------------------------------------
    # 12. Vertical side studs from dormer rafters down to main roof rafters
    # ----------------------------------------------------------------
    # Rafter underside on each side (constant along Y)
    z_raf_center_left = ridge_z + m_dormer * (x_left - ox)
    z_raf_under_left = z_raf_center_left - rafter_depth * 0.5

    z_raf_center_right = ridge_z - m_dormer * (x_right - ox)
    z_raf_under_right = z_raf_center_right - rafter_depth * 0.5

    for i, y_pos in enumerate(dormer_rafter_y_positions):
        # Top is underside of dormer rafter
        top_L = z_raf_under_left
        top_R = z_raf_under_right

        # Bottom is top of main roof rafter (or roof plane) at this y
        z_main_y = z_on_main_roof(y_pos)
        bottom = z_main_y + main_rafter_depth * 0.5

        height_L = max(0.0, top_L - bottom)
        height_R = max(0.0, top_R - bottom)

        if height_L > 0.0:
            center_z_L = bottom + 0.5 * height_L
            box(
                name=f"Dormer_SideStud_L_{i}",
                center=(x_left, y_pos, center_z_L),
                size=(stud_width, stud_depth, height_L),
            )
        if height_R > 0.0:
            center_z_R = bottom + 0.5 * height_R
            box(
                name=f"Dormer_SideStud_R_{i}",
                center=(x_right, y_pos, center_z_R),
                size=(stud_width, stud_depth, height_R),
            )

    # ----------------------------------------------------------------
    # 13. Horizontal top braces tying dormer rafters
    #     Shifted by one profile thickness in -Y and trimmed so they
    #     stay within the dormer roof volume (green markings).
    # ----------------------------------------------------------------
    brace_thickness = plate_thickness
    z_brace = ridge_z - (ridge_z - top_plate_z) * 0.3
    # Trimmed length: shorter than the dormer width, clearly inside.
    brace_width = max(0.0, width - 4.0 * stud_width)

    for i, y_pos in enumerate(dormer_rafter_y_positions):
        # Shift by one profile thickness in -Y
        brace_y = y_pos - stud_depth
        # Clamp to stay between front_y and ridge back line
        brace_y = max(min(brace_y, front_y), y_ridge_back)
        box(
            name=f"Dormer_TopBrace_{i}",
            center=(ox, brace_y, z_brace),
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
