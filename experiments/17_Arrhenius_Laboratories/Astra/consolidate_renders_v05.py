"""Consolidate disjoint Workbench batches after both renderer processes finish."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
records=[]
for batch,numbers in [('a',list(range(5,23))),('b',list(range(23,38))+list(range(41,45)))]:
    for number in numbers:
        source=HERE/f'render_batch_v05_{batch}_view_{number:02d}.png'
        target=HERE/f'experiment_17_astra_v05_blender_view_{number:02d}.png'
        assert source.exists(),source
        assert not target.exists(),f'Refusing to overwrite completed view {target.name}'
        source.replace(target)
        records.append({'batch':batch,'view':number,'file':target.name})
(HERE/'render_batches_v05.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'Consolidated {len(records)} disjoint Workbench images; overview01-04 retained.')
