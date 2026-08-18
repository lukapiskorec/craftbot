# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 05 - CHATGPT 5.1 - V01
# DESCRIPTION: CONSTRUCTION MANUAL META-PROMPT
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V14
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import importlib
import math
import craftbot_lib as craftbot

# Ensure latest version of craftbot_lib is used inside Blender
importlib.reload(craftbot)


# -----------------------------------------------------------------------------
# 2. GLOBAL CONSTANTS
# -----------------------------------------------------------------------------

# Small numeric tolerance
EPS = 1e-5

# House overall footprint (metres)
HOUSE_LEN = 7.32
HOUSE_WID = 5.40

# Platform and posts
PLATFORM_HEIGHT = 0.70
POST_SIZE = 0.12  # square post 120 x 120

# Bearers
BEARER_DEPTH = 0.197  # vertical thickness
BEARER_WIDTH = 0.06   # horizontal width (beam width when running along X)

# Joists (floor + roof/ceiling share section)
JOIST_DEPTH = 0.145   # vertical
JOIST_WIDTH = 0.047   # horizontal
JOIST_SPACING = 0.61  # centre spacing

# Floor boarding
FLOOR_THICK = 0.022

# Wall frame
WALL_STUD_HEIGHT = 2.745  # distance between plates
STUD_WIDTH = 0.047        # minor dimension
STUD_DEPTH = 0.097        # major dimension / wall thickness
STUD_SPACING = 0.61

# Plates
BOTTOM_PLATE_DEPTH = STUD_DEPTH
BOTTOM_PLATE_THICK = STUD_WIDTH
TOP_PLATE_DEPTH = STUD_DEPTH
TOP_PLATE_THICK = STUD_WIDTH

# Plywood
PLY_THICK_EXT = 0.009
PLY_THICK_INT = 0.006

# Roof sheeting
ROOF_THICK = 0.02

# Door and window rough opening sizes (from finished floor level)
DOOR_WIDTH = 0.84
DOOR_HEIGHT = 2.10
WINDOW_WIDTH = 1.22
WINDOW_HEIGHT = 1.22
WINDOW_SILL_HEIGHT = 0.90

# Roof pitch
ROOF_PITCH_DEG = 30.0

# Truss type selection
# ROOF_TRUSS_TYPE = "king_post"
ROOF_TRUSS_TYPE = "fink"


# -----------------------------------------------------------------------------
# 3. SMALL HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def half(x):
    """Return half of a value (used for clarity and consistency)."""
    return 0.5 * x


def add_post(name, x, y, base_z, height, size=POST_SIZE):
    """
    Place a vertical square post.

    Parameters
    ----------
    name : str
        Element name.
    x, y : float
        Plan coordinates of post centre.
    base_z : float
        Base Z level of post (bottom).
    height : float
        Total height of the post.
    size : float
        Square cross-section size (same in X and Y).
    """
    if height <= EPS:
        return

    craftbot.place_element(
        name=name,
        loc=(x, y, base_z + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(size), half(size), half(height)),
    )


def add_beam_x(name, x0, x1, y, z, width, depth):
    """
    Place a horizontal rectangular beam running along the X axis.

    Parameters
    ----------
    name : str
        Element name.
    x0, x1 : float
        Start and end X positions (world).
    y : float
        Constant Y coordinate.
    z : float
        Centre Z coordinate.
    width : float
        Beam width (Y direction).
    depth : float
        Beam depth (Z direction, vertical).
    """
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
    """
    Place a horizontal rectangular beam running along the Y axis.

    Parameters
    ----------
    name : str
        Element name.
    x : float
        Constant X coordinate.
    y0, y1 : float
        Start and end Y positions (world).
    z : float
        Centre Z coordinate.
    width : float
        Beam width (X direction).
    depth : float
        Beam depth (Z direction, vertical).
    """
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
    """
    Place a flat horizontal slab (floor deck).

    Parameters
    ----------
    name : str
        Element name.
    x0, x1 : float
        Extents along X.
    y0, y1 : float
        Extents along Y.
    z : float
        Centre Z coordinate.
    thick : float
        Slab thickness (Z direction).
    """
    lx = abs(x1 - x0)
    ly = abs(y1 - y0)
    if lx <= EPS or ly <= EPS or thick <= EPS:
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
    """
    Place a vertical stud segment between z0 and z1.

    Parameters
    ----------
    name : str
        Element name.
    x, y : float
        Plan coordinates of stud centreline.
    z0, z1 : float
        Bottom and top Z levels of the segment.
    """
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
    """
    Place a vertical plywood wall segment whose main length axis is X.

    Parameters
    ----------
    name : str
        Element name.
    x0, x1 : float
        Horizontal extents along X.
    y : float
        Reference Y coordinate (sheet offset applied internally).
    base_z : float
        Bottom Z of the segment.
    height : float
        Vertical height of the segment.
    thickness : float
        Plywood thickness (Y direction).
    """
    span = abs(x1 - x0)
    if span <= EPS or height <= EPS or thickness <= EPS:
        return

    cx = 0.5 * (x0 + x1)
    cy = y + half(thickness)
    cz = base_z + half(height)

    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(span), half(thickness), half(height)),
    )


def add_plywood_wall_y(name, x, y0, y1, base_z, height, thickness):
    """
    Place a vertical plywood wall segment whose main length axis is Y.

    Parameters
    ----------
    name : str
        Element name.
    x : float
        Reference X coordinate (sheet offset applied internally).
    y0, y1 : float
        Horizontal extents along Y.
    base_z : float
        Bottom Z of the segment.
    height : float
        Vertical height of the segment.
    thickness : float
        Plywood thickness (X direction).
    """
    span = abs(y1 - y0)
    if span <= EPS or height <= EPS or thickness <= EPS:
        return

    cx = x + half(thickness)
    cy = 0.5 * (y0 + y1)
    cz = base_z + half(height)

    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(thickness), half(span), half(height)),
    )


