---
name: lemonslice-hosted-daily
description: Build a Daily frontend for hosted Lemon Slice sessions.
license: MIT
---

# Lemon Slice Hosted Daily Frontend

## Official docs
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/examples/hosted-daily-app.md
- https://lemonslice.com/docs/reference/best-practices.md
- https://docs.daily.co/reference/daily-js/instance-methods/join
- https://docs.daily.co/reference/daily-js/instance-methods/leave
- https://docs.daily.co/reference/daily-js/instance-methods/destroy
- https://docs.daily.co/reference/daily-react/use-daily-event

## Guardrails
> **Guardrail:** Use only after `lemonslice-integration-choice` has explicitly selected this path.

This skill assumes the hosted backend already exists or is being implemented separately through `lemonslice-hosted`.

## Use this skill when
Use this skill when the developer is building a custom React, Next.js, or browser frontend for LemonSlice Hosted Pipeline, and the app backend already creates hosted sessions and returns Daily join material.

Use this skill when the frontend receives:

- `room_url`
- `token`
- optional `image_url`
- optional `session_id`

This skill is specifically for custom frontend UI with LemonSlice-hosted backend behavior.

## Do not use this skill when
- You are creating hosted rooms on the backend. Use `lemonslice-hosted`.
- You are using LiveKit Agents. Use `lemonslice-livekit`.
- You are using Pipecat. Use `lemonslice-pipecat`.
- You are using LemonSlice as a self-managed avatar/video layer. Use `lemonslice-self-managed`.
- You want a no-backend embed. Use `lemonslice-widget`.
- You are debugging raw LemonSlice REST endpoints. Use `lemonslice-api-reference`.
- You are only adding runtime controls/actions to an already-selected path. Use `lemonslice-control-actions`.

## What this skill builds
This skill builds the React/Next.js frontend Daily client for Hosted Pipeline sessions. It handles Daily room joining, event tracking, state transitions, error handling, and cleanup for LemonSlice avatars.

## Backend/frontend boundary
The frontend must request session credentials from the developer’s backend.

The frontend MUST NOT call LemonSlice REST APIs directly.

Correct frontend flow:

1. Frontend calls app backend, for example `POST /api/avatar/hosted-rooms`.
2. App backend authenticates the user.
3. App backend calls LemonSlice with server-only `LEMONSLICE_API_KEY`.
4. App backend returns safe Daily join material to the frontend.
5. Frontend joins Daily with `room_url` and `token`.

Forbidden in frontend/browser code:

- `LEMONSLICE_API_KEY`
- `X-API-Key`
- direct `fetch("https://lemonslice.com/api/liveai/rooms")`
- direct LemonSlice session creation
- logging raw Daily tokens

## Frontend credential contract
The frontend should receive a safe response from the app backend:

```json
{
  "session_id": "...",
  "room_url": "...",
  "token": "...",
  "image_url": "...",
  "status": "QUEUED"
}
```

Required frontend fields:

* `room_url`: Daily room URL to join
* `token`: Daily meeting token

Useful optional fields:

* `session_id`: app/backend tracking, support, analytics, cleanup
* `image_url`: display placeholder/avatar image while connecting
* `status`: initial backend-known state, usually `QUEUED`

Treat `token` as sensitive join material:

* do not log it
* do not expose it in analytics
* do not persist it longer than necessary
* do not reuse it after session failure/end unless backend explicitly says reuse is safe

## Daily client setup
Use `@daily-co/daily-js` or `@daily-co/daily-react` for your implementation. Ensure you create or reuse a single Daily call object to manage the meeting. Keep Daily UI strictly client-side.

## Daily join flow
Recommended flow:

1. User clicks Start.
2. Set UI state to `creating_room`.
3. Call the app backend to create/get hosted Daily credentials.
4. Validate that backend returned `room_url` and `token`.
5. Create or reuse a Daily call object.
6. Call Daily join with the returned `room_url` and `token`.
7. Set UI state to `joining_daily` while the Daily join is in progress.
8. After Daily join succeeds, set UI state to `waiting_for_bot`.
9. Start a startup timeout while waiting for `bot_ready`.
10. Transition to `active` only when LemonSlice sends `bot_ready` via `app-message`.

Important: Daily join success only means the browser joined the Daily room. It does not mean the LemonSlice avatar is ready. The avatar readiness signal is `bot_ready`.

## Readiness model
Do not treat these as active-call readiness:

- backend room creation success
- receiving `room_url`
- Daily `joined-meeting`
- participant join alone
- first remote media track alone

Use `bot_ready` as the readiness signal.

