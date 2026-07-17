# Documentation conflicts

Audited 2026-07-17.

## Control authentication

The current OpenAPI operation declares `security: []`, while its documented responses include `401 Authentication denied`. Rendered examples may omit `X-API-Key`.

Therefore:

- keep control calls in trusted backend code;
- preserve known-working authentication behavior;
- inspect both the current OpenAPI and rendered endpoint page;
- do not conclude that the endpoint is safely callable from a browser;
- report the conflict rather than claiming one universal auth rule.

## Runtime image-update duration

The realtime-updates overview describes very fast image changes, while the current control operation says an image swap can take up to five seconds and cuts off currently playing avatar audio.

Implementation skills must:

- invoke image replacement while the avatar is silent when possible;
- keep the current frame visible while replacement initializes;
- wait for the replacement frame rather than updating UI optimistically;
- avoid promising sub-second completion.

`update-image` resets the model, may interrupt current audio, and should be treated as asynchronous acknowledgement rather than proof that a new frame is visible.

## Agora

The product overview names Agora among self-managed paths, but the current public raw REST `transport_type` enum exposes only `livekit` and `daily`.

Do not send `transport_type: "agora"` based solely on product-level documentation. Require an official Agora integration contract, installed SDK, or current indexed documentation before implementation.

## Reset idle timeout

Rendered control documentation may include Reset Idle Timeout while a verified raw control schema omits it. Confirm the current operation contract before adding or removing support.

## Raw REST versus plugin fields

Framework plugins and raw REST can expose different fields on different release schedules. Model, aspect-ratio, local-image, and convenience options must be verified on the exact integration surface instead of copied across surfaces.

## Readiness language

`bot_ready` means the pipeline is streaming or eligible for controls. The user-visible active state must wait for the first rendered avatar frame.
