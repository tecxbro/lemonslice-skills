#!/usr/bin/env python3
"""Pretty-print generated and evaluation JSON files deterministically."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = (
    ROOT / "maintainers" / "evals" / "evals.json",
    ROOT
    / "lemonslice-api-reference"
    / "references"
    / "openapi.snapshot.json",
    ROOT
    / "maintainers"
    / "openapi"
    / "tests"
    / "fixtures"
    / "normalizer_cases.json",
    ROOT
    / "maintainers"
    / "openapi"
    / "tests"
    / "fixtures"
    / "lemonslice-openapi.sanitized.json",
)


def formatted(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed: list[Path] = []
    for path in TARGETS:
        if not path.is_file():
            print(f"Missing JSON target: {path.relative_to(ROOT)}", file=sys.stderr)
            return 2
        expected = formatted(path)
        current = path.read_text(encoding="utf-8")
        if current != expected:
            changed.append(path)
            if not args.check:
                path.write_text(expected, encoding="utf-8")

    if args.check and changed:
        for path in changed:
            print(f"Needs formatting: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if changed:
        print(f"Formatted {len(changed)} JSON file(s).")
    else:
        print("Repository JSON data is already formatted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
