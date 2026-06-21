# LiveKit Setup and Wiring

## Contents
- Install package
- Environment variables
- Python wiring pattern
- Node/TypeScript wiring pattern
- Gemini Live S2S guidance

## Install package
Use the repo’s existing package manager.

Python:

```bash
pip install "livekit-agents[lemonslice]"
```

Python with uv:

```bash
uv add "livekit-agents[lemonslice]"
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
* For `agent_image_url`, prefer a publicly accessible image URL focused on the face. Official docs recommend 368 × 560 pixels; LemonSlice will center-crop if dimensions differ.
* When using `agent_id` with the LiveKit plugin, do not assume LemonSlice web-app voice/personality settings carry over. The LiveKit plugin uses the developer’s own STT/LLM/TTS stack; selected LemonSlice voices and personalities are ignored.
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

## Gemini Live S2S guidance
If the LiveKit agent uses Gemini Live S2S and the official LemonSlice docs path is being followed, set:

```python
response_done_timeout=0.8
```

Use this to help LemonSlice detect response completion when end-of-response events are missing or delayed.

Do not blindly add this to every project. Add it when:
* the project uses Gemini Live S2S, or
* the official docs/example for the selected LiveKit path explicitly recommends it.
