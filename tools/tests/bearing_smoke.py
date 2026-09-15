"""Blender-only bearing adapter tests; run with --background --factory-startup.

No files are saved and no experiment artifacts are read or changed.
"""
import math
import os
import sys
import unittest

import bpy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_bearing import check_pairs


class BearingMeshTests(unittest.TestCase):
    def setUp(self):
        self.objects = {}
        for name, downward in (("Foot", True), ("Seat", False)):
            mesh = bpy.data.meshes.new(name)
            vertices = [(-.045, -.018, 0), (.045, -.018, 0),
                        (.045, .018, 0), (-.045, .018, 0)]
            mesh.from_pydata(vertices, [], [(3, 2, 1, 0) if downward else (0, 1, 2, 3)])
            mesh.update()
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            self.objects[name] = obj
        self.pair = dict(member="Foot", member_face=0, support="Seat", support_face=0)
        bpy.context.view_layer.update()

    def tearDown(self):
        for obj in self.objects.values():
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)

    def report(self, **changes):
        bpy.context.view_layer.update()
        return check_pairs([dict(self.pair, **changes)], self.objects)[0]

    def test_world_space_transform_and_overhang(self):
        for obj in self.objects.values():
            obj.location = (1, 2, 3)
            obj.rotation_euler.z = math.radians(37)
            obj.scale = (2, 1, 1)
        self.assertTrue(self.report()["ok"])
        self.objects["Foot"].scale.x = 2 * .091505 / .09
        report = self.report()
        self.assertFalse(report["ok"])
        self.assertAlmostEqual(report["max_edge_overhang"], .001505, places=6)

    def test_vertical_gap_and_sloping_face(self):
        self.objects["Foot"].location.z = .002
        self.assertFalse(self.report()["ok"])
        self.objects["Foot"].location.z = 0
        self.objects["Foot"].rotation_euler.x = .1
        self.assertIn("horizontal", self.report()["error"])

    def test_missing_wrong_and_self_support_faces(self):
        for changes in (dict(member="Missing"), dict(member_face=10),
                        dict(member_face=True), dict(support="Foot"),
                        dict(member="Seat", support="Foot")):
            with self.subTest(changes=changes):
                self.assertFalse(self.report(**changes)["ok"])
                self.assertIn("error", self.report(**changes))

    def test_unapplied_modifier_rejected(self):
        self.objects["Foot"].modifiers.new("Bevel", "BEVEL")
        self.assertIn("apply modifiers", self.report()["error"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BearingMeshTests)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise RuntimeError("bearing adapter tests failed")
