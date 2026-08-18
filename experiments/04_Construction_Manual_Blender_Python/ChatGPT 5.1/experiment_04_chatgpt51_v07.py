# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V07
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot

# reload to pick up latest craftbot_lib
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
BEARER_WIDTH = 0.06   # horizontal width (Y for X-beams)

# Floor / roof joists
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

# Roof slab (boards / membrane above roof beams)
ROOF_THICK = 0.05

# Door & window parameters (rough opening sizes)
DOOR_WIDTH = 0.84          # main entrance door width
DOOR_HEIGHT = 2.10         # from finished floor level
WINDOW_WIDTH = 1.22        # approx 2M module
WINDOW_HEIGHT = 1.22
WINDOW_SILL_HEIGHT = 0.90  # from finished floor level

EPS = 1e-5


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
    """Beam running along Y."""
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
    """Rectangular plate (floor/roof)."""
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
    """Plywood sheet spanning along X, face normal ±Y.

    'y' is NOT the sheet centre; sheet centre.y = y + thickness / 2.
    """
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
    """Plywood sheet spanning along Y, face normal ±X.

    'x' is NOT the sheet centre; sheet centre.x = x + thickness / 2.
    """
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


def merge_intervals(intervals):
    """Merge overlapping [a,b] intervals."""
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
    """Return list of solid [z0,z1] segments within [z_min,z_max]."""
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

    # Bearers: centre lines align with post/stud centre lines (y0 and y1)
    bearer_z = PLATFORM_HEIGHT + half(BEARER_DEPTH)
    bearer_x0 = x0 - half(POST_SIZE)
    bearer_x1 = x1 + half(POST_SIZE)

    south_bearer_y = y0  # aligned to post/stud centre
    north_bearer_y = y1  # aligned to post/stud centre

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

    # Joists: extend beyond bearer centre-lines for better bearing
    joist_z = bearer_z + half(BEARER_DEPTH) + half(JOIST_DEPTH)
    n_joists = int(HOUSE_LEN / JOIST_SPACING) + 1

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

    # Floor boards fully above joists
    floor_z = joist_z + half(JOIST_DEPTH) + half(FLOOR_THICK)
    add_slab("Floor", x0, x1, y0, y1, floor_z, FLOOR_THICK)

    return floor_z


# ---------------------------------------------------------------------------
# WALL FRAMES + OPENINGS + PLYWOOD
# ---------------------------------------------------------------------------

