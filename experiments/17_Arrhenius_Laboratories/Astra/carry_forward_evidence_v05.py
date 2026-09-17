"""Bind unchanged prior structural evidence to verified v05 member identity."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'retained_v05.json').read_text())
assert manifest['retained']==29870 and len(manifest['changed'])==6
assert all(n.startswith(('SouthClosure_West','SouthClosure_East')) for n in manifest['changed'])
counts=Counter(re.sub(r'_[0-9].*','',n) for n in manifest['added'])
rows=[manifest['geometry'],
      'Retention regression compares exact world-vertex signatures of every original member against immutable v04.',
      '29,870 of 29,876 original members are bit-identical. Only six buried metal weather-return pieces were trimmed; all primary frame, slabs, cores, foundations, internal stairs, insert joints, facade brackets and walking surfaces are unchanged.',
      'The following geometric evidence therefore carries forward by exact member identity. These are retained v04 measurements verified unchanged, not newly rerun or counted as separate v05 tests.']
for filename,meaning in [
    ('supports_v04.txt','250 full-footprint seats; 866 ordinary +8 reduced +2 alternate beam cases; 22 local connection faces; 8 core-base unions; rim/foundation paths'),
    ('insert_joint_followup_v04.txt','45 internal integral slab interfaces:36 level1 +9 roof; full13.8749976158m2 concrete face coverage and0.40m support band beyond; kept separate from67 horizontal-seat cases')]:
    path=HERE/filename
    content=path.read_text(encoding='utf-8')
    assert '8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657' in content,filename
    rows += [f'{filename}: {meaning}',f'  report SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}']
rows += ['Current v05 checks: completion_v05.txt reruns4534 ordinary slab ends plus261 intended200mm seats and all new support interfaces; structural_followup_v05.txt rechecks actual core/diaphragm interfaces and insert/foundation context.',
         'south_v05.txt separately repeats57 bracket contacts and primary14,056-member signature comparison against v04; rim_contacts_v05.txt repeats16 rim/header groups. Route/headroom/public envelopes use current complete v05 geometry.',
         'Eight0.065m2 reduced corbel seats retain18.75% area reduction; no capacity-equivalence claim.',
         'Insert is continuous cast-integral reinforced concrete at its45 internal slab lines and0.16m2 beam-column faces; reinforcement development, shear/moment capacity, anchors, soil, diaphragm forces and section sizing remain inferred.',
         'ADDED OBJECT FAMILIES:']
rows += [f'{family}: {count}' for family,count in sorted(counts.items())]
rows += ['BURIED CLOSURE EXCEPTIONS (all other original objects unchanged):']
rows += [f'{c["name"]}: removed {c["removed_volume_m3"]:.9f}m3 at {c["removed_bounds"]}; {c["remaining_pieces"]} remaining fitted pieces' for c in manifest['closure_changes']]
(HERE/'carried_evidence_v05.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows))
