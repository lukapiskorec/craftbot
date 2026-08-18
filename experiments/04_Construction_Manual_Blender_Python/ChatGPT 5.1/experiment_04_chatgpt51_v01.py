# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V01
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot   # make sure this file is on the Python path

importlib.reload(craftbot)

# ------------------------------------------------------------------
# UNITS & BASIC DIMENSIONS  (all in metres)
# ------------------------------------------------------------------

MM = 0.001

# Overall footprint (similar to example house)
HOUSE_LEN = 7.32        # X direction (approx 7320 mm)
HOUSE_WID = 5.40        # Y direction (approx 5400 mm)

PLATFORM_HEIGHT = 0.70  # raised floor above ground (700 mm)
POST_SIZE        = 0.12 # 120 x 120 posts

BEARER_DEPTH = 0.197
BEARER_WIDTH = 0.06

JOIST_DEPTH = 0.145
JOIST_WIDTH = 0.047
JOIST_SPACING = 0.61

FLOOR_THICK = 0.022

# Wall frame
WALL_HEIGHT     = 2.745   # floor to ceiling (2745 mm)
STUD_WIDTH      = 0.047
STUD_DEPTH      = 0.097   # wall thickness for exterior walls
STUD_SPACING    = 0.61

TOP_PLATE_THICK = STUD_WIDTH
TOP_PLATE_DEPTH = STUD_DEPTH
BOTTOM_PLATE_THICK = STUD_WIDTH
BOTTOM_PLATE_DEPTH = STUD_DEPTH

PLY_THICK_EXT = 0.009
PLY_THICK_INT = 0.006

# Roof
ROOF_THICK = 0.05

# Convenience: half sizes
def half(x): return x * 0.5


# ------------------------------------------------------------------
# HELPER FUNCTIONS TO PLACE ELEMENTS
# ------------------------------------------------------------------

def add_post(name, x, y, base_z, height, size=POST_SIZE):
    """Vertical post aligned with Z."""
    craftbot.place_element(
        name=name,
        loc=(x, y, base_z + half(height)),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(size), half(size), half(height)),
    )


def add_beam_x(name, x0, x1, y, z, width, depth):
    """Horizontal beam running along +X."""
    length = abs(x1 - x0)
    cx = (x0 + x1) * 0.5
    craftbot.place_element(
        name=name,
        loc=(cx, y, z),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(length), half(width), half(depth)),
    )


def add_beam_y(name, x, y0, y1, z, width, depth):
    """Horizontal beam running along +Y."""
    length = abs(y1 - y0)
    cy = (y0 + y1) * 0.5
    # swap X/Y in scale so long side is along Y
    craftbot.place_element(
        name=name,
        loc=(x, cy, z),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(width), half(length), half(depth)),
    )


def add_slab(name, x0, x1, y0, y1, z, thick):
    """Rectangular flat plate (floor/roof)."""
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    lx = abs(x1 - x0)
    ly = abs(y1 - y0)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, z),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(lx), half(ly), half(thick)),
    )


def add_stud(name, x, y, base_z, height):
    add_post(name, x, y, base_z, height, size=STUD_DEPTH)


def add_plate_x(name, x0, x1, y, z, depth=STUD_DEPTH, thick=STUD_WIDTH):
    add_beam_x(name, x0, x1, y, z, width=thick, depth=depth)


def add_plate_y(name, x, y0, y1, z, depth=STUD_DEPTH, thick=STUD_WIDTH):
    add_beam_y(name, x, y0, y1, z, width=thick, depth=depth)


def add_plywood_wall_x(name, x0, x1, y, base_z, height, thickness):
    """Wall panel whose outer face is at +Y for given y."""
    lx = abs(x1 - x0)
    cx = (x0 + x1) * 0.5
    zc = base_z + half(height)
    # shift half thickness outward in +Y
    craftbot.place_element(
        name=name,
        loc=(cx, y + half(thickness), zc),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(lx), half(thickness), half(height)),
    )


def add_plywood_wall_y(name, x, y0, y1, base_z, height, thickness):
    """Wall panel whose outer face is at +X for given x."""
    ly = abs(y1 - y0)
    cy = (y0 + y1) * 0.5
    zc = base_z + half(height)
    craftbot.place_element(
        name=name,
        loc=(x + half(thickness), cy, zc),
        axis=(0, 0, 1),
        angle=0.0,
        scale=(half(thickness), half(ly), half(height)),
    )


# ------------------------------------------------------------------
# PLATFORM: POSTS, BEARERS, JOISTS, FLOOR
# ------------------------------------------------------------------

