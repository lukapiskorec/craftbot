"""Capped vector plans derived from actual frozen mesh sections; no model edits."""
from pathlib import Path
import math
import html
import bpy
import numpy as np
HERE=Path(__file__).resolve().parent
def hull(points):
    points=sorted(set(points));out=[]
    for seq in (points,points[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and (half[-1][0]-half[-2][0])*(p[1]-half[-2][1])-(half[-1][1]-half[-2][1])*(p[0]-half[-2][0])<=0:half.pop()
            half.append(p)
        out.extend(half[:-1])
    return out
meshes=[(o,[o.matrix_world @ v.co for v in o.data.vertices]) for o in bpy.data.objects if o.type=='MESH']
SPECS=[('32','West offices / corridor / laboratories',(.4,17.6,35.,56.),1,
       [(3.1,54.8,'OFFICES'),(7.7,54.8,'CORRIDOR'),(13.1,54.8,'LABORATORIES')]),
       ('33','East asymmetric rooms and ground courtyard gallery',(36.5,53.6,35.,56.),0,
       [(38.2,54.8,'GALLERY'),(42.2,54.8,'LABS'),(46.2,54.8,'CORRIDOR'),(50.7,54.8,'OFFICES')]),
       ('34','West-wing access to the courtyard insert',(7.,23.,71.,79.),1,
       [(8.,77.5,'CORRIDOR'),(13.,77.5,'LAB / APPROACH'),(18.1,77.5,'LINK'),(21.,77.5,'INSERT')])]
for level in range(5):
    for i,(label,box) in enumerate((('W',(.5,10.,56.,68.)),('E',(43.,53.5,56.,68.)),('N',(26.,49.,105.,114.)),('S',(36.3,49.,6.,18.)))):
        SPECS.append((f'route_{label}{level}',f'{label} stair — level {level} at z{3.6*level:.1f}m',box,level,[]))
for name,title,(xa,xb,ya,yb),level,labels in SPECS:
    width,height=1300,1000;scale=min(1180/(xb-xa),840/(yb-ya));ox=(width-scale*(xb-xa))/2;oy=100
    def xy(x,y):return ox+(x-xa)*scale,oy+(yb-y)*scale
    def polygon(poly,fill,stroke='none',sw=.5):
        coords=' '.join(f'{xy(x,y)[0]:.2f},{xy(x,y)[1]:.2f}' for x,y in poly)
        return f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#f4f2ed"/>',f'<text x="45" y="40" font-family="Arial" font-size="26">{html.escape(title)}</text>',f'<text x="45" y="70" font-family="Arial" font-size="15">Frozen v03 mesh | solid wall sections at floor +1.20m | inferred scale | north up</text>','<defs><clipPath id="crop"><rect x="'+str(ox)+'" y="'+str(oy)+'" width="'+str(scale*(xb-xa))+'" height="'+str(scale*(yb-ya))+'"/></clipPath></defs><g clip-path="url(#crop)">']
    z=3.6*level;sections=[]
    for obj,points in meshes:
        if max(p.x for p in points)<xa or min(p.x for p in points)>xb or max(p.y for p in points)<ya or min(p.y for p in points)>yb:continue
        if min(p.z for p in points)>z+1.2 or max(p.z for p in points)<z-.001:continue
        for face in obj.data.polygons:
            verts=[points[i] for i in face.vertices]
            if face.normal.z>.99 and all(abs(p.z-z)<.001 for p in verts):
                svg.append(polygon(hull([(p.x,p.y) for p in verts]),'#dfddd5','#c7c5bd',.4))
        cuts=[];height_cut=z+1.2
        for edge in obj.data.edges:
            p,q=(points[i] for i in edge.vertices)
            if min(p.z,q.z)<=height_cut<=max(p.z,q.z) and abs(p.z-q.z)>1e-7:
                t=(height_cut-p.z)/(q.z-p.z);cuts.append((p.x+t*(q.x-p.x),p.y+t*(q.y-p.y)))
        poly=hull(cuts)
        if len(poly)>2:
            color='#7ca3a7' if 'Glass' in obj.name else '#514d45' if obj.name.startswith(('Office','Lab','Corridor','EastGallery')) else '#807b71'
            sections.append(polygon(poly,color,'#38362f',.5))
    svg.extend(sections)
    if name.startswith('route_'):
        archive=np.load(HERE/f'{name.replace("route_","route_v03_")}.npz');path=archive['path']
        if len(path):
            coords=' '.join(f'{xy(x,y)[0]:.2f},{xy(x,y)[1]:.2f}' for x,y in path)
            svg.append(f'<polyline points="{coords}" fill="none" stroke="#39776a" stroke-opacity=".3" stroke-width="{1.2*scale}" stroke-linejoin="round" stroke-linecap="round"/>')
            svg.append(f'<polyline points="{coords}" fill="none" stroke="#145749" stroke-width="2"/>')
    svg.append('</g>')
    for x,y,text in labels:
        u,v=xy(x,y);svg.append(f'<text x="{u}" y="{v}" text-anchor="middle" font-family="Arial" font-size="13" fill="#111">{text}</text>')
    svg.append('<text x="45" y="962" font-family="Arial" font-size="15">Dark = actual capped partitions/structure; blue = glass; pale = supporting floor; green = tested 1.20m route.</text>')
    svg.append('<text x="45" y="986" font-family="Arial" font-size="13">Labels describe inferred room use. This drawing does not certify structural capacity or statutory compliance.</text></svg>')
    content=''.join(svg);(HERE/f'plan_v03_{name}.svg').write_text(content,encoding='utf-8')
    (HERE/f'plan_v03_{name}.html').write_text('<!doctype html><html><body style="margin:0">'+content+'</body></html>',encoding='utf-8')
print(f'Generated {len(SPECS)} actual-mesh capped vector plans',flush=True)
