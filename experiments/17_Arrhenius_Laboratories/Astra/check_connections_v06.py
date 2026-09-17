"""Read-only general corbel roots, facade continuity and insert joint supplement."""
from pathlib import Path
from collections import Counter,deque
import runpy
HERE=Path(__file__).resolve().parent
insert=runpy.run_path(str(HERE/'insert_joint_followup_v06.py'))
cache=insert['cache'];faces=cache['faces'];contacts=cache['contacts']
lines=[cache['lines'][0]]
assert len(insert['rows'])==45 and all(r[5] and r[6] for r in insert['rows'])
assert sum(r[-1] for r in cache['insert_ends'])==67
lines.append('Insert:45 full vertical interfaces and adjoining400mm bands pass;67 separate horizontal end-strip cases pass.')
root_areas={};missing=[]
for name in faces:
    if not name.startswith(('CorbelWing_','CorbelSeat_')):continue
    column='Column_'+name.split('_')[1]
    patches=contacts(name,lambda n:n==column)
    root_areas[name]=sum(p[4] for p in patches)
    if root_areas[name]<.01:missing.append(name)
assert not missing,missing
for family in ('CorbelWing','CorbelSeat'):
    rows=[a for n,a in root_areas.items() if n.startswith(family+'_')]
    lines.append(f'{family}: {len(rows)} finite shaft roots; minimum actual opposed area {min(rows):.12f}m2.')
panels=[n for n in faces if n.startswith('Panel_')]
primary=('Column_','Corbel','Beam_','FloorSlab_','PerimeterLedger','GradeBeam','Footing','Pedestal','CoreWall','RoofSlab','InsertSlab','Retaining')
graph={n:set() for n in panels};roots={};families=Counter()
for name in panels:
    for other,axis,sign,plane,area,poly in contacts(name,lambda n:n.startswith(primary+('Panel_',))):
        if area<1e-5:continue
        if other.startswith('Panel_'):graph[name].add(other)
        else:roots.setdefault(name,[]).append((other,area));families[other.split('_')[0]]+=1
reached=set(roots);queue=deque(roots)
while queue:
    name=queue.popleft()
    for other in graph[name]:
        if other not in reached:reached.add(other);queue.append(other)
unrooted=sorted(set(panels)-reached)
lines.append(f'Facade panels: {len(panels)} pieces; {len(roots)} direct positive-area primary-concrete interfaces; {len(reached)} connected through finite panel interfaces; unresolved {len(unrooted)}.')
lines.append('Primary interface family counts: '+repr(dict(families)))
lines.append('Unresolved panel names: '+repr(unrooted))
for name in unrooted:
    lines.append(name+' bounds '+repr(cache['bounds'][name])+' all finite contacts '+repr([(p[0],p[1],p[4]) for p in contacts(name)]))
lines.append('Attachment/reinforcement capacities are inferred, not established by these geometric interfaces. Whole-model SAT establishes nib/primary-concrete priority over fitted infill separately.')
(HERE/'connections_v06.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines),flush=True)
assert not unrooted,unrooted
