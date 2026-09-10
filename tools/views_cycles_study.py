"""Fable v09 style comparisons. Use with render_views.py --style cycles.

Names are palette + light; every view gets a foundation on/off pair.
The camera stays fixed across the 12 primary comparisons.
"""

RESOLUTION = (3072, 3072)
CYCLES = dict(
    samples=128, noise_threshold=.015, world_strength=.2,
    sun_intensity=.4, sun_size=3, exposure=0,
    foundation_collections=["Foundation"],
    material_roles={
        "Foundation": "concrete", "Plinths": "concrete",
        "Splices": "metal", "Connections": "metal", "Roofing": "cladding",
        "Glazing": "glass",
        "Cladding_Shed": "cladding", "Cladding_Tower": "cladding",
        "Cladding_HeadHouse": "cladding", "Cladding_Interior": "cladding",
        "Shed_Roof_Boards": "cladding", "Terrace_Deck": "cladding",
        "HeadHouse_Floor": "cladding",
        # Slabs are CLT and guards are timber in this model: keep them timber.
    },
)

VIEWS = [
    dict(name=f"{palette}_{light}", palette=palette, azim=305, elev=-25,
         sun_rotation=rotation, sun_elevation=elevation, margin=1.16, hide=[])
    for palette in ("white", "muted", "washed", "weathered")
    for light, rotation, elevation in (
        ("reference", -430, 45), ("crosslight", -160, 45), ("low_sun", 20, 25)
    )
]

# Open the envelope to judge light on the framing, as in the first reference.
FRAME_HIDE = ["Shed_Roof_Boards", "Terrace_Deck", "HeadHouse_Floor", "Slabs",
              "Cladding_Shed", "Cladding_Tower", "Cladding_HeadHouse", "Glazing",
              "Infill_Walls", "Roofing", "Cladding_Interior", "Doors"]
VIEWS += [dict(name=f"{palette}_frame", palette=palette, azim=225, elev=-30,
               sun_rotation=-160, sun_elevation=45, margin=1.16, hide=FRAME_HIDE)
          for palette in ("white", "washed")]
