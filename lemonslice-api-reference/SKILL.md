---
name: lemonslice-api-reference
description: Use Lemon Slice REST APIs correctly.
license: MIT
---

# Lemon Slice API Reference

> **Guardrail:** Use only after `lemonslice-integration-choice` has explicitly selected this path.

Use this skill when the user or code is directly calling Lemon Slice APIs from backend/server code, especially for endpoint correctness, request/response fields, status polling, list endpoints, OpenAPI validation, and common mixups between self-managed and hosted API families.

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
- The user or code is directly calling Lemon Slice REST APIs from backend/server code.
- You need to verify endpoint correctness, request/response fields, status polling, list endpoints, or OpenAPI validation.
- You need to debug direct Lemon Slice REST API calls or common mixups between self-managed and hosted API families.

## Do not use this skill when
- Implementing frontend Daily UI, LiveKit SDK integration, Pipecat pipeline integration, or Widget embed usage.
- Creating a Lemon Slice product overview or production-hardening-only guide.
- Creating a generic REST tutorial.

## Base URL
```text
https://lemonslice.com/api
```
Endpoint paths are relative to this base URL. For example, `POST /liveai/sessions` means `POST https://lemonslice.com/api/liveai/sessions`.

**Base URL Bugs to Avoid:**
- `https://lemonslice.com/api/api/liveai/sessions` (duplicate `/api`)
- `https://lemonslice.com/liveai/sessions` (missing `/api`)

## Authentication
All REST calls use the following headers (for JSON body requests):
```http
X-API-Key: <server-side LemonSlice API key>
Content-Type: application/json
```

**Security Rules:**
- Keep `LEMONSLICE_API_KEY` server-side only.
- Never call Lemon Slice REST APIs directly from browser/client/mobile code.
- Never expose `X-API-Key` in frontend bundles.
- Never return the Lemon Slice API key to users.
- Never log API keys.
- Treat hosted Daily `token` as sensitive join material.
- Never log hosted Daily tokens.

## Endpoint families
| Family | Path | Meaning |
|---|---|---|
| Self-managed | `/liveai/sessions` | Developer owns STT/LLM/TTS/transport orchestration; Lemon Slice receives agent audio and returns synced avatar A/V. |
| Hosted | `/liveai/rooms` | Lemon Slice manages the AI pipeline; backend creates a hosted Daily room and frontend joins with returned credentials. |

**Warnings:**
- Do not mix `/liveai/sessions` and `/liveai/rooms`.
- Self-managed Daily transport still uses `/liveai/sessions`.
- Hosted Daily rooms use `/liveai/rooms`.
- The word "Daily" alone does not mean Hosted Pipeline.

## OpenAPI spec
https://lemonslice.com/docs/openapi.json

Use the OpenAPI spec as the machine-readable source of truth to verify:
- base URL
- endpoint paths
- request schemas
- response schemas
- required fields
- enum values
- documented error status codes

**Rule:** Do not invent fields if a field is not documented. If prose docs and OpenAPI disagree, report the mismatch instead of inventing an API contract.

## Self-managed endpoints

Self-managed endpoint family: `/liveai/sessions`

### Create self-managed session
**Endpoint:**
```http
POST /liveai/sessions
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/sessions
```
**Headers:**
```http
X-API-Key: <api-key>
Content-Type: application/json
```

**Purpose:**
Creates a self-managed session that takes avatar audio and returns synchronized video/audio.

**Required body fields:**
- `transport_type`
- exactly one of `agent_id` or `agent_image_url`

**Transport properties:**
- For `transport_type: "livekit"`, include `properties.livekit_url` and `properties.livekit_token`.
- For `transport_type: "daily"`, `properties.daily_room_url` and `properties.daily_token` may be supplied. If `daily_room_url` is omitted, Lemon Slice can create a Daily room at additional cost.
- Do not omit `properties` unless the selected transport’s documented behavior allows it.

**Allowed `transport_type` values:**
- `livekit`
- `daily`

**Disallowed invented values:** `webrtc`, `browser`, `hosted`, `room`, `rooms`, `pipecat`, `tavus`

**LiveKit self-managed request example:**
```json
{
  "agent_id": "agent_abc123",
  "transport_type": "livekit",
  "properties": {
    "livekit_url": "wss://example.livekit.cloud",
    "livekit_token": "..."
  }
}
```

**Daily self-managed request example:**
```json
{
  "agent_id": "agent_abc123",
  "transport_type": "daily",
  "properties": {
    "daily_room_url": "https://your-domain.daily.co/your-room",
    "daily_token": "..."
  }
}
```

