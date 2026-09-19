import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_card  # noqa: E402


class ApiCardTest(unittest.TestCase):
    def test_build_lists_every_kit_module_and_key_functions(self):
        text = api_card.build()
        for m in api_card.MODULES:
            self.assertIn(f"### `{m}.py`", text)
        for fn in ("place_element(", "box(name, coll, x0, x1, y0, y1, z0, z1)", "sloped_member(", "stud_wall(", "positions("):
            self.assertIn(fn, text)
        self.assertNotIn("_rules_for", text)          # private names stay out

    def test_card_is_short(self):
        # the point of the card: about 3 k tokens, not the 17 k of the modules
        self.assertLess(len(api_card.build()), 20000)

    def test_fabrication_kit_has_its_own_card(self):
        text = api_card.build_fabrication()
        for m in api_card.FABRICATION:
            self.assertIn(f"### `{m}.py`", text)
            self.assertIn(f"### `{m}.py`", api_card.build())      # named on the main card, without signatures
        for fn in ("write_members(", "write_cutlist(", "visible_lines(members, right, up)", "class `SheetSet(scale, experiment, subtitle", "min_scale("):
            self.assertIn(fn, text)
        self.assertNotIn("write_cutlist(", api_card.build())

    def test_bearing_api_and_codex_closeout_are_documented(self):
        text = api_card.build()
        self.assertIn("check_bearing(foot, seat, tol=1e-06)", text)
        self.assertIn("check_pairs(pairs, objects=None, tol=1e-06)", text)
        self.assertIn("--transcript-source", text)
        self.assertIn("--no-archive", text)


if __name__ == "__main__":
    unittest.main()
