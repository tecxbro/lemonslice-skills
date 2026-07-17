---
name: lemonslice-overview
description: Explain LemonSlice Character World Models, capabilities, deployment modes, integration paths, and the skill map. Use for conceptual questions or when the user wants an overview rather than implementation.
license: MIT
---

# LemonSlice overview

## Character World Model

LemonSlice turns a single character image plus streaming speech audio into real-time interactive character video. Ordinary avatar creation does not require per-character training or fine-tuning.

## Basic media contract

Inputs:

1. avatar image or configured agent;
2. streaming TTS audio;
3. optional provisioned action/control events.

Output:

- synchronized avatar audio and video in a WebRTC call.

A typical conversational pipeline is: STT/VAD hears the user → LLM selects a response → TTS generates audio → LemonSlice generates synchronized character video.

## Capability groups

### Generative model capabilities

- human, cartoon, animal, mascot, and other facial characters;
- hand and full-body motion;
- emotional expression;
- clothing, object, background, and scene changes where supported;
- physics- and spatially-aware motion.

### Deterministic application controls

Only controls explicitly exposed by the selected integration and provisioned for the account/avatar are deterministic application events. Do not turn every product capability into an assumed public API action.

## Deployment map

### Self-Managed Pipeline

The developer owns STT, VAD/turn detection, LLM, TTS, tools, conversation state, and UI. LemonSlice supplies avatar media.

Subpaths:

- new official starter → `lemonslice-quickstart`;
- existing LiveKit Agents app → `lemonslice-livekit`;
- existing Pipecat pipeline, including Pipecat-over-Daily → `lemonslice-pipecat`;
- custom raw LiveKit or Daily transport → `lemonslice-self-managed`;
- Zoom, Meet, Teams, or Webex bridge → `lemonslice-meeting-platforms`.

### Hosted Pipeline

LemonSlice owns STT, LLM, TTS, and avatar generation. The app owns authorization, room creation through `lemonslice-hosted`, and a custom Daily frontend through `lemonslice-hosted-daily`.

### Widget

A prebuilt LemonSlice-managed call experience for the fastest embed and least application-owned lifecycle control.

## Cross-cutting skills

- runtime image, prompt, idle, action, or terminate controls → `lemonslice-control-actions`;
- model, aspect ratio, framing, or green screen → `lemonslice-appearance-rendering`;
- lifecycle, readiness, latency, cleanup, and billing safety → `lemonslice-production-patterns`;
- exact endpoint/schema questions → `lemonslice-api-reference`.

## Product claims caveat

Do not translate product-level capacity statements such as long calls or high concurrency into guaranteed account entitlements. Verify the user's current plan, account, region, model, and integration limits.

## Routing

Use `lemonslice-integration-choice` for ambiguous requests. Explicit framework or feature requests go directly to their implementation skill.

Current sources:
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/introduction/index.md
- https://lemonslice.com/docs/quickstart.md
- https://lemonslice.com/docs/reference/production-checklist.md
- https://lemonslice.com/docs/livekit/index.md
- https://lemonslice.com/docs/pipecat/index.md
