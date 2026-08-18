# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 08 - CHATGPT 5.1 - V03
# THE SEGAL METHOD
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot

importlib.reload(craftbot)


# ------------------------------------------------------------------
# PARAMETERS

# Modular grid
MODULE = 1.2          # 1.2 m module (matches 1200 mm boards)
NX = 8                # bays in X (doubled)
NY = 3                # bays in Y

# Storeys
N_STOREYS = 2         # ground + upper floor

# Basic dimensions (metres / Blender units)
STOREY_HEIGHT = 2.4   # floor-to-floor
FLOOR_ELEV = 0.6      # bottom of ground floor deck above ground
FLOOR_THICK = 0.2     # floor slab thickness
ROOF_THICK = 0.2      # roof slab thickness

# Timber section sizes
POST_SECTION = 0.10   # 100 x 100 mm posts
BEAM_SECTION = 0.10   # 100 x 100 mm beams

# Wall thickness (plywood + build-up)
WALL_THICK = 0.12

# Stair parameters
N_STEPS = 12
STAIR_WIDTH = MODULE
STAIR_RUN = MODULE * 3.0  # horizontal run of stair

# Double-height configuration
VOID_SIDE = "E"       # remove upper floor + roof on east half

# ------------------------------------------------------------------
# DERIVED DIMENSIONS

Lx = NX * MODULE      # overall length (X)
Ly = NY * MODULE      # overall width (Y)

# Vertical levels
POST_HEIGHT = FLOOR_ELEV + N_STOREYS * STOREY_HEIGHT       # top of posts
ROOF_BEAM_LEVEL = POST_HEIGHT                              # where roof beams sit

FLOOR0_BOTTOM = FLOOR_ELEV
FLOOR1_BOTTOM = FLOOR_ELEV + STOREY_HEIGHT

FLOOR0_CENTER = FLOOR0_BOTTOM + FLOOR_THICK / 2.0
FLOOR1_CENTER = FLOOR1_BOTTOM + FLOOR_THICK / 2.0
ROOF_CENTER = ROOF_BEAM_LEVEL + ROOF_THICK / 2.0

# Beam levels (centres)
FLOOR0_BEAMS_Z = FLOOR0_BOTTOM - BEAM_SECTION / 2.0
FLOOR1_BEAMS_Z = FLOOR1_BOTTOM - BEAM_SECTION / 2.0
ROOF_BEAMS_Z = ROOF_BEAM_LEVEL - BEAM_SECTION / 2.0

# For splitting slabs
X_MID = Lx / 2.0

# ------------------------------------------------------------------
# WALL OPENINGS (by bay index)
# We treat each facade by module bay and skip panels for openings.

# Ground-floor door bays (full bay opening)
GROUND_DOORS = {
    "E": [1],  # central bay on east facade (j index)
}

# Ground-floor window bays (full bay opening)
GROUND_WINDOWS = {
    "S": [2, 5],  # two windows on south facade (i indices)
}

# Upper-floor window bays (full bay opening)
UPPER_WINDOWS = {
    "E": [1],        # large window over door
    "S": [2, 5],     # windows aligned with ground-floor ones
}


# ------------------------------------------------------------------
# HELPER: create axis-aligned box by center + size

def make_box(name, center, size):
    """
    Wrapper around craftbot.place_element() to create a box with
    size (sx, sy, sz) centred at (cx, cy, cz).
    """
    cx, cy, cz = center
    sx, sy, sz = size

    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(sx / 2.0, sy / 2.0, sz / 2.0),
    )


# ------------------------------------------------------------------
# 1. POSTS

def build_posts():
    """
    Place posts at all grid intersections (including middle).
    """
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY + 1):
            y = j * MODULE
            z_center = POST_HEIGHT / 2.0
            make_box(
                name=f"Post_{i}_{j}",
                center=(x, y, z_center),
                size=(POST_SECTION, POST_SECTION, POST_HEIGHT),
            )


# ------------------------------------------------------------------
# 2. BEAMS (trimmed to posts)

def build_beam_layer(z_center, label):
    """
    Create a full tartan of beams at height z_center.
    Beams are trimmed so they stop at the inner faces of the posts.
    """
    # Effective span between inner faces of posts
    span = MODULE - POST_SECTION

    # X-direction beams (span between posts along X)
    for j in range(NY + 1):
        y = j * MODULE
        for i in range(NX):
            x0 = i * MODULE
            cx = x0 + MODULE / 2.0
            make_box(
                name=f"BeamX_{label}_{i}_{j}",
                center=(cx, y, z_center),
                size=(span, BEAM_SECTION, BEAM_SECTION),
            )

    # Y-direction beams (span between posts along Y)
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY):
            y0 = j * MODULE
            cy = y0 + MODULE / 2.0
            make_box(
                name=f"BeamY_{label}_{i}_{j}",
                center=(x, cy, z_center),
                size=(BEAM_SECTION, span, BEAM_SECTION),
            )


def build_all_beams():
    # Ground floor supporting beams
    build_beam_layer(FLOOR0_BEAMS_Z, "FL0")

    # Upper floor supporting beams
    build_beam_layer(FLOOR1_BEAMS_Z, "FL1")

    # Roof beams
    build_beam_layer(ROOF_BEAMS_Z, "ROOF")


# ------------------------------------------------------------------
# 3. FLOORS

def build_floor0():
    """
    Ground floor deck covering the entire footprint.
    """
    make_box(
        name="Floor0_Deck",
        center=(Lx / 2.0, Ly / 2.0, FLOOR0_CENTER),
        size=(Lx, Ly, FLOOR_THICK),
    )


