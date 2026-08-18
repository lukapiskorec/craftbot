# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V14
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot

# Reload to make sure we use the latest craftbot_lib in Blender
importlib.reload(craftbot)

# ---------------------------------------------------------------------------
# GLOBAL PARAMETERS (metres)
# ---------------------------------------------------------------------------

EPS = 1e-5  # numerical tolerance

# Overall footprint
HOUSE_LEN = 7.32
HOUSE_WID = 5.40

# Support posts / platform
PLATFORM_HEIGHT = 0.70
POST_SIZE = 0.12  # square post 120 x 120

# Bearers (girders) under joists
BEARER_DEPTH = 0.197  # vertical
BEARER_WIDTH = 0.06   # horizontal width (Y for X-beams)

# Floor / roof joists / ceiling joists
JOIST_DEPTH = 0.145   # vertical (Z)
JOIST_WIDTH = 0.047   # horizontal width (X)
JOIST_SPACING = 0.61  # centre-to-centre

# Floor decking
FLOOR_THICK = 0.022

# Wall frame
WALL_STUD_HEIGHT = 2.745  # clear stud between plates
STUD_WIDTH = 0.047        # minor cross-section
STUD_DEPTH = 0.097        # wall thickness / major cross-section
STUD_SPACING = 0.61       # stud module

# Plates (same section as studs)
BOTTOM_PLATE_DEPTH = STUD_DEPTH   # vertical (Z)
BOTTOM_PLATE_THICK = STUD_WIDTH   # width (plan)
TOP_PLATE_DEPTH = STUD_DEPTH
TOP_PLATE_THICK = STUD_WIDTH

# Plywood sheathing
PLY_THICK_EXT = 0.009
PLY_THICK_INT = 0.006

# Roof sheeting (boards / metal)
ROOF_THICK = 0.02

# Door & window parameters (rough opening sizes)
DOOR_WIDTH = 0.84          # main entrance door width
DOOR_HEIGHT = 2.10         # from finished floor level
WINDOW_WIDTH = 1.22        # approx 2M module
WINDOW_HEIGHT = 1.22
WINDOW_SILL_HEIGHT = 0.90  # from finished floor level

# Roof pitch (symmetric gable)
ROOF_PITCH_DEG = 30.0

# ---- SELECT TRUSS TYPE HERE ----
# Options: "king_post" or "fink"
# ROOF_TRUSS_TYPE = "king_post"
ROOF_TRUSS_TYPE = "fink"


# ---------------------------------------------------------------------------
# SMALL UTILITY HELPERS
# ---------------------------------------------------------------------------

def half(x: float) -> float:
    """Convenience helper for repeatedly using 'half(value)'."""
    return 0.5 * x


def add_post(name, x, y, base_z, height, size=POST_SIZE):
    """Vertical element with square cross-section `size`."""
    craftbot.place_element(
        name=name,
        loc=(x, y, base_z + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(size), half(size), half(height)),
    )


def add_beam_x(name, x0, x1, y, z, width, depth):
    """Rectangular beam running along X direction."""
    length = abs(x1 - x0)
    if length <= EPS:
        return
    cx = 0.5 * (x0 + x1)
    craftbot.place_element(
        name=name,
        loc=(cx, y, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(length), half(width), half(depth)),
    )


def add_beam_y(name, x, y0, y1, z, width, depth):
    """Rectangular beam running along Y direction."""
    length = abs(y1 - y0)
    if length <= EPS:
        return
    cy = 0.5 * (y0 + y1)
    craftbot.place_element(
        name=name,
        loc=(x, cy, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(width), half(length), half(depth)),
    )


def add_slab(name, x0, x1, y0, y1, z, thick):
    """Flat horizontal slab (used for floor boards)."""
    lx = abs(x1 - x0)
    ly = abs(y1 - y0)
    if lx <= EPS or ly <= EPS:
        return
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    craftbot.place_element(
        name=name,
        loc=(cx, cy, z),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(lx), half(ly), half(thick)),
    )


