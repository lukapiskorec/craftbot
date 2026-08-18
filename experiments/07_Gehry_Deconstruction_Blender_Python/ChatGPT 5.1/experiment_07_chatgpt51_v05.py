# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 07 - CHATGPT 5.1 - V05
# GEHRY DECONSTRUCTED LIVING UNIT
# ------------------------------------------------------------------

import bpy
import importlib
import math

import craftbot_lib as craftbot
import experiment_04_chatgpt51_v14_lib as base

# Ensure latest versions while iterating in Blender
importlib.reload(craftbot)
importlib.reload(base)

# ---------------------------------------------------------------------------
# GLOBAL SHORTCUTS / CONSTANTS
# ---------------------------------------------------------------------------

EPS = base.EPS
half = base.half

L = base.HOUSE_LEN
W = base.HOUSE_WID

STUD_W = base.STUD_WIDTH
STUD_D = base.STUD_DEPTH
STUD_SPACING = base.STUD_SPACING

JOIST_W = base.JOIST_WIDTH
JOIST_D = base.JOIST_DEPTH
JOIST_SPACING = base.JOIST_SPACING

PLY_THICK = base.PLY_THICK

# Wall curvature controls
SOUTH_EXTRA_Z = 0.35
SOUTH_OFF_AMP = 0.65
SOUTH_OFF_SHIFT = -0.20

NORTH_EXTRA_Z = 0.25
NORTH_OFF_AMP = 0.50
NORTH_OFF_SHIFT = 0.18

WEST_EXTRA_Z = 0.30
WEST_OFF_AMP = 0.70

EAST_EXTRA_Z = 0.30
EAST_OFF_AMP = 0.80

# Hypar curvature controls
HYPAR_LOW_DELTA = 0.05
HYPAR_HIGH_DELTA = 2.00

# Corner – roof clearance margins
CORNER_MARGIN_HIGH = 0.15
CORNER_MARGIN_LOW = 0.35

# Cladding + tessellation proportions
CLAD_BOARD_WIDTH = STUD_SPACING * 0.7
CLAD_BOARD_THICK = PLY_THICK * 0.5
CLAD_OFFSET = 0.03

TESS_BOARD_WIDTH = STUD_W * 1.1
TESS_BOARD_THICK = PLY_THICK * 0.4

ROOF_BOARD_WIDTH = JOIST_SPACING * 0.8
ROOF_BOARD_THICK = PLY_THICK * 0.6
ROOF_BOARD_LIFT = 0.02


# ---------------------------------------------------------------------------
# BASIC GEOMETRY HELPERS
# ---------------------------------------------------------------------------

