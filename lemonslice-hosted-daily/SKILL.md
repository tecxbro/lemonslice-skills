---
name: lemonslice-hosted-daily
description: Implement a React/Next.js Daily frontend for LemonSlice Hosted Pipeline credentials. Covers two-gate readiness, event parsing, placeholder images, image-change sequencing, retries with fresh credentials, and cleanup.
license: MIT
---

# LemonSlice Hosted Daily frontend

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

The official Hosted creation response includes `room_url`, `token`, `image_url`, and `session_id`.

A product backend may intentionally omit `image_url` from its browser response when the frontend does not use the placeholder, but it should first validate the complete upstream LemonSlice response. Never call LemonSlice REST or expose `X-API-Key` from browser code.

## State machine

Use explicit states such as `idle`, `creating_room`, `joining_daily`, `pipeline_ready`, `waiting_for_frame`, `active`, `ending`, `ended`, and `retryable_failed`.

## Placeholder image

Use `image_url` as an initialization placeholder when appropriate. Do not treat placeholder display as visual avatar readiness.

Transition to active call UI only after the actual remote avatar video track renders a frame.

## Readiness contract

1. **Pipeline readiness:** incoming Daily `app-message` where `ev.data.type === "bot_ready"`.
2. **Visual readiness:** first rendered avatar frame using `useAvatarReady` from `@lemonsliceai/avatar/react`.

`bot_ready` enables lifecycle/control eligibility but does not prove a rendered frame. Keep ringing UI until `useAvatarReady` fires.

```tsx
const avatarTrack = useMediaTrack("LemonSlice Agent", "video");

useAvatarReady(avatarTrack?.persistentTrack ?? null, {
  onReady: () => setAvatarReady(true),
});
```

Identify the agent safely using participant metadata/identity established by the backend or documented `user_name`; do not assume every remote participant is LemonSlice.

## Event directions

Incoming LemonSlice events use `ev.data.type`. Outgoing controls use `event`:

```ts
callObject.sendAppMessage({ event: "chat-msg", message: userText }, "*");
callObject.sendAppMessage({ event: "force-end" }, "*");
```

Do not confuse incoming `type` with outgoing `event`. Ignore unknown nonfatal incoming messages while recording their envelope and type in structured diagnostics.

## Image-change sequence

When runtime appearance changes are enabled, model the complete asynchronous sequence rather than a single optimistic update:

1. send the documented `/imagine ...` message through `chat-msg`;
2. mark the UI as update-requested;
3. handle generation/start/progress/completion/failure messages defensively;
4. keep the current avatar visible until a replacement track/frame is actually ready;
5. update local state only after completion and first rendered replacement frame;
6. surface failure without ending an otherwise healthy call.

Do not send another image-change request while one is active unless the documented protocol explicitly supports replacement or cancellation.

If the new image update fails, preserve the active call and existing avatar whenever the current media remains healthy. Do not promise sub-second completion.

## Failure and cleanup

Handle startup timeout, fatal `daily_error`, Daily top-level `error`, identified-agent `participant-left`, `left-meeting`, `idle_timeout`, `video_generation_error`, late events after local hangup, component unmount, and user hangup.

Retry must call the backend for fresh room credentials. Never reuse a stale Daily token after terminal failure. Clear timers, tokens, room URLs, placeholder URLs, tracks, event listeners, and call objects.

See:
- [`references/event-matrix.md`](references/event-matrix.md)
- [`references/state-machine.md`](references/state-machine.md)
- https://lemonslice.com/docs/reference/production-checklist.md
