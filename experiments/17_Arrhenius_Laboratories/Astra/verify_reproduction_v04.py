"""Build the complete generator and compare actual geometry to the saved patch."""
from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
expected=(HERE/'headroom_v04.txt').read_text(encoding='utf-8').splitlines()[0].split('=')[1].split(';')[0]
runpy.run_path(str(HERE/'experiment_17_astra_v04.py'),run_name='__main__')
report=runpy.run_path(str(HERE/'snapshot_v04.py'))['identity']()
actual=report.split('=')[1].split(';')[0]
report+='\nFull generator matches completed snapshot: '+str(actual==expected)+'\n'
(HERE/'reproduction_v04.txt').write_text(report,encoding='utf-8');print(report,flush=True)
assert actual==expected,(actual,expected)
