# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 09 - CHATGPT 5.1 - V10
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

NUM_FLOORS      = 10        # regular residential floors (above podium)
ROOF_FLOORS     = 2         # "storeys" of height in gable roof
FLOOR_HEIGHT    = 3.0       # floor-to-floor height

BUILDING_LENGTH = 30.0      # overall length (X)
BUILDING_WIDTH  = 14.0      # overall width  (Y)

CORE_LENGTH     = 6.0       # core length (X)
CORE_WIDTH      = 5.0       # core width  (Y)  <-- widened for stair room

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

DOOR_WIDTH          = 1.6   # core / interior doors
DOOR_HEIGHT         = 2.1

# Stairs (discrete treads, based on experiment_10)
STAIR_STEPS_PER_FLIGHT = 10        # risers per flight
STAIR_WIDTH            = 1.10      # stair width (across X)
STAIR_TREAD_DEPTH      = 0.25      # tread depth (along Y)
STAIR_LANDING_LENGTH   = 1.00      # landing depth (both floor & mid-level)
STAIR_LANDING_GAP      = 0.20      # X-gap between the two flights
STAIR_LANDING_THICK    = 0.15
STAIR_CLEAR_CORE_Y     = 0.05      # clearance to core walls (Y)
STAIR_CLEAR_ELEV_X     = 0.10      # clearance between elevator and stair

# Elevators – shallow in X, on the west side of the core
ELEVATOR_DEPTH         = 1.60      # depth along X
ELEVATOR_WIDTH_Y       = 1.60      # width along Y (per shaft)
ELEVATOR_CLEAR_TOP     = 0.0

# Middle core walkway
CORE_WALKWAY_CLEAR     = 0.05      # gap to elevators / stairs

# ------------------------------------------------------------------
# COLLECTION HELPERS
# ------------------------------------------------------------------

def get_or_create_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)

    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    return coll


def add_object_to_collection(obj_name: str, coll_name: str):
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return

    coll = get_or_create_collection(coll_name)

    if obj.name not in coll.objects:
        coll.objects.link(obj)

    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def clear_scene():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()


# ------------------------------------------------------------------
# BASIC BLOCK WRAPPER
# ------------------------------------------------------------------

def make_block(name,
               cx, cy, cz,
               sx, sy, sz,
               rot_axis=(0, 0, 1),
               rot_angle_deg=0.0,
               collection=None):
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
# CORE GEOMETRY HELPERS
# ------------------------------------------------------------------

def core_interior_bounds():
    """Interior faces of the CLT core walls."""
    x_min = -CORE_LENGTH / 2.0 + WALL_THICKNESS
    x_max =  CORE_LENGTH / 2.0 - WALL_THICKNESS
    y_min = -CORE_WIDTH  / 2.0 + WALL_THICKNESS
    y_max =  CORE_WIDTH  / 2.0 - WALL_THICKNESS
    return x_min, x_max, y_min, y_max


def elevator_bounds():
    """
    Bounding box of the elevator zone (both shafts together).
    Only the X-extent is used for the middle slab / stair offset,
    Y-extent is full core height.
    """
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    x_min_e = x_in_min
    x_max_e = min(x_in_min + ELEVATOR_DEPTH, x_in_max - 0.5)  # keep margin to stair
    return x_min_e, x_max_e, y_in_min, y_in_max


def stair_layout_params():
    """
    Origin and X-span for the double-flight stair:

    - Stair assembly hugs the +X interior face of the core.
    - y0 is the SOUTH-most Y of the stair assembly, equal to
      (south interior core wall + landing length), so the floor
      landing can extend from the south wall up to the first riser
      without gaps.
    """
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()

    double_width = 2.0 * STAIR_WIDTH + STAIR_LANDING_GAP

    # X: centre of both flights/landing, near +X interior core wall
    ox = x_in_max - STAIR_CLEAR_CORE_Y - double_width / 2.0

    # Y: south-most extent of stair geometry; floor landing will
    # extend from y_in_min to y0.
    y0 = y_in_min + STAIR_LANDING_LENGTH

    return ox, y0, double_width


def core_middle_slab_span():
    """
    X/Y span for the middle core slab (lobby between elevators and stairs),
    used both for slab geometry and to align the core doors.
    """
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    x_min_e, x_max_e, _, _ = elevator_bounds()
    ox_stair, _, double_width = stair_layout_params()
    x_stair_west = ox_stair - double_width / 2.0

    x_min = x_max_e + CORE_WALKWAY_CLEAR
    x_max = x_stair_west - CORE_WALKWAY_CLEAR
    return x_min, x_max, y_in_min, y_in_max


