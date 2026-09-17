"""Apply independent review wording to the existing actual-mesh section."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
path=HERE/'plan_v07_support_55.svg'
source=path.read_text(encoding='utf-8')
assert 'inferred capacity' in source
path.write_text(source.replace('inferred capacity','capacity unverified'),encoding='utf-8')
