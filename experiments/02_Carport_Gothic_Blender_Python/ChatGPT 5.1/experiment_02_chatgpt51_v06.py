# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 02 - CHATGPT 5.1 - V06
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

POST_SIZE   = 0.20
BEAM_SIZE   = 0.20
PURLIN_SIZE = 0.14

FRAME_WIDTH = 4.0
BAY_LENGTH  = 3.0
NUM_BAYS    = 3

EAVE_HEIGHT    = 3.0
ROOF_PITCH_DEG = 45.0

NUM_PURLINS = 7

NUM_BENTS    = NUM_BAYS + 1
TOTAL_LENGTH = NUM_BAYS * BAY_LENGTH
HALF_SPAN    = FRAME_WIDTH / 2.0

ROOF_PITCH_RAD = math.radians(ROOF_PITCH_DEG)
ROOF_RISE      = math.tan(ROOF_PITCH_RAD) * HALF_SPAN
RIDGE_HEIGHT   = EAVE_HEIGHT + ROOF_RISE


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def beam_between(name, p1, p2, size=BEAM_SIZE):
    """Place rectangular timber between points p1 and p2."""
    from mathutils import Vector
    from math import acos, degrees

    v1 = Vector(p1)
    v2 = Vector(p2)
    direction = v2 - v1
    length = direction.length
    if length == 0:
        return

    mid = (v1 + v2) * 0.5
    dir_n = direction.normalized()

    base = Vector((1.0, 0.0, 0.0))
    dot = max(min(base.dot(dir_n), 1.0), -1.0)

    if abs(dot - 1.0) < 1e-6:
        axis = (0,0,1)
        angle_deg = 0
    elif abs(dot + 1.0) < 1e-6:
        axis = (0,0,1)
        angle_deg = 180
    else:
        axis_vec = base.cross(dir_n).normalized()
        angle_deg = degrees(acos(dot))
        axis = axis_vec

    scale = (length * 0.5, size * 0.5, size * 0.5)

    craftbot.place_element(
        name=name,
        loc=mid,
        axis=axis,
        angle=angle_deg,
        scale=scale
    )


def lerp(a, b, t):
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


# ------------------------------------------------------------------
# MAIN BUILD
# ------------------------------------------------------------------

def build_frame():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    bent_positions = [i * BAY_LENGTH for i in range(NUM_BENTS)]

    # POSTS + TIE BEAMS
    for i, y in enumerate(bent_positions):
        Lb = (-HALF_SPAN, y, 0)
        Lt = (-HALF_SPAN, y, EAVE_HEIGHT)
        Rb = ( HALF_SPAN, y, 0)
        Rt = ( HALF_SPAN, y, EAVE_HEIGHT)

        beam_between(f"post_L_{i}", Lb, Lt, POST_SIZE)
        beam_between(f"post_R_{i}", Rb, Rt, POST_SIZE)

        beam_between(f"tie_{i}", Lt, Rt, BEAM_SIZE)

    # SIDE PLATES
    for name, x in (("L",-HALF_SPAN), ("R",HALF_SPAN)):
        beam_between(f"plate_{name}", (x,0,EAVE_HEIGHT), (x,TOTAL_LENGTH,EAVE_HEIGHT), BEAM_SIZE)

    # RAFTERS + BRACES + TRUSS
    for i,y in enumerate(bent_positions):
        make_bent(i,y)

    # RIDGE
    beam_between("ridge", (0,0,RIDGE_HEIGHT), (0,TOTAL_LENGTH,RIDGE_HEIGHT), BEAM_SIZE*0.7)

    # PURLINS
    make_purlins()


def make_bent(index, y):
    eL = (-HALF_SPAN, y, EAVE_HEIGHT)
    eR = ( HALF_SPAN, y, EAVE_HEIGHT)
    ridge = (0, y, RIDGE_HEIGHT)

    beam_between(f"rafter_L_{index}", eL, ridge)
    beam_between(f"rafter_R_{index}", eR, ridge)

    add_knee_braces(index,y)

    if index in (0, NUM_BENTS-1):
        make_gable_truss(index, y, eL, eR, ridge)


def add_knee_braces(index,y):
    start_z = EAVE_HEIGHT * 0.55
    inset_x = HALF_SPAN * 0.45

    beam_between(
        f"knee_L_{index}",
        (-HALF_SPAN, y, start_z),
        (-inset_x,  y, EAVE_HEIGHT),
        BEAM_SIZE*0.6
    )
    beam_between(
        f"knee_R_{index}",
        ( HALF_SPAN, y, start_z),
        ( inset_x,  y, EAVE_HEIGHT),
        BEAM_SIZE*0.6
    )


# ------------------------------------------------------------------
# CORRECT GABLE TRUSS
# ------------------------------------------------------------------

def make_gable_truss(index, y, eave_L, eave_R, ridge):

    # Collar slightly lower than 50% for better match (visual check)
    t_collar = 0.43

    left_top  = lerp(eave_L, ridge, t_collar)
    right_top = lerp(eave_R, ridge, t_collar)

    # Short posts bottom (at tie elevation)
    left_bottom  = (left_top[0],  y, EAVE_HEIGHT)
    right_bottom = (right_top[0], y, EAVE_HEIGHT)

    # Short posts
    beam_between(f"short_L_{index}", left_bottom, left_top, BEAM_SIZE*0.8)
    beam_between(f"short_R_{index}", right_bottom, right_top, BEAM_SIZE*0.8)

    # Collar
    beam_between(f"collar_{index}", left_top, right_top, BEAM_SIZE*0.8)

    # King post
    collar_mid = (
        (left_top[0] + right_top[0])*0.5,
        y,
        (left_top[2] + right_top[2])*0.5
    )
    beam_between(f"king_{index}", collar_mid, ridge, BEAM_SIZE*0.7)

    # X BRACING (correct nodes)
    beam_between(f"x_A_{index}", left_bottom,  right_top, BEAM_SIZE*0.6)
    beam_between(f"x_B_{index}", right_bottom, left_top,  BEAM_SIZE*0.6)


# ------------------------------------------------------------------
# PURLINS
# ------------------------------------------------------------------

def make_purlins():
    eL = (-HALF_SPAN, 0, EAVE_HEIGHT)
    eR = ( HALF_SPAN, 0, EAVE_HEIGHT)
    r  = (0,0,RIDGE_HEIGHT)

    for j in range(NUM_PURLINS):
        t = (j+1)/(NUM_PURLINS+1)

        xL = eL[0] + (r[0]-eL[0])*t
        zL = eL[2] + (r[2]-eL[2])*t
        beam_between(f"purlin_L_{j:02d}", (xL,0,zL), (xL,TOTAL_LENGTH,zL), PURLIN_SIZE)

        xR = eR[0] + (r[0]-eR[0])*t
        zR = eR[2] + (r[2]-eR[2])*t
        beam_between(f"purlin_R_{j:02d}", (xR,0,zR), (xR,TOTAL_LENGTH,zR), PURLIN_SIZE)


# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_frame()
