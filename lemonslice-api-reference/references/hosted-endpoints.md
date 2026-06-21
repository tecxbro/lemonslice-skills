# Hosted Endpoints

## Contents
- Endpoint family
- Create hosted session
- Hosted response fields
- Get hosted session
- List hosted sessions
- Security rules
- Common mistakes

## Endpoint family
Hosted uses `/liveai/rooms`.

Hosted means LemonSlice manages STT/LLM/TTS and returns Daily join material.

## Create hosted session
Endpoint:
`POST /liveai/rooms`

Required body:
```json
{
  "agent_id": "agent_..."
}
```

Do not send self-managed fields:
- `transport_type`
- `properties`
- `agent_image_url`
- `livekit_url`
- `livekit_token`
- `daily_room_url`
- `daily_token`
- `simulcast`

## Create response
Hosted create returns:
- `room_url`
- `token`
- `image_url`
- `session_id`

## Security
Treat `token` as sensitive Daily join material.
Do not log it.
Return it only to authorized frontend code that needs to join the room.

## Get hosted session
Endpoint:
`GET /liveai/rooms/{session_id}`

Use the `session_id` returned by `POST /liveai/rooms`.

Do not use:
- Daily room slug
- full room URL
- self-managed session id

## List hosted sessions
Endpoint:
`GET /liveai/rooms`

```json
{
  "rooms": [
    {
      "agent_id": "agent_abc123",
      "session_id": "3f7c2b91-9e1f-4a6a-8e9d-2c7c3e7d9b5a",
      "created_at": "2026-04-29T20:34:56.000Z",
      "session_status": "COMPLETED",
      "credits_used": 10.5
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

## Completion metadata
```json
{
  "session_status": "COMPLETED",
  "cost": 10,
  "llm_ended_reason": "Client disconnected: 1000",
  "llm_started_at": 1772746376,
  "llm_ended_at": 1772746535,
  "messages": [
    {
      "role": "user",
      "message": "hello",
      "seconds_from_start": 0
    },
    {
      "role": "agent",
      "message": "Hello! How can I assist you today?",
      "seconds_from_start": 10
    }
  ]
}
```
