"""Actual face unions for the newly added support system; no capacity claim."""
from pathlib import Path
import json
import runpy
import sys
from collections import deque
import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]/'tools'))
import geometry2d as g2
audit = runpy.run_path(str(HERE / 'structural_followup_v06.py'))
faces, bounds, index = (audit[k] for k in ('faces', 'bounds', 'index'))
area, coverage, intersect, contacts = (audit[k] for k in ('area', 'coverage', 'intersect', 'contacts'))
lines = [runpy.run_path(str(HERE / 'snapshot_v06.py'))['identity']()]
failures = []

def assert_case(label, ok, detail):
    lines.append(f'{label}: PASS{ok}; {detail}')
    if not ok:
        failures.append(label)

# The local50mm support extensions are integral roots, not free bearing pads.
for name in sorted(n for n in faces if n.startswith('CorbelNib_')):
    joints=contacts(name,lambda n:n.startswith('CorbelWing_'),axes=(1,))
    root_area=sum(a for n,axis,sign,plane,a,p in joints)
    assert_case(name+' 200mm-deep integral wing root',abs(root_area-.07)<1e-5,
                f'actual positive-area root {root_area:.9f}m2; required .35x.20=.070m2')

def support_union(poly, z, prefixes):
    candidates = [(name, f[3]) for name, f in index.get((2, 1, round(z, 4)), [])
                  if name.startswith(prefixes) and abs(z-f[2]) < 2e-5
                  and area(intersect(poly, f[3])) > 1e-9]
    return coverage(poly, [p for _, p in candidates]), sorted(set(n for n, _ in candidates))

# A face's uncovered area is checked with an explicit float32 seam allowance:
# 20 micrometres times perimeter. This accommodates retained translated boxes,
# not millimetre gaps, and the report preserves raw areas.
def seam_allowance(poly):
    return 2e-5 * sum(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
                     for a, b in zip(poly, poly[1:]+poly[:1]))

for name in sorted(n for n in faces if n.startswith('CourtStair_') or n == 'CourtStairTopLanding'):
    for axis, sign, z, poly, _ in faces[name]:
        if axis != 2 or sign != -1:
            continue
        seated, supports = support_union(poly, z, ('CourtWaist', 'CourtLandingSupport'))
        assert_case(name+' full underside', area(poly)-seated <= seam_allowance(poly),
                    f'required {area(poly):.9f}m2; seated {seated:.9f}m2; {supports}')

for label, rect, z, minimum, prefixes in (
    ('Waist bottom seat', (33.,35.45,89.70,89.90), -.35, .49, ('CourtStairFooting',)),
    ('Landing lower ledge seat', (33.15,35.35,95.80,96.00), 2.50, .44, ('CourtLandingLedge',)),
    ('Landing raised corbel seat', (35.35,35.45,95.50,96.00), 2.70, .05, ('CorbelWing_76_1_-1',))):
    poly = g2.rect(*rect)
    seated, supports = support_union(poly, z, prefixes)
    upper=coverage(poly,[f[3] for n,f in index.get((2,-1,round(z,4)),[])
                        if n.startswith('CourtLandingSupport') and abs(f[2]-z)<2e-5]) if label.startswith('Landing') else minimum
    assert_case(label, minimum-seated <= seam_allowance(poly),
                f'required {minimum:.9f}m2; seated {seated:.9f}m2; actual supported plate underside {upper:.9f}m2; {supports}')
    assert_case(label+' receiving plate face',minimum-upper<=seam_allowance(poly),f'actual area {upper:.9f}m2')

