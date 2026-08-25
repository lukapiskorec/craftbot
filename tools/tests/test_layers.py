import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import layers as L


class ClassifyTests(unittest.TestCase):
    def test_structure_members_are_frame_whatever_the_collection(self):
        self.assertEqual(L.classify("04_x", "Ceiling", "Ceiling_Nog_3"), "frame")
        self.assertEqual(L.classify("04_x", "Structure/Roof_Framing", "Truss_2_Web"), "frame")
        self.assertEqual(L.classify("11_x", "Walls", "Beam_WingOpening_2"), "frame")

    def test_roof_is_covering_not_framing(self):
        self.assertEqual(L.classify("04_x", "Roof/Roof_Covering", "Fascia_S_1"), "roof")
        self.assertEqual(L.classify("04_x", "Roof/Roof_Covering", "Ridge_Cap_N_2"), "roof")
        self.assertEqual(L.classify("04_x", "Ceiling", "Ceiling_Ply_4"), "roof")
        self.assertEqual(L.classify("11_x", "Sheathing/SH_Main", "Board_N_12"), "roof")
        self.assertEqual(L.classify("01_x", "Roof_Rafters", "Rafter_7"), "frame")

    def test_wall_sheathing_splits_ext_int(self):
        self.assertEqual(L.classify("04_x", "Facade/Exterior_Sheathing", "Ply_Ext_S_1"), "cladding ext")
        self.assertEqual(L.classify("04_x", "Facade/Interior_Sheathing", "Ply_Int_S_1"), "cladding int")
        self.assertEqual(L.classify("04_x", "Facade/Interior_Sheathing", "Ply_P1_3"), "interior")
        self.assertEqual(L.classify("04_x", "Roof/Gable_Sheathing", "Gable_Ply_2"), "cladding ext")
        self.assertEqual(L.classify("07_x", "Old_House/Exterior_Sheathing", "OH_Ply_Ext_N_1"), "cladding ext")

    def test_fixtures(self):
        self.assertEqual(L.classify("04_x", "Facade/Openings", "Window_S_Glass"), "fixtures")
        self.assertEqual(L.classify("04_x", "Stairs", "Tread_3"), "fixtures")
        self.assertEqual(L.classify("08_x", "Balustrade", "Bal_Void_N_Post_2"), "fixtures")
        self.assertEqual(L.classify("06_x", "Structure/Eave_Rails", "Eave_Rail_1"), "frame")

    def test_foundations(self):
        self.assertEqual(L.classify("04_x", "Structure/Foundation", "Footing_1"), "foundations")
        self.assertEqual(L.classify("09_x", "Podium/Podium_Frame", "Column_S_2"), "foundations")

    def test_uninformative_collection_is_ignored(self):
        self.assertEqual(L.classify("07_x", "Structure", "Ply_S_ext_seg_1"), "cladding ext")

    def test_overrides_per_experiment(self):
        self.assertEqual(L.classify("08_x", "Facade/East/East_Battens", "Rail_E_1"), "cladding ext")
        self.assertEqual(L.classify("08_x", "Facade/South/South_Windows", "CanopyStrut"), "fixtures")
        self.assertEqual(L.classify("04_x", "Facade/Beading", "Skirt_S_0"), "cladding int")
        self.assertEqual(L.classify("04_x", "Facade/Beading", "Skirt_P1_A_2"), "interior")
        self.assertEqual(L.classify("09_x", "Core/Core_Walls", "Core_W_S3"), "interior")
        self.assertEqual(L.classify("09_x", "Core/Core_Slabs", "Core_Slab_Corr_2"), "floors")
        self.assertEqual(L.classify("09_x", "Podium/Podium_Walls", "Podium_Core_S_S1"), "foundations")
        self.assertEqual(L.classify("09_x", "Openings/Glazing", "Roof_Glass_S_1"), "fixtures")
        self.assertEqual(L.classify("09_x", "Roof/Roof_Panels", "Roof_S_1"), "roof")
        self.assertEqual(L.classify("09_x", "Floors/Ribs", "Rib_L2_3"), "floors")
        self.assertEqual(L.classify("09_x", "Structure/Knee_Walls", "Knee_S_L5"), "interior")
        self.assertEqual(L.classify("09_x", "Podium/Podium_Stairs", "Flight_A_1"), "fixtures")
        self.assertEqual(L.classify("09_x", "", "Ext_Long_+Y_L1"), "frame")
        self.assertEqual(L.classify("02_x", "", "diag_3"), "frame")

    def test_unmatched_is_other(self):
        self.assertEqual(L.classify("99_x", "", "Mystery_1"), "other")


class BakeTests(unittest.TestCase):
    def test_bake_dict_adds_layer_fields_idempotently(self):
        model = {
            "collections": ["", "Roof/Roof_Covering"],
            "boxes": [["Post_1", 0] + [0.0] * 12, ["Fascia_S_1", 1] + [0.0] * 12],
            "meshes": [{"name": "Footing_1", "collection": 0, "verts": [], "faces": []}],
        }
        L.bake_dict(model, "04_Construction_Manual_Blender_Python")
        L.bake_dict(model, "04_Construction_Manual_Blender_Python")
        self.assertEqual(model["layers"], L.LAYERS)
        self.assertEqual(len(model["boxes"][0]), 15)
        self.assertEqual(model["layers"][model["boxes"][0][14]], "frame")
        self.assertEqual(model["layers"][model["boxes"][1][14]], "roof")
        self.assertEqual(model["layers"][model["meshes"][0]["layer"]], "foundations")

    def test_experiment_of(self):
        self.assertEqual(
            L.experiment_of("experiments/04_Construction_Manual_Blender_Python/Fable/x.py"),
            "04_Construction_Manual_Blender_Python")
        self.assertEqual(
            L.experiment_of(r"C:\viewer\models\09_How_to_CLT_Blender_Python\fable_v01.json"),
            "09_How_to_CLT_Blender_Python")


if __name__ == "__main__":
    unittest.main()
