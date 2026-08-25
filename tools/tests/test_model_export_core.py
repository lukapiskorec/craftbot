import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import model_export_core as core

CUBE_VERTS = [(1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1),
              (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1)]
CUBE_FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
              (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]


class TestCubeDetect(unittest.TestCase):
    def test_exact_cube(self):
        self.assertTrue(core.is_unit_cube(CUBE_VERTS, CUBE_FACES))

    def test_cube_within_eps(self):
        verts = [(x + 1e-8, y, z) for x, y, z in CUBE_VERTS]
        self.assertTrue(core.is_unit_cube(verts, CUBE_FACES))

    def test_not_cube_vert_count(self):
        self.assertFalse(core.is_unit_cube(CUBE_VERTS[:6], CUBE_FACES))

    def test_not_cube_moved_vert(self):
        verts = list(CUBE_VERTS)
        verts[0] = (2, 1, -1)
        self.assertFalse(core.is_unit_cube(verts, CUBE_FACES))

    def test_prism_is_not_cube(self):
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1)]
        faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        self.assertFalse(core.is_unit_cube(verts, faces))


class TestRound(unittest.TestCase):
    def test_int_collapse(self):
        self.assertEqual(core.rnd(2.0000001), 2)
        self.assertIsInstance(core.rnd(2.0000001), int)

    def test_keep_decimals(self):
        self.assertEqual(core.rnd(2.123456789), 2.12346)


class TestBuildModel(unittest.TestCase):
    def records(self):
        return [
            {"name": "Post_01", "collection": "Frame", "kind": "box",
             "matrix": [1, 0, 0, 0.5, 0, 1, 0, 0, 0, 0, 2, 1.0]},
            {"name": "Board_01", "collection": "", "kind": "mesh",
             "verts": [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0], "faces": [[0, 1, 2, 3]]},
        ]

    def test_build(self):
        d = core.build_model_dict("experiments/x/v01.py", self.records())
        self.assertEqual(d["format"], "craftbot-model")
        self.assertEqual(d["version"], 1)
        self.assertEqual(d["collections"], ["", "Frame"])
        # row[14] = viewer layer index (Frame collection -> "frame")
        self.assertEqual(d["boxes"], [["Post_01", 1, 1, 0, 0, 0.5, 0, 1, 0, 0, 0, 0, 2, 1, 0]])
        self.assertEqual(d["layers"][0], "frame")
        self.assertEqual(d["meshes"][0]["collection"], 0)
        self.assertEqual(d["layers"][d["meshes"][0]["layer"]], "cladding ext")

    def test_dump_compact(self):
        d = core.build_model_dict("s", self.records())
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "m.json")
            n = core.dump_compact(d, p)
            with open(p, "rb") as f:
                raw = f.read()
            self.assertEqual(n, len(raw))
            self.assertNotIn(b": ", raw)
            self.assertEqual(json.loads(raw)["format"], "craftbot-model")


class TestIndex(unittest.TestCase):
    def test_index(self):
        entries = [
            {"experiment": "02_Carport_Gothic_Blender_Python", "agent": "Fable",
             "v": "v02", "file": "02/f_v02.json", "elements": 5, "bytes": 100},
            {"experiment": "02_Carport_Gothic_Blender_Python", "agent": "Fable",
             "v": "v01", "file": "02/f_v01.json", "elements": 4, "bytes": 90},
            {"experiment": "01_Carport_Assembly_Blender_Python", "agent": "ChatGPT 5.1",
             "v": "v01", "file": "01/c_v01.json", "elements": 3, "bytes": 80},
        ]
        idx = core.build_index(entries)
        exps = idx["experiments"]
        self.assertEqual([e["id"] for e in exps],
                         ["01_Carport_Assembly_Blender_Python",
                          "02_Carport_Gothic_Blender_Python"])
        self.assertEqual(exps[0]["title"], "01 Carport Assembly")
        self.assertEqual(exps[1]["title"], "02 Carport Gothic")
        vs = exps[1]["runs"][0]["versions"]
        self.assertEqual([v["v"] for v in vs], ["v01", "v02"])

    def test_agent_order(self):
        entries = [
            {"experiment": "01_X_Blender_Python", "agent": "Fable",
             "v": "v01", "file": "a.json", "elements": 1, "bytes": 10},
            {"experiment": "01_X_Blender_Python", "agent": "ChatGPT 5.1",
             "v": "v01", "file": "b.json", "elements": 1, "bytes": 10},
        ]
        idx = core.build_index(entries)
        runs = idx["experiments"][0]["runs"]
        self.assertEqual([r["agent"] for r in runs], ["ChatGPT 5.1", "Fable"])


class TestIndexRationale(unittest.TestCase):
    def test_run_carries_rationale_when_any_entry_has_one(self):
        base = {"experiment": "01_X", "file": "f", "elements": 1, "bytes": 1}
        idx = core.build_index([
            dict(base, agent="Fable", v="v01", rationale=None),
            dict(base, agent="Fable", v="v02", rationale="01_X/fable_rationale.md",
                 callouts="01_X/fable_callouts.json"),
            dict(base, agent="ChatGPT 5.1", v="v01", rationale=None),
        ])
        runs = {r["agent"]: r for r in idx["experiments"][0]["runs"]}
        self.assertEqual(runs["Fable"]["rationale"], "01_X/fable_rationale.md")
        self.assertEqual(runs["Fable"]["callouts"], "01_X/fable_callouts.json")
        self.assertNotIn("rationale", runs["ChatGPT 5.1"])
        self.assertNotIn("callouts", runs["ChatGPT 5.1"])


class TestWinding(unittest.TestCase):
    FLAT = [c for v in CUBE_VERTS for c in v]

    def test_signed_volume_sign(self):
        self.assertAlmostEqual(core.signed_volume(self.FLAT, CUBE_FACES), 8.0)
        reversed_faces = [tuple(reversed(f)) for f in CUBE_FACES]
        self.assertAlmostEqual(core.signed_volume(self.FLAT, reversed_faces), -8.0)

    def test_orient_outward_flips_only_inverted(self):
        self.assertEqual(core.orient_outward(self.FLAT, CUBE_FACES),
                         [list(f) for f in CUBE_FACES])
        reversed_faces = [tuple(reversed(f)) for f in CUBE_FACES]
        fixed = core.orient_outward(self.FLAT, reversed_faces)
        self.assertGreater(core.signed_volume(self.FLAT, fixed), 0)

    def test_build_model_dict_orients_meshes(self):
        rec = {"name": "P", "collection": "", "kind": "mesh", "verts": self.FLAT,
               "faces": [tuple(reversed(f)) for f in CUBE_FACES]}
        model = core.build_model_dict("s", [rec])
        self.assertGreater(core.signed_volume(self.FLAT, model["meshes"][0]["faces"]), 0)


if __name__ == "__main__":
    unittest.main()
