---
name: lemonslice-api-reference
description: Select and validate LemonSlice REST endpoints, inspect current OpenAPI, handle authentication conflicts, and avoid duplicating volatile schemas in skill prose.
license: MIT
---

# LemonSlice API reference workflow

Use generated references for exact contracts:

- [`references/endpoint-matrix.md`](references/endpoint-matrix.md)
- [`references/openapi.snapshot.json`](references/openapi.snapshot.json)
- [`references/docs-conflicts.md`](references/docs-conflicts.md)
- [`references/pagination.md`](references/pagination.md)

Run `python lemonslice-api-reference/scripts/sync_openapi.py --check` before relying on volatile fields when internet access is available.

## Endpoint selection

- Self-managed avatar-only sessions: `/liveai/sessions`
- Hosted Pipeline rooms: `/liveai/rooms`
- Runtime controls: `/liveai/sessions/{session_id}/control`
- External meetings: `/liveai/sessions/{session_id}/join-meeting` and `/leave-meeting`

Do not mix endpoint families.

## Alternative selectors

For self-managed JSON creation, validate exactly one of:

- `agent_id`
- `agent_image_url`

Reject both and reject neither. When the schema uses `oneOf`, preserve and implement alternatives rather than combining all required fields.

The current OpenAPI separately declares multipart `image` + `payload`; preserve media types as separate contracts and remove multipart assumptions if a future snapshot no longer declares it.

## Transport validation

Current raw REST values are:

- `livekit`
- `daily`

Do not infer `pipecat`, `agora`, `hosted`, `browser`, or `webrtc` as raw `transport_type` values.

Pipecat is an integration framework and may use Daily underneath. Hosted uses `/liveai/rooms`, not a new self-managed transport value.

## Status handling

Document and handle both endpoint families:

- `GET /liveai/sessions/{session_id}`
- `GET /liveai/rooms/{session_id}`

Handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, and `FAILED`. Do not collapse `QUEUED` into failure.

## Pagination

List endpoints use `page` and `limit`, with `limit` capped at 100, and pagination metadata including `has_more`. Keep exact pagination behavior in [`references/pagination.md`](references/pagination.md).

## Response parsing

Implementation agents must:

1. check HTTP status before trusting the body;
2. parse JSON defensively;
3. preserve redacted non-JSON error bodies in trusted diagnostics;
4. validate exact response fields and types;
5. never confuse Hosted response fields with self-managed response fields;
6. never expose API keys or unrestricted transport credentials to browser code.

## Authentication and response source-of-truth rule

Do not assume one rule for every endpoint or merge conflicting surfaces.

- Create, get, and list session/room endpoints require `X-API-Key`.
- Meeting join and leave endpoints require `X-API-Key`.
- The verified control OpenAPI operation declares `security: []` and includes a `413` response.
- The current rendered control page omits `X-API-Key` and lists `200`, `400`, `404`, and `500`, omitting `413`.

For the control endpoint:

1. keep the call in trusted backend/server code;
2. inspect the current OpenAPI operation and rendered endpoint page;
3. preserve the existing application's known-working authentication behavior;
4. validate required payload fields in application code even when the schema is incomplete;
5. report the conflict instead of asserting an unsupported universal rule.

Never conclude that the endpoint is safely callable from a browser because `security: []` appears in one contract surface.

## Validation workflow

1. Inspect current endpoint docs and OpenAPI.
2. Validate required fields, exactly-one constraints, enums, media types, status codes, and response shapes.
3. Distinguish raw OpenAPI, rendered product documentation, and installed SDK signatures.
4. Use abortable timeouts.
5. Preserve app authorization and ownership.
6. Record docs/version conflicts in the implementation report.

The verified discriminator currently includes `reset-idle-timeout`. Re-check the current operation before adding or removing it because this is a volatile control surface.
