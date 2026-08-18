# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 03 - CHATGPT 5.1 - V06
# DESCRIPTION: VIPP SHELTER
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # must be on Blender's sys.path

importlib.reload(craftbot)


# ------------------------------------------------------------------
# GLOBAL PARAMETERS  (meters)

# Overall base geometry
UNIT_LENGTH = 11.5   # X, main shelter body
UNIT_WIDTH  = 5.2    # Y

WALL_HEIGHT = 3.0    # clear wall height from finished floor

# Support posts
POST_HEIGHT = 0.8
POST_SIZE   = 0.25   # square posts

# Floor / roof build-up
FLOOR_THICK = 0.30   # solid floor cassette (deck + build-up)
ROOF_THICK  = 0.25   # solid roof build-up

# Timber sections
STUD_THICK  = 0.045  # across wall thickness
STUD_WIDTH  = 0.095  # in wall plane

PLATE_THICK = STUD_THICK
PLATE_WIDTH = STUD_WIDTH

JOIST_THICK = 0.045
JOIST_DEPTH = 0.195

STUD_SPACING = 0.6   # typical spacing

# Upper module (2.5 m strip sitting on roof)
TOP_STRIP_WIDTH  = 2.5
TOP_STRIP_LENGTH = 10.0       # two 5 m parts along X

# Loft zone (upper floor)
LOFT_LENGTH      = 5.0        # first 5 m of the top strip
LOFT_WIDTH       = TOP_STRIP_WIDTH
LOFT_CLEAR       = 2.2
LOFT_DECK_THICK  = 0.025

# Large window opening in long walls
WINDOW_OPENING_MARGIN = 1.5   # from each short end
WINDOW_HEAD_HEIGHT    = 2.2   # above finished floor

# Skylight footprints (derived from upper floor plan proportions)
# - Loft skylight (over bed) inside 5 x 2.5 m area
SKY_LOFT_LENGTH = 2.88        # ≈ 0.58 * 5 m
SKY_LOFT_WIDTH  = 1.72        # ≈ 0.69 * 2.5 m

# - Main skylight (over living) inside 5 x 2.5 m area
SKY_MAIN_LENGTH = 4.15        # ≈ 0.83 * 5 m
SKY_MAIN_WIDTH  = 1.85        # ≈ 0.74 * 2.5 m

# Position of 10 m top strip along UNIT_LENGTH (anchored at negative end)
TOP_STRIP_X_MIN = -UNIT_LENGTH / 2.0
TOP_STRIP_X_MAX = TOP_STRIP_X_MIN + TOP_STRIP_LENGTH

# Centers of each 5 m half of top strip (for skylights)
SKY_LOFT_CENTER_X = TOP_STRIP_X_MIN + LOFT_LENGTH / 2.0        # first 5 m
SKY_MAIN_CENTER_X = TOP_STRIP_X_MIN + LOFT_LENGTH + 2.5        # second 5 m
# Skylights centered in 2.5 m strip across Y:
SKY_CENTER_Y = 0.0

# Upstand (skylight wall) heights above main roof
UPSTAND_LOFT_HEIGHT    = 1.2
UPSTAND_MAIN_HEIGHT    = 0.8

# Glass thickness
SKYLIGHT_GLASS_THICK = 0.08

# Interior partitions / modules
INT_WALL_THICK   = 0.10       # interior stud+cladding depth simplified
BATHROOM_LEN     = 3.0        # length from entrance end inward
STORAGE_LEN      = 1.7        # storage/kitchen block length
GAP_BATH_STORAGE = 0.7        # gap between bathroom and storage block


# ------------------------------------------------------------------
# HELPERS

def make_box(name, size_x, size_y, size_z, center,
             axis=(0.0, 0.0, 1.0), angle_deg=0.0):
    """Wrapper around craftbot.place_element()."""
    sx, sy, sz = size_x / 2.0, size_y / 2.0, size_z / 2.0
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
    return POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK


