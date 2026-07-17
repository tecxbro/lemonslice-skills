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
- Raw REST currently documents exactly one of `agent_id` or `agent_image_url`.
- Validate the full response shape and persist `session_id` against an authorized app-owned record.
- Use an abortable request timeout and structured errors.
- Implement explicit termination and lifecycle cleanup.

## Plugin/docs drift

LiveKit and Pipecat integration docs expose `model` and `aspect_ratio`, while the downloadable raw REST OpenAPI can lag or omit plugin fields. Do not send plugin-only fields through direct REST unless the current endpoint schema or a tested API version supports them.

## Meeting routing

External Zoom, Google Meet, Microsoft Teams, or Webex requests route to `lemonslice-meeting-platforms`. That workflow currently requires a LiveKit-based self-managed session.

## Example server request

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
      idle_timeout: 600,
      properties: {
        livekit_url: input.livekitUrl,
        livekit_token: input.livekitToken,
      },
    }),
    signal: controller.signal,
  });

  const body = await response.json().catch(() => null);
  if (!response.ok || !body || typeof body.session_id !== "string") {
    throw new Error(`LemonSlice session create failed (${response.status})`);
  }
  return { sessionId: body.session_id };
} finally {
  clearTimeout(timeout);
}
```

Never return raw API keys or unrestricted transport tokens. Run available checks and verify cleanup paths.

References:
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/openapi.json
