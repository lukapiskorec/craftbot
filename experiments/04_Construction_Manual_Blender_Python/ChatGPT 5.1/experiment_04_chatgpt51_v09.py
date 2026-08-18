# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V09
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

# Roof sheeting (board / metal)
ROOF_THICK = 0.02

# Door & window parameters (rough opening sizes)
DOOR_WIDTH = 0.84          # main entrance door width
DOOR_HEIGHT = 2.10         # from finished floor level
WINDOW_WIDTH = 1.22        # approx 2M module
WINDOW_HEIGHT = 1.22
WINDOW_SILL_HEIGHT = 0.90  # from finished floor level

# Roof pitch (symmetric gable)
ROOF_PITCH_DEG = 30.0

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
    """Rectangular plate (floor)."""
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

    south_bearer_y = y0
    north_bearer_y = y1

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

    # Bottom plates, X-direction
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

    # Bottom plates, Y-direction: shortened to butt into S/N plates
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
    # DEFINE OPENINGS (positions)
    # ------------------------------------------------------------------

    # South wall: door + window
    wall_len_x = HOUSE_LEN
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
    wall_len_y = HOUSE_WID
    win_center_w = y_s + wall_len_y * 0.5
    win_w_y0 = win_center_w - WINDOW_WIDTH * 0.5
    win_w_y1 = win_center_w + WINDOW_WIDTH * 0.5

    # East wall window
    win_center_e = y_s + wall_len_y * 0.5
    win_e_y0 = win_center_e - WINDOW_WIDTH * 0.5
    win_e_y1 = win_center_e + WINDOW_WIDTH * 0.5

    # Vertical extents (rough openings)
    door_bottom_z = floor_top_z
    door_top_z = floor_top_z + DOOR_HEIGHT

    win_sill_z = floor_top_z + WINDOW_SILL_HEIGHT
    win_head_z = win_sill_z + WINDOW_HEIGHT

    # clamp to stud range
    door_bottom_z = max(door_bottom_z, stud_base_z)
    door_top_z = min(door_top_z, stud_top_z)
    win_sill_z = max(win_sill_z, stud_base_z)
    win_head_z = min(win_head_z, stud_top_z)

    # Horizontal member geometry (lintels, sills, heads)
    h_depth = STUD_WIDTH
    h_thick = STUD_WIDTH

    # Lintel / sill / head centres & vertical spans
    door_lintel_center_z = door_top_z + half(h_depth)
    door_lintel_bottom_z = door_top_z
    door_lintel_top_z = door_top_z + h_depth

    win_sill_center_z = win_sill_z - half(h_depth)
    win_sill_bottom_z = win_sill_z - h_depth
    win_sill_top_z = win_sill_z

    win_head_center_z = win_head_z + half(h_depth)
    win_head_bottom_z = win_head_z
    win_head_top_z = win_head_z + h_depth

    # Clear opening extents in Z for studs (include horizontals)
    door_clear_z0 = door_bottom_z
    door_clear_z1 = min(door_lintel_top_z, stud_top_z)

    win_clear_z0 = max(win_sill_bottom_z, stud_base_z)
    win_clear_z1 = min(win_head_top_z, stud_top_z)

    # Clear opening extents in plan (inside faces of jamb studs)
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
    # STUDS WITH TRIMMED SEGMENTS (no collisions with lintels/sills/heads)
    # ------------------------------------------------------------------

    def place_segmented_stud(name_prefix, index, x, y, open_ranges):
        solid_segments = complement_intervals(stud_base_z, stud_top_z, open_ranges)
        for si, (z0, z1) in enumerate(solid_segments):
            add_stud_segment(f"{name_prefix}_{index}_{si}", x, y, z0, z1)

    # SOUTH & NORTH walls (along X)
    n_s = int(HOUSE_LEN / STUD_SPACING) + 1
    stud_x_positions = []
    for i in range(n_s + 1):
        x = x_w + i * STUD_SPACING
        if x > x_e:
            x = x_e
        stud_x_positions.append(x)

    stud_x_positions.extend(
        [door_x0, door_x1, win_s_x0, win_s_x1, win_n_x0, win_n_x1]
    )
    stud_x_positions = sorted(set(round(v, 4) for v in stud_x_positions))

    # South wall studs
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        if door_clear_x0 < x < door_clear_x1:
            open_ranges.append((door_clear_z0, door_clear_z1))
        if win_s_clear_x0 < x < win_s_clear_x1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_S", i, x, y_s, open_ranges)

    # North wall studs
    for i, x in enumerate(stud_x_positions):
        open_ranges = []
        if win_n_clear_x0 < x < win_n_clear_x1:
            open_ranges.append((win_clear_z0, win_clear_z1))
        place_segmented_stud("Stud_N", i, x, y_n, open_ranges)

    # WEST & EAST walls (along Y)
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
    # LINTELS, WINDOW SILLS / HEADS
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

    # Window sills & heads
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
    # PLYWOOD SHEATHING WITH OPENINGS (VERTICAL STRIPS)
    # ------------------------------------------------------------------

    ply_base_z = floor_top_z
    ply_height = wall_total_height
    ply_top_z = ply_base_z + ply_height

    # plywood helpers
    def build_ply_wall_x(wall_name_prefix, y_sheet, thickness, openings_spans):
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

    # openings data for plywood (use rough openings)
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

    # Exterior ply
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

    # Interior ply
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
# ROOF: CEILING JOISTS + PITCHED TRUSSED RAFTER ROOF
# ---------------------------------------------------------------------------

