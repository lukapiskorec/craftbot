"""Independent full generator reproduction of the append-only support snapshot."""
from pathlib import Path
import json
import runpy
HERE=Path(__file__).resolve().parent
expected=json.loads((HERE/'retained_v05.json').read_text())['geometry'].split('=')[1].split(';')[0]
runpy.run_path(str(HERE/'experiment_17_astra_v05.py'),run_name='__main__')
identity=runpy.run_path(str(HERE/'snapshot_v05.py'))['identity']()
actual=identity.split('=')[1].split(';')[0]
report=identity+'\nFull generator matches completed snapshot: '+str(actual==expected)+'\n'
(HERE/'reproduction_v05.txt').write_text(report,encoding='utf-8')
print(report,flush=True)
assert actual==expected,(actual,expected)
