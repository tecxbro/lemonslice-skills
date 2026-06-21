---
name: lemonslice-production-patterns
description: "Production-readiness checklist for Lemon Slice integrations after the feature works."
license: MIT
---

# Lemon Slice Production Patterns

## Official docs

- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/reference/best-practices.md
- https://lemonslice.com/docs/reference/authentication.md
- https://lemonslice.com/docs/reference/overview.md
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/api-reference/get-hosted-session.md
- https://lemonslice.com/docs/openapi.json

## Use this skill when

Use this skill after a Lemon Slice integration already works and needs production hardening.

Use it for:
- API key safety
- backend/frontend separation
- readiness and `bot_ready`
- startup timeout
- idle timeout
- GPU timeout
- cleanup and explicit session termination
- Daily disconnect handling
- LiveKit disconnect handling
- Pipecat pipeline error handling
- latency budgeting
- STT/LLM/TTS optimization
- logging and observability

This is usually a **secondary skill**, matching the router’s production-hardening route. The router already routes security, latency, reliability, deployment, cleanup, timeouts, `bot_ready`, disconnects, and error handling to this skill.

## Do not use this skill when

Do not use this skill to build the first working integration.

Route first to:
- `lemonslice-livekit` for LiveKit Agents
- `lemonslice-pipecat` for Pipecat pipelines
- `lemonslice-hosted` for hosted backend session creation
- `lemonslice-hosted-daily` for frontend Daily room joining
- `lemonslice-self-managed` for raw self-managed session setup
- `lemonslice-api-reference` for endpoint correctness
- `lemonslice-control-actions` for runtime actions, image updates, prompt updates, and termination details

This skill audits production readiness after the selected path works.

## What production-ready means

A Lemon Slice integration is production-ready when:
- credentials are server-only
- frontend only receives safe session/join material
- avatar readiness waits for `bot_ready`
- startup cannot hang forever
- idle/GPU/provider timeouts are understood
- cleanup runs on all terminal paths
- disconnects and provider errors are handled
- latency is measured across STT, LLM, TTS, and avatar generation
- logs support debugging without leaking secrets

## Agent workflow

1. Confirm the selected integration path.
   - Inspect repo evidence.
   - Identify LiveKit, Pipecat, Hosted backend, Hosted Daily frontend, Self-managed/API, Widget, or Control Actions.
   - Do not treat the word “Daily” as automatically Hosted Daily.

2. Audit credentials.
   - `LEMONSLICE_API_KEY` must exist only in backend, agent, worker, or server environment.
   - Browser/client/mobile code must never contain `LEMONSLICE_API_KEY` or `X-API-Key`.
   - Do not log API keys, Daily tokens, LiveKit tokens, room credentials, or raw stack traces.

3. Audit readiness.
   - Do not treat session creation, room join, participant join, or first media track as avatar readiness.
   - Wait for `bot_ready`.
   - Add startup timeout if `bot_ready` never arrives.
   - On timeout, clean up and expose retry.

4. Audit lifecycle.
   - Cleanup must run on user hangup, startup timeout, idle timeout, fatal error, participant leave, Daily disconnect, LiveKit disconnect, Pipecat task cancellation, deployment shutdown, and process shutdown.

5. Audit timeouts.
   - Check startup timeout.
   - Check LemonSlice idle timeout.
   - Check GPU timeout.
   - Check third-party provider timeouts.

6. Audit latency.
   - Measure STT, LLM, TTS, avatar generation, and network separately.
   - Do not invent hard FPS or response-time guarantees.

7. Audit observability.
   - Log safe session IDs, status transitions, time to `bot_ready`, timeout reason, disconnect reason, retry count, and terminal state.
   - Redact all credentials.

## Security and credential boundaries

Rules:
- Keep `LEMONSLICE_API_KEY` server-only.
- Use `X-API-Key` only from trusted backend/server/agent code.
- Never put `LEMONSLICE_API_KEY` in frontend env vars.
- Never use `NEXT_PUBLIC_LEMONSLICE_API_KEY`.
- Never call LemonSlice REST APIs directly from browser/client/mobile code.
- Never return the LemonSlice API key to frontend code.
- Never log API keys.
- Treat hosted Daily `token`, LiveKit tokens, Daily tokens, and room credentials as sensitive join material.

