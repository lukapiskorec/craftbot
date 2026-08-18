# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 09 - CHATGPT 5.1 - V04
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
PARTY_WALL_T    = 0.16      # CLT party / internal wall thickness
SLAB_THICKNESS  = 0.24      # CLT floor slab thickness
ROOF_THICKNESS  = 0.16      # CLT roof panel thickness

PODIUM_HEIGHT   = 1.0       # concrete podium height

BUILDING_HEIGHT = NUM_FLOORS * FLOOR_HEIGHT
ROOF_HEIGHT     = ROOF_FLOORS * FLOOR_HEIGHT

CORRIDOR_WIDTH  = 2.0       # corridor between core and party wall

# Openings
WINDOW_SILL_HEIGHT  = 0.9
WINDOW_HEIGHT       = 1.4
WINDOW_WIDTH        = 3.0
WINDOWS_PER_FACADE  = 3
RANDOM_SEED         = 12345

DOOR_WIDTH          = 1.2
DOOR_HEIGHT         = 2.1

# Stairs
STAIR_THICKNESS       = 0.25
STAIR_CLEARANCE       = 0.2
STAIR_ANGLE_DEG       = 40.0
STAIR_RISE_PER_FLIGHT = FLOOR_HEIGHT / 2.0   # two flights per storey

STAIR_ANGLE_RAD       = math.radians(STAIR_ANGLE_DEG)
STAIR_FLIGHT_LENGTH   = STAIR_RISE_PER_FLIGHT / math.sin(STAIR_ANGLE_RAD)
STAIR_RUN             = STAIR_RISE_PER_FLIGHT / math.tan(STAIR_ANGLE_RAD)
STAIR_WIDTH           = 1.2  # width across X

# Elevator placeholder
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

    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    return coll


def add_object_to_collection(obj_name: str, coll_name: str):
    """Move the object to a named collection."""
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return

    coll = get_or_create_collection(coll_name)

    if obj.name not in coll.objects:
        coll.objects.link(obj)

    # unlink from the root scene collection to keep hierarchy tidy
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
# BASIC BLOCK WRAPPER (craftbot.place_element)
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
    side_offset = 0 if side_label == 'N' else 1000
    rng = random.Random(RANDOM_SEED + side_offset + floor_index * 17)

    centres = []
    segment = BUILDING_LENGTH / WINDOWS_PER_FACADE
    edge_margin = WINDOW_WIDTH / 2.0 + 1.0

    for k in range(WINDOWS_PER_FACADE):
        base = -BUILDING_LENGTH / 2.0 + (k + 0.5) * segment
        jitter = rng.uniform(-segment * 0.25, segment * 0.25)
        c = base + jitter
        c = max(c, -BUILDING_LENGTH / 2.0 + edge_margin)
        c = min(c,  BUILDING_LENGTH / 2.0 - edge_margin)
        centres.append(c)

    centres.sort()
    return centres


# ------------------------------------------------------------------
# ENVELOPE GEOMETRY
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

        # Lower band below windows
        hz_low  = (sill_z - floor_bottom) / 2.0
        if hz_low > 0.0:
            cz_low  = floor_bottom + hz_low
            sx_low  = BUILDING_LENGTH / 2.0
            make_block(
                f"{side_label}_Wall_Low_L{i:02d}",
                0.0, y_pos, cz_low,
                sx_low, sy, hz_low,
                collection=coll_name,
            )

        # Upper band above windows
        hz_high = (floor_top - head_z) / 2.0
        if hz_high > 0.0:
            cz_high = head_z + hz_high
            sx_high = BUILDING_LENGTH / 2.0
            make_block(
                f"{side_label}_Wall_High_L{i:02d}",
                0.0, y_pos, cz_high,
                sx_high, sy, hz_high,
                collection=coll_name,
            )

        # Vertical piers between window openings
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

        make_block(
            f"East_Wall_L{i:02d}",
            BUILDING_LENGTH / 2.0, 0.0, cz,
            sx, sy, hz,
            collection="Walls_East",
        )

        make_block(
            f"West_Wall_L{i:02d}",
            -BUILDING_LENGTH / 2.0, 0.0, cz,
            sx, sy, hz,
            collection="Walls_West",
        )


