---
name: lemonslice-hosted
description: Create and manage LemonSlice Hosted Pipeline backend sessions. Use this when LemonSlice should manage STT/LLM/TTS/avatar behavior and the developer backend needs to call `POST /api/liveai/rooms`, store `session_id`, validate `room_url`, `token`, `image_url`, poll `GET /api/liveai/rooms/{session_id}`, and return safe Daily join material to a frontend. Do not use for self-managed `/liveai/sessions`, LiveKit, Pipecat, Widget, or frontend Daily UI.
license: MIT
---

# Lemon Slice Hosted Pipeline Backend

## Official docs
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/api-reference/get-hosted-session.md
- https://lemonslice.com/docs/api-reference/list-hosted-sessions.md
- https://lemonslice.com/docs/hosted/endpoint/authentication.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/reference/best-practices.md

## Guardrails
> **Guardrail:** Use only after `lemonslice-integration-choice` has explicitly selected this path.

## Use this skill when
The developer wants Lemon Slice to handle the entire AI pipeline (STT, LLM, TTS, avatar), and the backend needs to create/manage these sessions.

## Do not use this skill when
- The developer is bringing their own STT/LLM/TTS (use `lemonslice-self-managed`, `lemonslice-livekit`, or `lemonslice-pipecat`).
- The developer only wants a simple web widget without a backend (use `lemonslice-widget`).
- You need to build the frontend Daily UI for the hosted session (use `lemonslice-hosted-daily`).

## What Hosted Pipeline means
Hosted Pipeline means LemonSlice manages STT, LLM, TTS, and avatar behavior.
The developer backend creates hosted rooms.
The developer frontend joins the returned Daily room.

## Backend/frontend boundary
The backend creates the hosted session and returns connection credentials to the frontend.
The frontend joins the Daily room.
This skill covers ONLY the backend responsibilities. Frontend Daily joining belongs to `lemonslice-hosted-daily`.

## Environment variables
Required:
```bash
LEMONSLICE_API_KEY=...
```

Rules:
Keep it server-only.
Never expose it to frontend/browser/mobile/public config.
Never log it.
Only use it in backend routes, server functions, workers, or trusted server code.

## Create hosted room API contract
```http
POST https://lemonslice.com/api/liveai/rooms
```

Headers:
```http
X-API-Key: <server-side LemonSlice API key>
Content-Type: application/json
```

Body:
```json
{
  "agent_id": "agent_..."
}
```

Expected response:
```json
{
  "room_url": "...",
  "token": "...",
  "image_url": "...",
  "session_id": "..."
}
```

Do not send unsupported fields unless official docs later verify them. `agent_id` is the required creation field. Use `/api/liveai/rooms`, not `/api/liveai/sessions`.

## Backend wrapper pattern
The app should expose its own backend route, for example:

```http
POST /api/avatar/hosted-rooms
GET /api/avatar/hosted-rooms/:sessionId
```

The backend route should:
1. authenticate the app user if the app has users
2. choose or validate the LemonSlice `agent_id`
3. read `LEMONSLICE_API_KEY` from server-only environment
4. call LemonSlice `POST /api/liveai/rooms`
5. validate the LemonSlice response
6. store session metadata
7. return safe join material to the frontend

```ts
async function createHostedRoomForUser(userId: string, agentId: string) {
  assertAuthorized(userId)

  const res = await fetch("https://lemonslice.com/api/liveai/rooms", {
    method: "POST",
    headers: {
      "X-API-Key": process.env.LEMONSLICE_API_KEY!,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ agent_id: agentId })
  })

  const room = await parseAndValidateHostedRoom(res)

  await storeHostedSession({
    userId,
    agentId,
    sessionId: room.session_id,
    roomUrl: room.room_url,
    imageUrl: room.image_url,
    status: "QUEUED"
  })

  return {
    session_id: room.session_id,
    room_url: room.room_url,
    token: room.token,
    image_url: room.image_url
  }
}
```

