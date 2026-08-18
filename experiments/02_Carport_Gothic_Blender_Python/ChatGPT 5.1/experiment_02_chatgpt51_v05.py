# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 02 - CHATGPT 5.1 - V05
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
POST_SIZE   = 0.20    # posts (square)
BEAM_SIZE   = 0.20    # main beams / rafters
PURLIN_SIZE = 0.14    # purlins (slightly slimmer)

# Plan / elevation
FRAME_WIDTH = 4.0     # overall width (X), outside of posts
BAY_LENGTH  = 3.0     # bay spacing in Y
NUM_BAYS    = 3       # number of bays along length

EAVE_HEIGHT    = 3.0
ROOF_PITCH_DEG = 45.0

# Roof grid
NUM_PURLINS = 7       # per slope, between eave and ridge

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

    base = Vector((1.0, 0.0, 0.0))  # +X axis
    dot = max(min(base.dot(dir_n), 1.0), -1.0)

    if abs(dot - 1.0) < 1e-6:
        axis = (0.0, 0.0, 1.0)
        angle_deg = 0.0
    elif abs(dot + 1.0) < 1e-6:
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
    Longer knee braces from mid-high post up towards the tie,
    slightly inboard from the posts, giving a stronger triangular frame.
    """
    # Start a bit above half the post height
    start_z = EAVE_HEIGHT * 0.55
    # End fairly inboard along the tie
    inset_x = HALF_SPAN * 0.45

    # Left brace
    p_post = (-HALF_SPAN, y, start_z)
    p_tie  = (-inset_x,   y, EAVE_HEIGHT)
    beam_between(f"knee_{index}_L", p_post, p_tie, BEAM_SIZE * 0.6)

    # Right brace
    p_post = ( HALF_SPAN, y, start_z)
    p_tie  = ( inset_x,   y, EAVE_HEIGHT)
    beam_between(f"knee_{index}_R", p_post, p_tie, BEAM_SIZE * 0.6)


def make_gable_truss_details(index, y, eave_L, eave_R, ridge):
    """
    Gable truss to match the reference:
    - Two short vertical posts from main tie up to the collar (aligned with rafters)
    - Collar between these posts
    - King post from collar up to ridge
    - Symmetric X braces between short vertical posts
        * left_bottom  -> right_top
        * right_bottom -> left_top
    """
    # Height factor for collar: roughly midway between tie and ridge
    t_collar = 0.50

    # Collar endpoints along the rafters
    collar_L = lerp(eave_L, ridge, t_collar)
    collar_R = lerp(eave_R, ridge, t_collar)

    # Short vertical posts from tie (z = EAVE_HEIGHT) up to collar points
    left_bottom  = (collar_L[0], y, EAVE_HEIGHT)
    right_bottom = (collar_R[0], y, EAVE_HEIGHT)

    beam_between(f"panel_post_L_{index}", left_bottom,  collar_L, BEAM_SIZE * 0.8)
    beam_between(f"panel_post_R_{index}", right_bottom, collar_R, BEAM_SIZE * 0.8)

    # Collar beam between the tops of these posts
    beam_between(f"collar_{index}", collar_L, collar_R, BEAM_SIZE * 0.8)

    # King post from collar midpoint up to ridge
    collar_mid = (
        (collar_L[0] + collar_R[0]) * 0.5,
        y,
        (collar_L[2] + collar_R[2]) * 0.5,
    )
    beam_between(f"king_{index}", collar_mid, ridge, BEAM_SIZE * 0.7)

    # X braces: bottom of one short post to top of the opposite one
    beam_between(f"diag_{index}_A", left_bottom,  collar_R, BEAM_SIZE * 0.6)
    beam_between(f"diag_{index}_B", right_bottom, collar_L, BEAM_SIZE * 0.6)


def make_purlins():
    """
    Purlins parallel to the ridge on both slopes, at regular positions
    up from eave to ridge. Slimmer than rafters for clearer hierarchy.
    """
    eave_L_2d = (-HALF_SPAN, 0.0, EAVE_HEIGHT)
    eave_R_2d = ( HALF_SPAN, 0.0, EAVE_HEIGHT)
    ridge_2d  = (0.0,       0.0, RIDGE_HEIGHT)

    for j in range(NUM_PURLINS):
        t = (j + 1) / (NUM_PURLINS + 1)  # avoid exact eave and ridge

        # Left slope
        xL = eave_L_2d[0] + (ridge_2d[0] - eave_L_2d[0]) * t
        zL = eave_L_2d[2] + (ridge_2d[2] - eave_L_2d[2]) * t
        p1L = (xL, 0.0,          zL)
        p2L = (xL, TOTAL_LENGTH, zL)
        beam_between(f"purlin_L_{j:02d}", p1L, p2L, PURLIN_SIZE)

        # Right slope
        xR = eave_R_2d[0] + (ridge_2d[0] - eave_R_2d[0]) * t
        zR = eave_R_2d[2] + (ridge_2d[2] - eave_R_2d[2]) * t
        p1R = (xR, 0.0,          zR)
        p2R = (xR, TOTAL_LENGTH, zR)
        beam_between(f"purlin_R_{j:02d}", p1R, p2R, PURLIN_SIZE)


# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_frame()
