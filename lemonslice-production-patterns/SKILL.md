---
name: lemonslice-production-patterns
description: Audits production readiness for Lemon Slice integrations after the selected path works. Use for API key safety, backend/frontend separation, bot_ready readiness, startup timeout, cleanup, disconnects, latency, logging, and deployment hardening.
license: MIT
---

# Lemon Slice Production Patterns

## Use this skill when
Use this after the selected Lemon Slice integration already works and needs production hardening.

Use it for:
- API key safety
- backend/frontend separation
- `bot_ready`
- startup timeout
- idle timeout
- cleanup
- explicit termination
- Daily disconnect handling
- LiveKit disconnect handling
- Pipecat pipeline error handling
- latency budgeting
- logging and observability

## Do not use this skill when
Do not use this to build the first working integration.

Route first to:
- `lemonslice-livekit`
- `lemonslice-pipecat`
- `lemonslice-hosted`
- `lemonslice-hosted-daily`
- `lemonslice-self-managed`
- `lemonslice-widget`
- `lemonslice-api-reference`
- `lemonslice-control-actions`

## Production audit workflow
1. Confirm the selected integration path.
2. Audit credentials.
3. Audit backend/frontend boundary.
4. Audit readiness and `bot_ready`.
5. Audit startup timeout.
6. Audit lifecycle cleanup.
7. Audit disconnect/error handling.
8. Audit latency budget.
9. Audit logging and observability.

## Core rules
- `LEMONSLICE_API_KEY` stays server-side only.
- `X-API-Key` is never used in frontend/browser/mobile code.
- Frontend calls app backend, not Lemon Slice REST APIs directly.
- Do not mark avatar active until `bot_ready`.
- Do not wait forever for `bot_ready`; add startup timeout.
- Cleanup must run on hangup, timeout, fatal error, disconnect, and component/process shutdown.
- Do not log API keys, Daily tokens, LiveKit tokens, room credentials, or raw stack traces.

## Reference files
Load only the reference file needed for the audit:

- `references/security-readiness-cleanup.md` — read for secrets, frontend/backend boundary, `bot_ready`, startup timeout, idle timeout, GPU timeout, cleanup, and terminal paths.
- `references/path-specific-checklists.md` — read for LiveKit, Pipecat, Hosted backend, Hosted Daily frontend, Self-managed/API, or Widget production checks.
- `references/latency-observability.md` — read when optimizing latency or adding safe logs/metrics.

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