def add_stud_segment(name, x, y, z0, z1):
    """Place a vertical stud segment between z0 and z1."""
    height = z1 - z0
    if height <= EPS:
        return
    craftbot.place_element(
        name=name,
        loc=(x, y, z0 + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(STUD_DEPTH), half(STUD_DEPTH), half(height)),
    )


def add_plywood_wall_x(name, x0, x1, y, base_z, height, thickness):
    """Plywood sheet spanning along X, face normal ±Y."""
    lx = abs(x1 - x0)
    if lx <= EPS or height <= EPS:
        return
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
    if ly <= EPS or height <= EPS:
        return
    cy = 0.5 * (y0 + y1)
    zc = base_z + half(height)
    craftbot.place_element(
        name=name,
        loc=(x + half(thickness), cy, zc),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(thickness), half(ly), half(height)),
    )


# ----- Interval helpers used for trimming studs and plywood -----

def merge_intervals(intervals):
    """Merge overlapping [a, b] intervals into a minimal set."""
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda t: t[0])
    merged = [list(intervals[0])]
    for a, b in intervals[1:]:
        last_a, last_b = merged[-1]
        if a <= last_b + EPS:
            merged[-1][1] = max(last_b, b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def complement_intervals(z_min, z_max, open_intervals):
    """
    Given a base interval [z_min, z_max] and a list of "open" sub-intervals
    (where material is removed), return the list of remaining solid segments.
    """
    if not open_intervals:
        return [(z_min, z_max)]

    merged = merge_intervals(open_intervals)
    segments = []
    cursor = z_min

    for a, b in merged:
        if b <= cursor + EPS:
            continue
        if a > cursor + EPS:
            segments.append((cursor, a))
        cursor = max(cursor, b)

    if cursor < z_max - EPS:
        segments.append((cursor, z_max))

    return segments


# ---------------------------------------------------------------------------
# PLATFORM: POSTS, BEARERS, JOISTS, FLOOR
# ---------------------------------------------------------------------------

def build_platform():
    """Create posts, bearers, floor joists and decking."""
    x0 = 0.0
    x1 = HOUSE_LEN
    y0 = 0.0
    y1 = HOUSE_WID

    # ----- posts -----
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

    # ----- bearers -----
    bearer_z = PLATFORM_HEIGHT + half(BEARER_DEPTH)

    # bearers run along X and are centred on stud/post lines
    south_bearer_y = y0
    north_bearer_y = y1
    bearer_x0 = x0 - half(POST_SIZE)
    bearer_x1 = x1 + half(POST_SIZE)

    add_beam_x(
        "Bearer_South",
        bearer_x0,
        bearer_x1,
        south_bearer_y,
        bearer_z,
        width=BEARER_WIDTH,
        depth=BEARER_DEPTH,
    )
    add_beam_x(
        "Bearer_North",
        bearer_x0,
        bearer_x1,
        north_bearer_y,
        bearer_z,
        width=BEARER_WIDTH,
        depth=BEARER_DEPTH,
    )

    # ----- floor joists -----
    joist_z = bearer_z + half(BEARER_DEPTH) + half(JOIST_DEPTH)
    n_joists = int(HOUSE_LEN / JOIST_SPACING) + 1

    # Joists extend slightly beyond bearer centre-lines for better bearing
    south_end = south_bearer_y - 0.5 * BEARER_WIDTH
    north_end = north_bearer_y + 0.5 * BEARER_WIDTH

    for j in range(n_joists):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1
        add_beam_y(
            f"Joist_{j}",
            x,
            south_end,
            north_end,
            joist_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # ----- floor decking -----
    floor_z = joist_z + half(JOIST_DEPTH) + half(FLOOR_THICK)
    add_slab("Floor", x0, x1, y0, y1, floor_z, FLOOR_THICK)

    return floor_z


# ---------------------------------------------------------------------------
# WALL FRAMES + OPENINGS + PLYWOOD
# ---------------------------------------------------------------------------

def build_walls(floor_z):
    """
    Build all four walls:
      - bottom/top plates
      - trimmed studs around door and window openings
      - lintels / heads / sills
      - interior and exterior plywood broken into segments.
    Returns: top Z of the wall plates (used for roof).
    """
    # Basic extents
    x_w = 0.0
    x_e = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # Floor top surface
    floor_top_z = floor_z + half(FLOOR_THICK)

    # ----- plate and stud heights -----
    bottom_plate_center_z = floor_top_z + half(BOTTOM_PLATE_DEPTH)
    bottom_plate_top_z = floor_top_z + BOTTOM_PLATE_DEPTH

    stud_base_z = bottom_plate_top_z
    stud_height = WALL_STUD_HEIGHT
    stud_top_z = stud_base_z + stud_height

    top_plate_center_z = stud_base_z + stud_height + half(TOP_PLATE_DEPTH)

    wall_total_height = BOTTOM_PLATE_DEPTH + stud_height + TOP_PLATE_DEPTH
    wall_top_z = top_plate_center_z + half(TOP_PLATE_DEPTH)

    # Plates along X-direction are continuous and have priority
    plate_x0 = x_w - half(STUD_DEPTH)
    plate_x1 = x_e + half(STUD_DEPTH)

    # ----- bottom plates -----
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

    # Y-direction bottom plates butt into the X-direction plates
    y0_inner = y_s + half(BOTTOM_PLATE_THICK)
    y1_inner = y_n - half(BOTTOM_PLATE_THICK)

    add_beam_y(
        "Bottom_W",
        x_w,
        y0_inner,
        y1_inner,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )
    add_beam_y(
        "Bottom_E",
        x_e,
        y0_inner,
        y1_inner,
        bottom_plate_center_z,
        width=BOTTOM_PLATE_THICK,
        depth=BOTTOM_PLATE_DEPTH,
    )

    # ----- top plates -----
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
        y0_inner,
        y1_inner,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )
    add_beam_y(
        "Top_E",
        x_e,
        y0_inner,
        y1_inner,
        top_plate_center_z,
        width=TOP_PLATE_THICK,
        depth=TOP_PLATE_DEPTH,
    )

    # ------------------------------------------------------------------
    # OPENINGS (plan positions only – heights defined further below)
    # ------------------------------------------------------------------

    wall_len_x = HOUSE_LEN
    wall_len_y = HOUSE_WID

    # South wall: door + centred window
    door_center_s = x_w + 1.5 * STUD_SPACING
    door_x0 = door_center_s - DOOR_WIDTH * 0.5
    door_x1 = door_center_s + DOOR_WIDTH * 0.5

    win_center_s = x_w + wall_len_x * 0.5
    win_s_x0 = win_center_s - WINDOW_WIDTH * 0.5
    win_s_x1 = win_center_s + WINDOW_WIDTH * 0.5

    # North wall window
    win_center_n = x_w + wall_len_x * 0.5
    win_n_x0 = win_center_n - WINDOW_WIDTH * 0.5
    win_n_x1 = win_center_n + WINDOW_WIDTH * 0.5

    # West wall window (along Y)
    win_center_w = y_s + wall_len_y * 0.5
    win_w_y0 = win_center_w - WINDOW_WIDTH * 0.5
    win_w_y1 = win_center_w + WINDOW_WIDTH * 0.5

    # East wall window
    win_center_e = y_s + wall_len_y * 0.5
    win_e_y0 = win_center_e - WINDOW_WIDTH * 0.5
    win_e_y1 = win_center_e + WINDOW_WIDTH * 0.5

    # ------------------------------------------------------------------
    # OPENINGS (vertical extents)
    # ------------------------------------------------------------------

    # Door opening
    door_bottom_z = max(floor_top_z, stud_base_z)
    door_top_z = min(floor_top_z + DOOR_HEIGHT, stud_top_z)

    # Window openings (same for all windows)
    win_sill_z = max(floor_top_z + WINDOW_SILL_HEIGHT, stud_base_z)
    win_head_z = min(win_sill_z + WINDOW_HEIGHT, stud_top_z)

    # Horizontal elements (lintels / heads / sills) use stud section
    h_depth = STUD_WIDTH
    h_thick = STUD_WIDTH

    # Centres and bounding z for horizontals
    door_lintel_center_z = door_top_z + half(h_depth)
    door_lintel_top_z = door_top_z + h_depth

    win_sill_center_z = win_sill_z - half(h_depth)
    win_sill_bottom_z = win_sill_z - h_depth
    win_head_center_z = win_head_z + half(h_depth)
    win_head_top_z = win_head_z + h_depth

    # Clear ranges in Z where studs must be removed (include horizontals)
    door_clear_z0 = door_bottom_z
    door_clear_z1 = min(door_lintel_top_z, stud_top_z)

    win_clear_z0 = max(win_sill_bottom_z, stud_base_z)
    win_clear_z1 = min(win_head_top_z, stud_top_z)

    # Clear ranges in X/Y for studs (inside faces of jamb studs)
    door_clear_x0 = door_x0 + half(STUD_DEPTH)
    door_clear_x1 = door_x1 - half(STUD_DEPTH)

    win_s_clear_x0 = win_s_x0 + half(STUD_DEPTH)
    win_s_clear_x1 = win_s_x1 - half(STUD_DEPTH)
    win_n_clear_x0 = win_n_x0 + half(STUD_DEPTH)
    win_n_clear_x1 = win_n_x1 - half(STUD_DEPTH)

    win_w_clear_y0 = win_w_y0 + half(STUD_DEPTH)
    win_w_clear_y1 = win_w_y1 - half(STUD_DEPTH)
    win_e_clear_y0 = win_e_y0 + half(STUD_DEPTH)
    win_e_clear_y1 = win_e_y1 - half(STUD_DEPTH)

    # ------------------------------------------------------------------
    # STUDS (trimmed with complement_intervals)
    # ------------------------------------------------------------------

    def place_segmented_stud(name_prefix, index, x, y, open_ranges):
        """Compute solid segments along Z and place separate stud segments."""
        solid_segments = complement_intervals(stud_base_z, stud_top_z, open_ranges)
        for si, (z0, z1) in enumerate(solid_segments):
            add_stud_segment(f"{name_prefix}_{index}_{si}", x, y, z0, z1)

    # --- South & North walls (studs along X) ---
    n_s = int(HOUSE_LEN / STUD_SPACING) + 1
    stud_x_positions = []
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        stud_x_positions.append(x)

    # Also ensure jamb positions are present
    stud_x_positions.extend(
        [door_x0, door_x1, win_s_x0, win_s_x1, win_n_x0, win_n_x1]
    )
    stud_x_positions = sorted(set(round(v, 4) for v in stud_x_positions))

    # South wall studs (door + window)
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        if door_clear_x0 < x < door_clear_x1:
            open_ranges.append((door_clear_z0, door_clear_z1))
        if win_s_clear_x0 < x < win_s_clear_x1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_S", i, x, y_s, open_ranges)

    # North wall studs (window only)
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        if win_n_clear_x0 < x < win_n_clear_x1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_N", i, x, y_n, open_ranges)

    # --- West & East walls (studs along Y) ---
    n_w = int(HOUSE_WID / STUD_SPACING) + 1
    stud_y_positions = []
    for i in range(n_w + 1):
        y = y_s + i * STUD_SPACING
        if y > y_n:
            y = y_n
        stud_y_positions.append(y)

    stud_y_positions.extend([win_w_y0, win_w_y1, win_e_y0, win_e_y1])
    stud_y_positions = sorted(set(round(v, 4) for v in stud_y_positions))

    # West wall studs
    for i, y in enumerate(stud_y_positions):
        open_ranges = []
        if win_w_clear_y0 < y < win_w_clear_y1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_W", i, x_w, y, open_ranges)

    # East wall studs
    for i, y in enumerate(stud_y_positions):
        open_ranges = []
        if win_e_clear_y0 < y < win_e_clear_y1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_E", i, x_e, y, open_ranges)

    # ------------------------------------------------------------------
    # LINTELS, WINDOW SILLS & HEADS
    # ------------------------------------------------------------------

    # Door lintel (south)
    add_beam_x(
        "Door_Lintel_S",
        door_x0,
        door_x1,
        y_s,
        door_lintel_center_z,
        width=h_thick,
        depth=h_depth,
    )

    # South window
    add_beam_x(
        "Window_Sill_S",
        win_s_x0,
        win_s_x1,
        y_s,
        win_sill_center_z,
        width=h_thick,
        depth=h_depth,
    )
    add_beam_x(
        "Window_Head_S",
        win_s_x0,
        win_s_x1,
        y_s,
        win_head_center_z,
        width=h_thick,
        depth=h_depth,
    )

    # North window
    add_beam_x(
        "Window_Sill_N",
        win_n_x0,
        win_n_x1,
        y_n,
        win_sill_center_z,
        width=h_thick,
        depth=h_depth,
    )
    add_beam_x(
        "Window_Head_N",
        win_n_x0,
        win_n_x1,
        y_n,
        win_head_center_z,
        width=h_thick,
        depth=h_depth,
    )

    # West window (along Y)
    add_beam_y(
        "Window_Sill_W",
        x_w,
        win_w_y0,
        win_w_y1,
        win_sill_center_z,
        width=h_thick,
        depth=h_depth,
    )
    add_beam_y(
        "Window_Head_W",
        x_w,
        win_w_y0,
        win_w_y1,
        win_head_center_z,
        width=h_thick,
        depth=h_depth,
    )

    # East window (along Y)
    add_beam_y(
        "Window_Sill_E",
        x_e,
        win_e_y0,
        win_e_y1,
        win_sill_center_z,
        width=h_thick,
        depth=h_depth,
    )
    add_beam_y(
        "Window_Head_E",
        x_e,
        win_e_y0,
        win_e_y1,
        win_head_center_z,
        width=h_thick,
        depth=h_depth,
    )

    # ------------------------------------------------------------------
    # PLYWOOD SHEATHING WITH OPENINGS (vertical strips)
    # ------------------------------------------------------------------

    ply_base_z = floor_top_z
    ply_height = wall_total_height
    ply_top_z = ply_base_z + ply_height

    # Helpers specialised for X / Y walls.  They:
    #   1. subdivide the wall into vertical strips
    #   2. trim each strip in Z against all openings
    #   3. place separate plywood segments.

    def build_ply_wall_x(wall_name_prefix, y_sheet, thickness, openings_spans):
        # create split boundaries from wall ends + opening edges
        boundaries = [x_w, x_e]
        for op in openings_spans:
            boundaries.extend([op["span"][0], op["span"][1]])
        boundaries = sorted(set(round(v, 4) for v in boundaries))

        for i in range(len(boundaries) - 1):
            xa = boundaries[i]
            xb = boundaries[i + 1]
            if xb - xa <= EPS:
                continue
            xmid = 0.5 * (xa + xb)

            z_open = []
            for op in openings_spans:
                u0, u1 = op["span"]
                if u0 < xmid < u1:
                    z_open.append(op["vspan"])

            solid_z_segments = complement_intervals(ply_base_z, ply_top_z, z_open)

            for si, (z0, z1) in enumerate(solid_z_segments):
                h = z1 - z0
                if h <= EPS:
                    continue
                add_plywood_wall_x(
                    f"{wall_name_prefix}_seg{i}_{si}",
                    xa,
                    xb,
                    y_sheet,
                    z0,
                    h,
                    thickness,
                )

    def build_ply_wall_y(wall_name_prefix, x_sheet, thickness, openings_spans_y):
        boundaries = [y_s, y_n]
        for op in openings_spans_y:
            boundaries.extend([op["span"][0], op["span"][1]])
        boundaries = sorted(set(round(v, 4) for v in boundaries))

        for i in range(len(boundaries) - 1):
            ya = boundaries[i]
            yb = boundaries[i + 1]
            if yb - ya <= EPS:
                continue
            ymid = 0.5 * (ya + yb)

            z_open = []
            for op in openings_spans_y:
                v0, v1 = op["span"]
                if v0 < ymid < v1:
                    z_open.append(op["vspan"])

            solid_z_segments = complement_intervals(ply_base_z, ply_top_z, z_open)

            for si, (z0, z1) in enumerate(solid_z_segments):
                h = z1 - z0
                if h <= EPS:
                    continue
                add_plywood_wall_y(
                    f"{wall_name_prefix}_seg{i}_{si}",
                    x_sheet,
                    ya,
                    yb,
                    z0,
                    h,
                    thickness,
                )

    # Opening definitions specifically for plywood (rough openings)
    openings_s = [
        {"span": (door_clear_x0, door_clear_x1), "vspan": (door_bottom_z, door_top_z)},
        {"span": (win_s_clear_x0, win_s_clear_x1), "vspan": (win_sill_z, win_head_z)},
    ]
    openings_n = [
        {"span": (win_n_clear_x0, win_n_clear_x1), "vspan": (win_sill_z, win_head_z)},
    ]
    openings_w = [
        {"span": (win_w_clear_y0, win_w_clear_y1), "vspan": (win_sill_z, win_head_z)},
    ]
    openings_e = [
        {"span": (win_e_clear_y0, win_e_clear_y1), "vspan": (win_sill_z, win_head_z)},
    ]

    # --- Exterior ply ---
    build_ply_wall_x(
        "Ply_S_ext",
        y_s - (STUD_DEPTH * 0.5 + PLY_THICK_EXT),
        PLY_THICK_EXT,
        openings_s,
    )
    build_ply_wall_x(
        "Ply_N_ext",
        y_n + STUD_DEPTH * 0.5,
        PLY_THICK_EXT,
        openings_n,
    )
    build_ply_wall_y(
        "Ply_W_ext",
        x_w - (STUD_DEPTH * 0.5 + PLY_THICK_EXT),
        PLY_THICK_EXT,
        openings_w,
    )
    build_ply_wall_y(
        "Ply_E_ext",
        x_e + STUD_DEPTH * 0.5,
        PLY_THICK_EXT,
        openings_e,
    )

    # --- Interior ply ---
    build_ply_wall_x(
        "Ply_S_int",
        y_s + STUD_DEPTH * 0.5 - PLY_THICK_INT,
        PLY_THICK_INT,
        openings_s,
    )
    build_ply_wall_x(
        "Ply_N_int",
        y_n - STUD_DEPTH * 0.5,
        PLY_THICK_INT,
        openings_n,
    )
    build_ply_wall_y(
        "Ply_W_int",
        x_w + STUD_DEPTH * 0.5 - PLY_THICK_INT,
        PLY_THICK_INT,
        openings_w,
    )
    build_ply_wall_y(
        "Ply_E_int",
        x_e - STUD_DEPTH * 0.5,
        PLY_THICK_INT,
        openings_e,
    )

    return wall_top_z


# ---------------------------------------------------------------------------
# ROOF: CEILING JOISTS + TRUSSES + ROOF SHEETS
# ---------------------------------------------------------------------------

def add_rafter(name, x, y_low, y_mid, wall_top_z, rise, width, depth):
    """
    Single rafter from wall plate at y_low up to ridge at y_mid.
    This is a rotated box around the X axis.
    """
    span_y = abs(y_mid - y_low)
    if span_y <= EPS:
        return
    theta = math.atan2(rise, span_y)
    length = math.sqrt(span_y**2 + rise**2)

    y_c = 0.5 * (y_low + y_mid)
    z_c = wall_top_z + rise * 0.5

    sign = 1.0 if y_mid > y_low else -1.0
    angle_deg = math.degrees(theta) * sign

    craftbot.place_element(
        name=name,
        loc=(x, y_c, z_c),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(width), half(length), half(depth)),
    )


