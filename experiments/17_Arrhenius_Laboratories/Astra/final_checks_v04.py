"""Freeze collection metadata, then run the actual-mesh v04 evidence suite."""
from pathlib import Path
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import craftbot_lib
# Only these collection assignments changed while preflight was running;
# coordinates and member names are unchanged and match the final source.
base=bpy.data.objects.get('EntranceApproachBase')
if base:
    bpy.data.objects.remove(base,do_unlink=True)
    for i,(ya,yb) in enumerate(((-.9,-.2),(.2,.3))):
        xy=[(21.,ya),(24.,ya),(24.,yb),(21.,yb)]
        craftbot_lib.mesh_prism(f'EntranceApproachBase_Fit{i}','Foundation',[(x,y,-.4) for x,y in xy],[(x,y,-.25) for x,y in xy])
craftbot_lib.move_to(bpy.data.objects['EntranceApproachSlab'],'Floors')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v04.blend'))
for name in ('check_south','check_public_routes','check_headroom','check_routes','verify_route_envelopes','check_supports','check_rims','draw_plans'):
    print('EVIDENCE START '+name,flush=True)
    runpy.run_path(str(HERE/(name+'_v04.py')),run_name='__main__')
    print('EVIDENCE COMPLETE '+name,flush=True)
