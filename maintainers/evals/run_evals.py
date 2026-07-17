#!/usr/bin/env python3
"""Validate eval definitions and score externally materialized agent results.

Static validation checks that fixtures and assertions are well formed. Behavioral
scoring requires one result directory per case with `_meta.json`, a user-facing
response (`_response.md` or `_meta.json.response`), and any command outcomes
produced by an externally isolated executor in `_command-results.json`.

This scorer never executes code from an agent-modified project.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "evals.json"
IGNORED_NAMES = {
    "_meta.json",
    "_response.md",
    "_command-results.json",
    "_prompt.md",
    "_runner-contract.json",
}
IGNORED_PARTS = {".git", "node_modules", "__pycache__", ".next", "dist", "build"}
BLOCKED_COMMAND_PATTERNS = (
    r"\bnpm\s+(?:i|install|ci)\b",
    r"\bpnpm\s+(?:i|install)\b",
    r"\byarn\s+(?:add|install)\b",
    r"\bpip(?:3)?\s+install\b",
    r"\buv\s+add\b",
)
RESPONSE_REGEX_KEYS = ("must_match", "must_not_match")
TEXT_LIST_KEYS = ("must_contain", "must_not_contain", *RESPONSE_REGEX_KEYS)


def load() -> list[dict[str, Any]]:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 4:
        raise ValueError("Unsupported eval schema; expected schema_version 4")
    cases = payload.get("evals")
    if not isinstance(cases, list) or not cases:
        raise ValueError("evals must be a non-empty list")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("eval ids must be unique")
    return cases


def is_ignored(path: Path) -> bool:
    return (
        any(part in IGNORED_PARTS for part in path.parts)
        or path.name in IGNORED_NAMES
    )


def file_map(directory: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(directory)
        if is_ignored(rel):
            continue
        files[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def changed_files(fixture: Path, result: Path) -> tuple[set[str], set[str], set[str]]:
    before, after = file_map(fixture), file_map(result)
    created = set(after) - set(before)
    deleted = set(before) - set(after)
    changed = {path for path in set(before) & set(after) if before[path] != after[path]}
    return created, changed, deleted


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


def check_json_structure(
    case_id: str,
    rel: str,
    text: str,
    structure: dict[str, Any],
) -> list[str]:
    if structure.get("format") != "json":
        return [
            f"{case_id}: {rel}: only JSON structural assertions are supported; "
            "use a maintained external YAML parser before enabling YAML assertions"
        ]
    try:
        parsed = json.loads(text)
    except Exception as exc:
        return [f"{case_id}: {rel}: could not parse JSON: {exc}"]

    errors: list[str] = []
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
            type_map: dict[str, Any] = {
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


def validate_text_rules(case_id: str, scope: str, rules: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in TEXT_LIST_KEYS:
        if key in rules and not isinstance(rules[key], list):
            errors.append(f"{case_id}: {scope}.{key} must be a list")
    for pattern in rules.get("must_match", []) + rules.get("must_not_match", []):
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"{case_id}: invalid regex {pattern!r}: {exc}")
    if "max_length" in rules and (
        not isinstance(rules["max_length"], int) or rules["max_length"] < 1
    ):
        errors.append(f"{case_id}: {scope}.max_length must be a positive integer")
    if "required_sections" in rules and not isinstance(rules["required_sections"], list):
        errors.append(f"{case_id}: {scope}.required_sections must be a list")
    for key in ("required_uncertainty_language", "required_conflict_language"):
        if key in rules and not isinstance(rules[key], bool):
            errors.append(f"{case_id}: {scope}.{key} must be boolean")
    return errors


def validate(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    required = {
        "id",
        "prompt",
        "fixture",
        "expected_skill",
        "required_changed_files",
        "allowed_changed_files",
        "forbidden_changed_files",
        "file_assertions",
        "response_assertions",
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

        for key in (
            "required_changed_files",
            "allowed_changed_files",
            "forbidden_changed_files",
            "commands",
        ):
            if key in case and not isinstance(case[key], list):
                errors.append(f"{case_id}: {key} must be a list")

        one_of = case.get("one_of_changed_files", [])
        if not isinstance(one_of, list) or any(
            not isinstance(group, list) or not group for group in one_of
        ):
            errors.append(
                f"{case_id}: one_of_changed_files must be a list of non-empty file-pattern lists"
            )

        assertions = case["file_assertions"]
        if not isinstance(assertions, dict):
            errors.append(f"{case_id}: file_assertions must be an object")
        else:
            for rel, rules in assertions.items():
                if not isinstance(rules, dict):
                    errors.append(f"{case_id}: file assertion for {rel} must be an object")
                    continue
                errors.extend(validate_text_rules(case_id, rel, rules))
                if "structure" in rules:
                    structure = rules["structure"]
                    if not isinstance(structure, dict) or structure.get("format") != "json":
                        errors.append(
                            f"{case_id}: {rel}.structure must use format='json'"
                        )

        response_rules = case["response_assertions"]
        if not isinstance(response_rules, dict):
            errors.append(f"{case_id}: response_assertions must be an object")
        else:
            errors.extend(validate_text_rules(case_id, "response_assertions", response_rules))

        for command in case.get("commands", []):
            if not isinstance(command, str) or not command.strip():
                errors.append(f"{case_id}: commands must contain non-empty strings")
            elif any(re.search(pattern, command) for pattern in BLOCKED_COMMAND_PATTERNS):
                errors.append(
                    f"{case_id}: install commands do not belong in scoring definitions: {command}"
                )
    return errors


def check_text_assertions(
    case_id: str,
    scope: str,
    text: str,
    rules: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for needle in rules.get("must_contain", []):
        if needle not in text:
            errors.append(f"{case_id}: {scope}: required text missing: {needle!r}")
    for needle in rules.get("must_not_contain", []):
        if needle and needle in text:
            errors.append(f"{case_id}: {scope}: forbidden text present: {needle!r}")
    for pattern in rules.get("must_match", []):
        if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
            errors.append(f"{case_id}: {scope}: required regex did not match: {pattern!r}")
    for pattern in rules.get("must_not_match", []):
        if re.search(pattern, text, re.MULTILINE | re.DOTALL):
            errors.append(f"{case_id}: {scope}: forbidden regex matched: {pattern!r}")
    if "max_length" in rules and len(text) > rules["max_length"]:
        errors.append(
            f"{case_id}: {scope}: response length {len(text)} exceeds {rules['max_length']}"
        )
    for section in rules.get("required_sections", []):
        heading = re.compile(rf"^#+\s+{re.escape(section)}\s*$", re.IGNORECASE | re.MULTILINE)
        if not heading.search(text):
            errors.append(f"{case_id}: {scope}: required section missing: {section!r}")
    lowered = text.lower()
    if rules.get("required_uncertainty_language") and not any(
        term in lowered for term in ("uncertain", "verify", "current contract", "may differ")
    ):
        errors.append(f"{case_id}: {scope}: uncertainty/verification language missing")
    if rules.get("required_conflict_language") and not any(
        term in lowered for term in ("conflict", "inconsistent", "disagree", "different sources")
    ):
        errors.append(f"{case_id}: {scope}: documentation-conflict language missing")
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
        errors.extend(check_text_assertions(case_id, rel, text, rules))
        if "structure" in rules:
            errors.extend(check_json_structure(case_id, rel, text, rules["structure"]))
    return errors


def read_meta(result: Path) -> tuple[dict[str, Any] | None, str | None]:
    meta_path = result / "_meta.json"
    if not meta_path.is_file():
        return None, "_meta.json missing; selected skill cannot be verified"
    try:
        value = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"invalid _meta.json: {exc}"
    if not isinstance(value, dict):
        return None, "_meta.json must contain an object"
    return value, None


def read_response(result: Path, meta: dict[str, Any] | None) -> tuple[str | None, str | None]:
    response_path = result / "_response.md"
    if response_path.is_file():
        return response_path.read_text(encoding="utf-8"), None
    if meta and isinstance(meta.get("response"), str):
        return meta["response"], None
    return None, "user-facing response missing; provide _response.md or _meta.json.response"


def check_response_assertions(
    case: dict[str, Any], result: Path, meta: dict[str, Any] | None
) -> list[str]:
    response, error = read_response(result, meta)
    if error:
        return [f"{case['id']}: {error}"]
    assert response is not None
    return check_text_assertions(
        case["id"], "response", response, case["response_assertions"]
    )


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def check_changed_files(case: dict[str, Any], actual: set[str]) -> list[str]:
    case_id = case["id"]
    errors: list[str] = []
    required = case["required_changed_files"]
    allowed = list(dict.fromkeys(required + case["allowed_changed_files"]))
    forbidden = case["forbidden_changed_files"]
    one_of = case.get("one_of_changed_files", [])

    missing = [pattern for pattern in required if not matches_any_actual(actual, pattern)]
    if missing:
        errors.append(f"{case_id}: required changes missing: {missing}")

    if one_of and not any(
        all(matches_any_actual(actual, pattern) for pattern in group) for group in one_of
    ):
        errors.append(
            f"{case_id}: none of the one_of_changed_files alternatives were satisfied: {one_of}"
        )

    forbidden_hits = sorted(path for path in actual if matches(path, forbidden))
    if forbidden_hits:
        errors.append(f"{case_id}: forbidden files changed: {forbidden_hits}")

    one_of_patterns = [pattern for group in one_of for pattern in group]
    unrelated = sorted(
        path
        for path in actual
        if not matches(path, allowed + one_of_patterns)
    )
    if unrelated:
        errors.append(f"{case_id}: unrelated files changed: {unrelated}")
    return errors


def matches_any_actual(actual: set[str], pattern: str) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for path in actual)


def check_command_results(case: dict[str, Any], result: Path) -> list[str]:
    commands = case.get("commands", [])
    if not commands:
        return []
    path = result / "_command-results.json"
    if not path.is_file():
        return [
            f"{case['id']}: _command-results.json missing; command outcomes must come "
            "from an externally isolated executor"
        ]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{case['id']}: invalid _command-results.json: {exc}"]
    if not isinstance(payload, dict) or payload.get("isolated") is not True:
        return [f"{case['id']}: command results must declare isolated=true"]
    results = payload.get("results")
    if not isinstance(results, list):
        return [f"{case['id']}: command results must contain a results list"]
    by_command = {
        item.get("command"): item
        for item in results
        if isinstance(item, dict) and isinstance(item.get("command"), str)
    }
    errors: list[str] = []
    for command in commands:
        item = by_command.get(command)
        if item is None:
            errors.append(f"{case['id']}: command result missing: {command}")
            continue
        if item.get("returncode") != 0:
            output = f"{item.get('stdout', '')}\n{item.get('stderr', '')}".strip()[-2000:]
            errors.append(
                f"{case['id']}: externally isolated command failed "
                f"({item.get('returncode')}): {command}\n{output}"
            )
    return errors


def score_case(case: dict[str, Any], result: Path) -> list[str]:
    case_id = case["id"]
    fixture = ROOT / case["fixture"]
    if not result.is_dir():
        return [f"{case_id}: result directory missing"]

    errors: list[str] = []
    meta, meta_error = read_meta(result)
    if meta_error:
        errors.append(f"{case_id}: {meta_error}")
    elif meta and meta.get("selected_skill") != case["expected_skill"]:
        errors.append(
            f"{case_id}: expected skill {case['expected_skill']}, "
            f"got {meta.get('selected_skill')}"
        )

    created, changed, deleted = changed_files(fixture, result)
    actual = created | changed | deleted
    errors.extend(check_changed_files(case, actual))
    errors.extend(check_file_assertions(case, result))
    errors.extend(check_response_assertions(case, result, meta))
    errors.extend(check_command_results(case, result))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()

    try:
        cases = load()
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    errors = validate(cases)
    if args.results_dir:
        for case in cases:
            errors.extend(score_case(case, args.results_dir / case["id"]))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"\n{len(errors)} failure(s).")
        return 1

    mode = "definitions and behavioral results" if args.results_dir else "evaluation definitions"
    print(f"PASS: validated {mode} for {len(cases)} cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
