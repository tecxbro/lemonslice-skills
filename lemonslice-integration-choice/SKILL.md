---
name: lemonslice-integration-choice
description: MANDATORY ROUTER. Must run first to choose the correct Lemon Slice path (Self-Managed, LiveKit, Pipecat, Hosted, Widget).
license: MIT
---

# Lemon Slice Integration Choice

> **MANDATORY ROUTER:** For any vague request like “add Lemon Slice to my app,” “integrate Lemon Slice,” “add an avatar,” “add video agent,” or “make this work with Lemon Slice,” this skill MUST run first before any implementation skill. Do not write Lemon Slice implementation code until this router has selected the path.

## Official docs
- https://lemonslice.com/docs/llms.txt
- https://lemonslice.com/docs/introduction.md
- https://lemonslice.com/docs/widget/overview.md
- https://lemonslice.com/docs/hosted/overview.md
- https://lemonslice.com/docs/hosted/integrations/daily-room-integration.md
- https://lemonslice.com/docs/api-reference/create-hosted-session.md
- https://lemonslice.com/docs/reference/overview.md
- https://lemonslice.com/docs/livekit.md
- https://lemonslice.com/docs/pipecat.md
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/reference/best-practices.md
- https://lemonslice.com/docs/reference/actions.md

## Use this skill when
You receive any request to integrate Lemon Slice or add an avatar, and you need to determine the correct technical path.

## Do not use this skill when
The integration path has already been formally selected and explicitly documented in your current task context.

## Agent workflow

### Step 1: Repo Inspection
Prefer inspecting the repo and making a best-effort route from evidence. Ask a clarifying question ONLY when the repo has no detectable framework/backend/UI signal and multiple paths remain equally likely.

Look for:
- `@livekit/*`, `livekit-agents`, `AgentSession`, `Room`, `RoomEvent` → **LiveKit**.
- `pipecat-ai`, `PipelineTask`, `DailyTransport`, `LemonSliceTransport` → **Pipecat**.
- `@daily-co/daily-js`, `@daily-co/daily-react`, `room_url`, `token`, hosted backend route → **Hosted Daily** or Pipecat depending on backend.
- Plain website with no backend and user asks for embed → **Widget**.
- Existing backend calling `https://lemonslice.com/api/liveai/rooms` → **Hosted/API**.
- Existing backend calling `https://lemonslice.com/api/liveai/sessions` → **Self-managed/API**.
- Frontend-only use of `LEMONSLICE_API_KEY` → production/security issue; route to **Production Patterns**.

### Step 2: Decision Tree
Use the following ordered decision tree to route to the correct skills:

**A. Widget (`lemonslice-widget`)**
Route here when the user wants the fastest no-backend website embed, a corner chat/avatar widget, marketing site embed (Shopify/Squarespace/Wix/Next.js), or “just paste it into my site.” The basic integration is just `<lemon-slice-widget agent-id="agent_id">` plus a script tag.

**B. LiveKit (`lemonslice-livekit`)**
Route here when the repo uses LiveKit Agents, LiveKit rooms, LiveKit token routes, `AgentSession`, `RoomOutputOptions`, or a LiveKit worker. Lemon Slice is added as the avatar video layer.

**C. Pipecat (`lemonslice-pipecat`)**
Route here when the repo uses Pipecat, Daily transport through Pipecat, `Pipeline`, `PipelineTask`, `DailyParams`, or `LemonSliceTransport`. **Important:** “Daily” inside Pipecat does NOT mean Hosted Daily. Pipecat is still self-managed.

**D. Hosted Pipeline (`lemonslice-hosted`)**
Route here when Lemon Slice should manage STT, LLM, TTS, and avatar, while the developer only creates/manages hosted sessions server-side. Creates a Daily room through `POST /liveai/rooms` and returns credentials.

**E. Hosted Daily (`lemonslice-hosted-daily`)**
Route here ONLY when the backend already creates hosted sessions and the task is to build the frontend that joins the returned Daily room. The frontend listens for Lemon Slice events on Daily’s `app-message` (especially `bot_ready`).

**F. Self-Managed generic (`lemonslice-self-managed`)**
Route here when the developer owns STT/LLM/TTS but is not clearly using LiveKit or Pipecat. Uses `POST /liveai/sessions` requiring `transport_type` of `livekit` or `daily`.

**G. Raw API usage (`lemonslice-api-reference`)**
Route here when the user specifically needs direct backend REST calls, status polling, metadata retrieval, or debugging `/liveai/rooms` vs `/liveai/sessions`.

**H. Control/actions (`lemonslice-control-actions`)**
Route here ONLY after a session path is known and the task is about termination, pose/action triggers, image updates, prompt updates, `/imagine`, force-end, or runtime control.

**I. Production hardening (`lemonslice-production-patterns`)**
Route here as a follow-up pass (Secondary skill) after the primary integration path. Select this when the request involves security, latency, reliability, timeouts, cleanup, `bot_ready`, disconnects, startup failures, or production review.

### Step 3: Output Contract
You must support "route chaining" (returning a primary skill and optional secondary skills). Before concluding this skill and moving to implementation, you MUST output your routing decision in exactly this Markdown format:

```text
Selected path: [Path Name]
Primary skill: [lemonslice-...]
Secondary skill(s): [lemonslice-... or None]
Why: [Brief justification based on decision tree]
Evidence from user/repo: [Signals found during inspection]
Do not use: [Paths you explicitly rejected]
Next action: [The immediate next step, usually reading the primary skill]
```

## Validation checklist
- [ ] Did I inspect the repo for framework signals first?
- [ ] Did I avoid asking unnecessary clarification questions?
- [ ] Did I format my decision using the exact Output Contract?
- [ ] Did I stop and output the decision before writing any code?
