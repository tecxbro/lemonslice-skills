---
name: lemonslice-hosted
description: Create and manage Lemon Slice hosted backend sessions.
license: MIT
---

# Lemon Slice Hosted Pipeline Backend

## Official docs
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/api-reference/get-hosted-session.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md

## Use this skill when
The developer wants Lemon Slice to handle the entire AI pipeline (STT, LLM, TTS, avatar), and the backend needs to create/manage these sessions.

## Do not use this skill when
- The developer is bringing their own STT/LLM/TTS (use `lemonslice-self-managed`, `lemonslice-livekit`, or `lemonslice-pipecat`).
- The developer only wants a simple web widget without a backend (use `lemonslice-widget`).
- You need to build the frontend Daily UI for the hosted session (use `lemonslice-hosted-daily`).

## Hosted meaning
Hosted Pipeline means LemonSlice manages STT, LLM, TTS, and avatar behavior.
The developer backend creates hosted rooms.
The developer frontend joins the returned Daily room.

## Backend/frontend boundary
The backend creates the hosted session and returns connection credentials to the frontend.
The frontend joins the Daily room.
This skill covers ONLY the backend responsibilities. Frontend Daily joining belongs to `lemonslice-hosted-daily`.

## Environment variables and Security
Required:
```bash
LEMONSLICE_API_KEY=...
```

Rules:
Keep it server-only.
Never expose it to frontend/browser/mobile/public config.
Never log it.
Only use it in backend routes, server functions, workers, or trusted server code.

## Create room summary
- `POST /api/liveai/rooms`
- `agent_id` is required
- returns `room_url`, `token`, `image_url`, `session_id`

## Route next
After the backend returns `room_url` and `token`, use `lemonslice-hosted-daily` for the frontend Daily integration.
Do not put Daily React UI, DailyIframe setup, app-message handling, or bot_ready UI transitions in this backend skill.

## Reference files
Load only the reference file needed for the task:

- `references/backend-room-contract.md` — read for full API contract, backend wrapper example, session storage fields, status polling, and error handling.

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
