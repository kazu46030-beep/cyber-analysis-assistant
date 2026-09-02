"""Tests for repeated report-generation evaluation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_report_runs", ROOT / "scripts/evaluate_report_runs.py"
)
assert SPEC and SPEC.loader
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


class ReportRunTests(unittest.TestCase):
    def test_three_runs_are_semantically_consistent(self) -> None:
        result = EVALUATOR.evaluate_all()
        self.assertEqual(result["run_count"], 3)
        self.assertEqual(result["total_reports"], 15)
        self.assertTrue(result["semantic_consistency"])
        self.assertTrue(all(run["critical_finding_recall"] == 1.0 for run in result["runs"]))
        self.assertEqual(len({run["semantic_fingerprint"] for run in result["runs"]}), 1)

    def test_missing_report_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(EVALUATOR.EvaluationError, "missing or empty"):
                EVALUATOR.evaluate_run("missing", Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
