# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 06 - CHATGPT 5.1 - V01
# DESCRIPTION: PROUVE CABANON
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot   # uses place_element() from craftbot_lib.py

# Reload to ensure latest version of craftbot_lib is used
importlib.reload(craftbot)

# ----------------------------------------------------------------------
# GLOBAL PARAMETERS (metres)
# ----------------------------------------------------------------------

EPS = 1e-5

# Overall footprint
UNIT_LEN = 6.00    # X direction
UNIT_WID = 6.00    # Y direction

# Floor
FLOOR_THICK = 0.18
FLOOR_LEVEL = 0.00 + FLOOR_THICK  # top of floor slab

# Structural timber sizes
POST_SIZE   = 0.12         # square posts 120 x 120
BEAM_WIDTH  = 0.08         # beam width in plan
BEAM_DEPTH  = 0.18         # beam depth vertically
PURLIN_WIDTH = 0.06
PURLIN_DEPTH = 0.08

# Cladding panels (timber slat cassettes)
PANEL_THICK = 0.04
PANEL_HEIGHT = 2.10        # clear height of wall panels

# Roof geometry (mono-pitch, front low, back high)
ROOF_LOW_EAVE_Z  = FLOOR_LEVEL + 2.20
ROOF_HIGH_EAVE_Z = FLOOR_LEVEL + 2.60
ROOF_SLOPE = (ROOF_HIGH_EAVE_Z - ROOF_LOW_EAVE_Z) / UNIT_WID

ROOF_SHEET_THICK = 0.03
NUM_PURLINS = 8

# Portal frame position
PORTAL_X = UNIT_LEN * 0.5
PORTAL_Y_INSET = 1.00       # distance of posts from front/back edges

# Wall panel layout
PANELS_PER_LONG_SIDE = 4
PANELS_PER_SHORT_SIDE = 3


# ----------------------------------------------------------------------
# SMALL UTILITY HELPERS
# ----------------------------------------------------------------------

def half(x: float) -> float:
    return 0.5 * x


def add_slab(name, x0, x1, y0, y1, z_center, thick):
    """Horizontal slab aligned with XY plane."""
    lx = abs(x1 - x0)
    ly = abs(y1 - y0)
    if lx <= EPS or ly <= EPS:
        return
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, z_center),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(lx), half(ly), half(thick)),
    )


def add_post(name, x, y, base_z, top_z, size=POST_SIZE):
    """Vertical post with square cross-section."""
    height = top_z - base_z
    if height <= EPS:
        return
    craftbot.place_element(
        name=name,
        loc=(x, y, base_z + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(size), half(size), half(height)),
    )


def add_beam_x(name, x0, x1, y, z_center, width, depth):
    """Rectangular beam running along X direction."""
    length = abs(x1 - x0)
    if length <= EPS:
        return
    cx = 0.5 * (x0 + x1)
    craftbot.place_element(
        name=name,
        loc=(cx, y, z_center),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(length), half(width), half(depth)),
    )


def add_beam_y(name, x, y0, y1, z_center, width, depth):
    """Rectangular beam running along Y direction (horizontal)."""
    length = abs(y1 - y0)
    if length <= EPS:
        return
    cy = 0.5 * (y0 + y1)
    craftbot.place_element(
        name=name,
        loc=(x, cy, z_center),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(width), half(length), half(depth)),
    )


def add_sloped_beam_y(name, x, y0, z0, y1, z1, width, depth):
    """
    Beam running between (y0, z0) and (y1, z1) in the YZ plane,
    oriented along its own local Y axis, rotated about world X.
    Used for the central mono-pitch portal beam and roof sheet.
    """
    dy = y1 - y0
    dz = z1 - z0
    length = math.sqrt(dy * dy + dz * dz)
    if length <= EPS:
        return

    yc = 0.5 * (y0 + y1)
    zc = 0.5 * (z0 + z1)
    angle_rad = math.atan2(dz, dy)
    angle_deg = math.degrees(angle_rad)

    craftbot.place_element(
        name=name,
        loc=(x, yc, zc),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(width), half(length), half(depth)),
    )


