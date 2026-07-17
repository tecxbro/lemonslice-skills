#!/usr/bin/env python3
"""Materialize evaluation fixtures for an external behavioral agent runner."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "evals.json"


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    cases = payload.get("evals")
    if not isinstance(cases, list):
        raise ValueError("evals.json does not contain an evals list")
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    for case in load_cases():
        case_id = case["id"]
        source = ROOT / case["fixture"]
        destination = args.output / case_id
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        (destination / "_prompt.md").write_text(case["prompt"] + "\n", encoding="utf-8")
        (destination / "_runner-contract.json").write_text(
            json.dumps(
                {
                    "case_id": case_id,
                    "required_outputs": [
                        "_meta.json with selected_skill",
                        "_response.md or _meta.json.response",
                        "_command-results.json when commands are configured",
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        manifest.append({"id": case_id, "workspace": case_id})

    (args.output / "manifest.json").write_text(
        json.dumps({"cases": manifest}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Materialized {len(manifest)} behavioral evaluation workspaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