def add_roof_plane(name, x0, x1, y_low, y_mid, wall_top_z, rise, thick):
    """
    Sloped rectangular roof sheet from eave (y_low) up to ridge (y_mid).

    The sheet is positioned so its *bottom* surface sits just on top of the
    rafters (plus a tiny clearance), matching the underlying structure.
    """
    span_y = abs(y_mid - y_low)
    if span_y <= EPS:
        return
    theta = math.atan2(rise, span_y)
    length_slope = math.sqrt(span_y**2 + rise**2)

    xc = 0.5 * (x0 + x1)
    yc = 0.5 * (y_low + y_mid)

    # rafter centre
    rafter_center_z = wall_top_z + rise * 0.5

    # Move plane so its bottom sits exactly on top of rafters (plus small gap)
    clearance = 0.005  # 5 mm
    zc = (
        rafter_center_z
        + (half(JOIST_DEPTH) + half(thick)) * math.cos(theta)
        + clearance * math.cos(theta)
    )

    sign = 1.0 if y_mid > y_low else -1.0
    angle_deg = math.degrees(theta) * sign

    craftbot.place_element(
        name=name,
        loc=(xc, yc, zc),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(x1 - x0), half(length_slope), half(thick)),
    )


def add_vertical_member(name, x, y, z0, z1, width):
    """Simple vertical web member (used for king post)."""
    h = z1 - z0
    if h <= EPS:
        return
    craftbot.place_element(
        name=name,
        loc=(x, y, z0 + half(h)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(width), half(width), half(h)),
    )


