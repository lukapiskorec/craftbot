# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 07 - CHATGPT 5.1 - V01
# GEHRY DECONSTRUCTED LIVING UNIT
#
# DESCRIPTION:
#   1) Imports experiment_04_chatgpt51_v14 to build the simple timber box.
#   2) Computes reference levels (floor, wall-top, ridge) from the same
#      parameters.
#   3) Adds a set of deconstructivist interventions inspired by Gehry:
#        - South-facing sloped glass wedge (ruled surface).
#        - Secondary fractured glass plane at roof level.
#        - Corrugated “shards” wrapping the box on east/west sides.
#        - Tilted / fractured opening frames on the south façade.
#        - Dynamic interior glulam “fan” beams and a suspended mezzanine.
#
#   All geometry is assembled using craftbot_lib.place_element().
# ------------------------------------------------------------------

import bpy
import importlib
import math

import craftbot_lib as craftbot
import experiment_04_chatgpt51_v14 as base  # builds the original house on import

# Always reload to make sure we are using the latest versions in Blender
importlib.reload(craftbot)
importlib.reload(base)

# ---------------------------------------------------------------------------
# SMALL HELPERS
# ---------------------------------------------------------------------------

def half(x: float) -> float:
    return 0.5 * x


def add_box_euler(
    name: str,
    loc: tuple,
    size: tuple,
    rot_deg: tuple = (0.0, 0.0, 0.0),
    euler_order: str = "XYZ",
):
    """
    Convenience wrapper around craftbot.place_element for an arbitrarily
    rotated box defined by its center, full size and Euler angles in degrees.
    """
    rx, ry, rz = rot_deg
    sx, sy, sz = size
    craftbot.place_element(
        name=name,
        loc=loc,
        euler=(math.radians(rx), math.radians(ry), math.radians(rz)),
        euler_order=euler_order,
        scale=(half(sx), half(sy), half(sz)),
    )


def add_vertical_blade(
    name: str,
    x: float,
    y: float,
    z0: float,
    z1: float,
    thickness_x: float,
    width_y: float,
    rot_z_deg: float = 0.0,
):
    """
    Tall, thin vertical “blade” element, useful for corrugated shells or
    framing shards. Rotates around Z.
    """
    height = z1 - z0
    if height <= 0.0:
        return
    cz = z0 + half(height)
    add_box_euler(
        name,
        (x, y, cz),
        (thickness_x, width_y, height),
        rot_deg=(0.0, 0.0, rot_z_deg),
    )


# ---------------------------------------------------------------------------
# REFERENCE LEVELS AND GLOBAL SHORTCUTS
# (mirror base experiment_04_chatgpt51_v14)
# ---------------------------------------------------------------------------

def compute_reference_levels():
    """
    Reconstruct key Z-levels analytically from the parameters used in
    experiment_04_chatgpt51_v14 so we can place new geometry relative
    to the existing box.
    """
    P = base.PLATFORM_HEIGHT
    BD = base.BEARER_DEPTH
    JD = base.JOIST_DEPTH
    FT = base.FLOOR_THICK
    BPD = base.BOTTOM_PLATE_DEPTH
    TPD = base.TOP_PLATE_DEPTH
    STUD = base.WALL_STUD_HEIGHT

    # From build_platform()
    floor_z = P + BD + JD + half(FT)
    floor_top_z = floor_z + half(FT)

    # From build_walls()
    wall_top_z = floor_top_z + BPD + STUD + TPD

    # Roof rise / ridge from build_roof()
    span_half = half(base.HOUSE_WID)
    theta = math.radians(base.ROOF_PITCH_DEG)
    roof_rise = span_half * math.tan(theta)
    ridge_z = wall_top_z + roof_rise

    return floor_z, floor_top_z, wall_top_z, ridge_z


# ---------------------------------------------------------------------------
# GEHRY-INSPIRED INTERVENTIONS
# ---------------------------------------------------------------------------

