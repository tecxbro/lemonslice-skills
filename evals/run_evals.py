#!/usr/bin/env python3
"""Validate eval fixtures or score materialized agent results.

A results directory contains one subdirectory per eval id. Each subdirectory is
the repository state after the evaluated agent ran. An optional `_meta.json`
may include `{"selected_skill": "lemonslice-livekit"}`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "evals.json"


def load() -> list[dict[str, Any]]:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 2:
        raise ValueError("Unsupported eval schema")
    evals = payload.get("evals")
    if not isinstance(evals, list) or not evals:
        raise ValueError("evals must be a non-empty list")
    ids = [case.get("id") for case in evals]
    if len(ids) != len(set(ids)):
        raise ValueError("eval ids must be unique")
    return evals


def all_text(directory: Path) -> str:
    chunks: list[str] = []
    for path in directory.rglob("*"):
        if not path.is_file() or path.name == "_meta.json":
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return "\n".join(chunks)


def validate(evals: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    required = {
        "id", "prompt", "fixture", "expected_skill",
        "expected_files", "must_contain", "must_not_contain",
    }
    for case in evals:
        missing = sorted(required - set(case))
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: missing keys {missing}")
            continue
        fixture = ROOT / case["fixture"]
        if not fixture.is_dir():
            errors.append(f"{case['id']}: fixture missing: {fixture}")
        elif not any(path.is_file() for path in fixture.rglob("*")):
            errors.append(f"{case['id']}: fixture has no files")
        for key in ("expected_files", "must_contain", "must_not_contain"):
            if not isinstance(case[key], list):
                errors.append(f"{case['id']}: {key} must be a list")
    return errors


def score_case(case: dict[str, Any], result: Path) -> list[str]:
    errors: list[str] = []
    if not result.is_dir():
        return [f"{case['id']}: result directory missing"]

    meta_path = result / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        selected = meta.get("selected_skill")
        if selected != case["expected_skill"]:
            errors.append(
                f"{case['id']}: expected skill {case['expected_skill']}, got {selected}"
            )

    for rel in case["expected_files"]:
        if not (result / rel).is_file():
            errors.append(f"{case['id']}: expected file missing: {rel}")

    text = all_text(result)
    for needle in case["must_contain"]:
        if needle not in text:
            errors.append(f"{case['id']}: required text missing: {needle!r}")
    for needle in case["must_not_contain"]:
        if needle and needle in text:
            errors.append(f"{case['id']}: forbidden text present: {needle!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()

    try:
        evals = load()
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    errors = validate(evals)
    if args.results_dir:
        for case in evals:
            errors.extend(score_case(case, args.results_dir / case["id"]))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"\n{len(errors)} failure(s).")
        return 1

    mode = "fixtures and results" if args.results_dir else "eval schema and fixtures"
    print(f"PASS: validated {mode} for {len(evals)} cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