def merge_intervals(intervals):
    """
    Merge a list of [a, b] intervals into a set of non-overlapping ranges.

    Parameters
    ----------
    intervals : list of [float, float]
        Intervals to merge.

    Returns
    -------
    list of [float, float]
        Merged intervals in ascending order.
    """
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda ab: ab[0])
    merged = [list(sorted_intervals[0])]

    for a, b in sorted_intervals[1:]:
        if b < a:
            a, b = b, a
        last_a, last_b = merged[-1]
        # Overlap or touching (within EPS) => merge
        if a <= last_b + EPS:
            if b > last_b:
                merged[-1][1] = b
        else:
            merged.append([a, b])

    return merged


def complement_intervals(z_min, z_max, open_intervals):
    """
    Compute the complement of a set of open intervals within [z_min, z_max].

    Parameters
    ----------
    z_min, z_max : float
        Overall solid range extents.
    open_intervals : list of (float, float)
        Intervals to remove (e.g. door/window openings).

    Returns
    -------
    list of (float, float)
        Solid ranges (segments) remaining after subtraction.
    """
    if z_max - z_min <= EPS:
        return []

    # Clamp open intervals to [z_min, z_max]
    clipped = []
    for a, b in open_intervals:
        lo = max(min(a, b), z_min)
        hi = min(max(a, b), z_max)
        if hi - lo > EPS:
            clipped.append([lo, hi])

    merged = merge_intervals(clipped)
    segments = []

    current = z_min
    for a, b in merged:
        if a > current + EPS:
            seg0 = current
            seg1 = min(a, z_max)
            if seg1 - seg0 > EPS:
                segments.append((seg0, seg1))
        current = max(current, b)
        if current >= z_max - EPS:
            break

    if z_max - current > EPS:
        segments.append((current, z_max))

    return segments


# -----------------------------------------------------------------------------
# 4. PLATFORM CONSTRUCTION
# -----------------------------------------------------------------------------

