"""Measure each final presentation snapshot against generated v07 geometry."""
from pathlib import Path
import json
import runpy
import sys
import bpy

HERE = Path(__file__).resolve().parent
def snapshot():
    return {o.name:{'vertices':[tuple(o.matrix_world@v.co) for v in o.data.vertices],
                    'matrix':[tuple(row) for row in o.matrix_world],
                    'local':[tuple(v.co) for v in o.data.vertices]}
            for o in bpy.data.objects if o.type=='MESH'}

bpy.ops.wm.open_mainfile(filepath=str(HERE/'preflight_v07.blend'))
before=snapshot()
before_identity=runpy.run_path(str(HERE/'snapshot_v07.py'))['identity']()
reports=[]
for filename in ('experiment_17_astra_v07_blender.blend','render_batch_v07_a.blend','render_batch_v07_b.blend','render_batch_v07_c.blend','experiment_17_astra_v07_cycles.blend'):
    if not (HERE/filename).exists() and '--partial' in sys.argv:
        continue
    bpy.ops.wm.open_mainfile(filepath=str(HERE/filename))
    after=snapshot()
    assert before.keys()==after.keys()
    changes=[]
    for name,a in before.items():
        b=after[name]
        if a==b:continue
        assert a['local']==b['local'],name
        delta=max(abs(x-y) for p,q in zip(a['vertices'],b['vertices']) for x,y in zip(p,q))
        assert delta<4e-6,(name,delta)
        if delta:
            assert name.startswith(('CourtStair_','CourtStairHandrail_','InsertInclineRail_','SouthInclineRail_')),name
        changes.append({'name':name,'max_axis_delta_m':delta,'local_unchanged':True,'matrix_unchanged':a['matrix']==b['matrix']})
    report={'file':filename,'identity':runpy.run_path(str(HERE/'snapshot_v07.py'))['identity'](),
            'reference_identity':before_identity,'changes':changes,
            'world_changed_count':sum(c['max_axis_delta_m']>0 for c in changes),
            'max_axis_delta_m':max((c['max_axis_delta_m'] for c in changes),default=0)}
    reports.append(report)
    print(filename,report['world_changed_count'],'world changes;',report['max_axis_delta_m'],'m',flush=True)
(HERE/'render_identity_difference_v07.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
