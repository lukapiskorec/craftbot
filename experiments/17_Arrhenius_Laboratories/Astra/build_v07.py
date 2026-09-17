"""Freeze v07 generator output before bounded checks and final rendering."""
from pathlib import Path
import runpy
import bpy

HERE = Path(__file__).resolve().parent
runpy.run_path(str(HERE / 'experiment_17_astra_v07.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'preflight_v07.blend'))
print(runpy.run_path(str(HERE / 'snapshot_v07.py'))['identity'](), flush=True)
