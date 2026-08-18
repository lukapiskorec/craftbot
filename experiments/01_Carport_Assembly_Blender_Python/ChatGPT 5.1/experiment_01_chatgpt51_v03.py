# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 01 - CHATGPT 5.1 - V03
# DESCRIPTION: CARPORT TIMBER FRAME ASSEMBLY
# ------------------------------------------------------------------

import bpy
import importlib
import math
from mathutils import Vector

import craftbot_lib as craftbot

# Ensure we pick up any edits to craftbot_lib without restarting Blender
importlib.reload(craftbot)


# ------------------------------------------------------------------
# GLOBAL PARAMETERS
# ------------------------------------------------------------------

# Global dimensions (meters)
LENGTH      = 7.2   # overall length along X (between end posts)
SPAN        = 5.0   # clear span between post rows along Y
NUM_BAYS    = 3     # number of bays along the length

# Vertical dimensions
EAVES_HEIGHT    = 2.4   # post height to wall plate / tie level
ROOF_PITCH_DEG  = 35.0  # roof pitch

# Member sections (square for simplicity)
POST_SIZE   = 0.18
PLATE_SIZE  = 0.18
TIE_SIZE    = 0.18
RAFTER_SIZE = 0.10
BRACE_SIZE  = 0.14

# Rafter spacing along length
RAFTER_SPACING = 0.6

# Roof overhang past eaves (horizontal projection in plan, along Y)
EAVE_OVERHANG = 0.45

# Bracing parameters
LONGITUDINAL_BRACE_POST_DROP = 0.35   # vertical drop of brace from top of post
TRANSVERSE_BRACE_POST_DROP   = 0.30   # same for knee-braces in Y
TRANSVERSE_BRACE_INSET_Y     = 0.70   # distance from post along tie for brace foot
TRUSS_TIE_FACTOR             = 0.60   # how far along tie the truss braces attach (0..1 from centre to post)
TRUSS_POST_THICKNESS_FACTOR  = 0.8    # king-post thickness relative to POST_SIZE


# ------------------------------------------------------------------
# DERIVED VALUES
# ------------------------------------------------------------------

HALF_SPAN   = SPAN / 2.0
BAY_LENGTH  = LENGTH / NUM_BAYS
PITCH_RAD   = math.radians(ROOF_PITCH_DEG)

# Ridge height so that z(HALF_SPAN) = EAVES_HEIGHT on the roof plane
RIDGE_HEIGHT = EAVES_HEIGHT + math.tan(PITCH_RAD) * HALF_SPAN

# X positions of bents (post frames)
BENT_X = [-LENGTH / 2.0 + i * BAY_LENGTH for i in range(NUM_BAYS + 1)]

# Y positions of post rows
ROW_Y = [-HALF_SPAN, +HALF_SPAN]


# ------------------------------------------------------------------
# HELPER: roof height as a function of Y-offset (absolute value)
# ------------------------------------------------------------------

def roof_z_at_y(abs_y: float) -> float:
    """Return roof height z at a given absolute horizontal distance from ridge.

    Parameters
    ----------
    abs_y : float
        Positive distance from ridge in plan (|y|).
    """
    return RIDGE_HEIGHT - math.tan(PITCH_RAD) * abs_y


# ------------------------------------------------------------------
# HELPER: place a prismatic element between two 3D points
# ------------------------------------------------------------------

def place_between(name, p0, p1, size_yz):
    """Place a rectangular prismatic timber between p0 and p1.

    The local +X axis of the cube is aligned with the segment p0→p1,
    and Y/Z are used for the square cross-section (size_yz).
    """
    p0_v = Vector(p0)
    p1_v = Vector(p1)
    mid  = 0.5 * (p0_v + p1_v)

    dir_vec = p1_v - p0_v
    length = dir_vec.length
    if length < 1e-6:
        return None

    dir_vec.normalize()

    # We want to rotate the cube so its local +X points along dir_vec.
    x_axis = Vector((1.0, 0.0, 0.0))

    # Handle almost-parallel and opposite cases explicitly
    if (dir_vec - x_axis).length < 1e-6:
        axis = (0.0, 0.0, 1.0)
        angle_deg = 0.0
    elif (dir_vec + x_axis).length < 1e-6:
        axis = (0.0, 0.0, 1.0)
        angle_deg = 180.0
    else:
        axis_vec = x_axis.cross(dir_vec)
        axis_vec.normalize()
        dot = max(-1.0, min(1.0, x_axis.dot(dir_vec)))
        angle_rad = math.acos(dot)
        angle_deg = math.degrees(angle_rad)
        axis = axis_vec

    return craftbot.place_element(
        name=name,
        loc=mid,
        axis=axis,
        angle=angle_deg,
        scale=(length * 0.5, size_yz * 0.5, size_yz * 0.5),
    )


# ------------------------------------------------------------------
# BUILD FUNCTIONS
# ------------------------------------------------------------------

def build_posts():
    """Create all vertical posts."""
    for j, y in enumerate(ROW_Y):
        for i, x in enumerate(BENT_X):
            base = (x, y, 0.0)
            top  = (x, y, EAVES_HEIGHT)
            name = f"Post_{j}_{i}"
            place_between(name, base, top, POST_SIZE)


def build_wall_plates():
    """Create wall plate segments along the long sides (eaves beams)."""
    for j, y in enumerate(ROW_Y):
        for i in range(len(BENT_X) - 1):
            x0 = BENT_X[i]
            x1 = BENT_X[i + 1]
            p0 = (x0, y, EAVES_HEIGHT)
            p1 = (x1, y, EAVES_HEIGHT)
            name = f"WallPlate_{j}_{i}"
            place_between(name, p0, p1, PLATE_SIZE)


