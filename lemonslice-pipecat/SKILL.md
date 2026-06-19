---
name: lemonslice-pipecat
description: Add Lemon Slice avatars to Pipecat pipelines.
license: MIT
---

# Lemon Slice Pipecat Integration

## Official docs
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/examples/pipecat-app.md
- https://lemonslice.com/docs/reference/overview.md
- https://lemonslice.com/docs/reference/best-practices.md
- https://lemonslice.com/docs/reference/authentication.md
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md

## Guardrails
Use this only after `lemonslice-integration-choice` selected Pipecat.

Use this when:
* repo is a Pipecat Python agent project
* task is adding LemonSlice avatar video to an existing Pipecat STT/LLM/TTS pipeline
* repo uses Daily through Pipecat transport
* user mentions `LemonSliceTransport`, `LemonSliceNewSessionRequest`, `daily_room_url`, or `daily_token` in a Pipecat context

Do not use this when:
* LiveKit Agents project → `lemonslice-livekit`
* LemonSlice manages STT/LLM/TTS → `lemonslice-hosted`
* frontend only joins hosted Daily room → `lemonslice-hosted-daily`
* no-backend website embed → `lemonslice-widget`
* raw REST session creation without Pipecat → `lemonslice-self-managed` or `lemonslice-api-reference`

> **Critical distinction to repeat:**
> Pipecat may use Daily as its WebRTC transport, but Pipecat is not Hosted Daily. In Pipecat, the developer owns the bot pipeline. Hosted Daily means Lemon Slice manages the agent pipeline and returns a Daily room for a frontend to join.

## What Pipecat + Lemon Slice means
* Pipecat remains the conversational agent framework.
* Developer owns STT, LLM, TTS, turn-taking, interruption handling, and pipeline orchestration.
* LemonSlice is the avatar video layer.
* `LemonSliceTransport` connects the Pipecat bot to LemonSlice avatar video.
* Daily can appear internally, but this is still not Hosted Daily.

## Detect a Pipecat project
Check for these Pipecat signals in the repository:
* `pyproject.toml`
* `requirements.txt`
* `uv.lock`
* imports from `pipecat`
* `Pipeline`
* `PipelineTask`
* `PipelineParams`
* STT / LLM / TTS services wired into a Pipecat pipeline
* Daily transport code inside a Pipecat bot
* Python bot entrypoints constructing and running a Pipecat pipeline

If no Pipecat signals exist, route back to `lemonslice-integration-choice`.

If LiveKit and Pipecat both exist, identify the actual agent entrypoint before editing. Do not edit both unless the repo intentionally has both.

## Install package
Install the Pipecat package with LemonSlice support:

```bash
pip install "pipecat-ai[lemonslice]"
```

Or for uv:
```bash
uv add "pipecat-ai[lemonslice]"
```

Or for poetry:
```bash
poetry add "pipecat-ai[lemonslice]"
```

Do not install LiveKit packages in a Pipecat project.

## Environment variables
Required:
```bash
LEMONSLICE_API_KEY=...
```

Rules:
* Keep it only in bot/server environment.
* Never expose to frontend/browser/mobile/public config.
* Update `.env.example` only with key name.
* Never log the real key.
* Never return the key to frontend code.

## Core imports
Use these exact official import paths (do not invent import paths):
```python
from pipecat.transports.lemonslice.transport import (
    LemonSliceNewSessionRequest,
    LemonSliceParams,
    LemonSliceTransport,
)
```

## Create the Lemon Slice transport
Here is a concise Python setup pattern:

```python
import os
import aiohttp

from pipecat.transports.lemonslice.transport import (
    LemonSliceNewSessionRequest,
    LemonSliceParams,
    LemonSliceTransport,
)

async def main():
    async with aiohttp.ClientSession() as session:
        transport = LemonSliceTransport(
            bot_name="Pipecat",
            api_key=os.getenv("LEMONSLICE_API_KEY"),
            session=session,
            session_request=LemonSliceNewSessionRequest(
                agent_image_url="https://example.com/avatar.png",
            ),
        )
```

Rules:
* `bot_name` is the Pipecat bot participant name.
* `api_key` comes from `LEMONSLICE_API_KEY`.
* `session` should be an `aiohttp.ClientSession`.
* `session_request` must be `LemonSliceNewSessionRequest`.
* Provide exactly one of `agent_id` or `agent_image_url`.

## LemonSliceNewSessionRequest
Required avatar identity:
* `agent_image_url`
* or `agent_id`

Rules:
* Never send both.
* Never send neither.

Optional fields:
* `agent_prompt`
* `agent_idle_prompt`
* `idle_timeout`
* `response_done_timeout`
* `daily_room_url`
* `daily_token`
* `lemonslice_properties`

## Daily room behavior
* Pipecat with LemonSlice uses Daily as the underlying transport layer.
* This does **not** mean Hosted Daily.
* `daily_room_url` and `daily_token` are optional.
* If `daily_room_url` is provided, LemonSlice uses that Daily room.
* If `daily_token` is provided, LemonSlice uses it for room auth.
* If `daily_room_url` is omitted, LemonSlice automatically creates a Daily room.
* Auto-created Daily rooms may create extra participant-minute cost.
* When LemonSlice auto-creates the room, the code should not assume the app owns room lifecycle exactly like a manually-created Daily room.