# Section every constant-Y interval of the sidewall/primary-concrete union.
# This detects missing wall above/below chamfered shoulders that contact or
# footprint-seat checks cannot see. Both boundaries and midpoints are checked.
def convex_hull(points):
    points=sorted(set(points));result=[]
    for seq in (points,points[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and (half[-1][0]-half[-2][0])*(p[1]-half[-2][1])-(half[-1][1]-half[-2][1])*(p[0]-half[-2][0])<=1e-12:half.pop()
            half.append(p)
        result.extend(half[:-1])
    return result

for label,xa,xb in [('W',18.55,18.85),('E',35.15,35.45)]:
    wall_objects=[];cuts={96.30,107.20}
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not obj.name.startswith(('TerraceWall','Corbel','Column_','InsertColumn','InsertBeam','RetainingWall','Beam_')):continue
        b=bounds[obj.name]
        if b[1]<xa-2e-5 or b[0]>xb+2e-5 or b[3]<96.30 or b[2]>107.20 or b[5]<0 or b[4]>2.75:continue
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        wall_objects.append((obj,points))
        cuts.update(round(p.y,5) for p in points if 96.30<p.y<107.20)
    cuts=sorted(cuts)
    samples=sorted(set(cuts+[(a+b)/2 for a,b in zip(cuts,cuts[1:]) if b-a>2e-5]))
    required=g2.rect(xa,xb,0.,2.75);worst=0.;bad=[]
    for y in samples:
        sections=[]
        for obj,points in wall_objects:
            hits=[(p.x,p.z) for p in points if abs(p.y-y)<2e-5]
            for edge in obj.data.edges:
                a,b=(points[i] for i in edge.vertices)
                if min(a.y,b.y)<=y<=max(a.y,b.y) and abs(b.y-a.y)>1e-8:
                    t=(y-a.y)/(b.y-a.y);hits.append((a.x+t*(b.x-a.x),a.z+t*(b.z-a.z)))
            poly=convex_hull(hits)
            if len(poly)>=3:sections.append(poly)
        missing=area(required)-coverage(required,sections);worst=max(worst,missing)
        if missing>seam_allowance(required):bad.append((y,missing))
    assert_case('Terrace '+label+' complete wall/concrete union',not bad,
                f'{len(samples)} Y boundaries/midpoints; maximum uncovered XZ area {worst:.9f}m2; failures {bad}')

terrace_required = terrace_seated = cantilever = 0.
for name in sorted(n for n in faces if n.startswith('NorthTerrace')):
    for axis, sign, z, poly, _ in faces[name]:
        if axis != 2 or sign != -1:
            continue
        supported = g2.clip_rect(poly, -100., 100., 0., 107.20)
        strip = g2.clip_rect(poly, -100., 100., 107.20, 108.)
        seated, supports = support_union(supported, z, ('Terrace', 'InsertColumn', 'InsertBeam', 'Retaining'))
        terrace_required += area(supported)
        terrace_seated += seated
        cantilever += area(strip)
        assert_case(name+' concrete seats / omitted earth boundary', seated>=0.,
                    f'required {area(supported):.9f}m2; seated {seated:.9f}m2; '
                    f'unmodeled earth underside {area(supported)-seated:.9f}m2; explicit north cantilever {area(strip):.9f}m2; {supports}')
assert_case('Terrace concrete/earth boundary total', terrace_seated>0 and abs(cantilever-.507)<.001,
            f'support-required {terrace_required:.9f}m2; seated {terrace_seated:.9f}m2; '
            f'unmodeled earth-bearing {terrace_required-terrace_seated:.9f}m2; 30mm north cantilever {cantilever:.9f}m2; nominal cantilever .507m2')

old_ends = json.loads((HERE/'slab_end_faces_v04.json').read_text())
new_ends = json.loads((HERE/'slab_end_faces_v06.json').read_text())
assert_case('4534 ordinary slab ends', len(new_ends)==4534 and all(r['passed'] for r in new_ends),
            f'{len(new_ends)} cases; {sum(not r["passed"] for r in new_ends)} failures')
former_fails = [r for r in old_ends if not r['passed']]
assert len(former_fails) == 261
for row in former_fails:
    name, side = row['name'], row['side']
    x0,x1,y0,y1,_,_ = bounds[name]
    z = 3.6*int(name.split('_')[1])-.25
    poly = g2.rect(x0,x1,y0,y0+.20) if side<0 else g2.rect(x0,x1,y1-.20,y1)
    seated, supports = support_union(poly,z,('PerimeterLedger','Beam_','Column_'))
    assert_case(name+f' end{side} 200mm', area(poly)-seated <= seam_allowance(poly),
                f'required {area(poly):.9f}m2; seated {seated:.9f}m2; {supports}')

ledger_graph={}
for name in sorted(n for n in faces if n.startswith(('PerimeterLedger','CourtLandingLedge'))):
    prefixes = ('Beam_', 'Column_') if name.startswith('PerimeterLedger') else ('RetainingWall',)
    joints = [c for c in contacts(name,lambda n:n.startswith(prefixes+('PerimeterLedger',)),axes=(0,1))]
    ledger_graph[name]=[n for n,axis,sign,plane,a,p in joints if a>1e-6]
    lines.append(name+' actual concrete interfaces: '+repr([(n,axis,round(a,8)) for n,axis,sign,plane,a,p in joints]))
for start in sorted(ledger_graph):
    queue=deque([start]);parent={start:None};target=None
    while queue:
        name=queue.popleft()
        if name.startswith(('Beam_','Column_','RetainingWall')):
            target=name;break
        for other in ledger_graph.get(name,[]):
            if other not in parent:parent[other]=name;queue.append(other)
    path=[]
    while target is not None:path.append(target);target=parent[target]
    assert_case(start+' integral root path',bool(path),' -> '.join(reversed(path)))

waists = sorted(n for n in faces if n.startswith('CourtWaist'))
waist_graph={}
for name in waists:
    joints = contacts(name,lambda n:n.startswith(('CourtWaist','CourtLandingSupport','CourtStairFooting')), axes=(1,2))
    waist_graph[name]={n for n,axis,sign,plane,a,p in joints if a>.01}
    assert_case(name+' positive-area waist chain', bool(joints),
                repr([(n,axis,round(a,8)) for n,axis,sign,plane,a,p in joints]))
for name in sorted(n for n in faces if n.startswith(('CourtLandingSupport','CourtLandingLedge','CourtStairFooting'))):
    joints=contacts(name,lambda n:n.startswith(('CourtWaist','CourtLandingSupport','CourtLandingLedge','CourtStairFooting','RetainingWall')),axes=(1,2))
    waist_graph[name]={n for n,axis,sign,plane,a,p in joints if a>.01}
for target_prefix in ('CourtStairFooting','RetainingWall'):
    for start in waists:
        queue=deque([start]);seen={start};found=None
        while queue:
            name=queue.popleft()
            if name.startswith(target_prefix):found=name;break
            for other in waist_graph.get(name,set()):
                if other not in seen:seen.add(other);queue.append(other)
        assert_case(start+' chain to '+target_prefix,found is not None,
                    f'positive-area joints >0.01m2; endpoint {found}')

for name in sorted(n for n in faces if n.startswith('TerraceWall')):
    for axis,sign,z,poly,_ in faces[name]:
        if axis!=2 or sign!=-1:
            continue
        seated,supports=support_union(poly,z,('Terrace','Insert','Retaining','Footing','GradeBeam','Pedestal','Corbel','Column_'))
        assert_case(name+' real concrete support union',area(poly)-seated<=seam_allowance(poly),
                    f'required {area(poly):.9f}m2; seated {seated:.9f}m2; {supports}')

north_walls=[b for n,b in bounds.items() if n.startswith('TerraceWall_N')]
gap=107.23-max(b[3] for b in north_walls)
assert_case('North soil/concrete clear of glazing',gap>=.03-2e-5,f'actual wall-to-glazing nominal datum gap {gap:.9f}m')
manifest={'closure_changes':json.loads(bpy.context.scene.get('closure_changes_v06','[]'))}
for change in manifest['closure_changes']:
    name=change['name'];old=change['before']
    pieces=[n for n in bounds if n==name or n.startswith(name+'_LedgerFit')]
    old_volume=(old[1]-old[0])*(old[3]-old[2])*(old[5]-old[4])
    remaining=sum((bounds[n][1]-bounds[n][0])*(bounds[n][3]-bounds[n][2])*(bounds[n][5]-bounds[n][4]) for n in pieces)
    assert_case(name+' minimal buried trim',abs(old_volume-remaining-change['removed_volume_m3'])<1e-6,
                f'old {old_volume:.9f}m3; remaining {remaining:.9f}m3; removed {change["removed_volume_m3"]:.9f}m3')
    for xa,xb,ya,yb,za,zb in change['removed_bounds']:
        poly=g2.rect(xa,xb,ya,yb)
        seats=[f[3] for n,f in index.get((2,1,round(zb,4)),[]) if n.startswith('PerimeterLedger') and bounds[n][4]<=za+2e-5]
        covered=coverage(poly,seats)
        assert_case(name+' removed volume filled by concrete',area(poly)-covered<1e-6,
                    f'required {area(poly):.9f}m2 through depth {zb-za:.9f}m; concrete {covered:.9f}m2')
    joints=[c for n in pieces for c in contacts(n,lambda n:n.startswith('PerimeterLedger'))]
    assert_case(name+' closure/concrete continuity',bool(joints),
                repr([(n,axis,round(a,8)) for n,axis,sign,plane,a,p in joints]))
lines.append('Joint reinforcement, anchors, soil, retaining stability and member capacities remain uncalculated architectural inference.')
lines.append(f'FAILURES {len(failures)}: {failures}')
(HERE/'completion_v06.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines),flush=True)
assert not failures, failures
