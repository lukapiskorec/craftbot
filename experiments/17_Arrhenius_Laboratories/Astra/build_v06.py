"""Build and freeze v06 before bounded correction and full regression checks."""
from pathlib import Path
import json
import runpy
import bpy

HERE=Path(__file__).resolve().parent
model=runpy.run_path(str(HERE/'experiment_17_astra_v06.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v06.blend'))
(HERE/'side_panel_changes_v06.json').write_text(json.dumps(model['SIDE_PANEL_CHANGES'],indent=2),encoding='utf-8')
print(runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),flush=True)
