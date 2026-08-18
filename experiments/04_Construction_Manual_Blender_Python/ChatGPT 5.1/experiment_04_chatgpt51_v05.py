# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 04 - CHATGPT 5.1 - V05
# DESCRIPTION: CONSTRUCTION MANUAL
# ------------------------------------------------------------------

import bpy
import math
import sys
import os

# Make sure craftbot_lib is importable if this script is run standalone
if "craftbot_lib" not in sys.modules:
    # if script is in same dir as craftbot_lib.py, add it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.append(script_dir)

import craftbot_lib as craftbot


# ------------------------------------------------------------------
# SCENE UTILS
# ------------------------------------------------------------------

def clear_scene():
    # delete all objects in current scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # remove unused meshes
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def place_box(name, center, size, axis=(0, 0, 1), angle=0.0):
    """
    Convenience wrapper around craftbot.place_element.

    center : (x, y, z) of box centre in metres
    size   : (sx, sy, sz) overall dimensions of the box
    """
    sx, sy, sz = size
    scale = (sx / 2.0, sy / 2.0, sz / 2.0)
    return craftbot.place_element(
        name=name,
        loc=center,
        axis=axis,
        angle=angle,
        scale=scale
    )


def add_beam_x(name, x0, x1, y, z, width, depth):
    """Beam running along global X."""
    length = x1 - x0
    cx = (x0 + x1) * 0.5
    cy = y
    cz = z
    return place_box(
        name,
        center=(cx, cy, cz),
        size=(length, width, depth)
    )


def add_beam_y(name, y0, y1, x, z, width, depth):
    """Beam running along global Y."""
    length = y1 - y0
    cx = x
    cy = (y0 + y1) * 0.5
    cz = z
    return place_box(
        name,
        center=(cx, cy, cz),
        size=(width, length, depth)
    )


def add_post(name, x, y, z0, height, width, depth):
    """Vertical post starting at z0."""
    cz = z0 + height * 0.5
    return place_box(
        name,
        center=(x, y, cz),
        size=(width, depth, height)
    )


# ------------------------------------------------------------------
# GLOBAL PARAMETERS (ADJUST TO MATCH YOUR EXISTING MODEL)
# ------------------------------------------------------------------

# Grid & overall footprint (approximate FRIM house module)
GRID = 0.61          # 610 mm module
NUM_BAYS_X = 10      # along global X
NUM_BAYS_Y = 6       # along global Y

LENGTH_X = NUM_BAYS_X * GRID
LENGTH_Y = NUM_BAYS_Y * GRID

# Structural sizes (approximate manual: 47 x 97 mm studs, 47 x 112 mm plates)
STUD_THICK = 0.047
STUD_DEPTH = 0.097

PLATE_THICK = 0.047
PLATE_DEPTH = STUD_DEPTH

JOIST_THICK = 0.047
JOIST_DEPTH = 0.145

BEARER_THICK = 0.072
BEARER_DEPTH = 0.145

POST_SIZE = 0.12     # square post 120 x 120

FLOOR_BOARD_THICK = 0.030

# Heights
PLATFORM_TOP_Z = 0.70          # top of floor boards
JOIST_TOP_Z = PLATFORM_TOP_Z - FLOOR_BOARD_THICK
JOIST_BOTTOM_Z = JOIST_TOP_Z - JOIST_DEPTH
BEARER_TOP_Z = JOIST_BOTTOM_Z
POST_TOP_Z = BEARER_TOP_Z
GROUND_Z = 0.0
POST_HEIGHT = POST_TOP_Z - GROUND_Z

WALL_HEIGHT = 2.745             # floor to ceiling (FRIM manual)
TOP_PLATE_TOP_Z = PLATFORM_TOP_Z + WALL_HEIGHT
TOP_PLATE_BOTTOM_Z = TOP_PLATE_TOP_Z - PLATE_THICK
STUD_BASE_Z = PLATFORM_TOP_Z + PLATE_THICK   # studs start on top of bottom plate
STUD_HEIGHT = WALL_HEIGHT - 2 * PLATE_THICK  # between plates

