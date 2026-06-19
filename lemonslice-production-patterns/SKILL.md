---
name: lemonslice-production-patterns
description: Make Lemon Slice integrations production-ready.
license: MIT
---

# Lemon Slice Production Patterns

## Use this skill when
You are reviewing, auditing, or finalizing a Lemon Slice integration and need to ensure it is secure, performant, and stable for production use.

## Do not use this skill when
You are just starting to build a prototype. Establish the core functionality using the specific integration skill first.

## Agent workflow
1. **Security Audit:**
   - Verify `LEMONSLICE_API_KEY` is completely absent from all client-side code (frontend frameworks, widget embeds in production).
   - Verify Daily tokens (if applicable) are generated server-side, short-lived, and passed securely (e.g., via `HttpOnly`, `Secure` cookies).
2. **Avatar Image Optimization:**
   - Ensure `agent_image_url` points to a publicly accessible, fast CDN.
   - Verify image dimensions are as close to **368x560 px** as possible to avoid unwanted center-cropping.
   - Use PNG to preserve transparency if using the Chroma Key pipeline.
3. **Session Lifecycle Management:**
   - Implement cleanup logic to terminate sessions when the user leaves the page or unmounts the component.
   - Configure `idle_timeout` during session creation to avoid runaway costs (default is 60s).
   - Rely on the hard 1-hour maximum duration as a safety net, not a primary control.
4. **Latency and Performance (Self-Managed):**
   - Optimize the STT -> LLM -> TTS pipeline. Lemon Slice generates video fast (25 FPS, <3s response), but it relies on audio arriving quickly.
   - Use Chroma Key (green screen) for horizontal displays to focus compute purely on the avatar, rather than rendering wide background environments.
5. **State Management:**
   - Store `session_id`s in your own backend database upon creation. Do not rely heavily on Lemon Slice's bulk list endpoints for your application's operational data.

## Common mistakes
- Exposing API keys in `.env.local` files that get bundled into Next.js/React frontend builds (e.g., prefixing with `NEXT_PUBLIC_`).
- Failing to issue cleanup/termination commands when a user forcefully closes a browser tab.

## Validation checklist
- [ ] Is the API key secure?
- [ ] Is the avatar image properly sized and hosted?
- [ ] Are idle timeouts explicitly configured or deliberately relying on the default?
- [ ] Is session termination handled gracefully?
