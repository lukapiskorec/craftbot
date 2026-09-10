import os
import sys
import unittest


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from presentation_facades import facade_for, facade_hint


class PresentationFacadeTests(unittest.TestCase):
    def test_cardinal_names(self):
        self.assertEqual(facade_hint("Cladding/South|Clap_S_04"), "south")
        self.assertEqual(facade_hint("Walls/West|inner-west-2"), "west")

    def test_signed_axis_names(self):
        self.assertEqual(facade_hint("|Panel_PosX_03"), "east")
        self.assertEqual(facade_hint("|Panel positive X 03"), "east")
        self.assertEqual(facade_hint("|Panel_NegX_03"), "west")
        self.assertEqual(facade_hint("|Panel_PosY_03"), "north")
        self.assertEqual(facade_hint("|Panel_Negative_Y_03"), "south")

    def test_single_cardinal_token(self):
        self.assertIsNone(facade_hint("Cladding|TowerIn_L2_E0_03"))
        self.assertEqual(facade_hint("Cladding|TowerIn_L2_E_03"), "east")
        self.assertEqual(facade_hint("Cladding|Bottom_N_04"), "north")

    def test_geometry_fallback_uses_standard_xy_axes(self):
        bounds = (-10.0, 10.0, -5.0, 5.0)
        self.assertEqual(facade_for("|Panel", (9.5, 0.0), bounds), "east")
        self.assertEqual(facade_for("|Panel", (-9.5, 0.0), bounds), "west")
        self.assertEqual(facade_for("|Panel", (0.0, -4.8), bounds), "south")
        self.assertEqual(facade_for("|Panel", (0.0, 4.8), bounds), "north")


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
