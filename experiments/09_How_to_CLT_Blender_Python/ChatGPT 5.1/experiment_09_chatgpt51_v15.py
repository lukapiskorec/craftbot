# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 09 - CHATGPT 5.1 - V15
# HOW TO CLT
# ------------------------------------------------------------------

import bpy
import math
import random
import importlib

import craftbot_lib as craftbot
importlib.reload(craftbot)

# ------------------------------------------------------------------
# GLOBAL PARAMETERS
# ------------------------------------------------------------------

NUM_FLOORS      = 10
ROOF_FLOORS     = 2
FLOOR_HEIGHT    = 3.0

BUILDING_LENGTH = 30.0
BUILDING_WIDTH  = 14.0

CORE_LENGTH     = 6.0
CORE_WIDTH      = 5.0

WALL_THICKNESS  = 0.16
PARTY_WALL_T    = 0.16
SLAB_THICKNESS  = 0.24
ROOF_THICKNESS  = 0.16

PODIUM_HEIGHT   = 1.0
BUILDING_HEIGHT = NUM_FLOORS * FLOOR_HEIGHT
ROOF_HEIGHT     = ROOF_FLOORS * FLOOR_HEIGHT

# Long façades (north/south)
WINDOW_SILL_HEIGHT  = 0.9
WINDOW_HEIGHT       = 1.4
WINDOW_WIDTH        = 3.0
WINDOWS_PER_FACADE  = 3
RANDOM_SEED         = 12345

# Short façades (east/west) – smaller windows
WINDOW_WIDTH_EW        = 1.5
WINDOWS_PER_FACADE_EW  = 2

# Doors
DOOR_WIDTH   = 1.6
DOOR_HEIGHT  = 2.1

# Stairs
STAIR_STEPS_PER_FLIGHT = 10
STAIR_WIDTH            = 1.10
STAIR_TREAD_DEPTH      = 0.25
STAIR_LANDING_LENGTH   = 1.00
STAIR_LANDING_GAP      = 0.20
STAIR_LANDING_THICK    = 0.15
STAIR_CLEAR_CORE_Y     = 0.05
STAIR_CLEAR_ELEV_X     = 0.10  # kept for potential future use

# Elevators – on west (-X) side of core
ELEVATOR_DEPTH   = 1.60
ELEVATOR_WIDTH_Y = 1.60

# Core middle slab clearance
CORE_WALKWAY_CLEAR = 0.05


# ------------------------------------------------------------------
# COLLECTION & SCENE HELPERS
# ------------------------------------------------------------------

def get_or_create_collection(name: str) -> bpy.types.Collection:
    """Return existing collection or create a new one and link it to the scene."""
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)

    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    return coll


