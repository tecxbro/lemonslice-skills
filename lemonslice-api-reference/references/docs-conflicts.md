# Documentation conflicts

Audited 2026-07-17.

## Control authentication

Rendered control examples omit `X-API-Key`; the OpenAPI operation has been observed with `security: []`; related responses can still include `401`. Keep control calls server-side, inspect current sources, and preserve known-working application behavior.

## Reset idle timeout

Rendered control documentation includes Reset Idle Timeout, while the downloaded OpenAPI snapshot may omit it. Do not remove working support or add it blindly; flag the conflict.

## Plugin fields versus raw REST

LiveKit/Pipecat docs expose model, aspect ratio, and local image conveniences that may not appear in raw REST schemas. Inspect installed plugin signatures and current endpoint schemas separately.

## Readiness language

`bot_ready` means the pipeline is streaming/eligible for controls. The user-visible active state must wait for the first rendered avatar frame.
