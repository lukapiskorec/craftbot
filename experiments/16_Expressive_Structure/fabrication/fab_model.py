# Fabrication model of experiment 16, GPT-6 v02, regenerated for a stick model.
# Parametric copy of ../GPT-6/experiment_16_gpt6_v02.py: same room, frame spacing,
# column undulation and roof field; the two timber stocks are replaced by the
# real sizes of the model sticks (stick mm x SCALE). Writes members.json in
# model millimetres and runs the overlap and contact checks.
#
#   blender --background --python fab_model.py
import os
import sys
import json
import math
import bpy

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.normpath(os.path.join(_HERE, '..', '..', '..', 'tools'))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import craftbot_lib as craftbot
import geometry2d as g2
from check_overlaps import find_overlaps
from check_contacts import find_floating
from layers import classify
from mathutils import Vector

# PARAMETERS: model scale and the two Karapori sticks (mm, thickness x face).
SCALE = 15
SLAT_STICK = (3, 5)      # frame, webs, rails, ties, braces, mat
BOARD_STICK = (2, 10)    # floor, ceiling, walls, roof cover
# Frames kept, door end first. range(7) is the full model; range(4) is the
# half model cut at the fourth frame.
FRAMES = list(range(7))
# Floor and ceiling boards run the full room length as one stick instead of
# one 33 mm piece per bay.
CONTINUOUS_FLOOR = True

S, FACE = SLAT_STICK[0]*SCALE/1000, SLAT_STICK[1]*SCALE/1000
B, BOARD_W = BOARD_STICK[0]*SCALE/1000, BOARD_STICK[1]*SCALE/1000
STOCK = {'S': '%dx%d' % SLAT_STICK, 'B': '%dx%d' % BOARD_STICK}

ROOM_W, ROOM_H = 3.0, 6.0
HALF = ROOM_W/2
FRAME_Y = [-HALF + .5*j for j in FRAMES]
Y0, Y1 = FRAME_Y[0], FRAME_Y[-1]
BAYS = len(FRAME_Y)-1
COLUMN_Z = [-B, 1.5, 3., 4.5, ROOM_H+B]
# Wall build-up fixes the inner chord line: board, rail, half a chord face.
INNER_X = HALF + B + S + FACE/2
OUTER_X = INNER_X + .6
ROOF_X = [-OUTER_X, -INNER_X, -.8, 0., .8, INNER_X, OUTER_X]
ROOF_BOTTOM = ROOM_H + B + FACE/2
CLERESTORY, DOOR_W, DOOR_H = 5.25, .9, 2.1
MAT_X = OUTER_X + .1
# Mat overhang: two whole slats beside the end sleeper seat the door jambs.
MAT_Y0, MAT_Y1 = Y0 - 2.5*FACE, Y1 + 2.5*FACE
assert 2.5*FACE >= B + 2*S
PALE = (.72, .57, .37, 1)
RED = (.48, .085, .065, 1)

def column_depth(k, j):
    return .3 if k == 0 else (.6 if k == 4 else .3 + .3*math.sin(math.pi*k/4+math.pi*j/6)**2)

def roof_top(x, j):
    return 6.650 + .300*math.sin(math.pi*(x+OUTER_X)/(2*OUTER_X))**2 + .200*math.sin(2*math.pi*j/6)

def tagged(obj, stock='S', red=False):
    if obj is not None:
        obj['stock'] = STOCK[stock]
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
            # Fitted foot bevel: horizontal seat is exactly FACE wide.
            slope = (q[0]-p[0])/(q[1]-p[1])
            excess = FACE*(math.sqrt(1+slope*slope)-1)/2
            if excess > 1e-10:
                poly = g2.clip(poly, (p[0]-FACE/2, p[1]), (1, -slope+excess/FACE))
                poly = g2.clip(poly, (p[0]+FACE/2, p[1]), (-1, slope+excess/FACE))
        profile(f'{name}_{k:02d}', coll, poly, y0, y1)

