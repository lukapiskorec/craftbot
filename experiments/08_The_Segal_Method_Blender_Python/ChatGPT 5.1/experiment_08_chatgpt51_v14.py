# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 08 - CHATGPT 5.1 - V14
# THE SEGAL METHOD
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot

importlib.reload(craftbot)


# ------------------------------------------------------------------
# COLLECTION SETUP

STRUCT_COLL_NAME = "Structure"
WALL_COLL_NAME = "WallPanels"
SLAT_COLL_NAME = "WallSlats"

STRUCT_COLL = None
WALL_COLL = None
SLAT_COLL = None


def ensure_collections():
    """Create or fetch collections for structure, wall panels, and slats."""
    global STRUCT_COLL, WALL_COLL, SLAT_COLL

    scene = bpy.context.scene

    STRUCT_COLL = bpy.data.collections.get(STRUCT_COLL_NAME)
    if STRUCT_COLL is None:
        STRUCT_COLL = bpy.data.collections.new(STRUCT_COLL_NAME)
        scene.collection.children.link(STRUCT_COLL)

    WALL_COLL = bpy.data.collections.get(WALL_COLL_NAME)
    if WALL_COLL is None:
        WALL_COLL = bpy.data.collections.new(WALL_COLL_NAME)
        scene.collection.children.link(WALL_COLL)

    SLAT_COLL = bpy.data.collections.get(SLAT_COLL_NAME)
    if SLAT_COLL is None:
        SLAT_COLL = bpy.data.collections.new(SLAT_COLL_NAME)
        scene.collection.children.link(SLAT_COLL)


# ------------------------------------------------------------------
# PARAMETERS

# Modular grid
MODULE = 1.2          # 1.2 m module
NX = 8                # bays in X
NY = 3                # bays in Y

# Storeys / levels
STOREY_HEIGHT = 2.4   # floor-to-floor
FLOOR_ELEV = 0.6      # bottom of ground floor deck above ground
FLOOR_THICK = 0.2     # floor slab thickness
ROOF_THICK = 0.2      # flat roof slab thickness

# Timber section sizes
POST_SECTION = 0.10   # 100 x 100 mm posts
BEAM_WIDTH = 0.10     # beam width in plan
BEAM_HEIGHT = 0.20    # beam depth (height) – twice the width

# Wall build-up
PANEL_THICK = 0.02    # thickness of inner/outer sheathing panels

# Stair parameters
N_STEPS = 12
STAIR_WIDTH = MODULE - POST_SECTION - PANEL_THICK
STAIR_RUN = MODULE * 3.0

# Window / door framing
FRAME_MARGIN = 0.05   # lateral margin from bay edges
FRAME_THICK = 0.04    # bar width in plane
FRAME_DEPTH = 0.03    # bar depth normal to wall

WINDOW_SILL_CLEAR = 0.0             # sill exactly on the floor
WINDOW_HEAD_CLEAR = -FRAME_THICK/2  # head touches underside of beam

DOOR_SILL_CLEAR = 0.0
DOOR_HEAD_CLEAR = 0.02

# Slatted cladding
SLAT_HEIGHT = 0.10
SLAT_GAP = 0.0

# Skylight / roof over double-height space
SKY_SLOPE_DEG = 15.0
SKY_ROOF_THICK = 0.05
SKY_RAFTER_WIDTH = 0.05
SKY_RAFTER_HEIGHT = 0.15
SKY_OVERHANG = 0.25
SKY_NORTH_BEAM_FACTOR = 1.0  # depth factor so north beam matches 2:1 proportion
SKY_SOUTH_BEAM_H = BEAM_WIDTH  # square south beam, sitting on wall


# ------------------------------------------------------------------
# DERIVED DIMENSIONS

Lx = NX * MODULE      # overall length (X)
Ly = NY * MODULE      # overall width (Y)
X_MID = Lx / 2.0

# Vertical levels
POST_HEIGHT = FLOOR_ELEV + 2 * STOREY_HEIGHT
ROOF_BEAM_LEVEL = POST_HEIGHT

FLOOR0_BOTTOM = FLOOR_ELEV
FLOOR1_BOTTOM = FLOOR_ELEV + STOREY_HEIGHT

