"""Continuous vertical headroom over convex usable tread/landing regions.

Unlike point sampling, intersect every projected underside with the walking
polygon. The height difference is affine, so its minimum is at an intersection
vertex. A 40mm radial edge allowance excludes the actual rail/post footprint.
Run in Blender after opening the saved v06 model; this does not alter geometry.
"""
from pathlib import Path
import ast
import math
import runpy
import sys
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
SNAPSHOT=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2

tree=ast.parse((HERE/'experiment_17_astra_v06.py').read_text(encoding='utf-8'))
centres=dict((label,(x,y)) for node in tree.body if isinstance(node,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='STAIRS' for t in node.targets)
             for label,x,y in ast.literal_eval(node.value))

def cells(bounds):
    return [(x,y) for x in range(math.floor(bounds[0]/6),math.floor(bounds[1]/6)+1)
                  for y in range(math.floor(bounds[2]/6),math.floor(bounds[3]/6)+1)]

undersides=[];index={};walks=[]
for obj in bpy.data.objects:
    if obj.type!='MESH': continue
    points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    matrix=obj.matrix_world.to_3x3().inverted().transposed()
    is_walk=obj.name.startswith(('StairTread_','StairLanding_'))
    for face in obj.data.polygons:
        normal=(matrix @ face.normal).normalized()
        vertices=[points[i] for i in face.vertices]
        outline=[(p.x,p.y) for p in vertices]
        if g2.signed_area(outline)<0: outline.reverse()
        if is_walk and normal.z>.999:
            cx,cy=centres[obj.name.split('_')[1]]
            if obj.name.startswith('StairLanding_'):
                walks.append((obj.name,g2.inset(outline,.04),vertices[0].z))
                continue
            radii=[math.hypot(x-cx,y-cy) for x,y in outline]
            mid=(min(radii)+max(radii))/2
            usable=[(cx+(x-cx)*(r+(.04 if r<mid else -.04))/r,
                     cy+(y-cy)*(r+(.04 if r<mid else -.04))/r) for (x,y),r in zip(outline,radii)]
            walks.append((obj.name,usable,vertices[0].z))
        if normal.z>=-.00001 or g2.area(outline)<1e-8: continue
        bounds=(min(p[0] for p in outline),max(p[0] for p in outline),min(p[1] for p in outline),max(p[1] for p in outline))
        number=len(undersides)
        undersides.append((obj.name,outline,normal,normal.dot(vertices[0]),bounds))
        for cell in cells(bounds): index.setdefault(cell,[]).append(number)

violations=[];minimum=(float('inf'),'','')
for name,walking,z in walks:
    bounds=(min(p[0] for p in walking),max(p[0] for p in walking),min(p[1] for p in walking),max(p[1] for p in walking))
    candidates={i for cell in cells(bounds) for i in index.get(cell,())}
    for i in candidates:
        other,outline,normal,plane,limit=undersides[i]
        if other==name or bounds[1]<=limit[0] or limit[1]<=bounds[0] or bounds[3]<=limit[2] or limit[3]<=bounds[2]: continue
        intersection=walking
        for a,b in zip(outline,outline[1:]+outline[:1]):
            intersection=g2.clip(intersection,a,(a[1]-b[1],b[0]-a[0]))
            if len(intersection)<3: break
        if len(intersection)<3 or g2.area(intersection)<1e-7: continue
        # Coplanar joint edges acquire micrometre-wide slivers at world
        # coordinates near 114m. Match the model's 1mm contact tolerance.
        if len(g2.inset(intersection,.0005))<3: continue
        gaps=[(plane-normal.x*x-normal.y*y)/normal.z-z for x,y in intersection]
        if max(gaps)<=.002: continue
        clearance=max(0.,min(gaps))
        if clearance<minimum[0]: minimum=(clearance,name,other)
        if clearance<2.10-.001: violations.append((clearance,name,other))

report=SNAPSHOT+f'\nCONTINUOUS HEADROOM: {len(walks)} convex walking regions; minimum {minimum[0]:.3f}m; {len(violations)} violations below2.10m\nGoverning: {minimum}\n'
report+='\n'.join(str(row) for row in sorted(violations))
(HERE/'headroom_v06.txt').write_text(report,encoding='utf-8')
print(report[:6000],flush=True)
if violations: raise RuntimeError('Stair headroom is below the design requirement')
