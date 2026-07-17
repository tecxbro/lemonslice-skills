---
name: lemonslice-self-managed
description: Implement raw LemonSlice self-managed sessions when the developer owns STT/LLM/TTS and no supported LiveKit or Pipecat plugin should own session creation.
license: MIT
---

# LemonSlice self-managed integration

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Prefer framework plugins when the repository already uses LiveKit Agents or Pipecat. Use raw REST only for a genuinely custom stack.

## Contract

- Create with `POST /liveai/sessions`, not `/liveai/rooms`.
- Keep `X-API-Key` in trusted server code.
- Use `transport_type: "livekit"` or `"daily"` and the matching transport properties.
- JSON requests use exactly one of `agent_id` or `agent_image_url`; reject both and reject neither.
- The verified OpenAPI also declares `multipart/form-data` with `image` and `payload`. Do not assume file upload support when a future snapshot omits that media type.
- The current raw contract documents `agent_prompt`, `agent_idle_prompt`, `idle_timeout`, `response_done_timeout`, `aspect_ratio`, `model`, and LiveKit-only `simulcast`.
- Raw REST, LiveKit plugins, and Pipecat are separate surfaces. Never copy a field between them without checking the current OpenAPI or installed constructor signature.
- Validate the full response shape and persist `session_id` against an authorized app-owned record.
- Use an abortable request timeout and structured errors.
- Implement explicit termination and lifecycle cleanup.

## Meeting routing

External Zoom, Google Meet, Microsoft Teams, or Webex requests route to `lemonslice-meeting-platforms`. That workflow currently requires a LiveKit-based self-managed session.

## Example JSON request

Keep the baseline request minimal; add model or rendering options only when the current snapshot and account support them.

```ts
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 20_000);

try {
  const response = await fetch("https://lemonslice.com/api/liveai/sessions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.LEMONSLICE_API_KEY!,
    },
    body: JSON.stringify({
      agent_image_url: input.agentImageUrl,
      transport_type: "livekit",
      agent_prompt: "a warm person speaking naturally",
      agent_idle_prompt: "a calm attentive person",
      idle_timeout: 600,
      response_done_timeout: 0.5,
      simulcast: true,
      properties: {
        livekit_url: input.livekitUrl,
        livekit_token: input.livekitToken,
      },
    }),
    signal: controller.signal,
  });

  const text = await response.text();
  let body: unknown = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    // Preserve a redacted non-JSON body in trusted diagnostics.
  }

  if (
    !response.ok ||
    !body ||
    typeof body !== "object" ||
    typeof (body as { session_id?: unknown }).session_id !== "string"
  ) {
    throw new Error(`LemonSlice session create failed (${response.status})`);
  }

  return { sessionId: (body as { session_id: string }).session_id };
} finally {
  clearTimeout(timeout);
}
```

## Session status

Use `GET /liveai/sessions/{session_id}` when the application needs backend reconciliation or status polling.

Handle:

- `QUEUED`
- `ACTIVE`
- `COMPLETED`
- `TIMED_OUT`
- `FAILED`

Do not treat `QUEUED` as immediate failure. Warm capacity may start in seconds, while a cold start can take substantially longer. Startup timeouts should be bounded but not unrealistically short; current status documentation says a cold start can take roughly 2.5 minutes.

Never return raw API keys or unrestricted transport tokens. Run available checks and verify cleanup paths.

References:
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md
- https://lemonslice.com/docs/openapi.json
