# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 03 - CHATGPT 5.1 - V04
# DESCRIPTION: VIPP SHELTER
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # make sure this is on Blender's sys.path

importlib.reload(craftbot)


# ------------------------------------------------------------------
# GLOBAL PARAMETERS  (all dimensions in meters)

# Overall geometry
UNIT_LENGTH = 11.5   # X
UNIT_WIDTH  = 5.2    # Y
WALL_HEIGHT = 3.0    # clear wall height from finished floor

# Support posts
POST_HEIGHT = 0.8
POST_SIZE   = 0.25   # square

# Floor / roof build-up
FLOOR_THICK = 0.30   # solid floor cassette & finish
ROOF_THICK  = 0.25   # solid roof build-up

# Timber sections
STUD_THICK  = 0.045  # thickness across wall
STUD_WIDTH  = 0.095  # width in plane of wall

PLATE_THICK = STUD_THICK
PLATE_WIDTH = STUD_WIDTH

JOIST_THICK = 0.045
JOIST_DEPTH = 0.195

STUD_SPACING = 0.6   # typical c/c spacing

# Loft
LOFT_LENGTH      = 5.0
LOFT_WIDTH       = 2.5
LOFT_CLEAR       = 2.2
LOFT_DECK_THICK  = 0.025

# Large side window opening in long walls
WINDOW_OPENING_MARGIN = 1.5       # from each short end
WINDOW_HEAD_HEIGHT    = 2.2       # head above finished floor
WINDOW_SILL_HEIGHT    = 0.3       # visual sill (not used structurally here)

# Skylight openings (in roof plane)
SKY1_LENGTH   = 3.8               # central skylight (over living)
SKY1_WIDTH    = 1.6
SKY1_CENTER_X = 0.0
SKY1_CENTER_Y = 0.0

SKY2_LENGTH   = 3.0               # loft skylight (over bed)
SKY2_WIDTH    = 2.2
SKY2_CENTER_X = -UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0
SKY2_CENTER_Y = UNIT_WIDTH / 2.0 - LOFT_WIDTH / 2.0

SKYLIGHT_GLASS_THICK = 0.08

# Upstand (skylight wall) heights above main roof
UPSTAND_LOFT_HEIGHT    = 1.2
UPSTAND_CENTRAL_HEIGHT = 0.8


# ------------------------------------------------------------------
# HELPERS

def make_box(name, size_x, size_y, size_z, center,
             axis=(0.0, 0.0, 1.0), angle_deg=0.0):
    """Wrapper around craftbot.place_element()."""
    sx = size_x / 2.0
    sy = size_y / 2.0
    sz = size_z / 2.0
    craftbot.place_element(
        name=name,
        loc=center,
        axis=axis,
        angle=angle_deg,
        scale=(sx, sy, sz),
    )


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)


def level_floor_deck_top():
    """Z-level of the finished floor deck top surface."""
    return POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK


def level_roof_top():
    """Z-level of the outer roof skin (top of main flat roof, without skylights)."""
    return level_floor_deck_top() + WALL_HEIGHT + JOIST_DEPTH + ROOF_THICK


# ------------------------------------------------------------------
# SUPPORT POSTS

def build_posts():
    dx = UNIT_LENGTH / 2.0 - POST_SIZE / 2.0
    dy = UNIT_WIDTH  / 2.0 - POST_SIZE / 2.0
    zc = POST_HEIGHT / 2.0

    coords = [
        (+dx, +dy, zc),
        (+dx, -dy, zc),
        (-dx, +dy, zc),
        (-dx, -dy, zc),
    ]
    for i, (x, y, z) in enumerate(coords):
        make_box(f"Post_{i+1}", POST_SIZE, POST_SIZE, POST_HEIGHT, (x, y, z))


# ------------------------------------------------------------------
# FLOOR FRAMING (bearers + joists + solid deck)

