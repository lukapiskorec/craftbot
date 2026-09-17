"""Write final actual-mesh plan/section drawings from the loaded snapshot."""
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
for stem in ('draw_plans','draw_support_sections'):
    runpy.run_path(str(HERE/f'{stem}_v07.py'),run_name='__main__')