> Do not confuse these with Hosted Daily `room_url` and `token`.
> Hosted Daily uses `/liveai/rooms` and a Lemon Slice-managed agent.
> Pipecat uses `LemonSliceTransport` inside the developer-owned Pipecat pipeline.

## Pipeline wiring
Conceptual shape:

```python
pipeline = Pipeline(
    [
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,
        transport.output(),
        assistant_aggregator,
    ]
)

task = PipelineTask(
    pipeline,
    params=PipelineParams(
        audio_in_sample_rate=16000,
        audio_out_sample_rate=16000,
    ),
)
```

Explanation:
* `transport.input()` receives user audio.
* STT converts audio to text.
* LLM generates response.
* TTS creates agent audio.
* `transport.output()` sends agent audio toward LemonSlice.
* LemonSlice renders synced avatar audio/video.
* Do not route LemonSlice as a separate frontend widget.
* Do not replace Pipecat STT/LLM/TTS with hosted LemonSlice behavior.

## Bot / avatar / user room relationship
Explicit participant model:

1. **Human user**
   Speaks into Daily/WebRTC room and receives avatar audio/video.

2. **Pipecat bot participant**
   Runs developer-owned STT/LLM/TTS pipeline. Should not be displayed as the visible avatar.

3. **LemonSlice avatar participant**
   Receives bot/TTS audio and renders lip-synced avatar video/audio.

Rules:
* LemonSlice avatar participant is filtered out from `transport.on_client_connected` and `transport.on_client_disconnected`.
* Only human participant connections should trigger those handlers.
* Daily video UI should filter out the Pipecat bot participant.
* Avatar microphone is automatically muted to avoid feedback loops.

## Pipeline lifecycle
**Startup:**
* create/load STT, LLM, TTS, aggregators
* create `aiohttp.ClientSession`
* create `LemonSliceTransport`
* build `Pipeline`
* create `PipelineTask`
* start runner/task using existing repo pattern
* keep UI/call state loading until avatar ready

**During call:**
* user audio enters through `transport.input()`
* STT/LLM/TTS produce bot audio
* `transport.output()` sends audio to LemonSlice
* LemonSlice renders synchronized video/audio
* interruption messages are handled by transport

**Shutdown:**
* stop/cancel Pipecat task
* leave/disconnect Daily room where applicable
* close `aiohttp.ClientSession`
* terminate LemonSlice session where accessible
* handle user hangup, participant leave, idle timeout, startup timeout, pipeline errors, process shutdown, deployment shutdown

## Readiness and events
* Do not treat participant join as avatar readiness.
* Use `bot_ready` where available.
* Listen for:
  * `bot_ready`
  * `idle_timeout`
  * `daily_error`
  * `video_generation_error`
  * `participant-left`

For Daily app-message UIs, listen via `app-message`.

**Startup timeout behavior:**
If `bot_ready` never arrives:
* stop Pipecat task
* leave room
* clean up resources
* show/return retryable error state

## Error handling

**Configuration errors:**
* missing `LEMONSLICE_API_KEY`
* both `agent_id` and `agent_image_url`
* neither `agent_id` nor `agent_image_url`
* invalid/private `agent_image_url`
* wrong package/import path

**Session/startup errors:**
* LemonSlice session creation failure
* Daily room creation/join failure
* `bot_ready` timeout
* cold start delays

**Pipeline errors:**
* STT failure
* LLM failure
* TTS failure
* pipeline task cancellation
* unrecoverable pipeline exceptions

**Runtime room/avatar errors:**
* `daily_error`
* `video_generation_error`
* participant disconnect
* idle timeout
* user hangup
* network/WebRTC disconnect

**Fatal error handling:**
* log safe context
* never log API keys or raw tokens
* stop Pipecat pipeline/task
* disconnect/leave room where applicable
* clean up LemonSlice resources
* return retryable user-facing state

## Shutdown and cleanup
Explicit cleanup triggers:
* normal user hangup
* human participant leaves
* bot process shutdown signal
* Pipecat task cancellation
* startup timeout
* `idle_timeout`
* fatal `daily_error`
* `video_generation_error`
* STT/LLM/TTS failure
* Daily/WebRTC disconnect

If implementation has access to `session_id`, use LemonSlice control termination:
```json
{
  "event": "terminate"
}
```
But if the Pipecat transport abstracts session internals, use the official transport cleanup/close/shutdown path and do not invent private internals.

> Do not assume idle timeout is enough. Explicit cleanup prevents stale rooms, stale avatar sessions, and runaway billing.

## Recording config
* Recording config belongs in `lemonslice_properties`.
* Supported `enable_recording` values:
  * `cloud`
  * `cloud-audio-only`
  * `local`
  * `raw-tracks`
* If recording is enabled, `recordings_bucket` must be configured.
* Do not add recording config as arbitrary top-level fields.

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
