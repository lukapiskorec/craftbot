"""Source03 eye-level evidence, using frozen geometry and existing Cycles kit."""
from pathlib import Path
import json
import runpy
import sys
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import cycles_style
scene=bpy.context.scene
views=runpy.run_path(str(HERE/'views_astra.py'),init_globals={'Vector':Vector})
settings=dict(cycles_style.DEFAULTS)
settings.update(views['CYCLES'])
settings.update(samples=48,exposure=2.0,world_strength=.35,fill_strength=.75)
cycles_style.setup(scene,settings)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
view=dict(name='40_interior',palette='muted',azim=225,elev=5,sun_rotation=-160,sun_elevation=45,edges='none')
cycles_style.apply_view(scene,meshes,view,settings)
for coll in bpy.data.collections:coll.hide_render=coll.name in ('Site','Foundation')
for obj in meshes:obj.hide_render=False
camera=bpy.data.objects.new('InteriorEvidenceCamera',bpy.data.cameras.new('InteriorEvidenceCamera'))
scene.collection.objects.link(camera);scene.camera=camera
camera.data.type='PERSP';camera.data.lens=35.;camera.data.sensor_width=36.;camera.data.clip_start=.05
camera.location=(33.,10.1,5.2)
target=Vector((40.2,7.5,5.5))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.filepath=str(HERE/'experiment_17_astra_v06_cycles_view_40_interior.png')
record={'geometry':runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](),
        'camera':list(camera.location),'target':list(target),'lens_mm':35.,'eye_height_above_level1_m':1.6,
        'exposure_EV':2.0,'world_strength':.35,'fill_strength':.75,'samples':48,
        'notes':'Presentation daylight/fill only; genuine glass transmission; all building meshes retained. No invented lighting fixture.'}
(HERE/'interior_v06_40_settings.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
bpy.ops.render.render(write_still=True)
