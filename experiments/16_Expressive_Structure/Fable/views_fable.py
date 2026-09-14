# Views for experiment 16, Fable run (tools/render_views.py --views).
# Numbered once, appended only. Hide lists use bare collection names.
# x across the trusses, y along the row, door in the -y wall.
# azim 0 = camera on +x looking -x (side elevation of the row), 270 = camera at -y looking +y (door front).

Z_E, Z_H = M["Z_E"], M["Z_H"]
COVER = ["BoardsIn", "BoardsOut", "FloorBoards", "RoofDeck", "Door"]
RING = ["RingChords", "RingWebs", "Bracing", "RingSpacers", "RoofBracing"]   # v04 adds the spacers and the roof X's

VIEWS = [
    dict(name="01", azim=45, elev=30, hide=[]),
    dict(name="02", azim=135, elev=30, hide=[]),
    dict(name="03", azim=225, elev=30, hide=[]),
    dict(name="04", azim=315, elev=30, hide=[]),
    dict(name="05", azim=270, elev=89.9, hide=[]),                                  # top
    dict(name="06", azim=270, elev=0, hide=[]),                                     # front elevation, door side (-y)
    dict(name="07", azim=0, elev=0, hide=[]),                                       # side elevation along the row: the ripple
    dict(name="08", azim=225, elev=30, hide=COVER),                                 # frame only
    dict(name="09", azim=225, elev=-30, hide=[]),                                   # from below
    dict(name="10", azim=250, elev=12, hide=[]),                                    # matched to photo 01-soane-front: low three-quarter from the door side
    # ring truss node close-up: mid-leg of the truss at y = 0, +x side
    dict(name="11", azim=20, elev=10, hide=[], focus=(Vector((2.32 + 0.63, 0.0, 6.0)), 1.1)),
    # roof heel: bottom chord on the side wall head plate, top chord on the arris, deck eave; ring and bracing hidden
    dict(name="12", azim=330, elev=15, hide=RING, focus=(Vector((2.124, 0.0, Z_H + 0.15)), 0.8)),
    dict(name="13", azim=270, elev=0, hide=[], cut=("y", 0.0)),                     # cross section at y = 0 looking +y
    dict(name="14", azim=0, elev=0, hide=[], cut=("x", 0.0)),                       # long section at x = 0 looking -x: W wall face, end walls in section, trusses edge-on; the door opening (left) is closed in projection by its -x jamb
    dict(name="15", azim=270, elev=89.9, hide=[], cut=("z", 1.5)),                  # plan section at 1.5
    dict(name="16", azim=270, elev=-89.9, hide=[], cut=("z", 1.5)),                 # inside looking up: the shaft, band and roof trusses
    # bracing X close-up, +x side, lower panel, rings hidden so the halving joint and the leg contact read
    dict(name="17", azim=340, elev=8, hide=["RingChords", "RingWebs"], focus=(Vector((2.245, -1.625, 3.05)), 1.4)),
    # door from inside: camera at +y looking -y, everything nearer than y = -0.6 cut away
    dict(name="18", azim=90, elev=5, hide=[], cut=("y", -0.6), focus=(Vector((0.0, -2.0, 1.3)), 2.2)),
    # ring truss apex and corner over the box roof: clearance to the deck
    dict(name="19", azim=0, elev=5, hide=["Bracing"], focus=(Vector((0.0, 0.0, Z_E + 0.5)), 3.4), cut=("x", 0.4)),
    # east elevation with the ring hidden: the box, band and eave
    dict(name="20", azim=0, elev=0, hide=RING),
    # low oblique along the row: the ripple and its diagonal crests (a true side elevation, view 07, cannot show a depth that varies toward the camera)
    dict(name="21", azim=12, elev=10, hide=[]),
    # v02: ring eave corner close-up, truss 3 (y = -1.30, the shallowest -x corner, d = 0.33) seen face on from -y,
    # everything nearer than the mid-bay y = -1.40 cut away: the mitred outer corner and its clearance to the inner chord
    dict(name="22", azim=270, elev=0, hide=[], cut=("y", -1.40), focus=(Vector((-2.60, -1.30, Z_E)), 1.0)),
    # v02: ring apex close-up, same set-up as 22 (truss 3 face on from -y, cut at the mid-bay y = -1.40): the mitred apex
    # vertex, the two webs meeting at the apex node in their two planes, the inner chord clear of the deck ridge
    dict(name="23", azim=270, elev=0, hide=[], cut=("y", -1.40), focus=(Vector((0.0, -1.30, Z_E + 0.55)), 1.2)),
    # v02: wall board close-up, -y wall outer face beside the door, joints at 1.95 (B columns) and 3.25 (A columns) alternating
    dict(name="24", azim=270, elev=0, hide=RING, focus=(Vector((1.20, -2.178, 2.60)), 1.0)),
    # v02: box eave corner (+x, -y) with the ring hidden: side head plate, four-slat corner post, gable head plate, notched outer rail
    dict(name="25", azim=315, elev=15, hide=RING, focus=(Vector((2.10, -2.10, Z_H + 0.20)), 0.9)),
    # v02: door leaf from inside, camera at -x looking +x with everything at x < 0 cut away: boards, three ledges, two braces
    dict(name="26", azim=180, elev=0, hide=[], cut=("x", 0.0), focus=(Vector((0.48, -1.50, 1.20)), 1.3)),
    # v03: gable stud splices (R-21). Section 5 mm into the x = 0 stud pair of both end walls (N stud, S door cripple),
    # z about 2.9..9.9 (the frame is about 2.1 x radius tall; 4.5 showed the whole wall and 25 px stud bands): the
    # splices sit on rail centres, so only a cut through the slat shows them. 27: the A slat (x -0.03..0) from +x,
    # joints at 4.55 and 9.10; 28: the B slat (x 0..0.03) from -x, joints at 3.25 and 7.80, none at the sill rail 9.57.
    dict(name="27", azim=0, elev=0, hide=RING, cut=("x", -0.005), focus=(Vector((0.0, 0.0, 6.4)), 3.3)),
    dict(name="28", azim=180, elev=0, hide=RING, cut=("x", 0.005), focus=(Vector((0.0, 0.0, 6.4)), 3.3)),
    # v03: the same two sections at the radius of view 24, one splice per frame, because the Inspector could not read a
    # 20 px stud band in 27 and 28. N wall stud at y = 2.064: 29, 30 the A slat at 4.55 and at 9.10 with the sill rail
    # 9.51..9.63 and the board top in frame; 31, 32 the B slat at 3.25 and at 7.80 with the sill rail in frame (v02 had
    # a third cut there). S wall door cripple at y = -2.064: 33, 34 the B slat, same two frames.
    dict(name="29", azim=0, elev=0, hide=RING, cut=("x", -0.005), focus=(Vector((0.0, 2.064, 4.55)), 0.8)),
    dict(name="30", azim=0, elev=0, hide=RING, cut=("x", -0.005), focus=(Vector((0.0, 2.064, 9.30)), 0.8)),
    dict(name="31", azim=180, elev=0, hide=RING, cut=("x", 0.005), focus=(Vector((0.0, 2.064, 3.25)), 0.8)),
    dict(name="32", azim=180, elev=0, hide=RING, cut=("x", 0.005), focus=(Vector((0.0, 2.064, 8.70)), 1.1)),
    dict(name="33", azim=180, elev=0, hide=RING, cut=("x", 0.005), focus=(Vector((0.0, -2.064, 3.25)), 0.8)),
    dict(name="34", azim=180, elev=0, hide=RING, cut=("x", 0.005), focus=(Vector((0.0, -2.064, 8.70)), 1.1)),
    # v04: outer chord spacers (P2-01a) on the +x legs, bays 4-5 to 6-7 at outer vertex 32 (z about 5.9), seen from +x
    # and a little +y: the bevelled 30 x 120 bars between the facing chord slats, inclined by the depth difference
    dict(name="35", azim=30, elev=10, hide=[], focus=(Vector((3.0, 0.325, 5.93)), 1.3)),
    # v04: the roof from above with the deck hidden (P2-01b, P2-02): inner top chord spacers at every node between the
    # rings, the two zigzags per slope crossing as X's under the chords, bay 9-10 unbraced
    dict(name="36", azim=270, elev=89.9, hide=["RoofDeck"], focus=(Vector((0.0, 0.0, Z_E + 0.3)), 3.5)),
    # v04: from inside looking up with the deck and the box roof trusses hidden: the roof X's from below, the inner chords
    # and spacers behind them
    dict(name="37", azim=270, elev=-89.9, hide=["RoofDeck", "RoofTrusses"], cut=("z", 1.5), focus=(Vector((0.0, 0.0, Z_E)), 3.6)),
    # v04: frame-only box with the ring hidden (the v03 suggestion): studs, rails, door kings, jacks, header and cripple
    dict(name="38", azim=225, elev=30, hide=COVER + RING),
    # v04: one roof X crossing from above, E slope, panel 3-6 (crossing at x 1.16, y -0.325, bay 4-5): the halving joint
    # and the inner chord spacers at the nodes x 0.77 and 1.55 either side
    dict(name="39", azim=270, elev=89.9, hide=["RoofDeck"], focus=(Vector((1.16, -0.325, Z_E + 0.2)), 0.7)),
    # v04: section 15 mm past that crossing, looking +y: the two half laps stacked under the chord underside plane of
    # truss 5 behind, the deck 0.04 below. The inner spacer at x 1.55 is also cut by the plane but is not separable
    # here: its 30 x 120 section sits exactly in front of truss 5's chord, same depth, same alignment (v04 Inspector).
    dict(name="40", azim=270, elev=0, hide=[], cut=("y", -0.34), focus=(Vector((1.16, -0.34, Z_E + 0.13)), 0.6)),
]

COLORS = {
    "Foundation": (0.55, 0.55, 0.58, 1.0),
    "Floor": (0.72, 0.60, 0.42, 1.0),
    "Walls": (0.62, 0.42, 0.24, 1.0),
    "BoardsIn": (0.85, 0.75, 0.58, 1.0),
    "BoardsOut": (0.70, 0.30, 0.22, 1.0),
    "Door": (0.55, 0.80, 0.95, 1.0),
    "BoxRoof": (0.90, 0.80, 0.55, 1.0),
    "Ring": (0.40, 0.50, 0.62, 1.0),
    "RingWebs": (0.55, 0.65, 0.78, 1.0),
    "Bracing": (0.30, 0.60, 0.45, 1.0),
    "RingSpacers": (0.90, 0.55, 0.20, 1.0),
    "RoofBracing": (0.20, 0.72, 0.60, 1.0),
}

RESOLUTION = (1600, 1200)
