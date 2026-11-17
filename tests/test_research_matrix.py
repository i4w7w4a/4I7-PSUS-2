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
        self.assertEqual(set(populated), {(p, n, a) for p, sides in [("P1", [1, 2, 4]), ("P2", [1, 2, 3, 4]), ("P3", [1, 2, 4]), ("P4", [1, 2, 3]), ("P5", [1, 2, 3, 4]), ("P6", [1])] for n in sides for a in ["yes", "no"]} | {("P3", 3, a) for a in ["yes", "no"]} | {("P4", 4, "no"), ("P4", 4, "yes")})

    def test_p2_voice_author_capture(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        p = m["pillars"][1]
        self.assertEqual([s["title"] for s in p["sides"]], ["Да", "Нет", "Воздержание", "Скольжение"])
        for s in p["sides"]:
            self.assertEqual(s["status"], "author_discussion")
            for a in s["aspects"].values():
                self.assertEqual(a["status"], "captured")
                self.assertIn("6961372944", a["source"])
        self.assertIn("задание", p["sides"][0]["aspects"]["yes"]["text"])
        self.assertIn("аномалию", p["sides"][1]["aspects"]["no"]["text"])
        self.assertIn("намерение", p["sides"][2]["aspects"]["yes"]["text"])
        self.assertIn("адресату", p["sides"][3]["aspects"]["yes"]["text"])
        self.assertIn("внутренний диалог", p["sides"][3]["aspects"]["no"]["text"])
        self.assertIn("ошибочными", p["revision_note"])
        self.assertEqual(m["pillars"][3]["sides"][3]["aspects"]["yes"]["status"], "captured")

    def test_p4_author_capture(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        p = m["pillars"][3]
        for s in p["sides"][:2]:
            for a in s["aspects"].values():
                self.assertEqual(a["status"], "captured")
                self.assertIn("6961642283", a["source"])
        self.assertEqual(p["sides"][3]["aspects"]["yes"]["status"], "captured")
        self.assertIn("двусторонний канал", p["sides"][3]["aspects"]["yes"]["text"])
        self.assertIn("6961828374", p["sides"][3]["aspects"]["yes"]["source"])
        preset = p["sides"][3]
        self.assertEqual(preset["aspects"]["no"]["status"], "captured")
        self.assertIn("6961772643", preset["aspects"]["no"]["source"])
        self.assertIn("пресеты", preset["aspects"]["no"]["text"])
        self.assertIn("4.4.2", preset["revision_note"])
        proposal = p["sides"][2]["candidate_note"]
        self.assertEqual(proposal["origin"], "assistant_proposal_not_author_confirmed")
        self.assertIsNone(proposal["aspect_assignment"])
        self.assertEqual(proposal["status"], "superseded")
        for a in p["sides"][2]["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6961715345", a["source"])
        self.assertIn("строить", p["sides"][2]["aspects"]["yes"]["text"])
        self.assertIn("без вмешательства", p["sides"][2]["aspects"]["no"]["text"])
        self.assertEqual(p["engineering_caution"]["origin"], "assistant_engineering_precaution")
        self.assertIn("пространство", p["sides"][0]["aspects"]["no"]["text"])
        self.assertIn("не выравнивается", p["sides"][1]["aspects"]["no"]["text"])

    def test_p5_execution_and_boundary(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        p = m["pillars"][4]
        s = p["sides"][0]
        for a in s["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6961900886", a["source"])
        self.assertIn("Голосом", s["aspects"]["yes"]["text"])
        self.assertIn("остановить", s["aspects"]["no"]["text"])
        self.assertIn("возможно skills", s["author_examples"]["no"])
        self.assertEqual(s["editorial_interpretation"]["origin"], "assistant_interpretation")
        second = p["sides"][1]
        for a in second["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6961963253", a["source"])
        self.assertIn("что сохранить", second["aspects"]["no"]["text"])
        self.assertEqual(second["accepted_example"]["origin"], "assistant_example_accepted_by_author")
        third = p["sides"][2]
        for a in third["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6962026026", a["source"])
        self.assertIn("поддерживающую", third["aspects"]["yes"]["text"])
        self.assertIn("условие окончания", third["aspects"]["no"]["text"])
        self.assertIn("вечный сон", third["author_example"]["text"])
        fourth = p["sides"][3]
        for a in fourth["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6962084983", a["source"])
        self.assertIn("одну задачу", fourth["aspects"]["yes"]["text"])
        self.assertIn("границы", fourth["aspects"]["no"]["text"])
        self.assertEqual(fourth["editorial_examples"]["origin"], "assistant_examples_not_author_conditions")

    def test_p6_verdict_and_authority_limits(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        p = m["pillars"][5]
        s = p["sides"][0]
        for a in s["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6962175481", a["source"])
        self.assertIn("вердикт", s["aspects"]["yes"]["text"])
        self.assertIn("старшая инстанция", s["aspects"]["no"]["text"])
        self.assertEqual(s["editorial_interpretation"]["origin"], "assistant_interpretation")
        self.assertIn("не назначен", s["limitations"][0])
        for side in p["sides"][1:]:
            for a in side["aspects"].values():
                self.assertEqual(a["status"], "open")
                self.assertIsNone(a["text"])

    def test_gliding_fixation_is_not_contract(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        s = m["pillars"][0]["sides"][3]
        self.assertIn("Скольжение далее", s["aspects"]["yes"]["text"])
        self.assertIn("точка фиксации", s["aspects"]["no"]["text"])
        self.assertIn("6876277084", s["aspects"]["no"]["source"])
        self.assertIn("не установлено", s["open_questions"][0])
        self.assertIn("весь рассматриваемый аспект", s["node_note"])
        for a in m["pillars"][0]["sides"][2]["aspects"].values():
            self.assertEqual(a["status"], "open")

    def test_author_numbering_and_candidates(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        f = json.loads((ROOT / "model/research/foundation-20261114.json").read_text())
        for data in [m, f]:
            self.assertEqual(data["pillars"][1]["title"], "Голос")
            self.assertEqual(data["pillars"][2]["title"], "Скелет связей")
            self.assertEqual(data["numbering_revision"]["previous_to_current"], {"P2": "P3", "P3": "P2"})
            self.assertFalse(data["numbering_revision"]["historical_sources_rewritten"])
        for p in m["pillars"]:
            for s in p["sides"]:
                self.assertEqual(s["id"], f'{p["id"]}.research.side.{s["number"]}')
        for candidate in f["pillars"][1]["candidates"]:
            self.assertEqual(candidate["status"], "under_review")
            self.assertTrue(candidate["id"].startswith("P2."))
        self.assertIn("подтверждён", m["pillars"][2]["open_questions"][0])
        self.assertIn("детализацию", m["pillars"][2]["sides"][0]["aspects"]["no"]["text"])
        self.assertIn("якорь", m["pillars"][2]["sides"][1]["aspects"]["yes"]["text"])

    def test_p3_return_and_observation(self):
        m = json.loads((ROOT / "model/research/matrix-20261114.json").read_text())
        p = m["pillars"][2]
        self.assertIn("пока не найдена", p["sides"][1]["aspects"]["no"]["text"])
        self.assertIn("возврата", p["sides"][1]["aspects"]["yes"]["text"])
        self.assertIn("не натягивать", p["sides"][2]["aspects"]["no"]["text"])
        self.assertIn("6878777871", p["sides"][2]["aspects"]["yes"]["source"])
        self.assertEqual(p["sides"][2]["aspects"]["no"]["status"], "captured")
        gliding = p["sides"][3]
        self.assertIn("Движение вперёд", gliding["aspects"]["yes"]["text"])
        self.assertIn("Возврат внутрь", gliding["aspects"]["no"]["text"])
        self.assertIn("P3/2", gliding["aspects"]["no"]["text"])
        self.assertIn("затем сам исправил", gliding["revision_note"])
        for a in gliding["aspects"].values():
            self.assertEqual(a["status"], "captured")
            self.assertIn("6878834784", a["source"])

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