**Image URL variant example:**
```json
{
  "agent_image_url": "https://example.com/avatar.png",
  "agent_prompt": "a person talking",
  "transport_type": "livekit",
  "properties": {
    "livekit_url": "wss://example.livekit.cloud",
    "livekit_token": "..."
  }
}
```

**Optional fields:**
- `agent_prompt`: high-level speaking-state expression/demeanor guidance.
- `agent_idle_prompt`: affects idle-state expression/demeanor.
- `idle_timeout`: defaults to `60`; negative disables idle timeout.
- `response_done_timeout`: helps when TTS does not emit reliable end-of-response events.
- `simulcast`: LiveKit-only.

**Rules:**
- `agent_id` and `agent_image_url` are mutually exclusive. Never send both. Never send neither.

**Expected response:**
```json
{
  "session_id": "livekit-3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a"
}
```
Self-managed create does not return `room_url`, `token`, or `image_url`. Those are hosted create fields.

### Get self-managed session
**Endpoint:**
```http
GET /liveai/sessions/{session_id}
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/sessions/{session_id}
```
**Headers:**
```http
X-API-Key: <api-key>
```
**Purpose:**
Retrieve current status of a self-managed session.

**Response always includes:**
```json
{
  "session_status": "QUEUED"
}
```

**Allowed status values:**
`QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED`

**Completed response may include:**
```json
{
  "session_status": "COMPLETED",
  "cost": 10
}
```
**Rule:** Rely on `cost` only when `session_status` is `COMPLETED`.

### List self-managed sessions
**Endpoint:**
```http
GET /liveai/sessions
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/sessions
```
**Headers:**
```http
X-API-Key: <api-key>
```
**Purpose:**
Returns paginated self-managed sessions for the authenticated account.

**Query parameters:**
- `page`: integer, default 1, minimum 1
- `limit`: integer, default 25, minimum 1, maximum 100

**Expected response shape:**
```json
{
  "sessions": [
    {
      "session_id": "livekit-3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a",
      "created_at": "2026-04-29T20:34:56.000Z",
      "session_status": "COMPLETED",
      "credits_used": 10.5,
      "provider": "LIVEKIT"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 1,
    "total_pages": 1,
    "has_more": false
  }
}
```
**Rule:** List endpoints should be used for backend admin, support, reconciliation, diagnostics, or backfill. Do not expose raw account-wide Lemon Slice lists directly to end users.

### Control self-managed session
**Endpoint:**
```http
POST /liveai/sessions/{session_id}/control
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/sessions/{session_id}/control
```
**Headers:**
```http
X-API-Key: <api-key>
Content-Type: application/json
```

**Purpose:**
Send a control event to an active self-managed session.

**Success response:**
```json
{
  "success": true
}
```

**Documented event families:** `terminate`, `update-image`, `update-agent-prompt`, `update-idle-prompt`, `pose-trigger`

**Terminate body:**
```json
{
  "event": "terminate"
}
```

**Update image body:**
```json
{
  "event": "update-image",
  "image_url": "https://example.com/avatar.jpg"
}
```

**Update agent prompt body:**
```json
{
  "event": "update-agent-prompt",
  "agent_prompt": "a person talking"
}
```

**Update idle prompt body:**
```json
{
  "event": "update-idle-prompt",
  "idle_prompt": "a serious person"
}
```

**Pose/action trigger body:**
```json
{
  "event": "pose-trigger",
  "pose_trigger": {
    "name": "<ACTION_NAME>"
  }
}
```

**Rules:**
- The REST control endpoint is self-managed only.
- Do not invent `POST /liveai/rooms/{session_id}/control`.
- Action triggers must be supported/onboarded for the target avatar. Verify the current actions documentation before relying on a specific action name.
- Wait until avatar/session readiness before sending actions.
- Avoid overlapping action triggers unless the app has an action dispatcher.
- Image update resets the model and may interrupt currently playing audio.
- Image URL must be publicly accessible.

## Hosted endpoints

Hosted endpoint family: `/liveai/rooms`

Hosted Pipeline means Lemon Slice manages the AI pipeline. The backend creates a hosted room, and the frontend joins the returned Daily room.

### Create hosted session
**Endpoint:**
```http
POST /liveai/rooms
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/rooms
```
**Headers:**
```http
X-API-Key: <api-key>
Content-Type: application/json
```

