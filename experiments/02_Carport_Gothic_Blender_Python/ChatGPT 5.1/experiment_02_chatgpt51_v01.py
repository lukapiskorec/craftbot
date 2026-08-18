# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 02 - CHATGPT 5.1 - V01
# DESCRIPTION: CARPORT TIMBER FRAME GOTHIC
# ------------------------------------------------------------------

import bpy
import importlib
import math

import craftbot_lib as craftbot

importlib.reload(craftbot)  # handy while developing


# ------------------------------------------------------------------
# PARAMETERS (EDITABLE)
# ------------------------------------------------------------------

# Global sizes (in meters; Blender default units)
POST_SIZE = 0.20        # square posts 0.2 x 0.2
BEAM_SIZE = 0.20        # tie beams, plates, rafters thickness
FRAME_WIDTH = 4.0       # overall width in X (outside to outside of posts)
BAY_LENGTH = 3.0        # spacing between bents in Y
NUM_BAYS = 3            # number of bays along length (3 bays -> 4 bents)

EAVE_HEIGHT = 3.0       # top of posts / underside of tie beams
ROOF_PITCH_DEG = 45.0   # roof pitch
RAFTER_SPACING = 0.6    # along length (Y) between common rafters
BATTEN_SPACING = 0.35   # along roof slope between battens

# Derived values
NUM_BENTS = NUM_BAYS + 1
TOTAL_LENGTH = NUM_BAYS * BAY_LENGTH

HALF_SPAN = FRAME_WIDTH / 2.0
ROOF_PITCH_RAD = math.radians(ROOF_PITCH_DEG)

# For 45°: rise = HALF_SPAN; more generally:
ROOF_RISE = math.tan(ROOF_PITCH_RAD) * HALF_SPAN
RIDGE_HEIGHT = EAVE_HEIGHT + ROOF_RISE

# ------------------------------------------------------------------
# SMALL HELPERS
# ------------------------------------------------------------------


def box_along(axis, length, size):
    """
    Return scale tuple for a box with length along given axis ('x','y','z')
    and square cross-section of `size`.

    place_element uses a 2x2x2 cube, so we scale by length/2 and size/2.
    """
    half_len = length / 2.0
    half_size = size / 2.0

    if axis == 'x':
        return (half_len, half_size, half_size)
    elif axis == 'y':
        return (half_size, half_len, half_size)
    elif axis == 'z':
        return (half_size, half_size, half_len)
    else:
        raise ValueError("axis must be 'x', 'y', or 'z'")


def place_post(name, x, y, height=EAVE_HEIGHT, size=POST_SIZE):
    """Vertical post with base on z=0."""
    z_mid = height / 2.0
    scale = box_along('z', height, size)
    craftbot.place_element(
        name=name,
        loc=(x, y, z_mid),
        axis=(0, 0, 1),
        angle=0.0,
        scale=scale
    )


def place_beam_x(name, y, z, length=FRAME_WIDTH, size=BEAM_SIZE):
    """Horizontal beam spanning along X at given Y,Z."""
    x_mid = 0.0
    scale = box_along('x', length, size)
    craftbot.place_element(
        name=name,
        loc=(x_mid, y, z),
        axis=(0, 0, 1),
        angle=0.0,
        scale=scale
    )


def place_beam_y(name, x, z, length=BAY_LENGTH, size=BEAM_SIZE):
    """Horizontal beam spanning along Y at given X,Z."""
    y_mid = length / 2.0
    scale = box_along('y', length, size)
    craftbot.place_element(
        name=name,
        loc=(x, y_mid, z),
        axis=(0, 0, 1),
        angle=0.0,
        scale=scale
    )


def place_rafter_gable(name, side, y_pos):
    """
    Principal rafter in gable frame, running in X-Z plane.
    side: 'left' or 'right'
    y_pos: Y location of the bent
    """

    # Geometric data
    run = HALF_SPAN           # horizontal from center to post
    rise = ROOF_RISE          # vertical from eave to ridge
    length = math.sqrt(run**2 + rise**2)

    # Midpoint of rafter
    if side == 'left':
        x_eave = -HALF_SPAN
    elif side == 'right':
        x_eave = HALF_SPAN
    else:
        raise ValueError("side must be 'left' or 'right'")

    z_eave = EAVE_HEIGHT
    x_ridge = 0.0
    z_ridge = RIDGE_HEIGHT

    x_mid = (x_eave + x_ridge) / 2.0
    z_mid = (z_eave + z_ridge) / 2.0

    # Rotation: start from beam along +X, rotate around Y by +pitch
    # For left side the slope goes up towards +X; for right side we flip angle.
    angle_deg = ROOF_PITCH_DEG if side == 'left' else -ROOF_PITCH_DEG

    scale = box_along('x', length, BEAM_SIZE)

    craftbot.place_element(
        name=name,
        loc=(x_mid, y_pos, z_mid),
        axis=(0, 1, 0),
        angle=angle_deg,
        scale=scale
    )


def place_common_rafter(name, y_pos):
    """
    Common rafter pair (left and right) at a given Y.
    Uses same geometry as gable rafters, but positioned along Y.
    """
    place_rafter_gable(name + "_L", "left", y_pos)
    place_rafter_gable(name + "_R", "right", y_pos)