# ------------------------------------------------------------------
# RANDOM WINDOW LAYOUT
# ------------------------------------------------------------------

def window_centres_for(side_label: str, floor_index: int):
    """Randomised window centres along the building LENGTH (X)."""
    side_offset = 0 if side_label in {'N', 'S'} else 5000
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


def window_centres_for_short(side_label: str, floor_index: int):
    """Randomised window centres along the building WIDTH (Y) for E/W façades."""
    side_offset = 2000 if side_label == 'E' else 3000
    rng = random.Random(RANDOM_SEED + side_offset + floor_index * 19)

    centres = []
    segment = BUILDING_WIDTH / WINDOWS_PER_FACADE
    edge_margin = WINDOW_WIDTH / 2.0 + 1.0

    for k in range(WINDOWS_PER_FACADE):
        base = -BUILDING_WIDTH / 2.0 + (k + 0.5) * segment
        jitter = rng.uniform(-segment * 0.25, segment * 0.25)
        c = base + jitter
        c = max(c, -BUILDING_WIDTH / 2.0 + edge_margin)
        c = min(c,  BUILDING_WIDTH / 2.0 - edge_margin)
        centres.append(c)

    centres.sort()
    return centres


# ------------------------------------------------------------------
# ENVELOPE GEOMETRY
# ------------------------------------------------------------------

def build_podium():
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
    """North or South façade with random windows."""
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

        # Window piers
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
    """East and West façades with random windows."""
    sx = WALL_THICKNESS / 2.0

    for side_label in ('E', 'W'):
        is_east = side_label == 'E'
        coll_name = "Walls_East" if is_east else "Walls_West"
        x_pos = BUILDING_LENGTH / 2.0 if is_east else -BUILDING_LENGTH / 2.0

        for i in range(NUM_FLOORS):
            floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
            floor_top    = floor_bottom + FLOOR_HEIGHT

            sill_z = floor_bottom + WINDOW_SILL_HEIGHT
            head_z = sill_z + WINDOW_HEIGHT

            # lower band
            hz_low = (sill_z - floor_bottom) / 2.0
            if hz_low > 0.0:
                cz_low = floor_bottom + hz_low
                sy_low = BUILDING_WIDTH / 2.0
                make_block(
                    f"{side_label}_Wall_Low_L{i:02d}",
                    x_pos, 0.0, cz_low,
                    sx, sy_low, hz_low,
                    collection=coll_name,
                )

            # upper band
            hz_high = (floor_top - head_z) / 2.0
            if hz_high > 0.0:
                cz_high = head_z + hz_high
                sy_high = BUILDING_WIDTH / 2.0
                make_block(
                    f"{side_label}_Wall_High_L{i:02d}",
                    x_pos, 0.0, cz_high,
                    sx, sy_high, hz_high,
                    collection=coll_name,
                )

            # window piers along Y
            centres = window_centres_for_short(side_label, i)
            window_half = WINDOW_WIDTH / 2.0

            y_start = -BUILDING_WIDTH / 2.0
            segments = []
            for c in centres:
                left  = c - window_half
                right = c + window_half
                segments.append((y_start, left))
                y_start = right
            segments.append((y_start, BUILDING_WIDTH / 2.0))

            hz_mid = (head_z - sill_z) / 2.0
            cz_mid = sill_z + hz_mid

            for si, (a, b) in enumerate(segments):
                seg_width = b - a
                if seg_width <= 0.05:
                    continue
                sy_mid = seg_width / 2.0
                cy_mid = (a + b) / 2.0
                make_block(
                    f"{side_label}_Pier_L{i:02d}_{si}",
                    x_pos, cy_mid, cz_mid,
                    sx, sy_mid, hz_mid,
                    collection=coll_name,
                )


# ------------------------------------------------------------------
# CORE & INTERNAL WALLS
# ------------------------------------------------------------------

