"""Read-only frozen-mesh face/bearing evidence; no engineering capacity claims."""
from pathlib import Path
from collections import defaultdict, Counter
import re, sys, runpy, json
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
lines=[runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),
       'READ-ONLY actual saved geometry. Positive face area establishes a geometric interface, not anchors/reinforcement/capacity. Axis-face plane tolerance 0.01mm; area tolerance1e-7m2. No geometry changed.']

def intersect(poly,clip):
    for a,b in zip(clip,clip[1:]+clip[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
def subtract(poly,clip):
    pieces=[];remaining=poly
    for a,b in zip(clip,clip[1:]+clip[:1]):
        n=(a[1]-b[1],b[0]-a[0]);piece=g2.clip(remaining,a,(-n[0],-n[1]))
        if len(piece)>=3 and g2.area(piece)>1e-10:pieces.append(piece)
        remaining=g2.clip(remaining,a,n)
        if len(remaining)<3:break
    return pieces
def area(poly):return g2.area(poly) if len(poly)>=3 else 0.
def bounds2(poly):return (min(p[0] for p in poly),max(p[0] for p in poly),min(p[1] for p in poly),max(p[1] for p in poly))
def overlap(a,b,tol=1e-5):return not(a[1]<b[0]-tol or b[1]<a[0]-tol or a[3]<b[2]-tol or b[3]<a[2]-tol)
def coverage(required,polys):
    remainder=[required]
    for poly in polys:
        if not overlap(bounds2(required),bounds2(poly)):continue
        poly=intersect(poly,required)
        if area(poly)<1e-9:continue
        remainder=[p for r in remainder for p in subtract(r,poly)]
        if not remainder:break
    return area(required)-sum(area(p) for p in remainder)

faces={};bounds={};index=defaultdict(list)
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
    bounds[obj.name]=tuple(n for i in range(3) for n in (min(v[i] for v in vertices),max(v[i] for v in vertices)))
    ff=[]
    for polygon in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@polygon.normal).normalized()
        axis=max(range(3),key=lambda k:abs(normal[k]))
        if abs(normal[axis])<.99999:continue
        sign=1 if normal[axis]>0 else -1
        ps=[vertices[k] for k in polygon.vertices];plane=sum(p[axis] for p in ps)/len(ps)
        if max(abs(p[axis]-plane) for p in ps)>1e-5:continue
        dims=[k for k in range(3) if k!=axis]
        poly=[(p[dims[0]],p[dims[1]]) for p in ps]
        if g2.signed_area(poly)<0:poly.reverse()
        face=(axis,sign,plane,poly,bounds2(poly))
        ff.append(face);index[axis,sign,round(plane,4)].append((obj.name,face))
    faces[obj.name]=ff
print('Face cache complete',flush=True)

def contacts(name,allow=lambda n:True,axes=(0,1,2)):
    found=[]
    for axis,sign,plane,poly,bb in faces[name]:
        if axis not in axes:continue
        for other,face in index.get((axis,-sign,round(plane,4)),[]):
            if other==name or not allow(other):continue
            if abs(plane-face[2])>1e-5 or not overlap(bb,face[4]):continue
            common=intersect(poly,face[3]);a=area(common)
            if a>1e-7:found.append((other,axis,sign,plane,a,common))
    return found
def bottom_report(name):
    feet=[f for f in faces[name] if f[0]==2 and f[1]==-1]
    rows=[]
    for _,_,plane,poly,bb in feet:
        support=[]
        for other,f in index.get((2,1,round(plane,4)),[]):
            if other==name or abs(plane-f[2])>1e-5 or not overlap(bb,f[4]):continue
            a=area(intersect(poly,f[3]))
            if a>1e-7:support.append((other,a,f[3]))
        covered=coverage(poly,[p for n,a,p in support]);required=area(poly)
        rows.append((plane,required,covered,[(n,a) for n,a,p in support]))
    return rows
def family(name):return re.sub(r'_[0-9].*','',name)

lines.append('\n1. ORDINARY MAIN SLAB END BEARINGS')
lines.append('Audit actual rectangular bottom faces at nominal slab underside, y-span>=5.0m,x-span>=0.5m, with longitudinal ends on actual structural stations or external slab perimeter. Internal column-notch/decomposition ends are excluded, not treated as separate physical panels. Small/notched discontinuity remnants remain outside this bounded audit. Both actual end strips0.12m deep must be covered by real upward support faces.')
rows=[];support_families=Counter();excluded=0
for name,ff in faces.items():
    if '--priority' in sys.argv:continue
    m=re.match(r'FloorSlab_([1-5])_',name)
    if not m:continue
    expected=3.6*int(m.group(1))-.25
    for axis,sign,z,poly,bb in ff:
        if axis!=2 or sign!=-1 or abs(z-expected)>1e-5:continue
        x0,x1,y0,y1=bb
        datums=[6.*k for k in range(20)]+[.3,113.7]
        if int(m.group(1))==1:datums.append(6.35)
        if y1-y0<5 or x1-x0<.5 or abs(area(poly)-(x1-x0)*(y1-y0))>1e-5 or any(min(abs(y-d) for d in datums)>1e-4 for y in (y0,y1)):
            excluded+=1;continue
        supports=[(n,f) for n,f in index.get((2,1,round(z,4)),[]) if n.startswith(('PerimeterLedger','Beam_','StairHeader','StairRim','CoreWall','CoreRoofLedge','Corbel','Column_')) and n!=name and abs(f[2]-z)<1e-5 and overlap(bb,f[4])]
        for side in (-1,1):
            strip=g2.rect(x0,x1,y0,y0+.12) if side<0 else g2.rect(x0,x1,y1-.12,y1)
            hit=[(n,f) for n,f in supports if area(intersect(strip,f[3]))>1e-7]
            required=area(strip);actual=coverage(strip,[f[3] for n,f in hit]);ok=required-actual<1e-5
            lo,hi=0.,min(.5,(y1-y0)/2)
            for _ in range(10):
                depth=(lo+hi)/2
                trial=g2.rect(x0,x1,y0,y0+depth) if side<0 else g2.rect(x0,x1,y1-depth,y1)
                if area(trial)-coverage(trial,[f[3] for n,f in supports])<1e-6:lo=depth
                else:hi=depth
            rows.append((name,side,required,actual,lo,ok,[n for n,f in hit]))
            support_families.update(set(family(n) for n,f in hit))
    if len(rows) and len(rows)%200==0:print(f'Ordinary end cases {len(rows)}',flush=True)
fails=[r for r in rows if not r[5]]
lines.append(f'{len(rows)} end-strip cases; {len(fails)} do not attain0.12m full-width coverage; excluded {excluded} small/notched bottom faces. Minimum full-width supported depth {min((r[4] for r in rows),default=0):.6f}m. Families {dict(support_families)}')
fail_groups=Counter((int(r[0].split('_')[1]),round(bounds[r[0]][2 if r[1]<0 else 3],4)) for r in fails)
lines.append('Failures grouped by (floor index, actual y-end datum): '+repr(dict(sorted(fail_groups.items()))))
if '--priority' not in sys.argv:
    (HERE/'slab_end_faces_v06.json').write_text(json.dumps([dict(name=r[0],side=r[1],bounds=bounds[r[0]],required_area=r[2],actual_area=r[3],conservative_full_width_depth=r[4],passed=r[5],supports=r[6]) for r in rows],indent=2),encoding='utf-8')
lines.extend('END FAIL '+repr(row) for row in fails[:40])
lines.extend('REPRESENTATIVE '+repr(row) for row in rows[:4])
print('Main slab audit complete',flush=True)

lines.append('\n2. CORE / FLOOR AND ROOF DIAPHRAGM PHYSICAL INTERFACES')
lines.append('Areas below are actual coplanar opposed faces. x-normal and y-normal vertical areas establish both plan-direction abutments; they do not establish shear anchors or reinforcement.')
for label in 'WENS':
    names=[n for n in faces if n.startswith((f'CoreWall_{label}_',f'CoreWallBase_{label}_',f'CoreRoofLedge_{label}_'))]
    for level in range(6):
        allow=lambda n,l=level: n.startswith(f'FloorSlab_{l}_') or (l==0 and n==f'CoreGroundSlab_{label}') or (l==5 and n==f'CoreRoofSlab_{label}')
        cc=[(n,*c[:5]) for n in names for c in contacts(n,allow)]
        sums={axis:sum(c[5] for c in cc if c[2]==axis) for axis in range(3)}
        pairs=sorted(set((c[0],c[1]) for c in cc))
        lines.append(f'Core{label} level{level} z{level*3.6:.2f}: {len(pairs)} member pairs; x-normal area{sums[0]:.6f},y-normal{sums[1]:.6f},horizontal{sums[2]:.6f}m2; '+repr(pairs[:4]))
print('Core interfaces complete',flush=True)

lines.append('\n3. RETAINING / TERRACE / EXTERIOR COURT STAIR')
for name in sorted(n for n in faces if n.startswith(('RetainingWall','RetainingBase','NorthTerrace','CourtStair')) and not any(x in n for x in ('Handrail','Baluster'))):
    rows=bottom_report(name)
    lines.append(f'{name}: bounds{bounds[name]}; downward horizontal faces '+repr(rows))
    if name.startswith(('RetainingWall','NorthTerrace')):
        cc=contacts(name)
        lines.append('  Other actual positive-area contacts: '+repr([(n,axis,sign,round(plane,5),round(a,6)) for n,axis,sign,plane,a,p in cc]))
lines.append('The bottom-face audit includes every actual mesh object as a possible support; rail/edge-only contact yields no horizontal support area. Soil below foundation bottom is not modelled and is not itself a foundation discontinuity. Concept9 explicitly omits terrace earth/base; report its uncovered underside as an unmodeled ground-bearing boundary, not mesh-proved support.')
lines.append('REGIONAL EXISTING OBJECTS: x33..35.45,y89.7..107.23,z-1.25..3.1; includes boundary contacts, excludes CourtStair family already listed. Bounding boxes are candidates, not solid overlap assertions.')
for n,b in sorted(bounds.items()):
    if n.startswith('CourtStair'):continue
    if b[1]>=33.-1e-4 and b[0]<=35.45+1e-4 and b[3]>=89.7-1e-4 and b[2]<=107.23+1e-4 and b[5]>=-1.25 and b[4]<=3.1:
        lines.append(n+': '+repr(b))
lines.append('ALL SITE SURFACE BOUNDS: '+repr([(n,b) for n,b in bounds.items() if n.startswith(('SiteGround','CourtyardGarden','CourtPathEast','NorthTerrace'))]))
print('Retaining and site stairs complete',flush=True)

lines.append('\n4. PLANT / INSERT / ROOFLIGHT SUPPORT INTERFACES')
lines.append('Insert column base chain: actual column foot atz0 -> ground slab0..-.25 -> pedestal/gradebeam upward faces at-.25 -> named footing contacts below. These are local bearing footprints, not a slab punching-shear calculation.')
for name in sorted(n for n in faces if n.startswith('InsertColumn_')):
    for axis,sign,z,poly,bb in faces[name]:
        if axis!=2 or sign!=-1 or abs(z)>1e-5:continue
        seats=[(n,f) for n,f in index.get((2,1,-.25),[]) if n.startswith(('InsertPedestal','InsertGradeBeam')) and overlap(bb,f[4])]
        cov=coverage(poly,[f[3] for n,f in seats])
        lines.append(f'{name} projected ground-slab underside footprint: required{area(poly):.6f}m2,seated{cov:.6f}m2,on '+repr([n for n,f in seats if area(intersect(poly,f[3]))>1e-7]))
for name in sorted(n for n in faces if n.startswith(('PlantPlinth','RooflightSeatBeam','SkylightCurb','InsertBeam','InsertColumn','InsertPedestal','InsertFooting'))):
    rows=bottom_report(name)
    cc=contacts(name,lambda n:n.startswith(('FloorSlab','InsertSlab','InsertColumn','InsertBeam','InsertGradeBeam','InsertPedestal','InsertFooting','RooflightSeatBeam','Skylight','Plant','Retaining','Core','Beam_','EdgeBeam')))
    lines.append(f'{name}: bounds{bounds[name]}; bottom '+repr(rows))
    lines.append('  Contacts '+repr([(n,axis,sign,round(plane,5),round(a,6)) for n,axis,sign,plane,a,p in cc][:30]))

# Rooflight glass itself meets frames mainly on edge faces. Report those
# separately from a horizontal bearing claim.
for prefix in ('PlantClad','SkylightGlass','SkylightMullion','SkylightTransom','InsertSlab_1_','InsertSlab_2_'):
    names=sorted(n for n in faces if n.startswith(prefix))
    horizontal=Counter();vertical=Counter();unseated=[]
    for n in names:
        cc=contacts(n,lambda other:other.startswith(('Plant','FloorSlab','Skylight','Insert','Rooflight','Retaining')))
        horizontal.update(family(other) for other,axis,sign,plane,a,p in cc if axis==2 and sign==-1)
        vertical.update(family(other) for other,axis,sign,plane,a,p in cc if axis!=2)
        if not any(axis==2 and sign==-1 for other,axis,sign,plane,a,p in cc):unseated.append(n)
    lines.append(f'{prefix}: {len(names)} members; downward-bearing contact families{dict(horizontal)}; side-contact families{dict(vertical)}; no downward horizontal seat for{len(unseated)}. Examples '+repr(unseated[:8]))

insert_ends=[]
for name,ff in faces.items():
    m=re.match(r'InsertSlab_([12])_',name)
    if not m:continue
    zfloor=3.6*int(m.group(1))-.25
    for axis,sign,z,poly,bb in ff:
        if axis!=2 or sign!=-1 or abs(z-zfloor)>1e-5:continue
        x0,x1,y0,y1=bb
        if x1-x0<.5 or y1-y0<5. or abs(area(poly)-(x1-x0)*(y1-y0))>1e-5:continue
        if any(min(abs(y-d) for d in range(66,97,6))>1e-4 for y in (y0,y1)):continue
        support=[f[3] for n,f in index.get((2,1,round(z,4)),[]) if n.startswith(('InsertBeam','InsertColumn','InsertWestWall','InsertEndWall','RooflightSeatBeam','Retaining')) and overlap(bb,f[4])]
        for side in (-1,1):
            strip=g2.rect(x0,x1,y0,y0+.12) if side<0 else g2.rect(x0,x1,y1-.12,y1)
            cov=coverage(strip,support)
            insert_ends.append((name,side,y0 if side<0 else y1,area(strip),cov,area(strip)-cov<1e-5))
lines.append('INSERT ordinary fullspan rectangular end-strip screening (not a separate-piece assertion for notches): '+repr(insert_ends))
lines.append(f'Insert end strips: {len(insert_ends)} cases,{sum(not r[-1] for r in insert_ends)} lack0.12m end bearing. This is decisive only if these are independent precast spans: a declared cast-integral slab/beam transfer at the shared vertical joint is a different inferred connection, not horizontal bearing evidence.')

lines.append('\nLIMITATIONS: ordinary end-seat subset is explicitly bounded; no assumption that every clipped floor fragment is an independent spanning unit. Side-face continuity can represent a cast-integral or anchored joint only with a declared inferred connection, never proven gravity capacity. Positive face contact does not determine reinforcement, anchorage, bending, shear, diaphragm transfer, soil or retaining stability. No geometry changed or renders made.')
output=HERE/('structural_priority_v06.txt' if '--priority' in sys.argv else 'structural_followup_v06.txt')
output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('WROTE '+str(output),flush=True)
