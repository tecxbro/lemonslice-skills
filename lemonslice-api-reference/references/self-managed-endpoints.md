# Self-Managed Endpoints

## Contents
- Endpoint family
- Create self-managed session
- Transport properties
- Avatar identity
- Optional fields
- Get self-managed session
- List self-managed sessions
- Common mistakes

## Endpoint family
Self-managed uses `/liveai/sessions`.

Full base:
`https://lemonslice.com/api/liveai/sessions`

## Create self-managed session
Endpoint:
`POST /liveai/sessions`

Headers:
`X-API-Key`
`Content-Type: application/json`

Required:
- `transport_type`
- exactly one of `agent_id` or `agent_image_url`

Allowed `transport_type`:
- `livekit`
- `daily`

Disallowed invented values:
- `webrtc`
- `browser`
- `hosted`
- `rooms`
- `pipecat`
- `tavus`

## LiveKit transport example
```json
{
  "agent_id": "agent_abc123",
  "transport_type": "livekit",
  "properties": {
    "livekit_url": "wss://example.livekit.cloud",
    "livekit_token": "..."
  }
}
```

## Daily transport example
```json
{
  "agent_id": "agent_abc123",
  "transport_type": "daily",
  "properties": {
    "daily_room_url": "https://your-domain.daily.co/your-room",
    "daily_token": "..."
  }
}
```

## Optional fields
- `agent_prompt`
- `agent_idle_prompt`
- `idle_timeout`
- `response_done_timeout`
- `simulcast`

## Create response
Self-managed create returns:
`session_id`

It does not return:
- `room_url`
- `token`
- `image_url`

## Get self-managed session
Endpoint:
`GET /liveai/sessions/{session_id}`

Response always includes:
`session_status`

Statuses:
- `QUEUED`
- `ACTIVE`
- `COMPLETED`
- `TIMED_OUT`
- `FAILED`

Completed response may include:
`cost`

## List self-managed sessions
Endpoint:
`GET /liveai/sessions`

Query:
- `page`
- `limit`

```json
{
  "sessions": [
    {
      "session_id": "livekit-3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a",
      "created_at": "2026-04-29T20:34:56.000Z",
      "session_status": "COMPLETED",
      "credits_used": 10.5,
      "provider": "LIVEKIT"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 1,
    "total_pages": 1,
    "has_more": false
  }
}
```

## Common mistakes
- Using `/liveai/rooms` for self-managed sessions.
- Expecting self-managed create to return `room_url` or `token`.
- Calling REST APIs from frontend.
