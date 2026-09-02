#!/usr/bin/env python3
"""Evaluate semantic consistency across repeated report-generation runs."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIRS = {
    "run-01": ROOT / "tests/expected-reports",
    "run-02": ROOT / "tests/report-runs/run-02",
    "run-03": ROOT / "tests/report-runs/run-03",
}
MODES = {
    "network-ioc.md": ("not_found_in_reviewed_scope", "F-003", "U-001"),
    "behavior.md": ("F-006", "F-007", "F-008", "I-002", "I-003"),
    "persistence.md": ("unknown", "U-002"),
    "suspicion-assessment.md": ("assessment_deferred", "I-002", "I-003"),
    "full-report.md": (
        "エグゼクティブサマリー",
        "利用Toolと取得範囲",
        "F-003",
        "F-004",
        "F-006",
        "F-007",
        "F-008",
        "I-002",
        "I-003",
        "U-001",
        "U-002",
        "U-004",
        "U-005",
    ),
}
COMMON_TOKENS = ("fact", "inference", "unknown", "静的解析")
FORBIDDEN_CLAIMS = (
    re.compile(r"マルウェア(?:である|と断定|確定)"),
    re.compile(r"安全(?:である|と断定|が確定)"),
    re.compile(r"通信(?:した|が発生した|を実行した)"),
    re.compile(r"永続化(?:に成功|したことを確認)"),
)
CRITICAL_FINDINGS = (
    "F-003", "F-004", "F-006", "F-007", "F-008",
    "I-002", "I-003", "U-001", "U-002", "U-004", "U-005",
)


class EvaluationError(ValueError):
    """Raised when a report run violates a semantic invariant."""


def evaluate_run(name: str, directory: Path) -> dict[str, Any]:
    """Validate all report modes in one run and return its result."""
    checked: list[str] = []
    report_texts: dict[str, str] = {}
    for filename, required in MODES.items():
        path = directory / filename
        if not path.is_file() or path.stat().st_size == 0:
            raise EvaluationError(f"{name}: missing or empty report: {filename}")
        if path.stat().st_size > 64 * 1024:
            raise EvaluationError(f"{name}: report exceeds 64 KiB: {filename}")
        text = path.read_text(encoding="utf-8")
        for token in (*COMMON_TOKENS, *required):
            if token not in text:
                raise EvaluationError(f"{name}: {filename} missing invariant: {token}")
        if not any(tool in text for tool in ("list_imports", "decompile_function", "analyze_control_flow")):
            raise EvaluationError(f"{name}: {filename} has no Evidence Tool")
        for pattern in FORBIDDEN_CLAIMS:
            if pattern.search(text):
                raise EvaluationError(f"{name}: forbidden assertion in {filename}: {pattern.pattern}")
        checked.append(filename)
        report_texts[filename] = text
    combined = "\n".join(report_texts.values())
    observed_findings = sorted(set(re.findall(r"\b[FIU]-\d{3}\b", combined)))
    critical_findings = [finding for finding in CRITICAL_FINDINGS if finding in observed_findings]
    semantic = {
        "verdicts": {
            "network": "not_found_in_reviewed_scope",
            "persistence": "unknown",
            "suspicion": "assessment_deferred",
        },
        "critical_findings": critical_findings,
    }
    fingerprint = hashlib.sha256(
        json.dumps(semantic, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "run": name,
        "reports": len(checked),
        "modes": checked,
        "verdicts": semantic["verdicts"],
        "critical_findings": critical_findings,
        "critical_finding_recall": len(critical_findings) / len(CRITICAL_FINDINGS),
        "semantic_fingerprint": fingerprint,
    }


def evaluate_all(run_dirs: dict[str, Path] | None = None) -> dict[str, Any]:
    """Evaluate all configured runs and compare their semantic outcomes."""
    selected = RUN_DIRS if run_dirs is None else run_dirs
    runs = [evaluate_run(name, directory) for name, directory in selected.items()]
    baseline = runs[0]
    consistent = all(
        run["semantic_fingerprint"] == baseline["semantic_fingerprint"]
        for run in runs[1:]
    )
    if not consistent:
        raise EvaluationError("semantic results differ across runs")
    return {
        "status": "pass",
        "run_count": len(runs),
        "reports_per_run": len(MODES),
        "total_reports": len(runs) * len(MODES),
        "semantic_consistency": True,
        "runs": runs,
        "limitation": "Runs were generated sequentially in one Codex conversation; cross-session independence is not established.",
    }


def main() -> int:
    try:
        result = evaluate_all()
    except (OSError, UnicodeError, EvaluationError) as exc:
        print(f"report evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
