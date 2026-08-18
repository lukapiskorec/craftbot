# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 08 - CHATGPT 5.1 - V05
# THE SEGAL METHOD
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot

importlib.reload(craftbot)


# ------------------------------------------------------------------
# COLLECTION SETUP

STRUCT_COLL_NAME = "Structure"
WALL_COLL_NAME = "WallPanels"

STRUCT_COLL = None
WALL_COLL = None


def ensure_collections():
    """Create or fetch collections for structure and wall panels."""
    global STRUCT_COLL, WALL_COLL

    scene = bpy.context.scene

    STRUCT_COLL = bpy.data.collections.get(STRUCT_COLL_NAME)
    if STRUCT_COLL is None:
        STRUCT_COLL = bpy.data.collections.new(STRUCT_COLL_NAME)
        scene.collection.children.link(STRUCT_COLL)

    WALL_COLL = bpy.data.collections.get(WALL_COLL_NAME)
    if WALL_COLL is None:
        WALL_COLL = bpy.data.collections.new(WALL_COLL_NAME)
        scene.collection.children.link(WALL_COLL)


# ------------------------------------------------------------------
# PARAMETERS

# Modular grid
MODULE = 1.2          # 1.2 m module
NX = 8                # bays in X
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

# Wall build-up
PANEL_THICK = 0.02    # thickness of inner/outer sheathing panels

# Stair parameters
N_STEPS = 12
# width sized to clear inner column line, flush to north inner wall
STAIR_WIDTH = MODULE - POST_SECTION - PANEL_THICK
STAIR_RUN = MODULE * 3.0  # horizontal run of stair

# Double-height configuration
VOID_SIDE = "E"       # remove upper floor + roof on east half


# ------------------------------------------------------------------
# DERIVED DIMENSIONS

Lx = NX * MODULE      # overall length (X)
Ly = NY * MODULE      # overall width (Y)

# Vertical levels
POST_HEIGHT = FLOOR_ELEV + N_STOREYS * STOREY_HEIGHT      # top of posts
ROOF_BEAM_LEVEL = POST_HEIGHT                             # where roof beams sit

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

# Ground-floor door bays (full bay opening)
GROUND_DOORS = {
    "E": [1],  # door on east facade in middle Y-bay
}

# Ground-floor windows
GROUND_WINDOWS = {
    "S": [2, 5],
    "W": [1],  # new opening west middle
}

# Upper-floor windows
UPPER_WINDOWS = {
    "E": [1],
    "S": [2, 5],
    "W": [1],  # new opening west middle
}


# ------------------------------------------------------------------
# HELPER: create axis-aligned box by center + size into a collection

def make_box(name, center, size, coll_kind="structure"):
    """
    Wrapper around craftbot.place_element() to create a box with
    size (sx, sy, sz) centred at (cx, cy, cz), and move it into
    either the structure or wall-panels collection.
    """
    if coll_kind == "walls":
        coll = WALL_COLL
    else:
        coll = STRUCT_COLL

    cx, cy, cz = center
    sx, sy, sz = size

    obj = craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(sx / 2.0, sy / 2.0, sz / 2.0),
    )

    if coll is not None:
        # Link object to desired collection and unlink from others
        for c in list(obj.users_collection):
            if c != coll:
                c.objects.unlink(obj)
        if obj.name not in coll.objects:
            coll.objects.link(obj)

    return obj


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
                coll_kind="structure",
            )


# ------------------------------------------------------------------
# 2. BEAMS (trimmed to posts, with local omissions for stair headroom)

def build_beam_layer(z_center, label):
    """
    Create a full tartan of beams at height z_center.
    Beams are trimmed so they stop at the inner faces of the posts.
    Some beams on the upper floor are omitted to clear the stair.
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
                coll_kind="structure",
            )

    # Y-direction beams (span between posts along Y)
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY):
            # For upper floor, remove beams over the stair in bay j=2 (north-middle)
            if label == "FL1" and j == 2 and i in (5, 6):
                continue

            y0 = j * MODULE
            cy = y0 + MODULE / 2.0

            make_box(
                name=f"BeamY_{label}_{i}_{j}",
                center=(x, cy, z_center),
                size=(BEAM_SECTION, span, BEAM_SECTION),
                coll_kind="structure",
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
    Ground floor deck covering the footprint to the outer faces of
    posts/beams, stopping before the outer wall panels.
    """
    make_box(
        name="Floor0_Deck",
        center=(Lx / 2.0, Ly / 2.0, FLOOR0_CENTER),
        size=(Lx + POST_SECTION, Ly + POST_SECTION, FLOOR_THICK),
        coll_kind="structure",
    )


