"""Concept9 support completion after revised v06 joinery; earth omitted.

Existing concrete occupies integral ledger roots. New solids fit against it;
six buried weather-return intersections are fitted by the approved exception.
Reinforcement continuity and capacities are architectural inferences.
"""
from pathlib import Path
import math
import json
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]/'tools'))
from craftbot_lib import mesh_prism, prism_x
import geometry2d as g2
from planes import Frame, subtract, frame_prism


def build_supports():
    assert not any(o.name.startswith('PerimeterLedger') for o in bpy.data.objects)
    rectangles = []
    cells = {}
    nonrectangular = []

    def plan_cells(bounds):
        return [(x,y) for x in range(math.floor(bounds[0]/6), math.floor(bounds[1]/6)+1)
                for y in range(math.floor(bounds[2]/6), math.floor(bounds[3]/6)+1)]

    def register(bounds):
        number=len(rectangles)
        rectangles.append(bounds)
        for cell in plan_cells(bounds):
            cells.setdefault(cell,[]).append(number)

    def difference(bounds,cut):
        overlap=[max(bounds[i],cut[i]) if i%2==0 else min(bounds[i],cut[i]) for i in range(6)]
        if any(overlap[i+1]-overlap[i]<1e-5 for i in (0,2,4)):
            return [bounds]
        remaining=list(bounds);pieces=[]
        for axis in (0,2,4):
            if overlap[axis]>remaining[axis]+1e-5:
                piece=remaining.copy();piece[axis+1]=overlap[axis];pieces.append(tuple(piece))
            if overlap[axis+1]<remaining[axis+1]-1e-5:
                piece=remaining.copy();piece[axis]=overlap[axis+1];pieces.append(tuple(piece))
            remaining[axis:axis+2]=overlap[axis:axis+2]
        return pieces

    # Designer-approved exception: only buried weather-return concrete-seat
    # intersections are removed. Exposed return/skin geometry stays in place.
    closure_changes=[]
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.name.startswith(('SouthClosure_West','SouthClosure_East')):
            continue
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds=tuple(v for i in range(3) for v in (min(p[i] for p in points),max(p[i] for p in points)))
        pieces=[bounds]
        cuts=[]
        for floor in (10.8,14.4,18.):
            cut=(.30,53.70,.30,.50,floor-.45,floor-.25)
            if all(min(bounds[i+1],cut[i+1])-max(bounds[i],cut[i])>1e-5 for i in (0,2,4)):
                cuts.append(tuple(max(bounds[i],cut[i]) if i%2==0 else min(bounds[i],cut[i]) for i in range(6)))
                pieces=[p for old in pieces for p in difference(old,cut)]
        if not cuts:
            continue
        name=obj.name;collection=obj.users_collection[0]
        bpy.data.objects.remove(obj,do_unlink=True)
        for i,(xa,xb,ya,yb,za,zb) in enumerate(pieces):
            ring=[(xa,ya),(xb,ya),(xb,yb),(xa,yb)]
            mesh_prism(name if i==0 else f'{name}_LedgerFit{i}',collection,
                       [(x,y,za) for x,y in ring],[(x,y,zb) for x,y in ring])
        volume=sum((c[1]-c[0])*(c[3]-c[2])*(c[5]-c[4]) for c in cuts)
        closure_changes.append({'name':name,'before':bounds,'removed_bounds':cuts,
                                'removed_volume_m3':volume,'remaining_pieces':len(pieces)})

    for obj in bpy.data.objects:
        if obj.type!='MESH':
            continue
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        axes=[sorted(set(round(p[i],5) for p in points)) for i in range(3)]
        bounds=tuple(v for i in range(3) for v in (min(p[i] for p in points),max(p[i] for p in points)))
        if len(points)==8 and all(len(a)==2 for a in axes):
            register(bounds)
        else:
            normals=obj.matrix_world.to_3x3().inverted().transposed()
            planes=[(points[p.vertices[0]],-(normals@p.normal).normalized(),0.) for p in obj.data.polygons]
            nonrectangular.append((bounds,planes))

    def fitted(name,collection,*bounds):
        pieces=[bounds]
        candidates=sorted({i for cell in plan_cells(bounds) for i in cells.get(cell,())})
        for number in candidates:
            cut=rectangles[number]
            if any(min(bounds[i+1],cut[i+1])-max(bounds[i],cut[i])<1e-5 for i in (0,2,4)):
                continue
            pieces=[p for old in pieces for p in difference(old,cut)]
        for i,(xa,xb,ya,yb,za,zb) in enumerate(pieces):
            if name.startswith(('CourtLandingSupport','CourtLandingLedge','TerraceWall')):
                # Concept9.7: these solids meet XZ-profile corbel shoulders.
                # Split at their Y boundaries, then subtract actual vertical
                # profiles. Horizontal projection through the full Z depth
                # would wrongly remove wall below and seat concrete above.
                relevant=[(cut,planes) for cut,planes in nonrectangular
                          if all(min(v,w)-max(a,b)>1e-5 for a,v,b,w in
                                 ((xa,xb,cut[0],cut[1]),(ya,yb,cut[2],cut[3]),(za,zb,cut[4],cut[5])))]
                cuts=sorted({ya,yb,*[v for cut,_ in relevant for v in cut[2:4] if ya<v<yb]})
                frame=Frame((0,0,0),(1,0,0),(0,0,1))
                for band,(a,b) in enumerate(zip(cuts,cuts[1:])):
                    if b-a<1e-5:continue
                    polygons=[g2.rect(xa,xb,za,zb)]
                    for cut,planes in relevant:
                        if min(b,cut[3])-max(a,cut[2])<1e-5:continue
                        polygons=[p for old in polygons for p in subtract(frame,old,planes,-b,-a) if g2.area(p)>1e-8]
                    for part,poly in enumerate(polygons):
                        frame_prism(f'{name}_{i}_Slice{band}_{part}',collection,frame,poly,-b,-a)
                register((xa,xb,ya,yb,za,zb))
                continue
            ring=[(xa,ya),(xb,ya),(xb,yb),(xa,yb)]
            frame=Frame((0,0,0),(1,0,0),(0,1,0))
            polygons=[ring]
            for cut,planes in nonrectangular:
                if any(min(v,w)-max(a,b)<1e-5 for a,v,b,w in ((xa,xb,cut[0],cut[1]),(ya,yb,cut[2],cut[3]),(za,zb,cut[4],cut[5]))):
                    continue
                polygons=[p for old in polygons for p in subtract(frame,old,planes,za,zb) if g2.area(p)>1e-8]
            if polygons==[ring]:
                mesh_prism(f'{name}_{i}',collection,[(x,y,za) for x,y in ring],[(x,y,zb) for x,y in ring])
            else:
                for j,poly in enumerate(polygons):
                    frame_prism(f'{name}_{i}_Convex{j}',collection,frame,poly,za,zb)
            register((xa,xb,ya,yb,za,zb))
        return pieces

    # Root zones within the retained beam/shaft are removed from new volumes,
    # leaving positive-area construction joints and 200mm exposed slab seats.
    for side,levels,ya,yb in [('N',range(1,6),113.50,114.00),('S',range(3,6),0.,.50)]:
        for level in levels:
            top=3.6*level-.25
            fitted(f'PerimeterLedger_{side}_{level}','Structure/Beams',.30,53.70,ya,yb,top-.20,top)

    # Stair walking surfaces are retained. Twenty convex support pieces give
    # nineteen full horizontal seats and continuous vertical waist interfaces.
    for step in range(19):
        ya=89.70+.30*step;yb=89.70+.30*(step+1);top=.15*step
        parts=[('A',ya,89.90,-.35,-.35),('B',89.90,yb,-.25,-.20)] if step==0 else [('',ya,yb,.50*(ya-89.70)-.35,.50*(yb-89.70)-.35)]
        for suffix,a,b,za,zb in parts:
            prism_x(f'CourtWaist_{step+1:02d}{suffix}','SiteStairs',33.,35.45,
                    [(a,za),(b,zb),(b,top),(a,top)])
    fitted('CourtLandingSupport','SiteStairs',33.15,35.45,95.40,96.00,2.50,2.85)
    fitted('CourtLandingLedge','Insert/Retaining',33.15,35.45,95.80,96.20,2.30,2.50)
    fitted('CourtStairFooting','Foundation',32.85,35.60,89.50,90.10,-.75,-.35)

    # Closed retaining box: side walls butt the retained south wall; the north
    # wall stops 30mm before glazing. The existing paving cantilevers that gap.
    for label,rect in [('W',(18.55,18.85,96.30,107.20)),
                       ('E',(35.15,35.45,96.30,107.20)),
                       ('N',(18.55,35.45,106.90,107.20))]:
        fitted('TerraceWall_'+label,'Insert/Retaining',*rect,0.,2.75)
    for label,rect in [('W',(18.25,19.15,96.30,107.20)),
                       ('E',(34.85,35.75,96.30,107.20)),
                       ('N',(18.55,35.45,106.60,107.50))]:
        fitted('TerraceFooting_'+label,'Foundation',*rect,-.40,0.)
    # Earth, prepared subsoil and granular bases are an unmodeled boundary.
    bpy.context.view_layer.update()
    print('Added concept9 perimeter ledgers, stair waist/seats and retained terrace concrete.',flush=True)
    return closure_changes


if __name__=='__main__':
    CLOSURE_CHANGES=build_supports()
    bpy.context.scene['closure_changes_v06']=json.dumps(CLOSURE_CHANGES)
