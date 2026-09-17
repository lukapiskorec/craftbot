"""Arrhenius Laboratories, Astra v03. Architectural estimates: concept.md §§2–4.
Started from tools/experiment_template.py. Axes: x east, y north, z up.
Concrete sizes are plausible visual estimates, not engineered sections.
"""
import os
import sys
import math
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, '..', '..', '..', 'tools')))
import craftbot_lib as craftbot
import geometry2d as g2
import framing
from craftbot_lib import box, prism_x, prism_y, mesh_prism
from planes import member, bar, Frame, subtract, frame_prism
from ruled import Ruled, surface_quad, ruling_member, quad_frame

# All metric values are estimates carried by concept.md. Subdivisions below
# are derived from these modules; small tolerances are labelled fabrication.
LONG_BAY, N_LONG, CROSS_BAY, N_CROSS = 6., 19, 9., 6
L, W, STOREY, N_FLOORS = LONG_BAY*N_LONG, CROSS_BAY*N_CROSS, 3.6, 5
SLAB, SHAFT, BEAM_W, BEAM_D = .25, .60, .40, .65
CORBEL_W, CORBEL_D, CORBEL_H = 1.30, 1.00, .60
RECESS, PANEL, FRAME, FRAME_DEPTH, GLASS = .55, .22, .065, .10, .018
PARAPET, COLUMN_TOP, PANEL_MODULE, PANEL_GAP = 18.45, 18.6, 3., .02
CORE_WALL, PARTITION, DOOR_W, DOOR_H = .25, .10, 1.2, 2.4
STAIRS = [('W',3.65,61.),('E',50.35,61.),('N',32.4,110.30),('S',40.2,9.20)]
# Centres selected on inward/service side; solid core width remains 3x4.5m.
CORES = [('W',3.8,66.30),('E',50.2,66.30),('N',27.10,111.35),('S',45.3,8.5)]
STAIR_R, STAIR_INNER, N_RISERS = 2.7, 1.1, 22
STAIR_DIRECTION = {'W':0., 'E':0., 'N':0., 'S':180.}
FLIGHT_ANGLE = math.pi
SITE = (-18.,72.,-24.,132.)
def z_floor(i): return STOREY*i
def front_y(z): return 6.-(z-3.)*5.25/5. if 3.<=z<=8. else (.55 if z>8. else 6.)
ROOF_Z = z_floor(N_FLOORS)
assert (N_LONG,N_CROSS,N_FLOORS)==(19,6,5)
assert abs(front_y(8.)-.75)<1e-8 and abs(front_y(3.)-6.)<1e-8
assert abs(N_RISERS*(STOREY/N_RISERS)-STOREY)<1e-8
assert W==54 and L==114 and ROOF_Z==18
assert STAIRS[0][1]-(STAIR_R+.02)-(.55+PANEL)>=.15-1e-8
assert (W-.55-PANEL)-(STAIRS[1][1]+STAIR_R+.02)>=.15-1e-8
assert (L-.55-PANEL)-(STAIRS[2][2]+STAIR_R+.02)>=.15-1e-8
assert STAIRS[3][2]-.9-.02-6.15>=.15-1e-8
assert CORES[0][2]-2.375-(STAIRS[0][2]+STAIR_R+.02)>=.15-1e-8

craftbot.clear_scene()
def B(name,coll,*bounds):
    if any(bounds[i+1]-bounds[i]<1e-6 for i in (0,2,4)): return None
    x0,x1,y0,y1,z0,z1=bounds
    corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    return mesh_prism(name,coll,[(x,y,z0) for x,y in corners],[(x,y,z1) for x,y in corners])

column_centres=[(x,float(y)) for x in (0.,9.,18.,36.,45.,54.) for y in range(0,115,6)]
column_centres += [(27.,float(y)) for y in (0,6,12,108,114)]
column_holes=[(x-SHAFT/2,x+SHAFT/2,y-SHAFT/2,y+SHAFT/2) for x,y in column_centres]
stair_holes=[(x-2.75,x+2.75,y-1.4 if label!='S' else y-2.75,y+2.75 if label!='S' else y+1.4) for label,x,y in STAIRS]
gallery_holes=[(x-2.75,x+2.75,y-1.4 if label!='S' else y,y if label!='S' else y+1.4) for label,x,y in STAIRS]
access_holes=[(17.55,18.70,74.,76.)]
def core_bounds(label,x,y):
    hx,hy=(2.375,1.625) if label=='N' else (1.625,2.375)
    return x-hx,x+hx,y-hy,y+hy
core_holes=[core_bounds(label,x,y) for label,x,y in CORES]

def clipped_holes(rect,holes):
    x0,x1,y0,y1=rect
    return [(max(x0,a),min(x1,b),max(y0,c),min(y1,d)) for a,b,c,d in holes
            if min(x1,b)>max(x0,a) and min(y1,d)>max(y0,c)]

def circular_cuts(outline,circles,semicircle=False):
    """Convex floor/beam pieces outside polygonal circular apertures."""
    pieces=[outline];fr=Frame((0,0,0),(1,0,0),(0,1,0))
    for cx,cy,radius in circles:
        phase=180. if any(label=='S' and abs(cx-x)<1e-6 and abs(cy-y)<1e-6 for label,x,y in STAIRS) else 0.
        vertices=[(cx+radius*math.cos(math.radians(phase+k*5)),cy+radius*math.sin(math.radians(phase+k*5))) for k in range(37 if semicircle else 72)]
        cuts=[]
        for k,(x,y) in enumerate(vertices):
            nx,ny=vertices[(k+1)%len(vertices)];cuts.append((Vector((x,y,0)),Vector((y-ny,nx-x,0)).normalized(),0.))
        remaining=[]
        for poly in pieces:
            xa,xb=min(p[0] for p in poly),max(p[0] for p in poly)
            ya,yb=min(p[1] for p in poly),max(p[1] for p in poly)
            if xb<=cx-radius or xa>=cx+radius or yb<=cy-radius or ya>=cy+radius:
                remaining.append(poly)
            else: remaining.extend(piece for piece in subtract(fr,poly,cuts) if g2.area(piece)>1e-8)
        pieces=remaining
    return pieces

def cut_box(name,coll,x0,x1,y0,y1,z0,z1,holes,circles=()):
    holes=clipped_holes((x0,x1,y0,y1),holes)
    for i,(a,b,c,d) in enumerate(g2.tile(x0,x1,y0,y1,x1-x0,y1-y0,holes,False)):
        for j,poly in enumerate(circular_cuts(g2.rect(a,b,c,d),circles)):
            mesh_prism(f'{name}_{i}_{j}',coll,[(x,y,z0) for x,y in poly],[(x,y,z1) for x,y in poly])