def build_floor1():
    """
    Upper floor deck on the west half only (east half is double-height),
    extended to outer faces of posts/beams.
    """
    half_len = Lx / 2.0  # X_MID

    # West half extents from -POST/2 to X_MID + POST/2
    sx = half_len + POST_SECTION
    cx = (-POST_SECTION / 2.0 + half_len + POST_SECTION / 2.0) / 2.0  # = half_len / 2

    make_box(
        name="Floor1_Deck_W",
        center=(cx, Ly / 2.0, FLOOR1_CENTER),
        size=(sx, Ly + POST_SECTION, FLOOR_THICK),
        coll_kind="structure",
    )


# ------------------------------------------------------------------
# 4. ROOF (split in two halves, but only west half kept above void)

def build_roof():
    """
    Flat roof slab over the west half, extended to the outer faces
    of posts/beams and stopping before the outer wall panels.
    """
    half_len = Lx / 2.0  # X_MID

    sx = half_len + POST_SECTION
    cx = (-POST_SECTION / 2.0 + half_len + POST_SECTION / 2.0) / 2.0

    make_box(
        name="RoofDeck_W",
        center=(cx, Ly / 2.0, ROOF_CENTER),
        size=(sx, Ly + POST_SECTION, ROOF_THICK),
        coll_kind="structure",
    )


# ------------------------------------------------------------------
# 5. EXTERNAL WALLS WITH INNER/OUTER PANELS AND CAVITY

