#!/usr/bin/env python3
"""Normalize LemonSlice OpenAPI contracts and report documentation drift.

The downloader can probe the public sources repeatedly before selecting a body.
Exit codes:
  0: success / no drift
  1: stable source, tracked contract drift detected
  2: retrieval, parsing, or configuration failure
  3: source probes returned conflicting normalized contracts
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_OPENAPI_URL = "https://lemonslice.com/docs/openapi.json"
DEFAULT_LLMS_URL = "https://lemonslice.com/docs/llms.txt"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT = (
    ROOT
    / "lemonslice-api-reference"
    / "references"
    / "openapi.snapshot.json"
)
SOURCE_INCONSISTENT_EXIT = 3

SCHEMA_KEYS = (
    "format",
    "default",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "minProperties",
    "maxProperties",
    "pattern",
    "multipleOf",
)


@dataclass(frozen=True)
class FetchResult:
    body: bytes
    sha256: str
    final_url: str
    date: str | None
    etag: str | None
    age: str | None
    last_modified: str | None

    def metadata(self) -> dict[str, Any]:
        value = asdict(self)
        value.pop("body")
        return value


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def fetch(url: str, attempts: int = 3, timeout: int = 30) -> FetchResult:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "lemonslice-skills-drift/3",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                return FetchResult(
                    body=body,
                    sha256=hashlib.sha256(body).hexdigest(),
                    final_url=response.geturl(),
                    date=response.headers.get("Date"),
                    etag=response.headers.get("ETag"),
                    age=response.headers.get("Age"),
                    last_modified=response.headers.get("Last-Modified"),
                )
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Unable to fetch {url}: {last}")


def resolve_ref(spec: dict[str, Any], value: Any) -> Any:
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    ref = value["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return value
    current: Any = spec
    for part in ref[2:].split("/"):
        if not isinstance(current, dict):
            return value
        current = current[part.replace("~1", "/").replace("~0", "~")]
    if isinstance(current, dict):
        return {**current, **{key: item for key, item in value.items() if key != "$ref"}}
    return current


def normalized_types(schema: dict[str, Any]) -> list[str]:
    raw = schema.get("type")
    if isinstance(raw, str):
        values = [raw]
    elif isinstance(raw, list):
        values = [item for item in raw if isinstance(item, str)]
    else:
        values = []
    if schema.get("nullable") is True and "null" not in values:
        values.append("null")
    return sorted(set(values))


def normalize_discriminator(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, Any] = {}
    if isinstance(value.get("propertyName"), str):
        result["property_name"] = value["propertyName"]
    if isinstance(value.get("mapping"), dict):
        result["mapping"] = dict(sorted(value["mapping"].items()))
    return result or None


def merge_all_of_contract(target: dict[str, Any], member: dict[str, Any]) -> None:
    for key in ("required", "forbidden"):
        if member.get(key):
            target[key] = sorted(set(target.get(key, [])) | set(member[key]))
    if member.get("dependent_required"):
        combined = dict(target.get("dependent_required", {}))
        for name, fields in member["dependent_required"].items():
            combined[name] = sorted(set(combined.get(name, [])) | set(fields))
        target["dependent_required"] = dict(sorted(combined.items()))


def normalize_schema(
    spec: dict[str, Any],
    raw_schema: Any,
    seen: set[str] | None = None,
) -> dict[str, Any]:
    seen = set() if seen is None else set(seen)
    if not isinstance(raw_schema, dict):
        return {}

    if "$ref" in raw_schema:
        ref = raw_schema.get("$ref")
        if isinstance(ref, str):
            if ref in seen:
                return {"ref": ref}
            seen.add(ref)
        schema = resolve_ref(spec, raw_schema)
        if not isinstance(schema, dict):
            return {"ref": ref} if isinstance(ref, str) else {}
    else:
        schema = raw_schema

    result: dict[str, Any] = {}
    if isinstance(schema.get("title"), str) and schema["title"].strip():
        result["title"] = schema["title"].strip()

    types = normalized_types(schema)
    if types:
        result["types"] = types
    if "null" in types:
        result["nullable"] = True

    if isinstance(schema.get("enum"), list):
        result["enum"] = sorted(schema["enum"], key=lambda item: str(item))
    if "const" in schema:
        result["const"] = schema["const"]

    for source_key in SCHEMA_KEYS:
        if source_key in schema:
            destination = re.sub(r"(?<!^)(?=[A-Z])", "_", source_key).lower()
            result[destination] = schema[source_key]

    required = sorted(item for item in schema.get("required", []) if isinstance(item, str))
    if required:
        result["required"] = required

    negated = resolve_ref(spec, schema.get("not", {}))
    if isinstance(negated, dict):
        forbidden = sorted(
            item for item in negated.get("required", []) if isinstance(item, str)
        )
        if forbidden:
            result["forbidden"] = forbidden

    dependent = schema.get("dependentRequired", {})
    if isinstance(dependent, dict):
        normalized_dependent = {
            name: sorted(item for item in fields if isinstance(item, str))
            for name, fields in dependent.items()
            if isinstance(name, str) and isinstance(fields, list)
        }
        if normalized_dependent:
            result["dependent_required"] = dict(sorted(normalized_dependent.items()))

    properties = schema.get("properties", {})
    if isinstance(properties, dict) and properties:
        result["properties"] = {
            name: normalize_schema(spec, value, seen)
            for name, value in sorted(properties.items())
            if isinstance(name, str)
        }

    if "items" in schema:
        result["items"] = normalize_schema(spec, schema["items"], seen)

    for source_key, destination in (
        ("additionalProperties", "additional_properties"),
        ("unevaluatedProperties", "unevaluated_properties"),
    ):
        value = schema.get(source_key)
        if isinstance(value, bool):
            result[destination] = value
        elif isinstance(value, dict):
            result[destination] = normalize_schema(spec, value, seen)

    all_of = schema.get("allOf", [])
    if isinstance(all_of, list) and all_of:
        members = [normalize_schema(spec, member, seen) for member in all_of]
        result["all_of"] = members
        for member in members:
            merge_all_of_contract(result, member)

    for source_key, destination in (("oneOf", "one_of"), ("anyOf", "any_of")):
        variants = schema.get(source_key, [])
        if isinstance(variants, list) and variants:
            normalized_variants: list[dict[str, Any]] = []
            for variant in variants:
                normalized = normalize_schema(spec, variant, seen)
                event = (
                    normalized.get("properties", {})
                    .get("event", {})
                    .get("const")
                    if isinstance(normalized.get("properties"), dict)
                    else None
                )
                if isinstance(event, str):
                    normalized = {"event": event, **normalized}
                normalized_variants.append(normalized)
            result[destination] = normalized_variants

    discriminator = normalize_discriminator(schema.get("discriminator"))
    if discriminator:
        result["discriminator"] = discriminator

    return result


def normalize_content(spec: dict[str, Any], raw_content: Any) -> dict[str, Any]:
    content = raw_content if isinstance(raw_content, dict) else {}
    media_types: dict[str, Any] = {}
    for content_type, raw_media in sorted(content.items()):
        media = resolve_ref(spec, raw_media)
        schema = media.get("schema", {}) if isinstance(media, dict) else {}
        media_types[content_type] = {"schema": normalize_schema(spec, schema)}
    result: dict[str, Any] = {
        "content_types": sorted(media_types),
        "media_types": media_types,
    }
    if "application/json" in media_types:
        result["schema"] = media_types["application/json"]["schema"]
    return result


def normalize_request(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    body = resolve_ref(spec, operation.get("requestBody", {}))
    if not isinstance(body, dict):
        body = {}
    result = normalize_content(spec, body.get("content", {}))
    result["body_required"] = body.get("required") is True
    return result


def normalize_response(spec: dict[str, Any], raw_response: Any) -> dict[str, Any]:
    response = resolve_ref(spec, raw_response)
    if not isinstance(response, dict):
        response = {}
    return normalize_content(spec, response.get("content", {}))


def normalize_responses(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    responses = operation.get("responses", {})
    if not isinstance(responses, dict):
        return {}
    return {
        str(code): normalize_response(spec, response)
        for code, response in sorted(responses.items(), key=lambda item: str(item[0]))
    }


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
            names.add(
                "X-API-Key"
                if isinstance(scheme, dict) and scheme.get("name") == "X-API-Key"
                else name
            )
    return sorted(names)


def normalize_parameter(spec: dict[str, Any], raw_parameter: Any) -> tuple[str, str, dict[str, Any]] | None:
    parameter = resolve_ref(spec, raw_parameter)
    if not isinstance(parameter, dict):
        return None
    name, location = parameter.get("name"), parameter.get("in")
    if not isinstance(name, str) or location not in {"path", "query"}:
        return None
    normalized = {
        "required": parameter.get("required") is True,
        "schema": normalize_schema(spec, parameter.get("schema", {})),
    }
    return location, name, normalized


def normalize_parameters(
    spec: dict[str, Any],
    path_item: dict[str, Any],
    operation: dict[str, Any],
) -> dict[str, Any]:
    combined: dict[tuple[str, str], dict[str, Any]] = {}
    for source in (path_item.get("parameters", []), operation.get("parameters", [])):
        if not isinstance(source, list):
            continue
        for raw_parameter in source:
            normalized = normalize_parameter(spec, raw_parameter)
            if normalized:
                location, name, value = normalized
                combined[(location, name)] = value
    return {
        "path": {
            name: value
            for (location, name), value in sorted(combined.items())
            if location == "path"
        },
        "query": {
            name: value
            for (location, name), value in sorted(combined.items())
            if location == "query"
        },
    }


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
                "parameters": normalize_parameters(spec, item, operation),
                "request": normalize_request(spec, operation),
                "responses": normalize_responses(spec, operation),
            }
    return {"paths": sorted(paths), "operations": operations}


def compare(snapshot: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_paths, actual_paths = snapshot.get("paths", []), current.get("paths", [])
    added = sorted(set(actual_paths) - set(expected_paths))
    removed = sorted(set(expected_paths) - set(actual_paths))
    if added:
        errors.append(f"OpenAPI paths added: {', '.join(added)}")
    if removed:
        errors.append(f"OpenAPI paths removed: {', '.join(removed)}")

    expected_ops, actual_ops = snapshot.get("operations", {}), current.get("operations", {})
    for name in sorted(set(actual_ops) - set(expected_ops)):
        errors.append(f"OpenAPI operation added: {name}")
    for name in sorted(set(expected_ops) - set(actual_ops)):
        errors.append(f"Missing operation: {name}")
    for name in sorted(set(expected_ops) & set(actual_ops)):
        expected, actual = expected_ops[name], actual_ops[name]
        for key, label in (
            ("security", "security"),
            ("parameters", "parameters"),
            ("request", "request contract"),
            ("responses", "response contracts"),
        ):
            if expected.get(key) != actual.get(key):
                errors.append(
                    f"{name} {label} changed: expected "
                    f"{json.dumps(expected.get(key), sort_keys=True)}, found "
                    f"{json.dumps(actual.get(key), sort_keys=True)}"
                )
    return errors


DOC_URL_RE = re.compile(r"https://lemonslice\.com/docs/[A-Za-z0-9_./-]+")


def documentation_files() -> list[Path]:
    candidates = [ROOT / "README.md"]
    candidates.extend(ROOT.glob("references/**/*.md"))
    candidates.extend(ROOT.glob("lemonslice-*/SKILL.md"))
    candidates.extend(ROOT.glob("lemonslice-*/references/**/*.md"))
    return sorted({path for path in candidates if path.is_file()})


def check_documentation_links(llms_text: str) -> list[str]:
    indexed = {match.group(0).rstrip(").,`'\"") for match in DOC_URL_RE.finditer(llms_text)}
    exceptions = {DEFAULT_LLMS_URL, DEFAULT_OPENAPI_URL}
    errors: list[str] = []
    for document in documentation_files():
        text = document.read_text(encoding="utf-8")
        for raw in DOC_URL_RE.findall(text):
            url = raw.rstrip(").,`'\"")
            variants = {
                url,
                url.replace(".md", ""),
                url.replace("/index.md", ""),
                url + ".md",
                url.rstrip("/") + "/index.md",
            }
            if url not in exceptions and not (variants & indexed):
                errors.append(
                    f"{document.relative_to(ROOT)} links to unindexed docs page: {url}"
                )
    return errors


def probe_source(
    url: str,
    probe_count: int,
    normalizer: Callable[[bytes], Any] | None = None,
) -> tuple[list[FetchResult], list[str | None]]:
    results: list[FetchResult] = []
    normalized_digests: list[str | None] = []
    for _ in range(probe_count):
        result = fetch(url)
        results.append(result)
        normalized_digests.append(
            canonical_sha(normalizer(result.body)) if normalizer else None
        )
    return results, normalized_digests


def source_metadata(
    url: str,
    results: list[FetchResult],
    normalized_digests: list[str | None],
) -> dict[str, Any]:
    probes: list[dict[str, Any]] = []
    for result, normalized_digest in zip(results, normalized_digests, strict=True):
        item = result.metadata()
        if normalized_digest:
            item["normalized_sha256"] = normalized_digest
        probes.append(item)
    raw_digests = {result.sha256 for result in results}
    normalized_values = {value for value in normalized_digests if value is not None}
    return {
        "url": url,
        "probe_count": len(results),
        "raw_consistent": len(raw_digests) <= 1,
        "normalized_consistent": len(normalized_values) <= 1,
        "probes": probes,
    }


def normalize_openapi_bytes(body: bytes) -> dict[str, Any]:
    return normalize(json.loads(body))


def download_sources(
    source_dir: Path,
    openapi_url: str,
    llms_url: str,
    probe_count: int,
) -> tuple[int, dict[str, Any]]:
    source_dir.mkdir(parents=True, exist_ok=True)
    openapi_results, openapi_normalized = probe_source(
        openapi_url, probe_count, normalize_openapi_bytes
    )
    llms_results, llms_normalized = probe_source(llms_url, probe_count)

    for index, result in enumerate(openapi_results, start=1):
        (source_dir / f"openapi.probe-{index}.json").write_bytes(result.body)
    for index, result in enumerate(llms_results, start=1):
        (source_dir / f"llms.probe-{index}.txt").write_bytes(result.body)

    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "openapi": source_metadata(openapi_url, openapi_results, openapi_normalized),
        "llms": source_metadata(llms_url, llms_results, llms_normalized),
    }
    metadata_path = source_dir / "source-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    openapi_consistent = metadata["openapi"]["normalized_consistent"]
    llms_consistent = metadata["llms"]["raw_consistent"]
    if not openapi_consistent or not llms_consistent:
        return SOURCE_INCONSISTENT_EXIT, metadata

    (source_dir / "openapi.json").write_bytes(openapi_results[0].body)
    (source_dir / "llms.txt").write_bytes(llms_results[0].body)
    return 0, metadata


def metadata_lines(metadata: dict[str, Any] | None) -> list[str]:
    if not metadata:
        return ["Source metadata was not supplied."]
    lines: list[str] = []
    for name in ("openapi", "llms"):
        source = metadata.get(name, {})
        if not isinstance(source, dict):
            continue
        lines.append(
            f"- **{name}**: probes={source.get('probe_count')}, "
            f"raw_consistent={source.get('raw_consistent')}, "
            f"normalized_consistent={source.get('normalized_consistent')}"
        )
        for index, probe in enumerate(source.get("probes", []), start=1):
            if not isinstance(probe, dict):
                continue
            lines.append(
                f"  - probe {index}: sha256=`{probe.get('sha256')}`, "
                f"normalized_sha256=`{probe.get('normalized_sha256')}`, "
                f"etag=`{probe.get('etag')}`, age=`{probe.get('age')}`, "
                f"date=`{probe.get('date')}`, final_url=`{probe.get('final_url')}`"
            )
    return lines or ["Source metadata was empty."]


def write_report(
    path: Path,
    errors: list[str],
    current: dict[str, Any],
    metadata: dict[str, Any] | None,
    *,
    inconsistent: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = "SOURCE_INCONSISTENT" if inconsistent else ("FAIL" if errors else "PASS")
    lines = [
        "# LemonSlice documentation drift report",
        "",
        f"Status: {status}",
        "",
        "## Source metadata",
        "",
        *metadata_lines(metadata),
        "",
    ]
    if inconsistent:
        lines += [
            "## Source instability",
            "",
            "Repeated probes returned conflicting contracts. No source version was selected automatically.",
            "",
        ]
    elif errors:
        lines += ["## Drift detected", "", *[f"- {error}" for error in errors], ""]
    else:
        lines += ["No tracked OpenAPI or documentation-index drift detected.", ""]
    lines += [
        "## Current paths",
        "",
        *[f"- `{name}`" for name in current.get("paths", [])],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def load_metadata(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def load_sources(args: argparse.Namespace) -> tuple[bytes, str, dict[str, Any] | None]:
    if args.openapi_file and args.llms_file:
        return (
            args.openapi_file.read_bytes(),
            args.llms_file.read_text(encoding="utf-8"),
            load_metadata(args.source_metadata_file),
        )
    if args.openapi_file or args.llms_file:
        raise ValueError("--openapi-file and --llms-file must be supplied together")

    openapi_results, openapi_digests = probe_source(
        args.openapi_url, args.probe_count, normalize_openapi_bytes
    )
    llms_results, llms_digests = probe_source(args.llms_url, args.probe_count)
    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "openapi": source_metadata(args.openapi_url, openapi_results, openapi_digests),
        "llms": source_metadata(args.llms_url, llms_results, llms_digests),
    }
    if not metadata["openapi"]["normalized_consistent"] or not metadata["llms"]["raw_consistent"]:
        raise SourceInconsistent(metadata)
    return openapi_results[0].body, llms_results[0].body.decode("utf-8"), metadata


class SourceInconsistent(RuntimeError):
    def __init__(self, metadata: dict[str, Any]):
        super().__init__("Source probes returned conflicting contracts")
        self.metadata = metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-snapshot", action="store_true")
    parser.add_argument("--download-sources", action="store_true")
    parser.add_argument("--probe-count", type=int, default=1)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "artifacts" / "sources")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "docs-drift.md")
    parser.add_argument("--openapi-url", default=DEFAULT_OPENAPI_URL)
    parser.add_argument("--llms-url", default=DEFAULT_LLMS_URL)
    parser.add_argument("--openapi-file", type=Path)
    parser.add_argument("--llms-file", type=Path)
    parser.add_argument("--source-metadata-file", type=Path)
    args = parser.parse_args()

    if args.probe_count < 1:
        print("Configuration error: --probe-count must be at least 1", file=sys.stderr)
        return 2

    if args.download_sources:
        try:
            code, metadata = download_sources(
                args.source_dir, args.openapi_url, args.llms_url, args.probe_count
            )
        except Exception as exc:
            print(f"Source download failed: {exc}", file=sys.stderr)
            return 2
        if code == SOURCE_INCONSISTENT_EXIT:
            write_report(args.report, [], {"paths": []}, metadata, inconsistent=True)
            print("Source probes returned conflicting contracts.", file=sys.stderr)
        else:
            print(f"Downloaded stable source contracts to {args.source_dir}")
        return code

    try:
        openapi_bytes, llms_text, metadata = load_sources(args)
        spec = json.loads(openapi_bytes)
    except SourceInconsistent as exc:
        write_report(args.report, [], {"paths": []}, exc.metadata, inconsistent=True)
        print(str(exc), file=sys.stderr)
        return SOURCE_INCONSISTENT_EXIT
    except Exception as exc:
        write_report(
            args.report,
            [f"Source retrieval/parsing failed: {exc}"],
            {"paths": []},
            None,
        )
        print(exc, file=sys.stderr)
        return 2

    current = normalize(spec)
    if args.write_snapshot:
        payload = {
            "audited_at": time.strftime("%Y-%m-%d"),
            "source_metadata": metadata,
            **current,
        }
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"Wrote {args.snapshot}")
        return 0

    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    errors = compare(snapshot, current)
    errors.extend(check_documentation_links(llms_text))
    write_report(args.report, errors, current, metadata)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("No LemonSlice documentation drift detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
