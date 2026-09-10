"""Final edge-light response comparison: washed timber, crosslight, no foundation."""
from views_cycles_study import CYCLES as BASE, FRAME_HIDE

RESOLUTION = (3072, 3072)
CYCLES = dict(BASE, edges="bevel", foundation="hide", edge_width=.010,
              edge_darkness=.22, fill_strength=.25,
              glass_roughness=.015, glass_transmission=1., glass_ior=1.45)
VIEWS = []
for label, response in (("lit", 1.), ("reduced", .30), ("unlit", 0.)):
    VIEWS.append(dict(name=f"washed_clad_{label}", palette="washed", azim=305, elev=-25,
                      sun_rotation=-160, sun_elevation=45, margin=1.16, hide=[],
                      edge_light_response=response))
    VIEWS.append(dict(name=f"washed_frame_{label}", palette="washed", azim=225, elev=-30,
                      sun_rotation=-160, sun_elevation=45, margin=1.16, hide=FRAME_HIDE,
                      edge_light_response=response))
