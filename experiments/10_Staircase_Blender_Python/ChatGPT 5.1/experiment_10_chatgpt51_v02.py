# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 10 - CHATGPT 5.1 - V02
# STAIRCASE
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # make sure craftbot_lib.py is on sys.path

# For interactive tweaking during development
importlib.reload(craftbot)


def build_double_flight_stair(
        num_levels=10,
        floor_height=3.0,
        steps_per_flight=10,
        stair_width=1.10,
        tread_depth=0.28,
        landing_length=None,
        landing_gap=0.20,
        landing_thickness=0.15,
        floor_thickness=0.20,
        floor_side_factor=3.0,
        floor_clearance=0.05,
        origin=(0.0, 0.0, 0.0),
):
    """
    Build a multi-storey U-shaped double-flight stair using only scaled cubes.

    Geometric conventions
    ---------------------
    - Z axis: vertical (up).
    - First flight (F1) runs in +Y.
    - Second flight (F2) runs back in -Y.
    - Landings span in X between the two flights and sit at mid-height.

    Parameters
    ----------
    num_levels        : total number of floor levels (e.g. 10 => 9 segments)
    floor_height      : floor-to-floor height
    steps_per_flight  : number of risers per flight
    stair_width       : width of each stair flight
    tread_depth       : depth of a tread along Y
    landing_length    : length of mid-landing along Y (if None, = stair_width)
    landing_gap       : gap between the two flights in X
    landing_thickness : landing slab thickness
    floor_thickness   : floor slab thickness
    floor_side_factor : factor for floor slab length on the side opposite landing
    floor_clearance   : Y-gap between stairwell and floor slab (no overlap)
    origin            : (x, y, z) base reference of stair tower
    """

    if landing_length is None:
        landing_length = stair_width

    # ------------------------------------------------------------------
    # Derived parameters
    # ------------------------------------------------------------------
    num_segments = num_levels - 1
    total_steps_per_segment = 2 * steps_per_flight
    riser_height = floor_height / total_steps_per_segment
    flight_run = steps_per_flight * tread_depth

    ox, oy, oz = origin

    # X positions for the two flights (symmetric about origin.x)
    x1 = ox - (stair_width + landing_gap) / 2.0   # first flight (F1)
    x2 = ox + (stair_width + landing_gap) / 2.0   # second flight (F2)

    # Step box scale (remember craftbot uses a base cube 2x2x2)
    step_scale = (
        stair_width / 2.0,
        tread_depth / 2.0,
        riser_height / 2.0,
    )

    # Landing box scale
    landing_scale = (
        (2.0 * stair_width + landing_gap) / 2.0,
        landing_length / 2.0,
        landing_thickness / 2.0,
    )

    # ------------------------------------------------------------------
    # Floor slabs (trimmed, only on side opposite landing)
    # ------------------------------------------------------------------
    # Floors live on negative Y, stopping just before the stairwell.
    floor_extent_x = 4.0 * stair_width
    floor_extent_y = floor_side_factor * flight_run

    floor_scale = (
        floor_extent_x / 2.0,
        floor_extent_y / 2.0,
        floor_thickness / 2.0,
    )

    # The stairwell boundary on Y is at y0 = oy.
    # Let floor slabs occupy [y_min, y_max] with y_max < y0 (no overlap).
    y_max_floor = oy - floor_clearance
    y_min_floor = y_max_floor - floor_extent_y
    y_floor_center = 0.5 * (y_min_floor + y_max_floor)

    for k in range(num_levels):
        z_floor_center = oz + k * floor_height - floor_thickness / 2.0
        craftbot.place_element(
            name=f"Floor_{k:02d}",
            loc=(ox, y_floor_center, z_floor_center),
            scale=floor_scale,
        )

    # ------------------------------------------------------------------
    # Storey segments: pair of flights + mid-landing
    # ------------------------------------------------------------------
    for seg in range(num_segments):
        z0 = oz + seg * floor_height
        y0 = oy  # reference for this segment in Y

        # --------------------------------------------------------------
        # First flight (F1) – runs in +Y from floor towards landing
        # --------------------------------------------------------------
        for s in range(steps_per_flight):
            cx = x1
            cy = y0 + tread_depth * (s + 0.5)
            cz = z0 + riser_height * (s + 0.5)

            craftbot.place_element(
                name=f"Step_S{seg:02d}_F1_{s:02d}",
                loc=(cx, cy, cz),
                scale=step_scale,
            )

        # --------------------------------------------------------------
        # Mid-landing – centred between flights in X
        # --------------------------------------------------------------
        y_landing_center = y0 + flight_run + landing_length / 2.0
        # Top of landing is level with top of last F1 step
        z_landing_top = z0 + riser_height * steps_per_flight
        z_landing_center = z_landing_top - landing_thickness / 2.0

        craftbot.place_element(
            name=f"Landing_S{seg:02d}",
            loc=(ox, y_landing_center, z_landing_center),
            scale=landing_scale,
        )

        # --------------------------------------------------------------
        # Second flight (F2) – runs back in -Y from the BEGINNING
        # of the landing and shifted one riser DOWN relative to landing.
        #
        #  - Start in Y at the *near* edge of the landing (y_start_f2).
        #  - First tread top is at the same height as landing top
        #    (one riser lower than in the previous version).
        # --------------------------------------------------------------
        y_start_f2 = y0 + flight_run  # beginning of landing (near edge)

        for s in range(steps_per_flight):
            cx = x2
            # Move along -Y starting from the beginning of the landing
            cy = y_start_f2 - tread_depth * (s + 0.5)

            # Shift entire flight down by one riser compared to the
            # original version:
            #   old: z0 + riser_height * (steps_per_flight + s + 0.5)
            #   new: z0 + riser_height * (steps_per_flight + s - 0.5)
            cz = z0 + riser_height * (steps_per_flight + s - 0.5)

            craftbot.place_element(
                name=f"Step_S{seg:02d}_F2_{s:02d}",
                loc=(cx, cy, cz),
                scale=step_scale,
            )


# ------------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_double_flight_stair(
        num_levels=10,
        floor_height=3.0,
        steps_per_flight=10,
        stair_width=1.10,
        tread_depth=0.28,
        landing_length=1.10,
        landing_gap=0.20,
        landing_thickness=0.15,
        floor_thickness=0.20,
        floor_side_factor=3.0,   # length of floor on the side opposite landing
        floor_clearance=0.05,    # small gap so the stair never touches the floor
        origin=(0.0, 0.0, 0.0),
    )