def add_diagonal_member(name, x, y0, z0, y1, z1, width):
    """Diagonal web member in the truss plane (YZ)."""
    dy = y1 - y0
    dz = z1 - z0
    length = math.sqrt(dy * dy + dz * dz)
    if length <= EPS:
        return
    theta = math.atan2(dz, dy)
    angle_deg = math.degrees(theta)

    yc = 0.5 * (y0 + y1)
    zc = 0.5 * (z0 + z1)

    craftbot.place_element(
        name=name,
        loc=(x, yc, zc),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(width), half(length), half(width)),
    )


def z_on_rafter(y, y_s, y_n, wall_top_z, roof_rise):
    """
    For a symmetric gable roof: given a Y between the two eaves,
    return the Z coordinate on the rafter line.
    """
    y_mid = 0.5 * (y_s + y_n)
    span_half = y_mid - y_s
    theta = math.atan2(roof_rise, span_half)
    if y <= y_mid:
        dist = y - y_s
    else:
        dist = y_n - y
    return wall_top_z + dist * math.tan(theta)


# ----- KING-POST TRUSS WEBS -----

def build_truss_webs_king_post(
    j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z
):
    """Internal members for a king-post truss: central post + two struts."""
    y_center = y_mid

    # king post from bottom chord up to ridge
    add_vertical_member(
        f"KingPost_{j}",
        x,
        y_center,
        chord_top_z,
        ridge_z,
        width=JOIST_WIDTH,
    )

    # rafter midpoints left & right
    y_mid_left = 0.5 * (y_s + y_mid)
    y_mid_right = 0.5 * (y_mid + y_n)
    z_mid_left = z_on_rafter(y_mid_left, y_s, y_n, wall_top_z, roof_rise)
    z_mid_right = z_on_rafter(y_mid_right, y_s, y_n, wall_top_z, roof_rise)

    # diagonals from bottom centre to rafter midpoints
    add_diagonal_member(
        f"Strut_Left_{j}",
        x,
        y_center,
        chord_top_z,
        y_mid_left,
        z_mid_left,
        width=JOIST_WIDTH,
    )
    add_diagonal_member(
        f"Strut_Right_{j}",
        x,
        y_center,
        chord_top_z,
        y_mid_right,
        z_mid_right,
        width=JOIST_WIDTH,
    )


