# Latency and Observability

## Contents
- Latency budget
- Metrics to collect
- Safe logs
- Forbidden logs
- Common mistakes

## Latency budget stages
- user audio capture/network
- VAD / turn detection
- STT latency
- LLM first-token latency
- LLM full-response latency
- tool/function-call latency
- TTS first-byte latency
- TTS streaming stability
- avatar video generation
- WebRTC/network delivery

## Safe logs
- selected integration path
- app user/account id where allowed
- app session id
- LemonSlice `session_id`
- status transitions
- time to `bot_ready`
- startup timeout fired/not fired
- idle timeout
- disconnect reason
- terminal status
- retry count
- LemonSlice HTTP status code
- provider error class
- LiveKit `metric` fields where available:
  - `time_to_first_push`
  - `tts_audio_delay`

## Never log
- `LEMONSLICE_API_KEY`
- `X-API-Key`
- hosted Daily `token`
- LiveKit token
- Daily token
- raw Authorization headers
- full room credentials
- raw stack traces in frontend responses
