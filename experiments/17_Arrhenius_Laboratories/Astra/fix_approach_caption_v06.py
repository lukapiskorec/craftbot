"""Correct omitted-earth wording only, without changing drawing geometry."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ('draw_plans_v06.py','plan_v06_35.svg','plan_v06_35.html'):
    path=HERE/name
    source=path.read_text(encoding='utf-8').replace('150mm LAWN STEP','150mm STEP TO UNMODELED GROUND')
    path.write_text(source,encoding='utf-8')
