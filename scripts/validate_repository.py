#!/usr/bin/env python3
"""Validate skill structure, MCP contracts, Evidence, and expected reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAX_EVIDENCE_BYTES = 64 * 1024
MAX_OBSERVATIONS = 100
NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PRIVATE_IPV4_RE = re.compile(
    r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
    r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
)
USER_PATH_RE = re.compile(r"(?:/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[^\\\s]+)")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
FORBIDDEN_ALLOWED_TOOL_RE = re.compile(
    r"^(?:set_|rename_|create_|delete_|apply_|save_|open_|close_|import_|"
    r"export_|load_|restore_|archive_|checkin_|run_|reanalyze$|debugger_|"
    r"emulate_|oracle_|server_|tool_)"
)
EXPLICITLY_BLOCKED = {
    "list_functions",
    "disassemble_function",
    "disassemble_bytes",
    "read_memory",
    "inspect_memory_content",
    "get_function_pcode",
    "get_language_metadata",
    "extract_iocs_with_context",
    "search_byte_patterns",
    "list_instances",
    "connect_instance",
    "list_tool_groups",
    "load_tool_group",
    "unload_tool_group",
    "search_tools",
    "check_tools",
}
FORBIDDEN_EVIDENCE_KEYS = {
    "program_name",
    "executable_path",
    "base_address",
    "address",
    "local_path",
    "tenant_id",
    "api_key",
    "token",
}


class ValidationError(ValueError):
    """Raised when a validation invariant is violated."""


def load_json(path: Path, *, max_bytes: int | None = None) -> Any:
    """Load UTF-8 JSON with an optional input-size limit."""
    if not path.is_file():
        raise ValidationError(f"file not found: {path}")
    size = path.stat().st_size
    if size == 0:
        raise ValidationError(f"empty file: {path}")
    if max_bytes is not None and size > max_bytes:
        raise ValidationError(f"file exceeds {max_bytes} bytes: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValidationError(f"file is not valid UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed JSON at line {exc.lineno}: {path}") from exc


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def validate_evidence(path: Path) -> None:
    """Validate the bounded Evidence interchange fixture."""
    data = _require_mapping(load_json(path, max_bytes=MAX_EVIDENCE_BYTES), "evidence")
    required = {"schema_version", "subject", "metadata", "acquisition", "observations", "limits"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValidationError(f"missing evidence fields: {', '.join(missing)}")
    subject = _require_mapping(data["subject"], "subject")
    for key in ("id", "kind", "provenance", "identifiers_redacted"):
        if key not in subject:
            raise ValidationError(f"subject.{key} is required")
    if subject["identifiers_redacted"] is not True:
        raise ValidationError("subject.identifiers_redacted must be true")
    def check_sensitive_keys(value: Any, location: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in FORBIDDEN_EVIDENCE_KEYS:
                    raise ValidationError(f"sensitive evidence key is forbidden: {location}.{key}")
                check_sensitive_keys(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_sensitive_keys(child, f"{location}[{index}]")
    check_sensitive_keys(data, "evidence")
    observations = data["observations"]
    if not isinstance(observations, list):
        raise ValidationError("observations must be an array")
    if len(observations) > MAX_OBSERVATIONS:
        raise ValidationError(f"observations exceed {MAX_OBSERVATIONS}")
    allowed_tools = contract_tool_names()
    seen: set[str] = set()
    for index, item in enumerate(observations):
        obs = _require_mapping(item, f"observations[{index}]")
        for key in ("id", "classification", "category", "summary", "evidence", "source"):
            if key not in obs:
                raise ValidationError(f"observations[{index}].{key} is required")
        if obs["id"] in seen:
            raise ValidationError(f"duplicate observation id: {obs['id']}")
        seen.add(obs["id"])
        if obs["classification"] not in {"fact", "inference", "unknown"}:
            raise ValidationError(f"invalid classification: {obs['classification']}")
        if not isinstance(obs["summary"], str) or not obs["summary"].strip():
            raise ValidationError(f"empty summary: {obs['id']}")
        source = _require_mapping(obs["source"], f"{obs['id']}.source")
        for key in ("tool", "target", "scope"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise ValidationError(f"{obs['id']}.source.{key} is required")
        if source["tool"] not in allowed_tools:
            raise ValidationError(f"disallowed source tool: {source['tool']}")


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse the simple scalar frontmatter used by repository skills."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"missing YAML frontmatter: {path}")
    try:
        block = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValidationError(f"unterminated YAML frontmatter: {path}") from exc
    values: dict[str, str] = {}
    for line in block.splitlines():
        match = re.fullmatch(r"([a-z_]+):\s*(?:\"([^\"]*)\"|'([^']*)'|([^#]+?))\s*", line)
        if match:
            values[match.group(1)] = next(value for value in match.groups()[1:] if value is not None).strip()
    return values


def validate_skills() -> list[str]:
    """Validate skill names, metadata, references, and safety boundaries."""
    checked: list[str] = []
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        entry = skill_dir / "SKILL.md"
        if not entry.is_file():
            raise ValidationError(f"missing SKILL.md: {skill_dir}")
        metadata = parse_frontmatter(entry)
        name = metadata.get("name", "")
        if not NAME_RE.fullmatch(name) or name != skill_dir.name:
            raise ValidationError(f"invalid or mismatched skill name: {skill_dir}")
        if not metadata.get("description"):
            raise ValidationError(f"missing skill description: {skill_dir}")
        agent_yaml = skill_dir / "agents" / "openai.yaml"
        agent_text = agent_yaml.read_text(encoding="utf-8")
        if f"${name}" not in agent_text:
            raise ValidationError(f"default_prompt does not mention ${name}: {agent_yaml}")
        checked.append(name)

    for markdown in sorted(ROOT.rglob("*.md")):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            target = target.split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target):
                continue
            if not (markdown.parent / target).resolve().is_file():
                raise ValidationError(f"broken link in {markdown}: {target}")

    static_text = (ROOT / "skills/ghidra-static-analysis/SKILL.md").read_text(encoding="utf-8")
    report_text = (ROOT / "skills/malware-analysis-report/SKILL.md").read_text(encoding="utf-8")
    for phrase in ("検体を実行せず", "未信頼データ", "全Strings", "断定しない"):
        if phrase not in static_text:
            raise ValidationError(f"missing static-analysis safety boundary: {phrase}")
    for phrase in ("外部照会", "Toolを再実行しない", "断定しない"):
        if phrase not in report_text:
            raise ValidationError(f"missing report safety boundary: {phrase}")
    return checked


def validate_document_hygiene() -> int:
    """Reject internal addressing, user paths, and private-key material in public text."""
    paths = [ROOT / "README.md"]
    paths.extend((ROOT / "docs").rglob("*.md"))
    paths.extend((ROOT / "skills").rglob("*.md"))
    paths.extend((ROOT / "skills").rglob("*.yaml"))
    checked = 0
    for path in sorted(set(paths)):
        text = path.read_text(encoding="utf-8")
        for label, pattern in (
            ("RFC1918 address", PRIVATE_IPV4_RE),
            ("user-specific path", USER_PATH_RE),
            ("private key", PRIVATE_KEY_RE),
        ):
            if pattern.search(text):
                raise ValidationError(f"{label} found in public text: {path}")
        checked += 1
    return checked


def contract_tool_names() -> set[str]:
    contract = _require_mapping(
        load_json(ROOT / "tests/contracts/ghidramcp-allowed-tools.json"), "tool contract"
    )
    tools = contract.get("tools")
    if not isinstance(tools, list):
        raise ValidationError("contract.tools must be an array")
    return {tool["name"] for tool in tools}


def _contract_params(schema: str) -> dict[str, tuple[str, bool]]:
    """Extract simple name/type/required tuples from the runtime TypeScript schema."""
    if schema == "{ [key: string]: unknown; }":
        return {}
    fields: dict[str, tuple[str, bool]] = {}
    for name, optional, value_type in re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*)(\?)?:\s*(string|number|boolean)\s*;", schema
    ):
        fields[name] = (value_type, optional != "?")
    return fields


def validate_catalog() -> tuple[int, int, int, str]:
    """Compare the actual runtime snapshot against the independent allowlist contract."""
    catalog = _require_mapping(
        load_json(ROOT / "tests/fixtures/ghidramcp-tool-catalog.json"), "tool catalog"
    )
    contract = _require_mapping(
        load_json(ROOT / "tests/contracts/ghidramcp-allowed-tools.json"), "tool contract"
    )
    catalog_tools = catalog.get("tools")
    contract_tools = contract.get("tools")
    if not isinstance(catalog_tools, list) or not isinstance(contract_tools, list):
        raise ValidationError("catalog.tools and contract.tools must be arrays")
    if catalog.get("tool_count") != len(catalog_tools):
        raise ValidationError("catalog tool_count mismatch")
    by_name: dict[str, dict[str, Any]] = {}
    for tool in catalog_tools:
        item = _require_mapping(tool, "catalog tool")
        name = item.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValidationError(f"invalid or duplicate catalog tool: {name}")
        if item.get("policy") not in {"allowed", "blocked_unlisted"}:
            raise ValidationError(f"unclassified catalog tool: {name}")
        by_name[name] = item
    expected = {tool["name"]: tool for tool in contract_tools}
    allowed_snapshot = {name for name, tool in by_name.items() if tool["policy"] == "allowed"}
    if allowed_snapshot != set(expected):
        raise ValidationError("runtime allowed-tool classification differs from contract")
    for name, expected_tool in expected.items():
        actual = by_name.get(name)
        if actual is None:
            raise ValidationError(f"allowed tool missing from runtime catalog: {name}")
        if actual.get("input_schema_ts") != expected_tool.get("input_schema_ts"):
            raise ValidationError(f"input schema mismatch: {name}")
        if FORBIDDEN_ALLOWED_TOOL_RE.search(name) or name in EXPLICITLY_BLOCKED:
            raise ValidationError(f"forbidden tool allowed by contract: {name}")

    server_schema = _require_mapping(
        load_json(ROOT / "tests/fixtures/ghidramcp-server-schema.json"), "server schema"
    )
    server_tools = server_schema.get("tools")
    if not isinstance(server_tools, list) or server_schema.get("tool_count") != len(server_tools):
        raise ValidationError("server schema tool_count mismatch")
    server_by_name = {tool["name"]: tool for tool in server_tools}
    for name, expected_tool in expected.items():
        actual = server_by_name.get(name)
        if actual is None:
            raise ValidationError(f"allowed tool missing from live server schema: {name}")
        if actual.get("method") != "GET":
            raise ValidationError(f"allowed tool is not read-only GET: {name}")
        actual_params = {
            param["name"]: (
                "number" if param.get("type") in {"integer", "number"} else param.get("type"),
                bool(param.get("required")),
            )
            for param in actual.get("params", [])
        }
        expected_params = _contract_params(expected_tool["input_schema_ts"])
        if actual_params != expected_params:
            raise ValidationError(f"live server input schema mismatch: {name}")

    version = _require_mapping(
        load_json(ROOT / "tests/fixtures/ghidramcp-version.json"), "server version"
    )
    server_contract = _require_mapping(contract.get("server_contract"), "server contract")
    for key in ("plugin_name", "plugin_version"):
        if version.get(key) != server_contract.get(key):
            raise ValidationError(f"server {key} mismatch")
    return len(by_name), len(expected), len(server_by_name), str(version["plugin_version"])


def validate_reports() -> list[str]:
    """Check report-level safety and mode-specific completeness invariants."""
    report_dir = ROOT / "tests/expected-reports"
    requirements = {
        "network-ioc.md": ("not_found_in_reviewed_scope", "IOC候補"),
        "behavior.md": ("File／Directory操作", "Network／IPC"),
        "persistence.md": ("unknown", "永続化"),
        "suspicion-assessment.md": ("assessment_deferred", "調査Coverage"),
        "full-report.md": ("エグゼクティブサマリー", "利用Toolと取得範囲"),
    }
    checked: list[str] = []
    for filename, tokens in requirements.items():
        path = report_dir / filename
        if not path.is_file():
            raise ValidationError(f"missing expected report: {path}")
        text = path.read_text(encoding="utf-8")
        for token in (*tokens, "fact", "inference", "unknown", "静的解析"):
            if token not in text:
                raise ValidationError(f"expected report invariant missing ({token}): {path}")
        if "list_imports" not in text:
            raise ValidationError(f"report has no Evidence source Tool: {path}")
        checked.append(filename)
    return checked


def run_all() -> dict[str, Any]:
    """Run all repository checks and return a machine-readable summary."""
    skills = validate_skills()
    public_text_files = validate_document_hygiene()
    catalog_count, allowed_count, server_count, plugin_version = validate_catalog()
    validate_evidence(ROOT / "tests/fixtures/evidence/valid-safe-test-pe.json")
    reports = validate_reports()
    return {
        "status": "pass",
        "skills": skills,
        "public_text_files": public_text_files,
        "catalog_tools": catalog_count,
        "allowed_tools": allowed_count,
        "server_schema_tools": server_count,
        "plugin_version": plugin_version,
        "evidence_fixtures": 1,
        "expected_reports": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON result")
    args = parser.parse_args()
    try:
        result = run_all()
    except (OSError, ValidationError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "repository validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
