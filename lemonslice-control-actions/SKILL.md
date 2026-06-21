---
name: lemonslice-control-actions
description: Advanced runtime control for already-created LemonSlice sessions. Use this when the user needs self-managed REST controls (`POST /api/liveai/sessions/{session_id}/control`), `terminate`, `update-image`, prompt updates, `pose-trigger`, LiveKit LLM tool-call actions, Hosted Daily `sendAppMessage` controls (`chat-msg`, `/imagine`, `force-end`), Widget control boundaries, readiness before control, action allowlists, and race-condition avoidance. Do not use for choosing a path or creating the initial session.
license: MIT
---

# LemonSlice Control Actions

> Guardrail: Use only after `lemonslice-integration-choice` has selected the integration path, unless the user is only asking to understand LemonSlice control/action APIs.

This is the advanced runtime-control skill for already-created LemonSlice sessions.

Use this skill for:
- terminating active self-managed sessions
- triggering supported actions such as `wave` or `celebrate`
- wiring LiveKit LLM tool calls to LemonSlice actions
- sending Hosted Daily app-message controls such as `force-end`
- updating avatar images at runtime
- updating speaking and idle prompts
- waiting for readiness before control
- avoiding race conditions and overlapping action triggers

Do not use this skill for:
- choosing the integration path
- creating sessions from scratch
- building full Hosted Daily frontend state machines
- implementing mute/unmute/media routing
- generic production hardening unrelated to runtime controls

## Official docs

- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/reference/actions.md
- https://lemonslice.com/docs/openapi.json
- https://lemonslice.com/docs/reference/best-practices.md
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/examples/avatars-tool-calling.md
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/widget/control.md

## Control surfaces

Do not mix control surfaces.

| Path | Control mechanism | Use for |
|---|---|---|
| Self-managed REST | `POST /api/liveai/sessions/{session_id}/control` | terminate, image update, prompt update, supported action trigger |
| LiveKit agent integration | server-side helper / tool-call pattern | contextual LLM-driven actions |
| Hosted Daily frontend | Daily `sendAppMessage(...)` | `chat-msg`, `/imagine`, `force-end` |
| Widget | widget element methods | mute/unmute, mic on/off, send message |

Rules:
- Self-managed REST control uses `/liveai/sessions/{session_id}/control`.
- Do not invent `POST /liveai/rooms/{session_id}/control`.
- Hosted Daily controls go through Daily app messages.
- Widget controls are not action controls; they are widget UI/audio/message methods.

## Self-managed REST control

Endpoint:

```http
POST https://lemonslice.com/api/liveai/sessions/{session_id}/control
X-API-Key: <server-side LemonSlice API key>
Content-Type: application/json
```

Use this only from trusted backend/server code.

Never expose `X-API-Key` or `LEMONSLICE_API_KEY` to browser, mobile, or public frontend code.

Success response:

```json
{
  "success": true
}
```

### Terminate

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

### Update image

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

### Update agent prompt

```json
{
  "event": "update-agent-prompt",
  "agent_prompt": "a person talking with warm excitement"
}
```

Use for speaking-state expression/demeanor guidance.
Do not treat this as deterministic animation control.

### Update idle prompt

```json
{
  "event": "update-idle-prompt",
  "idle_prompt": "a calm person waiting attentively"
}
```

Use for idle-state expression/demeanor guidance.

### Pose/action trigger

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

## Action names and supported actions

Actions are specific custom motion sequences such as pointing, waving, cheering, celebrating, swaying, or branded gestures.

Rules:
- Natural hand gestures happen automatically while the avatar speaks.
- Custom actions are advanced and may require LemonSlice onboarding.
- Do not let the LLM invent arbitrary action names.
- Use a controlled internal action allowlist.
- Treat `wave` and `celebrate` as documented examples, not a full enum.
- Surface unsupported actions as safe errors or disabled UI states.

## LiveKit LLM tool-call action pattern

Use LLM tool calls when the action should be triggered by conversational context.

Example pattern:

```python
from livekit.agents import Agent, function_tool

class Assistant(Agent):
    @function_tool()
    async def celebrate(self) -> str:
        """Call this function when the user shares positive news."""
        return await self.trigger_action("celebrate")
```

Rules:

* Keep the tool name semantically clear.
* Use the tool docstring to tell the LLM when to call it.
* Map the tool to a supported internal action name.
* Keep the actual LemonSlice control call server-side.
* Do not expose LemonSlice API keys to the frontend.
* Do not let the LLM pass arbitrary raw action names directly to LemonSlice.

## Readiness before control

Never send control events before the avatar is ready.

Do not treat these as readiness:
- session creation success
- receiving `session_id`
- receiving `room_url` / `token`
- Daily room join success
- LiveKit participant join alone
- first remote track alone

Use the integration-specific readiness signal.

Hosted Daily:
- wait for `bot_ready` from Daily `app-message`

LiveKit:
- wait for LemonSlice `bot_ready` on the LemonSlice RPC/data channel

Self-managed status:
- use session/integration readiness and avoid sending controls to `QUEUED`, terminal, failed, or unknown sessions

Startup action pattern:
1. Start the avatar session.
2. Wait for avatar readiness.
3. Trigger action such as `wave`.
4. Continue greeting/conversation.

## Avoiding race conditions

Use a control dispatcher or equivalent guard.

The dispatcher should track:
- `isAvatarReady`
- `isTerminated`
- `actionInFlight`
- `imageUpdateInFlight`
- current session id
- terminal error state

Rules:
- Reject controls before readiness.
- Reject controls after terminate.
- Debounce repeated clicks.
- Avoid overlapping action triggers.
- Avoid image updates while audio is playing unless interruption is acceptable.
- Clear queued controls on timeout, disconnect, fatal error, or termination.
- Do not retry stale controls against a new session id unless the app explicitly remaps them.

```ts
type AvatarControlCommand =
  | { type: "terminate" }
  | { type: "triggerAction"; name: string }
  | { type: "updateImage"; imageUrl: string }
  | { type: "updateAgentPrompt"; agentPrompt: string }
  | { type: "updateIdlePrompt"; idlePrompt: string }

async function dispatchAvatarControl(command: AvatarControlCommand) {
  assertAvatarReady()
  assertNotTerminated()
  assertNoConflictingActionInFlight(command)
  // Send through the selected control surface.
}
```

## Hosted Daily controls

Hosted Daily is not self-managed REST control.

Hosted Daily means LemonSlice manages STT/LLM/TTS and the frontend joins a Daily room returned by `POST /liveai/rooms`.

Control is sent through Daily app messages.

### Send text

```ts
sendAppMessage(
  {
    event: "chat-msg",
    message: "Your message here",
    name: "User"
  },
  "*"
)
```

### Force end

```ts
sendAppMessage(
  { event: "force-end" },
  "*"
)
```

Behavior:

* immediately stops the realtime agent
* agent leaves the room
* billing stops
* frontend must still leave/cleanup local Daily state

After `force-end`:

* disable controls
* transition UI to ending/ended
* call Daily `leave()` where appropriate
* clear timers
* clear stale credentials
* clear queued controls

## Hosted Daily image updates with `/imagine`

For Hosted Daily, avatar image updates are sent as a `chat-msg` beginning with `/imagine`.

```ts
sendAppMessage(
  {
    event: "chat-msg",
    message: "/imagine being in front of a fireplace",
    name: "User"
  },
  "*"
)
```

Rules:

* `/imagine` does not trigger a spoken response.
* It regenerates the avatar image from the prompt.
* The avatar retains core identity and proportions.
* The agent continues normal interaction after the image update completes.
* The agent must allow users to modify appearance.
* Do not invent a hosted REST image update endpoint.

Handle these Hosted Daily image events:

* `image_change_requested`
* `image_created`
* `image_change_complete`
* `image_change_error`

## Hosted Daily event handling for controls

For Hosted Daily, listen to Daily `app-message`.

