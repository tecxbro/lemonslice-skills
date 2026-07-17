#!/usr/bin/env python3
"""Normalize LemonSlice OpenAPI contracts and report documentation drift."""
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
    "The current raw SessionInput uses exactly one of agent_id or agent_image_url for application/json requests.",
    "The current OpenAPI also declares multipart/form-data image upload and raw model/aspect_ratio fields; do not infer these fields when a future snapshot removes them.",
    "The control operation declares security: [] while also documenting a 401 response; preserve this as a documentation conflict.",
]


def fetch(url: str, attempts: int = 3, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "lemonslice-skills-drift/2"})
    last_error: Exception | None = None
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
    if isinstance(current, dict):
        return {**current, **{key: item for key, item in value.items() if key != "$ref"}}
    return current


def empty_summary() -> dict[str, Any]:
    return {
        "required": [], "forbidden": [], "enums": {}, "constants": {},
        "dependent_required": {}, "one_of": [], "any_of": [],
    }


def merge(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    for key in ("required", "forbidden"):
        target[key] = sorted(set(target[key]) | set(incoming.get(key, [])))
    for name, values in incoming.get("enums", {}).items():
        target["enums"][name] = sorted(set(target["enums"].get(name, [])) | set(values), key=str)
    target["constants"].update(incoming.get("constants", {}))
    for name, values in incoming.get("dependent_required", {}).items():
        target["dependent_required"][name] = sorted(
            set(target["dependent_required"].get(name, [])) | set(values)
        )
    target["one_of"].extend(incoming.get("one_of", []))
    target["any_of"].extend(incoming.get("any_of", []))
    if incoming.get("discriminator"):
        target["discriminator"] = incoming["discriminator"]


def clean(summary: dict[str, Any], schema: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if schema:
        title = schema.get("title")
        required = set(summary.get("required", []))
        if isinstance(title, str) and title.strip():
            result["title"] = title.strip()
        elif "agent_image_url" in required:
            result["title"] = "By agent_image_url"
        elif "agent_id" in required:
            result["title"] = "By agent_id"
    result.update(dict(sorted(summary.get("constants", {}).items())))
    for key in ("required", "forbidden"):
        if summary.get(key):
            result[key] = sorted(summary[key])
    if summary.get("enums"):
        result["enums"] = dict(sorted(summary["enums"].items()))
    if summary.get("dependent_required"):
        result["dependent_required"] = {
            name: sorted(values) for name, values in sorted(summary["dependent_required"].items())
        }
    for key in ("one_of", "any_of"):
        if summary.get(key):
            result[key] = summary[key]
    if summary.get("discriminator"):
        result["discriminator"] = summary["discriminator"]
    return result


def walk_raw(spec: dict[str, Any], schema: Any, seen: set[str] | None = None) -> dict[str, Any]:
    seen = seen or set()
    if not isinstance(schema, dict):
        return empty_summary()
    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen:
            return empty_summary()
        seen.add(ref)
        schema = resolve_ref(spec, schema)
        if not isinstance(schema, dict):
            return empty_summary()

    out = empty_summary()
    out["required"] = sorted(x for x in schema.get("required", []) if isinstance(x, str))
    negated = resolve_ref(spec, schema.get("not", {}))
    if isinstance(negated, dict):
        out["forbidden"] = sorted(x for x in negated.get("required", []) if isinstance(x, str))
    dependencies = schema.get("dependentRequired", {})
    if isinstance(dependencies, dict):
        out["dependent_required"] = {
            name: sorted(x for x in values if isinstance(x, str))
            for name, values in dependencies.items() if isinstance(name, str) and isinstance(values, list)
        }
    discriminator = schema.get("discriminator")
    if isinstance(discriminator, dict):
        normalized: dict[str, Any] = {}
        if isinstance(discriminator.get("propertyName"), str):
            normalized["property_name"] = discriminator["propertyName"]
        if isinstance(discriminator.get("mapping"), dict):
            normalized["mapping"] = dict(sorted(discriminator["mapping"].items()))
        if normalized:
            out["discriminator"] = normalized

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for name, raw in properties.items():
            prop = resolve_ref(spec, raw)
            if not isinstance(name, str) or not isinstance(prop, dict):
                continue
            if isinstance(prop.get("enum"), list):
                out["enums"][name] = sorted(prop["enum"], key=str)
            if "const" in prop:
                out["constants"][name] = prop["const"]
            nested = walk_raw(spec, prop, set(seen))
            for nested_name, values in nested["enums"].items():
                out["enums"][f"{name}.{nested_name}"] = values

    for member in schema.get("allOf", []) if isinstance(schema.get("allOf", []), list) else []:
        merge(out, walk_raw(spec, member, set(seen)))
    for source, destination in (("oneOf", "one_of"), ("anyOf", "any_of")):
        variants = schema.get(source, [])
        if isinstance(variants, list):
            for raw in variants:
                resolved = resolve_ref(spec, raw)
                variant_schema = resolved if isinstance(resolved, dict) else {}
                out[destination].append(clean(walk_raw(spec, variant_schema, set(seen)), variant_schema))
    return out


def walk_schema(spec: dict[str, Any], schema: Any, seen: set[str] | None = None) -> dict[str, Any]:
    """Preserve oneOf/anyOf alternatives; combine only allOf requirements."""
    return clean(walk_raw(spec, schema, seen))


def request_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    body = resolve_ref(spec, operation.get("requestBody", {}))
    content = body.get("content", {}) if isinstance(body, dict) else {}
    if not isinstance(content, dict):
        content = {}
    media_types = {
        content_type: walk_schema(
            spec,
            (resolve_ref(spec, media) or {}).get("schema", {})
            if isinstance(resolve_ref(spec, media), dict) else {},
        )
        for content_type, media in sorted(content.items())
    }
    result: dict[str, Any] = {
        "content_types": sorted(media_types),
        "media_types": media_types,
    }
    if "application/json" in media_types:
        result.update(media_types["application/json"])
    return result


def normalize_security(spec: dict[str, Any], value: Any) -> list[str]:
    if value == []:
        return []
    names: set[str] = set()
    schemes = spec.get("components", {}).get("securitySchemes", {})
    for requirement in value if isinstance(value, list) else []:
        if not isinstance(requirement, dict):
            continue
        for name in requirement:
            scheme = schemes.get(name, {}) if isinstance(schemes, dict) else {}
            names.add("X-API-Key" if isinstance(scheme, dict) and scheme.get("name") == "X-API-Key" else name)
    return sorted(names)


def normalize(spec: dict[str, Any]) -> dict[str, Any]:
    raw_paths = spec.get("paths", {})
    paths = raw_paths if isinstance(raw_paths, dict) else {}
    operations: dict[str, Any] = {}
    for path, raw_item in sorted(paths.items()):
        item = resolve_ref(spec, raw_item)
        if not isinstance(item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            operation = resolve_ref(spec, item.get(method))
            if not isinstance(operation, dict):
                continue
            security = operation.get("security", item.get("security", spec.get("security")))
            operations[f"{method.upper()} {path}"] = {
                "security": normalize_security(spec, security),
                "request": request_schema(spec, operation),
                "responses": sorted(str(code) for code in operation.get("responses", {})),
            }
    return {"paths": sorted(paths), "operations": operations}


def compare(snapshot: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_paths, current_paths = snapshot.get("paths", []), current.get("paths", [])
    added, removed = sorted(set(current_paths) - set(expected_paths)), sorted(set(expected_paths) - set(current_paths))
    if added:
        errors.append(f"OpenAPI paths added: {', '.join(added)}")
    if removed:
        errors.append(f"OpenAPI paths removed: {', '.join(removed)}")
    expected_ops, current_ops = snapshot.get("operations", {}), current.get("operations", {})
    for name in sorted(set(current_ops) - set(expected_ops)):
        errors.append(f"OpenAPI operation added: {name}")
    for name in sorted(set(expected_ops) - set(current_ops)):
        errors.append(f"Missing operation: {name}")
    for name in sorted(set(expected_ops) & set(current_ops)):
        expected, actual = expected_ops[name], current_ops[name]
        if expected.get("security") != actual.get("security"):
            errors.append(f"{name} security changed: expected {expected.get('security')}, found {actual.get('security')}")
        if expected.get("request") != actual.get("request"):
            errors.append(
                f"{name} request contract changed: expected {json.dumps(expected.get('request'), sort_keys=True)}, "
                f"found {json.dumps(actual.get('request'), sort_keys=True)}"
            )
        if expected.get("responses", []) != actual.get("responses", []):
            errors.append(
                f"{name} response codes changed: expected {expected.get('responses', [])}, "
                f"found {actual.get('responses', [])}"
            )
    return errors


DOC_URL_RE = re.compile(r"https://lemonslice\.com/docs/[A-Za-z0-9_./-]+")


def check_skill_links(llms_text: str) -> list[str]:
    indexed = {match.group(0).rstrip(").,`'\"") for match in DOC_URL_RE.finditer(llms_text)}
    exceptions = {DEFAULT_LLMS_URL, DEFAULT_OPENAPI_URL}
    errors: list[str] = []
    for skill in ROOT.glob("lemonslice-*/SKILL.md"):
        for raw in DOC_URL_RE.findall(skill.read_text(encoding="utf-8")):
            url = raw.rstrip(").,`'\"")
            variants = {url, url.replace(".md", ""), url.replace("/index.md", ""), url + ".md", url.rstrip("/") + "/index.md"}
            if url not in exceptions and not (variants & indexed):
                errors.append(f"{skill.relative_to(ROOT)} links to unindexed docs page: {url}")
    return errors


def write_report(path: Path, errors: list[str], current: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# LemonSlice documentation drift report", "", f"Status: {'FAIL' if errors else 'PASS'}", ""]
    lines += (["## Drift detected", ""] + [f"- {error}" for error in errors]) if errors else ["No tracked OpenAPI or documentation-index drift detected."]
    lines += ["", "## Current paths", "", *[f"- `{name}`" for name in current.get("paths", [])], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-snapshot", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "docs-drift.md")
    parser.add_argument("--openapi-url", default=DEFAULT_OPENAPI_URL)
    parser.add_argument("--llms-url", default=DEFAULT_LLMS_URL)
    parser.add_argument("--openapi-file", type=Path)
    parser.add_argument("--llms-file", type=Path)
    args = parser.parse_args()
    try:
        spec = json.loads(args.openapi_file.read_bytes() if args.openapi_file else fetch(args.openapi_url))
        llms_text = args.llms_file.read_text(encoding="utf-8") if args.llms_file else fetch(args.llms_url).decode()
    except Exception as exc:
        write_report(args.report, [f"Source retrieval/parsing failed: {exc}"], {"paths": []})
        print(exc, file=sys.stderr)
        return 2
    current = normalize(spec)
    if args.write_snapshot:
        payload = {"generated_from": args.openapi_url, "audited_at": time.strftime("%Y-%m-%d"), "notes": SNAPSHOT_NOTES, **current}
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {args.snapshot}")
        return 0
    errors = compare(json.loads(args.snapshot.read_text(encoding="utf-8")), current)
    errors.extend(check_skill_links(llms_text))
    write_report(args.report, errors, current)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("No LemonSlice documentation drift detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