def build_platform():
    """
    Build the elevated platform with posts, bearers, joists and floor deck.

    Returns
    -------
    float
        Z coordinate of the floor slab centre (for use by wall construction).
    """
    # Footprint extents
    x0 = 0.0
    x1 = HOUSE_LEN
    y0 = 0.0
    y1 = HOUSE_WID

    # -------------------------------------------------------------------------
    # Posts
    # -------------------------------------------------------------------------
    base_z = 0.0
    post_height = PLATFORM_HEIGHT

    post_positions = []

    # Four corners
    post_positions.append((x0, y0))
    post_positions.append((x1, y0))
    post_positions.append((x0, y1))
    post_positions.append((x1, y1))

    # Mid of long sides (south and north)
    mid_x = 0.5 * (x0 + x1)
    post_positions.append((mid_x, y0))  # south mid
    post_positions.append((mid_x, y1))  # north mid

    for i, (px, py) in enumerate(post_positions):
        add_post(f"Post_{i}", px, py, base_z, post_height, POST_SIZE)

    # -------------------------------------------------------------------------
    # Bearers (running along X at south and north)
    # -------------------------------------------------------------------------
    bearer_z = PLATFORM_HEIGHT + half(BEARER_DEPTH)
    south_bearer_y = y0
    north_bearer_y = y1

    bx0 = x0 - half(POST_SIZE)
    bx1 = x1 + half(POST_SIZE)

    add_beam_x("Bearer_South", bx0, bx1, south_bearer_y, bearer_z, BEARER_WIDTH, BEARER_DEPTH)
    add_beam_x("Bearer_North", bx0, bx1, north_bearer_y, bearer_z, BEARER_WIDTH, BEARER_DEPTH)

    # -------------------------------------------------------------------------
    # Floor joists (running along Y)
    # -------------------------------------------------------------------------
    joist_z = bearer_z + half(BEARER_DEPTH) + half(JOIST_DEPTH)

    n_joists = int(HOUSE_LEN / JOIST_SPACING) + 1
    joist_x_positions = []

    for i in range(n_joists):
        jx = x0 + i * JOIST_SPACING
        if i == n_joists - 1 or jx > x1:
            jx = x1
        if joist_x_positions and abs(jx - joist_x_positions[-1]) <= EPS:
            continue
        joist_x_positions.append(jx)

    jy0 = south_bearer_y - 0.5 * BEARER_WIDTH
    jy1 = north_bearer_y + 0.5 * BEARER_WIDTH

    for idx, jx in enumerate(joist_x_positions):
        add_beam_y(
            name=f"Joist_{idx}",
            x=jx,
            y0=jy0,
            y1=jy1,
            z=joist_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # -------------------------------------------------------------------------
    # Floor deck
    # -------------------------------------------------------------------------
    floor_z = joist_z + half(JOIST_DEPTH) + half(FLOOR_THICK)

    add_slab(
        name="Floor",
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        z=floor_z,
        thick=FLOOR_THICK,
    )

    # Return centre Z of floor slab (not top surface)
    return floor_z


# -----------------------------------------------------------------------------
# 5. WALLS, OPENINGS, AND PLYWOOD
# -----------------------------------------------------------------------------

def build_walls(floor_z):
    """
    Build all four walls (studs, plates, openings and plywood).

    Parameters
    ----------
    floor_z : float
        Z coordinate of the floor slab centre.

    Returns
    -------
    float
        Z coordinate of the very top of the wall (top of plates).
    """
    # Wall location extents
    x_w = 0.0
    x_e = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID

    # Finished floor top Z (upper surface of deck)
    floor_top_z = floor_z + half(FLOOR_THICK)

    # -------------------------------------------------------------------------
    # Vertical layering: plates and studs
    # -------------------------------------------------------------------------
    bottom_plate_center_z = floor_top_z + half(BOTTOM_PLATE_DEPTH)
    bottom_plate_top_z = floor_top_z + BOTTOM_PLATE_DEPTH

    stud_base_z = bottom_plate_top_z
    stud_height = WALL_STUD_HEIGHT
    stud_top_z = stud_base_z + stud_height

    top_plate_center_z = stud_top_z + half(TOP_PLATE_DEPTH)
    wall_top_z = top_plate_center_z + half(TOP_PLATE_DEPTH)

    # Total wall height (for plywood)
    wall_total_height = bottom_plate_top_z - floor_top_z + stud_height + TOP_PLATE_DEPTH

    # -------------------------------------------------------------------------
    # Plates along X (south and north)
    # -------------------------------------------------------------------------
    plate_x0 = x_w - half(STUD_DEPTH)
    plate_x1 = x_e + half(STUD_DEPTH)

    # Bottom plates along X
    add_beam_x(
        "Bottom_S",
        plate_x0,
        plate_x1,
        y_s,
        bottom_plate_center_z,
        BOTTOM_PLATE_THICK,
        BOTTOM_PLATE_DEPTH,
    )
    add_beam_x(
        "Bottom_N",
        plate_x0,
        plate_x1,
        y_n,
        bottom_plate_center_z,
        BOTTOM_PLATE_THICK,
        BOTTOM_PLATE_DEPTH,
    )

    # Top plates along X
    add_beam_x(
        "Top_S",
        plate_x0,
        plate_x1,
        y_s,
        top_plate_center_z,
        TOP_PLATE_THICK,
        TOP_PLATE_DEPTH,
    )
    add_beam_x(
        "Top_N",
        plate_x0,
        plate_x1,
        y_n,
        top_plate_center_z,
        TOP_PLATE_THICK,
        TOP_PLATE_DEPTH,
    )

    # -------------------------------------------------------------------------
    # Plates along Y (west and east) butt into X-plates
    # -------------------------------------------------------------------------
    bottom_y0 = y_s + half(BOTTOM_PLATE_THICK)
    bottom_y1 = y_n - half(BOTTOM_PLATE_THICK)

    top_y0 = y_s + half(TOP_PLATE_THICK)
    top_y1 = y_n - half(TOP_PLATE_THICK)

    # Bottom plates along Y
    add_beam_y(
        "Bottom_W",
        x_w,
        bottom_y0,
        bottom_y1,
        bottom_plate_center_z,
        BOTTOM_PLATE_THICK,
        BOTTOM_PLATE_DEPTH,
    )
    add_beam_y(
        "Bottom_E",
        x_e,
        bottom_y0,
        bottom_y1,
        bottom_plate_center_z,
        BOTTOM_PLATE_THICK,
        BOTTOM_PLATE_DEPTH,
    )

    # Top plates along Y
    add_beam_y(
        "Top_W",
        x_w,
        top_y0,
        top_y1,
        top_plate_center_z,
        TOP_PLATE_THICK,
        TOP_PLATE_DEPTH,
    )
    add_beam_y(
        "Top_E",
        x_e,
        top_y0,
        top_y1,
        top_plate_center_z,
        TOP_PLATE_THICK,
        TOP_PLATE_DEPTH,
    )

    # -------------------------------------------------------------------------
    # Door and window positions in plan
    # -------------------------------------------------------------------------
    # South wall door (centred 1.5 stud spacings from west)
    door_center_s = x_w + 1.5 * STUD_SPACING
    door_x0 = door_center_s - half(DOOR_WIDTH)
    door_x1 = door_center_s + half(DOOR_WIDTH)

    # South window (south wall, centred in length)
    win_center_s_x = 0.5 * (x_w + x_e)
    win_s_x0 = win_center_s_x - half(WINDOW_WIDTH)
    win_s_x1 = win_center_s_x + half(WINDOW_WIDTH)

    # North window (same X centre and width)
    win_center_n_x = win_center_s_x
    win_n_x0 = win_center_n_x - half(WINDOW_WIDTH)
    win_n_x1 = win_center_n_x + half(WINDOW_WIDTH)

    # West window (in Y, centred)
    win_center_w_y = 0.5 * (y_s + y_n)
    win_w_y0 = win_center_w_y - half(WINDOW_WIDTH)
    win_w_y1 = win_center_w_y + half(WINDOW_WIDTH)

    # East window (same Y centre and width)
    win_center_e_y = win_center_w_y
    win_e_y0 = win_center_e_y - half(WINDOW_WIDTH)
    win_e_y1 = win_center_e_y + half(WINDOW_WIDTH)

    # -------------------------------------------------------------------------
    # Vertical extents for openings (door/window)
    # -------------------------------------------------------------------------
    door_bottom_z = max(floor_top_z, stud_base_z)
    door_geom_top_z = floor_top_z + DOOR_HEIGHT
    door_top_z = min(door_geom_top_z, stud_top_z)

    window_sill_z = max(floor_top_z + WINDOW_SILL_HEIGHT, stud_base_z)
    window_geom_head_z = window_sill_z + WINDOW_HEIGHT
    window_head_z = min(window_geom_head_z, stud_top_z)

    # -------------------------------------------------------------------------
    # Horizontal members: lintels, sills, heads (Z extents)
    # -------------------------------------------------------------------------
    horiz_depth = STUD_WIDTH   # vertical thickness
    horiz_width = STUD_WIDTH   # beam width (horizontal minor)

    # Door lintel
    door_lintel_center_z = door_top_z + half(horiz_depth)
    door_lintel_top_z = door_top_z + horiz_depth

    # Window sill (below sill Z)
    window_sill_center_z = window_sill_z - half(horiz_depth)
    window_sill_bottom_z = window_sill_z - horiz_depth

    # Window head (above head Z)
    window_head_center_z = window_head_z + half(horiz_depth)
    window_head_top_z = window_head_z + horiz_depth

    # Clear vertical ranges for stud trimming
    door_clear_z0 = door_bottom_z
    door_clear_z1 = min(door_lintel_top_z, stud_top_z)

    window_clear_z0 = max(window_sill_bottom_z, stud_base_z)
    window_clear_z1 = min(window_head_top_z, stud_top_z)

    # -------------------------------------------------------------------------
    # Clear horizontal spans (between inner faces of jamb studs)
    # -------------------------------------------------------------------------
    # South door clear span in X
    door_clear_x0 = door_x0 + half(STUD_DEPTH)
    door_clear_x1 = door_x1 - half(STUD_DEPTH)

    # South window clear span in X
    win_s_clear_x0 = win_s_x0 + half(STUD_DEPTH)
    win_s_clear_x1 = win_s_x1 - half(STUD_DEPTH)

    # North window clear span in X
    win_n_clear_x0 = win_n_x0 + half(STUD_DEPTH)
    win_n_clear_x1 = win_n_x1 - half(STUD_DEPTH)

    # West window clear span in Y
    win_w_clear_y0 = win_w_y0 + half(STUD_DEPTH)
    win_w_clear_y1 = win_w_y1 - half(STUD_DEPTH)

    # East window clear span in Y
    win_e_clear_y0 = win_e_y0 + half(STUD_DEPTH)
    win_e_clear_y1 = win_e_y1 - half(STUD_DEPTH)

    # -------------------------------------------------------------------------
    # Local helper for segmented studs
    # -------------------------------------------------------------------------
    def place_segmented_stud(name_prefix, index, x, y, open_ranges):
        """
        Place segmented stud at given (x, y) with Z segments computed from
        open intervals (door/window holes).

        Parameters
        ----------
        name_prefix : str
            Prefix for naming (e.g. "Stud_S").
        index : int
            Index of stud in sequence.
        x, y : float
            Plan position of stud.
        open_ranges : list of (float, float)
            Open Z intervals (to be removed).
        """
        solid_segments = complement_intervals(stud_base_z, stud_top_z, open_ranges)
        for seg_i, (z0, z1) in enumerate(solid_segments):
            seg_name = f"{name_prefix}_{index}_seg{seg_i}"
            add_stud_segment(seg_name, x, y, z0, z1)

    # -------------------------------------------------------------------------
    # South and North wall studs (X positions)
    # -------------------------------------------------------------------------
    stud_x_positions = []

    # Regular studs at multiples of spacing
    n_studs_x = int(HOUSE_LEN / STUD_SPACING) + 1
    for i in range(n_studs_x):
        sx = x_w + i * STUD_SPACING
        if i == n_studs_x - 1 or sx > x_e:
            sx = x_e
        stud_x_positions.append(sx)

    # Add jamb positions explicitly
    stud_x_positions.extend([door_x0, door_x1, win_s_x0, win_s_x1, win_n_x0, win_n_x1])

    # Deduplicate positions with rounding to 4 decimals
    rounded_to_real = {}
    for sx in stud_x_positions:
        key = round(sx, 4)
        if key not in rounded_to_real:
            rounded_to_real[key] = sx

    unique_x_positions = sorted(rounded_to_real.values())

    # South & North wall studs with opening trims
    for idx, sx in enumerate(unique_x_positions):
        # South wall
        open_ranges_s = []
        if door_clear_x0 < sx < door_clear_x1:
            open_ranges_s.append((door_clear_z0, door_clear_z1))
        if win_s_clear_x0 < sx < win_s_clear_x1:
            open_ranges_s.append((window_clear_z0, window_clear_z1))
        place_segmented_stud("Stud_S", idx, sx, y_s, open_ranges_s)

        # North wall
        open_ranges_n = []
        if win_n_clear_x0 < sx < win_n_clear_x1:
            open_ranges_n.append((window_clear_z0, window_clear_z1))
        place_segmented_stud("Stud_N", idx, sx, y_n, open_ranges_n)

    # -------------------------------------------------------------------------
    # West and East wall studs (Y positions)
    # -------------------------------------------------------------------------
    stud_y_positions = []

    n_studs_y = int(HOUSE_WID / STUD_SPACING) + 1
    for i in range(n_studs_y):
        sy = y_s + i * STUD_SPACING
        if i == n_studs_y - 1 or sy > y_n:
            sy = y_n
        stud_y_positions.append(sy)

    # Add jamb positions for west/east windows
    stud_y_positions.extend([win_w_y0, win_w_y1, win_e_y0, win_e_y1])

    rounded_to_real_y = {}
    for sy in stud_y_positions:
        key = round(sy, 4)
        if key not in rounded_to_real_y:
            rounded_to_real_y[key] = sy

    unique_y_positions = sorted(rounded_to_real_y.values())

    for idx, sy in enumerate(unique_y_positions):
        # West wall
        open_ranges_w = []
        if win_w_clear_y0 < sy < win_w_clear_y1:
            open_ranges_w.append((window_clear_z0, window_clear_z1))
        place_segmented_stud("Stud_W", idx, x_w, sy, open_ranges_w)

        # East wall
        open_ranges_e = []
        if win_e_clear_y0 < sy < win_e_clear_y1:
            open_ranges_e.append((window_clear_z0, window_clear_z1))
        place_segmented_stud("Stud_E", idx, x_e, sy, open_ranges_e)

    # -------------------------------------------------------------------------
    # Horizontal elements: door lintel + window sills & heads
    # -------------------------------------------------------------------------
    # South door lintel (runs along X)
    add_beam_x(
        "Door_Lintel_S",
        door_x0,
        door_x1,
        y_s,
        door_lintel_center_z,
        horiz_width,
        horiz_depth,
    )

    # South window sill & head
    add_beam_x(
        "Window_Sill_S",
        win_s_x0,
        win_s_x1,
        y_s,
        window_sill_center_z,
        horiz_width,
        horiz_depth,
    )
    add_beam_x(
        "Window_Head_S",
        win_s_x0,
        win_s_x1,
        y_s,
        window_head_center_z,
        horiz_width,
        horiz_depth,
    )

    # North window sill & head
    add_beam_x(
        "Window_Sill_N",
        win_n_x0,
        win_n_x1,
        y_n,
        window_sill_center_z,
        horiz_width,
        horiz_depth,
    )
    add_beam_x(
        "Window_Head_N",
        win_n_x0,
        win_n_x1,
        y_n,
        window_head_center_z,
        horiz_width,
        horiz_depth,
    )

    # West window sill & head (run along Y)
    add_beam_y(
        "Window_Sill_W",
        x_w,
        win_w_y0,
        win_w_y1,
        window_sill_center_z,
        horiz_width,
        horiz_depth,
    )
    add_beam_y(
        "Window_Head_W",
        x_w,
        win_w_y0,
        win_w_y1,
        window_head_center_z,
        horiz_width,
        horiz_depth,
    )

    # East window sill & head (run along Y)
    add_beam_y(
        "Window_Sill_E",
        x_e,
        win_e_y0,
        win_e_y1,
        window_sill_center_z,
        horiz_width,
        horiz_depth,
    )
    add_beam_y(
        "Window_Head_E",
        x_e,
        win_e_y0,
        win_e_y1,
        window_head_center_z,
        horiz_width,
        horiz_depth,
    )

    # -------------------------------------------------------------------------
    # Plywood sheathing (exterior & interior, trimmed around openings)
    # -------------------------------------------------------------------------
    ply_base_z = floor_top_z
    ply_height = wall_total_height
    ply_top_z = ply_base_z + ply_height

    # Opening definitions per wall using clear spans and geometric Z extents
    # South wall openings: door + south window
    openings_s = [
        {"span": (door_clear_x0, door_clear_x1), "vspan": (door_bottom_z, door_top_z)},
        {"span": (win_s_clear_x0, win_s_clear_x1), "vspan": (window_sill_z, window_head_z)},
    ]

    # North wall openings: north window only
    openings_n = [
        {"span": (win_n_clear_x0, win_n_clear_x1), "vspan": (window_sill_z, window_head_z)},
    ]

    # West wall openings: west window only
    openings_w = [
        {"span": (win_w_clear_y0, win_w_clear_y1), "vspan": (window_sill_z, window_head_z)},
    ]

    # East wall openings: east window only
    openings_e = [
        {"span": (win_e_clear_y0, win_e_clear_y1), "vspan": (window_sill_z, window_head_z)},
    ]

    def build_ply_wall_x(prefix, sheet_y, thickness, openings):
        """
        Build plywood segments along an X-oriented wall with trimming around openings.

        Parameters
        ----------
        prefix : str
            Base name prefix for elements.
        sheet_y : float
            Reference Y coordinate (before thickness offset inside add_plywood_wall_x).
        thickness : float
            Sheet thickness.
        openings : list of dict
            Each dict has:
                'span': (x0, x1) horizontal opening span (clear),
                'vspan': (z0, z1) vertical opening span.
        """
        if thickness <= EPS:
            return

        # Collect boundary positions along X: wall edges + opening edges
        xs = [x_w, x_e]
        for op in openings:
            xs.extend(list(op["span"]))
        xs = sorted(xs)

        # Loop over each horizontal strip between consecutive boundaries
        for i in range(len(xs) - 1):
            xa = xs[i]
            xb = xs[i + 1]
            if xb - xa <= EPS:
                continue

            mid_x = 0.5 * (xa + xb)

            # Determine vertical open ranges that intersect strip
            open_z_ranges = []
            for op in openings:
                s0, s1 = op["span"]
                if s0 <= mid_x <= s1:
                    vz0, vz1 = op["vspan"]
                    open_z_ranges.append((vz0, vz1))

            # Compute solid vertical segments via complement
            solid_segments = complement_intervals(ply_base_z, ply_top_z, open_z_ranges)

            for j, (z0, z1) in enumerate(solid_segments):
                seg_height = z1 - z0
                if seg_height <= EPS:
                    continue
                name = f"{prefix}_seg{i}_{j}"
                add_plywood_wall_x(name, xa, xb, sheet_y, z0, seg_height, thickness)

    def build_ply_wall_y(prefix, sheet_x, thickness, openings):
        """
        Build plywood segments along a Y-oriented wall with trimming around openings.

        Parameters
        ----------
        prefix : str
            Base name prefix for elements.
        sheet_x : float
            Reference X coordinate (before thickness offset inside add_plywood_wall_y).
        thickness : float
            Sheet thickness.
        openings : list of dict
            Each dict has:
                'span': (y0, y1) horizontal opening span (clear),
                'vspan': (z0, z1) vertical opening span.
        """
        if thickness <= EPS:
            return

        ys = [y_s, y_n]
        for op in openings:
            ys.extend(list(op["span"]))
        ys = sorted(ys)

        for i in range(len(ys) - 1):
            ya = ys[i]
            yb = ys[i + 1]
            if yb - ya <= EPS:
                continue

            mid_y = 0.5 * (ya + yb)

            open_z_ranges = []
            for op in openings:
                s0, s1 = op["span"]
                if s0 <= mid_y <= s1:
                    vz0, vz1 = op["vspan"]
                    open_z_ranges.append((vz0, vz1))

            solid_segments = complement_intervals(ply_base_z, ply_top_z, open_z_ranges)

            for j, (z0, z1) in enumerate(solid_segments):
                seg_height = z1 - z0
                if seg_height <= EPS:
                    continue
                name = f"{prefix}_seg{i}_{j}"
                add_plywood_wall_y(name, sheet_x, ya, yb, z0, seg_height, thickness)

    # Exterior plywood (offset outward by half stud depth + thickness)
    # South exterior ply
    ply_s_ext_y = y_s - (half(STUD_DEPTH) + PLY_THICK_EXT)
    build_ply_wall_x("Ply_S_ext", ply_s_ext_y, PLY_THICK_EXT, openings_s)

    # North exterior ply
    ply_n_ext_y = y_n + (half(STUD_DEPTH) + PLY_THICK_EXT)
    build_ply_wall_x("Ply_N_ext", ply_n_ext_y, PLY_THICK_EXT, openings_n)

    # West exterior ply
    ply_w_ext_x = x_w - (half(STUD_DEPTH) + PLY_THICK_EXT)
    build_ply_wall_y("Ply_W_ext", ply_w_ext_x, PLY_THICK_EXT, openings_w)

    # East exterior ply
    ply_e_ext_x = x_e + (half(STUD_DEPTH) + PLY_THICK_EXT)
    build_ply_wall_y("Ply_E_ext", ply_e_ext_x, PLY_THICK_EXT, openings_e)

    # Interior plywood (offset inside by half stud depth - thickness)
    # South interior ply
    ply_s_int_y = y_s + (half(STUD_DEPTH) - PLY_THICK_INT)
    build_ply_wall_x("Ply_S_int", ply_s_int_y, PLY_THICK_INT, openings_s)

    # North interior ply
    ply_n_int_y = y_n - (half(STUD_DEPTH) - PLY_THICK_INT)
    build_ply_wall_x("Ply_N_int", ply_n_int_y, PLY_THICK_INT, openings_n)

    # West interior ply
    ply_w_int_x = x_w + (half(STUD_DEPTH) - PLY_THICK_INT)
    build_ply_wall_y("Ply_W_int", ply_w_int_x, PLY_THICK_INT, openings_w)

    # East interior ply
    ply_e_int_x = x_e - (half(STUD_DEPTH) - PLY_THICK_INT)
    build_ply_wall_y("Ply_E_int", ply_e_int_x, PLY_THICK_INT, openings_e)

    # Return the top of wall (top of plates)
    return wall_top_z


# -----------------------------------------------------------------------------
# 6. ROOF: TRUSSES AND SHEETING
# -----------------------------------------------------------------------------

def add_rafter(name, x, y_low, y_mid, wall_top_z, rise, width, depth):
    """
    Create a sloped rafter beam in the YZ plane, rotated about the X axis.

    Parameters
    ----------
    name : str
        Element name.
    x : float
        X coordinate of the rafter (plan).
    y_low : float
        Eave Y coordinate (start).
    y_mid : float
        Ridge Y coordinate (end).
    wall_top_z : float
        Z coordinate at top of wall plates (eaves level).
    rise : float
        Vertical rise from eaves to ridge.
    width : float
        Rafter width (X direction).
    depth : float
        Rafter depth (Z direction).
    """
    dy = y_mid - y_low
    span = abs(dy)
    if span <= EPS or rise <= EPS:
        return

    length = math.hypot(span, rise)
    angle_rad = math.atan2(rise, span)
    angle_deg = math.degrees(angle_rad)

    # Positive angle if slope goes from lower to higher Y, negative otherwise
    sign = 1.0 if dy >= 0.0 else -1.0
    angle = sign * angle_deg

    cy = 0.5 * (y_low + y_mid)
    cz = wall_top_z + half(rise)

    craftbot.place_element(
        name=name,
        loc=(x, cy, cz),
        axis=(1.0, 0.0, 0.0),
        angle=angle,
        scale=(half(width), half(length), half(depth)),
    )


def add_roof_plane(name, x0, x1, y_low, y_mid, wall_top_z, rise, thick):
    """
    Create a sloped rectangular roof sheathing plane.

    Parameters
    ----------
    name : str
        Element name.
    x0, x1 : float
        Plan extents along X.
    y_low : float
        Eave Y coordinate.
    y_mid : float
        Ridge Y coordinate.
    wall_top_z : float
        Z at top of wall plates (eaves level).
    rise : float
        Vertical rise from eaves to ridge.
    thick : float
        Roof sheathing thickness.
    """
    lx = abs(x1 - x0)
    dy = y_mid - y_low
    span = abs(dy)
    if lx <= EPS or span <= EPS or thick <= EPS or rise <= EPS:
        return

    slope_length = math.hypot(span, rise)
    pitch_rad = math.atan2(rise, span)
    pitch_deg = math.degrees(pitch_rad)
    sign = 1.0 if dy >= 0.0 else -1.0
    angle = sign * pitch_deg

    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y_low + y_mid)

    # Rafter centre Z at mid slope
    rafter_center_z = wall_top_z + half(rise)

    # Offset roof plane so bottom surface sits just above rafters
    clearance = 0.005
    # Use cos(theta) as specified to estimate vertical offset
    offset = (half(JOIST_DEPTH) + half(thick) + clearance) * math.cos(pitch_rad)
    cz = rafter_center_z + offset

    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(1.0, 0.0, 0.0),
        angle=angle,
        scale=(half(lx), half(slope_length), half(thick)),
    )


