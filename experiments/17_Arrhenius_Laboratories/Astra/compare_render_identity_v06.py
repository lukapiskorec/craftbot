"""Diagnose saved render transforms against the checked support snapshot."""
from pathlib import Path
import json
import runpy
import bpy
HERE=Path(__file__).resolve().parent
def snapshot():
    return {o.name:{'vertices':[tuple(o.matrix_world@v.co) for v in o.data.vertices],
                    'matrix':[tuple(row) for row in o.matrix_world],
                    'local':[tuple(v.co) for v in o.data.vertices]}
            for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(HERE/'preflight_v06.blend'))
before=snapshot()
preflight_identity=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
reports=[]
master=None
for filename in ('experiment_17_astra_v06_blender.blend','experiment_17_astra_v06_cycles.blend','experiment_17_astra_v06_detail.blend'):
    bpy.ops.wm.open_mainfile(filepath=str(HERE/filename))
    after=snapshot();changes=[]
    if master is None:master=after
    assert before.keys()==after.keys()
    for name,a in before.items():
        b=after[name]
        if a!=b:
            assert len(a['vertices'])==len(b['vertices'])
            delta=max(abs(x-y) for p,q in zip(a['vertices'],b['vertices']) for x,y in zip(p,q))
            changes.append({'name':name,'max_axis_delta_m':delta,'local_unchanged':a['local']==b['local'],
                            'matrix_unchanged':a['matrix']==b['matrix'],
                            'before_matrix':a['matrix'],'after_matrix':b['matrix']})
    identity=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
    assert all(c['local_unchanged'] for c in changes)
    assert all(c['max_axis_delta_m']<4e-6 for c in changes)
    assert all(c['name'].startswith(('CourtStair_','CourtStairHandrail_','InsertInclineRail_','SouthInclineRail_'))
               for c in changes if c['max_axis_delta_m']>0)
    master_changes=[]
    for name,a in master.items():
        b=after[name]
        if a['vertices']!=b['vertices']:
            delta=max(abs(x-y) for p,q in zip(a['vertices'],b['vertices']) for x,y in zip(p,q))
            master_changes.append({'name':name,'max_axis_delta_m':delta})
    assert all(c['name'].startswith(('CourtStairHandrail_','InsertInclineRail_')) and c['max_axis_delta_m']<4e-6 for c in master_changes),master_changes
    reports.append({'file':filename,'identity':identity,'reference_identity':preflight_identity,'changes':changes,'world_changed_count':sum(c['max_axis_delta_m']>0 for c in changes),'max_axis_delta_m':max((c['max_axis_delta_m'] for c in changes),default=0),'differences_from_master':master_changes})
    print(filename,len(changes),'changed; max delta',reports[-1]['max_axis_delta_m'],flush=True)
(HERE/'render_identity_difference_v06.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
