# Security, Readiness, and Cleanup

## Contents
- Credential boundaries
- Backend/frontend boundary
- Readiness and `bot_ready`
- Startup timeout
- Idle and GPU timeout
- Cleanup triggers
- Cleanup actions
- Common mistakes

## Credential boundaries
Rules:
- Keep `LEMONSLICE_API_KEY` server-only.
- Use `X-API-Key` only from trusted backend/server/agent code.
- Never put `LEMONSLICE_API_KEY` in frontend env vars.
- Never use `NEXT_PUBLIC_LEMONSLICE_API_KEY`.
- Never call LemonSlice REST APIs directly from browser/client/mobile code.
- Never return the LemonSlice API key to frontend code.
- Never log API keys.
- Treat hosted Daily `token`, LiveKit tokens, Daily tokens, and room credentials as sensitive join material.

## Backend/frontend boundary
Backend responsibilities:
- authenticate/authorize app user
- call LemonSlice APIs with server-only `LEMONSLICE_API_KEY`
- validate LemonSlice responses
- store `session_id` and safe metadata
- return only safe session/join material to frontend
- reconcile terminal statuses where needed

Frontend responsibilities:
- call app backend, not LemonSlice directly
- join LiveKit/Daily only with safe credentials returned by backend
- listen for readiness/error/disconnect events
- clear timers and credentials on terminal states
- show retry UI when startup or runtime fails

## Readiness
Do not treat these as readiness:
- backend session created
- `session_id` returned
- hosted `room_url` / `token` returned
- Daily join succeeded
- LiveKit room connected
- participant joined
- first media track appeared

Required:
- wait for `bot_ready`
- start timeout while waiting
- cleanup on timeout
- expose retry

## Cleanup triggers
- normal user hangup
- frontend component unmount
- startup timeout
- `bot_ready` never arrives
- `idle_timeout`
- fatal `daily_error`
- `video_generation_error`
- participant leaves unexpectedly
- Daily/WebRTC disconnect
- LiveKit room disconnect
- Pipecat task cancellation
- STT/LLM/TTS failure
- backend request timeout
- process signal
- deployment shutdown

## Cleanup actions
- stop accepting user input
- clear timers
- leave/disconnect Daily or LiveKit room where applicable
- cancel agent/pipeline task where applicable
- close async HTTP/session resources
- clear stale room credentials/tokens
- mark local session terminal or retryable
- explicitly terminate LemonSlice session where the selected path supports it
