---
name: lemonslice-livekit
description: Add Lemon Slice avatars to LiveKit Agents.
license: MIT
---

# Lemon Slice LiveKit Integration

## Official docs

- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/examples/livekit-app-python.md
- https://lemonslice.com/docs/examples/livekit-app-nodejs.md
- https://lemonslice.com/docs/reference/authentication.md
- https://lemonslice.com/docs/reference/best-practices.md
- https://lemonslice.com/docs/reference/overview.md
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md
- https://lemonslice.com/docs/api-reference/control-self-managed-session.md
- https://lemonslice.com/docs/openapi.json

## Guardrails

Use this only after `lemonslice-integration-choice` selected LiveKit.

Do not use this for:
- non-LiveKit projects
- Pipecat projects
- hosted LemonSlice sessions
- widget/no-backend embeds
- raw self-managed REST work unless it is explicitly part of a LiveKit transport integration

## Detect Python vs Node LiveKit project

Inspect repo files before editing.

Python LiveKit signals:
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`
- `poetry.lock`
- dependency names like `livekit-agents`
- imports like `from livekit.agents import ...`
- Python worker/agent entrypoints using `JobContext`, `AgentSession`, `ctx.room`
- existing plugins imported from `livekit.plugins`

Node/TypeScript LiveKit signals:
- `package.json`
- `pnpm-lock.yaml`
- `package-lock.json`
- `yarn.lock`
- dependencies like `@livekit/agents`
- `.ts`, `.tsx`, `.js`, `.mjs` LiveKit agent entrypoints
- imports from `@livekit/agents`

Decision rules:
- If only Python signals exist, follow Python install/import/wiring.
- If only Node signals exist, follow Node install/import/wiring.
- If both exist, identify the actual LiveKit worker entrypoint before editing.
- Do not edit both Python and Node paths unless the repo intentionally contains both workers.
- If no LiveKit framework signal exists, route back to `lemonslice-integration-choice`.

## Install package

Use the repo’s existing package manager.

Python:

```bash
pip install "livekit-agents[lemonslice]"
```

Node with npm:

```bash
npm install @livekit/agents-plugin-lemonslice
```

Node with pnpm:

```bash
pnpm add @livekit/agents-plugin-lemonslice
```

Do not add raw LemonSlice REST client code for normal LiveKit plugin setup. The LiveKit plugin path handles session creation internally.

## Environment variables

Required server-side variable:

```bash
LEMONSLICE_API_KEY=...
```

Rules:
* Keep `LEMONSLICE_API_KEY` only in the LiveKit agent/server environment.
* Never expose it to browser, mobile, frontend bundle, public config, or client-side code.
* Update `.env.example` only with the key name, never a real value.
* Do not log the raw key.

## Python wiring pattern

In the LiveKit agent worker, after the LiveKit `AgentSession` is created and before/around session start, create the LemonSlice avatar session.

```python
from livekit.plugins import lemonslice

avatar = lemonslice.AvatarSession(
    agent_id="<LEMONSLICE_AGENT_ID>",
    # or agent_image_url="https://example.com/avatar.png",
    idle_timeout=60,
)