# Regular spacings
STUD_SPACING = GRID        # 610 mm
JOIST_SPACING = GRID       # 610 mm

# Door and window sizes from manual / modular grid
DOOR_WIDTH = 0.84          # main entrance door 840 mm
DOOR_HEIGHT = 2.10         # from floor level
WINDOW_WIDTH = 1.22        # 2M wide (approx)
WINDOW_HEIGHT = 1.22
WINDOW_SILL_HEIGHT = 0.90  # bottom of window from floor

# Small epsilon for float comparisons
EPS = 1e-5


# ------------------------------------------------------------------
# BUILD PLATFORM: POSTS, BEARERS, JOISTS, FLOOR
# ------------------------------------------------------------------

def build_platform():
    # Corner coordinates of footprint
    x0, x1 = 0.0, LENGTH_X
    y0, y1 = 0.0, LENGTH_Y

    # Posts at corners
    post_z0 = GROUND_Z
    post_h = POST_HEIGHT

    post_x_positions = [x0, x1]
    post_y_positions = [y0, y1]

    # four corner posts
    idx = 0
    for px in post_x_positions:
        for py in post_y_positions:
            add_post(
                name=f"Post_{idx}",
                x=px,
                y=py,
                z0=post_z0,
                height=post_h,
                width=POST_SIZE,
                depth=POST_SIZE,
            )
            idx += 1

    # Bearers along perimeter (X has priority and runs continuous)
    bearer_z = BEARER_TOP_Z - BEARER_DEPTH * 0.5

    # South / North bearers (along X, continuous)
    add_beam_x(
        "Bearer_South",
        x0=x0 - BEARER_DEPTH,  # extend beyond posts a bit
        x1=x1 + BEARER_DEPTH,
        y=y0,
        z=bearer_z,
        width=BEARER_THICK,
        depth=BEARER_DEPTH,
    )

    add_beam_x(
        "Bearer_North",
        x0=x0 - BEARER_DEPTH,
        x1=x1 + BEARER_DEPTH,
        y=y1,
        z=bearer_z,
        width=BEARER_THICK,
        depth=BEARER_DEPTH,
    )

    # East / West bearers (between the two X bearers)
    add_beam_y(
        "Bearer_West",
        y0=y0 + BEARER_DEPTH,
        y1=y1 - BEARER_DEPTH,
        x=x0,
        z=bearer_z,
        width=BEARER_THICK,
        depth=BEARER_DEPTH,
    )

    add_beam_y(
        "Bearer_East",
        y0=y0 + BEARER_DEPTH,
        y1=y1 - BEARER_DEPTH,
        x=x1,
        z=bearer_z,
        width=BEARER_THICK,
        depth=BEARER_DEPTH,
    )

    # Joists along X, bearing on South/North bearers and extending slightly past centre lines
    joist_bottom_z = JOIST_BOTTOM_Z + JOIST_DEPTH * 0.5

    num_joists = int(LENGTH_Y / JOIST_SPACING) + 1
    for j in range(num_joists):
        y = y0 + j * JOIST_SPACING
        if y > y1 + EPS:
            break

        # extend joists past centre-line of bearers
        x_start = x0 - BEARER_DEPTH * 0.25
        x_end = x1 + BEARER_DEPTH * 0.25

        add_beam_x(
            name=f"Joist_{j}",
            x0=x_start,
            x1=x_end,
            y=y,
            z=joist_bottom_z,
            width=JOIST_THICK,
            depth=JOIST_DEPTH,
        )

    # Floor boards as single slab for now
    floor_thick = FLOOR_BOARD_THICK
    floor_z = PLATFORM_TOP_Z - floor_thick * 0.5
    place_box(
        "Floor_Boards",
        center=((x0 + x1) * 0.5, (y0 + y1) * 0.5, floor_z),
        size=(LENGTH_X, LENGTH_Y, floor_thick),
    )


