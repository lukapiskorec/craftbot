"""Actual horizontal seats and named structural contacts, without capacity claims."""
from pathlib import Path
from collections import deque
import sys
import runpy
import bpy
HERE=Path(__file__).resolve().parent
SNAPSHOT=runpy.run_path(str(HERE/'snapshot_v04.py'))['identity']()
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from check_overlaps import hull
from check_contacts import _gap
from check_bearing import check_bearing
import geometry2d as g2

def intersect(poly,clip):
    for a,b in zip(clip,clip[1:]+clip[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
def subtract(poly,clip):
    out=[];remaining=poly
    for a,b in zip(clip,clip[1:]+clip[:1]):
        n=(a[1]-b[1],b[0]-a[0]);piece=g2.clip(remaining,a,(-n[0],-n[1]))
        if len(piece)>=3 and g2.area(piece)>1e-9:out.append(piece)
        remaining=g2.clip(remaining,a,n)
        if len(remaining)<3:break
    return out
def covered(required,polys):
    pieces=[required]
    for poly in polys:
        pieces=[p for original in pieces for p in subtract(original,poly)]
        if not pieces:break
    return g2.area(required)-sum(g2.area(p) for p in pieces)

def face(obj,up):
    points=[obj.matrix_world @ v.co for v in obj.data.vertices]
    faces=[[tuple(points[i]) for i in p.vertices] for p in obj.data.polygons if p.normal.z*up>.999]
    return max(faces,key=lambda ps:g2.area([(p[0],p[1]) for p in ps])) if faces else None
seats=[];fails=[]
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    support=None
    if obj.name.startswith('Column_'):support='Pedestal_'+obj.name.split('_')[1]
    elif obj.name.startswith('Pedestal_'):support='FootingPad_'+obj.name.split('_')[1]
    elif obj.name.startswith('CoreFoundation_'):support='CoreFooting_'+obj.name.split('_')[1]
    if support and bpy.data.objects.get(support):
        foot=face(obj,-1);seat=face(bpy.data.objects[support],1)
        report=check_bearing(foot,seat,tol=1e-5)
        seats.append((obj.name,support,report))
        if not report['ok']:fails.append((obj.name,support,report))

prefixes=('Column_','Corbel','Beam_','GradeBeam_','EdgeBeam','StairHeader','StairRim','Pedestal_','FootingPad_','CoreBeamLedge',
          'CoreWall_','CoreFoundation_','CoreFooting_','CoreRoofLedge','InsertColumn','InsertBeam','InsertPedestal','InsertFooting','RetainingWall','RetainingBase')
members=[(o.name,hull(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)]
members.sort(key=lambda p:p[1][3].x);graph={n:set() for n,h in members}
for i,(name,a) in enumerate(members):
    for other,b in members[i+1:]:
        if b[3].x>a[4].x+.002:break
        if any(a[3][j]>b[4][j]+.002 or b[3][j]>a[4][j]+.002 for j in (1,2)):continue
        if _gap(a,b)<=.002:graph[name].add(other);graph[other].add(name)
groups={}
groups['EntranceApproachGradeBeam']=['GradeBeam_0_0_2_0']
for name in graph:
    if name.startswith('StairRim_'):groups.setdefault('_'.join(name.split('_')[:3]),[]).append(name)
paths=[]
for key,names in sorted(groups.items()):
    queue=deque(names);parent={n:None for n in names};target=None
    while queue:
        n=queue.popleft()
        if n.startswith('FootingPad_'):target=n;break
        for other in sorted(graph[n]):
            if other not in parent:parent[other]=n;queue.append(other)
    path=[]
    while target is not None:path.append(target);target=parent[target]
    paths.append((key,list(reversed(path))))
lines=[SNAPSHOT,f'FULL FOOTPRINT SEATS: {len(seats)} tested; {len(fails)} failures; actual mesh horizontal faces; 0.01mm numerical tolerance.']
lines.extend(f'{name} -> {support}: area{report["required_area"]:.4f}m2; coverage{report["coverage"]:.6f}; gap{report["gap"]:.8f}m' for name,support,report in seats)
lines.append('\nRIM / ENTRANCE GRADE-BEAM TO FOUNDATION CONTACT PATHS: actual SAT gaps<=2mm; contacts do not establish bearing area or joint capacity.')
lines.extend(key+': '+' -> '.join(path) if path else key+': NO PATH' for key,path in paths)
tops={};bottoms={}
for obj in bpy.data.objects:
    if obj.type!='MESH' or not obj.name.startswith(('CorbelSeat','CorbelWing','Beam_')):continue
    up=-1 if obj.name.startswith('Beam_') else 1
    points=[obj.matrix_world @ v.co for v in obj.data.vertices]
    for face_poly in obj.data.polygons:
        if face_poly.normal.z*up<.999:continue
        vertices=[points[i] for i in face_poly.vertices];poly=[(p.x,p.y) for p in vertices]
        if g2.signed_area(poly)<0:poly.reverse()
        target=bottoms if up<0 else tops
        target.setdefault(round(vertices[0].z,4),[]).append((obj.name,poly))
seat_rows=[];seat_fail=[]
columns=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Column_')]
for column in columns:
    points=[column.matrix_world @ v.co for v in column.data.vertices]
    x=(min(p.x for p in points)+max(p.x for p in points))/2;y=(min(p.y for p in points)+max(p.y for p in points))/2
    for level in range(1,6):
        z=round(3.6*level-.9,4);beam_y=6.35 if level==1 and abs(y-6)<.001 else y
        if level<3 and y<.1:continue
        for side in (-1,1):
            if (x<.1 and side<0) or (x>53.9 and side>0):continue
            if 12.1<y<107.9 and ((abs(x-18)<.1 and side>0) or (abs(x-36)<.1 and side<0)):continue
            a,b=sorted((x+side*.3,x+side*.5));required=g2.rect(a,b,beam_y-.2,beam_y+.2)
            def local(entries):return [p for n,p in entries if max(px for px,py in p)>=a-.001 and min(px for px,py in p)<=b+.001 and max(py for px,py in p)>=beam_y-.201 and min(py for px,py in p)<=beam_y+.201]
            seat_area=covered(required,local(tops.get(z,[])));beam_area=covered(required,local(bottoms.get(z,[])))
            ok=seat_area>=.08-1e-5 and beam_area>=.08-1e-5
            seat_rows.append((column.name,level,side,seat_area,beam_area,ok))
            if not ok:seat_fail.append(seat_rows[-1])
lines.append(f'\nNOMINAL0.20x0.40m CORBEL END SEATS: {len(seat_rows)} expected geometric cases; {len(seat_fail)} exceptions. Both corbel-top and actual beam-underside union must cover0.080m2. Exceptions require local structural review; do not infer unsupported loads from missing beams alone.')
lines.extend(repr(row) for row in seat_fail)
reduced=[row for row in seat_fail if row[0]=='Column_81' and row[1]>1 and row[3]>=.08-1e-5 and row[4]>=.065-1e-5]
alternate=[row for row in seat_fail if row[0]=='Column_81' and row[1]==1]
lines.append(f'Designer classification: {len(seat_rows)-len(seat_fail)} ordinary0.20x0.40m seats; {len(reduced)} reduced0.20x0.325m seats (18.75% width/area reduction; capacity unverified); {len(alternate)} first-raised cases use core-ledges checked below. No blanket876-case capacity/pass claim.')
def horizontal_polys(prefix,z,up):
    polygons=[]
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not obj.name.startswith(prefix):continue
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        for p in obj.data.polygons:
            vertices=[points[i] for i in p.vertices]
            if p.normal.z*up>.999 and all(abs(v.z-z)<.00001 for v in vertices):
                poly=[(v.x,v.y) for v in vertices]
                if g2.signed_area(poly)<0:poly.reverse()
                polygons.append(poly)
    return polygons
connection_rows=[]
def connection(label,rect,z,below,above):
    required=g2.rect(*rect);area=g2.area(required)
    lower=covered(required,horizontal_polys(below,z,1))
    upper=covered(required,horizontal_polys(above,z,-1))
    ok=min(lower,upper)>=area-1e-5
    connection_rows.append((label,area,lower,upper,ok))
for label,xa,xb in [('W',43.475,43.675),('E',46.925,47.125)]:
    connection('Core beam alternate seat '+label,(xa,xb,6.15,6.55),2.70,'CoreBeamLedge_S_'+label,'Beam_1_')
for level in range(3):
    z=3.6*level-.25
    for label,seat,attachment,floor_prefix in [('W',(17.55,17.70),(17.35,17.55),f'FloorSlab_{level}_0_'),('E',(18.55,18.70),(18.70,18.90),f'InsertSlab_{level}_')]:
        ledger=f'InsertLinkLedger_{label}_{level}'
        support=f'EdgeBeam_{level}_1_' if label=='W' and level>0 else ledger
        connection(f'Link deck level{level} {label}0.15m seat via {support}',(*seat,74.,76.),z,support,f'InsertLinkDeck_{level}')
        if label=='W' and level>0:attachment=(17.35,17.50)
        connection(f'Link ledger level{level} {label}{attachment[1]-attachment[0]:.2f}m attachment',(*attachment,74.,76.),z,ledger,floor_prefix)
for level in (0,1):
    z=3.6*level+2.40
    for side,xa,xb in [('Wing',17.23,17.45),('Insert',18.55,18.75)]:
        for j,(ya,yb) in enumerate(((74.10,74.30),(75.70,75.90))):
            connection(f'Link lintel level{level} {side} jamb{j}',(xa,xb,ya,yb),z,f'InsertLinkPier_{side}_{level}_{j}',f'InsertLinkLintel_{side}_{level}')
lines.append('\nLOCAL CORE/LINK CONNECTION FACES: required horizontal seat areas and actual below/above mesh coverage; ledger attachment requires inferred anchors, not gravity-only bearing.')
lines.extend(repr(row) for row in connection_rows)
lines.append(f'Local connection face failures: {sum(not row[-1] for row in connection_rows)} / {len(connection_rows)}')
base_rows=[]
for label in 'WENS':
    supports=horizontal_polys(f'CoreFoundation_{label}',-.25,1)
    bases=horizontal_polys(f'CoreWallBase_{label}_',-.25,-1)
    upper_bases=horizontal_polys(f'CoreWallBase_{label}_',0.,1)
    wall_feet=horizontal_polys(f'CoreWall_{label}_0_',0.,-1)
    for kind,feet,seats_at_level in [('base-to-foundation',bases,supports),('wall-to-base',wall_feet,upper_bases)]:
        required=sum(g2.area(poly) for poly in feet);supported=sum(covered(poly,seats_at_level) for poly in feet)
        base_rows.append((label,kind,len(feet),required,supported,required-supported<1e-5))
lines.append('\nCORE VERTICAL BASE CONTINUITY: actual horizontal faces, both0.25m strip interfaces.')
lines.extend(repr(row) for row in base_rows)
lines.append(f'Core base union failures: {sum(not row[-1] for row in base_rows)} / {len(base_rows)}')
lines.append('\nLIMITATIONS: lateral/moment transfer is inferred where faces meet on a side; the contact graph is undirected and does not establish gravity capacity. Slab end bearings, corbel seat lengths, retaining restraint and diaphragm design require separate evidence/review. Sections are plausible visual estimates, not calculated.')
(HERE/'supports_v04.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(lines[0],flush=True)
for key,path in paths:print(key+': '+' -> '.join(path),flush=True)
if fails:print('Seat failures:',fails,flush=True)
