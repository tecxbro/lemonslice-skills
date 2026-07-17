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

## Routing

Use `lemonslice-integration-choice` only for ambiguous requests. When the user already names LiveKit, Pipecat, Hosted Daily, Widget, a meeting platform, runtime control, or rendering/compositing, route directly to that skill.

## Skills

| Skill | Purpose |
| --- | --- |
| `lemonslice-overview` | Product map, Character World Models, and integration paths |
| `lemonslice-integration-choice` | Route ambiguous requests without overriding explicit choices |
| `lemonslice-livekit` | Python and Node LiveKit Agents integration |
| `lemonslice-pipecat` | Pipecat transport integration |
| `lemonslice-self-managed` | Raw self-managed session integration when no framework plugin owns it |
| `lemonslice-hosted` | Backend creation and management of LemonSlice-hosted rooms |
| `lemonslice-hosted-daily` | Daily frontend for hosted rooms |
| `lemonslice-widget` | Embed and control the no-code widget |
| `lemonslice-api-reference` | Endpoint selection, schema validation, and docs-conflict handling |
| `lemonslice-control-actions` | Runtime image, prompt, action, idle-reset, and termination controls |
| `lemonslice-production-patterns` | Readiness, errors, timeouts, latency, cleanup, and billing safety |
| `lemonslice-meeting-platforms` | Zoom, Google Meet, Microsoft Teams, and Webex meeting bots |
| `lemonslice-appearance-rendering` | Model/aspect-ratio selection, image framing, and WebGL compositing |

## What these skills guarantee

When repository edits are requested, implementation skills:

1. Inspect the repository, runtime entrypoint, framework, package manager, and installed SDK versions.
2. Preserve the existing architecture and make the smallest complete change.
3. Keep `LEMONSLICE_API_KEY` in trusted server/agent code.
4. Distinguish pipeline readiness from the first rendered avatar frame.
5. Run available formatting, type checking, tests, and builds.
6. Report files changed, commands run, results, and documentation/version conflicts.

See [`references/implementation-contract.md`](references/implementation-contract.md).

## Documentation version

Last audited against:

- LemonSlice `llms.txt`: **2026-07-17**
- LemonSlice OpenAPI and rendered endpoint docs: **2026-07-17**

LemonSlice documentation and published SDK versions can temporarily differ. Implementation skills inspect installed package signatures before using newly documented options.

## Maintenance

- `lemonslice-api-reference/scripts/sync_openapi.py` checks endpoint paths, request contracts, enums, security metadata, and documentation links.
- `.github/workflows/docs-drift.yml` runs weekly, on skill changes, and manually.
- Exact generated/volatile contracts live in reference files; `SKILL.md` files focus on routing and implementation workflow.
- Documentation conflicts are recorded instead of being silently resolved by guesswork.

## Evaluation

```bash
python evals/run_evals.py --validate
python evals/run_evals.py --results-dir /path/to/agent-results
```

The harness verifies routing, expected edits, forbidden patterns, and fixture coverage.

License: MIT.
