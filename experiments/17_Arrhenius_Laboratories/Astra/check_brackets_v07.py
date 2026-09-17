"""Actual finite steel/concrete interfaces and slab bands for concept10."""
from pathlib import Path
import json
import runpy
import sys
import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
import geometry2d as g2

TOL = 2e-5
faces = []
for obj in bpy.data.objects:
    if obj.type != 'MESH' or not obj.name.startswith(('FloorSlab_', 'Panel_CourtSouth_', 'Beam_', 'GradeBeam_', 'CourtFacadeBracket_')):
        continue
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    for face in obj.data.polygons:
        normal = (obj.matrix_world.to_3x3().inverted().transposed() @ face.normal).normalized()
        axis = max(range(3), key=lambda i: abs(normal[i]))
        if abs(normal[axis]) < .99999:
            continue
        ps = [points[i] for i in face.vertices]
        dims = [i for i in range(3) if i != axis]
        poly = [(p[dims[0]], p[dims[1]]) for p in ps]
        if g2.signed_area(poly) < 0:
            poly.reverse()
        faces.append((obj.name, axis, 1 if normal[axis] > 0 else -1, sum(p[axis] for p in ps) / len(ps), poly))

def area(poly):
    return g2.area(poly) if len(poly) > 2 else 0.

def subtract(poly, cutter):
    outside = []
    for a, b in zip(cutter, cutter[1:] + cutter[:1]):
        n = (a[1] - b[1], b[0] - a[0])
        piece = g2.clip(poly, a, (-n[0], -n[1]))
        if area(piece) > 1e-12:
            outside.append(piece)
        poly = g2.clip(poly, a, n)
        if len(poly) < 3:
            break
    return outside

def cover(prefix, axis, sign, plane, target):
    remainder = [target]
    patches = []
    for name, ax, sg, d, poly in faces:
        if not name.startswith(prefix) or ax != axis or sg != sign or abs(plane - d) > TOL:
            continue
        prior = sum(area(p) for p in remainder)
        remainder = [q for p in remainder for q in subtract(p, poly)]
        covered = prior - sum(area(p) for p in remainder)
        if covered > 1e-10:
            patches.append({'name': name, 'area_m2': covered})
    missing = sum(area(p) for p in remainder)
    perimeter = sum(((a[0]-b[0])**2 + (a[1]-b[1])**2)**.5 for a,b in zip(target,target[1:]+target[:1]))
    assert missing <= TOL * perimeter, (prefix, plane, target, missing)
    assert patches, (prefix, target)
    return {'required_m2': area(target), 'uncovered_m2': missing, 'contacts': patches}

def opposed(a, b, plane, target):
    return {'positive_face': cover(a, 1, 1, plane, target), 'negative_face': cover(b, 1, -1, plane, target)}

centres = {1:(21.20,22.70),2:(24.20,25.70),3:(27.60,28.60),4:(30.20,31.70),5:(33.20,34.70)}
rows = []
for bay, xx in centres.items():
    for f in range(6):
        level = 3.6 * f
        panel = f'Panel_CourtSouth_{bay}_' + ('Base' if f == 0 else str(f-1))
        rz = (-.15,0.) if f == 0 else (level-.20,level-.10)
        pz = (0.,.15) if f == 0 else rz
        for side, x in enumerate(xx):
            prefix = f'CourtFacadeBracket_{bay}_{f}_{side}_'
            root, web, receiver = (prefix + role for role in ('Root','Web','Receiver'))
            assert all(bpy.data.objects.get(n) is not None for n in (root,web,receiver))
            slab = f'FloorSlab_{f}_'
            piece_bounds = {}
            for name in (root,web,receiver):
                ps=[bpy.data.objects[name].matrix_world@v.co for v in bpy.data.objects[name].data.vertices]
                bb=tuple(value for axis in range(3) for value in (min(p[axis] for p in ps),max(p[axis] for p in ps)))
                piece_bounds[name]={'bounds_m':bb,'dimensions_m':[bb[2*i+1]-bb[2*i] for i in range(3)]}
                assert bb[2]>=12.30-TOL and bb[3]<=12.55+TOL
                assert bb[5] <= (.15 if f==0 else level-.10)+TOL
            row = {'panel':panel,'bracket':prefix,'level':level,'x':x,'actual_piece_dimensions':piece_bounds,
                   'slab_root':opposed(slab,root,12.30,g2.rect(x-.05,x+.05,*rz)),
                   'root_web':opposed(root,web,12.31,g2.rect(x-.005,x+.005,*rz)),
                   'web_receiver':opposed(web,receiver,12.54,g2.rect(x-.005,x+.005,*pz)),
                   'receiver_panel':opposed(receiver,panel,12.55,g2.rect(x-.05,x+.05,*pz)),
                   'continuous_slab_strip':cover(slab,2,-1,level-.25,g2.rect(x-.05,x+.05,12.,12.30)),
                   'slab_bearing_band':cover(slab,2,-1,level-.25,g2.rect(x-.05,x+.05,12.,12.20)),
                   'beam_bearing_band':cover('GradeBeam_' if f==0 else f'Beam_{f}_',2,1,level-.25,g2.rect(x-.05,x+.05,12.,12.20))}
            rows.append(row)
assert len(rows) == 60
report = {'identity':runpy.run_path(str(HERE/'snapshot_v07.py'))['identity'](),
          'connections':rows,'connection_count':60,'steel_mesh_count':180,
          'rule':'Opposed actual finite face unions, 20 micrometre coordinate allowance. Slab underside continuous across actual root-to-beam strip; actual 200 mm support band. Glass excluded. Anchors, welds, capacities and local slab design remain inferred.'}
(HERE/'brackets_v07.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['identity'],flush=True)
print('BRACKETS: 60/60 roots, receivers, two welded interfaces, continuous slab strips and actual 200 mm Beam/GradeBeam bands PASS',flush=True)
