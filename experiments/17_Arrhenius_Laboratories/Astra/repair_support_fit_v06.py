"""Place the9.7 branch inside the shared local fitter, not closure rewriting."""
from pathlib import Path
path=Path(__file__).with_name('support_geometry_v06.py')
source=path.read_text(encoding='utf-8')
start=source.index("            if name.startswith(('CourtLandingSupport'")
end=source.index('            ring=',start)
branch=source[start:end]
source=source[:start]+source[end:]
position=source.index('            ring=',source.index('    def fitted('))
source=source[:position]+branch+source[position:]
path.write_text(source,encoding='utf-8')
