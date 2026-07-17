---
name: lemonslice-hosted-daily
description: Implement a React/Next.js Daily frontend for LemonSlice Hosted Pipeline credentials. Covers two-gate readiness, event parsing, complete image-change sequence, safe participant identification, retries with fresh credentials, and cleanup.
license: MIT
---

# LemonSlice Hosted Daily frontend

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Assume a trusted backend returns `room_url`, `token`, optional `image_url`, and `session_id`. Never call LemonSlice REST or expose `X-API-Key` from browser code.

## State machine

Use explicit states such as `idle`, `creating_room`, `joining_daily`, `pipeline_ready`, `waiting_for_frame`, `active`, `ending`, `ended`, and `retryable_failed`.

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

Incoming LemonSlice events use `ev.data.type`:

- `bot_ready`
- `idle_timeout`
- `daily_error`
- `video_generation_error`
- transcription and image-update lifecycle events documented by Hosted Daily

Outgoing controls use `event`:

```ts
callObject.sendAppMessage({ event: "chat-msg", message: userText }, "*");
callObject.sendAppMessage({ event: "force-end" }, "*");
```

Do not confuse incoming `type` with outgoing `event`.

## Image-change sequence

When runtime appearance changes are enabled, model the complete asynchronous sequence rather than a single optimistic update:

1. send the documented `/imagine ...` message through `chat-msg`;
2. mark the UI as update-requested;
3. handle the documented generation/start/progress/completion/failure app-messages defensively;
4. keep the current avatar visible until a replacement track/frame is actually ready;
5. update local state only after completion/first rendered replacement frame;
6. surface failure without ending an otherwise healthy call.

Do not promise sub-second completion; image updates may take several seconds.

## Failure and cleanup

Handle:

- startup timeout;
- fatal `daily_error` during startup or call;
- Daily top-level `error`;
- `participant-left` for the identified agent;
- `left-meeting`;
- `idle_timeout`;
- `video_generation_error`;
- component unmount and user hangup.

Retry must call the backend for fresh room credentials. Never reuse a stale Daily token after terminal failure. Clear timers, tokens, room URLs, tracks, and call objects.

See:
- `references/event-matrix.md`
- `references/state-machine.md`
- https://lemonslice.com/docs/reference/production-checklist.md
