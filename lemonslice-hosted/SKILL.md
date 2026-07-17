---
name: lemonslice-hosted
description: Implement trusted backend creation and management of LemonSlice Hosted Pipeline rooms. LemonSlice owns STT/LLM/TTS/avatar generation; the app owns authorization and frontend credentials delivery.
license: MIT
---

# LemonSlice Hosted backend

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Use Hosted Pipeline when LemonSlice owns STT, LLM, TTS, and avatar generation and the application wants a custom Daily frontend.

## Security and ownership

- Call `POST /liveai/rooms` only from trusted backend code.
- Authenticate and authorize every app-owned room/session record.
- Keep `LEMONSLICE_API_KEY` and `X-API-Key` out of browser code.
- Return only the minimum Daily join material needed by the authorized user.
- Do not log raw Daily tokens.
- Store LemonSlice `session_id`, app user/tenant ownership, lifecycle status, and timestamps.
- Never authorize access based only on possession of `session_id`.

## Creation behavior

Validate complete responses, not truthiness. The official Hosted creation response includes `room_url`, `token`, `image_url`, and `session_id`.

```ts
if (
  !response.ok ||
  !body ||
  typeof body.room_url !== "string" ||
  typeof body.token !== "string" ||
  typeof body.image_url !== "string" ||
  typeof body.session_id !== "string"
) {
  throw new Error(`Invalid LemonSlice hosted response (${response.status})`);
}
```

Expect `QUEUED` during startup. Cold starts can take substantially longer when warm capacity is unavailable, so use a bounded client startup state rather than declaring API failure immediately.

The backend must not mark a session visually ready. The frontend owns first-frame detection through `lemonslice-hosted-daily`.

## Backend reconciliation

Use `GET /liveai/rooms/{session_id}` when the application needs final status, cost, timestamps, end reason, or conversation-message reconciliation.

Persist app ownership separately from LemonSlice identifiers. Reconcile abandoned clients and terminal sessions from trusted backend code.

## Startup timeout versus API failure

A UI startup timeout and an API session failure are different.

- A client may stop waiting and offer retry.
- The backend must still reconcile or terminate the earlier session.
- A retry must use newly created room credentials.
- Never reuse a stale Daily token after a terminal client attempt.

## Capabilities and lifecycle

- Route `/imagine ...` or other Hosted capability work only when the product intentionally enables it.
- Provide an app backend cleanup/reconciliation endpoint when the frontend needs to record hangup, invalidate local ownership, or reconcile a failed room.
- Treat provider errors, timeouts, and partial responses as structured failures.

Run server tests and authorization checks.

References:
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/api-reference/get-hosted-session.md
