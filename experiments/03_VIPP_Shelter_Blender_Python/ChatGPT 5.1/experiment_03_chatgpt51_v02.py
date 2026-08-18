# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 03 - CHATGPT 5.1 - V02
# DESCRIPTION: VIPP SHELTER
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot  # make sure this is on sys.path

importlib.reload(craftbot)

# ------------------------------------------------------------------
# GLOBAL PARAMETERS  (all dimensions in meters)

# Overall geometry
UNIT_LENGTH = 11.5   # X
UNIT_WIDTH  = 5.2    # Y
WALL_HEIGHT = 3.0    # clear wall height (stud height approx.)

POST_HEIGHT = 0.8
POST_SIZE   = 0.25   # square posts

FLOOR_THICK = 0.30   # overall floor cassette depth (for solid deck)
ROOF_THICK  = 0.25   # roof build-up (solid deck)

# Timber sizes (approximate)
STUD_THICK  = 0.045  # in wall thickness direction
STUD_WIDTH  = 0.095  # in plane of wall

PLATE_THICK = STUD_THICK
PLATE_WIDTH = STUD_WIDTH

JOIST_THICK = 0.045
JOIST_DEPTH = 0.195

# Layout
STUD_SPACING = 0.6    # c/c spacing for studs and joists

# Loft
LOFT_LENGTH = 5.0
LOFT_WIDTH  = 2.5
LOFT_CLEAR  = 2.2      # clear height below loft
LOFT_DECK_THICK = 0.025

# Skylights (plan extents along X)
SKY1_LENGTH = 4.0  # central strip
SKY1_CENTER_X = 0.0

SKY2_LENGTH = 3.5  # over loft
SKY2_CENTER_X = -UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0

SKY_STRIP_WIDTH = 1.2
SKYLIGHT_THICK  = 0.10


# ------------------------------------------------------------------
# HELPERS

def make_box(name, size_x, size_y, size_z, center,
             axis=(0.0, 0.0, 1.0), angle_deg=0.0):
    """
    Wrapper around craftbot.place_element().
    size_* are full dimensions along world axes before rotation.
    center is (x, y, z) world coordinate of box center.
    """
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


clear_scene()


# ------------------------------------------------------------------
# SUPPORT POSTS

def build_posts():
    dx = UNIT_LENGTH / 2.0 - POST_SIZE / 2.0
    dy = UNIT_WIDTH / 2.0 - POST_SIZE / 2.0
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
# FLOOR FRAMING  (bearers + joists + deck)

def build_floor_framing():
    # Bearers (rim beams) along X resting on posts
    z_bearer_center = POST_HEIGHT + JOIST_DEPTH / 2.0
    bearer_len = UNIT_LENGTH
    bearer_sec = (JOIST_DEPTH, JOIST_THICK)  # depth vertical (Z), thickness in Y

    y_offset = UNIT_WIDTH / 2.0 - JOIST_THICK / 2.0
    for side, y in (("PosY", +y_offset), ("NegY", -y_offset)):
        make_box(
            f"Floor_Bearer_{side}",
            bearer_len,
            bearer_sec[1],
            bearer_sec[0],
            (0.0, y, z_bearer_center),
        )

    # Floor joists running across Y between bearers
    x_min = -UNIT_LENGTH / 2.0 + JOIST_DEPTH / 2.0
    x_max = +UNIT_LENGTH / 2.0 - JOIST_DEPTH / 2.0

    num_joists = int((x_max - x_min) / STUD_SPACING) + 1
    for i in range(num_joists):
        x = x_min + i * STUD_SPACING
        make_box(
            f"Floor_Joist_{i+1}",
            JOIST_THICK,
            UNIT_WIDTH - 2.0 * JOIST_THICK,
            JOIST_DEPTH,
            (x, 0.0, z_bearer_center),
        )

    # Solid floor deck on top (plywood + finish as one slab)
    z_deck_center = POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK / 2.0
    make_box(
        "Floor_Deck",
        UNIT_LENGTH,
        UNIT_WIDTH,
        FLOOR_THICK,
        (0.0, 0.0, z_deck_center),
    )


