---
name: lemonslice-quickstart
description: Bootstrap a new LemonSlice video-agent project from the official Next.js and LiveKit quickstart. Use when the user wants a new app, the fastest recommended setup, or to clone the official starter; route existing LiveKit repositories to lemonslice-livekit.
license: MIT
---

# LemonSlice Quickstart

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

Use this skill for **new-project bootstrapping**. Do not use it to replace an existing LiveKit Agents architecture.

## Routing guardrail

1. Inspect the repository before editing.
2. If an existing LiveKit Agents worker, room flow, or frontend already exists, route to `lemonslice-livekit`.
3. If the repository is empty or the user explicitly requests the official starter, follow the official Quickstart structure.

## Workflow

1. Determine whether the target is a new or existing repository.
2. Inspect the official Quickstart and current package signatures.
3. Preserve the selected package manager and lockfile.
4. Scaffold the official Next.js + LiveKit structure without adding an alternate architecture beside it.
5. Keep `LEMONSLICE_API_KEY` in server/agent code and list only the variable name in `.env.example`.
6. Preserve the Quickstart's STT, VAD/turn detection, LLM, TTS, tools, and conversation state unless the user asks to change providers.
7. Verify the LiveKit agent starts, the browser joins the intended room, the LemonSlice remote avatar track is subscribed, and the first avatar frame actually renders.
8. Run install, format, typecheck, tests, and a production build using the repository's package manager.
9. Report every file changed and command run, including failures and installed-version conflicts.

## Readiness

Do not declare the app ready merely because the agent process started or `bot_ready` arrived. The browser experience is ready only after the remote avatar video track renders its first frame.

## Completion

Use [`references/verification.md`](references/verification.md) as the final checklist. Do not leave the user with a detached sample file that the generated application never imports.

References:
- https://lemonslice.com/docs/quickstart.md
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
