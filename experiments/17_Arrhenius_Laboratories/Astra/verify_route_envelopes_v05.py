"""Continuous convex swept-route coverage/obstacle test on saved geometry.
Consumes paths from check_routes_v05.py. Each swept disc is enclosed by a
32-sided circumscribed polygon. Floor coverage is exact convex subtraction;
obstacles are actual convex solids projected within2.10m above walking level.
"""
from pathlib import Path
import math
import runpy
import sys
import bpy
import numpy as np
HERE=Path(__file__).resolve().parent
SNAPSHOT=runpy.run_path(str(HERE/'snapshot_v05.py'))['identity']()
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2

def hull(points):
    points=sorted(set(points));halves=[]
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    for seq in (points,points[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and cross(half[-2],half[-1],p)<=0:half.pop()
            half.append(p)
        halves.extend(half[:-1])
    return halves
def bounds(poly):return min(x for x,y in poly),max(x for x,y in poly),min(y for x,y in poly),max(y for x,y in poly)
def overlaps(a,b):return a[1]>b[0] and b[1]>a[0] and a[3]>b[2] and b[3]>a[2]
def intersection(poly,clip):
    for a,b in zip(clip,clip[1:]+clip[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
def difference(poly,clip):
    remaining=poly;outside=[]
    for a,b in zip(clip,clip[1:]+clip[:1]):
        n=(a[1]-b[1],b[0]-a[0]);piece=g2.clip(remaining,a,(-n[0],-n[1]))
        if len(piece)>=3 and g2.area(piece)>1e-8:outside.append(piece)
        remaining=g2.clip(remaining,a,n)
        if len(remaining)<3:break
    return outside

meshes=[]
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    points=[obj.matrix_world @ v.co for v in obj.data.vertices]
    meshes.append((obj,points,min(p.z for p in points),max(p.z for p in points)))
rows=[];failures=[]
for level in range(5):
    z=3.6*level;floors=[];obstacles=[]
    for obj,points,zlo,zhi in meshes:
        if zhi<z-.001 or zlo>z+2.10:continue
        for face in obj.data.polygons:
            vertices=[points[i] for i in face.vertices]
            if face.normal.z>.999 and all(abs(p.z-z)<.001 for p in vertices):
                poly=hull([(p.x,p.y) for p in vertices]);floors.append((poly,bounds(poly)))
        cuts=[(p.x,p.y) for p in points if z+.002<=p.z<=z+2.10]
        for height in (z+.002,z+2.10):
            for edge in obj.data.edges:
                a,b=(points[i] for i in edge.vertices)
                if min(a.z,b.z)<=height<=max(a.z,b.z) and abs(a.z-b.z)>1e-7:
                    t=(height-a.z)/(b.z-a.z);cuts.append((a.x+t*(b.x-a.x),a.y+t*(b.y-a.y)))
        poly=hull(cuts)
        if len(poly)>2 and g2.area(poly)>1e-8:obstacles.append((obj.name,poly,bounds(poly)))
    cases={label:np.load(HERE/f'route_v05_{label}{level}.npz')['path'].tolist() for label in 'WENS'}
    if level>0:
        cases['LOOP']=[(7.7,14.),(7.7,109.0125),(46.3,109.0125),(46.3,13.2),(40.2,13.2),(40.2,10.3),(7.7,10.3),(7.7,14.)]
    for label,(cx,cy) in {'W':(3.65,61.),'E':(50.35,61.),'N':(32.4,110.3),'S':(40.2,9.2)}.items():
        side=-1 if label!='S' else 1
        cases[label+'_GALLERY']=[(cx-1.9,cy+side*.7),(cx+1.9,cy+side*.7)]
    if level==0:
        cases['E_COURT_GALLERY']=[(48.45,60.3),(46.3,60.3),(46.3,61.),(38.3,61.)]
        cases['SOUTH_ENTRANCE_FOYER']=[(22.5,.9),(22.5,10.3),(38.3,10.3),(38.3,15.)]
    if level<2:cases['INSERT_ACCESS']=[(7.7,75.),(22.,75.)]
    for label,path in cases.items():
        if not path:failures.append((label,level,'no sampled path'));continue
        simplified=[path[0]]
        for i in range(1,len(path)-1):
            before=(round(path[i][0]-path[i-1][0],4),round(path[i][1]-path[i-1][1],4))
            after=(round(path[i+1][0]-path[i][0],4),round(path[i+1][1]-path[i][1],4))
            if before!=after:simplified.append(path[i])
        simplified.append(path[-1]);uncovered=0.;wide_uncovered=0.;hits=set();max_seam=0.
        half_width=.70 if label=='INSERT_ACCESS' else .60
        radius=half_width/math.cos(math.pi/32)
        for p,q in zip(simplified,simplified[1:]):
            tube=hull([(pt[0]+radius*math.cos(2*math.pi*k/32+math.pi/32),pt[1]+radius*math.sin(2*math.pi*k/32+math.pi/32)) for pt in (p,q) for k in range(32)])
            bb=bounds(tube);remaining=[tube]
            for floor,fb in floors:
                if not overlaps(bb,fb):continue
                remaining=[piece for poly in remaining for piece in difference(poly,floor)]
                if not remaining:break
            uncovered+=sum(g2.area(poly) for poly in remaining)
            for piece in remaining:
                # World-coordinate Blender float32 seams can be several
                # micrometres wide. Measure each residual's maximum inset
                # diameter instead of adding its area repeatedly along turns.
                lo,hi=0.,.001
                for iteration in range(18):
                    mid=(lo+hi)/2
                    if len(g2.inset(piece,mid))>=3:lo=mid
                    else:hi=mid
                max_seam=max(max_seam,2*lo)
                if len(g2.inset(piece,.00001))>=3:wide_uncovered+=g2.area(piece)
            for name,ob,obounds in obstacles:
                if overlaps(bb,obounds):
                    overlap=intersection(tube,ob)
                    if g2.area(overlap)>1e-7 and len(g2.inset(overlap,.00001))>=3:hits.add(name)
        ok=wide_uncovered<1e-7 and not hits
        row=f'{label} level{level}: {len(simplified)-1} continuous swept segments; verified envelope width{2*half_width:.3f}m/headroom2.100m; raw seam area{uncovered:.9f}m2; max residual inscribed diameter{max_seam*1000:.6f}mm; unsupported area beyond20micrometre numerical allowance{wide_uncovered:.9f}m2; obstacle hits{len(hits)}; PASS{ok}'
        rows.append(row);print(row,flush=True)
        if not ok:failures.append((label,level,uncovered,sorted(hits)))
report=SNAPSHOT+'\nCONTINUOUS1.20m ROUTE/2.10m HEIGHT ENVELOPES (insert1.40m);32-sided circumscribed discs; actual-mesh floor union and clipped solids\n'+'\n'.join(rows)+'\nFailures: '+repr(failures)+'\nTolerance:20micrometre maximum inscribed diameter for float32 floor/doorway seams,1e-7m2 per obstacle intersection; no engineering/code claim.\n'
(HERE/'route_envelopes_v05.txt').write_text(report,encoding='utf-8')
if failures:raise RuntimeError(str(failures))
