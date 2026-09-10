"""Focused revision: clear glass + neutral fill; compare seams on/off.

Four material palettes, one light, plus white/washed exposed-frame views.
24 renders with matched edge and foundation states. Override settings via CLI.
"""
from views_cycles_study import CYCLES as BASE, FRAME_HIDE

RESOLUTION = (3072, 3072)
CYCLES = dict(BASE, edges="both", edge_width=.006, edge_darkness=.22, fill_strength=.25,
              glass_roughness=.015, glass_transmission=1., glass_ior=1.45)
VIEWS = [dict(name=f"{palette}_main", palette=palette, azim=305, elev=-25,
              sun_rotation=-160, sun_elevation=45, margin=1.16, hide=[])
         for palette in ("white", "muted", "washed", "weathered")]
VIEWS += [dict(name=f"{palette}_frame", palette=palette, azim=225, elev=-30,
               sun_rotation=-160, sun_elevation=45, margin=1.16, hide=FRAME_HIDE)
          for palette in ("white", "washed")]
