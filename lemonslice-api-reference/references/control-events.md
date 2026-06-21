# Control Events

## Contents
- Control endpoint
- Terminate
- Update image
- Update agent prompt
- Update idle prompt
- Pose/action trigger
- Control rules
- Common mistakes

## Endpoint
Self-managed control endpoint:
`POST /liveai/sessions/{session_id}/control`

Full URL:
`https://lemonslice.com/api/liveai/sessions/{session_id}/control`

Headers:
- `X-API-Key`
- `Content-Type: application/json`

Success:
```json
{
  "success": true
}
```

## Terminate
```json
{
  "event": "terminate"
}
```

## Update image
```json
{
  "event": "update-image",
  "image_url": "https://example.com/avatar.jpg"
}
```

## Update agent prompt
```json
{
  "event": "update-agent-prompt",
  "agent_prompt": "a person talking"
}
```

## Update idle prompt
```json
{
  "event": "update-idle-prompt",
  "idle_prompt": "a serious person"
}
```

## Pose/action trigger
```json
{
  "event": "pose-trigger",
  "pose_trigger": {
    "name": "<ACTION_NAME>"
  }
}
```

## Rules
- Control endpoint is self-managed only.
- Do not invent `POST /liveai/rooms/{session_id}/control`.
- Action names must be supported for the avatar.
- Wait for readiness before sending actions.