def build_walls(floor_z):
    # Top of floor boards
    floor_top_z = floor_z + half(FLOOR_THICK)

    x_w = 0.0
    x_e = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # Bottom plates sit fully on top of floor
    bottom_plate_center_z = floor_top_z + half(BOTTOM_PLATE_DEPTH)
    bottom_plate_top_z = floor_top_z + BOTTOM_PLATE_DEPTH

    # Studs stand on top of bottom plates
    stud_base_z = bottom_plate_top_z
    stud_height = WALL_STUD_HEIGHT
    stud_top_z = stud_base_z + stud_height

    # Top plates sit on top of studs
    top_plate_center_z = stud_base_z + stud_height + half(TOP_PLATE_DEPTH)
    wall_total_height = BOTTOM_PLATE_DEPTH + stud_height + TOP_PLATE_DEPTH
    wall_top_z = top_plate_center_z + half(TOP_PLATE_DEPTH)

    # Plates along X-direction are continuous and have priority
    plate_x0 = x_w - half(STUD_DEPTH)
    plate_x1 = x_e + half(STUD_DEPTH)

    # Bottom plates, X-direction (priority)
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

    # Bottom plates, Y-direction: shortened to butt into S/N plates (no overlap)
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

    # Top plates: same priority logic as bottom plates
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
    # DEFINE OPENINGS (positions on the existing box)
    # ------------------------------------------------------------------

    # Door on south wall, near west; windows centred on each wall.
    # Positions are along wall local axis (X for S/N, Y for E/W).

    # South wall
    wall_len_x = HOUSE_LEN
    door_center_s = x_w + 1.5 * STUD_SPACING   # ~0.9 m from west
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
    wall_len_y = HOUSE_WID
    win_center_w = y_s + wall_len_y * 0.5
    win_w_y0 = win_center_w - WINDOW_WIDTH * 0.5
    win_w_y1 = win_center_w + WINDOW_WIDTH * 0.5

    # East wall window
    win_center_e = y_s + wall_len_y * 0.5
    win_e_y0 = win_center_e - WINDOW_WIDTH * 0.5
    win_e_y1 = win_center_e + WINDOW_WIDTH * 0.5

    # Vertical extents
    door_bottom_z = floor_top_z          # rough opening from floor
    door_top_z = floor_top_z + DOOR_HEIGHT

    win_sill_z = floor_top_z + WINDOW_SILL_HEIGHT
    win_head_z = win_sill_z + WINDOW_HEIGHT

    # clamp to stud range
    door_bottom_z = max(door_bottom_z, stud_base_z)
    door_top_z = min(door_top_z, stud_top_z)
    win_sill_z = max(win_sill_z, stud_base_z)
    win_head_z = min(win_head_z, stud_top_z)

    # Clear opening extents (inside faces of jamb studs)
    # -> we use these for trimming studs & plywood; jamb studs remain solid.
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
    # STUDS WITH TRIMMED SEGMENTS (jamb studs remain full length)
    # ------------------------------------------------------------------

    def place_segmented_stud(name_prefix, index, x, y, open_ranges):
        """Place one stud broken into segments around openings."""
        solid_segments = complement_intervals(stud_base_z, stud_top_z, open_ranges)
        for si, (z0, z1) in enumerate(solid_segments):
            add_stud_segment(f"{name_prefix}_{index}_{si}", x, y, z0, z1)

    # --- SOUTH & NORTH walls (along X) ---

    n_s = int(HOUSE_LEN / STUD_SPACING) + 1
    stud_x_positions = []
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        stud_x_positions.append(x)

    # add jamb positions explicitly (door + window edges)
    stud_x_positions.extend(
        [door_x0, door_x1, win_s_x0, win_s_x1, win_n_x0, win_n_x1]
    )
    stud_x_positions = sorted(set(round(v, 4) for v in stud_x_positions))

    # South wall studs
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        # door clear opening
        if door_clear_x0 < x < door_clear_x1:
            open_ranges.append((door_bottom_z, door_top_z))
        # south window clear opening
        if win_s_clear_x0 < x < win_s_clear_x1:
            open_ranges.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_S", i, x, y_s, open_ranges)

    # North wall studs
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        if win_n_clear_x0 < x < win_n_clear_x1:
            open_ranges.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_N", i, x, y_n, open_ranges)

    # --- WEST & EAST walls (along Y) ---

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
            open_ranges.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_W", i, x_w, y, open_ranges)

    # East wall studs
    for i, y in enumerate(stud_y_positions):
        open_ranges = []
        if win_e_clear_y0 < y < win_e_clear_y1:
            open_ranges.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_E", i, x_e, y, open_ranges)

    # ------------------------------------------------------------------
    # LINTELS, WINDOW SILLS / HEADS
    # ------------------------------------------------------------------

    lintel_depth = STUD_DEPTH
    lintel_thick = STUD_WIDTH

    # Door lintel (south) - between jamb studs
    add_beam_x(
        "Door_Lintel_S",
        door_x0,
        door_x1,
        y_s,
        door_top_z + half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )

    # Window sills & heads
    # South window
    add_beam_x(
        "Window_Sill_S",
        win_s_x0,
        win_s_x1,
        y_s,
        win_sill_z - half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )
    add_beam_x(
        "Window_Head_S",
        win_s_x0,
        win_s_x1,
        y_s,
        win_head_z + half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )

    # North window
    add_beam_x(
        "Window_Sill_N",
        win_n_x0,
        win_n_x1,
        y_n,
        win_sill_z - half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )
    add_beam_x(
        "Window_Head_N",
        win_n_x0,
        win_n_x1,
        y_n,
        win_head_z + half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )

    # West window (along Y)  -- FIXED PARAM ORDER
    add_beam_y(
        "Window_Sill_W",
        x_w,
        win_w_y0,
        win_w_y1,
        win_sill_z - half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )
    add_beam_y(
        "Window_Head_W",
        x_w,
        win_w_y0,
        win_w_y1,
        win_head_z + half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )

    # East window (along Y)  -- FIXED PARAM ORDER
    add_beam_y(
        "Window_Sill_E",
        x_e,
        win_e_y0,
        win_e_y1,
        win_sill_z - half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )
    add_beam_y(
        "Window_Head_E",
        x_e,
        win_e_y0,
        win_e_y1,
        win_head_z + half(lintel_thick),
        width=lintel_thick,
        depth=lintel_depth,
    )

    # ------------------------------------------------------------------
    # PLYWOOD SHEATHING WITH OPENINGS (VERTICAL STRIPS)
    # ------------------------------------------------------------------

    ply_base_z = floor_top_z
    ply_height = wall_total_height
    ply_top_z = ply_base_z + ply_height

    # Helper to build X-wall plywood (S/N)
    def build_ply_wall_x(wall_name_prefix, y_sheet, thickness, openings_spans):
        """
        openings_spans: list of dicts:
          { 'span': (u0,u1), 'vspan': (z0,z1) } along X / Z
        y_sheet is the 'y' parameter fed to add_plywood_wall_x (not centre).
        """
        # boundaries along X
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

            # which openings affect this strip?
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

    # Helper to build Y-wall plywood (W/E)
    def build_ply_wall_y(wall_name_prefix, x_sheet, thickness, openings_spans_y):
        """
        openings_spans_y: list of dicts:
          { 'span': (v0,v1), 'vspan': (z0,z1) } along Y / Z
        x_sheet is 'x' fed to add_plywood_wall_y (not centre).
        """
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

    # Openings data per wall for plywood (use CLEAR spans!)
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

    # --- Exterior plywood ---
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

    # --- Interior plywood ---
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
# ROOF / CEILING BEAMS + ROOF SLAB
# ---------------------------------------------------------------------------

def build_roof(wall_top_z):
    x0 = 0.0
    x1 = HOUSE_LEN
    y0 = 0.0
    y1 = HOUSE_WID

    # Ceiling / roof beams: copy floor joist layout (along Y), sitting on top plates
    beam_bottom_z = wall_top_z
    beam_center_z = beam_bottom_z + half(JOIST_DEPTH)

    n_beams = int(HOUSE_LEN / JOIST_SPACING) + 1
    for j in range(n_beams):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1
        add_beam_y(
            f"RoofBeam_{j}",
            x,
            y0,
            y1,
            beam_center_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # Roof slab on top of beams
    roof_bottom_z = beam_bottom_z + JOIST_DEPTH
    roof_center_z = roof_bottom_z + half(ROOF_THICK)
    add_slab("Roof", x0, x1, y0, y1, roof_center_z, ROOF_THICK)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def build_house():
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


build_house()
