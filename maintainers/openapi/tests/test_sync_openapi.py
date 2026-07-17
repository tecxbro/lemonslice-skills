from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "sync_openapi.py"
FIXTURES = HERE / "fixtures"
INTEGRATION_FIXTURE = FIXTURES / "lemonslice-openapi.sanitized.json"

spec = importlib.util.spec_from_file_location("sync_openapi", SCRIPT)
assert spec and spec.loader
sync_openapi = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sync_openapi
spec.loader.exec_module(sync_openapi)


class NormalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads((FIXTURES / "normalizer_cases.json").read_text(encoding="utf-8"))

    def test_schema_cases(self) -> None:
        empty_spec = {"components": {"schemas": {}}}
        for case in self.cases["schema_cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    sync_openapi.normalize_schema(empty_spec, case["schema"]),
                    case["expected"],
                )

    def test_full_operation_cases(self) -> None:
        for case in self.cases["normalize_cases"]:
            with self.subTest(case=case["name"]):
                normalized = sync_openapi.normalize(case["spec"])
                self.assertEqual(
                    normalized["operations"][case["operation"]],
                    case["expected"],
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

    def test_sanitized_lemonslice_fixture(self) -> None:
        source = json.loads(INTEGRATION_FIXTURE.read_text(encoding="utf-8"))
        normalized = sync_openapi.normalize(source)

        hosted = normalized["operations"]["POST /liveai/rooms"]
        self.assertEqual(
            hosted["responses"]["201"]["schema"]["required"],
            ["image_url", "room_url", "session_id", "token"],
        )
        self.assertEqual(
            hosted["responses"]["401"]["schema"]["required"],
            ["detail"],
        )

        sessions = normalized["operations"]["POST /liveai/sessions"]
        selector_variants = sessions["request"]["schema"]["one_of"]
        self.assertEqual(selector_variants[0]["forbidden"], ["agent_id"])
        self.assertEqual(selector_variants[1]["forbidden"], ["agent_image_url"])

        status = normalized["operations"]["GET /liveai/sessions/{session_id}"]
        self.assertTrue(status["parameters"]["path"]["session_id"]["required"])
        status_schema = status["responses"]["200"]["schema"]
        self.assertEqual(
            status_schema["properties"]["session_status"]["enum"],
            ["ACTIVE", "COMPLETED", "FAILED", "QUEUED", "TIMED_OUT"],
        )
        self.assertTrue(status_schema["properties"]["cost"]["nullable"])

        listing = normalized["operations"]["GET /liveai/rooms"]
        self.assertEqual(
            listing["parameters"]["query"]["limit"]["schema"]["maximum"],
            100,
        )

    def test_probe_metadata_detects_normalized_instability(self) -> None:
        body_a = b'{"openapi":"3.1.0","paths":{}}'
        body_b = b'{"openapi":"3.1.0","paths":{"/x":{}}}'
        result_a = sync_openapi.FetchResult(
            body_a, "a", "https://example/a", None, None, None, None
        )
        result_b = sync_openapi.FetchResult(
            body_b, "b", "https://example/b", None, None, None, None
        )
        metadata = sync_openapi.source_metadata(
            "https://example/openapi.json",
            [result_a, result_b],
            [
                sync_openapi.canonical_sha(sync_openapi.normalize_openapi_bytes(body_a)),
                sync_openapi.canonical_sha(sync_openapi.normalize_openapi_bytes(body_b)),
            ],
        )
        self.assertFalse(metadata["raw_consistent"])
        self.assertFalse(metadata["normalized_consistent"])


if __name__ == "__main__":
    unittest.main()
