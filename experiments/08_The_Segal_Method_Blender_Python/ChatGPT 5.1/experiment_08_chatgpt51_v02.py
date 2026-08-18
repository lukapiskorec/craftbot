# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 08 - CHATGPT 5.1 - V02
# THE SEGAL METHOD
# ------------------------------------------------------------------

import bpy
import sys
import os
import importlib

import craftbot_lib as craftbot
importlib.reload(craftbot)


# ------------------------------------------------------------------
# PARAMETERS

# Modular grid
MODULE = 1.2          # 1.2 m module (matches 1200 mm boards)
NX = 8                # bays in X (doubled from 4 -> 8)
NY = 3                # bays in Y

# Storeys
N_STOREYS = 2         # ground + upper floor

# Basic dimensions (in metres / Blender units)
STOREY_HEIGHT = 2.4   # floor-to-floor distance
FLOOR_ELEV = 0.6      # bottom of ground floor deck above ground
FLOOR_THICK = 0.2     # floor slab (deck) thickness
ROOF_THICK = 0.2      # roof slab thickness
OVERHANG = 0.3        # (kept for possible later use)

# Timber section sizes
POST_SECTION = 0.10   # 100 x 100 mm posts
BEAM_SECTION = 0.10   # 100 x 100 mm beams

# Wall thickness (plywood + build-up)
WALL_THICK = 0.12

# Stair parameters
N_STEPS = 12
STAIR_WIDTH = MODULE
STAIR_RUN = MODULE * 3.0  # horizontal run of the stair


# ------------------------------------------------------------------
# DERIVED DIMENSIONS

Lx = NX * MODULE      # overall length (X)
Ly = NY * MODULE      # overall width (Y)

# Vertical levels
POST_HEIGHT = FLOOR_ELEV + N_STOREYS * STOREY_HEIGHT  # top of posts / beam level
ROOF_BEAM_LEVEL = POST_HEIGHT                         # where roof beams sit

# Floor levels (bottom of slab)
FLOOR0_BOTTOM = FLOOR_ELEV
FLOOR1_BOTTOM = FLOOR_ELEV + STOREY_HEIGHT

# Centers for slabs
FLOOR0_CENTER = FLOOR0_BOTTOM + FLOOR_THICK / 2.0
FLOOR1_CENTER = FLOOR1_BOTTOM + FLOOR_THICK / 2.0
ROOF_CENTER = ROOF_BEAM_LEVEL + ROOF_THICK / 2.0

# Beam layers (centers)
FLOOR0_BEAMS_Z = FLOOR0_BOTTOM - BEAM_SECTION / 2.0
FLOOR1_BEAMS_Z = FLOOR1_BOTTOM - BEAM_SECTION / 2.0
ROOF_BEAMS_Z = ROOF_BEAM_LEVEL - BEAM_SECTION / 2.0

# Split / double-height configuration
X_MID = Lx / 2.0
VOID_SIDE = "E"   # "E" = remove slabs on east half, creating double-height zone there


# ------------------------------------------------------------------
# HELPER: create axis-aligned box by center + size

def make_box(name, center, size):
    """
    Helper that wraps craftbot.place_element() to create a box of
    given size (sx, sy, sz) centered at (cx, cy, cz).
    """
    cx, cy, cz = center
    sx, sy, sz = size

    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=(0.0, 0.0, 1.0),
        angle=0.0,
        scale=(sx / 2.0, sy / 2.0, sz / 2.0),
    )


# ------------------------------------------------------------------
# 1. POSTS

def build_posts():
    """
    Place posts at all grid intersections, including the middle
    of the house.
    """
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY + 1):
            y = j * MODULE
            z_center = POST_HEIGHT / 2.0

            make_box(
                name=f"Post_{i}_{j}",
                center=(x, y, z_center),
                size=(POST_SECTION, POST_SECTION, POST_HEIGHT),
            )


# ------------------------------------------------------------------
# 2. BEAMS (FLOOR + ROOF)

def build_beam_layer(z_center, label):
    """
    Create a full tartan of beams at height z_center tying the posts.
    """
    # X-direction beams (span along X, between posts along Y grid lines)
    for j in range(NY + 1):
        y = j * MODULE
        for i in range(NX):
            x0 = i * MODULE
            cx = x0 + MODULE / 2.0

            make_box(
                name=f"BeamX_{label}_{i}_{j}",
                center=(cx, y, z_center),
                size=(MODULE, BEAM_SECTION, BEAM_SECTION),
            )

    # Y-direction beams (span along Y, between posts along X grid lines)
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY):
            y0 = j * MODULE
            cy = y0 + MODULE / 2.0

            make_box(
                name=f"BeamY_{label}_{i}_{j}",
                center=(x, cy, z_center),
                size=(BEAM_SECTION, MODULE, BEAM_SECTION),
            )


