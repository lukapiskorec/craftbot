"""Recompute only post-joinery9.x support families on the initial saved v06."""
from pathlib import Path
import runpy
import bpy
HERE=Path(__file__).resolve().parent
old_closures=bpy.context.scene['closure_changes_v06']
prefixes=('PerimeterLedger','CourtWaist','CourtLandingSupport','CourtLandingLedge','CourtStairFooting','TerraceWall','TerraceFooting')
bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)])
runpy.run_path(str(HERE/'support_geometry_v06.py'),run_name='__main__')
# The six actual enclosure trims already exist and are unchanged by9.7.
bpy.context.scene['closure_changes_v06']=old_closures
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v06.blend'))
print(runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),flush=True)
