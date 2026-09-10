# Views for experiment 15 (Koreni), Fable run. Exec'd by tools/render_views.py
# with M (the script namespace) and Vector in scope. Numbered once, appended
# only. Collection names are bare children: the variation prefix is part of
# the child name (A_Terrain, B_Steel, ...), because collection names are
# global in Blender and the three variations sit in one scene.
#
# Strip origins: A y = 0..20, B y = 30..50, C y = 60..80; bar on y = 7..13 of
# each strip, pavilion x = 5..11. Azimuth 270 = camera at low y looking +y
# (from the ESE side toward WNW); azimuth 90 = camera at high y looking -y.
#
# Every view with a cut carries a focus: the harness derives the clip
# distance from the direction to the focus centre, and without a focus the
# fitted framing shifts the camera sideways, which tilts that direction and
# lands the plane about 1.5 m off for the outer strips (seen in v01, views
# 10, 11, 13 to 15). Workbench renders back faces, so a solid straddling a
# cut plane shows its far inner face as a solid fill: a cut inside a wall
# shows that wall, not what is behind it (views 22 and 30); a section past
# the wall with the coplanar guard hidden shows the flight (view 39).

YA, YB, YC = 0.0, 30.0, 60.0
A_F, A_BOX = M["A_FLOOR"], M["A_BOX_FLOOR"]
B_F = M["B_FLOOR"]
C_L = M["C_LEVELS"]

HIDE_NOT_A = ["B_Cut", "C_Steps"]
HIDE_NOT_B = ["A_Bridge", "C_Steps"]
HIDE_NOT_C = ["A_Bridge", "B_Cut"]
STRIP_R = 40.0                                          # focus radius framing one 106 m strip


def frame_only(L):
    """Skins, glass and slabs hidden (R-48)."""
    return [f"{L}_Terrain", f"{L}_Glazing", f"{L}_Slabs"]


def strip(yo, z=0.0):
    return (Vector((47.0, yo + 10.0, z)), STRIP_R)


