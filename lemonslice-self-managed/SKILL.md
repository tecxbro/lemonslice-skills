---
name: lemonslice-self-managed
description: Build with Lemon Slice as the avatar layer in a custom agent stack.
license: MIT
---

# Lemon Slice Self-Managed Pipeline

## Use this skill when
The developer owns the entire AI stack (STT, LLM, TTS) and wants to use Lemon Slice exclusively as the video generation layer.

## Do not use this skill when
- The developer wants Lemon Slice to handle the STT/LLM/TTS (use `lemonslice-hosted`).
- The developer is using LiveKit (use `lemonslice-livekit`).
- The developer is using Pipecat (use `lemonslice-pipecat`).

## Agent workflow
1. Ensure the API key (`LEMONSLICE_API_KEY`) is kept server-side.
2. Create a session using `POST /api/liveai/sessions`.
   - Provide `transport_type` (e.g., `livekit`).
   - Provide transport `properties` (e.g., `livekit_url`, `livekit_token`).
   - Provide avatar identity via `agent_image_url` (recommended 368x560 px) OR `agent_id`.
   - Provide `agent_prompt` for demeanor/expression.
3. Understand the session lifecycle: `QUEUED` -> `ACTIVE` -> `COMPLETED`.
4. The backend should poll `GET /api/liveai/rooms/{session_id}` (or `GET /api/liveai/sessions/{session_id}`) to check status if necessary.

## Common mistakes
- Using hosted endpoints (`/api/liveai/rooms` for creation) instead of self-managed endpoints (`/api/liveai/sessions`).
- Exposing the `LEMONSLICE_API_KEY` in frontend code.
- Providing both `agent_image_url` and `agent_id`. They are mutually exclusive.

## Validation checklist
- [ ] Is the session created using `POST /api/liveai/sessions`?
- [ ] Is `LEMONSLICE_API_KEY` only used securely on the backend?
- [ ] Is only one of `agent_image_url` or `agent_id` provided?
