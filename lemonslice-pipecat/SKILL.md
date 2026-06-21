---
name: lemonslice-pipecat
description: Adds Lemon Slice avatar video to Pipecat Python pipelines. Use for pipecat-ai[lemonslice], LemonSliceTransport, LemonSliceNewSessionRequest, Daily transport behavior, participant filtering, lifecycle, and cleanup.
license: MIT
---

# Lemon Slice Pipecat Integration

## Official docs
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/examples/pipecat-app.md
- https://lemonslice.com/docs/reference/overview.md
- https://lemonslice.com/docs/reference/best-practices.md

## Use this skill when
- Router selected Pipecat.
- Repo is a Pipecat Python agent project.
- Task adds LemonSlice avatar video to an existing Pipecat STT/LLM/TTS pipeline.
- Repo uses Daily through Pipecat transport.
- User mentions `LemonSliceTransport`, `LemonSliceNewSessionRequest`, `daily_room_url`, or `daily_token` in a Pipecat context.

## Do not use this skill when
- LiveKit project → `lemonslice-livekit`
- LemonSlice manages STT/LLM/TTS → `lemonslice-hosted`
- Frontend only joins hosted Daily room → `lemonslice-hosted-daily`
- No-backend website embed → `lemonslice-widget`
- Raw REST without Pipecat → `lemonslice-self-managed` or `lemonslice-api-reference`

## Critical distinction
Pipecat may use Daily as its WebRTC transport, but Pipecat is not Hosted Daily. In Pipecat, the developer owns STT/LLM/TTS and pipeline orchestration. Hosted Daily means Lemon Slice manages the agent pipeline and returns Daily room credentials for a frontend to join.

## Core rules
- Install `pipecat-ai[lemonslice]`.
- Use `LemonSliceTransport`.
- Use `LemonSliceNewSessionRequest`.
- Keep `LEMONSLICE_API_KEY` server-side.
- Provide exactly one of `agent_id` or `agent_image_url`.
- Do not call `/liveai/rooms` for Pipecat.
- Do not replace Pipecat STT/LLM/TTS with Hosted Pipeline behavior.

## Reference files
Load only the reference file needed for the Pipecat task:

- `references/transport-setup.md` — read when installing `pipecat-ai[lemonslice]`, adding imports, or constructing `LemonSliceTransport`.
- `references/daily-room-and-participants.md` — read when handling `daily_room_url`, `daily_token`, auto-created Daily rooms, or human/bot/avatar participant filtering.
- `references/lifecycle-errors-recording.md` — read when implementing startup, shutdown, errors, cleanup, or recording config.

## Common mistakes
* Using this skill before router selected Pipecat.
* Seeing Daily and incorrectly routing to `lemonslice-hosted-daily`.
* Treating Pipecat Daily transport as Hosted Daily.
* Calling `/liveai/rooms` for Pipecat.
* Replacing developer-owned Pipecat STT/LLM/TTS with hosted LemonSlice behavior.
* Installing LiveKit LemonSlice packages in a Pipecat project.
* Exposing `LEMONSLICE_API_KEY` to client code.
* Providing both `agent_id` and `agent_image_url`.
* Providing neither `agent_id` nor `agent_image_url`.
* Forgetting `daily_room_url` and `daily_token` are optional.
* Omitting `daily_room_url` without accounting for auto-created Daily room behavior and cost.
* Showing Pipecat bot participant as the avatar.
* Treating participant join as readiness instead of `bot_ready`.
* Ignoring startup timeout, `daily_error`, `video_generation_error`, participant leave, and idle timeout.
* Forgetting to stop/cancel pipeline and close async resources.
* Logging API keys, Daily tokens, or room credentials.

## Validation checklist
- [ ] Is `pipecat-ai[lemonslice]` installed?
- [ ] Is `LemonSliceTransport` configured in the Pipecat pipeline?
- [ ] Are the official import paths used?
- [ ] Is `LemonSliceNewSessionRequest` passing exactly one of `agent_image_url` or `agent_id`?
- [ ] If `daily_room_url` is omitted, is the code designed to handle Lemon Slice auto-creating the room?
- [ ] Is the participant logic filtering out the bot participant and avoiding feedback loops?
- [ ] Does the implementation wait for `bot_ready` instead of participant join?
- [ ] Is there explicit shutdown logic on normal termination or timeouts?
- [ ] Are API keys absent from frontend-facing logs or returns?
- [ ] Are there startup timeouts?
- [ ] Did `lemonslice-integration-choice` explicitly select Pipecat?
- [ ] Did I inspect repo evidence before editing?
- [ ] Is `LemonSliceParams` used only according to the official Pipecat transport pattern?
- [ ] Are `daily_room_url` and `daily_token` treated as optional?
- [ ] Does the implementation preserve the developer-owned STT/LLM/TTS pipeline?
- [ ] Did I avoid Hosted Daily `/liveai/rooms` unless the router selected `lemonslice-hosted-daily`?
- [ ] Did I repeat the key distinction: Pipecat may use Daily, but it is not Hosted Daily?
