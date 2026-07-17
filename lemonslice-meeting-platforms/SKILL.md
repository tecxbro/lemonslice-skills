---
name: lemonslice-meeting-platforms
description: Implement LemonSlice avatars joining Zoom, Google Meet, Microsoft Teams, or Webex from a LiveKit-based self-managed session. Covers plugin preference, direct endpoints, scoped broadcast tokens, meeting_bot_id, WebSocket audio tunnel, and guaranteed leave cleanup.
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

## Workflow

1. Validate the HTTPS meeting URL and supported host.
2. Create/identify the active LemonSlice self-managed `session_id`.
3. Create a least-privilege, short-lived LiveKit `broadcast_token` scoped to the intended room/publication.
4. Call `POST /liveai/sessions/{session_id}/join-meeting` from trusted backend code with:
   - `meeting_url`
   - `livekit_url`
   - `broadcast_token`
   - optional `bot_name`
5. Validate `meeting_bot_id` and `websocket_url`.
6. Persist `meeting_bot_id` against the authorized app session.
7. Connect and supervise the returned WebSocket audio tunnel.
8. Invoke leave on user hangup, join failure after partial success, WebSocket failure, timeout, cancellation, process shutdown, or session termination.
9. Revoke/expire tokens and clear stored tunnel state.

Never expose `LEMONSLICE_API_KEY` or an unrestricted broadcast token to the browser.

See `references/livekit-plugin.md` and `references/rest-endpoints.md`.

Indexed official references:
- https://lemonslice.com/docs/examples/livekit-zoom.md
- https://lemonslice.com/docs/livekit/index.md
