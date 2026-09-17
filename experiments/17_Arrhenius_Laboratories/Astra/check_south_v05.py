"""Actual mesh enclosure offset, retained frame and bracket face checks."""
from pathlib import Path
import hashlib
import runpy
import bpy
HERE=Path(__file__).resolve().parent
def vertices(obj):return [obj.matrix_world@v.co for v in obj.data.vertices]
def bounds(obj):
    p=vertices(obj)
    return tuple(value for a in range(3) for value in (min(v[a] for v in p),max(v[a] for v in p)))
def signatures():
    prefixes=('Column_','Corbel','Beam_','EdgeBeam','FloorSlab','CoreWall','CoreFoundation','Footing','Pedestal','Stair','InsertLink','InsertSlab')
    return {o.name:hashlib.sha256(repr([tuple(round(c,6) for c in p) for p in vertices(o)]).encode()).hexdigest() for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)}
frozen=bpy.data.filepath
current=signatures()
bpy.ops.wm.open_mainfile(filepath=str(HERE/'preflight_v04.blend'))
prior=signatures()
differences=sorted(n for n in prior.keys()|current.keys() if prior.get(n)!=current.get(n))
bpy.ops.wm.open_mainfile(filepath=frozen)
rows=[runpy.run_path(str(HERE/'snapshot_v05.py'))['identity'](),f'Retained frame/floor/stair/insert signatures: {len(current)} current / {len(prior)} v04; changed {differences}']
objects=[o for o in bpy.data.objects if o.type=='MESH']
bb={o.name:bounds(o) for o in objects}
def contact(name,prefixes,axis,face):
    a=bb[name];otheraxes=[i for i in range(3) if i!=axis];area=0.;contacts=[]
    for n,b in bb.items():
        if n==name or not n.startswith(prefixes):continue
        if abs(a[axis*2+face]-b[axis*2+1-face])>2e-5:continue
        sides=[max(0.,min(a[2*i+1],b[2*i+1])-max(a[2*i],b[2*i])) for i in otheraxes]
        if min(sides)>1e-6:area+=sides[0]*sides[1];contacts.append(n)
    return area,contacts
failed=[]
for name in sorted(n for n in bb if n.startswith('SouthSupportBracket')):
    rail=contact(name,('SouthSupportPost','SouthSupportRail'),1,0)
    concrete=contact(name,('Column_','Beam_'),1,1)
    ok=rail[0]>=.00599 and concrete[0]>=.00999
    rows.append(f'{name}: rail face {rail}; concrete face {concrete}; PASS{ok}')
    if not ok:failed.append(name)
backings=[b for n,b in bb.items() if n.startswith('SouthFasciaBacking')]
assert len(backings)==1,backings
expected=(.55,53.45,-1.,-.78,12.6,18.)
assert max(abs(a-b) for a,b in zip(backings[0],expected))<2e-5
rail_back=max(b[3] for n,b in bb.items() if n.startswith('SouthSupportPost'))
corbel_front=min(b[2] for n,b in bb.items() if n.startswith('CorbelWing') and b[2]<0 and b[5]>9.6)
rows.append(f'Actual rail/corbel clearance {corbel_front-rail_back:.8f}m; minimum0.030m (float32 tolerance20micrometres).')
rows.append(f'Bracket failures {failed}; retained member changes {differences}')
(HERE/'south_v05.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows),flush=True)
assert not failed and not differences
assert corbel_front-rail_back>=.03-2e-5
