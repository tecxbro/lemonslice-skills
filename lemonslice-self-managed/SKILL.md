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
- JSON requests use exactly one of `agent_id` or `agent_image_url`; multipart requests can upload the image file directly.
- The current endpoint schema exposes `model`, `aspect_ratio`, `simulcast`, and recording configuration. Validate the live schema before using volatile options.
- Validate the full response shape and persist `session_id` against an authorized app-owned record.
- Use an abortable request timeout and structured errors.
- Implement explicit termination and lifecycle cleanup.

## Plugin/docs drift

Raw REST and framework plugins can expose different constructor fields or release on different schedules. Inspect the current endpoint schema for REST calls and the installed package signature for LiveKit/Pipecat code. Never assume an option supported by one surface is accepted by another.

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
      model: "flash",
      aspect_ratio: "1x1",
      simulcast: true,
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
