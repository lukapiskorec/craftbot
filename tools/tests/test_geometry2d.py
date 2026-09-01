import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import geometry2d as g


SQUARE = g.rect(0.0, 2.0, 0.0, 2.0)


class ClipTests(unittest.TestCase):
    def test_half_plane_keeps_normal_side(self):
        half = g.clip(SQUARE, (1.0, 0.0), (1.0, 0.0))        # keep x >= 1
        self.assertAlmostEqual(g.area(half), 2.0)
        self.assertTrue(all(x >= 1.0 - 1e-9 for x, _ in half))

    def test_clip_rect_intersection(self):
        tri = [(0.0, 0.0), (4.0, 0.0), (0.0, 4.0)]
        piece = g.clip_rect(tri, 1.0, 3.0, 0.0, 2.0)
        self.assertAlmostEqual(g.area(piece), 4.0 - 0.5)        # 2x2 minus the corner cut by x + y = 4

    def test_clip_u_keeps_side(self):
        left = g.clip_u(SQUARE, 0.5, True)
        right = g.clip_u(SQUARE, 0.5, False)
        self.assertAlmostEqual(g.area(left), 1.0)
        self.assertAlmostEqual(g.area(right), 3.0)

    def test_inset_any_winding(self):
        cw = list(reversed(SQUARE))
        for poly in (SQUARE, cw):
            small = g.inset(poly, 0.5)
            self.assertAlmostEqual(g.area(small), 1.0)
        self.assertEqual(g.inset(SQUARE, 1.5), [])

    def test_strip_dimensions(self):
        s = g.strip((0.0, 0.0), (3.0, 0.0), 0.2, ext=0.5)
        self.assertAlmostEqual(g.area(s), 4.0 * 0.2)

    def test_line_isect_and_point_in_loops(self):
        self.assertEqual(g.line_isect((0, 0), (2, 2), (0, 2), (2, 0)), (1.0, 1.0))
        self.assertIsNone(g.line_isect((0, 0), (1, 0), (0, 1), (1, 1)))
        hole = g.rect(0.5, 1.0, 0.5, 1.0)
        self.assertTrue(g.point_in_loops(0.25, 0.25, [SQUARE, hole]))
        self.assertFalse(g.point_in_loops(0.75, 0.75, [SQUARE, hole]))

    def test_scan_intervals_with_hole(self):
        hole = g.rect(0.5, 1.0, 0.5, 1.0)
        spans = g.scan_intervals([SQUARE, hole], 0.75)
        self.assertEqual(len(spans), 2)
        self.assertAlmostEqual(spans[0][1], 0.5)
        self.assertAlmostEqual(spans[1][0], 1.0)


class IntervalTests(unittest.TestCase):
    def test_positions_flush_ends_and_grid(self):
        pos = g.positions(0.0, 2.7, 0.6, 0.05)
        self.assertAlmostEqual(pos[0], 0.025)
        self.assertAlmostEqual(pos[-1], 2.675)
        self.assertAlmostEqual(pos[1], 0.6)
        # 2.4 is within half a spacing of the last stud -> dropped
        self.assertNotIn(2.4, [round(p, 6) for p in pos])
        self.assertEqual(len(pos), 5)
        # 2.4 is 0.575 from the end stud of a 3.0 wall -> kept
        self.assertIn(2.4, [round(p, 6) for p in g.positions(0.0, 3.0, 0.6, 0.05)])

    def test_positions_external_grid(self):
        pos = g.positions(1.0, 4.0, 1.0, 0.1, grid0=0.3)
        self.assertAlmostEqual(pos[1], 2.3)

    def test_count_fit(self):
        self.assertEqual(g.count_fit(2.5, 1.0)[0], 2)
        self.assertAlmostEqual(g.count_fit(2.5, 1.0)[1], 0.5)
        self.assertEqual(g.count_fit(3.0, 1.0), (3, 0.0))

    def test_split_range_and_strips(self):
        self.assertEqual(g.split_range(0.0, 10.0, [(2.0, 3.0), (8.0, 12.0)]), [(0.0, 2.0), (3.0, 8.0)])
        self.assertEqual(g.strips(0.0, 3.0, [1.0, 2.0, 5.0]), [(0.0, 1.0), (1.0, 2.0), (2.0, 3.0)])

    def test_split_rows(self):
        rows = g.split_rows([(0.0, 3.0)], [(0, 1, 1.0, 2.0)])
        self.assertEqual(rows, [(0.0, 1.0), (1.0, 2.0), (2.0, 3.0)])


class TileTests(unittest.TestCase):
    def test_tile_covers_area_minus_holes(self):
        hole = (1.0, 2.0, 0.5, 1.5)
        cells = g.tile(0.0, 5.0, 0.0, 3.0, 2.4, 1.2, [hole], stagger=True)
        total = sum((cb - ca) * (bb - ba) for ca, cb, ba, bb in cells)
        self.assertAlmostEqual(total, 15.0 - 1.0)
        for ca, cb, ba, bb in cells:
            self.assertLessEqual(cb - ca, 2.4 + 1e-9)
            self.assertLessEqual(bb - ba, 1.2 + 1e-9)
            inside = ca >= hole[0] - 1e-9 and cb <= hole[1] + 1e-9 and ba >= hole[2] - 1e-9 and bb <= hole[3] + 1e-9
            self.assertFalse(inside)

    def test_tile_stagger_shifts_odd_rows(self):
        cells = g.tile(0.0, 4.8, 0.0, 2.4, 2.4, 1.2, stagger=True)
        row0 = sorted(c for c in cells if c[2] == 0.0)
        row1 = sorted(c for c in cells if c[2] == 1.2)
        self.assertAlmostEqual(row0[0][1], 2.4)
        self.assertAlmostEqual(row1[0][1], 1.2)


class WallPiecesTests(unittest.TestCase):
    def test_pieces_cover_wall_minus_openings(self):
        wall = g.rect(0.0, 6.0, 0.0, 3.0)
        openings = [(1.0, 2.0, 0.9, 2.1), (4.0, 5.0, 0.0, 2.1), (4.0, 5.0, 2.4, 2.8)]
        pieces = g.wall_pieces(wall, openings)
        self.assertAlmostEqual(sum(g.area(p) for p in pieces), 18.0 - 1.2 - 2.1 - 0.4)
        # piers, sill, lintel, and for the door column: spandrel + lintel
        self.assertEqual(len(pieces), 3 + 2 + 2)

    def test_overlapping_columns_rejected(self):
        with self.assertRaises(AssertionError):
            g.wall_pieces(g.rect(0, 4, 0, 3), [(1, 2, 1, 2), (1.5, 2.5, 1, 2)])

    def test_gable_profile(self):
        gable = [(0.0, 0.0), (6.0, 0.0), (6.0, 2.0), (3.0, 4.0), (0.0, 2.0)]
        pieces = g.wall_pieces(gable, [(2.5, 3.5, 0.9, 2.1)])
        self.assertAlmostEqual(sum(g.area(p) for p in pieces), g.area(gable) - 1.2)


if __name__ == "__main__":
    unittest.main()
