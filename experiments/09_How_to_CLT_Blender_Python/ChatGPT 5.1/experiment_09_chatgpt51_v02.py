# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 09 - CHATGPT 5.1 - V02
# HOW TO CLT
# ------------------------------------------------------------------

import bpy
import math
import importlib
import random

import craftbot_lib as craftbot
importlib.reload(craftbot)

# ------------------------------------------------------------------
# GLOBAL PARAMETERS
# ------------------------------------------------------------------

NUM_FLOORS      = 10        # regular residential floors
ROOF_FLOORS     = 2         # "storeys" of height in gable roof
FLOOR_HEIGHT    = 3.0       # floor-to-floor height

BUILDING_LENGTH = 30.0      # overall length (X)
BUILDING_WIDTH  = 14.0      # overall width  (Y)

CORE_LENGTH     = 6.0       # core length (X)
CORE_WIDTH      = 4.0       # core width  (Y)

WALL_THICKNESS  = 0.16      # CLT wall thickness
PARTY_WALL_T    = 0.16      # CLT party wall thickness
SLAB_THICKNESS  = 0.24      # CLT floor slab thickness
ROOF_THICKNESS  = 0.16      # CLT roof panel thickness

PODIUM_HEIGHT   = 1.0       # concrete podium

BUILDING_HEIGHT = NUM_FLOORS * FLOOR_HEIGHT
ROOF_HEIGHT     = ROOF_FLOORS * FLOOR_HEIGHT

# ------------------------------------------------------------------
# OPENINGS (APARTMENTS + CORE)
# ------------------------------------------------------------------

WINDOW_SILL_HEIGHT  = 0.9   # sill above finished floor
WINDOW_HEIGHT       = 1.4
WINDOW_WIDTH        = 3.0
WINDOWS_PER_FACADE  = 3
RANDOM_SEED         = 12345 # used for facade opening jitter (repeatable)

DOOR_WIDTH          = 1.2   # core door width
DOOR_HEIGHT         = 2.1

# ------------------------------------------------------------------
# STAIRS (INSIDE CORE, CLEAR OF ELEVATOR SHAFT)
# ------------------------------------------------------------------

STAIR_THICKNESS       = 0.25
STAIR_CLEARANCE       = 0.2
STAIR_ANGLE_DEG       = 40.0
STAIR_RISE_PER_FLIGHT = FLOOR_HEIGHT / 2.0   # two flights per storey

STAIR_ANGLE_RAD       = math.radians(STAIR_ANGLE_DEG)
STAIR_FLIGHT_LENGTH   = STAIR_RISE_PER_FLIGHT / math.sin(STAIR_ANGLE_RAD)
STAIR_PROJ_X          = STAIR_FLIGHT_LENGTH * math.cos(STAIR_ANGLE_RAD)
STAIR_WIDTH           = 1.2  # along Y

# Elevator shaft placeholder (inside core, to keep stairs clear)
ELEVATOR_WIDTH_X      = 1.6
ELEVATOR_WIDTH_Y      = 1.6

# ------------------------------------------------------------------
# COLLECTION HELPERS
# ------------------------------------------------------------------

def get_or_create_collection(name: str) -> bpy.types.Collection:
    """Return a collection, creating (and linking) it if needed."""
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)

    # Ensure it is linked to the scene root
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)

    return coll


