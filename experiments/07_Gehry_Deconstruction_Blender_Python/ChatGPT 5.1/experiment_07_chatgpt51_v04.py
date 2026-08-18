# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 07 - CHATGPT 5.1 - V04
# GEHRY DECONSTRUCTED LIVING UNIT
#
# DESCRIPTION:
#   Deconstructivist living unit generated directly as a timber
#   frame + ruled-surface walls and a hyperbolic-paraboloid roof.
#
#   Usage:
#     - Place this file next to craftbot_lib.py and
#       experiment_04_chatgpt51_v14_lib.py.
#     - Run it from the Blender text editor.
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

# Wall curvature controls (kept consistent between wall + tessellation)
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
    ruled surfaces (walls, rafters, cladding strips).

    The local X-axis of the cube is aligned with the segment direction.
    thickness_y and thickness_z correspond to local Y/Z.
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

    Returns
    -------
    floor_z : float
        Centre of floor slab.
    floor_top_z : float
        Finished floor level (FFL).
    stud_base_z : float
        Start of clear wall framing above bottom plate.
    stud_top_z : float
        Top of clear wall framing (before top plate).
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


# ---------------------------------------------------------------------------
# WALL PROFILE SAMPLERS (TOP CHORDS)
# ---------------------------------------------------------------------------

def south_top_point(t, stud_top_z):
    y0 = 0.0
    x = L * t
    y_offset = SOUTH_OFF_AMP * math.sin(math.pi * t) + SOUTH_OFF_SHIFT
    z = stud_top_z + SOUTH_EXTRA_Z * math.sin(2.0 * math.pi * t + 0.4)
    return (x, y0 + y_offset, z)


def north_top_point(t, stud_top_z):
    y1 = W
    x = L * t
    y_offset = -NORTH_OFF_AMP * math.sin(math.pi * t + 0.7) + NORTH_OFF_SHIFT
    z = stud_top_z + 0.20 + NORTH_EXTRA_Z * math.cos(2.0 * math.pi * t + 0.9)
    return (x, y1 + y_offset, z)


def west_top_point(t, stud_top_z):
    x0 = 0.0
    y = W * t
    x_offset = WEST_OFF_AMP * math.sin(math.pi * t + 0.2)
    z = stud_top_z + WEST_EXTRA_Z * math.sin(2.0 * math.pi * t + 1.2)
    return (x0 + x_offset, y, z)


def east_top_point(t, stud_top_z):
    x1 = L
    y = W * t
    x_offset = -EAST_OFF_AMP * math.sin(math.pi * t * 1.4 + 0.7)
    z = stud_top_z + 0.18 + EAST_EXTRA_Z * math.cos(2.0 * math.pi * t + 0.1)
    return (x1 + x_offset, y, z)


# ---------------------------------------------------------------------------
# RULED WALLS
# ---------------------------------------------------------------------------