def level_roof_top():
    return level_floor_deck_top() + WALL_HEIGHT + JOIST_DEPTH + ROOF_THICK


# ------------------------------------------------------------------
# SUPPORT POSTS

def build_posts():
    dx = UNIT_LENGTH / 2.0 - POST_SIZE / 2.0
    dy = UNIT_WIDTH  / 2.0 - POST_SIZE / 2.0
    zc = POST_HEIGHT / 2.0

    for i, (x, y) in enumerate([
        (+dx, +dy),
        (+dx, -dy),
        (-dx, +dy),
        (-dx, -dy),
    ]):
        make_box(f"Post_{i+1}", POST_SIZE, POST_SIZE, POST_HEIGHT, (x, y, zc))


# ------------------------------------------------------------------
# FLOOR FRAMING

def build_floor_framing():
    # Bearers along X
    z_bearer_center = POST_HEIGHT + JOIST_DEPTH / 2.0
    bearer_len = UNIT_LENGTH
    y_off = UNIT_WIDTH / 2.0 - JOIST_THICK / 2.0

    for side, y in (("PosY", +y_off), ("NegY", -y_off)):
        make_box(
            f"Floor_Bearer_{side}",
            bearer_len,
            JOIST_THICK,
            JOIST_DEPTH,
            (0.0, y, z_bearer_center),
        )

    # Joists across Y
    x_min = -UNIT_LENGTH / 2.0 + JOIST_DEPTH / 2.0
    x_max = +UNIT_LENGTH / 2.0 - JOIST_DEPTH / 2.0
    num = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num):
        x = x_min + i * STUD_SPACING
        make_box(
            f"Floor_Joist_{i+1}",
            JOIST_THICK,
            UNIT_WIDTH - 2 * JOIST_THICK,
            JOIST_DEPTH,
            (x, 0.0, z_bearer_center),
        )

    # Solid deck
    z_deck = POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK / 2.0
    make_box("Floor_Deck", UNIT_LENGTH, UNIT_WIDTH, FLOOR_THICK, (0.0, 0.0, z_deck))


# ------------------------------------------------------------------
# WALL FRAMING WITH LARGE WINDOW

