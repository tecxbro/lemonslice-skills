---
name: lemonslice-control-actions
description: Control sessions, actions, image updates, and termination.
license: MIT
---

# Lemon Slice Control Actions

## Use this skill when
You need to programmatically control an active avatar session, specifically terminating the avatar without dropping the underlying transport connection, or controlling its behavioral demeanor.

## Do not use this skill when
- You are trying to handle mute/unmute/interrupt logic. That is handled at the orchestration layer (LiveKit/Pipecat SDKs), not via Lemon Slice REST endpoints.
- The session is not yet `ACTIVE`.

## Agent workflow
1. **Behavioral Control:**
   - Use `agent_prompt` during session creation for high-level demeanor and emotional style.
2. **Session Termination (Self-Managed):**
   - Use `POST /api/liveai/sessions/{session_id}/control` to send termination commands.
   - This cleanly stops the avatar generation without tearing down the underlying LiveKit or Daily room.
3. **Session Lifecycle Constraints:**
   - Sessions remain active until manually terminated, the `idle_timeout` is reached (default 60s), or the maximum duration (1 hour) is hit.
4. **Specific Actions (Wave, Turn, Dance):**
   - Check the orchestration framework's RPC channels for executing deterministic motion actions.

## Common mistakes
- Attempting to send REST requests to interrupt the avatar's speech. Use the LiveKit data channel or Pipecat VAD capabilities instead.
- Sending control actions before the session status is `ACTIVE`.

## Validation checklist
- [ ] Is the control action appropriate for the Lemon Slice REST API vs the orchestration framework SDK?
- [ ] Does the code verify the session is `ACTIVE` before issuing commands?
- [ ] Are termination commands sent cleanly to avoid orphaned avatar connections?
