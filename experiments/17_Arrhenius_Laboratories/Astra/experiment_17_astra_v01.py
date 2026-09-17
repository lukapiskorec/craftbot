"""Arrhenius Laboratories, Astra v01. Architectural estimates: concept.md §§2–4.
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
from planes import member
from ruled import Ruled, surface_quad, ruling_member

# All metric values are estimates carried by concept.md. Subdivisions below
# are derived from these modules; small tolerances are labelled fabrication.
LONG_BAY, N_LONG, CROSS_BAY, N_CROSS = 6., 19, 9., 6
L, W, STOREY, N_FLOORS = LONG_BAY*N_LONG, CROSS_BAY*N_CROSS, 3.6, 5
SLAB, SHAFT, BEAM_W, BEAM_D = .25, .60, .40, .65
CORBEL_W, CORBEL_D, CORBEL_H = 1.30, 1.00, .60
RECESS, PANEL, FRAME, FRAME_DEPTH, GLASS = .55, .22, .065, .10, .018
PARAPET, COLUMN_TOP, PANEL_MODULE, PANEL_GAP = 18.45, 18.6, 3., .02
CORE_WALL, PARTITION, DOOR_W, DOOR_H = .25, .10, 1.2, 2.4
STAIRS = [('W',3.,61.),('E',51.,61.),('N',32.4,110.7),('S',40.2,5.4)]
# Centres selected on inward/service side; solid core width remains 3x4.5m.
CORES = [('W',3.8,66.2),('E',50.2,66.2),('N',27.9,110.7),('S',45.3,8.5)]
STAIR_R, STAIR_INNER, N_RISERS = 2.7, 1.1, 22
SITE = (-18.,72.,-24.,132.)
def z_floor(i): return STOREY*i
def front_y(z): return 6.-(z-3.)*5.25/5. if 3.<=z<=8. else (.55 if z>8. else 6.)
ROOF_Z = z_floor(N_FLOORS)
assert (N_LONG,N_CROSS,N_FLOORS)==(19,6,5)
assert abs(front_y(8.)-.75)<1e-8 and abs(front_y(3.)-6.)<1e-8
assert abs(N_RISERS*(STOREY/N_RISERS)-STOREY)<1e-8
assert W==54 and L==114 and ROOF_Z==18

craftbot.clear_scene()
def B(name,coll,*bounds):
    if any(bounds[i+1]-bounds[i]<1e-6 for i in (0,2,4)): return None
    return box(name,coll,*bounds)

column_centres=[(x,float(y)) for x in (0.,9.,18.,36.,45.,54.) for y in range(0,115,6)]
column_centres += [(27.,float(y)) for y in (0,6,12,108,114)]
column_holes=[(x-SHAFT/2,x+SHAFT/2,y-SHAFT/2,y+SHAFT/2) for x,y in column_centres]
stair_holes=[(x-STAIR_R,x+STAIR_R,y-STAIR_R,y+STAIR_R) for _,x,y in STAIRS]
core_holes=[(x-1.625,x+1.625,y-2.375,y+2.375) for _,x,y in CORES]

def cut_box(name,coll,x0,x1,y0,y1,z0,z1,holes):
    for i,(a,b,c,d) in enumerate(g2.tile(x0,x1,y0,y1,x1-x0,y1-y0,holes,False)):
        B(f'{name}_{i}',coll,a,b,c,d,z0,z1)

def slab_zone(name,coll,rect,z,holes):
    a,b,c,d=rect
    framing.tile_sheets(name,coll,a,b,c,d,z-SLAB,z,sheet_l=9.,sheet_w=6.,holes=holes,stagger=False)

# Foundations form the independent roots of the load paths. Site surfaces
# are split outside the ring so soil never intersects occupied rooms.
for i,(x,y) in enumerate(column_centres):
    B(f'FootingPad_{i}','Foundation',x-.9,x+.9,y-.9,y+.9,-1.25,-.60)
    B(f'Pedestal_{i}','Foundation',x-.3,x+.3,y-.3,y+.3,-.60,-SLAB)
for name,xc,yc in CORES:
    B(f'CoreFooting_{name}','Foundation',xc-2.,xc+2.,yc-2.75,yc+2.75,-1.25,-.8)
    B(f'CoreFoundation_{name}','Foundation',xc-1.625,xc+1.625,yc-2.375,yc+2.375,-.8,-SLAB)
for name,r,z in [('South',(-18,72,-24,-.9),-.15),('West',(-18,-.9,-.9,132),-.15),('East',(54.9,72,-.9,132),-.15),('North',(-.9,54.9,114.9,132),1.5)]:
    B('SiteGround_'+name,'Site',*r,z-.20,z)
B('CourtyardGarden','Site',18.55,35.45,12.55,65.8,-.3,-.1)
B('CourtPathEast','Site',33.,35.45,65.8,89.7,-.25,0.)
B('NorthTerrace','Site',18.55,35.45,96.3,107.45,2.75,3.)

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
        spans=[(0.,18.),(36.,54.)] if 12<y<108 else [(0.,54.)]
        for s,(a,b) in enumerate(spans):
            if y < front_y(z-SLAB) and z<8: continue
            cut_box(f'Beam_{f}_{iy}_{s}','Structure/Beams',a,b,y-.2,y+.2,z-SLAB-BEAM_D,z-SLAB,all_holes)
    for name,x,y in STAIRS:
        a,b,c,d=x-STAIR_R,x+STAIR_R,y-STAIR_R,y+STAIR_R
        for j,r in enumerate([(a-.4,a,c-.4,d+.4),(b,b+.4,c-.4,d+.4),(a,b,c-.4,c),(a,b,d,d+.4)]):
            cut_box(f'StairEdgeBeam_{name}_{f}_{j}','Structure/Beams',*r,z-SLAB-BEAM_D,z-SLAB,column_holes+core_holes)
    # Facade ledgers carry panel leaves and tie the slab perimeter to shafts.
    for j,x in enumerate((.55,17.45,36.55,53.45)):
        cut_box(f'EdgeBeam_{f}_{j}','Structure/Beams',x-.20,x+.20,max(.3,front_y(z-SLAB)),113.7,z-SLAB-BEAM_D,z-SLAB,all_holes)

for f in range(6):
    z=z_floor(f)
    south=.30 if f==0 or z>=8 else front_y(z-SLAB)+.12
    ring=[(.3,17.70,south,113.70),(36.30,53.70,south,113.70),(17.70,36.30,south,12.30),(17.70,36.30,107.70,113.70)]
    for i,r in enumerate(ring):
        slab_zone(f'FloorSlab_{f}_{i}','Roof/RoofSlabs' if f==5 else 'Floors',r,z,column_holes+core_holes+(stair_holes if f>0 else []))

# Four service cores: wall-centre rectangles 3x4.5m, doorway toward corridor.
for name,x,y in CORES:
    a,b,c,d=x-1.625,x+1.625,y-2.375,y+2.375
    for f in range(5):
        z=z_floor(f)
        B(f'CoreWall_{name}_{f}_W','Structure/Cores',a,a+.25,c,d,z, z+STOREY)
        B(f'CoreWall_{name}_{f}_E','Structure/Cores',b-.25,b,c,d,z, z+STOREY)
        B(f'CoreWall_{name}_{f}_N','Structure/Cores',a+.25,b-.25,d-.25,d,z,z+STOREY)
        framing.wall_along_x(f'CoreWall_{name}_{f}_S','Structure/Cores',[(a+.25,z),(b-.25,z),(b-.25,z+STOREY),(a+.25,z+STOREY)],c,c+.25,[(x-.6,x+.6,z,z+DOOR_H)])

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
    window(f'SouthFineStrip_{i}','x',a,b,.75,8.,8.45,False)
    window(f'SouthGround_{i}','x',a,b,6.,0.,3.,False)
B('SouthVentBacking','Facade/SouthMetal',.55,53.45,.75,.97,8.45,9.6)
for i in range(3): B(f'SouthVentLine_{i}','Facade/SteelFrames',.55,53.45,.71,.75,8.65+i*.30,8.69+i*.30)
SOUTH=Ruled((.55,.75,8.),(53.45,.75,8.),(.55,6.,3.),(53.45,6.,3.),out=(0,-1,-1))
slant_len=math.hypot(5.25,5.)
for i,(a,b) in enumerate(g2.columns(.55,53.45,1.5)):
    for j,(c,d) in enumerate(((0.,.5),(.5,1.))):
        surface_quad(f'SouthInclineGlass_{i}_{j}','Facade/Glass',SOUTH,(a-.55+FRAME/2)/52.9,(b-.55-FRAME/2)/52.9,c+FRAME/(2*slant_len),d-FRAME/(2*slant_len),0.,GLASS)
for i,x in enumerate([.55+1.5*k for k in range(36)]+[53.45]):
    t=min(1.,(x-.55)/52.9)
    member(f'SouthInclineRafter_{i}','Facade/SteelFrames',SOUTH.P(t,0),SOUTH.P(t,1),FRAME,.10,(1,0,0))
for j,u in enumerate((0.,.5,1.)):
    member(f'SouthInclineRail_{j}','Facade/SteelFrames',SOUTH.P(0,u),SOUTH.P(1,u),FRAME,.10,(0,5.25,-5))
# The central door replaces the middle lower-glass unit with a clear framed pair.
# Door leaves are visually subdivided within the glazed wall, opening into foyer.
for i,x in enumerate((25.8,27.,28.2)):
    B(f'EntranceDoorJamb_{i}','Entrance',x-.0325,x+.0325,5.90,6.,0.,2.4)
B('EntranceDoorHead','Entrance',25.8,28.2,5.90,6.,2.4,2.465)

# Asymmetric room partitions; service/stair openings are cut consistently.
def partition(name,along,a,b,c,z,doors=()):
    cuts=[]
    for ha,hb,hc,hd in stair_holes+core_holes+column_holes:
        if along=='x' and hc<c+.1 and hd>c: cuts.append((ha,hb))
        if along=='y' and ha<c+.1 and hb>c: cuts.append((hc,hd))
    merged=[]
    for lo,hi in sorted(cuts):
        if merged and lo<=merged[-1][1]: merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
        else: merged.append((lo,hi))
    for i,(lo,hi) in enumerate(g2.split_range(a,b,merged)):
        holes=[(max(lo,d-.6),min(hi,d+.6),z,z+2.4) for d in doors if d+.6>lo and d-.6<hi]
        pts=[(lo,z),(hi,z),(hi,z+3.35),(lo,z+3.35)]
        if along=='x': framing.wall_along_x(f'{name}_{i}','Interior/Partitions',pts,c,c+.1,holes)
        else: framing.wall_along_y(f'{name}_{i}','Interior/Partitions',pts,c,c+.1,holes)
for f in range(5):
    z=z_floor(f)
    for x in (6.1,9.2,44.7,47.8): partition(f'CorridorWall_{f}_{x}','y',12.8,107.1,x,z,range(15,108,6))
    if f==0: partition('EastGalleryWall','y',12.8,107.1,39.8,z,range(15,108,6))
    for k,y in enumerate(range(15,108,3)):
        partition(f'OfficeWest_{f}_{k}','x',.77,6.1,y,z)
        if k%3 !=1: partition(f'OfficeEast_{f}_{k}','x',47.9,53.23,y,z)
    for k,y in enumerate(range(18,108,6)):
        if k%3!=1: partition(f'LabWest_{f}_{k}','x',9.3,17.23,y,z)
        partition(f'LabEast_{f}_{k}','x',39.9 if f==0 else 36.77,44.7,y,z)

# Curved stairs: 22 convex annular tread segments per half-turn. The segmented
# waist joins underside-to-underside; landings connect the alternating flights.
def arc_quad(x,y,ri,ro,a,b,z0,z1,name,coll):
    pts=[(x+ri*math.cos(a),y+ri*math.sin(a)),(x+ro*math.cos(a),y+ro*math.sin(a)),(x+ro*math.cos(b),y+ro*math.sin(b)),(x+ri*math.cos(b),y+ri*math.sin(b))]
    return mesh_prism(name,coll,[(u,v,z0) for u,v in pts],[(u,v,z1) for u,v in pts])
for label,x,y in STAIRS:
    for f in range(4):
        base=z_floor(f); phase=math.pi*(f%2)
        for k in range(N_RISERS):
            a=phase+k*math.pi/N_RISERS;b=phase+(k+1)*math.pi/N_RISERS
            z=base+(k+1)*STOREY/N_RISERS
            arc_quad(x,y,STAIR_INNER,STAIR_R,a,b,z-.12,z,f'StairTread_{label}_{f}_{k}','Stairs/Treads')
            arc_quad(x,y,STAIR_INNER,STAIR_R,a,b,z-.12-.18-STOREY/N_RISERS,z-.12,f'StairWaist_{label}_{f}_{k}','Stairs/Waists')
            for side,r in enumerate((STAIR_INNER,STAIR_R)):
                p=(x+r*math.cos(a),y+r*math.sin(a),z+1.05)
                q=(x+r*math.cos(b),y+r*math.sin(b),z+1.05+STOREY/N_RISERS)
                member(f'StairHandrail_{label}_{f}_{k}_{side}','Stairs/Rails',p,q,.04,.04,(0,0,1))
                for t in (.25,.75):
                    ang=a+(b-a)*t
                    u,v=x+r*math.cos(ang),y+r*math.sin(ang)
                    B(f'StairBaluster_{label}_{f}_{k}_{side}_{t}','Stairs/Rails',u-.0125,u+.0125,v-.0125,v+.0125,z,z+1.05+t*STOREY/N_RISERS)
        for end in (0,1):
            if f>0 and end==0: continue  # shared landing emitted by previous flight
            sign=(-1 if (f+end)%2 else 1)
            xa,xb=sorted((x+sign*STAIR_INNER,x+sign*STAIR_R))
            zl=base+end*STOREY
            B(f'StairLanding_{label}_{f}_{end}','Stairs/Landings',xa,xb,y-.90,y,zl-.25,zl)

# Northern courtyard insert: two levels, skylight grid, side glazing.
insert=(18.55,31.5,66.,96.)
for f in range(3):
    z=z_floor(f)
    slab_zone(f'InsertSlab_{f}','Insert/InsertFloors',insert,z,[(20.,30.,69.,93.)] if f==2 else [])
for ix,x in enumerate((18.75,25.0,31.25)):
    for iy,y in enumerate(range(66,97,6)):
        B(f'InsertColumn_{ix}_{iy}','Insert/InsertStructure',x-.20,x+.20,y,y+.4,0.,6.95)
for f in (1,2):
    z=z_floor(f)
    for j,y in enumerate(range(66,97,6)):
        B(f'InsertBeam_{f}_{j}','Insert/InsertStructure',18.55,31.5,y,y+.4,z-.65,z-.25)
for i,(a,b) in enumerate(g2.columns(66.,96.,3.)):
    window(f'InsertEast_{i}','y',a,b,31.40,.10,3.0,False)
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
for i in range(20):
    surface_quad(f'InsertInclineGlass_{i}','Insert/InsertGlass',INSERT_SLOPE,i/20+.001,(i+1)/20-.001,0.,1.,0.,GLASS)
for i in range(21):
    member(f'InsertInclineRafter_{i}','Insert/SkylightFrames',INSERT_SLOPE.P(i/20,0),INSERT_SLOPE.P(i/20,1),.065,.10,(0,1,0))
for i,u in enumerate((0.,1.)):
    member(f'InsertInclineRail_{i}','Insert/SkylightFrames',INSERT_SLOPE.P(0,u),INSERT_SLOPE.P(1,u),.065,.10,(1,0,0))
B('RetainingBase','Foundation',18.55,35.45,95.7,96.6,-.4,0.)
B('RetainingWall','Insert/Retaining',18.55,35.45,96.,96.3,0.,3.)
B('CourtStairTopLanding','SiteStairs',33.,35.45,95.4,96.,2.85,3.)
framing.flight('CourtStair','SiteStairs',89.7,1,33.,35.45,0.,20,.30,.15,.15)
# flight runs along X: rotate the complete generated family into the east passage.
for obj in list(bpy.data.collections['SiteStairs'].objects):
    # Kit creates transformed boxes; rigid world transform swaps X/Y.
    from mathutils import Matrix
    obj.matrix_world=Matrix(((0,1,0,0),(1,0,0,0),(0,0,1,0),(0,0,0,1))) @ obj.matrix_world
for side,x in enumerate((33.,35.45)):
    member(f'CourtStairHandrail_{side}','SiteStairs',(x,89.7,1.05),(x,95.7,4.05),.04,.04,(1,0,0))
    for j in range(21):
        y=89.7+j*.30;z=j*.15
        B(f'CourtStairBaluster_{side}_{j}','SiteStairs',x-.0125,x+.0125,y-.0125,y+.0125,z,z+1.05)

# Flat roof parapets and three sparse sheet-metal plant housings.
for j,x in enumerate((.55,17.23,36.55,53.23)):
    B(f'ParapetLong_{j}','Roof/Parapets',x,x+.22,.77,113.23,18.,18.45)
for j,y in enumerate((.55,113.23)):
    B(f'ParapetEnd_{j}','Roof/Parapets',.55,53.45,y,y+.22,18.,18.45)
for j,(xc,yc,w,l,h) in enumerate(((8.5,20.,5.4,10.8,4.8),(45.5,84.,5.4,10.8,4.8),(27.,6.,9.,6.,2.1))):
    a,b,c,d=xc-w/2,xc+w/2,yc-l/2,yc+l/2
    B(f'PlantPlinth_{j}','Roof/Plant',a,b,c,d,18.,18.2)
    # Chamfered lower metal transition; radii derived from the column catalogue.
    if j<2:
        prism_y(f'PlantClad_{j}','Roof/Plant',c,d,[(a+.60,18.2),(b-.60,18.2),(b-.18,18.38),(b,18.8),(b,18.2+h),(a,18.2+h),(a,18.8),(a+.18,18.38)])
    else: B(f'PlantClad_{j}','Roof/Plant',a,b,c,d,18.2,18.2+h)
    for k,(u,v) in enumerate(g2.columns(a,b,.45)):
        B(f'PlantSeam_{j}_{k}','Roof/Plant',u,u+.018,c-.018,c,18.2,18.2+h)
    for k in range(int(h/.30)):
        B(f'PlantLouvre_{j}_{k}','Roof/PlantLouvres',a,b,d,d+.065,18.35+k*.30,18.43+k*.30)
for wing,x in enumerate((9.,45.)):
    for j,y in enumerate((30.,96.)): B(f'RoofDrain_{wing}_{j}','Roof/Drains',x-.15,x+.15,y-.15,y+.15,18.,18.025)

# Material graph carries actual glass transmission into .blend and Cycles.
glass_material=bpy.data.materials.new('Transparent architectural glass')
glass_material.use_nodes=True
shader=glass_material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(.47,.58,.59,1)
shader.inputs['Transmission Weight'].default_value=1.
shader.inputs['Roughness'].default_value=.04
for obj in bpy.data.objects:
    if obj.type=='MESH' and 'Glass' in obj.name: obj.data.materials.append(glass_material)
print(f'Built Arrhenius v01: {len([o for o in bpy.data.objects if o.type=="MESH"])} elements; 19x6 grid; five occupied levels; roof {ROOF_Z}m')
