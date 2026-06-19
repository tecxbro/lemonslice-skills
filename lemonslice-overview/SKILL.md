---
name: lemonslice-overview
description: Conceptual product map for Lemon Slice. Use this first to understand what Lemon Slice is, what it is not, why multiple integration paths exist, what each Lemon Slice skill is for, and where the agent should route next.
license: MIT
---

# Lemon Slice Overview

## Official docs
- LemonSlice LLM docs index
- Introduction / Welcome
- Reference overview
- LiveKit integration
- Pipecat integration
- Widget overview
- Hosted Pipeline overview
- Hosted Daily integration
- Best practices
- Actions / controls

## Use this skill when
You need a conceptual product map to understand the architecture of Lemon Slice, its integration paths, and how the various agent skills in this repository map to those paths.

## Do not use this skill when
- The user already selected a path and needs implementation instructions.
- The task requires endpoint payloads, package installation, or code edits.
- The task is a production audit.
- The task is specifically about runtime control/actions.
- The task is specifically about frontend Daily joining.

## What Lemon Slice is

Lemon Slice is the real-time avatar video layer for production voice and video agents.

In the main production path, a developer already has or builds an agent stack:
- STT
- LLM
- TTS
- orchestration
- transport/session handling

Lemon Slice adds the avatar video layer: it receives agent audio and produces lip-synced avatar video over WebRTC.

The primary production integrations are LiveKit and Pipecat.

## What Lemon Slice is not

Lemon Slice is not always a full AI backend.

In self-managed, LiveKit, and Pipecat paths, Lemon Slice does not replace the developer’s STT, LLM, TTS, agent logic, or orchestration.

Lemon Slice is not always a widget. The widget is only one integration path.

Lemon Slice is not something frontend code should call directly with private API keys.

Lemon Slice is not a replacement for transport lifecycle handling, readiness checks, interruption handling, latency budgeting, or production cleanup.

## Why multiple integration paths exist

The paths exist because different teams want different levels of control.

The main questions are:
1. Who owns STT/LLM/TTS?
2. Who owns the frontend UI?
3. Is this a production agent, a prototype, or a no-code embed?
4. Is the project already built on LiveKit, Pipecat, Daily, or just a website?

Lemon Slice supports multiple paths so teams can either:
- keep their existing agent stack and add avatar video,
- let Lemon Slice manage the AI pipeline,
- or use a prebuilt widget for the fastest embed.

## Product path map

| Path | Who owns STT/LLM/TTS? | Who owns UI? | Use when |
|---|---|---|---|
| LiveKit | Developer | Developer | Existing or planned LiveKit Agents stack |
| Pipecat | Developer | Developer | Existing or planned Pipecat pipeline |
| Self-Managed API | Developer | Developer | Custom stack without LiveKit/Pipecat |
| Hosted Pipeline | Lemon Slice | Developer | Developer wants Lemon Slice to manage STT/LLM/TTS but wants custom UI |
| Hosted Daily | Lemon Slice | Developer | Backend already created hosted session and frontend must join Daily room |
| Widget | Lemon Slice | Lemon Slice/prebuilt | Fast no-backend website embed |

## Skill map

- `lemonslice-overview`: Product map and conceptual orientation.
- `lemonslice-integration-choice`: Mandatory router for choosing the correct path.
- `lemonslice-self-managed`: Use Lemon Slice as avatar/video layer in a custom developer-owned stack.
- `lemonslice-livekit`: Add Lemon Slice avatars to LiveKit Agents.
- `lemonslice-pipecat`: Add Lemon Slice avatars to Pipecat pipelines.
- `lemonslice-hosted`: Create/manage hosted sessions where Lemon Slice manages STT/LLM/TTS.
- `lemonslice-hosted-daily`: Build the frontend that joins a hosted Lemon Slice Daily room.
- `lemonslice-widget`: Embed and control the no-backend web widget.
- `lemonslice-api-reference`: Use raw Lemon Slice REST APIs correctly.
- `lemonslice-control-actions`: Runtime control, actions, emotions, image updates, and termination.
- `lemonslice-production-patterns`: Security, latency, reliability, cleanup, and deployment hardening.

## Where to route next

After this overview:

- If the user request is vague, route to `lemonslice-integration-choice`.
- If the project clearly uses LiveKit, route to `lemonslice-livekit`.
- If the project clearly uses Pipecat, route to `lemonslice-pipecat`.
- If the developer owns STT/LLM/TTS but no framework is clear, route to `lemonslice-self-managed`.
- If Lemon Slice should manage STT/LLM/TTS, route to `lemonslice-hosted`.
- If the backend already returns Daily room credentials, route to `lemonslice-hosted-daily`.
- If the user wants a no-backend website embed, route to `lemonslice-widget`.
- If the task is about endpoint correctness, route to `lemonslice-api-reference`.
- If the task is about runtime actions or termination, route to `lemonslice-control-actions`.
- If the task is about production hardening, security, latency, cleanup, or deployment, route to `lemonslice-production-patterns`.

## Common mistakes
- Confusing Hosted Pipeline with Self-Managed Pipeline. Hosted means Lemon Slice runs the AI; Self-Managed means you run the AI.
- Starting to code before choosing a clear integration path. The APIs and packages are entirely different for each path.
- Assuming Lemon Slice provides the LLM brains for LiveKit/Pipecat pipelines.

## Validation checklist

- [ ] Did I explain Lemon Slice as the avatar/video layer, not always the full agent backend?
- [ ] Did I clearly distinguish self-managed, hosted, and widget paths?
- [ ] Did I explain why multiple paths exist?
- [ ] Did I map every repo skill to its purpose?
- [ ] Did I route vague requests to `lemonslice-integration-choice`?
- [ ] Did I avoid endpoint payloads, package installs, and implementation-heavy details?
- [ ] Did I avoid duplicating the full router decision tree?