def build_walls():
    """
    External walls split into inner and outer panels, creating an
    empty cavity between them. Outer panels are extended vertically
    so they cover the zones where floor/ceiling slabs occur.
    In the double-height zone (east half) inner panels are continuous
    over both storeys, closing the gap where the slab would be.
    """

    # Inner lower storey
    lower_inner_z_bottom = FLOOR0_BOTTOM + FLOOR_THICK
    lower_inner_z_top = FLOOR1_BOTTOM
    h_lower_inner = lower_inner_z_top - lower_inner_z_bottom
    z_lower_inner = lower_inner_z_bottom + h_lower_inner / 2.0

    # Inner upper storey
    upper_inner_z_bottom = FLOOR1_BOTTOM + FLOOR_THICK
    upper_inner_z_top = ROOF_BEAM_LEVEL
    h_upper_inner = upper_inner_z_top - upper_inner_z_bottom
    z_upper_inner = upper_inner_z_bottom + h_upper_inner / 2.0

    # Combined inner height (for double-height zone)
    total_inner_h = upper_inner_z_top - lower_inner_z_bottom
    z_inner_total = (lower_inner_z_bottom + upper_inner_z_top) / 2.0

    # Outer lower
    lower_outer_z_bottom = FLOOR0_BOTTOM
    lower_outer_z_top = FLOOR1_BOTTOM
    h_lower_outer = lower_outer_z_top - lower_outer_z_bottom
    z_lower_outer = lower_outer_z_bottom + h_lower_outer / 2.0

    # Outer upper
    upper_outer_z_bottom = FLOOR1_BOTTOM
    upper_outer_z_top = ROOF_BEAM_LEVEL
    h_upper_outer = upper_outer_z_top - upper_outer_z_bottom
    z_upper_outer = upper_outer_z_bottom + h_upper_outer / 2.0

    # SOUTH and NORTH facades (vary along X)
    for side, y_base in (("S", 0.0), ("N", Ly)):
        # Positions of inner and outer panels in Y
        if side == "S":
            y_inner = y_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0
            y_outer = y_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
        else:  # "N"
            y_inner = y_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
            y_outer = y_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0

        for i in range(NX):
            cx = (i + 0.5) * MODULE

            has_door = i in GROUND_DOORS.get(side, [])
            has_gwin = i in GROUND_WINDOWS.get(side, [])
            has_uwin = i in UPPER_WINDOWS.get(side, [])

            in_void = (i >= NX // 2)  # east half bays only

            # --- INNER PANELS ---
            if in_void and not (has_door or has_gwin or has_uwin):
                # single tall inner panel for double-height zone
                make_box(
                    name=f"Wall_{side}_Inner_DH_{i}",
                    center=(cx, y_inner, z_inner_total),
                    size=(MODULE, PANEL_THICK, total_inner_h),
                    coll_kind="walls",
                )
            else:
                # ground storey inner
                if not (has_door or has_gwin):
                    make_box(
                        name=f"Wall_{side}_Inner_G_{i}",
                        center=(cx, y_inner, z_lower_inner),
                        size=(MODULE, PANEL_THICK, h_lower_inner),
                        coll_kind="walls",
                    )
                # upper storey inner
                if not has_uwin:
                    make_box(
                        name=f"Wall_{side}_Inner_U_{i}",
                        center=(cx, y_inner, z_upper_inner),
                        size=(MODULE, PANEL_THICK, h_upper_inner),
                        coll_kind="walls",
                    )

            # --- OUTER PANELS (always split) ---
            if not (has_door or has_gwin):
                make_box(
                    name=f"Wall_{side}_Outer_G_{i}",
                    center=(cx, y_outer, z_lower_outer),
                    size=(MODULE, PANEL_THICK, h_lower_outer),
                    coll_kind="walls",
                )

            if not has_uwin:
                make_box(
                    name=f"Wall_{side}_Outer_U_{i}",
                    center=(cx, y_outer, z_upper_outer),
                    size=(MODULE, PANEL_THICK, h_upper_outer),
                    coll_kind="walls",
                )

    # WEST and EAST facades (vary along Y)
    for side, x_base in (("W", 0.0), ("E", Lx)):
        if side == "W":
            x_inner = x_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0
            x_outer = x_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
        else:  # "E"
            x_inner = x_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
            x_outer = x_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0

        for j in range(NY):
            cy = (j + 0.5) * MODULE

            has_door = j in GROUND_DOORS.get(side, [])
            has_gwin = j in GROUND_WINDOWS.get(side, [])
            has_uwin = j in UPPER_WINDOWS.get(side, [])

            in_void = (side == "E")  # entire east facade is double-height

            # --- INNER PANELS ---
            if in_void and not (has_door or has_gwin or has_uwin):
                make_box(
                    name=f"Wall_{side}_Inner_DH_{j}",
                    center=(x_inner, cy, z_inner_total),
                    size=(PANEL_THICK, MODULE, total_inner_h),
                    coll_kind="walls",
                )
            else:
                if not (has_door or has_gwin):
                    make_box(
                        name=f"Wall_{side}_Inner_G_{j}",
                        center=(x_inner, cy, z_lower_inner),
                        size=(PANEL_THICK, MODULE, h_lower_inner),
                        coll_kind="walls",
                    )

                if not has_uwin:
                    make_box(
                        name=f"Wall_{side}_Inner_U_{j}",
                        center=(x_inner, cy, z_upper_inner),
                        size=(PANEL_THICK, MODULE, h_upper_inner),
                        coll_kind="walls",
                    )

            # --- OUTER PANELS ---
            if not (has_door or has_gwin):
                make_box(
                    name=f"Wall_{side}_Outer_G_{j}",
                    center=(x_outer, cy, z_lower_outer),
                    size=(PANEL_THICK, MODULE, h_lower_outer),
                    coll_kind="walls",
                )

            if not has_uwin:
                make_box(
                    name=f"Wall_{side}_Outer_U_{j}",
                    center=(x_outer, cy, z_upper_outer),
                    size=(PANEL_THICK, MODULE, h_upper_outer),
                    coll_kind="walls",
                )


# ------------------------------------------------------------------
# 6. STAIRCASE (shifted in -X and up against north wall, narrower)

def build_staircase():
    """
    Straight stair from ground floor to upper floor, placed in the
    double-height zone on the east side, shifted towards -X so that
    the top step connects correctly with the upper floor deck and
    positioned against the north wall. Width is reduced so it fits
    between the columns without intersecting them.
    """

    # Vertical: from top of ground floor deck to top of upper floor deck
    z0 = FLOOR0_BOTTOM + FLOOR_THICK
    z_top = FLOOR1_BOTTOM + FLOOR_THICK
    total_rise = z_top - z0

    step_rise = total_rise / N_STEPS
    step_depth = STAIR_RUN / N_STEPS

    # Run from east towards west: bottom at higher X, top at lower X.
    top_x = X_MID                    # near edge of upper floor
    bottom_x = X_MID + STAIR_RUN     # in the open double-height half

    # Y-position: against inside face of the north inner wall
    inner_face_y = Ly - POST_SECTION / 2.0 - PANEL_THICK
    y_center = inner_face_y - STAIR_WIDTH / 2.0

    for n in range(N_STEPS):
        cx = bottom_x - (n + 0.5) * step_depth
        cz = z0 + (n + 0.5) * step_rise

        make_box(
            name=f"StairStep_{n:02d}",
            center=(cx, y_center, cz),
            size=(step_depth, STAIR_WIDTH, step_rise),
            coll_kind="structure",
        )


# ------------------------------------------------------------------
# MAIN ENTRY POINT

def build_unit():
    ensure_collections()
    build_posts()
    build_all_beams()
    build_floor0()
    build_floor1()
    build_roof()
    build_walls()
    build_staircase()


if __name__ == "__main__":
    build_unit()
