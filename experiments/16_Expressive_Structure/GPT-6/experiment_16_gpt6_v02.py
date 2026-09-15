# CRAFT BOT experiment 16, GPT-6 v02. Derived from immutable v01.
# All dimensions: concept.md fixed geometry; derived cuts are labelled below.
import os
import sys
import math
import bpy

_HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
for _d in (os.path.join(_HERE, '..', '..', '..', 'tools'), os.path.join(_HERE, '..', 'tools'), _HERE):
    _d = os.path.normpath(_d)
    if os.path.isfile(os.path.join(_d, 'craftbot_lib.py')) and _d not in sys.path:
        sys.path.insert(0, _d)

import craftbot_lib as craftbot
import geometry2d as g2
import planes
import framing
from mathutils import Vector

# PARAMETERS: catalogue and fixed profiles from the released concept.
ROOM_W, ROOM_H = 3.0, 6.0
B, S, FACE = .024, .036, .090
FRAME_Y = [-1.5 + .5*j for j in range(7)]
COLUMN_Z = [-B, 1.5, 3., 4.5, ROOM_H+B]
ROOF_X = [-2.2, -1.6, -.8, 0., .8, 1.6, 2.2]
INNER_X, ROOF_BOTTOM = 1.6, 6.069
CLERESTORY, DOOR_W, DOOR_H = 5.25, .9, 2.1
MAT_X, MAT_Y = 2.3, 1.61
CHORD_OFF = S
PALE = (.72, .57, .37, 1)
RED = (.48, .085, .065, 1)

def column_depth(k, j):
    return .3 if k == 0 else (.6 if k == 4 else .3 + .3*math.sin(math.pi*k/4+math.pi*j/6)**2)

def roof_top(x, j):
    return 6.650 + .300*math.sin(math.pi*(x+2.2)/4.4)**2 + .200*math.sin(2*math.pi*j/6)

def tagged(obj, stock='S', red=False):
    if obj is not None:
        obj['stock'] = stock
        obj['material'] = 'timber'
        obj.color = RED if red else PALE
    return obj

def box(name, coll, x0, x1, y0, y1, z0, z1, stock='S', red=False):
    assert min(x1-x0, y1-y0, z1-z0) > 1e-7, name
    return tagged(craftbot.box(name, coll, x0, x1, y0, y1, z0, z1), stock, red)

def profile(name, coll, poly, y0, y1, red=False):
    if len(poly) >= 3 and g2.area(poly) > 1e-9:
        return tagged(craftbot.prism_y(name, coll, y0, y1, poly), red=red)

def strip_between(p, q, width=FACE, clips=()):
    poly = g2.strip(p, q, width, ext=.5)
    for point, normal in clips:
        poly = g2.clip(poly, point, normal)
    return poly

def cut_polyline(name, coll, nodes, y0, y1):
    # Complementary bisectors at every polygonal chord joint.
    for k, (p, q) in enumerate(zip(nodes, nodes[1:])):
        d = (Vector(q)-Vector(p)).normalized()
        n0 = d if k == 0 else (d+(Vector(p)-Vector(nodes[k-1])).normalized()).normalized()
        n1 = -d if k == len(nodes)-2 else -(d+(Vector(nodes[k+2])-Vector(q)).normalized()).normalized()
        # Feet/head are horizontal bearing planes, independently of chord angle.
        if k == 0: n0 = Vector((0., 1.))
        if k == len(nodes)-2: n1 = Vector((0., -1.))
        poly = strip_between(p, q, clips=[(p, n0), (q, n1)])
        if k == 0:
            # Derived fitted foot bevel: horizontal seat is exactly FACE wide.
            # Two cuts remove only the projecting tips; they meet the original
            # stock edges FACE above the seat and leave the rest of the chord.
            slope = (q[0]-p[0])/(q[1]-p[1])
            excess = FACE*(math.sqrt(1+slope*slope)-1)/2
            if excess > 1e-10:
                poly = g2.clip(poly, (p[0]-FACE/2, p[1]), (1, -slope+excess/FACE))
                poly = g2.clip(poly, (p[0]+FACE/2, p[1]), (-1, slope+excess/FACE))
        profile(f'{name}_{k:02d}', coll, poly, y0, y1)