## Backend/frontend separation

Backend responsibilities:
- authenticate/authorize app user
- call LemonSlice APIs with server-only `LEMONSLICE_API_KEY`
- validate LemonSlice responses
- store `session_id` and safe metadata
- return only safe session/join material to frontend
- reconcile terminal statuses where needed

Frontend responsibilities:
- call app backend, not LemonSlice directly
- join LiveKit/Daily only with safe credentials returned by backend
- listen for readiness/error/disconnect events
- clear timers and credentials on terminal states
- show retry UI when startup or runtime fails

## Readiness and startup timeout

Do not mark the avatar active until `bot_ready`.

Not enough:
- backend session created
- `session_id` returned
- hosted `room_url` / `token` returned
- LiveKit room connected
- Daily join succeeded
- participant joined
- first media track appeared

Required behavior:
- start in loading / waiting state
- listen for `bot_ready`
- clear startup timer when `bot_ready` arrives
- transition to active only after `bot_ready`
- if timeout fires, leave/disconnect room, terminate where supported, clear local state, and show retry

## Timeout checklist

Startup timeout:
- app-defined
- starts when waiting for avatar readiness
- failure path must clean up and show retry

Idle timeout:
- default is 60 seconds where documented
- negative idle timeout disables idle timeout
- do not rely on idle timeout as the only cleanup mechanism

GPU timeout:
- default is 30 minutes where documented
- do not assume sessions can run forever

Third-party timeouts:
- LiveKit room/session limits
- Daily room/session behavior
- STT provider timeout
- LLM provider timeout
- TTS provider timeout
- hosting/serverless execution timeout

## Cleanup and termination

Cleanup triggers:
- normal user hangup
- frontend component unmount
- startup timeout
- `bot_ready` never arrives
- `idle_timeout`
- fatal `daily_error`
- `video_generation_error`
- participant leaves unexpectedly
- Daily/WebRTC disconnect
- LiveKit room disconnect
- Pipecat task cancellation
- STT/LLM/TTS failure
- backend request timeout
- process signal
- deployment shutdown

Cleanup actions:
- stop accepting user input
- clear timers
- leave/disconnect Daily or LiveKit room where applicable
- cancel agent/pipeline task where applicable
- close async HTTP/session resources
- clear stale room credentials/tokens
- mark local session terminal or retryable
- explicitly terminate LemonSlice session where the selected path supports it

## Path-specific production checks

### LiveKit

Check:
- `LEMONSLICE_API_KEY` is only in the LiveKit agent/server environment.
- The app waits for `bot_ready`, not participant join.
- The app handles LemonSlice data-channel events:
  - `bot_ready`
  - `idle_timeout`
  - `error`
  - `video_generation_error`
  - `metric`
- The app handles LiveKit disconnect paths:
  - room disconnect
  - participant disconnect
  - agent shutdown
  - process/deployment shutdown
- The app handles AgentSession provider failures:
  - STT failure
  - LLM failure
  - TTS failure
- Metrics are recorded safely:
  - `time_to_first_push`
  - `tts_audio_delay`
- Cleanup uses the correct shutdown path:
  - `ctx.room.disconnect()` when ending the room connection
  - `ctx.shutdown()` when stopping the Agent JobContext
  - self-managed `terminate` when stopping only LemonSlice avatar generation

### Pipecat

Check:
- `LEMONSLICE_API_KEY` is only in the Pipecat bot/server environment.
- `LemonSliceTransport` is used inside the Pipecat pipeline.
- Daily appearing in the project is not automatically Hosted Daily.
- The participant model is correct:
  - human user
  - Pipecat bot participant
  - LemonSlice avatar participant
- The UI does not show the Pipecat bot participant as the avatar.
- The implementation handles:
  - `bot_ready` where available
  - `idle_timeout`
  - `daily_error`
  - `video_generation_error`
  - participant leave
  - STT failure
  - LLM failure
  - TTS failure
  - pipeline task cancellation
  - Daily/WebRTC disconnect
- Cleanup:
  - stop/cancel Pipecat task
  - leave/disconnect room where applicable
  - close `aiohttp.ClientSession`
  - terminate LemonSlice session where accessible
  - do not invent private transport internals

