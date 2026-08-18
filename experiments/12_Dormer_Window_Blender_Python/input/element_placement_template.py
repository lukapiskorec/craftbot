# ------------------------------------------------------------------
# CRAFT BOT - MAIN SCRIPT
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# MODULE IMPORTS

import bpy
import sys
import os
import importlib
import craftbot_lib as craftbot # if you have problems importing custom modules from lib folder , run add_module_path_to_system.py first


# ------------------------------------------------------------------
# MAIN

importlib.reload(craftbot)  # handy while developing

# Example usage: place a few cubes
craftbot.place_element(
    name="Cubert_A",
    loc=(0, 0, 0),
    axis=(1, 0, 0),   # X axis
    angle=45,         # degrees
    scale=(2, 2, 2),
)

craftbot.place_element(
    name="Cubert_B",
    loc=(4, 0, 0),
    axis=(0, 0, 1),   # Z axis
    angle=90,
    scale=(1, 2, 1),
)

craftbot.place_element(
    name="Cubert_C",
    loc=(0, 4, 0),
    axis=(0, 1, 0),   # Y axis
    angle=30,
    scale=(1, 1, 3),
)

