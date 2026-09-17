"""Final selected image inventory; excludes the unselected white presentation trial."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
for n in (53,54):
    source=HERE/f'experiment_17_astra_v06_detail_view_{n}.png'
    (HERE/f'experiment_17_astra_v06_blender_view_{n}.png').write_bytes(source.read_bytes())
wb=[HERE/f'experiment_17_astra_v06_blender_view_{n:02}.png' for n in list(range(1,38))+list(range(41,55))]
cycles=[HERE/f'experiment_17_astra_v06_cycles_view_{n}_muted_none_no_foundation.png' for n in (12,15,28)]
cycles.append(HERE/'experiment_17_astra_v06_cycles_view_40_interior.png')
plans=sorted(HERE.glob('plan_v06_*.png'))
assert len(plans)==30
selected=wb+cycles+plans
assert all(p.exists() for p in selected),[p.name for p in selected if not p.exists()]
assert len(selected)==85
raw=(HERE/'render_v06.log').read_bytes()
gate=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
assert 'OVERLAP CHECK: 29976 members, 0 penetrating pairs (> 1 mm)' in gate
assert 'CONTACT CHECK: 29976 members, 0 floating (nothing within 2 mm)' in gate
report={'counts':{'workbench':len(wb),'cycles':len(cycles),'capped_drawings':len(plans),'selected_total':len(selected)},
        'standard_gate':{'members':29976,'pairs':0,'floating':0,'overlap_tolerance_mm':1,'contact_tolerance_mm':2,'source':'render_v06.log; unmodified stock tools, main saved master'},
        'geometry_bridge':json.loads((HERE/'render_identity_difference_v06.json').read_text()),
        'interior_settings':json.loads((HERE/'interior_v06_40_settings.json').read_text()),
        'images':[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in selected],
        'excluded_trials':['experiment_17_astra_v06_cycles_view_12_none_no_foundation.png'],
        'presentation_corrections':'View52 is occluded and is superseded for landing-detail judgment by53. View50 retains historical approach-slab misclassification;54 shows corrected fixture taxonomy. Both originals remain inventoried for honest version history.',
        'limitations':'Images and zero-pair/contact gates do not resolve the explicit CourtSouth facade attachment gap. See independent structural review and Builder notes.'}
(HERE/'render_evidence_v06.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['counts'])
