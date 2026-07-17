# Documentation conflicts

Audited 2026-07-17.

## Public OpenAPI source instability

Different retrieval locations have returned materially different `openapi.json` bodies during the same audit window.

One observed GitHub Actions runner response included:

- `application/json` and `multipart/form-data` for self-managed creation;
- raw `model` and `aspect_ratio` fields;
- `reset-idle-timeout` in the control discriminator;
- control response `413` without `401`.

Another public retrieval location returned:

- `application/json` only;
- no raw `model` or `aspect_ratio` fields in `SessionInput`;
- five control events without `reset-idle-timeout`;
- control response `401` without `413`.

Treat this as source inconsistency, not as permission to choose the more convenient contract. The drift workflow probes repeatedly, records SHA-256 digests, final URLs, dates, ETags, ages, and last-modified values, and exits with a distinct source-inconsistent status when normalized contracts conflict.

Generated snapshots contain generated contract data and source metadata only. Human interpretation belongs in this file.

Implementation skills must:

- inspect the exact source evidence captured for the run;
- avoid transferring volatile fields across REST and plugin surfaces;
- avoid promising multipart, raw model options, or idle-reset support unless the active contract is stable and explicit;
- report source inconsistency when different locations disagree.

## Control authentication and responses

Observed control contracts disagree on authentication metadata and response codes. One OpenAPI representation declares `security: []` with `413`; another declares `security: []` while documenting `401` and omitting `413`. Rendered examples may omit `X-API-Key`.

Therefore:

- keep control calls in trusted backend code;
- preserve known-working authentication behavior;
- inspect both the captured OpenAPI evidence and rendered endpoint page;
- do not conclude that the endpoint is safely callable from a browser;
- report the response/auth conflict rather than claiming one universal rule.

Application adapters must validate required payload fields even when one schema variant is incomplete.

## Runtime image-update duration

The realtime-updates overview describes very fast image changes, while control documentation warns that an image swap can take several seconds and can cut off currently playing avatar audio.

Implementation skills must:

- invoke image replacement while the avatar is silent when possible;
- keep the current frame visible while replacement initializes;
- wait for the replacement frame rather than updating UI optimistically;
- avoid promising sub-second completion.

`update-image` resets the model and should be treated as asynchronous acknowledgement rather than proof that a new frame is visible.

## Agora

The product overview names Agora among self-managed paths, but observed raw REST `transport_type` enums expose only `livekit` and `daily`.

Do not send `transport_type: "agora"` based solely on product-level documentation. Require an official Agora integration contract, installed SDK, or current indexed documentation before implementation.

## Reset idle timeout

`reset-idle-timeout` has appeared in one observed control discriminator and is absent from another. Do not add or remove it based on a single edge response. Re-check the captured source probes and preserve known-working behavior while reporting the conflict.

## Raw REST versus plugin fields

Framework plugins and raw REST can expose different fields on different release schedules. Raw `model`, `aspect_ratio`, and multipart input have appeared in one observed OpenAPI representation and are absent from another. Neither observation establishes matching constructor fields in LiveKit Python, LiveKit Node, or Pipecat.

## Readiness language

`bot_ready` means the pipeline is streaming or eligible for controls. The user-visible active state must wait for the first rendered avatar frame.
