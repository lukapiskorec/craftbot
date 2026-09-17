"""Point containment screen for approved terrace walls outside actual corbels."""
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
objects=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('TerraceWall','Corbel','Column_','InsertColumn','RetainingWall'))]
def contains(obj,point):
    vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
    normals=obj.matrix_world.to_3x3().inverted().transposed()
    return all((point-vertices[p.vertices[0]]).dot(normals@p.normal)<=1e-6 for p in obj.data.polygons)
lines=[]
for x in (18.60,35.40):
    for y in (96.40,101.80,102.20):
        for z in (1.00,2.72):
            point=Vector((x,y,z));hits=[o.name for o in objects if contains(o,point)]
            lines.append(f'Approved terrace wall point{tuple(point)}: contained by {hits}')
(HERE/'terrace_fit_probe_v06.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines),flush=True)
