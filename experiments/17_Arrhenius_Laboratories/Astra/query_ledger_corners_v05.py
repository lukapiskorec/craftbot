"""Read-only evidence of retained weather-closure obstruction at ledger corners."""
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH':continue
    ps=[o.matrix_world@v.co for v in o.data.vertices]
    b=tuple(v for k in range(3) for v in (min(p[k] for p in ps),max(p[k] for p in ps)))
    if any(min(b[k+1],c[k+1])-max(b[k],c[k])<1e-6 for k in (0,2,4) for c in [(0.54,.59,.30,.50,10.35,10.55)]):continue
    rows.append((o.name,b))
(HERE/'ledger_corner_query_v05.txt').write_text('\n'.join(map(str,rows)),encoding='utf-8')
print('\n'.join(map(str,rows)))
