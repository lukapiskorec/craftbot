"""Cutaway visibility, frame priority and assembled-coordinate contracts."""
import copy
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import callout_diagrams as cd
import callout_cutaways as cut


def box(name, layer, center, half):
    return dict(name=name, layer=layer, group='',
                verts=(cd.CORNERS*np.array(half)+center).tolist(), faces=cd.FACES)


class CutawayTests(unittest.TestCase):
    def test_room_highlights_stay_on_the_wall_with_the_leader(self):
        members=[box('SideBoard_a','cladding ext',[0,0,0],[1,1,1]),
                 box('SideBoard_b','cladding ext',[0,3,0],[1,1,1]),
                 box('EndBoard_a','cladding ext',[3,0,0],[1,1,1])]
        members[0]['group']=members[1]['group']='Facade/SideBoards'
        members[2]['group']='Facade/EndBoards'
        targets=[dict(owner=0,selected={0,1,2},callout={'id':'quiet-room'})]
        reviewed=cut.reviewed_targets(members,targets,('16','gpt6'))
        self.assertEqual(reviewed[0]['selected'],{0,1})
        self.assertEqual(reviewed[0]['owner'],0)
        self.assertEqual(targets[0]['selected'],{0,1,2})
        self.assertEqual(cut.reviewed_targets(members,targets,('16','fable')),targets)

    def test_complete_stair_and_ladder_context_preserves_highlight_selection(self):
        members = [box('selected','fixtures',[0,0,0],[1,1,1]),
                   box('Ladder_Stile_1','fixtures',[10,0,0],[1,1,1]),
                   box('VoidGuard_T_End_TopRail','fixtures',[20,0,0],[1,1,1])]
        members[1]['group']='New/Ladder'
        members[2]['group']='New/Guards'
        targets=[dict(owner=0,point=np.array([-100.,-100.,100.]),selected={0})]
        kept,added=cut.restore_reviewed_context(members,targets,{0},('14','fable'))
        self.assertEqual(kept,{0,1,2})
        self.assertEqual(added,{1,2})
        self.assertEqual(targets[0]['selected'],{0})
        members[1]['group']='Stairs'
        kept,added=cut.restore_reviewed_context(members,targets,{0},('04','fable'))
        self.assertEqual(kept,{0,1})

    def test_white_fill_exception_is_only_experiment_one_slab(self):
        members=[box('Slab','foundations',[0,0,0],[3,3,.1]),
                 box('Post','frame',[0,0,2],[.1,.1,2])]
        self.assertEqual(cut.white_highlights(members,('01','fable')),{0})
        self.assertEqual(cut.white_highlights(members,('02','fable')),set())

    def test_entrance_header_and_right_facade_are_context_only(self):
        members=[box('EntranceJamb_1_0','fixtures',[500,-1550,1000],[45,18,1000]),
                 box('EntranceHeader_0','fixtures',[0,-1550,2145],[540,18,45]),
                 box('EndBoard_-1_0_24_0','cladding ext',[700,-1512,1000],[45,12,1000])]
        members[0]['group']=members[1]['group']='Entrance'
        members[2]['group']='Facade/EndBoards'
        targets=[dict(owner=0,point=np.array([-100.,-100.,100.]),selected={0})]
        kept,added=cut.restore_reviewed_context(members,targets,{0},('16','gpt6'))
        self.assertEqual(kept,{0,1,2})
        self.assertEqual(added,{1,2})
        self.assertEqual(targets[0]['selected'],{0})

    def test_translucent_glass_does_not_hide_framing(self):
        members = [box('post','frame',[0,0,0],[1,1,1]),
                   box('glass','fixtures',[0,0,4],[3,3,.5])]
        right,up = np.array([1.,0,0]),np.array([0.,1,0])
        opaque = cd.owner_lines(members,right,up)
        transparent = cd.owner_lines(members,right,up,transparent={1})
        self.assertNotIn(0,{owner for owner,line in opaque})
        self.assertIn(0,{owner for owner,line in transparent})
        self.assertIn(1,{owner for owner,line in transparent})

    def test_restore_half_roof_without_highlighting_added_context(self):
        members = [box('frame','frame',[-20,-20,0],[1,1,1])]
        members += [box(f'roof{i}','roof',[i*4,10,10],[1,1,.5]) for i in range(10)]
        target = dict(owner=0,point=np.array([-100.,-100.,100.]),selected={0})
        kept,added = cut.restore_enclosure(members,[target],{0},.5)
        self.assertEqual(len(kept-{0}),5)
        self.assertEqual(added,kept-{0})
        self.assertEqual(target['selected'],{0})

    def test_equal_heading_and_quote_sizes_in_layout(self):
        import callout_overviews as overview
        entries = [dict(number=1,anchor=(0,0),callout=dict(label='Heading',quote='Quotation',section='1'))]
        rows,size = overview.layout_rows(entries,150,300,60,heading_delta=0)
        self.assertAlmostEqual(rows[0]['height'],size*1.25+size*1.3+5.5)

    def test_translucent_svg_keeps_opacity_and_drawing_order(self):
        sheet = cut.CutawaySheet(420,594)
        sheet.line((20,20),(40,40))
        sheet.glass_tint([[(20,20),(40,20),(40,40)]],.2)
        sheet.line((20,30),(40,30))
        svg = sheet.svg()
        self.assertIn('fill-opacity="0.2"',svg)
        self.assertLess(svg.index('M20.00,574.00'),svg.index('fill-opacity'))
        self.assertGreater(svg.index('M20.00,564.00'),svg.index('fill-opacity'))
        self.assertEqual(svg.count('<svg '),1)
        self.assertEqual(svg.count('<rect '),1)

    def test_translucent_pane_does_not_clip_highlight_fill_behind_it(self):
        import callout_overviews as overview
        from geometry2d import area
        poly = np.array([(0.,0.),(4.,0.),(4.,4.),(0.,4.)])
        faces = [(0,poly,(np.array([0.,0.,0.]),np.array([0.,0.,1.]))),
                 (1,poly,(np.array([0.,0.,2.]),np.array([0.,0.,1.])))]
        self.assertEqual(overview.visible_regions(faces,{0}),[])
        visible = overview.visible_regions(faces,{0},transparent={1})
        self.assertAlmostEqual(sum(area(p) for p in visible),16)

    def test_ray_identifies_only_nearer_cover(self):
        members = [box('target','frame',[0,0,0],[1,1,1]),
                   box('cover','roof',[0,0,4],[3,3,.5]),
                   box('behind','roof',[0,0,-4],[3,3,.5])]
        view = cut.Projection(members, np.array([1.,0,0]), np.array([0.,1,0]))
        self.assertEqual(view.blockers([0,0,1],0), {1})

    def test_carving_exposes_target_without_moving_or_removing_frame(self):
        members = [box('post','frame',[0,0,0],[1,1,1]),
                   box('roof','roof',[0,0,4],[4,4,.5]),
                   box('back','cladding ext',[0,5,0],[4,.5,4])]
        original = copy.deepcopy(members)
        view = cut.Projection(members,np.array([1.,0,0]),np.array([0.,1,0]))
        targets = [dict(owner=0,point=np.array([0.,0,1]),matched={0},selected={0})]
        kept,removed = cut.carve(members,view,targets,1.0)
        self.assertIn(0,kept)
        self.assertNotIn(1,kept)
        self.assertFalse(view.blockers(targets[0]['point'],0)&kept)
        self.assertEqual(members,original)
        self.assertEqual(kept|removed,set(range(3)))

    def test_target_selection_prefers_unblocked_frame_member(self):
        members = [box('postA','frame',[0,0,0],[1,1,1]),
                   box('postB','frame',[10,0,0],[1,1,1]),
                   box('frameCover','frame',[0,0,4],[3,3,.5])]
        view = cut.Projection(members,np.array([1.,0,0]),np.array([0.,1,0]))
        targets = cut.choose_targets(members,view,[dict(id='posts',match={'names':'post*'})])
        self.assertEqual(targets[0]['owner'],1)
        self.assertFalse(view.blockers(targets[0]['point'],1))

    def test_hidden_target_is_rejected_instead_of_drawn_through_context(self):
        members = [box('post','frame',[0,0,0],[1,1,1])]
        target = dict(owner=0,point=np.array([0.,0,1]),matched={0},selected={0},
                      number=1,callout={'id':'post'})
        with self.assertRaisesRegex(ValueError,'still hidden'):
            cut.anchor_entries(members,[],[target],{0})

    def test_leader_uses_visible_edge_and_omitted_neighbors_are_not_highlighted(self):
        members = [box('post','frame',[0,0,0],[1,1,1]),
                   box('neighbor','frame',[3,0,0],[1,1,1])]
        target = dict(owner=0,point=np.array([0.,0,1]),matched={0,1},selected={0,1},
                      number=1,callout={'id':'post'})
        entries = cut.anchor_entries(members,[(0,((0,0),(2,0)))],[target],{0})
        self.assertEqual(entries[0]['anchor'],[1.,0.])
        self.assertEqual(entries[0]['selected'],{0})
        self.assertFalse(entries[0]['revealed'])


if __name__ == '__main__':
    unittest.main()