**Required body:**
```json
{
  "agent_id": "agent_abc123"
}
```
**Rule:** Do not send self-managed fields here (`transport_type`, `properties`, `agent_image_url`, `livekit_url`, `livekit_token`, `daily_room_url`, `daily_token`, `simulcast`).

**Expected response:**
```json
{
  "room_url": "https://lemonslice.daily.co/abc123",
  "token": "eyJhbGciOiJIUzI1NiIsInR5a...",
  "image_url": "https://cdn.lemonslice.com/agents/agent_abc123.png",
  "session_id": "3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a"
}
```

**Security rules:**
- Treat `token` as sensitive Daily join material.
- Return it only to the authorized frontend that needs to join the room.
- Do not log it.
- Avoid long-term token storage unless required.

### Get hosted session
**Endpoint:**
```http
GET /liveai/rooms/{session_id}
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/rooms/{session_id}
```
**Headers:**
```http
X-API-Key: <api-key>
```
**Purpose:**
Retrieve current status of a hosted session.

**Path parameter:**
`session_id` - Use the `session_id` returned by `POST /liveai/rooms`.

**Naming note:** The prose docs call this path parameter `session_id`; the OpenAPI spec may label the same path parameter as `room_id`. Use the `session_id` returned by `POST /liveai/rooms`, not the Daily room URL or room slug.

**Do not use:** Daily room slug, full room_url, or self-managed session_id from `/liveai/sessions`.

**Basic response:**
```json
{
  "session_status": "QUEUED"
}
```

**Allowed status values:**
`QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED`

**Completed hosted response may include:**
```json
{
  "session_status": "COMPLETED",
  "cost": 10,
  "llm_ended_reason": "Client disconnected: 1000",
  "llm_started_at": 1772746376,
  "llm_ended_at": 1772746535,
  "messages": [
    {
      "role": "user",
      "message": "hello",
      "seconds_from_start": 0
    },
    {
      "role": "agent",
      "message": "Hello! How can I assist you today?",
      "seconds_from_start": 10
    }
  ]
}
```
**Rule:** Hosted get may include more completion metadata than self-managed get (`cost`, `llm_ended_reason`, `llm_started_at`, `llm_ended_at`, `messages`). Only rely on these completion fields when `session_status` is `COMPLETED`.

### List hosted sessions
**Endpoint:**
```http
GET /liveai/rooms
```
**Full URL:**
```text
https://lemonslice.com/api/liveai/rooms
```
**Headers:**
```http
X-API-Key: <api-key>
```
**Purpose:**
Returns paginated hosted sessions for the authenticated account.

**Query parameters:**
- `page`: integer, default 1, minimum 1
- `limit`: integer, default 25, minimum 1, maximum 100

**Expected response shape:**
```json
{
  "rooms": [
    {
      "agent_id": "agent_abc123",
      "session_id": "3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a",
      "created_at": "2026-04-29T20:34:56.000Z",
      "session_status": "COMPLETED",
      "credits_used": 10.5
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 1,
    "total_pages": 1,
    "has_more": false
  }
}
```
**Rule:** Hosted list endpoints should be used for backend admin, support, reconciliation, diagnostics, or backfill. Do not expose raw account-wide Lemon Slice room lists directly to end users.

## Status handling
For both hosted and self-managed sessions, handle these statuses:
`QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED`

**Guidance:**
- `QUEUED`: session is waiting for GPU capacity.
- `ACTIVE`: avatar/session is live.
- `COMPLETED`: successful terminal state.
- `TIMED_OUT`: terminal timeout state.
- `FAILED`: terminal failure state.

**Terminal statuses:** `COMPLETED`, `TIMED_OUT`, `FAILED`

**Warning:** Do not assume only `ACTIVE` and `COMPLETED` exist.

## Error handling
Backend handling is required for:
- 400 invalid request or missing required fields
- 401 missing/invalid API key
- 402 insufficient funds
- 403 unauthorized account/session/agent access
- 404 agent/session/room not found
- 500 Lemon Slice/server error
- network timeout
- invalid response shape

**Backend behavior:**
- Validate Lemon Slice response shape before trusting it.
- Log safe context only.
- Never log API keys.
- Never log hosted Daily tokens.
- Never leak raw stack traces to frontend.
- Convert Lemon Slice API errors into app-level errors.
- Persist enough local state to reconcile sessions later.

## Common endpoint mixups

### Mistake 1: Using hosted rooms for self-managed
- **Wrong:** `POST /liveai/rooms` when the developer owns STT/LLM/TTS.
- **Correct:** `POST /liveai/sessions`

