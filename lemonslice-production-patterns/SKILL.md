---
name: lemonslice-production-patterns
description: Production-hardening checklist for LemonSlice LiveKit, Pipecat, Hosted Daily, Widget, and raw REST integrations. Covers first-frame readiness, failures, capacity, abandoned sessions, image updates, data handling, latency, cleanup, and billing safety.
license: MIT
---

# LemonSlice production patterns

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## 1. Ringing and two-gate readiness

Avatar initialization takes time. Use a ringing/loading state.

- Pipeline gate: `bot_ready`
- Visual gate: first rendered frame through the selected LiveKit/Daily readiness mechanism

Only the visual gate enters active-call UI. Never describe `bot_ready`, participant join, a placeholder image, or control acknowledgement as proof of a rendered frame.

## 2. Connect and disconnect lifecycle

LiveKit: handle identified-avatar `ParticipantDisconnected` and room `Disconnected`.

Hosted Daily: handle identified-agent `participant-left`, `left-meeting`, top-level `error`, and LemonSlice app-message failures.

Reset UI, release local media state, and require fresh credentials for a new attempt.

## 3. Pipeline and room errors

- LiveKit `AgentSession` errors: distinguish STT, LLM, TTS, tools, and avatar failures.
- Hosted Daily: classify `daily_error`, `video_generation_error`, transport errors, and recoverable image-update failures.
- Raw REST/Hosted backend: preserve HTTP status, defensively parsed JSON, and redacted non-JSON bodies.

## 4. Startup failure

- Handle `startup_failure` where the integration exposes it.
- Add a bounded startup timer without treating `QUEUED` as `FAILED`.
- A client timeout does not prove the provider session ended.
- Retry with newly created credentials, never stale room/token material.

## 5. Timeouts and billing safety

Review provider idle timeout, maximum session/call constraints, LiveKit/Daily timeouts, application inactivity timeout, external meeting timeout, and local startup timeout.

A disabled/negative idle timeout requires explicit termination on hangup, error, deployment shutdown, and abandoned clients. Hosted hangup should send the documented end control and still leave/destroy locally.

## 6. Capacity claims versus account limits

Product-level concurrency, long-call, resolution, model, and deployment capabilities do not guarantee the same limits for every account. Verify the current plan, account, region, model, transport, and integration constraints before sizing or promising behavior.

Do not hard-code universal claims such as 24-hour calls or 1000+ concurrency into implementation logic or customer-facing guarantees.

## 7. Abandoned-session reconciliation

A browser closing unexpectedly may prevent client-side cleanup. Backends should persist app ownership and provider identifiers, poll/reconcile status, and terminate or expire abandoned resources where supported.

Reconciliation must be idempotent and safe after backend restart. Never authorize cleanup or status access based only on possession of a provider `session_id`.

## 8. Runtime image replacement

Runtime image replacement can interrupt current avatar audio. Schedule it during silence when possible and treat provider acknowledgement as asynchronous.

Keep the existing frame visible until the replacement frame renders. Prevent overlapping updates unless replacement/cancellation is explicitly documented. Preserve the healthy active call when an appearance update fails.

## 9. Latency budget

Measure end of user speech, final STT, LLM first token/completion, tools, first TTS audio, avatar time-to-first-push, remote track subscription, network, and first rendered frame separately.

Published benchmark values are dated measurements under a specific stack, not universal SLAs. Move non-critical work off the response path and test interruption behavior with the actual VAD/turn strategy.

## 10. Transcription

Transcription is optional. Prefer final-only results when rapidly changing interim text reduces trust. Label user versus agent text and never make transcript display the call-readiness gate.

## 11. Data handling

Do not log:

- API keys;
- Daily or LiveKit tokens;
- raw audio;
- unredacted transcripts;
- private prompts or tool payloads;
- uploaded avatar image URLs when signed or private;
- recording credentials, cloud-role material, or signed download URLs.

Use structured identifiers, status codes, durations, and redacted error categories. Apply retention and access controls to transcripts, images, recordings, and conversation metadata.

## 12. Verification

Test `bot_ready` with no rendered frame, queued startup, avatar disconnect, room disconnect, startup timeout/failure, fatal and recoverable errors, user hangup, abandoned browser, idle timeout, image-update failure, retry, process shutdown, and no frontend credential exposure.

Reference:
- https://lemonslice.com/docs/reference/production-checklist.md
