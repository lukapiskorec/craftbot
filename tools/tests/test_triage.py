import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import triage  # noqa: E402


class TriageTest(unittest.TestCase):
    def test_family_strips_trailing_indices(self):
        self.assertEqual(triage.family("TowerClad_S_B1_026"), "TowerClad_S_B")
        self.assertEqual(triage.family("Rafter_03N_tail"), "Rafter")
        self.assertEqual(triage.family("Ridge_Board"), "Ridge_Board")
        self.assertEqual(triage.family("Post_31"), "Post")

    def test_families_groups_by_name_and_depth(self):
        hits = [(0.0190, "TowerIn_L3_N_047", "Infill_L3_W1_TopPlate"),
                (0.0190, "TowerIn_L3_S_047", "Infill_L3_W0_Stud_00"),
                (0.0110, "TowerClad_S_B3_0_026", "TowerClad_W_B3_0_026"),
                (0.0036, "TowerClad_S_B0_3_005", "TowerClad_E_B0_0_010")]
        rows = triage.families(hits)
        self.assertEqual(rows[0][:4], (2, "TowerIn_L", "Infill_L", 19.0))
        self.assertEqual(len(rows), 3)
        text = triage.format_families(rows)
        self.assertIn("OVERLAP FAMILIES: 3", text)
        self.assertIn("TowerIn_L  x  Infill_L", text)

    def test_empty(self):
        self.assertEqual(triage.families([]), [])
        self.assertIn("0", triage.format_families([]))


if __name__ == "__main__":
    unittest.main()
