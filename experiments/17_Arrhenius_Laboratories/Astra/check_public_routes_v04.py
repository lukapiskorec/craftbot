"""Continuous width/headroom strips along entrance and stepped court routes.
Uses exact convex mesh sections, records riser transitions separately.
"""
from pathlib import Path
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
from mathutils import Vector
def hull(points):
    points=sorted(set(points));out=[]
    for seq in (points,points[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and (half[-1][0]-half[-2][0])*(p[1]-half[-2][1])-(half[-1][1]-half[-2][1])*(p[0]-half[-2][0])<=0:half.pop()
            half.append(p)
        out.extend(half[:-1])
    return out
def difference(poly,clip):
    inside=poly;out=[]
    for a,b in zip(clip,clip[1:]+clip[:1]):
        normal=(a[1]-b[1],b[0]-a[0])
        piece=g2.clip(inside,a,(-normal[0],-normal[1]))
        if len(piece)>2 and g2.area(piece)>1e-9:out.append(piece)
        inside=g2.clip(inside,a,normal)
        if len(inside)<3:break
    return out
meshes=[(o,[o.matrix_world@v.co for v in o.data.vertices]) for o in bpy.data.objects if o.type=='MESH']
strips=[('Lawn',21.9,23.1,-2.,-.9,-.15),('Paving',21.9,23.1,-.9,.3,0.),('Porch',21.9,23.1,.3,1.5,0.),
        ('CourtGarden',33.75,34.95,64.,65.8,-.1),('CourtPath',33.75,34.95,65.8,89.7,0.)]
strips += [(f'CourtTread{i+1}',33.75,34.95,89.7+i*.3,90.+i*.3,(i+1)*.15) for i in range(19)]
strips += [('CourtTop',33.75,34.95,95.4,96.,3.),('RetainingTop',33.75,34.95,96.,96.3,3.),('Terrace',33.75,34.95,96.3,100.,3.)]
strips += [('DoorAperture',21.3,23.7,5.95,6.15,0.)]
rows=[runpy.run_path(str(HERE/'snapshot_v04.py'))['identity']()];failures=[]
for label,xa,xb,ya,yb,z in strips:
    walk=g2.rect(xa,xb,ya,yb);remaining=[walk];hits=[]
    height_clear=2.4-.00002 if label=='DoorAperture' else 2.1
    for obj,points in meshes:
        if min(p.x for p in points)>xb or max(p.x for p in points)<xa or min(p.y for p in points)>yb or max(p.y for p in points)<ya:continue
        if min(p.z for p in points)>z+height_clear or max(p.z for p in points)<z-2e-5:continue
        for face in obj.data.polygons:
            verts=[points[i] for i in face.vertices]
            if face.normal.z>.999 and all(abs(p.z-z)<2e-5 for p in verts):
                floor=hull([(p.x,p.y) for p in verts])
                remaining=[piece for poly in remaining for piece in difference(poly,floor)]
        cuts=[(p.x,p.y) for p in points if z+.002<=p.z<=z+height_clear]
        for height in (z+.002,z+height_clear):
            for edge in obj.data.edges:
                a,b=(points[i] for i in edge.vertices)
                if min(a.z,b.z)<=height<=max(a.z,b.z) and abs(b.z-a.z)>1e-8:
                    t=(height-a.z)/(b.z-a.z);cuts.append((a.x+t*(b.x-a.x),a.y+t*(b.y-a.y)))
        poly=g2.clip_rect(hull(cuts),xa,xb,ya,yb)
        if len(poly)>2 and len(g2.inset(poly,.00001))>2 and g2.area(poly)>1e-7:hits.append(obj.name)
    gap=sum(g2.area(p) for p in remaining if len(g2.inset(p,.00001))>2)
    ok=not hits and gap<1e-7
    rows.append(f'{label}: width{xb-xa:.3f}m/headroom{height_clear:.3f}m; floor z{z:.3f}; gap{gap:.9f}m2; obstacles{hits}; PASS{ok}')
    if not ok:failures.append(label)
rows+=['Risers: lawn to paving0.150m; garden to path0.100m; nineteen tread tops plus landing make20 x0.150m rises to3.000m. Consecutive strip boundaries coincide; these are stepped pedestrian routes, not accessible ramps.',f'Failures: {failures}']
def bbox(points):return tuple(value for axis in range(3) for value in (min(p[axis] for p in points),max(p[axis] for p in points)))
byname={o.name:bbox(p) for o,p in meshes}
paving=byname['EntranceApproachSlab'];remaining=[g2.rect(*paving[:4])];areas={}
for name,b in byname.items():
    if not name.startswith(('EntranceApproachBase','GradeBeam_')) or abs(b[5]-paving[4])>2e-5:continue
    seat=g2.clip_rect(g2.rect(*b[:4]),*paving[:4])
    if len(seat)<3:continue
    areas[name]=g2.area(seat)
    remaining=[piece for poly in remaining for piece in difference(poly,seat)]
bearing=sum(g2.area(p) for p in remaining)<1e-5
rows.append(f'Approach full-footprint slab support atz{paving[4]:.3f}: actual face areas{areas}; PASS{bearing}; prepared soil below fitted base inferred.')
occupied=[(.77,17.23,.77,113.23,0.,18.),(36.77,53.23,.77,113.23,0.,18.),(17.23,36.77,6.3,12.3,0.,18.),(17.23,36.77,107.7,113.23,0.,18.),(18.75,31.3,66.2,95.8,0.,7.2)]
terrain_hits=[name for name,b in byname.items() if name.startswith(('SiteGround','CourtyardGarden','NorthTerrace','CourtPathEast')) and any(all(min(b[i+1],r[i+1])-max(b[i],r[i])>2e-5 for i in (0,2,4)) for r in occupied)]
rows.append(f'Terrain / occupied-volume intersections: {terrain_hits}; primary wing/link and insert interior boxes conservatively tested.')
(HERE/'public_routes_v04.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows),flush=True)
assert not failures and bearing and not terrain_hits
