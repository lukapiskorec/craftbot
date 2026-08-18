# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 02 - CHATGPT 5.1 - V02
# DESCRIPTION: CARPORT TIMBER FRAME GOTHIC
# ------------------------------------------------------------------

import bpy
import importlib
import math

import craftbot_lib as craftbot
importlib.reload(craftbot)


# ------------------------------------------------------------------
# GLOBAL PARAMETERS
# ------------------------------------------------------------------

# Cross-sections
POST_SIZE = 0.20    # posts (square)
BEAM_SIZE = 0.20    # beams / rafters

# Plan / elevation
FRAME_WIDTH = 4.0   # overall width (X), outside of posts
BAY_LENGTH  = 3.0   # bay spacing in Y
NUM_BAYS    = 3     # number of bays along length

EAVE_HEIGHT   = 3.0
ROOF_PITCH_DEG = 45.0

# Roof grid
NUM_PURLINS = 7     # per slope, between eave and ridge

# Derived
NUM_BENTS    = NUM_BAYS + 1
TOTAL_LENGTH = NUM_BAYS * BAY_LENGTH
HALF_SPAN    = FRAME_WIDTH / 2.0

ROOF_PITCH_RAD = math.radians(ROOF_PITCH_DEG)
ROOF_RISE      = math.tan(ROOF_PITCH_RAD) * HALF_SPAN
RIDGE_HEIGHT   = EAVE_HEIGHT + ROOF_RISE


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------

def beam_between(name, p1, p2, size=BEAM_SIZE):
    """
    Place a rectangular timber between two 3D points p1 and p2.
    The local X axis of the cube is aligned along the segment.
    """
    from mathutils import Vector
    from math import acos, degrees

    v1 = Vector(p1)
    v2 = Vector(p2)
    direction = v2 - v1
    length = direction.length
    if length == 0:
        return

    mid = v1 + 0.5 * direction
    dir_n = direction.normalized()

    # Rotate from +X to desired direction using axis-angle
    base = Vector((1.0, 0.0, 0.0))
    dot = max(min(base.dot(dir_n), 1.0), -1.0)

    if abs(dot - 1.0) < 1e-6:
        # already aligned
        axis = (0.0, 0.0, 1.0)
        angle_deg = 0.0
    elif abs(dot + 1.0) < 1e-6:
        # opposite direction
        axis = (0.0, 0.0, 1.0)
        angle_deg = 180.0
    else:
        axis_vec = base.cross(dir_n)
        axis_vec.normalize()
        axis = axis_vec
        angle_deg = degrees(acos(dot))

    scale = (length / 2.0, size / 2.0, size / 2.0)

    craftbot.place_element(
        name=name,
        loc=mid,
        axis=axis,
        angle=angle_deg,
        scale=scale,
    )


def lerp(a, b, t):
    """Linear interpolation between two 3D points a, b."""
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


# ------------------------------------------------------------------
# FRAME CONSTRUCTION
# ------------------------------------------------------------------

def build_frame():
    # Clean scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    bent_positions = [i * BAY_LENGTH for i in range(NUM_BENTS)]

    # --------------------------------------------------------------
    # 1. POSTS + TIE BEAMS (ALL BENTS)
    # --------------------------------------------------------------
    for i, y in enumerate(bent_positions):
        left_base  = (-HALF_SPAN, y, 0.0)
        left_top   = (-HALF_SPAN, y, EAVE_HEIGHT)
        right_base = ( HALF_SPAN, y, 0.0)
        right_top  = ( HALF_SPAN, y, EAVE_HEIGHT)

        beam_between(f"post_{i}_L", left_base, left_top, POST_SIZE)
        beam_between(f"post_{i}_R", right_base, right_top, POST_SIZE)

        # Tie beam across tops of posts
        beam_between(f"tie_{i}", left_top, right_top, BEAM_SIZE)

    # --------------------------------------------------------------
    # 2. SIDE PLATES ALONG LENGTH
    # --------------------------------------------------------------
    for side, x in (("L", -HALF_SPAN), ("R", HALF_SPAN)):
        p1 = (x, 0.0, EAVE_HEIGHT)
        p2 = (x, TOTAL_LENGTH, EAVE_HEIGHT)
        beam_between(f"plate_{side}", p1, p2, BEAM_SIZE)

    # --------------------------------------------------------------
    # 3. RAFTERS + BRACES ON EACH BENT
    # --------------------------------------------------------------
    for i, y in enumerate(bent_positions):
        make_bent(i, y)

    # --------------------------------------------------------------
    # 4. RIDGE BOARD
    # --------------------------------------------------------------
    ridge_start = (0.0, 0.0, RIDGE_HEIGHT)
    ridge_end   = (0.0, TOTAL_LENGTH, RIDGE_HEIGHT)
    beam_between("ridge", ridge_start, ridge_end, BEAM_SIZE * 0.7)

    # --------------------------------------------------------------
    # 5. PURLINS (PARALLEL TO RIDGE)
    # --------------------------------------------------------------
    make_purlins()