def add_wall_panel_x(name, x0, x1, y, base_z, top_z, thick, outward=1.0):
    """
    Vertical panel spanning along X, face normal ±Y.
    outward = +1 moves panel towards +Y; outward = -1 towards -Y.
    """
    lx = abs(x1 - x0)
    height = top_z - base_z
    if lx <= EPS or height <= EPS:
        return
    cx = 0.5 * (x0 + x1)
    cy = y + outward * half(thick)
    cz = 0.5 * (base_z + top_z)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(lx), half(thick), half(height)),
    )


def add_wall_panel_y(name, x, y0, y1, base_z, top_z, thick, outward=1.0):
    """
    Vertical panel spanning along Y, face normal ±X.
    outward = +1 moves panel towards +X; outward = -1 towards -X.
    """
    ly = abs(y1 - y0)
    height = top_z - base_z
    if ly <= EPS or height <= EPS:
        return
    cy = 0.5 * (y0 + y1)
    cx = x + outward * half(thick)
    cz = 0.5 * (base_z + top_z)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(thick), half(ly), half(height)),
    )


# ----------------------------------------------------------------------
# PLATFORM
# ----------------------------------------------------------------------

def build_platform():
    """
    Simple solid floor slab representing concrete or metal deck.
    Returns: top Z level of the floor.
    """
    z_center = FLOOR_LEVEL - half(FLOOR_THICK)
    add_slab(
        "Floor_Slab",
        0.0,
        UNIT_LEN,
        0.0,
        UNIT_WID,
        z_center,
        FLOOR_THICK,
    )
    return FLOOR_LEVEL


# ----------------------------------------------------------------------
# PRIMARY STRUCTURE: PORTAL FRAME + EDGE BEAMS
# ----------------------------------------------------------------------

def build_primary_frame(floor_top_z):
    """
    Build:
      - central mono-pitch portal frame (2 posts + sloped beam)
      - front and back longitudinal edge beams
    """

    # 1) Central sloped beam defining roof pitch
    add_sloped_beam_y(
        "Portal_Beam",
        PORTAL_X,
        0.0,
        ROOF_LOW_EAVE_Z,
        UNIT_WID,
        ROOF_HIGH_EAVE_Z,
        width=BEAM_WIDTH,
        depth=BEAM_DEPTH,
    )

    # 2) Portal posts positioned slightly in from front/back edges
    y_front = PORTAL_Y_INSET
    y_back = UNIT_WID - PORTAL_Y_INSET

    z_front_on_beam = ROOF_LOW_EAVE_Z + ROOF_SLOPE * y_front
    z_back_on_beam = ROOF_LOW_EAVE_Z + ROOF_SLOPE * y_back

    add_post(
        "Portal_Post_Front",
        PORTAL_X,
        y_front,
        floor_top_z,
        z_front_on_beam,
        size=POST_SIZE,
    )
    add_post(
        "Portal_Post_Back",
        PORTAL_X,
        y_back,
        floor_top_z,
        z_back_on_beam,
        size=POST_SIZE,
    )

    # 3) Front and back edge beams along X
    add_beam_x(
        "Edge_Beam_Front",
        0.0,
        UNIT_LEN,
        0.0,
        ROOF_LOW_EAVE_Z,
        width=BEAM_WIDTH,
        depth=BEAM_DEPTH,
    )
    add_beam_x(
        "Edge_Beam_Back",
        0.0,
        UNIT_LEN,
        UNIT_WID,
        ROOF_HIGH_EAVE_Z,
        width=BEAM_WIDTH,
        depth=BEAM_DEPTH,
    )

    # 4) Corner posts tying beams down to floor (simple verticals)
    add_post(
        "Corner_SW",
        0.0,
        0.0,
        floor_top_z,
        ROOF_LOW_EAVE_Z,
        size=POST_SIZE,
    )
    add_post(
        "Corner_SE",
        UNIT_LEN,
        0.0,
        floor_top_z,
        ROOF_LOW_EAVE_Z,
        size=POST_SIZE,
    )
    add_post(
        "Corner_NW",
        0.0,
        UNIT_WID,
        floor_top_z,
        ROOF_HIGH_EAVE_Z,
        size=POST_SIZE,
    )
    add_post(
        "Corner_NE",
        UNIT_LEN,
        UNIT_WID,
        floor_top_z,
        ROOF_HIGH_EAVE_Z,
        size=POST_SIZE,
    )


# ----------------------------------------------------------------------
# ROOF: PURLINS AND SHEET
# ----------------------------------------------------------------------