### Hosted backend

Check:
- Backend calls `POST /api/liveai/rooms`.
- Backend uses `X-API-Key` server-side only.
- Backend sends documented hosted create body with `agent_id`.
- Backend validates response fields:
  - `room_url`
  - `token`
  - `image_url`
  - `session_id`
- Backend stores `session_id`.
- Backend does not log hosted Daily `token`.
- Backend does not expose raw LemonSlice errors or stack traces.
- Backend handles:
  - 400 invalid request
  - 401 missing/invalid API key
  - 402 insufficient funds
  - 403 unauthorized access
  - 404 missing agent/session
  - 500 LemonSlice/server error
  - network timeout
  - invalid response shape
- Backend reconciles session status using hosted get endpoint where needed.

### Hosted Daily frontend

Check:
- Frontend receives `room_url` and `token` from app backend.
- Frontend does not call LemonSlice REST APIs.
- Frontend treats Daily `token` as sensitive.
- Daily join success does not equal avatar readiness.
- UI enters active state only after `bot_ready`.
- Frontend listens to Daily `app-message`.
- Required LemonSlice hosted events:
  - `bot_ready`
  - `idle_timeout`
  - `daily_error`
  - `video_generation_error`
- Required Daily lifecycle events:
  - `participant-left`
  - `left-meeting`
  - Daily top-level `error`
- Startup timeout calls `leave()` and shows retry.
- Retry requests fresh backend credentials.
- User hangup sends `force-end` where appropriate, then runs local cleanup.
- Component unmount clears timers and leaves/destroys the call object.

### Self-managed/API

Check:
- Self-managed uses `/liveai/sessions`, not `/liveai/rooms`.
- Hosted uses `/liveai/rooms`, not `/liveai/sessions`.
- LemonSlice REST calls are backend-only.
- `session_id` is stored.
- Status handling includes:
  - `QUEUED`
  - `ACTIVE`
  - `COMPLETED`
  - `TIMED_OUT`
  - `FAILED`
- Terminal statuses are:
  - `COMPLETED`
  - `TIMED_OUT`
  - `FAILED`
- Backend handles API errors and invalid response shape.
- Control/termination uses documented self-managed control endpoint:
  - `POST /liveai/sessions/{session_id}/control`
  - body `{ "event": "terminate" }`
- Do not invent hosted control endpoint:
  - no `POST /liveai/rooms/{session_id}/control`

## Latency budget

Production latency is the full voice-agent path, not just LemonSlice.

Audit:
- user audio capture/network
- VAD / turn detection
- STT latency
- LLM first-token latency
- LLM full-response latency
- tool/function-call latency
- TTS first-byte latency
- TTS streaming stability
- avatar video generation
- WebRTC/network delivery

Rules:
- Set a latency target before adding more features.
- Measure each stage separately.
- Optimize STT, LLM, and TTS first when responses feel slow.
- Move slow tools or heavy reasoning off the critical path.
- Use `response_done_timeout` only when the selected integration or provider behavior needs it.
- Do not invent hard FPS or response-time guarantees.

## Error handling

Every production integration must convert low-level failures into safe app states.

Required handling:
- startup timeout
- missing `bot_ready`
- `idle_timeout`
- `daily_error`
- `video_generation_error`
- LiveKit disconnect
- Daily disconnect
- participant left unexpectedly
- STT failure
- LLM failure
- TTS failure
- Pipecat task cancellation
- LemonSlice API 400/401/402/403/404/500
- network timeout
- invalid LemonSlice response shape

User-facing behavior:
- do not expose stack traces
- show retry where retry is safe
- request fresh credentials on retry
- do not reuse stale Daily room URL/token after terminal failure
- mark terminal states clearly

## Logging and observability

Log safe fields:
- selected integration path
- app user/account id where allowed
- app session id
- LemonSlice `session_id`
- status transitions
- time to `bot_ready`
- startup timeout fired/not fired
- idle timeout
- disconnect reason
- terminal status
- retry count
- LemonSlice HTTP status code
- provider error class
- LiveKit `metric` fields where available:
  - `time_to_first_push`
  - `tts_audio_delay`

