# Pipecat version surface

Fill this table from the current official docs and the installed `LemonSliceNewSessionRequest` signature before editing application code.

| Field | Current docs | Installed signature | Safe to use? |
| --- | --- | --- | --- |
| `agent_image_url` | Verify | Inspect | Only when accepted by installed version |
| `agent_id` | Verify | Inspect | Only when accepted; enforce selector rules |
| `agent_prompt` | Verify | Inspect | Only when accepted |
| `agent_idle_prompt` | Verify | Inspect | Only when accepted |
| `idle_timeout` | Verify | Inspect | Only when accepted and cleanup is implemented |
| `response_done_timeout` | Verify | Inspect | Only when accepted and needed by the TTS flow |
| `model` | Verify | Inspect | Do not infer from raw REST or LiveKit |
| `aspect_ratio` | Verify | Inspect | Do not infer from raw REST or LiveKit |
| `daily_room_url` | Verify | Inspect | Only for the documented existing-room flow |
| `daily_token` | Verify | Inspect | Keep secret and scoped |
| `lemonslice_properties` | Verify | Inspect | Validate nested shape exactly |
| `enable_recording` | Verify | Inspect | Requires valid recording configuration |
| `recordings_bucket` | Verify | Inspect | Required when recording is enabled |

Record the installed package version and the source file/type declaration inspected. Do not “fix” a type error by passing undocumented keys through an untyped dictionary unless the user explicitly accepts that compatibility risk.
