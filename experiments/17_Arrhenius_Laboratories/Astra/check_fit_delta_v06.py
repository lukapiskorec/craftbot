"""Measure the approved9.7 repair against first v06 build before any render."""
from pathlib import Path
import hashlib
import json
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from check_overlaps import hull,penetration
from triage import families,format_families
PREFIXES=('CourtLandingSupport','CourtLandingLedge','TerraceWall')
def signature(obj):
    return hashlib.sha256(repr([tuple(round(c,6) for c in obj.matrix_world@v.co) for v in obj.data.vertices]).encode()).hexdigest()
def volume(obj):
    ps=[obj.matrix_world@v.co for v in obj.data.vertices];total=0.
    for face in obj.data.polygons:
        a=ps[face.vertices[0]]
        for i in range(1,len(face.vertices)-1):total+=a.dot(ps[face.vertices[i]].cross(ps[face.vertices[i+1]]))/6
    return abs(total)
frozen=bpy.data.filepath
current={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
current_volumes={p:sum(volume(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(p)) for p in PREFIXES}
bpy.ops.wm.open_mainfile(filepath=str(HERE/'preflight_v06.blend1'))
baseline=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
assert '448544c4a053d93cf4d5fb853cf10661e274adea4dd2549fd5ca661521e54e45' in baseline,baseline
prior={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
prior_volumes={p:sum(volume(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(p)) for p in PREFIXES}
bpy.ops.wm.open_mainfile(filepath=frozen)
changed=[n for n in prior.keys()|current.keys() if prior.get(n)!=current.get(n)]
assert all(n.startswith(PREFIXES) for n in changed),[n for n in changed if not n.startswith(PREFIXES)]
new_names={n for n in changed if n in current}
all_hulls=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH']
hits=[]
for name,a in all_hulls:
    if name not in new_names:continue
    for other,b in all_hulls:
        if other==name or (other in new_names and other<name):continue
        if any(min(a[4][k],b[4][k])-max(a[3][k],b[3][k])<.001 for k in range(3)):continue
        depth=penetration(a,b)
        if depth>.001:hits.append((depth,name,other))
report={'baseline':baseline,'current':runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),
        'changed_names':changed,'restored_volumes':{p:current_volumes[p]-prior_volumes[p] for p in PREFIXES},
        'prior_volumes':prior_volumes,'current_volumes':current_volumes,'local_pairs':hits}
(HERE/'fit_delta_v06.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['current'],flush=True)
print('Concept9.7 restored concrete volumes:',report['restored_volumes'],flush=True)
print(format_families(families(hits),30),flush=True)
assert not hits,hits