craftbot.clear_scene()

# BASE: approved integrated sole strips in the upper mat layer.
sole_x = [-1.9, -1.6, 1.6, 1.9]
lower_x = [-2.2, -1.9, -1.6, -1.2, -.8, -.4, 0., .4, .8, 1.2, 1.6, 1.9, 2.2]
sole_holes = [(x-FACE/2, x+FACE/2) for x in sole_x]
for i, x in enumerate(lower_x):
    box(f'MatLower_{i:02d}', 'Ground/LowerSleepers', x-FACE/2, x+FACE/2, -MAT_Y, MAT_Y, -.096, -.060)
for i, x in enumerate(sole_x):
    box(f'SoleRunner_{i:02d}', 'Ground/SoleRunners', x-FACE/2, x+FACE/2, -MAT_Y, MAT_Y, -.060, -B)
for j, y in enumerate(FRAME_Y):
    for k, (a,b) in enumerate(g2.split_range(-MAT_X, MAT_X, sole_holes)):
        box(f'MatUpper_{j:02d}_{k:02d}', 'Ground/UpperSleepers', a,b,y-FACE/2,y+FACE/2,-.060,-B)
# Adjacent ripped edge slat gives both doorway jamb plies a base seat.
box('EntranceBaseSeat', 'Ground/UpperSleepers', -.63,.63,-MAT_Y,-1.545,-.060,-B)

# Floor/ceiling: close-laid 90 mm boards, all ends on the frame stations.
for i,(a,b) in enumerate(g2.columns(-1.5,1.5,FACE)):
    for j,(ya,yb) in enumerate(zip(FRAME_Y,FRAME_Y[1:])):
        box(f'FloorBoard_{i:02d}_{j:02d}', 'Floor', a,b,ya,yb,-B,0,stock='B')
        box(f'CeilingBoard_{i:02d}_{j:02d}', 'Ceiling', a,b,ya,yb,ROOM_H,ROOM_H+B,stock='B')

# Paired exterior columns and the web-plane triangle system.
for j,y in enumerate(FRAME_Y):
    for side in (-1,1):
        inner = [(side*INNER_X,z) for z in COLUMN_Z]
        outer = [(side*(INNER_X+column_depth(k,j)),z) for k,z in enumerate(COLUMN_Z)]
        for ply in (-1,1):
            ya,yb = y+ply*S-S/2,y+ply*S+S/2
            cut_polyline(f'ColumnInner_{side}_{j:02d}_{ply}', 'Structure/ColumnChords', inner,ya,yb)
            cut_polyline(f'ColumnOuter_{side}_{j:02d}_{ply}', 'Structure/ColumnChords', outer,ya,yb)
        for k,z in enumerate(COLUMN_Z):
            xa,xb=sorted((inner[k][0],outer[k][0]))
            za,zb=max(-B,z-FACE/2),min(ROOM_H+B,z+FACE/2)
            box(f'ColumnRung_{side}_{j:02d}_{k}', 'Structure/ColumnWebs',xa,xb,y-S/2,y+S/2,za,zb,red=True)
        for k in range(4):
            p,q = (inner[k],outer[k+1]) if (k+j)%2 == 0 else (outer[k],inner[k+1])
            za,zb=COLUMN_Z[k]+FACE/2,COLUMN_Z[k+1]-FACE/2
            poly=strip_between(p,q,clips=[((0,za),(0,1)),((0,zb),(0,-1))])
            # Both ends meet the rung; side faces lap the paired chords.
            profile(f'ColumnDiagonal_{side}_{j:02d}_{k}', 'Structure/ColumnWebs',poly,y-S/2,y+S/2,red=True)
        # Supported 360 mm straps on the outside faces of each paired chord splice.
        for k in (1,2,3):
            for chord,nodes in [('I',inner),('O',outer)]:
                x,z=nodes[k]
                for ply in (-1,1):
                    ya,yb=sorted((y+ply*.054,y+ply*.090))
                    box(f'ColumnStrap_{side}_{j:02d}_{chord}_{k}_{ply}','Structure/NodeStraps',x-FACE/2,x+FACE/2,ya,yb,z-.18,z+.18)