def make_bent(index, y):
    """
    Build the vertical 2D frame lying in X–Z at position y.
    Common parts for all bents:
      - pair of rafters
      - knee braces
    Gable bents (0 and last) get extra truss detailing.
    """
    # 3D reference points at this y
    eave_L = (-HALF_SPAN, y, EAVE_HEIGHT)
    eave_R = ( HALF_SPAN, y, EAVE_HEIGHT)
    ridge  = (0.0,       y, RIDGE_HEIGHT)

    # Principal rafters
    beam_between(f"rafter_{index}_L", eave_L, ridge, BEAM_SIZE)
    beam_between(f"rafter_{index}_R", eave_R, ridge, BEAM_SIZE)

    # Knee braces on all bents
    add_knee_braces(index, y)

    # Gable truss detail only on end bents
    if index in (0, NUM_BENTS - 1):
        make_gable_truss_details(index, y, eave_L, eave_R, ridge)


def add_knee_braces(index, y):
    """
    Longer knee braces from mid-post up to the tie beam, both sides.
    This gives a clearer triangular frame than short stubs.
    """
    bottom_z = EAVE_HEIGHT * 0.35
    inset_x = 0.7

    # Left
    p_post_low = (-HALF_SPAN, y, bottom_z)
    p_tie_near = (-HALF_SPAN + inset_x, y, EAVE_HEIGHT)
    beam_between(f"knee_{index}_L", p_post_low, p_tie_near, BEAM_SIZE * 0.6)

    # Right
    p_post_low = ( HALF_SPAN, y, bottom_z)
    p_tie_near = ( HALF_SPAN - inset_x, y, EAVE_HEIGHT)
    beam_between(f"knee_{index}_R", p_post_low, p_tie_near, BEAM_SIZE * 0.6)


def make_gable_truss_details(index, y, eave_L, eave_R, ridge):
    """
    Extra members for the end bents to approximate the reference gable:
    - Collar between rafters
    - King post (up and a short extension down)
    - Crossed internal braces creating an "X" web.
    """
    # Collar between rafters at about 60% height between eave and ridge
    t_collar = 0.6
    collar_L = lerp(eave_L, ridge, t_collar)
    collar_R = lerp(eave_R, ridge, t_collar)
    beam_between(f"collar_{index}", collar_L, collar_R, BEAM_SIZE * 0.8)

    # King post: collar mid to ridge
    collar_mid = (
        (collar_L[0] + collar_R[0]) * 0.5,
        y,
        (collar_L[2] + collar_R[2]) * 0.5,
    )
    king_top = (0.0, y, RIDGE_HEIGHT)
    beam_between(f"king_{index}_upper", collar_mid, king_top, BEAM_SIZE * 0.7)

    # Lower king post extension down towards tie
    tie_mid = (0.0, y, EAVE_HEIGHT)
    mid_down = lerp(tie_mid, collar_mid, 0.45)
    beam_between(f"king_{index}_lower", tie_mid, mid_down, BEAM_SIZE * 0.7)

    # Crossed internal braces from tie mid to collar ends (approximate "X")
    beam_between(f"web_{index}_A", tie_mid, collar_R, BEAM_SIZE * 0.6)
    beam_between(f"web_{index}_B", tie_mid, collar_L, BEAM_SIZE * 0.6)


def make_purlins():
    """
    Purlins parallel to the ridge on both slopes, at regular positions
    up from eave to ridge. These, together with the rafters at each bent,
    form a roof grid closer to the reference model.
    """
    # 2D references in X–Z for interpolation
    eave_L_2d = (-HALF_SPAN, 0.0, EAVE_HEIGHT)
    eave_R_2d = ( HALF_SPAN, 0.0, EAVE_HEIGHT)
    ridge_2d  = (0.0,       0.0, RIDGE_HEIGHT)

    for j in range(NUM_PURLINS):
        t = (j + 1) / (NUM_PURLINS + 1)  # keeps away from exact eave & ridge

        # Left slope
        xL = eave_L_2d[0] + (ridge_2d[0] - eave_L_2d[0]) * t
        zL = eave_L_2d[2] + (ridge_2d[2] - eave_L_2d[2]) * t
        p1L = (xL, 0.0, zL)
        p2L = (xL, TOTAL_LENGTH, zL)
        beam_between(f"purlin_L_{j:02d}", p1L, p2L, BEAM_SIZE * 0.6)

        # Right slope
        xR = eave_R_2d[0] + (ridge_2d[0] - eave_R_2d[0]) * t
        zR = eave_R_2d[2] + (ridge_2d[2] - eave_R_2d[2]) * t
        p1R = (xR, 0.0, zR)
        p2R = (xR, TOTAL_LENGTH, zR)
        beam_between(f"purlin_R_{j:02d}", p1R, p2R, BEAM_SIZE * 0.6)


# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_frame()
