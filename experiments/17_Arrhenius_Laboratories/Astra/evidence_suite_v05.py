"""Run current geometry circulation evidence and actual-mesh drawings."""
from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
for name in ('check_public_routes','check_headroom','check_routes','verify_route_envelopes','draw_plans','draw_support_sections'):
    print('EVIDENCE START '+name,flush=True)
    runpy.run_path(str(HERE/(name+'_v05.py')),run_name='__main__')
    print('EVIDENCE COMPLETE '+name,flush=True)