# ROOF: flat bottom chord directly on four aligned column-head seats per rib.
# Upper chord bearing faces bevel to the additive piecewise planar roof field.
roof_facets=[]
for j,y in enumerate(FRAME_Y):
    for ply in (-1,1):
        ya,yb=y+ply*S-S/2,y+ply*S+S/2
        for k,(xa,xb) in enumerate(zip(ROOF_X,ROOF_X[1:])):
            a=xa-FACE/2 if k==0 else xa
            b=xb+FACE/2 if k==5 else xb
            box(f'RoofLower_{j:02d}_{ply}_{k}', 'RoofStructure/LowerChords',a,b,ya,yb,ROOM_H+B,ROOM_H+B+FACE)
            sx=(roof_top(xb,j)-roof_top(xa,j))/(xb-xa)
            adjacent=max(0,min(5,j if ply>0 else j-1))
            sy=(roof_top(xa,adjacent+1)-roof_top(xa,adjacent))/.5
            def top_at(x,yy): return roof_top(xa,j)+sx*(x-xa)+FACE/2+sy*(yy-y)
            # Bevel only the top of a full S blank; no face exceeds S stock.
            stock_top=max(top_at(xa,ya),top_at(xa,yb))
            bottom0=stock_top-FACE*math.sqrt(1+sx*sx)
            lo=[(a,ya,bottom0+sx*(a-xa)),(b,ya,bottom0+sx*(b-xa)),(b,ya,top_at(b,ya)),(a,ya,top_at(a,ya))]
            hi=[(a,yb,bottom0+sx*(a-xa)),(b,yb,bottom0+sx*(b-xa)),(b,yb,top_at(b,yb)),(a,yb,top_at(a,yb))]
            tagged(craftbot.mesh_prism(f'RoofUpper_{j:02d}_{ply}_{k}','RoofStructure/UpperChords',lo,hi))
    for k,x in enumerate(ROOF_X):
        box(f'RoofPost_{j:02d}_{k}','RoofStructure/RoofWebs',x-FACE/2,x+FACE/2,y-S/2,y+S/2,ROOF_BOTTOM,roof_top(x,j),red=True)
    for k,(xa,xb) in enumerate(zip(ROOF_X,ROOF_X[1:])):
        p,q=((xa,ROOF_BOTTOM),(xb,roof_top(xb,j))) if (j+k)%2==0 else ((xa,roof_top(xa,j)),(xb,ROOF_BOTTOM))
        poly=strip_between(p,q,clips=[((xa+FACE/2,0),(1,0)),((xb-FACE/2,0),(-1,0)),((0,ROOF_BOTTOM),(0,1))])
        # The web ends at the common upper centreline, below roof bearing faces.
        sx=(roof_top(xb,j)-roof_top(xa,j))/(xb-xa)
        poly=g2.clip(poly,(xa,roof_top(xa,j)),(sx,-1))
        profile(f'RoofDiagonal_{j:02d}_{k}','RoofStructure/RoofWebs',poly,y-S/2,y+S/2,red=True)