def slab_zone(name,coll,rect,z,holes,circles=()):
    a,b,c,d=rect
    # Panel ends land on the beam axes, including sawn first/last strips.
    # Starting every zone's six-metre tiling at its facade inset would put
    # the next unit's end beyond the supporting beam.
    support_axes=[6.*k for k in range(20)]
    if abs(z-STOREY)<1e-6: support_axes[1]=6.35  # south beam seats behind the recessed glazing
    for row,(ya,yb) in enumerate(g2.strips(c,d,support_axes)):
        band=(a,b,ya,yb)
        for cell,(xa,xb,yc,yd) in enumerate(g2.tile(a,b,ya,yb,1.5,6.,clipped_holes(band,holes),False)):
            for j,poly in enumerate(circular_cuts(g2.rect(xa,xb,yc,yd),circles,True)):
                mesh_prism(f'{name}_Row{row}_{cell}_{j}',coll,[(x,y,z-SLAB) for x,y in poly],[(x,y,z) for x,y in poly])

# Foundations form the independent roots of the load paths. Site surfaces
# are split outside the ring so soil never intersects occupied rooms.
for i,(x,y) in enumerate(column_centres):
    B(f'FootingPad_{i}','Foundation',x-.9,x+.9,y-.9,y+.9,-1.25,-.60)
    B(f'Pedestal_{i}','Foundation',x-.3,x+.3,y-.3,y+.3,-.60,-SLAB)
for name,xc,yc in CORES:
    a,b,c,d=core_bounds(name,xc,yc)
    B(f'CoreFooting_{name}','Foundation',a-.375,b+.375,c-.375,d+.375,-1.25,-.8)
    B(f'CoreFoundation_{name}','Foundation',a,b,c,d,-.8,-SLAB)
for iy,y in enumerate(range(0,115,6)):
    spans=[(0.,18.),(36.,54.)] if 12<y<108 else [(0.,54.)]
    for j,(a,b) in enumerate(spans):
        cut_box(f'GradeBeam_{iy}_{j}','Foundation',a,b,y-.2,y+.2,-.60,-SLAB,column_holes+core_holes)
for name,r,z in [('South',(-18,72,-24,-.9),-.15),('West',(-18,-.9,-.9,132),-.15),('East',(54.9,72,-.9,132),-.15),('North',(-.9,54.9,114.9,132),1.5)]:
    B('SiteGround_'+name,'Site',*r,-.35,z)
B('CourtyardGarden','Site',18.55,35.45,12.55,65.8,-.3,-.1)
B('CourtPathEast','Site',33.,35.45,65.8,89.7,-.25,0.)
B('NorthTerrace','Site',18.55,35.45,96.3,107.23,2.75,3.)

# Continuous concrete shafts; slabs and beams are cut around shafts.
for i,(x,y) in enumerate(column_centres):
    B(f'Column_{i}','Structure/Columns',x-.3,x+.3,y-.3,y+.3,-SLAB,COLUMN_TOP)
    for f in range(1,6):
        top=z_floor(f)-SLAB-BEAM_D
        # Four convex shoulder pieces touch the shaft without double volume.
        for sign in (-1,1):
            ya,yb=sorted((y+sign*.3,y+sign*CORBEL_W/2))
            pts=[(ya,top-CORBEL_H*.45),(yb,top-CORBEL_H),(yb,top),(ya,top)] if sign<0 else [(ya,top-CORBEL_H),(yb,top-CORBEL_H*.45),(yb,top),(ya,top)]
            prism_x(f'CorbelWing_{i}_{f}_{sign}','Structure/Corbels',x-CORBEL_D/2,x+CORBEL_D/2,pts)
            xa,xb=sorted((x+sign*.3,x+sign*CORBEL_D/2))
            B(f'CorbelSeat_{i}_{f}_{sign}','Structure/Corbels',xa,xb,y-.3,y+.3,top-CORBEL_H,top)

# Transverse beams on every station; opening edge beams close load paths.
all_holes=column_holes+stair_holes+core_holes
for f in range(1,6):
    z=z_floor(f)
    for iy,y in enumerate(range(0,115,6)):
        beam_y=6.35 if f==1 and y==6 else y
        spans=[(0.,18.),(36.,54.)] if 12<y<108 else [(0.,54.)]
        for s,(a,b) in enumerate(spans):
            if y < front_y(z-SLAB) and z<8: continue
            cut_box(f'Beam_{f}_{iy}_{s}','Structure/Beams',a,b,beam_y-.2,beam_y+.2,z-SLAB-BEAM_D,z-SLAB,column_holes+core_holes,[(x,y,2.85) for _,x,y in STAIRS] if f<5 else [])
    if f<5:
        # North rim also connects to the y114 transverse beam; other rims
        # meet the retained y60 (W/E) or y6.35/y12 (S) beam branches directly.
        cut_box(f'StairHeader_N_{f}','Structure/Beams',32.2,32.6,110.3,113.8,z-SLAB-BEAM_D,z-SLAB,column_holes+core_holes,[(32.4,110.3,2.85)])
    # Facade ledgers carry panel leaves and tie the slab perimeter to shafts.
    for j,x in enumerate((.30,17.70,36.30,53.70)):
        transverse_cuts=[(-1.,55.,(6.35 if f==1 and yy==6 else yy)-.2,(6.35 if f==1 and yy==6 else yy)+.2) for yy in range(0,115,6)]
        cut_box(f'EdgeBeam_{f}_{j}','Structure/Beams',x-.20,x+.20,max(.3,front_y(z-SLAB)),113.7,z-SLAB-BEAM_D,z-SLAB,column_holes+core_holes+transverse_cuts,[(sx,sy,2.85) for _,sx,sy in STAIRS] if f<5 else [])

for f in range(6):
    z=z_floor(f)
    south=.30 if f==0 or z>=8 else front_y(z-SLAB)+.12
    ring=[(.3,17.70,south,113.70),(36.30,53.70,south,113.70),(17.70,36.30,south,12.30),(17.70,36.30,107.70,113.70)]
    for i,r in enumerate(ring):
        slab_zone(f'FloorSlab_{f}_{i}','Roof/RoofSlabs' if f==5 else 'Floors',r,z,column_holes+core_holes+(gallery_holes if 0<f<5 else [])+(access_holes if f<3 else []),[(x,y,2.75) for _,x,y in STAIRS] if 0<f<5 else [])

