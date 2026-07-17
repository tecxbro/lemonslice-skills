---
name: lemonslice-integration-choice
description: Route ambiguous LemonSlice integration requests to the correct implementation path. Use when the user has not made clear who owns STT/LLM/TTS, which WebRTC framework is used, or whether they want a widget, hosted pipeline, self-managed pipeline, third-party meeting bot, runtime control, or rendering/compositing. Do not use when the implementation path is already explicit.
license: MIT
---

# LemonSlice integration choice

## Route directly when explicit

- LiveKit Agents or `AvatarSession` → `lemonslice-livekit`
- Pipecat or `LemonSliceTransport` → `lemonslice-pipecat`
- Hosted room backend → `lemonslice-hosted`
- Hosted Daily frontend → `lemonslice-hosted-daily`
- Widget/custom element → `lemonslice-widget`
- Zoom, Google Meet, Teams, Webex, `join-meeting` → `lemonslice-meeting-platforms`
- Runtime image/prompt/action/terminate → `lemonslice-control-actions`
- Lite/Flash/Pro, aspect ratio, image framing, green screen → `lemonslice-appearance-rendering`
- Production audit → `lemonslice-production-patterns`
- Exact REST schema/debugging → `lemonslice-api-reference`

Do not force every LemonSlice request through this router.

## Resolve ambiguous requests

Inspect the repository first. Determine:

1. Who owns STT, LLM, and TTS?
2. Which realtime framework already exists?
3. Is the requested output a prebuilt widget, custom frontend, or avatar-only media layer?
4. Is the target an ordinary WebRTC room or an external meeting platform?
5. Is the user asking for initial integration, runtime control, or visual rendering?

Routing:

| Evidence | Primary skill |
| --- | --- |
| `livekit-agents`, `@livekit/agents`, `AgentSession`, `JobContext` | `lemonslice-livekit` |
| Pipecat pipeline and Daily transport | `lemonslice-pipecat` |
| LemonSlice owns STT/LLM/TTS and backend creates `/liveai/rooms` | `lemonslice-hosted` |
| Browser receives `room_url` and Daily token | `lemonslice-hosted-daily` |
| `<lemonslice-widget>` or no-backend embed | `lemonslice-widget` |
| Developer owns STT/LLM/TTS without supported plugin | `lemonslice-self-managed` |
| External conference URL | `lemonslice-meeting-platforms` |

Ask one concise question only when repository evidence cannot resolve a materially different implementation path.

## Output

State the selected path and one-sentence reason, then implement using the selected skill. Do not require rigid Markdown wording.
