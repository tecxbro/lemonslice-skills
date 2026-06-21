# Path-Specific Production Checklists

## Contents
- LiveKit
- Pipecat
- Hosted backend
- Hosted Daily frontend
- Self-managed/API
- Widget

## LiveKit
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

## Pipecat
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

## Hosted backend
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

## Hosted Daily frontend
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

## Self-managed/API
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

## Widget
- script loaded once
- no API key in frontend
- metadata calls backend/admin only
- live site checked for website builders
