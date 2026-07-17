---
name: lemonslice-api-reference
description: Select and validate LemonSlice REST endpoints, inspect current OpenAPI evidence, handle authentication and CDN-source conflicts, and avoid duplicating volatile schemas in skill prose.
license: MIT
---

# LemonSlice API reference workflow

Use generated references for exact contracts:

- [`references/endpoint-matrix.md`](references/endpoint-matrix.md)
- [`references/openapi.snapshot.json`](references/openapi.snapshot.json)
- [`references/docs-conflicts.md`](references/docs-conflicts.md)
- [`references/pagination.md`](references/pagination.md)

Run the source probe before relying on volatile fields when internet access is available:

```bash
python lemonslice-api-reference/scripts/sync_openapi.py \
  --download-sources \
  --source-dir artifacts/sources \
  --probe-count 3
```

If normalized probes conflict, stop and report source inconsistency. Do not choose one edge response automatically.

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

Multipart support, raw model fields, and other media types are volatile observations. Use them only when the stable captured OpenAPI explicitly exposes them.

## Transport validation

Observed raw REST values are:

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

List endpoints have been observed with `page` and `limit`, including a `limit` maximum of 100 and pagination metadata such as `has_more`. Treat the generated parameter contract as authoritative for the captured source and keep explanatory guidance in [`references/pagination.md`](references/pagination.md).

## Response parsing

Implementation agents must:

1. check HTTP status before trusting the body;
2. parse JSON defensively;
3. preserve redacted non-JSON error bodies in trusted diagnostics;
4. validate exact response fields, types, enums, nullability, and content types;
5. never confuse Hosted response fields with self-managed response fields;
6. never expose API keys or unrestricted transport credentials to browser code.

The normalizer tracks required path/query parameters, request-body alternatives, media types, response-body schemas, required response fields, enum changes, defaults, bounds, formats, and nullable types.

## Authentication and response source-of-truth rule

Do not assume one rule for every endpoint or merge conflicting surfaces.

- Create, get, and list session/room endpoints require `X-API-Key` in observed contracts.
- Meeting join and leave endpoints require `X-API-Key` in observed contracts.
- Control endpoint observations disagree on `401` versus `413`, optional idle-reset support, and other details while `security: []` has appeared.

For the control endpoint:

1. keep the call in trusted backend/server code;
2. inspect the captured OpenAPI probes and rendered endpoint page;
3. preserve the existing application's known-working authentication behavior;
4. validate required payload fields in application code even when one schema is incomplete;
5. report the conflict instead of asserting an unsupported universal rule.

Never conclude that the endpoint is safely callable from a browser because `security: []` appears in one contract surface.

## Validation workflow

1. Probe the public sources repeatedly and record source metadata.
2. Stop with a source-inconsistent result when normalized contracts differ.
3. Reuse the same saved source files for snapshot generation and drift comparison.
4. Validate required fields, exactly-one constraints, enums, parameters, media types, status codes, and response schemas.
5. Distinguish raw OpenAPI, rendered product documentation, and installed SDK signatures.
6. Use abortable timeouts.
7. Preserve app authorization and ownership.
8. Record docs/version conflicts in the implementation report.

See [`references/docs-conflicts.md`](references/docs-conflicts.md) for volatile control, multipart, and model-surface observations.
