---
name: lemonslice-hosted-daily
description: Builds browser or React/Next.js Daily frontends for Lemon Slice Hosted Pipeline sessions. Use when the app backend already returns hosted Daily join material such as room_url and token.
license: MIT
---

# Lemon Slice Hosted Daily Frontend

## Official docs
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/examples/hosted-daily-app.md
- https://lemonslice.com/docs/reference/best-practices.md

## Use this skill when
- The app is building a custom browser, React, or Next.js frontend.
- Lemon Slice Hosted Pipeline is selected.
- The app backend already creates hosted sessions or will be implemented through `lemonslice-hosted`.
- Frontend receives `room_url` and `token`.

## Do not use this skill when
- Creating hosted rooms on backend → `lemonslice-hosted`
- Using LiveKit → `lemonslice-livekit`
- Using Pipecat → `lemonslice-pipecat`
- Using self-managed REST → `lemonslice-self-managed`
- Using Widget → `lemonslice-widget`
- Debugging raw REST → `lemonslice-api-reference`
- Only adding runtime controls → `lemonslice-control-actions`

## Core rules
- Frontend calls app backend, not Lemon Slice directly.
- Frontend must never contain `LEMONSLICE_API_KEY`.
- Frontend must never send `X-API-Key`.
- Frontend receives `room_url` and `token`.
- Treat `token` as sensitive join material.
- Daily join success is not avatar readiness.
- Active UI starts only after `bot_ready`.
- Retry should request fresh credentials from backend.

## Reference files
Load only the reference file needed for the frontend task:

- `references/daily-join-state-machine.md` — read when implementing the Daily join flow, UI states, startup timeout, and retry behavior.
- `references/events-controls-cleanup.md` — read when wiring Daily `app-message`, `bot_ready`, `force-end`, `/imagine`, participant leave, errors, and cleanup.
- `references/react-nextjs-patterns.md` — read when implementing Hosted Daily UI in React or Next.js.

## Common mistakes
- Calling LemonSlice REST APIs directly from React/browser code.
- Putting `LEMONSLICE_API_KEY` in `NEXT_PUBLIC_*` or any frontend env var.
- Logging the Daily `token`.
- Treating Daily join success as avatar readiness.
- Treating participant join as readiness instead of `bot_ready`.
- Forgetting to listen to `app-message`.
- Forgetting startup timeout when `bot_ready` never arrives.
- Retrying with stale `room_url` / `token`.
- Not cleaning up on `participant-left`.
- Not calling `leave()` on failure, timeout, or component unmount.
- Forgetting to send `force-end` for intentional user hangup when appropriate.
- Building backend room creation inside this skill instead of routing to `lemonslice-hosted`.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` select Hosted Daily?
- [ ] Is this frontend Daily UI work, not hosted backend creation?
- [ ] Does the frontend receive `room_url` and `token` from the app backend?
- [ ] Does the frontend avoid direct LemonSlice REST API calls?
- [ ] Is `LEMONSLICE_API_KEY` absent from all frontend/browser/public env code?
- [ ] Is the Daily `token` treated as sensitive join material?
- [ ] Does the frontend join Daily with `room_url` and `token`?
- [ ] Does UI wait for `bot_ready` before entering `active`?
- [ ] Are LemonSlice events handled through `app-message`?
- [ ] Are `idle_timeout`, `daily_error`, and `video_generation_error` handled?
- [ ] Is `participant-left` handled with cleanup logic?
- [ ] Is there a startup timeout if `bot_ready` never arrives?
- [ ] Does timeout call `leave()` and show retry UI?
- [ ] Does retry create/request fresh credentials instead of blindly reusing stale ones?
- [ ] Is there a clear state machine?
- [ ] Does user hangup run cleanup and send `force-end` where appropriate?
- [ ] Are timers cleared on success, failure, hangup, and component unmount?
- [ ] Does React/Next.js code keep Daily UI client-side and room creation server-side?