craftbot.clear_scene()

# BASE: two crossed mat layers, sole runners integrated in the upper layer.
sole_x = [-(INNER_X+.3), -INNER_X, INNER_X, INNER_X+.3]
lower_x = [-OUTER_X, -(INNER_X+.3), -INNER_X, -1.2, -.8, -.4, 0., .4, .8, 1.2, INNER_X, INNER_X+.3, OUTER_X]
sole_holes = [(x-FACE/2, x+FACE/2) for x in sole_x]
for i, x in enumerate(lower_x):
    box(f'MatLower_{i:02d}', 'Ground/LowerSleepers', x-FACE/2, x+FACE/2, MAT_Y0, MAT_Y1, -B-2*S, -B-S)
for i, x in enumerate(sole_x):
    box(f'SoleRunner_{i:02d}', 'Ground/SoleRunners', x-FACE/2, x+FACE/2, MAT_Y0, MAT_Y1, -B-S, -B)
for j, y in enumerate(FRAME_Y):
    for k, (a, b) in enumerate(g2.split_range(-MAT_X, MAT_X, sole_holes)):
        box(f'MatUpper_{j:02d}_{k:02d}', 'Ground/UpperSleepers', a, b, y-FACE/2, y+FACE/2, -B-S, -B)
JAMB = DOOR_W/2 + FACE
for i in range(2):
    box(f'EntranceBaseSeat_{i}', 'Ground/UpperSleepers', -JAMB-FACE, JAMB+FACE, MAT_Y0+i*FACE, MAT_Y0+(i+1)*FACE, -B-S, -B)

# Floor/ceiling: close-laid boards.
board_runs = [(Y0, Y1)] if CONTINUOUS_FLOOR else list(zip(FRAME_Y, FRAME_Y[1:]))
for i, (a, b) in enumerate(g2.columns(-HALF, HALF, BOARD_W)):
    for j, (ya, yb) in enumerate(board_runs):
        box(f'FloorBoard_{i:02d}_{j:02d}', 'Floor', a, b, ya, yb, -B, 0, stock='B')
        box(f'CeilingBoard_{i:02d}_{j:02d}', 'Ceiling', a, b, ya, yb, ROOM_H, ROOM_H+B, stock='B')

# Paired exterior columns and the web-plane triangle system.
for j, y in enumerate(FRAME_Y):
    for side in (-1, 1):
        inner = [(side*INNER_X, z) for z in COLUMN_Z]
        outer = [(side*(INNER_X+column_depth(k, FRAMES[j])), z) for k, z in enumerate(COLUMN_Z)]
        for ply in (-1, 1):
            ya, yb = y+ply*S-S/2, y+ply*S+S/2
            cut_polyline(f'ColumnInner_{side}_{j:02d}_{ply}', 'Structure/ColumnChords', inner, ya, yb)
            cut_polyline(f'ColumnOuter_{side}_{j:02d}_{ply}', 'Structure/ColumnChords', outer, ya, yb)
        for k, z in enumerate(COLUMN_Z):
            # Rungs run to the far edges of both chords for a full glue lap.
            xa, xb = sorted((inner[k][0]-side*FACE/2, outer[k][0]+side*FACE/2))
            za, zb = max(-B, z-FACE/2), min(ROOM_H+B, z+FACE/2)
            box(f'ColumnRung_{side}_{j:02d}_{k}', 'Structure/ColumnWebs', xa, xb, y-S/2, y+S/2, za, zb, red=True)
        for k in range(4):
            p, q = (inner[k], outer[k+1]) if (k+FRAMES[j]) % 2 == 0 else (outer[k], inner[k+1])
            za, zb = COLUMN_Z[k]+FACE/2, COLUMN_Z[k+1]-FACE/2
            poly = strip_between(p, q, clips=[((0, za), (0, 1)), ((0, zb), (0, -1))])
            profile(f'ColumnDiagonal_{side}_{j:02d}_{k}', 'Structure/ColumnWebs', poly, y-S/2, y+S/2, red=True)
        # Straps on the outside faces of each paired chord splice.
        for k in (1, 2, 3):
            for chord, nodes in [('I', inner), ('O', outer)]:
                x, z = nodes[k]
                for ply in (-1, 1):
                    ya, yb = sorted((y+ply*1.5*S, y+ply*2.5*S))
                    box(f'ColumnStrap_{side}_{j:02d}_{chord}_{k}_{ply}', 'Structure/NodeStraps', x-FACE/2, x+FACE/2, ya, yb, z-2*FACE, z+2*FACE)

