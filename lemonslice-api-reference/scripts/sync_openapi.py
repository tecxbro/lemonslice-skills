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
SNAPSHOT_NOTES = [
    "Raw REST and framework plugin contracts are tracked separately.",
    "The current raw SessionInput uses exactly one of agent_id or agent_image_url.",
    "Model and aspect-ratio fields must not be inferred from framework plugin documentation.",
    "The control operation declares security: [] while also documenting a 401 response; preserve this as a documentation conflict.",
]


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
                time.sleep(2**attempt)
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
    if not isinstance(current, dict):
        return current
    siblings = {key: item for key, item in value.items() if key != "$ref"}
    return {**current, **siblings}


def _empty_summary() -> dict[str, Any]:
    return {
        "required": [],
        "forbidden": [],
        "enums": {},
        "constants": {},
        "dependent_required": {},
        "one_of": [],
        "any_of": [],
    }


def _merge_enums(target: dict[str, list[Any]], incoming: dict[str, list[Any]]) -> None:
    for name, values in incoming.items():
        target[name] = sorted(set(target.get(name, [])) | set(values), key=str)


def _merge_summary(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    target["required"] = sorted(set(target["required"]) | set(incoming.get("required", [])))
    target["forbidden"] = sorted(set(target["forbidden"]) | set(incoming.get("forbidden", [])))
    _merge_enums(target["enums"], incoming.get("enums", {}))
    target["constants"].update(incoming.get("constants", {}))
    for name, dependencies in incoming.get("dependent_required", {}).items():
        target["dependent_required"][name] = sorted(
            set(target["dependent_required"].get(name, [])) | set(dependencies)
        )
    target["one_of"].extend(incoming.get("one_of", []))
    target["any_of"].extend(incoming.get("any_of", []))
    if "discriminator" in incoming:
        target["discriminator"] = incoming["discriminator"]


def _variant_title(schema: dict[str, Any], summary: dict[str, Any]) -> str | None:
    title = schema.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    required = set(summary.get("required", []))
    for selector in ("agent_image_url", "agent_id"):
        if selector in required:
            return f"By {selector}"
    return None


def _clean_summary(summary: dict[str, Any], *, variant_schema: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if variant_schema is not None:
        title = _variant_title(variant_schema, summary)
        if title:
            result["title"] = title
    for name, value in sorted(summary.get("constants", {}).items()):
        result[name] = value
    for key in ("required", "forbidden"):
        values = summary.get(key, [])
        if values:
            result[key] = sorted(values)
    enums = summary.get("enums", {})
    if enums:
        result["enums"] = dict(sorted(enums.items()))
    dependent = summary.get("dependent_required", {})
    if dependent:
        result["dependent_required"] = {
            name: sorted(values) for name, values in sorted(dependent.items())
        }
    for key in ("one_of", "any_of"):
        variants = summary.get(key, [])
        if variants:
            result[key] = variants
    if "discriminator" in summary:
        result["discriminator"] = summary["discriminator"]
    return result


def walk_schema(
    spec: dict[str, Any],
    schema: Any,
    seen: set[str] | None = None,
) -> dict[str, Any]:
    """Return a stable schema summary without flattening alternatives."""
    seen = seen or set()
    if not isinstance(schema, dict):
        return {}
    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen:
            return {}
        seen.add(ref)
        schema = resolve_ref(spec, schema)
        if not isinstance(schema, dict):
            return {}

    summary = _empty_summary()
    summary["required"] = sorted(
        value for value in schema.get("required", []) if isinstance(value, str)
    )

    not_schema = resolve_ref(spec, schema.get("not", {}))
    if isinstance(not_schema, dict):
        summary["forbidden"] = sorted(
            value for value in not_schema.get("required", []) if isinstance(value, str)
        )

    dependent = schema.get("dependentRequired", {})
    if isinstance(dependent, dict):
        for name, values in dependent.items():
            if isinstance(name, str) and isinstance(values, list):
                summary["dependent_required"][name] = sorted(
                    value for value in values if isinstance(value, str)
                )

    discriminator = schema.get("discriminator")
    if isinstance(discriminator, dict):
        normalized: dict[str, Any] = {}
        property_name = discriminator.get("propertyName")
        if isinstance(property_name, str):
            normalized["property_name"] = property_name
        mapping = discriminator.get("mapping")
        if isinstance(mapping, dict):
            normalized["mapping"] = dict(sorted(mapping.items()))
        if normalized:
            summary["discriminator"] = normalized

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for name, raw in properties.items():
            prop = resolve_ref(spec, raw)
            if not isinstance(name, str) or not isinstance(prop, dict):
                continue
            if isinstance(prop.get("enum"), list):
                summary["enums"][name] = sorted(prop["enum"], key=str)
            if "const" in prop:
                summary["constants"][name] = prop["const"]
            nested = walk_schema(spec, prop, set(seen))
            for nested_name, values in nested.get("enums", {}).items():
                summary["enums"][f"{name}.{nested_name}"] = values

    all_of = schema.get("allOf", [])
    if isinstance(all_of, list):
        for member in all_of:
            _merge_summary(summary, walk_schema(spec, member, set(seen)))

    for source_key, output_key in (("oneOf", "one_of"), ("anyOf", "any_of")):
        variants = schema.get(source_key, [])
        if not isinstance(variants, list):
            continue
        for raw_variant in variants:
            resolved = resolve_ref(spec, raw_variant)
            variant_schema = resolved if isinstance(resolved, dict) else {}
            variant_summary = walk_schema(spec, variant_schema, set(seen))
            summary[output_key].append(
                _clean_summary(variant_summary, variant_schema=variant_schema)
            )

    return _clean_summary(summary)


def request_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    request_body = resolve_ref(spec, operation.get("requestBody", {}))
    content = request_body.get("content", {}) if isinstance(request_body, dict) else {}
    if not isinstance(content, dict) or not content:
        return {"content_types": [], "media_types": {}}

    media_types: dict[str, Any] = {}
    for content_type, media in sorted(content.items()):
        media = resolve_ref(spec, media)
        schema = media.get("schema", {}) if isinstance(media, dict) else {}
        media_types[content_type] = walk_schema(spec, schema)

    result: dict[str, Any] = {
        "content_types": sorted(media_types),
        "media_types": media_types,
    }
    json_summary = media_types.get("application/json")
    if isinstance(json_summary, dict):
        result.update(json_summary)
    return result


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
    normalized_paths: list[str] = []
    if not isinstance(paths, dict):
        paths = {}
    for path, raw_path_item in sorted(paths.items()):
        normalized_paths.append(path)
        path_item = resolve_ref(spec, raw_path_item)
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            operation = resolve_ref(spec, path_item.get(method))
            if not isinstance(operation, dict):
                continue
            security = operation.get(
                "security",
                path_item.get("security", spec.get("security")),
            )
            operations[f"{method.upper()} {path}"] = {
                "security": normalize_security(spec, security),
                "request": request_schema(spec, operation),
                "responses": sorted(str(code) for code in operation.get("responses", {}).keys()),
            }
    return {"paths": normalized_paths, "operations": operations}


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

    expected_operations = snapshot.get("operations", {})
    current_operations = current.get("operations", {})
    for name in sorted(set(current_operations) - set(expected_operations)):
        errors.append(f"OpenAPI operation added: {name}")
    for name in sorted(set(expected_operations) - set(current_operations)):
        errors.append(f"Missing operation: {name}")

    for name in sorted(set(expected_operations) & set(current_operations)):
        expected = expected_operations[name]
        actual = current_operations[name]
        if expected.get("security") != actual.get("security"):
            errors.append(
                f"{name} security changed: expected {expected.get('security')}, "
                f"found {actual.get('security')}"
            )
        if expected.get("request") != actual.get("request"):
            errors.append(
                f"{name} request contract changed: expected "
                f"{json.dumps(expected.get('request'), sort_keys=True)}, found "
                f"{json.dumps(actual.get('request'), sort_keys=True)}"
            )
        if expected.get("responses", []) != actual.get("responses", []):
            errors.append(
                f"{name} response codes changed: expected {expected.get('responses', [])}, "
                f"found {actual.get('responses', [])}"
            )
    return errors


DOC_URL_RE = re.compile(r"https://lemonslice\.com/docs/[A-Za-z0-9_./-]+")


def normalize_doc_url(url: str) -> str:
    return url.rstrip(").,`'\"")


def check_skill_links(llms_text: str) -> list[str]:
    errors: list[str] = []
    indexed = {normalize_doc_url(match.group(0)) for match in DOC_URL_RE.finditer(llms_text)}
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
        openapi_bytes = args.openapi_file.read_bytes() if args.openapi_file else fetch(args.openapi_url)
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
            "notes": SNAPSHOT_NOTES,
            **current,
        }
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
