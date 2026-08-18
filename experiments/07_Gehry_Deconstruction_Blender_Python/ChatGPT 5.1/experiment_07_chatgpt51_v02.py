# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 07 - CHATGPT 5.1 - V02
# GEHRY DECONSTRUCTED LIVING UNIT
#
# DESCRIPTION:
#   Deconstructivist living unit generated directly as a timber
#   frame + ruled-surface walls and a hyperbolic-paraboloid roof.
#
#   This script:
#     * uses experiment_04_chatgpt51_v14_lib.py only as a parameter
#       library + helper set (no call to build_house()).
#     * builds the platform from the base library.
#     * replaces all walls and the roof with new ruled geometry,
#       inspired by Gehry’s deconstructivist language.
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

# Ensure we always use the latest versions while iterating in Blender
importlib.reload(craftbot)
importlib.reload(base)

# ---------------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------------

EPS = base.EPS
half = base.half


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
# LEVELS AND GLOBAL PARAMETERS
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


# ---------------------------------------------------------------------------
# RULED WALLS
# ---------------------------------------------------------------------------

def build_ruled_wall_south(floor_top_z, stud_base_z, stud_top_z):
    """
    South wall: broken / twisted greenhouse facade.

    Guiding idea:
      - Bottom line is straight on the platform edge.
      - Top line is pulled out and pushed in with varying height to
        create a warped ruled surface.
    """
    L = base.HOUSE_LEN
    y0 = 0.0

    n = int(L / base.STUD_SPACING) + 1
    stud_w = base.STUD_WIDTH
    stud_d = base.STUD_DEPTH

    # Extra height variation on this wall
    extra_height = 0.35

    for i in range(n):
        t = i / max(1, n - 1)
        x = L * t

        # bottom directrix (on FFL)
        p0 = (x, y0, floor_top_z)

        # top directrix: offset in plan and modulated in height
        y_offset = 0.30 * math.sin(math.pi * t) - 0.10
        z_wave = extra_height * math.sin(2.0 * math.pi * t + 0.4)
        z_top = stud_top_z + z_wave

        p1 = (x, y0 + y_offset, z_top)

        # Create a doorway by omitting rulings around the centre bay
        if 0.40 <= t <= 0.58 and p1[2] - p0[2] > 1.9:
            # skip to leave clear opening
            continue

        add_segment_between_points(
            f"S_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w,
        )

    # Horizontal chords approximating head / sill as fractured beams
    # Bottom chord (slightly lifted from FFL)
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
            thickness_y=stud_d * 0.9,
            thickness_z=stud_w * 0.9,
        )

    # Top fractured chord following the warped upper line
    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        y_off0 = 0.30 * math.sin(math.pi * t0) - 0.10
        y_off1 = 0.30 * math.sin(math.pi * t1) - 0.10
        z0 = stud_top_z + extra_height * math.sin(2.0 * math.pi * t0 + 0.4)
        z1 = stud_top_z + extra_height * math.sin(2.0 * math.pi * t1 + 0.4)

        p0 = (L * t0, y0 + y_off0, z0)
        p1 = (L * t1, y0 + y_off1, z1)

        add_segment_between_points(
            f"S_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w * 1.1,
        )


def build_ruled_wall_north(floor_top_z, stud_base_z, stud_top_z):
    """
    North wall: quieter ruled surface, leaning inward with
    a different wave profile, acting as a counterpoint to the
    south facade.
    """
    L = base.HOUSE_LEN
    y1 = base.HOUSE_WID

    n = int(L / base.STUD_SPACING) + 1
    stud_w = base.STUD_WIDTH
    stud_d = base.STUD_DEPTH

    extra_height = 0.25

    for i in range(n):
        t = i / max(1, n - 1)
        x = L * t

        p0 = (x, y1, floor_top_z)

        y_offset = -0.22 * math.sin(math.pi * t + 0.7) + 0.12
        z_wave = extra_height * math.cos(2.0 * math.pi * t + 0.9)
        z_top = stud_top_z + 0.20 + z_wave

        p1 = (x, y1 + y_offset, z_top)

        add_segment_between_points(
            f"N_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w,
        )

    # Head chord
    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        y_off0 = -0.22 * math.sin(math.pi * t0 + 0.7) + 0.12
        y_off1 = -0.22 * math.sin(math.pi * t1 + 0.7) + 0.12
        z0 = stud_top_z + 0.20 + extra_height * math.cos(2.0 * math.pi * t0 + 0.9)
        z1 = stud_top_z + 0.20 + extra_height * math.cos(2.0 * math.pi * t1 + 0.9)

        p0 = (L * t0, y1 + y_off0, z0)
        p1 = (L * t1, y1 + y_off1, z1)

        add_segment_between_points(
            f"N_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w * 1.05,
        )


