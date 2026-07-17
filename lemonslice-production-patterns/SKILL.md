---
name: lemonslice-production-patterns
description: Production-hardening checklist for LemonSlice LiveKit, Pipecat, Hosted Daily, Widget, and raw REST integrations. Covers first-frame readiness, disconnects, errors, startup failures, timeouts, latency, VAD, transcription, security, and billing cleanup.
license: MIT
---

# LemonSlice production patterns

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## 1. Ringing and two-gate readiness

Avatar initialization takes time. Use a ringing/loading state.

- Pipeline gate: `bot_ready`
- Visual gate: first rendered frame through `LiveKitAvatarReadyWatcher` or Daily `useAvatarReady`

Only the visual gate enters active-call UI. Never describe `bot_ready` as proof of a rendered frame.

## 2. Connect and disconnect lifecycle

LiveKit:

- `RoomEvent.ParticipantDisconnected` for avatar departure
- `RoomEvent.Disconnected` for room/network failure

Hosted Daily:

- identified agent `participant-left`
- `left-meeting`
- Daily top-level `error`

Reset UI and allow a fresh retry.

## 3. Pipeline and room errors

- LiveKit `AgentSession` errors: distinguish STT, LLM, and TTS; terminate on non-recoverable errors.
- Hosted Daily: handle `daily_error`, especially `fatal: true`, and `video_generation_error`.
- Log structured context without API keys, tokens, raw audio, or sensitive prompt content.

## 4. Startup failure

- Handle `startup_failure` on LiveKit topic `lemonslice/message`.
- Add a bounded startup timeout.
- During Hosted Daily startup, a fatal `daily_error` ends the attempt.
- Retry with newly created credentials, never stale tokens.

## 5. Timeouts and billing safety

Review:

- LemonSlice idle timeout;
- LemonSlice GPU/session maximum;
- LiveKit/Daily/provider timeouts;
- application inactivity timeout;
- external meeting timeout.

`idle_timeout=-1` requires explicit termination on hangup, error, deployment shutdown, and abandoned clients. Hosted hangup should send `force-end` and still leave/destroy locally.

## 6. Latency budget

Measure STT, turn detection, LLM, tools, TTS, avatar time-to-first-push, network, and first rendered frame separately. Do not blame video by default. Move non-critical work off the response path.

Use VAD/turn detection to reduce perceived latency and test interruption behavior.

## 7. Transcription

Transcription is optional. Prefer final-only results when rapidly changing interim text would reduce trust. Label user versus agent text and never make transcript display the call-readiness gate.

## 8. Verification

Test:

- `bot_ready` with no rendered frame;
- avatar participant disconnect;
- room disconnect;
- startup timeout/failure;
- fatal and recoverable pipeline errors;
- user hangup;
- idle timeout;
- retry;
- process shutdown;
- no frontend API-key exposure.

Reference:
- https://lemonslice.com/docs/reference/production-checklist.md
