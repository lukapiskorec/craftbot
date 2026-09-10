"""Workbench line masks matching views_cycles_line_source.py exactly."""
from views_cycles_study import FRAME_HIDE

RESOLUTION = (3072, 3072)
VIEWS = [
    dict(name="clad", azim=305, elev=-25, margin=1.16,
         hide=["Foundation"], fit_hide=[]),
    dict(name="frame", azim=225, elev=-30, margin=1.16,
         hide=FRAME_HIDE + ["Foundation"], fit_hide=FRAME_HIDE),
]
