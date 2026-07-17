# Endpoint matrix

Audited 2026-07-17.

| Path | Method | Purpose | Authentication |
| --- | --- | --- | --- |
| `/liveai/sessions` | POST | Create self-managed session | `X-API-Key` |
| `/liveai/sessions` | GET | List self-managed sessions | `X-API-Key` |
| `/liveai/sessions/{session_id}` | GET | Get self-managed session | `X-API-Key` |
| `/liveai/sessions/{session_id}/control` | POST | Runtime control | **Docs conflict: inspect current sources** |
| `/liveai/sessions/{session_id}/join-meeting` | POST | Join Zoom/Meet/Teams/Webex | `X-API-Key` |
| `/liveai/sessions/{session_id}/leave-meeting` | POST | Leave external meeting | `X-API-Key` |
| `/liveai/rooms` | POST | Create Hosted Pipeline room | `X-API-Key` |
| `/liveai/rooms` | GET | List hosted rooms | `X-API-Key` |
| `/liveai/rooms/{session_id}` | GET | Get hosted room | `X-API-Key` |

Self-managed JSON uses exactly one of `agent_id` or `agent_image_url`; multipart requests can upload an image file. The current raw REST schema also exposes `model`, `aspect_ratio`, `simulcast`, and recording configuration. Validate installed plugin signatures separately.
