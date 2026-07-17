#!/usr/bin/env python3
"""Check LemonSlice OpenAPI and documentation index for contract drift.

Uses only the Python standard library. It never rewrites skill prose.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_OPENAPI_URL = "https://lemonslice.com/docs/openapi.json"
DEFAULT_LLMS_URL = "https://lemonslice.com/docs/llms.txt"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT = Path(__file__).resolve().parents[1] / "references" / "openapi.snapshot.json"


def fetch(url: str, attempts: int = 3, timeout: int = 30) -> bytes:
    last_error: Exception | None = None
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "lemonslice-skills-docs-drift/1.0"},
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Unable to fetch {url}: {last_error}")


def resolve_ref(spec: dict[str, Any], value: Any) -> Any:
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    ref = value["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return value
    current: Any = spec
    for part in ref[2:].split("/"):
        current = current[part.replace("~1", "/").replace("~0", "~")]
    return current


def walk_schema(spec: dict[str, Any], schema: Any, seen: set[str] | None = None) -> dict[str, Any]:
    """Return a stable summary of required properties and enums."""
    seen = seen or set()
    if not isinstance(schema, dict):
        return {"required": [], "enums": {}}
    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen:
            return {"required": [], "enums": {}}
        seen.add(ref)
        return walk_schema(spec, resolve_ref(spec, schema), seen)

    required = set(schema.get("required", []))
    enums: dict[str, list[Any]] = {}
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for name, raw in properties.items():
            prop = resolve_ref(spec, raw)
            if isinstance(prop, dict) and isinstance(prop.get("enum"), list):
                enums[name] = sorted(prop["enum"], key=str)
            nested = walk_schema(spec, prop, set(seen))
            for nested_name, values in nested["enums"].items():
                enums[f"{name}.{nested_name}"] = values

    for key in ("oneOf", "anyOf", "allOf"):
        variants = schema.get(key, [])
        if isinstance(variants, list):
            for variant in variants:
                summary = walk_schema(spec, variant, set(seen))
                required.update(summary["required"])
                for name, values in summary["enums"].items():
                    enums.setdefault(name, [])
                    enums[name] = sorted(set(enums[name]) | set(values), key=str)

    return {"required": sorted(required), "enums": dict(sorted(enums.items()))}


def request_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    content = operation.get("requestBody", {}).get("content", {})
    if not isinstance(content, dict):
        return {"required": [], "enums": {}}
    media = content.get("application/json") or next(iter(content.values()), {})
    return walk_schema(spec, media.get("schema", {}))


def normalize_security(spec: dict[str, Any], value: Any) -> list[str]:
    if value == []:
        return []
    names: set[str] = set()
    schemes = spec.get("components", {}).get("securitySchemes", {})
    if isinstance(value, list):
        for requirement in value:
            if not isinstance(requirement, dict):
                continue
            for name in requirement:
                scheme = schemes.get(name, {}) if isinstance(schemes, dict) else {}
                header_name = scheme.get("name") if isinstance(scheme, dict) else None
                names.add("X-API-Key" if header_name == "X-API-Key" else name)
    return sorted(names)


def normalize(spec: dict[str, Any]) -> dict[str, Any]:
    paths = spec.get("paths", {})
    operations: dict[str, Any] = {}
    for path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            operation = path_item.get(method)
            if not isinstance(operation, dict):
                continue
            security = operation.get("security", spec.get("security"))
            operations[f"{method.upper()} {path}"] = {
                "security": normalize_security(spec, security),
                "request": request_schema(spec, operation),
                "responses": sorted(str(code) for code in operation.get("responses", {}).keys()),
            }
    return {
        "paths": sorted(paths.keys()),
        "operations": operations,
    }


def compare(snapshot: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_paths = snapshot.get("paths", [])
    current_paths = current.get("paths", [])
    if expected_paths != current_paths:
        added = sorted(set(current_paths) - set(expected_paths))
        removed = sorted(set(expected_paths) - set(current_paths))
        if added:
            errors.append(f"OpenAPI paths added: {', '.join(added)}")
        if removed:
            errors.append(f"OpenAPI paths removed: {', '.join(removed)}")

    for name, expected in snapshot.get("operations", {}).items():
        actual = current.get("operations", {}).get(name)
        if actual is None:
            errors.append(f"Missing operation: {name}")
            continue

        if expected.get("security") != actual.get("security"):
            errors.append(
                f"{name} security changed: expected {expected.get('security')}, "
                f"found {actual.get('security')}"
            )

        expected_required = expected.get("request", {}).get("required", [])
        actual_required = actual.get("request", {}).get("required", [])
        if expected_required != actual_required:
            errors.append(
                f"{name} required fields changed: expected {expected_required}, "
                f"found {actual_required}"
            )

        expected_request = expected.get("request", {})
        if "enums" in expected_request:
            expected_enums = expected_request.get("enums", {})
            actual_enums = actual.get("request", {}).get("enums", {})
            if expected_enums != actual_enums:
                errors.append(
                    f"{name} enums changed: expected {expected_enums}, found {actual_enums}"
                )

        expected_responses = expected.get("responses", [])
        if expected_responses != actual.get("responses", []):
            errors.append(
                f"{name} response codes changed: expected {expected_responses}, "
                f"found {actual.get('responses', [])}"
            )
    return errors


DOC_URL_RE = re.compile(r"https://lemonslice\.com/docs/[A-Za-z0-9_./-]+")


def normalize_doc_url(url: str) -> str:
    return url.rstrip(").,`'\"")


def check_skill_links(llms_text: str) -> list[str]:
    errors: list[str] = []
    indexed = {
        normalize_doc_url(match.group(0))
        for match in DOC_URL_RE.finditer(llms_text)
    }
    exceptions = {
        "https://lemonslice.com/docs/llms.txt",
        "https://lemonslice.com/docs/openapi.json",
    }
    for skill in ROOT.glob("lemonslice-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        for raw in DOC_URL_RE.findall(text):
            url = normalize_doc_url(raw)
            if url in exceptions:
                continue
            alternatives = {
                url,
                url.replace(".md", ""),
                url.replace("/index.md", ""),
                url + ".md",
                url.rstrip("/") + "/index.md",
            }
            if not (alternatives & indexed):
                errors.append(f"{skill.relative_to(ROOT)} links to unindexed docs page: {url}")
    return errors


def write_report(path: Path, errors: list[str], current: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LemonSlice documentation drift report",
        "",
        f"Status: {'FAIL' if errors else 'PASS'}",
        "",
    ]
    if errors:
        lines += ["## Drift detected", ""] + [f"- {error}" for error in errors]
    else:
        lines += ["No tracked OpenAPI or documentation-index drift detected."]
    lines += [
        "",
        "## Current paths",
        "",
        *[f"- `{path_name}`" for path_name in current.get("paths", [])],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail on drift (default behavior)")
    parser.add_argument("--write-snapshot", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "docs-drift.md")
    parser.add_argument("--openapi-url", default=DEFAULT_OPENAPI_URL)
    parser.add_argument("--llms-url", default=DEFAULT_LLMS_URL)
    parser.add_argument("--openapi-file", type=Path)
    parser.add_argument("--llms-file", type=Path)
    args = parser.parse_args()

    try:
        openapi_bytes = (
            args.openapi_file.read_bytes()
            if args.openapi_file
            else fetch(args.openapi_url)
        )
        llms_text = (
            args.llms_file.read_text(encoding="utf-8")
            if args.llms_file
            else fetch(args.llms_url).decode("utf-8")
        )
        spec = json.loads(openapi_bytes)
    except Exception as exc:
        write_report(args.report, [f"Source retrieval/parsing failed: {exc}"], {"paths": []})
        print(exc, file=sys.stderr)
        return 2

    current = normalize(spec)
    if args.write_snapshot:
        payload = {
            "generated_from": args.openapi_url,
            "audited_at": time.strftime("%Y-%m-%d"),
            **current,
        }
        args.snapshot.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"Wrote {args.snapshot}")
        return 0

    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    errors = compare(snapshot, current)
    errors.extend(check_skill_links(llms_text))
    write_report(args.report, errors, current)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("No LemonSlice documentation drift detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
