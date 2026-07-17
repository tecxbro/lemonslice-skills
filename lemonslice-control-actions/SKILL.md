---
name: lemonslice-control-actions
description: Add trusted LemonSlice runtime controls for self-managed REST, LiveKit tool calls, or Hosted Daily messages. Covers auth conflict handling, readiness gates, image/prompt updates, idle reset, actions, and termination.
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

Supported control categories include:

- terminate;
- update image/appearance;
- update speaking prompt;
- update idle prompt;
- reset idle timeout;
- supported action/emotion controls when enabled for that account/avatar.

Image updates are asynchronous and may take several seconds. Do not promise `<1s` or immediately claim the replacement frame is visible.

## Application adapter

Do not let an LLM call LemonSlice directly or invent action names. Expose a narrow application helper:

```ts
type AvatarControl =
  | { event: "terminate" }
  | { event: "reset_idle_timeout" }
  | { event: "update_agent_prompt"; prompt: string }
  | { event: "update_idle_prompt"; prompt: string }
  | { event: "update_image"; image_url: string }
  | { event: "action"; name: AllowedAvatarAction };

async function controlAvatar(
  ownedSessionId: string,
  control: AvatarControl,
): Promise<void> {
  await assertUserOwnsSession(ownedSessionId);
  await lemonSliceControlClient.send(ownedSessionId, control);
}
```

`AllowedAvatarAction` must come from the application's provisioned allowlist. Enterprise actions require character-specific onboarding; never accept arbitrary model-generated action names.

## Hosted Daily

Outgoing app messages use `event`, for example `chat-msg` and `force-end`. Incoming lifecycle messages use `ev.data.type`. Route `/imagine` only when intentionally enabled and track the full asynchronous update lifecycle.

## Safety and cleanup

Validate URLs/prompts, rate-limit controls, avoid overlapping actions, log session IDs but not credentials, and terminate on explicit hangup. Report the control-auth and reset-idle OpenAPI conflicts.

References:
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/reference/actions.md
