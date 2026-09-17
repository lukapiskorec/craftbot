"""Create the v05 generator from immutable v04 with one support-completion call."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
destination=HERE/'experiment_17_astra_v05.py'
assert not destination.exists()
source=(HERE/'experiment_17_astra_v04.py').read_text(encoding='utf-8').replace('v04','v05')
anchor='# Material graph carries actual glass transmission into .blend and Cycles.'
addition='''# Concept8 support completion is append-only: all inherited objects remain
# identical. Local helper is versioned alongside this generator.
import runpy
runpy.run_path(os.path.join(_HERE, 'support_geometry_v05.py'), run_name='__main__')

'''
assert source.count(anchor)==1
destination.write_text(source.replace(anchor,addition+anchor),encoding='utf-8')