def add_vertical_member(name, x, y, z0, z1, width):
    """
    Add a vertical web member (e.g. king post).

    Parameters
    ----------
    name : str
        Element name.
    x, y : float
        Plan coordinates.
    z0, z1 : float
        Bottom and top Z.
    width : float
        Square cross-section width (X and Y).
    """
    height = z1 - z0
    if height <= EPS:
        return

    craftbot.place_element(
        name=name,
        loc=(x, y, z0 + half(height)),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(half(width), half(width), half(height)),
    )


def add_diagonal_member(name, x, y0, z0, y1, z1, width):
    """
    Add a diagonal web member in the YZ plane, rotated about X.

    Parameters
    ----------
    name : str
        Element name.
    x : float
        Constant X coordinate.
    y0, z0 : float
        Start point (Y, Z).
    y1, z1 : float
        End point (Y, Z).
    width : float
        Cross-section width (X and Z).
    """
    dy = y1 - y0
    dz = z1 - z0
    length = math.hypot(dy, dz)
    if length <= EPS:
        return

    angle_rad = math.atan2(dz, dy)
    angle_deg = math.degrees(angle_rad)

    cy = 0.5 * (y0 + y1)
    cz = 0.5 * (z0 + z1)

    craftbot.place_element(
        name=name,
        loc=(x, cy, cz),
        axis=(1.0, 0.0, 0.0),
        angle=angle_deg,
        scale=(half(width), half(length), half(width)),
    )