### Mistake 2: Using self-managed sessions for Hosted Pipeline
- **Wrong:** `POST /liveai/sessions` when Lemon Slice should manage STT/LLM/TTS and return Daily credentials.
- **Correct:** `POST /liveai/rooms`

### Mistake 3: Treating self-managed Daily as Hosted Daily
- **Wrong assumption:** `transport_type: "daily"` means Hosted Pipeline.
- **Correct:** `transport_type: "daily"` inside `POST /liveai/sessions` is still self-managed.

### Mistake 4: Expecting hosted fields from self-managed create
- **Wrong expectation from `POST /liveai/sessions`:** `{"room_url": "...", "token": "...", "image_url": "...", "session_id": "..."}`
- **Correct self-managed response:** `{"session_id": "..."}`

### Mistake 5: Sending self-managed body to hosted create
- **Wrong body for `POST /liveai/rooms`:** `{"transport_type": "livekit", "properties": {"livekit_url": "...", "livekit_token": "..."}}`
- **Correct hosted body:** `{"agent_id": "agent_abc123"}`

### Mistake 6: Using Daily room URL as hosted status ID
- **Wrong:** `GET /liveai/rooms/https://lemonslice.daily.co/abc123`
- **Correct:** `GET /liveai/rooms/{session_id}` (Use the `session_id` returned by hosted create)

### Mistake 7: Inventing hosted control endpoint
- **Wrong invented endpoint:** `POST /liveai/rooms/{session_id}/control`
- **Correct documented REST control endpoint:** `POST /liveai/sessions/{session_id}/control`
- Hosted Daily hang-up/control patterns belong in `lemonslice-hosted-daily` or `lemonslice-control-actions`, depending on selected path.

### Mistake 8: Calling Lemon Slice REST from frontend
- **Wrong:** browser fetch to Lemon Slice with `X-API-Key`, mobile app containing `LEMONSLICE_API_KEY`, public Next.js client component calling Lemon Slice directly.
- **Correct:** frontend calls your backend, backend calls Lemon Slice with `X-API-Key`, backend returns only safe app/session/join data.

## Agent workflow
1. Confirm `lemonslice-integration-choice` selected API reference/raw REST.
2. Identify endpoint family:
   - `/liveai/sessions` for self-managed
   - `/liveai/rooms` for hosted
3. Confirm the call is backend/server-side.
4. Confirm base URL and auth.
5. Validate request body fields against the selected endpoint.
6. Validate response expectations against the selected endpoint.
7. Check status handling.
8. Check list pagination if list endpoints are used.
9. Check control event body if control endpoint is used.
10. Flag common endpoint mixups.
11. Route elsewhere if the task is actually LiveKit, Pipecat, Widget, Hosted Daily frontend, or production hardening.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` select raw API/reference work?
- [ ] Is the code calling Lemon Slice from trusted backend/server code only?
- [ ] Is the base URL exactly `https://lemonslice.com/api`?
- [ ] Are endpoint paths appended without duplicating `/api`?
- [ ] Is `X-API-Key` used server-side?
- [ ] Is `Content-Type: application/json` set for JSON bodies?
- [ ] Is self-managed using `/liveai/sessions`?
- [ ] Is hosted using `/liveai/rooms`?
- [ ] Does self-managed create provide exactly one of `agent_id` or `agent_image_url`?
- [ ] Does self-managed create include `transport_type` as only `livekit` or `daily`?
- [ ] Does self-managed create include the correct `properties` for LiveKit or Daily?
- [ ] Does self-managed create expect only `session_id`?
- [ ] Does hosted create send only the documented `agent_id` body?
- [ ] Does hosted create validate `room_url`, `token`, `image_url`, and `session_id`?
- [ ] Does get/status handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, and `FAILED`?
- [ ] Does self-managed get treat `cost` as completion-only?
- [ ] Does hosted get treat `cost`, timestamps, end reason, and messages as completion-only?
- [ ] Do list calls use `page` and `limit` safely?
- [ ] Are list responses kept backend/admin-scoped instead of exposed raw to users?
- [ ] Does control use `/liveai/sessions/{session_id}/control`, not `/liveai/rooms/{session_id}/control`?
- [ ] Are control event bodies limited to documented event shapes?
- [ ] Are API keys, hosted Daily tokens, and stack traces excluded from logs and frontend responses?
- [ ] Did the answer avoid becoming a LiveKit/Pipecat/Widget/Hosted-Daily implementation guide?