When `bot_ready` arrives:

- clear startup timeout
- set state to `active`
- enable text input / microphone UI / call controls
- hide loading spinner
- show the avatar as ready

## App-message event model
LemonSlice Hosted Daily events arrive through Daily `app-message`.

The frontend should listen for `app-message` and parse the message defensively.

Required events to handle:

### `bot_ready`

Meaning: LemonSlice avatar/bot is ready.

Required behavior:

- clear startup timeout
- transition `waiting_for_bot` -> `active`
- show active call UI

### `idle_timeout`

Meaning: the session ended because of inactivity.

Required behavior:

- transition to `ended`
- leave the Daily room if still connected
- clear timers
- show restart/retry UI

### `daily_error`

Meaning: Daily/hosted pipeline error.

Required behavior:

- read fields defensively, for example `error`, `err_msg`, `message`, `fatal`
- if fatal or during startup, leave room and transition to `retryable_failed`
- show user-visible retry UI
- do not expose raw stack traces

### `video_generation_error`

Meaning: avatar video generation failed.

Required behavior:

- transition to `retryable_failed` unless app has a documented recovery path
- leave room or disable call controls
- show user-visible error
- offer retry by creating a fresh room through backend

Optional events to surface:

- `user_transcription`
- `agent_transcription`
- image or appearance update events if the app supports them

## Required state machine
Recommended states:

- `idle`
- `creating_room`
- `joining_daily`
- `waiting_for_bot`
- `active`
- `ending`
- `ended`
- `retryable_failed`
- `failed`

Recommended transitions:

| From | Trigger | To | Required behavior |
| --- | --- | --- | --- |
| `idle` | user clicks start | `creating_room` | disable start button, show loading |
| `creating_room` | backend returns room credentials | `joining_daily` | validate `room_url` and `token` |
| `creating_room` | backend error | `retryable_failed` | show retry UI |
| `joining_daily` | Daily join resolves | `waiting_for_bot` | start startup timeout |
| `joining_daily` | Daily join fails | `retryable_failed` | leave/destroy call object if needed |
| `waiting_for_bot` | `bot_ready` | `active` | clear startup timeout |
| `waiting_for_bot` | startup timeout | `retryable_failed` | leave room, show retry UI |
| `waiting_for_bot` | fatal `daily_error` | `retryable_failed` | leave room, show retry UI |
| `active` | user hangs up | `ending` | send `force-end` if appropriate, then leave |
| `active` | `idle_timeout` | `ended` | cleanup and show restart UI |
| `active` | bot participant leaves unexpectedly | `retryable_failed` | cleanup and show retry UI |
| `active` | `video_generation_error` | `retryable_failed` | cleanup or disable call UI |
| `ending` | Daily leave completes | `ended` | clear local state |
| `retryable_failed` | user retries | `creating_room` | create a fresh hosted room |

## Startup timeout and retry UI
The frontend must not wait forever for `bot_ready`.

Recommended behavior:

1. Start a timer after Daily join succeeds and state becomes `waiting_for_bot`.
2. Use a clear threshold, for example 30 seconds, unless the app has a product-specific value.
3. If `bot_ready` arrives before timeout:
   - clear timer
   - transition to `active`
4. If timeout fires:
   - call Daily `leave()`
   - clear timer
   - clear local room credentials
   - transition to `retryable_failed`
   - show retry UI

Retry behavior:

- Retry should call the app backend again.
- Backend should create a fresh hosted room or return fresh credentials.
- Do not blindly reuse stale `room_url` and `token`.

## Participant leave and cleanup
The frontend must handle Daily participant and room lifecycle events.

Handle:

- `participant-left`
- `left-meeting`
- Daily top-level `error`

Required behavior:

- If the local user leaves, cleanup and move to `ended`.
- If the LemonSlice bot/agent leaves, move to `ended` or `retryable_failed` depending on whether this was expected.
- Do not assume every `participant-left` event is the bot.
- Track the bot participant if the app can identify it.
- Always clear startup timeout and retry timers.
- Always clear stale `room_url` and `token` after terminal states.

Clean up timers and stale credentials in these scenarios:
- on hangup
- on idle timeout
- on fatal error
- on startup timeout
- on participant leave
- on component unmount

## Sending app messages to the hosted agent
Use Daily app messages for hosted-agent controls and chat.

Supported guidance:

### Send user text

Use `chat-msg` when the user sends text to the hosted agent.

Shape:

```ts
callObject.sendAppMessage(
  {
    event: "chat-msg",
    message: userText
  },
  "*"
)
```

### End session

