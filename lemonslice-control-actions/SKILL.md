---
name: lemonslice-control-actions
description: Add trusted LemonSlice runtime controls for self-managed REST, LiveKit tool calls, or Hosted Daily messages. Covers auth conflict handling, readiness gates, image and prompt updates, provisioned actions, and termination.
license: MIT
---

# LemonSlice runtime controls

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Use only after the base integration path is known.

## Readiness

Controls require **pipeline readiness** (`bot_ready`). User-facing “avatar visible” UI still requires a first rendered frame. Do not merge these gates.

## Self-managed control endpoint

`POST /liveai/sessions/{session_id}/control`

Keep it in trusted server code. Current documentation conflicts on control authentication; follow the source-of-truth rule in `lemonslice-api-reference` and preserve known-working behavior.

The current raw control contract uses these event names:

- `terminate`
- `update-image`
- `update-agent-prompt`
- `update-idle-prompt`
- `pose-trigger`

Do not describe `reset_idle_timeout` as part of the current raw control contract unless it appears in a newly verified endpoint schema.

Only actions provisioned for the current account and character may be triggered. Never translate arbitrary LLM prose directly into a `pose-trigger` name.

## Application adapter

Do not let an LLM call LemonSlice directly or invent action names. Expose a narrow application helper:

```ts
const ALLOWED_ACTIONS = new Set([
  // Populate from the app's provisioned LemonSlice action catalog.
] as const);

type AllowedAvatarAction = typeof ALLOWED_ACTIONS extends Set<infer T>
  ? T
  : never;

type AvatarControl =
  | { event: "terminate" }
  | { event: "update-image"; image_url: string }
  | { event: "update-agent-prompt"; agent_prompt: string }
  | { event: "update-idle-prompt"; idle_prompt: string }
  | {
      event: "pose-trigger";
      pose_trigger: {
        name: AllowedAvatarAction;
      };
    };

async function controlAvatar(
  ownedSessionId: string,
  control: AvatarControl,
): Promise<void> {
  await assertUserOwnsSession(ownedSessionId);

  if (
    control.event === "pose-trigger" &&
    !ALLOWED_ACTIONS.has(control.pose_trigger.name)
  ) {
    throw new Error("Avatar action is not provisioned");
  }

  await lemonSliceControlClient.send(ownedSessionId, control);
}
```

## Update-image behavior

`update-image` resets the avatar model. Audio currently playing may be cut off, so invoke it while the avatar is silent when possible.

Treat the control response as acknowledgement only. It does not prove that the new avatar frame is visible. Keep the existing frame until the replacement track/frame is ready.

Do not send a second image update while one is active unless the documented protocol explicitly supports replacement or cancellation. If replacement fails and the current media remains healthy, preserve the active call and existing avatar.

## Hosted Daily

Outgoing app messages use `event`, for example `chat-msg` and `force-end`. Incoming lifecycle messages use `ev.data.type`. Route `/imagine` only when intentionally enabled and track the full asynchronous update lifecycle.

## Safety and cleanup

Validate URLs and prompts, rate-limit controls, avoid overlapping actions, log session IDs but not credentials, and terminate on explicit hangup. Report control-authentication conflicts rather than claiming one universal rule.

References:
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/reference/actions.md
- https://lemonslice.com/docs/reference/realtime-updates.md
