---
name: lemonslice-overview
description: Explain LemonSlice Character World Models, capabilities, integration paths, and the skill map. Use for conceptual questions or when the user wants an overview rather than implementation.
license: MIT
---

# LemonSlice overview

LemonSlice provides real-time interactive character video from one image and streaming audio. It is commonly the graphics or “face” layer on top of STT, LLM, and TTS, while Hosted Pipeline and Widget can also own more of the stack.

## Product map

- **Self-managed / LiveKit:** developer owns STT, LLM, TTS, agent logic, and UI; LemonSlice generates avatar media.
- **Self-managed / Pipecat:** same ownership model through `LemonSliceTransport`.
- **Raw self-managed REST:** for custom stacks not covered by framework plugins.
- **Hosted Pipeline:** LemonSlice owns STT, LLM, TTS, and avatar generation; the app owns a custom Daily frontend.
- **Widget:** prebuilt embed with minimal backend work.
- **Third-party meetings:** a LiveKit-based self-managed avatar can join Zoom, Google Meet, Microsoft Teams, or Webex.
- **Runtime control:** update appearance/prompts, reset idle timeout, trigger supported actions, or terminate.
- **Appearance/rendering:** choose Standard/Lite/Flash/Pro, aspect ratio, source-image framing, or WebGL green-screen compositing.

Capabilities include photorealistic and stylized characters, non-human/cartoon characters, full-body motion, emotions/actions, real-time appearance changes, and client-side compositing.

## Routing

Use `lemonslice-integration-choice` for ambiguous requests. Explicit framework or feature requests go directly to their implementation skill.

## Current sources

- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/introduction/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/reference/green-screen.md
- https://lemonslice.com/docs/examples/livekit-zoom.md
