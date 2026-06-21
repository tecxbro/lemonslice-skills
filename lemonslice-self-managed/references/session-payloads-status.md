# Session Payloads and Status

## Contents
- Create request examples
- Transport type
- Transport properties
- Optional fields
- Get session / status polling
- Lifecycle states

## Create request examples
#### LiveKit transport example
```json
{
  "transport_type": "livekit",
  "agent_id": "agent_abc123",
  "properties": {
    "livekit_url": "wss://example.livekit.cloud",
    "livekit_token": "..."
  }
}
```

#### Daily transport example
```json
{
  "transport_type": "daily",
  "agent_image_url": "https://example.com/avatar.png",
  "properties": {
    "daily_room_url": "https://your-domain.daily.co/your-room",
    "daily_token": "..."
  }
}
```

## Transport type
`transport_type` tells LemonSlice how the agent audio is delivered and how the synced A/V is returned.

Allowed:
- `livekit`
- `daily`

Not allowed:
- `webrtc`
- `browser`
- `hosted`
- `rooms`
- `pipecat`
- `tavus`
- arbitrary provider names

## Transport properties
`properties` contains transport-specific connection details.

For `transport_type: "livekit"`:
- `properties.livekit_url` is required.
- `properties.livekit_token` is required.
- `simulcast` is available only with LiveKit transport.

For `transport_type: "daily"`:
- `properties.daily_room_url` is optional.
- `properties.daily_token` is optional.
- If `daily_room_url` is omitted, LemonSlice can create a Daily room, with additional cost.
- Daily recording config belongs inside Daily transport properties, not as generic top-level fields.

## Optional fields
| Field | Purpose | Notes |
|---|---|---|
| `agent_prompt` | Influences speaking-state expression/demeanor | High-level, not precise deterministic control |
| `agent_idle_prompt` | Influences idle-state expression/demeanor | High-level idle behavior |
| `idle_timeout` | Seconds before idle timeout | Default 60; negative disables idle timeout |
| `response_done_timeout` | Seconds without new audio before response is treated complete | Useful for TTS providers without reliable end events |
| `simulcast` | Publishes multiple video resolutions | LiveKit transport only |

## Get session / status polling
Use `GET /api/liveai/sessions/{session_id}` when the backend needs status or completion metadata.

The response always includes `session_status`.

When the session is completed, it may include `cost`.

## Lifecycle states
- `QUEUED`: session is waiting for a GPU container. Usually quick when warm capacity exists; cold start can take longer.
- `ACTIVE`: avatar is live.
- `COMPLETED`: session ended successfully. Completed responses may include `cost`.
- `TIMED_OUT`: GPU container timed out.
- `FAILED`: session ended with an error.