# Convenience to know reference levels
def level_floor_deck_top():
    return POST_HEIGHT + JOIST_DEPTH + FLOOR_THICK


# ------------------------------------------------------------------
# WALL FRAMING (balloon frame around perimeter)

def build_wall_framing():
    z0 = level_floor_deck_top()
    stud_len = WALL_HEIGHT
    stud_center_z = z0 + stud_len / 2.0

    # Bottom & top plates
    plate_height = PLATE_WIDTH  # orient so plate width is vertical
    plate_width  = PLATE_THICK

    z_bottom_plate_center = z0 + plate_height / 2.0
    z_top_plate_center    = z0 + stud_len - plate_height / 2.0

    # Long walls - plates along X
    y_inner = UNIT_WIDTH / 2.0 - plate_width / 2.0

    for side, y in (("PosY", +y_inner), ("NegY", -y_inner)):
        # Bottom plate
        make_box(
            f"Bottom_Plate_Long_{side}",
            UNIT_LENGTH,
            plate_width,
            plate_height,
            (0.0, y, z_bottom_plate_center),
        )
        # Top plate
        make_box(
            f"Top_Plate_Long_{side}",
            UNIT_LENGTH,
            plate_width,
            plate_height,
            (0.0, y, z_top_plate_center),
        )

    # Short walls - plates along Y
    x_inner = UNIT_LENGTH / 2.0 - plate_width / 2.0
    for side, x in (("PosX", +x_inner), ("NegX", -x_inner)):
        make_box(
            f"Bottom_Plate_Short_{side}",
            plate_width,
            UNIT_WIDTH,
            plate_height,
            (x, 0.0, z_bottom_plate_center),
        )
        make_box(
            f"Top_Plate_Short_{side}",
            plate_width,
            UNIT_WIDTH,
            plate_height,
            (x, 0.0, z_top_plate_center),
        )

    # Studs along long walls
    x_min = -UNIT_LENGTH / 2.0 + STUD_SPACING
    x_max = +UNIT_LENGTH / 2.0 - STUD_SPACING
    num_studs = int((x_max - x_min) / STUD_SPACING) + 1

    for i in range(num_studs):
        x = x_min + i * STUD_SPACING
        for side, y_sign in (("PosY", +1), ("NegY", -1)):
            y = y_sign * (UNIT_WIDTH / 2.0 - plate_width - STUD_THICK / 2.0)
            make_box(
                f"Stud_Long_{side}_{i+1}",
                STUD_WIDTH,
                STUD_THICK,
                stud_len,
                (x, y, stud_center_z),
            )

    # Studs along short walls
    y_min = -UNIT_WIDTH / 2.0 + STUD_SPACING
    y_max = +UNIT_WIDTH / 2.0 - STUD_SPACING
    num_short_studs = int((y_max - y_min) / STUD_SPACING) + 1

    for i in range(num_short_studs):
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
# LOFT FRAMING (joists + deck, hung from studs)

def build_loft_framing():
    z0 = level_floor_deck_top()
    z_loft_bottom = z0 + LOFT_CLEAR
    z_joist_center = z_loft_bottom + JOIST_DEPTH / 2.0

    # Joists running across Y, occupying only LOFT_WIDTH near +Y side
    x_start = -UNIT_LENGTH / 2.0
    x_end   = x_start + LOFT_LENGTH

    num_joists = int(LOFT_LENGTH / STUD_SPACING) + 1
    for i in range(num_joists):
        x = x_start + i * STUD_SPACING
        make_box(
            f"Loft_Joist_{i+1}",
            JOIST_THICK,
            LOFT_WIDTH,
            JOIST_DEPTH,
            (x, (UNIT_WIDTH / 2.0) - LOFT_WIDTH / 2.0, z_joist_center),
        )

    # Loft deck (plywood)
    z_deck_center = z_loft_bottom + JOIST_DEPTH + LOFT_DECK_THICK / 2.0
    make_box(
        "Loft_Deck",
        LOFT_LENGTH,
        LOFT_WIDTH,
        LOFT_DECK_THICK,
        (-UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0,
         (UNIT_WIDTH / 2.0) - LOFT_WIDTH / 2.0,
         z_deck_center),
    )