Never log:
- `LEMONSLICE_API_KEY`
- `X-API-Key`
- hosted Daily `token`
- LiveKit token
- Daily token
- raw Authorization headers
- full room credentials
- raw stack traces in frontend responses

## Common mistakes

- Treating a working demo as production-ready.
- Exposing `LEMONSLICE_API_KEY` in frontend/client/mobile code.
- Calling LemonSlice REST APIs directly from browser code.
- Logging API keys, Daily tokens, LiveKit tokens, or room credentials.
- Treating Daily join success as avatar readiness.
- Treating participant join as `bot_ready`.
- Waiting forever when `bot_ready` never arrives.
- Retrying with stale hosted `room_url` / `token`.
- Forgetting cleanup on component unmount.
- Forgetting cleanup on user hangup.
- Forgetting cleanup on deployment/process shutdown.
- Relying only on idle timeout instead of explicit termination.
- Ignoring GPU timeout and third-party provider timeouts.
- Ignoring STT/LLM/TTS errors in LiveKit or Pipecat.
- Treating LiveKit `metric` events as fatal errors.
- Confusing self-managed Daily with Hosted Daily.
- Confusing `/liveai/sessions` with `/liveai/rooms`.
- Inventing unsupported production metrics or guarantees.

## Validation checklist

### Routing
- [ ] Did `lemonslice-integration-choice` already select the primary integration path?
- [ ] Is this production hardening, not first implementation?
- [ ] Did I avoid duplicating full LiveKit/Pipecat/Hosted implementation steps?

### Security
- [ ] Is `LEMONSLICE_API_KEY` server-only?
- [ ] Is `X-API-Key` absent from frontend/client/mobile code?
- [ ] Are Daily/LiveKit tokens treated as sensitive join material?
- [ ] Are secrets absent from logs, analytics, crash reports, and frontend responses?

### Backend/frontend boundary
- [ ] Does frontend call app backend instead of LemonSlice directly?
- [ ] Does backend validate LemonSlice responses?
- [ ] Does backend return only safe session/join material?
- [ ] Is `session_id` stored where status, cleanup, or support needs it?

### Readiness
- [ ] Does UI/backend wait for `bot_ready`?
- [ ] Does it avoid treating room creation, Daily join, LiveKit join, participant join, or first media track as readiness?
- [ ] Is there a startup timeout?
- [ ] Does startup timeout clean up and expose retry?

### Lifecycle
- [ ] Is cleanup implemented for normal hangup?
- [ ] Is cleanup implemented for startup timeout?
- [ ] Is cleanup implemented for idle timeout?
- [ ] Is cleanup implemented for fatal errors?
- [ ] Is cleanup implemented for Daily disconnects?
- [ ] Is cleanup implemented for LiveKit disconnects?
- [ ] Is cleanup implemented for Pipecat task cancellation?
- [ ] Is cleanup implemented for process/deployment shutdown?
- [ ] Does the selected path explicitly terminate LemonSlice where supported?

### Errors
- [ ] LiveKit: are `idle_timeout`, `error`, `video_generation_error`, `metric`, disconnects, and AgentSession STT/LLM/TTS errors handled?
- [ ] Pipecat: are STT/LLM/TTS failures, pipeline cancellation, participant leave, and Daily/WebRTC disconnects handled?
- [ ] Hosted Daily: are `app-message`, `bot_ready`, `idle_timeout`, `daily_error`, `video_generation_error`, and `participant-left` handled?
- [ ] API/backend: are 400/401/402/403/404/500, network timeout, and invalid response shape handled?

### Timeouts
- [ ] Is startup timeout implemented?
- [ ] Is idle timeout configured intentionally?
- [ ] Is GPU timeout understood?
- [ ] Are third-party provider timeouts checked?
- [ ] Is `response_done_timeout` used only when justified?

### Latency
- [ ] Is there a latency budget?
- [ ] Are STT, LLM, TTS, avatar generation, and network measured separately?
- [ ] Is slow work moved off the critical path?
- [ ] Are VAD/turn detection settings reviewed where applicable?

### Observability
- [ ] Are status transitions logged safely?
- [ ] Is time to `bot_ready` measured?
- [ ] Are timeout and disconnect reasons captured?
- [ ] Are terminal states captured?
- [ ] Are LiveKit metric events captured where available?
