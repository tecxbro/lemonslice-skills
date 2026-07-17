# Model and aspect-ratio surface matrix

Verify every option against the exact integration surface and current account before implementation.

| Option | LiveKit Python | LiveKit Node | Pipecat | Raw REST | Account check |
| --- | --- | --- | --- | --- | --- |
| Default | Inspect signature | Inspect signature | Inspect signature | Current OpenAPI | No special model assumed |
| Lite | Verify | Verify | Verify | Current OpenAPI currently exposes it | Yes |
| Flash | Verify | Verify | Verify | Current OpenAPI currently exposes it | Yes |
| Pro | Verify | Verify | Verify | Current OpenAPI currently exposes it | Yes |
| `2x3` | Verify | Verify | Verify | Current OpenAPI currently exposes it | Confirm model constraints |
| `9x16` | Verify | Verify | Verify | Current OpenAPI currently exposes it | Confirm model constraints |
| `1x1` | Verify | Verify | Verify | Current OpenAPI currently exposes it | Confirm model constraints |

A future OpenAPI snapshot may add or remove raw options. Never preserve a stale value merely because another plugin still accepts it.

## Benchmark guidance

Flash is intended for latency-sensitive applications. Any published benchmark number must include:

- benchmark date;
- STT, turn-detection, LLM, TTS, and avatar component stack;
- measurement definition and start/end points;
- network and hardware context where available;
- a clear statement that the result is not a guaranteed production SLA.
