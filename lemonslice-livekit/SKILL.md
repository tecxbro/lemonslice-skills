---
name: lemonslice-livekit
description: Add Lemon Slice avatars to LiveKit Agents.
license: MIT
---

# Lemon Slice LiveKit Integration

## Use this skill when
Use this only after `lemonslice-integration-choice` selected LiveKit.

## Do not use this when
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

## Core rules
- Wait for `bot_ready`, not participant join.
- Keep `LEMONSLICE_API_KEY` server-side only.

## Reference files
Load only the reference file needed for the task:

- `references/setup-and-wiring.md` — read for `pip`/`npm` install commands, Python/Node setup patterns, `agent_id` vs `agent_image_url`, API key setup, and Gemini Live S2S `response_done_timeout`.
- `references/readiness-events-shutdown.md` — read for `bot_ready` details, LiveKit data-channel events (`idle_timeout`, `error`, `metric`), startup timeouts, `ctx.room.disconnect()`, `ctx.shutdown()`, and `terminate`.

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