# ROOF: flat bottom chord on the column heads, upper chords bevelled to the roof field.
roof_facets = []
for j, y in enumerate(FRAME_Y):
    jj = FRAMES[j]
    for ply in (-1, 1):
        ya, yb = y+ply*S-S/2, y+ply*S+S/2
        # One continuous lower chord per ply: 4.5 m, a whole 300 mm stick.
        box(f'RoofLower_{j:02d}_{ply}', 'RoofStructure/LowerChords', -OUTER_X-FACE/2, OUTER_X+FACE/2, ya, yb, ROOM_H+B, ROOM_H+B+FACE)
        for k, (xa, xb) in enumerate(zip(ROOF_X, ROOF_X[1:])):
            a = xa-FACE/2 if k == 0 else xa
            b = xb+FACE/2 if k == 5 else xb
            sx = (roof_top(xb, jj)-roof_top(xa, jj))/(xb-xa)
            adjacent = max(FRAMES[0], min(FRAMES[-1]-1, jj if ply > 0 else jj-1))
            sy = (roof_top(xa, adjacent+1)-roof_top(xa, adjacent))/.5
            def top_at(x, yy): return roof_top(xa, jj)+sx*(x-xa)+FACE/2+sy*(yy-y)
            stock_top = max(top_at(xa, ya), top_at(xa, yb))
            bottom0 = stock_top-FACE*math.sqrt(1+sx*sx)
            lo = [(a, ya, bottom0+sx*(a-xa)), (b, ya, bottom0+sx*(b-xa)), (b, ya, top_at(b, ya)), (a, ya, top_at(a, ya))]
            hi = [(a, yb, bottom0+sx*(a-xa)), (b, yb, bottom0+sx*(b-xa)), (b, yb, top_at(b, yb)), (a, yb, top_at(a, yb))]
            # mesh_prism wants its first ring counter-clockwise seen from the second:
            # that is the yb ring seen from ya, so the rings go in as (hi, lo).
            tagged(craftbot.mesh_prism(f'RoofUpper_{j:02d}_{ply}_{k}', 'RoofStructure/UpperChords', hi, lo))
    for k, x in enumerate(ROOF_X):
        # Posts lap the full depth of both chords: from the underside of the
        # lower chord to just under the roof boards at the post's low corner.
        slope_x = max(abs(roof_top(b, jj)-roof_top(a, jj))/(b-a) for a, b in zip(ROOF_X, ROOF_X[1:]) if x in (a, b))
        slope_y = max(abs(roof_top(x, n+1)-roof_top(x, n))/.5 for n in (jj-1, jj) if FRAMES[0] <= n < FRAMES[-1])
        top = roof_top(x, jj)+FACE/2-slope_x*FACE/2-slope_y*S/2
        box(f'RoofPost_{j:02d}_{k}', 'RoofStructure/RoofWebs', x-FACE/2, x+FACE/2, y-S/2, y+S/2, ROOM_H+B, top, red=True)
    for k, (xa, xb) in enumerate(zip(ROOF_X, ROOF_X[1:])):
        p, q = ((xa, ROOF_BOTTOM), (xb, roof_top(xb, jj))) if (jj+k) % 2 == 0 else ((xa, roof_top(xa, jj)), (xb, ROOF_BOTTOM))
        poly = strip_between(p, q, clips=[((xa+FACE/2, 0), (1, 0)), ((xb-FACE/2, 0), (-1, 0)), ((0, ROOF_BOTTOM), (0, 1))])
        sx = (roof_top(xb, jj)-roof_top(xa, jj))/(xb-xa)
        poly = g2.clip(poly, (xa, roof_top(xa, jj)), (sx, -1))
        profile(f'RoofDiagonal_{j:02d}_{k}', 'RoofStructure/RoofWebs', poly, y-S/2, y+S/2, red=True)

