# Endpoint matrix

Audited 2026-07-17. Regenerate the OpenAPI snapshot before treating volatile fields as current.

| Endpoint | Purpose | Auth | Request alternatives | Success response | Status behavior |
| --- | --- | --- | --- | --- | --- |
| `POST /liveai/sessions` | Create self-managed session | `X-API-Key` | JSON: exactly one of `agent_id` or `agent_image_url`; current OpenAPI also declares multipart `image` + `payload` | `session_id` | Creation may enter `QUEUED`; reconcile with the get endpoint |
| `GET /liveai/sessions` | List self-managed sessions | `X-API-Key` | `page`, `limit` | Session collection + pagination metadata | Preserve `has_more`; do not merge Hosted records |
| `GET /liveai/sessions/{session_id}` | Reconcile one self-managed session | `X-API-Key` | Path identifier | Session record | Handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED` |
| `POST /liveai/sessions/{session_id}/control` | Runtime control | **Documentation conflict** | Discriminated control-event union | Acknowledgement | Acknowledgement is not visual completion; image replacement is asynchronous |
| `POST /liveai/sessions/{session_id}/join-meeting` | Join Zoom, Meet, Teams, or Webex | `X-API-Key` | Meeting URL + LiveKit broadcast credentials | `meeting_bot_id`, `websocket_url` | External admission/lobby state remains separate from LemonSlice readiness |
| `POST /liveai/sessions/{session_id}/leave-meeting` | Leave external meeting | `X-API-Key` | Persisted meeting-bot/session identifiers | Leave acknowledgement | Make retry-safe after partial failure |
| `POST /liveai/rooms` | Create Hosted Pipeline room | `X-API-Key` | Hosted agent/session request | `room_url`, `token`, `image_url`, `session_id` | May enter `QUEUED`; frontend visual readiness still requires a rendered frame |
| `GET /liveai/rooms` | List Hosted Pipeline rooms | `X-API-Key` | `page`, `limit` | Hosted room collection + pagination metadata | Preserve `has_more`; do not confuse with self-managed sessions |
| `GET /liveai/rooms/{session_id}` | Reconcile one Hosted room | `X-API-Key` | Path identifier | Room status, timestamps, cost/end data where returned | Handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED` |

The current raw self-managed snapshot includes `model`, `aspect_ratio`, `simulcast`, and both JSON and multipart media types. These are raw-OpenAPI facts, not permission to infer matching fields in every LiveKit, Node, Python, or Pipecat package surface.