# Four service cores: wall-centre rectangles 3x4.5m, doorway toward corridor.
for name,x,y in CORES:
    a,b,c,d=core_bounds(name,x,y)
    for f in range(5):
        z=z_floor(f)
        B(f'CoreWall_{name}_{f}_W','Structure/Cores',a,a+.25,c,d,z, z+STOREY)
        B(f'CoreWall_{name}_{f}_E','Structure/Cores',b-.25,b,c,d,z, z+STOREY)
        B(f'CoreWall_{name}_{f}_N','Structure/Cores',a+.25,b-.25,d-.25,d,z,z+STOREY)
        framing.wall_along_x(f'CoreWall_{name}_{f}_S','Structure/Cores',[(a+.25,z),(b-.25,z),(b-.25,z+STOREY),(a+.25,z+STOREY)],c,c+.25,[(x-.6,x+.6,z,z+DOOR_H)])
    # Service shafts are capped at the common roof plane, with an explicit
    # integral wall ledge; the ground cap bears on the core foundation.
    B(f'CoreGroundSlab_{name}','Floors',a+.25,b-.25,c+.25,d-.25,-SLAB,0.)
    B(f'CoreRoofSlab_{name}','Roof/RoofSlabs',a+.25,b-.25,c+.25,d-.25,ROOF_Z-SLAB,ROOF_Z)
    for j,r in enumerate(((a+.25,a+.45,c+.25,d-.25),(b-.45,b-.25,c+.25,d-.25),
                           (a+.45,b-.45,c+.25,c+.45),(a+.45,b-.45,d-.45,d-.25))):
        B(f'CoreRoofLedge_{name}_{j}','Structure/Cores',*r,ROOF_Z-SLAB-.25,ROOF_Z-SLAB)

def window(name,along,a,b,depth,z0,z1,narrow=True):
    """One half-bay unit, glass bounded by butt-jointed timber members."""
    maker=framing.rect_fn('Facade/TimberFrames',along,depth,depth+FRAME_DEPTH)
    maker(name+'_Sill',a,b,z0,z0+FRAME)
    maker(name+'_Head',a,b,z1-FRAME,z1)
    for n,u in enumerate((a,b-FRAME)):
        maker(name+f'_Jamb{n}',u,u+FRAME,z0+FRAME,z1-FRAME)
    cuts=[a+FRAME,b-FRAME]
    if narrow:
        u=b-.65
        maker(name+'_OperableMullion',u-FRAME/2,u+FRAME/2,z0+FRAME,z1-FRAME)
        panes=[(a+FRAME,u-FRAME/2),(u+FRAME/2,b-FRAME)]
    else: panes=[tuple(cuts)]
    glass_maker=framing.rect_fn('Facade/Glass',along,depth+(FRAME_DEPTH-GLASS)/2,depth+(FRAME_DEPTH+GLASS)/2)
    for i,(u,v) in enumerate(panes): glass_maker(name+f'_Glass{i}',u,v,z0+FRAME,z1-FRAME)

def typical_facade(name,along,a,b,depth):
    maker=framing.rect_fn('Facade/PrecastPanels',along,depth,depth+PANEL)
    for k,(u,v) in enumerate(g2.columns(a,b,PANEL_MODULE)):
        u+=PANEL_GAP/2;v-=PANEL_GAP/2
        maker(f'Panel_{name}_{k}_Base',u,v,0,.45)
        for f in range(5):
            z=z_floor(f); sill=z+(.45 if f==0 else 1.10); head=z+3.05
            window(f'Window_{name}_{k}_{f}',along,u,v,depth,sill,head)
            top=z_floor(f+1)+(1.10 if f<4 else .45)
            maker(f'Panel_{name}_{k}_{f}',u,v,head,min(top,PARAPET))

for name,x,ya,yb in [('West',.55,.55,113.45),('East',53.23,.55,113.45),('CourtWest',17.23,12.55,107.45),('CourtEast',36.55,12.55,107.45)]:
    typical_facade(name,'y',ya,yb,x)
typical_facade('North','x',.55,53.45,113.23)
typical_facade('CourtNorth','x',17.45,36.55,107.23)
typical_facade('CourtSouth','x',17.45,36.55,12.55)

# Public south front, deliberately independent of the typical spandrel kit.
# Metal strips are visible raised standing seams at the specified 450mm pitch.
B('SouthFasciaBacking','Facade/SouthMetal',.55,53.45,.53,.75,12.6,18.)
for i in range(118):
    x=.55+i*.45
    B(f'SouthFasciaSeam_{i}','Facade/SouthMetal',x,min(x+.018,53.45),.50,.53,12.6,18.)
B('SouthFasciaLip','Facade/SouthMetal',.55,53.45,.33,.75,12.5,12.6)
for i,(a,b) in enumerate(g2.columns(.55,53.45,3.)):
    window(f'SouthRibbon_{i}','x',a,b,.75,9.6,12.5,False)
    window(f'SouthFineStrip_{i}','x',a,b,.75,8.06,8.45,False)
    window(f'SouthGround_{i}','x',a,b,6.,0.,3.,False)
B('SouthVentBacking','Facade/SouthMetal',.55,53.45,.75,.97,8.45,9.6)
for i in range(3): B(f'SouthVentLine_{i}','Facade/SteelFrames',.77,53.23,.71,.75,8.65+i*.30,8.69+i*.30)
SOUTH=Ruled((.55,.75,8.),(53.45,.75,8.),(.55,6.,3.),(53.45,6.,3.),out=(0,-1,-1))
slant_len=math.hypot(5.25,5.)
front_beam_cuts=[]
for obj in bpy.data.objects:
    if not obj.name.startswith('EdgeBeam_'): continue
    points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    bounds=tuple(value for axis in range(3) for value in (min(p[axis] for p in points),max(p[axis] for p in points)))
    if bounds[4]>=8. or bounds[5]<=3.: continue
    planes=[(points[face.vertices[0]],-(obj.matrix_world.to_3x3() @ face.normal).normalized(),0.) for face in obj.data.polygons]
    front_beam_cuts.append((bounds,planes))
for i,(a,b) in enumerate(g2.columns(.55,53.45,1.5)):
    column_cut=[]
    for cx in range(0,55,9):
        if a<cx+.3 and b>cx-.3:
            column_cut=[(Vector((cx-.3,0,0)),Vector((1,0,0)),0),
                        (Vector((cx+.3,0,0)),Vector((-1,0,0)),0),
                        (Vector((0,5.7,0)),Vector((0,1,0)),0),
                        (Vector((0,6.3,0)),Vector((0,-1,0)),0)]
    for j,(c,d) in enumerate(((0.,.5),(.5,1.))):
        name=f'SouthInclineGlass_{i}_{j}'
        fr,outline=quad_frame(SOUTH,(a-.55+FRAME/2)/52.9,(b-.55-FRAME/2)/52.9,c+FRAME/(2*slant_len),d-FRAME/(2*slant_len),name)
        outline=fr.clip(fr.clip(outline,(.77,0,0),(1,0,0)),(53.23,0,0),(-1,0,0))
        pieces=subtract(fr,outline,column_cut,0.,GLASS) if column_cut else [outline]
        for bounds,planes in front_beam_cuts:
            if bounds[1]<=a or bounds[0]>=b: continue
            pieces=[piece for poly in pieces for piece in subtract(fr,poly,planes,0.,GLASS) if g2.area(piece)>1e-8]
        for k,poly in enumerate(pieces): frame_prism(f'{name}_{k}','Facade/Glass',fr,poly,0.,GLASS)
