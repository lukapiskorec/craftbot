"""Actual frozen-mesh rim/frame contacts; does not assess joint capacity."""
from pathlib import Path
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from check_overlaps import hull
from check_contacts import _gap
rims=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('StairRim_')]
beams=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Beam_','EdgeBeam','StairHeader'))]
groups={}
for name,a in rims:
    key='_'.join(name.split('_')[:3])
    contacts=groups.setdefault(key,set())
    for other,b in beams:
        if any(a[3][i]>b[4][i]+.002 or b[3][i]>a[4][i]+.002 for i in range(3)): continue
        if _gap(a,b)<=.002: contacts.add(other)
report='FROZEN v03 RIM/FRAME CONTACTS; standard SAT gap<=2mm; not bearing-area/capacity verification\n'
for key,names in sorted(groups.items()): report+=f'{key}: {len(names)} beam/header members: '+', '.join(sorted(names))+'\n'
report+=f'Rim levels without any beam/header contact: {sum(not names for names in groups.values())}\n'
(HERE/'rim_contacts_v03.txt').write_text(report,encoding='utf-8')
print(report,flush=True)