def build_south_glass_wedge(floor_top_z, wall_top_z):
    """
    Large sloped glass wedge leaning out of the south façade, echoing the
    Gehry kitchen greenhouse. Geometrically this is a single ruled surface
    (a plane) twisting slightly in plan.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    # Primary glass plane
    length_x = 0.65 * L
    depth_y = 2.2
    thickness_z = 0.06

    cx = 0.5 * L
    cy = -half(depth_y)  # extend to the south (negative Y, outside the box)
    cz = floor_top_z + 1.45

    # Strong outward tilt and slight twist in plan
    add_box_euler(
        "Glass_Wedge_Main",
        (cx, cy, cz),
        (length_x, depth_y, thickness_z),
        rot_deg=(-48.0, 0.0, 14.0),
    )

    # Secondary glass strip closer to the ridge, creating a split / fractured
    # greenhouse profile.
    length_x2 = 0.38 * L
    depth_y2 = 1.6
    thickness_z2 = 0.05

    cx2 = 0.68 * L
    cy2 = -0.35
    cz2 = wall_top_z + 0.45

    add_box_euler(
        "Glass_Wedge_Upper",
        (cx2, cy2, cz2),
        (length_x2, depth_y2, thickness_z2),
        rot_deg=(-32.0, 0.0, -9.0),
    )


def build_corrugated_shards(floor_z, wall_top_z):
    """
    Corrugated-metal-like shells wrapping the original timber box on the
    east and west, slightly rotated to break orthogonality and echo the
    layered wrappers of the Gehry residence.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    z0 = floor_z
    z1 = wall_top_z + 1.40  # extend a bit beyond the roof line

    shell_thickness = 0.12
    shell_width = 0.70

    # WEST shard - leans away and rotates slightly
    add_vertical_blade(
        "Shard_West_Main",
        x=0.18 * L,
        y=-half(shell_width) - 0.35,
        z0=z0,
        z1=z1,
        thickness_x=L * 0.38,
        width_y=shell_width,
        rot_z_deg=8.0,
    )

    # EAST shard - counter-rotated
    add_vertical_blade(
        "Shard_East_Main",
        x=0.82 * L,
        y=W + half(shell_width) + 0.35,
        z0=z0,
        z1=z1,
        thickness_x=L * 0.42,
        width_y=shell_width,
        rot_z_deg=-10.0,
    )

    # A lower “garden wall” shard on the south-west corner
    add_vertical_blade(
        "Shard_South_Low",
        x=0.12 * L,
        y=-0.90,
        z0=floor_z,
        z1=floor_z + 1.40,
        thickness_x=L * 0.26,
        width_y=0.30,
        rot_z_deg=18.0,
    )