FLOOR0_CENTER = FLOOR0_BOTTOM + FLOOR_THICK / 2.0
FLOOR1_CENTER = FLOOR1_BOTTOM + FLOOR_THICK / 2.0
ROOF_CENTER = ROOF_BEAM_LEVEL + ROOF_THICK / 2.0

# Beam levels (centres) – tops flush with slab undersides
FLOOR0_BEAMS_Z = FLOOR0_BOTTOM - BEAM_HEIGHT / 2.0
FLOOR1_BEAMS_Z = FLOOR1_BOTTOM - BEAM_HEIGHT / 2.0
ROOF_BEAMS_Z = ROOF_BEAM_LEVEL - BEAM_HEIGHT / 2.0

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
    "W": [1],  # opening west middle
}

# Upper-floor windows
UPPER_WINDOWS = {
    "E": [1],
    "S": [2, 5],
    "W": [1],  # opening west middle
}


# ------------------------------------------------------------------
# HELPER: create box into a collection

def make_box(name, center, size, coll_kind="structure", euler=None):
    """
    Wrapper around craftbot.place_element() to create a box with
    size (sx, sy, sz) centred at (cx, cy, cz), and move it into
    the appropriate collection. Optional `euler` (radians).
    """
    if coll_kind == "walls":
        coll = WALL_COLL
    elif coll_kind == "slats":
        coll = SLAT_COLL
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
        euler=euler,
        euler_order='XYZ',
        matrix=None,
    )

    if coll is not None:
        for c in list(obj.users_collection):
            if c != coll:
                c.objects.unlink(obj)
        if obj.name not in coll.objects:
            coll.objects.link(obj)

    return obj


# ------------------------------------------------------------------
# 1. POSTS

def build_posts():
    """Place posts at all grid intersections (including middle)."""
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
    span = MODULE - POST_SECTION  # clear span between inner faces of posts

    # X-direction beams
    for j in range(NY + 1):
        y = j * MODULE
        for i in range(NX):
            x0 = i * MODULE
            cx = x0 + MODULE / 2.0
            make_box(
                name=f"BeamX_{label}_{i}_{j}",
                center=(cx, y, z_center),
                size=(span, BEAM_WIDTH, BEAM_HEIGHT),
                coll_kind="structure",
            )

    # Y-direction beams
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY):
            # Remove two beams above stair head on upper floor
            if label == "FL1" and j == 2 and i in (5, 6):
                continue
            y0 = j * MODULE
            cy = y0 + MODULE / 2.0
            make_box(
                name=f"BeamY_{label}_{i}_{j}",
                center=(x, cy, z_center),
                size=(BEAM_WIDTH, span, BEAM_HEIGHT),
                coll_kind="structure",
            )


def build_all_beams():
    build_beam_layer(FLOOR0_BEAMS_Z, "FL0")
    build_beam_layer(FLOOR1_BEAMS_Z, "FL1")
    build_beam_layer(ROOF_BEAMS_Z, "ROOF")


# ------------------------------------------------------------------
# 3. FLOORS & ROOF

def build_floor0():
    """Ground floor deck to outer faces of structure."""
    make_box(
        name="Floor0_Deck",
        center=(Lx / 2.0, Ly / 2.0, FLOOR0_CENTER),
        size=(Lx + POST_SECTION, Ly + POST_SECTION, FLOOR_THICK),
        coll_kind="structure",
    )


def build_floor1():
    """Upper floor deck on west half only (east half double-height)."""
    half_len = Lx / 2.0
    sx = half_len + POST_SECTION
    cx = half_len / 2.0
    make_box(
        name="Floor1_Deck_W",
        center=(cx, Ly / 2.0, FLOOR1_CENTER),
        size=(sx, Ly + POST_SECTION, FLOOR_THICK),
        coll_kind="structure",
    )


def build_roof():
    """Flat roof over west half, to outer faces of structure."""
    half_len = Lx / 2.0
    sx = half_len + POST_SECTION
    cx = half_len / 2.0
    make_box(
        name="RoofDeck_W",
        center=(cx, Ly / 2.0, ROOF_CENTER),
        size=(sx, Ly + POST_SECTION, ROOF_THICK),
        coll_kind="structure",
    )


# ------------------------------------------------------------------
# 4. SLAT HELPERS

