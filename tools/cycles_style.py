"""Cycles presentation style; source meshes preserved, optional render-only bevels.

Nishita defaults transcribed from outputs/Screenshot 2025-12-11 224642.png.
Palette values are sRGB swatches, converted to linear for shader inputs.
"""

import math
import re
from collections import Counter

import bpy


PALETTES = {
    "white": dict(timber=(.89, .885, .875), cladding=(.89, .885, .875),
                  concrete=(.89, .885, .875), metal=(.89, .885, .875),
                  glass=(.89, .885, .875)),
    "muted": dict(timber=(.57, .51, .44), cladding=(.73, .68, .60),
                  concrete=(.89, .885, .87), metal=(.32, .335, .35),
                  glass=(.66, .72, .75)),
    "washed": dict(timber=(.72, .67, .60), cladding=(.83, .79, .72),
                   concrete=(.90, .895, .88), metal=(.43, .445, .46),
                   glass=(.71, .76, .78)),
    "weathered": dict(timber=(.57, .55, .51), cladding=(.73, .71, .66),
                      concrete=(.88, .885, .88), metal=(.29, .31, .33),
                      glass=(.64, .70, .73)),
}

DEFAULTS = dict(samples=128, noise_threshold=.015, exposure=0, world_strength=.2,
                sun_size=3, sun_intensity=.4, fill_strength=.25, edges="none", edge_width=.010,
                edge_darkness=.22,
                edge_light_response=.30,
                overlap_shadow_epsilon=.001,
                foundation="hide",
                glass_roughness=.015, glass_transmission=1., glass_ior=1.45)

DEFAULT_VIEW = dict(palette="washed", azim=305, elev=-25, margin=1.16,
                    sun_rotation=-160, sun_elevation=45)


def cli_settings(args, settings):
    settings = dict(DEFAULTS, **settings)
    for name in DEFAULTS:
        value = getattr(args, name, None)
        if value is not None:
            settings[name] = value
    if settings["samples"] < 1 or min(settings[k] for k in ("edge_width", "fill_strength", "overlap_shadow_epsilon", "world_strength", "sun_intensity")) < 0:
        raise ValueError("Samples must be positive; edge width and light strengths must be non-negative")
    if not 0 <= settings["edge_darkness"] <= 1:
        raise ValueError("Edge darkness must be between 0 and 1")
    if not 0 <= settings["edge_light_response"] <= 1:
        raise ValueError("Edge light response must be between 0 and 1")
    if not all(0 <= settings[k] <= 1 for k in ("glass_roughness", "glass_transmission")) or settings["glass_ior"] < 1:
        raise ValueError("Glass roughness/transmission must be 0..1; IOR must be >= 1")
    if args.foundation_collections is not None:
        settings["foundation_collections"] = args.foundation_collections.split(",")
    if args.foundation is not None:
        settings["foundation"] = args.foundation
    roles = dict(settings.get("material_roles", {}))
    for assignment in args.material_role:
        collection, role = assignment.rsplit("=", 1)
        if role not in PALETTES["white"]:
            raise ValueError(f"Unknown material role: {role}")
        roles[collection] = role
    settings["material_roles"] = roles
    return settings


def cli_views(args, views):
    output = []
    for view in views:
        view = dict(view)
        for flag, key in (("azimuth", "azim"), ("elevation", "elev"), ("margin", "margin"),
                          ("sun_rotation", "sun_rotation"), ("sun_elevation", "sun_elevation")):
            if getattr(args, flag) is not None:
                view[key] = getattr(args, flag)
        if args.hide:
            view["hide"] = list(dict.fromkeys(view.get("hide", []) + args.hide.split(",")))
        for palette in args.palettes.split(",") if args.palettes else [view.get("palette", "white")]:
            if palette not in PALETTES:
                raise ValueError(f"Unknown palette: {palette}")
            output.append(dict(view, palette=palette, base_name=view["name"],
                               name=f"{view['name']}_{palette}" if args.palettes else view["name"]))
    return output


