"""Build append-only support completion on the frozen v04 baseline."""
from pathlib import Path
import hashlib
import json
import runpy
import sys
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
before=runpy.run_path(str(HERE/'snapshot_v04.py'))['identity']()
assert '8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657' in before,before

def signatures():
    return {o.name:hashlib.sha256(repr([tuple(p) for v in o.data.vertices for p in [o.matrix_world@v.co]]).encode()).hexdigest()
            for o in bpy.data.objects if o.type=='MESH'}

prior=signatures()
completion=runpy.run_path(str(HERE/'support_geometry_v05.py'),run_name='__main__')
current=signatures()
changed=[n for n,s in prior.items() if current.get(n)!=s]
closures=completion['CLOSURE_CHANGES']
assert sorted(changed)==sorted(c['name'] for c in closures),changed
assert len(changed)==6,changed
new=sorted(current.keys()-prior.keys())
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v05.blend'))
identity=runpy.run_path(str(HERE/'snapshot_v05.py'))['identity']()
(HERE/'retained_v05.json').write_text(json.dumps({'baseline':before,'geometry':identity,'baseline_members':len(prior),'retained':len(prior)-len(changed),'changed':changed,'closure_changes':closures,'added':new},indent=2),encoding='utf-8')
print(identity,flush=True)
print(f'Retained {len(prior)-len(changed)} exact member signatures; changed {len(changed)} buried closure pieces; added {len(new)}',flush=True)

# Local preflight compares each NEW member to all candidates using the kit's
# exact SAT. The final standard whole-model check remains a separate one-time
# frozen-geometry gate; this bounded development check does not replace it.
from check_overlaps import hull,penetration
from triage import families,format_families
all_hulls=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH']
new_names=set(new+changed);hits=[]
for name,a in all_hulls:
    if name not in new_names:continue
    for other,b in all_hulls:
        if other==name or (other in new_names and other<name):continue
        if any(min(a[4][k],b[4][k])-max(a[3][k],b[3][k])<.001 for k in range(3)):continue
        depth=penetration(a,b)
        if depth>.001:hits.append((depth,name,other))
text=identity+'\nNEW-MEMBER SAT: '+str(len(hits))+' penetrating pairs\n'+format_families(families(hits),100)
(HERE/'support_preflight_v05.txt').write_text(text+'\n'+'\n'.join(map(str,hits)),encoding='utf-8')
print(text,flush=True)