def add_object_to_collection(obj_name: str, coll_name: str):
    """Ensure object is in the target collection and not in the master scene root."""
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return

    coll = get_or_create_collection(coll_name)
    if obj.name not in coll.objects:
        coll.objects.link(obj)

    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def clear_scene():
    """Remove all mesh objects from the current scene."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()


# ------------------------------------------------------------------
# BASIC BLOCK WRAPPER
# ------------------------------------------------------------------

def make_block(
    name,
    cx, cy, cz,
    sx, sy, sz,
    rot_axis=(0, 0, 1),
    rot_angle_deg=0.0,
    collection=None,
):
    """Convenience wrapper calling craftbot.place_element and assigning collection."""
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
# CORE & STAIR LAYOUT HELPERS
# ------------------------------------------------------------------

def core_interior_bounds():
    """Interior faces of the CLT core walls."""
    x_min = -CORE_LENGTH / 2.0 + WALL_THICKNESS
    x_max =  CORE_LENGTH / 2.0 - WALL_THICKNESS
    y_min = -CORE_WIDTH  / 2.0 + WALL_THICKNESS
    y_max =  CORE_WIDTH  / 2.0 - WALL_THICKNESS
    return x_min, x_max, y_min, y_max


def elevator_bounds():
    """Interior X-span used for both elevator shafts on the west side."""
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    x_min_e = x_in_min
    x_max_e = min(x_in_min + ELEVATOR_DEPTH, x_in_max - 0.5)
    return x_min_e, x_max_e, y_in_min, y_in_max


def stair_layout_params():
    """
    Origin and X-span for the double-flight stair, shifted toward the
    north interior core wall but leaving a gap on the south.
    """
    x_in_min, x_in_max, y_in_min, _ = core_interior_bounds()
    double_width = 2.0 * STAIR_WIDTH + STAIR_LANDING_GAP
    ox = x_in_max - STAIR_CLEAR_CORE_Y - double_width / 2.0
    y0 = y_in_min + STAIR_LANDING_LENGTH
    return ox, y0, double_width


def core_middle_slab_span():
    """X/Y span for the middle core slab (between elevators and stairs)."""
    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    x_min_e, x_max_e, _, _ = elevator_bounds()
    ox_stair, _, double_width = stair_layout_params()
    x_stair_west = ox_stair - double_width / 2.0

    x_min = x_max_e + CORE_WALKWAY_CLEAR
    x_max = x_stair_west - CORE_WALKWAY_CLEAR
    return x_min, x_max, y_in_min, y_in_max


# ------------------------------------------------------------------
# RANDOM WINDOW LAYOUT – LONG FAÇADES
# ------------------------------------------------------------------

def window_centres_for(side_label: str, floor_index: int):
    """
    Randomised window centres along the building length (X) for
    north/south façades. Side label is 'N' or 'S'.
    """
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
    """North or South façade with randomised windows."""
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

        # Lower band
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

        # Upper band
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
    """
    East and West façades with smaller windows and slight randomisation.
    Windows never cross the middle where the interior wall meets the façade.
    """
    sx = WALL_THICKNESS / 2.0

    inside_y_min = -BUILDING_WIDTH / 2.0
    inside_y_max =  BUILDING_WIDTH / 2.0
    side_margin  = 1.5
    window_half  = WINDOW_WIDTH_EW / 2.0
    central_clear_half = PARTY_WALL_T  # keep clear around y = 0

    for side_label in ('E', 'W'):
        is_east = side_label == 'E'
        coll_name = "Walls_East" if is_east else "Walls_West"
        x_pos = BUILDING_LENGTH / 2.0 if is_east else -BUILDING_LENGTH / 2.0
        side_offset = 0 if is_east else 2000

        for i in range(NUM_FLOORS):
            rng = random.Random(RANDOM_SEED + side_offset + i * 29)

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

            # randomised window centres (south and north), kept away from y=0
            min_c_s = inside_y_min + side_margin + window_half
            max_c_s = -central_clear_half - window_half
            base_s  = 0.5 * (min_c_s + max_c_s)
            c_s = max(min_c_s, min(max_c_s, base_s + rng.uniform(-0.5, 0.5)))

            min_c_n = central_clear_half + window_half
            max_c_n = inside_y_max - side_margin - window_half
            base_n  = 0.5 * (min_c_n + max_c_n)
            c_n = max(min_c_n, min(max_c_n, base_n + rng.uniform(-0.5, 0.5)))

            centres = [c_s, c_n]
            centres.sort()

            hz_mid = (head_z - sill_z) / 2.0
            cz_mid = sill_z + hz_mid

            segments = []
            y_left = inside_y_min
            for c in centres:
                left  = c - window_half
                right = c + window_half
                segments.append((y_left, left))
                y_left = right
            segments.append((y_left, inside_y_max))

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
# CORE & ELEVATORS
# ------------------------------------------------------------------

def build_core_with_openings():
    """
    Long core walls (+Y/-Y) with doors aligned to the middle slab,
    and short core walls (+X/-X) without openings.
    """
    sy_long  = WALL_THICKNESS / 2.0
    sx_short = WALL_THICKNESS / 2.0

    core_slab_x_min, core_slab_x_max, _, _ = core_middle_slab_span()
    door_center_x = 0.5 * (core_slab_x_min + core_slab_x_max)
    door_half     = DOOR_WIDTH / 2.0

    x_left    = -CORE_LENGTH / 2.0
    x_right   =  CORE_LENGTH / 2.0

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        door_bottom = floor_bottom
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_top = (floor_top - door_top) / 2.0
        cz_top = door_top + hz_top

        hz_mid = (door_top - door_bottom) / 2.0
        cz_mid = door_bottom + hz_mid

        door_left  = door_center_x - door_half
        door_right = door_center_x + door_half
        segments   = [(x_left, door_left), (door_right, x_right)]

        for side_sign, suffix in ((+1, "+Y"), (-1, "-Y")):
            y_pos = side_sign * CORE_WIDTH / 2.0

            # top band above door
            if hz_top > 0.0:
                make_block(
                    f"Core_Long_{suffix}_Top_L{i:02d}",
                    0.5 * (x_left + x_right), y_pos, cz_top,
                    (x_right - x_left) / 2.0, sy_long, hz_top,
                    collection="Core",
                )

            # mid band with door opening
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

        # short walls (+X/-X)
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
    Two elevator shafts split per floor, each built as four walls.
    Door openings are on the EAST wall of each shaft, facing the
    core's middle slab.
    """
    x_min_e, x_max_e, y_in_min, y_in_max = elevator_bounds()

    # South shaft interior Y extents
    y_s_in_min = y_in_min
    y_s_in_max = y_in_min + ELEVATOR_WIDTH_Y

    # North shaft interior Y extents
    y_n_in_max = y_in_max
    y_n_in_min = y_in_max - ELEVATOR_WIDTH_Y

    def build_shaft(tag, x_min_inner, x_max_inner, y_in_min_shaft, y_in_max_shaft):
        x_center_int = 0.5 * (x_min_inner + x_max_inner)
        y_center_int = 0.5 * (y_in_min_shaft + y_in_max_shaft)

        ext_x = (x_max_inner - x_min_inner) + 2.0 * WALL_THICKNESS
        ext_y = (y_in_max_shaft - y_in_min_shaft) + 2.0 * WALL_THICKNESS

        x_west_center = x_min_inner - WALL_THICKNESS / 2.0
        x_east_center = x_max_inner + WALL_THICKNESS / 2.0
        sx_side       = WALL_THICKNESS / 2.0
        sy_side_full  = ext_y / 2.0

        y_south_center = y_in_min_shaft - WALL_THICKNESS / 2.0
        y_north_center = y_in_max_shaft + WALL_THICKNESS / 2.0
        sy_front       = WALL_THICKNESS / 2.0
        sx_front       = ext_x / 2.0

        # Door on EAST wall, narrower than shaft width (along Y)
        door_half_y   = DOOR_WIDTH / 2.0
        door_center_y = y_center_int

        y_wall_min = y_in_min_shaft - WALL_THICKNESS
        y_wall_max = y_in_max_shaft + WALL_THICKNESS

        for i in range(NUM_FLOORS):
            floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
            floor_top    = floor_bottom + FLOOR_HEIGHT

            hz_full = FLOOR_HEIGHT / 2.0
            cz_full = floor_bottom + hz_full

            # West wall – full height
            make_block(
                f"Elev_{tag}_W_L{i:02d}",
                x_west_center, y_center_int, cz_full,
                sx_side, sy_side_full, hz_full,
                collection="Core",
            )

            # North & south walls – full height
            make_block(
                f"Elev_{tag}_N_L{i:02d}",
                x_center_int, y_north_center, cz_full,
                sx_front, sy_front, hz_full,
                collection="Core",
            )
            make_block(
                f"Elev_{tag}_S_L{i:02d}",
                x_center_int, y_south_center, cz_full,
                sx_front, sy_front, hz_full,
                collection="Core",
            )

            # EAST wall with door opening
            door_bottom = floor_bottom
            door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

            hz_top = (floor_top - door_top) / 2.0
            cz_top = door_top + hz_top

            hz_mid = (door_top - door_bottom) / 2.0
            cz_mid = door_bottom + hz_mid

            door_y_min = door_center_y - door_half_y
            door_y_max = door_center_y + door_half_y
            segments = [
                (y_wall_min, door_y_min),
                (door_y_max, y_wall_max),
            ]

            # top band – full Y
            if hz_top > 0.0:
                make_block(
                    f"Elev_{tag}_E_Top_L{i:02d}",
                    x_east_center, 0.5 * (y_wall_min + y_wall_max), cz_top,
                    sx_side, (y_wall_max - y_wall_min) / 2.0, hz_top,
                    collection="Core",
                )

            # mid band with door opening
            for si, (a, b) in enumerate(segments):
                seg_len = b - a
                if seg_len <= 0.05:
                    continue
                sy_seg = seg_len / 2.0
                cy_seg = (a + b) / 2.0
                make_block(
                    f"Elev_{tag}_E_Mid_L{i:02d}_{si}",
                    x_east_center, cy_seg, cz_mid,
                    sx_side, sy_seg, hz_mid,
                    collection="Core",
                )

    build_shaft("S", x_min_e, x_max_e, y_s_in_min, y_s_in_max)
    build_shaft("N", x_min_e, x_max_e, y_n_in_min, y_n_in_max)


