"""Concept10: inferred thin welded/anchored CourtSouth facade fixtures."""
from pathlib import Path
import sys
import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
from craftbot_lib import mesh_prism

# Designer concept10.1; all hardware dimensions are architectural inference.
CENTRES = {1:(21.20,22.70),2:(24.20,25.70),3:(27.60,28.60),4:(30.20,31.70),5:(33.20,34.70)}
PLATE_WIDTH, STEEL_THICKNESS, STOREY = .10, .01, 3.6

def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return tuple(value for axis in range(3) for value in (min(p[axis] for p in points), max(p[axis] for p in points)))

slabs = [(o.name, bounds(o)) for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('FloorSlab_')]

def steel(name, x0, x1, y0, y1, z0, z1):
    outline = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    return mesh_prism(name, 'Facade/SteelFrames', [(x,y,z0) for x,y in outline], [(x,y,z1) for x,y in outline])

for bay, xx in CENTRES.items():
    for f in range(6):
        level = STOREY * f
        panel = bpy.data.objects[f'Panel_CourtSouth_{bay}_' + ('Base' if f == 0 else str(f-1))]
        receiver_y = bounds(panel)[2]
        root_z = (-.15,0.) if f == 0 else (level-.20,level-.10)
        panel_z = (0.,.15) if f == 0 else root_z
        for side, x in enumerate(xx):
            root_planes = [b[3] for name,b in slabs if name.startswith(f'FloorSlab_{f}_')
                           and b[0] <= x-.05 and b[1] >= x+.05 and abs(b[3]-12.30) < 2e-5]
            assert root_planes and max(root_planes)-min(root_planes) < 1e-8, (bay,f,x,root_planes)
            root_y = root_planes[0]
            assert abs(receiver_y-root_y-.25) < 2e-5
            prefix = f'CourtFacadeBracket_{bay}_{f}_{side}_'
            steel(prefix+'Root',x-.05,x+.05,root_y,root_y+STEEL_THICKNESS,*root_z)
            steel(prefix+'Receiver',x-.05,x+.05,receiver_y-STEEL_THICKNESS,receiver_y,*panel_z)
            steel(prefix+'Web',x-.005,x+.005,root_y+STEEL_THICKNESS,receiver_y-STEEL_THICKNESS,root_z[0],panel_z[1])

assert sum(o.type == 'MESH' and o.name.startswith('CourtFacadeBracket_') for o in bpy.data.objects) == 180
print('Concept10: 60 discrete CourtSouth bracket assemblies / 180 steel fixtures', flush=True)
