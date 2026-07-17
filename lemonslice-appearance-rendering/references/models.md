# Model reference

Audited 2026-07-17.

| Model | Use | Constraints |
| --- | --- | --- |
| Standard/default | General baseline | Leave `model` unset |
| Lite | Cost-sensitive high-volume apps | Lower resolution; `2x3` and `1x1` only; enterprise access may apply |
| Flash | Latency-sensitive apps | Test visual artifacts and quality for the actual character |
| Pro | High-resolution immersive experiences | Confirm account and installed SDK support |

Plugin docs currently use `model` in Python/Pipecat and `extraPayload.model` in Node.