def build_ruled_wall_west(floor_top_z, stud_base_z, stud_top_z):
    """
    West wall: vertical rulings along Y, with the top line sliding in X
    so the entire wall twists toward the landscape.
    """
    W = base.HOUSE_WID
    x0 = 0.0

    n = int(W / base.STUD_SPACING) + 1
    stud_w = base.STUD_WIDTH
    stud_d = base.STUD_DEPTH

    extra_height = 0.30

    for i in range(n):
        t = i / max(1, n - 1)
        y = W * t

        p0 = (x0, y, floor_top_z)

        x_offset = 0.35 * math.sin(math.pi * t + 0.2)
        z_wave = extra_height * math.sin(2.0 * math.pi * t + 1.2)
        z_top = stud_top_z + z_wave

        p1 = (x0 + x_offset, y, z_top)

        # Leave out a band near the middle to act as fractured window
        if 0.30 <= t <= 0.55:
            continue

        add_segment_between_points(
            f"W_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w,
        )

    # Top sliding chord
    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        x_off0 = 0.35 * math.sin(math.pi * t0 + 0.2)
        x_off1 = 0.35 * math.sin(math.pi * t1 + 0.2)
        z0 = stud_top_z + extra_height * math.sin(2.0 * math.pi * t0 + 1.2)
        z1 = stud_top_z + extra_height * math.sin(2.0 * math.pi * t1 + 1.2)

        p0 = (x0 + x_off0, W * t0, z0)
        p1 = (x0 + x_off1, W * t1, z1)

        add_segment_between_points(
            f"W_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w * 1.05,
        )


def build_ruled_wall_east(floor_top_z, stud_base_z, stud_top_z):
    """
    East wall: mirror but not symmetric with west wall, sliding in X
    with different frequency to generate interference patterns in
    the rafters above.
    """
    W = base.HOUSE_WID
    x1 = base.HOUSE_LEN

    n = int(W / base.STUD_SPACING) + 1
    stud_w = base.STUD_WIDTH
    stud_d = base.STUD_DEPTH

    extra_height = 0.30

    for i in range(n):
        t = i / max(1, n - 1)
        y = W * t

        p0 = (x1, y, floor_top_z)

        x_offset = -0.40 * math.sin(math.pi * t * 1.4 + 0.7)
        z_wave = extra_height * math.cos(2.0 * math.pi * t + 0.1)
        z_top = stud_top_z + 0.18 + z_wave

        p1 = (x1 + x_offset, y, z_top)

        add_segment_between_points(
            f"E_Stud_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w,
        )

    for i in range(n - 1):
        t0 = i / max(1, n - 1)
        t1 = (i + 1) / max(1, n - 1)

        x_off0 = -0.40 * math.sin(math.pi * t0 * 1.4 + 0.7)
        x_off1 = -0.40 * math.sin(math.pi * t1 * 1.4 + 0.7)
        z0 = stud_top_z + 0.18 + extra_height * math.cos(2.0 * math.pi * t0 + 0.1)
        z1 = stud_top_z + 0.18 + extra_height * math.cos(2.0 * math.pi * t1 + 0.1)

        p0 = (x1 + x_off0, W * t0, z0)
        p1 = (x1 + x_off1, W * t1, z1)

        add_segment_between_points(
            f"E_Chord_T_{i:02d}",
            p0,
            p1,
            thickness_y=stud_d,
            thickness_z=stud_w * 1.05,
        )


def build_ruled_walls(floor_top_z, stud_base_z, stud_top_z):
    build_ruled_wall_south(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_north(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_west(floor_top_z, stud_base_z, stud_top_z)
    build_ruled_wall_east(floor_top_z, stud_base_z, stud_top_z)


# ---------------------------------------------------------------------------
# HYPERBOLIC PARABOLOID ROOF (DOUBLE RULED SURFACE)
# ---------------------------------------------------------------------------

def build_hypar_roof(stud_top_z):
    """
    Roof as a classical hyperbolic paraboloid patch spanning the
    rectangular plan of the unit. Constructed entirely from straight
    rafters (rulings) in two intersecting families.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    # Corner heights: alternate low / high to create saddle surface
    z_low = stud_top_z + 0.25
    z_high = stud_top_z + 1.20

    A = (0.0, 0.0, z_high)   # SW high
    B = (L,   0.0, z_low)    # SE low
    C = (L,   W,   z_high)   # NE high
    D = (0.0, W,   z_low)    # NW low

    # Family 1: rulings from AB to DC
    n1 = int(L / base.JOIST_SPACING) + 1
    rafter_w = base.JOIST_WIDTH
    rafter_d = base.JOIST_DEPTH

    for i in range(n1):
        t = i / max(1, n1 - 1)
        p0 = lerp(A, B, t)
        p1 = lerp(D, C, t)
        add_segment_between_points(
            f"Roof_Rul_1_{i:02d}",
            p0,
            p1,
            thickness_y=rafter_w,
            thickness_z=rafter_d,
        )

    # Family 2: rulings from AD to BC (secondary rafters / purlins)
    n2 = int(W / base.JOIST_SPACING) + 1
    for j in range(n2):
        s = j / max(1, n2 - 1)
        q0 = lerp(A, D, s)
        q1 = lerp(B, C, s)
        add_segment_between_points(
            f"Roof_Rul_2_{j:02d}",
            q0,
            q1,
            thickness_y=rafter_w * 0.75,
            thickness_z=rafter_d * 0.75,
        )


# ---------------------------------------------------------------------------
# MAIN ASSEMBLY
# ---------------------------------------------------------------------------

def build_gehry_ruled_unit():
    floor_z, floor_top_z, stud_base_z, stud_top_z = compute_base_levels()

    # Walls as ruled surfaces
    build_ruled_walls(floor_top_z, stud_base_z, stud_top_z)

    # Roof as hyperbolic paraboloid
    build_hypar_roof(stud_top_z)


# Execute immediately when this script runs inside Blender
build_gehry_ruled_unit()
