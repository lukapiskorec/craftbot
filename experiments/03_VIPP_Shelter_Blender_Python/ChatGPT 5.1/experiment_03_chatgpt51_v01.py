# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 03 - CHATGPT 5.1 - V01
# DESCRIPTION: VIPP SHELTER
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # make sure this imports correctly

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS  (all in meters)

UNIT_LENGTH = 11.5   # overall length in X
UNIT_WIDTH  = 5.2    # overall width in Y
WALL_HEIGHT = 3.0    # clear wall height from floor cassette
FLOOR_THICK = 0.30
ROOF_THICK  = 0.25
LOFT_LENGTH = 5.0
LOFT_WIDTH  = 2.5
LOFT_THICK  = 0.25

POST_HEIGHT = 0.80
POST_SIZE   = 0.25   # square posts

WALL_THICK  = 0.15   # for visual representation, not literal

# Skylight sizes (on plan, simplified)
SKY_STRIP_LENGTH = 4.0
SKY_STRIP_WIDTH  = 1.2
SKY_THICK        = 0.10

# Coordinate convention:
# X = length (11.5 m), Y = width (5.2 m), Z = height


# ------------------------------------------------------------------
# HELPER FUNCTIONS

def make_box(name, size_x, size_y, size_z, center):
    """
    Convenience wrapper around craftbot.place_element().
    size_* are full dimensions; center is (x, y, z) of the box center.
    """
    sx = size_x / 2.0
    sy = size_y / 2.0
    sz = size_z / 2.0
    craftbot.place_element(
        name=name,
        loc=center,
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(sx, sy, sz),
    )


# ------------------------------------------------------------------
# CLEAN SCENE (optional)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

clear_scene()


# ------------------------------------------------------------------
# SUPPORT POSTS

def build_posts():
    # Four corner posts; you can add midspan posts if you like.
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
# FLOOR CASSETTE

def build_floor():
    zc = POST_HEIGHT + FLOOR_THICK / 2.0
    make_box(
        "Floor_Cassette",
        UNIT_LENGTH,
        UNIT_WIDTH,
        FLOOR_THICK,
        (0.0, 0.0, zc),
    )


# ------------------------------------------------------------------
# EXTERIOR WALLS

def build_walls():
    z_base = POST_HEIGHT + FLOOR_THICK
    zc = z_base + WALL_HEIGHT / 2.0

    # Long walls (X direction), one each side in Y
    y_offset = UNIT_WIDTH / 2.0 - WALL_THICK / 2.0
    make_box(
        "Wall_Long_PosY",
        UNIT_LENGTH,
        WALL_THICK,
        WALL_HEIGHT,
        (0.0, +y_offset, zc),
    )
    make_box(
        "Wall_Long_NegY",
        UNIT_LENGTH,
        WALL_THICK,
        WALL_HEIGHT,
        (0.0, -y_offset, zc),
    )

    # Short walls (Y direction), one each end in X
    x_offset = UNIT_LENGTH / 2.0 - WALL_THICK / 2.0
    make_box(
        "Wall_Short_PosX",
        WALL_THICK,
        UNIT_WIDTH,
        WALL_HEIGHT,
        (+x_offset, 0.0, zc),
    )
    make_box(
        "Wall_Short_NegX",
        WALL_THICK,
        UNIT_WIDTH,
        WALL_HEIGHT,
        (-x_offset, 0.0, zc),
    )


# ------------------------------------------------------------------
# LOFT SLAB (partial width)

def build_loft():
    z_base = POST_HEIGHT + FLOOR_THICK + 2.2  # clear height below loft
    zc = z_base + LOFT_THICK / 2.0

    # Loft is placed toward the negative X end of the volume.
    x_center = -UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0

    # Loft occupies only one side in Y; here we put it on the +Y side.
    y_center = (UNIT_WIDTH / 2.0) - (LOFT_WIDTH / 2.0)

    make_box(
        "Loft_Slab",
        LOFT_LENGTH,
        LOFT_WIDTH,
        LOFT_THICK,
        (x_center, y_center, zc),
    )


# ------------------------------------------------------------------
# ROOF SLAB

def build_roof():
    z_base = POST_HEIGHT + FLOOR_THICK + WALL_HEIGHT
    zc = z_base + ROOF_THICK / 2.0

    make_box(
        "Roof_Slab",
        UNIT_LENGTH,
        UNIT_WIDTH,
        ROOF_THICK,
        (0.0, 0.0, zc),
    )


# ------------------------------------------------------------------
# UPPER BOX (the narrow volume on the roof)

def build_upper_box():
    z_base = POST_HEIGHT + FLOOR_THICK + WALL_HEIGHT + ROOF_THICK
    height = 1.4

    x_center = -UNIT_LENGTH / 4.0   # shifted toward loft end
    y_center = 0.0                  # centered across width

    make_box(
        "Upper_Box",
        LOFT_LENGTH,   # roughly over the loft zone
        LOFT_WIDTH,    # narrower than full width
        height,
        (x_center, y_center, z_base + height / 2.0),
    )


# ------------------------------------------------------------------
# SKYLIGHTS (simple glass prisms above roof)

def build_skylights():
    z_roof_top = POST_HEIGHT + FLOOR_THICK + WALL_HEIGHT + ROOF_THICK

    # Skylight over loft
    x_center_loft = -UNIT_LENGTH / 2.0 + LOFT_LENGTH / 2.0
    y_center_loft = (UNIT_WIDTH / 2.0) - (LOFT_WIDTH / 2.0)

    make_box(
        "Skylight_Loft",
        LOFT_LENGTH * 0.8,
        LOFT_WIDTH * 0.8,
        SKY_THICK,
        (x_center_loft, y_center_loft, z_roof_top + SKY_THICK / 2.0),
    )

    # Central skylight strip
    x_center_strip = 0.0
    y_center_strip = 0.0
    make_box(
        "Skylight_Strip",
        SKY_STRIP_LENGTH,
        SKY_STRIP_WIDTH,
        SKY_THICK,
        (x_center_strip, y_center_strip, z_roof_top + SKY_THICK / 2.0),
    )


# ------------------------------------------------------------------
# BUILD ALL

def build_shelter():
    build_posts()
    build_floor()
    build_walls()
    build_loft()
    build_roof()
    build_upper_box()
    build_skylights()

build_shelter()
