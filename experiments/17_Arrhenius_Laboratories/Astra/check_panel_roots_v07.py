"""All-plane facade attachment paths, including monolithic chamfer fragments."""
from pathlib import Path
from collections import defaultdict,deque
import json,runpy,sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
baseline='--baseline' in sys.argv
identity=runpy.run_path(str(HERE/('snapshot_v05.py' if baseline else 'snapshot_v07.py')))['identity']()
primary=('Column_','Corbel','Beam_','FloorSlab_','PerimeterLedger','GradeBeam','Footing','Pedestal','CoreWall','RoofSlab','InsertSlab','Retaining','TerraceFooting')
if baseline:primary+=('EdgeBeam_',)
secondary=('CourtFacadeBracket_', 'Panel_','Window_','SouthFineStrip_','SouthFascia','SouthVent','SouthBracket','SouthRibbon','SouthSide','SouthIncline')
objects={o.name:o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(primary+secondary) and 'Glass' not in o.name}
faces={};index=defaultdict(list)
def clip(poly,cutter):
    for a,b in zip(cutter,cutter[1:]+cutter[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
for name,obj in objects.items():
    points=[obj.matrix_world@v.co for v in obj.data.vertices];ff=[]
    for f in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@f.normal).normalized()
        ps=[points[i] for i in f.vertices];d=sum(normal.dot(p) for p in ps)/len(ps)
        axis=max(range(3),key=lambda i:abs(normal[i]));dims=[i for i in range(3) if i!=axis]
        poly=[(p[dims[0]],p[dims[1]]) for p in ps]
        if g2.signed_area(poly)<0:poly.reverse()
        key=tuple(round(n,3) for n in normal)
        face=(normal,d,axis,poly);ff.append(face);index[key,round(d,3)].append((name,face))
    faces[name]=ff
cache={}
def contacts(name):
    if name in cache:return cache[name]
    found={}
    for normal,d,axis,poly in faces[name]:
        key=tuple(round(-n,3) for n in normal)
        for shift in (-.001,0,.001):
            for other,(n2,d2,ax2,p2) in index.get((key,round(-d+shift,3)),[]):
                if other==name or ax2!=axis or normal.dot(n2)>-.99999 or abs(d+d2)>2e-5:continue
                common=clip(poly,p2)
                area=g2.area(common)/abs(normal[axis]) if len(common)>2 else 0.
                if area>1e-5:found[other]=found.get(other,0.)+area
    cache[name]=found
    return found
rows=[];fail=[]
for name in sorted(n for n in objects if n.startswith('Panel_')):
    queue=deque([name]);parents={name:None};target=None
    while queue:
        current=queue.popleft()
        if current.startswith(primary):target=current;break
        for other,area in contacts(current).items():
            if other not in parents:parents[other]=(current,area);queue.append(other)
    if target is None:fail.append(name);continue
    route=[]
    while parents[target] is not None:
        previous,area=parents[target];route.append((previous,target,area));target=previous
    rows.append({'panel':name,'path':list(reversed(route))})
report={'identity':identity,'panel_count':sum(n.startswith('Panel_') for n in objects),'rooted':len(rows),'unresolved':fail,'paths':rows,
        'rule':'Actual opposed coplanar faces including sloped fragments,20micrometre plane tolerance; each edge area>10mm2. Glass is excluded from support paths. Timber framing attachment is inferred, not reinforcement or anchor capacity proof.'}
(HERE/('panel_baseline_v05_for_v07.json' if baseline else 'panel_roots_v07.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
detail=[]
for name in ([] if baseline else fail):
    if not name.endswith(('_0','_Base')):continue
    obj=objects[name];ps=[obj.matrix_world@v.co for v in obj.data.vertices]
    bb=tuple(c for i in range(3) for c in (min(p[i] for p in ps),max(p[i] for p in ps)))
    nearest=[]
    for other,o in objects.items():
        if not other.startswith(primary):continue
        qs=[o.matrix_world@v.co for v in o.data.vertices]
        ab=tuple(c for i in range(3) for c in (min(p[i] for p in qs),max(p[i] for p in qs)))
        gap=sum(max(0,bb[2*i]-ab[2*i+1],ab[2*i]-bb[2*i+1])**2 for i in range(3))**.5
        if gap<.5:nearest.append((gap,other,ab))
    detail.append((name,bb,sorted(nearest)[:6]))
if not baseline:(HERE/'panel_root_gaps_v07.txt').write_text(identity+'\n'+repr(detail)+'\n',encoding='utf-8')
print(identity,flush=True);print('Panel roots',len(rows),'unresolved',fail,flush=True)
