# Daily Join State Machine

## Contents
- Credential contract
- Join flow
- Readiness model
- Required states
- State transitions
- Startup timeout
- Retry behavior
- Common mistakes

## Credential contract
Frontend receives:
- `room_url`
- `token`
Optional:
- `session_id`
- `image_url`
- `status`

## Join flow
Recommended flow:

1. User clicks Start.
2. Set UI state to `creating_room`.
3. Call the app backend to create/get hosted Daily credentials.
4. Validate that backend returned `room_url` and `token`.
5. Create or reuse a Daily call object.
6. Call Daily join with the returned `room_url` and `token`.
7. Set UI state to `joining_daily` while the Daily join is in progress.
8. After Daily join succeeds, set UI state to `waiting_for_bot`.
9. Start a startup timeout while waiting for `bot_ready`.
10. Transition to `active` only when LemonSlice sends `bot_ready` via `app-message`.

Important: Daily join success only means the browser joined the Daily room. It does not mean the LemonSlice avatar is ready. The avatar readiness signal is `bot_ready`.

## Readiness model
Daily join success is not readiness.
Only `bot_ready` transitions to active.

## States
- `idle`
- `creating_room`
- `joining_daily`
- `waiting_for_bot`
- `active`
- `ending`
- `ended`
- `retryable_failed`
- `failed`

## Transitions
| From | Trigger | To | Required behavior |
| --- | --- | --- | --- |
| `idle` | user clicks start | `creating_room` | disable start button, show loading |
| `creating_room` | backend returns room credentials | `joining_daily` | validate `room_url` and `token` |
| `creating_room` | backend error | `retryable_failed` | show retry UI |
| `joining_daily` | Daily join resolves | `waiting_for_bot` | start startup timeout |
| `joining_daily` | Daily join fails | `retryable_failed` | leave/destroy call object if needed |
| `waiting_for_bot` | `bot_ready` | `active` | clear startup timeout |
| `waiting_for_bot` | startup timeout | `retryable_failed` | leave room, show retry UI |
| `waiting_for_bot` | fatal `daily_error` | `retryable_failed` | leave room, show retry UI |
| `active` | user hangs up | `ending` | send `force-end` if appropriate, then leave |
| `active` | `idle_timeout` | `ended` | cleanup and show restart UI |
| `active` | bot participant leaves unexpectedly | `retryable_failed` | cleanup and show retry UI |
| `active` | `video_generation_error` | `retryable_failed` | cleanup or disable call UI |
| `ending` | Daily leave completes | `ended` | clear local state |
| `retryable_failed` | user retries | `creating_room` | create a fresh hosted room |

## Startup timeout
The frontend must not wait forever for `bot_ready`.

Recommended behavior:

1. Start a timer after Daily join succeeds and state becomes `waiting_for_bot`.
2. Use a clear threshold, for example 30 seconds, unless the app has a product-specific value.
3. If `bot_ready` arrives before timeout:
   - clear timer
   - transition to `active`
4. If timeout fires:
   - call Daily `leave()`
   - clear timer
   - clear local room credentials
   - transition to `retryable_failed`
   - show retry UI

Retry behavior:

- Retry should call the app backend again.
- Backend should create a fresh hosted room or return fresh credentials.
- Do not blindly reuse stale `room_url` and `token`.

## Retry
Retry calls backend again.
Do not reuse stale `room_url` or `token`.
