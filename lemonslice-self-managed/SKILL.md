---
name: lemonslice-self-managed
description: Build self-managed LemonSlice sessions for custom developer-owned STT/LLM/TTS stacks. Use this when the user owns the agent pipeline and needs backend REST setup with `POST /api/liveai/sessions`, `GET /api/liveai/sessions/{session_id}`, `transport_type: livekit|daily`, `properties`, `agent_id` or `agent_image_url`, status handling, and server-side `X-API-Key`. Do not use for official LiveKit/Pipecat plugins, Hosted `/liveai/rooms`, Widget, or Hosted Daily frontend.
license: MIT
---

# Lemon Slice Self-Managed Pipeline

## Official docs
- https://lemonslice.com/docs/api-reference/create-self-managed-session.md
- https://lemonslice.com/docs/api-reference/get-self-managed-session.md

## Use this skill when
- `lemonslice-integration-choice` has selected Self-Managed.
- The developer owns STT, LLM, TTS, turn-taking, orchestration, and transport/session handling.
- LemonSlice should only receive agent audio and produce synced avatar video/audio.
- The repo does not clearly use the official LiveKit or Pipecat integration path.
- The task is about raw self-managed REST session creation/status/control setup.

## Do not use this skill when
- Hosted Pipeline: LemonSlice manages STT/LLM/TTS.
- Widget: no-backend website embed.
- Hosted Daily frontend: backend already returns Daily room credentials from hosted sessions.
- LiveKit Agents: use `lemonslice-livekit`.
- Pipecat pipeline: use `lemonslice-pipecat`.
- Production hardening-only audit: use `lemonslice-production-patterns`.
- Runtime control/actions-only task: use `lemonslice-control-actions`.

## What self-managed means
Self-managed means the developer brings the AI pipeline:
- STT
- LLM
- TTS
- turn-taking
- interruption handling
- app/backend orchestration
- transport/session ownership

LemonSlice does not replace those pieces. LemonSlice receives the agent’s audio and returns synchronized avatar video/audio over the selected WebRTC transport.

## Agent workflow
1. Confirm routing
   - Make sure `lemonslice-integration-choice` selected self-managed.
   - If the repo uses LiveKit Agents, route to `lemonslice-livekit`.
   - If the repo uses Pipecat, route to `lemonslice-pipecat`.

2. Keep credentials server-side
   - Store `LEMONSLICE_API_KEY` only in backend/agent-server env.
   - Use `X-API-Key` from server-side code only.

3. Choose transport
   - Use `transport_type: "livekit"` or `transport_type: "daily"`.
   - Do not invent other transport values.

4. Choose avatar identity
   - Provide exactly one of `agent_id` or `agent_image_url`.

5. Build transport `properties`
   - LiveKit requires `livekit_url` and `livekit_token`.
   - Daily uses `daily_room_url` and `daily_token`; omitting room URL lets LemonSlice create one at extra cost.

6. Add only documented optional fields
   - `agent_prompt`
   - `agent_idle_prompt`
   - `idle_timeout`
   - `response_done_timeout`
   - `simulcast`

7. Create session
   - Call `POST /api/liveai/sessions`.
   - Store returned `session_id`.

8. Track lifecycle
   - Poll `GET /api/liveai/sessions/{session_id}` if status is needed.
   - Handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, and `FAILED`.

9. Hand off control/actions
   - For runtime actions, emotions, image updates, or termination, route to `lemonslice-control-actions`.

## Endpoint family
Self-managed uses `/liveai/sessions`.

Hosted/Widget room flows use `/liveai/rooms`.

Do not mix these endpoint families.

## Create request examples

#### LiveKit transport example
```json
{
  "transport_type": "livekit",
  "agent_id": "agent_abc123",
  "properties": {
    "livekit_url": "wss://example.livekit.cloud",
    "livekit_token": "..."
  }
}
```

#### Daily transport example
```json
{
  "transport_type": "daily",
  "agent_image_url": "https://example.com/avatar.png",
  "properties": {
    "daily_room_url": "https://your-domain.daily.co/your-room",
    "daily_token": "..."
  }
}
```

## Create session
`POST /api/liveai/sessions` returns `session_id`.

Store `session_id` in backend state. Use it for:
- status polling
- control/action calls
- cleanup/termination flows

## transport_type
`transport_type` tells LemonSlice how the agent audio is delivered and how the synced A/V is returned.

Allowed:
- `livekit`
- `daily`

Not allowed:
- `webrtc`
- `browser`
- `hosted`
- `rooms`
- `pipecat`
- `tavus`
- arbitrary provider names

## transport properties
`properties` contains transport-specific connection details.

For `transport_type: "livekit"`:
- `properties.livekit_url` is required.
- `properties.livekit_token` is required.
- `simulcast` is available only with LiveKit transport.