# ------------------------------------------------------------------
# CORE & INTERNAL WALLS
# ------------------------------------------------------------------

def build_core_with_openings():
    """
    Build CLT core walls with a door opening on the +Y long wall
    on every floor.
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
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_top = (floor_top - door_top) / 2.0
        cz_top = door_top + hz_top

        if hz_top > 0.0:
            make_block(
                f"Core_Long_+Y_Top_L{i:02d}",
                0.0, CORE_WIDTH / 2.0, cz_top,
                CORE_LENGTH / 2.0, sy_long, hz_top,
                collection="Core",
            )

        door_half = DOOR_WIDTH / 2.0
        x_left    = -CORE_LENGTH / 2.0
        x_right   = CORE_LENGTH / 2.0

        segments = [(x_left, -door_half), (door_half, x_right)]
        hz_mid   = (door_top - door_bottom) / 2.0
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
    the core – mainly to visualise separation from the stairs.
    """
    inner_x_half = CORE_LENGTH / 2.0 - WALL_THICKNESS

    sx = ELEVATOR_WIDTH_X / 2.0
    sy = ELEVATOR_WIDTH_Y / 2.0
    sz = (PODIUM_HEIGHT + BUILDING_HEIGHT + ROOF_HEIGHT) / 2.0

    # Place towards -X side of core interior
    cx = -(inner_x_half - sx)
    cy = 0.0
    cz = PODIUM_HEIGHT + BUILDING_HEIGHT / 2.0

    make_block(
        "Elevator_Shaft",
        cx, cy, cz,
        sx, sy, sz,
        collection="Core",
    )


def build_party_walls():
    """
    Party walls separating corridor (around core) and apartments
    on north and south sides, with a doorway per floor.
    """
    inside_x_min = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    inside_x_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS

    # position of party walls measured from centreline in Y
    offset = CORE_WIDTH / 2.0 + CORRIDOR_WIDTH
    sy = PARTY_WALL_T / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        door_bottom = floor_bottom
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_mid  = (door_top - door_bottom) / 2.0
        cz_mid  = door_bottom + hz_mid
        hz_top  = (floor_top - door_top) / 2.0
        cz_top  = door_top + hz_top

        x_door  = 0.0
        door_hf = DOOR_WIDTH / 2.0
        xL      = inside_x_min
        xR      = inside_x_max

        segments = [(xL, x_door - door_hf),
                    (x_door + door_hf, xR)]

        for side, label in ((+offset, "N"), (-offset, "S")):
            # vertical piers either side of door
            for si, (a, b) in enumerate(segments):
                seg_len = b - a
                if seg_len <= 0.05:
                    continue
                sx_seg = seg_len / 2.0
                cx_seg = (a + b) / 2.0
                make_block(
                    f"Party_{label}_Pier_L{i:02d}_{si}",
                    cx_seg, side, cz_mid,
                    sx_seg, sy, hz_mid,
                    collection="Walls_Interior",
                )

            # band above door
            sx_top = (inside_x_max - inside_x_min) / 2.0
            cx_top = (inside_x_min + inside_x_max) / 2.0
            if hz_top > 0.0:
                make_block(
                    f"Party_{label}_Top_L{i:02d}",
                    cx_top, side, cz_top,
                    sx_top, sy, hz_top,
                    collection="Walls_Interior",
                )