def build_platform():
    x0 = 0.0
    x1 = HOUSE_LEN
    y0 = 0.0
    y1 = HOUSE_WID

    # posts at four corners and midpoints of long sides
    post_z0 = 0.0
    post_h = PLATFORM_HEIGHT

    post_positions = [
        (x0, y0),
        (x1, y0),
        (x0, y1),
        (x1, y1),
        ((x0 + x1) * 0.5, y0),
        ((x0 + x1) * 0.5, y1),
    ]

    for i, (px, py) in enumerate(post_positions):
        add_post(f"Post_{i}", px, py, post_z0, post_h)

    # bearers along X direction on both sides
    bearer_z = PLATFORM_HEIGHT + half(BEARER_DEPTH)
    add_beam_x("Bearer_South", x0, x1, y0 + half(POST_SIZE), bearer_z,
               width=BEARER_WIDTH, depth=BEARER_DEPTH)
    add_beam_x("Bearer_North", x0, x1, y1 - half(POST_SIZE), bearer_z,
               width=BEARER_WIDTH, depth=BEARER_DEPTH)

    # floor joists running in Y, sitting on bearers
    joist_z = bearer_z + half(BEARER_DEPTH) + half(JOIST_DEPTH)
    n_joists = int(HOUSE_LEN / JOIST_SPACING) + 1

    for j in range(n_joists):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            break
        add_beam_y(f"Joist_{j}", x,
                   y0 + half(POST_SIZE),
                   y1 - half(POST_SIZE),
                   joist_z,
                   width=JOIST_WIDTH,
                   depth=JOIST_DEPTH)

    # floor slab / boards
    floor_z = joist_z + half(JOIST_DEPTH) + half(FLOOR_THICK)
    add_slab("Floor", x0, x1, y0, y1, floor_z, FLOOR_THICK)

    return floor_z


# ------------------------------------------------------------------
# WALL FRAMES + PLYWOOD CLADDING
# ------------------------------------------------------------------

def build_walls(floor_z):
    base_z = floor_z + half(FLOOR_THICK)  # top of floor

    # Bottom & top plates around perimeter
    # South wall (along X, at y0)
    y_s = 0.0
    y_n = HOUSE_WID
    x_w = 0.0
    x_e = HOUSE_LEN

    bottom_z = base_z + half(BOTTOM_PLATE_THICK)
    top_z    = base_z + WALL_HEIGHT - half(TOP_PLATE_THICK)

    # bottom plates
    add_plate_x("Bottom_S", x_w, x_e, y_s, bottom_z)
    add_plate_x("Bottom_N", x_w, x_e, y_n, bottom_z)
    add_plate_y("Bottom_W", x_w, y_s, y_n, bottom_z)
    add_plate_y("Bottom_E", x_e, y_s, y_n, bottom_z)

    # top plates
    add_plate_x("Top_S", x_w, x_e, y_s, top_z)
    add_plate_x("Top_N", x_w, x_e, y_n, top_z)
    add_plate_y("Top_W", x_w, y_s, y_n, top_z)
    add_plate_y("Top_E", x_e, y_s, y_n, top_z)

    # Studs on each wall at 610 mm, sharing corners
    # South wall studs
    n_s = int(HOUSE_LEN / STUD_SPACING) + 1
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        add_stud(f"Stud_S_{i}", x, y_s, base_z, WALL_HEIGHT)

    # North wall studs
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        add_stud(f"Stud_N_{i}", x, y_n, base_z, WALL_HEIGHT)

    # West & East wall studs
    n_w = int(HOUSE_WID / STUD_SPACING) + 1
    for i in range(n_w + 1):
        y = y_s + i * STUD_SPACING
        if y > y_n:
            y = y_n
        add_stud(f"Stud_W_{i}", x_w, y, base_z, WALL_HEIGHT)
        add_stud(f"Stud_E_{i}", x_e, y, base_z, WALL_HEIGHT)

    # Exterior plywood cladding (one big panel per wall for simplicity)
    add_plywood_wall_x(
        "Ply_S_ext", x_w, x_e, y_s - half(STUD_DEPTH),
        base_z, WALL_HEIGHT, PLY_THICK_EXT
    )
    add_plywood_wall_x(
        "Ply_N_ext", x_w, x_e, y_n,
        base_z, WALL_HEIGHT, PLY_THICK_EXT
    )
    add_plywood_wall_y(
        "Ply_W_ext", x_w - half(STUD_DEPTH), y_s, y_n,
        base_z, WALL_HEIGHT, PLY_THICK_EXT
    )
    add_plywood_wall_y(
        "Ply_E_ext", x_e, y_s, y_n,
        base_z, WALL_HEIGHT, PLY_THICK_EXT
    )

    # Interior lining (optional, pushed slightly inwards)
    add_plywood_wall_x(
        "Ply_S_int", x_w, x_e, y_s + STUD_DEPTH,
        base_z, WALL_HEIGHT, PLY_THICK_INT
    )
    add_plywood_wall_x(
        "Ply_N_int", x_w, x_e, y_n - STUD_DEPTH,
        base_z, WALL_HEIGHT, PLY_THICK_INT
    )
    add_plywood_wall_y(
        "Ply_W_int", x_w + STUD_DEPTH, y_s, y_n,
        base_z, WALL_HEIGHT, PLY_THICK_INT
    )
    add_plywood_wall_y(
        "Ply_E_int", x_e - STUD_DEPTH, y_s, y_n,
        base_z, WALL_HEIGHT, PLY_THICK_INT
    )

    return base_z + WALL_HEIGHT


# ------------------------------------------------------------------
# SIMPLE FLAT ROOF SLAB (placeholder for trussed roof)
# ------------------------------------------------------------------

def build_roof(wall_top_z):
    roof_z = wall_top_z + half(ROOF_THICK)
    add_slab("Roof", 0.0, HOUSE_LEN, 0.0, HOUSE_WID, roof_z, ROOF_THICK)


# ------------------------------------------------------------------
# MAIN BUILD SEQUENCE
# ------------------------------------------------------------------

def build_house():
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


# Run when script is executed
build_house()
