# Readiness, Events, and Shutdown

## Contents
- Readiness and events
- Shutdown behavior

## Readiness and events
Do not treat LiveKit participant join as avatar readiness.

The explicit readiness signal is:
- `bot_ready`

Official LiveKit RPC topic:
- topic: `lemonslice`
- readiness type: `bot_ready`

The agent must wait for `bot_ready` before:
- showing “avatar ready”
- sending control/actions
- assuming video generation is healthy
- allowing user-facing interactions that depend on the avatar

Handle these LemonSlice data-channel events:
- `bot_ready`: avatar is initialized and ready.
- `idle_timeout`: avatar session idled out. Stop waiting for output, clean up state, and shut down if appropriate.
- `error`: general LemonSlice/avatar error. Log with context, surface a safe error state, and clean up.
- `video_generation_error`: avatar video generation failed. Treat as avatar-path failure, not necessarily LiveKit room failure.
- `metric`: telemetry/observability event. For `metric`, record useful fields such as `time_to_first_push` and `tts_audio_delay`. Treat `tts_audio_delay=true` as a latency/realtime-delivery signal, not as a LemonSlice crash by itself.

Add a startup timeout around `bot_ready`. If it never arrives, fail safely, clean up the room/avatar, and expose a retry path.

## Shutdown behavior
Implement cleanup for:
- normal worker shutdown
- user hangup
- LiveKit room disconnect
- `idle_timeout`
- startup timeout waiting for `bot_ready`
- `error`
- `video_generation_error`
- process signals / deployment shutdown

The official docs give three exact shutdown paths:
1. `ctx.room.disconnect()` closes the LiveKit room connection and ends the LemonSlice avatar session.
2. `ctx.shutdown()` stops the Agent `JobContext` and LemonSlice avatar session without shutting down the LiveKit room.
3. `terminate` shuts down only the LemonSlice avatar without shutting down the LiveKit room or agent.

Also, if not shut down, the LemonSlice session remains active until idle timeout or the 1-hour maximum session duration expires.

Do not confuse terminating LemonSlice avatar generation with deleting unrelated app state.
