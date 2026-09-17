"""Read-only face bounds for Designer's next-version decision."""
from pathlib import Path
from collections import defaultdict
import bpy

groups = defaultdict(list)
for obj in bpy.data.objects:
    if obj.type != 'MESH': continue
    coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
    bounds = tuple(value for k in range(3) for value in (min(v[k] for v in coords), max(v[k] for v in coords)))
    x0,x1,y0,y1,z0,z1 = bounds
    if z1 < 9.6 or y0 > 1.1: continue
    family = None
    for prefix in ('SouthFasciaBacking','SouthFasciaSeam','SouthFasciaLip','SouthRibbon','SouthVent','Column_','CorbelWing_','CorbelSeat_','Beam_','EdgeBeam_','FloorSlab_'):
        if obj.name.startswith(prefix): family = prefix; break
    if family: groups[family].append((obj.name,bounds))
lines = ['Frozen v03 actual mesh bounds; metres. Min/max unions are not solid-volume claims.']
for family, rows in sorted(groups.items()):
    combined = tuple((min if k%2==0 else max)(bounds[k] for _,bounds in rows) for k in range(6))
    lines.append(f'{family}: {len(rows)} pieces; x/y/z bounds {combined}')
    if family in ('SouthRibbon','SouthFasciaBacking','SouthFasciaLip','Column_','CorbelWing_','CorbelSeat_','Beam_','EdgeBeam_'):
        lines.extend(f'  {name}: {bounds}' for name,bounds in rows[:8])
Path(__file__).with_suffix('.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
