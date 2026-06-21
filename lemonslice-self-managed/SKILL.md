---
name: lemonslice-self-managed
description: Build with Lemon Slice as the avatar/video layer in a custom developer-owned STT/LLM/TTS stack.
license: MIT
---

# Lemon Slice Self-Managed Pipeline

## Official docs
- https://lemonslice.com/docs/api-reference/create-self-managed-session
- https://lemonslice.com/docs/api-reference/get-self-managed-session

## Use this skill when
- `lemonslice-integration-choice` has selected Self-Managed.
- The developer owns STT, LLM, TTS, turn-taking, orchestration, and transport/session handling.
- LemonSlice should only receive agent audio and produce synced avatar video/audio.
- The repo does not clearly use the official LiveKit or Pipecat integration path.
- The task is about raw self-managed REST session creation/status/control setup.

## Do not use this skill when
- Hosted Pipeline: LemonSlice manages STT/LLM/TTS.
- Widget: no-backend website embed.
- Hosted Daily frontend: backend already returns Daily room credentials from hosted sessions.
- LiveKit Agents: use `lemonslice-livekit`.
- Pipecat pipeline: use `lemonslice-pipecat`.
- Production hardening-only audit: use `lemonslice-production-patterns`.
- Runtime control/actions-only task: use `lemonslice-control-actions`.

## What self-managed means
Self-managed means the developer brings the AI pipeline:
- STT
- LLM
- TTS
- turn-taking
- interruption handling
- app/backend orchestration
- transport/session ownership

LemonSlice does not replace those pieces. LemonSlice receives the agent’s audio and returns synchronized avatar video/audio over the selected WebRTC transport.

## API key handling
The LemonSlice API key must stay in trusted backend/agent-server code.

Do not:
- call LemonSlice REST APIs directly from frontend/browser/mobile clients
- expose `X-API-Key` in client bundles
- return the API key to frontend code
- log the raw API key
- store the API key in public repo files

Frontend code may receive app-owned session state, but never the LemonSlice API key.

## Endpoint family
Self-managed uses `/liveai/sessions`.

Hosted/Widget room flows use `/liveai/rooms`.

Do not mix these endpoint families.

## Avatar identity
Provide exactly one avatar identity:

- `agent_id`: use an existing LemonSlice agent.
- `agent_image_url`: use a public image URL for zero-shot avatar creation.

Never send both.
Never send neither.
Prefer a stable HTTPS URL for `agent_image_url`.

## Routing elsewhere
Route to `lemonslice-livekit` when:
- the repo clearly uses LiveKit Agents
- the user asks for the official LiveKit plugin
- the task is about `AvatarSession`, LiveKit room wiring, or `bot_ready`

Route to `lemonslice-pipecat` when:
- the repo clearly uses Pipecat
- the task is about `LemonSliceTransport`
- the task is a Pipecat pipeline, even if Daily appears in the transport

Stay in `lemonslice-self-managed` when:
- the developer owns STT/LLM/TTS
- the repo does not clearly use LiveKit/Pipecat
- the work is direct REST session creation/status with `/api/liveai/sessions`

Route to `lemonslice-hosted` when:
- LemonSlice should manage STT/LLM/TTS

Route to `lemonslice-hosted-daily` when:
- hosted backend already created a Daily room and frontend needs to join it

Route to `lemonslice-control-actions` when:
- the task is about actions, emotions, image updates, or termination

## Reference files
Load only the reference file needed for the task:

- `references/session-payloads-status.md` — read for LiveKit/Daily JSON request examples, `transport_type`, `properties`, optional fields, get/status endpoint, and lifecycle states.

## Common mistakes
- Using `/api/liveai/rooms` or `/api/liveai/rooms/{id}` for self-managed sessions.
- Forgetting the `properties` object.
- Providing `transport_type: "daily"` but assuming this means Hosted Daily.
- Providing both `agent_id` and `agent_image_url`.
- Providing neither `agent_id` nor `agent_image_url`.
- Exposing `LEMONSLICE_API_KEY` or `X-API-Key` to frontend code.
- Using undocumented `transport_type` values.
- Adding undocumented top-level fields.
- Using this generic self-managed REST skill when the repo clearly uses LiveKit Agents or Pipecat.
- Treating `simulcast` as available for Daily transport; it is LiveKit-only.
- Ignoring `QUEUED`, `TIMED_OUT`, and `FAILED` states.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` explicitly select self-managed?
- [ ] Is the repo free of clear LiveKit/Pipecat framework signals that should route elsewhere?
- [ ] Does session creation use `POST /api/liveai/sessions`?
- [ ] Does status polling use `GET /api/liveai/sessions/{session_id}`?
- [ ] Is `LEMONSLICE_API_KEY` used only server-side via `X-API-Key`?
- [ ] Is `transport_type` exactly `livekit` or `daily`?
- [ ] Does the payload include exactly one of `agent_id` or `agent_image_url`?
- [ ] Does the payload include the correct `properties` for the selected transport?
- [ ] Are optional fields limited to documented fields?
- [ ] Is `simulcast` only used with LiveKit transport?
- [ ] Is the returned `session_id` stored for status/control/cleanup?
- [ ] Does the implementation handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, and `FAILED`?
- [ ] Does the skill avoid becoming a LiveKit or Pipecat implementation guide?
- [ ] Does the skill avoid Hosted `/liveai/rooms` endpoint confusion?
