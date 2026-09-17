"""Exact SAT delta check: unchanged29,985 meshes already passed preflight."""
from pathlib import Path
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from check_overlaps import hull,penetration
from check_contacts import _gap
members=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH']
bases=[item for item in members if item[0].startswith('CoreWallBase_')]
hits=[];floating=[]
for name,a in bases:
    touching=False
    for other,b in members:
        if other==name or any(a[3][j]>b[4][j]+.002 or b[3][j]>a[4][j]+.002 for j in range(3)):continue
        touching |= _gap(a,b)<=.002
        if any(a[3][j]>b[4][j]-.001 or b[3][j]>a[4][j]-.001 for j in range(3)):continue
        depth=penetration(a,b)
        if depth>.001:hits.append((name,other,depth))
    if not touching:floating.append(name)
report=f'BASE DELTA: {len(bases)} new convex members versus all{len(members)} meshes; {len(hits)} penetrating pairs; {len(floating)} floating\n'+repr(hits)+'\n'+repr(floating)+'\n'
(HERE/'core_base_pairs_v03.txt').write_text(report,encoding='utf-8');print(report,flush=True)
assert not hits and not floating