def build_floor1():
    """
    Upper floor deck split into two halves along X.
    One half is omitted to create the double-height volume.
    """
    half_len = Lx / 2.0

    # West half
    if VOID_SIDE != "W":
        make_box(
            name="Floor1_Deck_W",
            center=(half_len / 2.0, Ly / 2.0, FLOOR1_CENTER),
            size=(half_len, Ly, FLOOR_THICK),
        )

    # East half
    if VOID_SIDE != "E":
        make_box(
            name="Floor1_Deck_E",
            center=(half_len + half_len / 2.0, Ly / 2.0, FLOOR1_CENTER),
            size=(half_len, Ly, FLOOR_THICK),
        )


# ------------------------------------------------------------------
# 4. ROOF (split in two halves)

def build_roof():
    """
    Flat roof slab split into two halves along X.
    The half above the double-height void is omitted.
    """
    half_len = Lx / 2.0

    # West half
    if VOID_SIDE != "W":
        make_box(
            name="RoofDeck_W",
            center=(half_len / 2.0, Ly / 2.0, ROOF_CENTER),
            size=(half_len, Ly, ROOF_THICK),
        )

    # East half
    if VOID_SIDE != "E":
        make_box(
            name="RoofDeck_E",
            center=(half_len + half_len / 2.0, Ly / 2.0, ROOF_CENTER),
            size=(half_len, Ly, ROOF_THICK),
        )


# ------------------------------------------------------------------
# 5. EXTERNAL WALLS WITH OPENINGS

def build_walls():
    """
    External walls split by storey, with bay-sized openings for
    door and windows. Openings are implemented simply by omitting
    panels in the corresponding bays.
    """

    # lower storey: from top of ground floor deck to underside of upper floor
    lower_z_bottom = FLOOR0_BOTTOM + FLOOR_THICK
    lower_z_top = FLOOR1_BOTTOM
    h_lower = lower_z_top - lower_z_bottom
    lower_z_center = lower_z_bottom + h_lower / 2.0

    # upper storey: from top of upper floor deck to underside of roof beams
    upper_z_bottom = FLOOR1_BOTTOM + FLOOR_THICK
    upper_z_top = ROOF_BEAM_LEVEL
    h_upper = upper_z_top - upper_z_bottom
    upper_z_center = upper_z_bottom + h_upper / 2.0

    # SOUTH and NORTH facades (vary along X)
    for side, y in (("S", 0.0), ("N", Ly)):
        for i in range(NX):
            cx = (i + 0.5) * MODULE

            # Ground-storey panel (skip bays with doors/windows)
            if i not in GROUND_DOORS.get(side, []) and i not in GROUND_WINDOWS.get(side, []):
                make_box(
                    name=f"Wall_{side}_G_{i}",
                    center=(cx, y, lower_z_center),
                    size=(MODULE, WALL_THICK, h_lower),
                )

            # Upper-storey panel (skip window bays)
            if i not in UPPER_WINDOWS.get(side, []):
                make_box(
                    name=f"Wall_{side}_U_{i}",
                    center=(cx, y, upper_z_center),
                    size=(MODULE, WALL_THICK, h_upper),
                )

    # WEST and EAST facades (vary along Y)
    for side, x in (("W", 0.0), ("E", Lx)):
        for j in range(NY):
            cy = (j + 0.5) * MODULE

            # Ground-storey panel
            if j not in GROUND_DOORS.get(side, []) and j not in GROUND_WINDOWS.get(side, []):
                make_box(
                    name=f"Wall_{side}_G_{j}",
                    center=(x, cy, lower_z_center),
                    size=(WALL_THICK, MODULE, h_lower),
                )

            # Upper-storey panel
            if j not in UPPER_WINDOWS.get(side, []):
                make_box(
                    name=f"Wall_{side}_U_{j}",
                    center=(x, cy, upper_z_center),
                    size=(WALL_THICK, MODULE, h_upper),
                )


# ------------------------------------------------------------------
# 6. STAIRCASE (rotated 180° in XY)

def build_staircase():
    """
    Straight stair from ground floor to upper floor, placed in the
    double-height zone on the east side. After building the run,
    the stair is rotated 180 degrees in the XY plane by mirroring
    each step about the run's centre.
    """

    # Vertical: from top of ground floor to top of upper floor deck
    z0 = FLOOR0_BOTTOM + FLOOR_THICK          # top of ground floor deck
    z_top_floor1 = FLOOR1_BOTTOM + FLOOR_THICK
    total_rise = z_top_floor1 - z0

    step_rise = total_rise / N_STEPS
    step_depth = STAIR_RUN / N_STEPS

    # Place stair rectangle in east half, centred in Y
    x_start = X_MID + (Lx / 2.0 - STAIR_RUN) / 2.0
    x_end = x_start + STAIR_RUN
    x_center_run = (x_start + x_end) / 2.0

    y_center = Ly / 2.0

    for n in range(N_STEPS):
        # original (unrotated) position
        x0 = x_start + n * step_depth
        z_base = z0 + n * step_rise

        # compute centre before rotation
        cx_old = x0 + step_depth / 2.0

        # 180-degree rotation about run centre in XY:
        # x -> 2 * x_center_run - x
        cx_new = 2.0 * x_center_run - cx_old
        x0_rot = cx_new - step_depth / 2.0

        cz = z_base + step_rise / 2.0

        make_box(
            name=f"StairStep_{n:02d}",
            center=(x0_rot + step_depth / 2.0, y_center, cz),
            size=(step_depth, STAIR_WIDTH, step_rise),
        )


# ------------------------------------------------------------------
# MAIN ENTRY POINT

def build_unit():
    build_posts()
    build_all_beams()
    build_floor0()
    build_floor1()
    build_roof()
    build_walls()
    build_staircase()


if __name__ == "__main__":
    build_unit()
