---
name: lemonslice-livekit
description: Implement LemonSlice avatars in existing Python or Node LiveKit Agents apps. Covers installed-version inspection, AvatarSession wiring, provider ownership, two-gate readiness, latency measurement, failures, and cleanup.
license: MIT
---

# LemonSlice LiveKit integration

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Routing

For a new, empty project, consider `lemonslice-quickstart`. Use this skill when integrating into an existing LiveKit Agents repository or modifying the generated Quickstart.

Do not add raw `/liveai/sessions` creation for a normal plugin integration.

## Provider ownership

LemonSlice supplies avatar media. Preserve the application's existing STT, VAD/turn detection, LLM, TTS, tools, and conversation state. Do not replace these merely to add LemonSlice unless the user asks.

## Inspect before editing

Detect Python (`livekit-agents`) versus Node (`@livekit/agents`) from manifests, lockfiles, imports, and the real worker entrypoint. Inspect the installed LemonSlice plugin version and actual constructor signature/source before using documented fields.

Do not infer Node options from Python fields, Python options from Node fields, or either plugin surface from raw REST. Inspect the installed package's constructor signature.

## Install

```bash
# Python
uv add "livekit-agents[lemonslice]"
# or the repository's existing Python package manager

# Node
pnpm add @livekit/agents-plugin-lemonslice
# or the repository's existing JavaScript package manager
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
        # Preserve existing STT, LLM, TTS, VAD, turn detection, tools.
    )

    avatar = lemonslice.AvatarSession(
        # Exactly one supported selector in the installed signature:
        agent_image_url="https://example.com/avatar.png",
        # agent_id="...",
        # agent_image=pil_image,
        agent_prompt="a warm person speaking naturally",
        agent_idle_prompt="a calm attentive person",
        idle_timeout=600,
        model="flash",          # only after installed-signature/account verification
        aspect_ratio="1x1",     # only after installed-signature/account verification
        simulcast=True,
    )

    session_id = await avatar.start(session, room=ctx.room)
    await session.start(...)
```

## Node implementation

```ts
import { voice } from "@livekit/agents";
import * as lemonslice from "@livekit/agents-plugin-lemonslice";

const session = new voice.AgentSession({
  // Preserve existing STT, LLM, TTS, VAD, turn detection, and tools.
});

const avatar = new lemonslice.AvatarSession({
  agentImageUrl: "https://example.com/avatar.png",
  // agentId: "...",
  // agentImage: "/absolute/path/avatar.png", // or Buffer, if installed types support it
  // agentImageMimeType: "image/jpeg",
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

Before committing, confirm every first-class option and `extraPayload` key against the installed package. Do not invent imports or constructor fields.

## Readiness contract

Treat readiness as two separate gates:

1. **Pipeline readiness**
   - topic: `lemonslice`
   - payload: `type: "bot_ready"`
   - use for startup lifecycle, control eligibility, and startup timeout handling.
2. **Visual readiness**
   - frontend first rendered frame
   - use to transition from ringing/loading UI to active-call UI.

`bot_ready` is not proof that a frame rendered.

```tsx
import { LiveKitAvatarReadyWatcher } from "@lemonsliceai/avatar/livekit-react";

<LiveKitAvatarReadyWatcher onReady={() => setAvatarReady(true)} />
```

Also handle `RoomEvent.ParticipantDisconnected` for the identified avatar and `RoomEvent.Disconnected` for room failure.

## Events and failures

Handle LemonSlice topic events including `bot_ready`, `idle_timeout`, `error` with fatal classification, `video_generation_error`, and metrics such as `time_to_first_push` and `tts_audio_delay` where exposed.

Handle `startup_failure` on topic `lemonslice/message`. Add a bounded startup timer. Subscribe to `AgentSession` errors and distinguish STT, LLM, and TTS failures; terminate on non-recoverable errors.

## Latency measurement

Measure separately:

- end of user speech;
- final STT;
- LLM first token and completion;
- first TTS audio;
- LemonSlice time-to-first-push;
- remote track subscription;
- first rendered frame.

Published Flash benchmark figures, including 471 ms avatar TTFB and about 2.04 seconds average end-to-end latency, describe a dated benchmark with a specific STT/LLM/TTS stack and measurement definition. They are not universal SLAs.

## Cleanup and validation

Cover user hangup, avatar participant disconnect, room disconnect, startup timeout, fatal pipeline error, process shutdown, and idle timeout.

- `ctx.room.disconnect()` ends the room and avatar session.
- `ctx.shutdown()` stops the job/avatar without necessarily closing the room.
- Runtime `terminate` ends only LemonSlice avatar generation.

Do not leave a disabled idle timeout without explicit termination and billing safeguards.

Run the repository's formatter, type checker, tests, and build. Verify no browser bundle contains `LEMONSLICE_API_KEY`, readiness uses first-frame gating, existing providers remain intact, and the installed plugin accepts all configured fields.

References:
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
- https://lemonslice.com/blog/lemonslice-flash
