---
name: lemonslice-control-actions
description: Control sessions, actions, image updates, and termination.
license: MIT
---

# Lemon Slice Control Actions

## Official docs
- https://lemonslice.com/docs/api-reference/control-self-managed-session

## Use this skill when
You need to programmatically control an active avatar session, specifically terminating the avatar without dropping the underlying transport connection.

## Do not use this skill when
- You are trying to handle mute/unmute/interrupt logic. That is handled at the orchestration layer (LiveKit/Pipecat SDKs).
- The session is not yet active/ready.

## Agent workflow
1. **Verify Readiness:**
   - Require session readiness before sending controls.
2. **Session Termination (Self-Managed):**
   - Use `POST /api/liveai/sessions/{session_id}/control` to send control events.
   - Include the documented control event: `terminate`.
   - This cleanly stops the avatar generation without tearing down the underlying LiveKit or Daily room.
3. **Hosted Daily Hang-up:**
   - Note that Hosted Daily uses the `force-end` app message for user hang-up (if supported by docs).
4. **Unsupported Actions:**
   - Do NOT claim support for actions like `wave`, `turn`, `dance`, `image updates`, or `action triggers` unless the official docs expose their body schemas explicitly.

## Common mistakes
- Attempting to send REST requests to interrupt the avatar's speech.
- Assuming undocumented actions like "wave" exist.
- Sending control actions before the session is ready.

## Validation checklist
- [ ] Does the code verify session readiness before issuing commands?
- [ ] Is the `terminate` event used correctly for self-managed control?
- [ ] Are undocumented or unverified actions strictly avoided?
