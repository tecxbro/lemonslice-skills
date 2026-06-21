# Pipecat Transport Setup

## Contents
- Install
- Environment
- Imports
- Transport constructor
- New session request
- Pipeline placement
- Common mistakes

## Install
- `pip install "pipecat-ai[lemonslice]"`
- `uv add "pipecat-ai[lemonslice]"`
- `poetry add "pipecat-ai[lemonslice]"`

## Environment
- Keep `LEMONSLICE_API_KEY` server-side.

## Imports
Use these exact official import paths (do not invent import paths):
```python
from pipecat.transports.lemonslice.transport import (
    LemonSliceNewSessionRequest,
    LemonSliceParams,
    LemonSliceTransport,
)
```

## Transport constructor
Here is a concise Python setup pattern:

```python
import os
import aiohttp

from pipecat.transports.lemonslice.transport import (
    LemonSliceNewSessionRequest,
    LemonSliceParams,
    LemonSliceTransport,
)

async def main():
    async with aiohttp.ClientSession() as session:
        transport = LemonSliceTransport(
            bot_name="Pipecat",
            api_key=os.getenv("LEMONSLICE_API_KEY"),
            session=session,
            session_request=LemonSliceNewSessionRequest(
                agent_image_url="https://example.com/avatar.png",
            ),
        )
```

Rules:
* `bot_name` is the Pipecat bot participant name.
* `api_key` comes from `LEMONSLICE_API_KEY`.
* `session` should be an `aiohttp.ClientSession`.
* `session_request` must be `LemonSliceNewSessionRequest`.
* Provide exactly one of `agent_id` or `agent_image_url`.

## New session request
Required avatar identity:
* `agent_image_url`
* or `agent_id`

Rules:
* Never send both.
* Never send neither.

Optional fields:
* `agent_prompt`
* `agent_idle_prompt`
* `idle_timeout`
* `response_done_timeout`
* `daily_room_url`
* `daily_token`
* `lemonslice_properties`

## Pipeline placement
Conceptual shape:

```python
pipeline = Pipeline(
    [
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,
        transport.output(),
        assistant_aggregator,
    ]
)

task = PipelineTask(
    pipeline,
    params=PipelineParams(
        audio_in_sample_rate=16000,
        audio_out_sample_rate=16000,
    ),
)
```

Explanation:
* `transport.input()` receives user audio.
* STT converts audio to text.
* LLM generates response.
* TTS creates agent audio.
* `transport.output()` sends agent audio toward LemonSlice.
* LemonSlice renders synced avatar audio/video.
* Do not route LemonSlice as a separate frontend widget.
* Do not replace Pipecat STT/LLM/TTS with hosted LemonSlice behavior.
