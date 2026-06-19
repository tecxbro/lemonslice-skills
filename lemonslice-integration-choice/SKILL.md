---
name: lemonslice-integration-choice
description: Help choose the correct Lemon Slice integration path (Self-Managed, LiveKit, Pipecat, Hosted, Hosted Daily, or Widget).
license: MIT
---

# Lemon Slice Integration Choice

## Use this skill when
You need to decide which Lemon Slice integration path to use for a new project, or you need to verify that an existing project is using the correct approach.

## Do not use this skill when
You already know exactly which integration path you are building and just need the implementation details.

## Agent workflow
1. Analyze the user's requirements and tech stack.
2. Use the following routing table to determine the correct path:

| User wants                      | Route to                         |
| ------------------------------- | -------------------------------- |
| Bring your own STT/LLM/TTS      | `lemonslice-self-managed`        |
| LiveKit Agents                  | `lemonslice-livekit`             |
| Pipecat pipeline                | `lemonslice-pipecat`             |
| Lemon Slice manages the session | `lemonslice-hosted`              |
| Daily frontend for hosted room  | `lemonslice-hosted-daily`        |
| Website embed                   | `lemonslice-widget`              |
| Raw REST API usage              | `lemonslice-api-reference`       |
| Actions/control/session ending  | `lemonslice-control-actions`     |
| Reliability/security/latency    | `lemonslice-production-patterns` |

3. If the user's request is ambiguous, stop and ask clarifying questions before writing any code. Do NOT guess the integration path.
4. Once the path is determined, proceed to the corresponding skill file.

## Common mistakes
- Starting to write code before explicitly confirming the integration path.
- Assuming "Daily" means "Hosted Daily". Pipecat also uses Daily as a transport, but it is a Self-Managed integration.
- Assuming a website embed requires complex API integration. If they just want a simple drop-in, route to `lemonslice-widget`.

## Validation checklist
- [ ] Have I explicitly mapped the user's requirements to one of the paths in the routing table?
- [ ] Have I asked clarifying questions if the requirements are ambiguous?
- [ ] Have I routed to the correct subsequent skill before writing code?
