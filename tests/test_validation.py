"""Normal, malformed, missing-field, limit, and policy tests."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_repository", ROOT / "scripts/validate_repository.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class EvidenceValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_path = ROOT / "tests/fixtures/evidence/valid-safe-test-pe.json"
        self.valid = json.loads(self.valid_path.read_text(encoding="utf-8"))

    def write_case(self, content: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        with handle:
            handle.write(content)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def test_valid_fixture(self) -> None:
        VALIDATOR.validate_evidence(self.valid_path)

    def test_malformed_json(self) -> None:
        path = ROOT / "tests/fixtures/evidence/invalid-malformed.json"
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "malformed JSON"):
            VALIDATOR.validate_evidence(path)

    def test_missing_source(self) -> None:
        path = ROOT / "tests/fixtures/evidence/invalid-missing-source.json"
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "source is required"):
            VALIDATOR.validate_evidence(path)

    def test_empty_file(self) -> None:
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "empty file"):
            VALIDATOR.validate_evidence(self.write_case(""))

    def test_oversize_file(self) -> None:
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "exceeds"):
            VALIDATOR.validate_evidence(self.write_case(" " * (VALIDATOR.MAX_EVIDENCE_BYTES + 1)))

    def test_invalid_classification(self) -> None:
        case = copy.deepcopy(self.valid)
        case["observations"][0]["classification"] = "assumed"
        path = self.write_case(json.dumps(case))
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "invalid classification"):
            VALIDATOR.validate_evidence(path)

    def test_disallowed_source_tool(self) -> None:
        case = copy.deepcopy(self.valid)
        case["observations"][0]["source"]["tool"] = "read_memory"
        path = self.write_case(json.dumps(case))
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "disallowed source tool"):
            VALIDATOR.validate_evidence(path)

    def test_sensitive_identifier_key(self) -> None:
        case = copy.deepcopy(self.valid)
        case["metadata"]["executable_path"] = "C:/sensitive/example.exe"
        path = self.write_case(json.dumps(case))
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "sensitive evidence key"):
            VALIDATOR.validate_evidence(path)


class RepositoryValidationTests(unittest.TestCase):
    def test_runtime_catalog_contract(self) -> None:
        total, allowed, server_total, version = VALIDATOR.validate_catalog()
        self.assertEqual(total, 273)
        self.assertEqual(allowed, 24)
        self.assertEqual(server_total, 239)
        self.assertEqual(version, "7.0.0")

    def test_skill_structure_and_safety(self) -> None:
        self.assertEqual(
            VALIDATOR.validate_skills(),
            ["ghidra-static-analysis", "malware-analysis-report"],
        )

    def test_public_docs_have_no_internal_identifiers(self) -> None:
        self.assertGreater(VALIDATOR.validate_document_hygiene(), 0)

    def test_expected_reports(self) -> None:
        self.assertEqual(len(VALIDATOR.validate_reports()), 5)


if __name__ == "__main__":
    unittest.main()