def build_floor_framing():
    # Bearers along X
    z_bearer_center = POST_HEIGHT + JOIST_DEPTH / 2.0
    bearer_len = UNIT_LENGTH
    y_offset = UNIT_WIDTH / 2.0 - JOIST_THICK / 2.0

    for side, y in (("PosY", +y_offset), ("NegY", -y_offset)):
        make_box(
            f"Floor_Bearer_{side}",
            bearer_len,
            JOIST_THICK,
            JOIST_DEPTH,
            (0.0, y, z_bearer_center),
        )

    # Floor joists across Y
    x_min = -UNIT_LENGTH / 2.0 + JOIST_DEPTH / 2.0
    x_max = +UNIT_LENGTH / 2.0 - JOIST_DEPTH / 2.0
    num_joists = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num_joists):
        x = x_min + i * STUD_SPACING
        make_box(
            f"Floor_Joist_{i+1}",
            JOIST_THICK,
            UNIT_WIDTH - 2 * JOIST_THICK,
            JOIST_DEPTH,
            (x, 0.0, z_bearer_center),
        )

    # Solid floor deck
    z_deck_center = POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK / 2.0
    make_box(
        "Floor_Deck",
        UNIT_LENGTH,
        UNIT_WIDTH,
        FLOOR_THICK,
        (0.0, 0.0, z_deck_center),
    )


# ------------------------------------------------------------------
# BALLOON-FRAME WALLS WITH LARGE WINDOW OPENINGS

def build_wall_framing():
    z_floor_top = level_floor_deck_top()

    stud_len = WALL_HEIGHT
    stud_center_z = z_floor_top + stud_len / 2.0

    plate_height = PLATE_WIDTH  # plate “on edge”
    plate_width  = PLATE_THICK

    z_bottom_plate = z_floor_top + plate_height / 2.0
    z_top_plate    = z_floor_top + stud_len - plate_height / 2.0

    # Long walls: continuous bottom plate + double top plate
    y_inner = UNIT_WIDTH / 2.0 - plate_width / 2.0
    for side, y in (("PosY", +y_inner), ("NegY", -y_inner)):
        make_box(
            f"Bottom_Plate_Long_{side}",
            UNIT_LENGTH,
            plate_width,
            plate_height,
            (0.0, y, z_bottom_plate),
        )
        make_box(
            f"Top_Plate_Long_{side}",
            UNIT_LENGTH,
            plate_width,
            plate_height,
            (0.0, y, z_top_plate),
        )
        make_box(
            f"Top_Plate2_Long_{side}",
            UNIT_LENGTH,
            plate_width,
            plate_height,
            (0.0, y, z_top_plate + plate_height),
        )

    # Short walls: similar plates
    x_inner = UNIT_LENGTH / 2.0 - plate_width / 2.0
    for side, x in (("PosX", +x_inner), ("NegX", -x_inner)):
        make_box(
            f"Bottom_Plate_Short_{side}",
            plate_width,
            UNIT_WIDTH,
            plate_height,
            (x, 0.0, z_bottom_plate),
        )
        make_box(
            f"Top_Plate_Short_{side}",
            plate_width,
            UNIT_WIDTH,
            plate_height,
            (x, 0.0, z_top_plate),
        )
        make_box(
            f"Top_Plate2_Short_{side}",
            plate_width,
            UNIT_WIDTH,
            plate_height,
            (x, 0.0, z_top_plate + plate_height),
        )

    # Window opening extents along X (big side glazing)
    opening_x_min = -UNIT_LENGTH / 2.0 + WINDOW_OPENING_MARGIN
    opening_x_max = +UNIT_LENGTH / 2.0 - WINDOW_OPENING_MARGIN

    # Long wall studs (skip window opening)
    x_min = -UNIT_LENGTH / 2.0 + STUD_SPACING
    x_max = +UNIT_LENGTH / 2.0 - STUD_SPACING
    num_long = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num_long):
        x = x_min + i * STUD_SPACING
        if opening_x_min < x < opening_x_max:
            continue

        for side, y_sign in (("PosY", +1), ("NegY", -1)):
            y = y_sign * (UNIT_WIDTH / 2.0 - plate_width - STUD_THICK / 2.0)
            make_box(
                f"Stud_Long_{side}_{i+1}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, stud_center_z),
            )

    # Jamb studs at window edges
    for side, y_sign in (("PosY", +1), ("NegY", -1)):
        y = y_sign * (UNIT_WIDTH / 2.0 - plate_width - STUD_THICK / 2.0)
        for label, x in (("Left", opening_x_min), ("Right", opening_x_max)):
            make_box(
                f"Stud_Long_{side}_Jamb_{label}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, stud_center_z),
            )

    # Headers (lintels) above the window opening
    header_len = opening_x_max - opening_x_min
    z_head_bottom = z_floor_top + WINDOW_HEAD_HEIGHT
    z_head_center = z_head_bottom + JOIST_DEPTH / 2.0

    for side, y_sign in (("PosY", +1), ("NegY", -1)):
        y = y_sign * (UNIT_WIDTH / 2.0 - plate_width - STUD_THICK / 2.0)
        make_box(
            f"Header_Long_{side}",
            header_len,
            STUD_THICK,
            JOIST_DEPTH,
            ((opening_x_min + opening_x_max) / 2.0, y, z_head_center),
        )

    # Short wall studs (no openings modeled here)
    y_min = -UNIT_WIDTH / 2.0 + STUD_SPACING
    y_max = +UNIT_WIDTH / 2.0 - STUD_SPACING
    num_short = int((y_max - y_min) / STUD_SPACING) + 1

    for i in range(num_short):
        y = y_min + i * STUD_SPACING
        for side, x_sign in (("PosX", +1), ("NegX", -1)):
            x = x_sign * (UNIT_LENGTH / 2.0 - plate_width - STUD_THICK / 2.0)
            make_box(
                f"Stud_Short_{side}_{i+1}",
                STUD_THICK,
                STUD_WIDTH,
                stud_len,
                (x, y, stud_center_z),
            )


