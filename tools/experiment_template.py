# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT SCRIPT TEMPLATE
#
# Copy this file to experiments/<NN>_.../Fable/experiment_NN_fable_v01.py
# and replace the BUILD section. It shows the layout every Fable run
# converged on: one parameter block, derived levels as functions, the
# shared kits from tools/, members in named collections, a print of the
# element count at the end.
#
# Run headless (renders + overlap check):
#   blender --background --python tools/render_views.py -- <this file> <abs out prefix>
# ------------------------------------------------------------------

import os
import sys
import math
import importlib

import bpy

# tools/ on the path whether the script runs from Blender's text editor,
# headless via render_views.py, or from any working directory
_HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
for _d in (os.path.join(_HERE, "..", "..", "..", "tools"), os.path.join(_HERE, "..", "tools"), _HERE):
    _d = os.path.normpath(_d)
    if os.path.isfile(os.path.join(_d, "craftbot_lib.py")) and _d not in sys.path:
        sys.path.insert(0, _d)

import craftbot_lib as craftbot
import geometry2d as g2
import planes
import framing
for _m in (craftbot, g2, planes, framing):
    importlib.reload(_m)        # handy while iterating inside Blender

from mathutils import Vector
from craftbot_lib import box, prism_x
from planes import member, sloped_member, vy, vz, Roof

# ------------------------------------------------------------------
# PARAMETERS (one block; everything below derives from these)

L, W = 6.0, 4.0                 # building length (X) and span (Y)
POST = (0.15, 0.15)             # post section x, y
POST_H = 2.4
PLATE = (0.15, 0.10)            # width (y), depth (z)
RAF = (0.05, 0.15)              # rafter width (x), depth perpendicular to the slope
PITCH = math.radians(30.0)
SPACING = 0.6
OVERHANG = 0.5

S, C, T = math.sin(PITCH), math.cos(PITCH), math.tan(PITCH)

# derived levels
PLATE_TOP = POST_H + PLATE[1]
DV = RAF[1] * math.sqrt(1 + T * T)               # rafter depth measured vertically
RAF_TOP0 = PLATE_TOP + DV - T * PLATE[0]         # rafter top line at the plate outer face:
                                                 # the underside meets the plate top at its inner face (seat = plate width)
Y_OUT = W / 2 + PLATE[0] / 2                     # plate outer face
ROOF = {sgn: Roof(f"Main_{side}", out=(0, sgn), c=Y_OUT, z0=RAF_TOP0, s=T)   # rafter top planes
        for side, sgn in (("S", -1), ("N", 1))}
RIDGE_Z = ROOF[-1].z(0.0, 0.0)

# ------------------------------------------------------------------
# BUILD

craftbot.clear_scene()

box("Slab", "Foundation", -0.5, L + 0.5, -W / 2 - 0.5, W / 2 + 0.5, -0.15, 0.0)

for i, x in enumerate(g2.positions(0.0, L, 3.0, POST[0])):
    for side, sgn in (("S", -1), ("N", 1)):
        y = sgn * W / 2
        box(f"Post_{i}{side}", "Structure/Posts",
            x - POST[0] / 2, x + POST[0] / 2, y - POST[1] / 2, y + POST[1] / 2, 0.0, POST_H)

for side, sgn in (("S", -1), ("N", 1)):
    y = sgn * W / 2
    box(f"Plate_{side}", "Structure/Plates", 0.0, L, y - PLATE[0] / 2, y + PLATE[0] / 2, POST_H, PLATE_TOP)

# rafters: build long in the vertical plane and clip. Body = above the plate
# (seat cut) and on its own side of the ridge plane; tail = outside the plate,
# full depth, plumb end. Body and tail share the heel face, so both stay convex.
for k, x in enumerate(g2.positions(0.0, L, SPACING, RAF[0])):
    for side, sgn in (("S", -1), ("N", 1)):
        p0, d = (x, sgn * Y_OUT), (0, -sgn)                     # start at the plate outer face, run inward
        sloped_member(f"Rafter_{k:02d}{side}", "Roof/Rafters", p0, d, T, RAF_TOP0, RAF[1], RAF[0],
                      0.0, Y_OUT + 0.5, clips=[vz(PLATE_TOP, +1), vy(0.0, sgn)])
        sloped_member(f"Rafter_{k:02d}{side}_tail", "Roof/Rafters", p0, d, T, RAF_TOP0, RAF[1], RAF[0],
                      -OVERHANG, 0.0)

print(f"Built template model: {len([o for o in bpy.data.objects if o.type == 'MESH'])} elements, "
      f"ridge z = {RIDGE_Z:.3f} m")