def build_fractured_south_openings(floor_top_z, wall_top_z):
    """
    A set of tilted frames on the south façade marking fractured openings.
    They do not boolean-cut the wall, but visually suggest diagonal cuts
    and misaligned windows.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    frame_depth_y = 0.24   # projects slightly out of the south wall
    frame_thick_z = 0.10
    frame_height = 1.90

    base_z = floor_top_z + 0.85

    x_positions = [
        0.28 * L,
        0.50 * L,
        0.74 * L,
    ]
    z_rotations = [
        -18.0,
        7.0,
        -11.0,
    ]
    x_tilts = [
        12.0,
        -8.0,
        15.0,
    ]

    for i, (xp, rz, rx) in enumerate(zip(x_positions, z_rotations, x_tilts)):
        name = f"South_Fractured_Frame_{i:02d}"
        cz = base_z + half(frame_height)
        cy = -half(frame_depth_y)  # just in front of the south wall at y=0
        add_box_euler(
            name,
            (xp, cy, cz),
            (0.10, frame_depth_y, frame_height),
            rot_deg=(rx, 0.0, rz),
        )

    # A horizontal “cut” beam that slides across two of the frames
    cut_length = 0.40 * L
    cut_thickness = 0.08
    cut_height = 0.16

    add_box_euler(
        "South_Horizontal_Cut",
        (0.58 * L, -0.05, floor_top_z + 1.98),
        (cut_length, cut_thickness, cut_height),
        rot_deg=(0.0, 0.0, 14.0),
    )


def build_interior_fan_beams(floor_top_z, ridge_z):
    """
    Interior glulam fan: three heavy diagonal beams crossing the interior
    volume, rotating in plan and section to generate a dynamic space.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    # Common beam section (glulam)
    beam_thick_x = 0.22
    beam_thick_z = 0.40

    # Beam 1 – sweeping across the centre
    length_y1 = 1.35 * W
    cz1 = floor_top_z + 2.10
    add_box_euler(
        "Beam_Fan_01",
        (0.52 * L, 0.52 * W, cz1),
        (beam_thick_x, length_y1, beam_thick_z),
        rot_deg=(18.0, 21.0, 10.0),
    )

    # Beam 2 – rotated the other way, slightly higher
    length_y2 = 1.15 * W
    cz2 = floor_top_z + 2.55
    add_box_euler(
        "Beam_Fan_02",
        (0.40 * L, 0.60 * W, cz2),
        (beam_thick_x, length_y2, beam_thick_z),
        rot_deg=(-14.0, 26.0, -16.0),
    )

    # Beam 3 – almost vertical strut tying down the ridge
    length_y3 = 0.95 * W
    cz3 = half(floor_top_z + ridge_z) + 0.15
    add_box_euler(
        "Beam_Fan_03",
        (0.68 * L, 0.48 * W, cz3),
        (beam_thick_x, length_y3, beam_thick_z),
        rot_deg=(-32.0, 35.0, 4.0),
    )


def build_suspended_mezzanine(floor_top_z):
    """
    A small hanging mezzanine / gallery volume attached to the north side,
    reminiscent of the floating timber box in the later Gehry residence
    photographs.
    """
    L = base.HOUSE_LEN
    W = base.HOUSE_WID

    length_x = 0.46 * L
    depth_y = 1.25
    thickness_z = 0.45

    cx = 0.70 * L
    cy = 0.82 * W
    cz = floor_top_z + 2.15

    add_box_euler(
        "Mezzanine_Box",
        (cx, cy, cz),
        (length_x, depth_y, thickness_z),
        rot_deg=(0.0, 0.0, 4.0),
    )

    # Two skewed hangers tying mezzanine back to the roof
    hanger_thick = 0.10
    hanger_len_z = 1.20

    add_box_euler(
        "Mezzanine_Hanger_01",
        (cx - 0.16 * L, cy - 0.15, cz + half(hanger_len_z)),
        (hanger_thick, hanger_thick, hanger_len_z),
        rot_deg=(-10.0, -18.0, 6.0),
    )
    add_box_euler(
        "Mezzanine_Hanger_02",
        (cx + 0.12 * L, cy - 0.10, cz + half(hanger_len_z)),
        (hanger_thick, hanger_thick, hanger_len_z),
        rot_deg=(14.0, -22.0, -4.0),
    )


def build_deconstructive_layer():
    """
    Top-level function for all Gehry-inspired additions.
    Assumes the original box from experiment_04_chatgpt51_v14 has already
    been built (which happens automatically on module import).
    """
    floor_z, floor_top_z, wall_top_z, ridge_z = compute_reference_levels()

    build_south_glass_wedge(floor_top_z, wall_top_z)
    build_corrugated_shards(floor_z, wall_top_z)
    build_fractured_south_openings(floor_top_z, wall_top_z)
    build_interior_fan_beams(floor_top_z, ridge_z)
    build_suspended_mezzanine(floor_top_z)


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def build_gehry_unit():
    """
    1) The import of experiment_04_chatgpt51_v14 has already executed its
       build_house() call, creating the simple timber living unit.
    2) We now overlay the deconstructive interventions.
    """
    build_deconstructive_layer()


# Execute immediately when this script is run in Blender
build_gehry_unit()
