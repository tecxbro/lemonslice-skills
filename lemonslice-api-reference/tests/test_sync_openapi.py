from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "sync_openapi.py"
FIXTURES = HERE / "fixtures" / "normalizer_cases.json"

spec = importlib.util.spec_from_file_location("sync_openapi", SCRIPT)
assert spec and spec.loader
sync_openapi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_openapi)


class NormalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_schema_cases(self) -> None:
        empty_spec = {"components": {"schemas": {}}}
        for case in self.cases["schema_cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    sync_openapi.walk_schema(empty_spec, case["schema"]),
                    case["expected"],
                )

    def test_normalize_cases(self) -> None:
        for case in self.cases["normalize_cases"]:
            with self.subTest(case=case["name"]):
                normalized = sync_openapi.normalize(case["spec"])
                operation = normalized["operations"][case["operation"]]
                if "expected_security" in case:
                    self.assertEqual(operation["security"], case["expected_security"])
                if "expected_content_types" in case:
                    self.assertEqual(
                        operation["request"]["content_types"],
                        case["expected_content_types"],
                    )
                    self.assertEqual(
                        sorted(operation["request"]["media_types"]),
                        case["expected_content_types"],
                    )

    def test_compare_cases(self) -> None:
        for case in self.cases["compare_cases"]:
            with self.subTest(case=case["name"]):
                errors = sync_openapi.compare(case["snapshot"], case["current"])
                rendered = "\n".join(errors).lower()
                if "contains" in case:
                    self.assertIn(case["contains"].lower(), rendered)
                for expected in case.get("contains_all", []):
                    self.assertIn(expected.lower(), rendered)


if __name__ == "__main__":
    unittest.main()