def build_slats_sn(name_prefix, cx, y, z_bottom, z_top, span):
    """Horizontal slats for S/N facades (span along X)."""
    h = z_top - z_bottom
    if h <= 0:
        return
    step = SLAT_HEIGHT + SLAT_GAP
    k = 0
    while True:
        z0 = z_bottom + k * step
        if z0 + SLAT_HEIGHT > z_top + 1e-6:
            break
        zc = z0 + SLAT_HEIGHT / 2.0
        make_box(
            name=f"{name_prefix}_slat_{k}",
            center=(cx, y, zc),
            size=(span, PANEL_THICK, SLAT_HEIGHT),
            coll_kind="slats",
        )
        k += 1


def build_slats_ew(name_prefix, x, cy, z_bottom, z_top, span):
    """Horizontal slats for E/W facades (span along Y)."""
    h = z_top - z_bottom
    if h <= 0:
        return
    step = SLAT_HEIGHT + SLAT_GAP
    k = 0
    while True:
        z0 = z_bottom + k * step
        if z0 + SLAT_HEIGHT > z_top + 1e-6:
            break
        zc = z0 + SLAT_HEIGHT / 2.0
        make_box(
            name=f"{name_prefix}_slat_{k}",
            center=(x, cy, zc),
            size=(PANEL_THICK, span, SLAT_HEIGHT),
            coll_kind="slats",
        )
        k += 1


# ------------------------------------------------------------------
# 5. EXTERNAL WALLS WITH INNER/OUTER PANELS + SLATS