def build_apartment_internal_walls():
    """
    Additional internal walls splitting each apartment into two rooms
    (north & south apartments), with doors so all spaces are accessible.
    """
    inside_y_min = -BUILDING_WIDTH / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH / 2.0 - WALL_THICKNESS

    # party wall positions as in build_party_walls
    offset = CORE_WIDTH / 2.0 + CORRIDOR_WIDTH

    # apartment zones in Y
    yN_start = offset + PARTY_WALL_T / 2.0
    yN_end   = inside_y_max
    yS_end   = -offset - PARTY_WALL_T / 2.0
    yS_start = inside_y_min

    sx_wall  = PARTY_WALL_T / 2.0
    edge_margin = DOOR_WIDTH / 2.0 + 0.3

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        door_bottom = floor_bottom
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_mid  = (door_top - door_bottom) / 2.0
        cz_mid  = door_bottom + hz_mid
        hz_top  = (floor_top - door_top) / 2.0
        cz_top  = door_top + hz_top

        # NORTH internal wall (x = 0)
        if yN_end - yN_start > DOOR_WIDTH + 2 * edge_margin:
            y_doorN = yN_start + 1.5
            y_doorN = max(y_doorN, yN_start + edge_margin)
            y_doorN = min(y_doorN, yN_end - edge_margin)
            door_hf = DOOR_WIDTH / 2.0

            segmentsN = [
                (yN_start, y_doorN - door_hf),
                (y_doorN + door_hf, yN_end),
            ]

            for si, (a, b) in enumerate(segmentsN):
                seg_len = b - a
                if seg_len <= 0.05:
                    continue
                sy_seg = seg_len / 2.0
                cy_seg = (a + b) / 2.0
                make_block(
                    f"IntWall_N_Pier_L{i:02d}_{si}",
                    0.0, cy_seg, cz_mid,
                    sx_wall, sy_seg, hz_mid,
                    collection="Walls_Interior",
                )

            sy_top = (yN_end - yN_start) / 2.0
            cy_top = (yN_start + yN_end) / 2.0
            if hz_top > 0.0:
                make_block(
                    f"IntWall_N_Top_L{i:02d}",
                    0.0, cy_top, cz_top,
                    sx_wall, sy_top, hz_top,
                    collection="Walls_Interior",
                )

        # SOUTH internal wall (x = 0)
        if yS_end - yS_start > DOOR_WIDTH + 2 * edge_margin:
            y_doorS = yS_end - 1.5
            y_doorS = max(y_doorS, yS_start + edge_margin)
            y_doorS = min(y_doorS, yS_end - edge_margin)
            door_hf = DOOR_WIDTH / 2.0

            segmentsS = [
                (yS_start, y_doorS - door_hf),
                (y_doorS + door_hf, yS_end),
            ]

            for si, (a, b) in enumerate(segmentsS):
                seg_len = b - a
                if seg_len <= 0.05:
                    continue
                sy_seg = seg_len / 2.0
                cy_seg = (a + b) / 2.0
                make_block(
                    f"IntWall_S_Pier_L{i:02d}_{si}",
                    0.0, cy_seg, cz_mid,
                    sx_wall, sy_seg, hz_mid,
                    collection="Walls_Interior",
                )

            sy_top = (yS_end - yS_start) / 2.0
            cy_top = (yS_start + yS_end) / 2.0
            if hz_top > 0.0:
                make_block(
                    f"IntWall_S_Top_L{i:02d}",
                    0.0, cy_top, cz_top,
                    sx_wall, sy_top, hz_top,
                    collection="Walls_Interior",
                )


# ------------------------------------------------------------------
# SLABS – CONTINUOUS AROUND CORE (NO GAPS)
# ------------------------------------------------------------------