Use `force-end` when the user intentionally ends the hosted session.

Shape:

```ts
callObject.sendAppMessage(
  {
    event: "force-end"
  },
  "*"
)
```

After sending `force-end`, the frontend should still run local cleanup:

* disable controls
* transition to `ending`
* call `leave()`
* clear timers
* clear stale credentials

### Appearance/image updates

Only document `/imagine ...` through `chat-msg` if the app is intentionally allowing runtime image modification.

Do not invent unsupported app-message events.

## React/Next.js implementation guidance
For Next.js App Router:

- Put Daily room UI in a client component.
- Use `"use client"` for components that use Daily, browser media APIs, or React hooks tied to the call object.
- Keep hosted room creation in a server route, route handler, server action, or external backend.
- Do not place `LEMONSLICE_API_KEY` in public env vars such as `NEXT_PUBLIC_*`.
- Do not call LemonSlice directly from client components.

Recommended frontend modules:

- `HostedDailyRoom.tsx`: client component for Daily room UI
- `useHostedDailySession.ts`: hook that owns state machine, join, event handlers, cleanup
- `app/api/.../route.ts` or backend route: creates hosted room through `lemonslice-hosted`

Recommended hook responsibilities:

- store current state
- request credentials from backend
- create Daily call object
- join Daily
- register event listeners (memoize event callbacks when using Daily React hooks)
- start/clear startup timeout
- send app messages
- leave/destroy on cleanup

## Error handling requirements
The frontend must handle these failures:

### Backend room creation failure

Examples:

- unauthorized user
- backend validation error
- LemonSlice API error hidden behind app backend
- network timeout

Frontend behavior:

- transition `creating_room` -> `retryable_failed`
- show retry UI
- do not expose raw backend stack traces

### Daily join failure

Frontend behavior:

- transition `joining_daily` -> `retryable_failed`
- leave/destroy call object if partially initialized
- show retry UI

### Missing `bot_ready`

Frontend behavior:

- startup timeout fires
- call `leave()`
- transition to `retryable_failed`
- retry creates a fresh hosted room

### `daily_error`

Frontend behavior:

- parse defensively
- fatal errors become `retryable_failed`
- nonfatal errors may become a toast or warning

### `video_generation_error`

Frontend behavior:

- treat as avatar generation failure
- show retry UI
- cleanup stale call/session state

### `idle_timeout`

Frontend behavior:

- treat as normal ended session
- cleanup
- show restart UI

### Participant leave

Frontend behavior:

- distinguish local user leave, bot leave, and unrelated participant leave when possible
- cleanup if bot leaves unexpectedly

## Common mistakes
- Calling LemonSlice REST APIs directly from React/browser code.
- Putting `LEMONSLICE_API_KEY` in `NEXT_PUBLIC_*` or any frontend env var.
- Logging the Daily `token`.
- Treating Daily join success as avatar readiness.
- Treating participant join as readiness instead of `bot_ready`.
- Forgetting to listen to `app-message`.
- Forgetting startup timeout when `bot_ready` never arrives.
- Retrying with stale `room_url` / `token`.
- Not cleaning up on `participant-left`.
- Not calling `leave()` on failure, timeout, or component unmount.
- Forgetting to send `force-end` for intentional user hangup when appropriate.
- Building backend room creation inside this skill instead of routing to `lemonslice-hosted`.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` select Hosted Daily?
- [ ] Is this frontend Daily UI work, not hosted backend creation?
- [ ] Does the frontend receive `room_url` and `token` from the app backend?
- [ ] Does the frontend avoid direct LemonSlice REST API calls?
- [ ] Is `LEMONSLICE_API_KEY` absent from all frontend/browser/public env code?
- [ ] Is the Daily `token` treated as sensitive join material?
- [ ] Does the frontend join Daily with `room_url` and `token`?
- [ ] Does UI wait for `bot_ready` before entering `active`?
- [ ] Are LemonSlice events handled through `app-message`?
- [ ] Are `idle_timeout`, `daily_error`, and `video_generation_error` handled?
- [ ] Is `participant-left` handled with cleanup logic?
- [ ] Is there a startup timeout if `bot_ready` never arrives?
- [ ] Does timeout call `leave()` and show retry UI?
- [ ] Does retry create/request fresh credentials instead of blindly reusing stale ones?
- [ ] Is there a clear state machine?
- [ ] Does user hangup run cleanup and send `force-end` where appropriate?
- [ ] Are timers cleared on success, failure, hangup, and component unmount?
- [ ] Does React/Next.js code keep Daily UI client-side and room creation server-side?
