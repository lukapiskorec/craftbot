"""Derive new v05 diagnostic sources; never overwrite rendered versions."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
for name in ('snapshot', 'check_routes', 'verify_route_envelopes',
             'check_headroom', 'check_supports', 'check_rims', 'check_south',
             'check_public_routes', 'draw_plans', 'rasterize_plans',
             'render_interior', 'structural_followup'):
    destination = HERE / f'{name}_v05.py'
    if destination.exists():
        raise RuntimeError(f'Refusing to overwrite {destination.name}')
    source = (HERE / f'{name}_v04.py').read_text(encoding='utf-8').replace('v04', 'v05')
    if name == 'check_south':
        source = source.replace('preflight_v03.blend', 'preflight_v04.blend').replace('} v03;', '} v04;')
    if name == 'structural_followup':
        source = source.replace("('Beam_','EdgeBeam','StairHeader'", "('PerimeterLedger','Beam_','EdgeBeam','StairHeader'")
    destination.write_text(source, encoding='utf-8')
print('Prepared isolated v05 diagnostics from immutable v04.')
