"""Run requested bounded v07 check modules against the loaded snapshot."""
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
names = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['check_delta','check_brackets','check_panel_roots','verify_route_envelopes','check_public_routes']
for name in names:
    print('VERIFY START '+name,flush=True)
    runpy.run_path(str(HERE/f'{name}_v07.py'),run_name='__main__')
    print('VERIFY COMPLETE '+name,flush=True)