def build_core_with_openings():
    """
    Doors on BOTH +Y and -Y sides of the core, aligned with the
    central core slab span.
    """
    sy_long  = WALL_THICKNESS / 2.0
    sx_short = WALL_THICKNESS / 2.0

    core_slab_x_min, core_slab_x_max, _, _ = core_middle_slab_span()
    door_center_x = 0.5 * (core_slab_x_min + core_slab_x_max)
    door_half     = DOOR_WIDTH / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        door_bottom = floor_bottom
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_top = (floor_top - door_top) / 2.0
        cz_top = door_top + hz_top

        hz_mid = (door_top - door_bottom) / 2.0
        cz_mid = door_bottom + hz_mid

        x_left    = -CORE_LENGTH / 2.0
        x_right   =  CORE_LENGTH / 2.0
        door_left = door_center_x - door_half
        door_right= door_center_x + door_half

        segments  = [(x_left, door_left), (door_right, x_right)]

        for side_sign, suffix in ((+1, "+Y"), (-1, "-Y")):
            y_pos = side_sign * CORE_WIDTH / 2.0

            if hz_top > 0.0:
                make_block(
                    f"Core_Long_{suffix}_Top_L{i:02d}",
                    0.5 * (x_left + x_right), y_pos, cz_top,
                    (x_right - x_left) / 2.0, sy_long, hz_top,
                    collection="Core",
                )

            for si, (a, b) in enumerate(segments):
                seg_width = b - a
                if seg_width <= 0.05:
                    continue
                sx_mid = seg_width / 2.0
                cx_mid = (a + b) / 2.0
                make_block(
                    f"Core_Long_{suffix}_Pier_L{i:02d}_{si}",
                    cx_mid, y_pos, cz_mid,
                    sx_mid, sy_long, hz_mid,
                    collection="Core",
                )

        hz_full = FLOOR_HEIGHT / 2.0
        cz_full = floor_bottom + hz_full
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


def build_elevator_shafts():
    """
    Two separate elevator shafts, one in the south-west and one in the
    north-west corner of the core (hugging the -X wall).
    """
    x_min_e, x_max_e, y_in_min, y_in_max = elevator_bounds()
    x_center = 0.5 * (x_min_e + x_max_e)
    sx       = 0.5 * (x_max_e - x_min_e)

    half_y = ELEVATOR_WIDTH_Y / 2.0

    cy_s = y_in_min + half_y  # south-west shaft
    cy_n = y_in_max - half_y  # north-west shaft
    sy_s = half_y
    sy_n = half_y

    total_height = PODIUM_HEIGHT + BUILDING_HEIGHT + ROOF_HEIGHT + ELEVATOR_CLEAR_TOP
    sz = total_height / 2.0
    cz = sz

    make_block(
        "Elevator_Shaft_S",
        x_center, cy_s, cz,
        sx, sy_s, sz,
        collection="Core",
    )

    make_block(
        "Elevator_Shaft_N",
        x_center, cy_n, cz,
        sx, sy_n, sz,
        collection="Core",
    )


