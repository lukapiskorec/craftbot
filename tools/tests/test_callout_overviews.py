"""Overview layout and exact vector fill clipping."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import callout_overviews as overview
from geometry2d import area


class OverviewTests(unittest.TestCase):
    def test_completely_hidden_callout_gets_explicit_internal_view(self):
        from tools.tests.test_callout_diagrams import model
        import callout_diagrams as cd
        members = cd.decode_model(model())
        lines = []
        entries = overview.selections(members,lines,[dict(id='hidden',label='Post',section='1',match={'names':'Post'})])
        self.assertTrue(entries[0]['revealed'])
        self.assertEqual(entries[0]['selected'],{0})
        self.assertTrue(lines)

    def test_convex_subtraction_preserves_area_around_hole(self):
        square = [(0,0), (4,0), (4,4), (0,4)]
        hole = [(1,1), (3,1), (3,3), (1,3)]
        pieces = overview.subtract_convex(square, hole)
        self.assertAlmostEqual(sum(area(p) for p in pieces), 12)
        self.assertEqual(overview.subtract_convex(square, square), [])
        self.assertAlmostEqual(sum(area(p) for p in overview.subtract_convex(square,
            [(5,0),(6,0),(6,4),(5,4)])), 16)

    def test_front_face_clips_selected_face(self):
        import numpy as np
        square = np.array([(0.,0.),(4.,0.),(4.,4.),(0.,4.)])
        foreground = np.array([(1.,1.),(3.,1.),(3.,3.),(1.,3.)])
        faces = [(0, square, (np.array([0.,0.,0.]),np.array([0.,0.,1.]))),
                 (1, foreground, (np.array([1.,1.,1.]),np.array([0.,0.,1.])))]
        pieces = overview.visible_regions(faces, {0})
        self.assertAlmostEqual(sum(area(p) for p in pieces), 12)
        pieces = overview.visible_regions(faces, {1})
        self.assertAlmostEqual(sum(area(p) for p in pieces), 4)

    def test_depth_crossing_clips_only_nearer_half(self):
        import numpy as np
        poly = np.array([(0.,0.),(4.,0.),(4.,4.),(0.,4.)])
        # Occluder depth x-2 crosses the selected z=0 face at x=2.
        faces = [(0, poly, (np.array([0.,0.,0.]),np.array([0.,0.,1.]))),
                 (1, poly, (np.array([0.,0.,-2.]),np.array([-1.,0.,1.])))]
        pieces = overview.visible_regions(faces, {0})
        self.assertAlmostEqual(sum(area(p) for p in pieces), 8.08, places=5)

    def test_rows_are_spatially_ordered_and_fit_without_overlap(self):
        entries = [dict(number=i+1, anchor=(0,y), callout=dict(label='A label '*4,
                   quote='A full quotation '*10, section='5')) for i,y in enumerate([100,900,400])]
        ordered, size = overview.layout_rows(entries, 150, 540, 65)
        self.assertEqual([e['number'] for e in ordered], [2,3,1])
        for a,b in zip(ordered,ordered[1:]):
            self.assertGreater(a['bottom'], b['top'])
        self.assertGreaterEqual(ordered[-1]['bottom'],65-1e-9)
        self.assertGreaterEqual(size,2.8)


if __name__ == '__main__':
    unittest.main()
