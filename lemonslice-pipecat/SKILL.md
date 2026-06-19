---
name: lemonslice-pipecat
description: Add Lemon Slice avatars to Pipecat pipelines.
license: MIT
---

# Lemon Slice Pipecat Integration

## Use this skill when
The developer is building a conversational AI pipeline using the Pipecat framework and wants to use Lemon Slice for video avatar generation.

## Do not use this skill when
- The project uses LiveKit Agents (use `lemonslice-livekit`).
- The developer wants Lemon Slice to manage the full STT/LLM/TTS stack (use `lemonslice-hosted`).

## Agent workflow
1. **Install package:** Use `pipecat-ai[lemonslice]`.
2. **Setup Transport:** 
   - Pipecat uses Daily as the transport layer for Lemon Slice.
   - Use `LemonSliceTransport` to connect the Pipecat bot to a virtual Daily room.
   - You can provide an existing `daily_room_url` or let the transport auto-provision one.
3. **Configure Pipeline:**
   - The Pipecat bot acts as the "brain" (audio -> STT -> LLM -> TTS).
   - The Lemon Slice avatar acts as the "face" receiving TTS audio and rendering video.
   - Configure `agent_image_url` (or `agent_id`) on the transport.
4. **Frontend Integration:**
   - Use `@pipecat-ai/client-react` or `@pipecat-ai/client-js` to render the custom UI. The Daily Prebuilt UI is typically not used.

## Common mistakes
- Confusing Pipecat's use of Daily with the "Hosted Daily" integration. Pipecat is a Self-Managed pipeline; Hosted Daily means Lemon Slice manages the pipeline.
- Trying to connect a Pipecat bot to a LiveKit transport when using Lemon Slice. The Pipecat integration specifically targets Daily as the WebRTC layer.

## Validation checklist
- [ ] Is `pipecat-ai[lemonslice]` installed?
- [ ] Is `LemonSliceTransport` configured in the Pipecat pipeline?
- [ ] Are the bot, avatar, and user all joining the same Daily room?
