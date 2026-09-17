"""Read-only50mm route raster of actual horizontal floor/landing mesh faces.
Obstacles use actual convex sections50mm above floor. Omitting higher obstacles
is optimistic: a missing route here cannot be cured by adding those obstacles.
Raster sampling is evidence for review, not a continuous/code compliance proof.
"""
from pathlib import Path
from collections import deque
import math
import bpy
import numpy as np

HERE=Path(__file__).resolve().parent
meshes=[]
for obj in bpy.data.objects:
    if obj.type!='MESH': continue
    points=[obj.matrix_world @ v.co for v in obj.data.vertices]
    if max(p.x for p in points)<.5 or min(p.x for p in points)>10 or max(p.y for p in points)<56 or min(p.y for p in points)>66: continue
    meshes.append((obj,points))

def convex_hull(points):
    points=sorted(set(points))
    def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower=[];upper=[]
    for p in points:
        while len(lower)>1 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper)>1 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]

def raster(poly,target):
    if len(poly)<3: return
    ia=max(0,int(math.floor((min(p[0] for p in poly)-xs[0])/step)))
    ib=min(len(xs),int(math.ceil((max(p[0] for p in poly)-xs[0])/step))+1)
    ja=max(0,int(math.floor((min(p[1] for p in poly)-ys[0])/step)))
    jb=min(len(ys),int(math.ceil((max(p[1] for p in poly)-ys[0])/step))+1)
    if ia>=ib or ja>=jb:return
    xx,yy=np.meshgrid(xs[ia:ib],ys[ja:jb]);inside=np.ones(xx.shape,dtype=bool)
    for a,b in zip(poly,poly[1:]+poly[:1]): inside &= (b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0])>=-1e-6
    target[ja:jb,ia:ib] |= inside
step=.05
rows=[]
for level in (1,4):
    z=3.6*level
    xs=np.arange(.5,10.01,step)
    ys=np.arange(56.,66.01,step)
    clear=np.zeros((len(ys),len(xs)),dtype=bool)
    landing=np.zeros_like(clear)
    blocked=np.zeros_like(clear)
    for obj,points in meshes:
        for face in obj.data.polygons:
            vertices=[points[i] for i in face.vertices]
            if face.normal.z>.999 and all(abs(p.z-z)<.001 for p in vertices):
                poly=convex_hull([(p.x,p.y) for p in vertices]);raster(poly,clear)
                if obj.name.startswith('StairLanding_W_'): raster(poly,landing)
        cuts=[];height=z+.05
        for edge in obj.data.edges:
            a,b=(points[i] for i in edge.vertices)
            if min(a.z,b.z)<=height<=max(a.z,b.z) and abs(a.z-b.z)>1e-7:
                t=(height-a.z)/(b.z-a.z);cuts.append((a.x+t*(b.x-a.x),a.y+t*(b.y-a.y)))
        raster(convex_hull(cuts),blocked)
    clear &= ~blocked
    landing &= clear
    # Inscribed sampled disc: points on/inside radius0.60 at50mm spacing.
    disc=clear.copy()
    radius=round(.6/step)
    for dy in range(-radius,radius+1):
        for dx in range(-radius,radius+1):
            if dx*dx+dy*dy>radius*radius: continue
            shifted=np.zeros_like(clear)
            ja,jb=max(0,-dy),min(len(ys),len(ys)-dy)
            ia,ib=max(0,-dx),min(len(xs),len(xs)-dx)
            shifted[ja:jb,ia:ib]=clear[ja+dy:jb+dy,ia+dx:ib+dx]
            disc &= shifted
    seeds=list(zip(*np.where(disc & landing)))
    seen=set(seeds); queue=deque(seeds)
    while queue:
        j,i=queue.popleft()
        for jj,ii in ((j-1,i),(j+1,i),(j,i-1),(j,i+1)):
            if 0<=jj<len(ys) and 0<=ii<len(xs) and disc[jj,ii] and (jj,ii) not in seen:
                seen.add((jj,ii));queue.append((jj,ii))
    reached=any(xs[i]>=9.0 for j,i in seen)
    row=f'West level{level} z{z:.2f}: {int(landing.sum())} landing sample centres; {len(seeds)} support/clearance-disc centres; route reaches x9.0 corridor: {reached}; reached cells {len(seen)}'
    print(row,flush=True);rows.append(row)
    np.savez(HERE/f'route_v02_W{level}.npz',xs=xs,ys=ys,clear=clear,landing=landing,disc=disc)
(HERE/'routes_v02.txt').write_text('FROZEN v02 MESH ROUTE DIAGNOSTIC; 50mm samples; 1.20m disc; actual floor faces and obstacle section50mm above floor\n'+'\n'.join(rows)+'\nHigher obstacles omitted (optimistic). Raster sampling does not prove continuous clearances or regulatory compliance.\n',encoding='utf-8')
