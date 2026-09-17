"""Compact current evidence inventory; reports pending gates explicitly."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
changes=json.loads((HERE/'changes_v06.json').read_text())
panels=json.loads((HERE/'panel_roots_v06.json').read_text())
unresolved=panels['unresolved']
altered=set(changes['changed']+changes['deleted']+changes['added'])
assert not set(unresolved)&altered
allframes=[n for n in altered if n.startswith('Window_CourtSouth_')]
paths=[r for r in panels['paths'] if any(x in r['panel'] for x in ('PorchKeep','ShoulderFit'))]
rows=['# v06 numeric evidence checkpoint','',panels['identity'],'',
 f"- Actual v05 correspondence: {changes['unchanged']} unchanged meshes; {len(changes['changed'])} changed shared names; {len(changes['deleted'])} deleted; {len(changes['added'])} added.",
 '- Fresh factory-startup generation exactly reproduces the29,976-mesh frozen snapshot (reproduction_v06.txt).',
 '- All1,250wings and1,250seats have finite actual shaft roots; minimum.359998741151m2.866ordinary beam seats.140m2;8core-reduced.11375m2;2alternate seats freshly verified.',
 '- All45 insert integral vertical interfaces and400mm adjoining bands pass; required/covered13.874997615814m2.67horizontal insert cases remain separately classified.',
 '- 4,534 ordinary slab ends pass120mm; all261 repaired perimeter ends pass200mm. All16rim support paths,250foundation footprint seats,22local connections and8core-base unions pass.',
 '- 48continuous route envelopes pass.16CorbelSeat ceiling/route cases across4routes have minimum2.0999996185302727m within20micrometre numerical allowance;368stair regions separately minimum2.700m.',
 '- Ground boundary: no122former ground/soil/base masses; retained terrace underside184.089966431m2 requires11.399926567m2 actualconcrete plus172.690039864m2 explicitlyunmodeled earth; separate.507056778m2 northcantilever.',
 f"- All-plane facade graph roots{panels['rooted']}/{panels['panel_count']} pieces; all changed southcorner pieces resolved. Remaining{len(unresolved)} CourtSouthpieces are bit-identical to v05; {len(allframes)} CourtSouth window pieces changed by current fitting elsewhere in that family.",
 '- CourtSouth unresolved250mm slab-to-panel gap is recorded in panel_root_gaps_v06.txt:24 inherited cases and6 cases losing old timber-jamb/corbel contact after rotation, verified with glass excluded. Designer/Coordinator disposition pending. No actual support closure is claimed for those30panels.',
 '- Independent R39 actual landing/wall fit acceptance complete. Stock gate29976/0pairs/0floating passes; all85 images independently reviewed and final measured render bridge passes. Overall structural convergence remains open solely for CourtSouth30 attachments.'
]
(HERE/'evidence_checkpoint_v06.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows))
