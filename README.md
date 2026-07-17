# LemonSlice Skills

Agent skills for building production LemonSlice integrations.

> This repository is community-maintained and is **not** the official LemonSlice skills repository.

## Repository layout

The installable skills live in the top-level `lemonslice-*` directories.
They contain Markdown instructions, YAML interface metadata, and reference data.

Repository tests, OpenAPI monitoring, evaluation fixtures, and validators live
under `maintainers/` and are not part of the skill instructions.

## Install

```bash
npx skills add tecxbro/lemonslice-skills
```

Install one skill:

```bash
npx skills add tecxbro/lemonslice-skills --skill lemonslice-livekit
```

## Product modes

LemonSlice supports three top-level deployment modes:

- **Self-Managed Pipeline:** the application owns STT, VAD/turn detection, LLM, TTS, tools, conversation state, and transport integration; LemonSlice supplies avatar media.
- **Hosted Pipeline:** LemonSlice owns the conversational pipeline and avatar generation; the application owns authorization and a custom Daily frontend.
- **Widget:** LemonSlice owns the prebuilt embed and call experience.

Framework-specific skills describe implementation paths inside those modes.

## Routing

Use `lemonslice-integration-choice` only for ambiguous requests. When the user already names a new-project Quickstart, LiveKit, Pipecat, Hosted Daily, Widget, a meeting platform, runtime control, or rendering/compositing, route directly to that skill.

## Skills

| Skill | Purpose |
| --- | --- |
| `lemonslice-overview` | Character World Model, product modes, capabilities, and skill map |
| `lemonslice-integration-choice` | Route ambiguous requests and chain material secondary concerns |
| `lemonslice-quickstart` | Bootstrap a new project from the official Next.js + LiveKit starter |
| `lemonslice-livekit` | Integrate into an existing Python or Node LiveKit Agents app |
| `lemonslice-pipecat` | Integrate into an existing Pipecat pipeline |
| `lemonslice-self-managed` | Raw self-managed REST for a custom LiveKit or Daily stack |
| `lemonslice-hosted` | Backend creation and reconciliation of Hosted Pipeline rooms |
| `lemonslice-hosted-daily` | Daily frontend for Hosted Pipeline credentials |
| `lemonslice-widget` | Embed and control the prebuilt widget |
| `lemonslice-api-reference` | Endpoint selection, OpenAPI normalization, and docs-conflict handling |
| `lemonslice-control-actions` | Runtime image, prompt, provisioned action, idle-reset, and terminate controls |
| `lemonslice-production-patterns` | Readiness, errors, capacity, latency, reconciliation, cleanup, and data safety |
| `lemonslice-meeting-platforms` | Zoom, Google Meet, Microsoft Teams, and Webex meeting bots |
| `lemonslice-appearance-rendering` | Model/aspect surfaces, image framing, and WebGL compositing |

## Contract source hierarchy

1. Inspect the current repository and installed SDK/package signature.
2. Use the integration-specific official documentation.
3. Use the current OpenAPI for raw REST contracts.
4. Treat rendered endpoint pages as another observable source when they conflict with the downloadable schema.
5. Record conflicts instead of copying a field across surfaces.
6. Verify account-gated features such as models, actions, recording, high resolution, long calls, concurrency, or special deployment modes.

A single successful OpenAPI request is not proof that all public CDN locations are serving the same contract. The drift workflow probes repeatedly, records response metadata and digests, and reports source inconsistency instead of selecting a conflicting version automatically.

The product overview may reference integrations such as Agora, but this repository does not invent an Agora raw REST contract. Agora requests require current official integration documentation or an inspectable installed SDK.

## What these skills guarantee

When repository edits are requested, implementation skills:

1. Inspect the repository, runtime entrypoint, framework, package manager, and installed SDK versions.
2. Preserve the existing architecture and make the smallest complete change.
3. Keep `LEMONSLICE_API_KEY` in trusted server/agent code.
4. Distinguish provider acknowledgement and pipeline readiness from the first rendered avatar frame.
5. Implement lifecycle cleanup and backend reconciliation where needed.
6. Run available formatting, type checking, tests, and builds.
7. Report files changed, commands run, results, and documentation/version conflicts.

See [`references/implementation-contract.md`](references/implementation-contract.md).

## Documentation version

Last audited against:

- LemonSlice `llms.txt`: **2026-07-17**
- LemonSlice OpenAPI and rendered endpoint docs: **2026-07-17**

LemonSlice documentation, OpenAPI, rendered pages, CDN edges, account entitlements, and published SDK versions can temporarily differ. Implementation skills inspect the exact active surface before using volatile options.

## Maintenance

- `maintainers/openapi/sync_openapi.py` probes source stability and tracks parameters, request media types, request schemas, response media types, response schemas, enums, constraints, nullability, security, and endpoints.
- `maintainers/openapi/tests/` validates normalization offline against composition fixtures and a sanitized LemonSlice-shaped OpenAPI fixture.
- `maintainers/validation/validate_skills.py` validates skill structure and local links across repository Markdown.
- `maintainers/validation/format_repository_data.py` keeps generated and evaluation JSON reviewable.
- `.github/workflows/docs-drift.yml` downloads each live source once after repeated probes, then reuses that saved evidence for normalization and comparison.
- `.github/workflows/evals.yml` performs **static validation only**: skill structure, evaluation definitions, normalizer tests, documentation links, and JSON formatting.
- `.github/workflows/behavioral-evals.yml` prepares fixtures or scores results produced by an external agent executor. It does not claim to run an agent automatically.
- Exact generated contracts live in reference files; human interpretation and cross-source conflicts live in Markdown references.

## Evaluation

```bash
python maintainers/evals/run_evals.py --validate
python maintainers/evals/run_evals.py --results-dir /path/to/agent-results
```

Static validation confirms that the 31 behavioral cases, fixtures, regexes, file rules, and response assertions are well formed. It does **not** prove that an agent passed those cases.

Behavioral scoring compares externally materialized agent results against original fixtures, verifies selected skills, evaluates user-facing responses, enforces required/allowed/forbidden file patterns, and scores command results produced by an externally isolated environment. The scorer itself never executes agent-modified project code. See [`maintainers/evals/README.md`](maintainers/evals/README.md).

License: MIT.
