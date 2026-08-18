# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 09 - CHATGPT 5.1 - V01
# HOW TO CLT
# ------------------------------------------------------------------

import bpy
import math
import importlib
import craftbot_lib as craftbot   # make sure this is on sys.path

importlib.reload(craftbot)

# -------------------------------------------------------------------
# GLOBAL PARAMETERS (in Blender units ≈ meters)
# -------------------------------------------------------------------

NUM_FLOORS      = 10    # number of regular residential floors
ROOF_FLOORS     = 2     # number of "storeys worth" of height in gable roof
FLOOR_HEIGHT    = 3.0   # floor-to-floor height (clear level step)

BUILDING_LENGTH = 30.0  # overall length (x-direction)
BUILDING_WIDTH  = 14.0  # overall width  (y-direction)

CORE_LENGTH     = 6.0   # lift/stair core length  (x)
CORE_WIDTH      = 4.0   # lift/stair core width   (y)

WALL_THICKNESS  = 0.16  # CLT wall thickness
PARTY_WALL_T    = 0.16  # CLT party wall thickness
SLAB_THICKNESS  = 0.24  # CLT floor slab thickness
ROOF_THICKNESS  = 0.16  # CLT roof panel thickness

PODIUM_HEIGHT   = 1.0   # concrete podium height

# Derived
BUILDING_HEIGHT = NUM_FLOORS * FLOOR_HEIGHT
ROOF_HEIGHT     = ROOF_FLOORS * FLOOR_HEIGHT   # vertical rise from eaves to ridge

# -------------------------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------------------------

