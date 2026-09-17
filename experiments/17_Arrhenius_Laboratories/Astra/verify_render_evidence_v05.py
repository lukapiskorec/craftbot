"""Bind all completed render products to the frozen mesh identity."""
from pathlib import Path
import hashlib
import json
import runpy
import bpy
HERE=Path(__file__).resolve().parent
frozen=json.loads((HERE/'retained_v05.json').read_text())['geometry']
generated=frozen.split('=')[1].split(';')[0]
expected='9968993522e362026e472282a4226d99961ec4017ae27497458e024213082417'
bridge=json.loads((HERE/'render_identity_difference_v05.json').read_text())
expected_by_file={r['file']:r['identity'].split('=')[1].split(';')[0] for r in bridge}
expected_by_file['preflight_v05.blend']=generated
blend_reports=[]
for filename in ('preflight_v05.blend','experiment_17_astra_v05_blender.blend','render_batch_v05_a.blend','render_batch_v05_b.blend','experiment_17_astra_v05_cycles.blend'):
    bpy.ops.wm.open_mainfile(filepath=str(HERE/filename))
    identity=runpy.run_path(str(HERE/'snapshot_v05.py'))['identity']()
    assert identity.split('=')[1].split(';')[0]==expected_by_file[filename],identity
    blend_reports.append(identity)
workbench=[f'experiment_17_astra_v05_blender_view_{i:02d}.png' for i in list(range(1,38))+list(range(41,45))]
cycles=[f'experiment_17_astra_v05_cycles_view_{i:02d}_muted_none_no_foundation.png' for i in (12,15,28)]
cycles.append('experiment_17_astra_v05_cycles_view_40_interior.png')
plans=[f'plan_v05_{i:02d}.png' for i in range(32,36)]
plans += [f'plan_v05_route_{label}{level}.png' for label in 'WENS' for level in range(5)]
plans += [f'plan_v05_support_{i:02d}.png' for i in range(41,45)]
artifacts=[]
for name in workbench+cycles+plans:
    path=HERE/name
    assert path.exists() and path.stat().st_size>1000,name
    artifacts.append({'file':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
interior=json.loads((HERE/'interior_v05_40_settings.json').read_text())
assert expected in interior['geometry']
prior=json.loads((HERE/'interior_v04_40_settings.json').read_text())
keys=('camera','target','lens_mm','eye_height_above_level1_m','exposure_EV','world_strength','fill_strength','samples')
assert all(interior[k]==prior[k] for k in keys)
assert all(r['max_axis_delta_m']<4e-6 for r in bridge)
assert all(c['local_unchanged'] for r in bridge for c in r['changes'])
report={'geometry_hash':expected,'generated_geometry_hash':generated,'meshes':30167,'blends':blend_reports,
        'transform_roundoff_bridge':'render_identity_difference_v05.json',
        'bridge_explanation':'The render harness resets matrix_world; Blender decomposition changes93 transforms. Master has29 world-coordinate changes up to3.814697265625e-6m relative to generated geometry. Secondary batches have31 changed objects relative to generated. Relative to master they differ on two handrails below0.5micrometre and two insert glazing rails below3.82micrometres. All local meshes unchanged. Each batch has its actual identity and explicit micro-roundoff bridge; exact hash equality across batches is NOT claimed. SAT/contact ran on master rendered geometry after reset/save. Targeted court tread regression is render_support_bridge_v05.txt.',
        'workbench_count':len(workbench),'cycles_count':len(cycles),'actual_mesh_plan_count':len(plans),
        'interior_40_settings_unchanged':{k:interior[k] for k in keys},'artifacts':artifacts,
        'numeric_check_log':'render_v05.log','pair_file':'experiment_17_astra_v05_blender_pairs.txt',
        'policy':'Standard complete SAT/contact ran once on master rendered geometry. Generated support snapshot and saved render batches are bridged by per-object transform evidence; exact equality is not claimed.'}
(HERE/'render_evidence_v05.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(f'FINAL RENDER EVIDENCE: {len(workbench)} Workbench, {len(cycles)} Cycles, {len(plans)} capped plans; master hash {expected}; generated preflight and all render batches explicitly bridged; interior40 unchanged.',flush=True)
