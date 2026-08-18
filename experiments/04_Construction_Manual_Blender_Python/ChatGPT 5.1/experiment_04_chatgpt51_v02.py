# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V02
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot

# Always reload to pick up changes to craftbot_lib during development
importlib.reload(craftbot)

# ---------------------------------------------------------------------------
# BASIC PARAMETERS (metres)
# ---------------------------------------------------------------------------

MM = 0.001

# Overall footprint
HOUSE_LEN = 7.32
HOUSE_WID = 5.40

# Support posts / platform
PLATFORM_HEIGHT = 0.70
POST_SIZE = 0.12  # square post 120 x 120

# Bearers (girders) under joists
BEARER_DEPTH = 0.197  # vertical
BEARER_WIDTH = 0.06   # horizontal width

# Floor joists
JOIST_DEPTH = 0.145   # vertical
JOIST_WIDTH = 0.047   # horizontal width
JOIST_SPACING = 0.61  # centre-to-centre

# Floor decking
FLOOR_THICK = 0.022

# Wall frame
WALL_STUD_HEIGHT = 2.745  # clear stud length between plates
STUD_WIDTH = 0.047        # minor cross-section
STUD_DEPTH = 0.097        # wall thickness / major cross-section
STUD_SPACING = 0.61

# Plates (same section as studs, rotated)
BOTTOM_PLATE_DEPTH = STUD_DEPTH   # vertical (height)
BOTTOM_PLATE_THICK = STUD_WIDTH   # horizontal
TOP_PLATE_DEPTH = STUD_DEPTH
TOP_PLATE_THICK = STUD_WIDTH

# Plywood sheathing
PLY_THICK_EXT = 0.009
PLY_THICK_INT = 0.006

# Roof slab (placeholder for trusses)
ROOF_THICK = 0.05


# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def half(x: float) -> float:
    return 0.5 * x


def add_post(name, x, y, base_z, height, size=POST_SIZE):
    """Vertical element with square cross-section 'size'."""
    craftbot.place_element(
        name=name,
        loc=(x, y, base_z + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(size), half(size), half(height)),
    )


def add_beam_x(name, x0, x1, y, z, width, depth):
    """Beam running along X."""
    length = abs(x1 - x0)
    cx = 0.5 * (x0 + x1)
    craftbot.place_element(
        name=name,
        loc=(cx, y, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(length), half(width), half(depth)),
    )


def add_beam_y(name, x, y0, y1, z, width, depth):
    """Beam running along Y."""
    length = abs(y1 - y0)
    cy = 0.5 * (y0 + y1)
    craftbot.place_element(
        name=name,
        loc=(x, cy, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(width), half(length), half(depth)),
    )


def add_slab(name, x0, x1, y0, y1, z, thick):
    """Rectangular plate (floor/roof)."""
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    lx = abs(x1 - x0)
    ly = abs(y1 - y0)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(lx), half(ly), half(thick)),
    )


def add_stud(name, x, y, base_z, height):
    """Wall stud, oriented like a post but with stud section."""
    add_post(name, x, y, base_z, height, size=STUD_DEPTH)


def add_plywood_wall_x(name, x0, x1, y, base_z, height, thickness):
    """Plywood sheet spanning along X, face normal ±Y."""
    lx = abs(x1 - x0)
    cx = 0.5 * (x0 + x1)
    zc = base_z + half(height)
    craftbot.place_element(
        name=name,
        loc=(cx, y + half(thickness), zc),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(lx), half(thickness), half(height)),
    )


def add_plywood_wall_y(name, x, y0, y1, base_z, height, thickness):
    """Plywood sheet spanning along Y, face normal ±X."""
    ly = abs(y1 - y0)
    cy = 0.5 * (y0 + y1)
    zc = base_z + half(height)
    craftbot.place_element(
        name=name,
        loc=(x + half(thickness), cy, zc),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(thickness), half(ly), half(height)),
    )


# ---------------------------------------------------------------------------
# PLATFORM: POSTS, BEARERS, JOISTS, FLOOR
# ---------------------------------------------------------------------------