for i,x in enumerate([.55+1.5*k for k in range(36)]+[53.45]):
    t=min(1.,(x-.55)/52.9)
    for segment,(u0,u1) in enumerate(((0.,.5),(.5,1.))):
        margin=FRAME/(2*slant_len)
        member(f'SouthInclineRafter_{i}_{segment}','Facade/SteelFrames',SOUTH.P(t,u0+margin),SOUTH.P(t,u1-margin),FRAME,.10,(1,0,0))
for j,u in enumerate((0.,.5,1.)):
    notches=[(cx-.3,cx+.3) for cx in range(0,55,9)]
    if u==1.:
        notches += [(bounds[0],bounds[1]) for bounds,_ in front_beam_cuts if bounds[2]<6.05 and bounds[3]>5.95 and bounds[4]<3.05 and bounds[5]>2.95]
    merged=[]
    for lo,hi in sorted(notches):
        if merged and lo<=merged[-1][1]: merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
        else: merged.append((lo,hi))
    intervals=g2.split_range(.55,53.45,merged) if u==1. else [(.55,53.45)]
    for segment,(a,b) in enumerate(intervals):
        member(f'SouthInclineRail_{j}_{segment}','Facade/SteelFrames',SOUTH.P((a-.55)/52.9,u),SOUTH.P((b-.55)/52.9,u),FRAME,.10,(0,5.25,-5))
# The central door replaces the middle lower-glass unit with a clear framed pair.
# Door leaves are visually subdivided within the glazed wall, opening into foyer.
for i,x in enumerate((25.8,27.,28.2)):
    B(f'EntranceDoorJamb_{i}','Entrance',x-.0325,x+.0325,5.90,6.,0.,2.4)
B('EntranceDoorHead','Entrance',25.8,28.2,5.90,6.,2.4,2.465)

# Asymmetric room partitions; service/stair openings are cut consistently.
def partition(name,along,a,b,c,z,doors=(),door_width=1.2):
    openings=[d if isinstance(d,tuple) else (d,door_width) for d in doors]
    cuts=[]
    for ha,hb,hc,hd in stair_holes+core_holes+column_holes:
        if along=='x' and hc<c+.1 and hd>c: cuts.append((ha,hb))
        if along=='y' and ha<c+.1 and hb>c: cuts.append((hc,hd))
    merged=[]
    for lo,hi in sorted(cuts):
        if merged and lo<=merged[-1][1]: merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
        else: merged.append((lo,hi))
    for i,(lo,hi) in enumerate(g2.split_range(a,b,merged)):
        holes=[(max(lo,d-width/2),min(hi,d+width/2),z,z+2.4) for d,width in openings if d+width/2>lo and d-width/2<hi]
        pts=[(lo,z),(hi,z),(hi,z+3.35),(lo,z+3.35)]
        if along=='x': framing.wall_along_x(f'{name}_{i}','Interior/Partitions',pts,c,c+.1,holes)
        else: framing.wall_along_y(f'{name}_{i}','Interior/Partitions',pts,c,c+.1,holes)
for f in range(5):
    z=z_floor(f)
    for x,jog in ((6.1,6.5),(9.2,9.6),(44.7,44.3),(47.8,47.4)):
        if x==6.1:
            room_edges=[12.8,*range(15,108,3),107.1]
        elif x==47.8:
            room_edges=[12.8,*[y for k,y in enumerate(range(15,108,3)) if k%3!=1],107.1]
        elif x==9.2:
            room_edges=[12.8,*[y for k,y in enumerate(range(18,108,6)) if k%3!=1],107.1]
        else:
            room_edges=[12.8,*range(18,108,6),107.1]
        room_doors=[]
        for a,b in zip(room_edges,room_edges[1:]):
            if b-a<1.2:continue
            centre=(a+b)/2
            # A12m lab midpoint lies on a main column; its first6m-bay
            # midpoint provides the same room with a usable doorway.
            if x==9.2 and abs(centre/6-round(centre/6))*6<.9:centre-=3.
            assert a+.60<=centre<=b-.60
            room_doors.append(centre)
        for j,(ya,yb,xx) in enumerate(((12.8,57.8,x),(57.8,64.1,jog),(64.1,107.1,x))):
            if x==44.7 and j==0:ya=13.95
            # Fixed inward landing route: 1.40m opening gives 0.10m each
            # side beyond the concept's 1.20m usable route.
            doors=[61.0 if x==44.7 else 60.3] if j==1 else room_doors
            if x==9.2 and f<2:doors=[(d,1.4) if abs(d-75.)<.001 else d for d in doors]
            partition(f'CorridorWall_{f}_{x}_{j}','y',ya,yb,xx,z,doors,1.4 if j==1 else 1.2)
        for j,y in enumerate((57.8,64.0)):
            partition(f'CorridorJog_{f}_{x}_{j}','x',min(x,jog),max(x,jog)+.1,y,z)
    if f==0: partition('EastGalleryWall','y',12.8,107.1,39.8,z,[*range(15,57,6),61.0,*range(69,108,6)],1.4)
    for k,y in enumerate(range(15,108,3)):
        partition(f'OfficeWest_{f}_{k}','x',.77,6.1,y,z)
        if k%3 !=1: partition(f'OfficeEast_{f}_{k}','x',47.9,53.23,y,z)
    for k,y in enumerate(range(18,108,6)):
        if k%3!=1: partition(f'LabWest_{f}_{k}','x',9.3,17.23,y,z)
        partition(f'LabEast_{f}_{k}','x',39.9 if f==0 else 36.77,44.7,y,z)

# Source-correct identical semicircles; straight opposite-side floor galleries.
def arc_quad(x,y,ri,ro,a,b,z0,z1,name,coll):
    pts=[(x+ri*math.cos(a),y+ri*math.sin(a)),(x+ro*math.cos(a),y+ro*math.sin(a)),(x+ro*math.cos(b),y+ro*math.sin(b)),(x+ri*math.cos(b),y+ri*math.sin(b))]
    if g2.signed_area(pts)<0: pts.reverse()
    return mesh_prism(name,coll,[(u,v,z0) for u,v in pts],[(u,v,z1) for u,v in pts])

