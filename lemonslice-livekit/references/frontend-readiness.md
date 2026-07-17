# LiveKit frontend readiness

Use `LiveKitAvatarReadyWatcher` from `@lemonsliceai/avatar/livekit-react` for the first rendered frame. Keep `bot_ready` as a separate pipeline/control gate.

Also handle:

- `RoomEvent.ParticipantDisconnected` for avatar departure
- `RoomEvent.Disconnected` for room/network failure
- topic `lemonslice/message`, type `startup_failure`
- a bounded startup timer and retry UI
