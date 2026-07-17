#!/usr/bin/env python3
"""Validate eval fixtures and score materialized repository results.

A results directory contains one subdirectory per eval id. Each result is the
repository state after the evaluated agent ran. `_meta.json` must contain the
selected skill. Commands are executed only when both `--run-commands` and
`--sandboxed` are supplied; the runner never installs dependencies itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "evals.json"
IGNORED_PARTS = {".git", "node_modules", "__pycache__", ".next", "dist", "build"}
BLOCKED_COMMAND_PATTERNS = (
    r"\bnpm\s+(?:i|install|ci)\b",
    r"\bpnpm\s+(?:i|install)\b",
    r"\byarn\s+(?:add|install)\b",
    r"\bpip(?:3)?\s+install\b",
    r"\buv\s+add\b",
    r"\bcurl\b",
    r"\bwget\b",
)


def load() -> list[dict[str, Any]]:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 3:
        raise ValueError("Unsupported eval schema; expected schema_version 3")
    cases = payload.get("evals")
    if not isinstance(cases, list) or not cases:
        raise ValueError("evals must be a non-empty list")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("eval ids must be unique")
    return cases


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts) or path.name == "_meta.json"


def file_map(directory: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(directory)
        if is_ignored(rel):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files[rel.as_posix()] = digest
    return files


def changed_files(fixture: Path, result: Path) -> tuple[set[str], set[str], set[str]]:
    before, after = file_map(fixture), file_map(result)
    created = set(after) - set(before)
    deleted = set(before) - set(after)
    changed = {path for path in set(before) & set(after) if before[path] != after[path]}
    return created, changed, deleted


def parse_simple_yaml(text: str) -> Any:
    """Parse a conservative YAML subset: indentation mappings and scalar lists."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    def scalar(value: str) -> Any:
        value = value.strip()
        if not value:
            return {}
        if value in {"true", "false"}:
            return value == "true"
        if value in {"null", "~"}:
            return None
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("unsupported YAML list placement")
            parent.append(scalar(line[2:]))
            continue
        if ":" not in line or not isinstance(parent, dict):
            raise ValueError("unsupported YAML syntax")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        value = scalar(raw_value)
        parent[key] = value
        if value == {}:
            stack.append((indent, value))
    return root


