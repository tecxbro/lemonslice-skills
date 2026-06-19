---
name: lemonslice-api-reference
description: Use Lemon Slice REST APIs correctly.
license: MIT
---

# Lemon Slice API Reference

## Use this skill when
You need to call raw Lemon Slice REST endpoints for session creation, status polling, or metadata retrieval from a backend environment.

## Do not use this skill when
- You are trying to make API calls from a frontend browser environment (never expose the API key).
- You are using the LiveKit plugin or Pipecat, which abstract most of these API calls internally.

## Agent workflow
1. **Base Configuration:**
   - Base URL: `https://lemonslice.com/api`
   - Authentication: Add the `X-API-Key` header to all requests.
2. **Identify the correct endpoint family:**
   - **Self-Managed:** Uses the `/liveai/sessions/` path prefix.
   - **Hosted:** Uses the `/liveai/rooms/` path prefix.
   - Do NOT mix these.
3. **Common Request Parameters (Creation):**
   - Identity: `agent_id` (dashboard configured) OR `agent_image_url` (dynamic, ideally 368x560 px). They are mutually exclusive.
   - Behavior: `agent_prompt` to control demeanor.
   - Transport (Self-Managed): `transport_type` (e.g., `livekit`) and `properties` (e.g., URLs and tokens).
4. **Session Status:**
   - Polling endpoints return a `session_status`: `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, `FAILED`.

## Common mistakes
- Sending both `agent_id` and `agent_image_url`.
- Using `/liveai/sessions` when you want a hosted room.
- Expecting a bulk list endpoint to handle all pagination. Best practice is to store `session_id`s in the developer's database upon creation.

## Validation checklist
- [ ] Are requests hitting the correct base URL (`https://lemonslice.com/api`)?
- [ ] Is the `X-API-Key` header present?
- [ ] Is the code using the correct path prefix (`sessions` vs `rooms`) for the chosen integration?