def build_wall_framing():
    z_floor = level_floor_deck_top()
    stud_len = WALL_HEIGHT
    stud_center_z = z_floor + stud_len / 2.0

    plate_h = PLATE_WIDTH
    plate_w = PLATE_THICK
    z_bottom_plate = z_floor + plate_h / 2.0
    z_top_plate    = z_floor + stud_len - plate_h / 2.0

    # Long walls: bottom + double top plates
    y_inner = UNIT_WIDTH / 2.0 - plate_w / 2.0
    for side, y in (("PosY", +y_inner), ("NegY", -y_inner)):
        make_box(f"Bottom_Plate_Long_{side}",
                 UNIT_LENGTH, plate_w, plate_h, (0.0, y, z_bottom_plate))
        make_box(f"Top_Plate_Long_{side}",
                 UNIT_LENGTH, plate_w, plate_h, (0.0, y, z_top_plate))
        make_box(f"Top_Plate2_Long_{side}",
                 UNIT_LENGTH, plate_w, plate_h, (0.0, y, z_top_plate + plate_h))

    # Short walls: plates
    x_inner = UNIT_LENGTH / 2.0 - plate_w / 2.0
    for side, x in (("PosX", +x_inner), ("NegX", -x_inner)):
        make_box(f"Bottom_Plate_Short_{side}",
                 plate_w, UNIT_WIDTH, plate_h, (x, 0.0, z_bottom_plate))
        make_box(f"Top_Plate_Short_{side}",
                 plate_w, UNIT_WIDTH, plate_h, (x, 0.0, z_top_plate))
        make_box(f"Top_Plate2_Short_{side}",
                 plate_w, UNIT_WIDTH, plate_h, (x, 0.0, z_top_plate + plate_h))

    # Window opening extents
    open_x_min = -UNIT_LENGTH / 2.0 + WINDOW_OPENING_MARGIN
    open_x_max = +UNIT_LENGTH / 2.0 - WINDOW_OPENING_MARGIN

    # Long wall studs (skip opening)
    x_min = -UNIT_LENGTH / 2.0 + STUD_SPACING
    x_max = +UNIT_LENGTH / 2.0 - STUD_SPACING
    num_long = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num_long):
        x = x_min + i * STUD_SPACING
        if open_x_min < x < open_x_max:
            continue
        for side, y_sign in (("PosY", +1), ("NegY", -1)):
            y = y_sign * (UNIT_WIDTH / 2.0 - plate_w - STUD_THICK / 2.0)
            make_box(
                f"Stud_Long_{side}_{i+1}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, stud_center_z),
            )

    # Jamb studs
    for side, y_sign in (("PosY", +1), ("NegY", -1)):
        y = y_sign * (UNIT_WIDTH / 2.0 - plate_w - STUD_THICK / 2.0)
        for label, x in (("Left", open_x_min), ("Right", open_x_max)):
            make_box(
                f"Stud_Long_{side}_Jamb_{label}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, stud_center_z),
            )

    # Window headers
    header_len = open_x_max - open_x_min
    z_head_bottom = z_floor + WINDOW_HEAD_HEIGHT
    z_head_center = z_head_bottom + JOIST_DEPTH / 2.0

    for side, y_sign in (("PosY", +1), ("NegY", -1)):
        y = y_sign * (UNIT_WIDTH / 2.0 - plate_w - STUD_THICK / 2.0)
        make_box(
            f"Header_Long_{side}",
            header_len,
            STUD_THICK,
            JOIST_DEPTH,
            ((open_x_min + open_x_max) / 2.0, y, z_head_center),
        )

    # Short wall studs (simple, no openings)
    y_min = -UNIT_WIDTH / 2.0 + STUD_SPACING
    y_max = +UNIT_WIDTH / 2.0 - STUD_SPACING
    num_short = int((y_max - y_min) / STUD_SPACING) + 1

    for i in range(num_short):
        y = y_min + i * STUD_SPACING
        for side, x_sign in (("PosX", +1), ("NegX", -1)):
            x = x_sign * (UNIT_LENGTH / 2.0 - plate_w - STUD_THICK / 2.0)
            make_box(
                f"Stud_Short_{side}_{i+1}",
                STUD_THICK,
                STUD_WIDTH,
                stud_len,
                (x, y, stud_center_z),
            )


# ------------------------------------------------------------------
# LOFT FRAMING (centered 2.5 m strip)

def build_loft_framing():
    z_floor = level_floor_deck_top()
    z_loft_bottom = z_floor + LOFT_CLEAR
    z_joist_center = z_loft_bottom + JOIST_DEPTH / 2.0

    x_start = TOP_STRIP_X_MIN
    num = int(LOFT_LENGTH / STUD_SPACING) + 1

    for i in range(num):
        x = x_start + i * STUD_SPACING
        make_box(
            f"Loft_Joist_{i+1}",
            JOIST_THICK,
            LOFT_WIDTH,
            JOIST_DEPTH,
            (x, SKY_CENTER_Y, z_joist_center),
        )

    z_deck_center = z_loft_bottom + JOIST_DEPTH + LOFT_DECK_THICK / 2.0
    make_box(
        "Loft_Deck",
        LOFT_LENGTH,
        LOFT_WIDTH,
        LOFT_DECK_THICK,
        (TOP_STRIP_X_MIN + LOFT_LENGTH / 2.0, SKY_CENTER_Y, z_deck_center),
    )


# ------------------------------------------------------------------
# SKYLIGHT UPSTAND HELPER