# ------------------------------------------------------------------
# LOFT FRAMING (joists + deck in upper sleeping zone)

def build_loft_framing():
    z_floor_top = level_floor_deck_top()
    z_loft_bottom = z_floor_top + LOFT_CLEAR
    z_joist_center = z_loft_bottom + JOIST_DEPTH / 2.0

    x_start = -UNIT_LENGTH / 2.0
    num_joists = int(LOFT_LENGTH / STUD_SPACING) + 1

    for i in range(num_joists):
        x = x_start + i * STUD_SPACING
        make_box(
            f"Loft_Joist_{i+1}",
            JOIST_THICK,
            LOFT_WIDTH,
            JOIST_DEPTH,
            (x, UNIT_WIDTH / 2.0 - LOFT_WIDTH / 2.0, z_joist_center),
        )

    z_deck_center = z_loft_bottom + JOIST_DEPTH + LOFT_DECK_THICK / 2.0
    make_box(
        "Loft_Deck",
        LOFT_LENGTH,
        LOFT_WIDTH,
        LOFT_DECK_THICK,
        (
            -UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0,
            UNIT_WIDTH / 2.0 - LOFT_WIDTH / 2.0,
            z_deck_center,
        ),
    )


# ------------------------------------------------------------------
# HELPER: BUILD A FRAMED SKYLIGHT UPSTAND AROUND A ROOF OPENING