# ------------------------------------------------------------------
# ROOF FRAMING (joists with skylight openings + deck)

def build_roof_framing():
    z0 = level_floor_deck_top() + WALL_HEIGHT
    z_joist_center = z0 + JOIST_DEPTH / 2.0

    # Skylight regions along X where we omit joists
    def in_skylight_region(x):
        half1 = SKY1_LENGTH / 2.0
        half2 = SKY2_LENGTH / 2.0
        in1 = (SKY1_CENTER_X - half1) <= x <= (SKY1_CENTER_X + half1)
        in2 = (SKY2_CENTER_X - half2) <= x <= (SKY2_CENTER_X + half2)
        return in1 or in2

    # Roof joists running across Y
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
            UNIT_WIDTH - 2.0 * PLATE_THICK,
            JOIST_DEPTH,
            (x, 0.0, z_joist_center),
        )

    # Roof deck / sheathing as a solid slab
    z_deck_center = z0 + JOIST_DEPTH + ROOF_THICK / 2.0
    make_box(
        "Roof_Deck",
        UNIT_LENGTH,
        UNIT_WIDTH,
        ROOF_THICK,
        (0.0, 0.0, z_deck_center),
    )

    # Simple skylight solids for visualization (glass volumes)
    z_sky_center = z_deck_center + SKYLIGHT_THICK / 2.0

    # Central strip skylight
    make_box(
        "Skylight_Central",
        SKY1_LENGTH,
        SKY_STRIP_WIDTH,
        SKYLIGHT_THICK,
        (SKY1_CENTER_X, 0.0, z_sky_center),
    )

    # Loft skylight
    make_box(
        "Skylight_Loft",
        SKY2_LENGTH,
        LOFT_WIDTH * 0.9,
        SKYLIGHT_THICK,
        (SKY2_CENTER_X,
         (UNIT_WIDTH / 2.0) - LOFT_WIDTH / 2.0,
         z_sky_center),
    )


# ------------------------------------------------------------------
# OPTIONAL: SIMPLE EXTERIOR SHELL (for context)

def build_exterior_shell():
    z_floor_center = level_floor_deck_top() - FLOOR_THICK / 2.0
    make_box(
        "Shell_Floor",
        UNIT_LENGTH,
        UNIT_WIDTH,
        FLOOR_THICK,
        (0.0, 0.0, z_floor_center),
    )

    # Walls as thin outer plates
    shell_thick = 0.05
    shell_height = WALL_HEIGHT

    y_outer = UNIT_WIDTH / 2.0 - shell_thick / 2.0
    x_outer = UNIT_LENGTH / 2.0 - shell_thick / 2.0
    z_wall_center = level_floor_deck_top() + shell_height / 2.0

    make_box("Shell_Wall_Long_PosY", UNIT_LENGTH, shell_thick, shell_height,
             (0.0, +y_outer, z_wall_center))
    make_box("Shell_Wall_Long_NegY", UNIT_LENGTH, shell_thick, shell_height,
             (0.0, -y_outer, z_wall_center))
    make_box("Shell_Wall_Short_PosX", shell_thick, UNIT_WIDTH, shell_height,
             (+x_outer, 0.0, z_wall_center))
    make_box("Shell_Wall_Short_NegX", shell_thick, UNIT_WIDTH, shell_height,
             (-x_outer, 0.0, z_wall_center))

    # Roof outer skin already represented by Roof_Deck


# ------------------------------------------------------------------
# BUILD COMPLETE STRUCTURE

def build_shelter():
    build_posts()
    build_floor_framing()
    build_wall_framing()
    build_loft_framing()
    build_roof_framing()
    build_exterior_shell()


build_shelter()
