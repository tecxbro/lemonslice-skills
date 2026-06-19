---
name: lemonslice-livekit
description: Add Lemon Slice avatars to LiveKit Agents.
license: MIT
---

# Lemon Slice LiveKit Integration

## Use this skill when
The developer is building a voice AI agent using the LiveKit Agents framework and wants to add a Lemon Slice avatar video track.

## Do not use this skill when
- The project does not use LiveKit.
- The project uses Pipecat (use `lemonslice-pipecat`).
- The developer wants a hosted session (use `lemonslice-hosted`).

## Agent workflow
1. **Detect language:** Identify if the project is Python or Node.js.
2. **Install package:**
   - Python: `livekit-agents[lemonslice]~=1.5` or `livekit-plugins-lemonslice`
   - Node.js: `@livekit/agents-plugin-lemonslice`
3. **Configure Avatar Session:**
   - Initialize the `AvatarSession` from the plugin.
   - Provide `agent_image_url` (or `agent_id`) and `agent_prompt`.
4. **Start Session:**
   - Await the `start()` method on the avatar, passing the LiveKit session and room context (e.g., `await avatar.start(session, room=ctx.room)`).
5. **Handle lifecycle:**
   - Wait for avatar readiness (`bot_ready` or participant join).
   - Listen for RPC events over the data channel for errors or metrics.
   - Gracefully disconnect the room to shut down the avatar.

## Common mistakes
- Trying to manually call Lemon Slice REST APIs to create the session. The LiveKit plugin handles session creation internally.
- Putting the `LEMONSLICE_API_KEY` in the frontend client. It must remain in the backend/agent server environment variables.
- Using hosted session APIs alongside LiveKit. This is a self-managed integration.

## Validation checklist
- [ ] Is the correct LiveKit plugin installed for the language?
- [ ] Is `LEMONSLICE_API_KEY` in the server environment?
- [ ] Is the avatar started within the LiveKit room context?
