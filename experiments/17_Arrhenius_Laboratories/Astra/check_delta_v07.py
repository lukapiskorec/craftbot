"""Exact retention of v06 and local SAT for only added facade hardware."""
from pathlib import Path
import json
import runpy
import sys
import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
from check_overlaps import hull, penetration
import layers

def snapshot():
    return {o.name: {'local': [tuple(v.co) for v in o.data.vertices],
                     'world': [tuple(o.matrix_world @ v.co) for v in o.data.vertices],
                     'matrix': [tuple(row) for row in o.matrix_world],
                     'faces': [tuple(p.vertices) for p in o.data.polygons],
                     'collections': sorted(c.name for c in o.users_collection)}
            for o in bpy.data.objects if o.type == 'MESH'}

frozen = bpy.data.filepath
current = snapshot()
identity = runpy.run_path(str(HERE / 'snapshot_v07.py'))['identity']()
bpy.ops.wm.open_mainfile(filepath=str(HERE / 'preflight_v06.blend'))
baseline = snapshot()
baseline_identity = runpy.run_path(str(HERE / 'snapshot_v06.py'))['identity']()
assert '523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416' in baseline_identity
removed = sorted(baseline.keys() - current.keys())
changed = sorted(n for n in baseline.keys() & current.keys() if baseline[n] != current[n])
added = sorted(current.keys() - baseline.keys())
assert not removed and not changed, (removed, changed)
assert len(added) == 180 and all(n.startswith('CourtFacadeBracket_') for n in added), added
bpy.ops.wm.open_mainfile(filepath=frozen)
all_hulls = [(o.name, hull(o)) for o in bpy.data.objects if o.type == 'MESH']
added_set = set(added)
hits = []
for name, a in all_hulls:
    if name not in added_set:
        continue
    assert layers.classify('17', 'Facade/SteelFrames', name) == 'fixtures'
    for other, b in all_hulls:
        if other == name or (other in added_set and other < name):
            continue
        if any(min(a[4][k], b[4][k]) - max(a[3][k], b[3][k]) < .001 for k in range(3)):
            continue
        depth = penetration(a, b)
        if depth > .001:
            hits.append((depth, name, other))
report = {'identity': identity, 'baseline': baseline_identity, 'retained_exactly': len(baseline),
          'removed': removed, 'changed': changed, 'added': added, 'local_pairs': hits,
          'fixture_count': len(added), 'rule': 'Every prior local/world vertex, transform, face and collection is exact; SAT covers all added objects against all meshes.'}
(HERE / 'delta_v07.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(identity, flush=True)
print(f'EXACT RETENTION {len(baseline)}; added {len(added)} fixtures; local pairs {len(hits)}', flush=True)
assert not hits, hits