# ----- FINK TRUSS WEBS -----

def build_truss_webs_fink(
    j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z
):
    """
    Fink truss with four web elements:

        1) midpoint of south rafter -> 1st third of bottom chord
        2) 1st third of bottom chord -> ridge
        3) midpoint of north rafter -> 2nd third of bottom chord
        4) 2nd third of bottom chord -> ridge

    This matches the reference figure used earlier.
    """

    # bottom chord thirds (along Y)
    span_y = y_n - y_s
    y_third_1 = y_s + span_y / 3.0
    y_third_2 = y_s + 2.0 * span_y / 3.0

    z_third_1 = chord_top_z
    z_third_2 = chord_top_z

    # rafter midpoints (south and north)
    y_mid_s = 0.5 * (y_s + y_mid)
    y_mid_n = 0.5 * (y_mid + y_n)

    z_mid_s = z_on_rafter(y_mid_s, y_s, y_n, wall_top_z, roof_rise)
    z_mid_n = z_on_rafter(y_mid_n, y_s, y_n, wall_top_z, roof_rise)

    # Fink element 1: mid south rafter -> 1st third of bottom chord
    add_diagonal_member(
        f"Fink_1_{j}",
        x,
        y_mid_s,
        z_mid_s,
        y_third_1,
        z_third_1,
        width=JOIST_WIDTH,
    )

    # Fink element 2: 1st third of bottom chord -> ridge
    add_diagonal_member(
        f"Fink_2_{j}",
        x,
        y_third_1,
        z_third_1,
        y_mid,
        ridge_z,
        width=JOIST_WIDTH,
    )

    # Fink element 3: mid north rafter -> 2nd third of bottom chord
    add_diagonal_member(
        f"Fink_3_{j}",
        x,
        y_mid_n,
        z_mid_n,
        y_third_2,
        z_third_2,
        width=JOIST_WIDTH,
    )

    # Fink element 4: 2nd third of bottom chord -> ridge
    add_diagonal_member(
        f"Fink_4_{j}",
        x,
        y_third_2,
        z_third_2,
        y_mid,
        ridge_z,
        width=JOIST_WIDTH,
    )


