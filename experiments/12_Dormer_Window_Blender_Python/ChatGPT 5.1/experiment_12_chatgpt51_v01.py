# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 12 - CHATGPT 5.1 - V01
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
#   E = eave point, R = ridge point
#   section_y = width of timber (local Y)
#   section_z = depth of timber (local Z)
#   Uses the `matrix` argument of place_element(). :contentReference[oaicite:3]{index=3}
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
    # 'up' is chosen as global Z as much as possible.
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
# Main dormer constructor
# -------------------------------------------------------------------
def build_dormer(
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
):
    """
    Build a simple doghouse dormer as a set of scaled cubes.

    origin: (x, y, z) of the bottom-center of the FRONT wall.
    Units are Blender units (typically meters if scene is set that way).
    """

    ox, oy, oz = origin

    # Basic derived values
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
    # 4. Ridge beam
    # ----------------------------------------------------------------
    pitch_rad = math.radians(roof_pitch_deg)
    run = half_w + overhang
    rise = run * math.tan(pitch_rad)
    ridge_z = top_plate_z + rise

    ridge_center = (ox, side_plate_center_y, ridge_z)
    box(
        name="Dormer_Ridge",
        center=ridge_center,
        size=(rafter_width, depth, rafter_depth),
    )

    # ----------------------------------------------------------------
    # 5. Common rafters (left & right at each Y position)
    # ----------------------------------------------------------------
    num_rafters = max(2, int(depth / rafter_spacing) + 1)

    for i in range(num_rafters):
        # Clamp last rafter exactly to back wall
        t = min(i * rafter_spacing, depth)
        y_pos = front_y - t

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


# -------------------------------------------------------------------
# Execute with a reasonable default
# -------------------------------------------------------------------
build_dormer(
    origin=(0.0, 0.0, 0.0),
    width=2.0,
    depth=1.6,
    wall_height=1.2,
    roof_pitch_deg=35.0,
)
