# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 10 - CHATGPT 5.1 - V03
# STAIRCASE
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # make sure craftbot_lib.py is on sys.path

# Helpful during development
importlib.reload(craftbot)


def build_double_flight_stair(
        num_levels=10,
        floor_height=3.0,
        steps_per_flight=10,      # logical risers per flight
        stair_width=1.10,
        tread_depth=0.28,
        landing_length=None,
        landing_gap=0.20,
        landing_thickness=0.15,
        floor_thickness=0.20,
        floor_side_factor=3.0,
        floor_clearance=0.0,      # 0 => no Y-gap between floor and stair
        origin=(0.0, 0.0, 0.0),
):
    """
    Build a multi-storey U-shaped double-flight stair using only scaled cubes.

    Axes
    ----
    - Z: vertical (up).
    - First flight (F1) runs in +Y from floor to landing.
    - Second flight (F2) runs back in -Y from landing to the next floor.
    - Landings span in X between the two flights.

    Notes
    -----
    - 'steps_per_flight' defines the logical number of risers per flight.
      Geometrically we show one tread less per flight:
        * F1: we draw steps F1_00 .. F1_08 (F1_09 omitted).
        * F2: we draw steps F2_01 .. F2_09 (F2_00 omitted).
      The missing risers are taken up as the vertical step between the
      last tread and the landing / floor, which is what you typically want.
    """

    if landing_length is None:
        landing_length = stair_width

    # ------------------------------------------------------------------
    # Derived stair parameters
    # ------------------------------------------------------------------
    visible_steps_per_flight = steps_per_flight - 1   # we omit one tread per flight
    num_segments = num_levels - 1

    # Riser height based on full logical count (unchanged)
    total_steps_per_segment = 2 * steps_per_flight
    riser_height = floor_height / total_steps_per_segment

    # Horizontal runs
    flight_run_visible = visible_steps_per_flight * tread_depth
    flight_run_logical = steps_per_flight * tread_depth  # if needed elsewhere

    ox, oy, oz = origin

    # X positions for the two flights (symmetric about origin.x)
    x1 = ox - (stair_width + landing_gap) / 2.0   # first flight (F1)
    x2 = ox + (stair_width + landing_gap) / 2.0   # second flight (F2)

    # Step box scale (base cube is 2x2x2)
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
    # Floor slabs (trimmed, only on side opposite landing; no Y-gap)
    # ------------------------------------------------------------------
    floor_extent_x = 4.0 * stair_width
    floor_extent_y = floor_side_factor * flight_run_visible

    floor_scale = (
        floor_extent_x / 2.0,
        floor_extent_y / 2.0,
        floor_thickness / 2.0,
    )

    # Floors live on negative Y and end at y = oy - floor_clearance.
    y_max_floor = oy - floor_clearance        # edge right at stair start when clearance = 0
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
    # Storey segments: F1 + landing + F2
    # ------------------------------------------------------------------
    for seg in range(num_segments):
        z0 = oz + seg * floor_height
        y0 = oy  # reference Y for this segment

        # --------------------------------------------------------------
        # First flight (F1) – runs +Y
        # We draw only 0 .. visible_steps_per_flight-1 (omit F1_09)
        # --------------------------------------------------------------
        for s in range(visible_steps_per_flight):
            cx = x1
            cy = y0 + tread_depth * (s + 0.5)
            cz = z0 + riser_height * (s + 0.5)

            craftbot.place_element(
                name=f"Step_S{seg:02d}_F1_{s:02d}",
                loc=(cx, cy, cz),
                scale=step_scale,
            )

        # --------------------------------------------------------------
        # Mid-landing
        #   - Near edge of landing starts at the nose of F1_08,
        #     i.e. at y = y0 + flight_run_visible.
        # --------------------------------------------------------------
        y_near_landing = y0 + flight_run_visible
        y_landing_center = y_near_landing + landing_length / 2.0

        # Top of landing is still at mid-height = riser_height * steps_per_flight
        z_landing_top = z0 + riser_height * steps_per_flight
        z_landing_center = z_landing_top - landing_thickness / 2.0

        craftbot.place_element(
            name=f"Landing_S{seg:02d}",
            loc=(ox, y_landing_center, z_landing_center),
            scale=landing_scale,
        )

        # --------------------------------------------------------------
        # Second flight (F2) – runs -Y
        #
        # We omit F2_00 and generate treads F2_01 .. F2_09:
        #   k = 0 .. visible_steps_per_flight-1  -> step index = k+1
        #   - In plan: bottom tread nose at y_near_landing,
        #     then stepping back in -Y.
        #   - In height: we keep the original pattern; we simply
        #     skip the geometry that used to be F2_00.
        # --------------------------------------------------------------
        for k in range(visible_steps_per_flight):
            step_index = k + 1  # for naming: F2_01 .. F2_09

            cx = x2
            # Plan position: nose at y_near_landing - k*d, center = nose - d/2
            cy = y_near_landing - tread_depth * (k + 0.5)

            # Vertical position:
            #   original F2 formula was:
            #       cz = z0 + h * (steps_per_flight + s - 0.5)
            #   for s = 0..9 (F2_00..F2_09).
            #   Here we skip s = 0, so s = k+1:
            cz = z0 + riser_height * (steps_per_flight + k + 0.5)

            craftbot.place_element(
                name=f"Step_S{seg:02d}_F2_{step_index:02d}",
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
        floor_side_factor=3.0,
        floor_clearance=0.0,   # no Y-gap between stair and floor plates
        origin=(0.0, 0.0, 0.0),
    )
