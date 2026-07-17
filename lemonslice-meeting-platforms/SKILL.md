---
name: lemonslice-meeting-platforms
description: Implement LemonSlice avatars joining Zoom, Google Meet, Microsoft Teams, or Webex from a LiveKit-based self-managed session. Covers external admission, explicit states, scoped tokens, meeting_bot_id persistence, audio tunnel supervision, and retry-safe leave cleanup.
license: MIT
---

# LemonSlice third-party meeting platforms

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Trigger for Zoom, Google Meet, Microsoft Teams, Webex, meeting bot, `join-meeting`, `leave-meeting`, `meeting_bot_id`, `broadcast_token`, or external conference avatar.

## Preconditions

1. Confirm the LemonSlice session is **LiveKit-based self-managed**.
2. Do not use meeting endpoints for an ordinary LiveKit room.
3. Inspect the installed LiveKit LemonSlice plugin version.
4. Prefer supported plugin functionality when available.
5. Use direct REST only when explicitly required or plugin support is unavailable.

Do not promise successful admission to the meeting. External lobbies, authentication, host approval, bot policies, meeting permissions, capacity, and platform outages remain outside LemonSlice session readiness.

## State model

Represent at least:

- `session_ready`
- `joining_external_meeting`
- `waiting_in_lobby`
- `joined`
- `audio_tunnel_active`
- `leaving`
- `left`
- `failed`

Do not collapse `session_ready` into `joined`; the external platform can reject or delay admission after the LemonSlice session is healthy.

## Workflow

1. Validate the HTTPS meeting URL and supported host.
2. Create or identify the active self-managed `session_id`.
3. Create a least-privilege, short-lived LiveKit `broadcast_token` scoped to the intended room/publication.
4. Call `POST /liveai/sessions/{session_id}/join-meeting` from trusted backend code with `meeting_url`, `livekit_url`, `broadcast_token`, and optional `bot_name`.
5. Validate `meeting_bot_id` and `websocket_url`.
6. Persist `meeting_bot_id` immediately after join succeeds, before opening later resources that may fail.
7. Connect and supervise the returned WebSocket audio tunnel.
8. Model lobby/waiting/admission separately from LemonSlice pipeline readiness.
9. Invoke leave on user hangup, join failure after partial success, lobby timeout, WebSocket failure, cancellation, process shutdown, or session termination.
10. Revoke/expire tokens and clear stored tunnel state.

## Idempotency

The leave operation must be safe to retry after partial failures. Persist enough ownership and meeting-bot state to reconcile a browser crash or backend restart. Treat already-left/not-found outcomes according to the current endpoint contract rather than creating duplicate bots.

Never expose `LEMONSLICE_API_KEY` or an unrestricted broadcast token to the browser.

## Agora

Only apply an Agora path when the task actually involves Agora conferencing and current official integration documentation or an inspectable SDK exists. Do not assume Agora follows the Zoom/Meet/Teams/Webex meeting-bot workflow, and do not invent a raw `transport_type` value.

See:
- [`references/livekit-plugin.md`](references/livekit-plugin.md)
- [`references/rest-endpoints.md`](references/rest-endpoints.md)
- https://lemonslice.com/docs/examples/livekit-zoom.md
- https://lemonslice.com/docs/livekit/index.md