def rail_post(name,coll,x,y,z,p,q):
    """Post top is bevelled to the actual underside plane of its rail."""
    p,q=Vector(p),Vector(q);axis=(q-p).normalized()
    up=(Vector((0,0,1))-axis*axis.z).normalized()
    corners=[(x-.0125,y-.0125),(x+.0125,y-.0125),(x+.0125,y+.0125),(x-.0125,y+.0125)]
    tops=[p.z-(up.x*(u-p.x)+up.y*(v-p.y)+.02)/up.z for u,v in corners]
    return mesh_prism(name,coll,[(u,v,z) for u,v in corners],[(u,v,top) for (u,v),top in zip(corners,tops)])
walking_samples=[]
for label,x,y in STAIRS:
    for f in range(4):
        base=z_floor(f);phase=math.radians(STAIR_DIRECTION[label])
        for k in range(N_RISERS):
            a=phase+k*FLIGHT_ANGLE/N_RISERS;b=phase+(k+1)*FLIGHT_ANGLE/N_RISERS
            z=base+(k+1)*STOREY/N_RISERS
            arc_quad(x,y,STAIR_INNER,STAIR_R,a,b,z-.12,z,f'StairTread_{label}_{f}_{k}','Stairs/Treads')
            arc_quad(x,y,STAIR_INNER,STAIR_R,a,b,max(base,z-.12-.18-STOREY/N_RISERS),z-.12,f'StairWaist_{label}_{f}_{k}','Stairs/Waists')
            if f>0 and k<2:
                arc_quad(x,y,STAIR_INNER,STAIR_R,a,b,base-.43,base,f'StairLowerJoint_{label}_{f}_{k}','Stairs/Waists')
            for fraction in (.02,.5,.98):
                angle=a+(b-a)*fraction
                for radius in (1.14,1.90,2.66): walking_samples.append((f'{label}_{f}_{k}',x+radius*math.cos(angle),y+radius*math.sin(angle),z))
            for side,r in enumerate((STAIR_INNER,STAIR_R)):
                p=(x+r*math.cos(a),y+r*math.sin(a),z-STOREY/N_RISERS+1.05)
                q=(x+r*math.cos(b),y+r*math.sin(b),z+1.05)
                radial_clips=[(Vector(p),Vector((-math.sin(a),math.cos(a),0))),
                              (Vector(q),Vector((math.sin(b),-math.cos(b),0)))]
                bar(f'StairHandrail_{label}_{f}_{k}_{side}','Stairs/Rails',p,q,(0,0,1),.04,.04,ext=(.08,.08),clips=radial_clips)
                for t in (.25,.75):
                    ang=a+(b-a)*t
                    u,v=x+r*math.cos(ang),y+r*math.sin(ang)
                    rail_post(f'StairBaluster_{label}_{f}_{k}_{side}_{t}','Stairs/Rails',u,v,z,p,q)
        level=base+STOREY;landing_start=phase+FLIGHT_ANGLE
        # Both joints continue at least 0.20m into their landing assembly
        # at the inner radius; the extra depth stays below the walking face.
        lap_angle=.20/STAIR_INNER
        if f>0:arc_quad(x,y,STAIR_INNER,STAIR_R,phase-lap_angle,phase,base-.43,base-.25,f'StairLowerLap_{label}_{f}','Stairs/Waists')
        arc_quad(x,y,STAIR_INNER,STAIR_R,landing_start,landing_start+lap_angle,level-.43,level-.25,f'StairUpperLap_{label}_{f}','Stairs/Waists')
        side=-1 if label!='S' else 1
        ya,yb=sorted((y,y+side*1.4))
        B(f'StairLanding_{label}_{f}_Gallery','Stairs/Landings',x-2.75,x+2.75,ya,yb,level-.25,level)
        rail_a,rail_b=sorted((y,y+side*.04))
        B(f'StairLandingRail_{label}_{f}','Stairs/Rails',x-1.1,x+1.1,rail_a,rail_b,level+1.03,level+1.07)
        for k in range(9):
            u=x-1.05+k*2.10/8;v=y+side*.02
            B(f'StairLandingPost_{label}_{f}_{k}','Stairs/Rails',u-.0125,u+.0125,v-.0125,v+.0125,level,level+1.03)
        for u in (x-1.9,x,x+1.9):walking_samples.append((f'{label}_{f}_Gallery',u,y+side*.7,level))
        for k in range(72):
            a=math.radians(5*k);b=a+math.radians(5)
            arc_quad(x,y,2.75,2.85,a,b,level-SLAB-BEAM_D,level-SLAB,f'StairRim_{label}_{f}_{k}','Structure/StairRims')

# Gallery-side diameter headers mate to the retained full rim. Split at the
# integrated flight-root thickening, so connections occupy actual volume once.
header_frame=Frame((0,0,0),(1,0,0),(0,1,0))
for label,x,y in STAIRS:
    side=-1 if label!='S' else 1
    ya,yb=sorted((y,y+side*.40))
    for f in range(1,5):
        level=z_floor(f)
        poly=g2.rect(x-2.75,x+2.75,ya,yb)
        circle=[(x+2.75*math.cos(math.radians(k*5)),y+2.75*math.sin(math.radians(k*5))) for k in range(72)]
        for a,b in zip(circle,circle[1:]+circle[:1]):poly=g2.clip(poly,a,(a[1]-b[1],b[0]-a[0]))
        root_cuts=[]
        for obj in bpy.data.objects:
            if not obj.name.startswith((f'StairLowerLap_{label}_',f'StairUpperLap_{label}_')):continue
            points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
            if abs(max(p.z for p in points)-(level-.25))>.001:continue
            root_cuts.append([(points[face.vertices[0]],-face.normal,0.) for face in obj.data.polygons])
        for layer,(za,zb) in enumerate(((level-.90,level-.43),(level-.43,level-.25))):
            pieces=[poly]
            if layer:
                for cuts in root_cuts:pieces=[piece for original in pieces for piece in subtract(header_frame,original,cuts,za,zb) if g2.area(piece)>1e-8]
            for j,piece in enumerate(pieces):frame_prism(f'StairHeaderDiameter_{label}_{f}_{layer}_{j}','Structure/Beams',header_frame,piece,za,zb)

# Northern courtyard insert: two levels, skylight grid, side glazing.
insert=(18.55,31.5,66.,96.)
for f in range(3):
    z=z_floor(f)
    slab_zone(f'InsertSlab_{f}','Insert/InsertFloors',insert,z,access_holes+([(20.,30.,69.,93.)] if f==2 else []))
for ix,x in enumerate((18.75,25.0,31.25)):
    for iy,y in enumerate(range(66,97,6)):
        B(f'InsertFooting_{ix}_{iy}','Foundation',x-.9,x+.9,y-.7,y+1.1,-1.25,-.60)
        B(f'InsertPedestal_{ix}_{iy}','Foundation',x-.2,x+.2,y,y+.4,-.60,-.25)
        B(f'InsertColumn_{ix}_{iy}','Insert/InsertStructure',x-.20,x+.20,y,y+.4,0.,6.95)