def add_rafter(name, x, y_low, y_mid, wall_top_z, rise, width, depth):
    """Single rafter from wall plate at y_low up to ridge at y_mid."""
    span_y = abs(y_mid - y_low)
    if span_y <= EPS:
        return
    theta = math.atan2(rise, span_y)
    L = math.sqrt(span_y**2 + rise**2)

    y_c = 0.5 * (y_low + y_mid)
    z_c = wall_top_z + rise * 0.5

    # sign decides which way it slopes
    sign = 1.0 if y_mid > y_low else -1.0
    angle_deg = math.degrees(theta) * sign

    craftbot.place_element(
        name=name,
        loc=(x, y_c, z_c),
        axis=(1.0, 0.0, 0.0),  # rotate in YZ plane
        angle=angle_deg,
        scale=(half(width), half(L), half(depth)),
    )


def add_roof_plane(name, x0, x1, y_low, y_mid, wall_top_z, rise, thick):
    """Sloped rectangular roof sheet from y_low up to ridge at y_mid."""
    span_y = abs(y_mid - y_low)
    if span_y <= EPS:
        return
    theta = math.atan2(rise, span_y)
    L_slope = math.sqrt(span_y**2 + rise**2)

    xc = 0.5 * (x0 + x1)
    yc = 0.5 * (y_low + y_mid)
    zc = wall_top_z + rise * 0.5

    sign = 1.0 if y_mid > y_low else -1.0
    angle_deg = math.degrees(theta) * sign

    craftbot.place_element(
        name=name,
        loc=(xc, yc, zc),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(x1 - x0), half(L_slope), half(thick)),
    )


def build_roof(wall_top_z):
    x0 = 0.0
    x1 = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # ------------------ Ceiling joists (bottom chords) ------------------
    south_end = y_s - 0.5 * TOP_PLATE_THICK
    north_end = y_n + 0.5 * TOP_PLATE_THICK

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
            south_end,
            north_end,
            beam_center_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # ------------------ Trussed rafters (top chords) --------------------
    y_mid = 0.5 * (y_s + y_n)
    span_half = y_mid - y_s
    theta_rad = math.radians(ROOF_PITCH_DEG)
    roof_rise = span_half * math.tan(theta_rad)

    # rafters at same spacing as ceiling joists
    for j in range(n_beams):
        x = x0 + j * JOIST_SPACING
        if x > x1:
            x = x1

        # south rafter (eaves at south wall)
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

        # north rafter (eaves at north wall)
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

    # ------------------ Roof sheeting (two sloped planes) ---------------
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
# MAIN
# ---------------------------------------------------------------------------

def build_house():
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


build_house()