def build_roof(floor_top_z):
    """
    Build roof joists/purlins spanning along X between front/back beams,
    plus a single large sloped roof sheet.
    """
    # Purlins along X, positioned at different Y following roof slope
    for i in range(NUM_PURLINS):
        if NUM_PURLINS == 1:
            t = 0.5
        else:
            t = i / (NUM_PURLINS - 1)
        y = t * UNIT_WID
        z_center = ROOF_LOW_EAVE_Z + ROOF_SLOPE * y
        add_beam_x(
            f"Purlin_{i:02d}",
            0.0,
            UNIT_LEN,
            y,
            z_center,
            width=PURLIN_WIDTH,
            depth=PURLIN_DEPTH,
        )

    # Single sheet representing timber boards + waterproofing
    z_front_sheet = (
        ROOF_LOW_EAVE_Z
        + PURLIN_DEPTH * 0.5
        + ROOF_SHEET_THICK * 0.5
    )
    z_back_sheet = (
        ROOF_HIGH_EAVE_Z
        + PURLIN_DEPTH * 0.5
        + ROOF_SHEET_THICK * 0.5
    )

    add_sloped_beam_y(
        "Roof_Sheet",
        UNIT_LEN * 0.5,
        0.0,
        z_front_sheet,
        UNIT_WID,
        z_back_sheet,
        width=UNIT_LEN,
        depth=ROOF_SHEET_THICK,
    )


# ----------------------------------------------------------------------
# WALL PANELS WITH TIMBER-SLAT CLADDING
# ----------------------------------------------------------------------

def build_wall_panels(floor_top_z):
    """
    Builds a ring of prefabricated wall panels around the perimeter.
    Panels are modelled as thin boxes; door opening is left in front wall.
    """
    base_z = floor_top_z
    top_z = floor_top_z + PANEL_HEIGHT

    # --- Long sides (front and back) ---
    panel_len_long = UNIT_LEN / PANELS_PER_LONG_SIDE

    # front (y = 0), outward = -1 (panels sit slightly outside footprint)
    door_index = PANELS_PER_LONG_SIDE // 2  # leave one bay open as door

    for i in range(PANELS_PER_LONG_SIDE):
        if i == door_index:
            continue  # door opening
        x0 = i * panel_len_long
        x1 = (i + 1) * panel_len_long
        add_wall_panel_x(
            f"Panel_Front_{i}",
            x0,
            x1,
            0.0,
            base_z,
            top_z,
            PANEL_THICK,
            outward=-1.0,
        )

    # back (y = UNIT_WID)
    for i in range(PANELS_PER_LONG_SIDE):
        x0 = i * panel_len_long
        x1 = (i + 1) * panel_len_long
        add_wall_panel_x(
            f"Panel_Back_{i}",
            x0,
            x1,
            UNIT_WID,
            base_z,
            top_z,
            PANEL_THICK,
            outward=+1.0,
        )

    # --- Short sides (left and right) ---
    panel_len_short = UNIT_WID / PANELS_PER_SHORT_SIDE

    # left (x = 0)
    for j in range(PANELS_PER_SHORT_SIDE):
        y0 = j * panel_len_short
        y1 = (j + 1) * panel_len_short
        add_wall_panel_y(
            f"Panel_Left_{j}",
            0.0,
            y0,
            y1,
            base_z,
            top_z,
            PANEL_THICK,
            outward=-1.0,
        )

    # right (x = UNIT_LEN)
    for j in range(PANELS_PER_SHORT_SIDE):
        y0 = j * panel_len_short
        y1 = (j + 1) * panel_len_short
        add_wall_panel_y(
            f"Panel_Right_{j}",
            UNIT_LEN,
            y0,
            y1,
            base_z,
            top_z,
            PANEL_THICK,
            outward=+1.0,
        )


# ----------------------------------------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------------------------------------

def build_unit():
    """
    Build full prefabricated timber unit:
      1) floor platform
      2) primary frame (portal + edge beams + corner posts)
      3) roof purlins and sheet
      4) perimeter wall panels (timber-slat cassettes)
    """
    floor_top_z = build_platform()
    build_primary_frame(floor_top_z)
    build_roof(floor_top_z)
    build_wall_panels(floor_top_z)


# Execute immediately when script is run in Blender
build_unit()
