"""Tests of the fabrication kit: qr_code, cutlist, hidden_lines, vector_pdf, drafting, newsprint."""
import math
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import qr_code
import cutlist
import vector_pdf
import drafting
import title_blocks
import newsprint
from hidden_lines import visible_lines


def box(name, x0, x1, y0, y1, z0, z1, stock="3x5"):
    """A box member wound outwards, like export_members writes."""
    verts = [[x, y, z] for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    faces = [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]]
    return {"name": name, "group": "Test", "layer": "frame", "stock": stock, "verts": verts, "faces": faces}


def total_length(lines):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in lines)


class QrCode(unittest.TestCase):
    def test_reed_solomon_matches_published_vector(self):
        data = [32, 91, 11, 120, 209, 114, 220, 77, 67, 64, 236, 17, 236, 17, 236, 17]
        self.assertEqual(qr_code.reed_solomon(data, 10), [196, 35, 39, 119, 235, 215, 231, 226, 93, 23])

    def test_format_bits_for_level_l_mask_0(self):
        m = qr_code.build(1, [0] * 26, 0)
        bits = [m[i][8] for i in range(6)] + [m[7][8], m[8][8], m[8][7]] + [m[8][14 - i] for i in range(9, 15)]
        self.assertEqual("".join("1" if b else "0" for b in reversed(bits)), "111011111000100")

    def test_a_viewer_url_fits_version_5(self):
        url = "https://lukapiskorec.github.io/craftbot/?model=models%2F16_Expressive_Structure%2Fgpt6_v02.json"
        self.assertEqual(len(qr_code.qr_matrix(url)), 37)


class Cutlist(unittest.TestCase):
    def test_measure_reads_length_and_section_of_a_box(self):
        length, thickness, face, square = cutlist.measure(box("A_0", 0, 100, 0, 5, 0, 3))
        self.assertEqual((round(length, 6), round(thickness, 6), round(face, 6), square), (100, 3, 5, True))

    def test_pack_first_fit_with_kerf(self):
        self.assertEqual(len(cutlist.pack([150, 150], 300, kerf=1)), 2)      # 150 + 1 + 150 > 300
        self.assertEqual(len(cutlist.pack([150, 149], 300, kerf=1)), 1)
        with self.assertRaises(AssertionError):
            cutlist.pack([301], 300)

    def test_write_cutlist_counts_sticks_and_rejects_a_wrong_profile(self):
        data = {"stick_length": 300, "members": [box(f"Rail_{i}", 0, 200, 0, 5, 0, 3) for i in range(3)]}
        with tempfile.TemporaryDirectory() as out:
            order = cutlist.write_cutlist(data, out, "t", "i", {"3x5": 0.4}, spare=0)
            self.assertEqual(order, {"3x5": 3})
            self.assertTrue(os.path.isfile(os.path.join(out, "cutlist.csv")))
            data["members"].append(box("Fat_0", 0, 50, 0, 9, 0, 3))
            with self.assertRaises(AssertionError):
                cutlist.write_cutlist(data, out, "t", "i", {"3x5": 0.4})


class HiddenLines(unittest.TestCase):
    def test_a_box_seen_from_the_front_shows_its_outline(self):
        lines = visible_lines([box("A", 0, 10, 0, 10, 0, 10)], drafting.X, drafting.Z)
        self.assertAlmostEqual(total_length(lines), 40, places=6)

    def test_a_nearer_box_hides_the_one_behind(self):
        front, back = box("F", 0, 10, 0, 1, 0, 10), box("B", 2, 8, 5, 6, 2, 8)      # viewer at -y
        lines = visible_lines([front, back], drafting.X, drafting.Z)
        self.assertAlmostEqual(total_length(lines), 40, places=6)

    def test_touching_boxes_keep_the_joint_line(self):
        left, right = box("L", 0, 10, 0, 10, 0, 10), box("R", 10, 20, 0, 10, 0, 10)
        lines = visible_lines([left, right], drafting.X, drafting.Z)
        self.assertAlmostEqual(total_length(lines), 80, places=6)      # both outlines, the shared edge twice


class VectorPdf(unittest.TestCase):
    def test_pdf_has_one_page_per_sheet(self):
        sheet = vector_pdf.Sheet(*vector_pdf.A2)
        sheet.poly([(10, 10), (60, 10), (60, 40)])
        sheet.text(10, 45, "(a)", 3)
        with tempfile.TemporaryDirectory() as out:
            path = os.path.join(out, "t.pdf")
            vector_pdf.write_pdf(path, [sheet, sheet])
            with open(path, "rb") as f:
                body = f.read()
        self.assertTrue(body.startswith(b"%PDF-1.4") and body.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"/Count 2", body)
        self.assertIn("<polygon", sheet.svg())


