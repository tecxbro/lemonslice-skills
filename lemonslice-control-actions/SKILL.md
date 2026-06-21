---
name: lemonslice-control-actions
description: Routes and verifies Lemon Slice runtime controls for already-created sessions. Use for self-managed REST control events, LiveKit tool-call actions, Hosted Daily app-message controls, Widget methods, image/prompt updates, termination, readiness, and race-condition handling.
license: MIT
---

# LemonSlice Control Actions

## Use this skill when
- A LemonSlice session already exists or the integration path is already selected.
- The task is runtime control, termination, action triggering, image updates, prompt updates, Hosted Daily app-message controls, Widget methods, or race-condition handling.

## Do not use this skill for
- Choosing the integration path.
- Creating sessions from scratch.
- Building full Hosted Daily frontend state machines.
- Generic production hardening unrelated to runtime controls.

## Control surfaces

| Path | Control mechanism | Use for |
|---|---|---|
| Self-managed REST | `POST /api/liveai/sessions/{session_id}/control` | terminate, image update, prompt update, pose/action trigger |
| LiveKit | server-side helper / tool-call pattern | contextual LLM-driven actions |
| Hosted Daily | Daily `sendAppMessage(...)` | `chat-msg`, `/imagine`, `force-end` |
| Widget | widget element methods | mute/unmute, mic on/off, send message |

## Core rules
- Confirm the selected path first.
- Do not send controls before readiness.
- Do not expose `X-API-Key` or `LEMONSLICE_API_KEY` to frontend code.
- Do not invent `/liveai/rooms/{session_id}/control`.
- Do not let the LLM invent arbitrary action names.
- Use an allowlist for supported action names.
- Use a dispatcher/lock/queue for overlapping controls.

## Reference files
Load only the reference file needed for the control task:

- `references/self-managed-rest-control.md` — read for `terminate`, `update-image`, prompt updates, and `pose-trigger` request bodies.
- `references/hosted-daily-control.md` — read for `chat-msg`, `force-end`, `/imagine`, and Hosted Daily image-change events.
- `references/livekit-tool-actions.md` — read for LiveKit LLM tool-call action wiring.
- `references/control-dispatcher.md` — read when adding readiness gates, debouncing, queues, stale-session protection, or race-condition handling.

## Common mistakes
- Sending controls before `bot_ready`.
- Treating session creation as avatar readiness.
- Treating Daily join success as avatar readiness.
- Treating participant join as avatar readiness.
- Calling LemonSlice REST APIs directly from frontend code.
- Exposing `X-API-Key` or `LEMONSLICE_API_KEY` in browser/mobile code.
- Inventing `POST /liveai/rooms/{session_id}/control`.
- Using Hosted Daily `force-end` for self-managed REST sessions.
- Using self-managed `terminate` as if it were a Daily frontend hangup.
- Hardcoding `wave` or `celebrate` without checking avatar support.
- Letting the LLM invent arbitrary action names.
- Sending overlapping action triggers without a dispatcher.
- Updating image while the avatar is speaking and then being surprised that audio cuts off.
- Treating prompt updates as deterministic animation commands.
- Forgetting to clear queued controls after terminate, timeout, error, or disconnect.
- Confusing Widget methods with session/action controls.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` select or confirm the path?
- [ ] Is the selected path self-managed REST, LiveKit, Hosted Daily, or Widget?
- [ ] If self-managed, does control use `POST /api/liveai/sessions/{session_id}/control`?
- [ ] If self-managed, is `X-API-Key` server-side only?
- [ ] If self-managed, are event bodies limited to documented shapes?
- [ ] Is `terminate` used only for the self-managed control endpoint?
- [ ] Is `pose-trigger` documented as an Actions-guide pattern and verified against current docs/avatar support?
- [ ] Are action names allowlisted or verified for the avatar?
- [ ] Does LiveKit LLM tool calling map tools to supported internal action names?
- [ ] Does the implementation wait for `bot_ready` or equivalent readiness before controls?
- [ ] Is there a startup timeout if readiness never arrives?
- [ ] Is there an action dispatcher, debounce, lock, or queue policy?
- [ ] Are image updates guarded because they can interrupt audio?
- [ ] Are `update-agent-prompt` and `update-idle-prompt` treated as high-level demeanor guidance?
- [ ] If Hosted Daily, does control use `sendAppMessage`, not REST `/rooms/.../control`?
- [ ] If Hosted Daily, does hangup send `force-end` and still run local Daily cleanup?
- [ ] If Hosted Daily, is `/imagine` sent through `chat-msg` only?
- [ ] If Widget, are only widget-supported methods documented?
- [ ] Are terminal states/errors clearing queued controls and stale session state?