# ------------------------------------------------------------------
# INTERIOR WALLS – DIAGRAM ALIGNMENT
# ------------------------------------------------------------------

def build_interior_walls_diagram():
    """
    Interior walls following the diagram:

    - One east–west wall through the middle (y = 0) with no openings.
    - Two north–south walls that extend the core's ±X walls out
      to the façades. Each N–S wall has two door openings (one
      per apartment) close to the core.
    - N–S walls are shifted one wall thickness towards the centre
      so they align with the interior faces of the core ±X walls.
    """
    inside_x_min = -BUILDING_LENGTH / 2.0 + WALL_THICKNESS
    inside_x_max =  BUILDING_LENGTH / 2.0 - WALL_THICKNESS
    inside_y_min = -BUILDING_WIDTH  / 2.0 + WALL_THICKNESS
    inside_y_max =  BUILDING_WIDTH  / 2.0 - WALL_THICKNESS

    # Core outer faces
    y_core_south_outer = -CORE_WIDTH / 2.0 - WALL_THICKNESS / 2.0
    y_core_north_outer =  CORE_WIDTH / 2.0 + WALL_THICKNESS / 2.0
    x_core_west_outer  = -CORE_LENGTH / 2.0 - WALL_THICKNESS / 2.0
    x_core_east_outer  =  CORE_LENGTH / 2.0 + WALL_THICKNESS / 2.0

    # N–S walls: shift one wall thickness towards centre
    x_ns_west = x_core_west_outer - PARTY_WALL_T / 2.0 + WALL_THICKNESS
    x_ns_east = x_core_east_outer + PARTY_WALL_T / 2.0 - WALL_THICKNESS
    sx_ns     = PARTY_WALL_T / 2.0

    # Apartment extents (south and north)
    apt_south_min = inside_y_min
    apt_south_max = y_core_south_outer
    apt_north_min = y_core_north_outer
    apt_north_max = inside_y_max

    door_half_y  = DOOR_WIDTH / 2.0
    door_offset  = 0.30

    def clamp(v, a, b):
        return max(a, min(b, v))

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        floor_top    = floor_bottom + FLOOR_HEIGHT

        door_bottom = floor_bottom
        door_top    = min(floor_bottom + DOOR_HEIGHT, floor_top - 0.2)

        hz_mid = (door_top - door_bottom) / 2.0
        cz_mid = door_bottom + hz_mid

        hz_top = (floor_top - door_top) / 2.0
        cz_top = door_top + hz_top

        # door centres along Y
        y_door_south = clamp(
            y_core_south_outer - (door_half_y + door_offset),
            apt_south_min + door_half_y,
            apt_south_max - door_half_y,
        )
        y_door_north = clamp(
            y_core_north_outer + (door_half_y + door_offset),
            apt_north_min + door_half_y,
            apt_north_max - door_half_y,
        )

        segs_south = [
            (apt_south_min, y_door_south - door_half_y),
            (y_door_south + door_half_y, apt_south_max),
        ]
        segs_north = [
            (apt_north_min, y_door_north - door_half_y),
            (y_door_north + door_half_y, apt_north_max),
        ]

        for x_ns, tag in ((x_ns_west, "W"), (x_ns_east, "E")):
            # mid band with door openings
            for si, (a, b) in enumerate(segs_south + segs_north):
                seg_len = b - a
                if seg_len <= 0.05:
                    continue
                sy_seg = seg_len / 2.0
                cy_seg = (a + b) / 2.0
                make_block(
                    f"Int_NS_{tag}_Mid_L{i:02d}_{si}",
                    x_ns, cy_seg, cz_mid,
                    sx_ns, sy_seg, hz_mid,
                    collection="Walls_Interior",
                )

            # top band continuous per apartment (no doors)
            if hz_top > 0.0:
                for sj, (a, b) in enumerate(
                    ((apt_south_min, apt_south_max),
                     (apt_north_min, apt_north_max))
                ):
                    seg_len = b - a
                    if seg_len <= 0.05:
                        continue
                    sy_seg = seg_len / 2.0
                    cy_seg = (a + b) / 2.0
                    make_block(
                        f"Int_NS_{tag}_Top_L{i:02d}_{sj}",
                        x_ns, cy_seg, cz_top,
                        sx_ns, sy_seg, hz_top,
                        collection="Walls_Interior",
                    )

    # East–west middle wall (y=0), no openings, split left/right of core.
    y_mid = 0.0
    sy_ew = PARTY_WALL_T / 2.0

    segs_x = [
        (inside_x_min, x_core_west_outer),
        (x_core_east_outer, inside_x_max),
    ]

    for i in range(NUM_FLOORS):
        floor_bottom = PODIUM_HEIGHT + i * FLOOR_HEIGHT
        hz_full      = FLOOR_HEIGHT / 2.0
        cz_full      = floor_bottom + hz_full

        for sk, (a, b) in enumerate(segs_x):
            seg_len = b - a
            if seg_len <= 0.05:
                continue
            sx_seg = seg_len / 2.0
            cx_seg = (a + b) / 2.0
            make_block(
                f"Int_EW_Mid_L{i:02d}_{sk}",
                cx_seg, y_mid, cz_full,
                sx_seg, sy_ew, hz_full,
                collection="Walls_Interior",
            )


