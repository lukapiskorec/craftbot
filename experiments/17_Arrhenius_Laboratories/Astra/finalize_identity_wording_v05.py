"""Correct final documentation to the measured pairwise rounding differences."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
replacements={
    'inspection_v05.md':('Secondary batches differ from master only in two court handrails by less than0.5micrometre, giving31 changed objects relative to preflight.',
                         'Secondary batches differ from master on two court handrails by less than0.5micrometre and two insert glazing rails by at most3.814698micrometres, giving31 changed objects relative to preflight.'),
    'version_notes.md':('they differ from master only on two court handrails by less than0.5 micrometre.',
                        'they differ from master on two court handrails by less than0.5 micrometre and two insert glazing rails by at most3.814698 micrometres.'),
}
for filename,(old,new) in replacements.items():
    path=HERE/filename
    content=path.read_text(encoding='utf-8')
    assert old in content,filename
    path.write_text(content.replace(old,new),encoding='utf-8')
