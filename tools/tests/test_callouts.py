import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import callouts as C

MD = """# Doc
## 2. Inputs
Rise 5 x 182 with the same 230 run.
### 5.1 Heels
From v04 the heel is 28 mm
outside the wall face.
```
9 x 9 in a fence
```
## 6. Geometry
stair 800, 5 x 182 / 230, landing.
"""

MODEL = {
    "collections": ["", "Structure/Foundation"],
    "boxes": [["Post_1", 1] + [0] * 13, ["Post_2", 0] + [0] * 13],
    "meshes": [{"name": "Truss_1_W2", "collection": 0}],
}


class GlobTests(unittest.TestCase):
    def test_glob(self):
        re_ = C.glob_re("Truss_*_W?|Post_*")
        self.assertTrue(re_.match("Truss_1_W2"))
        self.assertTrue(re_.match("Post_7"))
        self.assertFalse(re_.match("XPost_7"))

    def test_resolve_with_collection(self):
        self.assertEqual(C.resolve(MODEL, {"names": "Post_*"}), ["Post_1", "Post_2"])
        self.assertEqual(C.resolve(MODEL, {"names": "Post_*", "collection": "Structure/*"}), ["Post_1"])


class DocTests(unittest.TestCase):
    def test_sections(self):
        self.assertEqual([s for s, _ in C.sections(MD)], ["2", "5.1", "6"])

    def test_find_quote_scoped_and_whitespace_insensitive(self):
        self.assertIsNotNone(C.find_quote(MD, "5.1", "the heel is 28 mm outside the wall face"))
        self.assertIsNone(C.find_quote(MD, "2", "5 x 182 / 230"))
        hit = C.find_quote(MD, "5.1", "9 x 9 in a fence")
        self.assertTrue(C.in_fence(MD, hit[0]))
        self.assertEqual(C.section_range(MD, "6")[1], len(MD))


class CheckTests(unittest.TestCase):
    def good(self):
        return {"callouts": [
            {"id": "heel", "label": "Heel", "section": "5.1",
             "quote": "the heel is 28 mm outside the wall face",
             "match": {"names": "Truss_*"}, "anchor": "nearest"},
        ]}

    def test_valid_file(self):
        errors, report = C.check(self.good(), MD, {"v01": MODEL})
        self.assertEqual(errors, [])
        self.assertEqual(len(report), 1)

    def test_errors(self):
        data = {"callouts": [
            {"id": "Bad Id", "label": "", "section": "9", "quote": "nope",
             "match": {"names": "Nothing_*"}, "anchor": "top"},
            {"id": "heel", "label": "x", "section": "5.1", "quote": "9 x 9 in a fence",
             "match": {"names": "Post_*"}},
            {"id": "heel", "label": "x", "section": "6", "match": {}},
        ]}
        errors, _ = C.check(data, MD, {"v01": MODEL})
        joined = "\n".join(errors)
        for needle in ["id must be", "label missing", "not a heading", "quote not found",
                       "anchor must be", "matches no element", "code fence", "duplicate id",
                       "match.names missing"]:
            self.assertIn(needle, joined)

    def test_too_many(self):
        data = {"callouts": [dict(self.good()["callouts"][0], id=f"c{i}") for i in range(16)]}
        errors, _ = C.check(data, MD, {"v01": MODEL})
        self.assertTrue(any("max 15" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