def build_tie_beams():
    """Create tie beams across the width at each bent."""
    for i, x in enumerate(BENT_X):
        p0 = (x, -HALF_SPAN, EAVES_HEIGHT)
        p1 = (x, +HALF_SPAN, EAVES_HEIGHT)
        name = f"TieBeam_{i}"
        place_between(name, p0, p1, TIE_SIZE)


def build_longitudinal_braces():
    """Create diagonal braces between posts and wall plates along X.

    Braces start slightly below the plate on the post and connect to the
    plate in the next/previous bay, roughly matching the reference model.
    """
    # Braces only at intermediate bents (not at the very ends)
    for j, y in enumerate(ROW_Y):
        for i in range(1, len(BENT_X) - 1):
            x = BENT_X[i]

            # Upper point on post, just below plate
            z_low = EAVES_HEIGHT - LONGITUDINAL_BRACE_POST_DROP
            p_low = (x, y, z_low)

            # Upper points on wall plates, offset in X towards next / prev bay
            offset = BAY_LENGTH * 0.35
            p_high_fwd  = (x + offset, y, EAVES_HEIGHT)
            p_high_back = (x - offset, y, EAVES_HEIGHT)

            name_fwd  = f"LongBrace_F_{j}_{i}"
            name_back = f"LongBrace_B_{j}_{i}"

            place_between(name_fwd,  p_low, p_high_fwd,  BRACE_SIZE)
            place_between(name_back, p_low, p_high_back, BRACE_SIZE)


def build_transverse_knee_braces():
    """Create knee-braces in the bent plane (Y-direction), post → tie.

    These are the braces clearly visible in the reference images, tying each
    post to the tie beam and stiffening the frame in the transverse direction.
    """
    for i, x in enumerate(BENT_X):
        for side_index, y in enumerate(ROW_Y):
            sign = 1.0 if y > 0 else -1.0

            # Post point just below top
            z_post = EAVES_HEIGHT - TRANSVERSE_BRACE_POST_DROP
            p_post = (x, y, z_post)

            # Point along the tie beam, inset towards the centre
            y_tie = sign * (HALF_SPAN - TRANSVERSE_BRACE_INSET_Y)
            p_tie = (x, y_tie, EAVES_HEIGHT)

            name = f"KneeBrace_T_{i}_{side_index}"
            place_between(name, p_post, p_tie, BRACE_SIZE)


def build_ridge_beam():
    """Create the ridge beam along the apex."""
    p0 = (-LENGTH / 2.0, 0.0, RIDGE_HEIGHT)
    p1 = (+LENGTH / 2.0, 0.0, RIDGE_HEIGHT)
    place_between("RidgeBeam", p0, p1, PLATE_SIZE)


def build_rafters():
    """Create rafters at regular spacing with eaves overhang."""
    x = -LENGTH / 2.0
    idx = 0

    abs_y_eave = HALF_SPAN + EAVE_OVERHANG
    z_eave = roof_z_at_y(abs_y_eave)

    while x <= LENGTH / 2.0 + 1e-6:
        # Left side rafter (negative Y)
        p_eaves_L = (x, -abs_y_eave, z_eave)
        p_ridge_L = (x, 0.0, RIDGE_HEIGHT)
        name_L = f"Rafter_{idx}_L"
        place_between(name_L, p_eaves_L, p_ridge_L, RAFTER_SIZE)

        # Right side rafter (positive Y)
        p_eaves_R = (x, +abs_y_eave, z_eave)
        p_ridge_R = (x, 0.0, RIDGE_HEIGHT)
        name_R = f"Rafter_{idx}_R"
        place_between(name_R, p_eaves_R, p_ridge_R, RAFTER_SIZE)

        x += RAFTER_SPACING
        idx += 1


def build_king_post_trusses():
    """Build a simple king-post truss on every bent.

    Each truss consists of:
      - a vertical king-post from tie level to ridge level;
      - a pair of braces from the tie beam up to mid-height of the king-post.
    """
    for i, x in enumerate(BENT_X):
        # King post from tie to ridge
        p0 = (x, 0.0, EAVES_HEIGHT)
        p1 = (x, 0.0, RIDGE_HEIGHT)
        king_size = POST_SIZE * TRUSS_POST_THICKNESS_FACTOR
        place_between(f"KingPost_{i}", p0, p1, king_size)

        # Diagonal braces from tie (near posts) to mid-height of king post
        y_tie_L = -HALF_SPAN * TRUSS_TIE_FACTOR
        y_tie_R = +HALF_SPAN * TRUSS_TIE_FACTOR
        z_mid_king = EAVES_HEIGHT + 0.5 * (RIDGE_HEIGHT - EAVES_HEIGHT)
        p_mid_king = (x, 0.0, z_mid_king)

        p_tie_L = (x, y_tie_L, EAVES_HEIGHT)
        p_tie_R = (x, y_tie_R, EAVES_HEIGHT)

        place_between(f"TrussBrace_L_{i}", p_tie_L, p_mid_king, BRACE_SIZE)
        place_between(f"TrussBrace_R_{i}", p_tie_R, p_mid_king, BRACE_SIZE)


# ------------------------------------------------------------------
# MAIN BUILD ROUTINE
# ------------------------------------------------------------------

def build_frame():
    build_posts()
    build_wall_plates()
    build_tie_beams()
    build_longitudinal_braces()
    build_transverse_knee_braces()
    build_ridge_beam()
    build_rafters()
    build_king_post_trusses()


if __name__ == "__main__":
    build_frame()