def build_skylight_upstand(prefix, center_x, center_y,
                           length_x, length_y, wall_height):
    """
    Build a balloon-framed upstand (short wall) around a roof opening.
    - prefix: object name prefix
    - center_x, center_y: footprint center in plan
    - length_x, length_y: footprint dimensions
    - wall_height: height from roof top to top of upstand (plates included)
    """
    z_roof_top = level_roof_top()
    plate_height = PLATE_WIDTH
    plate_width  = PLATE_THICK

    # Bottom and top plate vertical positions
    z_bottom_plate = z_roof_top + plate_height / 2.0
    z_top_plate    = z_roof_top + wall_height - plate_height / 2.0

    # Stud length (between plates)
    stud_len = wall_height - 2.0 * plate_height
    z_stud_center = z_roof_top + plate_height + stud_len / 2.0

    # LONG SIDES (parallel to X)
    y_long_pos = center_y + (length_y / 2.0 - plate_width / 2.0)
    y_long_neg = center_y - (length_y / 2.0 - plate_width / 2.0)

    for side, y in (("PosY", y_long_pos), ("NegY", y_long_neg)):
        # Bottom plate
        make_box(
            f"{prefix}_BottomPlate_Long_{side}",
            length_x,
            plate_width,
            plate_height,
            (center_x, y, z_bottom_plate),
        )
        # Top plate
        make_box(
            f"{prefix}_TopPlate_Long_{side}",
            length_x,
            plate_width,
            plate_height,
            (center_x, y, z_top_plate),
        )

        # Studs along length
        x_min = center_x - length_x / 2.0 + STUD_SPACING
        x_max = center_x + length_x / 2.0 - STUD_SPACING
        num = max(1, int((x_max - x_min) / STUD_SPACING) + 1)
        for i in range(num):
            x = x_min + i * STUD_SPACING
            make_box(
                f"{prefix}_Stud_Long_{side}_{i+1}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, z_stud_center),
            )

    # SHORT SIDES (parallel to Y)
    x_short_pos = center_x + (length_x / 2.0 - plate_width / 2.0)
    x_short_neg = center_x - (length_x / 2.0 - plate_width / 2.0)

    for side, x in (("PosX", x_short_pos), ("NegX", x_short_neg)):
        make_box(
            f"{prefix}_BottomPlate_Short_{side}",
            plate_width,
            length_y,
            plate_height,
            (x, center_y, z_bottom_plate),
        )
        make_box(
            f"{prefix}_TopPlate_Short_{side}",
            plate_width,
            length_y,
            plate_height,
            (x, center_y, z_top_plate),
        )

        # Studs along width
        y_min = center_y - length_y / 2.0 + STUD_SPACING
        y_max = center_y + length_y / 2.0 - STUD_SPACING
        num = max(1, int((y_max - y_min) / STUD_SPACING) + 1)
        for i in range(num):
            y = y_min + i * STUD_SPACING
            make_box(
                f"{prefix}_Stud_Short_{side}_{i+1}",
                STUD_THICK,
                STUD_WIDTH,
                stud_len,
                (x, y, z_stud_center),
            )

    # Glass slab on top of upstand
    z_glass_center = z_roof_top + wall_height + SKYLIGHT_GLASS_THICK / 2.0
    make_box(
        f"{prefix}_Glass",
        length_x - 0.1,
        length_y - 0.1,
        SKYLIGHT_GLASS_THICK,
        (center_x, center_y, z_glass_center),
    )


# ------------------------------------------------------------------
# ROOF FRAMING + SKYLIGHT OPENINGS + UPSTANDS

def build_roof_framing():
    z_floor_top = level_floor_deck_top()
    z_roof_joist_bottom = z_floor_top + WALL_HEIGHT
    z_joist_center = z_roof_joist_bottom + JOIST_DEPTH / 2.0

    # Helper: does an X coordinate lie under either skylight opening?
    def in_skylight_region(x):
        half1 = SKY1_LENGTH / 2.0
        half2 = SKY2_LENGTH / 2.0
        in1 = (SKY1_CENTER_X - half1) <= x <= (SKY1_CENTER_X + half1)
        in2 = (SKY2_CENTER_X - half2) <= x <= (SKY2_CENTER_X + half2)
        return in1 or in2

    # Roof joists across Y, trimmed around skylights
    x_min = -UNIT_LENGTH / 2.0 + STUD_SPACING
    x_max = +UNIT_LENGTH / 2.0 - STUD_SPACING
    num_joists = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num_joists):
        x = x_min + i * STUD_SPACING
        if in_skylight_region(x):
            continue
        make_box(
            f"Roof_Joist_{i+1}",
            JOIST_THICK,
            UNIT_WIDTH - 2 * PLATE_THICK,
            JOIST_DEPTH,
            (x, 0.0, z_joist_center),
        )

    # Solid roof deck
    z_deck_center = z_roof_joist_bottom + JOIST_DEPTH + ROOF_THICK / 2.0
    make_box(
        "Roof_Deck",
        UNIT_LENGTH,
        UNIT_WIDTH,
        ROOF_THICK,
        (0.0, 0.0, z_deck_center),
    )

    # Build framed skylight upstands (balloon-frame mini-walls)
    build_skylight_upstand(
        prefix="Skylight_Central",
        center_x=SKY1_CENTER_X,
        center_y=SKY1_CENTER_Y,
        length_x=SKY1_LENGTH,
        length_y=SKY1_WIDTH,
        wall_height=UPSTAND_CENTRAL_HEIGHT,
    )

    build_skylight_upstand(
        prefix="Skylight_Loft",
        center_x=SKY2_CENTER_X,
        center_y=SKY2_CENTER_Y,
        length_x=SKY2_LENGTH,
        length_y=SKY2_WIDTH,
        wall_height=UPSTAND_LOFT_HEIGHT,
    )