def z_on_rafter(y, y_s, y_n, wall_top_z, roof_rise):
    """
    Compute Z coordinate on a symmetric gable rafter at a given Y.

    Parameters
    ----------
    y : float
        Position along Y where Z is required.
    y_s, y_n : float
        South and north eave Y coordinates.
    wall_top_z : float
        Z at eaves (top of wall).
    roof_rise : float
        Vertical rise from eaves to ridge.

    Returns
    -------
    float
        Z coordinate on rafter line at Y.
    """
    y_mid = 0.5 * (y_s + y_n)
    half_span = y_mid - y_s
    if half_span <= EPS:
        return wall_top_z

    slope = roof_rise / half_span

    if y <= y_mid:
        # South half: line from (y_s, wall_top_z) to (y_mid, wall_top_z + roof_rise)
        return wall_top_z + slope * max(0.0, y - y_s)
    else:
        # North half: line from (y_n, wall_top_z) down to ridge
        return wall_top_z + slope * max(0.0, y_n - y)


def build_truss_webs_king_post(j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z):
    """
    Build king-post truss webs at index j.

    Parameters
    ----------
    j : int
        Section index.
    x : float
        X position of truss.
    y_s, y_n, y_mid : float
        South eave, north eave, and ridge Y positions.
    chord_top_z : float
        Z at top of bottom chord.
    ridge_z : float
        Ridge Z.
    roof_rise : float
        Rise from eaves to ridge.
    wall_top_z : float
        Top of wall Z (eaves).
    """
    width = JOIST_WIDTH

    # Vertical king post at bottom chord centre
    add_vertical_member(
        name=f"KingPost_{j}",
        x=x,
        y=y_mid,
        z0=chord_top_z,
        z1=ridge_z,
        width=width,
    )

    # Midpoints of rafters left (south) and right (north)
    y_mid_s = 0.5 * (y_s + y_mid)
    y_mid_n = 0.5 * (y_mid + y_n)

    z_mid_s = z_on_rafter(y_mid_s, y_s, y_n, wall_top_z, roof_rise)
    z_mid_n = z_on_rafter(y_mid_n, y_s, y_n, wall_top_z, roof_rise)

    # Diagonal struts from bottom chord centre to mid rafters
    add_diagonal_member(
        name=f"KingDiag_S_{j}",
        x=x,
        y0=y_mid,
        z0=chord_top_z,
        y1=y_mid_s,
        z1=z_mid_s,
        width=width,
    )

    add_diagonal_member(
        name=f"KingDiag_N_{j}",
        x=x,
        y0=y_mid,
        z0=chord_top_z,
        y1=y_mid_n,
        z1=z_mid_n,
        width=width,
    )


