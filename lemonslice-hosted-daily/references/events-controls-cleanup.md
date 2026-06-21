# Events, Controls, and Cleanup

## Contents
- App-message events
- Daily lifecycle events
- Send text
- Force end
- Runtime image updates
- Cleanup rules
- Error handling
- Common mistakes

## App-message events
LemonSlice Hosted Daily events arrive through Daily `app-message`.

The frontend should listen for `app-message` and parse the message defensively.

Required events to handle:

### `bot_ready`

Meaning: LemonSlice avatar/bot is ready.

Required behavior:

- clear startup timeout
- transition `waiting_for_bot` -> `active`
- show active call UI

### `idle_timeout`

Meaning: the session ended because of inactivity.

Required behavior:

- transition to `ended`
- leave the Daily room if still connected
- clear timers
- show restart/retry UI

### `daily_error`

Meaning: Daily/hosted pipeline error.

Required behavior:

- read fields defensively, for example `error`, `err_msg`, `message`, `fatal`
- if fatal or during startup, leave room and transition to `retryable_failed`
- show user-visible retry UI
- do not expose raw stack traces

### `video_generation_error`

Meaning: avatar video generation failed.

Required behavior:

- transition to `retryable_failed` unless app has a documented recovery path
- leave room or disable call controls
- show user-visible error
- offer retry by creating a fresh room through backend

Optional events to surface:

- `user_transcription`
- `agent_transcription`

### Image-change events

Handle these if the app supports runtime image updates:

- `image_change_requested`
- `image_created`
- `image_change_complete`
- `image_change_error`

## Controls
Use Daily app messages for hosted-agent controls and chat.

Supported guidance:

### Send user text

Use `chat-msg` when the user sends text to the hosted agent.

Shape:

```ts
callObject.sendAppMessage(
  {
    event: "chat-msg",
    message: userText
  },
  "*"
)
```

### End session

Use `force-end` when the user intentionally ends the hosted session.

Shape:

```ts
callObject.sendAppMessage(
  {
    event: "force-end"
  },
  "*"
)
```

After sending `force-end`, the frontend should still run local cleanup:

* disable controls
* transition to `ending`
* call `leave()`
* clear timers
* clear stale credentials

### Appearance/image updates

Only document `/imagine ...` through `chat-msg` if the app is intentionally allowing runtime image modification.

Do not invent unsupported app-message events.

## Cleanup
The frontend must handle Daily participant and room lifecycle events.

Handle:

- `participant-left`
- `left-meeting`
- Daily top-level `error`

Required behavior:

- If the local user leaves, cleanup and move to `ended`.
- If the LemonSlice bot/agent leaves, move to `ended` or `retryable_failed` depending on whether this was expected.
- Do not assume every `participant-left` event is the bot.
- Track the bot participant if the app can identify it.
- Always clear startup timeout and retry timers.
- Always clear stale `room_url` and `token` after terminal states.

Clean up timers and stale credentials in these scenarios:
- on hangup
- on idle timeout
- on fatal error
- on startup timeout
- on participant leave
- on component unmount
