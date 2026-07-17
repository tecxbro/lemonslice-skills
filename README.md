# LemonSlice Skills

Agent skills for building production LemonSlice integrations.

> This repository is community-maintained and is **not** the official LemonSlice skills repository.

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

LemonSlice documentation, OpenAPI, rendered pages, account entitlements, and published SDK versions can temporarily differ. Implementation skills inspect the exact surface before using volatile options.

## Maintenance

- `lemonslice-api-reference/scripts/sync_openapi.py` preserves alternatives, media types, enums, security metadata, and response codes.
- `lemonslice-api-reference/tests/` validates normalization offline.
- `scripts/validate_skills.py` validates skill structure and local references.
- `.github/workflows/docs-drift.yml` runs live drift checks and uploads the normalized current contract.
- `.github/workflows/evals.yml` validates skills, eval fixtures, normalizer tests, and documentation links without requiring live LemonSlice API access.
- Exact generated/volatile contracts live in reference files; `SKILL.md` files focus on routing and implementation workflow.

## Evaluation

```bash
python evals/run_evals.py --validate
python evals/run_evals.py --results-dir /path/to/agent-results
```

The harness compares materialized results against original fixtures, verifies selected skills, evaluates per-file assertions, rejects unrelated edits, and can run explicitly configured validation commands in a sandboxed test environment.

License: MIT.
