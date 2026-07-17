---
name: lemonslice-livekit
description: Implement LemonSlice avatars in Python or Node LiveKit Agents apps. Covers package/version detection, exact AvatarSession wiring, local image inputs, model/aspect-ratio options, two-gate readiness, frontend first-frame detection, events, startup failure, AgentSession errors, and cleanup.
license: MIT
---

# LemonSlice LiveKit integration

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Inspect before editing

Detect Python (`livekit-agents`) versus Node (`@livekit/agents`) from manifests, lockfiles, imports, and the actual worker entrypoint. Inspect the installed LemonSlice plugin version and constructor signature/source before using newly documented fields. Documentation may lead published plugin types.

Do not add raw `/liveai/sessions` creation for a normal plugin integration.

## Install

```bash
# Python
uv add "livekit-agents[lemonslice]"
# or: pip install "livekit-agents[lemonslice]"

# Node
pnpm add @livekit/agents-plugin-lemonslice
# or the repository's existing package manager
```

Keep `LEMONSLICE_API_KEY` server-side and add only its name to `.env.example`.

## Python implementation

```python
from livekit import agents
from livekit.agents import AgentSession
from livekit.plugins import lemonslice

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        # existing STT, LLM, TTS, VAD, turn detection
    )

    avatar = lemonslice.AvatarSession(
        # Exactly one:
        agent_image_url="https://example.com/avatar.png",
        # agent_id="...",
        # agent_image=pil_image,
        agent_prompt="a warm person speaking naturally",
        agent_idle_prompt="a calm attentive person",
        idle_timeout=600,
        model="flash",          # optional: lite | flash | pro
        aspect_ratio="1x1",     # optional: 2x3 | 9x16 | 1x1
        # response_done_timeout=0.8,  # Gemini Live S2S when needed
        simulcast=True,
    )

    session_id = await avatar.start(session, room=ctx.room)
    await session.start(...)
```

Use exactly one of `agent_image_url`, `agent_id`, or `agent_image`.

## Node implementation

```ts
import { voice } from "@livekit/agents";
import * as lemonslice from "@livekit/agents-plugin-lemonslice";

const session = new voice.AgentSession({
  // existing STT, LLM, TTS, VAD, turn detection
});

const avatar = new lemonslice.AvatarSession({
  // Exactly one:
  agentImageUrl: "https://example.com/avatar.png",
  // agentId: "...",
  // agentImage: "/absolute/path/avatar.png", // or Buffer
  // agentImageMimeType: "image/jpeg",        // Buffer only
  agentPrompt: "a warm person speaking naturally",
  agentIdlePrompt: "a calm attentive person",
  idleTimeout: 600,
  extraPayload: {
    model: "flash",
    aspectRatio: "1x1",
    responseDoneTimeout: 0.8,
    simulcast: true,
  },
});

const sessionId = await avatar.start(session, room);
await session.start(/* existing options */);
```

Before committing, confirm the installed package supports each first-class option and `extraPayload` shape. Do not invent imports.

## Readiness contract

Treat readiness as two separate gates:

1. **Pipeline readiness**
   - topic: `lemonslice`
   - payload: `type: "bot_ready"`
   - use for startup lifecycle, control eligibility, and startup timeout handling.
2. **Visual readiness**
   - frontend first rendered frame
   - use to transition from ringing/loading UI to active-call UI.

`bot_ready` is not proof that a frame has rendered.

Frontend:

```tsx
import { LiveKitAvatarReadyWatcher } from "@lemonsliceai/avatar/livekit-react";

<LiveKitAvatarReadyWatcher onReady={() => setAvatarReady(true)} />
```

Keep a ringing UI until `onReady`. Also listen for `RoomEvent.ParticipantDisconnected` for the avatar identity and `RoomEvent.Disconnected` for room failure.

## Required events and failures

Handle LemonSlice topic events:

- `bot_ready`
- `idle_timeout`
- `error` (`fatal` determines terminal handling)
- `video_generation_error`
- `metric` (`time_to_first_push`, `tts_audio_delay`)

Handle `startup_failure` on topic `lemonslice/message`. Add a bounded startup timer. Subscribe to `AgentSession` error events and distinguish STT, LLM, and TTS failures; terminate on non-recoverable errors.

## Cleanup

Cover user hangup, avatar participant disconnect, room disconnect, startup timeout, fatal pipeline error, process shutdown, and idle timeout.

- `ctx.room.disconnect()` ends the room and avatar session.
- `ctx.shutdown()` stops the job/avatar without necessarily closing the room.
- Runtime `terminate` ends only LemonSlice avatar generation.

Do not leave a disabled idle timeout without explicit termination and billing safeguards.

## Validation

Run the repository's formatter, type checker, tests, and build. Verify no browser bundle contains `LEMONSLICE_API_KEY`, readiness uses first-frame UI gating, and the installed plugin accepts all configured fields.

References:
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