class Drafting(unittest.TestCase):
    def test_unroll_keeps_lengths_across_a_fold(self):
        flat_facet = [([0, 0, 0], [10, 0, 0], [10, 5, 0], [0, 5, 0])]
        up_facet = [([10, 0, 0], [10, 0, 10], [10, 5, 10], [10, 5, 0])]      # folds up 90 degrees at x = 10
        (a,), (b,) = drafting.unroll([flat_facet, up_facet])
        self.assertAlmostEqual(b[1][0] - a[0][0], 20, places=9)      # 10 + 10 laid in one line
        self.assertAlmostEqual(math.dist(b[0], b[3]), 5, places=9)

    def test_depth_layers_count_up_from_the_paper(self):
        members = [box("Near", 0, 1, 0, 1, 0, 1), box("Far", 0, 1, 5, 6, 0, 1)]
        layers = drafting.depth_layers(members, drafting.cross(drafting.X, drafting.Z))      # viewer at -y
        self.assertEqual(layers, {"Near": "L2", "Far": "L1"})

    def test_min_scale_and_place_agree(self):
        scale = drafting.min_scale((4.6, 3.3, 7.3))
        self.assertEqual(scale, 14)      # the default footer r keeps 32 mm clear; 15 with the 40 mm footer l
        self.assertEqual(drafting.min_scale((4.6, 3.3, 7.3), footer="l"), 15)
        w, h = vector_pdf.A2
        drafting.place((0, 0, 4600 / scale, 7300 / scale), w, h)      # fits
        with self.assertRaises(AssertionError):
            drafting.place((0, 0, 4600 / 13, 7300 / 13), w, h)

    def test_coincident_plies_are_labelled_once_and_crossed_braces_are_not_merged(self):
        plies = [box("Ply_a", 0, 100, 0, 3, 0, 5), box("Ply_b", 0, 100, 6, 9, 0, 5)]      # same outline seen from -y
        drawing = drafting.Drawing(plies, drafting.X, drafting.Z)
        kept, codes = drafting.merge_coincident(plies, drafting.depth_layers(plies, drawing.toward), drawing)
        self.assertEqual(([m["name"] for m in kept], codes), (["Ply_a"], {"Ply_a": "L1+L2"}))
        rise, fall = box("Rise", 0, 1, 0, 1, 0, 1), box("Fall", 0, 1, 0, 1, 0, 1)
        rise["verts"] = [[0, 0, 0], [100, 0, 100], [100, 3, 100], [0, 3, 0], [0, 0, 5], [100, 0, 105], [100, 3, 105], [0, 3, 5]]
        fall["verts"] = [[0, 0, 100], [100, 0, 0], [100, 3, 0], [0, 3, 100], [0, 0, 105], [100, 0, 5], [100, 3, 5], [0, 3, 105]]
        for m in (rise, fall):
            m["faces"] = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [3, 2, 6, 7], [0, 3, 7, 4], [1, 2, 6, 5]]
        kept, _ = drafting.merge_coincident([rise, fall], {"Rise": "L1", "Fall": "L2"}, drawing)
        self.assertEqual(len(kept), 2)

    def test_parts_without_a_stick_stay_out_of_the_cut_list(self):
        slab = box("Raft_0", 0, 200, 0, 200, 0, 9, stock=None)
        data = {"stick_length": 300, "members": [slab, box("Rail_0", 0, 200, 0, 5, 0, 3)]}
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(cutlist.write_cutlist(data, out, "t", "i", {"3x5": 0.4}, spare=0), {"3x5": 1})

    def test_section_shades_the_cut_face(self):
        drawing = drafting.Drawing([box("A", 0, 10, 0, 10, 0, 10)], drafting.X, drafting.Y, cut=5)
        self.assertTrue(any(fill == 0.7 for _, _, fill, _ in drawing.faces))

    def test_sheet_set_writes_numbered_files(self):
        sheets = drafting.SheetSet(15, "Experiment", "subtitle", viewer_url="https://example.org/x")
        sheets.view("Plan, test", drafting.Drawing([box("A", 0, 100, 0, 50, 0, 3)], drafting.X, drafting.Y))
        with tempfile.TemporaryDirectory() as out:
            sheets.write(os.path.join(out, "pdf"), os.path.join(out, "svg"))
            self.assertEqual(sorted(os.listdir(os.path.join(out, "pdf"))), ["00_all_sheets.pdf", "01_plan_test.pdf"])
            self.assertEqual(os.listdir(os.path.join(out, "svg")), ["01_plan_test.svg"])

    def test_a_landscape_sheet_is_turned_upright_when_added(self):
        sheets = drafting.SheetSet(15, "E", "s", credits=[("SUPERVISION", "someone")])
        wide = sheets.blank(landscape=True)
        wide.text(100, 20, "label", 3)
        wide.line((0, 0), (594, 0))
        sheets.add("Wide", wide)
        sheet = sheets.sheets[0][1]
        self.assertEqual((sheet.w, sheet.h), vector_pdf.A2)
        self.assertEqual(sheet.ops[1][1], [(420, 0), (420, 594)])      # the old bottom edge lies along the right edge
        self.assertEqual((sheet.ops[0][1], sheet.ops[0][2], sheet.ops[0][6][6]), (400, 100, 0))      # the label reads upright
        self.assertEqual(wide.ops[0][6][6], -90)      # because the blank set it turned
        self.assertEqual(wide.offset(0, -1), (-1, 0))
        self.assertIn('rotate(90', wide.svg())
        self.assertIn("SUPERVISION", sheet.svg())
        upright = drafting.SheetSet(15, "E", "s", upright=False)
        upright.add("Wide", upright.blank(landscape=True))
        self.assertEqual(upright.sheets[0][1].w, 594)

    def test_a_plain_page_takes_a_number_but_no_title_block(self):
        sheets = drafting.SheetSet(15, "E", "s")
        sheets.page("Text", sheets.blank())
        sheets.add("Plan", sheets.blank())
        self.assertEqual(sheets.sheets[0][1].ops, [])
        self.assertIn(">02<", sheets.sheets[1][1].svg())

    def test_every_footer_draws_and_the_default_names_its_fonts(self):
        for key in title_blocks.FOOTERS:
            sheets = drafting.SheetSet(15, "Experiment", "subtitle", viewer_url="https://example.org/x", studio="{mark}", footer=key)
            sheets.add("Title", sheets.blank(landscape=key == "a"), "note")
            self.assertIn("MEK-Mono", sheets.sheets[0][1].svg())
        self.assertEqual(title_blocks.DEFAULT, "r")
        default = drafting.SheetSet(15, "E", "s")
        default.add("Title", default.blank())
        self.assertIn("Segoe UI", default.sheets[0][1].svg())
        with self.assertRaises(AssertionError):
            drafting.SheetSet(15, "E", "s", footer="z")


