"""Byte-identical canonical copies and exact final Workbench name inventory."""
from pathlib import Path
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
groups={'a':range(10,26),'b':list(range(26,38))+list(range(41,55)),'c':range(1,10)}
records=[]
for batch,numbers in groups.items():
    for number in numbers:
        source=HERE/f'render_batch_v07_{batch}_view_{number:02d}.png'
        target=HERE/f'experiment_17_astra_v07_blender_view_{number:02d}.png'
        if not source.exists():continue
        content=source.read_bytes()
        if content[-12:-4]!=b'\x00\x00\x00\x00IEND':continue
        if target.exists():assert target.read_bytes()==content,target.name
        else:target.write_bytes(content)
        records.append({'batch':batch,'view':number,'source':source.name,'file':target.name,'sha256':hashlib.sha256(content).hexdigest()})
expected={f'experiment_17_astra_v07_blender_view_{n:02d}.png' for n in list(range(1,38))+list(range(41,59))}
actual={p.name for p in HERE.glob('experiment_17_astra_v07_blender_view_*.png')}
assert not actual-expected,actual-expected
(HERE/'render_batches_v07.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'Workbench canonical images {len(actual)}/55; missing {sorted(expected-actual)}')
if '--final' in sys.argv:assert actual==expected,expected-actual