def build_skylight_upstand(prefix, center_x, center_y,
                           length_x, length_y, wall_height):
    """
    Balloon-framed upstand (short stud wall) around roof opening.
    """
    z_roof_top = level_roof_top()
    plate_h = PLATE_WIDTH
    plate_w = PLATE_THICK

    z_bottom_plate = z_roof_top + plate_h / 2.0
    z_top_plate    = z_roof_top + wall_height - plate_h / 2.0

    stud_len = wall_height - 2.0 * plate_h
    z_stud_center = z_roof_top + plate_h + stud_len / 2.0

    # Long sides (parallel to X)
    y_pos = center_y + (length_y / 2.0 - plate_w / 2.0)
    y_neg = center_y - (length_y / 2.0 - plate_w / 2.0)

    for side, y in (("PosY", y_pos), ("NegY", y_neg)):
        # Bottom & top plates
        make_box(f"{prefix}_BottomPlate_Long_{side}",
                 length_x, plate_w, plate_h,
                 (center_x, y, z_bottom_plate))
        make_box(f"{prefix}_TopPlate_Long_{side}",
                 length_x, plate_w, plate_h,
                 (center_x, y, z_top_plate))

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

    # Short sides (parallel to Y)
    x_pos = center_x + (length_x / 2.0 - plate_w / 2.0)
    x_neg = center_x - (length_x / 2.0 - plate_w / 2.0)

    for side, x in (("PosX", x_pos), ("NegX", x_neg)):
        make_box(f"{prefix}_BottomPlate_Short_{side}",
                 plate_w, length_y, plate_h,
                 (x, center_y, z_bottom_plate))
        make_box(f"{prefix}_TopPlate_Short_{side}",
                 plate_w, length_y, plate_h,
                 (x, center_y, z_top_plate))

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

    # Glass slab on top
    z_glass = z_roof_top + wall_height + SKYLIGHT_GLASS_THICK / 2.0
    make_box(
        f"{prefix}_Glass",
        length_x - 0.1,
        length_y - 0.1,
        SKYLIGHT_GLASS_THICK,
        (center_x, center_y, z_glass),
    )


# ------------------------------------------------------------------
# ROOF FRAMING + SKYLIGHTS

def build_roof_framing():
    z_floor = level_floor_deck_top()
    z_roof_joist_bottom = z_floor + WALL_HEIGHT
    z_joist_center = z_roof_joist_bottom + JOIST_DEPTH / 2.0

    # For trimming joists in skylight zones
    def in_skylight_region(x):
        half_main = SKY_MAIN_LENGTH / 2.0
        half_loft = SKY_LOFT_LENGTH / 2.0
        in_main = (SKY_MAIN_CENTER_X - half_main) <= x <= (SKY_MAIN_CENTER_X + half_main)
        in_loft = (SKY_LOFT_CENTER_X - half_loft) <= x <= (SKY_LOFT_CENTER_X + half_loft)
        return in_main or in_loft

    x_min = -UNIT_LENGTH / 2.0 + STUD_SPACING
    x_max = +UNIT_LENGTH / 2.0 - STUD_SPACING
    num = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num):
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
    z_deck = z_roof_joist_bottom + JOIST_DEPTH + ROOF_THICK / 2.0
    make_box("Roof_Deck", UNIT_LENGTH, UNIT_WIDTH, ROOF_THICK, (0.0, 0.0, z_deck))

    # Framed skylight upstands
    build_skylight_upstand(
        prefix="Skylight_Loft",
        center_x=SKY_LOFT_CENTER_X,
        center_y=SKY_CENTER_Y,
        length_x=SKY_LOFT_LENGTH,
        length_y=SKY_LOFT_WIDTH,
        wall_height=UPSTAND_LOFT_HEIGHT,
    )

    build_skylight_upstand(
        prefix="Skylight_Main",
        center_x=SKY_MAIN_CENTER_X,
        center_y=SKY_CENTER_Y,
        length_x=SKY_MAIN_LENGTH,
        length_y=SKY_MAIN_WIDTH,
        wall_height=UPSTAND_MAIN_HEIGHT,
    )


