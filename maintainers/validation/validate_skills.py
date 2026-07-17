#!/usr/bin/env python3
"""Validate LemonSlice skill structure and local documentation references."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
SKILL_GLOB = "lemonslice-*/SKILL.md"
REQUIRED_FRONTMATTER = {"name", "description", "license"}
NON_IMPLEMENTATION_SKILLS = {
    "lemonslice-api-reference",
    "lemonslice-integration-choice",
    "lemonslice-overview",
}
TRIGGER_WORDS = {
    "add",
    "bootstrap",
    "build",
    "embed",
    "explain",
    "implement",
    "integrate",
    "production",
    "route",
    "select",
    "use",
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
URL_RE = re.compile(r"(?:https?://|mailto:)[^\s)>]+")
SKILL_NAME_RE = re.compile(r"\blemonslice-[a-z0-9-]+\b")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
REAL_SECRET_RE = re.compile(
    r"(?:LEMONSLICE_API_KEY|X-API-Key)\s*(?:=|:)\s*[\"']"
    r"(?!<|\$\{|process\.env|os\.environ)[^\"']{12,}[\"']",
    re.IGNORECASE,
)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def documentation_files() -> list[Path]:
    candidates = [ROOT / "README.md"]
    candidates.extend(ROOT.glob("references/**/*.md"))
    candidates.extend(ROOT.glob("lemonslice-*/SKILL.md"))
    candidates.extend(ROOT.glob("lemonslice-*/references/**/*.md"))
    candidates.extend(ROOT.glob("maintainers/**/*.md"))
    return sorted({path for path in candidates if path.is_file()})


def local_links(path: Path, text: str) -> Iterable[tuple[str, Path]]:
    for raw in MARKDOWN_LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        yield raw, (path.parent / target).resolve()


def referenced_skill_names(text: str) -> set[str]:
    """Return skill identifiers from prose/code, excluding URL path segments."""
    without_urls = URL_RE.sub("", text)
    return set(SKILL_NAME_RE.findall(without_urls))


def validate_agent_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^interface:\s*$", text, re.MULTILINE):
        errors.append(f"{path.relative_to(ROOT)}: missing interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf"^\s{{2}}{field}:\s*\S", text, re.MULTILINE):
            errors.append(f"{path.relative_to(ROOT)}: missing interface.{field}")
    return errors


def validate_links(documents: list[Path], known_skills: set[str]) -> list[str]:
    errors: list[str] = []
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for raw, resolved in local_links(path, text):
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: local link does not exist: {raw}"
                )
        for referenced in sorted(referenced_skill_names(text)):
            if referenced not in known_skills and referenced != "lemonslice-skills":
                errors.append(
                    f"{path.relative_to(ROOT)}: referenced skill does not exist: {referenced}"
                )
    return errors


def validate_skill(path: Path, known_skills: set[str]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    relative = path.relative_to(ROOT)

    missing = sorted(REQUIRED_FRONTMATTER - set(metadata))
    if missing:
        errors.append(f"{relative}: missing frontmatter fields: {', '.join(missing)}")
        return errors

    directory_name = path.parent.name
    if metadata["name"] != directory_name:
        errors.append(
            f"{relative}: frontmatter name {metadata['name']!r} "
            f"does not match directory {directory_name!r}"
        )

    description_words = set(re.findall(r"[a-z]+", metadata["description"].lower()))
    if not (description_words & TRIGGER_WORDS):
        errors.append(
            f"{relative}: description needs a positive trigger/implementation condition"
        )

    if directory_name not in NON_IMPLEMENTATION_SKILLS:
        if "references/implementation-contract.md" not in text:
            errors.append(f"{relative}: implementation skill must link to implementation contract")

    for heading in HEADING_RE.findall(text):
        if "Lemon Slice" in heading:
            errors.append(
                f"{relative}: stale 'Lemon Slice' naming in heading: {heading!r}"
            )

    if REAL_SECRET_RE.search(text):
        errors.append(f"{relative}: possible placeholder or embedded credential")

    raw_api_reference = "https://lemonslice.com/api/liveai/" in text
    volatile_raw_fields = any(
        token in text for token in ("model", "aspect_ratio", "transport_type", "enable_recording")
    )
    if raw_api_reference and volatile_raw_fields:
        if "openapi" not in text.lower() and "lemonslice-api-reference" not in text:
            errors.append(
                f"{relative}: duplicates volatile raw API fields without an OpenAPI/reference source"
            )

    for referenced in sorted(referenced_skill_names(text)):
        if referenced not in known_skills and referenced != "lemonslice-skills":
            errors.append(f"{relative}: referenced skill does not exist: {referenced}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--links-only",
        action="store_true",
        help="Validate local links and referenced skill names across repository Markdown.",
    )
    args = parser.parse_args()

    skills = sorted(ROOT.glob(SKILL_GLOB))
    if not skills:
        print("FAIL: no LemonSlice skills found", file=sys.stderr)
        return 1

    known_skills = {path.parent.name for path in skills}
    documents = documentation_files()
    errors = validate_links(documents, known_skills)

    if not args.links_only:
        for path in skills:
            errors.extend(validate_skill(path, known_skills))
        for agent_yaml in sorted(ROOT.glob("lemonslice-*/agents/openai.yaml")):
            errors.extend(validate_agent_yaml(agent_yaml))

    if errors:
        unique_errors = sorted(set(errors))
        for error in unique_errors:
            print(f"FAIL: {error}")
        print(f"\n{len(unique_errors)} validation failure(s).")
        return 1

    mode = "documentation links" if args.links_only else "skill structure and documentation"
    print(f"PASS: validated {mode} for {len(skills)} skills and {len(documents)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
