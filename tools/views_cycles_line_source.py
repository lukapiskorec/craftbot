"""Matched Cycles sources for the Workbench line-overlay study."""
from views_cycles_study import CYCLES as BASE, FRAME_HIDE

RESOLUTION = (3072, 3072)
CYCLES = dict(BASE, edges="none", foundation="hide", fill_strength=.25,
              glass_roughness=.015, glass_transmission=1., glass_ior=1.45)
VIEWS = [
    dict(name="clad", palette="washed", azim=305, elev=-25, sun_rotation=-160,
         sun_elevation=45, margin=1.16, hide=[]),
    dict(name="frame", palette="washed", azim=225, elev=-30, sun_rotation=-160,
         sun_elevation=45, margin=1.16, hide=FRAME_HIDE),
]