def lerp(p, q, t):
    """Linear interpolation between 3D points p and q."""
    return (
        (1.0 - t) * p[0] + t * q[0],
        (1.0 - t) * p[1] + t * q[1],
        (1.0 - t) * p[2] + t * q[2],
    )


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_len(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def add_segment_between_points(
    name,
    p0,
    p1,
    thickness_y,
    thickness_z,
):
    """
    Place a rectangular prism whose long axis is the straight segment
    from p0 to p1. This is the basic "ruling" element used to build
    walls, rafters, tessellation boards and cladding.
    """
    v = vec_sub(p1, p0)
    length = vec_len(v)
    if length <= EPS:
        return

    cx = 0.5 * (p0[0] + p1[0])
    cy = 0.5 * (p0[1] + p1[1])
    cz = 0.5 * (p0[2] + p1[2])
    center = (cx, cy, cz)

    # Align global X-axis with segment using axis-angle rotation
    ex = (1.0, 0.0, 0.0)
    v_norm = (v[0] / length, v[1] / length, v[2] / length)
    dot = max(-1.0, min(1.0, vec_dot(ex, v_norm)))
    angle_rad = math.acos(dot)

    if angle_rad <= EPS:
        axis = (0.0, 0.0, 1.0)
        angle_deg = 0.0
    else:
        axis = vec_cross(ex, v_norm)
        axis_len = vec_len(axis)
        if axis_len <= EPS:
            axis = (0.0, 0.0, 1.0)
        else:
            axis = (axis[0] / axis_len, axis[1] / axis_len, axis[2] / axis_len)
        angle_deg = math.degrees(angle_rad)

    craftbot.place_element(
        name=name,
        loc=center,
        axis=axis,
        angle=angle_deg,
        scale=(half(length), half(thickness_y), half(thickness_z)),
    )


# ---------------------------------------------------------------------------
# LEVELS AND HYPAR CORNERS
# ---------------------------------------------------------------------------

def compute_base_levels():
    """
    Use the original platform geometry for support, but compute our own
    wall and roof control heights.
    """
    floor_z = base.build_platform()
    floor_top_z = floor_z + half(base.FLOOR_THICK)

    stud_base_z = floor_top_z + base.BOTTOM_PLATE_DEPTH
    stud_top_z = stud_base_z + base.WALL_STUD_HEIGHT

    return floor_z, floor_top_z, stud_base_z, stud_top_z


def get_hypar_corners(stud_top_z):
    """
    Return coordinates of the four hypar roof corners.
    High corners are SW + NE; low corners are SE + NW.
    """
    z_low = stud_top_z + HYPAR_LOW_DELTA
    z_high = stud_top_z + HYPAR_HIGH_DELTA

    corners = {
        "SW": (0.0, 0.0, z_high),
        "SE": (L,   0.0, z_low),
        "NE": (L,   W,   z_high),
        "NW": (0.0, W,   z_low),
    }
    return corners


def get_corner_wall_tops(corners):
    """
    Compute top points for wall corner studs, slightly below the roof
    hypar to avoid overlap. These become the end points of the wall
    wave and the start/end of top chords.
    """
    tops = {}

    for label, (x, y, z_roof) in corners.items():
        if label in ("SW", "NE"):  # high corners
            top_z = z_roof - CORNER_MARGIN_HIGH
        else:                      # low corners
            top_z = z_roof - CORNER_MARGIN_LOW
        tops[label] = (x, y, top_z)

    return tops


# ---------------------------------------------------------------------------
# WALL PROFILE SAMPLERS (TOP CHORDS)
#   Each sampler:
#     - uses corner wall tops at t=0/1
#     - interpolates linearly between corners
#     - modulates height with a wave that vanishes at the ends
# ---------------------------------------------------------------------------

def south_top_point(t, corner_tops):
    if t <= EPS:
        return corner_tops["SW"]
    if t >= 1.0 - EPS:
        return corner_tops["SE"]

    x = L * t
    # base linearly between SW and SE in Z
    z_base = lerp(corner_tops["SW"], corner_tops["SE"], t)[2]
    # vertical wave, zero at ends
    wave_factor = math.sin(math.pi * t)
    z = z_base + SOUTH_EXTRA_Z * math.sin(2.0 * math.pi * t + 0.4) * wave_factor
    # plan offset
    y0 = 0.0
    y_offset = SOUTH_OFF_AMP * math.sin(math.pi * t) + SOUTH_OFF_SHIFT
    return (x, y0 + y_offset, z)


def north_top_point(t, corner_tops):
    if t <= EPS:
        return corner_tops["NW"]
    if t >= 1.0 - EPS:
        return corner_tops["NE"]

    x = L * t
    z_base = lerp(corner_tops["NW"], corner_tops["NE"], t)[2]
    wave_factor = math.sin(math.pi * t)
    z = z_base + NORTH_EXTRA_Z * math.cos(2.0 * math.pi * t + 0.9) * wave_factor

    y1 = W
    y_offset = -NORTH_OFF_AMP * math.sin(math.pi * t + 0.7) + NORTH_OFF_SHIFT
    return (x, y1 + y_offset, z)


def west_top_point(t, corner_tops):
    if t <= EPS:
        return corner_tops["SW"]
    if t >= 1.0 - EPS:
        return corner_tops["NW"]

    y = W * t
    z_base = lerp(corner_tops["SW"], corner_tops["NW"], t)[2]
    wave_factor = math.sin(math.pi * t)
    z = z_base + WEST_EXTRA_Z * math.sin(2.0 * math.pi * t + 1.2) * wave_factor

    x0 = 0.0
    x_offset = WEST_OFF_AMP * math.sin(math.pi * t + 0.2)
    return (x0 + x_offset, y, z)


def east_top_point(t, corner_tops):
    if t <= EPS:
        return corner_tops["SE"]
    if t >= 1.0 - EPS:
        return corner_tops["NE"]

    y = W * t
    z_base = lerp(corner_tops["SE"], corner_tops["NE"], t)[2]
    wave_factor = math.sin(math.pi * t)
    z = z_base + EAST_EXTRA_Z * math.cos(2.0 * math.pi * t + 0.1) * wave_factor

    x1 = L
    x_offset = -EAST_OFF_AMP * math.sin(math.pi * t * 1.4 + 0.7)
    return (x1 + x_offset, y, z)


# ---------------------------------------------------------------------------
# RULED WALLS
# ---------------------------------------------------------------------------

def build_ruled_wall_south(floor_top_z, corner_tops):
    y0 = 0.0
    n = int(L / STUD_SPACING) + 1

    # studs between bottom FFL line and warped top line
    for i in range(1, n - 1):  # skip exact corners (handled separately)
        t = i / max(1, n - 1)
        x = L * t

        p0 = (x, y0, floor_top_z)
        p1 = south_top_point(t, corner_tops)

        add_segment_between_points(
            f"S_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W,
        )

    # top chords
    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = south_top_point(t0, corner_tops)
        p1 = south_top_point(t1, corner_tops)

        add_segment_between_points(
            f"S_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W * 1.1,
        )


def build_ruled_wall_north(floor_top_z, corner_tops):
    n = int(L / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)
        x = L * t

        p0 = (x, W, floor_top_z)
        p1 = north_top_point(t, corner_tops)

        add_segment_between_points(
            f"N_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W,
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = north_top_point(t0, corner_tops)
        p1 = north_top_point(t1, corner_tops)

        add_segment_between_points(
            f"N_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W * 1.05,
        )


def build_ruled_wall_west(floor_top_z, corner_tops):
    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        p0 = (0.0, W * t, floor_top_z)
        p1 = west_top_point(t, corner_tops)

        # swap thickness_y / thickness_z to mimic 90° roll
        add_segment_between_points(
            f"W_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D,
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = west_top_point(t0, corner_tops)
        p1 = west_top_point(t1, corner_tops)

        add_segment_between_points(
            f"W_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D * 1.05,
        )


def build_ruled_wall_east(floor_top_z, corner_tops):
    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        p0 = (L, W * t, floor_top_z)
        p1 = east_top_point(t, corner_tops)

        # swap thickness_y / thickness_z to mimic 90° roll
        add_segment_between_points(
            f"E_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D,
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = east_top_point(t0, corner_tops)
        p1 = east_top_point(t1, corner_tops)

        add_segment_between_points(
            f"E_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D * 1.05,
        )


def build_corner_studs(floor_top_z, corner_tops):
    """
    Four shared corner studs: vertical, square profile, heights
    taken directly from corner wall tops.
    """
    s = max(STUD_W, STUD_D) * 1.2  # square profile

    for label, (x, y, top_z) in corner_tops.items():
        p0 = (x, y, floor_top_z)
        p1 = (x, y, top_z)

        add_segment_between_points(
            f"Corner_{label}",
            p0,
            p1,
            thickness_y=s,
            thickness_z=s,
        )


def build_ruled_walls(floor_top_z, corner_tops):
    build_ruled_wall_south(floor_top_z, corner_tops)
    build_ruled_wall_north(floor_top_z, corner_tops)
    build_ruled_wall_west(floor_top_z, corner_tops)
    build_ruled_wall_east(floor_top_z, corner_tops)
    build_corner_studs(floor_top_z, corner_tops)


# ---------------------------------------------------------------------------
# HYPERBOLIC PARABOLOID ROOF (DOUBLE RULED SURFACE)
# ---------------------------------------------------------------------------

def build_hypar_roof(corners):
    """
    Roof as a classical hyperbolic paraboloid patch spanning the
    rectangular plan of the unit. Constructed entirely from straight
    rafters (rulings) in two intersecting families.
    """
    A = corners["SW"]
    B = corners["SE"]
    C = corners["NE"]
    D = corners["NW"]

    n1 = int(L / JOIST_SPACING) + 1

    # Family 1: rulings from AB to DC
    for i in range(n1):
        t = i / max(1, n1 - 1)
        p0 = lerp(A, B, t)
        p1 = lerp(D, C, t)
        add_segment_between_points(
            f"Roof_Rul_1_{i:02d}",
            p0,
            p1,
            thickness_y=JOIST_W,
            thickness_z=JOIST_D,
        )

    # Family 2: rulings from AD to BC (secondary rafters / purlins)
    n2 = int(W / JOIST_SPACING) + 1
    for j in range(n2):
        s = j / max(1, n2 - 1)
        q0 = lerp(A, D, s)
        q1 = lerp(B, C, s)
        add_segment_between_points(
            f"Roof_Rul_2_{j:02d}",
            q0,
            q1,
            thickness_y=JOIST_W * 0.75,
            thickness_z=JOIST_D * 0.75,
        )


# ---------------------------------------------------------------------------
# TESSELLATION PLATES (WALL–ROOF CONNECTORS)
# ---------------------------------------------------------------------------

def build_tessellation_south(corners, corner_tops):
    A = corners["SW"]
    B = corners["SE"]

    n = int(L / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        wall_pt = south_top_point(t, corner_tops)
        roof_pt = lerp(A, B, t)

        # shift outwards in Y-
        wall_pt = (wall_pt[0], wall_pt[1] - CLAD_OFFSET, wall_pt[2])
        roof_pt = (roof_pt[0], roof_pt[1] - CLAD_OFFSET, roof_pt[2])

        add_segment_between_points(
            f"Tess_S_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=TESS_BOARD_WIDTH,
            thickness_z=TESS_BOARD_THICK,
        )


def build_tessellation_north(corners, corner_tops):
    D = corners["NW"]
    C = corners["NE"]

    n = int(L / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        wall_pt = north_top_point(t, corner_tops)
        roof_pt = lerp(D, C, t)

        wall_pt = (wall_pt[0], wall_pt[1] + CLAD_OFFSET, wall_pt[2])
        roof_pt = (roof_pt[0], roof_pt[1] + CLAD_OFFSET, roof_pt[2])

        add_segment_between_points(
            f"Tess_N_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=TESS_BOARD_WIDTH,
            thickness_z=TESS_BOARD_THICK,
        )


def build_tessellation_west(corners, corner_tops):
    A = corners["SW"]
    D = corners["NW"]

    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        s = i / max(1, n - 1)

        wall_pt = west_top_point(s, corner_tops)
        roof_pt = lerp(A, D, s)

        wall_pt = (wall_pt[0] - CLAD_OFFSET, wall_pt[1], wall_pt[2])
        roof_pt = (roof_pt[0] - CLAD_OFFSET, roof_pt[1], roof_pt[2])

        # rotated 90° about axis: swap thickness_y / thickness_z
        add_segment_between_points(
            f"Tess_W_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=TESS_BOARD_THICK,
            thickness_z=TESS_BOARD_WIDTH,
        )


def build_tessellation_east(corners, corner_tops):
    B = corners["SE"]
    C = corners["NE"]

    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        s = i / max(1, n - 1)

        wall_pt = east_top_point(s, corner_tops)
        roof_pt = lerp(B, C, s)

        wall_pt = (wall_pt[0] + CLAD_OFFSET, wall_pt[1], wall_pt[2])
        roof_pt = (roof_pt[0] + CLAD_OFFSET, roof_pt[1], roof_pt[2])

        # rotated 90° about axis: swap thickness_y / thickness_z
        add_segment_between_points(
            f"Tess_E_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=TESS_BOARD_THICK,
            thickness_z=TESS_BOARD_WIDTH,
        )


def build_tessellation_plates(corners, corner_tops):
    build_tessellation_south(corners, corner_tops)
    build_tessellation_north(corners, corner_tops)
    build_tessellation_west(corners, corner_tops)
    build_tessellation_east(corners, corner_tops)


# ---------------------------------------------------------------------------
# FACADE PLYWOOD / BOARD CLADDING
# ---------------------------------------------------------------------------

def build_cladding_south(floor_top_z, corners, corner_tops):
    A = corners["SW"]
    B = corners["SE"]

    n = int(L / STUD_SPACING) + 1

    for i in range(n):
        t = i / max(1, n - 1)
        x = L * t

        # bottom and wall-top points
        bottom = (x, 0.0 - CLAD_OFFSET, floor_top_z)
        top_wall = south_top_point(t, corner_tops)
        top_wall = (top_wall[0], top_wall[1] - CLAD_OFFSET, top_wall[2])

        # lower board (stud zone)
        add_segment_between_points(
            f"Clad_S_L_{i:02d}",
            bottom,
            top_wall,
            thickness_y=CLAD_BOARD_WIDTH,
            thickness_z=CLAD_BOARD_THICK,
        )

        # upper board (tessellation zone) towards roof edge
        roof_edge = lerp(A, B, t)
        roof_edge = (roof_edge[0], roof_edge[1] - CLAD_OFFSET, roof_edge[2])

        add_segment_between_points(
            f"Clad_S_U_{i:02d}",
            top_wall,
            roof_edge,
            thickness_y=CLAD_BOARD_WIDTH,
            thickness_z=CLAD_BOARD_THICK,
        )


def build_cladding_north(floor_top_z, corners, corner_tops):
    D = corners["NW"]
    C = corners["NE"]

    n = int(L / STUD_SPACING) + 1

    for i in range(n):
        t = i / max(1, n - 1)
        x = L * t

        bottom = (x, W + CLAD_OFFSET, floor_top_z)
        top_wall = north_top_point(t, corner_tops)
        top_wall = (top_wall[0], top_wall[1] + CLAD_OFFSET, top_wall[2])

        add_segment_between_points(
            f"Clad_N_L_{i:02d}",
            bottom,
            top_wall,
            thickness_y=CLAD_BOARD_WIDTH,
            thickness_z=CLAD_BOARD_THICK,
        )

        roof_edge = lerp(D, C, t)
        roof_edge = (roof_edge[0], roof_edge[1] + CLAD_OFFSET, roof_edge[2])

        add_segment_between_points(
            f"Clad_N_U_{i:02d}",
            top_wall,
            roof_edge,
            thickness_y=CLAD_BOARD_WIDTH,
            thickness_z=CLAD_BOARD_THICK,
        )


def build_cladding_west(floor_top_z, corners, corner_tops):
    A = corners["SW"]
    D = corners["NW"]

    n = int(W / STUD_SPACING) + 1

    for i in range(n):
        s = i / max(1, n - 1)
        y = W * s

        bottom = (-CLAD_OFFSET, y, floor_top_z)
        top_wall = west_top_point(s, corner_tops)
        top_wall = (top_wall[0] - CLAD_OFFSET, top_wall[1], top_wall[2])

        # swap cross-section for rotated sense, like west studs / tess
        add_segment_between_points(
            f"Clad_W_L_{i:02d}",
            bottom,
            top_wall,
            thickness_y=CLAD_BOARD_THICK,
            thickness_z=CLAD_BOARD_WIDTH,
        )

        roof_edge = lerp(A, D, s)
        roof_edge = (roof_edge[0] - CLAD_OFFSET, roof_edge[1], roof_edge[2])

        add_segment_between_points(
            f"Clad_W_U_{i:02d}",
            top_wall,
            roof_edge,
            thickness_y=CLAD_BOARD_THICK,
            thickness_z=CLAD_BOARD_WIDTH,
        )


def build_cladding_east(floor_top_z, corners, corner_tops):
    B = corners["SE"]
    C = corners["NE"]

    n = int(W / STUD_SPACING) + 1

    for i in range(n):
        s = i / max(1, n - 1)
        y = W * s

        bottom = (L + CLAD_OFFSET, y, floor_top_z)
        top_wall = east_top_point(s, corner_tops)
        top_wall = (top_wall[0] + CLAD_OFFSET, top_wall[1], top_wall[2])

        add_segment_between_points(
            f"Clad_E_L_{i:02d}",
            bottom,
            top_wall,
            thickness_y=CLAD_BOARD_THICK,
            thickness_z=CLAD_BOARD_WIDTH,
        )

        roof_edge = lerp(B, C, s)
        roof_edge = (roof_edge[0] + CLAD_OFFSET, roof_edge[1], roof_edge[2])

        add_segment_between_points(
            f"Clad_E_U_{i:02d}",
            top_wall,
            roof_edge,
            thickness_y=CLAD_BOARD_THICK,
            thickness_z=CLAD_BOARD_WIDTH,
        )


def build_cladding(floor_top_z, corners, corner_tops):
    build_cladding_south(floor_top_z, corners, corner_tops)
    build_cladding_north(floor_top_z, corners, corner_tops)
    build_cladding_west(floor_top_z, corners, corner_tops)
    build_cladding_east(floor_top_z, corners, corner_tops)


# ---------------------------------------------------------------------------
# ROOF COVER (TESSELLATED BOARDS)
# ---------------------------------------------------------------------------

def build_roof_cover(corners):
    """
    Tessellated roof cover as boards following the first ruled family
    of the hypar (AB–DC). Boards sit slightly above the rafters.
    """
    A = corners["SW"]
    B = corners["SE"]
    C = corners["NE"]
    D = corners["NW"]

    n1 = int(L / JOIST_SPACING) + 1

    for i in range(n1):
        t = i / max(1, n1 - 1)
        p0 = lerp(A, B, t)
        p1 = lerp(D, C, t)

        p0 = (p0[0], p0[1], p0[2] + ROOF_BOARD_LIFT)
        p1 = (p1[0], p1[1], p1[2] + ROOF_BOARD_LIFT)

        add_segment_between_points(
            f"Roof_Clad_{i:02d}",
            p0,
            p1,
            thickness_y=ROOF_BOARD_WIDTH,
            thickness_z=ROOF_BOARD_THICK,
        )


# ---------------------------------------------------------------------------
# MAIN ASSEMBLY
# ---------------------------------------------------------------------------

def build_gehry_ruled_unit():
    floor_z, floor_top_z, stud_base_z, stud_top_z = compute_base_levels()

    corners = get_hypar_corners(stud_top_z)
    corner_tops = get_corner_wall_tops(corners)

    # Ruled walls with aligned corners
    build_ruled_walls(floor_top_z, corner_tops)

    # Hypar roof structure
    build_hypar_roof(corners)

    # Tessellation plates between walls and roof
    build_tessellation_plates(corners, corner_tops)

    # Plywood / board cladding on façades
    build_cladding(floor_top_z, corners, corner_tops)

    # Roof tessellated cover
    build_roof_cover(corners)


# Execute immediately when this script runs inside Blender
build_gehry_ruled_unit()
