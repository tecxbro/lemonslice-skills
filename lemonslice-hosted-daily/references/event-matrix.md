# Hosted Daily event matrix

Event names outside the stable core must be verified against the current Hosted Daily documentation before implementation.

| Direction | Envelope field | Event | Meaning | Terminal? | Expected UI transition | Cleanup required? |
| --- | --- | --- | --- | --- | --- | --- |
| Incoming | `ev.data.type` | `bot_ready` | Pipeline is streaming and controls may be eligible; not first-frame proof | No | `joining_daily` → `pipeline_ready` / `waiting_for_frame` | No |
| Incoming | `ev.data.type` | duplicate `bot_ready` | Repeated readiness notification | No | No transition; keep current state | No; record duplicate diagnostic |
| Incoming | `ev.data.type` | `idle_timeout` | Session ended from inactivity | Yes | Any live state → `ended` | Leave/destroy call object and clear credentials |
| Incoming | `ev.data.type` | `daily_error` | Hosted/Daily pipeline failure; inspect fatal flag | Sometimes | Fatal → `retryable_failed`; nonfatal → preserve call | Fatal: full cleanup; nonfatal: diagnostics only |
| Incoming | Daily top level | `error` | Daily client/transport failure | Usually | Startup/active → `retryable_failed` | Leave/destroy, detach listeners, clear tracks |
| Incoming | Daily top level | `participant-left` | A participant left; terminal only for the identified avatar participant | Sometimes | Avatar departure → `retryable_failed` or `ended` | Clear avatar track; leave if call is unusable |
| Incoming | Daily top level | `left-meeting` | Local Daily client has left | Yes | `ending` → `ended`; unexpected leave → failed | Destroy call object and listeners |
| Incoming | `ev.data.type` | `video_generation_error` | Avatar segment generation failed | Sometimes | Startup → failed; healthy active call → warning | Preserve healthy current media when possible |
| Outgoing | `event` | `chat-msg` | User text or intentionally enabled `/imagine` command | No | No automatic transition | Rate-limit and validate text |
| Outgoing | `event` | `force-end` | Explicit Hosted hangup | Yes | Active → `ending` | Always leave/destroy locally even if send fails |
| Local/Outgoing | application state | image update requested | App accepted one image-change request | No | Active → updating appearance | Block overlapping request unless protocol permits it |
| Incoming | documented image envelope | image generation started | Replacement generation began | No | Keep active call and old frame visible | Start/update timeout |
| Incoming | documented image envelope | image generation completed | Provider reports replacement complete | No | Stay updating until replacement frame renders | Clear generation timeout after frame readiness |
| Incoming | documented image envelope | image generation failed | Replacement failed | No when old media is healthy | Updating → active with error notice | Clear pending state; preserve old frame |
| Incoming | documented transcription envelope | transcription event | Interim/final user or agent transcript where enabled | No | Update transcript only; never call readiness | Redact/log according to data policy |
| Incoming | any | unknown nonfatal event | Forward-compatible message not yet understood | No | No transition | Record structured diagnostic; ignore safely |
| Incoming | any | late event after local hangup | Provider message arrives after terminal local state | No | Remain `ended` | Ignore mutation; allow only redacted diagnostic |

The parser must distinguish Daily top-level events from LemonSlice `app-message` envelopes and must never let unknown nonfatal messages crash the call state machine.