def build_party_walls():
    inside_x_min = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    inside_x_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS

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
    Existing E–W interior walls that separate apartments from the core
    corridor (with door openings).
    """
    inside_y_min = -BUILDING_WIDTH / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH / 2.0 - WALL_THICKNESS

    offset = CORE_WIDTH / 2.0 + CORRIDOR_WIDTH

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

        # NORTH
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

        # SOUTH
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


def build_extra_ns_partition_walls():
    """
    Two additional N–S interior walls per floor, at +/- BUILDING_LENGTH/4,
    splitting the long apartments into three bays.
    """
    inside_y_min = -BUILDING_WIDTH / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH / 2.0 - WALL_THICKNESS

    x_positions = [
        -BUILDING_LENGTH / 4.0,
        +BUILDING_LENGTH / 4.0,
    ]

    sx_wall = PARTY_WALL_T / 2.0
    sy_wall = (inside_y_max - inside_y_min) / 2.0
    cy_wall = (inside_y_min + inside_y_max) / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        hz_full = FLOOR_HEIGHT / 2.0
        cz_full = floor_bottom + hz_full

        for xi, x in enumerate(x_positions):
            make_block(
                f"Apt_NS_Wall_{xi}_L{i:02d}",
                x, cy_wall, cz_full,
                sx_wall, sy_wall, hz_full,
                collection="Walls_Interior",
            )


# ------------------------------------------------------------------
# SLABS – INCLUDING CORE MIDDLE SLAB
# ------------------------------------------------------------------

def build_floor_slabs():
    inside_x_min = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    inside_x_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS
    inside_y_min = -BUILDING_WIDTH  / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH  / 2.0 - WALL_THICKNESS

    core_x_min = -CORE_LENGTH / 2.0 - WALL_THICKNESS / 2.0
    core_x_max =  CORE_LENGTH / 2.0 + WALL_THICKNESS / 2.0
    core_y_min = -CORE_WIDTH  / 2.0 - WALL_THICKNESS / 2.0
    core_y_max =  CORE_WIDTH  / 2.0 + WALL_THICKNESS / 2.0

    core_slab_x_min, core_slab_x_max, y_in_min, y_in_max = core_middle_slab_span()

    sz = SLAB_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_top = PODIUM_HEIGHT + (i + 1) * FLOOR_HEIGHT
        cz        = floor_top - SLAB_THICKNESS / 2.0

        # Left wing
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

        # Right wing
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

        # North central slab
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

        # South central slab
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

        # Middle slab inside the core between elevators and stair
        if core_slab_x_max > core_slab_x_min:
            sx_core = (core_slab_x_max - core_slab_x_min) / 2.0
            cx_core = (core_slab_x_min + core_slab_x_max) / 2.0
            sy_core = (y_in_max - y_in_min) / 2.0
            cy_core = (y_in_min + y_in_max) / 2.0
            make_block(
                f"Slab_Core_L{i:02d}",
                cx_core, cy_core, cz,
                sx_core, sy_core, sz,
                collection="Slabs",
            )


def build_roof():
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
# STAIRS – DOUBLE FLIGHT AT +X CORE EDGE
# ------------------------------------------------------------------

def build_stairs():
    """
    Multi-storey U-shaped double-flight stair:

      - flights at +X core edge (shifted northwards),
      - floor-level landing spans from south interior core wall
        to the first riser (no gaps),
      - mid-height landing between flights.
    """
    steps_per_flight = STAIR_STEPS_PER_FLIGHT
    tread_depth      = STAIR_TREAD_DEPTH
    stair_width      = STAIR_WIDTH
    landing_length   = STAIR_LANDING_LENGTH
    landing_gap      = STAIR_LANDING_GAP
    landing_thick    = STAIR_LANDING_THICK

    visible_steps_per_flight = steps_per_flight - 1
    num_levels   = NUM_FLOORS
    num_segments = num_levels - 1

    total_steps_per_segment = 2 * steps_per_flight
    riser_height = FLOOR_HEIGHT / total_steps_per_segment

    flight_run_visible = visible_steps_per_flight * tread_depth

    # layout
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    ox, y0, double_width = stair_layout_params()
    oz = PODIUM_HEIGHT + FLOOR_HEIGHT  # first residential floor level

    step_sx = stair_width / 2.0
    step_sy = tread_depth / 2.0
    step_sz = riser_height / 2.0

    landing_sx = double_width / 2.0
    landing_sy = landing_length / 2.0
    landing_sz = landing_thick / 2.0

    x1 = ox - (stair_width + landing_gap) / 2.0   # west flight
    x2 = ox + (stair_width + landing_gap) / 2.0   # east flight

    for seg in range(num_segments):
        z0 = oz + seg * FLOOR_HEIGHT

        # Floor-level landing: south edge at y_in_min,
        # north edge at y0 -> Y-centre is (y_in_min + y0)/2
        y_floor_center = (y_in_min + y0) / 2.0
        z_floor_center = z0 - landing_thick / 2.0
        make_block(
            name=f"Landing_Floor_S{seg:02d}",
            cx=ox, cy=y_floor_center, cz=z_floor_center,
            sx=landing_sx, sy=(y0 - y_in_min) / 2.0, sz=landing_sz,
            collection="Stairs",
        )

        # First flight – up in +Y starting from y0
        for s in range(visible_steps_per_flight):
            cx = x1
            cy = y0 + tread_depth * (s + 0.5)
            cz = z0 + riser_height * (s + 0.5)

            make_block(
                name=f"Step_S{seg:02d}_F1_{s:02d}",
                cx=cx, cy=cy, cz=cz,
                sx=step_sx, sy=step_sy, sz=step_sz,
                collection="Stairs",
            )

        # Mid-level landing – between flights, near north wall
        y_near_landing   = y0 + flight_run_visible
        y_landing_center = y_near_landing + landing_length / 2.0

        z_landing_top    = z0 + riser_height * steps_per_flight
        z_landing_center = z_landing_top - landing_thick / 2.0

        make_block(
            name=f"Landing_Mid_S{seg:02d}",
            cx=ox, cy=y_landing_center, cz=z_landing_center,
            sx=landing_sx, sy=landing_sy, sz=landing_sz,
            collection="Stairs",
        )

        # Second flight – up in -Y from mid-landing back towards centre
        for k in range(visible_steps_per_flight):
            step_index = k + 1

            cx = x2
            cy = y_near_landing - tread_depth * (k + 0.5)
            cz = z0 + riser_height * (steps_per_flight + k + 0.5)

            make_block(
                name=f"Step_S{seg:02d}_F2_{step_index:02d}",
                cx=cx, cy=cy, cz=cz,
                sx=step_sx, sy=step_sy, sz=step_sz,
                collection="Stairs",
            )


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def build_clt_highrise(clear=True):
    if clear:
        clear_scene()

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
    build_extra_ns_partition_walls()

    build_core_with_openings()
    build_elevator_shafts()

    build_floor_slabs()
    build_roof()
    build_stairs()


if __name__ == "__main__":
    build_clt_highrise(clear=True)
