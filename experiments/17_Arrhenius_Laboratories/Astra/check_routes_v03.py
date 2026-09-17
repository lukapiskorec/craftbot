"""Actual-mesh circulation diagnostic, all stairs/levels, 2.10m envelope.
50mm floor samples and a conservative 1.30m sampled disc provide a 50mm
margin around the required 1.20m route. This remains sampled evidence.
"""
from pathlib import Path
from collections import deque
import math
import runpy
import bpy
import numpy as np

HERE=Path(__file__).resolve().parent
SNAPSHOT=runpy.run_path(str(HERE/'snapshot_v03.py'))['identity']()
STEP=.05
STAIRS={'W':(3.65,61.),'E':(50.35,61.),'N':(32.4,110.3),'S':(40.2,9.2)}
BOXES={'W':(.5,11.,56.,68.),'E':(43.,53.5,56.,68.),
       'N':(29.,49.,105.,113.5),'S':(36.5,49.,6.3,18.)}
def hull(points):
    points=sorted(set(points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    halves=[]
    for seq in (points,list(reversed(points))):
        half=[]
        for p in seq:
            while len(half)>1 and cross(half[-2],half[-1],p)<=0:half.pop()
            half.append(p)
        halves.append(half[:-1])
    return halves[0]+halves[1]

def raster(poly,target):
    if len(poly)<3:return
    ia=max(0,int(math.floor((min(p[0] for p in poly)-xs[0])/STEP)))
    ib=min(len(xs),int(math.ceil((max(p[0] for p in poly)-xs[0])/STEP))+1)
    ja=max(0,int(math.floor((min(p[1] for p in poly)-ys[0])/STEP)))
    jb=min(len(ys),int(math.ceil((max(p[1] for p in poly)-ys[0])/STEP))+1)
    if ia>=ib or ja>=jb:return
    xx,yy=np.meshgrid(xs[ia:ib],ys[ja:jb]);inside=np.ones(xx.shape,dtype=bool)
    for a,b in zip(poly,poly[1:]+poly[:1]):inside &= (b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0])>=-1e-6
    target[ja:jb,ia:ib] |= inside

meshes=[]
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    points=[obj.matrix_world @ v.co for v in obj.data.vertices]
    bounds=tuple(v for axis in range(3) for v in (min(p[axis] for p in points),max(p[axis] for p in points)))
    meshes.append((obj,points,bounds))
rows=[];failures=[]
for label,(cx,cy) in STAIRS.items():
    a,b,c,d=BOXES[label];xs=np.arange(a,b+.01,STEP);ys=np.arange(c,d+.01,STEP)
    local=[item for item in meshes if item[2][1]>=a and item[2][0]<=b and item[2][3]>=c and item[2][2]<=d]
    for level in range(5):
        z=3.6*level;clear=np.zeros((len(ys),len(xs)),dtype=bool);landing=np.zeros_like(clear);blocked=np.zeros_like(clear)
        for obj,points,bounds in local:
            if bounds[5]<z-.001 or bounds[4]>z+2.10:continue
            for face in obj.data.polygons:
                vertices=[points[i] for i in face.vertices]
                if face.normal.z>.999 and all(abs(p.z-z)<.001 for p in vertices):
                    poly=hull([(p.x,p.y) for p in vertices]);raster(poly,clear)
                    if obj.name.startswith('StairLanding_'+label+'_'):raster(poly,landing)
            # Projection of actual convex solid clipped to the walking height interval.
            cuts=[(p.x,p.y) for p in points if z+.01<=p.z<=z+2.10]
            for height in (z+.01,z+2.10):
                for edge in obj.data.edges:
                    p,q=(points[i] for i in edge.vertices)
                    if min(p.z,q.z)<=height<=max(p.z,q.z) and abs(p.z-q.z)>1e-7:
                        t=(height-p.z)/(q.z-p.z);cuts.append((p.x+t*(q.x-p.x),p.y+t*(q.y-p.y)))
            raster(hull(cuts),blocked)
        # Start at the arrival endpoint of the repeated semicircle; ground
        # starts at the departure endpoint. Test a single connected origin.
        side=-1 if label!='S' else 1
        start_x=cx+side*1.90*(1 if level else -1);start_y=cy+side*.70
        xx,yy=np.meshgrid(xs,ys)
        start_zone=(abs(xx-start_x)<.11)&(abs(yy-start_y)<.11)
        if level==0:landing=start_zone
        else:landing &= start_zone
        clear &= ~blocked;landing &= clear;disc=clear.copy();radius=round(.65/STEP)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy>radius*radius:continue
                shifted=np.zeros_like(clear);ja,jb=max(0,-dy),min(len(ys),len(ys)-dy);ia,ib=max(0,-dx),min(len(xs),len(xs)-dx)
                shifted[ja:jb,ia:ib]=clear[ja+dy:jb+dy,ia+dx:ib+dx];disc &= shifted
        seeds=list(zip(*np.where(disc & landing)))
        seeds=sorted(seeds,key=lambda p:(xs[p[1]]-start_x)**2+(ys[p[0]]-start_y)**2)[:1]
        seen=set(seeds);queue=deque(seeds);parents={p:None for p in seeds};target=None
        while queue:
            j,i=queue.popleft();x,y=xs[i],ys[j]
            reached=(label=='W' and 7.6<x<8.5 and y>65) or (label=='E' and 45.5<x<46.4 and y>65) or (label=='N' and 45.5<x<46.8 and y<106.5) or (label=='S' and 45.5<x<46.8 and y>15)
            if reached:target=(j,i);break
            for jj,ii in ((j-1,i),(j+1,i),(j,i-1),(j,i+1)):
                if 0<=jj<len(ys) and 0<=ii<len(xs) and disc[jj,ii] and (jj,ii) not in seen:seen.add((jj,ii));parents[jj,ii]=(j,i);queue.append((jj,ii))
        path=[];node=target
        while node is not None:path.append((float(xs[node[1]]),float(ys[node[0]])));node=parents[node]
        row=f'{label} level{level} z{z:.2f}: landing-disc centres {len(seeds)}; 1.20m route/2.10m height to main corridor: {target is not None}; visited {len(seen)}'
        print(row,flush=True);rows.append(row)
        if target is None:failures.append((label,level))
        np.savez(HERE/f'route_v03_{label}{level}.npz',xs=xs,ys=ys,clear=clear,landing=landing,disc=disc,path=np.array(path))
(HERE/'routes_v03.txt').write_text(SNAPSHOT+'\nACTUAL-MESH ROUTES; 50mm samples; 1.30m sampled disc for required1.20m; full2.10m obstacle envelope\n'+'\n'.join(rows)+'\nSampled geometric evidence, not regulatory compliance.\n',encoding='utf-8')
if failures:raise RuntimeError(f'Circulation fails: {failures}')
