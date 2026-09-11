"""Blender smoke test: paired visibility and object-linked material overrides.

blender --background --factory-startup --python-exit-code 1 --python tools/tests/cycles_smoke.py
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycles_style

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
foundation = bpy.data.collections.new("Foundation")
plinths = bpy.data.collections.new("Plinths")
frame = bpy.data.collections.new("Frame")
metal = bpy.data.collections.new("Metal")
scene.collection.children.link(foundation)
foundation.children.link(plinths)
scene.collection.children.link(frame)
scene.collection.children.link(metal)
bpy.ops.mesh.primitive_cube_add()
timber = bpy.context.object
for collection in list(timber.users_collection):
    collection.objects.unlink(timber)
frame.objects.link(timber)
steel = bpy.data.objects.new("Steel", timber.data)
metal.objects.link(steel)
foot = bpy.data.objects.new("Foot", timber.data.copy())
plinths.objects.link(foot)
source_glass = bpy.data.materials.new("UnlabelledClearMaterial")
source_glass.use_nodes = True
source_glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 1
screen = bpy.data.objects.new("Screen", timber.data.copy())
screen.data.materials.append(source_glass)
frame.objects.link(screen)
window_pane = bpy.data.objects.new("Window_Pane_01", timber.data.copy())
frame.objects.link(window_pane)
settings = dict(material_roles={"Metal": "metal", "Plinths": "concrete"},
                foundation_collections=["Foundation"],
                camera_background_srgb=(.57647, .66275, .75686))
views = [dict(name="A", azim=305, elev=-25, hide=["Frame"]),
         dict(name="B", azim=225, elev=-30, hide=[])]
paired = cycles_style.paired_views(views, {"A"}, settings)
assert len(paired) == 2
assert paired[0]["hide"] == ["Frame"]
assert paired[1]["hide"] == ["Frame", "Foundation"]
assert paired[0]["fit_hide"] == paired[1]["fit_hide"] == ["Frame"]
assert paired[0]["azim"] == paired[1]["azim"]
assert foot in foundation.all_objects[:]
assert views[0]["hide"] == ["Frame"], "Pair expansion mutated the source views"
original_vertices = [tuple(v.co) for v in timber.data.vertices]
assert cycles_style.material_role(screen, {}) == "glass"
assert cycles_style.material_role(window_pane, {}) == "glass"
cycles_style.setup(scene, settings)
cycles_style.apply_view(scene, [timber, steel, foot, screen, window_pane], dict(palette="muted"), settings)
assert timber.data == steel.data
assert timber.material_slots[0].material.name == "Presentation_muted_timber"
assert steel.material_slots[0].material.name == "Presentation_muted_metal"
assert foot.material_slots[0].material.name == "Presentation_muted_concrete"
assert screen.material_slots[0].material.name == "Presentation_muted_glass"
assert window_pane.material_slots[0].material.name == "Presentation_muted_glass"
timber_nodes = timber.material_slots[0].material.node_tree.nodes
assert timber_nodes["ContactShadowRayLength"].operation == "LESS_THAN"
assert abs(timber_nodes["ContactShadowRayLength"].inputs[1].default_value - .001) < 1e-9
assert timber_nodes["ContactShadowOverlap"].operation == "MAXIMUM"
assert any(link.from_socket.name == "Backfacing" and link.to_node == timber_nodes["ContactShadowOverlap"]
           for link in timber.material_slots[0].material.node_tree.links)
assert timber_nodes["ContactShadowSelector"].operation == "MULTIPLY"
assert timber_nodes.get("ContactShadowMix") is not None
assert screen.material_slots[0].material.node_tree.nodes.get("ContactShadowMix") is None
assert original_vertices == [tuple(v.co) for v in timber.data.vertices]
cycles_style.apply_view(scene, [timber, steel, foot], dict(palette="white"), settings)
assert timber.material_slots[0].material.diffuse_color[:] == steel.material_slots[0].material.diffuse_color[:]
assert steel.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value == 0
assert scene.render.engine == "CYCLES" and scene.cycles.use_denoising
assert scene.world.node_tree.nodes["IndirectFill"].inputs["Strength"].default_value == .25
camera_or_transmission = scene.world.node_tree.nodes["CameraOrTransmissionRay"]
assert camera_or_transmission.operation == "MAXIMUM"
first_inputs = {link.from_socket.name for link in scene.world.node_tree.links
                if link.to_node == camera_or_transmission}
assert first_inputs == {"Is Camera Ray", "Is Transmission Ray"}
ray_selector = scene.world.node_tree.nodes["CameraTransmissionOrGlossyRay"]
assert ray_selector.operation == "MAXIMUM"
assert any(link.from_socket.name == "Is Glossy Ray" and link.to_node == ray_selector
           for link in scene.world.node_tree.links)
assert any(link.from_node == camera_or_transmission and link.to_node == ray_selector
           for link in scene.world.node_tree.links)
camera_mix = scene.world.node_tree.nodes["CameraBackgroundMix"]
assert any(link.from_node == ray_selector and link.to_node == camera_mix
           for link in scene.world.node_tree.links)
for palette in cycles_style.PALETTES:
    mat = cycles_style.material(palette, "glass", {})
    shader = mat.node_tree.nodes["Principled BSDF"]
    assert shader.inputs["Transmission Weight"].default_value == 1
    assert shader.inputs["Roughness"].default_value < .02
    assert shader.inputs["Base Color"].default_value[:] == (1, 1, 1, 1)
cycles_style.apply_view(scene, [timber, steel, foot], dict(palette="white", edges="bevel"), settings)
assert timber.modifiers["PresentationEdges"].show_render
assert not timber.modifiers["PresentationEdges"].show_viewport
assert timber.modifiers["PresentationEdges"].material == timber.data["presentation_edge_slot"]
assert timber.material_slots[timber.data["presentation_edge_slot"]].material.name.startswith("PresentationEdge_white_timber")
edge_response = timber.material_slots[timber.data["presentation_edge_slot"]].material.node_tree.nodes["EdgeLightResponse"].inputs[0].default_value
assert abs(edge_response - .30) < 1e-6
assert original_vertices == [tuple(v.co) for v in timber.data.vertices]
cycles_style.apply_view(scene, [timber, steel, foot], dict(palette="white", edges="none"), settings)
assert not timber.modifiers["PresentationEdges"].show_render
assert len(cycles_style.paired_views(views, {"A"}, dict(settings, edges="both"))) == 4
unlit = cycles_style.edge_material("washed", "timber", dict(edge_darkness=.22, edge_light_response=0))
assert unlit.node_tree.nodes["EdgeLightResponse"].inputs[0].default_value == 0
print("PASS: foundation pairs, shared meshes, clear glass/background, contact-shadow bypass, fill, render-only edge toggles, unchanged vertices")