def place_batten_row(name_prefix, y_pos):
    """
    Place a line of battens at a given Y across both roof slopes.
    Each batten is a short beam along Y attached to surface of rafters.
    For simplicity we place them in X direction just below the roof surface
    at a fixed Z offset along the slope.
    """
    # Batten width along Y spans total length, but here this function
    # is called per rafter line (so we make short battens along X instead).
    # We'll instead make battens along Y at two X positions (left and right)
    # close to the roof surfaces.

    # Small offset down from roof surface
    offset_down = 0.05

    # For left slope
    x_left = -HALF_SPAN + BEAM_SIZE / 2.0
    z_left = EAVE_HEIGHT + (ROOF_RISE - offset_down) * (abs(x_left) / HALF_SPAN)
    craftbot.place_element(
        name=name_prefix + "_left",
        loc=(x_left, y_pos, z_left),
        axis=(0, 0, 1),
        angle=0.0,
        scale=box_along('y', BEAM_SIZE * 1.5, BEAM_SIZE / 2.0)
    )

    # For right slope
    x_right = HALF_SPAN - BEAM_SIZE / 2.0
    z_right = EAVE_HEIGHT + (ROOF_RISE - offset_down) * (abs(x_right) / HALF_SPAN)
    craftbot.place_element(
        name=name_prefix + "_right",
        loc=(x_right, y_pos, z_right),
        axis=(0, 0, 1),
        angle=0.0,
        scale=box_along('y', BEAM_SIZE * 1.5, BEAM_SIZE / 2.0)
    )


def place_knee_brace(name, x_post, y_bent, up_direction):
    """
    Knee brace between post and tie beam in gable frame.
    up_direction: +1 or -1 to control orientation along X.
    """

    brace_length = 1.0
    angle_deg = 45.0 * up_direction

    # Midpoint approx between post upper corner and tie beam
    x_mid = x_post - up_direction * (POST_SIZE / 2.0)
    y_mid = y_bent
    z_mid = EAVE_HEIGHT - POST_SIZE / 2.0

    craftbot.place_element(
        name=name,
        loc=(x_mid, y_mid, z_mid),
        axis=(0, 1, 0),   # rotate in X-Z plane
        angle=angle_deg,
        scale=box_along('x', brace_length, BEAM_SIZE / 1.5)
    )


def place_king_post_and_collar(prefix, y_bent):
    """King post and collar in gable bent."""
    # King post
    kp_height = RIDGE_HEIGHT - EAVE_HEIGHT
    kp_z_mid = (EAVE_HEIGHT + RIDGE_HEIGHT) / 2.0
    craftbot.place_element(
        name=prefix + "_king_post",
        loc=(0.0, y_bent, kp_z_mid),
        axis=(0, 0, 1),
        angle=0.0,
        scale=box_along('z', kp_height, BEAM_SIZE * 0.8)
    )

    # Collar at mid-height between tie and ridge
    z_collar = (EAVE_HEIGHT + RIDGE_HEIGHT) / 2.0
    place_beam_x(prefix + "_collar", y=y_bent, z=z_collar,
                 length=FRAME_WIDTH * 0.9, size=BEAM_SIZE * 0.8)


# ------------------------------------------------------------------
# BUILD THE FRAME
# ------------------------------------------------------------------

def build_timber_frame():
    # Optional: delete existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # ---- Posts for all bents ----
    bent_positions = [i * BAY_LENGTH for i in range(NUM_BENTS)]

    for i, y_bent in enumerate(bent_positions):
        for side, x in (("L", -HALF_SPAN), ("R", HALF_SPAN)):
            place_post(f"post_{i}_{side}", x, y_bent)

    # ---- Tie beams / eaves beams per bent (across width) ----
    for i, y_bent in enumerate(bent_positions):
        place_beam_x(f"tie_beam_{i}", y=y_bent, z=EAVE_HEIGHT)

    # ---- Longitudinal wall plates along each side ----
    for side, x in (("L", -HALF_SPAN), ("R", HALF_SPAN)):
        craftbot.place_element(
            name=f"wall_plate_{side}",
            loc=(x, TOTAL_LENGTH / 2.0, EAVE_HEIGHT),
            axis=(0, 0, 1),
            angle=0.0,
            scale=box_along('y', TOTAL_LENGTH, BEAM_SIZE)
        )

    # ---- End trusses (front and back) ----
    for label, y_bent in (("front", bent_positions[0]),
                          ("back", bent_positions[-1])):

        # Principal rafters
        place_rafter_gable(f"rafter_{label}_L", "left", y_bent)
        place_rafter_gable(f"rafter_{label}_R", "right", y_bent)

        # King post + collar
        place_king_post_and_collar(f"truss_{label}", y_bent)

        # Knee braces from posts to tie beam
        place_knee_brace(f"knee_{label}_L", -HALF_SPAN, y_bent, up_direction=+1)
        place_knee_brace(f"knee_{label}_R", HALF_SPAN, y_bent, up_direction=-1)

    # ---- Ridge beam ----
    craftbot.place_element(
        name="ridge_beam",
        loc=(0.0, TOTAL_LENGTH / 2.0, RIDGE_HEIGHT),
        axis=(0, 0, 1),
        angle=0.0,
        scale=box_along('y', TOTAL_LENGTH, BEAM_SIZE * 0.8)
    )

    # ---- Common rafters along length ----
    num_rafters = int(TOTAL_LENGTH / RAFTER_SPACING) + 1
    for i in range(num_rafters):
        y = i * RAFTER_SPACING
        if y > TOTAL_LENGTH:
            continue
        place_common_rafter(f"rafter_{i:02d}", y)

    # ---- Roof battens (optional, simplified) ----
    # We place batten rows along length at regular spacing.
    # For simplicity: sample along roof run using the rafter length.
    run = HALF_SPAN
    rise = ROOF_RISE
    rafter_length = math.sqrt(run**2 + rise**2)
    num_battens = int(rafter_length / BATTEN_SPACING)

    for j in range(num_battens):
        # approximate y positions evenly along length
        y = (j / max(1, num_battens - 1)) * TOTAL_LENGTH
        place_batten_row(f"batten_{j:02d}", y)


# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_timber_frame()
