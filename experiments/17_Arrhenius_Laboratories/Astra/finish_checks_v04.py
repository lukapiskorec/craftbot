from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
for name in ('verify_route_envelopes','check_supports','check_rims','draw_plans'):
    print('EVIDENCE START '+name,flush=True)
    runpy.run_path(str(HERE/(name+'_v04.py')),run_name='__main__')
    print('EVIDENCE COMPLETE '+name,flush=True)
