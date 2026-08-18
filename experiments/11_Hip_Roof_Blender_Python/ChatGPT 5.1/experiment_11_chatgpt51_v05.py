# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 11 - CHATGPT 5.1 - V05
# HIP ROOF
# ------------------------------------------------------------------

import bpy
from mathutils import Vector, Matrix
import importlib
import craftbot_lib as craftbot
importlib.reload(craftbot)


# -----------------------------------------------------------
# BASIC ELEMENT CREATOR
# -----------------------------------------------------------

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


# -----------------------------------------------------------
# MAIN HIP ROOF
# -----------------------------------------------------------

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
    Main rectangular hip roof:
    - Perimeter plates
    - Common rafters
    - Hip rafters
    - King rafters at short ends
    - Ceiling joists spanning the short direction (Y)
    - Jack rafters around the hips
    """

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

    # --------- Plates ----------
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

    # --------- Ridge ----------
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

    # --------- Hip rafters ----------
    create_prismatic_member("Hip_NW", corner_NW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SW", corner_SW, ridge_W,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_NE", corner_NE, ridge_E,
                            width=hip_w, depth=hip_d)
    create_prismatic_member("Hip_SE", corner_SE, ridge_E,
                            width=hip_w, depth=hip_d)

    # --------- Common rafters along N and S ----------
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

    # --------- Jack rafters around hips ----------
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

    # --------- King rafters on short ends ----------
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

    # --------- Ceiling joists (span short direction, Y) ----------
    joist_z = plate_z - 0.18   # below plate level
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


# -----------------------------------------------------------
# SOUTH T-WING (ROTATED, WITH VALLEYS)
# -----------------------------------------------------------

def build_T_wing_rotated(main_geom,
                         wing_length=6.0,
                         wing_width=6.0):
    """
    Perpendicular gable-roof wing on the south side.

    Ridge of the wing runs in Y, creating a T-shaped roof.
    Adds valley rafters and valley jack rafters where it
    intersects the main south slope.
    """
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

    # Footprint: attached to south side, centre on X=0
    y_north = -half_W
    y_south = -half_W - wing_len_Y

    # Wing ridge (runs in Y)
    ridge_height_wing = plate_z + wing_half_X * k
    ridge_start = (0.0, y_north, ridge_height_wing)
    ridge_end   = (0.0, y_south, ridge_height_wing)

    create_prismatic_member(
        "Wing_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Wing plates (eaves) along Y at x = ± wing_half_X
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

    # Gable end at south (plate along X)
    create_prismatic_member(
        "Wing_Plate_S",
        start=(-wing_half_X, y_south, plate_z),
        end=( wing_half_X, y_south, plate_z),
        width=plate_w,
        depth=plate_d,
    )

    # Common rafters of T-wing
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

    # ---------- Valley rafters at intersection with main roof ----------
    # Define main south slope plane
    Pm1 = Vector((-half_L, -half_W, plate_z))
    Pm2 = Vector(( half_L, -half_W, plate_z))
    Pm3 = Vector(( 0.0,    0.0,    ridge_height_main))
    n_main = (Pm2 - Pm1).cross(Pm3 - Pm1)
    d_main = -n_main.dot(Pm1)

    # Valley top: intersection of wing ridge with main south slope plane
    z_ridge = ridge_height_wing
    y_valley_top = -(n_main.z * z_ridge + d_main) / n_main.y
    valley_top = Vector((0.0, y_valley_top, z_ridge))

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

    # ---------- Valley jack rafters (main roof side) ----------
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


# -----------------------------------------------------------
# DORMER – REBUILT TO MATCH TYPICAL DORMER FRAMING
# -----------------------------------------------------------

def build_dormer_from_diagram(main_geom,
                              dormer_width=3.0,
                              dormer_depth=2.0,
                              wall_height=1.0):
    """
    Gable dormer on the north slope of the main roof, following the
    logic of the 'Typical dormer framing' diagram:

    - Rectangular opening in the north roof
    - Double rafters either side of opening
    - Double header across cut rafters
    - Dormer walls (side studs + plates)
    - Dormer gable roof with ridge parallel to main ridge
    - Valley rafters and valley jack rafters
    """

    half_L = main_geom["half_L"]
    half_W = main_geom["half_W"]
    ridge_height = main_geom["ridge_height"]
    plate_z = main_geom["plate_z"]
    slope_rise = main_geom["slope_rise"]
    slope_run = main_geom["slope_run"]
    rafter_size = main_geom["rafter_size"]

    raf_w, raf_d = rafter_size
    k = slope_rise / slope_run

    # --------- Main north roof plane ---------
    Pn1 = Vector((-half_L, half_W, plate_z))
    Pn2 = Vector(( half_L, half_W, plate_z))
    Pn3 = Vector(( 0.0,   0.0,   ridge_height))
    n_main = (Pn2 - Pn1).cross(Pn3 - Pn1)
    d_main = -n_main.dot(Pn1)

    def roof_z_at(x, y):
        # Solve n_x*x + n_y*y + n_z*z + d = 0 for z
        return -(n_main.x * x + n_main.y * y + d_main) / n_main.z

    # --------- Dormer opening in plan ---------
    center_x = 0.0
    half_dW = dormer_width * 0.5
    x_L = center_x - half_dW
    x_R = center_x + half_dW

    # Choose opening position along slope
    y_front = half_W - 1.5              # front line (towards eave)
    y_back  = y_front - dormer_depth    # towards ridge
    y_mid   = 0.5 * (y_front + y_back)

    z_front_plane = roof_z_at(0.0, y_front)
    z_back_plane  = roof_z_at(0.0, y_back)

    # Four opening corners on roof plane
    FL = Vector((x_L, y_front, roof_z_at(x_L, y_front)))
    FR = Vector((x_R, y_front, roof_z_at(x_R, y_front)))
    BL = Vector((x_L, y_back,  roof_z_at(x_L, y_back)))
    BR = Vector((x_R, y_back,  roof_z_at(x_R, y_back)))

    # --------- Double rafters on main roof ---------
    for sign, tag in ((-1, "L"), (1, "R")):
        x = center_x + sign * half_dW
        eave_pt  = (x, half_W, plate_z)
        ridge_pt = (x, 0.0,    ridge_height)
        create_prismatic_member(
            f"Main_Double_Rafter_{tag}_1",
            start=eave_pt,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )
        create_prismatic_member(
            f"Main_Double_Rafter_{tag}_2",
            start=eave_pt,
            end=ridge_pt,
            width=raf_w,
            depth=raf_d,
        )

    # --------- Double header across opening ---------
    create_prismatic_member(
        "Dormer_Double_Header",
        start=FL,
        end=FR,
        width=raf_w,
        depth=raf_d * 1.25,
    )

    # --------- Dormer wall top plates (side + front/back) ---------
    top_plate_z_front = z_front_plane + wall_height

    # Front plate
    create_prismatic_member(
        "Dormer_Plate_Front",
        start=(x_L, y_front, top_plate_z_front),
        end=(x_R, y_front, top_plate_z_front),
        width=raf_w,
        depth=raf_d,
    )

    # Back plate: project back, keep same wall height above local roof
    top_plate_z_back = z_back_plane + wall_height
    create_prismatic_member(
        "Dormer_Plate_Back",
        start=(x_L, y_back, top_plate_z_back),
        end=(x_R, y_back, top_plate_z_back),
        width=raf_w,
        depth=raf_d,
    )

    # Side plates
    create_prismatic_member(
        "Dormer_Plate_W",
        start=(x_L, y_back,  top_plate_z_back),
        end=(x_L, y_front, top_plate_z_front),
        width=raf_w,
        depth=raf_d,
    )
    create_prismatic_member(
        "Dormer_Plate_E",
        start=(x_R, y_back,  top_plate_z_back),
        end=(x_R, y_front, top_plate_z_front),
        width=raf_w,
        depth=raf_d,
    )

    # --------- Dormer gable roof ---------
    dormer_run = 0.5 * dormer_depth
    # Use same pitch as main roof
    ridge_height_local = dormer_run * k
    dormer_ridge_z = 0.5 * (top_plate_z_front + top_plate_z_back) + ridge_height_local

    ridge_start = (x_L, y_mid, dormer_ridge_z)
    ridge_end   = (x_R, y_mid, dormer_ridge_z)

    create_prismatic_member(
        "Dormer_Ridge",
        start=ridge_start,
        end=ridge_end,
        width=raf_w,
        depth=raf_d,
    )

    # Dormer rafters front/back (jack rafters in the diagram sense)
    n_steps = max(int(dormer_width / 0.6), 1)
    for i in range(n_steps + 1):
        t = i / max(n_steps, 1)
        x = x_L + t * dormer_width

        plate_front = (x, y_front, top_plate_z_front)
        plate_back  = (x, y_back,  top_plate_z_back)
        ridge_pt    = (x, y_mid,   dormer_ridge_z)

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

    # --------- Valley rafters (intersection with main roof) ---------
    # Start at front upper corners of side walls, end at eave line
    for sign, tag in ((-1, "L"), (1, "R")):
        x_corner = center_x + sign * half_dW
        valley_top = Vector((x_corner, y_front, top_plate_z_front))

        # Drop to north eave, shifting x to get diagonal valley in plan
        offset_y = half_W - y_front
        valley_bottom = Vector((x_corner + sign * offset_y,
                                half_W,
                                plate_z))

        create_prismatic_member(
            f"Dormer_Valley_{tag}",
            start=valley_top,
            end=valley_bottom,
            width=raf_w,
            depth=raf_d * 1.25,
        )

        # --------- Valley jack rafters from dormer ridge to valley line ---------
        n_vj = 3
        for j in range(1, n_vj + 1):
            s = j / (n_vj + 1)

            # Point along ridge biased to that side
            if sign < 0:
                x_ridge = x_L + s * (dormer_width * 0.5)
            else:
                x_ridge = x_R - s * (dormer_width * 0.5)
            ridge_pt = Vector((x_ridge, y_mid, dormer_ridge_z))

            valley_pt = valley_top.lerp(valley_bottom, s)

            create_prismatic_member(
                f"Dormer_Valley_Jack_{tag}_{j:02d}",
                start=ridge_pt,
                end=valley_pt,
                width=raf_w,
                depth=raf_d,
            )


# -----------------------------------------------------------
# BUILD WHOLE SCENE
# -----------------------------------------------------------

def build_scene():
    # Main roof parameters
    length = 12.0   # X direction
    width = 6.0     # Y direction
    plate_z = 0.0

    slope_rise = 1.0
    slope_run = 2.0   # steeper roof than 1:3
    rafter_spacing = 0.6

    plate_size = (0.038, 0.140)
    rafter_size = (0.038, 0.184)
    ridge_size = (0.038, 0.184)
    hip_extra_depth = 0.050

    # Main hip roof
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

    # South T-wing with valleys
    build_T_wing_rotated(
        main_geom=main_geom,
        wing_length=6.0,
        wing_width=6.0,
    )

    # North dormer framed according to the manual diagram
    build_dormer_from_diagram(
        main_geom=main_geom,
        dormer_width=3.0,
        dormer_depth=2.0,
        wall_height=1.0,
    )


if __name__ == "__main__":
    build_scene()
