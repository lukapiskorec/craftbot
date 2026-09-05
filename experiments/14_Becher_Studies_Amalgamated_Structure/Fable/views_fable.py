# Views for experiment 14 (tools/render_views.py --views). Numbered once,
# stable across versions, append only.

# Collection names are global in Blender, so hide lists and colours use the bare
# child names (Existing/Shed_Walls is the collection "Shed_Walls"). v01-v03 renders
# used the slash paths and hid nothing.
COVER = ["Shed_Roof_Boards", "Terrace_Deck", "HeadHouse_Floor",
         "Slabs", "Cladding_Shed", "Cladding_Tower", "Cladding_HeadHouse",
         "Glazing", "Infill_Walls", "Roofing", "Cladding_Interior", "Doors"]

VIEWS = [
    dict(name="01", azim=45, elev=30, hide=[]),
    dict(name="02", azim=135, elev=30, hide=[]),
    dict(name="03", azim=225, elev=30, hide=[]),
    dict(name="04", azim=315, elev=30, hide=[]),
    dict(name="05", azim=270, elev=89.9, hide=[]),                          # top
    dict(name="06", azim=270, elev=0, hide=[]),                             # south elevation
    dict(name="07", azim=0, elev=0, hide=[]),                               # east elevation
    dict(name="08", azim=225, elev=30, hide=COVER),                         # frame only
    dict(name="09", azim=225, elev=-30, hide=[]),                           # from below
    dict(name="10", azim=305, elev=12, hide=[]),                            # matched to the photo (from the SE, low)
    dict(name="11", azim=270, elev=0, hide=[], cut=("y", 1.2)),             # long section through the stair strip
    dict(name="12", azim=270, elev=89.9, hide=[], cut=("z", M["z_slab_top"](1) + 1.3)),   # L1 plan section
    dict(name="13", azim=240, elev=25, hide=COVER[1:], focus=(Vector((2.4, 2.4, 3.6)), 2.2)),   # posts through the shed roof
    dict(name="14", azim=220, elev=15, hide=["Cladding_Shed", "Shed_Walls", "Shed_Roof_Boards", "Shed_Roof", "Shed_Ceiling", "Shed_Outriggers"],
         focus=(Vector((0.0, 0.0, 0.7)), 1.0)),    # repaired post foot (shed hidden; v01/v02 renders of this view showed the wall)
    dict(name="15", azim=200, elev=35, hide=["Shed_Roof_Boards", "Slabs", "Cladding_Tower", "Infill_Walls", "Glazing"], focus=(Vector((7.0, 1.2, 3.6)), 2.6)),  # stair hole in the roof
    dict(name="16", azim=270, elev=89.9, hide=[], cut=("z", 0.9)),          # ground floor plan section
    dict(name="17", azim=330, elev=15, hide=[], focus=(Vector((12.3, 2.4, 7.0)), 7.5)),   # trestle relic and tie-back
    dict(name="18", azim=250, elev=10, hide=[], focus=(Vector((4.0, -1.8, 2.4)), 1.6)),     # shed outriggers through the clapboard
    dict(name="19", azim=225, elev=25, hide=COVER, focus=(Vector((0.0, 0.0, 12.6)), 2.4)),  # terrace corner: girt, brace, beam, joists
    dict(name="20", azim=290, elev=10, hide=[], focus=(Vector((7.2, -0.3, 8.6)), 2.8)),     # facade bay: exposed post, girt, brace, boards between
    dict(name="21", azim=200, elev=30, hide=["Cladding_Tower", "Infill_Walls", "Glazing"], focus=(Vector((6.8, 1.2, 4.9)), 2.4)),  # L1 void guard and beam seats
    dict(name="22", azim=90, elev=0, hide=[], cut=("y", 2.2)),               # cross-wall section looking south: interior boards, stairs, stringers
    dict(name="23", azim=250, elev=8, hide=[], focus=(Vector((3.3, -1.9, 2.3)), 1.3)),     # outrigger, knee and canopy
    dict(name="24", azim=210, elev=15, hide=[], focus=(Vector((4.1, 2.3, 14.8)), 1.8)),    # ladder to the head house door
    dict(name="25", azim=200, elev=20, hide=["Cladding_Shed", "Shed_Walls", "Shed_Roof_Boards", "Shed_Roof", "Shed_Ceiling", "Cladding_Interior", "Shed_Outriggers"],
         focus=(Vector((5.5, 1.2, 1.6)), 3.2)),                                            # ground stair: stringers and landing posts
    dict(name="26", azim=305, elev=12, hide=["Cladding_Tower", "Cladding_Shed", "Cladding_HeadHouse", "Roofing", "Shed_Roof_Boards", "Terrace_Deck", "HeadHouse_Floor", "Slabs", "Glazing", "Doors", "Infill_Walls", "Shed_Walls", "HeadHouse_Walls"],
         focus=(Vector((4.8, 2.4, 8.0)), 6.0)),                                            # interior boards alone, from the photo direction
]

COLORS = {
    "Foundation": (0.55, 0.55, 0.58, 1.0),
    "Existing": (0.42, 0.28, 0.16, 1.0),          # preserved timber: dark brown
    "Shed_Roof_Boards": (0.55, 0.42, 0.28, 1.0),
    "Terrace_Deck": (0.55, 0.42, 0.28, 1.0),
    "HeadHouse_Floor": (0.55, 0.42, 0.28, 1.0),
    "Repairs": (0.90, 0.50, 0.15, 1.0),           # repairs: orange
    "Splices": (0.35, 0.35, 0.40, 1.0),
    "New": (0.85, 0.78, 0.60, 1.0),               # new timber: pale glulam
    "Slabs": (0.92, 0.88, 0.72, 1.0),
    "Stairs": (0.80, 0.70, 0.50, 1.0),
    "Glazing": (0.55, 0.80, 0.95, 1.0),
    "Cladding_Tower": (0.62, 0.55, 0.42, 1.0),
    "Cladding_Shed": (0.70, 0.66, 0.58, 1.0),
    "Cladding_HeadHouse": (0.62, 0.55, 0.42, 1.0),
    "Roofing": (0.50, 0.52, 0.55, 1.0),
    "Guards": (0.35, 0.35, 0.40, 1.0),
    "Connections": (0.30, 0.32, 0.36, 1.0),
    "Cladding_Interior": (0.88, 0.80, 0.62, 1.0),
    "Doors": (0.45, 0.30, 0.18, 1.0),
    "Ladder": (0.70, 0.55, 0.35, 1.0),
}

RESOLUTION = (1600, 1200)
