"""Copy immutable v06 sources into the bounded v07 revision."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / 'experiment_17_astra_v06.py').read_text(encoding='utf-8')
source = source.replace('Astra v06.', 'Astra v07.').replace('Built Arrhenius v06:', 'Built Arrhenius v07:')
marker = "# Material graph carries actual glass transmission into .blend and Cycles."
source = source.replace(marker, "# Concept10: discrete slab-rooted CourtSouth facade fixtures.\nrunpy.run_path(os.path.join(_HERE, 'facade_brackets_v07.py'), run_name='__main__')\n\n" + marker)
(HERE / 'experiment_17_astra_v07.py').write_text(source, encoding='utf-8')
for stem in ('snapshot', 'check_panel_roots', 'check_public_routes', 'verify_route_envelopes', 'check_headroom'):
    source = (HERE / f'{stem}_v06.py').read_text(encoding='utf-8').replace('v06', 'v07')
    # Prior route polylines remain the independent fixed paths under test.
    source = source.replace("f'route_v07_", "f'route_v06_")
    if stem == 'check_panel_roots':
        source = source.replace("secondary=('Panel_'", "secondary=('CourtFacadeBracket_', 'Panel_'")
    (HERE / f'{stem}_v07.py').write_text(source, encoding='utf-8')