def clear_scene():
    """Delete all mesh objects from the scene (optional)."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()


def make_block(name, cx, cy, cz, sx, sy, sz, rot_axis=(0, 0, 1), rot_angle_deg=0.0):
    """
    Convenience wrapper around craftbot.place_element for a box.

    Parameters:
        name : object name
        cx, cy, cz : centre coordinates
        sx, sy, sz : half-dimensions (scale) in x, y, z
        rot_axis   : rotation axis (world)
        rot_angle_deg : rotation angle in degrees
    """
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=rot_axis,
        angle=rot_angle_deg,
        scale=(sx, sy, sz),
    )


# -------------------------------------------------------------------
# BUILDING COMPONENTS
# -------------------------------------------------------------------

def build_podium():
    """Concrete podium / ground slab."""
    cx, cy = 0.0, 0.0
    cz      = PODIUM_HEIGHT / 2.0
    sx      = BUILDING_LENGTH / 2.0
    sy      = BUILDING_WIDTH / 2.0
    sz      = PODIUM_HEIGHT / 2.0

    make_block(
        "Podium",
        cx, cy, cz,
        sx, sy, sz,
    )


def build_core():
    """Stack CLT core wall panels per floor around the lift/stair shaft."""
    # Core is centered at origin
    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        cz = floor_bottom + FLOOR_HEIGHT / 2.0
        hz = FLOOR_HEIGHT / 2.0

        # long walls of core (parallel to X)
        sx_long = CORE_LENGTH / 2.0
        sy_long = WALL_THICKNESS / 2.0

        make_block(
            f"Core_Long_+Y_L{i:02d}",
            0.0,
            +CORE_WIDTH / 2.0,
            cz,
            sx_long, sy_long, hz,
        )

        make_block(
            f"Core_Long_-Y_L{i:02d}",
            0.0,
            -CORE_WIDTH / 2.0,
            cz,
            sx_long, sy_long, hz,
        )

        # short walls of core (parallel to Y)
        sx_short = WALL_THICKNESS / 2.0
        sy_short = CORE_WIDTH / 2.0

        make_block(
            f"Core_Short_+X_L{i:02d}",
            +CORE_LENGTH / 2.0,
            0.0,
            cz,
            sx_short, sy_short, hz,
        )

        make_block(
            f"Core_Short_-X_L{i:02d}",
            -CORE_LENGTH / 2.0,
            0.0,
            cz,
            sx_short, sy_short, hz,
        )


def build_exterior_walls():
    """Exterior CLT walls per floor (simple continuous panels)."""
    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        cz = floor_bottom + FLOOR_HEIGHT / 2.0
        hz = FLOOR_HEIGHT / 2.0

        # long facades (parallel to X)
        sx_long = BUILDING_LENGTH / 2.0
        sy_long = WALL_THICKNESS / 2.0

        make_block(
            f"Ext_Long_+Y_L{i:02d}",
            0.0,
            BUILDING_WIDTH / 2.0,
            cz,
            sx_long, sy_long, hz,
        )

        make_block(
            f"Ext_Long_-Y_L{i:02d}",
            0.0,
            -BUILDING_WIDTH / 2.0,
            cz,
            sx_long, sy_long, hz,
        )

        # short facades (parallel to Y)
        sx_short = WALL_THICKNESS / 2.0
        sy_short = BUILDING_WIDTH / 2.0

        make_block(
            f"Ext_Short_+X_L{i:02d}",
            BUILDING_LENGTH / 2.0,
            0.0,
            cz,
            sx_short, sy_short, hz,
        )

        make_block(
            f"Ext_Short_-X_L{i:02d}",
            -BUILDING_LENGTH / 2.0,
            0.0,
            cz,
            sx_short, sy_short, hz,
        )


def build_party_walls():
    """
    Simple example of CLT party walls: one longitudinal wall
    on each side of the core (could be extended into a grid).
    """
    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        cz = floor_bottom + FLOOR_HEIGHT / 2.0
        hz = FLOOR_HEIGHT / 2.0

        # Example: one wall each side of core
        offset = CORE_WIDTH / 2.0 + 2.0  # 2 m corridor on each side

        sx = BUILDING_LENGTH / 2.0
        sy = PARTY_WALL_T / 2.0

        make_block(
            f"Party_+Y_L{i:02d}",
            0.0,
            +offset,
            cz,
            sx, sy, hz,
        )

        make_block(
            f"Party_-Y_L{i:02d}",
            0.0,
            -offset,
            cz,
            sx, sy, hz,
        )


def build_floor_slabs():
    """
    CLT floor slabs spanning from exterior walls towards the core.
    Here we model two 'wings' per floor, leaving a rectangular void
    over the core.
    """
    wing_length = (BUILDING_LENGTH - CORE_LENGTH) / 2.0
    sy          = BUILDING_WIDTH / 2.0
    sz          = SLAB_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_top = PODIUM_HEIGHT + (i + 1) * FLOOR_HEIGHT
        cz = floor_top - SLAB_THICKNESS / 2.0

        # left wing (negative X)
        sx_left = wing_length / 2.0
        cx_left = -(CORE_LENGTH / 2.0 + wing_length / 2.0)

        make_block(
            f"Slab_Left_L{i:02d}",
            cx_left, 0.0, cz,
            sx_left, sy, sz,
        )

        # right wing (positive X)
        sx_right = wing_length / 2.0
        cx_right = +(CORE_LENGTH / 2.0 + wing_length / 2.0)

        make_block(
            f"Slab_Right_L{i:02d}",
            cx_right, 0.0, cz,
            sx_right, sy, sz,
        )


def build_roof():
    """
    Double-pitched CLT roof representing a multi-storey gable volume.

    Eaves sit at top of last floor; ridge is ROOF_HEIGHT above that.
    Two large CLT panels are rotated about the X axis.
    """
    eaves_z    = PODIUM_HEIGHT + BUILDING_HEIGHT
    ridge_z    = eaves_z + ROOF_HEIGHT
    roof_mid_z = (eaves_z + ridge_z) / 2.0

    half_span  = BUILDING_WIDTH / 2.0
    rise       = ROOF_HEIGHT

    # Slope angle from horizontal
    roof_angle_rad = math.atan2(rise, half_span)
    roof_angle_deg = math.degrees(roof_angle_rad)

    # Length of each pitched panel in plan-normal direction
    slope_length = math.sqrt(half_span ** 2 + rise ** 2)

    # Half-dimensions of roof plates
    sx = BUILDING_LENGTH / 2.0
    sy = slope_length / 2.0
    sz = ROOF_THICKNESS / 2.0

    # Centres of roof plates: halfway between eave and ridge in plan
    # => at y = ± half_span / 2 = ± BUILDING_WIDTH / 4
    y_offset = BUILDING_WIDTH / 4.0

    # Positive slope (falls to +Y)
    make_block(
        "Roof_Plate_+Y",
        0.0,
        +y_offset,
        roof_mid_z,
        sx, sy, sz,
        rot_axis=(1, 0, 0),
        rot_angle_deg=-roof_angle_deg,  # negative: down towards +Y
    )

    # Negative slope (falls to -Y)
    make_block(
        "Roof_Plate_-Y",
        0.0,
        -y_offset,
        roof_mid_z,
        sx, sy, sz,
        rot_axis=(1, 0, 0),
        rot_angle_deg=+roof_angle_deg,  # positive: down towards -Y
    )


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

def build_clt_highrise(clear=True):
    """Entry point to build the whole CLT tower."""
    if clear:
        clear_scene()

    build_podium()
    build_core()
    build_exterior_walls()
    build_party_walls()
    build_floor_slabs()
    build_roof()


# Execute when run inside Blender
if __name__ == "__main__":
    build_clt_highrise(clear=True)