# Full board roof, one planar facet per bay and truss panel.
for j, (ya, yb) in enumerate(zip(FRAME_Y, FRAME_Y[1:])):
    jj = FRAMES[j]
    y0 = ya-1.5*S if j == 0 else ya
    y1 = yb+1.5*S if j == BAYS-1 else yb
    for k, (xa, xb) in enumerate(zip(ROOF_X, ROOF_X[1:])):
        x0 = xa-FACE/2 if k == 0 else xa
        x1 = xb+FACE/2 if k == 5 else xb
        sx = (roof_top(xb, jj)-roof_top(xa, jj))/(xb-xa)
        sy = (roof_top(xa, jj+1)-roof_top(xa, jj))/(yb-ya)
        dz = B*math.sqrt(1+sx*sx+sy*sy)
        def surface(x, y): return roof_top(xa, jj)+FACE/2+sx*(x-xa)+sy*(y-ya)
        for i, (a, b) in enumerate(g2.columns(x0, x1, BOARD_W/math.sqrt(1+sx*sx), rip_min=.04)):
            lo = [(a, y0, surface(a, y0)), (b, y0, surface(b, y0)), (b, y1, surface(b, y1)), (a, y1, surface(a, y1))]
            hi = [(x, y, z+dz) for x, y, z in lo]
            tagged(craftbot.mesh_prism(f'RoofBoard_{j:02d}_{k}_{i:02d}', 'RoofCover', lo, hi), 'B')
        roof_facets.append((x0, x1, y0, y1, sx, sy))

# WALLS: side walls stop at the clerestory; end walls stay closed to the ceiling.
rail_z = sorted(set([0., .75, 1.5, 2.1, 2.25, 3., 3.75, 4.5, 5.25, 6.]))
WALL = HALF + B
for side in (-1, 1):
    xa, xb = sorted((side*WALL, side*(WALL+S)))
    for k, z in enumerate(rail_z):
        if z > CLERESTORY: continue
        za, zb = max(0, z-FACE/2), min(CLERESTORY, z+FACE/2)
        box(f'SideRail_{side}_{k:02d}', 'WallSupport/SideRails', xa, xb, Y0, Y1, za, zb, red=True)
    for i, (a, b) in enumerate(g2.columns(Y0, Y1, BOARD_W)):
        cuts = [0., 2.25, CLERESTORY] if i % 2 == 0 else [0., 1.5, 3.75, CLERESTORY]
        for k, (za, zb) in enumerate(zip(cuts, cuts[1:])):
            xa, xb = sorted((side*HALF, side*WALL))
            box(f'SideBoard_{side}_{i:02d}_{k}', 'Facade/SideBoards', xa, xb, a, b, za, zb, 'B', True)
