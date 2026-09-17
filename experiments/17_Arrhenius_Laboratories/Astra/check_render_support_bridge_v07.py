"""Recheck actual tread seats after harmless render-matrix float32 roundoff."""
from pathlib import Path
import json
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
identity=runpy.run_path(str(HERE/'snapshot_v07.py'))['identity']()

bridge=json.loads((HERE/'render_identity_difference_v07.json').read_text())[0]
changed=[c for c in bridge['changes'] if c['max_axis_delta_m']>0]
assert len(changed)<=100
assert max(c['max_axis_delta_m'] for c in changed)<4e-6
assert all(c['name'].startswith(('CourtStair_','CourtStairHandrail_','InsertInclineRail_','SouthInclineRail_')) for c in changed)
assert all(c['local_unchanged'] for c in bridge['changes'])
def area(poly):return g2.area(poly) if len(poly)>2 else 0.
def subtract(poly,clip):
    pieces=[]
    for a,b in zip(clip,clip[1:]+clip[:1]):
        normal=(a[1]-b[1],b[0]-a[0])
        outside=g2.clip(poly,a,(-normal[0],-normal[1]))
        if area(outside)>1e-10:pieces.append(outside)
        poly=g2.clip(poly,a,normal)
        if len(poly)<3:break
    return pieces
def horizontal(obj,sign):
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    found=[]
    for face in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized()
        if normal.z*sign<.99999:continue
        points=[verts[i] for i in face.vertices]
        z=sum(v.z for v in points)/len(points)
        assert max(abs(v.z-z) for v in points)<1e-5
        poly=[(v.x,v.y) for v in points]
        if g2.signed_area(poly)<0:poly.reverse()
        found.append((z,poly))
    return found
supports=[(o.name,z,poly) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CourtWaist') for z,poly in horizontal(o,1)]
lines=[identity,
       f"Measured render bridge: {len(bridge['changes'])} transform changes; {len(changed)} world-coordinate changes; maximum {bridge['max_axis_delta_m']}m.",
       'All local meshes unchanged. Every primary support world vertex is unchanged; changed families limited by assertions to court treads and inclined glazing rails.',
       'Actual rendered tread underside unions below use existing20-micrometre float32 seam allowance.']
count=0
for obj in sorted((o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CourtStair_')),key=lambda o:o.name):
    feet=horizontal(obj,-1);assert len(feet)==1
    for z,poly in feet:
        remainder=[poly];names=[]
        for name,height,seat in supports:
            if abs(z-height)>2e-5:continue
            prior=sum(area(p) for p in remainder)
            remainder=[q for p in remainder for q in subtract(p,seat)]
            if prior-sum(area(p) for p in remainder)>1e-8:names.append(name)
        missing=sum(area(p) for p in remainder)
        tolerance=2e-5*sum(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5 for a,b in zip(poly,poly[1:]+poly[:1]))
        assert missing<=tolerance,(obj.name,missing,tolerance)
        lines.append(f'{obj.name}: required{area(poly):.12f}m2; uncovered{missing:.12f}m2; tolerance{tolerance:.12f}m2; seats{names}; PASS')
        count+=1
assert count==19
lines+=['19/19 actual final rendered tread underside unions PASS. Existing public/route margins use20-micrometre geometric seam allowances; affected tread drift is below0.24micrometre, other changed rails below3.82micrometres. No physical route or support change.','Standard gate is recorded separately in render_v07.log and the saved pair/contact reports; this bridge does not rerun it.']
(HERE/'render_support_bridge_v07.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines),flush=True)