For `transport_type: "daily"`:
- `properties.daily_room_url` is optional.
- `properties.daily_token` is optional.
- If `daily_room_url` is omitted, LemonSlice can create a Daily room, with additional cost.
- Daily recording config belongs inside Daily transport properties, not as generic top-level fields.

## agent_id vs agent_image_url
Provide exactly one avatar identity:

- `agent_id`: use an existing LemonSlice agent.
- `agent_image_url`: use a public image URL for zero-shot avatar creation.

Never send both.
Never send neither.
Prefer a stable HTTPS URL for `agent_image_url`.

## Optional fields
| Field | Purpose | Notes |
|---|---|---|
| `agent_prompt` | Influences speaking-state expression/demeanor | High-level, not precise deterministic control |
| `agent_idle_prompt` | Influences idle-state expression/demeanor | High-level idle behavior |
| `idle_timeout` | Seconds before idle timeout | Default 60; negative disables idle timeout |
| `response_done_timeout` | Seconds without new audio before response is treated complete | Useful for TTS providers without reliable end events |
| `simulcast` | Publishes multiple video resolutions | LiveKit transport only |

## Get session / status polling
Use `GET /api/liveai/sessions/{session_id}` when the backend needs status or completion metadata.

The response always includes `session_status`.

When the session is completed, it may include `cost`.

## Lifecycle states
- `QUEUED`: session is waiting for a GPU container. Usually quick when warm capacity exists; cold start can take longer.
- `ACTIVE`: avatar is live.
- `COMPLETED`: session ended successfully. Completed responses may include `cost`.
- `TIMED_OUT`: GPU container timed out.
- `FAILED`: session ended with an error.

## API key handling
The LemonSlice API key must stay in trusted backend/agent-server code.

Do not:
- call LemonSlice REST APIs directly from frontend/browser/mobile clients
- expose `X-API-Key` in client bundles
- return the API key to frontend code
- log the raw API key
- store the API key in public repo files

Frontend code may receive app-owned session state, but never the LemonSlice API key.

## When to route elsewhere
Route to `lemonslice-livekit` when:
- the repo clearly uses LiveKit Agents
- the user asks for the official LiveKit plugin
- the task is about `AvatarSession`, LiveKit room wiring, or `bot_ready`

Route to `lemonslice-pipecat` when:
- the repo clearly uses Pipecat
- the task is about `LemonSliceTransport`
- the task is a Pipecat pipeline, even if Daily appears in the transport

Stay in `lemonslice-self-managed` when:
- the developer owns STT/LLM/TTS
- the repo does not clearly use LiveKit/Pipecat
- the work is direct REST session creation/status with `/api/liveai/sessions`

Route to `lemonslice-hosted` when:
- LemonSlice should manage STT/LLM/TTS

Route to `lemonslice-hosted-daily` when:
- hosted backend already created a Daily room and frontend needs to join it

Route to `lemonslice-control-actions` when:
- the task is about actions, emotions, image updates, or termination

## Common mistakes
- Using `/api/liveai/rooms` or `/api/liveai/rooms/{id}` for self-managed sessions.
- Forgetting the `properties` object.
- Providing `transport_type: "daily"` but assuming this means Hosted Daily.
- Providing both `agent_id` and `agent_image_url`.
- Providing neither `agent_id` nor `agent_image_url`.
- Exposing `LEMONSLICE_API_KEY` or `X-API-Key` to frontend code.
- Using undocumented `transport_type` values.
- Adding undocumented top-level fields.
- Using this generic self-managed REST skill when the repo clearly uses LiveKit Agents or Pipecat.
- Treating `simulcast` as available for Daily transport; it is LiveKit-only.
- Ignoring `QUEUED`, `TIMED_OUT`, and `FAILED` states.

## Validation checklist
- [ ] Did `lemonslice-integration-choice` explicitly select self-managed?
- [ ] Is the repo free of clear LiveKit/Pipecat framework signals that should route elsewhere?
- [ ] Does session creation use `POST /api/liveai/sessions`?
- [ ] Does status polling use `GET /api/liveai/sessions/{session_id}`?
- [ ] Is `LEMONSLICE_API_KEY` used only server-side via `X-API-Key`?
- [ ] Is `transport_type` exactly `livekit` or `daily`?
- [ ] Does the payload include exactly one of `agent_id` or `agent_image_url`?
- [ ] Does the payload include the correct `properties` for the selected transport?
- [ ] Are optional fields limited to documented fields?
- [ ] Is `simulcast` only used with LiveKit transport?
- [ ] Is the returned `session_id` stored for status/control/cleanup?
- [ ] Does the implementation handle `QUEUED`, `ACTIVE`, `COMPLETED`, `TIMED_OUT`, and `FAILED`?
- [ ] Does the skill avoid becoming a LiveKit or Pipecat implementation guide?
- [ ] Does the skill avoid Hosted `/liveai/rooms` endpoint confusion?