def setup(scene, settings):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = settings.get("samples", 128)
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = settings.get("noise_threshold", .015)
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 16
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 12
    scene.cycles.seed = 14
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = settings.get("exposure", 0.0)
    scene.view_settings.gamma = 1.0
    preferences = bpy.context.preferences.addons["cycles"].preferences
    scene.cycles.device = "CPU"
    for backend in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            preferences.compute_device_type = backend
            preferences.get_devices()
        except (TypeError, ValueError, RuntimeError):
            continue
        devices = [d for d in preferences.devices if d.type == backend]
        if devices:
            for device in preferences.devices:
                device.use = device.type == backend
            scene.cycles.device = "GPU"
            if backend == "OPTIX":
                scene.cycles.denoiser = "OPTIX"
            print("CYCLES_DEVICE", backend, [d.name for d in devices], flush=True)
            break
    # Use only sky illumination; model scripts may have supplied their own lamps.
    for obj in scene.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PresentationWorld")
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    nodes.clear()
    sky = nodes.new("ShaderNodeTexSky")
    sky.name = "PresentationSky"
    sky.sky_type = "NISHITA"
    sky.sun_disc = True
    sky.sun_size = math.radians(settings.get("sun_size", 3.0))
    sky.sun_intensity = settings.get("sun_intensity", .4)
    sky.altitude = 0
    sky.air_density = sky.dust_density = sky.ozone_density = 1
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = settings.get("world_strength", .2)
    output = nodes.new("ShaderNodeOutputWorld")
    scene.world.node_tree.links.new(sky.outputs["Color"], background.inputs["Color"])
    # Add neutral fill only to diffuse rays. The optional presentation background
    # below handles camera, transmission and glossy rays. There is no ground mesh.
    fill = nodes.new("ShaderNodeBackground")
    fill.name = "IndirectFill"
    fill.inputs["Color"].default_value = (1, 1, 1, 1)
    fill.inputs["Strength"].default_value = settings.get("fill_strength", .25)
    addition = nodes.new("ShaderNodeAddShader")
    paths = nodes.new("ShaderNodeLightPath")
    mix = nodes.new("ShaderNodeMixShader")
    links = scene.world.node_tree.links
    links.new(background.outputs[0], addition.inputs[0])
    links.new(fill.outputs[0], addition.inputs[1])
    links.new(paths.outputs["Is Diffuse Ray"], mix.inputs[0])
    links.new(background.outputs[0], mix.inputs[1])
    links.new(addition.outputs[0], mix.inputs[2])
    camera_background = settings.get("camera_background_srgb")
    if camera_background:
        linear = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
                       for c in camera_background)
        camera_fill = nodes.new("ShaderNodeBackground")
        camera_fill.name = "CameraBackground"
        camera_fill.inputs["Color"].default_value = (*linear, 1)
        camera_fill.inputs["Strength"].default_value = 1
        camera_mix = nodes.new("ShaderNodeMixShader")
        camera_mix.name = "CameraBackgroundMix"
        camera_or_transmission = nodes.new("ShaderNodeMath")
        camera_or_transmission.name = "CameraOrTransmissionRay"
        camera_or_transmission.operation = "MAXIMUM"
        links.new(paths.outputs["Is Camera Ray"], camera_or_transmission.inputs[0])
        links.new(paths.outputs["Is Transmission Ray"], camera_or_transmission.inputs[1])
        ray_selector = nodes.new("ShaderNodeMath")
        ray_selector.name = "CameraTransmissionOrGlossyRay"
        ray_selector.operation = "MAXIMUM"
        links.new(camera_or_transmission.outputs[0], ray_selector.inputs[0])
        links.new(paths.outputs["Is Glossy Ray"], ray_selector.inputs[1])
        links.new(ray_selector.outputs[0], camera_mix.inputs[0])
        links.new(mix.outputs[0], camera_mix.inputs[1])
        links.new(camera_fill.outputs[0], camera_mix.inputs[2])
        links.new(camera_mix.outputs[0], output.inputs["Surface"])
    else:
        links.new(mix.outputs[0], output.inputs["Surface"])


def paired_views(views, only, settings):
    """Every selected view gets both states, including all foundation descendants."""
    foundations = settings.get("foundation_collections")
    if foundations is None:
        foundations = [c.name for c in bpy.data.collections if re.search(r"foundation|footing|plinth|podium", c.name, re.I)]
    missing = [name for name in foundations if bpy.data.collections.get(name) is None]
    if missing:
        raise ValueError(f"Missing foundation collections: {missing}")
    settings["foundation_collections"] = foundations
    if not foundations:
        print("No foundation collections detected; producing one foundation-free state. Use --foundation-collections to override.")
    paired = []
    for view in views:
        if only and view["name"] not in only and view.get("base_name") not in only:
            continue
        base_hide = [name for name in view.get("hide", []) if name not in foundations]
        mode = settings.get("foundation", "both")
        states = ("with_foundation", "no_foundation") if mode == "both" and foundations else (
            "with_foundation" if mode == "show" else "no_foundation",)
        edges = view.get("edges", settings.get("edges", "none"))
        for edge in ("none", "bevel") if edges == "both" else (edges,):
            for state in states:
                paired.append(dict(view, name=f"{view['name']}_{edge}_{state}", edges=edge,
                                   study=view.get("base_name", view["name"]), foundation=state,
                                   fit_hide=view.get("fit_hide", base_hide),
                                   hide=base_hide + (foundations if state == "no_foundation" else [])))
    if not paired:
        raise ValueError("No views selected")
    return paired