# ------------------------------------------------------------------
# WALL STUD FRAMING WITH DOORS & WINDOWS
# ------------------------------------------------------------------

def compute_openings():
    """
    Returns a dict describing window/door openings on each wall.
    The walls are:
        South: y = y0
        North: y = y1
        West:  x = x0
        East:  x = x1
    Each entry: list of dicts with keys:
        'type': 'door' or 'window'
        'span': (u0, u1)  # along wall local axis (X for N/S, Y for E/W)
    """
    x0, x1 = 0.0, LENGTH_X
    y0, y1 = 0.0, LENGTH_Y

    openings = {
        "S": [],
        "N": [],
        "W": [],
        "E": [],
    }

    # South wall: one centred window + one entrance door offset from west
    wall_len_x = x1 - x0

    # Window centred
    w_c_south = x0 + wall_len_x * 0.5
    w0_south = w_c_south - WINDOW_WIDTH * 0.5
    w1_south = w_c_south + WINDOW_WIDTH * 0.5

    # Door near west side
    door_offset_from_west = GRID * 1.5   # about 0.9 m from corner
    d_c_south = x0 + door_offset_from_west
    d0_south = d_c_south - DOOR_WIDTH * 0.5
    d1_south = d_c_south + DOOR_WIDTH * 0.5

    openings["S"].append({"type": "window", "span": (w0_south, w1_south)})
    openings["S"].append({"type": "door", "span": (d0_south, d1_south)})

    # North wall: centred window only
    w_c_north = x0 + wall_len_x * 0.5
    w0_north = w_c_north - WINDOW_WIDTH * 0.5
    w1_north = w_c_north + WINDOW_WIDTH * 0.5
    openings["N"].append({"type": "window", "span": (w0_north, w1_north)})

    # West wall: centred window along Y
    wall_len_y = y1 - y0
    w_c_west = y0 + wall_len_y * 0.5
    w0_west = w_c_west - WINDOW_WIDTH * 0.5
    w1_west = w_c_west + WINDOW_WIDTH * 0.5
    openings["W"].append({"type": "window", "span": (w0_west, w1_west)})

    # East wall: centred window along Y
    w_c_east = y0 + wall_len_y * 0.5
    w0_east = w_c_east - WINDOW_WIDTH * 0.5
    w1_east = w_c_east + WINDOW_WIDTH * 0.5
    openings["E"].append({"type": "window", "span": (w0_east, w1_east)})

    return openings


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda t: t[0])
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e + EPS:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))
    return merged


def solid_segments(z_min, z_max, open_intervals):
    """
    Given vertical range [z_min, z_max] and list of open intervals,
    return list of solid [z0, z1] segments.
    """
    if not open_intervals:
        return [(z_min, z_max)]

    merged_open = merge_intervals(open_intervals)
    segments = []
    cursor = z_min
    for s, e in merged_open:
        if e <= cursor + EPS:
            continue
        if s > cursor + EPS:
            segments.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < z_max - EPS:
        segments.append((cursor, z_max))
    return segments


