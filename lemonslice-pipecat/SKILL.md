---
name: lemonslice-pipecat
description: Implement LemonSlice in existing Pipecat Python pipelines using LemonSliceTransport. Covers installed-version fields, framework ownership, Daily behavior, recording validation, first-frame readiness, errors, and cleanup.
license: MIT
---

# LemonSlice Pipecat integration

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Guardrails

Pipecat may use Daily internally; that does **not** make it LemonSlice Hosted Daily. The developer still owns the Pipecat pipeline.

Do not replace existing Pipecat STT, LLM, TTS, VAD, aggregators, processors, tools, or interruption strategy merely to add LemonSlice.

Inspect the installed `pipecat-ai` version and `LemonSliceNewSessionRequest` signature before editing. Use [`references/version-surface.md`](references/version-surface.md) to record documentation-versus-installed-package differences.

## Install and configure

```bash
uv add "pipecat-ai[lemonslice]"
# or the repository's existing Python package manager
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
            # or agent_id="..."
            agent_prompt="a warm person speaking naturally",
            agent_idle_prompt="a calm attentive person",
            idle_timeout=600,
            response_done_timeout=0.8,
            # Add model/aspect/Daily/recording fields only when the
            # installed signature and account support them.
        ),
    )
```

Use exactly one installed/supported image selector. Keep `LEMONSLICE_API_KEY` server-side.

## Recording contract

When `enable_recording` is used, require a valid `recordings_bucket`. Recording configuration belongs to the Daily transport property surface in the current contract.

Never log AWS role configuration, generated recording access material, bucket credentials, Daily tokens, or signed recording URLs. Treat recording modes, storage requirements, and price claims as volatile.

## Pipeline placement

Place `transport.input()` before STT and `transport.output()` after TTS. Preserve aggregators and existing interruption handling.

Do not assume every remote Daily participant is human or every Daily event is a Hosted event. Keep participant filtering and Pipecat's existing connect/disconnect semantics intact.

## Readiness

Backend transport readiness and frontend visual readiness are separate. Use the actual remote avatar video track and first rendered frame before leaving ringing/loading UI. Reuse the Daily frontend pattern in [`references/frontend-readiness.md`](references/frontend-readiness.md); participant join or `bot_ready` alone is not proof of rendered video.

## Cleanup and validation

Handle user disconnect, task cancellation, Daily errors, idle timeout, startup timeout, and process shutdown. Close the Pipecat task, transport, and `aiohttp.ClientSession`.

Run format, type, test, and build checks. Confirm installed signatures and preserve the existing pipeline's providers and interruption strategy.

References:
- https://lemonslice.com/docs/pipecat/index.md
- https://lemonslice.com/docs/reference/production-checklist.md
