import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ResearchMatrixTests(unittest.TestCase):
    def test_dimensions_and_open_cells(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        self.assertEqual(m["status"], "under_review")
        self.assertFalse(m["canonical_model_changed"])
        self.assertIsNone(m["spatial_assignment"])
        self.assertEqual([p["id"] for p in m["pillars"]], [f"P{i}" for i in range(1, 8)])
        populated = []
        for p in m["pillars"]:
            self.assertEqual([s["number"] for s in p["sides"]], [1, 2, 3, 4])
            for s in p["sides"]:
                self.assertEqual(set(s["aspects"]), {"yes", "no"})
                for name, a in s["aspects"].items():
                    if a["status"] == "captured":
                        populated.append((p["id"], s["number"], name))
                        self.assertTrue(a["text"])
                        self.assertTrue(a["source"])
                    else:
                        self.assertEqual(a["status"], "open")
                        self.assertIsNone(a["text"])
        self.assertEqual(set(populated), {("P1", n, a) for n in [1, 2] for a in ["yes", "no"]})

    def test_second_side_correction(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        a = m["pillars"][0]["sides"][1]["aspects"]
        self.assertIn("ответы", a["yes"]["text"])
        self.assertIn("сомневаться", a["no"]["text"])
        self.assertIn("6875047183", a["yes"]["source"])
        canonical = json.loads((ROOT / "model/4i7.json").read_text())
        for p in canonical["pillars"]:
            for s in p["side_positions"].values():
                self.assertEqual(s["status"], "unassigned")

if __name__ == "__main__":
    unittest.main()
