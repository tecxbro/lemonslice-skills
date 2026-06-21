# Hosted Daily Control

## Contents
- Control surface
- Send text
- Force end
- `/imagine`
- Image-change events
- Cleanup after control
- Common mistakes

## Control surface
Hosted Daily controls use Daily `sendAppMessage`.
Do not use REST control endpoint.

## Send text
```ts
sendAppMessage(
  {
    event: "chat-msg",
    message: "Your message here",
    name: "User"
  },
  "*"
)
```

## Force end
```ts
sendAppMessage(
  { event: "force-end" },
  "*"
)
```

Behavior:

* immediately stops the realtime agent
* agent leaves the room
* billing stops
* frontend must still leave/cleanup local Daily state

After `force-end`:

* disable controls
* transition UI to ending/ended
* call Daily `leave()` where appropriate
* clear timers
* clear stale credentials
* clear queued controls

## `/imagine`
For Hosted Daily, avatar image updates are sent as a `chat-msg` beginning with `/imagine`.

```ts
sendAppMessage(
  {
    event: "chat-msg",
    message: "/imagine being in front of a fireplace",
    name: "User"
  },
  "*"
)
```

Rules:

* `/imagine` does not trigger a spoken response.
* It regenerates the avatar image from the prompt.
* The avatar retains core identity and proportions.
* The agent continues normal interaction after the image update completes.
* The agent must allow users to modify appearance.
* Do not invent a hosted REST image update endpoint.

Handle these Hosted Daily image events:

* `image_change_requested`
* `image_created`
* `image_change_complete`
* `image_change_error`

## Image-change events
- `image_change_requested`
- `image_created`
- `image_change_complete`
- `image_change_error`
