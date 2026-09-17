"""Capped actual-mesh support sections, SVG for native GDI+ rasterization."""
from pathlib import Path
import html
import runpy
import bpy
HERE=Path(__file__).resolve().parent

def hull(points):
    points=sorted(set(points));out=[]
    for seq in (points,points[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and (half[-1][0]-half[-2][0])*(p[1]-half[-2][1])-(half[-1][1]-half[-2][1])*(p[0]-half[-2][0])<=1e-10:
                half.pop()
            half.append(p)
        out.extend(half[:-1])
    return out

identity=runpy.run_path(str(HERE/'snapshot_v07.py'))['identity']()
meshes=[(o,[o.matrix_world@v.co for v in o.data.vertices]) for o in bpy.data.objects if o.type=='MESH']
sections=[
    ('41',34.3,(89.1,96.7,-1.4,3.5),'Court stair: retained walking surfaces on stepped-top concrete waist',
     ['19 full tread underside seats; 20 rises x 150mm retained.',
      'Bottom seat: 200mm / 0.49m2 onto footing; ground is unmodeled.',
      'Landing: separate 0.44m2 lower ledge and 0.05m2 upper corbel seats.']),
    ('42',34.3,(95.3,107.7,-1.5,3.6),'Terrace: retained construction; earth/base deliberately omitted',
     ['Actual concrete wall seats; remaining earth-bearing footprint unmodeled.',
      'North wall stops 30mm before glazing; 30mm slab edge is a cantilever.',
      'Retained strip footings terminate at an unmodeled founding boundary.']),
    ('43',12.,(113.1,114.5,2.35,3.85),'North slab end: added 200mm seat on integral beam-edge ledger',
     ['Existing slab end y113.70; retained beam begins y113.80.',
      'Ledger y113.50..113.80; root lies in retained beam concrete.',
      'Section through level 1; same support fitted at levels 1-5.']),
    ('44',12.,(-.4,1.,9.55,11.05),'South slab end: added 200mm seat on integral beam-edge ledger',
     ['Existing slab begins y0.30; retained beam ends y0.20.',
      'Ledger y0.20..0.50; root lies in retained beam concrete.',
      'Section through level 3; same support fitted at levels 3-5.']),
    ('51',35.40,(101.2,102.8,-.5,3.3),'Terrace wall: exact concrete fit below and above rotated shoulder',
     ['Retained wall envelope stays complete through the column station.',
      'Existing corbel fills only its actual intersection with the wall.',
      'Original footing and terrace levels; no replacement soil geometry.']),
    ('52',35.40,(95.1,96.7,1.9,3.3),'Court landing: upper plate bears on actual rotated corbel',
     ['Landing walking top remains 3.00m; full underside support at 2.85m.',
      'Upper cap underside at 2.70m: 0.05m2 corbel seat.',
      'Separate lower plate bears on 0.44m2 ledge at 2.50m.']),
]
sections += [
    ('55',21.20,(11.90,12.85,3.20,3.75),'Upper CourtSouth attachment: actual steel and concrete section',
     ['Two discrete connectors per panel; 250mm slab-to-panel gap.',
      'End plates 10mm; web 10mm; all upper pieces 100mm high.',
      'Vertical anchor interfaces 0.010m2; weld interfaces 0.001m2; capacity unverified.']),
    ('56',21.20,(11.90,12.85,-.40,.45),'Ground CourtSouth attachment: continuous stepped web',
     ['Root plate -0.15..0.00m; receiver 0.00..0.15m; web -0.15..0.15m.',
      'Vertical anchor interfaces 0.015m2; weld interfaces 0.0015m2.',
      'Real ground slab bears 200mm on GradeBeam; earth remains unmodeled.']),
]
for number,plane,extents,title,notes in sections:
    ya,yb,za,zb=extents
    scale=min(1160/(yb-ya),640/(zb-za));ox=70;oy=760
    def screen(p):return ox+(p[0]-ya)*scale,oy-(p[1]-za)*scale
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="1000" viewBox="0 0 1300 1000">',
         '<defs><clipPath id="drawing"><rect x="65" y="100" width="1170" height="665"/></clipPath></defs>',
         '<rect x="0" y="0" width="1300" height="1000" fill="#ffffff"/>',
         f'<text x="55" y="45" font-size="23" font-family="Arial">{html.escape(title)}</text>',
         f'<text x="55" y="78" font-size="16" font-family="Arial">Actual mesh section x={plane:.2f}m. Grey retained, blue fitted support; earth omitted.</text>',
         '<g clip-path="url(#drawing)">']
    for obj,ps in meshes:
        if min(p.x for p in ps)>plane+1e-6 or max(p.x for p in ps)<plane-1e-6:
            continue
        if max(p.y for p in ps)<ya or min(p.y for p in ps)>yb or max(p.z for p in ps)<za or min(p.z for p in ps)>zb:
            continue
        points=[]
        for edge in obj.data.edges:
            a,b=(ps[i] for i in edge.vertices)
            if abs(a.x-plane)<1e-6:points.append((a.y,a.z))
            if min(a.x,b.x)<plane<max(a.x,b.x):
                t=(plane-a.x)/(b.x-a.x);p=a+t*(b-a);points.append((p.y,p.z))
        poly=hull(points)
        if len(poly)<3:continue
        name=obj.name
        color='#c8c6bf'
        if name.startswith(('PerimeterLedger','CourtWaist','CourtLanding','CourtStairFooting','TerraceWall','TerraceFooting')):color='#82afc0'
        if name.startswith(('TerraceFill','TerraceBase','TerraceSubsoil','CourtSubsoil')):color='#c1a77e'
        if 'Glass' in name:color='#a8d8e2'
        if name.startswith('CourtFacadeBracket_'):color='#82afc0'
        coords=' '.join(f'{x:.3f},{y:.3f}' for x,y in map(screen,poly))
        svg.append(f'<polygon points="{coords}" fill="{color}" stroke="#303030" stroke-width="1"><title>{html.escape(name)}</title></polygon>')
    svg.append('</g>')
    for i,note in enumerate(notes):
        svg.append(f'<text x="55" y="{810+32*i}" font-size="19" font-family="Arial">{html.escape(note)}</text>')
    svg.append('<text x="55" y="935" font-size="16" font-family="Arial">Inferred construction geometry; reinforcement, joints, soil and capacities are not calculated.</text>')
    svg.append('</svg>')
    (HERE/f'plan_v07_support_{number}.svg').write_text('\n'.join(svg),encoding='utf-8')
(HERE/'support_sections_v07.txt').write_text(identity+'\nActual capped section SVGs41-44/51/52/55/56; native rasterizer produces PNGs.\n',encoding='utf-8')