for iy,y in enumerate(range(66,97,6)):
    B(f'InsertGradeBeam_{iy}','Foundation',18.55,31.5,y,y+.4,-.60,-.25)
for f in (1,2):
    z=z_floor(f)
    for j,y in enumerate(range(66,97,6)):
        B(f'InsertBeam_{f}_{j}','Insert/InsertStructure',18.55,31.5,y,y+.4,z-.65,z-.25)
for j,y in enumerate((72.,78.,84.,90.)):
    B(f'RooflightSeatBeam_{j}','Insert/InsertStructure',19.9,30.1,y,y+.20,6.95,7.4)

# The two insert floors connect through a short enclosed link. Ledger roots
# attach below retained concrete; the0.15m end strips are replaced by the deck.
for f in range(3):
    z=z_floor(f)
    B(f'InsertLinkDeck_{f}','Insert/InsertFloors',17.55,18.70,74.,76.,z-.25,z)
    for label,xa,xb in [('W',17.35,17.70),('E',18.55,18.90)]:
        B(f'InsertLinkLedger_{label}_{f}','Insert/InsertStructure',xa,xb,74.,76.,z-.40,z-.25)
for side,ya,yb in [('S',74.,74.15),('N',75.85,76.)]:
    B(f'InsertLinkWall_{side}','Insert/InsertWalls',17.45,18.55,ya,yb,0.,7.20)
framing.wall_along_y('InsertWestWall','Insert/InsertWalls',[(66.,0.),(96.,0.),(96.,7.20),(66.,7.20)],18.55,18.75,
                     [(74.30,75.70,z_floor(f),z_floor(f)+2.40) for f in (0,1)])
for f in (0,1):
    z=z_floor(f)
    for side,xa,xb,frame_x in [('Wing',17.23,17.45,17.45),('Insert',18.55,18.75,18.75)]:
        for j,(ya,yb) in enumerate(((74.10,74.30),(75.70,75.90))):
            B(f'InsertLinkPier_{side}_{f}_{j}','Insert/InsertStructure',xa,xb,ya,yb,z,z+2.40)
        B(f'InsertLinkLintel_{side}_{f}','Insert/InsertStructure',xa,xb,74.10,75.90,z+2.40,z+2.60)
        for j,(ya,yb) in enumerate(((74.235,74.30),(75.70,75.765))):
            B(f'InsertLinkDoorJamb_{side}_{f}_{j}','Facade/TimberFrames',frame_x,frame_x+.10,ya,yb,z,z+2.40)
        B(f'InsertLinkDoorHead_{side}_{f}','Facade/TimberFrames',frame_x,frame_x+.10,74.30,75.70,z+2.40,z+2.465)
# First raised south beams terminate at the existing service core instead
# of Column81. Integral ledges preserve the full0.20x0.40m beam-end seat.
B('CoreBeamLedge_S_W','Structure/Cores',43.475,43.875,6.15,6.55,2.50,2.70)
B('CoreBeamLedge_S_E','Structure/Cores',46.725,47.125,6.15,6.55,2.50,2.70)
for i,(a,b) in enumerate(g2.columns(66.,96.,3.)):
    window(f'InsertEast_{i}','y',a,b,31.40,.10,3.0,False)
# End walls close the two-storey insert. The east shelf closes the junction
# between its recessed ground glass and the outward lower edge of the slope.
for label,ya,yb in [('South',66.,66.2),('North',95.8,96.)]:
    B(f'InsertEndWall_{label}','Insert/InsertWalls',18.55,31.5,ya,yb,0.,6.95)
    prism_y(f'InsertEndWedge_{label}','Insert/InsertWalls',ya,yb,[(31.5,3.),(33.,3.),(31.5,6.9)])
B('InsertEastShelf','Insert/InsertFloors',31.5,33.,66.,96.,2.85,3.)
for j,x in enumerate((20.,30.)):
    B(f'SkylightCurbX_{j}','Insert/SkylightFrames',x-.10,x+.10,68.9,93.1,7.2,7.4)
for j,y in enumerate((69.,93.)):
    B(f'SkylightCurbY_{j}','Insert/SkylightFrames',20.1,29.9,y-.10,y+.10,7.2,7.4)
for i,(a,b) in enumerate(g2.columns(20.,30.,1.5)):
    for j,(c,d) in enumerate(g2.columns(69.,93.,1.5)):
        B(f'SkylightGlass_{i}_{j}','Insert/InsertGlass',a+.0325,b-.0325,c+.0325,d-.0325,7.532,7.55)
for i,x in enumerate([20.+1.5*k for k in range(7)]+[30.]):
    B(f'SkylightMullion_{i}','Insert/SkylightFrames',x-.0325,x+.0325,69.,93.,7.4,7.55)
for j in range(17):
    y=69.+1.5*j
    B(f'SkylightTransom_{j}','Insert/SkylightFrames',20.,30.,y-.0325,y+.0325,7.4,7.55)
INSERT_SLOPE=Ruled((31.5,66.,6.9),(31.5,96.,6.9),(33.,66.,3.),(33.,96.,3.),out=(1,0,0))
insert_margin=FRAME/(2*math.hypot(1.5,3.9))
for i in range(20):
    surface_quad(f'InsertInclineGlass_{i}','Insert/InsertGlass',INSERT_SLOPE,i/20+FRAME/60,(i+1)/20-FRAME/60,insert_margin,1.-insert_margin,0.,GLASS)
for i in range(21):
    offset=INSERT_SLOPE.normal(i/20,.5)*.065
    member(f'InsertInclineRafter_{i}','Insert/SkylightFrames',INSERT_SLOPE.P(i/20,insert_margin)+offset,INSERT_SLOPE.P(i/20,1.-insert_margin)+offset,.065,.10,(0,1,0))
for i,u in enumerate((0.,1.)):
    offset=INSERT_SLOPE.normal(.5,u)*.065
    member(f'InsertInclineRail_{i}','Insert/SkylightFrames',INSERT_SLOPE.P(0,u)+offset,INSERT_SLOPE.P(1,u)+offset,.065,.10,(1.5,0,-3.9))
B('RetainingBase','Foundation',18.55,35.45,95.7,96.6,-.4,0.)
B('RetainingWall','Insert/Retaining',18.55,35.45,96.,96.3,0.,3.)
framing.flight('CourtStair','SiteStairs',89.7,1,33.,35.45,0.,20,.30,.15,.15)
# flight runs along X: rotate the complete generated family into the east passage.
for obj in list(bpy.data.collections['SiteStairs'].objects):
    # Kit creates transformed boxes; rigid world transform swaps X/Y.
    from mathutils import Matrix
    obj.matrix_world=Matrix(((0,1,0,0),(1,0,0,0),(0,0,1,0),(0,0,0,1))) @ obj.matrix_world
