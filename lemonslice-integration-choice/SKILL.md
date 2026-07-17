---
name: lemonslice-integration-choice
description: Route ambiguous LemonSlice requests to the correct primary implementation skill and add only materially relevant secondary skills. Do not use when the integration path is already explicit.
license: MIT
---

# LemonSlice integration choice

## Route directly when explicit

- New project, official starter, fastest recommended setup, or Quickstart → `lemonslice-quickstart`
- Existing LiveKit Agents app, `AvatarSession`, `AgentSession`, or `JobContext` → `lemonslice-livekit`
- Existing Pipecat pipeline, even when Pipecat uses Daily → `lemonslice-pipecat`
- Custom raw LiveKit or Daily transport → `lemonslice-self-managed`
- Hosted room backend → `lemonslice-hosted`
- Hosted Daily frontend → `lemonslice-hosted-daily`
- Widget/custom element/no-backend embed → `lemonslice-widget`
- Zoom, Google Meet, Teams, Webex, or `join-meeting` → `lemonslice-meeting-platforms`
- Exact REST schema or docs conflict → `lemonslice-api-reference`
- Production audit → `lemonslice-production-patterns`

Do not force every LemonSlice request through this router.

## Feature chaining

Choose one primary implementation skill. Add secondary skills only when their concerns are materially part of the request.

- Runtime image, prompt, idle, provisioned motion, or terminate → base skill + `lemonslice-control-actions`
- Model, image framing, aspect ratio, chroma key, or green screen → base skill + `lemonslice-appearance-rendering`
- Lifecycle, latency, failure, capacity, or cleanup hardening → base skill + `lemonslice-production-patterns`
- Exact raw endpoint validation → base skill + `lemonslice-api-reference`

Examples:

- LiveKit + Production Patterns
- LiveKit + Appearance Rendering
- Hosted + Hosted Daily
- Self-Managed + Control Actions
- Meeting Platforms + Production Patterns

## Agora guardrail

For an explicit Agora request, inspect current official Agora integration documentation or an installed SDK first. Do not invent `transport_type: "agora"`; the verified raw enum currently exposes `livekit` and `daily`.

## Resolve ambiguous requests

Inspect the repository first. Determine:

1. whether this is a new project or an existing architecture;
2. who owns STT, VAD/turn detection, LLM, and TTS;
3. which realtime framework already exists;
4. whether the output is a widget, custom frontend, or avatar-only media layer;
5. whether the target is an ordinary WebRTC room or an external meeting platform;
6. whether runtime control, rendering, or production hardening is also required.

| Evidence | Primary skill |
| --- | --- |
| Empty/new repository and official starter request | `lemonslice-quickstart` |
| `livekit-agents`, `@livekit/agents`, `AgentSession`, `JobContext` | `lemonslice-livekit` |
| Pipecat pipeline and Daily transport | `lemonslice-pipecat` |
| LemonSlice owns STT/LLM/TTS and backend creates `/liveai/rooms` | `lemonslice-hosted` |
| Browser receives Hosted `room_url` and Daily token | `lemonslice-hosted-daily` |
| `<lemonslice-widget>` or no-backend embed | `lemonslice-widget` |
| Developer owns STT/LLM/TTS without a supported plugin | `lemonslice-self-managed` |
| External conference URL | `lemonslice-meeting-platforms` |

State the selected primary path and one-sentence reason, then implement using it. Do not replace an existing architecture merely because another integration is easier to demonstrate.
