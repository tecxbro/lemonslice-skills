# Lifecycle, Errors, and Recording

## Contents
- Startup
- During call
- Shutdown
- Readiness/events
- Error handling
- Recording config
- Common mistakes

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