# End walls: the door end always; the far end only when the last frame is kept.
ends = [(-1, Y0)] + ([(1, Y1)] if FRAMES[-1] == 6 else [])
for side, yw in ends:
    ya, yb = sorted((yw+side*B, yw+side*(B+S)))
    for k, z in enumerate(rail_z):
        za, zb = max(0, z-FACE/2), min(ROOM_H, z+FACE/2)
        holes = [(-JAMB, JAMB)] if side == -1 and za < DOOR_H+FACE else []
        for p, (a, b) in enumerate(g2.split_range(-(INNER_X-FACE/2), INNER_X-FACE/2, holes)):
            box(f'EndRail_{side}_{k:02d}_{p}', 'WallSupport/EndRails', a, b, ya, yb, za, zb, red=True)
    wall_runs = [(-WALL, -DOOR_W/2), (-DOOR_W/2, DOOR_W/2), (DOOR_W/2, WALL)] if side == -1 else [(-WALL, WALL)]
    for run, (ra, rb) in enumerate(wall_runs):
        for i, (a, b) in enumerate(g2.columns(ra, rb, BOARD_W)):
            bottom = DOOR_H if side == -1 and run == 1 else 0.
            cuts = [bottom]+[z for z in ([2.25, 5.25] if i % 2 == 0 else [1.5, 3.75]) if bottom < z < ROOM_H]+[ROOM_H]
            for k, (za, zb) in enumerate(zip(cuts, cuts[1:])):
                ya, yb = sorted((yw, yw+side*B))
                box(f'EndBoard_{side}_{run}_{i:02d}_{k}', 'Facade/EndBoards', a, b, ya, yb, za, zb, 'B', True)

# Doubled jambs carry a two-ply header.
for side in (-1, 1):
    xa, xb = sorted((side*DOOR_W/2, side*JAMB))
    for ply in range(2):
        ya, yb = Y0-B-(ply+1)*S, Y0-B-ply*S
        box(f'EntranceJamb_{side}_{ply}', 'Entrance', xa, xb, ya, yb, -B, DOOR_H)
for ply in range(2):
    ya, yb = Y0-B-(ply+1)*S, Y0-B-ply*S
    box(f'EntranceHeader_{ply}', 'Entrance', -JAMB, JAMB, ya, yb, DOOR_H, DOOR_H+FACE)

# Longitudinal ties at nodes, outside the inner chords; braces in both end bays.
for side in (-1, 1):
    xa, xb = sorted((side*(INNER_X+FACE/2), side*(INNER_X+FACE/2+S)))
    for k, z in enumerate(COLUMN_Z):
        za, zb = max(-B, z-FACE/2), min(ROOM_H+B, z+FACE/2)
        for segment, (ya, yb) in enumerate(g2.split_range(Y0-1.5*S, Y1+1.5*S, [(y-S/2, y+S/2) for y in FRAME_Y])):
            box(f'LongTie_{side}_{k}_{segment:02d}', 'Bracing/LongitudinalTies', xa, xb, ya, yb, za, zb)
    for j in sorted({0, BAYS-1}):
        ya, yb = FRAME_Y[j], FRAME_Y[j+1]
        for k, (za, zb) in enumerate(zip(COLUMN_Z, COLUMN_Z[1:])):
            p, q = ((ya, za), (yb, zb)) if k % 2 == 0 else ((yb, za), (ya, zb))
            poly = strip_between(p, q, clips=[((ya+S/2, 0), (1, 0)), ((yb-S/2, 0), (-1, 0)), ((0, za+FACE/2), (0, 1)), ((0, zb-FACE/2), (0, -1))])
            tagged(craftbot.prism_x(f'LongBrace_{side}_{j}_{k}', 'Bracing/LongitudinalDiagonals', xa, xb, poly), red=True)

# Roof-plan braces: each crossed pair in its own S layer between the frames.
for j, (ya, yb) in enumerate(zip(FRAME_Y, FRAME_Y[1:])):
    a, b = ya+1.5*S, yb-1.5*S
    for diagonal in (0, 1):
        p, q = ((-INNER_X, a), (INNER_X, b)) if diagonal == 0 else ((INNER_X, a), (-INNER_X, b))
        poly = g2.clip_rect(g2.strip(p, q, FACE, ext=.5), -INNER_X, INNER_X, a, b)
        z0 = ROOM_H+B+diagonal*S
        tagged(craftbot.prism(f'RoofPlanBrace_{j}_{diagonal}', 'Bracing/RoofPlan', (0, 0, 0), (1, 0, 0), (0, 1, 0), poly, z0, z0+S), red=True)

