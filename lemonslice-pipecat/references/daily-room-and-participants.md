# Daily Room and Participants

## Contents
- Daily behavior
- Auto-created rooms
- Human/bot/avatar model
- Participant filtering
- UI rules
- Common mistakes

## Daily behavior
* Pipecat with LemonSlice uses Daily as the underlying transport layer.
* This does **not** mean Hosted Daily.
* `daily_room_url` and `daily_token` are optional.
* If `daily_room_url` is provided, LemonSlice uses that Daily room.
* If `daily_token` is provided, LemonSlice uses it for room auth.
* If `daily_room_url` is omitted, LemonSlice automatically creates a Daily room.
* Auto-created Daily rooms may create extra participant-minute cost.
* When LemonSlice auto-creates the room, the code should not assume the app owns room lifecycle exactly like a manually-created Daily room.

> Do not confuse these with Hosted Daily `room_url` and `token`.
> Hosted Daily uses `/liveai/rooms` and a Lemon Slice-managed agent.
> Pipecat uses `LemonSliceTransport` inside the developer-owned Pipecat pipeline.

## Participants
Explicit participant model:

1. **Human user**
   Speaks into Daily/WebRTC room and receives avatar audio/video.

2. **Pipecat bot participant**
   Runs developer-owned STT/LLM/TTS pipeline. Should not be displayed as the visible avatar.

3. **LemonSlice avatar participant**
   Receives bot/TTS audio and renders lip-synced avatar video/audio.

Rules:
* LemonSlice avatar participant is filtered out from `transport.on_client_connected` and `transport.on_client_disconnected`.
* Only human participant connections should trigger those handlers.
* Daily video UI should filter out the Pipecat bot participant.
* Avatar microphone is automatically muted to avoid feedback loops.