# Full slat roof. Vertical facet seams are complementary and have no open area.
for j,(ya,yb) in enumerate(zip(FRAME_Y,FRAME_Y[1:])):
    y0=ya-.054 if j==0 else ya
    y1=yb+.054 if j==5 else yb
    for k,(xa,xb) in enumerate(zip(ROOF_X,ROOF_X[1:])):
        x0=xa-.045 if k==0 else xa
        x1=xb+.045 if k==5 else xb
        sx=(roof_top(xb,j)-roof_top(xa,j))/(xb-xa)
        sy=(roof_top(xa,j+1)-roof_top(xa,j))/(yb-ya)
        dz=B*math.sqrt(1+sx*sx+sy*sy)
        def surface(x,y): return roof_top(xa,j)+FACE/2+sx*(x-xa)+sy*(y-ya)
        # Derived projected width: real cross-board face is never wider than90 mm.
        for i,(a,b) in enumerate(g2.columns(x0,x1,FACE/math.sqrt(1+sx*sx),rip_min=.02)):
            lo=[(a,y0,surface(a,y0)),(b,y0,surface(b,y0)),(b,y1,surface(b,y1)),(a,y1,surface(a,y1))]
            hi=[(x,y,z+dz) for x,y,z in lo]
            tagged(craftbot.mesh_prism(f'RoofBoard_{j:02d}_{k}_{i:02d}','RoofCover',lo,hi),'B')
        roof_facets.append((x0,x1,y0,y1,sx,sy))

# WALLS: side walls stop at5.25; end walls stay closed to the ceiling.
rail_z=sorted(set([0.,.75,1.5,2.1,2.25,3.,3.75,4.5,5.25,6.]))
for side in (-1,1):
    # Side battens are S ripped to31 mm to close the specified face gap.
    xa,xb=sorted((side*1.524,side*1.555))
    for k,z in enumerate(rail_z):
        if z>CLERESTORY: continue
        za,zb=max(0,z-FACE/2),min(CLERESTORY,z+FACE/2)
        box(f'SideRail_{side}_{k:02d}','WallSupport/SideRails',xa,xb,-1.5,1.5,za,zb,red=True)
    for i,(a,b) in enumerate(g2.columns(-1.5,1.5,FACE)):
        cuts=[0.,2.25,CLERESTORY] if i%2==0 else [0.,1.5,3.75,CLERESTORY]
        for k,(za,zb) in enumerate(zip(cuts,cuts[1:])):
            xa,xb=sorted((side*1.5,side*1.524))
            box(f'SideBoard_{side}_{i:02d}_{k}','Facade/SideBoards',xa,xb,a,b,za,zb,'B',True)
    # End rails end at the inner chord faces, whose plies carry their reactions.
    ya,yb=sorted((side*1.524,side*1.560))
    for k,z in enumerate(rail_z):
        za,zb=max(0,z-FACE/2),min(ROOM_H,z+FACE/2)
        holes=[(-.54,.54)] if side==-1 and za<DOOR_H+.09 else []
        for p,(a,b) in enumerate(g2.split_range(-1.555,1.555,holes)):
            box(f'EndRail_{side}_{k:02d}_{p}','WallSupport/EndRails',a,b,ya,yb,za,zb,red=True)
    # Board columns are explicitly split at doorway edges, not partly across them.
    wall_runs=[(-1.524,-.45),(-.45,.45),(.45,1.524)] if side==-1 else [(-1.524,1.524)]
    for run,(ra,rb) in enumerate(wall_runs):
        for i,(a,b) in enumerate(g2.columns(ra,rb,FACE)):
            bottom=DOOR_H if side==-1 and run==1 else 0.
            cuts=[bottom]+[z for z in ([2.25,5.25] if i%2==0 else [1.5,3.75]) if bottom<z<ROOM_H]+[ROOM_H]
            for k,(za,zb) in enumerate(zip(cuts,cuts[1:])):
                assert zb-za<=3.000001
                ya,yb=sorted((side*1.5,side*1.524))
                box(f'EndBoard_{side}_{run}_{i:02d}_{k}','Facade/EndBoards',a,b,ya,yb,za,zb,'B',True)

# Doubled jambs carry a two-ply header with90 mm end seats.
for side in (-1,1):
    xa,xb=sorted((side*.45,side*.54))
    for ply in range(2):
        ya,yb=-1.524-(ply+1)*S,-1.524-ply*S
        box(f'EntranceJamb_{side}_{ply}','Entrance',xa,xb,ya,yb,-B,DOOR_H)
for ply in range(2):
    ya,yb=-1.524-(ply+1)*S,-1.524-ply*S
    box(f'EntranceHeader_{ply}','Entrance',-.54,.54,ya,yb,DOOR_H,DOOR_H+FACE)

