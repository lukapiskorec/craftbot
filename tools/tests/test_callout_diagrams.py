"""Geometry and layout contracts for the exported callout drawings."""
import copy
import re
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import callout_diagrams as diagrams
from hidden_lines import visible_lines


def model():
    return {'format': 'craftbot-model', 'version': 1,
            'collections': ['', 'Structure'], 'layers': ['frame', 'roof'],
            'boxes': [['Post', 1, 2, 0, 0, 10, 0, 1, 0, 20, 0, 0, 3, 30, 0]],
            'meshes': []}


class CalloutDiagramsTests(unittest.TestCase):
    def test_compaction_preserves_segments_styles_and_order(self):
        from vector_pdf import Sheet
        sheet = Sheet(420, 594)
        sheet.line((20, 30), (40, 50))
        sheet.line((40, 50), (60, 70))
        sheet.line((60, 70), (80, 90), lw=.25)
        sheet.text(20, 25, 'Keep this text')
        svg = diagrams.compact_svg(sheet.svg())
        self.assertEqual(svg.count('<path '), 2)
        self.assertEqual(re.findall(r'M([\d.,]+)L([\d.,]+)', svg),
                         [('20.00,564.00', '40.00,544.00'), ('40.00,544.00', '60.00,524.00'),
                          ('60.00,524.00', '80.00,504.00')])
        self.assertIn('stroke-width="0.25"', svg)
        self.assertIn('Keep this text', svg)

    def test_box_export_matrix_and_layer_names(self):
        member = diagrams.decode_model(model())[0]
        np.testing.assert_allclose(np.min(member['verts'], axis=0), [8000, 19000, 27000])
        np.testing.assert_allclose(np.max(member['verts'], axis=0), [12000, 21000, 33000])
        self.assertEqual(member['layer'], 'frame')
        self.assertEqual(member['group'], 'Structure')
        vertices = np.array(member['verts'])
        for face in member['faces']:
            p = vertices[face]
            self.assertGreater(np.dot(np.cross(p[1]-p[0], p[2]-p[0]), p.mean(0)-vertices.mean(0)), 0)

    def test_explosion_is_rigid_and_layers_do_not_overlap(self):
        members = diagrams.decode_model(model())
        second = copy.deepcopy(members[0])
        second.update(name='Roof', layer='roof')
        members.append(second)
        original = copy.deepcopy(members)
        exploded, bands = diagrams.explode(members, diagrams.RIGHT, diagrams.UP)
        self.assertEqual(members, original)
        for before, after in zip(members, exploded):
            delta = np.array(after['verts'])-before['verts']
            np.testing.assert_allclose(delta, np.broadcast_to(delta[0], delta.shape))
        self.assertGreater(bands[1]['bounds'][1], bands[0]['bounds'][3])

    def test_owner_lines_match_fabrication_hidden_line_solver(self):
        members = diagrams.decode_model(model())
        second = copy.deepcopy(members[0])
        second['verts'] = (np.array(second['verts'])+[500, -1200, 500]).tolist()
        members.append(second)
        expected = visible_lines(members, diagrams.RIGHT, diagrams.UP)
        actual = diagrams.owner_lines(members, diagrams.RIGHT, diagrams.UP)
        self.assertEqual(len(expected), len(actual))
        np.testing.assert_allclose([line for _, line in actual], expected)
        self.assertEqual({owner for owner, _ in actual}, {0, 1})

    def test_empty_and_missing_match_fail(self):
        self.assertEqual(diagrams.owner_lines([], diagrams.RIGHT, diagrams.UP), [])
        with self.assertRaisesRegex(ValueError, 'No geometry'):
            diagrams.match_indices(diagrams.decode_model(model()), {'names': 'Missing*'})

    def test_collection_match_and_alternatives(self):
        members = diagrams.decode_model(model())
        self.assertEqual(diagrams.match_indices(members, {'names': 'Other|P?st', 'collection': 'Str*'}), {0})

    def test_landscape_and_portrait_selected_by_fit(self):
        self.assertEqual(diagrams.page_layout((0, 0, 1000, 100))[:2], (594, 420))
        self.assertEqual(diagrams.page_layout((0, 0, 100, 1000))[:2], (420, 594))


if __name__ == '__main__':
    unittest.main()
