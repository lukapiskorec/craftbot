"""Close-up diagnostic of actual 25 mm tower cladding boards."""
from views_cycles_study import CYCLES as BASE

RESOLUTION = (1024, 1024)
CYCLES = dict(BASE, samples=64, edges="bevel", foundation="hide",
              edge_darkness=.22, fill_strength=.25,
              glass_roughness=.015, glass_transmission=1., glass_ior=1.45)
COMMON = dict(palette="washed", azim=270, elev=0, sun_rotation=-160,
              sun_elevation=45, hide=[], focus=(Vector((4.8, 0.13, 8.0)), 1.2))
VIEWS = [
    dict(COMMON, name="width_003_unlit", edge_width=.003, edge_light_response=0),
    dict(COMMON, name="width_006_unlit", edge_width=.006, edge_light_response=0),
    dict(COMMON, name="width_010_unlit", edge_width=.010, edge_light_response=0),
    dict(COMMON, name="width_006_reduced", edge_width=.006, edge_light_response=.30),
    dict(COMMON, name="width_006_lit", edge_width=.006, edge_light_response=1),
]