def build_ruled_wall_south(floor_top_z, stud_base_z, stud_top_z):
    y0 = 0.0
    n = int(L / STUD_SPACING) + 1

    # studs between bottom FFL line and warped top line
    for i in range(1, n - 1):  # skip corners; shared corner studs instead
        t = i / max(1, n - 1)
        x = L * t

        p0 = (x, y0, floor_top_z)
        p1 = south_top_point(t, stud_top_z)

        add_segment_between_points(
            f"S_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W,
        )

    # chords as before
    z_chord_bottom = floor_top_z + 0.25
    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)
        b0 = (L * t0, y0, z_chord_bottom)
        b1 = (L * t1, y0 + 0.15 * math.sin(math.pi * t1), z_chord_bottom)
        add_segment_between_points(
            f"S_Chord_B_{i:02d}",
            b0,
            b1,
            thickness_y=STUD_D * 0.9,
            thickness_z=STUD_W * 0.9,
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = south_top_point(t0, stud_top_z)
        p1 = south_top_point(t1, stud_top_z)

        add_segment_between_points(
            f"S_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W * 1.1,
        )


def build_ruled_wall_north(floor_top_z, stud_base_z, stud_top_z):
    n = int(L / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)
        x = L * t

        p0 = (x, W, floor_top_z)
        p1 = north_top_point(t, stud_top_z)

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

        p0 = north_top_point(t0, stud_top_z)
        p1 = north_top_point(t1, stud_top_z)

        add_segment_between_points(
            f"N_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_D,
            thickness_z=STUD_W * 1.05,
        )


def build_ruled_wall_west(floor_top_z, stud_base_z, stud_top_z):
    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        p0 = (0.0, W * t, floor_top_z)
        p1 = west_top_point(t, stud_top_z)

        # swap thickness_y / thickness_z to mimic 90° roll
        add_segment_between_points(
            f"W_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,   # rotated
            thickness_z=STUD_D,   # rotated
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = west_top_point(t0, stud_top_z)
        p1 = west_top_point(t1, stud_top_z)

        add_segment_between_points(
            f"W_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D * 1.05,
        )


def build_ruled_wall_east(floor_top_z, stud_base_z, stud_top_z):
    n = int(W / STUD_SPACING) + 1

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        p0 = (L, W * t, floor_top_z)
        p1 = east_top_point(t, stud_top_z)

        # swap thickness_y / thickness_z to mimic 90° roll
        add_segment_between_points(
            f"E_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,   # rotated
            thickness_z=STUD_D,   # rotated
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        p0 = east_top_point(t0, stud_top_z)
        p1 = east_top_point(t1, stud_top_z)

        add_segment_between_points(
            f"E_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=STUD_W,
            thickness_z=STUD_D * 1.05,
        )


def build_corner_studs(floor_top_z, corners):
    """
    Four shared corner studs so that studs from adjoining walls meet
    with identical size and rotation. They are vertical, square in
    profile, and their heights respond to the hypar roof: shorter
    where the roof dips, taller where it rises.
    """
    s = max(STUD_W, STUD_D) * 1.2  # square profile

    high_labels = ("SW", "NE")
    low_labels = ("SE", "NW")

    for label, (x, y, z_roof) in corners.items():
        if label in high_labels:
            top_z = z_roof - 0.15  # close to high roof, but non-touching
        elif label in low_labels:
            top_z = z_roof - 0.35  # further below low roof
        else:
            top_z = z_roof - 0.20

        p0 = (x, y, floor_top_z)
        p1 = (x, y, top_z)

        add_segment_between_points(
            f"Corner_{label}",
            p0,
            p1,
            thickness_y=s,
            thickness_z=s,
        )


def build_ruled_walls(floor_top_z, stud_base_z, stud_top_z, corners):
    build_ruled_wall_south(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_north(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_west(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_east(floor_top_z, stud_base_z, stud_top_z)
    build_corner_studs(floor_top_z, corners)


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

def build_tessellation_south(corners, stud_top_z):
    A = corners["SW"]
    B = corners["SE"]

    n = int(L / STUD_SPACING) + 1
    plate_w = 0.25
    plate_t = 0.04

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        wall_pt = south_top_point(t, stud_top_z)
        roof_pt = lerp(A, B, t)

        add_segment_between_points(
            f"Tess_S_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=plate_w,
            thickness_z=plate_t,
        )


def build_tessellation_north(corners, stud_top_z):
    D = corners["NW"]
    C = corners["NE"]

    n = int(L / STUD_SPACING) + 1
    plate_w = 0.25
    plate_t = 0.04

    for i in range(1, n - 1):
        t = i / max(1, n - 1)

        wall_pt = north_top_point(t, stud_top_z)
        roof_pt = lerp(D, C, t)

        add_segment_between_points(
            f"Tess_N_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=plate_w,
            thickness_z=plate_t,
        )


def build_tessellation_west(corners, stud_top_z):
    A = corners["SW"]
    D = corners["NW"]

    n = int(W / STUD_SPACING) + 1
    plate_w = 0.25
    plate_t = 0.04

    for i in range(1, n - 1):
        s = i / max(1, n - 1)

        wall_pt = west_top_point(s, stud_top_z)
        roof_pt = lerp(A, D, s)

        add_segment_between_points(
            f"Tess_W_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=plate_w,
            thickness_z=plate_t,
        )


def build_tessellation_east(corners, stud_top_z):
    B = corners["SE"]
    C = corners["NE"]

    n = int(W / STUD_SPACING) + 1
    plate_w = 0.25
    plate_t = 0.04

    for i in range(1, n - 1):
        s = i / max(1, n - 1)

        wall_pt = east_top_point(s, stud_top_z)
        roof_pt = lerp(B, C, s)

        add_segment_between_points(
            f"Tess_E_{i:02d}",
            wall_pt,
            roof_pt,
            thickness_y=plate_w,
            thickness_z=plate_t,
        )


def build_tessellation_plates(corners, stud_top_z):
    """
    Segmented plates that visually close the gap between each wall's
    top chord and the edge of the hypar roof, built as small ruled
    boards.
    """
    build_tessellation_south(corners, stud_top_z)
    build_tessellation_north(corners, stud_top_z)
    build_tessellation_west(corners, stud_top_z)
    build_tessellation_east(corners, stud_top_z)


# ---------------------------------------------------------------------------
# MAIN ASSEMBLY
# ---------------------------------------------------------------------------

def build_gehry_ruled_unit():
    floor_z, floor_top_z, stud_base_z, stud_top_z = compute_base_levels()

    corners = get_hypar_corners(stud_top_z)

    # Walls as enhanced ruled surfaces with shared corner studs
    build_ruled_walls(floor_top_z, stud_base_z, stud_top_z, corners)

    # Roof as strongly curved hyperbolic paraboloid
    build_hypar_roof(corners)

    # Tessellation plates between wall chords and roof edges
    build_tessellation_plates(corners, stud_top_z)


# Execute immediately when this script runs inside Blender
build_gehry_ruled_unit()
