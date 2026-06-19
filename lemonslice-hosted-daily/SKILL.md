---
name: lemonslice-hosted-daily
description: Build a Daily frontend for hosted Lemon Slice sessions.
license: MIT
---

# Lemon Slice Hosted Daily Frontend

## Use this skill when
You are building the frontend user interface for a Hosted Lemon Slice session, and the backend has already created the session and returned the Daily room credentials.

## Do not use this skill when
- You are trying to use Pipecat (use `lemonslice-pipecat`).
- You are writing the backend code to create the session (use `lemonslice-hosted`).
- You just want a simple drop-in website widget (use `lemonslice-widget`).

## Agent workflow
1. **Receive Credentials:** 
   - The frontend should securely request session credentials from the developer's backend.
   - It will receive a Daily room URL and an authentication token.
2. **Connect to Daily:**
   - Use `@daily-co/daily-js` or `@pipecat-ai/client-react` to join the room using the provided URL and token.
3. **State Management:**
   - Implement the connection state machine: `idle` -> `joining` -> `connected` -> `avatar_ready` -> `active` -> `ended`.
4. **Render Media:**
   - Listen for `participant-joined` events.
   - When the avatar joins, render its remote video track.
5. **Cleanup:**
   - Ensure the Daily call object is destroyed on component unmount or session end.

## Common mistakes
- Attempting to call Lemon Slice REST APIs directly from the React/frontend code to create the session. The frontend should only communicate with the developer's backend.
- Using `localStorage` for the Daily token instead of secure, short-lived methods (e.g., `HttpOnly` cookies in production).

## Validation checklist
- [ ] Is the frontend completely devoid of Lemon Slice API keys?
- [ ] Is the connection logic using the URL and token provided by the backend?
- [ ] Are remote video tracks correctly attached to `<video>` elements?
- [ ] Is proper cleanup implemented on unmount?
