# Backend Room Contract

## Contents
- Create hosted room contract
- Backend wrapper pattern
- Safe response to frontend
- Session storage fields
- Get hosted status
- List hosted sessions
- Error handling

## Create hosted room contract
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

## Session storage fields
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

## Get hosted status
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

## List hosted sessions
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