# ------------------------------------------------------------------
# SIMPLE EXTERIOR SHELL (with long-side window opening)

def build_exterior_shell():
    z_floor_center = level_floor_deck_top() - FLOOR_THICK / 2.0
    make_box(
        "Shell_Floor",
        UNIT_LENGTH,
        UNIT_WIDTH,
        FLOOR_THICK,
        (0.0, 0.0, z_floor_center),
    )

    shell_thick  = 0.05
    shell_height = WALL_HEIGHT
    z_wall_center = level_floor_deck_top() + shell_height / 2.0

    x_outer = UNIT_LENGTH / 2.0 - shell_thick / 2.0

    # Short end walls
    make_box(
        "Shell_Wall_Short_PosX",
        shell_thick,
        UNIT_WIDTH,
        shell_height,
        (x_outer, 0.0, z_wall_center),
    )
    make_box(
        "Shell_Wall_Short_NegX",
        shell_thick,
        UNIT_WIDTH,
        shell_height,
        (-x_outer, 0.0, z_wall_center),
    )

    # Long walls with big opening
    opening_x_min = -UNIT_LENGTH / 2.0 + WINDOW_OPENING_MARGIN
    opening_x_max = +UNIT_LENGTH / 2.0 - WINDOW_OPENING_MARGIN

    left_len  = opening_x_min - (-UNIT_LENGTH / 2.0)
    right_len = (UNIT_LENGTH / 2.0) - opening_x_max
    y_outer   = UNIT_WIDTH / 2.0 - shell_thick / 2.0

    # Positive Y side (front glazing)
    if left_len > 0:
        make_box(
            "Shell_Long_PosY_Left",
            left_len,
            shell_thick,
            shell_height,
            (-UNIT_LENGTH / 2.0 + left_len / 2.0, +y_outer, z_wall_center),
        )
    if right_len > 0:
        make_box(
            "Shell_Long_PosY_Right",
            right_len,
            shell_thick,
            shell_height,
            (UNIT_LENGTH / 2.0 - right_len / 2.0, +y_outer, z_wall_center),
        )

    # Negative Y side (back)
    if left_len > 0:
        make_box(
            "Shell_Long_NegY_Left",
            left_len,
            shell_thick,
            shell_height,
            (-UNIT_LENGTH / 2.0 + left_len / 2.0, -y_outer, z_wall_center),
        )
    if right_len > 0:
        make_box(
            "Shell_Long_NegY_Right",
            right_len,
            shell_thick,
            shell_height,
            (UNIT_LENGTH / 2.0 - right_len / 2.0, -y_outer, z_wall_center),
        )


# ------------------------------------------------------------------
# BUILD EVERYTHING

def build_shelter():
    clear_scene()
    build_posts()
    build_floor_framing()
    build_wall_framing()
    build_loft_framing()
    build_roof_framing()
    build_exterior_shell()


# Uncomment this line if you want the model to generate
# immediately when you run the script inside Blender:
build_shelter()