def build_roof(wall_top_z):
    """Build ceiling joists, trusses (webs) and roof sheets."""
    x0 = 0.0
    x1 = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # ------------------ ceiling joists / bottom chords ------------------
    south_end = y_s - 0.5 * TOP_PLATE_THICK
    north_end = y_n + 0.5 * TOP_PLATE_THICK

    beam_bottom_z = wall_top_z
    beam_center_z = beam_bottom_z + half(JOIST_DEPTH)
    chord_top_z = beam_center_z + half(JOIST_DEPTH)

    n_beams = int(HOUSE_LEN / JOIST_SPACING) + 1

    # Place parallel beams along Y
    for j in range(n_beams):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1
        add_beam_y(
            f"RoofBeam_{j}",
            x,
            south_end,
            north_end,
            beam_center_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # ------------------ trusses (rafters + webs) ------------------------
    y_mid = 0.5 * (y_s + y_n)
    span_half = y_mid - y_s
    theta_rad = math.radians(ROOF_PITCH_DEG)
    roof_rise = span_half * math.tan(theta_rad)
    ridge_z = wall_top_z + roof_rise

    for j in range(n_beams):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1

        # rafters from wall top to ridge
        add_rafter(
            f"Rafter_S_{j}",
            x,
            y_s,
            y_mid,
            wall_top_z,
            roof_rise,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )
        add_rafter(
            f"Rafter_N_{j}",
            x,
            y_n,
            y_mid,
            wall_top_z,
            roof_rise,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

        # choose web layout
        if ROOF_TRUSS_TYPE == "fink":
            build_truss_webs_fink(
                j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z
            )
        else:  # default: king_post
            build_truss_webs_king_post(
                j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z
            )

    # ------------------ roof sheeting (two sloped planes) ---------------
    add_roof_plane(
        "Roof_Slope_S",
        x0,
        x1,
        y_s,
        y_mid,
        wall_top_z,
        roof_rise,
        ROOF_THICK,
    )
    add_roof_plane(
        "Roof_Slope_N",
        x0,
        x1,
        y_n,
        y_mid,
        wall_top_z,
        roof_rise,
        ROOF_THICK,
    )


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def build_house():
    """Build full house: platform, walls with openings, and roof."""
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


# Execute immediately when script is run in Blender
build_house()
