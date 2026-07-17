---
name: lemonslice-pipecat
description: Implement LemonSlice in Pipecat Python pipelines using LemonSliceTransport. Covers current session fields, Daily ownership, recording configuration, participant behavior, first-frame readiness, errors, and cleanup.
license: MIT
---

# LemonSlice Pipecat integration

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Guardrail

Pipecat may use Daily internally; that does **not** make it LemonSlice Hosted Daily. The developer still owns STT, LLM, TTS, and the Pipecat pipeline.

Inspect the installed `pipecat-ai` version and `LemonSliceNewSessionRequest` signature before editing.

## Install and configure

```bash
uv add "pipecat-ai[lemonslice]"
# or pip install "pipecat-ai[lemonslice]"
```

```python
import os
import aiohttp
from pipecat.transports.lemonslice.transport import (
    LemonSliceNewSessionRequest,
    LemonSliceTransport,
)

async with aiohttp.ClientSession() as http:
    transport = LemonSliceTransport(
        bot_name="Pipecat",
        api_key=os.environ["LEMONSLICE_API_KEY"],
        session=http,
        session_request=LemonSliceNewSessionRequest(
            agent_image_url="https://example.com/avatar.png",
            # or agent_id="...",
            agent_prompt="a warm person speaking naturally",
            agent_idle_prompt="a calm attentive person",
            idle_timeout=600,
            response_done_timeout=0.8,
            model="flash",
            aspect_ratio="1x1",
            # daily_room_url=existing_room_url,
            # daily_token=existing_token,
            # lemonslice_properties={...},
        ),
    )
```

Use exactly one of `agent_image_url` or `agent_id`. Keep `LEMONSLICE_API_KEY` server-side.

Current documented fields:

- `agent_prompt`, `agent_idle_prompt`, `idle_timeout`, `response_done_timeout`
- `model`: `lite`, `flash`, `pro`
- `aspect_ratio`: `2x3`, `9x16`, `1x1`
- optional `daily_room_url` and `daily_token`
- `lemonslice_properties.enable_recording`: `cloud`, `cloud-audio-only`, `local`, `raw-tracks`
- `recordings_bucket` when recording is enabled

Treat recording and LemonSlice-created Daily room prices as volatile; verify current docs before quoting or encoding them.

## Pipeline placement

Place `transport.input()` before STT and `transport.output()` after TTS. Preserve aggregators and existing interruption handling. LemonSlice automatically mutes its avatar microphone, sends response lifecycle controls, and filters the avatar participant out of human connect/disconnect callbacks. The UI should also hide the Pipecat relay participant.

## Readiness

Backend transport readiness and frontend visual readiness are separate. Use the actual remote avatar video track and first rendered frame before leaving ringing/loading UI. Reuse the Daily frontend pattern in `references/frontend-readiness.md`; do not treat participant join or `bot_ready` alone as proof of rendered video.

## Cleanup and validation

Handle user disconnect, task cancellation, Daily errors, idle timeout, startup timeout, and process shutdown. Close the Pipecat task, transport, and `aiohttp.ClientSession`. Run format/type/test/build checks and confirm installed signatures.

References:
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
