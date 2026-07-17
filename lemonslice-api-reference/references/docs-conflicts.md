# Documentation conflicts

Audited 2026-07-17.

## Control authentication and responses

The verified OpenAPI control operation declares `security: []` and includes response code `413`. The current rendered endpoint page omits `X-API-Key` and lists `200`, `400`, `404`, and `500`, omitting `413`.

Therefore:

- keep control calls in trusted backend code;
- preserve known-working authentication behavior;
- inspect both the current OpenAPI and rendered endpoint page;
- do not conclude that the endpoint is safely callable from a browser;
- report the response/auth conflict rather than claiming one universal rule.

The rendered page also states that `image_url` is required for `update-image`, while the current normalized OpenAPI variant does not mark `image_url` required. Application adapters must still require it.

## Runtime image-update duration

The realtime-updates overview describes very fast image changes, while the control documentation warns that an image swap can take several seconds and can cut off currently playing avatar audio.

Implementation skills must:

- invoke image replacement while the avatar is silent when possible;
- keep the current frame visible while replacement initializes;
- wait for the replacement frame rather than updating UI optimistically;
- avoid promising sub-second completion.

`update-image` resets the model and should be treated as asynchronous acknowledgement rather than proof that a new frame is visible.

## Agora

The product overview names Agora among self-managed paths, but the current public raw REST `transport_type` enum exposes only `livekit` and `daily`.

Do not send `transport_type: "agora"` based solely on product-level documentation. Require an official Agora integration contract, installed SDK, or current indexed documentation before implementation.

## Reset idle timeout

The verified control discriminator currently includes `reset-idle-timeout`. Keep the exact kebab-case event name and re-check the snapshot before changing support.

## Raw REST versus plugin fields

Framework plugins and raw REST can expose different fields on different release schedules. The current raw OpenAPI exposes model/aspect options and multipart input, but those facts do not establish matching constructor fields in LiveKit Python, LiveKit Node, or Pipecat.

## Readiness language

`bot_ready` means the pipeline is streaming or eligible for controls. The user-visible active state must wait for the first rendered avatar frame.
