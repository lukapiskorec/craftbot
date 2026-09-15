import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_bearing import check_bearing


def rectangle(width=0.09, depth=0.036, z=0.0, x=0.0):
    return [(x-width/2, -depth/2, z), (x+width/2, -depth/2, z),
            (x+width/2, depth/2, z), (x-width/2, depth/2, z)]


class BearingTests(unittest.TestCase):
    def test_full_seat_and_reversed_winding(self):
        for foot in (rectangle(), list(reversed(rectangle()))):
            report = check_bearing(foot, rectangle(depth=0.1))
            self.assertTrue(report["ok"])
            self.assertAlmostEqual(report["coverage"], 1.0)

    def test_experiment_16_overhang_is_not_full_bearing(self):
        report = check_bearing(rectangle(width=0.091505), rectangle())
        self.assertFalse(report["ok"])
        self.assertAlmostEqual(report["max_edge_overhang"], 0.0007525)
        self.assertAlmostEqual(report["coverage"], 0.09/0.091505)

    def test_edge_only_contact(self):
        report = check_bearing(rectangle(x=0.09), rectangle())
        self.assertFalse(report["ok"])
        self.assertAlmostEqual(report["supported_area"], 0.0)

    def test_gap_and_penetration_fail_despite_footprint_containment(self):
        for z in (0.002, -0.002):
            report = check_bearing(rectangle(z=z), rectangle())
            self.assertFalse(report["ok"])
            self.assertAlmostEqual(report["gap"], z)
            self.assertEqual(report["supported_area"], 0.0)

    def test_rotated_horizontal_seat_uses_polygon_not_bounds(self):
        # Both shapes have identical XY bounds; the square overhangs the diamond.
        diamond = [(0, -1, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0)]
        report = check_bearing(rectangle(2, 2), diamond)
        self.assertFalse(report["ok"])
        self.assertAlmostEqual(report["coverage"], 0.5)
        self.assertTrue(check_bearing(diamond, diamond)["ok"])

    def test_rejects_sloping_concave_degenerate_and_nonfinite_faces(self):
        bad_faces = [
            [(0, 0, 0), (1, 0, 0), (1, 1, 0.1), (0, 1, 0.1)],
            [(0, 0, 0), (2, 0, 0), (1, 0.5, 0), (2, 2, 0), (0, 2, 0)],
            [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
            [(0, 0, 0), (math.nan, 0, 0), (1, 1, 0)],
            [(0, 0, 0), (1, 1, 0), (0, 1, 0), (1, 0, 0)],
        ]
        for face in bad_faces:
            with self.subTest(face=face), self.assertRaises(ValueError):
                check_bearing(face, rectangle())

    def test_tolerance_is_explicit_and_small(self):
        self.assertTrue(check_bearing(rectangle(z=0.5e-6), rectangle())["ok"])
        self.assertFalse(check_bearing(rectangle(z=2e-6), rectangle())["ok"])
        for tol in (-1, 0, math.nan):
            with self.assertRaises(ValueError):
                check_bearing(rectangle(), rectangle(), tol=tol)


if __name__ == "__main__":
    unittest.main()
