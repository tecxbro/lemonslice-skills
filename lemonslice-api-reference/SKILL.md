---
name: lemonslice-api-reference
description: Verifies Lemon Slice REST API correctness for backend/server code. Use for base URL, auth, OpenAPI checks, endpoint-family debugging, request/response fields, status polling, list endpoints, and hosted-vs-self-managed API mixups.
license: MIT
---

# Lemon Slice API Reference

## Official docs
- https://lemonslice.com/docs/openapi.json
- https://lemonslice.com/docs/reference/authentication.md
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md
- https://lemonslice.com/docs/api-reference/list-self-managed-sessions.md
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/reference/actions.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/api-reference/get-hosted-session.md
- https://lemonslice.com/docs/api-reference/list-hosted-sessions.md
- https://lemonslice.com/docs/hosted/endpoint/authentication.md

## Use this skill when
- Backend/server code calls Lemon Slice REST APIs directly.
- You need to verify endpoint paths, auth, request fields, response fields, status polling, list endpoints, or OpenAPI behavior.
- The bug may be a mixup between self-managed `/liveai/sessions` and hosted `/liveai/rooms`.

## Do not use this skill when
- Building LiveKit plugin integration.
- Building Pipecat transport integration.
- Building Hosted Daily frontend UI.
- Embedding the Widget.
- Doing production hardening only.
- Choosing an integration path from scratch.

## Core rules
- Base URL: `https://lemonslice.com/api`
- REST calls use `X-API-Key` from trusted backend/server code only.
- Self-managed uses `/liveai/sessions`.
- Hosted uses `/liveai/rooms`.
- Widget metadata uses `/liveai/rooms`.
- Do not mix endpoint families.
- Use OpenAPI as the machine-readable source of truth.
- If OpenAPI and prose docs disagree, report the mismatch instead of inventing fields.

## Reference files
Load only the reference file needed for the task:

- `references/self-managed-endpoints.md` — read when creating, getting, listing, or polling self-managed sessions.
- `references/hosted-endpoints.md` — read when creating, getting, listing, or debugging hosted rooms.
- `references/control-events.md` — read when sending self-managed runtime control events.
- `references/errors-and-statuses.md` — read when handling API errors, terminal statuses, pagination, or response validation.

## Common mistakes
- Using `/liveai/rooms` for self-managed sessions.
- Using `/liveai/sessions` for hosted sessions.
- Calling Lemon Slice REST APIs from frontend code.
- Expecting self-managed create to return `room_url` or `token`.
- Expecting hosted create to accept `transport_type`, `properties`, `agent_image_url`, `livekit_url`, `livekit_token`, `daily_room_url`, `daily_token`, or `simulcast`.
- Inventing `/liveai/rooms/{session_id}/control`.
- Logging API keys or hosted Daily tokens.

## Validation checklist
- [ ] Is the call backend/server-side?
- [ ] Is base URL exactly `https://lemonslice.com/api`?
- [ ] Is `X-API-Key` server-side only?
- [ ] Is the endpoint family correct?
- [ ] Did self-managed use `/liveai/sessions`?
- [ ] Did hosted/widget metadata use `/liveai/rooms`?
- [ ] Did I load only the relevant reference file?
- [ ] Did I avoid inventing undocumented fields?