def build_all_beams():
    # Ground floor supporting beams
    build_beam_layer(FLOOR0_BEAMS_Z, "FL0")

    # Upper floor supporting beams (ceiling of ground floor)
    build_beam_layer(FLOOR1_BEAMS_Z, "FL1")

    # Roof beams (ceiling of upper floor)
    build_beam_layer(ROOF_BEAMS_Z, "ROOF")


# ------------------------------------------------------------------
# 3. FLOORS

def build_floor0():
    """
    Ground floor deck covering the entire footprint.
    """
    make_box(
        name="Floor0_Deck",
        center=(Lx / 2.0, Ly / 2.0, FLOOR0_CENTER),
        size=(Lx, Ly, FLOOR_THICK),
    )


def build_floor1():
    """
    Upper floor deck split in two halves along X.
    We keep only one half and omit the other half (VOID_SIDE)
    to create a double-height zone running through the house.
    """
    half_len = Lx / 2.0

    # West half
    if VOID_SIDE != "W":
        make_box(
            name="Floor1_Deck_W",
            center=(half_len / 2.0, Ly / 2.0, FLOOR1_CENTER),
            size=(half_len, Ly, FLOOR_THICK),
        )

    # East half
    if VOID_SIDE != "E":
        make_box(
            name="Floor1_Deck_E",
            center=(half_len + half_len / 2.0, Ly / 2.0, FLOOR1_CENTER),
            size=(half_len, Ly, FLOOR_THICK),
        )


# ------------------------------------------------------------------
# 4. ROOF (SPLIT INTO TWO HALVES)

def build_roof():
    """
    Flat roof slab split into two halves along X. As with the
    upper floor, we skip the half on VOID_SIDE so that the
    double-height space is open right up to the roof.
    """
    half_len = Lx / 2.0

    # West half
    if VOID_SIDE != "W":
        make_box(
            name="RoofDeck_W",
            center=(half_len / 2.0, Ly / 2.0, ROOF_CENTER),
            size=(half_len, Ly, ROOF_THICK),
        )

    # East half
    if VOID_SIDE != "E":
        make_box(
            name="RoofDeck_E",
            center=(half_len + half_len / 2.0, Ly / 2.0, ROOF_CENTER),
            size=(half_len, Ly, ROOF_THICK),
        )


# ------------------------------------------------------------------
# 5. EXTERNAL WALLS (PLYWOOD INFILL)

def build_walls():
    """
    Tall external wall panels running from ground-floor level up
    to the roof beams, clamped between posts.
    """
    z_bottom = FLOOR0_BOTTOM
    z_top = ROOF_BEAM_LEVEL
    wall_height = z_top - z_bottom
    z_center = z_bottom + wall_height / 2.0

    # SOUTH and NORTH sides (panels along X, faces in Y)
    for side, y in (("S", 0.0), ("N", Ly)):
        for i in range(NX):
            cx = (i + 0.5) * MODULE
            make_box(
                name=f"Wall_{side}_{i}",
                center=(cx, y, z_center),
                size=(MODULE, WALL_THICK, wall_height),
            )

    # WEST and EAST sides (panels along Y, faces in X)
    for side, x in (("W", 0.0), ("E", Lx)):
        for j in range(NY):
            cy = (j + 0.5) * MODULE
            make_box(
                name=f"Wall_{side}_{j}",
                center=(x, cy, z_center),
                size=(WALL_THICK, MODULE, wall_height),
            )


# ------------------------------------------------------------------
# 6. STAIRCASE

def build_staircase():
    """
    Straight stair from ground floor up to the upper floor.
    Modelled as a stack of rectangular treads (no rotation),
    located in the double-height zone on the east side.
    """
    # Vertical: from top of ground floor to top of upper floor deck
    z0 = FLOOR0_BOTTOM + FLOOR_THICK  # top of ground floor deck
    z_top_floor1 = FLOOR1_BOTTOM + FLOOR_THICK
    total_rise = z_top_floor1 - z0

    step_rise = total_rise / N_STEPS
    step_depth = STAIR_RUN / N_STEPS

    # Place the stair in the eastern (void) half, roughly centered in Y
    x_start = X_MID + (Lx / 2.0 - STAIR_RUN) / 2.0
    y_center = Ly / 2.0

    for n in range(N_STEPS):
        # Each step is a block extending along +X
        x0 = x_start + n * step_depth
        z_base = z0 + n * step_rise

        cx = x0 + step_depth / 2.0
        cz = z_base + step_rise / 2.0

        make_box(
            name=f"StairStep_{n:02d}",
            center=(cx, y_center, cz),
            size=(step_depth, STAIR_WIDTH, step_rise),
        )


# ------------------------------------------------------------------
# MAIN ENTRY POINT

def build_unit():
    build_posts()
    build_all_beams()
    build_floor0()
    build_floor1()
    build_roof()
    build_walls()
    build_staircase()


if __name__ == "__main__":
    build_unit()