def build_walls():
    """
    External walls split into inner and outer panels, creating an
    empty cavity between them. Outer panels on ground and upper
    storeys meet exactly at FLOOR1_BOTTOM (no overlap).
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

    # Combined inner height (for double-height zones with no slab)
    total_inner_h = upper_inner_z_top - lower_inner_z_bottom
    z_inner_total = (lower_inner_z_bottom + upper_inner_z_top) / 2.0

    # Outer lower – from ground to first-floor level
    lower_outer_z_bottom = FLOOR0_BOTTOM
    lower_outer_z_top = FLOOR1_BOTTOM
    h_lower_outer = lower_outer_z_top - lower_outer_z_bottom
    z_lower_outer = lower_outer_z_bottom + h_lower_outer / 2.0

    # Outer upper – from first-floor level to above roof beams
    upper_outer_z_bottom = FLOOR1_BOTTOM
    upper_outer_z_top = ROOF_BEAM_LEVEL + BEAM_HEIGHT / 2.0
    h_upper_outer = upper_outer_z_top - upper_outer_z_bottom
    z_upper_outer = upper_outer_z_bottom + h_upper_outer / 2.0

    # SOUTH and NORTH facades (vary along X)
    for side, y_base in (("S", 0.0), ("N", Ly)):
        if side == "S":
            y_inner = y_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0
            y_outer = y_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
        else:
            y_inner = y_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
            y_outer = y_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0

        for i in range(NX):
            cx = (i + 0.5) * MODULE
            has_door = i in GROUND_DOORS.get(side, [])
            has_gwin = i in GROUND_WINDOWS.get(side, [])
            has_uwin = i in UPPER_WINDOWS.get(side, [])
            in_void = (i >= NX // 2)  # east half bays structurally double-height

            # --- INNER PANELS ---
            if in_void and not (has_door or has_gwin or has_uwin):
                # Single double-height inner panel (no openings)
                make_box(
                    name=f"Wall_{side}_Inner_DH_{i}",
                    center=(cx, y_inner, z_inner_total),
                    size=(MODULE, PANEL_THICK, total_inner_h),
                    coll_kind="walls",
                )
                build_slats_sn(
                    f"Slat_{side}_Inner_DH_{i}",
                    cx,
                    y_inner,
                    lower_inner_z_bottom,
                    upper_inner_z_top,
                    MODULE,
                )
            else:
                # Ground storey inner
                if not (has_door or has_gwin):
                    make_box(
                        name=f"Wall_{side}_Inner_G_{i}",
                        center=(cx, y_inner, z_lower_inner),
                        size=(MODULE, PANEL_THICK, h_lower_inner),
                        coll_kind="walls",
                    )
                    build_slats_sn(
                        f"Slat_{side}_Inner_G_{i}",
                        cx,
                        y_inner,
                        lower_inner_z_bottom,
                        lower_inner_z_top,
                        MODULE,
                    )
                # Upper storey inner
                if not has_uwin:
                    make_box(
                        name=f"Wall_{side}_Inner_U_{i}",
                        center=(cx, y_inner, z_upper_inner),
                        size=(MODULE, PANEL_THICK, h_upper_inner),
                        coll_kind="walls",
                    )
                    build_slats_sn(
                        f"Slat_{side}_Inner_U_{i}",
                        cx,
                        y_inner,
                        upper_inner_z_bottom,
                        upper_inner_z_top,
                        MODULE,
                    )

            # --- OUTER PANELS + SLATS ---
            if not (has_door or has_gwin):
                make_box(
                    name=f"Wall_{side}_Outer_G_{i}",
                    center=(cx, y_outer, z_lower_outer),
                    size=(MODULE, PANEL_THICK, h_lower_outer),
                    coll_kind="walls",
                )
                build_slats_sn(
                    f"Slat_{side}_Outer_G_{i}",
                    cx,
                    y_outer,
                    lower_outer_z_bottom,
                    lower_outer_z_top,
                    MODULE,
                )

            if not has_uwin:
                make_box(
                    name=f"Wall_{side}_Outer_U_{i}",
                    center=(cx, y_outer, z_upper_outer),
                    size=(MODULE, PANEL_THICK, h_upper_outer),
                    coll_kind="walls",
                )
                build_slats_sn(
                    f"Slat_{side}_Outer_U_{i}",
                    cx,
                    y_outer,
                    upper_outer_z_bottom,
                    upper_outer_z_top,
                    MODULE,
                )

    # WEST and EAST facades (vary along Y)
    for side, x_base in (("W", 0.0), ("E", Lx)):
        if side == "W":
            x_inner = x_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0
            x_outer = x_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
        else:
            x_inner = x_base - POST_SECTION / 2.0 - PANEL_THICK / 2.0
            x_outer = x_base + POST_SECTION / 2.0 + PANEL_THICK / 2.0

        for j in range(NY):
            cy = (j + 0.5) * MODULE
            has_door = j in GROUND_DOORS.get(side, [])
            has_gwin = j in GROUND_WINDOWS.get(side, [])
            has_uwin = j in UPPER_WINDOWS.get(side, [])
            in_void = (side == "E")

            # --- INNER PANELS ---
            if in_void and not (has_door or has_gwin or has_uwin):
                make_box(
                    name=f"Wall_{side}_Inner_DH_{j}",
                    center=(x_inner, cy, z_inner_total),
                    size=(PANEL_THICK, MODULE, total_inner_h),
                    coll_kind="walls",
                )
                build_slats_ew(
                    f"Slat_{side}_Inner_DH_{j}",
                    x_inner,
                    cy,
                    lower_inner_z_bottom,
                    upper_inner_z_top,
                    MODULE,
                )
            else:
                if not (has_door or has_gwin):
                    make_box(
                        name=f"Wall_{side}_Inner_G_{j}",
                        center=(x_inner, cy, z_lower_inner),
                        size=(PANEL_THICK, MODULE, h_lower_inner),
                        coll_kind="walls",
                    )
                    build_slats_ew(
                        f"Slat_{side}_Inner_G_{j}",
                        x_inner,
                        cy,
                        lower_inner_z_bottom,
                        lower_inner_z_top,
                        MODULE,
                    )
                if not has_uwin:
                    make_box(
                        name=f"Wall_{side}_Inner_U_{j}",
                        center=(x_inner, cy, z_upper_inner),
                        size=(PANEL_THICK, MODULE, h_upper_inner),
                        coll_kind="walls",
                    )
                    build_slats_ew(
                        f"Slat_{side}_Inner_U_{j}",
                        x_inner,
                        cy,
                        upper_inner_z_bottom,
                        upper_inner_z_top,
                        MODULE,
                    )

            # --- OUTER PANELS + SLATS ---
            if not (has_door or has_gwin):
                make_box(
                    name=f"Wall_{side}_Outer_G_{j}",
                    center=(x_outer, cy, z_lower_outer),
                    size=(PANEL_THICK, MODULE, h_lower_outer),
                    coll_kind="walls",
                )
                build_slats_ew(
                    f"Slat_{side}_Outer_G_{j}",
                    x_outer,
                    cy,
                    lower_outer_z_bottom,
                    lower_outer_z_top,
                    MODULE,
                )

            if not has_uwin:
                make_box(
                    name=f"Wall_{side}_Outer_U_{j}",
                    center=(x_outer, cy, z_upper_outer),
                    size=(PANEL_THICK, MODULE, h_upper_outer),
                    coll_kind="walls",
                )
                build_slats_ew(
                    f"Slat_{side}_Outer_U_{j}",
                    x_outer,
                    cy,
                    upper_outer_z_bottom,
                    upper_outer_z_top,
                    MODULE,
                )


# ------------------------------------------------------------------
# 6. WINDOW / DOOR FRAMES (no glass)

def build_window_frames():
    """
    Adds timber frames and pane subdivisions in each opening.
    Frames are placed at the mid-plane between inner and outer panels
    (column line), with bottoms sitting on the floor and heads touching
    the beams above. The upper south window in the double-height bay
    is extended downward to cover the missing-slab gap.
    """

    lower_inner_z_bottom = FLOOR0_BOTTOM + FLOOR_THICK
    lower_inner_z_top = FLOOR1_BOTTOM
    upper_inner_z_bottom = FLOOR1_BOTTOM + FLOOR_THICK
    upper_inner_z_top = ROOF_BEAM_LEVEL

    # Beam undersides
    ground_head = FLOOR1_BOTTOM - BEAM_HEIGHT
    upper_head = ROOF_BEAM_LEVEL - BEAM_HEIGHT

    dh_bottom = lower_inner_z_bottom
    dh_top_eff = upper_head  # currently unused, but kept for clarity

    # SOUTH & NORTH (vary X)
    for side, y_base in (("S", 0.0), ("N", Ly)):
        y_mid = y_base

        for i in range(NX):
            cx = (i + 0.5) * MODULE
            has_door = i in GROUND_DOORS.get(side, [])
            has_gwin = i in GROUND_WINDOWS.get(side, [])
            has_uwin = i in UPPER_WINDOWS.get(side, [])
            in_dh = (i >= NX // 2)

            if has_door:
                add_door_frame_sn(
                    name_prefix=f"Door_{side}_G_{i}",
                    cx=cx,
                    y=y_mid,
                    z_bottom=lower_inner_z_bottom,
                    z_top=ground_head,
                )
            elif has_gwin:
                add_window_frame_sn(
                    name_prefix=f"Frame_{side}_G_{i}",
                    cx=cx,
                    y=y_mid,
                    z_bottom=lower_inner_z_bottom,
                    z_top=ground_head,
                )

            if has_uwin:
                # South upper window in double-height bay: extend down
                if side == "S" and in_dh:
                    zb = FLOOR1_BOTTOM   # top-of-beam level
                else:
                    zb = upper_inner_z_bottom
                add_window_frame_sn(
                    name_prefix=f"Frame_{side}_U_{i}",
                    cx=cx,
                    y=y_mid,
                    z_bottom=zb,
                    z_top=upper_head,
                )

    # WEST & EAST (vary Y)
    for side, x_base in (("W", 0.0), ("E", Lx)):
        x_mid = x_base

        for j in range(NY):
            cy = (j + 0.5) * MODULE
            in_dh = (side == "E")

            has_door = j in GROUND_DOORS.get(side, [])
            has_gwin = j in GROUND_WINDOWS.get(side, [])
            has_uwin = j in UPPER_WINDOWS.get(side, [])

            # Ground openings
            if has_door:
                add_door_frame_ew(
                    name_prefix=f"Door_{side}_G_{j}",
                    x=x_mid,
                    cy=cy,
                    z_bottom=lower_inner_z_bottom,
                    z_top=ground_head,
                )
            elif has_gwin:
                add_window_frame_ew(
                    name_prefix=f"Frame_{side}_G_{j}",
                    x=x_mid,
                    cy=cy,
                    z_bottom=lower_inner_z_bottom,
                    z_top=ground_head,
                )

            # Upper windows (taller on east in double-height zone)
            if has_uwin:
                if in_dh:
                    zb = FLOOR1_BOTTOM  # no slab, start at beam level
                else:
                    zb = upper_inner_z_bottom
                add_window_frame_ew(
                    name_prefix=f"Frame_{side}_U_{j}",
                    x=x_mid,
                    cy=cy,
                    z_bottom=zb,
                    z_top=upper_head,
                )


def _frame_dims(open_height, sill_clear, head_clear):
    """Compute frame height and base level from opening and clearances."""
    height = open_height - sill_clear - head_clear
    if height <= 0:
        return None, None
    z_base = sill_clear
    return height, z_base


def add_window_frame_sn(name_prefix, cx, y, z_bottom, z_top, transom_z=None):
    """Window frame for S/N facades (span along X), with mullions."""
    open_height = z_top - z_bottom
    height, local_base = _frame_dims(open_height, WINDOW_SILL_CLEAR, WINDOW_HEAD_CLEAR)
    if height is None:
        return
    z_base = z_bottom + local_base
    zc = z_base + height / 2.0

    width = MODULE - 2 * FRAME_MARGIN

    # Perimeter stiles
    sx = FRAME_THICK
    sy = FRAME_DEPTH
    sz = height

    left_cx = cx - width / 2.0 + FRAME_THICK / 2.0
    right_cx = cx + width / 2.0 - FRAME_THICK / 2.0
    make_box(f"{name_prefix}_stile_L", (left_cx, y, zc), (sx, sy, sz))
    make_box(f"{name_prefix}_stile_R", (right_cx, y, zc), (sx, sy, sz))

    # Top & bottom rails
    sx = width
    sy = FRAME_DEPTH
    sz = FRAME_THICK

    top_z = z_base + height - FRAME_THICK / 2.0
    bot_z = z_base + FRAME_THICK / 2.0
    make_box(f"{name_prefix}_rail_T", (cx, y, top_z), (sx, sy, sz))
    make_box(f"{name_prefix}_rail_B", (cx, y, bot_z), (sx, sy, sz))

    # Vertical mullions (2, creating 3 panes)
    sx = FRAME_THICK
    sy = FRAME_DEPTH
    sz = height
    for k, offset in enumerate((-width / 6.0, width / 6.0)):
        mx = cx + offset
        make_box(f"{name_prefix}_mullion_{k}", (mx, y, zc), (sx, sy, sz))

    # Horizontal transom
    sx = width
    sy = FRAME_DEPTH
    sz = FRAME_THICK
    tz = zc if transom_z is None else transom_z
    make_box(f"{name_prefix}_transom", (cx, y, tz), (sx, sy, sz))


def add_window_frame_ew(name_prefix, x, cy, z_bottom, z_top):
    """Window frame for E/W facades (span along Y), with mullions."""
    open_height = z_top - z_bottom
    height, local_base = _frame_dims(open_height, WINDOW_SILL_CLEAR, WINDOW_HEAD_CLEAR)
    if height is None:
        return
    z_base = z_bottom + local_base
    zc = z_base + height / 2.0

    width = MODULE - 2 * FRAME_MARGIN

    # Stiles (along Y)
    sx = FRAME_DEPTH
    sy = FRAME_THICK
    sz = height

    left_cy = cy - width / 2.0 + FRAME_THICK / 2.0
    right_cy = cy + width / 2.0 - FRAME_THICK / 2.0
    make_box(f"{name_prefix}_stile_L", (x, left_cy, zc), (sx, sy, sz))
    make_box(f"{name_prefix}_stile_R", (x, right_cy, zc), (sx, sy, sz))

    # Rails
    sx = FRAME_DEPTH
    sy = width
    sz = FRAME_THICK

    top_z = z_base + height - FRAME_THICK / 2.0
    bot_z = z_base + FRAME_THICK / 2.0
    make_box(f"{name_prefix}_rail_T", (x, cy, top_z), (sx, sy, sz))
    make_box(f"{name_prefix}_rail_B", (x, cy, bot_z), (sx, sy, sz))

    # Vertical mullions
    sx = FRAME_DEPTH
    sy = FRAME_THICK
    sz = height
    for k, offset in enumerate((-width / 6.0, width / 6.0)):
        my = cy + offset
        make_box(f"{name_prefix}_mullion_{k}", (x, my, zc), (sx, sy, sz))

    # Transom
    sx = FRAME_DEPTH
    sy = width
    sz = FRAME_THICK
    make_box(f"{name_prefix}_transom", (x, cy, zc), (sx, sy, sz))


def add_door_frame_sn(name_prefix, cx, y, z_bottom, z_top):
    """Door frame for S/N facades."""
    open_height = z_top - z_bottom
    height, local_base = _frame_dims(open_height, DOOR_SILL_CLEAR, DOOR_HEAD_CLEAR)
    if height is None:
        return
    z_base = z_bottom + local_base
    zc = z_base + height / 2.0

    width = MODULE - 2 * FRAME_MARGIN

    # Stiles
    sx = FRAME_THICK
    sy = FRAME_DEPTH
    sz = height

    left_cx = cx - width / 2.0 + FRAME_THICK / 2.0
    right_cx = cx + width / 2.0 - FRAME_THICK / 2.0
    make_box(f"{name_prefix}_stile_L", (left_cx, y, zc), (sx, sy, sz))
    make_box(f"{name_prefix}_stile_R", (right_cx, y, zc), (sx, sy, sz))

    # Rails
    sx = width
    sy = FRAME_DEPTH
    sz = FRAME_THICK

    top_z = z_base + height - FRAME_THICK / 2.0
    bot_z = z_base + FRAME_THICK / 2.0
    make_box(f"{name_prefix}_rail_T", (cx, y, top_z), (sx, sy, sz))
    make_box(f"{name_prefix}_rail_B", (cx, y, bot_z), (sx, sy, sz))


def add_door_frame_ew(name_prefix, x, cy, z_bottom, z_top):
    """Door frame for E/W facades."""
    open_height = z_top - z_bottom
    height, local_base = _frame_dims(open_height, DOOR_SILL_CLEAR, DOOR_HEAD_CLEAR)
    if height is None:
        return
    z_base = z_bottom + local_base
    zc = z_base + height / 2.0

    width = MODULE - 2 * FRAME_MARGIN

    # Stiles
    sx = FRAME_DEPTH
    sy = FRAME_THICK
    sz = height

    left_cy = cy - width / 2.0 + FRAME_THICK / 2.0
    right_cy = cy + width / 2.0 - FRAME_THICK / 2.0
    make_box(f"{name_prefix}_stile_L", (x, left_cy, zc), (sx, sy, sz))
    make_box(f"{name_prefix}_stile_R", (x, right_cy, zc), (sx, sy, sz))

    # Rails
    sx = FRAME_DEPTH
    sy = width
    sz = FRAME_THICK

    top_z = z_base + height - FRAME_THICK / 2.0
    bot_z = z_base + FRAME_THICK / 2.0
    make_box(f"{name_prefix}_rail_T", (x, cy, top_z), (sx, sy, sz))
    make_box(f"{name_prefix}_rail_B", (x, cy, bot_z), (sx, sy, sz))


# ------------------------------------------------------------------
# 7. STAIRCASE (INTERIOR)

def build_staircase():
    """
    Straight stair from ground floor to upper floor, placed in the
    double-height zone on the east side; top step connects with the
    upper floor deck and stair is tight against the north wall.
    """

    z0 = FLOOR0_BOTTOM + FLOOR_THICK
    z_top = FLOOR1_BOTTOM + FLOOR_THICK
    total_rise = z_top - z0

    step_rise = total_rise / N_STEPS
    step_depth = STAIR_RUN / N_STEPS

    bottom_x = X_MID + STAIR_RUN

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
# 8. PORCH STAIR (EAST DOOR)

def build_porch_stair():
    """
    Small straight stair in front of the east door down to ground.
    """
    n = 4
    total_rise = FLOOR0_BOTTOM + FLOOR_THICK
    step_rise = total_rise / n
    step_depth = 0.25

    x_facade = Lx
    door_j = GROUND_DOORS["E"][0]
    cy = (door_j + 0.5) * MODULE
    door_width = MODULE - 2 * FRAME_MARGIN

    for k in range(n):
        # flipped run: highest step (k = n-1) is nearest x_facade
        cx = x_facade + (n - k - 0.5) * step_depth
        cz = (k + 0.5) * step_rise
        make_box(
            name=f"PorchStep_{k}",
            center=(cx, cy, cz),
            size=(step_depth, door_width, step_rise),
            coll_kind="structure",
        )

# ------------------------------------------------------------------
# 9. SKYLIGHT ROOF OVER DOUBLE-HEIGHT SPACE

def build_skylight():
    """
    Rafters above the east double-height space, plus roof plates and
    north/south support beams. Rafters follow the structural grid, with
    one intermediate rafter between primary grid lines. Roof plates sit
    on top of rafters and overhang slightly to north and south.
    """

    theta = math.radians(SKY_SLOPE_DEG)

    # Width between supporting beams (south–north)
    span_support = Ly + POST_SECTION
    span_y = span_support + 2.0 * SKY_OVERHANG

    # Local y of the south support line in rafter coordinates
    y_support_local = -span_support / 2.0

    # South support level: top of south skylight beam sitting on wall
    z_south_beam_top = ROOF_BEAM_LEVEL + SKY_SOUTH_BEAM_H
    z_low = z_south_beam_top

    # Position rafter centres so bottom at south support line is at z_low
    local_z_support_bottom_raf = (
        y_support_local * math.sin(theta)
        + (-SKY_RAFTER_HEIGHT / 2.0) * math.cos(theta)
    )
    z_center_raf = z_low - local_z_support_bottom_raf

    # Roof plates sit on top of rafters
    z_center_plate = z_center_raf + (
        (SKY_RAFTER_HEIGHT / 2.0 + SKY_ROOF_THICK / 2.0) * math.cos(theta)
    )

    euler = (theta, 0.0, 0.0)

    # Rafter X positions: grid lines + mid-bays
    x_start = (NX // 2) * MODULE
    x_end = NX * MODULE
    step = MODULE / 2.0

    rafter_x = []
    x = x_start
    while x <= x_end + 1e-6:
        rafter_x.append(x)
        x += step

    # Rafters (orientation along Y)
    for idx, rx in enumerate(rafter_x):
        make_box(
            name=f"SkylightRafter_{idx}",
            center=(rx, Ly / 2.0, z_center_raf),
            size=(SKY_RAFTER_WIDTH, span_y, SKY_RAFTER_HEIGHT),
            coll_kind="structure",
            euler=euler,
        )

    # Roof plates between rafters
    for k in range(len(rafter_x) - 1):
        x0 = rafter_x[k]
        x1 = rafter_x[k + 1]
        cx = 0.5 * (x0 + x1)
        sx = x1 - x0
        make_box(
            name=f"SkylightRoof_{k}",
            center=(cx, Ly / 2.0, z_center_plate),
            size=(sx, span_y, SKY_ROOF_THICK),
            coll_kind="structure",
            euler=euler,
        )

    # -------------------------
    # NORTH & SOUTH HORIZONTAL BEAMS
    # -------------------------

    # Beam span extended so ends are flush with outer wall (beyond column centres)
    base_span_x = rafter_x[-1] - rafter_x[0]
    beam_span_x = base_span_x + POST_SECTION  # extend half-section each side
    beam_cx = 0.5 * (rafter_x[0] + rafter_x[-1])

    # North heavy beam – under rafters at high side
    local_z_north_bottom_raf = (
        (span_y / 2.0) * math.sin(theta)
        + (-SKY_RAFTER_HEIGHT / 2.0) * math.cos(theta)
    )
    z_north_bottom_raf = z_center_raf + local_z_north_bottom_raf
    beam_top_n = z_north_bottom_raf - 0.02

    north_beam_depth = BEAM_HEIGHT * SKY_NORTH_BEAM_FACTOR
    z_beam_north_center = beam_top_n - north_beam_depth / 2.0

    make_box(
        name="SkylightNorthBeam",
        center=(beam_cx, Ly, z_beam_north_center),
        size=(beam_span_x, BEAM_WIDTH, north_beam_depth),
        coll_kind="structure",
    )

    # Extend posts up to north beam underside
    beam_bottom_n = z_beam_north_center - north_beam_depth / 2.0
    ext_height = beam_bottom_n - POST_HEIGHT
    if ext_height > 0:
        for i in range(NX // 2, NX + 1):
            x_post = i * MODULE
            zc_ext = POST_HEIGHT + ext_height / 2.0
            make_box(
                name=f"PostExt_N_{i}",
                center=(x_post, Ly, zc_ext),
                size=(POST_SECTION, POST_SECTION, ext_height),
                coll_kind="structure",
            )

    # South beam – square profile sitting entirely on top of existing wall
    z_beam_south_center = ROOF_BEAM_LEVEL + SKY_SOUTH_BEAM_H / 2.0
    make_box(
        name="SkylightSouthBeam",
        center=(beam_cx, 0.0, z_beam_south_center),
        size=(beam_span_x, SKY_SOUTH_BEAM_H, SKY_SOUTH_BEAM_H),
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
    build_window_frames()
    build_staircase()
    build_porch_stair()
    build_skylight()


if __name__ == "__main__":
    build_unit()
