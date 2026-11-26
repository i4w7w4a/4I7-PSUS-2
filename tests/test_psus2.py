"""Чтение независимым участником из другого каталога и сверка при возвращении."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import context_pack
import project_memory as memory


class Psus2Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name) / "4I7 PSUS 2"
        for path in ("psus2", "scripts/project_memory.py", *context_pack.SOURCE_PATHS):
            target = self.project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, target)
        self.store = self.project / "memory/projects/4i7-psus-2"
        memory.init_store(self.store, "4i7-psus-2", "owner")
        self.apply("import_source", id="S-1", source_key="request", content="Условия опыта",
                   locator="fixture:request", author_ref="owner")
        self.ref = {"id": "S-1", "version": 1}

    def apply(self, action, **payload):
        revision = memory.read_store(self.store)["revision"]
        memory.apply_operation(self.store, {
            "project_id": "4i7-psus-2", "actor": "owner", "action": action,
            "operation_id": f"op-{revision}", "expected_revision": revision, "payload": payload,
        })

    def run_cli(self, *args):
        return subprocess.run([self.project / "psus2", *args], cwd=self.project.parent,
                              capture_output=True, text=True)

    def test_summary_keeps_rules_objections_and_return_conditions(self):
        self.apply("put_record", id="D1", kind="decision", scope="pilot", key="format",
                   text="Сохранить WAV", source_refs=[self.ref])
        self.apply("accept", id="D1", authority_ref=self.ref, supersedes=[])
        self.apply("put_record", id="D3", kind="decision", scope="project", key="id",
                   text="Сохранить идентификатор", source_refs=[self.ref])
        self.apply("accept", id="D3", authority_ref=self.ref, supersedes=[])
        self.apply("put_record", id="D2", kind="decision", scope="pilot", key="format",
                   text="Рассмотреть FLAC", source_refs=[self.ref])
        self.apply("put_record", id="A1", kind="claim", scope="pilot", assessment="unverified",
                   text="Файл не помещается", source_refs=[self.ref])
        self.apply("link", **{"from": "A1", "to": "D1", "kind": "contradicts"})
        self.apply("mark_review", id="D1", reason="Проверить объём файла")
        self.apply("put_record", id="R1", kind="review-anchor", scope="pilot", text="Каков объём?",
                   source_refs=[self.ref], trigger="После экспорта",
                   exit_criteria="Измерить файл", reopen_if="Новый экспорт")
        self.apply("import_source", id="S-1", source_key="request", content="Новая редакция",
                   locator="fixture:request-2", author_ref="owner")
        self.apply("import_source", id="S-UNUSED", source_key="unrelated", content="Иной опыт",
                   locator="fixture:unused", author_ref="owner")

        result = self.run_cli("--node", "P7.1")
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("Фокус P7.1 · Хранитель", "P7.1.1", "P7.1.2", "Действующие положения (2)",
                         "D1 · Сохранить WAV [S-1:v1]", "Предложения (1)", "D2 · Рассмотреть FLAC",
                         "A1 ↔ D1", "Наблюдения (1)", "Файл не помещается [S-1:v1] · unverified", "Открытые вопросы (1)", "После экспорта",
                         "Требуют пересмотра", "Область · project\n    D3", "Область · pilot\n    D1"):
            self.assertIn(expected, result.stdout)
        self.assertEqual(result.stdout.count("S-1:v1 → fixture:request\n"), 1)
        self.assertNotIn("fixture:request-2", result.stdout)
        self.assertNotIn("S-UNUSED", result.stdout)
        self.assertNotIn("P7.2.1", result.stdout)
        self.assertNotIn("Следующий шаг", result.stdout)

    def test_default_and_personal_packets_read_one_checked_project(self):
        pack = json.loads(self.run_cli("--json").stdout)
        self.assertEqual(pack["requested_nodes"], ["i"])
        self.assertEqual(pack["working_memory"]["project_id"], "4i7-psus-2")
        self.assertIsNone(pack["memory_binding"]["participant_checkpoint"])
        memory.save_checkpoint(self.store, "oracle", pack["snapshot"]["content_id"],
                               "Опыт", "Открыть файл", memory.read_store(self.store)["head"])
        resumed = self.run_cli("--participant", "oracle")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("Открыть файл", resumed.stdout)
        self.assertNotIn("Открыть файл", self.run_cli().stdout)
        self.apply("mark_review", id="S-1", reason="Изменилось основание")
        for args in (("--participant", "oracle"), ("--participant", "new"), ("--node", "P8")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("Ошибка чтения", result.stderr)
        self.assertEqual(self.run_cli().returncode, 0)


if __name__ == "__main__":
    unittest.main()