def build_wall_studs_with_openings():
    x0, x1 = 0.0, LENGTH_X
    y0, y1 = 0.0, LENGTH_Y

    openings = compute_openings()

    # Pre-compute vertical extents for door & window
    door_base_z = PLATFORM_TOP_Z
    door_top_z = door_base_z + DOOR_HEIGHT

    win_sill_z = PLATFORM_TOP_Z + WINDOW_SILL_HEIGHT
    win_head_z = win_sill_z + WINDOW_HEIGHT

    stud_top_z = STUD_BASE_Z + STUD_HEIGHT

    # Helper to place vertical segmented studs
    def place_segmented_stud(name_prefix, idx, x, y, open_vertical_ranges):
        segs = solid_segments(STUD_BASE_Z, stud_top_z, open_vertical_ranges)
        for si, (z0, z1) in enumerate(segs):
            h = z1 - z0
            if h <= EPS:
                continue
            add_post(
                name=f"{name_prefix}_{idx}_{si}",
                x=x,
                y=y,
                z0=z0,
                height=h,
                width=STUD_THICK,
                depth=STUD_DEPTH,
            )

    # ------------- SOUTH WALL (y = y0) -------------

    south_open = openings["S"]

    # Collect opening spans
    south_door_spans = [o["span"] for o in south_open if o["type"] == "door"]
    south_win_spans = [o["span"] for o in south_open if o["type"] == "window"]

    # Build stud positions: regular grid plus jambs at opening edges
    stud_positions_x = []
    n = int(LENGTH_X / STUD_SPACING) + 1
    for i in range(n + 1):
        px = x0 + i * STUD_SPACING
        if px <= x1 + EPS:
            stud_positions_x.append(px)

    # Add jamb positions
    for span in south_door_spans + south_win_spans:
        stud_positions_x.extend(span)

    stud_positions_x = sorted(stud_positions_x)
    # Deduplicate with tolerance
    unique_pos = []
    for px in stud_positions_x:
        if not unique_pos or abs(px - unique_pos[-1]) > 1e-4:
            unique_pos.append(px)
    stud_positions_x = unique_pos

    idx = 0
    for px in stud_positions_x:
        open_vertical = []

        # door opening segment
        for d0, d1 in south_door_spans:
            if d0 < px < d1:
                open_vertical.append((door_base_z, door_top_z))

        # window opening segment
        for w0, w1 in south_win_spans:
            if w0 < px < w1:
                open_vertical.append((win_sill_z, win_head_z))

        place_segmented_stud("Stud_S", idx, px, y0, open_vertical)
        idx += 1

    # ------------- NORTH WALL (y = y1) -------------

    north_open = openings["N"]
    north_win_spans = [o["span"] for o in north_open if o["type"] == "window"]

    stud_positions_x_N = stud_positions_x  # symmetric footprint

    idx = 0
    for px in stud_positions_x_N:
        open_vertical = []
        for w0, w1 in north_win_spans:
            if w0 < px < w1:
                open_vertical.append((win_sill_z, win_head_z))

        place_segmented_stud("Stud_N", idx, px, y1, open_vertical)
        idx += 1

    # ------------- WEST WALL (x = x0) -------------

    west_open = openings["W"]
    west_win_spans = [o["span"] for o in west_open if o["type"] == "window"]

    stud_positions_y_W = []
    n = int(LENGTH_Y / STUD_SPACING) + 1
    for i in range(n + 1):
        py = y0 + i * STUD_SPACING
        if py <= y1 + EPS:
            stud_positions_y_W.append(py)
    for span in west_win_spans:
        stud_positions_y_W.extend(span)
    stud_positions_y_W = sorted(stud_positions_y_W)
    uniq = []
    for py in stud_positions_y_W:
        if not uniq or abs(py - uniq[-1]) > 1e-4:
            uniq.append(py)
    stud_positions_y_W = uniq

    idx = 0
    for py in stud_positions_y_W:
        open_vertical = []
        for w0, w1 in west_win_spans:
            if w0 < py < w1:
                open_vertical.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_W", idx, x0, py, open_vertical)
        idx += 1

    # ------------- EAST WALL (x = x1) -------------

    east_open = openings["E"]
    east_win_spans = [o["span"] for o in east_open if o["type"] == "window"]

    stud_positions_y_E = stud_positions_y_W  # symmetric

    idx = 0
    for py in stud_positions_y_E:
        open_vertical = []
        for w0, w1 in east_win_spans:
            if w0 < py < w1:
                open_vertical.append((win_sill_z, win_head_z))
        place_segmented_stud("Stud_E", idx, x1, py, open_vertical)
        idx += 1

    # ------------- Bottom & Top Plates -------------

    plate_z_bottom = PLATFORM_TOP_Z + PLATE_THICK * 0.5
    plate_z_top = TOP_PLATE_BOTTOM_Z + PLATE_THICK * 0.5

    # South / North plates along X
    add_beam_x(
        "BottomPlate_S",
        x0=x0,
        x1=x1,
        y=y0,
        z=plate_z_bottom,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_x(
        "BottomPlate_N",
        x0=x0,
        x1=x1,
        y=y1,
        z=plate_z_bottom,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_y(
        "BottomPlate_W",
        y0=y0,
        y1=y1,
        x=x0,
        z=plate_z_bottom,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_y(
        "BottomPlate_E",
        y0=y0,
        y1=y1,
        x=x1,
        z=plate_z_bottom,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )

    # Top plates
    add_beam_x(
        "TopPlate_S",
        x0=x0,
        x1=x1,
        y=y0,
        z=plate_z_top,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_x(
        "TopPlate_N",
        x0=x0,
        x1=x1,
        y=y1,
        z=plate_z_top,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_y(
        "TopPlate_W",
        y0=y0,
        y1=y1,
        x=x0,
        z=plate_z_top,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )
    add_beam_y(
        "TopPlate_E",
        y0=y0,
        y1=y1,
        x=x1,
        z=plate_z_top,
        width=PLATE_THICK,
        depth=PLATE_DEPTH,
    )

    # ------------- Lintels and Sills for Doors / Windows -------------

    lintel_depth = STUD_DEPTH
    lintel_thick = PLATE_THICK

    # South wall
    for (d0, d1) in south_door_spans:
        # Door lintel
        z = door_top_z + lintel_thick * 0.5
        add_beam_x(
            "DoorLintel_S",
            x0=d0,
            x1=d1,
            y=y0,
            z=z,
            width=lintel_thick,
            depth=lintel_depth,
        )

    for (w0, w1) in south_win_spans:
        # Window sill
        z_sill = win_sill_z - lintel_thick * 0.5
        add_beam_x(
            "WindowSill_S",
            x0=w0,
            x1=w1,
            y=y0,
            z=z_sill,
            width=lintel_thick,
            depth=lintel_depth,
        )
        # Window head
        z_head = win_head_z + lintel_thick * 0.5
        add_beam_x(
            "WindowHead_S",
            x0=w0,
            x1=w1,
            y=y0,
            z=z_head,
            width=lintel_thick,
            depth=lintel_depth,
        )

    # North wall window
    for (w0, w1) in north_win_spans:
        z_sill = win_sill_z - lintel_thick * 0.5
        add_beam_x(
            "WindowSill_N",
            x0=w0,
            x1=w1,
            y=y1,
            z=z_sill,
            width=lintel_thick,
            depth=lintel_depth,
        )
        z_head = win_head_z + lintel_thick * 0.5
        add_beam_x(
            "WindowHead_N",
            x0=w0,
            x1=w1,
            y=y1,
            z=z_head,
            width=lintel_thick,
            depth=lintel_depth,
        )

    # West wall window (runs along Y)
    for (w0, w1) in west_win_spans:
        z_sill = win_sill_z - lintel_thick * 0.5
        add_beam_y(
            "WindowSill_W",
            y0=w0,
            y1=w1,
            x=x0,
            z=z_sill,
            width=lintel_thick,
            depth=lintel_depth,
        )
        z_head = win_head_z + lintel_thick * 0.5
        add_beam_y(
            "WindowHead_W",
            y0=w0,
            y1=w1,
            x=x0,
            z=z_head,
            width=lintel_thick,
            depth=lintel_depth,
        )

    # East wall window (along Y)
    for (w0, w1) in east_win_spans:
        z_sill = win_sill_z - lintel_thick * 0.5
        add_beam_y(
            "WindowSill_E",
            y0=w0,
            y1=w1,
            x=x1,
            z=z_sill,
            width=lintel_thick,
            depth=lintel_depth,
        )
        z_head = win_head_z + lintel_thick * 0.5
        add_beam_y(
            "WindowHead_E",
            y0=w0,
            y1=w1,
            x=x1,
            z=z_head,
            width=lintel_thick,
            depth=lintel_depth,
        )


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def main():
    clear_scene()
    build_platform()
    build_wall_studs_with_openings()


if __name__ == "__main__":
    main()
