# Maintainer tooling

This directory contains repository-maintenance utilities. It is not part of
the installable LemonSlice skill content.

## Directories

- `openapi/` — downloads, normalizes, compares, and tests LemonSlice OpenAPI contracts.
- `evals/` — behavioral evaluation definitions, fixtures, workspace preparation, and result scoring.
- `validation/` — repository structure, Markdown link, and generated JSON validation.

The installable skills live in the top-level `lemonslice-*` directories and
consist primarily of Markdown instructions, YAML interface metadata, and
reference data.

## Static validation

```bash
python maintainers/validation/validate_skills.py
python maintainers/validation/validate_skills.py --links-only
python maintainers/validation/format_repository_data.py --check
python maintainers/evals/run_evals.py --validate
python -m unittest discover \
  -s maintainers/openapi/tests \
  -p "test_*.py" \
  -v
```

## Behavioral evaluation preparation

```bash
python maintainers/evals/materialize_workspaces.py \
  --output artifacts/eval-inputs
```

## OpenAPI drift

```bash
python maintainers/openapi/sync_openapi.py --check
```