Required events:
- `bot_ready`
- `idle_timeout`
- `daily_error`
- `video_generation_error`
- `image_change_requested`
- `image_created`
- `image_change_complete`
- `image_change_error`

Control implications:
- enable controls only after `bot_ready`
- disable controls on `idle_timeout`
- disable or fail controls on fatal `daily_error`
- treat `video_generation_error` as avatar-path failure
- show image update progress from image-change events
- clear queued controls if the room ends or agent leaves

## Widget control boundary

Widget controls are not the same as self-managed session actions.

The widget exposes methods such as:
- `mute()`
- `unmute()`
- `isMuted()`
- `micOn()`
- `micOff()`
- `sendMessage(message)`

Rules:
- Do not document `pose-trigger`, `terminate`, or `/liveai/sessions/{session_id}/control` as widget methods.
- If the user is controlling the no-backend widget, route deeper work to `lemonslice-widget`.
- This skill may mention widget controls only to prevent mixing them with advanced session actions.

## Common mistakes

- Sending controls before `bot_ready`.
- Treating session creation as avatar readiness.
- Treating Daily join success as avatar readiness.
- Treating participant join as avatar readiness.
- Calling LemonSlice REST APIs directly from frontend code.
- Exposing `X-API-Key` or `LEMONSLICE_API_KEY` in browser/mobile code.
- Inventing `POST /liveai/rooms/{session_id}/control`.
- Using Hosted Daily `force-end` for self-managed REST sessions.
- Using self-managed `terminate` as if it were a Daily frontend hangup.
- Hardcoding `wave` or `celebrate` without checking avatar support.
- Letting the LLM invent arbitrary action names.
- Sending overlapping action triggers without a dispatcher.
- Updating image while the avatar is speaking and then being surprised that audio cuts off.
- Treating prompt updates as deterministic animation commands.
- Forgetting to clear queued controls after terminate, timeout, error, or disconnect.
- Confusing Widget methods with session/action controls.

## Agent workflow

1. Confirm the selected integration path.
2. Identify the control surface:
   - self-managed REST
   - LiveKit tool-call helper
   - Hosted Daily app-message
   - Widget element methods
3. Confirm avatar readiness before control.
4. Confirm the command is supported for the selected control surface.
5. Validate the exact request/event shape.
6. Check API key safety.
7. Add guardrails for race conditions and overlapping controls.
8. Add terminal-state cleanup.
9. Route to another skill if the task is actually session creation, Hosted Daily UI, Widget embed, or raw API reference work.

## Validation checklist

- [ ] Did `lemonslice-integration-choice` select or confirm the path?
- [ ] Is the selected path self-managed REST, LiveKit, Hosted Daily, or Widget?
- [ ] If self-managed, does control use `POST /api/liveai/sessions/{session_id}/control`?
- [ ] If self-managed, is `X-API-Key` server-side only?
- [ ] If self-managed, are event bodies limited to documented shapes?
- [ ] Is `terminate` used only for the self-managed control endpoint?
- [ ] Is `pose-trigger` documented as an Actions-guide pattern and verified against current docs/avatar support?
- [ ] Are action names allowlisted or verified for the avatar?
- [ ] Does LiveKit LLM tool calling map tools to supported internal action names?
- [ ] Does the implementation wait for `bot_ready` or equivalent readiness before controls?
- [ ] Is there a startup timeout if readiness never arrives?
- [ ] Is there an action dispatcher, debounce, lock, or queue policy?
- [ ] Are image updates guarded because they can interrupt audio?
- [ ] Are `update-agent-prompt` and `update-idle-prompt` treated as high-level demeanor guidance?
- [ ] If Hosted Daily, does control use `sendAppMessage`, not REST `/rooms/.../control`?
- [ ] If Hosted Daily, does hangup send `force-end` and still run local Daily cleanup?
- [ ] If Hosted Daily, is `/imagine` sent through `chat-msg` only?
- [ ] If Widget, are only widget-supported methods documented?
- [ ] Are terminal states/errors clearing queued controls and stale session state?
