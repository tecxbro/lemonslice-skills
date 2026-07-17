# Hosted Daily event matrix

| Direction | Field | Example | Purpose |
| --- | --- | --- | --- |
| Incoming | `ev.data.type` | `bot_ready` | Pipeline is streaming; not first-frame proof |
| Incoming | `ev.data.type` | `idle_timeout` | Session ended from inactivity |
| Incoming | `ev.data.type` | `daily_error` | Hosted/Daily pipeline failure |
| Incoming | `ev.data.type` | `video_generation_error` | Avatar segment failure |
| Outgoing | `event` | `chat-msg` | User text or intentional `/imagine` command |
| Outgoing | `event` | `force-end` | Explicit hangup |

Parse unknown messages defensively and preserve forward compatibility.
