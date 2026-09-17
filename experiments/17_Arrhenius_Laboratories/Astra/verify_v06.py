"""Current frozen-model evidence in independent bounded check modules."""
from pathlib import Path
import runpy
import sys
HERE=Path(__file__).resolve().parent
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['check_corrections','check_supports','check_completion','check_rims','check_south','check_public_routes','check_headroom','verify_route_envelopes']
for name in names:
    print('VERIFY START '+name,flush=True)
    runpy.run_path(str(HERE/f'{name}_v06.py'),run_name='__main__')
    print('VERIFY COMPLETE '+name,flush=True)
