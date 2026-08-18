# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 10 - CHATGPT 5.1 - V01
# STAIRCASE
# ------------------------------------------------------------------

import bpy
import importlib
import craftbot_lib as craftbot  # assumes craftbot_lib.py is on sys.path

# Handy during development
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
        origin=(0.0, 0.0, 0.0),
):
    """
    Build a multi-storey U-shaped double-flight stair using only scaled cubes.

    num_levels      : total number of floor levels (e.g. 10 levels => 9 segments)
    floor_height    : floor-to-floor height [Blender units]
    steps_per_flight: number of treads per flight
    stair_width     : clear width of each flight
    tread_depth     : depth of each tread
    landing_length  : length of mid-landing in plan (if None, uses stair_width)
    landing_gap     : horizontal gap between flights (in X-direction)
    landing_thickness: vertical thickness of landing slab
    floor_thickness : thickness of floor slabs
    origin          : (x, y, z) base reference of the stair tower
    """

    if landing_length is None:
        landing_length = stair_width

    # Derived parameters
    num_segments = num_levels - 1
    total_steps_per_segment = 2 * steps_per_flight
    riser_height = floor_height / total_steps_per_segment
    flight_run = steps_per_flight * tread_depth

    ox, oy, oz = origin

    # X positions for the two flights
    x1 = ox - (stair_width + landing_gap) / 2.0   # first flight
    x2 = ox + (stair_width + landing_gap) / 2.0   # second flight

    # Convenience dimensions for boxes (remember base cube is 2x2x2)
    step_scale = (
        stair_width / 2.0,
        tread_depth / 2.0,
        riser_height / 2.0,
    )

    landing_scale = (
        (2.0 * stair_width + landing_gap) / 2.0,
        landing_length / 2.0,
        landing_thickness / 2.0,
    )

    # ------------------------------------------------------------------
    # Optional: create floor slabs at all levels
    # ------------------------------------------------------------------
    floor_extent_x = 4.0 * stair_width
    floor_extent_y = 4.0 * flight_run

    floor_scale = (
        floor_extent_x / 2.0,
        floor_extent_y / 2.0,
        floor_thickness / 2.0,
    )

    for k in range(num_levels):
        z_floor_center = oz + k * floor_height - floor_thickness / 2.0
        craftbot.place_element(
            name=f"Floor_{k:02d}",
            loc=(ox, oy, z_floor_center),
            scale=floor_scale,
        )

    # ------------------------------------------------------------------
    # Build each storey segment (pair of flights + mid-landing)
    # ------------------------------------------------------------------
    for seg in range(num_segments):
        z0 = oz + seg * floor_height
        y0 = oy

        # ------------------------
        # First flight (runs +Y)
        # ------------------------
        for s in range(steps_per_flight):
            step_name = f"Step_S{seg:02d}_F1_{s:02d}"

            # Center coordinates of this step
            cx = x1
            cy = y0 + tread_depth * (s + 0.5)
            cz = z0 + riser_height * (s + 0.5)

            craftbot.place_element(
                name=step_name,
                loc=(cx, cy, cz),
                scale=step_scale,
            )

        # ------------------------
        # Mid-landing
        # ------------------------
        y_landing_center = y0 + flight_run + landing_length / 2.0
        # Place landing so its top surface matches top of last step of F1
        z_landing_top = z0 + riser_height * steps_per_flight
        z_landing_center = z_landing_top - landing_thickness / 2.0

        craftbot.place_element(
            name=f"Landing_S{seg:02d}",
            loc=(ox, y_landing_center, z_landing_center),
            scale=landing_scale,
        )

        # ------------------------
        # Second flight (runs -Y, back towards origin)
        # ------------------------
        y_far = y0 + flight_run + landing_length  # far edge of landing

        for s in range(steps_per_flight):
            step_name = f"Step_S{seg:02d}_F2_{s:02d}"

            cx = x2
            cy = y_far - tread_depth * (s + 0.5)
            cz = z0 + riser_height * (steps_per_flight + s + 0.5)

            craftbot.place_element(
                name=step_name,
                loc=(cx, cy, cz),
                scale=step_scale,
            )


# ------------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------------

if __name__ == "__main__":
    # You can tweak these parameters as needed
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
        origin=(0.0, 0.0, 0.0),
    )