# Ground plan diagonals fitted into the two crossed mat layers.
for diagonal in (0, 1):
    p, q = ((-INNER_X, Y0), (INNER_X, Y1)) if diagonal == 0 else ((INNER_X, Y0), (-INNER_X, Y1))
    poly = g2.strip(p, q, FACE, ext=.5)
    xholes = [(x-FACE/2, x+FACE/2) for x in (lower_x if diagonal == 0 else sole_x)]
    xruns = g2.split_range(-INNER_X, INNER_X, xholes)
    yruns = [(Y0, Y1)] if diagonal == 0 else g2.split_range(Y0, Y1, [(y-FACE/2, y+FACE/2) for y in FRAME_Y])
    for i, (xa, xb) in enumerate(xruns):
        for j, (ya, yb) in enumerate(yruns):
            piece = g2.clip_rect(poly, xa, xb, ya, yb)
            if len(piece) > 2 and g2.area(piece) > 1e-8:
                z0 = -B-2*S+diagonal*S
                tagged(craftbot.prism(f'GroundPlanBrace_{diagonal}_{i}_{j}', 'Bracing/GroundPlan', (0, 0, 0), (1, 0, 0), (0, 1, 0), piece, z0, z0+S), red=True)

# CHECKS
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
def bounds_enter(obj, lower, upper):
    vertices = [obj.matrix_world@Vector(v) for v in obj.bound_box]
    return all(min(max(v[i] for v in vertices), upper[i])-max(min(v[i] for v in vertices), lower[i]) > 1e-6 for i in range(3))
for obj in meshes:
    assert not bounds_enter(obj, (-HALF, Y0, 0), (HALF, Y1, ROOM_H)), ('clear room', obj.name)
    assert not bounds_enter(obj, (-DOOR_W/2, MAT_Y0, 0), (DOOR_W/2, Y0, DOOR_H)), ('clear entrance', obj.name)
overlaps = find_overlaps(tol=0.001)
floating = find_floating(tol=0.002)
print(f'FAB MODEL 1:{SCALE}: {len(meshes)} members, {len(overlaps)} overlapping pairs (> 1 mm real), {len(floating)} floating.')
for depth, a, b in sorted(overlaps, reverse=True)[:30]:
    print(f'  OVERLAP {depth*1000:7.1f} mm  {a}  {b}')
for name in list(floating)[:30]:
    print(f'  FLOATING {name}')

# The drawings cull back faces, so every face normal must point outwards.
for o in meshes:
    centre = sum((v.co for v in o.data.vertices), Vector())/len(o.data.vertices)
    for face in o.data.polygons:
        assert face.normal.dot(face.center-centre) > 0, ('face wound inwards', o.name)

# EXPORT: world meshes in model millimetres.
k = 1000/SCALE
parent = {c.name: p for p in bpy.data.collections for c in p.children}
def group_path(c):
    return (group_path(parent[c.name])+'/' if c.name in parent else '')+c.name
members = []
for o in meshes:
    M = o.matrix_world
    members.append({
        'name': o.name,
        'group': group_path(o.users_collection[0]),
        'layer': classify('16', group_path(o.users_collection[0]), o.name),
        'stock': o['stock'],
        'red': abs(o.color[0]-RED[0]) < 1e-4,
        'verts': [[round(c*k, 4) for c in (M@v.co)] for v in o.data.vertices],
        'faces': [list(p.vertices) for p in o.data.polygons],
    })
with open(os.path.join(_HERE, 'members.json'), 'w') as f:
    json.dump({'scale': SCALE, 'stick_length': 300, 'frames': FRAMES,
               'frame_y': [round(y*k, 4) for y in FRAME_Y], 'members': members}, f)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(_HERE, 'fab_model.blend'))
print('Wrote members.json and fab_model.blend')
