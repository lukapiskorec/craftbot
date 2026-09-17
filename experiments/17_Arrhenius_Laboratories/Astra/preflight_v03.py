"""Unrendered build preflight. Uses the kit SAT with an x-sorted broad phase.
The final render repeats the unmodified standard check as independent evidence.
"""
from pathlib import Path
import runpy
import sys
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
model=runpy.run_path(str(HERE/'experiment_17_astra_v03.py'),run_name='__main__')
from check_overlaps import hull,penetration
from check_contacts import _gap
from triage import families,format_families

objects=[o for o in bpy.data.objects if o.type=='MESH']
hulls=sorted([(o.name,hull(o)) for o in objects],key=lambda item:item[1][3].x)
touched=set();hits=[]
for i,(name_a,a) in enumerate(hulls):
    for name_b,b in hulls[i+1:]:
        if b[3].x>a[4].x+.002: break
        if any(a[3][j]>b[4][j]+.002 or b[3][j]>a[4][j]+.002 for j in (1,2)): continue
        if not all(n in touched for n in (name_a,name_b)) and _gap(a,b)<=.002:
            touched.update((name_a,name_b))
        if any(a[3][j]>b[4][j]-.001 or b[3][j]>a[4][j]-.001 for j in range(3)): continue
        depth=penetration(a,b)
        if depth>.001: hits.append((depth,name_a,name_b))
hits.sort(reverse=True)
floating=sorted(n for n,_ in hulls if n not in touched)
summary=f'PREFLIGHT: {len(objects)} members, {len(hits)} pairs, {len(floating)} floating\n'
(HERE/'preflight_v03_pairs.txt').write_text(summary+''.join(f'{p*1000:.3f} mm  {a}  x  {b}\n' for p,a,b in hits))
(HERE/'preflight_v03_summary.txt').write_text(summary+format_families(families(hits),70)+'\nFLOATING\n'+'\n'.join(floating))
print(summary+format_families(families(hits),30)+'\nFLOATING\n'+'\n'.join(floating),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v03.blend'))
runpy.run_path(str(HERE/'check_headroom_v03.py'),run_name='__main__')