## Safe response to frontend
The backend may return:
```json
{
  "session_id": "...",
  "room_url": "...",
  "token": "...",
  "image_url": "...",
  "status": "QUEUED"
}
```

The backend must never return:
LEMONSLICE_API_KEY
server environment variables
internal account-level LemonSlice data
other users’ sessions
raw stack traces

Treat the Daily token as sensitive join material.
Return it only to the authorized frontend that needs to join the room.
Do not log it.
Avoid long-term token storage unless the app truly needs it.

## Session storage
Minimum recommended stored fields:
internal_app_session_id, optional
lemonslice_session_id
agent_id
app_user_id or account_id, if applicable
room_url
image_url
session_status
created_at
updated_at
ended_at, nullable
cost, nullable
llm_started_at, nullable
llm_ended_at, nullable
llm_ended_reason, nullable
messages, optional after completion

The backend must persist the `session_id`. It stores enough metadata to reconcile status later.
Do not log or unnecessarily store the raw Daily token.
Users should only access their own sessions (authorization required).

## Get hosted session status
```http
GET https://lemonslice.com/api/liveai/rooms/{session_id}
```

Headers:
```http
X-API-Key: <server-side LemonSlice API key>
```

Statuses:
QUEUED
ACTIVE
COMPLETED
TIMED_OUT
FAILED

The backend should call this get endpoint when reconciling state.
The backend should update local session storage.
Terminal statuses are: `COMPLETED`, `TIMED_OUT`, `FAILED`.
Do not let the frontend call LemonSlice directly for status.

## Optional: list hosted sessions
Use `GET /api/liveai/rooms` only for backend admin, reconciliation, support, diagnostics, or backfill jobs.
Do not expose a raw account-wide LemonSlice session list directly to frontend users.
Always filter through app ownership and permissions.

## Error handling
Cover likely backend behavior for:
400 invalid request
401 missing/invalid API key
402 insufficient funds
403 unauthorized session/account access
404 agent/session not found
500 LemonSlice/server error
network timeout
invalid response shape

Backend should:
log safe context only
never log API keys
never log raw Daily tokens
return app-level errors to frontend
avoid leaking raw stack traces
mark local session failed when appropriate

## Route next
After the backend returns `room_url` and `token`, use `lemonslice-hosted-daily` for the frontend Daily integration.
Do not put Daily React UI, DailyIframe setup, app-message handling, or bot_ready UI transitions in this backend skill.

## Common mistakes
- Using `/api/liveai/sessions` instead of `/api/liveai/rooms`.
- Treating Hosted Pipeline like Pipecat or LiveKit.
- Exposing `LEMONSLICE_API_KEY` to frontend code.
- Letting frontend call LemonSlice REST APIs directly.
- Sending unsupported create fields instead of only `agent_id`.
- Forgetting to store `session_id`.
- Logging the Daily `token`.
- Treating `room_url` alone as enough without `token`.
- Exposing account-wide hosted session lists to frontend users.
- Putting Daily frontend UI code into this backend skill instead of routing to `lemonslice-hosted-daily`.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` select Hosted?
- [ ] Is this backend code, not frontend Daily UI?
- [ ] Does creation call `POST /api/liveai/rooms`?
- [ ] Is `X-API-Key` used only server-side?
- [ ] Is `agent_id` the required hosted creation field?
- [ ] Are unsupported request fields avoided?
- [ ] Are `room_url`, `token`, `image_url`, and `session_id` validated from the response?
- [ ] Is `session_id` stored?
- [ ] Is the Daily token treated as sensitive?
- [ ] Does the backend return only safe join material?
- [ ] Does status use `GET /api/liveai/rooms/{session_id}`?
- [ ] Are hosted statuses handled: `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED`?
- [ ] Is account/user ownership enforced before returning session data?
- [ ] Are API keys, raw tokens, and stack traces absent from logs and frontend responses?
- [ ] Is frontend Daily implementation routed to `lemonslice-hosted-daily`?
