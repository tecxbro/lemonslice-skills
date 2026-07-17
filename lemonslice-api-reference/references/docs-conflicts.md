# Documentation conflicts

Audited 2026-07-17.

## Control authentication and responses

The rendered control examples omit `X-API-Key`, and the current OpenAPI operation declares `security: []`. The current OpenAPI response set includes `413`, while the rendered page shows `200`, `400`, `404`, and `500`. Keep control calls server-side, inspect both sources, and preserve known-working application behavior rather than asserting a universal authentication rule.

## Reset idle timeout

Rendered control documentation includes Reset Idle Timeout. Confirm the current control event schema before adding or removing it, because the rendered page and downloadable OpenAPI can expose different levels of detail.

## Raw REST versus plugin fields

The current self-managed REST schema exposes `model`, `aspect_ratio`, `simulcast`, recording configuration, and multipart image upload. LiveKit and Pipecat plugin constructors can still lag or expose different first-class fields, so inspect the installed package signature separately from the endpoint schema.

## Readiness language

`bot_ready` means the pipeline is streaming/eligible for controls. The user-visible active state must wait for the first rendered avatar frame.
