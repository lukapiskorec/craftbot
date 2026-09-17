"""Independent full generator reproduction of corrected frozen v06."""
from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
expected='523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416'
runpy.run_path(str(HERE/'experiment_17_astra_v06.py'),run_name='__main__')
identity=runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()
actual=identity.split('=')[1].split(';')[0]
report=identity+'\nFull generator matches corrected frozen snapshot: '+str(actual==expected)+'\n'
(HERE/'reproduction_v06.txt').write_text(report,encoding='utf-8')
print(report,flush=True)
assert actual==expected,(actual,expected)
