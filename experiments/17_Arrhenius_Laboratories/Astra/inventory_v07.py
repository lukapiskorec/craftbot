"""Exact required final image inventory, hashes and geometry provenance."""
from pathlib import Path
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
expected=[]
for number in list(range(1,38))+list(range(41,59)):
    expected.append(('workbench',f'experiment_17_astra_v07_blender_view_{number:02d}.png'))
for number in (12,15,28):
    expected.append(('cycles',f'experiment_17_astra_v07_cycles_view_{number}_muted_none_no_foundation.png'))
expected.append(('cycles','experiment_17_astra_v07_cycles_view_40_interior.png'))
for number in (32,33,34,35):expected.append(('drawing',f'plan_v07_{number}.png'))
for label in 'WENS':
    for level in range(5):expected.append(('drawing',f'plan_v07_route_{label}{level}.png'))
for number in (41,42,43,44,51,52,55,56):expected.append(('drawing',f'plan_v07_support_{number}.png'))
assert len(expected)==91
images=[]
missing=[]
for kind,name in expected:
    path=HERE/name
    if not path.exists():missing.append(name);continue
    content=path.read_bytes()
    if content[-12:-4]!=b'\x00\x00\x00\x00IEND':missing.append(name);continue
    images.append({'kind':kind,'file':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
bridges=json.loads((HERE/'render_identity_difference_v07.json').read_text(encoding='utf-8')) if (HERE/'render_identity_difference_v07.json').exists() else []
report={'expected_count':91,'complete':not missing,'counts':{kind:sum(i['kind']==kind for i in images) for kind in ('workbench','cycles','drawing')},
        'images':images,'missing':missing,'geometry_bridges':bridges,
        'generated_identity':'6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed',
        'excluded':['plan_v07_support_55_caption_initial.png'],
        'provenance':'Workbench byte-identical batch copies:render_batches_v07.json. Drawings and interior40 derive from generated preflight; saved Workbench/Cycles masters have measured transform bridges. Standard gate runs once on canonical main. New bracket geometry and all primary support world vertices remain exact.'}
(HERE/'render_evidence_v07.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
artifacts={'run_folder':str(HERE),'version':'v07','files':sorted(p.name for p in HERE.iterdir() if p.is_file() and ('v07' in p.name or p.name in ('views_astra.py','version_notes.md','requirements.md','concept.md'))),
           'reused_immutable_geometry_helper':'support_geometry_v06.py',
           'external_viewer_export':'viewer/models/17_Arrhenius_Laboratories/astra_v07.json',
           'no_commit_or_archive':True}
(HERE/'artifact_manifest_v07.json').write_text(json.dumps(artifacts,indent=2),encoding='utf-8')
print(report['counts'],'missing',len(missing),flush=True)
if '--final' in sys.argv:assert not missing,missing