def build_truss_webs_fink(j, x, y_s, y_n, y_mid, chord_top_z, ridge_z, roof_rise, wall_top_z):
    """
    Build Fink truss webs with exactly four diagonal members.

    Parameters
    ----------
    j : int
        Section index.
    x : float
        X position of truss.
    y_s, y_n, y_mid : float
        South eave, north eave, and ridge Y positions.
    chord_top_z : float
        Z at top of bottom chord.
    ridge_z : float
        Ridge Z.
    roof_rise : float
        Rise from eaves to ridge.
    wall_top_z : float
        Top of wall Z (eaves).
    """
    width = JOIST_WIDTH

    total_span = y_n - y_s
    if total_span <= EPS:
        return

    # One-third and two-thirds points along bottom chord
    y_third_1 = y_s + total_span / 3.0
    y_third_2 = y_s + 2.0 * total_span / 3.0

    # Z values on bottom chord
    z_third_1 = chord_top_z
    z_third_2 = chord_top_z

    # Midpoints of rafters
    y_mid_s = 0.5 * (y_s + y_mid)
    y_mid_n = 0.5 * (y_mid + y_n)

    z_mid_s = z_on_rafter(y_mid_s, y_s, y_n, wall_top_z, roof_rise)
    z_mid_n = z_on_rafter(y_mid_n, y_s, y_n, wall_top_z, roof_rise)

    # 1. From mid south rafter down to first bottom-third
    add_diagonal_member(
        name=f"Fink_1_{j}",
        x=x,
        y0=y_mid_s,
        z0=z_mid_s,
        y1=y_third_1,
        z1=z_third_1,
        width=width,
    )

    # 2. From first bottom-third up to ridge
    add_diagonal_member(
        name=f"Fink_2_{j}",
        x=x,
        y0=y_third_1,
        z0=z_third_1,
        y1=y_mid,
        z1=ridge_z,
        width=width,
    )

    # 3. From mid north rafter down to second bottom-third
    add_diagonal_member(
        name=f"Fink_3_{j}",
        x=x,
        y0=y_mid_n,
        z0=z_mid_n,
        y1=y_third_2,
        z1=z_third_2,
        width=width,
    )

    # 4. From second bottom-third up to ridge
    add_diagonal_member(
        name=f"Fink_4_{j}",
        x=x,
        y0=y_third_2,
        z0=z_third_2,
        y1=y_mid,
        z1=ridge_z,
        width=width,
    )


