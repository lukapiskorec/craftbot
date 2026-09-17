"""Read-only candidate contact intervals for Designer; generates no members."""
from pathlib import Path
import runpy,sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
identity=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
faces=[]
for obj in bpy.data.objects:
    if obj.type!='MESH' or not obj.name.startswith(('FloorSlab_','Panel_CourtSouth_','Beam_','GradeBeam_')):continue
    ps=[obj.matrix_world@v.co for v in obj.data.vertices]
    for face in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized()
        axis=max(range(3),key=lambda i:abs(normal[i]))
        if abs(normal[axis])<.99999:continue
        coords=[ps[i] for i in face.vertices];plane=sum(p[axis] for p in coords)/len(coords)
        dims=[i for i in range(3) if i!=axis];poly=[(p[dims[0]],p[dims[1]]) for p in coords]
        if g2.signed_area(poly)<0:poly.reverse()
        faces.append((obj.name,axis,1 if normal[axis]>0 else -1,plane,poly))
def area(poly):return g2.area(poly) if len(poly)>2 else 0.
def intersect(poly,clip):
    for a,b in zip(clip,clip[1:]+clip[:1]):
        poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        if len(poly)<3:return []
    return poly
def measure(prefix,axis,sign,plane,target):
    patches=[]
    for name,ax,sg,d,poly in faces:
        if name.startswith(prefix) and ax==axis and sg==sign and abs(plane-d)<2e-5:
            covered=area(intersect(target,poly))
            if covered>1e-7:patches.append((name,covered))
    return patches,sum(a for _,a in patches)
rows=[identity,'PROPOSAL CONTACT PROBE ONLY. No geometry created; thickness/material/detail require Designer approval.']
centres={1:(21.20,22.70),2:(24.20,25.70),3:(27.60,28.60),4:(30.20,31.70),5:(33.20,34.70)}
count=0
for bay,xx in centres.items():
    for f in range(6):
        level=3.6*f;panel=f'Panel_CourtSouth_{bay}_'+('Base' if f==0 else str(f-1))
        for x in xx:
            if f==0:bottom,top=-.15,.15;root=(-.15,0.);receive=(0.,.15)
            else:bottom,top=level-.20,level-.10;root=receive=(bottom,top)
            slab=measure(f'FloorSlab_{f}_',1,1,12.30,g2.rect(x-.05,x+.05,*root))
            end=measure(panel,1,-1,12.55,g2.rect(x-.05,x+.05,*receive))
            support=measure('GradeBeam_' if f==0 else f'Beam_{f}_',2,1,level-.25,g2.rect(x-.05,x+.05,12.,12.20))
            assert slab[1]>=.1*(root[1]-root[0])-2e-6,(panel,x,'slab',slab)
            assert end[1]>=.1*(receive[1]-receive[0])-2e-6,(panel,x,'panel',end)
            assert support[1]>=.02-2e-6,(panel,x,'support',support)
            rows.append(repr({'panel':panel,'material':'precast concrete per concept; Facade/PrecastPanels collection',
                             'candidate_bounds':(x-.05,x+.05,12.30,12.55,bottom,top),
                             'slab_root':slab,'panel_receiver':end,'slab_band_to_real_beam':support}))
            count+=1
rows.append(f'{count} candidate connections have complete nominal side interfaces and200mm real Beam/GradeBeam band. Upper members stay below walking floor; ground candidates stop atZ.15 in unoccupied court strip. Anchor/shear/bending capacity unverified. No shape chosen or approved.')
(HERE/'facade_connector_candidates_v06.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join([rows[0],rows[-1]]),flush=True)