VIEWS = [
    # the whole set: four orbits and top
    dict(name="01", azim=45, elev=30, hide=[]),
    dict(name="02", azim=135, elev=30, hide=[]),
    dict(name="03", azim=225, elev=30, hide=[]),
    dict(name="04", azim=315, elev=30, hide=[]),
    dict(name="05", azim=270, elev=89.9, hide=[]),                                  # top
    # long sections on the strip axes looking WNW (sketches 07 to 09 are long sections)
    dict(name="06", azim=270, elev=0, hide=HIDE_NOT_A, cut=("y", YA + 10.0), focus=strip(YA, -2.0)),
    dict(name="07", azim=270, elev=0, hide=HIDE_NOT_B, cut=("y", YB + 10.0), focus=strip(YB, -2.0)),
    dict(name="08", azim=270, elev=0, hide=HIDE_NOT_C, cut=("y", YC + 10.0), focus=strip(YC, -2.0)),
    # from below: A (the bridge undercroft), skin on
    dict(name="09", azim=225, elev=-30, hide=HIDE_NOT_A),
    # interior plan sections at 1.5 above each floor, roof and everything above cut away
    dict(name="10", azim=270, elev=89.9, hide=HIDE_NOT_A, cut=("z", A_F + 1.5), focus=strip(YA)),             # A bridge
    dict(name="11", azim=270, elev=89.9, hide=HIDE_NOT_A, cut=("z", A_BOX + 1.5), focus=strip(YA)),           # A lower box
    dict(name="12", azim=270, elev=89.9, hide=HIDE_NOT_B, cut=("z", B_F + 1.5), focus=strip(YB)),             # B
    dict(name="13", azim=270, elev=89.9, hide=HIDE_NOT_C, cut=("z", C_L[0][2] + 1.5), focus=strip(YC)),       # C L1
    dict(name="14", azim=270, elev=89.9, hide=HIDE_NOT_C, cut=("z", C_L[1][2] + 1.5), focus=strip(YC)),       # C L2
    dict(name="15", azim=270, elev=89.9, hide=HIDE_NOT_C, cut=("z", C_L[2][2] + 1.5), focus=strip(YC)),       # C L3
    # frame only per variation: skin, glass and slabs hidden (R-48); the lists are
    # spelled out because tools/closeout.py looks for a literal hide=["..."]
    dict(name="16", azim=225, elev=30, hide=["B_Cut", "C_Steps", "A_Terrain", "A_Glazing", "A_Slabs"]),
    dict(name="17", azim=225, elev=30, hide=["A_Bridge", "C_Steps", "B_Terrain", "B_Glazing", "B_Slabs"]),
    dict(name="18", azim=225, elev=30, hide=["A_Bridge", "B_Cut", "C_Terrain", "C_Glazing", "C_Slabs"]),
    # close-ups (R-48)
    dict(name="19", azim=300, elev=15, hide=HIDE_NOT_A + ["A_Glazing"],
         focus=(Vector((47.0, YA + 7.3, 0.0)), 2.5)),                                     # A girder on the column at x = 47
    dict(name="20", azim=300, elev=15, hide=HIDE_NOT_A + ["A_Glazing", "A_Terrain"],
         focus=(Vector((53.0, YA + 7.3, -0.3)), 3.0)),                                    # A girder on the box wall at x = 53
    dict(name="21", azim=0, elev=0, hide=HIDE_NOT_B, cut=("x", 20.0),
         focus=(Vector((20.0, YB + 10.0, -1.5)), 8.0)),                                   # B cross section at x = 20: retaining wall bases
    dict(name="22", azim=270, elev=0, hide=HIDE_NOT_C, cut=("y", YC + 7.8),
         focus=(Vector((30.5, YC + 7.8, -2.0)), 4.5)),                                    # C step wall at x = 29, section through the flight (see-through, kept for comparison)
    dict(name="23", azim=240, elev=25, hide=HIDE_NOT_C + ["C_Roof", "C_Glazing"],
         focus=(Vector((30.5, YC + 8.5, -2.0)), 4.5)),                                    # C step wall from outside the closed side (kept for comparison)
    # ESE elevations per variation (the glazed side of segments 1 and 3)
    dict(name="24", azim=270, elev=0, hide=HIDE_NOT_A),
    dict(name="25", azim=270, elev=0, hide=HIDE_NOT_B),
    dict(name="26", azim=270, elev=0, hide=HIDE_NOT_C),
    # from below with the skin hidden: footings, pads and girders of A
    dict(name="27", azim=225, elev=-30, hide=HIDE_NOT_A + ["A_Terrain"]),
    # A entry: pavilion rear wall, girder pockets, five risers
    dict(name="28", azim=210, elev=20, hide=HIDE_NOT_A + ["A_Roof", "A_Glazing", "A_Terrain"],
         focus=(Vector((11.5, YA + 10.0, 0.5)), 4.0)),
    # v02: A entry from inside the bar (door in the x = 11 wall, five risers, pier)
    dict(name="29", azim=20, elev=20, hide=HIDE_NOT_A + ["A_Roof", "A_Glazing", "A_Terrain", "A_Cores"],
         focus=(Vector((11.6, YA + 9.9, 0.6)), 2.5)),
    # v02: C stair 2 with the step wall, section just inside the closed wall (y = 7.19)
    dict(name="30", azim=270, elev=0, hide=HIDE_NOT_C, cut=("y", YC + 7.19),
         focus=(Vector((30.5, YC + 7.8, -2.0)), 4.0)),
    # v02: C stair 2 from the open side, roof and glass off
    dict(name="31", azim=100, elev=25, hide=HIDE_NOT_C + ["C_Roof", "C_Glazing"],
         focus=(Vector((30.5, YC + 8.0, -2.0)), 4.0)),
    # v02: terrace end walls (house end, terrace door, balustrade), roof off
    dict(name="32", azim=60, elev=20, hide=HIDE_NOT_A + ["A_Roof"], focus=(Vector((65.0, YA + 10.0, 2.5)), 5.0)),
    dict(name="33", azim=60, elev=20, hide=HIDE_NOT_B + ["B_Roof"], focus=(Vector((66.0, YB + 10.0, -1.0)), 5.0)),
    dict(name="34", azim=60, elev=20, hide=HIDE_NOT_C + ["C_Roof"], focus=(Vector((66.0, YC + 10.0, -2.3)), 5.0)),
    dict(name="35", azim=60, elev=20, hide=HIDE_NOT_C + ["C_Roof", "C_Glazing"], focus=(Vector((66.0, YC + 10.0, -2.3)), 5.0)),
    # v02: A dogleg stair and void framing, roof off; with and without the guards
    dict(name="36", azim=300, elev=35, hide=HIDE_NOT_A + ["A_Roof", "A_Glazing", "A_Terrain"],
         focus=(Vector((56.0, YA + 10.7, -1.0)), 4.5)),
    dict(name="37", azim=300, elev=35, hide=HIDE_NOT_A + ["A_Roof", "A_Terrain", "A_Steel"],
         focus=(Vector((56.0, YA + 10.7, -1.0)), 4.5)),
    # v02: B entry stair, high bay and step wall, section just inside the closed WNW wall
    dict(name="38", azim=90, elev=0, hide=HIDE_NOT_B, cut=("y", YB + 12.81),
         focus=(Vector((14.0, YB + 12.0, 0.5)), 5.0)),
    # v03: C stair 2 section past the closed wall (the harness renders back faces, so a
    # cut inside the wall shows the wall's inner face as a solid; view 30 kept), guard off
    dict(name="39", azim=270, elev=0, hide=HIDE_NOT_C + ["C_Glazing"], cut=("y", YC + 7.21),
         focus=(Vector((30.5, YC + 7.8, -2.0)), 4.0)),
    # v03: B entry stair section just inside the closed WNW wall (view 38 cut inside the wall), guard off
    dict(name="40", azim=90, elev=0, hide=HIDE_NOT_B + ["B_Glazing"], cut=("y", YB + 12.79),
         focus=(Vector((14.0, YB + 12.0, 0.5)), 5.0)),
    # v04: A entry from inside the bar, steep enough for the five risers to clear the slab edge (29 missed them)
    dict(name="41", azim=20, elev=50, hide=HIDE_NOT_A + ["A_Roof", "A_Glazing", "A_Terrain", "A_Cores"],
         focus=(Vector((11.6, YA + 9.9, 0.6)), 2.5)),
    # v04: the door from the pavilion into the bar (x = 11 wall) seen from inside the bar: section on x
    dict(name="42", azim=0, elev=0, hide=HIDE_NOT_B + ["B_Glazing"], cut=("x", 11.6),
         focus=(Vector((11.6, YB + 10.0, 0.5)), 4.0)),
    dict(name="43", azim=0, elev=0, hide=HIDE_NOT_C + ["C_Glazing"], cut=("x", 11.6),
         focus=(Vector((11.6, YC + 10.0, -0.5)), 4.0)),
    # v04: closed-wall doors onto B's courtyard (segment 1 y_max at x = 25.7, segment 2 y_min at 37.7),
    # sections just outside the wall face so the retaining wall is cut away
    dict(name="44", azim=90, elev=0, hide=HIDE_NOT_B, cut=("y", YB + 13.6),
         focus=(Vector((26.2, YB + 13.1, -1.6)), 3.5)),
    dict(name="45", azim=270, elev=0, hide=HIDE_NOT_B, cut=("y", YB + 6.4),
         focus=(Vector((38.2, YB + 6.9, -1.6)), 3.5)),
    # v04: C's closed-wall doors onto the grade, L2 at x = 44.5 and L3 at 56.5, both on the y_max wall
    dict(name="46", azim=90, elev=0, hide=HIDE_NOT_C, cut=("y", YC + 13.6),
         focus=(Vector((51.0, YC + 13.1, -3.2)), 7.5)),
    # v04: A core 1 with its store walls (R-19), plan at bridge + 1.5 zoomed on the core
    dict(name="47", azim=270, elev=89.9, hide=HIDE_NOT_A, cut=("z", A_F + 1.5),
         focus=(Vector((13.2, YA + 11.8, A_F)), 3.0)),
    # v04: C stair 1 with its guard from the open side and above, roof and cores off
    dict(name="48", azim=300, elev=35, hide=HIDE_NOT_C + ["C_Roof", "C_Cores"],
         focus=(Vector((12.2, YC + 12.2, -0.5)), 2.5)),
    # v04: C roof beam at x = 27 in its pocket at the top of segment 1's closed wall, from inside and
    # below (the dark slot of 22 and 39 is this beam's section, cut by their planes)
    dict(name="49", azim=270, elev=-15, hide=HIDE_NOT_C + ["C_Glazing"],
         focus=(Vector((27.0, YC + 12.9, 2.2)), 1.5)),
]

PALETTE = {
    "Terrain": (0.62, 0.66, 0.50, 1.0),
    "Footings": (0.45, 0.45, 0.47, 1.0),
    "Concrete": (0.72, 0.72, 0.70, 1.0),
    "Slabs": (0.80, 0.80, 0.78, 1.0),
    "Steel": (0.30, 0.34, 0.42, 1.0),
    "Glazing": (0.55, 0.80, 0.95, 1.0),
    "Cores": (0.85, 0.72, 0.55, 1.0),
    "Stairs": (0.78, 0.62, 0.45, 1.0),
    "Roof": (0.90, 0.85, 0.70, 1.0),
}
COLORS = {f"{L}_{sub}": rgba for L in "ABC" for sub, rgba in PALETTE.items()}

RESOLUTION = (1600, 1200)