# Longitudinal ties at nodes, outside inner chords; braces in both end bays.
# Their x thickness layers face-fix to chords, never occupy the room.
for side in (-1,1):
    xa,xb=sorted((side*1.645,side*1.681))
    for k,z in enumerate(COLUMN_Z):
        za,zb=max(-B,z-FACE/2),min(ROOM_H+B,z+FACE/2)
        # Fit ties between web faces; column rungs complete their continuous line.
        for segment,(ya,yb) in enumerate(g2.split_range(-1.554,1.554,[(y-S/2,y+S/2) for y in FRAME_Y])):
            box(f'LongTie_{side}_{k}_{segment:02d}','Bracing/LongitudinalTies',xa,xb,ya,yb,za,zb)
    for j in (0,5):
        ya,yb=FRAME_Y[j],FRAME_Y[j+1]
        for k,(za,zb) in enumerate(zip(COLUMN_Z,COLUMN_Z[1:])):
            p,q=((ya,za),(yb,zb)) if k%2==0 else ((yb,za),(ya,zb))
            poly=strip_between(p,q,clips=[((ya+S/2,0),(1,0)),((yb-S/2,0),(-1,0)),((0,za+FACE/2),(0,1)),((0,zb-FACE/2),(0,-1))])
            tagged(craftbot.prism_x(f'LongBrace_{side}_{j}_{k}','Bracing/LongitudinalDiagonals',xa,xb,poly),red=True)

# Roof-plan shear collectors: each crossed pair occupies separate36 mm layers,
# face-fixed between the paired lower chords at each500 mm frame bay.
for j,(ya,yb) in enumerate(zip(FRAME_Y,FRAME_Y[1:])):
    a,b=ya+.054,yb-.054
    for diagonal in (0,1):
        p,q=((-1.6,a),(1.6,b)) if diagonal==0 else ((1.6,a),(-1.6,b))
        poly=g2.clip_rect(g2.strip(p,q,FACE,ext=.5),-1.6,1.6,a,b)
        z0=ROOM_H+B+.018+diagonal*S
        tagged(craftbot.prism(f'RoofPlanBrace_{j}_{diagonal}','Bracing/RoofPlan',(0,0,0),(1,0,0),(0,1,0),poly,z0,z0+S),red=True)

# Ground plan diagonals fitted into the two crossed mat layers. They share
# end faces with the sleeper network; concealed connections transfer shear.
for diagonal in (0,1):
    p,q=((-1.6,-1.5),(1.6,1.5)) if diagonal==0 else ((1.6,-1.5),(-1.6,1.5))
    poly=g2.strip(p,q,FACE,ext=.5)
    xholes=[(x-.045,x+.045) for x in (lower_x if diagonal==0 else sole_x)]
    xruns=g2.split_range(-1.6,1.6,xholes)
    yruns=[(-1.5,1.5)] if diagonal==0 else g2.split_range(-1.5,1.5,[(y-.045,y+.045) for y in FRAME_Y])
    for i,(xa,xb) in enumerate(xruns):
        for j,(ya,yb) in enumerate(yruns):
            piece=g2.clip_rect(poly,xa,xb,ya,yb)
            if len(piece)>2 and g2.area(piece)>1e-8:
                z0=-.096+diagonal*S
                tagged(craftbot.prism(f'GroundPlanBrace_{diagonal}_{i}_{j}','Bracing/GroundPlan',(0,0,0),(1,0,0),(0,1,0),piece,z0,z0+S),red=True)

