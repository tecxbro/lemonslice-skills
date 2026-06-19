---
name: lemonslice-hosted
description: Create and manage Lemon Slice hosted sessions.
license: MIT
---

# Lemon Slice Hosted Pipeline

## Use this skill when
The developer wants Lemon Slice to handle the entire AI pipeline (STT, LLM, TTS, avatar), and the backend needs to create/manage these sessions.

## Do not use this skill when
- The developer is bringing their own STT/LLM/TTS (use `lemonslice-self-managed`, `lemonslice-livekit`, or `lemonslice-pipecat`).
- The developer only wants a simple web widget without a backend (use `lemonslice-widget`).
- You need to build the frontend Daily UI for the hosted session (use `lemonslice-hosted-daily`).

## Agent workflow
1. **Backend Session Creation:**
   - Call `POST /api/liveai/rooms` to create a hosted session.
   - Include `X-API-Key` in headers.
   - Provide `agent_id` OR `agent_image_url`, plus `agent_prompt`.
   - Optionally configure `idle_timeout` (defaults to 60s).
2. **Session Status:**
   - The creation endpoint returns a `session_id`.
   - Poll `GET /api/liveai/rooms/{session_id}` to check status (`QUEUED` -> `ACTIVE` -> `COMPLETED`).
3. **Handoff to Frontend:**
   - The backend must return the connection credentials (Daily room URL and token) to the frontend.
4. **Data Management:**
   - Store the `session_id` in your own database at creation time for pagination and filtering later, as bulk list APIs may be limited.

## Common mistakes
- Using `/api/liveai/sessions` (Self-Managed) instead of `/api/liveai/rooms` (Hosted).
- Exposing the `X-API-Key` to the frontend to let the frontend create sessions. The backend must create the session.
- Trying to manually orchestrate audio routing. In hosted mode, Lemon Slice handles all audio/video logic.

## Validation checklist
- [ ] Is the session created via `POST /api/liveai/rooms` from a secure backend?
- [ ] Does the backend pass the connection credentials securely to the frontend client?
- [ ] Are session IDs stored locally for future reference?
