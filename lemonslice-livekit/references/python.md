# LiveKit Python reference

Documented `AvatarSession` inputs as of 2026-07-17:

- exactly one of `agent_image_url`, `agent_id`, `agent_image`
- `agent_prompt`
- `agent_idle_prompt`
- `idle_timeout`
- `response_done_timeout`
- `model`: `lite`, `flash`, `pro`
- `aspect_ratio`: `2x3`, `9x16`, `1x1`
- `simulcast`

Inspect the installed `livekit-agents` plugin signature before using these fields. For Gemini Live S2S, current LemonSlice guidance recommends `response_done_timeout=0.8`.