def build_platform():
    x0 = 0.0
    x1 = HOUSE_LEN
    y0 = 0.0
    y1 = HOUSE_WID

    # Posts
    post_z0 = 0.0
    post_h = PLATFORM_HEIGHT

    post_positions = [
        (x0, y0),
        (x1, y0),
        (x0, y1),
        (x1, y1),
        (0.5 * (x0 + x1), y0),
        (0.5 * (x0 + x1), y1),
    ]

    for i, (px, py) in enumerate(post_positions):
        add_post(f"Post_{i}", px, py, post_z0, post_h)

    # Bearers extend beyond centre of end posts for better joints
    bearer_z = PLATFORM_HEIGHT + half(BEARER_DEPTH)
    bearer_x0 = x0 - half(POST_SIZE)
    bearer_x1 = x1 + half(POST_SIZE)

    add_beam_x(
        "Bearer_South",
        bearer_x0,
        bearer_x1,
        y0 + half(POST_SIZE),
        bearer_z,
        width=BEARER_WIDTH,
        depth=BEARER_DEPTH,
    )
    add_beam_x(
        "Bearer_North",
        bearer_x0,
        bearer_x1,
        y1 - half(POST_SIZE),
        bearer_z,
        width=BEARER_WIDTH,
        depth=BEARER_DEPTH,
    )

    # Joists sitting on bearers, no overlap
    joist_z = bearer_z + half(BEARER_DEPTH) + half(JOIST_DEPTH)
    n_joists = int(HOUSE_LEN / JOIST_SPACING) + 1

    for j in range(n_joists):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1
        add_beam_y(
            f"Joist_{j}",
            x,
            y0 + half(POST_SIZE),
            y1 - half(POST_SIZE),
            joist_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # Floor boards fully above joists
    floor_z = joist_z + half(JOIST_DEPTH) + half(FLOOR_THICK)
    add_slab("Floor", x0, x1, y0, y1, floor_z, FLOOR_THICK)

    return floor_z


# ---------------------------------------------------------------------------
# WALL FRAMES + PLYWOOD
# ---------------------------------------------------------------------------

def build_walls(floor_z):
    # Top of floor boards
    floor_top_z = floor_z + half(FLOOR_THICK)

    x_w = 0.0
    x_e = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # Bottom plates sit fully on top of floor (no overlap)
    bottom_plate_center_z = floor_top_z + half(BOTTOM_PLATE_DEPTH)
    bottom_plate_top_z = floor_top_z + BOTTOM_PLATE_DEPTH

    # Studs stand on top of bottom plates
    stud_base_z = bottom_plate_top_z
    stud_height = WALL_STUD_HEIGHT

    # Top plates sit on top of studs
    top_plate_center_z = stud_base_z + stud_height + half(TOP_PLATE_DEPTH)
    wall_total_height = BOTTOM_PLATE_DEPTH + stud_height + TOP_PLATE_DEPTH

    # Plates extend beyond corner studs for better lap joints
    plate_x0 = x_w - half(STUD_DEPTH)
    plate_x1 = x_e + half(STUD_DEPTH)
    plate_y0 = y_s - half(STUD_DEPTH)
    plate_y1 = y_n + half(STUD_DEPTH)

    # Bottom plates
    add_beam_x(
        "Bottom_S",
        plate_x0,
        plate_x1,
        y_s,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )
    add_beam_x(
        "Bottom_N",
        plate_x0,
        plate_x1,
        y_n,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )
    add_beam_y(
        "Bottom_W",
        x_w,
        plate_y0,
        plate_y1,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )
    add_beam_y(
        "Bottom_E",
        x_e,
        plate_y0,
        plate_y1,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )

    # Top plates
    add_beam_x(
        "Top_S",
        plate_x0,
        plate_x1,
        y_s,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )
    add_beam_x(
        "Top_N",
        plate_x0,
        plate_x1,
        y_n,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )
    add_beam_y(
        "Top_W",
        x_w,
        plate_y0,
        plate_y1,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )
    add_beam_y(
        "Top_E",
        x_e,
        plate_y0,
        plate_y1,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )

    # Studs on all four sides, clear of plates
    n_s = int(HOUSE_LEN / STUD_SPACING) + 1
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        add_stud(f"Stud_S_{i}", x, y_s, stud_base_z, stud_height)
        add_stud(f"Stud_N_{i}", x, y_n, stud_base_z, stud_height)

    n_w = int(HOUSE_WID / STUD_SPACING) + 1
    for i in range(n_w + 1):
        y = y_s + i * STUD_SPACING
        if y > y_n:
            y = y_n
        add_stud(f"Stud_W_{i}", x_w, y, stud_base_z, stud_height)
        add_stud(f"Stud_E_{i}", x_e, y, stud_base_z, stud_height)

    # Plywood sheathing: continuous from floor level to top plate
    ply_base_z = floor_top_z
    ply_height = wall_total_height

    # Exterior
    add_plywood_wall_x(
        "Ply_S_ext",
        x_w,
        x_e,
        y_s - half(STUD_DEPTH),
        ply_base_z,
        ply_height,
        PLY_THICK_EXT,
    )
    add_plywood_wall_x(
        "Ply_N_ext",
        x_w,
        x_e,
        y_n,
        ply_base_z,
        ply_height,
        PLY_THICK_EXT,
    )
    add_plywood_wall_y(
        "Ply_W_ext",
        x_w - half(STUD_DEPTH),
        y_s,
        y_n,
        ply_base_z,
        ply_height,
        PLY_THICK_EXT,
    )
    add_plywood_wall_y(
        "Ply_E_ext",
        x_e,
        y_s,
        y_n,
        ply_base_z,
        ply_height,
        PLY_THICK_EXT,
    )

    # Interior
    add_plywood_wall_x(
        "Ply_S_int",
        x_w,
        x_e,
        y_s + STUD_DEPTH,
        ply_base_z,
        ply_height,
        PLY_THICK_INT,
    )
    add_plywood_wall_x(
        "Ply_N_int",
        x_w,
        x_e,
        y_n - STUD_DEPTH,
        ply_base_z,
        ply_height,
        PLY_THICK_INT,
    )
    add_plywood_wall_y(
        "Ply_W_int",
        x_w + STUD_DEPTH,
        y_s,
        y_n,
        ply_base_z,
        ply_height,
        PLY_THICK_INT,
    )
    add_plywood_wall_y(
        "Ply_E_int",
        x_e - STUD_DEPTH,
        y_s,
        y_n,
        ply_base_z,
        ply_height,
        PLY_THICK_INT,
    )

    wall_top_z = top_plate_center_z + half(TOP_PLATE_DEPTH)
    return wall_top_z


# ---------------------------------------------------------------------------
# ROOF
# ---------------------------------------------------------------------------

def build_roof(wall_top_z):
    roof_z = wall_top_z + half(ROOF_THICK)
    add_slab("Roof", 0.0, HOUSE_LEN, 0.0, HOUSE_WID, roof_z, ROOF_THICK)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def build_house():
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


build_house()