def build_roof(wall_top_z):
    """
    Build the roof: ceiling joists (bottom chords), rafters, webs and roof sheeting.

    Parameters
    ----------
    wall_top_z : float
        Z coordinate of the top of walls (top of plates).
    """
    x0 = 0.0
    x1 = HOUSE_LEN
    y_s = 0.0
    y_n = HOUSE_WID
    y_mid = 0.5 * (y_s + y_n)

    # -------------------------------------------------------------------------
    # Ceiling joists / bottom chords (running along Y)
    # -------------------------------------------------------------------------
    # They extend slightly beyond top plate centres
    y0_chord = y_s - half(TOP_PLATE_THICK)
    y1_chord = y_n + half(TOP_PLATE_THICK)

    chord_center_z = wall_top_z + half(JOIST_DEPTH)
    chord_top_z = chord_center_z + half(JOIST_DEPTH)

    # Joist positions along X matching floor joists logic
    n_roof_joists = int(HOUSE_LEN / JOIST_SPACING) + 1
    roof_x_positions = []

    for i in range(n_roof_joists):
        rx = x0 + i * JOIST_SPACING
        if i == n_roof_joists - 1 or rx > x1:
            rx = x1
        if roof_x_positions and abs(rx - roof_x_positions[-1]) <= EPS:
            continue
        roof_x_positions.append(rx)

    for j, rx in enumerate(roof_x_positions):
        add_beam_y(
            name=f"RoofBeam_{j}",
            x=rx,
            y0=y0_chord,
            y1=y1_chord,
            z=chord_center_z,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

    # -------------------------------------------------------------------------
    # Rafters and truss webs
    # -------------------------------------------------------------------------
    half_span = half(y_n - y_s)
    pitch_rad = math.radians(ROOF_PITCH_DEG)
    roof_rise = half_span * math.tan(pitch_rad)
    ridge_z = wall_top_z + roof_rise

    for j, rx in enumerate(roof_x_positions):
        # South rafter (from south eave to ridge)
        add_rafter(
            name=f"Rafter_S_{j}",
            x=rx,
            y_low=y_s,
            y_mid=y_mid,
            wall_top_z=wall_top_z,
            rise=roof_rise,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

        # North rafter (from north eave to ridge)
        add_rafter(
            name=f"Rafter_N_{j}",
            x=rx,
            y_low=y_n,
            y_mid=y_mid,
            wall_top_z=wall_top_z,
            rise=roof_rise,
            width=JOIST_WIDTH,
            depth=JOIST_DEPTH,
        )

        # Truss webs based on selected type
        if ROOF_TRUSS_TYPE == "fink":
            build_truss_webs_fink(
                j=j,
                x=rx,
                y_s=y_s,
                y_n=y_n,
                y_mid=y_mid,
                chord_top_z=chord_top_z,
                ridge_z=ridge_z,
                roof_rise=roof_rise,
                wall_top_z=wall_top_z,
            )
        else:
            build_truss_webs_king_post(
                j=j,
                x=rx,
                y_s=y_s,
                y_n=y_n,
                y_mid=y_mid,
                chord_top_z=chord_top_z,
                ridge_z=ridge_z,
                roof_rise=roof_rise,
                wall_top_z=wall_top_z,
            )

    # -------------------------------------------------------------------------
    # Roof sheeting planes (south and north slopes)
    # -------------------------------------------------------------------------
    add_roof_plane(
        name="Roof_Slope_S",
        x0=x0,
        x1=x1,
        y_low=y_s,
        y_mid=y_mid,
        wall_top_z=wall_top_z,
        rise=roof_rise,
        thick=ROOF_THICK,
    )

    add_roof_plane(
        name="Roof_Slope_N",
        x0=x0,
        x1=x1,
        y_low=y_n,
        y_mid=y_mid,
        wall_top_z=wall_top_z,
        rise=roof_rise,
        thick=ROOF_THICK,
    )


# -----------------------------------------------------------------------------
# 7. MAIN ENTRY POINT
# -----------------------------------------------------------------------------

def build_house():
    """
    Build the complete small timber-frame house:
    platform, walls (with openings and plywood), and roof.
    """
    floor_z = build_platform()
    wall_top_z = build_walls(floor_z)
    build_roof(wall_top_z)


# Execute immediately when script is run in Blender
build_house()