class Newsprint(unittest.TestCase):
    def test_parse_reads_headings_items_tables_and_bold(self):
        blocks = newsprint.parse("# Head\n\nOne **two,** three.\n\n- item\n\n| A | B |\n|---|---|\n| a | b |\n\n![fig]")
        self.assertEqual([b[0] for b in blocks], ["h1", "p", "item", "p", "p", "figure"])
        self.assertEqual(blocks[1][1], [("One", False, False), ("two,", True, False), ("three.", False, False)])
        self.assertEqual(blocks[4][1][0], ("a.", True, False))

    def test_flow_justifies_lines_and_fills_pages(self):
        press = newsprint.Newsprint(lambda sheet, n: sheet.h-20, {"fig": ("caption", lambda sheet, x, y, w: 30.0)})
        blocks = newsprint.parse("## Head\n\n" + ("word " * 400) + "\n\n![fig]\n\n" + ("more text " * 200))
        pages, fill = press.flow(blocks, 3.0)
        self.assertEqual(len(pages), 1)
        widths = [op[6][7] for op in pages[0].ops if op[0] == "text" and op[6][7]]
        full = {round(press.width, 3), round(press.width - newsprint.INDENT, 3)}      # a first line is indented
        self.assertTrue(widths and all(round(w, 3) in full for w in widths))      # justified lines fit the column
        self.assertTrue(0 < fill < 1)
        size, pages, fill, cut = newsprint.fit(press, blocks * 30, max_pages=2, sizes=[3.0, 2.0])
        self.assertEqual((size, len(pages), cut), (2.0, 2, True))


if __name__ == "__main__":
    unittest.main()
