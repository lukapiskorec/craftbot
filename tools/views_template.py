# Views file for tools/render_views.py (pass with --views). Copy it next to
# the experiment script as Fable/views_fable.py and edit.
#
# This file is exec'd by the harness with these names in scope:
#   M       the experiment's namespace (dict): M["RIDGE_Z"], M["z_floor"](3), ...
#   Vector  mathutils.Vector, for focus points
# and must leave VIEWS (list of dicts), and optionally COLORS and RESOLUTION.
#
# View keys:
#   name   two-digit string; the file becomes <prefix>_view_<name>.png.
#          Number once, keep stable across versions, append new views at the end.
#   azim   camera azimuth in degrees: 0 = camera on +X looking -X, 90 = on +Y,
#          270 = camera south of the building looking north
#   elev   camera elevation in degrees (89.9 = top view, -30 = from below)
#   hide   collection names hidden in this view (children hidden with them)
#   focus  (Vector centre, radius) for a close-up; omit to fit the visible model
#   cut    ("x"|"y"|"z", value): section cut on the camera near-clip plane;
#          a true section only at elev 0 (vertical) or +-89.9 (plan)
#
# Mandatory for every model: the four orbits, one frame-only view (sheathing,
# cladding and decks hidden), one from below. Add elevations and top when the
# reference is a drawing, section cuts per storey when there is more than one,
# a view matched to the reference photo when the model is meant to resemble
# one, and a close-up for every joint that needs judgement. Add a view in the
# same version that adds the feature it shows.

VIEWS = [
    dict(name="01", azim=45, elev=30, hide=[]),
    dict(name="02", azim=135, elev=30, hide=[]),
    dict(name="03", azim=225, elev=30, hide=[]),
    dict(name="04", azim=315, elev=30, hide=[]),
    dict(name="05", azim=270, elev=89.9, hide=[]),                      # top
    dict(name="06", azim=270, elev=0, hide=[]),                         # south elevation
    dict(name="07", azim=0, elev=0, hide=[]),                           # east elevation
    dict(name="08", azim=225, elev=30, hide=["Sheathing", "Facade"]),   # frame only: list YOUR covering collections
    dict(name="09", azim=225, elev=-30, hide=[]),                       # from below
    # close-up: replace the point and radius with the joint under inspection
    dict(name="10", azim=300, elev=20, hide=["Roof"], focus=(Vector((0.0, -2.0, 2.6)), 1.2)),
    # section examples (uncomment and place):
    # dict(name="11", azim=270, elev=89.9, hide=[], cut=("z", M["Z_FLOOR"] + 1.3)),   # plan section
    # dict(name="12", azim=270, elev=0, hide=[], cut=("y", 0.0)),                     # cross section looking north
]

# Object colour per collection (children inherit). Unlisted collections are grey.
COLORS = {
    "Foundation": (0.55, 0.55, 0.58, 1.0),
    "Structure": (0.62, 0.42, 0.24, 1.0),
    "Roof": (0.90, 0.80, 0.55, 1.0),
    "Facade": (0.60, 0.66, 0.58, 1.0),
    "Openings": (0.55, 0.80, 0.95, 1.0),
}

RESOLUTION = (1600, 1200)