B('CourtStairTopLanding','SiteStairs',33.15,35.45,95.4,96.,2.85,3.)
for side,x in enumerate((33.30,35.40)):
    rail_start=(x,89.7,1.05);rail_end=(x,95.7,4.05)
    member(f'CourtStairHandrail_{side}','SiteStairs',rail_start,rail_end,.04,.04,(0,0,1))
    for j in range(21):
        y=89.7+j*.30;z=j*.15
        rail_post(f'CourtStairBaluster_{side}_{j}','SiteStairs',x,y,min(3.,z+.15),rail_start,rail_end)

# Flat roof parapets and three sparse sheet-metal plant housings.
for j,x in enumerate((.55,17.23,36.55,53.23)):
    B(f'ParapetLong_{j}','Roof/Parapets',x,x+.22,.77,113.23,18.,18.45)
for j,y in enumerate((.55,113.23)):
    B(f'ParapetEnd_{j}','Roof/Parapets',.55,53.45,y,y+.22,18.,18.45)
for j,(xc,yc,w,l,h) in enumerate(((8.5,20.,5.4,10.8,4.8),(45.5,84.,5.4,10.8,4.8),(27.,6.,9.,6.,2.1))):
    a,b,c,d=xc-w/2,xc+w/2,yc-l/2,yc+l/2
    B(f'PlantPlinth_{j}','Roof/Plant',a,b,c,d,18.,18.2)
    # Chamfered lower metal transition; radii derived from the column catalogue.
    profile=[(a+.60,18.2),(b-.60,18.2),(b-.18,18.38),(b,18.8),(b,18.2+h),(a,18.2+h),(a,18.8),(a+.18,18.38)] if j<2 else g2.rect(a,b,18.2,18.2+h)
    for end,(ya,yb) in enumerate(((c,c+.15),(d-.15,d))): prism_y(f'PlantClad_{j}_End{end}','Roof/Plant',ya,yb,profile)
    for k,poly in enumerate(g2.wall_pieces(profile,[(a+.15,b-.15,18.2,18.2+h-.15)])):
        prism_y(f'PlantClad_{j}_Shell{k}','Roof/Plant',c+.15,d-.15,poly)
    for k,(u,v) in enumerate(g2.columns(a,b,.45)):
        B(f'PlantSeam_{j}_{k}','Roof/Plant',u,u+.018,c-.018,c,18.2,18.2+h)
    for k in range(int(h/.30)):
        B(f'PlantLouvre_{j}_{k}','Roof/PlantLouvres',a,b,d,d+.065,18.35+k*.30,18.43+k*.30)
for wing,x in enumerate((9.,45.)):
    for j,y in enumerate((30.,96.)): B(f'RoofDrain_{wing}_{j}','Roof/Drains',x+.45,x+.75,y-.15,y+.15,18.,18.025)

def rect_bounds(obj):
    """Only exact axis-aligned boxes enter rectangular butt-joint fitting."""
    points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    axes=[sorted(set(round(p[i],5) for p in points)) for i in range(3)]
    if len(points)!=8 or any(len(values)!=2 for values in axes): return None
    return tuple(value for values in axes for value in (values[0],values[-1]))

def subtract_box(bounds,cut):
    """Six disjoint convex remnants; preserve the exact mating faces."""
    clipped=[max(bounds[i],cut[i]) if i%2==0 else min(bounds[i],cut[i]) for i in range(6)]
    if any(clipped[i+1]-clipped[i]<.00001 for i in (0,2,4)): return [bounds]
    remnants=[];middle=list(bounds)
    for axis in (0,2,4):
        if clipped[axis]>middle[axis]+.00001:
            piece=middle.copy();piece[axis+1]=clipped[axis];remnants.append(tuple(piece))
        if clipped[axis+1]<middle[axis+1]-.00001:
            piece=middle.copy();piece[axis]=clipped[axis+1];remnants.append(tuple(piece))
        middle[axis:axis+2]=clipped[axis:axis+2]
    return remnants

def joint_priority(name):
    # Construction precedence: continuous shafts/cores; crossing beams;
    # seated landings and slabs; fitted panels, frames and room partitions.
    if name.startswith(('StairTread','StairWaist','StairHandrail','StairBaluster')): return None
    if 'Footing' in name or name.startswith(('FootingPad','Pedestal','CoreFoundation','InsertPedestal')): return 0
    if name.startswith(('GradeBeam','InsertGradeBeam')): return .5
    if name.startswith('CoreBeamLedge'): return .95
    if name.startswith(('Column_','CoreWall','InsertColumn','CorbelSeat')): return 1
    if name.startswith(('Beam_','EdgeBeam','StairHeader','InsertBeam','RooflightSeatBeam','Retaining','StairRim')): return 2
    if name.startswith(('InsertLinkLedger','InsertLinkPier','InsertLinkLintel')): return 2
    if name.startswith('StairLanding'): return 2.5
    if name.startswith('InsertInclineRail'): return 2.9
    if name.startswith(('SouthInclineRail','SouthInclineRafter')): return 3.5
    if name.startswith(('FloorSlab','InsertSlab','InsertEastShelf','InsertLinkDeck')): return 3
    if name.startswith('PlantPlinth'): return 3.2
    if name.startswith(('Panel_','SouthFascia','SouthVentBacking','InsertEndWall','InsertWestWall','InsertLinkWall')): return 4
    if name.startswith(('Parapet','SkylightCurb','SkylightMullion')): return 4.5
    if name.startswith(('Window_','SouthRibbon','SouthFineStrip','SouthGround','InsertEast','SkylightTransom','EntranceDoor','InsertLinkDoor')): return 5
    if name.startswith(('Corridor','Office','Lab','EastGalleryWall')): return 6
    if name=='NorthTerrace': return 7
    return None

# Real openings through existing wing glazing/panels; new concrete jambs and
# lintels are subsequently fitted with the same construction precedence.
access_replacements=[]
for obj in list(bpy.data.objects):
    if obj.type!='MESH' or not obj.name.startswith(('Panel_CourtWest','Window_CourtWest')):continue
    bounds=rect_bounds(obj)
    if bounds is None:continue
    pieces=[bounds]
    for f in (0,1):pieces=[piece for original in pieces for piece in subtract_box(original,(17.20,17.55,74.30,75.70,z_floor(f),z_floor(f)+2.40))]
    if pieces!=[bounds]:access_replacements.append((obj,obj.name,obj.users_collection[0],pieces))
bpy.data.batch_remove(ids=[item[0] for item in access_replacements])
for _,name,coll,pieces in access_replacements:
    for j,piece in enumerate(pieces):B(f'{name}_Access{j}',coll,*piece)
