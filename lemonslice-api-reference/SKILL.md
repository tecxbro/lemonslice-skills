---
name: lemonslice-api-reference
description: Select and validate LemonSlice REST endpoints, inspect current OpenAPI, handle authentication conflicts, and avoid duplicating volatile schemas in skill prose.
license: MIT
---

# LemonSlice API reference workflow

Use generated references for exact contracts:

- `references/endpoint-matrix.md`
- `references/openapi.snapshot.json`
- `references/docs-conflicts.md`

Run `python lemonslice-api-reference/scripts/sync_openapi.py --check` before relying on volatile fields when internet access is available.

## Endpoint selection

- Self-managed avatar-only sessions: `/liveai/sessions`
- Hosted Pipeline rooms: `/liveai/rooms`
- Runtime controls: `/liveai/sessions/{session_id}/control`
- External meetings: `/liveai/sessions/{session_id}/join-meeting` and `/leave-meeting`

Do not mix endpoint families.

## Authentication source-of-truth rule

Do not assume one authentication rule for every endpoint.

- Create, get, and list session/room endpoints require `X-API-Key`.
- Meeting join and leave endpoints require `X-API-Key`.
- The current control endpoint rendered example omits the header, and the OpenAPI operation declares `security: []`.
- The current control OpenAPI response set includes `413`, while the rendered page lists `200`, `400`, `404`, and `500`.

For the control endpoint:

1. keep the call in trusted backend/server code;
2. inspect the current OpenAPI operation and rendered endpoint docs;
3. preserve the existing application's known-working authentication behavior;
4. report the conflict instead of asserting an unsupported universal rule.

Never conclude “control requires no authentication” from `security: []` alone.

## Validation workflow

1. Inspect current endpoint docs and OpenAPI.
2. Validate required fields, exactly-one constraints, enums, status codes, and response shapes.
3. Use abortable timeouts.
4. Parse non-JSON error bodies safely.
5. Never send raw keys from browser code.
6. Preserve app authorization and ownership.
7. Record docs/version conflicts in the implementation report.

`Reset Idle Timeout` appears in rendered control documentation. Verify the current control-event schema before changing support because rendered docs and OpenAPI can expose different detail.
