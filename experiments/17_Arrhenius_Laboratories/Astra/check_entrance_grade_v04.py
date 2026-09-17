"""Read-only inherited entrance and grade-route boundary evidence."""
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
rows=[]
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    if not obj.name.startswith(('SouthGround','EntranceDoor','Column_','CourtStair','Retaining','NorthTerrace','CourtPathEast')):continue
    p=[obj.matrix_world@v.co for v in obj.data.vertices]
    b=tuple(value for a in range(3) for value in (min(v[a] for v in p),max(v[a] for v in p)))
    if obj.name.startswith(('SouthGround','EntranceDoor','Column_')) and not(b[1]>25.7 and b[0]<28.3 and b[3]>5.8 and b[2]<6.4 and b[4]<2.4):continue
    rows.append(f'{obj.name}: {b}')
(HERE/'entrance_grade_boundary_v04.txt').write_text('\n'.join(rows),encoding='utf-8')
print('\n'.join(rows),flush=True)
