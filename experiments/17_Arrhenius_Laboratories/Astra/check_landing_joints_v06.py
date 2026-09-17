"""Finite actual interface dimensions for the approved stepped landing fit."""
from pathlib import Path
from collections import deque
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
prefixes=('CourtLandingSupport','CourtLandingLedge','CourtWaist_19','CorbelWing_76_1_-1','Column_76','RetainingWall')
objects={o.name:o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)}
faces={}
for name,obj in objects.items():
    points=[obj.matrix_world@v.co for v in obj.data.vertices];ff=[]
    for face in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized()
        axis=max(range(3),key=lambda i:abs(normal[i]))
        if abs(normal[axis])<.99999:continue
        ps=[points[i] for i in face.vertices];plane=sum(p[axis] for p in ps)/len(ps)
        dims=[i for i in range(3) if i!=axis];poly=[(p[dims[0]],p[dims[1]]) for p in ps]
        if g2.signed_area(poly)<0:poly.reverse()
        ff.append((axis,1 if normal[axis]>0 else -1,plane,poly))
    faces[name]=ff
def intersection(poly,clip):
    for a,b in zip(clip,clip[1:]+clip[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
joints=[];graph={n:set() for n in objects}
for name in objects:
    for other in objects:
        if other<=name:continue
        for axis,sign,z,poly in faces[name]:
            for ax,sg,plane,clip in faces[other]:
                if ax!=axis or sg==sign or abs(z-plane)>2e-5:continue
                patch=intersection(poly,clip)
                area=g2.area(patch) if len(patch)>=3 else 0.
                if area<1e-6:continue
                spans=tuple(max(p[i] for p in patch)-min(p[i] for p in patch) for i in range(2))
                joints.append((name,other,axis,z,area,spans))
                if area>.001:graph[name].add(other);graph[other].add(name)
rows=[runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),
      'Actual opposed planar face patches; dimensions are in the two axes normal to reported axis. Graph edges require >0.001m2, not an epsilon touch. Tiny chamfer fragments are monolithic decomposition, not independent seat units.']
rows += [repr(j) for j in joints if j[0].startswith(('CourtLanding','CorbelWing')) or j[1].startswith(('CourtLanding','CorbelWing'))]
roots=[j for j in joints if {j[0],j[1]}=={'CorbelWing_76_1_-1','Column_76'}]
assert sum(j[4] for j in roots)>=.36-2e-5,roots
for name in sorted(n for n in objects if n.startswith('CourtLandingSupport')):
    queue=deque([name]);parents={name:None};target=None
    while queue:
        current=queue.popleft()
        if current.startswith(('Column_76','RetainingWall')):target=current;break
        for other in sorted(graph[current]):
            if other not in parents:parents[other]=current;queue.append(other)
    assert target is not None,name
    route=[]
    while target is not None:route.append(target);target=parents[target]
    rows.append(name+' finite-interface path: '+' -> '.join(reversed(route)))
rows.append('Corbel/shaft root area '+str(sum(j[4] for j in roots))+'m2; nominal600x600mm. Capacities remain unverified.')
(HERE/'landing_joints_v06.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows),flush=True)