def add_object_to_collection(obj_name: str, coll_name: str):
    """Move the object to a named collection."""
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return

    coll = get_or_create_collection(coll_name)

    # membership on bpy_prop_collection expects a string (object name)
    if obj.name not in coll.objects:
        coll.objects.link(obj)

    # Optional: unlink from master root collection to keep things tidy
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def clear_scene():
    """Remove all mesh objects from the scene (collections remain)."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()


# ------------------------------------------------------------------
# BASIC BLOCK CREATION (WRAPS craftbot.place_element)
# ------------------------------------------------------------------

def make_block(name,
               cx, cy, cz,
               sx, sy, sz,
               rot_axis=(0, 0, 1),
               rot_angle_deg=0.0,
               collection=None):
    """
    Place a rectangular solid using craftbot.place_element and
    then move it into the specified collection.
    """
    craftbot.place_element(
        name=name,
        loc=(cx, cy, cz),
        axis=rot_axis,
        angle=rot_angle_deg,
        scale=(sx, sy, sz),
    )
    if collection is not None:
        add_object_to_collection(name, collection)


# ------------------------------------------------------------------
# RANDOM WINDOW LAYOUT
# ------------------------------------------------------------------

def window_centres_for(side_label: str, floor_index: int):
    """
    Deterministic pseudo-random window centres along X for the given
    facade (side_label in {'N','S'}) and floor index.
    """
    side_offset = 0 if side_label == 'N' else 1000
    rng = random.Random(RANDOM_SEED + side_offset + floor_index * 17)

    centres = []
    segment = BUILDING_LENGTH / WINDOWS_PER_FACADE
    edge_margin = WINDOW_WIDTH / 2.0 + 1.0   # keep away from corners

    for k in range(WINDOWS_PER_FACADE):
        base = -BUILDING_LENGTH / 2.0 + (k + 0.5) * segment
        jitter = rng.uniform(-segment * 0.25, segment * 0.25)
        c = base + jitter
        # Clamp to avoid falling outside facade
        c = max(c, -BUILDING_LENGTH / 2.0 + edge_margin)
        c = min(c,  BUILDING_LENGTH / 2.0 - edge_margin)
        centres.append(c)

    centres.sort()
    return centres


# ------------------------------------------------------------------
# GEOMETRY BUILDERS
# ------------------------------------------------------------------

def build_podium():
    """Concrete podium / ground floor slab."""
    cx, cy = 0.0, 0.0
    cz      = PODIUM_HEIGHT / 2.0
    sx      = BUILDING_LENGTH / 2.0
    sy      = BUILDING_WIDTH / 2.0
    sz      = PODIUM_HEIGHT / 2.0

    make_block(
        "Podium",
        cx, cy, cz,
        sx, sy, sz,
        collection="Podium",
    )


def build_long_facade_with_openings(side_label: str):
    """
    Build north (N) or south (S) long facade with apartment openings.

    For each floor:
      - continuous lower band (floor -> sill)
      - continuous upper band (head -> ceiling)
      - vertical piers in window zone (sill -> head) between windows
    Openings are placed per floor with seeded randomness.
    """
    assert side_label in {'N', 'S'}
    is_north = side_label == 'N'
    coll_name = "Walls_North" if is_north else "Walls_South"
    y_pos = BUILDING_WIDTH / 2.0 if is_north else -BUILDING_WIDTH / 2.0
    sy = WALL_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        sill_z  = floor_bottom + WINDOW_SILL_HEIGHT
        head_z  = sill_z + WINDOW_HEIGHT

        # Lower band (solid CLT below windows)
        hz_low  = (sill_z - floor_bottom) / 2.0
        if hz_low > 0:
            cz_low  = floor_bottom + hz_low
            sx_low  = BUILDING_LENGTH / 2.0
            make_block(
                f"{side_label}_Wall_Low_L{i:02d}",
                0.0, y_pos, cz_low,
                sx_low, sy, hz_low,
                collection=coll_name,
            )

        # Upper band (solid CLT above windows)
        hz_high = (floor_top - head_z) / 2.0
        if hz_high > 0:
            cz_high = head_z + hz_high
            sx_high = BUILDING_LENGTH / 2.0
            make_block(
                f"{side_label}_Wall_High_L{i:02d}",
                0.0, y_pos, cz_high,
                sx_high, sy, hz_high,
                collection=coll_name,
            )

        # Vertical piers between windows (window zone sill->head)
        centres = window_centres_for(side_label, i)
        window_half = WINDOW_WIDTH / 2.0

        x_left = -BUILDING_LENGTH / 2.0
        segments = []
        for c in centres:
            left  = c - window_half
            right = c + window_half
            segments.append((x_left, left))
            x_left = right
        segments.append((x_left, BUILDING_LENGTH / 2.0))

        hz_mid = (head_z - sill_z) / 2.0
        cz_mid = sill_z + hz_mid

        for si, (a, b) in enumerate(segments):
            seg_width = b - a
            if seg_width <= 0.05:
                continue
            sx_mid = seg_width / 2.0
            cx_mid = (a + b) / 2.0
            make_block(
                f"{side_label}_Pier_L{i:02d}_{si}",
                cx_mid, y_pos, cz_mid,
                sx_mid, sy, hz_mid,
                collection=coll_name,
            )


def build_short_facades():
    """Solid east / west walls per floor (no openings)."""
    sy = BUILDING_WIDTH / 2.0
    sx = WALL_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        cz = floor_bottom + FLOOR_HEIGHT / 2.0
        hz = FLOOR_HEIGHT / 2.0

        # East (+X)
        make_block(
            f"East_Wall_L{i:02d}",
            BUILDING_LENGTH / 2.0, 0.0, cz,
            sx, sy, hz,
            collection="Walls_East",
        )

        # West (-X)
        make_block(
            f"West_Wall_L{i:02d}",
            -BUILDING_LENGTH / 2.0, 0.0, cz,
            sx, sy, hz,
            collection="Walls_West",
        )


def build_party_walls():
    """
    Simple internal load-bearing party walls (two longitudinal walls).
    They separate the two apartment bands from the central corridor.
    """
    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        cz = floor_bottom + FLOOR_HEIGHT / 2.0
        hz = FLOOR_HEIGHT / 2.0

        offset = CORE_WIDTH / 2.0 + 2.0  # ~2 m corridor on each side of core

        sx = BUILDING_LENGTH / 2.0
        sy = PARTY_WALL_T / 2.0

        make_block(
            f"Party_+Y_L{i:02d}",
            0.0, +offset, cz,
            sx, sy, hz,
            collection="Walls_Interior",
        )

        make_block(
            f"Party_-Y_L{i:02d}",
            0.0, -offset, cz,
            sx, sy, hz,
            collection="Walls_Interior",
        )


def build_core_with_openings():
    """
    Build CLT core walls with an opening (door) on the +Y long wall
    on every floor. Other core walls remain solid per floor.
    """
    sy_long  = WALL_THICKNESS / 2.0
    sx_short = WALL_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT
        hz_full      = FLOOR_HEIGHT / 2.0
        cz_full      = floor_bottom + hz_full

        # Long wall on -Y (solid)
        sx_long = CORE_LENGTH / 2.0
        make_block(
            f"Core_Long_-Y_L{i:02d}",
            0.0, -CORE_WIDTH / 2.0, cz_full,
            sx_long, sy_long, hz_full,
            collection="Core",
        )

        # Long wall on +Y with door opening
        door_bottom = floor_bottom
        door_top    = floor_bottom + DOOR_HEIGHT

        # top band above door
        hz_top = (floor_top - door_top) / 2.0
        cz_top = door_top + hz_top
        if hz_top > 0.05:
            make_block(
                f"Core_Long_+Y_Top_L{i:02d}",
                0.0, CORE_WIDTH / 2.0, cz_top,
                CORE_LENGTH / 2.0, sy_long, hz_top,
                collection="Core",
            )

        # side piers left/right of door in door zone
        door_half = DOOR_WIDTH / 2.0
        x_left    = -CORE_LENGTH / 2.0
        x_right   = CORE_LENGTH / 2.0

        segments = [(x_left, -door_half), (door_half, x_right)]
        hz_mid   = DOOR_HEIGHT / 2.0
        cz_mid   = door_bottom + hz_mid

        for si, (a, b) in enumerate(segments):
            seg_width = b - a
            if seg_width <= 0.05:
                continue
            sx_mid = seg_width / 2.0
            cx_mid = (a + b) / 2.0
            make_block(
                f"Core_Long_+Y_Pier_L{i:02d}_{si}",
                cx_mid, CORE_WIDTH / 2.0, cz_mid,
                sx_mid, sy_long, hz_mid,
                collection="Core",
            )

        # Short walls (±X) solid
        sy_short = CORE_WIDTH / 2.0
        make_block(
            f"Core_Short_+X_L{i:02d}",
            CORE_LENGTH / 2.0, 0.0, cz_full,
            sx_short, sy_short, hz_full,
            collection="Core",
        )
        make_block(
            f"Core_Short_-X_L{i:02d}",
            -CORE_LENGTH / 2.0, 0.0, cz_full,
            sx_short, sy_short, hz_full,
            collection="Core",
        )


def build_elevator_shaft():
    """
    Solid placeholder volume for the internal elevator shaft inside
    the core – used mainly to keep stair flights from intersecting
    the elevator.
    """
    inner_x_half = CORE_LENGTH / 2.0 - WALL_THICKNESS

    sx = ELEVATOR_WIDTH_X / 2.0
    sy = ELEVATOR_WIDTH_Y / 2.0
    sz = (PODIUM_HEIGHT + BUILDING_HEIGHT + ROOF_HEIGHT) / 2.0

    # Place it towards the -X side of the core
    cx = -(inner_x_half - sx)
    cy = 0.0
    cz = PODIUM_HEIGHT + BUILDING_HEIGHT / 2.0

    make_block(
        "Elevator_Shaft",
        cx, cy, cz,
        sx, sy, sz,
        collection="Core",
    )


def build_floor_slabs():
    """
    CLT floor slabs that do NOT intersect exterior or core walls.

    Walls have priority: slabs stop at the inner faces of the
    exterior walls and at a clear distance from the core.
    Two 'wings' per floor, one on each side of the core.
    """
    # Y extents between inside faces of north/south walls
    y_min = -BUILDING_WIDTH / 2.0 + WALL_THICKNESS
    y_max =  BUILDING_WIDTH / 2.0 - WALL_THICKNESS
    sy    = (y_max - y_min) / 2.0
    cy    = (y_min + y_max) / 2.0

    # X extents for left and right wings between inside faces
    left_min  = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    left_max  = -CORE_LENGTH / 2.0 - WALL_THICKNESS
    right_min =  CORE_LENGTH / 2.0 + WALL_THICKNESS
    right_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS

    sx_left   = (left_max - left_min) / 2.0
    cx_left   = (left_min + left_max) / 2.0

    sx_right  = (right_max - right_min) / 2.0
    cx_right  = (right_min + right_max) / 2.0

    sz = SLAB_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_top = PODIUM_HEIGHT + (i + 1) * FLOOR_HEIGHT
        cz = floor_top - SLAB_THICKNESS / 2.0

        make_block(
            f"Slab_Left_L{i:02d}",
            cx_left, cy, cz,
            sx_left, sy, sz,
            collection="Slabs",
        )
        make_block(
            f"Slab_Right_L{i:02d}",
            cx_right, cy, cz,
            sx_right, sy, sz,
            collection="Slabs",
        )


def build_roof():
    """
    Double-pitched CLT roof representing a multi-storey gable volume.
    """
    eaves_z    = PODIUM_HEIGHT + BUILDING_HEIGHT
    ridge_z    = eaves_z + ROOF_HEIGHT
    roof_mid_z = (eaves_z + ridge_z) / 2.0

    half_span  = BUILDING_WIDTH / 2.0
    rise       = ROOF_HEIGHT

    roof_angle_rad = math.atan2(rise, half_span)
    roof_angle_deg = math.degrees(roof_angle_rad)

    slope_length = math.sqrt(half_span ** 2 + rise ** 2)

    sx = BUILDING_LENGTH / 2.0
    sy = slope_length / 2.0
    sz = ROOF_THICKNESS / 2.0

    # centres of roof plates offset slightly from building centre in Y
    y_offset = BUILDING_WIDTH / 4.0

    make_block(
        "Roof_Plate_+Y",
        0.0, +y_offset, roof_mid_z,
        sx, sy, sz,
        rot_axis=(1, 0, 0),
        rot_angle_deg=-roof_angle_deg,
        collection="Roof",
    )

    make_block(
        "Roof_Plate_-Y",
        0.0, -y_offset, roof_mid_z,
        sx, sy, sz,
        rot_axis=(1, 0, 0),
        rot_angle_deg=+roof_angle_deg,
        collection="Roof",
    )


def build_stairs():
    """
    Approximate dogleg stair flights inside the core that:
      - stay clear of the elevator shaft volume, and
      - reach from podium level to top residential floor.

    Each storey has two flights with rise = FLOOR_HEIGHT / 2.
    """
    inner_x_half = CORE_LENGTH / 2.0 - WALL_THICKNESS

    sx_flight = STAIR_FLIGHT_LENGTH / 2.0
    sy_flight = STAIR_WIDTH / 2.0
    sz_flight = STAIR_THICKNESS / 2.0

    # Place flights on +X side, away from elevator shaft (which is on -X)
    elevator_half_x = ELEVATOR_WIDTH_X / 2.0
    cx_stair = elevator_half_x + STAIR_CLEARANCE + STAIR_PROJ_X / 2.0
    cx_stair = min(cx_stair, inner_x_half - STAIR_PROJ_X / 2.0)

    cy_stair = 0.0

    for i in range(NUM_FLOORS):
        base_z = PODIUM_HEIGHT + i * FLOOR_HEIGHT

        # First flight: from base_z → base_z + STAIR_RISE_PER_FLIGHT
        cz1 = base_z + STAIR_RISE_PER_FLIGHT / 2.0
        make_block(
            f"Stair_Flight_A_L{i:02d}",
            cx_stair, cy_stair, cz1,
            sx_flight, sy_flight, sz_flight,
            rot_axis=(0, 1, 0),
            rot_angle_deg=STAIR_ANGLE_DEG,
            collection="Stairs",
        )

        # Second flight: from base_z + R → base_z + 2R (next floor level)
        cz2 = base_z + STAIR_RISE_PER_FLIGHT * 3.0 / 2.0
        make_block(
            f"Stair_Flight_B_L{i:02d}",
            cx_stair, cy_stair, cz2,
            sx_flight, sy_flight, sz_flight,
            rot_axis=(0, 1, 0),
            rot_angle_deg=STAIR_ANGLE_DEG,
            collection="Stairs",
        )


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def build_clt_highrise(clear=True):
    if clear:
        clear_scene()

    # Ensure all collections exist before building
    for cname in [
        "Podium",
        "Walls_North", "Walls_South",
        "Walls_East", "Walls_West",
        "Walls_Interior",
        "Core",
        "Slabs",
        "Roof",
        "Stairs",
    ]:
        get_or_create_collection(cname)

    build_podium()
    build_long_facade_with_openings('N')
    build_long_facade_with_openings('S')
    build_short_facades()
    build_party_walls()
    build_core_with_openings()
    build_elevator_shaft()
    build_floor_slabs()
    build_roof()
    build_stairs()


# Execute when run inside Blender
if __name__ == "__main__":
    build_clt_highrise(clear=True)
