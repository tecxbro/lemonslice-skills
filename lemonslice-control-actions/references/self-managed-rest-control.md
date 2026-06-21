# Self-Managed REST Control

## Contents
- Endpoint
- Terminate
- Update image
- Update agent prompt
- Update idle prompt
- Pose/action trigger
- Rules
- Common mistakes

## Endpoint
`POST /api/liveai/sessions/{session_id}/control`

Headers:
- `X-API-Key`
- `Content-Type: application/json`

## Terminate
```json
{
  "event": "terminate"
}
```

Meaning:

* immediately shuts down the LemonSlice avatar
* removes it from the WebRTC room
* does not necessarily mean the whole application, LiveKit room, Daily room, or agent process is deleted

Use this when the app wants to stop LemonSlice avatar generation for a self-managed session.

## Update image
```json
{
  "event": "update-image",
  "image_url": "https://example.com/avatar.jpg"
}
```

Rules:

* `image_url` must be publicly accessible.
* Image update resets the model.
* Any currently playing audio may be cut off.
* Best called when the avatar is silent.
* The image swap can take several seconds.

## Update agent prompt
```json
{
  "event": "update-agent-prompt",
  "agent_prompt": "a person talking with warm excitement"
}
```

Use for speaking-state expression/demeanor guidance.
Do not treat this as deterministic animation control.

## Update idle prompt
```json
{
  "event": "update-idle-prompt",
  "idle_prompt": "a calm person waiting attentively"
}
```

Use for idle-state expression/demeanor guidance.

## Pose/action trigger
The Actions guide documents triggering custom motion sequences with:

```json
{
  "event": "pose-trigger",
  "pose_trigger": {
    "name": "<ACTION_NAME>"
  }
}
```

Important:

* Action support depends on the avatar and LemonSlice onboarding.
* `wave` and `celebrate` are example action names from docs/examples.
* Do not promise that every avatar supports every action.
* Use an allowlist of supported action names in application code.
* If OpenAPI and prose docs differ, note the mismatch and verify against current docs before shipping code.

## Rules
- Self-managed only.
- Server-side only.
- No `/liveai/rooms/{session_id}/control`.