# ------------------------------------------------------------------
# SLABS
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
    x_min_e, x_max_e, y_in_min_e, y_in_max_e = elevator_bounds()

    # interior gap between the two elevator shafts (along Y)
    y_s_in_max = y_in_min_e + ELEVATOR_WIDTH_Y
    y_n_in_min = y_in_max_e - ELEVATOR_WIDTH_Y

    sz = SLAB_THICKNESS / 2.0

    for i in range(NUM_FLOORS):
        floor_top = PODIUM_HEIGHT + (i + 1) * FLOOR_HEIGHT
        cz        = floor_top - SLAB_THICKNESS / 2.0

        # left wing
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

        # right wing
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

        # north central
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

        # south central
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

        # middle slab inside core between elevators and stair
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

        # small slab between the two elevator shafts (closing the gap)
        if y_n_in_min > y_s_in_max:
            sx_e = (x_max_e - x_min_e) / 2.0
            cx_e = (x_max_e + x_min_e) / 2.0
            sy_e = (y_n_in_min - y_s_in_max) / 2.0
            cy_e = (y_n_in_min + y_s_in_max) / 2.0
            make_block(
                f"Slab_ElevGap_L{i:02d}",
                cx_e, cy_e, cz,
                sx_e, sy_e, sz,
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
# STAIRS – DOUBLE FLIGHT
# ------------------------------------------------------------------

def build_stairs():
    """
    Multi-storey U-shaped double-flight stair:

      - connects from podium level up to the top residential floor;
      - floor landing at each lower level inside the core, mid landing
        at half level, and a final top landing at the level of the
        last slabs (same Y extent as the floor landings).
    """
    steps_per_flight = STAIR_STEPS_PER_FLIGHT
    tread_depth      = STAIR_TREAD_DEPTH
    stair_width      = STAIR_WIDTH
    landing_gap      = STAIR_LANDING_GAP
    landing_thick    = STAIR_LANDING_THICK

    visible_steps_per_flight = steps_per_flight - 1
    total_steps_per_segment  = 2 * steps_per_flight
    riser_height             = FLOOR_HEIGHT / total_steps_per_segment

    flight_run_visible = visible_steps_per_flight * tread_depth

    x_in_min, x_in_max, y_in_min, y_in_max = core_interior_bounds()
    ox, y0, double_width = stair_layout_params()
    oz = PODIUM_HEIGHT  # first segment starts at podium level

    step_sx = stair_width / 2.0
    step_sy = tread_depth / 2.0
    step_sz = riser_height / 2.0

    x1 = ox - (stair_width + landing_gap) / 2.0   # west flight
    x2 = ox + (stair_width + landing_gap) / 2.0   # east flight

    num_levels   = NUM_FLOORS + 1
    num_segments = num_levels - 1

    for seg in range(num_segments):
        z0 = oz + seg * FLOOR_HEIGHT

        # -------- Floor-level landing (south) --------
        y_floor_south  = y_in_min
        y_floor_north  = y0
        y_floor_center = (y_floor_south + y_floor_north) / 2.0
        sy_floor       = (y_floor_north - y_floor_south) / 2.0

        z_floor_center = z0 - landing_thick / 2.0
        make_block(
            name=f"Landing_Floor_S{seg:02d}",
            cx=ox, cy=y_floor_center, cz=z_floor_center,
            sx=double_width / 2.0, sy=sy_floor, sz=landing_thick / 2.0,
            collection="Stairs",
        )

        # -------- First flight – up in +Y --------
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

        # -------- Mid landing (north) --------
        y_near_landing   = y0 + flight_run_visible
        y_mid_south      = y_near_landing
        y_mid_north      = y_in_max
        y_landing_center = (y_mid_south + y_mid_north) / 2.0
        sy_mid           = (y_mid_north - y_mid_south) / 2.0

        z_landing_top    = z0 + riser_height * steps_per_flight
        z_landing_center = z_landing_top - landing_thick / 2.0

        make_block(
            name=f"Landing_Mid_S{seg:02d}",
            cx=ox, cy=y_landing_center, cz=z_landing_center,
            sx=double_width / 2.0, sy=sy_mid, sz=landing_thick / 2.0,
            collection="Stairs",
        )

        # -------- Second flight – back down in -Y --------
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

    # -------- Top landing at last floor level (like floor landing) --------
    x_in_min, x_in_max, y_in_min, _ = core_interior_bounds()
    ox, y0, double_width = stair_layout_params()

    y_floor_south  = y_in_min
    y_floor_north  = y0
    y_floor_center = (y_floor_south + y_floor_north) / 2.0
    sy_floor       = (y_floor_north - y_floor_south) / 2.0

    top_floor_bottom = PODIUM_HEIGHT + NUM_FLOORS * FLOOR_HEIGHT
    z_top_center     = top_floor_bottom - landing_thick / 2.0

    make_block(
        name="Landing_Top",
        cx=ox, cy=y_floor_center, cz=z_top_center,
        sx=double_width / 2.0, sy=sy_floor, sz=landing_thick / 2.0,
        collection="Stairs",
    )


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def build_clt_highrise(clear=True):
    if clear:
        clear_scene()

    # Ensure all collections exist
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

    # Envelope
    build_podium()
    build_long_facade_with_openings('N')
    build_long_facade_with_openings('S')
    build_short_facades()

    # Core + vertical circulation
    build_core_with_openings()
    build_elevator_shafts()
    build_interior_walls_diagram()

    # Floors + roof
    build_floor_slabs()
    build_roof()

    # Stairs
    build_stairs()


if __name__ == "__main__":
    build_clt_highrise(clear=True)