# Numerically expressible brief checks. No performance certification implied.
assert ROOM_W == 3 and ROOM_H/ROOM_W == 2
assert len(FRAME_Y)==7 and all(abs(b-a-.5)<1e-9 for a,b in zip(FRAME_Y,FRAME_Y[1:]))
assert DOOR_W==.9 and DOOR_H==2.1 and CLERESTORY==5.25
assert abs(ROOF_BOTTOM-FACE/2-(ROOM_H+B))<1e-9
assert all(.3-1e-9<=column_depth(k,j)<=.6+1e-9 for k in range(5) for j in range(7))
assert all(o.get('stock') in ('B','S') and o.get('material')=='timber' for o in bpy.data.objects if o.type=='MESH')
# R01/02/03: the complete member bounds leave the clear room and entry empty.
def bounds_enter(obj, lower, upper):
    vertices=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return all(min(max(v[i] for v in vertices),upper[i])-max(min(v[i] for v in vertices),lower[i])>1e-6 for i in range(3))
for obj in (o for o in bpy.data.objects if o.type=='MESH'):
    assert not bounds_enter(obj,(-1.5,-1.5,0),(1.5,1.5,6)), ('clear room',obj.name)
    assert not bounds_enter(obj,(-.45,-MAT_Y,0),(.45,-1.5,DOOR_H)), ('clear entrance',obj.name)
# R04/07/08/14/15/16/17/18/19/20/21: assembly dimension chains.
assert len(roof_facets)==36
assert all(b-a<=.500001 for a,b in zip(FRAME_Y,FRAME_Y[1:]))
assert all(any(abs(x-foot)<1e-9 for x in lower_x) for foot in sole_x)
# R16: inspect every actual convex foot face, not merely support centerlines.
# One micrometre accommodates Blender mesh precision, not missing bearing.
bearing_tol = 1e-6
foot_widths = []
for obj in bpy.data.objects:
    if not (obj.name.startswith(('ColumnInner_', 'ColumnOuter_')) and obj.name.endswith('_00')):
        continue
    foot = [obj.matrix_world@v.co for v in obj.data.vertices
            if abs((obj.matrix_world@v.co).z+B) <= bearing_tol]
    assert len(foot) == 4, ('rectangular bearing face', obj.name)
    center_x = sum(v.x for v in foot)/len(foot)
    seat_x = min(sole_x, key=lambda x: abs(x-center_x))
    sole = bpy.data.objects[f'SoleRunner_{sole_x.index(seat_x):02d}']
    lower = bpy.data.objects[f'MatLower_{lower_x.index(seat_x):02d}']
    for support, top in ((sole, -B), (lower, -.060)):
        corners = [support.matrix_world@v.co for v in support.data.vertices]
        assert abs(max(v.z for v in corners)-top) <= bearing_tol
        assert all(min(v[axis] for v in corners)-bearing_tol <= point[axis]
                   <= max(v[axis] for v in corners)+bearing_tol
                   for point in foot for axis in (0, 1)), ('full foot bearing', obj.name, support.name)
    foot_widths.append(max(v.x for v in foot)-min(v.x for v in foot))
    assert abs(foot_widths[-1]-FACE) <= bearing_tol, ('full 90 mm seat', obj.name)
assert len(foot_widths) == 7*2*2*2
print(f'FOOT BEARING: {len(foot_widths)} full faces, widths {min(foot_widths)*1000:.3f}..{max(foot_widths)*1000:.3f} mm; sole and lower support contained.')
assert all(abs(abs(ROOF_X[k])-2.2)<1e-9 for k in (0,6))
assert abs(.54-.45-FACE)<1e-9
assert max(b-a for a,b in zip(rail_z,rail_z[1:]))<=.750001
assert all(o.name.startswith('SideBoard') is False or max((o.matrix_world@Vector(v)).z for v in o.bound_box)<=CLERESTORY+1e-6 for o in bpy.data.objects if o.type=='MESH')
MEMBER_COUNT=sum(o.type=='MESH' for o in bpy.data.objects)
print(f'Built Experiment16 GPT-6 v02: {MEMBER_COUNT} members; clear room3x3x6 m; 7 frames; 36 roof facets.')
print('CONNECTION BASIS: ceiling face-fixed to lower chords; all slat joints require concealed engineered fixings.')
print('LIMITS: stock is a geometric proposal; capacity, fasteners, anchorage, weatherproofing and soil/moisture design unverified.')