def get_path(value: Any, dotted_path: str) -> tuple[bool, Any]:
    current = value
    if dotted_path == "":
        return True, current
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def check_structure(
    case_id: str,
    rel: str,
    text: str,
    structure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    fmt = structure.get("format")
    try:
        if fmt == "json":
            parsed = json.loads(text)
        elif fmt == "yaml":
            try:
                import yaml  # type: ignore
            except ImportError:
                parsed = parse_simple_yaml(text)
            else:
                parsed = yaml.safe_load(text)
        else:
            return [f"{case_id}: {rel}: unsupported structure format {fmt!r}"]
    except Exception as exc:
        return [f"{case_id}: {rel}: could not parse {fmt}: {exc}"]

    for assertion in structure.get("assertions", []):
        path = assertion.get("path", "")
        exists, actual = get_path(parsed, path)
        if assertion.get("exists") is True and not exists:
            errors.append(f"{case_id}: {rel}: structure path missing: {path}")
            continue
        if assertion.get("exists") is False and exists:
            errors.append(f"{case_id}: {rel}: structure path should be absent: {path}")
            continue
        if "equals" in assertion and (not exists or actual != assertion["equals"]):
            errors.append(
                f"{case_id}: {rel}: {path} expected {assertion['equals']!r}, got {actual!r}"
            )
        if "type" in assertion and exists:
            expected_type = assertion["type"]
            type_map = {
                "object": dict,
                "array": list,
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "null": type(None),
            }
            py_type = type_map.get(expected_type)
            if py_type is None or not isinstance(actual, py_type):
                errors.append(
                    f"{case_id}: {rel}: {path} expected type {expected_type}, "
                    f"got {type(actual).__name__}"
                )
    return errors


def validate(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    required = {
        "id",
        "prompt",
        "fixture",
        "expected_skill",
        "expected_changed_files",
        "forbidden_changed_files",
        "file_assertions",
    }
    for case in cases:
        case_id = case.get("id", "<unknown>")
        missing = sorted(required - set(case))
        if missing:
            errors.append(f"{case_id}: missing keys {missing}")
            continue
        fixture = ROOT / case["fixture"]
        if not fixture.is_dir():
            errors.append(f"{case_id}: fixture missing: {fixture}")
        elif not file_map(fixture):
            errors.append(f"{case_id}: fixture has no files")
        for key in ("expected_changed_files", "forbidden_changed_files", "commands"):
            if key in case and not isinstance(case[key], list):
                errors.append(f"{case_id}: {key} must be a list")
        assertions = case["file_assertions"]
        if not isinstance(assertions, dict):
            errors.append(f"{case_id}: file_assertions must be an object")
            continue
        for rel, rules in assertions.items():
            if not isinstance(rules, dict):
                errors.append(f"{case_id}: file assertion for {rel} must be an object")
                continue
            for key in ("must_contain", "must_not_contain", "must_match", "must_not_match"):
                if key in rules and not isinstance(rules[key], list):
                    errors.append(f"{case_id}: {rel}.{key} must be a list")
            for pattern in rules.get("must_match", []) + rules.get("must_not_match", []):
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(f"{case_id}: invalid regex {pattern!r}: {exc}")
        for command in case.get("commands", []):
            if not isinstance(command, str) or not command.strip():
                errors.append(f"{case_id}: commands must contain non-empty strings")
            elif any(re.search(pattern, command) for pattern in BLOCKED_COMMAND_PATTERNS):
                errors.append(
                    f"{case_id}: command installs/downloads dependencies and is not allowed: {command}"
                )
    return errors


def check_file_assertions(case: dict[str, Any], result: Path) -> list[str]:
    errors: list[str] = []
    case_id = case["id"]
    for rel, rules in case["file_assertions"].items():
        path = result / rel
        expected_state = rules.get("state", "present")
        if expected_state == "deleted":
            if path.exists():
                errors.append(f"{case_id}: expected file to be deleted: {rel}")
            continue
        if not path.is_file():
            errors.append(f"{case_id}: asserted file missing: {rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{case_id}: asserted file is not UTF-8 text: {rel}")
            continue
        for needle in rules.get("must_contain", []):
            if needle not in text:
                errors.append(f"{case_id}: {rel}: required text missing: {needle!r}")
        for needle in rules.get("must_not_contain", []):
            if needle and needle in text:
                errors.append(f"{case_id}: {rel}: forbidden text present: {needle!r}")
        for pattern in rules.get("must_match", []):
            if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
                errors.append(f"{case_id}: {rel}: required regex did not match: {pattern!r}")
        for pattern in rules.get("must_not_match", []):
            if re.search(pattern, text, re.MULTILINE | re.DOTALL):
                errors.append(f"{case_id}: {rel}: forbidden regex matched: {pattern!r}")
        if "structure" in rules:
            errors.extend(check_structure(case_id, rel, text, rules["structure"]))
    return errors


def run_commands(case: dict[str, Any], result: Path, timeout: int) -> list[str]:
    errors: list[str] = []
    env = {**os.environ, "CI": "1"}
    for command in case.get("commands", []):
        completed = subprocess.run(
            command,
            cwd=result,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        if completed.returncode != 0:
            output = (completed.stdout + "\n" + completed.stderr).strip()[-2000:]
            errors.append(
                f"{case['id']}: command failed ({completed.returncode}): {command}\n{output}"
            )
    return errors


def score_case(
    case: dict[str, Any],
    result: Path,
    *,
    execute_commands: bool,
    command_timeout: int,
) -> list[str]:
    case_id = case["id"]
    fixture = ROOT / case["fixture"]
    if not result.is_dir():
        return [f"{case_id}: result directory missing"]

    errors: list[str] = []
    meta_path = result / "_meta.json"
    if not meta_path.is_file():
        errors.append(f"{case_id}: _meta.json missing; selected skill cannot be verified")
    else:
        try:
            selected = json.loads(meta_path.read_text(encoding="utf-8")).get("selected_skill")
        except Exception as exc:
            errors.append(f"{case_id}: invalid _meta.json: {exc}")
        else:
            if selected != case["expected_skill"]:
                errors.append(
                    f"{case_id}: expected skill {case['expected_skill']}, got {selected}"
                )

    created, changed, deleted = changed_files(fixture, result)
    actual = created | changed | deleted
    expected = set(case["expected_changed_files"])
    forbidden = set(case["forbidden_changed_files"])

    missing = expected - actual
    unrelated = actual - expected
    forbidden_hits = actual & forbidden
    if missing:
        errors.append(f"{case_id}: expected changes missing: {sorted(missing)}")
    if unrelated and not case.get("allow_unlisted_changes", False):
        errors.append(f"{case_id}: unrelated files changed: {sorted(unrelated)}")
    if forbidden_hits:
        errors.append(f"{case_id}: forbidden files changed: {sorted(forbidden_hits)}")

    errors.extend(check_file_assertions(case, result))
    if execute_commands:
        errors.extend(run_commands(case, result, command_timeout))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--run-commands", action="store_true")
    parser.add_argument(
        "--sandboxed",
        action="store_true",
        help="Confirm result commands run inside an explicitly sandboxed environment.",
    )
    parser.add_argument("--command-timeout", type=int, default=120)
    args = parser.parse_args()

    if args.run_commands and not args.sandboxed:
        print("Configuration error: --run-commands requires --sandboxed", file=sys.stderr)
        return 2

    try:
        cases = load()
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    errors = validate(cases)
    if args.results_dir:
        for case in cases:
            errors.extend(
                score_case(
                    case,
                    args.results_dir / case["id"],
                    execute_commands=args.run_commands,
                    command_timeout=args.command_timeout,
                )
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"\n{len(errors)} failure(s).")
        return 1

    mode = "fixtures and results" if args.results_dir else "eval schema and fixtures"
    print(f"PASS: validated {mode} for {len(cases)} cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