def material_role(obj, overrides):
    for collection in obj.users_collection:
        if collection.name in overrides:
            return overrides[collection.name]
    for slot in obj.material_slots:
        source = slot.material
        if source is None:
            continue
        if re.search(r"glass|glaz", source.name, re.I):
            return "glass"
        if source.use_nodes:
            for node in source.node_tree.nodes:
                if node.type != "BSDF_PRINCIPLED":
                    continue
                transmission = node.inputs.get("Transmission Weight") or node.inputs.get("Transmission")
                if transmission and transmission.default_value > 0:
                    return "glass"
    # Conservative name-based defaults; --material-role handles ambiguous models.
    text = " ".join([obj.name] + [c.name for c in obj.users_collection]).lower()
    for role, pattern in (("glass", r"glass|glaz|window.?pane|(?:^|[^a-z])pane(?:$|[^a-z])"),
                          ("concrete", r"concrete|foundation|plinth|footing"),
                          ("metal", r"steel|metal|splice|bracket|connection"),
                          ("cladding", r"clad|board|siding|sheath|lining")):
        if re.search(pattern, text):
            return role
    return "timber"


def material(palette, role, settings):
    name = f"Presentation_{palette}_{role}"
    swatch = (1, 1, 1) if role == "glass" else PALETTES[palette][role]
    linear = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in swatch)
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*linear, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = .78
    shader.inputs["Metallic"].default_value = 0
    shader.inputs["Transmission Weight"].default_value = 0
    if palette != "white" and role == "metal":
        shader.inputs["Metallic"].default_value = .45
        shader.inputs["Roughness"].default_value = .48
    elif role == "glass":
        shader.inputs["Transmission Weight"].default_value = settings.get("glass_transmission", 1.)
        shader.inputs["Roughness"].default_value = settings.get("glass_roughness", .015)
        shader.inputs["IOR"].default_value = settings.get("glass_ior", 1.45)
    if role != "glass":
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        ray_length = nodes.get("ContactShadowRayLength")
        if ray_length is None:
            output = nodes.get("Material Output")
            paths = nodes.new("ShaderNodeLightPath")
            paths.name = "ContactShadowLightPath"
            ray_length = nodes.new("ShaderNodeMath")
            ray_length.name = "ContactShadowRayLength"
            ray_length.operation = "LESS_THAN"
            geometry = nodes.new("ShaderNodeNewGeometry")
            geometry.name = "ContactShadowGeometry"
            overlap = nodes.new("ShaderNodeMath")
            overlap.name = "ContactShadowOverlap"
            overlap.operation = "MAXIMUM"
            selector = nodes.new("ShaderNodeMath")
            selector.name = "ContactShadowSelector"
            selector.operation = "MULTIPLY"
            transparent = nodes.new("ShaderNodeBsdfTransparent")
            transparent.name = "ContactShadowTransparent"
            mix = nodes.new("ShaderNodeMixShader")
            mix.name = "ContactShadowMix"
            for link in list(output.inputs["Surface"].links):
                links.remove(link)
            links.new(paths.outputs["Ray Length"], ray_length.inputs[0])
            links.new(ray_length.outputs[0], overlap.inputs[0])
            links.new(geometry.outputs["Backfacing"], overlap.inputs[1])
            links.new(paths.outputs["Is Shadow Ray"], selector.inputs[0])
            links.new(overlap.outputs[0], selector.inputs[1])
            links.new(selector.outputs[0], mix.inputs[0])
            links.new(shader.outputs[0], mix.inputs[1])
            links.new(transparent.outputs[0], mix.inputs[2])
            links.new(mix.outputs[0], output.inputs["Surface"])
        ray_length.inputs[1].default_value = settings.get("overlap_shadow_epsilon", .001)
    return mat