await avatar.start(session, room=ctx.room)
```

Rules:
* Use `lemonslice.AvatarSession`.
* Use exactly one of `agent_id` or `agent_image_url`.
* Start with `await avatar.start(session, room=ctx.room)`.
* Do not manually create `/api/liveai/sessions` from a normal LiveKit plugin integration unless the official docs explicitly require it for the selected path.

## Node/TypeScript wiring pattern

For Node projects, install:

```bash
npm install @livekit/agents-plugin-lemonslice
```

or:

```bash
pnpm add @livekit/agents-plugin-lemonslice
```

Then follow the official Node LiveKit example for the exact import/export shape.

Preserve the same conceptual wiring:
* create the LemonSlice avatar session from the official LiveKit LemonSlice plugin
* configure `agent_id` or `agent_image_url`
* keep `LEMONSLICE_API_KEY` server-side
* start the avatar against the active LiveKit agent session and room
* wait for `bot_ready` before treating the avatar as usable

Do not translate the Python import literally if the official Node package exports a different symbol shape.

## Readiness and events

Do not treat LiveKit participant join as avatar readiness.

The explicit readiness signal is:
- `bot_ready`

The agent must wait for `bot_ready` before:
- showing “avatar ready”
- sending control/actions
- assuming video generation is healthy
- allowing user-facing interactions that depend on the avatar

Handle these LemonSlice data-channel events:
- `bot_ready`: avatar is initialized and ready.
- `idle_timeout`: avatar session idled out. Stop waiting for output, clean up state, and shut down if appropriate.
- `error`: general LemonSlice/avatar error. Log with context, surface a safe error state, and clean up.
- `video_generation_error`: avatar video generation failed. Treat as avatar-path failure, not necessarily LiveKit room failure.
- `metric`: telemetry/observability event. Record/log it, but do not treat it as an error.

Add a startup timeout around `bot_ready`. If it never arrives, fail safely, clean up the room/avatar, and expose a retry path.

## Shutdown behavior

Implement cleanup for:
- normal worker shutdown
- user hangup
- LiveKit room disconnect
- `idle_timeout`
- startup timeout waiting for `bot_ready`
- `error`
- `video_generation_error`
- process signals / deployment shutdown

Preferred order:
1. Stop accepting new avatar-dependent work.
2. End or disconnect the LiveKit agent/session according to the project’s LiveKit lifecycle.
3. Stop LemonSlice avatar generation using the plugin’s documented cleanup method if available.
4. If the integration exposes a LemonSlice self-managed session id and control endpoint is appropriate, send the documented terminate control event:

```json
{ "event": "terminate" }
```

Do not confuse terminating LemonSlice avatar generation with deleting unrelated app state.

## Gemini Live S2S guidance

If the LiveKit agent uses Gemini Live S2S and the official LemonSlice docs path is being followed, set:

```python
response_done_timeout=0.8
```

Use this to help LemonSlice detect response completion when end-of-response events are missing or delayed.

Do not blindly add this to every project. Add it when:
* the project uses Gemini Live S2S, or
* the official docs/example for the selected LiveKit path explicitly recommends it.

## Common mistakes

- Using this skill before `lemonslice-integration-choice` selects LiveKit.
- Editing a Pipecat project as if it were LiveKit.
- Installing the Python package in a Node project or the Node package in a Python project.
- Exposing `LEMONSLICE_API_KEY` to frontend/browser/mobile code.
- Manually calling LemonSlice REST session creation in a normal LiveKit plugin integration.
- Providing both `agent_id` and `agent_image_url`.
- Providing neither `agent_id` nor `agent_image_url`.
- Treating LiveKit participant join as readiness instead of waiting for `bot_ready`.
- Ignoring `idle_timeout`, `error`, `video_generation_error`, and startup timeout paths.
- Treating `metric` as an error.
- Forgetting shutdown cleanup.
- Adding `response_done_timeout=0.8` to non-Gemini projects without docs-based reason.
- Inventing Node import names instead of following the official Node example.

## Validation checklist

- [ ] Did `lemonslice-integration-choice` explicitly select LiveKit?
- [ ] Did I inspect repo evidence before editing?
- [ ] Did I detect Python vs Node/TypeScript correctly?
- [ ] Did I install the correct official package for that language?
- [ ] Is `LEMONSLICE_API_KEY` only in server/agent environment?
- [ ] Did I avoid exposing API keys to frontend code?
- [ ] Does the implementation use `lemonslice.AvatarSession` or the official Node equivalent?
- [ ] Does the implementation provide exactly one of `agent_id` or `agent_image_url`?
- [ ] For Python, does it use `await avatar.start(session, room=ctx.room)`?
- [ ] Does readiness wait for `bot_ready`, not participant join?
- [ ] Are `idle_timeout`, `error`, `video_generation_error`, and `metric` handled?
- [ ] Is there a startup timeout if `bot_ready` never arrives?
- [ ] Is shutdown/cleanup implemented for normal end, disconnect, timeout, and errors?
- [ ] If Gemini Live S2S is used, is `response_done_timeout=0.8` configured?
- [ ] Did I avoid raw REST session creation unless the official docs require it for this path?