def build_floor_slabs():
    """
    Build floor slabs that are flush and continuous around the core.
    Walls have priority: slabs stop at the inner faces of the exterior
    walls and at the outer faces of the core walls.
    """
    inside_x_min = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    inside_x_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS
    inside_y_min = -BUILDING_WIDTH  / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH  / 2.0 - WALL_THICKNESS

    # outer faces of core walls
    core_x_min = -CORE_LENGTH / 2.0 - WALL_THICKNESS / 2.0
    core_x_max =  CORE_LENGTH / 2.0 + WALL_THICKNESS / 2.0
    core_y_min = -CORE_WIDTH  / 2.0 - WALL_THICKNESS / 2.0
    core_y_max =  CORE_WIDTH  / 2.0 + WALL_THICKNESS / 2.0

    sz = SLAB_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_top = PODIUM_HEIGHT + (i + 1) * FLOOR_HEIGHT
        cz        = floor_top - SLAB_THICKNESS / 2.0

        # Left wing slab (west of core)
        if core_x_min > inside_x_min:
            sx = (core_x_min - inside_x_min) / 2.0
            cx = (core_x_min + inside_x_min) / 2.0
            sy = (inside_y_max - inside_y_min) / 2.0
            cy = (inside_y_min + inside_y_max) / 2.0
            make_block(
                f"Slab_Left_L{i:02d}",
                cx, cy, cz,
                sx, sy, sz,
                collection="Slabs",
            )

        # Right wing slab (east of core)
        if inside_x_max > core_x_max:
            sx = (inside_x_max - core_x_max) / 2.0
            cx = (inside_x_max + core_x_max) / 2.0
            sy = (inside_y_max - inside_y_min) / 2.0
            cy = (inside_y_min + inside_y_max) / 2.0
            make_block(
                f"Slab_Right_L{i:02d}",
                cx, cy, cz,
                sx, sy, sz,
                collection="Slabs",
            )

        # North central slab (above core)
        if inside_y_max > core_y_max:
            sy = (inside_y_max - core_y_max) / 2.0
            cy = (inside_y_max + core_y_max) / 2.0
            sx = (core_x_max - core_x_min) / 2.0
            cx = (core_x_max + core_x_min) / 2.0
            make_block(
                f"Slab_North_L{i:02d}",
                cx, cy, cz,
                sx, sy, sz,
                collection="Slabs",
            )

        # South central slab (below core)
        if core_y_min > inside_y_min:
            sy = (core_y_min - inside_y_min) / 2.0
            cy = (core_y_min + inside_y_min) / 2.0
            sx = (core_x_max - core_x_min) / 2.0
            cx = (core_x_max + core_x_min) / 2.0
            make_block(
                f"Slab_South_L{i:02d}",
                cx, cy, cz,
                sx, sy, sz,
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


# ------------------------------------------------------------------
# STAIRS – DOUBLE FLIGHT WITH LANDING
# ------------------------------------------------------------------

def build_stairs():
    """
    Double-flight dogleg stair per storey inside the core, with a
    separate landing slab at mid-height.

    - Elevator shaft occupies the -X side of the core.
    - Stairs sit on the +X side inside the core.
    """
    inner_x_face_east = CORE_LENGTH / 2.0 - WALL_THICKNESS / 2.0
    inner_y_half      = CORE_WIDTH  / 2.0 - WALL_THICKNESS / 2.0

    sx_flight = STAIR_WIDTH / 2.0
    sy_flight = STAIR_FLIGHT_LENGTH / 2.0
    sz_flight = STAIR_THICKNESS / 2.0

    # Stairs placed near east interior face of core, with a small clearance
    cx = inner_x_face_east - sx_flight - STAIR_CLEARANCE

    for i in range(NUM_FLOORS):
        base_z = PODIUM_HEIGHT + i * FLOOR_HEIGHT

        # Landing slab at mid-height between storeys
        z_land   = base_z + STAIR_RISE_PER_FLIGHT
        sx_land  = STAIR_WIDTH / 2.0
        sy_land  = min(inner_y_half - 0.1, STAIR_RUN / 2.0)
        sz_land  = SLAB_THICKNESS / 2.0
        make_block(
            f"Stair_Landing_L{i:02d}",
            cx, 0.0, z_land + sz_land,
            sx_land, sy_land, sz_land,
            collection="Stairs",
        )

        # Lower flight (from floor up to landing, leaning towards +Y)
        cy1 = -(inner_y_half - sy_flight)
        cz1 = base_z + STAIR_RISE_PER_FLIGHT / 2.0
        make_block(
            f"Stair_Flight_Lower_L{i:02d}",
            cx, cy1, cz1,
            sx_flight, sy_flight, sz_flight,
            rot_axis=(1, 0, 0),
            rot_angle_deg=STAIR_ANGLE_DEG,
            collection="Stairs",
        )

        # Upper flight (from landing up to next floor, leaning towards -Y)
        cy2 = +(inner_y_half - sy_flight)
        cz2 = base_z + STAIR_RISE_PER_FLIGHT * 3.0 / 2.0
        make_block(
            f"Stair_Flight_Upper_L{i:02d}",
            cx, cy2, cz2,
            sx_flight, sy_flight, sz_flight,
            rot_axis=(1, 0, 0),
            rot_angle_deg=-STAIR_ANGLE_DEG,
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
    build_apartment_internal_walls()

    build_core_with_openings()
    build_elevator_shaft()

    build_floor_slabs()
    build_roof()
    build_stairs()


# Execute when run inside Blender
if __name__ == "__main__":
    build_clt_highrise(clear=True)