def edge_material(palette, role, settings):
    darkness = settings.get("edge_darkness", .22)
    response = settings.get("edge_light_response", .30)
    name = f"PresentationEdge_{palette}_{role}_{darkness:.3f}_{response:.3f}"
    swatch = PALETTES[palette][role]
    dark = tuple(c * darkness for c in swatch)
    linear = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in dark)
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*linear, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = .82
    shader.inputs["Metallic"].default_value = 0
    shader.inputs["Transmission Weight"].default_value = 0
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*linear, 1)
    emission.inputs["Strength"].default_value = 1
    mix = nodes.new("ShaderNodeMixShader")
    mix.name = "EdgeLightResponse"
    mix.inputs[0].default_value = response
    output = nodes.new("ShaderNodeOutputMaterial")
    links = mat.node_tree.links
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(shader.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return mat


def edge_slot(obj, mat):
    """Return an object-linked material slot dedicated to bevel faces."""
    key = "presentation_edge_slot"
    index = obj.data.get(key)
    if index is None or index >= len(obj.data.materials):
        obj.data.materials.append(mat)
        index = len(obj.data.materials) - 1
        obj.data[key] = index
    slot = obj.material_slots[index]
    slot.link = "OBJECT"
    slot.material = mat
    return index


def apply_view(scene, meshes, view, settings):
    palette = view.get("palette", "white")
    overrides = settings.get("material_roles", {})
    for obj in meshes:
        role = material_role(obj, overrides)
        mat = material(palette, role, settings)
        edge_index = obj.data.get("presentation_edge_slot")
        if not obj.material_slots:
            obj.data.materials.append(mat)
        for index, slot in enumerate(obj.material_slots):
            if index != edge_index:
                slot.link = "OBJECT"
                slot.material = mat
        bevel = obj.modifiers.get("PresentationEdges")
        if role != "glass" and view.get("edges", "none") == "bevel":
            edge_settings = dict(settings)
            for key in ("edge_width", "edge_darkness", "edge_light_response"):
                if key in view:
                    edge_settings[key] = view[key]
            if bevel is None:
                bevel = obj.modifiers.new("PresentationEdges", "BEVEL")
            bevel.width = edge_settings.get("edge_width", .010)
            bevel.segments = 2
            bevel.limit_method = "ANGLE"
            bevel.use_clamp_overlap = True
            bevel.material = edge_slot(obj, edge_material(palette, role, edge_settings))
            bevel.show_render = True
            bevel.show_viewport = False
        elif bevel is not None:
            bevel.show_render = False
    sky = scene.world.node_tree.nodes["PresentationSky"]
    sky.sun_elevation = math.radians(view.get("sun_elevation", DEFAULT_VIEW["sun_elevation"]))
    sky.sun_rotation = math.radians(view.get("sun_rotation", DEFAULT_VIEW["sun_rotation"]))


def record(scene, meshes, view, elapsed, settings):
    hidden = set()
    for name in view["hide"]:
        collection = bpy.data.collections.get(name)
        if collection:
            hidden.update(collection.all_objects)
    hidden.update(bpy.data.objects[name] for name in view.get("hide_objects", [])
                  if bpy.data.objects.get(name))
    return dict(name=view["name"], file=scene.render.filepath, palette=view.get("palette", "white"),
                foundation=view["foundation"], hide=view["hide"],
                study=view.get("study", view["name"]), edges=view.get("edges", "none"),
                edge_width=view.get("edge_width", settings.get("edge_width", .010)),
                edge_darkness=view.get("edge_darkness", settings.get("edge_darkness", .22)),
                edge_light_response=view.get("edge_light_response", settings.get("edge_light_response", .30)),
                camera=dict(type=scene.camera.data.type, azimuth=view["azim"], elevation=view["elev"],
                            location=list(scene.camera.location), ortho_scale=scene.camera.data.ortho_scale),
                sun_rotation=view.get("sun_rotation", DEFAULT_VIEW["sun_rotation"]),
                sun_elevation=view.get("sun_elevation", DEFAULT_VIEW["sun_elevation"]),
                resolution=[scene.render.resolution_x, scene.render.resolution_y],
                samples=scene.cycles.samples, device=scene.cycles.device, denoiser=scene.cycles.denoiser,
                swatches_srgb=dict(PALETTES[view.get("palette", "white")], glass=(1, 1, 1)),
                color_management=dict(transform=scene.view_settings.view_transform,
                                      look=scene.view_settings.look, exposure=scene.view_settings.exposure),
                mesh_count=len(meshes), hidden_mesh_count=sum(o in hidden for o in meshes),
                material_counts=dict(Counter(o.material_slots[0].material.name for o in meshes)),
                seconds=round(elapsed, 2))
