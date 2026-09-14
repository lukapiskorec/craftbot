"""Tests for the helpers promoted from experiment 16: columns, enforce_max, lap_length."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import geometry2d as g


class ColumnsTests(unittest.TestCase):
    def test_exact_fit(self):
        self.assertEqual(g.columns(0.0, 0.36, 0.12), [(0.0, 0.12), (0.12, 0.24), (0.24, 0.36)])

    def test_wide_remainder_is_one_ripped_board(self):
        cols = g.columns(0.0, 0.30, 0.12)
        self.assertEqual(len(cols), 3)
        self.assertAlmostEqual(cols[-1][1] - cols[-1][0], 0.06)

    def test_sliver_shared_by_last_two(self):
        cols = g.columns(0.0, 0.25, 0.12)                    # remainder 0.01 < rip_min
        self.assertEqual(len(cols), 3)
        self.assertAlmostEqual(cols[-1][1] - cols[-1][0], 0.065)
        self.assertAlmostEqual(cols[-2][1] - cols[-2][0], 0.065)
        self.assertAlmostEqual(cols[-1][1], 0.25)

    def test_covers_the_run(self):
        for a1 in (0.13, 0.5, 3.9, 4.36):
            cols = g.columns(0.0, a1, 0.12)
            self.assertAlmostEqual(cols[0][0], 0.0)
            self.assertAlmostEqual(cols[-1][1], a1)
            self.assertTrue(all(abs(b - c[0]) < 1e-9 for (_, b), c in zip(cols[:-1], cols[1:])))


class EnforceMaxTests(unittest.TestCase):
    RAILS = [0.65 * k for k in range(1, 15)]

    def test_short_piece_untouched(self):
        self.assertEqual(g.enforce_max([0.0, 4.0], self.RAILS, 4.8), [0.0, 4.0])

    def test_splice_at_support_nearest_midpoint(self):
        cuts = g.enforce_max([0.0, 9.1], self.RAILS, 4.8)
        self.assertEqual(cuts, [0.0, 4.55, 9.1])

    def test_repeats_until_every_piece_fits(self):
        cuts = g.enforce_max([0.144, 11.5], self.RAILS, 4.8)
        self.assertTrue(all(b - a <= 4.8 + 1e-9 for a, b in zip(cuts[:-1], cuts[1:])))
        self.assertTrue(all(c in self.RAILS for c in cuts[1:-1]))

    def test_no_support_raises(self):
        with self.assertRaises(ValueError):
            g.enforce_max([0.0, 6.0], [0.1, 5.9], 4.8)


class LapLengthTests(unittest.TestCase):
    def test_right_angle_is_the_width(self):
        self.assertAlmostEqual(g.lap_length((1, 0), (0, 1), 0.12), 0.12)

    def test_sixty_degree_x(self):
        # two diagonals of an X at 60 degrees to the horizontal cross at 60 degrees
        d1, d2 = (math.cos(math.radians(60)), math.sin(math.radians(60))), (math.cos(math.radians(60)), -math.sin(math.radians(60)))
        c = math.cos(math.radians(60))
        self.assertAlmostEqual(g.lap_length(d1, d2, 0.12, 0.01), 0.12 * (1 + c) / math.sin(math.radians(60)) + 0.01)

    def test_parallel_raises(self):
        with self.assertRaises(ValueError):
            g.lap_length((1, 0, 0), (2, 0, 0), 0.12)


if __name__ == "__main__":
    unittest.main()