# ------------------------------------------------------------------
# INTERIOR WALLS: BATHROOM + STORAGE/KITCHEN BLOCK

def build_interior_walls():
    """
    Adds:
    - Bathroom longitudinal wall (centerline) and cross wall.
    - Storage/kitchen wall volume.
    """
    z_floor = level_floor_deck_top()
    height  = WALL_HEIGHT
    z_center = z_floor + height / 2.0

    # ----- Bathroom partitions -----
    # Longitudinal wall along centerline, from entrance end inward
    bath_x_start = -UNIT_LENGTH / 2.0
    bath_x_end   = bath_x_start + BATHROOM_LEN
    bath_center_x = (bath_x_start + bath_x_end) / 2.0

    make_box(
        "Int_Bath_Wall_Long",
        BATHROOM_LEN,
        INT_WALL_THICK,
        height,
        (bath_center_x, 0.0, z_center),
    )

    # Cross wall closing bathroom at its inner edge (Y>0 half)
    make_box(
        "Int_Bath_Wall_Cross",
        INT_WALL_THICK,
        UNIT_WIDTH / 2.0,
        height,
        (bath_x_end, UNIT_WIDTH / 4.0, z_center),
    )

    # ----- Storage + kitchen volume -----
    # Block on the "top" side (Y > 0) after a short gap
    storage_x_start = bath_x_end + GAP_BATH_STORAGE
    storage_x_end   = storage_x_start + STORAGE_LEN
    storage_center_x = (storage_x_start + storage_x_end) / 2.0

    make_box(
        "Int_Storage_Volume",
        STORAGE_LEN,
        UNIT_WIDTH / 2.0,
        height,
        (storage_center_x, UNIT_WIDTH / 4.0, z_center),
    )


# ------------------------------------------------------------------
# SIMPLE EXTERIOR SHELL

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
    make_box("Shell_Wall_Short_PosX",
             shell_thick, UNIT_WIDTH, shell_height,
             (x_outer, 0.0, z_wall_center))
    make_box("Shell_Wall_Short_NegX",
             shell_thick, UNIT_WIDTH, shell_height,
             (-x_outer, 0.0, z_wall_center))

    # Long walls with opening
    open_x_min = -UNIT_LENGTH / 2.0 + WINDOW_OPENING_MARGIN
    open_x_max = +UNIT_LENGTH / 2.0 - WINDOW_OPENING_MARGIN

    left_len  = open_x_min - (-UNIT_LENGTH / 2.0)
    right_len = (UNIT_LENGTH / 2.0) - open_x_max
    y_outer   = UNIT_WIDTH / 2.0 - shell_thick / 2.0

    # Positive Y
    if left_len > 0:
        make_box("Shell_Long_PosY_Left",
                 left_len, shell_thick, shell_height,
                 (-UNIT_LENGTH / 2.0 + left_len / 2.0, +y_outer, z_wall_center))
    if right_len > 0:
        make_box("Shell_Long_PosY_Right",
                 right_len, shell_thick, shell_height,
                 (UNIT_LENGTH / 2.0 - right_len / 2.0, +y_outer, z_wall_center))

    # Negative Y
    if left_len > 0:
        make_box("Shell_Long_NegY_Left",
                 left_len, shell_thick, shell_height,
                 (-UNIT_LENGTH / 2.0 + left_len / 2.0, -y_outer, z_wall_center))
    if right_len > 0:
        make_box("Shell_Long_NegY_Right",
                 right_len, shell_thick, shell_height,
                 (UNIT_LENGTH / 2.0 - right_len / 2.0, -y_outer, z_wall_center))


# ------------------------------------------------------------------
# BUILD EVERYTHING

def build_shelter():
    clear_scene()
    build_posts()
    build_floor_framing()
    build_wall_framing()
    build_loft_framing()
    build_roof_framing()
    build_interior_walls()
    build_exterior_shell()


# Uncomment to generate immediately in Blender:
build_shelter()
