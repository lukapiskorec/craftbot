"""Derive isolated v04 sources from immutable v03; run once before renders."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
if (HERE/'experiment_17_astra_v04.py').exists():
    raise RuntimeError('v04 already exists; this initial derivation helper must not overwrite a version.')
source=(HERE/'experiment_17_astra_v03.py').read_text(encoding='utf-8').replace('v03','v04')
source=source.replace("B('SouthFasciaBacking','Facade/SouthMetal',.55,53.45,.53,.75,12.6,18.)", "B('SouthFasciaBacking','Facade/SouthMetal',.55,53.45,-1.00,-.78,12.6,18.)")
source=source.replace(".50,.53,12.6,18.)", "-1.03,-1.00,12.6,18.)")
source=source.replace(".33,.75,12.5,12.6)", "-1.20,-.78,12.5,12.6)")
source=source.replace("    window(f'SouthRibbon_{i}','x',a,b,.75,9.6,12.5,False)\n",'')
anchor="B('SouthVentBacking','Facade/SouthMetal',.55,53.45,.75,.97,8.45,9.6)"
addition='''# v04 concept3.2: secondary steel posts form the ribbon divisions, without
# duplicate timber jambs in the same depth. Actual glass centre is y=-.72.
south_divisions=[.55]+[float(x) for x in range(3,52,3)]+[53.45]
for i,x in enumerate(south_divisions):
    xa,xb=(x,x+.06) if i==0 else ((x-.06,x) if i==len(south_divisions)-1 else (x-.03,x+.03))
    B(f'SouthSupportPost_{i}','Facade/SteelFrames',xa,xb,-.78,-.68,9.6,18.)
    for j,z in enumerate((10.,13.6,17.2)):
        end=-.30 if i not in (0,len(south_divisions)-1) and abs(x/9-round(x/9))<1e-6 else -.20
        B(f'SouthSupportBracket_{i}_{j}','Facade/SteelFrames',xa,xb,-.68,end,z,z+.10)
for j,z in enumerate((10.,13.6,17.2)):
    B(f'SouthSupportRail_{j}','Facade/SteelFrames',.55,53.45,-.78,-.68,z,z+.10)
for i,(a,b) in enumerate(zip(south_divisions,south_divisions[1:])):
    lo=a+(.06 if i==0 else .03);hi=b-(.06 if i==len(south_divisions)-2 else .03)
    B(f'SouthRibbon_{i}_Sill','Facade/TimberFrames',lo,hi,-.78,-.68,9.6,9.665)
    B(f'SouthRibbon_{i}_Head','Facade/TimberFrames',lo,hi,-.78,-.68,12.435,12.5)
    B(f'SouthRibbon_{i}_Glass','Facade/Glass',lo,hi,-.729,-.711,9.665,12.435)
# Thirty-millimetre weather returns; fitted to retained concrete by the
# same convex construction-precedence pass as all other enclosure pieces.
for name,rect in [('Top',(.55,53.45,-.78,.77,17.97,18.)),
                  ('Head',(.55,53.45,-.78,.75,12.50,12.53)),
                  ('Sill',(.55,53.45,-.78,.97,9.57,9.60)),
                  ('West',(.55,.58,-.78,.77,9.60,17.97)),
                  ('East',(53.42,53.45,-.78,.77,9.60,17.97))]:
    B('SouthClosure_'+name,'Facade/SouthMetal',*rect)
assert abs(-.68-(-.65))>=.03-1e-8
'''
source=source.replace(anchor,addition+'\n'+anchor)
source=source.replace("    if name.startswith(('FloorSlab'", "    if name.startswith('SouthSupport'): return 3.6\n    if name.startswith('SouthClosure'): return 4.1\n    if name.startswith(('FloorSlab'")
(HERE/'experiment_17_astra_v04.py').write_text(source,encoding='utf-8')
for name in ('preflight','snapshot','check_routes','verify_route_envelopes','check_headroom','check_supports','check_rims','verify_reproduction','draw_plans','rasterize_plans'):
    old=HERE/f'{name}_v03.py'
    (HERE/f'{name}_v04.py').write_text(old.read_text(encoding='utf-8').replace('v03','v04'),encoding='utf-8')
