# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 08 - CHATGPT 5.1 - V01
# THE SEGAL METHOD
# ------------------------------------------------------------------

import bpy
import sys
import os
import importlib

import craftbot_lib as craftbot  # assumes craftbot_lib.py is importable
importlib.reload(craftbot)


# ------------------------------------------------------------------
# PARAMETERS (you can tweak these)

# Modular grid
MODULE = 1.2          # 1.2 m grid to match 1200 mm boards
NX = 4                # bays in X direction
NY = 3                # bays in Y direction

# Basic dimensions (in Blender units, interpreted as metres)
STOREY_HEIGHT = 2.4   # clear wall height above finished floor
FLOOR_ELEV = 0.6      # finished floor height above ground
FLOOR_THICK = 0.2     # floor build-up thickness
ROOF_THICK = 0.2      # roof build-up thickness
OVERHANG = 0.3        # roof overhang beyond walls

# Timber section sizes
POST_SECTION = 0.10   # square posts: 100 x 100 mm
BEAM_SECTION = 0.10   # beams: 100 x 100 mm (simplified)

# Plywood wall cladding thickness
WALL_THICK = 0.12     # total wall thickness (plywood + build-up)

# Derived extents
Lx = NX * MODULE      # overall length in X
Ly = NY * MODULE      # overall width in Y

# Posts go from ground up to underside of roof slab
POST_HEIGHT = FLOOR_ELEV + STOREY_HEIGHT + ROOF_THICK


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
        angle=0.0,  # no rotation; axis-aligned
        scale=(sx / 2.0, sy / 2.0, sz / 2.0),
    )


# ------------------------------------------------------------------
# 1. STRUCTURAL POSTS

def build_posts():
    """
    Place perimeter posts at grid intersections.
    """
    for i in range(NX + 1):
        for j in range(NY + 1):
            # perimeter only
            if i in (0, NX) or j in (0, NY):
                x = i * MODULE
                y = j * MODULE
                z_center = POST_HEIGHT / 2.0

                make_box(
                    name=f"Post_{i}_{j}",
                    center=(x, y, z_center),
                    size=(POST_SECTION, POST_SECTION, POST_HEIGHT),
                )


# ------------------------------------------------------------------
# 2. ROOF BEAMS (PERIMETER BEAMS AT TOP OF POSTS)

def build_roof_beams():
    """
    Place beams along X and Y tying the tops of posts together.
    """
    z_center = POST_HEIGHT - BEAM_SECTION / 2.0

    # X-direction beams between posts along each Y grid line
    for j in range(NY + 1):
        y = j * MODULE
        for i in range(NX):
            x0 = i * MODULE
            cx = x0 + MODULE / 2.0

            make_box(
                name=f"BeamX_{i}_{j}",
                center=(cx, y, z_center),
                size=(MODULE, BEAM_SECTION, BEAM_SECTION),
            )

    # Y-direction beams between posts along each X grid line
    for i in range(NX + 1):
        x = i * MODULE
        for j in range(NY):
            y0 = j * MODULE
            cy = y0 + MODULE / 2.0

            make_box(
                name=f"BeamY_{i}_{j}",
                center=(x, cy, z_center),
                size=(BEAM_SECTION, MODULE, BEAM_SECTION),
            )


# ------------------------------------------------------------------
# 3. FLOOR DECK (RAISED PLATFORM)

def build_floor():
    """
    Simplified floor: a single slab representing joists + deck.
    """
    z_center = FLOOR_ELEV + FLOOR_THICK / 2.0

    make_box(
        name="FloorDeck",
        center=(Lx / 2.0, Ly / 2.0, z_center),
        size=(Lx, Ly, FLOOR_THICK),
    )


# ------------------------------------------------------------------
# 4. ROOF SLAB (FLAT ROOF WITH OVERHANG)

def build_roof():
    """
    Simplified flat roof slab with constant thickness and overhang.
    """
    z_center = POST_HEIGHT + ROOF_THICK / 2.0

    make_box(
        name="RoofDeck",
        center=(Lx / 2.0, Ly / 2.0, z_center),
        size=(Lx + 2 * OVERHANG, Ly + 2 * OVERHANG, ROOF_THICK),
    )


# ------------------------------------------------------------------
# 5. EXTERNAL WALL INFILL (PLYWOOD CLADDING PANELS)

def build_walls():
    """
    Place plywood-clad infill panels in each bay between posts
    around the perimeter.
    """
    # Clear height from top of floor deck to underside of roof beams
    z_beam_bottom = POST_HEIGHT - BEAM_SECTION
    z_floor_top = FLOOR_ELEV + FLOOR_THICK
    wall_height = z_beam_bottom - z_floor_top
    z_center = z_floor_top + wall_height / 2.0

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
# MAIN ENTRY POINT

def build_unit():
    """
    Build the full one-storey Segal-style unit.
    Clear the selection first if needed.
    """
    build_posts()
    build_roof_beams()
    build_floor()
    build_roof()
    build_walls()


# Run immediately when script is executed inside Blender
if __name__ == "__main__":
    build_unit()