bpy.context.view_layer.update()
joinery=[]
for obj in list(bpy.data.objects):
    if obj.type!='MESH': continue
    priority=joint_priority(obj.name);bounds=rect_bounds(obj)
    if priority is not None and bounds: joinery.append((priority,obj.name,bounds,obj))
joinery.sort(key=lambda item:(item[0],item[1]))
# Index source rectangles by 6 m plan cells. This limits candidate fits to
# neighbouring construction; it does not change the intersection predicate.
joint_cells={}
fitted=0;replacements=[]
for source_index,(priority,name,bounds,obj) in enumerate(joinery):
    if source_index%4000==0: print(f'Joinery: {source_index}/{len(joinery)} sources',flush=True)
    cells=[(x,y) for x in range(math.floor(bounds[0]/6),math.floor(bounds[1]/6)+1)
                  for y in range(math.floor(bounds[2]/6),math.floor(bounds[3]/6)+1)]
    candidates={index for cell in cells for index in joint_cells.get(cell,())}
    pieces=[bounds]
    for index in sorted(candidates):
        cut=joinery[index][2]
        if any(bounds[i]>=cut[i+1]-.00001 or cut[i]>=bounds[i+1]-.00001 for i in (0,2,4)): continue
        pieces=[piece for original in pieces for piece in subtract_box(original,cut)]
    if pieces!=[bounds]:
        replacements.append((obj,name,obj.users_collection[0],pieces))
        fitted+=1
    # Original source volumes remain valid cutters: removed volume is always
    # occupied by the preceding, higher-priority construction.
    for cell in cells: joint_cells.setdefault(cell,[]).append(source_index)
bpy.data.batch_remove(ids=[item[0] for item in replacements])
for _,name,coll,pieces in replacements:
    for j,piece in enumerate(pieces): B(f'{name}_Fit{j}',coll,*piece)
print(f'Fitted {fitted} rectangular construction joints',flush=True)

# Fit walls and infill to the chamfered shoulders in their own thin-section
# frames. The kit subtracts the true convex corbel planes, retaining convex
# remnants instead of a large rectangular clearance around each shoulder.
corbel_cutters=[]
for obj in bpy.data.objects:
    if obj.type!='MESH': continue
    cutter_priority=.9 if obj.name.startswith('CorbelWing') else joint_priority(obj.name)
    if not obj.name.startswith('CorbelWing') and (cutter_priority not in (2,3,3.5) or rect_bounds(obj) is not None): continue
    points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    bounds=tuple(value for axis in range(3) for value in (min(p[axis] for p in points),max(p[axis] for p in points)))
    planes=[(points[face.vertices[0]],-(obj.matrix_world.to_3x3() @ face.normal).normalized(),0.) for face in obj.data.polygons]
    corbel_cutters.append((bounds,planes,cutter_priority))
corbel_replacements=[]
cutter_cells={}
for index,(bounds,planes,priority) in enumerate(corbel_cutters):
    for xx in range(math.floor(bounds[0]/6),math.floor(bounds[1]/6)+1):
        for yy in range(math.floor(bounds[2]/6),math.floor(bounds[3]/6)+1): cutter_cells.setdefault((xx,yy),[]).append(index)
for obj in list(bpy.data.objects):
    if obj.type!='MESH': continue
    priority=joint_priority(obj.name)
    if priority is None or priority<1 or obj.name.startswith(('Column','Corbel')): continue
    bounds=rect_bounds(obj)
    if bounds is None: continue
    indices={index for xx in range(math.floor(bounds[0]/6),math.floor(bounds[1]/6)+1) for yy in range(math.floor(bounds[2]/6),math.floor(bounds[3]/6)+1) for index in cutter_cells.get((xx,yy),())}
    cuts=[planes for index in sorted(indices) for cut,planes,cutter_priority in [corbel_cutters[index]] if priority>cutter_priority and all(min(bounds[i+1],cut[i+1])-max(bounds[i],cut[i])>.00001 for i in (0,2,4))]
    if not cuts: continue
    thickness_axis=min(range(3),key=lambda axis:bounds[2*axis+1]-bounds[2*axis])
    u_axis=(thickness_axis+1)%3;v_axis=(thickness_axis+2)%3
    axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
    fr=Frame((0,0,0),axes[u_axis],axes[v_axis])
    t0,t1=bounds[2*thickness_axis:2*thickness_axis+2]
    outline=g2.rect(*bounds[2*u_axis:2*u_axis+2],*bounds[2*v_axis:2*v_axis+2])
    pieces=[outline]
    for cutter in cuts:
        pieces=[piece for poly in pieces for piece in subtract(fr,poly,cutter,t0,t1) if g2.area(piece)>1e-8]
    corbel_replacements.append((obj,obj.name,obj.users_collection[0],fr,t0,t1,pieces))
bpy.data.batch_remove(ids=[item[0] for item in corbel_replacements])
for _,name,coll,fr,t0,t1,pieces in corbel_replacements:
    for j,poly in enumerate(pieces): frame_prism(f'{name}_ShoulderFit{j}',coll,fr,poly,t0,t1)
print(f'Fitted {len(corbel_replacements)} chamfered shoulder interfaces',flush=True)

def complete_core_bases():
    """Close the actual0.25m foundation-to-wall gap with matching wall bases.
    Run after fitting so the same deterministic function can verify an
    unrendered saved-model completion. Column volumes retain precedence.
    """
    column_cuts=[rect_bounds(obj) for obj in bpy.data.objects if obj.type=='MESH' and obj.name.startswith('Column_')]
    for label,x,y in CORES:
        a,b,c,d=core_bounds(label,x,y)
        strips=[('W',(a,a+.25,c,d)),('E',(b-.25,b,c,d)),
                ('S',(a+.25,b-.25,c,c+.25)),('N',(a+.25,b-.25,d-.25,d))]
        for side,rect in strips:
            pieces=[(*rect,-.25,0.)]
            for cut in column_cuts:
                if cut is not None:pieces=[piece for original in pieces for piece in subtract_box(original,cut)]
            for j,piece in enumerate(pieces):B(f'CoreWallBase_{label}_{side}_{j}','Structure/Cores',*piece)
complete_core_bases()

# Material graph carries actual glass transmission into .blend and Cycles.
glass_material=bpy.data.materials.new('Transparent architectural glass')
glass_material.use_nodes=True
shader=glass_material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(.47,.58,.59,1)
shader.inputs['Transmission Weight'].default_value=1.
shader.inputs['Roughness'].default_value=.04
for obj in bpy.data.objects:
    if obj.type=='MESH' and 'Glass' in obj.name: obj.data.materials.append(glass_material)
print(f'Built Arrhenius v03: {len([o for o in bpy.data.objects if o.type=="MESH"])} elements; 19x6 grid; five occupied levels; roof {ROOF_Z}m',flush=True)
